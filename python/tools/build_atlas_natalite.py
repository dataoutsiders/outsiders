# -*- coding: utf-8 -*-
"""
Atlas - taux de natalité par commune.

Naissances domiciliées (INSEE état civil, base « Naissances 2008-2025 », géographie au
1er janvier 2026, fichier EC_NAIS_COM.xlsx, onglets COM et ARM) : moyenne annuelle des
5 dernières années disponibles (2021-2025), rapportée à la population municipale 2023
(base RP 2023 DS_RP_POPULATION_PRINC_2023, AGE=_T, SEX=_T, équivalent exact de P21_POP),
exprimée pour 1000 habitants.

  taux = (somme naissances sur N années) / N / population * 1000

Agrégat département/EPCI sur les effectifs bruts. Relancer build_territoires_index.py ensuite.
"""
import io
import json
import time
import zipfile
import urllib.request
from pathlib import Path
import pandas as pd
from rp2023 import lire, decrire, communes_et_arrondissements, communes_seules, UA, DATA

H = UA
ROOT = Path(__file__).resolve().parents[2]
ATLAS = ROOT / "frontend" / "public" / "data" / "atlas"
COMMUNES = ATLAS / "communes"
EPCI_MAP = ROOT / "python" / "data" / "municipales" / "communes-epci.json"
# Depuis l'édition 2008-2025, la base communale des naissances n'est plus diffusée qu'en XLSX.
URL_NAIS = "https://www.insee.fr/fr/statistiques/fichier/1893255/base_naissances_2008-2025_geo2026_xlsx.zip"
ZIP_NAIS = DATA / "base_naissances_2008-2025_geo2026_xlsx.zip"
SERIES_POP = {"POP": {"AGE": "_T", "SEX": "_T", "RP_MEASURE": "POP"}}
KEY = "natalite"
N_ANNEES = 5  # fenêtre de lissage (dernières années disponibles)


def fetch(url, tries=4, timeout=300):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=timeout) as r:
                return r.read()
        except Exception as e:
            print("   retry", i + 1, e)
            time.sleep(3)
    raise RuntimeError(url)


def lire_naissances():
    """Naissances par commune (onglet COM) et arrondissement municipal (onglet ARM), une colonne par année."""
    raw = ZIP_NAIS.read_bytes() if ZIP_NAIS.exists() else fetch(URL_NAIS)
    zf = zipfile.ZipFile(io.BytesIO(raw))
    member = next(n for n in zf.namelist() if n.lower().endswith(".xlsx"))
    blob = zf.read(member)
    out = {}
    for onglet in ("COM", "ARM"):
        df = pd.read_excel(io.BytesIO(blob), sheet_name=onglet, dtype=str)
        df = df.rename(columns={df.columns[0]: "GEO"}).set_index("GEO")
        annees = [c for c in df.columns if str(c).strip().isdigit()]
        # « vm » (valeur manquante, dont commune rétablie) et « so » (sans objet) -> NaN
        out[onglet] = df[annees].apply(pd.to_numeric, errors="coerce").rename(columns=lambda c: int(str(c).strip()))
    return out, member


def dep_of(c):
    c = str(c)
    return c[:3] if c[:2] in ("97", "98") else c[:2]


