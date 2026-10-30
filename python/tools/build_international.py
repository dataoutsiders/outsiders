# -*- coding: utf-8 -*-
"""
Comparateur international - « Où se situe la France ? » (vision-et-sujets, section B).

Construit l'unité PAYS du moteur generique UnitView : la shortlist des 8 indicateurs
(validee le 2026-07-04 sur candidats testes par validate_eurostat.py) est recuperee
sur l'API Eurostat et ecrite au format decoupage.

Referentiel commun : UE27 + AELE (Islande, Norvege, Suisse) = 30 pays. Le Royaume-Uni
ne publie plus dans Eurostat depuis 2020, les pays candidats ont trop de trous : ecartes
pour garder des rangs comparables. Valeur manquante = null (UnitView affiche « n/d »).
La moyenne UE27 est ecrite en `references` (repere affiche par le moteur).

Sortie : frontend/public/data/decoupages/pays.json
Ensuite : entree `pays` dans frontend/src/config/decoupages.js (deja cablee), redeployer.
"""
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "frontend" / "public" / "data" / "decoupages" / "pays.json"

BASE = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"
H = {"User-Agent": "outsiders/1.0"}
BROWSER = "https://ec.europa.eu/eurostat/databrowser/view/{code}/default/table?lang=fr"

# UE27 + AELE hors Liechtenstein (pas de donnees sur la plupart des jeux).
REFERENTIEL = [
    "BE", "BG", "CZ", "DK", "DE", "EE", "IE", "EL", "ES", "FR", "HR", "IT", "CY",
    "LV", "LT", "LU", "HU", "MT", "NL", "AT", "PL", "PT", "RO", "SI", "SK", "FI",
    "SE", "IS", "NO", "CH",
]
EU_REF = "EU27_2020"  # agregat ecrit en reference (repere), pas dans le classement

# La shortlist validee (8 indicateurs, 4 paires editoriales). Millesimes mis a jour le
# 2026-10-30 : depenses publiques, pauvrete des enfants, decrochage, Gini, emploi des seniors et heures
# des temps pleins 2025 ; sante 2024 (derniers publies). Les parametres figent
# toutes les dimensions hors geo (regle actee lors de la validation).
INDICATEURS = [
    {
        "id": "dep_publiques",
        "code": "gov_10a_main",
        "annee": "2025",
        "params": {"unit": "PC_GDP", "sector": "S13", "na_item": "TE", "time": "2025"},
        "label": "Dépenses publiques (% du PIB)",
    },
    {
        "id": "pauvrete_enfants",
        "code": "ilc_peps01n",
        "annee": "2025",
        "params": {"unit": "PC", "sex": "T", "age": "Y_LT18", "time": "2025"},
        "label": "Enfants menacés de pauvreté ou d'exclusion (%)",
    },
    {
        "id": "esperance_vie",
        "code": "demo_mlexpec",
        "annee": "2024",
        "params": {"sex": "T", "age": "Y_LT1", "time": "2024"},
        "label": "Espérance de vie à la naissance (années)",
    },
    {
        "id": "mortalite_infantile",
        "code": "demo_minfind",
        "annee": "2024",
        "params": {"indic_de": "INFMORRT", "time": "2024"},
        "label": "Mortalité infantile (pour 1000 naissances)",
    },
    {
        "id": "decrochage",
        "code": "edat_lfse_14",
        "annee": "2025",
        "params": {"sex": "T", "age": "Y18-24", "unit": "PC", "wstatus": "POP", "time": "2025"},
        "label": "Décrochage scolaire des 18-24 ans (%)",
    },
    {
        "id": "gini",
        "code": "ilc_di12",
        "annee": "2025",
        "params": {"age": "TOTAL", "time": "2025"},
        "label": "Inégalités de revenu (Gini, 0-100)",
    },
    {
        "id": "emploi_seniors",
        "code": "lfsi_emp_a",
        "annee": "2025",
        "params": {"indic_em": "EMP_LFS", "sex": "T", "age": "Y55-64", "unit": "PC_POP", "time": "2025"},
        "label": "Emploi des 55-64 ans (%)",
    },
    {
        "id": "heures_tp",
        "code": "lfsa_ewhun2",
        "annee": "2025",
        "params": {"sex": "T", "age": "Y20-64", "worktime": "FT", "wstatus": "EMP", "unit": "HR",
                   "nace_r2": "TOTAL", "time": "2025"},
        "label": "Heures hebdomadaires des temps pleins (heures)",
    },
]

COULEUR_FR = "#3B82F6"
COULEUR_AUTRES = "#64748B"
SERIES_DEPUIS = 1995  # debut des trajectoires France vs UE27


