# -*- coding: utf-8 -*-
"""
Fiche territoire : échelles intercommunalité et région, et extraits légers des dossiers.

Émet (frontend/public/data/) :
  - atlas/epci-communes.json
        {"<siren>": {"dep": "<département principal>", "deps": [...], "communes": ["<code>", ...]}}
        (communes rangées par population décroissante)
        Appartenance des communes aux intercommunalités (python/data/municipales/communes-epci.json,
        géographie geo.api.gouv.fr déjà utilisée par toute la chaîne Atlas). Département principal =
        celui qui compte le plus d'habitants de l'intercommunalité (RP 2023, champ `pop` de l'Atlas).
  - atlas/regions.json
        {"sources": {<indicateur>: <origine de la valeur>}, "regions": [{code, nom, deps, pop, <indicateurs>}]}
        Valeurs régionales, indicateur par indicateur (voir METHODES ci-dessous) : valeur OFFICIELLE
        de la source quand elle existe au niveau région (Insee Filosofi, recensement),
        sinon recalculée depuis les numérateurs et dénominateurs, avec la même définition qu'au
        niveau département. Jamais de moyenne de médianes.
  - territoires/auto-ecoles-departements.json
        Extrait départemental du dossier Auto-écoles (le fichier complet pèse plus de 1 Mo).

Contrôle : chaque méthode régionale est d'abord appliquée aux départements et comparée aux valeurs
de atlas/departements.json (écart maximal affiché), pour vérifier qu'elle reproduit la définition
départementale de l'Atlas.

À lancer APRÈS les build_atlas_*.py et build_ecole.py, à relancer après build_auto_ecoles.py, et AVANT
build_territoires_index.py (qui ajoute intercommunalités et régions à l'index de recherche).
Hors-ligne sauf les statistiques DVF (30 Mo, mises en cache dans _cache_territoires/).
"""
import io
import json
import re
import time
import unicodedata
import zipfile
import urllib.request
from pathlib import Path

import pandas as pd

from rp2023 import lire, DATA, UA

ROOT = Path(__file__).resolve().parents[2]
PUB = ROOT / "frontend" / "public" / "data"
ATLAS = PUB / "atlas"
SHOW = PUB / "showcases"
OUT_TERR = PUB / "territoires"
EPCI_MAP = ROOT / "python" / "data" / "municipales" / "communes-epci.json"
SURNAMES = PUB / "onomastics" / "surnames.tsv"
MUNI = ROOT / "python" / "data" / "municipales" / "municipales-2026.csv"
ETABS = SHOW / "etablissements.tsv"
CACHE = Path(__file__).resolve().parent / "_cache_territoires"
FILOSOFI = Path(__file__).resolve().parent / "_cache_filosofi" / "DS_FILOSOFI_CC_2023_data.csv"
DVF_URL = "https://data-pipeline-open.s3.sbg.io.cloud.ovh.net/dvf/stats_whole_period.csv"
ZIP_NAIS = DATA / "base_naissances_2008-2025_geo2026_xlsx.zip"

# Régions au 1er janvier 2026 (code officiel géographique de l'Insee).
REGIONS = [
    ("11", "Île-de-France", ["75", "77", "78", "91", "92", "93", "94", "95"]),
    ("24", "Centre-Val de Loire", ["18", "28", "36", "37", "41", "45"]),
    ("27", "Bourgogne-Franche-Comté", ["21", "25", "39", "58", "70", "71", "89", "90"]),
    ("28", "Normandie", ["14", "27", "50", "61", "76"]),
    ("32", "Hauts-de-France", ["02", "59", "60", "62", "80"]),
    ("44", "Grand Est", ["08", "10", "51", "52", "54", "55", "57", "67", "68", "88"]),
    ("52", "Pays de la Loire", ["44", "49", "53", "72", "85"]),
    ("53", "Bretagne", ["22", "29", "35", "56"]),
    ("75", "Nouvelle-Aquitaine", ["16", "17", "19", "23", "24", "33", "40", "47", "64", "79", "86", "87"]),
    ("76", "Occitanie", ["09", "11", "12", "30", "31", "32", "34", "46", "48", "65", "66", "81", "82"]),
    ("84", "Auvergne-Rhône-Alpes", ["01", "03", "07", "15", "26", "38", "42", "43", "63", "69", "73", "74"]),
    ("93", "Provence-Alpes-Côte d'Azur", ["04", "05", "06", "13", "83", "84"]),
    ("94", "Corse", ["2A", "2B"]),
    ("01", "Guadeloupe", ["971"]),
    ("02", "Martinique", ["972"]),
    ("03", "Guyane", ["973"]),
    ("04", "La Réunion", ["974"]),
    ("06", "Mayotte", ["976"]),
]
REG_OF_DEP = {d: code for code, _, deps in REGIONS for d in deps}

