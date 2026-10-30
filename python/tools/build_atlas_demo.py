# -*- coding: utf-8 -*-
"""
Atlas - structure par âge (base RP 2023 « Population », DS_RP_POPULATION_PRINC_2023), par commune.

Indicateurs (fusionnés dans atlas/communes, departements.json, epci.json) :
  - jeunes  : % de 0-14 ans
  - ages65  : % de 65 ans et plus
Agrégat dept/EPCI sur les effectifs. Relancer build_territoires_index.py.
"""
import json
from pathlib import Path
from rp2023 import lire, decrire, communes_et_arrondissements, communes_seules

ROOT = Path(__file__).resolve().parents[2]
ATLAS = ROOT / "frontend" / "public" / "data" / "atlas"
COMMUNES = ATLAS / "communes"
EPCI_MAP = ROOT / "python" / "data" / "municipales" / "communes-epci.json"
# Correspondance RP 2021 -> RP 2023 (base DS_RP_POPULATION_PRINC_2023, page INSEE 9005956,
# RP_MEASURE=POP ; table de passage INSEE Table_passage_rp_population-migration.xlsx) :
#   P21_POP             -> AGE=_T, SEX=_T                                   exact
#   P21_POP0014         -> AGE=Y_LT15 « Moins de 15 ans », SEX=_T            exact
#   P21_H65P + P21_F65P -> AGE=Y_GE65 « 65 ans ou plus », SEX=_T (somme des deux sexes)  exact
SERIES = {
    "POP": {"AGE": "_T", "SEX": "_T", "RP_MEASURE": "POP"},
    "POP0014": {"AGE": "Y_LT15", "SEX": "_T", "RP_MEASURE": "POP"},
    "POP65P": {"AGE": "Y_GE65", "SEX": "_T", "RP_MEASURE": "POP"},
}

# (clé, numérateur, dénominateur)
INDICS = [
    ("jeunes", "POP0014", "POP"),
    ("ages65", "POP65P", "POP"),
]



def dep_of(c):
    c = str(c)
    return c[:3] if c[:2] in ("97", "98") else c[:2]


print("Lecture base RP 2023 population (INSEE)...")
decrire("population", SERIES)
tab = lire("population", SERIES)
raw_cols = sorted({c for _, num, den in INDICS for c in (num, den)})


def ratios(row):
    out = {}
    for key, num, den in INDICS:
        d = row[den]
        if d and d > 0:
            out[key] = round(row[num] / d * 100, 1)
    return out


# Niveau commune : communes (dont Paris, Lyon, Marseille entiers) et arrondissements municipaux.
com_vals = {com: ratios(r) for com, r in communes_et_arrondissements(tab).fillna(0).iterrows()}
print(f"   {len(com_vals)} communes")

# Sommes département / EPCI sur les communes seules : les arrondissements ne sont pas ajoutés une
# seconde fois à leur commune (Bouches-du-Rhône, Rhône).
g = communes_seules(tab).fillna(0)

comm_epci = {c["code"]: c.get("codeEpci") for c in json.loads(EPCI_MAP.read_text(encoding="utf-8"))}
dep_sum, ep_sum = {}, {}
for com, r in g.iterrows():
    d = dep_of(com)
    ds = dep_sum.setdefault(d, {c: 0 for c in raw_cols})
    for c in raw_cols:
        ds[c] += r[c]
    ep = comm_epci.get(com)
    if ep:
        es = ep_sum.setdefault(ep, {c: 0 for c in raw_cols})
        for c in raw_cols:
            es[c] += r[c]
dep_vals = {d: ratios(s) for d, s in dep_sum.items()}
ep_vals = {e: ratios(s) for e, s in ep_sum.items()}

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

print(f"-> structure d'âge fusionnée ({len(com_vals)} communes, {len(dep_vals)} dépts, {len(ep_vals)} EPCI)")
ex = dep_vals.get("23", {})
print(f"   ex. Creuse : jeunes {ex.get('jeunes')} %, 65+ {ex.get('ages65')} %")
