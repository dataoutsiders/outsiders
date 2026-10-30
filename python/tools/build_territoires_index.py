# -*- coding: utf-8 -*-
"""
Territoires, index de recherche + repères nationaux (HORS-LIGNE, aucun téléchargement).

Lit les JSON déjà construits par build_atlas_communes.py + l'index code→nom local, et émet :
  - frontend/public/data/atlas/territoires-index.json
        { "deps":[[code,nom],...], "communes":[[code,nom,dep],...],
          "epci":[[siren,nom,dep principal],...], "regions":[[code,nom],...] }
        (communes ayant au moins un indicateur ; intercommunalités de atlas/epci.json ; régions de
        atlas/regions.json, produit par build_territoires_echelles.py ; sert à la recherche)
  - frontend/public/data/atlas/stats-nationales.json
        { "<indicateur>": { "dept": {median,p10,p25,p75,p90,min,max,n},
                            "commune": {...} }, ... }
        (repères de distribution, pour situer un territoire et pour le tableau de bord national)

À relancer si les données de l'atlas changent (après build_atlas_communes.py).
"""
import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
ATLAS = ROOT / "frontend" / "public" / "data" / "atlas"
DEPTS = ATLAS / "departements.json"
COMMUNES = ATLAS / "communes"
EPCI = ROOT / "python" / "data" / "municipales" / "communes-epci.json"

# (id indicateur, clé au niveau département, clé au niveau commune)
INDICATEURS = [
    ("ips_ecole_public", "ips_ecole_public", "ips_ecole_public"),
    ("ips_college_public", "ips_college_public", "ips_college_public"),
    ("ips_lycee_public", "ips_lycee_public", "ips_lycee_public"),
    ("va_lycee", "va_lycee", "va_lycee"),
    ("revenu", "revenu", "revenu"),
    ("prix_m2", "prix_m2", "prix_m2"),
    ("idp", "idp_candidats", "idp"),
    ("diplome_sup", "diplome_sup", "diplome_sup"),
    ("hlm", "hlm", "hlm"),
    ("res_secondaires", "res_secondaires", "res_secondaires"),
    ("vacants", "vacants", "vacants"),
    ("proprietaires", "proprietaires", "proprietaires"),
    ("maisons", "maisons", "maisons"),
    ("jeunes", "jeunes", "jeunes"),
    ("ages65", "ages65", "ages65"),
    ("natalite", "natalite", "natalite"),
    ("cadres", "cadres", "cadres"),
    ("intermediaires", "intermediaires", "intermediaires"),
    ("employes", "employes", "employes"),
    ("ouvriers", "ouvriers", "ouvriers"),
    ("apl_mg", "apl_mg", "apl_mg"),
    ("apl_mg_60", "apl_mg_60", "apl_mg_60"),
    ("apl_dentistes", "apl_dentistes", "apl_dentistes"),
    ("apl_kines", "apl_kines", "apl_kines"),
    ("apl_infirmieres", "apl_infirmieres", "apl_infirmieres"),
    ("apl_sages_femmes", "apl_sages_femmes", "apl_sages_femmes"),
    ("depassement_spe", "depassement_spe", None),
    ("secteur2_spe", "secteur2_spe", None),
]


def dep_of(c):
    c = str(c)
    return c[:3] if c[:2] in ("97", "98") else c[:2]


# Planchers de plausibilité : écarte les valeurs aberrantes des sources brutes
# (ex. quelques prix DVF à 1 €/m² au niveau communal) qui pollueraient le « min » affiché.
FLOORS = {"prix_m2": 100, "revenu": 1000}


def stats(values, floor=None):
    """Repères de distribution d'une liste de nombres (ignore les manquants/aberrants)."""
    v = np.array([x for x in values if x is not None], dtype=float)
    v = v[~np.isnan(v)]
    if floor is not None:
        v = v[v >= floor]
    if v.size == 0:
        return None
    p10, p25, p50, p75, p90 = (round(float(x), 1) for x in np.percentile(v, [10, 25, 50, 75, 90]))
    return {
        "median": p50, "p10": p10, "p25": p25, "p75": p75, "p90": p90,
        "min": round(float(v.min()), 1), "max": round(float(v.max()), 1), "n": int(v.size),
    }


