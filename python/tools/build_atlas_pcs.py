# -*- coding: utf-8 -*-
"""
Atlas - composition sociale (PCS) à partir de la base RP 2023 « Emploi-Population active »
(exploitation complémentaire, lieu de résidence : DS_RP_EMPLOI_LR_COMP_2023).

Indicateurs (parmi les actifs occupés de 15 à 64 ans classés par CSP, CS1 à CS6) :
  - cadres         (CS3)
  - intermediaires (CS4)
  - employes       (CS5)
  - ouvriers       (CS6)
Agrégat dept/EPCI sur les effectifs.
Relancer build_territoires_index.py.
"""
import json
from pathlib import Path
import pandas as pd
from rp2023 import lire, decrire, communes_et_arrondissements, communes_seules

ROOT = Path(__file__).resolve().parents[2]
ATLAS = ROOT / "frontend" / "public" / "data" / "atlas"
COMMUNES = ATLAS / "communes"
EPCI_MAP = ROOT / "python" / "data" / "municipales" / "communes-epci.json"

# Correspondance RP 2021 -> RP 2023. Avec la base 2021, le préfixe auto-détecté était C21_ACTOCC1564
# (actifs occupés de 15 à 64 ans, exploitation complémentaire). Équivalent 2023 (base
# DS_RP_EMPLOI_LR_COMP_2023, page INSEE 9002680 ; table de passage Table_passage_rp_emploi.xlsx) :
#   C21_ACTOCC1564_CS<k> -> AGE=Y15T64 « De 15 à 64 ans », EMPSTA_ENQ=1 « Actif occupé », PCS=<k>  exact
# (PCS 1 Agriculteurs, 2 Artisans, commerçants et chefs d'entreprise, 3 Cadres et professions
# intellectuelles supérieures, 4 Professions intermédiaires, 5 Employés, 6 Ouvriers).
prefix = "ACTOCC1564"
SERIES = {f"{prefix}_CS{k}": {"AGE": "Y15T64", "EMPSTA_ENQ": "1", "PCS": str(k), "RP_MEASURE": "POP"}
          for k in range(1, 7)}

# clé indicateur -> numéro de CSP
INDICS = [("cadres", 3), ("intermediaires", 4), ("employes", 5), ("ouvriers", 6)]



def dep_of(c):
    c = str(c)
    return c[:3] if c[:2] in ("97", "98") else c[:2]


print("Lecture base RP 2023 emploi-population active, exploitation complémentaire (INSEE)...")
decrire("emploi_comp", SERIES)
tab = lire("emploi_comp", SERIES).fillna(0)
cs_cols = [f"{prefix}_CS{k}" for k in range(1, 7)]
tab["CSACT"] = tab[cs_cols].sum(axis=1)
agg_cols = cs_cols + ["CSACT"]


def ratios(row):
    den = row["CSACT"]
    if not den or den <= 0:
        return {}
    return {key: round(row[f"{prefix}_CS{k}"] / den * 100, 1) for key, k in INDICS}


# Niveau commune : communes (dont Paris, Lyon, Marseille entiers) et arrondissements municipaux.
com_vals = {com: ratios(r) for com, r in communes_et_arrondissements(tab).iterrows()}
print(f"   {len(com_vals)} communes")

# Sommes département / EPCI sur les communes seules (pas de double compte des arrondissements).
g = communes_seules(tab)

comm_epci = {c["code"]: c.get("codeEpci") for c in json.loads(EPCI_MAP.read_text(encoding="utf-8"))}
dep_sum, ep_sum = {}, {}
for com, r in g.iterrows():
    d = dep_of(com)
    ds = dep_sum.setdefault(d, {c: 0 for c in agg_cols})
    for c in agg_cols:
        ds[c] += r[c]
    ep = comm_epci.get(com)
    if ep:
        es = ep_sum.setdefault(ep, {c: 0 for c in agg_cols})
        for c in agg_cols:
            es[c] += r[c]
dep_vals = {d: ratios(pd.Series(s)) for d, s in dep_sum.items()}
ep_vals = {e: ratios(pd.Series(s)) for e, s in ep_sum.items()}

print("Fusion dans l'atlas...")
for fp in sorted(COMMUNES.glob("*.json")):
    data = json.loads(fp.read_text(encoding="utf-8"))
    changed = False
    for code in data:
        if code in com_vals and com_vals[code]:
            data[code].update(com_vals[code])
            changed = True
    if changed:
        fp.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

deps = json.loads((ATLAS / "departements.json").read_text(encoding="utf-8"))
for d in deps:
    if d["code"] in dep_vals:
        d.update(dep_vals[d["code"]])
(ATLAS / "departements.json").write_text(json.dumps(deps, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

epci = json.loads((ATLAS / "epci.json").read_text(encoding="utf-8"))
for e in epci:
    if e["code"] in ep_vals:
        e.update(ep_vals[e["code"]])
(ATLAS / "epci.json").write_text(json.dumps(epci, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

print(f"-> PCS fusionnée ({len(com_vals)} communes, {len(dep_vals)} dépts, {len(ep_vals)} EPCI)")
ex = dep_vals.get("75", {})
print(f"   ex. Paris : cadres {ex.get('cadres')} %, ouvriers {ex.get('ouvriers')} %")
