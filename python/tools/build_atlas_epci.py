# -*- coding: utf-8 -*-
"""
Atlas - maille EPCI (intercommunalités) pour la vue nationale.

Émet :
  - frontend/public/data/geo/epci.geojson  (contours SIMPLIFIÉS, propriété `code` = SIREN, `nom`)
  - frontend/public/data/atlas/epci.json    (array {code, nom, <indicateurs>})

Contours : référentiel OpenDataSoft (georef-france-epci, ~24 Mo) simplifié en Python pur
(Douglas-Peucker + arrondi des coordonnées) pour tomber autour de 1-2 Mo.
Indicateurs EPCI :
  - revenu : niveau de vie médian officiel de l'Insee par EPCI (Filosofi 2023)
  - prix_m2 : médiane officielle par EPCI des Statistiques DVF (échelle « epci »), comme au département
  - idp : part des noms classés « diversité » parmi les candidats municipaux 2026 des communes
    de l'EPCI (au moins 50 noms reconnus), même calcul qu'au département et à la région
  - IPS (école/collège/lycée public) + va_lycee : repris de ecole-ips.json["epci"]
"""
import io
import json
import gzip
import time
import statistics
import urllib.request
from pathlib import Path

H = {"User-Agent": "outsiders/1.0", "Accept-Encoding": "identity"}
ROOT = Path(__file__).resolve().parents[2]
ATLAS = ROOT / "frontend" / "public" / "data" / "atlas"
GEO = ROOT / "frontend" / "public" / "data" / "geo"
COMMUNES = ATLAS / "communes"
EPCI_MAP = ROOT / "python" / "data" / "municipales" / "communes-epci.json"
ECOLE_IPS = ROOT / "frontend" / "public" / "data" / "showcases" / "ecole-ips.json"
GEO.mkdir(parents=True, exist_ok=True)

EPS = 0.003  # tolérance Douglas-Peucker en degrés (~330 m)
RND = 4      # décimales conservées (~11 m)


def fetch(url, tries=4, timeout=300):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=timeout) as r:
                return r.read()
        except Exception as e:
            print("   retry", i + 1, e)
            time.sleep(3)
    raise RuntimeError(url)


def dp(pts, eps):
    """Douglas-Peucker itératif sur une polyligne [[x,y], ...]."""
    n = len(pts)
    if n < 3:
        return pts
    keep = [False] * n
    keep[0] = keep[n - 1] = True
    stack = [(0, n - 1)]
    while stack:
        a, b = stack.pop()
        ax, ay = pts[a]
        bx, by = pts[b]
        dx, dy = bx - ax, by - ay
        d2 = dx * dx + dy * dy
        idx, dmax = -1, 0.0
        for i in range(a + 1, b):
            px, py = pts[i]
            if d2 == 0:
                dist = ((px - ax) ** 2 + (py - ay) ** 2) ** 0.5
            else:
                t = ((px - ax) * dx + (py - ay) * dy) / d2
                t = 0.0 if t < 0 else (1.0 if t > 1 else t)
                qx, qy = ax + t * dx, ay + t * dy
                dist = ((px - qx) ** 2 + (py - qy) ** 2) ** 0.5
            if dist > dmax:
                idx, dmax = i, dist
        if dmax > eps and idx != -1:
            keep[idx] = True
            stack.append((a, idx))
            stack.append((idx, b))
    return [pts[i] for i in range(n) if keep[i]]


def simplify_ring(ring):
    # arrondi + dédoublonnage des points consécutifs, puis Douglas-Peucker
    out = []
    for x, y in ring:
        p = [round(x, RND), round(y, RND)]
        if not out or out[-1] != p:
            out.append(p)
    if len(out) >= 2 and out[0] != out[-1]:
        out.append(out[0])
    s = dp(out, EPS)
    if s[0] != s[-1]:
        s.append(s[0])
    return s if len(s) >= 4 else None


def simplify_geom(geom):
    t = geom["type"]
    c = geom["coordinates"]
    if t == "Polygon":
        rings = [r for r in (simplify_ring(r) for r in c) if r]
        return {"type": "Polygon", "coordinates": rings} if rings else None
    if t == "MultiPolygon":
        polys = []
        for poly in c:
            rings = [r for r in (simplify_ring(r) for r in poly) if r]
            if rings:
                polys.append(rings)
        return {"type": "MultiPolygon", "coordinates": polys} if polys else None
    return None


# 1. Contours EPCI (OpenDataSoft) + simplification
print("Contours EPCI (OpenDataSoft, ~24 Mo)...")
url = ("https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/"
       "georef-france-epci/exports/geojson?select=epci_code,epci_name,geo_shape&limit=-1")
src = json.loads(fetch(url))
print(f"   {len(src['features'])} EPCI, simplification...")
out_feats = []
epci_nom = {}
for f in src["features"]:
    p = f.get("properties", {})
    code = p.get("epci_code")
    nom = p.get("epci_name")
    code = code[0] if isinstance(code, list) else code
    nom = nom[0] if isinstance(nom, list) else nom
    geom = f.get("geometry")
    if not code or not geom:
        continue
    g = simplify_geom(geom)
    if not g:
        continue
    epci_nom[code] = nom
    out_feats.append({"type": "Feature", "properties": {"code": code, "nom": nom}, "geometry": g})

