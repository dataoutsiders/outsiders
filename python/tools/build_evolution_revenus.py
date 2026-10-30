# -*- coding: utf-8 -*-
"""
Dossier « Qui s'enrichit, qui décroche ? » : évolution de la position des communes
dans la distribution des niveaux de vie, de 2014 à 2021, contrôlée sur 2023.

Mesure : pour chaque commune, la part de la population (des communes comparées) qui vit
dans une commune au niveau de vie médian plus faible (rang centile pondéré, 0 à 100).
Une position relative neutralise l'inflation et le niveau général des revenus.

Sources (Insee, niveau de vie médian par unité de consommation) :
  - 2014 : Filosofi 2014, fichier communal republié sur data.gouv.fr (géographie 2016) ;
  - 2021 : Filosofi 2021, géographie 2025 (même dispositif que 2014) ;
  - 2023 : Filosofi 2 (module revenu_filosofi), contrôle seulement : l'Insee prévient que
    Filosofi 2 n'est pas directement comparable avec Filosofi 2012-2021.
Champ : France métropolitaine, communes présentes aux trois dates et dont le territoire n'a
pas changé depuis 2014 (fusions, communes nouvelles, rétablissements, changements de code
écartés d'après le fichier des mouvements de communes de l'Insee ; les simples changements
de nom sont gardés).

À lancer APRÈS build_atlas_population.py (la population est lue dans les JSON de l'Atlas).
Sortie : frontend/public/data/showcases/evolution-revenus.json
"""
import io
import os
import json
import time
import zipfile
import urllib.request
from pathlib import Path

import pandas as pd

from revenu_filosofi import _donnees as filosofi_2023

ROOT = Path(__file__).resolve().parents[2]
# ATLAS_DIR permet de tester sur une copie des JSON de l'Atlas.
ATLAS = Path(os.environ.get("ATLAS_DIR", ROOT / "frontend" / "public" / "data" / "atlas"))
EPCI_MAP = ROOT / "python" / "data" / "municipales" / "communes-epci.json"
OUT = ROOT / "frontend" / "public" / "data" / "showcases" / "evolution-revenus.json"
CACHE = Path(__file__).resolve().parent / "_cache_filosofi"
H = {"User-Agent": "Mozilla/5.0 (outsiders)", "Accept-Encoding": "identity"}

URL_2014 = ("https://static.data.gouv.fr/resources/niveau-de-vie-des-francais-par-commune/"
            "20171031-164656/FRANCE_COMMUNE_NIVEAU_DE_VIE-FIGARO.csv")
URL_2021 = "https://www.insee.fr/fr/statistiques/fichier/7756729/base-cc-filosofi-2021-geo2025_csv.zip"
URL_MVT = "https://www.insee.fr/fr/statistiques/fichier/8377162/v_mvt_commune_2025.csv"

SEUIL_RECHERCHE = 2000   # communes proposées dans la recherche
SEUIL_CLASSEMENT = 20000 # villes des classements


def fetch(url):
    for i in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=180) as r:
                return r.read()
        except Exception as e:
            print("   retry", i + 1, e)
            time.sleep(3)
    raise RuntimeError(url)


def en_cache(nom, url):
    CACHE.mkdir(exist_ok=True)
    f = CACHE / nom
    if not f.exists():
        f.write_bytes(fetch(url))
    return f


def med_filosofi(df):
    d = df[(df.FILOSOFI_MEASURE == "MED_SL") & df.GEO_OBJECT.isin(["COM", "ARM"])]
    return pd.Series(pd.to_numeric(d.OBS_VALUE, errors="coerce").values, index=d.GEO).dropna()


def dep_of(c):
    return c[:3] if c[:2] in ("97", "98") else c[:2]


print("Filosofi 2014 (fichier communal republié)...")
f14 = pd.read_csv(en_cache("filosofi_2014_communes.csv", URL_2014), sep=";", dtype=str)
r14 = pd.Series(pd.to_numeric(f14.MED14.str.replace(",", ".", regex=False), errors="coerce").values,
                index=f14.CODGEO).dropna()
noms = dict(zip(f14.CODGEO, f14.LIBGEO))

print("Filosofi 2021...")
z = zipfile.ZipFile(en_cache("base-cc-filosofi-2021-geo2025_csv.zip", URL_2021))
membre = next(n for n in z.namelist() if n.endswith("_data.csv"))
r21 = med_filosofi(pd.read_csv(z.open(membre), sep=";", dtype=str,
                               usecols=["GEO", "GEO_OBJECT", "FILOSOFI_MEASURE", "OBS_VALUE"]))

print("Filosofi 2 (2023, contrôle)...")
r23 = med_filosofi(filosofi_2023())

print("Mouvements de communes depuis 2014...")
mvt = pd.read_csv(en_cache("v_mvt_commune_2025.csv", URL_MVT), dtype=str)
# 10 = changement de nom, 70 = commune associée devenue déléguée : sans effet sur le périmètre.
mvt = mvt[(mvt.DATE_EFF >= "2014-01-01") & ~mvt.MOD.isin(["10", "70"])]
touchees = set(mvt.COM_AV) | set(mvt.COM_AP)

print("Population (JSON de l'Atlas)...")
pop = {}
for fp in sorted((ATLAS / "communes").glob("*.json")):
    for code, rec in json.loads(fp.read_text(encoding="utf-8")).items():
        if rec.get("pop"):
            pop[code] = rec["pop"]
if not pop:
    raise SystemExit("Aucune population dans les JSON de l'Atlas : lancer build_atlas_population.py d'abord.")
pop = pd.Series(pop, dtype=float)

