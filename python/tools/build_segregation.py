# -*- coding: utf-8 -*-
"""
Ségrégation résidentielle par ville : revenu et âge, à partir des carreaux
FiLoSoFi 200 m (INSEE), réexposés par Koumoul avec le code commune (lcog_geo).

Idée : « Quelles villes font cohabiter riches et pauvres, lesquelles les
séparent ? » et la même chose pour l'âge. Pour chaque commune > 10 000 hab, on
récupère ses carreaux de 200 m et on mesure à quel point les niveaux de vie (et
les âges) sont mélangés ou séparés dans l'espace.

RÈGLE : la sortie publique doit être COMPRÉHENSIBLE. On calcule des indices
techniques (P90/P10, Gini spatial, dissimilarité) mais on les traduit en un
score de mixité 0-100, un label verbal et une phrase concrète. Le rang national
(percentile) est calculé une fois toutes les villes connues.

Usage :
  python build_segregation.py 92051 35238 13055   # échantillon (affiche, n'écrit pas)
  python build_segregation.py                      # run national complet (écrit les JSON)
"""
import json, sys, time, math, os, statistics, zipfile, csv, io, unicodedata, urllib.request, urllib.parse
from collections import defaultdict
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
FRONT_DATA = (SCRIPT_DIR / '..' / '..' / 'frontend' / 'public' / 'data').resolve()
VECTEURS = FRONT_DATA / 'atlas' / 'communes-vecteurs.json'
OUT_DIR = FRONT_DATA / 'segregation'
CACHE_DIR = SCRIPT_DIR / '_cache_segregation'

# FiLoSoFi IRIS 2021 (revenus disponibles) : porte le rapport interdécile D9/D1
# PAR IRIS = la dispersion des revenus DANS un quartier (mélange interne réel,
# riches et pauvres, pas seulement pauvres/non-pauvres). Communes >= 5000 hab.
IRIS_URL = "https://www.insee.fr/fr/statistiques/fichier/8229323/BASE_TD_FILO_IRIS_2021_DISP_CSV.zip"

# Millésime : Koumoul sert les carreaux FiLoSoFi 2021 (données mises à jour le 04/03/2026 ;
# vérifié le 30/10/2026 contre le fichier Insee Filosofi2021_carreaux_200m_csv.zip,
# https://www.insee.fr/fr/statistiques/8735162). Le cache du 04/07/2026 est donc en 2021.
API = "https://opendata.koumoul.com/data-fair/api/v1/datasets/filosofi-carreaux-200m/lines"
SELECT = ("idcar_200m,lcog_geo,_geopoint,ind,men,men_pauv,i_est_200,ind_snv_avg,"
          "ind_0_3,ind_4_5,ind_6_10,ind_11_17,ind_18_24,ind_25_39,ind_40_54,ind_55_64,ind_65_79,ind_80p")
AGE_JEUNES = ("ind_0_3", "ind_4_5", "ind_6_10", "ind_11_17")
AGE_ACTIFS = ("ind_18_24", "ind_25_39", "ind_40_54", "ind_55_64")
AGE_SENIORS = ("ind_65_79", "ind_80p")

# Paris / Lyon / Marseille : les carreaux portent le code d'arrondissement.
PLM = {
    "75056": [f"751{n:02d}" for n in range(1, 21)],
    "69123": [f"6938{n}" for n in range(1, 10)],
    "13055": [f"132{n:02d}" for n in range(1, 17)],
}
ARR_PREFIX = ("751", "132")  # + "6938" (Lyon), traités à part

# ------------------------------------------------------------------ récupération

def qs_for(code):
    codes = PLM.get(code, [code])
    return "lcog_geo:(" + " OR ".join(codes) + ")"

def fetch(code, retries=4):
    """Tous les carreaux d'une commune, paginés. Cache disque pour reprise/rejeu."""
    CACHE_DIR.mkdir(exist_ok=True)
    cache = CACHE_DIR / f"{code}.json"
    if cache.exists():
        return json.loads(cache.read_text(encoding="utf-8"))
    url = f"{API}?" + urllib.parse.urlencode({"qs": qs_for(code), "size": 10000, "select": SELECT})
    out = []
    while url:
        for attempt in range(retries):
            try:
                with urllib.request.urlopen(url, timeout=90) as r:
                    d = json.load(r)
                break
            except Exception as e:
                if attempt == retries - 1:
                    raise
                time.sleep(2 * (attempt + 1))
        out += d.get("results", [])
        url = d.get("next")
    cache.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    time.sleep(0.15)  # politesse
    return out

