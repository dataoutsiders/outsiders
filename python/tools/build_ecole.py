# -*- coding: utf-8 -*-
"""
Terrain « École », artefacts depuis les données ouvertes Éducation nationale.

Sorties (frontend/public/data/showcases/) :
  - ecole-ips.json      : agrégats par DÉPARTEMENT et par EPCI, pour chaque niveau
                          (école/collège/lycée) et chaque secteur (public/privé/tous),
                          + cumul (sur le public) + valeur ajoutée des lycées (IVAL).
  - etablissements.tsv  : un établissement par ligne (IPS + percentile + VA lycée) →
                          recherche « tape ton établissement ».

Sources data.gouv.fr : IPS écoles/collèges/lycées + IVAL (valeur ajoutée des lycées).
Le mapping commune→EPCI vient de python/data/municipales/communes-epci.json (geo.api.gouv.fr).
"""
import io
import gzip
import json
import time
import urllib.request
import urllib.parse
from pathlib import Path
import numpy as np
import pandas as pd

H = {"User-Agent": "outsiders/1.0"}
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "frontend" / "public" / "data" / "showcases"
COMMUNES_EPCI = ROOT / "python" / "data" / "municipales" / "communes-epci.json"
OUT.mkdir(parents=True, exist_ok=True)

LEVELS = {
    "ecole": dict(q="indice de position sociale écoles", year="Rentrée scolaire",
                  dep="Code du département", deplab="Département", com="Nom de la commune",
                  comcode="Code INSEE de la commune", ips="IPS"),
    "college": dict(q="indice de position sociale collèges", year="Année scolaire",
                    dep="Code département", deplab="Libellé département", com="Libellé commune",
                    comcode="Code commune Insee", ips="IPS"),
    "lycee": dict(q="indice de position sociale lycées", year="Rentrée scolaire",
                  dep="Code du département", deplab="Département", com="Nom de la commune",
                  comcode="Code INSEE de la commune", ips="IPS de l'établissement"),
}


def fetch(url, tries=4):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=60) as r:
                return r.read()
        except Exception as e:
            print("   retry", i + 1, e)
            time.sleep(3)
    raise RuntimeError(f"échec {url}")


def read_csv_bytes(raw):
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    return pd.read_csv(io.BytesIO(raw), sep=";", dtype=str, encoding="utf-8")


def csv_url(q):
    raw = fetch("https://www.data.gouv.fr/api/1/datasets/?" + urllib.parse.urlencode({"q": q, "page_size": 6}))
    data = json.loads(raw)["data"]
    ds = next((d for d in data if "ducation" in ((d.get("organization") or {}).get("name", "")).lower()), data[0])
    cs = [r for r in ds.get("resources", []) if (r.get("format") or "").lower() == "csv"]
    cs.sort(key=lambda r: r.get("filesize") or 0, reverse=True)
    return cs[0]["url"]


def norm_dep(s):
    s = str(s).strip().upper()
    return s[1:] if len(s) == 3 and s.startswith("0") else s


def load_level(niveau, cfg):
    df = read_csv_bytes(fetch(csv_url(cfg["q"])))
    df["ips"] = pd.to_numeric(df[cfg["ips"]], errors="coerce")
    an = sorted(df[cfg["year"]].dropna().unique())[-1]
    df = df[(df[cfg["year"]] == an) & df["ips"].notna()].copy()
    out = pd.DataFrame({
        "uai": df["UAI"], "nom": df["Nom de l'établissement"], "commune": df[cfg["com"]],
        "comcode": df[cfg["comcode"]], "dep": df[cfg["dep"]].map(norm_dep), "deplab": df[cfg["deplab"]],
        "secteur": df["Secteur"], "ips": df["ips"], "niveau": niveau,
    })
    print(f"   {niveau:8} année {an} | {len(out)} établissements")
    return an, out


def load_ival():
    frames = []
    for q in ["indicateurs de valeur ajoutée des lycées d'enseignement général et technologique",
              "indicateurs de valeur ajoutée des lycées d'enseignement professionnel"]:
        df = read_csv_bytes(fetch(csv_url(q)))
        va, tx = "Valeur ajoutée du taux de réussite - Toutes séries", "Taux de réussite - Toutes séries"
        if va not in df.columns:
            continue
        an = sorted(df["Année"].dropna().unique())[-1]
        df = df[df["Année"] == an]
        frames.append(pd.DataFrame({"uai": df["UAI"], "va": pd.to_numeric(df[va], errors="coerce"),
                                    "taux": pd.to_numeric(df.get(tx), errors="coerce")}))
    return pd.concat(frames).dropna(subset=["uai"]).groupby("uai", as_index=False).mean(numeric_only=True)


