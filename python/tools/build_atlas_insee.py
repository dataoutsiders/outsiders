# -*- coding: utf-8 -*-
"""
Atlas - indicateurs issus des bases communales INSEE (recensement).

Phase B, indicateur par indicateur. Lit une base INSEE (module rp2023), calcule la valeur par commune,
agrège à département et EPCI, et FUSIONNE dans les fichiers atlas existants :
  - atlas/communes/<dep>.json   (clé par commune)
  - atlas/departements.json
  - atlas/epci.json

Indicateur courant : DIPLÔME = part de diplômés du supérieur (bac+2 ou plus) parmi les
non-scolarisés de 15 ans et plus (recensement 2023, base communale DS_RP_DIPLOMES_PRINC_2023).
Relancer ensuite build_territoires_index.py (stats-nationales).
"""
import json
from pathlib import Path
from rp2023 import lire, decrire, communes_et_arrondissements, communes_seules, PLM

ROOT = Path(__file__).resolve().parents[2]
ATLAS = ROOT / "frontend" / "public" / "data" / "atlas"
COMMUNES = ATLAS / "communes"
EPCI_MAP = ROOT / "python" / "data" / "municipales" / "communes-epci.json"

KEY = "diplome_sup"

# Correspondance RP 2021 -> RP 2023 (base DS_RP_DIPLOMES_PRINC_2023, page INSEE 9006527 ; la base
# porte sur la population de 15 ans ou plus non scolarisée, comme P21_NSCOL15P) :
#   P21_NSCOL15P       -> AGE=Y_GE15, EDUC=_T
#   P21_NSCOL15P_SUP2  -> EDUC=500_RP « Enseignement supérieur de cycle court : BTS, DUT, Deug... bac+2 »
#   P21_NSCOL15P_SUP34 -> EDUC=600_RP « Baccalauréat universitaire ou équivalent : licence... bac+3 ou bac+4 »
#   P21_NSCOL15P_SUP5  -> EDUC=700_RP « Diplôme de niveau bac + 5 ou plus »
# (table de passage INSEE Table_passage_rp_formation.xlsx : correspondances exactes).
SERIES = {
    "nscol": {"AGE": "Y_GE15", "EDUC": "_T", "RP_MEASURE": "POP"},
    "sup2": {"AGE": "Y_GE15", "EDUC": "500_RP", "RP_MEASURE": "POP"},
    "sup34": {"AGE": "Y_GE15", "EDUC": "600_RP", "RP_MEASURE": "POP"},
    "sup5": {"AGE": "Y_GE15", "EDUC": "700_RP", "RP_MEASURE": "POP"},
}



def dep_of(c):
    c = str(c)
    return c[:3] if c[:2] in ("97", "98") else c[:2]


print("Lecture base RP 2023 diplômes-formation (INSEE)...")
decrire("diplomes", SERIES)
tab = lire("diplomes", SERIES)


def prep(t):
    t = t.copy()
    t["sup"] = t["sup2"].fillna(0) + t["sup34"].fillna(0) + t["sup5"].fillna(0)
    return t.dropna(subset=["nscol"])


# Niveau commune : communes + arrondissements municipaux. Comme avec l'ancienne base IRIS (dont la
# colonne COM donnait les arrondissements pour Paris, Lyon, Marseille), les communes entières
# 75056 / 13055 / 69123 ne reçoivent pas de valeur : seuls leurs arrondissements en ont.
g = prep(communes_et_arrondissements(tab))
g = g[~g.index.isin(PLM)]
com_pct = {c: round(r.sup / r.nscol * 100, 1) for c, r in g.iterrows() if r.nscol and r.nscol > 0}
print(f"   {len(com_pct)} communes")

# Sommes département / EPCI sur les communes seules (Paris, Lyon, Marseille entiers) : chaque habitant
# compté une fois, et les métropoles (Grand Paris, Lyon, Aix-Marseille) incluent leur ville-centre.
g = prep(communes_seules(tab))

# Agrégat département + EPCI (sur les effectifs, pas la moyenne des %)
comm_epci = {c["code"]: c.get("codeEpci") for c in json.loads(EPCI_MAP.read_text(encoding="utf-8"))}
dep_sup, dep_ns, ep_sup, ep_ns = {}, {}, {}, {}
for com, r in g.iterrows():
    if not (r.nscol and r.nscol > 0):
        continue
    d = dep_of(com)
    dep_sup[d] = dep_sup.get(d, 0) + r.sup
    dep_ns[d] = dep_ns.get(d, 0) + r.nscol
    ep = comm_epci.get(com)
    if ep:
        ep_sup[ep] = ep_sup.get(ep, 0) + r.sup
        ep_ns[ep] = ep_ns.get(ep, 0) + r.nscol
dep_pct = {d: round(dep_sup[d] / dep_ns[d] * 100, 1) for d in dep_sup if dep_ns[d] > 0}
ep_pct = {e: round(ep_sup[e] / ep_ns[e] * 100, 1) for e in ep_sup if ep_ns[e] > 0}

# Fusion dans les fichiers atlas
print("Fusion dans l'atlas...")
n_com = 0
for fp in sorted(COMMUNES.glob("*.json")):
    data = json.loads(fp.read_text(encoding="utf-8"))
    changed = False
    for code in data:
        if code in com_pct:
            data[code][KEY] = com_pct[code]
            changed = True
            n_com += 1
    if changed:
        fp.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

deps = json.loads((ATLAS / "departements.json").read_text(encoding="utf-8"))
for d in deps:
    if d["code"] in dep_pct:
        d[KEY] = dep_pct[d["code"]]
(ATLAS / "departements.json").write_text(json.dumps(deps, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

epci = json.loads((ATLAS / "epci.json").read_text(encoding="utf-8"))
for e in epci:
    if e["code"] in ep_pct:
        e[KEY] = ep_pct[e["code"]]
(ATLAS / "epci.json").write_text(json.dumps(epci, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

print(f"-> {KEY} fusionné : {n_com} communes, {len(dep_pct)} départements, {len(ep_pct)} EPCI")
print(f"   ex. national : Paris(75) {dep_pct.get('75')} %, Creuse(23) {dep_pct.get('23')} %")
