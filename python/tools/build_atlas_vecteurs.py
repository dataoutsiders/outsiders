# -*- coding: utf-8 -*-
"""
Atlas - vecteurs communaux pour le « jumeau statistique ».

Émet `frontend/public/data/atlas/communes-vecteurs.json` : pour chaque commune de
1 000 hab. ou plus, son vecteur d'indicateurs + centroïde géographique. Le frontend
standardise (z-scores) et cherche le plus proche voisin / l'anti-jumeau, 100 %
navigateur. Restreint aux communes >= 1 000 hab. (indicateurs instables en deçà,
et fichier plus léger).

Format (colonnaire, compact) :
  { "cols": [...ids...], "mean": [...], "std": [...],
    "rows": [[code, nom, pop, lon, lat, v0, v1, ...], ...] }
"""
import io
import json
import time
import urllib.request
from pathlib import Path
import math

ROOT = Path(__file__).resolve().parents[2]
ATLAS = ROOT / "frontend" / "public" / "data" / "atlas"
COMMUNES = ATLAS / "communes"
OUT = ATLAS / "communes-vecteurs.json"
POP_MIN = 1000

COLS = [
    "revenu", "prix_m2", "diplome_sup", "ages65", "jeunes", "proprietaires",
    "maisons", "hlm", "vacants", "res_secondaires", "cadres", "ouvriers",
    "natalite", "idp",
]
H = {"User-Agent": "outsiders/1.0", "Accept-Encoding": "identity"}


def fetch(url, tries=4, timeout=180):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=timeout) as r:
                return r.read()
        except Exception as e:
            print("   retry", i + 1, e)
            time.sleep(3)
    return None


print("Lecture des communes de l'atlas...")
recs = {}
for fp in sorted(COMMUNES.glob("*.json")):
    for code, rec in json.loads(fp.read_text(encoding="utf-8")).items():
        recs[code] = rec
print(f"   {len(recs)} communes")

# Noms + centroïdes (geo.api, un seul appel). geo.api connaît les arrondissements
# municipaux (Paris/Lyon/Marseille), absents de l'index communes-epci.
print("Téléchargement noms + centroïdes (geo.api.gouv.fr)...")
centres, noms = {}, {}
raw = fetch("https://geo.api.gouv.fr/communes?fields=code,nom,centre&format=json")
if raw:
    try:
        for c in json.loads(raw):
            if c.get("nom"):
                noms[c["code"]] = c["nom"]
            ctr = c.get("centre")
            if ctr and ctr.get("coordinates"):
                lon, lat = ctr["coordinates"]
                centres[c["code"]] = (round(lon, 4), round(lat, 4))
        print(f"   {len(noms)} noms, {len(centres)} centroïdes")
    except Exception as e:
        print("   geo.api illisible:", e)
else:
    print("   geo.api indisponible (noms/distances dégradés)")

# geo.api ne liste pas les arrondissements municipaux : noms de repli (Paris,
# Lyon, Marseille), codes 751xx / 6938x / 132xx.
def _arr(i):
    return "1er" if i == 1 else f"{i}e"

for i in range(1, 21):
    noms.setdefault(f"751{i:02d}", f"Paris {_arr(i)}")
for i in range(1, 10):
    noms.setdefault(f"6938{i}", f"Lyon {_arr(i)}")
for i in range(1, 17):
    noms.setdefault(f"132{i:02d}", f"Marseille {_arr(i)}")

# Sélection des communes >= POP_MIN avec au moins un indicateur.
rows = []
for code, rec in recs.items():
    pop = rec.get("pop")
    if pop is None or pop < POP_MIN:
        continue
    vals = [rec.get(c) for c in COLS]
    if all(v is None for v in vals):
        continue
    lon, lat = centres.get(code, (None, None))
    nom = noms.get(code, f"Commune {code}")
    rows.append([code, nom, int(pop), lon, lat, vals])

print(f"   {len(rows)} communes >= {POP_MIN} hab. retenues")

# Moyenne / écart-type par colonne (sur les valeurs présentes).
mean, std = [], []
for j in range(len(COLS)):
    xs = [r[5][j] for r in rows if r[5][j] is not None]
    if xs:
        m = sum(xs) / len(xs)
        var = sum((x - m) ** 2 for x in xs) / len(xs)
        mean.append(round(m, 3))
        std.append(round(math.sqrt(var), 3) or 1.0)
    else:
        mean.append(0.0)
        std.append(1.0)

out_rows = [[code, nom, pop, lon, lat, *[(None if v is None else round(v, 2)) for v in vals]]
            for code, nom, pop, lon, lat, vals in rows]

OUT.write_text(
    json.dumps({"cols": COLS, "mean": mean, "std": std, "rows": out_rows}, ensure_ascii=False, separators=(",", ":")),
    encoding="utf-8",
)
size_kb = OUT.stat().st_size / 1024
print(f"-> communes-vecteurs.json ({len(out_rows)} communes, {size_kb:.0f} Ko)")
print(f"   ex. cols: {COLS}")