def fetch(code, params):
    q = "&".join(f"{k}={v}" for k, v in params.items())
    url = f"{BASE}/{code}?format=JSON&lang=fr&{q}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def jsonstat_geo_values(data):
    """{code geo: valeur} + {code geo: label fr}. Exige que seule geo varie (hors time)."""
    dims = data["id"]
    sizes = data["size"]
    libres = [d for d, s in zip(dims, sizes) if s > 1 and d not in ("geo", "time")]
    if libres:
        raise RuntimeError(f"dimensions non figees : {libres}")
    geo = data["dimension"]["geo"]["category"]
    idx2code = {v: k for k, v in geo["index"].items()}
    labels = geo.get("label", {})
    # index lineaire : geo est la seule dimension libre -> la position dans l'index suffit,
    # a un facteur pres si une dimension de taille 1 suit geo dans l'ordre des dimensions.
    stride = 1
    after = False
    for d, s in zip(dims, sizes):
        if after:
            stride *= s
        if d == "geo":
            after = True
    vals = {}
    for key, v in data["value"].items():
        gi = (int(key) // stride) % len(idx2code)
        vals[idx2code[gi]] = v
    noms = {c: labels.get(c, c).split(" (")[0] for c in idx2code.values()}
    return vals, noms


def jsonstat_rows(data):
    """Decode JSON-stat 2.0 generique : liste de dicts {dim: code, ..., value}."""
    dims = data["id"]
    sizes = data["size"]
    cats = {}
    for d in dims:
        idx = data["dimension"][d]["category"]["index"]
        cats[d] = {v: k for k, v in idx.items()}
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


def fetch_series(ind):
    """Trajectoire France + UE27 depuis SERIES_DEPUIS : [{a, fr, ue}] trie par annee."""
    params = {k: v for k, v in ind["params"].items() if k != "time"}
    q = "&".join(f"{k}={v}" for k, v in params.items())
    url = f"{BASE}/{ind['code']}?format=JSON&lang=fr&{q}&geo=FR&geo={EU_REF}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=120) as r:
        data = json.loads(r.read().decode("utf-8"))
    par_annee = {}
    for row in jsonstat_rows(data):
        try:
            a = int(row["time"])
        except (KeyError, ValueError):
            continue
        if a < SERIES_DEPUIS or row["value"] is None:
            continue
        d = par_annee.setdefault(a, {})
        if row["geo"] == "FR":
            d["fr"] = round(row["value"], 1)
        elif row["geo"] == EU_REF:
            d["ue"] = round(row["value"], 1)
    return [{"a": a, "fr": v.get("fr"), "ue": v.get("ue")}
            for a, v in sorted(par_annee.items())]


def main():
    valeurs = {}     # id indicateur -> {pays: valeur}
    references = {}  # id indicateur -> moyenne UE27
    noms_pays = {}
    print("Recuperation Eurostat (8 indicateurs, referentiel 30 pays)...")
    for ind in INDICATEURS:
        data = fetch(ind["code"], ind["params"])
        vals, noms = jsonstat_geo_values(data)
        noms_pays.update({c: n for c, n in noms.items() if c in REFERENTIEL})
        valeurs[ind["id"]] = {c: vals.get(c) for c in REFERENTIEL}
        references[ind["id"]] = vals.get(EU_REF)
        manquants = [c for c in REFERENTIEL if vals.get(c) is None]
        if valeurs[ind["id"]].get("FR") is None:
            raise RuntimeError(f"France absente de {ind['code']} : verifier les parametres")
        print(f"   {ind['id']:20} {ind['code']:14} FR={valeurs[ind['id']]['FR']:6.1f}"
              f"  UE27={references[ind['id']] if references[ind['id']] is not None else 'n/d'}"
              f"  manquants: {','.join(manquants) if manquants else 'aucun'}")

    print("Trajectoires France vs UE27...")
    series = {}
    for ind in INDICATEURS:
        s = fetch_series(ind)
        series[ind["id"]] = s
        avec_ue = sum(1 for p in s if p.get("ue") is not None)
        print(f"   {ind['id']:20} {len(s)} années ({s[0]['a']}-{s[-1]['a']}), UE27 sur {avec_ue}")

    # France en premiere colonne, puis ordre alphabetique francais.
    ordre = ["FR"] + sorted((c for c in REFERENTIEL if c != "FR"),
                            key=lambda c: noms_pays.get(c, c))
    categories = []
    for c in ordre:
        categories.append({
            "id": c.lower(),
            "nom": noms_pays.get(c, c),
            "couleur": COULEUR_FR if c == "FR" else COULEUR_AUTRES,
            "valeurs": {ind["id"]: (round(valeurs[ind["id"]][c], 1)
                                    if valeurs[ind["id"]][c] is not None else None)
                        for ind in INDICATEURS},
        })

    sources = {
        ind["id"]: {
            "label": f"Eurostat, {ind['code']} ({ind['annee']})",
            "full": f"Eurostat, {ind['label']}, jeu {ind['code']}, millésime {ind['annee']}.",
            "url": BROWSER.format(code=ind["code"]),
        }
        for ind in INDICATEURS
    }

    annees = sorted({ind["annee"] for ind in INDICATEURS})
    millesimes = annees[0] if len(annees) == 1 else f"{annees[0]}-{annees[-1]}"
    out = {
        "id": "pays",
        "note": ("30 pays : Union européenne (27), Islande, Norvège, Suisse. Le Royaume-Uni ne "
                 f"publie plus dans Eurostat. Millésimes {millesimes} selon l'indicateur. Repère "
                 "affiché : moyenne UE27. Les définitions sont harmonisées par Eurostat, mais "
                 "chaque enquête garde ses limites nationales."),
        "references": {k: (round(v, 1) if v is not None else None) for k, v in references.items()},
        "sources": sources,
        "series": series,
        "categories": categories,
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n-> {OUT}")
    print(f"   {len(categories)} pays, {len(INDICATEURS)} indicateurs")


if __name__ == "__main__":
    main()