df = pd.DataFrame({"r14": r14, "r21": r21, "r23": r23, "pop": pop}).dropna()
n_avant = len(df)
exclues = df.index.isin(list(touchees))
# Paris, Lyon et Marseille figurent à la fois comme communes et par arrondissements :
# on garde les arrondissements (plus fins) pour ne pas compter deux fois leurs habitants.
PLM = {"75056", "13055", "69123"}
df = df[~exclues & ~df.index.str.startswith("97") & ~df.index.isin(PLM)]
print(f"   {n_avant} communes aux trois dates ; {int(exclues.sum())} écartées (périmètre modifié) ; "
      f"{len(df)} gardées en métropole")


def rang_pondere(s, w):
    o = s.sort_values()
    cum = w[o.index].cumsum() / w.sum() * 100
    return cum.reindex(s.index)


for a in ("14", "21", "23"):
    df["p" + a] = rang_pondere(df["r" + a], df["pop"])
df["d"] = df.p21 - df.p14
df["d23"] = df.p23 - df.p14
df["dep"] = [dep_of(c) for c in df.index]
grandes = df[df["pop"] >= SEUIL_CLASSEMENT]
correlation = round(float(grandes.d.corr(grandes.d23)), 2)
print(f"   cohérence 2014-2021 / 2014-2023 (villes de {SEUIL_CLASSEMENT} hab. et plus) : {correlation}")


def moyenne_ponderee(g, col="d"):
    return round(float((g[col] * g["pop"]).sum() / g["pop"].sum()), 1)


# Anneaux : Paris, petite couronne, grande couronne, reste de la métropole par taille de commune.
def anneau(row):
    if row.dep == "75":
        return "Paris"
    if row.dep in ("92", "93", "94"):
        return "Petite couronne"
    if row.dep in ("77", "78", "91", "95"):
        return "Grande couronne"
    # Arrondissements de Lyon (6938x) et de Marseille (132xx) : on les classe avec leur ville.
    if row["pop"] >= 100000 or row.name.startswith(("6938", "132")):
        return "Grandes villes de province (100 000 hab. et plus)"
    if row["pop"] >= 20000:
        return "Villes moyennes de province (20 000 à 100 000 hab.)"
    return "Communes de province de moins de 20 000 hab."


df["anneau"] = df.apply(anneau, axis=1)
ordre = ["Paris", "Petite couronne", "Grande couronne",
         "Grandes villes de province (100 000 hab. et plus)",
         "Villes moyennes de province (20 000 à 100 000 hab.)",
         "Communes de province de moins de 20 000 hab."]
anneaux = []
for nom in ordre:
    g = df[df.anneau == nom]
    if len(g):
        anneaux.append({"nom": nom, "n": int(len(g)), "pop": int(g["pop"].sum()),
                        "evolution": moyenne_ponderee(g), "evolution_2023": moyenne_ponderee(g, "d23"),
                        "part_pop_en_hausse": round(float(g.loc[g.d > 0, "pop"].sum() / g["pop"].sum() * 100), 1)})

deps = []
for code, g in df.groupby("dep"):
    deps.append({"code": code, "n": int(len(g)), "evolution": moyenne_ponderee(g)})

comm_epci = {c["code"]: c.get("codeEpci") for c in json.loads(EPCI_MAP.read_text(encoding="utf-8"))}
df["epci"] = [comm_epci.get(c) for c in df.index]
epci = []
for code, g in df.dropna(subset=["epci"]).groupby("epci"):
    epci.append({"code": code, "n": int(len(g)), "evolution": moyenne_ponderee(g)})

recherche = df[df["pop"] >= SEUIL_RECHERCHE].sort_values("pop", ascending=False)
villes = [[c, noms.get(c, c), r.dep, int(r["pop"]), int(r.r14), int(r.r21), int(r.r23),
           round(r.p14, 1), round(r.p21, 1), round(r.p23, 1)]
          for c, r in recherche.iterrows()]

out = {
    "titre": "Qui s'enrichit, qui décroche ?",
    "mesure": "Rang centile pondéré par la population : part de la population des communes comparées "
              "qui vit dans une commune au niveau de vie médian plus faible (0 à 100).",
    "champ": {"communes": int(len(df)), "communes_ecartees_perimetre": int(exclues.sum()),
              "seuil_recherche": SEUIL_RECHERCHE, "seuil_classement": SEUIL_CLASSEMENT,
              "territoire": "France métropolitaine"},
    "coherence_2023": correlation,
    "anneaux": anneaux,
    "departements": deps,
    "epci": epci,
    "colonnes_villes": ["code", "nom", "dep", "pop", "revenu_2014", "revenu_2021", "revenu_2023",
                        "position_2014", "position_2021", "position_2023"],
    "villes": villes,
    "sources": [
        {"label": "Insee, Filosofi 2014 (fichier communal republié sur data.gouv.fr)",
         "url": "https://www.data.gouv.fr/datasets/niveau-de-vie-des-francais-par-commune"},
        {"label": "Insee, Filosofi 2021", "url": "https://www.insee.fr/fr/statistiques/7756729"},
        {"label": "Insee, Filosofi 2 (2023)", "url": "https://www.insee.fr/fr/statistiques/8984752"},
        {"label": "Insee, mouvements de communes depuis 1943", "url": "https://www.insee.fr/fr/information/8377162"},
    ],
}
OUT.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print(f"-> {OUT.name} ({len(villes)} communes de {SEUIL_RECHERCHE} hab. et plus, {len(epci)} EPCI, "
      f"{OUT.stat().st_size / 1e6:.1f} Mo)")
for a in anneaux:
    print(f"   {a['nom']} : {a['evolution']:+.1f} (2023 : {a['evolution_2023']:+.1f}), "
          f"{a['part_pop_en_hausse']} % de la population en hausse")
