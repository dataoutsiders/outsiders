# -*- coding: utf-8 -*-
"""
Lecture des bases du recensement de la population (RP) 2023 de l'INSEE, format « long » codé.

Depuis le RP 2023, l'INSEE ne publie plus les bases communales « base-cc-..._csv.zip » à colonnes
P21_... : chaque thème est diffusé en CSV long (DS_RP_<THEME>_<PRINC|COMP>_2023_CSV_FR.zip) avec
les colonnes GEO, GEO_OBJECT, des dimensions codées (AGE, SEX, OCS, TSH, PCS...), RP_MEASURE,
TIME_PERIOD (2012, 2017, 2023), OBS_VALUE, et un fichier _metadata.csv qui décode les modalités.

Ce module :
  - retrouve le CSV déjà décompressé dans python/data/insee_maj/<dossier>/, sinon décompresse le zip
    présent dans python/data/insee_maj/, sinon le télécharge (User-Agent de navigateur) ;
  - lit le CSV par morceaux en ne gardant que les niveaux géographiques et l'année demandés ;
  - extrait des « séries » : une série = une combinaison de modalités ; toute dimension non citée
    est forcée à « _T » (Total), ce qui évite tout double comptage entre modalités ;
  - décrit chaque série avec les libellés du fichier metadata (traçabilité des correspondances).

Géographie des bases 2023 : communes au 1er janvier 2026 (GEO_OBJECT = COM, y compris Paris,
Lyon, Marseille entiers 75056 / 69123 / 13055) et arrondissements municipaux (GEO_OBJECT = ARM).
"""
import io
import time
import zipfile
import urllib.request
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "python" / "data" / "insee_maj"
UA = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/130.0 Safari/537.36",
    "Accept-Encoding": "identity",
}
ANNEE = "2023"

# thème -> (identifiant de la page INSEE, nom du jeu, sous-dossier local)
SOURCES = {
    "population": (9005956, "DS_RP_POPULATION_PRINC_2023", "rp2023_population"),
    "diplomes": (9006527, "DS_RP_DIPLOMES_PRINC_2023", "rp2023_diplomes"),
    "logement": (8997194, "DS_RP_LOGEMENT_PRINC_2023", "rp2023_logement"),
    "emploi_comp": (9002680, "DS_RP_EMPLOI_LR_COMP_2023", "rp2023_emploi_lr_comp"),
}
META_COLS = {"GEO", "GEO_OBJECT", "FREQ", "OBS_STATUS", "TIME_PERIOD", "OBS_VALUE"}
# Communes à arrondissements municipaux : la base donne la commune entière (COM) ET ses arrondissements (ARM).
PLM = {"75056", "13055", "69123"}


def url(theme):
    page, nom, _ = SOURCES[theme]
    return f"https://www.insee.fr/fr/statistiques/fichier/{page}/{nom}_CSV_FR.zip"


def _fetch(u, tries=4, timeout=600):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=timeout) as r:
                return r.read()
        except Exception as e:
            print("   retry", i + 1, e)
            time.sleep(3)
    raise RuntimeError(u)


def fichiers(theme):
    """Chemins (data.csv, metadata.csv) du thème, téléchargés et décompressés au besoin."""
    _, nom, sous = SOURCES[theme]
    dossier = DATA / sous
    data, meta = dossier / f"{nom}_data.csv", dossier / f"{nom}_metadata.csv"
    if data.exists() and meta.exists():
        return data, meta
    zips = [DATA / f"{nom}_CSV_FR.zip", DATA / f"{nom}.zip"]
    zp = next((z for z in zips if z.exists()), None)
    if zp is None:
        print(f"   téléchargement {url(theme)}")
        zp = zips[0]
        DATA.mkdir(parents=True, exist_ok=True)
        zp.write_bytes(_fetch(url(theme)))
    dossier.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zp) as zf:
        for membre in zf.namelist():
            base = Path(membre).name
            if base in (data.name, meta.name):  # n'extraire que les deux fichiers attendus
                (dossier / base).write_bytes(zf.read(membre))
    if not (data.exists() and meta.exists()):
        raise RuntimeError(f"{zp} ne contient pas {data.name} / {meta.name}")
    return data, meta


