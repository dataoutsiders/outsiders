# -*- coding: utf-8 -*-
"""
Atlas - population par commune / département / EPCI (champ technique `pop`).

Ajoute la population municipale 2023 (base RP 2023 DS_RP_POPULATION_PRINC_2023, page
INSEE 9005956, AGE=_T, SEX=_T, RP_MEASURE=POP : équivalent exact de l'ancienne P21_POP)
à chaque enregistrement de l'atlas. Ce champ n'est PAS un
indicateur affiché : il sert au moteur de résidus (filtre et pondération par
taille) et au futur jumeau statistique. À relancer si l'atlas est régénéré.
"""
import json
from pathlib import Path
from rp2023 import lire, decrire, communes_et_arrondissements, communes_seules

ROOT = Path(__file__).resolve().parents[2]
ATLAS = ROOT / "frontend" / "public" / "data" / "atlas"
COMMUNES = ATLAS / "communes"
EPCI_MAP = ROOT / "python" / "data" / "municipales" / "communes-epci.json"
SERIES = {"POP": {"AGE": "_T", "SEX": "_T", "RP_MEASURE": "POP"}}
KEY = "pop"



def dep_of(c):
    c = str(c)
    return c[:3] if c[:2] in ("97", "98") else c[:2]


print("Lecture base RP 2023 population (INSEE)...")
decrire("population", SERIES)
tab = lire("population", SERIES)
pop = communes_et_arrondissements(tab)["POP"].fillna(0)
com_pop = {c: int(round(v)) for c, v in pop.items() if v > 0}
print(f"   {len(com_pop)} communes")

comm_epci = {c["code"]: c.get("codeEpci") for c in json.loads(EPCI_MAP.read_text(encoding="utf-8"))}
# La base donne la commune entière (75056/13055/69123, GEO_OBJECT=COM) ET ses arrondissements
# municipaux (751xx/132xx/693xx, GEO_OBJECT=ARM) : la SOMME dept/EPCI ne porte que sur les communes,
# pour ne pas compter Paris/Lyon/Marseille deux fois (le niveau commune garde tout).
dep_pop, ep_pop = {}, {}
for c, v in communes_seules(tab)["POP"].fillna(0).items():
    v = int(round(v))
    if v <= 0:
        continue
    dep_pop[dep_of(c)] = dep_pop.get(dep_of(c), 0) + v
    e = comm_epci.get(c)
    if e:
        ep_pop[e] = ep_pop.get(e, 0) + v

print("Fusion dans l'atlas...")
for fp in sorted(COMMUNES.glob("*.json")):
    data = json.loads(fp.read_text(encoding="utf-8"))
    changed = False
    for code in data:
        if code in com_pop:
            data[code][KEY] = com_pop[code]
            changed = True
    if changed:
        fp.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

deps = json.loads((ATLAS / "departements.json").read_text(encoding="utf-8"))
for d in deps:
    if d["code"] in dep_pop:
        d[KEY] = dep_pop[d["code"]]
(ATLAS / "departements.json").write_text(json.dumps(deps, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

epci = json.loads((ATLAS / "epci.json").read_text(encoding="utf-8"))
for e in epci:
    if e["code"] in ep_pop:
        e[KEY] = ep_pop[e["code"]]
(ATLAS / "epci.json").write_text(json.dumps(epci, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

print(f"-> population fusionnée ({len(com_pop)} communes, {len(dep_pop)} dépts, {len(ep_pop)} EPCI)")
print(f"   ex. Paris(75)={dep_pop.get('75')}, Creuse(23)={dep_pop.get('23')}")