def _num(s):
    s = (s or "").strip().replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None

_IRIS = None
def iris_by_commune():
    """{code commune -> [(rapport_interdecile, mediane), ...]} depuis le CSV INSEE."""
    global _IRIS
    if _IRIS is not None:
        return _IRIS
    CACHE_DIR.mkdir(exist_ok=True)
    zip_path = CACHE_DIR / "iris_filosofi.zip"
    if not zip_path.exists():
        print("Téléchargement du FiLoSoFi IRIS...")
        urllib.request.urlretrieve(IRIS_URL, zip_path)
    _IRIS = {}
    with zipfile.ZipFile(zip_path) as z:
        name = next(n for n in z.namelist() if n.startswith("BASE_TD_FILO_IRIS") and n.endswith(".csv"))
        with z.open(name) as f:
            for r in csv.DictReader(io.TextIOWrapper(f, "latin-1"), delimiter=";"):
                iris = r.get("IRIS", "")
                rd, med = _num(r.get("DISP_RD21")), _num(r.get("DISP_MED21"))
                if len(iris) < 5 or rd is None:
                    continue
                _IRIS.setdefault(iris[:5], []).append((rd, med))
    print(f"  IRIS chargés pour {len(_IRIS)} communes.")
    return _IRIS

def _normname(s):
    s = unicodedata.normalize("NFD", s or "").encode("ascii", "ignore").decode()
    return " ".join(s.upper().replace("-", " ").replace("'", " ").split())

def _plm_name(commune):
    n = _normname(commune)
    for ville in ("PARIS", "MARSEILLE", "LYON"):
        if n.startswith(ville + " ") and "ARRONDISSEMENT" in n:
            return ville
    return n

def _dep_of(code):
    if code[:2] in ("2A", "2B"):
        return code[:2]
    if code[:3] in ("971", "972", "973", "974", "976", "977", "978", "984", "986", "987", "988"):
        return code[:3]
    return code[:2]

