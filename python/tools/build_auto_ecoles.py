# -*- coding: utf-8 -*-
"""
Terrain « Auto-ecoles » : le taux de reussite au permis dit-il qui forme le mieux ?

Comparaison de sites « a contexte egal » sur une donnee publique reelle : le taux de
reussite au permis B en premiere presentation de chaque auto-ecole (Securite routiere).
Le taux brut mele la severite des examens du departement, le profil de la commune et le
travail de l'ecole. On estime ce qu'une ecole moyenne ferait dans le meme contexte
(l'« attendu »), puis l'ecart entre observe et attendu.

  1. auto-ecoles : taux B 1re presentation + nombre de candidats. Les ecoles en ligne ont
     une ligne par departement (agrement suffixe « _<dep> ») a l'adresse du siege :
     leur contexte = le departement seulement.
  2. commune INSEE : arrondissements PLM par code postal, puis base officielle des codes
     postaux (La Poste, anciennes communes en ligne 5), puis nom dans le departement.
  3. contexte communal : JSON atlas deja construits (recensement INSEE 2023) + profil
     social des collegiens (IPS des colleges publics : commune, a defaut intercommunalite,
     a defaut departement ; arrondissements de Paris = Paris).
  4. trois lectures de l'attendu : rien (moyenne nationale), departement (moyenne des
     ecoles du departement), departement + commune (regression ponderee par le nombre de
     candidats, effets fixes departement). Ecarts « retrecis » (bayesien empirique) et
     intervalle a 95 % : une petite ecole n'est pas designee pour un ecart que le hasard
     suffit a produire.
  5. decomposition des ecarts (departement / commune / ecole / hasard) et leviers a
     contexte egal (regression jointe, erreurs-types robustes).
  6. entre departements : correlation du taux moyen avec des indicateurs departementaux
     (habitat, milieu social, ecole dont brevet et IVAL), pour ouvrir l'effet departement.

Sortie : frontend/public/data/showcases/auto-ecoles.json
Usage  : python build_auto_ecoles.py [--explore]   (--explore compare les specifications)
"""
import json
import re
import sys
import unicodedata
import urllib.request
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

SCRIPT_DIR = Path(__file__).parent.resolve()
ROOT = SCRIPT_DIR.parent.parent
CACHE = SCRIPT_DIR / "_cache_auto_ecoles"
CACHE.mkdir(exist_ok=True)
ATLAS = ROOT / "frontend" / "public" / "data" / "atlas"
EPCI_MAP = ROOT / "python" / "data" / "municipales" / "communes-epci.json"
OUT = ROOT / "frontend" / "public" / "data" / "showcases" / "auto-ecoles.json"

DATASET = "liste-des-auto-ecoles-et-taux-de-reussite-au-permis-de-conduire"
URL_DATASET = f"https://www.data.gouv.fr/fr/datasets/{DATASET}/"
URL_AE = "https://autoecoles.securite-routiere.gouv.fr/sites/default/files/certified-schools/auto-ecoles.csv"
URL_POSTE = "https://data.laposte.fr/data-fair/api/v1/datasets/laposte-hexasmal/raw"
URL_CENTRES = "https://geo.api.gouv.fr/communes?fields=code,nom,centre&format=json"
URL_ARRDTS = "https://geo.api.gouv.fr/communes?type=arrondissement-municipal&fields=code,nom,centre&format=json"
URL_DEPS = "https://geo.api.gouv.fr/departements?fields=code,nom&format=json"
URL_DNB = ("https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/"
           "fr-en-dnb-par-etablissement/exports/csv?use_labels=true")
URL_DNB_PAGE = "https://www.data.gouv.fr/fr/datasets/diplome-national-du-brevet-par-etablissement-1/"
URL_IPS = "https://www.education.gouv.fr/depp/l-indice-de-position-sociale-ips-357755"
URL_IVAL = "https://www.data.gouv.fr/datasets/indicateurs-de-valeur-ajoutee-des-lycees-denseignement-general-et-technologique-2"
SESSIONS_DNB = (2019, 2021)  # 2020 : brevet au controle continu, ecarte
# Le serveur de la Securite routiere coupe la connexion sans User-Agent de navigateur.
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36"

MIN_N = 10          # candidats minimum pour afficher une ecole
MIN_N_MODELE = 20   # candidats minimum pour entrer dans l'estimation
MIN_ECOLES_DEP = 10  # ecoles minimum pour un departement dans les correlations
Z95 = 1.96