geojson = {"type": "FeatureCollection", "features": out_feats}
(GEO / "epci.geojson").write_text(json.dumps(geojson, separators=(",", ":")), encoding="utf-8")
size = (GEO / "epci.geojson").stat().st_size / 1_000_000
print(f"-> epci.geojson ({len(out_feats)} EPCI, {size:.1f} Mo)")

# 2. commune -> EPCI ; médiane des communes, en secours seulement (valeurs officielles plus bas)
comm_epci = {c["code"]: c.get("codeEpci") for c in json.loads(EPCI_MAP.read_text(encoding="utf-8"))}
buckets = {}
for fp in sorted(COMMUNES.glob("*.json")):
    for code, rec in json.loads(fp.read_text(encoding="utf-8")).items():
        ep = comm_epci.get(code)
        if not ep:
            continue
        b = buckets.setdefault(ep, {})
        for k in ("revenu", "prix_m2", "idp"):
            if rec.get(k) is not None:
                b.setdefault(k, []).append(rec[k])

# 3. IPS / VA EPCI
ips_epci = {}
for e in json.loads(ECOLE_IPS.read_text(encoding="utf-8")).get("epci", []):
    ips_epci[e["code"]] = {k: e[k] for k in ("ips_ecole_public", "ips_college_public", "ips_lycee_public", "va_lycee")
                           if e.get(k) is not None}

# 3 bis. Prix DVF officiel par EPCI (même fichier que build_atlas_communes.py, échelle « epci »).
import re
import unicodedata
import pandas as pd

dvf = pd.read_csv("https://data-pipeline-open.s3.sbg.io.cloud.ovh.net/dvf/stats_whole_period.csv",
                  dtype=str, low_memory=False)
dvf = dvf[dvf.echelle_geo == "epci"]
v = pd.to_numeric(dvf["med_prix_m2_whole_apt_maison"], errors="coerce")
prix_epci = {c: int(round(x)) for c, x in zip(dvf.code_geo, v) if pd.notna(x) and c}
print(f"   prix DVF officiel : {len(prix_epci)} EPCI")

# 3 ter. Diversité des noms des candidats municipaux 2026, sur les effectifs de l'EPCI.
SURNAMES = ROOT / "frontend" / "public" / "data" / "onomastics" / "surnames.tsv"
MUNI = ROOT / "python" / "data" / "municipales" / "municipales-2026.csv"


def norm(n):
    if n is None:
        return ""
    s = unicodedata.normalize("NFD", str(n).upper().strip())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn").replace("'", " ").replace("’", " ")
    return re.sub(r"\s+", " ", s).strip()


divers, connus = set(), set()
for line in SURNAMES.read_text(encoding="utf-8").splitlines():
    if "	" in line:
        nom, flag = line.split("	")
        connus.add(nom)
        if flag == "1":
            divers.add(nom)
cand = pd.read_csv(MUNI, sep=";", dtype=str, encoding="utf-8", low_memory=False)
cand.columns = [c.strip('"').strip() for c in cand.columns]
fl = cand["Nom sur le bulletin de vote"].str.strip('"').map(norm).map(
    lambda n: True if n in divers else (False if n in connus else None))
df = pd.DataFrame({"ep": cand["Code circonscription"].str.strip('"').map(comm_epci), "fl": fl}).dropna()
idp_epci = {ep: round(g.astype(bool).mean() * 100, 1) for ep, g in df.groupby("ep")["fl"] if g.size >= 50}
print(f"   diversité des candidats : {len(idp_epci)} EPCI (au moins 50 noms reconnus)")

# 4. fusion -> epci.json
from revenu_filosofi import niveaux_de_vie_medians
revenu_epci = niveaux_de_vie_medians()["epci"]
out = []
for code, nom in epci_nom.items():
    rec = {"code": code, "nom": nom}
    b = buckets.get(code, {})
    for k in ("revenu", "prix_m2", "idp"):
        if b.get(k):
            v = statistics.median(b[k])
            rec[k] = round(v, 1) if k == "idp" else int(round(v))
    if code in revenu_epci:
        rec["revenu"] = revenu_epci[code]  # valeur officielle, prioritaire sur la médiane de communes
    if code in prix_epci:
        rec["prix_m2"] = prix_epci[code]  # médiane officielle DVF de l'EPCI
    else:
        rec.pop("prix_m2", None)  # pas de médiane de médianes
    if code in idp_epci:
        rec["idp"] = idp_epci[code]  # calculée sur les candidats de l'EPCI
    else:
        rec.pop("idp", None)
    rec.update(ips_epci.get(code, {}))
    out.append(rec)
(ATLAS / "epci.json").write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
n_rev = sum(1 for r in out if "revenu" in r)
n_ips = sum(1 for r in out if "ips_college_public" in r)
print(f"-> epci.json ({len(out)} EPCI ; {n_rev} avec revenu, {n_ips} avec IPS collège)")