# Origine de chaque valeur régionale (reprise telle quelle dans regions.json et dans la documentation).
METHODES = {
    "revenu": "officielle : Insee, Filosofi 2023, niveau de vie médian de la région (GEO_OBJECT = REG)",
    # Prix immobilier : les statistiques DVF ne publient pas d'échelle région (échelles : nation,
    # département, EPCI, commune, section) et une médiane ne s'obtient pas en combinant des médianes
    # départementales : l'indicateur n'est PAS affiché à l'échelle régionale.
    "prix_m2": "non affiché : pas de médiane régionale publiée par les statistiques DVF",
    "diplome_sup": "officielle : Insee, recensement 2023, lignes région (GEO_OBJECT = REG), même rapport qu'au département",
    "hlm": "officielle : Insee, recensement 2023, lignes région",
    "res_secondaires": "officielle : Insee, recensement 2023, lignes région",
    "vacants": "officielle : Insee, recensement 2023, lignes région",
    "proprietaires": "officielle : Insee, recensement 2023, lignes région",
    "maisons": "officielle : Insee, recensement 2023, lignes région",
    "jeunes": "officielle : Insee, recensement 2023, lignes région",
    "ages65": "officielle : Insee, recensement 2023, lignes région",
    "cadres": "officielle : Insee, recensement 2023 (exploitation complémentaire), lignes région",
    "intermediaires": "officielle : Insee, recensement 2023 (exploitation complémentaire), lignes région",
    "employes": "officielle : Insee, recensement 2023 (exploitation complémentaire), lignes région",
    "ouvriers": "officielle : Insee, recensement 2023 (exploitation complémentaire), lignes région",
    "natalite": "calculée : naissances domiciliées 2021-2025 des communes de la région (état civil) / population "
                "2023 de ces communes, comme au département",
    "idp_candidats": "calculée : part des noms classés « diversité » parmi les candidats municipaux 2026 au nom "
                     "reconnu de la région (au moins 50), comme au département",
    "ips_ecole_public": "calculée : moyenne des IPS des écoles publiques de la région, comme au département "
                        "(pas de valeur régionale publiée par l'Éducation nationale)",
    "ips_college_public": "calculée : moyenne des IPS des collèges publics de la région, comme au département",
    "ips_lycee_public": "calculée : moyenne des IPS des lycées publics de la région, comme au département",
    "va_lycee": "calculée : moyenne des valeurs ajoutées des lycées de la région, comme au département",
    "pop": "officielle : Insee, recensement 2023, population municipale de la région",
}


def dep_of(c):
    c = str(c)
    return c[:3] if c[:2] in ("97", "98") else c[:2]


def ecart_max(calc, ref, cle):
    """Écart maximal entre une valeur départementale recalculée et celle de l'Atlas."""
    ecarts = [abs(calc[d] - r[cle]) for d, r in ref.items() if d in calc and r.get(cle) is not None]
    return (max(ecarts) if ecarts else None), len(ecarts)


deps_atlas = {d["code"]: d for d in json.loads((ATLAS / "departements.json").read_text(encoding="utf-8"))}
controles = []

# ---------------------------------------------------------------------------
# 1. Intercommunalités : appartenance des communes, département principal
# ---------------------------------------------------------------------------
print("Intercommunalités : appartenance des communes...")
pop_com = {}
for f in sorted((ATLAS / "communes").glob("*.json")):
    for code, rec in json.loads(f.read_text(encoding="utf-8")).items():
        if rec.get("pop"):
            pop_com[code] = rec["pop"]
membres = {}
for c in json.loads(EPCI_MAP.read_text(encoding="utf-8")):
    e = c.get("codeEpci")
    if e:
        membres.setdefault(e, []).append(c["code"])
epci_atlas = {e["code"] for e in json.loads((ATLAS / "epci.json").read_text(encoding="utf-8"))}
epci_out = {}
for e, coms in sorted(membres.items()):
    poids = {}
    for c in coms:
        poids[dep_of(c)] = poids.get(dep_of(c), 0) + pop_com.get(c, 0)
    deps = sorted(poids, key=lambda d: (-poids[d], d))
    # Communes rangées de la plus peuplée à la moins peuplée (ordre d'affichage de la fiche).
    epci_out[e] = {"dep": deps[0], "deps": deps,
                   "communes": sorted(coms, key=lambda c: (-pop_com.get(c, 0), c))}