# Contexte communal (recensement INSEE 2023 via l'atlas, IPS de l'Education nationale).
# Pas de revenu : la serie communale disponible dans l'atlas date de 2014.
SPECS = {
    "lean": ["lpop", "diplome_sup", "ages65", "proprietaires"],
    "ips": ["lpop", "diplome_sup", "ages65", "proprietaires", "ips_college"],
    "ips_sans_diplome": ["lpop", "ages65", "proprietaires", "ips_college"],
    "pcs": ["lpop", "diplome_sup", "cadres", "ouvriers", "ages65", "proprietaires"],
    "large": ["lpop", "diplome_sup", "cadres", "ouvriers", "jeunes", "ages65", "proprietaires", "hlm", "maisons"],
}
SPEC = "ips"
# Lecture des effets : variation « parlante » de chaque variable (libelle, variation, pas).
EFFETS = {
    "lpop": ("Taille de la commune", "population multipliée par 10", float(np.log(10))),
    "diplome_sup": ("Diplômés du supérieur", "+10 points de diplômés du supérieur", 10.0),
    "ages65": ("65 ans et plus", "+10 points de 65 ans et plus", 10.0),
    "proprietaires": ("Propriétaires", "+10 points de propriétaires", 10.0),
    "ips_college": ("Profil social des collégiens (IPS)", "+10 points d'IPS des collèges publics", 10.0),
    "cadres": ("Cadres", "+10 points de cadres", 10.0),
    "ouvriers": ("Ouvriers", "+10 points d'ouvriers", 10.0),
    "jeunes": ("Moins de 15 ans", "+10 points de moins de 15 ans", 10.0),
    "hlm": ("Logements HLM", "+10 points de HLM", 10.0),
    "maisons": ("Maisons", "+10 points de maisons", 10.0),
}
FLAGS = [  # (colonne source, bit, libelle du levier)
    ("aue_labelqualite_flag", 1, "Label qualité"),
    ("aue_ecoleasso_flag", 2, "École associative"),
    ("aue_permis1euro_flag", 4, "Permis à 1 € par jour"),
    ("aue_aac_flag", 8, "Conduite accompagnée proposée"),
    ("aue_cs_flag", 16, "Conduite supervisée proposée"),
]
# Suggestions de groupes par nom : la regle est affichee telle quelle, aucune appartenance
# a un reseau n'est revendiquee (« ecoles dont le nom contient ... »).
GROUPES = [
    {"id": "ecf", "label": "ECF", "q": "ECF"},
    {"id": "cer", "label": "CER", "q": "CER", "exclude": "ECF"},
    {"id": "mercure", "label": "Mercure Formation", "q": "MERCURE"},
    {"id": "stych", "label": "Stych", "q": "STYCH"},
    {"id": "lepermislibre", "label": "Lepermislibre", "q": "LEPERMISLIBRE", "enLigne": True},
    {"id": "marianne", "label": "Marianne Formation", "q": "MARIANNE FORMATION", "enLigne": True},
    {"id": "evs", "label": "EVS", "q": "EVS AUTO", "enLigne": True},
]
# Indicateurs departementaux confrontes au taux moyen de reussite (id, libelle, unite, famille).
DEP_INDICATEURS = [
    ("maisons", "Part de maisons", "%", "habitat"),
    ("proprietaires", "Part de propriétaires", "%", "habitat"),
    ("pop", "Population", "hab.", "habitat"),
    ("ages65", "Part des 65 ans et plus", "%", "habitat"),
    ("ouvriers", "Part d'ouvriers", "%", "social"),
    ("cadres", "Part de cadres", "%", "social"),
    ("diplome_sup", "Diplômés du supérieur", "%", "social"),
    ("ips_college_public", "IPS des collèges publics", "", "ecole"),
    ("dnb", "Réussite au brevet", "%", "ecole"),
    ("va_lycee", "Valeur ajoutée des lycées (IVAL)", "pts", "ecole"),
]
IPS_NIVEAUX = ["commune", "intercommunalité", "département"]


def fetch(url, name):
    path = CACHE / name
    if not path.exists():
        print(f"   telechargement {name}...")
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=600) as r:
            path.write_bytes(r.read())
    return path


def num(s):
    return pd.to_numeric(s.astype(str).str.replace(",", ".", regex=False), errors="coerce")


def norm(s):
    """Nom de commune comparable : majuscules sans accents, ligatures, ST/STE developpes."""
    s = str(s).upper().replace("Œ", "OE").replace("Æ", "AE")
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = re.sub(r"\bCEDEX\b.*$", "", s)
    s = re.sub(r"[^A-Z0-9]+", " ", s).strip()
    s = re.sub(r"\bSTE\b", "SAINTE", s)
    return re.sub(r"\bST\b", "SAINT", s)


def norm_dep(d):
    d = str(d).strip().upper()
    if d.endswith(("2A", "2B")):
        return d[-2:]
    return d.zfill(2) if d.isdigit() and len(d) <= 2 else d


def plm(cp, nom):
    """Arrondissement de Paris, Marseille ou Lyon d'apres le code postal."""
    cp = str(cp).strip()
    if len(cp) != 5 or not cp.isdigit():
        return None
    ville = nom.split(" ")[0] if nom else ""
    if ville == "PARIS" and cp.startswith("75"):
        a = 16 if cp == "75116" else int(cp[3:])
        return f"751{a:02d}" if 1 <= a <= 20 else None
    if ville == "MARSEILLE" and cp.startswith("130"):
        a = int(cp[3:])
        return f"132{a:02d}" if 1 <= a <= 16 else None
    if ville == "LYON" and cp.startswith("6900"):
        a = int(cp[4:])
        return f"6938{a}" if 1 <= a <= 9 else None
    return None