_COLLEGES = None
def colleges_by_ville():
    """{(dep, nom normalisé) -> {'pu':[ips...], 'pr':[ips...]}} pour les collèges
    (etablissements.tsv du dossier École). Sert à mesurer la ségrégation SCOLAIRE
    et l'écart public/privé, pour la comparer à la ségrégation résidentielle."""
    global _COLLEGES
    if _COLLEGES is not None:
        return _COLLEGES
    _COLLEGES = defaultdict(lambda: {"pu": [], "pr": []})
    with open(FRONT_DATA / "showcases" / "etablissements.tsv", encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            if r["niveau"] != "c" or not r["ips"].strip():
                continue
            key = (r["dep"], _plm_name(r["commune"]))
            _COLLEGES[key]["pr" if r["secteur"] == "pr" else "pu"].append(float(r["ips"]))
    return _COLLEGES

# ------------------------------------------------------------------ statistiques

def wquantile(pairs, q):
    pairs = sorted(pairs)
    if not pairs:
        return None
    tot = sum(w for _, w in pairs)
    acc, target = 0, q * tot
    for v, w in pairs:
        acc += w
        if acc >= target:
            return v
    return pairs[-1][0]

def wgini(pairs):
    pairs = sorted(pairs)
    tot = sum(w for _, w in pairs)
    totv = sum(v * w for v, w in pairs)
    if not tot or not totv:
        return None
    g, cwv = 0.0, 0.0
    for v, w in pairs:
        g += w * (2 * cwv + v * w) / (tot * totv)
        cwv += v * w
    return round(1 - g, 4)

def dissimilarity(a, b):
    A, B = sum(a), sum(b)
    if A == 0 or B == 0:
        return None
    return round(0.5 * sum(abs(ai / A - bi / B) for ai, bi in zip(a, b)), 4)

def entropy3(g1, g2, g3):
    """Entropie normalisée (0 = un seul groupe, 1 = parts égales) de 3 groupes."""
    tot = g1 + g2 + g3
    if tot == 0:
        return None
    h = 0.0
    for g in (g1, g2, g3):
        p = g / tot
        if p > 0:
            h -= p * math.log(p)
    return round(h / math.log(3), 4)

# ------------------------------------------------------------------ calcul ville

def compute_city(code, nom, pop):
    rows = fetch(code)
    if not rows:
        return None
    real = [r for r in rows if not r.get("i_est_200")]  # revenu fiable = non imputé
    inc = [(r["ind_snv_avg"], r["ind"]) for r in real
           if r.get("ind_snv_avg") and r.get("ind")]
    if len(inc) < 5:
        return None
    p10, p50, p90 = (wquantile(inc, q) for q in (.1, .5, .9))
    gini = wgini(inc)

    # Taux de pauvreté global de la ville (carreaux) : cadre le niveau et sert
    # à la composition des quartiers.
    men_tot = sum(r.get("men", 0) or 0 for r in rows)
    pauv_tot = sum(r.get("men_pauv", 0) or 0 for r in rows)
    taux_pauvrete = round(100 * pauv_tot / men_tot, 1) if men_tot else None

    # Axes IRIS (FiLoSoFi, revenus disponibles, communes >= 5000 hab) :
    #  - MÉLANGE INTERNE = médiane des rapports interdéciles D9/D1 des IRIS
    #    (dispersion des revenus DANS un quartier = hauts et bas revenus mêlés).
    #  - SÉPARATION = coefficient de variation des médianes entre IRIS
    #    (les quartiers diffèrent-ils par leur niveau de vie ?).
    coms = PLM.get(code, [code])
    irows = []
    for c in coms:
        irows += iris_by_commune().get(c, [])
    interne_rd = sep_cv = iris_p90p10 = None
    n_iris = len(irows)
    if irows:
        interne_rd = round(statistics.median([rd for rd, _ in irows]), 2)
        meds = sorted([m for _, m in irows if m])
        if len(meds) >= 2:
            mean_m = sum(meds) / len(meds)
            sep_cv = round(statistics.pstdev(meds) / mean_m, 3) if mean_m else None
        if len(meds) >= 10:
            iris_p90p10 = round(meds[int(0.9 * len(meds))] / meds[int(0.1 * len(meds))], 2)

    # Composition des quartiers : chaque carreau classé par sa part de ménages
    # pauvres, puis part des HABITANTS vivant dans chaque type. Plus concret que
    # l'indice : « X % des habitants vivent dans un quartier mixte ».
    q_mix = q_aise = q_pauv = 0.0
    for r in rows:
        m = r.get("men", 0) or 0
        nb = r.get("ind", 0) or 0
        if m <= 0 or nb <= 0:
            continue
        p = (r.get("men_pauv", 0) or 0) / m
        if p < 0.10:
            q_aise += nb
        elif p >= 0.40:
            q_pauv += nb
        else:
            q_mix += nb
    q_tot = q_mix + q_aise + q_pauv
    quartiers = {
        "pct_mixtes": round(100 * q_mix / q_tot) if q_tot else None,
        "pct_aises": round(100 * q_aise / q_tot) if q_tot else None,
        "pct_pauvres": round(100 * q_pauv / q_tot) if q_tot else None,
    }

    # École : dispersion d'IPS des collèges de la ville + écart public / privé.
    csec = colleges_by_ville().get((_dep_of(code), _plm_name(nom)))
    ecole = None
    if csec:
        ips_all = csec["pu"] + csec["pr"]
        if len(ips_all) >= 3:
            ips_pub = round(statistics.mean(csec["pu"])) if csec["pu"] else None
            ips_pr = round(statistics.mean(csec["pr"])) if csec["pr"] else None
            ecole = {
                "n_colleges": len(ips_all),
                "ips_std": round(statistics.pstdev(ips_all), 1),
                "ips_public": ips_pub,
                "ips_prive": ips_pr,
                "gap_pub_pr": (ips_pr - ips_pub) if (ips_pub is not None and ips_pr is not None) else None,
            }

    young = [sum(r.get(k, 0) or 0 for k in AGE_JEUNES) for r in rows]
    senior = [sum(r.get(k, 0) or 0 for k in AGE_SENIORS) for r in rows]
    d_age = dissimilarity(young, senior)
    ty, ta, ts = (sum(sum(r.get(k, 0) or 0 for k in grp) for r in rows)
                  for grp in (AGE_JEUNES, AGE_ACTIFS, AGE_SENIORS))

    ind_tot = sum(r.get("ind", 0) or 0 for r in rows)
    # Points pour la mini-carte : [lat, lon, niveau_de_vie, nb_hab], carreaux réels.
    carreaux = []
    for r in real:
        gp = (r.get("_geopoint") or "").split(",")
        if len(gp) == 2 and r.get("ind_snv_avg") and r.get("ind"):
            carreaux.append([round(float(gp[0]), 5), round(float(gp[1]), 5),
                             round(r["ind_snv_avg"]), round(r["ind"], 1)])
    return {
        "code": code, "nom": nom, "pop": pop,
        "n_carreaux": len(rows), "pct_impute": round(100 * (len(rows) - len(real)) / len(rows)),
        "pop_couverte": round(ind_tot),
        "revenu": {"p10": round(p10), "p50": round(p50), "p90": round(p90),
                   "p90_p10": round(p90 / p10, 2), "gini_spatial": gini,
                   "taux_pauvrete": taux_pauvrete,
                   "interne_rd": interne_rd, "sep_cv": sep_cv,
                   "iris_p90p10": iris_p90p10, "n_iris": n_iris},
        "age": {"dissimilarite": d_age, "entropie": entropy3(ty, ta, ts),
                "pct_jeunes": round(100 * ty / (ty + ta + ts)) if (ty + ta + ts) else None,
                "pct_seniors": round(100 * ts / (ty + ta + ts)) if (ty + ta + ts) else None},
        "quartiers": quartiers,
        "ecole": ecole,
        "carreaux": carreaux,
    }

# ------------------------------------------------------------------ langage clair

# Niveau de vie médian national 2021 (INSEE), pour situer une ville.
NAT_MEDIAN = 22040

def pct_rank(values, v):
    """Percentile : % de villes dont la valeur est PLUS BASSE (100 = la plus haute)."""
    if v is None or not values:
        return None
    return round(100 * sum(1 for x in values if x < v) / len(values))

def band(score):
    """haut (>=66) / moyen / bas (<=33) à partir d'un percentile."""
    if score is None:
        return None
    return "haut" if score >= 66 else ("bas" if score <= 33 else "moyen")

def niveau_label(p50):
    """Niveau de vie global de la ville : le CADRE, pour ne pas prendre un fort
    mélange interne (ex. Neuilly) pour de la mixité sociale."""
    if p50 is None:
        return None
    if p50 >= NAT_MEDIAN * 1.4:
        return "Très aisée"
    if p50 >= NAT_MEDIAN * 1.15:
        return "Aisée"
    if p50 <= NAT_MEDIAN * 0.7:
        return "Très modeste"
    if p50 <= NAT_MEDIAN * 0.85:
        return "Modeste"
    return "Intermédiaire"

MELANGE_LABEL = {"haut": "Quartiers très mélangés", "moyen": "Quartiers plutôt mélangés", "bas": "Quartiers homogènes"}
SEPAR_LABEL = {"haut": "Quartiers très séparés", "moyen": "Quartiers contrastés", "bas": "Quartiers semblables"}
AGE_LABEL = {"haut": "Âges séparés", "moyen": "Un peu triée par âge", "bas": "Âges mélangés"}

def typologie_revenu(sep_b, interne_b):
    """Étiquette courte, à partir de la séparation ENTRE quartiers et du mélange
    DANS les quartiers. (Le niveau de vie est porté à part.)"""
    if sep_b is None or interne_b is None:
        return None
    if sep_b == "haut":
        return "Fracturée"
    if sep_b == "bas":
        return "Mélangée" if interne_b == "haut" else ("Homogène" if interne_b == "bas" else "Peu séparée")
    return "Contrastée"

def phrase_revenu(nom, niveau, sep_b, interne_b, iris_p90p10):
    niv = {"Très aisée": "une ville très aisée", "Aisée": "une ville aisée",
           "Intermédiaire": "une ville au niveau de vie moyen",
           "Modeste": "une ville modeste", "Très modeste": "une ville très modeste"}.get(niveau, "")
    mel = ("ses quartiers mêlent fortement hauts et bas revenus" if interne_b == "haut"
           else "ses quartiers sont assez homogènes en revenus" if interne_b == "bas"
           else "ses quartiers mélangent modérément les revenus")
    if sep_b == "haut":
        sep_t = "et diffèrent nettement les uns des autres"
        if iris_p90p10:
            sep_t += f" (le quartier médian le plus aisé y gagne {iris_p90p10:.1f}× le plus modeste)"
    elif sep_b == "bas":
        sep_t = "et se ressemblent d'un bout à l'autre de la ville"
    else:
        sep_t = "et diffèrent un peu entre eux"
    return f"À {nom}, {niv} : {mel}, {sep_t}."

def phrase_age(nom, b):
    if b is None:
        return None
    if b == "haut":
        return f"À {nom}, quartiers jeunes et quartiers âgés sont nettement séparés."
    if b == "bas":
        return f"À {nom}, les âges se mélangent dans les quartiers."
    return f"À {nom}, jeunes et seniors habitent des quartiers un peu différents."

# ------------------------------------------------------------------ liste des villes

def liste_villes(seuil=10000):
    d = json.loads(VECTEURS.read_text(encoding="utf-8"))
    villes = []
    for r in d["rows"]:
        code, nom, pop = r[0], r[1], r[2]
        if not pop or pop <= seuil:
            continue
        if code[:3] in ARR_PREFIX or code[:4] == "6938":  # arrondissements PLM exclus
            continue
        villes.append((code, nom, pop))
    return villes

# ------------------------------------------------------------------ échantillon

def run_sample(codes):
    d = json.loads(VECTEURS.read_text(encoding="utf-8"))
    noms = {r[0]: (r[1], r[2]) for r in d["rows"]}
    print(f"{'Ville':<20}{'médiane':>9}{'tx_pauv':>8}{'interne_RD':>11}{'sep_CV':>8}{'nIRIS':>6}")
    print("-" * 65)
    for code in codes:
        nom, pop = noms.get(code, (code, 0))
        c = compute_city(code, nom, pop)
        if not c:
            print(f"{nom:<20}  (pas de données)")
            continue
        rv = c["revenu"]
        print(f"{nom:<20}{rv['p50']:>9}{rv['taux_pauvrete']:>7.1f}%{str(rv['interne_rd']):>11}{str(rv['sep_cv']):>8}{rv['n_iris']:>6}")

# ------------------------------------------------------------------ évitement établissement

def build_colleges_evitement():
    """Par collège PUBLIC : IPS vs revenu de son quartier (carreaux 200 m dans un
    rayon de 0,7 km). Résidu = rang national d'IPS − rang national du revenu local
    (débiaisé de l'effet plafond). Résidu très négatif = collège public socialement
    sous son quartier (gentrification / évitement) ; très positif = public attractif
    ou sélectif au-dessus de son voisinage. Écrit colleges-evitement.json."""
    if not (OUT_DIR / "villes.json").exists():
        print("  (villes.json manquant, évitement établissement sauté)"); return
    vj = json.loads((OUT_DIR / "villes.json").read_text(encoding="utf-8"))["villes"]
    code_of = {(_dep_of(v["code"]), _normname(v["nom"])): v["code"] for v in vj}

    def haversine(a, b, c, d):
        R, t = 6371.0, math.pi / 180
        dla, dlo = (c - a) * t, (d - b) * t
        x = math.sin(dla / 2) ** 2 + math.cos(a * t) * math.cos(c * t) * math.sin(dlo / 2) ** 2
        return 2 * R * math.asin(min(1, math.sqrt(x)))

    cols = []
    with open(FRONT_DATA / "showcases" / "etablissements.tsv", encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            if r["niveau"] != "c" or r["secteur"] != "pu":
                continue
            if not r["ips"].strip() or not r["lat"].strip():
                continue
            code = code_of.get((r["dep"], _plm_name(r["commune"])))
            if code:
                cols.append({"code": code, "nom": r["nom"], "commune": r["commune"], "dep": r["dep"],
                             "ips": float(r["ips"]), "lat": float(r["lat"]), "lon": float(r["lon"])})

    ccache = {}
    def carreaux(code):
        if code not in ccache:
            p = CACHE_DIR / f"{code}.json"
            pts = []
            if p.exists():
                for x in json.loads(p.read_text(encoding="utf-8")):
                    if x.get("i_est_200") or not x.get("ind_snv_avg") or not x.get("ind"):
                        continue
                    gp = (x.get("_geopoint") or "").split(",")
                    if len(gp) == 2:
                        pts.append((float(gp[0]), float(gp[1]), x["ind_snv_avg"], x["ind"]))
            ccache[code] = pts
        return ccache[code]

    ok = []
    for c in cols:
        near = [(rev, pop) for (la, lo, rev, pop) in carreaux(c["code"])
                if haversine(c["lat"], c["lon"], la, lo) <= 0.7]
        w = sum(p for _, p in near)
        if w and len(near) >= 3:
            c["revenu_local"] = sum(rev * p for rev, p in near) / w
            ok.append(c)
    if len(ok) < 50:
        print("  (évitement établissement : trop peu de collèges rattachés, sauté)"); return

    ips_all = sorted(c["ips"] for c in ok)
    inc_all = sorted(c["revenu_local"] for c in ok)
    for c in ok:
        c["ips_rang"] = pct_rank(ips_all, c["ips"])
        c["quartier_rang"] = pct_rank(inc_all, c["revenu_local"])
        c["resid"] = c["ips_rang"] - c["quartier_rang"]

    def pack(c):
        return {"nom": c["nom"], "commune": c["commune"], "dep": c["dep"], "ips": round(c["ips"]),
                "ips_rang": c["ips_rang"], "revenu_local": round(c["revenu_local"]),
                "quartier_rang": c["quartier_rang"], "resid": c["resid"]}
    out = {
        "n": len(ok), "rayon_km": 0.7,
        "decroches": [pack(c) for c in sorted(ok, key=lambda z: z["resid"])[:20]],
        "attractifs": [pack(c) for c in sorted(ok, key=lambda z: -z["resid"])[:20]],
    }
    (OUT_DIR / "colleges-evitement.json").write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    print(f"  collèges-évitement : {len(ok)} collèges publics rattachés, écrit.")

# ------------------------------------------------------------------ territorial (départements)

def build_departements():
    """Agrège les IRIS par DÉPARTEMENT (couverture de tout le territoire, pas
    seulement les villes > 10 000 hab). Par département : séparation entre
    quartiers (CV des médianes IRIS), mélange interne (interdécile médian),
    niveau de vie médian, en rangs nationaux. Écrit departements.json."""
    iris = iris_by_commune()
    try:
        idx = json.loads((FRONT_DATA / "atlas" / "territoires-index.json").read_text(encoding="utf-8"))
        noms = {c: n for c, n in idx.get("deps", [])}
    except Exception:
        noms = {}
    bydep = {}
    for commune, rows in iris.items():
        bydep.setdefault(_dep_of(commune), []).extend(rows)

    deps = []
    for dep, rows in bydep.items():
        meds = sorted(m for _, m in rows if m)
        if len(meds) < 5:
            continue
        mean_m = sum(meds) / len(meds)
        deps.append({
            "dep": dep, "nom": noms.get(dep, dep).title(), "n_iris": len(rows),
            "sep_cv": round(statistics.pstdev(meds) / mean_m, 3) if mean_m else None,
            "interdecile": round(statistics.median([rd for rd, _ in rows]), 2),
            "niveau": round(statistics.median(meds)),
        })
    sep_all = sorted(d["sep_cv"] for d in deps if d["sep_cv"] is not None)
    inter_all = sorted(d["interdecile"] for d in deps if d["interdecile"] is not None)
    niv_all = sorted(d["niveau"] for d in deps if d["niveau"] is not None)
    for d in deps:
        d["separation"] = pct_rank(sep_all, d["sep_cv"])
        d["melange_interne"] = pct_rank(inter_all, d["interdecile"])
        d["niveau_rang"] = pct_rank(niv_all, d["niveau"])
    deps.sort(key=lambda x: x["separation"] if x["separation"] is not None else -1, reverse=True)
    (OUT_DIR / "departements.json").write_text(
        json.dumps({"n": len(deps), "departements": deps}, ensure_ascii=False), encoding="utf-8")
    print(f"  départements : {len(deps)} écrits.")

# ------------------------------------------------------------------ run national

def run_national():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    villes = liste_villes()
    print(f"{len(villes)} villes > 10 000 hab à traiter...")
    computed = []
    for i, (code, nom, pop) in enumerate(villes, 1):
        try:
            c = compute_city(code, nom, pop)
        except Exception as e:
            print(f"  [{i}] {nom} ({code}) ERREUR: {e}")
            continue
        if c:
            computed.append(c)
        if i % 50 == 0:
            print(f"  {i}/{len(villes)} traitées ({len(computed)} valides)")

    # Trois axes revenu, percentiles nationaux : niveau de vie, mélange interne
    # (interdécile IRIS), séparation (dispersion des médianes IRIS). + tri par âge.
    p50_all = [c["revenu"]["p50"] for c in computed if c["revenu"]["p50"] is not None]
    interne_all = [c["revenu"]["interne_rd"] for c in computed if c["revenu"]["interne_rd"] is not None]
    sep_all = [c["revenu"]["sep_cv"] for c in computed if c["revenu"]["sep_cv"] is not None]
    dage_all = [c["age"]["dissimilarite"] for c in computed if c["age"]["dissimilarite"] is not None]
    ecole_std_all = [c["ecole"]["ips_std"] for c in computed if c.get("ecole")]
    index = []
    for c in computed:
        rv = c["revenu"]
        niveau_s = pct_rank(p50_all, rv["p50"])
        interne_s = pct_rank(interne_all, rv["interne_rd"])
        sep_s = pct_rank(sep_all, rv["sep_cv"])
        tri_s = pct_rank(dage_all, c["age"]["dissimilarite"])
        sep_b, interne_b, tri_b = band(sep_s), band(interne_s), band(tri_s)
        rv["niveau"] = niveau_label(rv["p50"])
        rv["niveau_score"] = niveau_s
        rv["melange_interne"] = interne_s
        rv["melange_label"] = MELANGE_LABEL.get(interne_b)
        rv["separation"] = sep_s
        rv["separation_label"] = SEPAR_LABEL.get(sep_b)
        rv["typologie"] = typologie_revenu(sep_b, interne_b)
        rv["phrase"] = phrase_revenu(c["nom"], rv["niveau"], sep_b, interne_b, rv["iris_p90p10"])
        c["age"]["tri"] = tri_s
        c["age"]["typologie"] = AGE_LABEL.get(tri_b)
        c["age"]["rang_national"] = tri_s
        c["age"]["phrase"] = phrase_age(c["nom"], tri_b)
        # École : percentile national de la ségrégation scolaire + écart à la
        # ségrégation résidentielle (+ = l'école trie PLUS que le logement).
        ec = c.get("ecole")
        if ec:
            ec["ips_std_pct"] = pct_rank(ecole_std_all, ec["ips_std"])
            ec["ecart_ecole_logement"] = (ec["ips_std_pct"] - sep_s) if (ec["ips_std_pct"] is not None and sep_s is not None) else None
        # Fiche par ville (avec les carreaux pour la carte).
        (OUT_DIR / f"{c['code']}.json").write_text(
            json.dumps(c, ensure_ascii=False), encoding="utf-8")
        # Entrée légère pour le classement / la recherche (sans les carreaux).
        index.append({k: c[k] for k in ("code", "nom", "pop")} | {
            "revenu": {kk: rv[kk] for kk in ("p90_p10", "taux_pauvrete", "niveau", "niveau_score", "melange_interne", "interne_rd", "separation", "typologie")},
            "age": {kk: c["age"][kk] for kk in ("dissimilarite", "tri", "typologie")},
            "ecole": ({"ips_std_pct": ec["ips_std_pct"], "ecart": ec["ecart_ecole_logement"],
                       "gap_pub_pr": ec["gap_pub_pr"], "ips_public": ec["ips_public"], "ips_prive": ec["ips_prive"]} if ec else None),
        })
    # Trié des plus séparées (entre quartiers) aux plus homogènes.
    index.sort(key=lambda v: v["revenu"]["separation"] if v["revenu"]["separation"] is not None else -1, reverse=True)
    (OUT_DIR / "villes.json").write_text(
        json.dumps({"n": len(index), "villes": index}, ensure_ascii=False), encoding="utf-8")
    print(f"OK : {len(index)} villes écrites dans {OUT_DIR}")
    build_colleges_evitement()
    build_departements()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "ecole":
        build_colleges_evitement()  # recalcule seulement l'évitement établissement
    elif len(sys.argv) > 1 and sys.argv[1] == "terr":
        build_departements()  # recalcule seulement l'agrégat départemental (via cache IRIS)
    elif len(sys.argv) > 1:
        run_sample(sys.argv[1:])
    else:
        run_national()