def libelles(theme):
    """{(COD_VAR, COD_MOD): LIB_MOD} et {COD_VAR: LIB_VAR} depuis le fichier metadata."""
    _, meta = fichiers(theme)
    m = pd.read_csv(meta, sep=";", dtype=str, encoding="utf-8")
    m = m[m["COD_VAR"] != "GEO"]
    mods = {(r.COD_VAR, r.COD_MOD): r.LIB_MOD for r in m.itertuples()}
    vars_ = dict(zip(m["COD_VAR"], m["LIB_VAR"]))
    return mods, vars_


def decrire(theme, series):
    """Affiche chaque série avec les libellés INSEE de ses modalités (dimensions non totales)."""
    mods, vars_ = libelles(theme)
    print(f"   Correspondances ({SOURCES[theme][1]}) :")
    for nom, spec in series.items():
        parts = []
        for d, v in spec.items():
            lib = mods.get((d, v), "?")
            parts.append(f"{d}={v} « {lib} »")
        print(f"     {nom:<12} = " + " ; ".join(parts) + " ; autres dimensions = _T (Total)")


def lire(theme, series, niveaux=("COM", "ARM"), annee=ANNEE, chunksize=2_000_000):
    """
    series : {nom: {dimension: modalité}} ; toute dimension non citée vaut « _T ».
    Retourne un DataFrame indexé par (GEO_OBJECT, GEO), une colonne par série (NaN si absente).
    """
    data, _ = fichiers(theme)
    header = pd.read_csv(data, sep=";", nrows=0).columns.tolist()
    dims = [c for c in header if c not in META_COLS]
    specs = {}
    for nom, spec in series.items():
        inconnues = set(spec) - set(dims)
        if inconnues:
            raise ValueError(f"série {nom} : dimensions inconnues {inconnues} (dispo : {dims})")
        specs[nom] = {d: spec.get(d, "_T") for d in dims}
    morceaux = {nom: [] for nom in specs}
    usecols = ["GEO", "GEO_OBJECT", "TIME_PERIOD", "OBS_VALUE"] + dims
    t0 = time.time()
    for ch in pd.read_csv(data, sep=";", dtype=str, usecols=usecols, chunksize=chunksize):
        ch = ch[ch["GEO_OBJECT"].isin(niveaux) & (ch["TIME_PERIOD"] == annee)]
        if ch.empty:
            continue
        for nom, spec in specs.items():
            m = pd.Series(True, index=ch.index)
            for d, v in spec.items():
                m &= ch[d] == v
            if m.any():
                morceaux[nom].append(ch.loc[m, ["GEO_OBJECT", "GEO", "OBS_VALUE"]])
    cols = {}
    for nom, parts in morceaux.items():
        if not parts:
            raise RuntimeError(f"série {nom} introuvable dans {data.name} : {series[nom]}")
        s = pd.concat(parts)
        if s.duplicated(["GEO_OBJECT", "GEO"]).any():
            raise RuntimeError(f"série {nom} : plusieurs lignes par territoire (dimension mal fixée)")
        cols[nom] = pd.to_numeric(s.set_index(["GEO_OBJECT", "GEO"])["OBS_VALUE"], errors="coerce")
    df = pd.DataFrame(cols)
    print(f"   {data.name} lu en {time.time() - t0:.0f} s : "
          + ", ".join(f"{k} {v}" for k, v in df.index.get_level_values(0).value_counts().items()))
    return df


def communes_et_arrondissements(df):
    """Valeurs au niveau commune affiché par l'Atlas : communes (COM) et arrondissements (ARM), indexées par code."""
    out = df.reset_index()
    return out.drop(columns="GEO_OBJECT").set_index("GEO")


def communes_seules(df):
    """Communes seulement (Paris, Lyon, Marseille entiers) : base des sommes département / EPCI, sans double compte."""
    return df.xs("COM", level="GEO_OBJECT")