def charge_poste():
    """Base officielle des codes postaux : (cp, nom) -> INSEE, par ordre de priorite."""
    p = pd.read_csv(fetch(URL_POSTE, "laposte-hexasmal.csv"), sep=";", encoding="latin-1", dtype=str)
    p = p.iloc[:, :5]
    p.columns = ["insee", "nom", "cp", "acheminement", "ligne5"]
    par_nom, par_ligne5, par_ach, par_cp = {}, {}, {}, {}
    for insee, nom, cp, ach, l5 in p.itertuples(index=False):
        par_cp.setdefault(cp, set()).add(insee)
        for d, champ in ((par_nom, nom), (par_ligne5, l5), (par_ach, ach)):
            if isinstance(champ, str) and champ.strip():
                d.setdefault((cp, norm(champ)), set()).add(insee)
    return [par_nom, par_ligne5, par_ach], par_cp


def resoudre(cp, commune, dep, dicos, par_cp, index_nom, ctx):
    n = norm(commune)
    code = plm(cp, n)
    if code:
        return code
    for d in dicos:
        cands = [c for c in d.get((cp, n), ()) if c in ctx]
        if len(cands) == 1:
            return cands[0]
    code = index_nom.get((dep, n))
    if code:
        return code
    cands = [c for c in par_cp.get(cp, ()) if c in ctx]
    return cands[0] if len(cands) == 1 else None


def charge_dnb():
    """Brevet des colleges par departement (sessions SESSIONS_DNB) : reussite et mentions B+TB."""
    d = pd.read_csv(fetch(URL_DNB, "dnb-par-etablissement.csv"), sep=";", low_memory=False, dtype={"Commune": str})
    d = d[d["Type d'etablissement"].str.upper().str.contains("COLLEGE", na=False) & d.Session.isin(SESSIONS_DNB)]
    for c in ["Presents", "Admis", "Admis Mention bien", "Admis Mention très bien"]:
        d[c] = pd.to_numeric(d[c], errors="coerce").fillna(0)
    d["dep"] = np.where(d.Commune.str.startswith("97"), d.Commune.str[:3], d.Commune.str[:2])
    g = d.groupby("dep")[["Presents", "Admis", "Admis Mention bien", "Admis Mention très bien"]].sum()
    return pd.DataFrame({
        "reussite": g.Admis / g.Presents * 100,
        "mentions": (g["Admis Mention bien"] + g["Admis Mention très bien"]) / g.Presents * 100,
    })


def ips_college(code, dep, ctx, epci_de, ips_epci, ips_dep):
    """IPS des colleges publics : commune, a defaut intercommunalite, a defaut departement.
    Renvoie (valeur, niveau) avec niveau 0 = commune, 1 = intercommunalite, 2 = departement."""
    v = ctx.get(code, {}).get("ips_college_public")
    if v is not None:
        return v, 0
    if code.startswith("751"):  # arrondissement de Paris sans valeur propre : Paris (departement 75)
        return ips_dep.get("75"), 2
    ville = "13055" if code.startswith("132") else "69123" if code.startswith("6938") else code
    e = epci_de.get(ville)
    if e and ips_epci.get(e) is not None:
        return ips_epci[e], 1
    return ips_dep.get(dep), 2


def wls(X, y, w):
    sw = np.sqrt(w)
    beta, *_ = np.linalg.lstsq(X * sw[:, None], y * sw, rcond=None)
    return beta


def wls_robuste(X, y, w):
    """Moindres carres ponderes + erreurs-types robustes (HC1)."""
    w = w / w.mean()
    XtW = X.T * w
    inv = np.linalg.pinv(XtW @ X)
    beta = inv @ (XtW @ y)
    r = y - X @ beta
    meat = (X.T * (w ** 2 * r ** 2)) @ X
    n, k = X.shape
    V = inv @ meat @ inv * n / max(1, n - k)
    return beta, np.sqrt(np.clip(np.diag(V), 0, None))


def r2w(y, yhat, w):
    ybar = np.average(y, weights=w)
    return 1 - np.sum(w * (y - yhat) ** 2) / np.sum(w * (y - ybar) ** 2)


def variance_tirage(a, n):
    ac = np.clip(a, 0.03, 0.97)
    return ac * (1 - ac) / n


def tau2_de(t, a, n):
    """Variance « vraie » des ecarts entre ecoles, au-dela du bruit binomial (moments)."""
    return max(1e-5, float(np.mean((t - a) ** 2 - variance_tirage(a, n))))


def retrecit(t, a, n, tau2):
    """Ecart retreci vers 0 (bayesien empirique) et intervalle a 95 %."""
    v = variance_tirage(a, n)
    B = tau2 / (tau2 + v)
    es = B * (t - a)
    s = np.sqrt(B * v)
    return es, es - Z95 * s, es + Z95 * s