manquants = epci_atlas - set(epci_out)
(ATLAS / "epci-communes.json").write_text(
    json.dumps(epci_out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print(f"   -> epci-communes.json : {len(epci_out)} intercommunalités, "
      f"{sum(len(v['communes']) for v in epci_out.values())} communes ; "
      f"{len(manquants)} intercommunalités de l'Atlas sans liste de communes")

# ---------------------------------------------------------------------------
# 2. Régions
# ---------------------------------------------------------------------------
reg = {code: {"code": code, "nom": nom, "deps": deps} for code, nom, deps in REGIONS}

# 2a. Revenu : médiane officielle Filosofi 2023 au niveau région
print("Revenu (Filosofi 2023, niveau région)...")
fi = pd.read_csv(FILOSOFI, sep=";", dtype=str, usecols=["GEO", "GEO_OBJECT", "FILOSOFI_MEASURE", "OBS_VALUE"])
fi = fi[(fi.FILOSOFI_MEASURE == "MED_SL") & fi.OBS_VALUE.notna()]
for r in fi[fi.GEO_OBJECT == "REG"].itertuples():
    if r.GEO in reg:
        reg[r.GEO]["revenu"] = int(round(float(r.OBS_VALUE)))
dep_fi = {r.GEO: int(round(float(r.OBS_VALUE))) for r in fi[fi.GEO_OBJECT == "DEP"].itertuples()}
controles.append(("revenu", *ecart_max(dep_fi, deps_atlas, "revenu")))

# 2b. Prix immobilier : statistiques DVF. Pas d'échelle région publiée : seul le contrôle départemental
# est fait ici, la région reste sans prix (voir METHODES).
print("Prix immobilier (statistiques DVF, échelle région)...")
CACHE.mkdir(exist_ok=True)
dvf_fichier = CACHE / "stats_whole_period.csv"
if not dvf_fichier.exists():
    for i in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(DVF_URL, headers=UA), timeout=300) as r:
                dvf_fichier.write_bytes(r.read())
            break
        except Exception as ex:
            print("   retry", i + 1, ex)
            time.sleep(3)
dvf = pd.read_csv(dvf_fichier, sep=",", dtype=str, usecols=["echelle_geo", "code_geo", "med_prix_m2_whole_apt_maison"])
dvf["v"] = pd.to_numeric(dvf["med_prix_m2_whole_apt_maison"], errors="coerce")
dvf = dvf.dropna(subset=["v"])
print("   échelles présentes :", sorted(dvf.echelle_geo.unique()))
for r in dvf[dvf.echelle_geo == "region"].itertuples():
    code = str(r.code_geo).zfill(2)
    if code in reg:
        reg[code]["prix_m2"] = int(round(r.v))
dep_px = {r.code_geo: round(r.v) for r in dvf[dvf.echelle_geo == "departement"].drop_duplicates("code_geo").itertuples()}
controles.append(("prix_m2", *ecart_max(dep_px, deps_atlas, "prix_m2")))

# 2c. Recensement 2023 : lignes région (et département pour le contrôle). Séries identiques à
# build_atlas_insee.py, build_atlas_logement.py, build_atlas_demo.py, build_atlas_pcs.py.
RP = {
    "diplomes": ({
        "nscol": {"AGE": "Y_GE15", "EDUC": "_T", "RP_MEASURE": "POP"},
        "sup2": {"AGE": "Y_GE15", "EDUC": "500_RP", "RP_MEASURE": "POP"},
        "sup34": {"AGE": "Y_GE15", "EDUC": "600_RP", "RP_MEASURE": "POP"},
        "sup5": {"AGE": "Y_GE15", "EDUC": "700_RP", "RP_MEASURE": "POP"},
    }, lambda t: {"diplome_sup": (t.sup2 + t.sup34 + t.sup5, t.nscol)}),
    "logement": ({
        "LOG": {"OCS": "_T", "RP_MEASURE": "DWELLINGS"},
        "RP": {"OCS": "DW_MAIN", "RP_MEASURE": "DWELLINGS"},
        "RSECOCC": {"OCS": "DW_SEC_DW_OCC", "RP_MEASURE": "DWELLINGS"},
        "LOGVAC": {"OCS": "DW_VAC", "RP_MEASURE": "DWELLINGS"},
        "MAISON": {"OCS": "_T", "TDW": "1", "RP_MEASURE": "DWELLINGS"},
        "RP_PROP": {"OCS": "DW_MAIN", "TSH": "100", "RP_MEASURE": "DWELLINGS"},
        "RP_LOCHLMV": {"OCS": "DW_MAIN", "TSH": "221", "RP_MEASURE": "DWELLINGS"},
    }, lambda t: {
        "proprietaires": (t.RP_PROP, t.RP), "hlm": (t.RP_LOCHLMV, t.RP),
        "res_secondaires": (t.RSECOCC, t.LOG), "vacants": (t.LOGVAC, t.LOG), "maisons": (t.MAISON, t.LOG),
    }),
    "population": ({
        "POP": {"AGE": "_T", "SEX": "_T", "RP_MEASURE": "POP"},
        "POP0014": {"AGE": "Y_LT15", "SEX": "_T", "RP_MEASURE": "POP"},
        "POP65P": {"AGE": "Y_GE65", "SEX": "_T", "RP_MEASURE": "POP"},
    }, lambda t: {"jeunes": (t.POP0014, t.POP), "ages65": (t.POP65P, t.POP)}),
    "emploi_comp": ({
        f"CS{k}": {"AGE": "Y15T64", "EMPSTA_ENQ": "1", "PCS": str(k), "RP_MEASURE": "POP"} for k in range(1, 7)
    }, lambda t: {
        key: (getattr(t, f"CS{k}"), sum(getattr(t, f"CS{j}") for j in range(1, 7)))
        for key, k in (("cadres", 3), ("intermediaires", 4), ("employes", 5), ("ouvriers", 6))
    }),
}
pop_reg_communes = None
for theme, (series, ratios) in RP.items():
    print(f"Recensement 2023, {theme} (lignes région et département)...")
    niveaux = ("REG", "DEP", "COM") if theme == "population" else ("REG", "DEP")
    tab = lire(theme, series, niveaux=niveaux).fillna(0)
    if theme == "population":
        pop_reg_communes = tab.xs("COM", level="GEO_OBJECT")["POP"]
    dep_calc = {}
    for (obj, geo), row in tab.iterrows():
        if obj not in ("REG", "DEP"):
            continue
        vals = {k: round(n / d * 100, 1) for k, (n, d) in ratios(row).items() if d and d > 0}
        if obj == "REG" and geo in reg:
            reg[geo].update(vals)
            if theme == "population":
                reg[geo]["pop"] = int(round(row.POP))
        elif obj == "DEP":
            for k, v in vals.items():
                dep_calc.setdefault(k, {})[geo] = v
    for k, calc in dep_calc.items():
        controles.append((k, *ecart_max(calc, deps_atlas, k)))

# 2d. Natalité : même calcul qu'au département (sommes des communes)
print("Natalité (naissances 2021-2025 / population 2023, sommes des communes)...")
zf = zipfile.ZipFile(io.BytesIO(ZIP_NAIS.read_bytes()))
blob = zf.read(next(n for n in zf.namelist() if n.lower().endswith(".xlsx")))
nais = pd.read_excel(io.BytesIO(blob), sheet_name="COM", dtype=str)
nais = nais.rename(columns={nais.columns[0]: "GEO"}).set_index("GEO")
annees = sorted(int(str(c).strip()) for c in nais.columns if str(c).strip().isdigit())
fenetre = annees[-5:]
nais = nais[[c for c in nais.columns if str(c).strip().isdigit() and int(str(c).strip()) in fenetre]]
nais = nais.apply(pd.to_numeric, errors="coerce")
nais_com = (nais.mean(axis=1) * len(fenetre)).dropna()
sn, sp, dn, dp = {}, {}, {}, {}
for code in set(nais_com.index) & set(pop_reg_communes.index):
    p = float(pop_reg_communes[code])
    if p <= 0:
        continue
    d = dep_of(code)
    dn[d] = dn.get(d, 0) + float(nais_com[code])
    dp[d] = dp.get(d, 0) + p
    r = REG_OF_DEP.get(d)
    if r:
        sn[r] = sn.get(r, 0) + float(nais_com[code])
        sp[r] = sp.get(r, 0) + p
for r in sn:
    reg[r]["natalite"] = round(sn[r] / len(fenetre) / sp[r] * 1000, 1)
controles.append(("natalite", *ecart_max(
    {d: round(dn[d] / len(fenetre) / dp[d] * 1000, 1) for d in dn}, deps_atlas, "natalite")))
print(f"   fenêtre {fenetre[0]}-{fenetre[-1]}")

# 2e. Diversité des noms des candidats municipaux 2026 : même calcul qu'au département
print("Diversité des candidats (IDP), même calcul qu'au département...")


def norm(n):
    if n is None:
        return ""
    s = unicodedata.normalize("NFD", str(n).upper().strip())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn").replace("'", " ").replace("’", " ")
    return re.sub(r"\s+", " ", s).strip()


divers, connus = set(), set()
for line in SURNAMES.read_text(encoding="utf-8").splitlines():
    if "\t" in line:
        nom, flag = line.split("\t")
        connus.add(nom)
        if flag == "1":
            divers.add(nom)
cand = pd.read_csv(MUNI, sep=";", dtype=str, encoding="utf-8", low_memory=False)
cand.columns = [c.strip('"').strip() for c in cand.columns]
fl = cand["Nom sur le bulletin de vote"].str.strip('"').map(norm).map(
    lambda n: True if n in divers else (False if n in connus else None))
com = cand["Code circonscription"].str.strip('"')
df = pd.DataFrame({"dp": com.map(dep_of), "fl": fl}).dropna(subset=["fl"])
df["fl"] = df["fl"].astype(bool)
df["rg"] = df["dp"].map(REG_OF_DEP)
for r, s in df.dropna(subset=["rg"]).groupby("rg")["fl"]:
    if s.size >= 50:
        reg[r]["idp_candidats"] = round(s.mean() * 100, 1)
controles.append(("idp_candidats", *ecart_max(
    {d: round(s.mean() * 100, 1) for d, s in df.groupby("dp")["fl"] if s.size >= 50}, deps_atlas, "idp_candidats")))

# 2f. IPS et valeur ajoutée : moyenne des établissements, comme au département (build_ecole.py)
print("IPS et valeur ajoutée (établissements, moyenne comme au département)...")
et = pd.read_csv(ETABS, sep="\t", dtype={"dep": str, "uai": str})
et["rg"] = et["dep"].map(REG_OF_DEP)
NIV = {"e": "ips_ecole_public", "c": "ips_college_public", "l": "ips_lycee_public"}
for niv, cle in NIV.items():
    sub = et[(et.niveau == niv) & (et.secteur == "pu")]
    for r, v in sub.groupby("rg")["ips"].mean().items():
        reg[r][cle] = round(float(v), 1)
    controles.append((cle, *ecart_max(sub.groupby("dep")["ips"].mean().round(1).to_dict(), deps_atlas, cle)))
lyc = et[(et.niveau == "l") & et.va.notna()]
for r, v in lyc.groupby("rg")["va"].mean().items():
    reg[r]["va_lycee"] = round(float(v), 1)
controles.append(("va_lycee", *ecart_max(lyc.groupby("dep")["va"].mean().round(1).to_dict(), deps_atlas, "va_lycee")))

regions = [reg[code] for code, _, _ in REGIONS]
(ATLAS / "regions.json").write_text(json.dumps({"sources": METHODES, "regions": regions},
                                               ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print(f"-> regions.json ({len(regions)} régions)")
for r in regions:
    absents = [k for k in METHODES if k not in r]
    print(f"   {r['code']} {r['nom']:<28} revenu={r.get('revenu')} prix={r.get('prix_m2')} "
          f"diplome={r.get('diplome_sup')} idp={r.get('idp_candidats')} | absents : {', '.join(absents) or '-'}")
print("Contrôle : méthode régionale appliquée aux départements, écart maximal avec atlas/departements.json")
for cle, e, n in controles:
    print(f"   {cle:<20} écart max {e} sur {n} départements")

# ---------------------------------------------------------------------------
# 3. Extraits légers des dossiers
# ---------------------------------------------------------------------------
print("Extrait du dossier Auto-écoles (départements)...")
OUT_TERR.mkdir(exist_ok=True)
ae = json.loads((SHOW / "auto-ecoles.json").read_text(encoding="utf-8"))
extrait = {
    "source": ae["source"],
    "taux_national": ae["stats"]["taux_national"],
    "departements": {d["code"]: {"nom": d["nom"], "taux": d["taux"], "ecoles": d["ecoles"], "candidats": d["candidats"]}
                     for d in ae["departements"]},
}
f = OUT_TERR / "auto-ecoles-departements.json"
f.write_text(json.dumps(extrait, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print(f"   -> {f.name} ({len(extrait['departements'])} départements, {f.stat().st_size / 1024:.0f} Ko)")
print("Terminé.")
