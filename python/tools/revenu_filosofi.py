# -*- coding: utf-8 -*-
"""
Revenu : niveau de vie médian (euros par an et par unité de consommation), Insee,
dispositif Filosofi 2, millésime 2023, géographie au 1er janvier 2025.

Source : « Indicateurs sur les revenus et la pauvreté au niveau local en 2023 »,
https://www.insee.fr/fr/statistiques/8984752 (fichier FILOSOFI_CC_csv.zip).

Remplace l'ancien fichier « niveau de vie par commune » republié par Le Figaro en 2017
(Filosofi 2014). Les valeurs départementales et intercommunales sont les médianes
officielles de l'Insee, et non plus des médianes de médianes communales.

Attention : l'Insee indique que les indicateurs Filosofi 2 (2023) ne sont pas
directement comparables avec ceux de Filosofi (2012 à 2021). Filosofi 2022 n'existe pas.
"""
import io
import time
import zipfile
import urllib.request
from pathlib import Path

import pandas as pd

URL = "https://www.insee.fr/fr/statistiques/fichier/8984752/FILOSOFI_CC_csv.zip"
MILLESIME = 2023
SOURCE = "Insee, Filosofi 2023"
SOURCE_URL = "https://www.insee.fr/fr/statistiques/8984752"

CACHE = Path(__file__).resolve().parent / "_cache_filosofi"
H = {"User-Agent": "Mozilla/5.0 (outsiders)", "Accept-Encoding": "identity"}


def _donnees() -> pd.DataFrame:
    CACHE.mkdir(exist_ok=True)
    fichier = CACHE / f"DS_FILOSOFI_CC_{MILLESIME}_data.csv"
    if not fichier.exists():
        for i in range(4):
            try:
                with urllib.request.urlopen(urllib.request.Request(URL, headers=H), timeout=180) as r:
                    raw = r.read()
                break
            except Exception as e:  # réseau capricieux de l'Insee
                print("   retry", i + 1, e)
                time.sleep(3)
        else:
            raise RuntimeError(URL)
        zf = zipfile.ZipFile(io.BytesIO(raw))
        membre = next(n for n in zf.namelist() if n.endswith("_data.csv"))
        fichier.write_bytes(zf.read(membre))
    return pd.read_csv(fichier, sep=";", dtype=str, usecols=["GEO", "GEO_OBJECT", "FILOSOFI_MEASURE", "OBS_VALUE"])


def niveaux_de_vie_medians(mesure: str = "MED_SL") -> dict:
    """Renvoie {'com': {code: valeur}, 'dep': {...}, 'epci': {...}} pour la mesure demandée.

    Les arrondissements de Paris, Lyon et Marseille (ARM) sont ajoutés aux communes.
    Seules les valeurs diffusées sont gardées (le secret statistique laisse des cases vides).
    """
    d = _donnees()
    d = d[(d.FILOSOFI_MEASURE == mesure) & d.OBS_VALUE.notna()].copy()
    d["v"] = pd.to_numeric(d.OBS_VALUE, errors="coerce")
    d = d.dropna(subset=["v"])
    par_niveau = {}
    for cle, objets in (("com", ("COM", "ARM")), ("dep", ("DEP",)), ("epci", ("EPCI",))):
        sub = d[d.GEO_OBJECT.isin(objets)]
        par_niveau[cle] = {g: int(round(v)) for g, v in zip(sub.GEO, sub.v)}
    return par_niveau


if __name__ == "__main__":
    r = niveaux_de_vie_medians()
    print({k: len(v) for k, v in r.items()}, "| 93066 :", r["com"].get("93066"), "| 93 :", r["dep"].get("93"))