print("Chargement des données de l'atlas...")
deps = json.loads(DEPTS.read_text(encoding="utf-8"))
# code commune -> dict d'indicateurs (union de tous les fichiers département)
communes = {}
for f in sorted(COMMUNES.glob("*.json")):
    for code, rec in json.loads(f.read_text(encoding="utf-8")).items():
        communes[code] = rec
print(f"   {len(deps)} départements, {len(communes)} communes avec données")

print("Index code commune -> nom (communes-epci.json)...")
nom_par_code = {c["code"]: c["nom"] for c in json.loads(EPCI.read_text(encoding="utf-8"))}

# ---- Index de recherche -------------------------------------------------
deps_index = [[d["code"], d.get("dep", d["code"])] for d in deps]
communes_index = []
sans_nom = 0
for code in communes:
    nom = nom_par_code.get(code)
    if nom is None:
        sans_nom += 1
        continue
    communes_index.append([code, nom, dep_of(code)])
communes_index.sort(key=lambda x: x[1])
# Intercommunalités et régions (fiches de la page Territoires, adressées par ?niveau=epci|region).
epci_index = []
epci_communes = ATLAS / "epci-communes.json"
dep_principal = json.loads(epci_communes.read_text(encoding="utf-8")) if epci_communes.exists() else {}
for e in json.loads((ATLAS / "epci.json").read_text(encoding="utf-8")):
    epci_index.append([e["code"], e.get("nom") or e["code"], (dep_principal.get(e["code"]) or {}).get("dep")])
epci_index.sort(key=lambda x: x[1])
regions_fp = ATLAS / "regions.json"
regions_index = ([[r["code"], r["nom"]] for r in json.loads(regions_fp.read_text(encoding="utf-8"))["regions"]]
                 if regions_fp.exists() else [])
index = {"deps": deps_index, "communes": communes_index, "epci": epci_index, "regions": regions_index}
(ATLAS / "territoires-index.json").write_text(
    json.dumps(index, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print(f"-> territoires-index.json ({len(deps_index)} dépts, {len(communes_index)} communes,"
      f" {sans_nom} sans nom ignorées, {len(epci_index)} intercommunalités, {len(regions_index)} régions)")

# Tranches de population (communes) : un même indicateur n'est pas « atypique »
# de la même façon dans un village et dans une grande ville. Bornes partagées avec
# popBracket() de frontend/src/lib/territoire.js.
def pop_bracket(p):
    if p is None:
        return None
    if p < 1000:
        return "0"
    if p < 5000:
        return "1"
    if p < 20000:
        return "2"
    if p < 100000:
        return "3"
    return "4"


# ---- Repères nationaux --------------------------------------------------
stats_nat = {}
for ind_id, dkey, ckey in INDICATEURS:
    floor = FLOORS.get(ind_id)
    s_dep = stats([d.get(dkey) for d in deps], floor)
    s_com = stats([r.get(ckey) for r in communes.values()], floor)
    # Distribution de l'indicateur par tranche de taille de commune.
    par_tranche = {}
    for rec in communes.values():
        b = pop_bracket(rec.get("pop"))
        if b is not None and rec.get(ckey) is not None:
            par_tranche.setdefault(b, []).append(rec.get(ckey))
    tranches = {b: s for b, vals in par_tranche.items() if (s := stats(vals, floor))}
    stats_nat[ind_id] = {"dept": s_dep, "commune": s_com, "tranches": tranches}
(ATLAS / "stats-nationales.json").write_text(
    json.dumps(stats_nat, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print("-> stats-nationales.json")
for ind_id in stats_nat:
    sc = stats_nat[ind_id]["commune"]
    print(f"   {ind_id:20s} commune: médiane={sc['median'] if sc else '–'} (n={sc['n'] if sc else 0})")
print("Terminé.")
