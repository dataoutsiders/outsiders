# -*- coding: utf-8 -*-
"""
Atlas, données communales par département (drill).

Émet un fichier par département : frontend/public/data/atlas/communes/<dep>.json
  = { "<code_insee>": { ips_ecole_public, ips_college_public, ips_lycee_public,
                        va_lycee, revenu, prix_m2 }, ... }

IPS/VA : repris de ecole-communes.json (communes avec établissements).
Revenu (Figaro) & prix/m² (DVF Etalab) : TOUTES les communes (pour une carte complète).
"""
import io
import re
import gzip
import json
import time
import unicodedata
import urllib.request
from pathlib import Path
import pandas as pd

H = {"User-Agent": "outsiders/1.0", "Accept-Encoding": "identity"}
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "frontend" / "public" / "data" / "atlas" / "communes"
ECOLE_COM = ROOT / "frontend" / "public" / "data" / "showcases" / "ecole-communes.json"
ECOLE_IPS = ROOT / "frontend" / "public" / "data" / "showcases" / "ecole-ips.json"
SURNAMES = ROOT / "frontend" / "public" / "data" / "onomastics" / "surnames.tsv"
MUNI = ROOT / "python" / "data" / "municipales" / "municipales-2026.csv"
OUT.mkdir(parents=True, exist_ok=True)


def fetch(url, tries=4):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=120) as r:
                return r.read()
        except Exception as e:
            print("   retry", i + 1, e)
            time.sleep(3)
    raise RuntimeError(url)


def read_csv_url(url, sep):
    raw = fetch(url)
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    return pd.read_csv(io.BytesIO(raw), sep=sep, dtype=str, encoding="utf-8", low_memory=False)


def dep_of(c):
    c = str(c)
    return c[:3] if c[:2] in ("97", "98") else c[:2]


print("Revenu (Insee Filosofi 2023)...")
from revenu_filosofi import niveaux_de_vie_medians
income = niveaux_de_vie_medians()["com"]

print("Prix DVF...")
# Statistiques DVF (data.gouv.fr, jeu « Statistiques DVF ») : fichier du 21/10/2026, ventes de juillet 2021 à juin 2026.
# L'ancienne adresse object.files.data.gouv.fr restait figée sur la livraison d'avril 2026.
dvf = read_csv_url("https://data-pipeline-open.s3.sbg.io.cloud.ovh.net/dvf/stats_whole_period.csv", ",")
dvf = dvf[dvf.echelle_geo == "commune"].copy()
dvf["v"] = pd.to_numeric(dvf["med_prix_m2_whole_apt_maison"], errors="coerce")
price = {r.code_geo: int(r.v) for r in dvf.dropna(subset=["v"]).itertuples() if r.code_geo}

print("IPS communes (ecole-communes.json)...")
ips = {}
for c in json.loads(ECOLE_COM.read_text(encoding="utf-8")):
    ips[c["code"]] = {k: c[k] for k in ("ips_ecole_public", "ips_college_public", "ips_lycee_public", "va_lycee")
                      if c.get(k) is not None}

# Diversité (IDP des candidats municipaux) par commune + département
print("Diversité IDP (candidats municipaux)...")
def norm(n):
    if n is None:
        return ""
    s = unicodedata.normalize("NFD", str(n).upper().strip())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn").replace("'", " ").replace("’", " ")
    return re.sub(r"\s+", " ", s).strip()

divers, known = set(), set()
for line in SURNAMES.read_text(encoding="utf-8").splitlines():
    if "\t" not in line:
        continue
    nom, flag = line.split("\t")
    known.add(nom)
    if flag == "1":
        divers.add(nom)

cand = pd.read_csv(MUNI, sep=";", dtype=str, encoding="utf-8", low_memory=False)
cand.columns = [c.strip('"').strip() for c in cand.columns]
fl = cand["Nom sur le bulletin de vote"].str.strip('"').map(norm).map(
    lambda n: True if n in divers else (False if n in known else None))
com = cand["Code circonscription"].str.strip('"')
df = pd.DataFrame({"com": com, "dp": com.map(dep_of), "fl": fl}).dropna(subset=["fl"])
idp_com = {c: round(s.mean() * 100, 1) for c, s in df.groupby("com")["fl"] if s.size >= 20}
idp_dep = {c: round(s.mean() * 100, 1) for c, s in df.groupby("dp")["fl"] if s.size >= 50}
print(f"   IDP : {len(idp_com)} communes, {len(idp_dep)} départements")

# Union de toutes les communes connues
codes = set(income) | set(price) | set(ips) | set(idp_com)
by_dep = {}
for code in codes:
    rec = dict(ips.get(code, {}))
    if code in income:
        rec["revenu"] = income[code]
    if code in price:
        rec["prix_m2"] = price[code]
    if code in idp_com:
        rec["idp"] = idp_com[code]
    if rec:
        by_dep.setdefault(dep_of(code), {})[code] = rec

for dep, communes in by_dep.items():
    (OUT / f"{dep}.json").write_text(json.dumps(communes, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
total = sum(len(v) for v in by_dep.values())
print(f"-> {len(by_dep)} fichiers commune, {total} communes")

# Fichier départemental unifié de l'atlas (école + richesse + diversité)
deps = json.loads(ECOLE_IPS.read_text(encoding="utf-8"))["departements"]
for d in deps:
    if d["code"] in idp_dep:
        d["idp_candidats"] = idp_dep[d["code"]]
(OUT.parent / "departements.json").write_text(json.dumps(deps, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print(f"-> departements.json ({len(deps)} départements)")
