# -*- coding: utf-8 -*-
"""
Comparateur international - VALIDATION de l'acces Eurostat + test des candidats (n'ecrit rien).

Meme demarche que la segregation : prouver le tuyau et tester les indicateurs candidats
AVANT de construire le pipeline (vision-et-sujets, section B). Interroge l'API de
dissemination Eurostat (JSON-stat 2.0) et affiche, par indicateur candidat, la valeur et
le rang de la France parmi les pays (agregats ecartes).

Usage :
  python python/tools/validate_eurostat.py            resume compact de tous les candidats
  python python/tools/validate_eurostat.py <code>     classement complet d'un indicateur
"""
import json
import sys
import urllib.request

BASE = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"
H = {"User-Agent": "outsiders/1.0"}

# Candidats a la shortlist. Toutes les dimensions hors geo doivent etre figees par params
# (le script signale celles qui restent libres). sens : 'bas' = une valeur basse est
# favorable, 'haut' = une valeur haute est favorable, None = descriptif.
DATASETS = [
    {
        "code": "gov_10a_main",
        "label": "Dépenses publiques (% du PIB)",
        "params": {"unit": "PC_GDP", "sector": "S13", "na_item": "TE", "time": "2023"},
        "sens": None,
    },
    {
        "code": "ilc_peps01n",
        "label": "Enfants menacés de pauvreté ou d'exclusion (AROPE, moins de 18 ans, %)",
        "params": {"unit": "PC", "sex": "T", "age": "Y_LT18", "time": "2024"},
        "sens": "bas",
    },
    {
        "code": "edat_lfse_14",
        "label": "Décrochage scolaire (18-24 ans, %)",
        "params": {"sex": "T", "age": "Y18-24", "unit": "PC", "wstatus": "POP", "time": "2024"},
        "sens": "bas",
    },
    {
        "code": "ilc_di12",
        "label": "Inégalités de revenu (Gini, 0-100)",
        "params": {"age": "TOTAL", "time": "2024"},
        "sens": "bas",
    },
    {
        "code": "lfsi_emp_a",
        "label": "Emploi des seniors (55-64 ans, %)",
        "params": {"indic_em": "EMP_LFS", "sex": "T", "age": "Y55-64", "unit": "PC_POP", "time": "2024"},
        "sens": "haut",
    },
    {
        "code": "lfsi_neet_a",
        "label": "Jeunes ni en emploi ni en études (NEET 15-29 ans, %)",
        "params": {"sex": "T", "age": "Y15-29", "unit": "PC_POP", "time": "2024"},
        "sens": "bas",
    },
    {
        "code": "demo_minfind",
        "label": "Mortalité infantile (pour 1000 naissances)",
        "params": {"indic_de": "INFMORRT", "time": "2023"},
        "sens": "bas",
    },
    {
        "code": "demo_mlexpec",
        "label": "Espérance de vie à la naissance (années)",
        "params": {"sex": "T", "age": "Y_LT1", "time": "2023"},
        "sens": "haut",
    },
    {
        "code": "lfsa_ewhun2",
        "label": "Heures hebdo effectives des temps pleins (heures)",
        "params": {"sex": "T", "age": "Y20-64", "worktime": "FT", "wstatus": "EMP", "unit": "HR",
                   "nace_r2": "TOTAL", "time": "2024"},
        "sens": None,
    },
    {
        "code": "ilc_lvho07a",
        "label": "Ménages écrasés par le coût du logement (> 40 % du revenu, %)",
        "params": {"age": "TOTAL", "sex": "T", "rskpovth": "TOTAL", "time": "2024"},
        "sens": "bas",
    },
]

# Agregats Eurostat a ecarter des classements (on ne garde que les pays).
AGREGATS = {"EU27_2020", "EA19", "EA20", "EA21", "EU28", "EU27_2007", "EA18"}


def fetch(code, params):
    q = "&".join(f"{k}={v}" for k, v in params.items())
    url = f"{BASE}/{code}?format=JSON&lang=fr&{q}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def jsonstat_rows(data):
    """Decode JSON-stat 2.0 : rend une liste de dicts {dim: (code, label), ..., value}."""
    dims = data["id"]
    sizes = data["size"]
    cats = {}
    for d in dims:
        cat = data["dimension"][d]["category"]
        idx2code = {v: k for k, v in cat["index"].items()}
        cats[d] = {i: (idx2code[i], cat.get("label", {}).get(idx2code[i], idx2code[i]))
                   for i in range(len(idx2code))}
    rows = []
    for key, val in data["value"].items():
        lin = int(key)
        combo = {}
        for d, size in zip(reversed(dims), reversed(sizes)):
            lin, r = divmod(lin, size)
            combo[d] = cats[d][r]
        combo["value"] = val
        rows.append(combo)
    return rows


def classement_pays(ds):
    data = fetch(ds["code"], ds["params"])
    rows = jsonstat_rows(data)
    pays = [r for r in rows if r["geo"][0] not in AGREGATS]
    libres = {}
    for d in (set(rows[0]) - {"geo", "time", "value"} if pays else set()):
        codes = sorted({r[d][0] for r in pays})
        if len(codes) > 1:
            libres[d] = codes[:12]
    return sorted(pays, key=lambda r: r["value"]), libres


def main():
    detail = sys.argv[1] if len(sys.argv) > 1 else None
    for ds in DATASETS:
        if detail and ds["code"] != detail:
            continue
        try:
            classement, libres = classement_pays(ds)
        except Exception as e:
            print(f"\n{ds['code']:14} {ds['label']}\n   ECHEC API : {e}")
            continue
        n = len(classement)
        fr = next((i for i, r in enumerate(classement) if r["geo"][0] == "FR"), None)
        print(f"\n{ds['code']:14} {ds['label']}  [{ds['params'].get('time')}]")
        if libres:
            print(f"   ! dimensions non figees : {libres} (completer params)")
        if fr is None:
            print(f"   {n} pays, France ABSENTE")
            continue
        r = classement[fr]
        lo, hi = classement[0], classement[-1]
        print(f"   France {r['value']:.1f}, rang {fr + 1}/{n} (tri croissant)"
              f"   min {lo['geo'][1]} {lo['value']:.1f}   max {hi['geo'][1]} {hi['value']:.1f}")
        if detail:
            for i, row in enumerate(classement):
                fleche = "  <-- FRANCE" if row["geo"][0] == "FR" else ""
                print(f"   {i + 1:2}. {row['geo'][1][:32]:32} {row['value']:6.1f}{fleche}")


if __name__ == "__main__":
    main()