def load_coords():
    """UAI -> (lat, lon) depuis l'Annuaire de l'éducation."""
    base = ("https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/"
            "fr-en-annuaire-education/exports/csv")
    for url in (base + "?select=identifiant_de_l_etablissement,latitude,longitude", base):
        try:
            raw = fetch(url)
            if raw[:2] == b"\x1f\x8b":
                raw = gzip.decompress(raw)
            df = pd.read_csv(io.BytesIO(raw), sep=";", dtype=str, encoding="utf-8")
            uai_c = next(c for c in df.columns if "identifiant" in c.lower())
            lat_c = next(c for c in df.columns if c.lower() == "latitude")
            lon_c = next(c for c in df.columns if c.lower() == "longitude")
            df["lat"] = pd.to_numeric(df[lat_c], errors="coerce").round(5)
            df["lon"] = pd.to_numeric(df[lon_c], errors="coerce").round(5)
            return df.dropna(subset=["lat", "lon"]).drop_duplicates(uai_c).set_index(uai_c)[["lat", "lon"]]
        except Exception as e:
            print("   coords:", e)
    return pd.DataFrame(columns=["lat", "lon"])


print("Chargement IPS (3 niveaux)...")
annees, frames = {}, []
for niveau, cfg in LEVELS.items():
    an, df = load_level(niveau, cfg)
    annees[niveau] = an
    frames.append(df)
etab = pd.concat(frames, ignore_index=True)

print("Chargement IVAL...")
etab = etab.merge(load_ival(), on="uai", how="left")
etab["pct"] = (etab.groupby("niveau")["ips"].rank(pct=True) * 100).round().astype("Int64")

print("Coordonnées (annuaire)...")
etab = etab.merge(load_coords(), left_on="uai", right_index=True, how="left")
print(f"   {etab['lat'].notna().sum()}/{len(etab)} établissements géolocalisés")

print("Croisement : revenus (Insee Filosofi 2023) + prix immobilier (DVF)...")
def read_csv_url(url, sep):
    raw = fetch(url)
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    return pd.read_csv(io.BytesIO(raw), sep=sep, dtype=str, encoding="utf-8", low_memory=False)

def dep_of(c):
    c = str(c)
    return c[:3] if c[:2] in ("97", "98") else c[:2]

# Niveau de vie médian, Insee Filosofi 2023 (valeurs officielles par commune et par département).
from revenu_filosofi import niveaux_de_vie_medians
_rev = niveaux_de_vie_medians()
income_com = pd.Series(_rev["com"], dtype=float)
income_dep = pd.Series(_rev["dep"], dtype=float)

# Statistiques DVF (data.gouv.fr, jeu « Statistiques DVF ») : fichier du 21/10/2026, ventes de juillet 2021 à juin 2026.
# L'ancienne adresse object.files.data.gouv.fr restait figée sur la livraison d'avril 2026.
dvf = read_csv_url("https://data-pipeline-open.s3.sbg.io.cloud.ovh.net/dvf/stats_whole_period.csv", ",")
dvf["price"] = pd.to_numeric(dvf["med_prix_m2_whole_apt_maison"], errors="coerce")
price_dep = dvf[dvf.echelle_geo == "departement"].dropna(subset=["price"]).drop_duplicates("code_geo").set_index("code_geo")["price"]
price_com = dvf[dvf.echelle_geo == "commune"].dropna(subset=["price"]).drop_duplicates("code_geo").set_index("code_geo")["price"]
print(f"   revenus : {len(income_dep)} dépts, {len(income_com)} communes | prix : {len(price_dep)} dépts, {len(price_com)} communes")

# commune -> EPCI
comm_epci = {c["code"]: c.get("codeEpci") for c in json.loads(COMMUNES_EPCI.read_text(encoding="utf-8")) if c.get("codeEpci")}
etab["epci"] = etab["comcode"].map(comm_epci)


def wide_rows(df, code_col, seuil=1):
    """Pour chaque maille×niveau : IPS moyen public / privé / tous."""
    rows = {}
    for (code, niveau), g in df.groupby([code_col, "niveau"]):
        if pd.isna(code) or code == "":
            continue
        for lab, sub in (("public", g[g.secteur == "public"]),
                         ("prive", g[g.secteur != "public"]),
                         ("tous", g)):
            if len(sub) >= seuil:
                rows.setdefault(str(code), {})[f"ips_{niveau}_{lab}"] = round(sub["ips"].mean(), 1)
    return rows


def va_by(df, code_col):
    return df[df.niveau == "lycee"].groupby(code_col)["va"].mean().round(1)


# ============================================================
# Départements (+ cumul sur le public)
# ============================================================
print("Agrégat départemental + EPCI...")
dep_rows, dep_va = wide_rows(etab, "dep"), va_by(etab, "dep")
dep_name = etab.groupby("dep")["deplab"].first()
deps = []
for code, vals in dep_rows.items():
    if all(f"ips_{n}_public" in vals for n in ("ecole", "college", "lycee")):
        va = dep_va.get(code)
        deps.append({"code": code, "dep": dep_name.get(code, ""), **vals,
                     "va_lycee": None if pd.isna(va) else float(va)})
