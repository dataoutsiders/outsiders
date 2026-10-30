# -*- coding: utf-8 -*-
"""
Atlas - indicateurs LOGEMENT (base RP Logement 2023, INSEE, DS_RP_LOGEMENT_PRINC_2023), par commune.

5 indicateurs (fusionnés dans atlas/communes, departements.json, epci.json) :
  - proprietaires    : % de propriétaires parmi les résidences principales
  - hlm              : % de logements HLM parmi les résidences principales
  - res_secondaires  : % de résidences secondaires parmi les logements
  - vacants          : % de logements vacants parmi les logements
  - maisons          : % de maisons individuelles parmi les logements
Agrégat dept/EPCI sur les effectifs (pas la moyenne des %). Relancer build_territoires_index.py.
"""
import json
from pathlib import Path
from rp2023 import lire, decrire, communes_et_arrondissements, communes_seules, PLM

ROOT = Path(__file__).resolve().parents[2]
ATLAS = ROOT / "frontend" / "public" / "data" / "atlas"
COMMUNES = ATLAS / "communes"
EPCI_MAP = ROOT / "python" / "data" / "municipales" / "communes-epci.json"
# Correspondance RP 2021 -> RP 2023 (base DS_RP_LOGEMENT_PRINC_2023, page INSEE 8997194,
# mesure RP_MEASURE=DWELLINGS « Logements » ; toute dimension non citée = _T « Total ») :
#   P21_LOG        -> OCS=_T                       (ensemble des logements)                 exact
#   P21_RP         -> OCS=DW_MAIN « Résidences principales »                                exact
#   P21_RSECOCC    -> OCS=DW_SEC_DW_OCC « Résidences secondaires et logements occasionnels » exact
#   P21_LOGVAC     -> OCS=DW_VAC « Logements vacants »                                      exact
#   P21_MAISON     -> OCS=_T, TDW=1 « Maison »                                              exact
#   P21_RP_PROP    -> OCS=DW_MAIN, TSH=100 « Propriétaire »                                 exact
#   P21_RP_LOCHLMV -> OCS=DW_MAIN, TSH=221 « Locataire de logement parc social vide »
#     Équivalent le plus proche, PAS strictement identique : l'ancienne variable comptait les
#     « locataires d'un logement HLM loué vide » ; le RP 2023 parle de « parc social » (pas de
#     modalité HLM distincte dans la base).
SERIES = {
    "LOG": {"OCS": "_T", "RP_MEASURE": "DWELLINGS"},
    "RP": {"OCS": "DW_MAIN", "RP_MEASURE": "DWELLINGS"},
    "RSECOCC": {"OCS": "DW_SEC_DW_OCC", "RP_MEASURE": "DWELLINGS"},
    "LOGVAC": {"OCS": "DW_VAC", "RP_MEASURE": "DWELLINGS"},
    "MAISON": {"OCS": "_T", "TDW": "1", "RP_MEASURE": "DWELLINGS"},
    "RP_PROP": {"OCS": "DW_MAIN", "TSH": "100", "RP_MEASURE": "DWELLINGS"},
    "RP_LOCHLMV": {"OCS": "DW_MAIN", "TSH": "221", "RP_MEASURE": "DWELLINGS"},
}

# (clé indicateur, numérateur, dénominateur)
INDICS = [
    ("proprietaires", "RP_PROP", "RP"),
    ("hlm", "RP_LOCHLMV", "RP"),
    ("res_secondaires", "RSECOCC", "LOG"),
    ("vacants", "LOGVAC", "LOG"),
    ("maisons", "MAISON", "LOG"),
]



def dep_of(c):
    c = str(c)
    return c[:3] if c[:2] in ("97", "98") else c[:2]


print("Lecture base RP 2023 logement (INSEE, 1,2 Go, lecture par morceaux)...")
decrire("logement", SERIES)
tab = lire("logement", SERIES)
raw_cols = list(SERIES)


def ratios(row):
    out = {}
    for key, num, den in INDICS:
        d = row[den]
        if d and d > 0:
            out[key] = round(row[num] / d * 100, 1)
    return out


# Niveau commune : communes + arrondissements. Comme avec l'ancienne base IRIS, les communes entières
# 75056 / 13055 / 69123 ne reçoivent pas de valeur (seuls leurs arrondissements en ont).
gc = communes_et_arrondissements(tab).fillna(0)
gc = gc[~gc.index.isin(PLM)]
com_vals = {com: ratios(r) for com, r in gc.iterrows()}
print(f"   {len(com_vals)} communes")

# Sommes département / EPCI sur les communes seules (Paris, Lyon, Marseille entiers) : les métropoles
# incluent leur ville-centre, sans double compte avec les arrondissements.
g = communes_seules(tab).fillna(0)

# Agrégat département + EPCI (somme des effectifs)
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

# Fusion atlas
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

print(f"-> logement fusionné ({len(com_vals)} communes, {len(dep_vals)} dépts, {len(ep_vals)} EPCI)")
ex = dep_vals.get("75", {})
print(f"   ex. Paris : HLM {ex.get('hlm')} %, propriétaires {ex.get('proprietaires')} %, vacants {ex.get('vacants')} %")