def verdict_z(z):
    z = abs(z)
    return "net" if z >= 3 else "probable" if z >= 2 else "indiscernable"


def pearson(x, y, w=None):
    x, y = np.asarray(x, float), np.asarray(y, float)
    ok = ~(np.isnan(x) | np.isnan(y))
    if ok.sum() < 5:
        return None
    x, y = x[ok], y[ok]
    w = np.ones(len(x)) if w is None else np.asarray(w, float)[ok]
    mx, my = np.average(x, weights=w), np.average(y, weights=w)
    cov = np.average((x - mx) * (y - my), weights=w)
    return float(cov / np.sqrt(np.average((x - mx) ** 2, weights=w) * np.average((y - my) ** 2, weights=w)))


def r1(x):
    if x is None:
        return None
    x = float(x)
    return None if np.isnan(x) else round(x, 1)


def main():
    explore = "--explore" in sys.argv

    date_fichier = None
    # Date réelle du fichier : en-tête Last-Modified du serveur de la Sécurité routière (la
    # métadonnée data.gouv.fr restait au 01/07/2025 alors que le fichier servi date du 19/02/2026).
    try:
        req = urllib.request.Request(URL_AE, headers={"User-Agent": UA}, method="HEAD")
        h = urllib.request.urlopen(req, timeout=60).headers
        lm, taille = h.get("Last-Modified"), h.get("Content-Length")
        cache_ae = CACHE / "auto-ecoles.csv"
        # Le cache doit être le fichier servi (même taille), sinon la date ne le décrit pas.
        if cache_ae.exists() and taille and int(taille) != cache_ae.stat().st_size:
            print("   (cache auto-ecoles.csv différent du fichier en ligne : vider le cache pour rafraîchir)")
            lm = None
        if lm:
            from email.utils import parsedate_to_datetime
            date_fichier = parsedate_to_datetime(lm).date().isoformat()
    except Exception as e:
        print(f"   (en-tête Last-Modified indisponible : {e})")
    try:
        if date_fichier:
            raise StopIteration
        req = urllib.request.Request(f"https://www.data.gouv.fr/api/1/datasets/{DATASET}/", headers={"User-Agent": UA})
        ds = json.load(urllib.request.urlopen(req, timeout=60))
        res = next(r for r in ds["resources"] if r["format"] == "csv")
        date_fichier = (res.get("last_modified") or "")[:10] or None
    except StopIteration:
        pass
    except Exception as e:  # metadonnee de confort : on continue sans
        print(f"   (date du fichier indisponible : {e})")

    # 1. Auto-ecoles ------------------------------------------------------------------
    raw = pd.read_csv(fetch(URL_AE, "auto-ecoles.csv"), sep=";", encoding="utf-8-sig", dtype=str)
    df = pd.DataFrame({
        "id": raw.raf_numero.str.strip(),
        "nom": raw.aue_raisonsociale.fillna("").str.replace(r"\s+", " ", regex=True).str.strip(),
        "cp": raw.aue_codepostal.fillna("").str.strip(),
        "commune_brute": raw.aue_commune.fillna(""),
        "dep": raw.dpt_id.map(norm_dep),
        "n": num(raw.B_nombre_1pra),
        "t": num(raw.B_taux_1pra),
    })
    df["en_ligne"] = raw.raf_numero.str.contains("_", na=False) | (raw.aue_enligne_flag.str.upper() == "TRUE")
    df["f"] = 0
    for col, bit, _ in FLAGS:
        df["f"] |= np.where(raw[col].str.upper() == "TRUE", bit, 0)
    print(f"   {len(df)} auto-ecoles, {int(df.t.notna().sum())} avec un taux B publie")

    deps_geo = {d["code"]: d["nom"] for d in json.loads(fetch(URL_DEPS, "departements.json").read_text(encoding="utf-8"))}
    df = df[df.n.notna() & df.t.notna() & (df.n >= MIN_N) & df.dep.isin(deps_geo)].copy()
    phys = ~df.en_ligne

    # 2. Rattachement communal --------------------------------------------------------
    ctx = {}
    for f in sorted((ATLAS / "communes").glob("*.json")):
        ctx.update(json.loads(f.read_text(encoding="utf-8")))
    idx = json.loads((ATLAS / "territoires-index.json").read_text(encoding="utf-8"))
    index_nom = {}
    for code, nom, dep in idx["communes"]:
        index_nom.setdefault((dep, norm(nom)), code)
    centres = {}
    for url, name in ((URL_CENTRES, "communes-centres.json"), (URL_ARRDTS, "arrondissements-centres.json")):
        for c in json.loads(fetch(url, name).read_text(encoding="utf-8")):
            if c.get("centre"):
                lon, lat = c["centre"]["coordinates"]
                centres[c["code"]] = (c["nom"], round(lat, 4), round(lon, 4))
    dicos, par_cp = charge_poste()
    df["insee"] = None
    df.loc[phys, "insee"] = [
        resoudre(r.cp, r.commune_brute, r.dep, dicos, par_cp, index_nom, ctx) for r in df[phys].itertuples()
    ]
    manquantes = df[phys & df.insee.isna()]
    print(f"   rattachement communal : {1 - len(manquantes) / phys.sum():.1%} des ecoles physiques "
          f"({len(manquantes)} sans commune)")
    if len(manquantes):
        print("     ex. :", list(manquantes.commune_brute.head(8)))

    # 3. Contexte communal ------------------------------------------------------------
    atlas_deps = {r["code"]: r for r in json.loads((ATLAS / "departements.json").read_text(encoding="utf-8"))}
    ips_dep = {c: r.get("ips_college_public") for c, r in atlas_deps.items()}
    ips_epci = {r["code"]: r.get("ips_college_public") for r in json.loads((ATLAS / "epci.json").read_text(encoding="utf-8"))}
    epci_de = {r["code"]: r["codeEpci"] for r in json.loads(EPCI_MAP.read_text(encoding="utf-8")) if r.get("codeEpci")}
    toutes = sorted({v for spec in SPECS.values() for v in spec})
    for v in toutes:
        if v == "lpop":
            df[v] = [np.log(max(ctx[c]["pop"], 50)) if c in ctx and ctx[c].get("pop") else np.nan for c in df.insee]
        elif v == "ips_college":
            vals = [ips_college(c, d, ctx, epci_de, ips_epci, ips_dep) if isinstance(c, str) else (None, None)
                    for c, d in zip(df.insee, df.dep)]
            df[v] = [x[0] for x in vals]
            df["ips_niveau"] = [x[1] for x in vals]
        else:
            df[v] = [ctx[c].get(v) if c in ctx else np.nan for c in df.insee]
        df[v] = pd.to_numeric(df[v], errors="coerce")

    # 4. Attendus --------------------------------------------------------------------
    taux_national = float(np.average(df.t, weights=df.n))
    est = df[phys & (df.n >= MIN_N_MODELE)]
    dep_moy = (est.t * est.n).groupby(est.dep).sum() / est.n.groupby(est.dep).sum()
    df["a0"] = taux_national
    df["a1"] = df.dep.map(dep_moy).fillna(taux_national)

    def ajuste(vars_, echantillon):
        deps = sorted(echantillon.dep.unique())
        mu, sd = echantillon[vars_].mean(), echantillon[vars_].std()

        def design(d, avec_ctx=True):
            D = pd.get_dummies(pd.Categorical(d.dep, categories=deps), drop_first=True).astype(float).values
            cols = [np.ones(len(d))]
            if avec_ctx:
                cols.append(((d[vars_] - mu) / sd).values)
            return np.column_stack(cols + [D])

        y, w = echantillon.t.values, echantillon.n.values.astype(float)
        X = design(echantillon)
        beta, se = wls_robuste(X, y, w)
        Xfe = design(echantillon, avec_ctx=False)
        r2_dep = r2w(y, Xfe @ wls(Xfe, y, w), w)
        r2 = r2w(y, X @ beta, w)
        effets = []
        for j, v in enumerate(vars_):
            lab, variation, pas = EFFETS[v]
            k = pas / sd[v] * 100  # coefficient standardise -> points pour la variation parlante
            effets.append({"id": v, "label": lab, "variation": variation, "effet": r1(beta[1 + j] * k),
                           "lo": r1((beta[1 + j] - Z95 * se[1 + j]) * k), "hi": r1((beta[1 + j] + Z95 * se[1 + j]) * k),
                           "verdict": verdict_z(beta[1 + j] / se[1 + j]) if se[1 + j] > 0 else "indiscernable"})
        return {"deps": deps, "design": design, "beta": beta, "r2": r2, "r2_dep": r2_dep, "effets": effets}

    avec_ctx = phys & df.insee.notna()
    if explore:
        # Echantillon commun a toutes les specifications, pour comparer les R2 a l'identique.
        commun = df[avec_ctx & df[toutes].notna().all(axis=1) & (df.n >= MIN_N_MODELE)]
        print(f"   niveaux de l'IPS utilise : {df[avec_ctx].ips_niveau.value_counts().sort_index().to_dict()}")
        for nom_spec, vars_ in SPECS.items():
            m = ajuste(vars_, commun)
            print(f"\n== {nom_spec} : n={len(commun)}  R2 dep={m['r2_dep']:.3f}  R2 complet={m['r2']:.3f}")
            for e in m["effets"]:
                print(f"   {e['label']:36s} {e['effet']:+6.1f} pts [{e['lo']:+.1f} ; {e['hi']:+.1f}]  {e['verdict']}  ({e['variation']})")
        return

    vars_ = SPECS[SPEC]
    ok = avec_ctx & df[vars_].notna().all(axis=1)
    est2 = df[ok & (df.n >= MIN_N_MODELE)]
    modele = ajuste(vars_, est2)
    predictible = ok & df.dep.isin(modele["deps"])
    df["a2"] = df.a1
    df.loc[predictible, "a2"] = np.clip(modele["design"](df[predictible]) @ modele["beta"], 0.03, 0.97)
    # mode : 2 = departement + commune, 1 = departement (ecole en ligne), 0 = departement (commune inconnue)
    df["m"] = np.where(predictible, 2, np.where(df.en_ligne, 1, 0))
    print(f"   modele {SPEC} : n={len(est2)}, R2 departement={modele['r2_dep']:.3f}, complet={modele['r2']:.3f}")
    for e in modele["effets"]:
        print(f"     {e['label']:36s} {e['effet']:+.1f} pts ({e['verdict']})")

    # Ecarts retrecis et intervalles
    tau2_1 = tau2_de(est.t.values, df.loc[est.index, "a1"].values, est.n.values)
    tau2_2 = tau2_de(est2.t.values, df.loc[est2.index, "a2"].values, est2.n.values)
    df["e1"], df["lo1"], df["hi1"] = retrecit(df.t.values, df.a1.values, df.n.values, tau2_1)
    df["e2"], df["lo2"], df["hi2"] = retrecit(df.t.values, df.a2.values, df.n.values, tau2_2)
    print(f"   ecart-type des ecarts propres aux ecoles : {np.sqrt(tau2_2) * 100:.1f} pts (departement seul : {np.sqrt(tau2_1) * 100:.1f})")

    # 5a. Decomposition des ecarts (sur l'echantillon d'estimation) --------------------
    e = df.loc[est2.index]
    w = e.n.values.astype(float)
    var_tot = float(np.average((e.t - np.average(e.t, weights=w)) ** 2, weights=w))
    resid = float(np.average((e.t - e.a2) ** 2, weights=w))
    bruit = float(np.average(variance_tirage(e.a2.values, e.n.values), weights=w))
    decomposition = {
        "departement": r1(modele["r2_dep"] * 100),
        "commune": r1((modele["r2"] - modele["r2_dep"]) * 100),
        "ecole": r1(max(0.0, resid - bruit) / var_tot * 100),
        "hasard": r1(min(bruit, resid) / var_tot * 100),
    }
    print("   decomposition :", decomposition)

    # 5b. Leviers a contexte egal (regression jointe sur l'ecart au modele complet) ----
    ybar = (e.t - e.a2).values * 100
    X = [np.ones(len(e))]
    noms = []
    for col, bit, lab in FLAGS:
        X.append(((e.f.values & bit) > 0).astype(float))
        noms.append((f"f{bit}", lab, int(((e.f.values & bit) > 0).sum())))
    X.append((e.n.values < 50).astype(float))
    noms.append(("vol_petit", "Moins de 50 candidats (vs 50 à 149)", int((e.n < 50).sum())))
    X.append((e.n.values >= 150).astype(float))
    noms.append(("vol_grand", "150 candidats et plus (vs 50 à 149)", int((e.n >= 150).sum())))
    beta, se = wls_robuste(np.column_stack(X), ybar, w)
    leviers = []
    for j, (id_, lab, n_oui) in enumerate(noms, start=1):
        leviers.append({"id": id_, "label": lab, "effet": r1(beta[j]), "lo": r1(beta[j] - Z95 * se[j]),
                        "hi": r1(beta[j] + Z95 * se[j]), "verdict": verdict_z(beta[j] / se[j]), "n": n_oui})
        print(f"   levier {lab:40s} {beta[j]:+.1f} pts (z={beta[j] / se[j]:+.1f}, n={n_oui})")

    # 5c. En ligne vs physique (attendu = departement pour les deux) --------------------
    ech = df[df.n >= MIN_N_MODELE]
    y1 = (ech.t - ech.a1).values * 100
    b, s = wls_robuste(np.column_stack([np.ones(len(ech)), ech.en_ligne.astype(float).values]), y1, ech.n.values.astype(float))
    en_ligne = {"effet": r1(b[1]), "lo": r1(b[1] - Z95 * s[1]), "hi": r1(b[1] + Z95 * s[1]),
                "verdict": verdict_z(b[1] / s[1]), "n_lignes": int(ech.en_ligne.sum()),
                "n_candidats": int(ech[ech.en_ligne].n.sum()), "enseignes": []}
    for g in (g for g in GROUPES if g.get("enLigne")):
        sub = ech[ech.en_ligne & ech.nom.str.upper().str.contains(r"\b" + g["q"] + r"\b", regex=True)]
        if len(sub) >= 5:
            bb, ss = wls_robuste(np.ones((len(sub), 1)), (sub.t - sub.a1).values * 100, sub.n.values.astype(float))
            en_ligne["enseignes"].append({"label": g["label"], "effet": r1(bb[0]), "lo": r1(bb[0] - Z95 * ss[0]),
                                          "hi": r1(bb[0] + Z95 * ss[0]), "verdict": verdict_z(bb[0] / ss[0]),
                                          "departements": len(sub), "taux": r1(np.average(sub.t, weights=sub.n) * 100)})
    print("   en ligne :", {k: v for k, v in en_ligne.items() if k != "enseignes"})

    # 6. Chiffres de synthese -----------------------------------------------------------
    q_brut = pd.qcut(est2.t.rank(method="first"), 4, labels=False)
    q_ctx = pd.qcut(df.loc[est2.index, "e2"].rank(method="first"), 4, labels=False)
    change_quart = float((q_brut != q_ctx).mean())
    saute_2 = float(((q_brut - q_ctx).abs() >= 2).mean())
    # La proportion d'ecoles nettement au-dessus / en dessous (intervalle hors de 0)
    verdicts = {"dessus": int((df.lo2 > 0).sum()), "dessous": int((df.hi2 < 0).sum())}

    # Departements : taux moyen + indicateurs pour ouvrir l'effet departement
    dnb = charge_dnb()
    tab_deps = []
    for code, g in df.groupby("dep"):
        a = atlas_deps.get(code, {})
        d = {"code": code, "nom": deps_geo.get(code, code), "taux": r1(np.average(g.t, weights=g.n) * 100),
             "ecoles": int(len(g)), "candidats": int(g.n.sum())}
        for k in ("maisons", "proprietaires", "ages65", "ouvriers", "cadres", "diplome_sup", "ips_college_public", "va_lycee"):
            d[k] = r1(a.get(k))
        d["pop"] = a.get("pop")
        d["dnb"] = r1(dnb.reussite.get(code)) if code in dnb.index else None
        tab_deps.append(d)
    tab_deps.sort(key=lambda d: d["taux"])
    grands = [d for d in tab_deps if d["ecoles"] >= 20]
    grands_metro = [d for d in grands if len(d["code"]) == 2]

    # Correlations en metropole (un departement = un point, non pondere, comme le nuage de la page)
    metro_d = [d for d in tab_deps if len(d["code"]) == 2 and d["ecoles"] >= MIN_ECOLES_DEP]
    y_dep = [d["taux"] for d in metro_d]
    def valeur(d, key):
        v = d.get(key)
        return np.nan if v is None else (np.log10(v) if key == "pop" else v)
    correlations = []
    for key, lab, unite, famille in DEP_INDICATEURS:
        x = [valeur(d, key) for d in metro_d]
        r = pearson(x, y_dep)
        rw = pearson(x, y_dep, [d["candidats"] for d in metro_d])
        correlations.append({"id": key, "label": lab, "unite": unite, "famille": famille,
                             "r": None if r is None else round(r, 2)})
        print(f"   correlation dep {lab:34s} r={r:+.2f} (pondere {rw:+.2f})")
    Xu = np.column_stack([np.ones(len(metro_d)), [valeur(d, "maisons") for d in metro_d], [valeur(d, "pop") for d in metro_d]])
    yu = np.asarray(y_dep, float)
    oku = ~np.isnan(Xu).any(axis=1)
    bu, *_ = np.linalg.lstsq(Xu[oku], yu[oku], rcond=None)
    r2_urbain = 1 - ((yu[oku] - Xu[oku] @ bu) ** 2).sum() / ((yu[oku] - yu[oku].mean()) ** 2).sum()
    print(f"   departements de metropole : {len(metro_d)} ; maisons + taille rendent compte de {r2_urbain:.1%} des ecarts")

    # Exemple positif pour l'introduction (metropole) : nettement sous la moyenne nationale
    # en brut, nettement au-dessus de son attendu, volume solide. Jamais d'exemple negatif
    # nomme dans le texte : les ecoles sous l'attendu restent dans l'outil, avec leur intervalle.
    metro = df.dep.str.len() == 2
    exemple = None
    for sous, n_min in ((0.05, 150), (0.03, 100), (0.0, 80)):  # du plus parlant au plus permissif
        cand = df[metro & (df.m == 2) & (df.t <= taux_national - sous) & (df.lo2 > 0) & (df.n >= n_min)]
        if len(cand):
            break
    if len(cand):
        x = cand.sort_values("e2", ascending=False).iloc[0]
        exemple = {"id": x.id, "nom": x.nom, "commune": centres.get(x.insee, (x.commune_brute,))[0], "dep": x.dep,
                   "dep_nom": deps_geo.get(x.dep, x.dep), "t": r1(x.t * 100), "a1": r1(x.a1 * 100),
                   "a2": r1(x.a2 * 100), "e2": r1(x.e2 * 100), "n": int(x.n)}

    groupes = []
    for g in GROUPES:
        mask = df.nom.str.upper().str.contains(r"\b" + g["q"] + r"\b", regex=True)
        if g.get("exclude"):
            mask &= ~df.nom.str.upper().str.contains(r"\b" + g["exclude"] + r"\b", regex=True)
        if mask.sum() >= 8:
            groupes.append({**g, "n": int(mask.sum())})

    # 7. Lignes -------------------------------------------------------------------------
    cols = ["id", "nom", "commune", "insee", "dep", "m", "n", "t", "a1", "a2", "e1", "lo1", "hi1", "e2", "lo2", "hi2",
            "f", "lat", "lon"]
    rows = []
    for x in df.sort_values(["dep", "nom"]).itertuples():
        if x.en_ligne:
            commune, lat, lon = deps_geo.get(x.dep, x.dep), None, None
        else:
            commune, lat, lon = centres.get(x.insee, (x.commune_brute.title(), None, None))
        rows.append([x.id, x.nom, commune, x.insee, x.dep, int(x.m), int(x.n), r1(x.t * 100), r1(x.a1 * 100),
                     r1(x.a2 * 100), r1(x.e1 * 100), r1(x.lo1 * 100), r1(x.hi1 * 100), r1(x.e2 * 100),
                     r1(x.lo2 * 100), r1(x.hi2 * 100), int(x.f), lat, lon])

    # Ce que le modele sait de chaque commune (affiche sur la fiche d'une ecole)
    com_cols = ["pop", "diplome_sup", "ages65", "proprietaires", "ips", "ips_niveau"]
    com_rows = {}
    for x in df[df.m == 2].drop_duplicates("insee").itertuples():
        c = ctx.get(x.insee, {})
        com_rows[x.insee] = [c.get("pop"), r1(c.get("diplome_sup")), r1(c.get("ages65")), r1(c.get("proprietaires")),
                             r1(x.ips_college), None if pd.isna(x.ips_niveau) else int(x.ips_niveau)]
    niveaux = df[df.m == 2].ips_niveau.value_counts().to_dict()

    out = {
        "titre": "La meilleure auto-école est-elle celle qui a le meilleur taux ?",
        "genere": date.today().isoformat(),
        "source": {"label": "Sécurité routière, liste des auto-écoles et taux de réussite au permis de conduire (data.gouv.fr)",
                   "url": URL_DATASET, "date_fichier": date_fichier},
        "sources_contexte": [
            {"label": "Insee, recensement de la population 2023 (population, diplômes, âges, logement), via l'atlas Outsiders",
             "url": "https://www.insee.fr/fr/statistiques/9005956"},
            {"label": "Éducation nationale, indice de position sociale (IPS) des collèges, via l'atlas Outsiders",
             "url": URL_IPS},
            {"label": "Éducation nationale, diplôme national du brevet par établissement (sessions 2019 et 2021)",
             "url": URL_DNB_PAGE},
            {"label": "Éducation nationale, valeur ajoutée des lycées (IVAL), via l'atlas Outsiders", "url": URL_IVAL},
            {"label": "La Poste, base officielle des codes postaux (rattachement des adresses aux communes)",
             "url": "https://www.data.gouv.fr/fr/datasets/base-officielle-des-codes-postaux/"},
        ],
        "stats": {
            "ecoles": int(len(df)), "physiques": int(phys.sum()), "lignes_en_ligne": int(df.en_ligne.sum()),
            "candidats": int(df.n.sum()), "taux_national": r1(taux_national * 100),
            "rattachement": r1((1 - len(manquantes) / phys.sum()) * 100),
            "r2_departement": r1(modele["r2_dep"] * 100), "r2_complet": r1(modele["r2"] * 100),
            "ecart_type_ecoles": r1(np.sqrt(tau2_2) * 100),
            "change_quart": r1(change_quart * 100), "saute_deux_quarts": r1(saute_2 * 100),
            "verdicts": verdicts, "min_n": MIN_N, "min_n_modele": MIN_N_MODELE, "n_modele": int(len(est2)),
            "dep_min": grands[0] if grands else None, "dep_max": grands[-1] if grands else None,
            "dep_min_metro": grands_metro[0] if grands_metro else None,
            "ips_niveaux": {IPS_NIVEAUX[int(k)]: int(v) for k, v in niveaux.items()},
            "deps_correlation": len(metro_d), "min_ecoles_dep": MIN_ECOLES_DEP,
            "r2_dep_urbain": r1(r2_urbain * 100),
        },
        "decomposition": decomposition,
        "effets_contexte": modele["effets"],
        "leviers": leviers,
        "en_ligne": en_ligne,
        "departements": tab_deps,
        "correlations_dep": correlations,
        "exemple": exemple,
        "groupes": groupes,
        "flags": [{"bit": bit, "label": lab} for _, bit, lab in FLAGS],
        "ips_niveaux": IPS_NIVEAUX,
        "communes": {"cols": com_cols, "rows": com_rows},
        "cols": cols,
        "rows": rows,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"   -> {OUT.relative_to(ROOT)} ({OUT.stat().st_size / 1e6:.2f} Mo, {len(rows)} lignes, {len(com_rows)} communes)")
    print("   stats :", {k: v for k, v in out["stats"].items() if k not in ("dep_min", "dep_max", "dep_min_metro")})
    print("   exemple :", exemple)


if __name__ == "__main__":
    main()