# ---- Naissances --------------------------------------------------------
print("Lecture base naissances 2008-2025, géographie 2026 (INSEE)...")
nais_tabs, member = lire_naissances()
years = sorted(nais_tabs["COM"].columns)
window = years[-N_ANNEES:]
print(f"   {member} | années dispo: {years[0]}..{years[-1]} | fenêtre retenue: {window}")
n_years = len(window)
# Somme sur la fenêtre. Pour les rares communes rétablies (« vm » sur une partie des années), les
# années manquantes sont remplacées par la moyenne des années connues (sinon le taux serait sous-estimé).
nais_com = (nais_tabs["COM"][window].mean(axis=1) * n_years).dropna()   # communes, dont 75056 / 13055 / 69123 entiers
nais_arm = (nais_tabs["ARM"][window].mean(axis=1) * n_years).dropna()   # arrondissements municipaux (et 751XX... non localisés)
incomplets = int(nais_tabs["COM"][window].isna().any(axis=1).sum())
print(f"   {incomplets} communes rétablies avec des années manquantes (complétées par la moyenne des années connues)")
print(f"   {len(nais_com)} communes et {len(nais_arm)} arrondissements avec naissances")
print(f"   ex. brut: 75056={nais_com.get('75056')}, 23096={nais_com.get('23096')}, "
      f"arr. Paris 75101={nais_arm.get('75101')}")

# ---- Population (dénominateur) -----------------------------------------
print("Lecture base RP 2023 population (INSEE)...")
decrire("population", SERIES_POP)
tab = lire("population", SERIES_POP)
pop_com = communes_seules(tab)["POP"].fillna(0)
pop_tous = communes_et_arrondissements(tab)["POP"].fillna(0)
print(f"   {len(pop_tous)} communes et arrondissements avec population")

# ---- Taux par commune + agrégats --------------------------------------
# Niveau commune : communes et arrondissements. Sommes département / EPCI sur les communes seules
# (Paris, Lyon, Marseille entiers), sans ajouter une seconde fois les arrondissements.
nais_tous = pd.concat([nais_com, nais_arm])
com_vals, dn, dp, en, ep = {}, {}, {}, {}, {}
comm_epci = {c["code"]: c.get("codeEpci") for c in json.loads(EPCI_MAP.read_text(encoding="utf-8"))}
for code in set(nais_tous.index) & set(pop_tous.index):
    n, p = float(nais_tous[code]), float(pop_tous[code])
    if p > 0:
        com_vals[code] = round(n / n_years / p * 1000, 1)
for code in set(nais_com.index) & set(pop_com.index):
    n, p = float(nais_com[code]), float(pop_com[code])
    if p <= 0:
        continue
    d = dep_of(code)
    dn[d] = dn.get(d, 0) + n
    dp[d] = dp.get(d, 0) + p
    e = comm_epci.get(code)
    if e:
        en[e] = en.get(e, 0) + n
        ep[e] = ep.get(e, 0) + p
dep_vals = {d: round(dn[d] / n_years / dp[d] * 1000, 1) for d in dn if dp[d] > 0}
ep_vals = {e: round(en[e] / n_years / ep[e] * 1000, 1) for e in en if ep[e] > 0}
print(f"   {len(com_vals)} communes appariées, {len(dep_vals)} dépts, {len(ep_vals)} EPCI")

# ---- Fusion atlas ------------------------------------------------------
print("Fusion dans l'atlas...")
for fp in sorted(COMMUNES.glob("*.json")):
    data = json.loads(fp.read_text(encoding="utf-8"))
    changed = False
    for code in data:
        if code in com_vals:
            data[code][KEY] = com_vals[code]
            changed = True
    if changed:
        fp.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

deps = json.loads((ATLAS / "departements.json").read_text(encoding="utf-8"))
for d in deps:
    if d["code"] in dep_vals:
        d[KEY] = dep_vals[d["code"]]
(ATLAS / "departements.json").write_text(json.dumps(deps, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

epci = json.loads((ATLAS / "epci.json").read_text(encoding="utf-8"))
for e in epci:
    if e["code"] in ep_vals:
        e[KEY] = ep_vals[e["code"]]
(ATLAS / "epci.json").write_text(json.dumps(epci, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

print(f"-> natalité fusionnée (fenêtre {window[0]}-{window[-1]}, pour 1000 hab.)")
print(f"   ex. national : Seine-St-Denis(93)={dep_vals.get('93')}, Paris(75)={dep_vals.get('75')}, "
      f"Creuse(23)={dep_vals.get('23')}")