dd = pd.DataFrame(deps)
for n in ("ecole", "college", "lycee"):
    dd["q_" + n] = pd.qcut(dd[f"ips_{n}_public"], 3, labels=["bas", "moyen", "haut"])
dd["cumul"] = np.where((dd.q_ecole == "bas") & (dd.q_college == "bas") & (dd.q_lycee == "bas"), "triple-bas",
              np.where((dd.q_ecole == "haut") & (dd.q_college == "haut") & (dd.q_lycee == "haut"), "triple-haut", "mixte"))
dd["ips_moyen"] = dd[["ips_ecole_public", "ips_college_public", "ips_lycee_public"]].mean(axis=1).round(1)
dd["revenu"] = dd["code"].map(income_dep).round(0)
dd["prix_m2"] = dd["code"].map(price_dep).round(0)
dep_records = json.loads(dd.drop(columns=[c for c in dd.columns if c.startswith("q_")]).to_json(orient="records", force_ascii=False))

# ============================================================
# EPCI
# ============================================================
epci_rows, epci_va = wide_rows(etab, "epci", seuil=2), va_by(etab, "epci")
epci_records = []
for code, vals in epci_rows.items():
    va = epci_va.get(code)
    epci_records.append({"code": code, **vals, "va_lycee": None if pd.isna(va) else float(va)})

ips_json = OUT / "ecole-ips.json"
ips_json.write_text(json.dumps({"annees": annees, "departements": dep_records, "epci": epci_records},
                               ensure_ascii=False, indent=2), encoding="utf-8")
nbas = int((dd.cumul == "triple-bas").sum())
print(f"   -> {ips_json.name} | {len(dep_records)} dépts ({nbas} triple-bas) | {len(epci_records)} EPCI")

# ============================================================
# Communes (points : centroïdes geo.api)
# ============================================================
print("Centroïdes communes (geo.api)...")
craw = fetch("https://geo.api.gouv.fr/communes?fields=code,centre&format=json")
if craw[:2] == b"\x1f\x8b":
    craw = gzip.decompress(craw)
centroids = {}
for c in json.loads(craw):
    ce = c.get("centre") or {}
    if ce.get("coordinates"):
        lon, lat = ce["coordinates"]
        centroids[c["code"]] = (round(lat, 5), round(lon, 5))

print("Agrégat communal...")
com_rows = wide_rows(etab, "comcode")
com_meta = etab.groupby("comcode").agg(nom=("commune", "first"), dep=("dep", "first"), n=("uai", "size"))
com_va = va_by(etab, "comcode")
communes = []
for code, vals in com_rows.items():
    cen = centroids.get(code)
    if not cen:
        continue
    va = com_va.get(code)
    rv, px = income_com.get(code), price_com.get(code)
    communes.append({"code": code, "nom": com_meta.loc[code, "nom"], "dep": com_meta.loc[code, "dep"],
                     "lat": cen[0], "lon": cen[1], "n": int(com_meta.loc[code, "n"]), **vals,
                     "va_lycee": None if pd.isna(va) else float(va),
                     "revenu": None if pd.isna(rv) else int(rv),
                     "prix_m2": None if pd.isna(px) else int(px)})
com_json = OUT / "ecole-communes.json"
com_json.write_text(json.dumps(communes, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print(f"   -> {com_json.name} ({len(communes)} communes, {com_json.stat().st_size/1024/1024:.1f} Mo)")

# ============================================================
# Établissements (recherche)
# ============================================================
print("Fichier établissements...")
def clean(s):
    return str(s).replace("\t", " ").replace("\n", " ").strip()

NIV = {"ecole": "e", "college": "c", "lycee": "l"}
lines = ["uai\tnom\tcommune\tdep\tsecteur\tniveau\tips\tpct\tva\ttaux\tlat\tlon"]
for r in etab.itertuples(index=False):
    va = "" if pd.isna(r.va) else round(r.va, 1)
    taux = "" if pd.isna(r.taux) else round(r.taux, 1)
    pct = "" if pd.isna(r.pct) else int(r.pct)
    lat = "" if pd.isna(r.lat) else r.lat
    lon = "" if pd.isna(r.lon) else r.lon
    lines.append(f"{clean(r.uai)}\t{clean(r.nom)}\t{clean(r.commune)}\t{clean(r.dep)}\t"
                 f"{'pu' if r.secteur == 'public' else 'pr'}\t{NIV[r.niveau]}\t{round(r.ips,1)}\t{pct}\t{va}\t{taux}\t{lat}\t{lon}")
etab_tsv = OUT / "etablissements.tsv"
etab_tsv.write_text("\n".join(lines), encoding="utf-8")
print(f"   -> {etab_tsv.name} ({len(etab)} étabts, {etab_tsv.stat().st_size/1024/1024:.1f} Mo)")
print("\nTERMINÉ.")
