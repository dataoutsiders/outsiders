# -*- coding: utf-8 -*-
"""
Terrain « Qui represente qui ? » : l'Assemblee nationale, 17e legislature.

Croise pour chaque groupe politique : sexe, age, famille socioprofessionnelle INSEE
(fournie par l'AN, pas de recodage) et diversite des noms (IDP, meme referentiel
surnames.tsv que l'outil et le dossier Elus). Ajoute le portrait des COLLABORATEURS
parlementaires (2 000+, listes par depute avec civilite + nom) : parite et IDP,
par groupe. References population sourcees (INSEE, TEPP) pour lire chaque ecart.

Source : open data AN (AMO10, deputes actifs + mandats actifs + organes), cache local
dans _cache_assemblee/ (vider pour re-telecharger, ex. apres un remaniement de groupes).

Sortie : frontend/public/data/showcases/assemblee.json
"""
import io
import json
import re
import unicodedata
import urllib.request
import zipfile
from collections import Counter
from datetime import date
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
REPO_ROOT = SCRIPT_DIR.parent.parent
ONO_DIR = REPO_ROOT / "frontend" / "public" / "data" / "onomastics"
OUT = REPO_ROOT / "frontend" / "public" / "data" / "showcases" / "assemblee.json"
CACHE = SCRIPT_DIR / "_cache_assemblee"
CACHE.mkdir(exist_ok=True)
H = {"User-Agent": "outsiders/1.0"}

URLS = [
    "https://data.assemblee-nationale.fr/static/openData/repository/17/amo/deputes_actifs_mandats_actifs_organes/AMO10_deputes_actifs_mandats_actifs_organes.json.zip",
]

# References population, verifiees le 2026-07-04 (chaque ecart se lit contre la France reelle).
REF_PCS = {  # actifs occupes, INSEE enquete Emploi 2023 (France hors Mayotte)
    "agriculteurs": 1.5, "artisans": 6.7, "cadres": 22.4,
    "intermediaires": 25.1, "employes": 25.2, "ouvriers": 18.6,
}
REF_FEMMES = 51.5   # part des femmes dans la population, INSEE 1er janvier 2025
REF_IDP = 7.0       # baseline population du referentiel (onomastics/meta.json, TEPP 2023)

PCS_LABELS = {
    "agriculteurs": "Agriculteurs exploitants",
    "artisans": "Artisans, commerçants, chefs d'entreprise",
    "cadres": "Cadres et professions intellectuelles supérieures",
    "intermediaires": "Professions intermédiaires",
    "employes": "Employés",
    "ouvriers": "Ouvriers",
    "sans": "Sans profession déclarée",
}

# Groupes politiques : couleur et ordre d'affichage (hemicycle, gauche -> droite).
GROUPES_META = [
    ("GDR", "#991B1B"), ("LFI-NFP", "#DC2626"), ("ECOS", "#16A34A"), ("SOC", "#EC4899"),
    ("LIOT", "#0D9488"), ("DEM", "#F97316"), ("EPR", "#EAB308"), ("HOR", "#38BDF8"),
    ("DR", "#2563EB"), ("UDDPLR", "#4338CA"), ("RN", "#1E3A8A"), ("NI", "#9CA3AF"),
]
ORDRE = {s: i for i, (s, _) in enumerate(GROUPES_META)}
COULEURS = dict(GROUPES_META)


# --- Normalisation et referentiel IDP : identiques au moteur (build_showcase_elus) ---
def normaliser(nom):
    if nom is None:
        return ""
    s = str(nom).upper().strip()
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = s.replace("'", " ").replace("’", " ")
    s = re.sub(r"\s+", " ", s)
    return s.strip()


print("Chargement du référentiel surnames.tsv...")
divers_set, known_set = set(), set()
with open(ONO_DIR / "surnames.tsv", encoding="utf-8") as f:
    for line in f:
        nom, flag = line.rstrip("\n").split("\t")
        known_set.add(nom)
        if flag == "1":
            divers_set.add(nom)


def idp_flag(nom):
    n = normaliser(nom)
    if n in divers_set:
        return True
    if n in known_set:
        return False
    return None


# --- Open data AN ---
def get(d, *keys):
    for k in keys:
        if not isinstance(d, dict):
            return None
        d = d.get(k)
    return d


def txt(v):
    if isinstance(v, dict):
        v = v.get("#text")
    return v if isinstance(v, str) and v.strip() else None


def fetch_zip():
    cached = CACHE / "amo10.zip"
    if cached.exists():
        return cached.read_bytes()
    for url in URLS:
        with urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=300) as r:
            blob = r.read()
        cached.write_bytes(blob)
        return blob


def fam_id(fam):
    f = (fam or "").lower()
    for prefix, fid in [("agriculteurs", "agriculteurs"), ("artisans", "artisans"),
                        ("cadres", "cadres"), ("professions inter", "intermediaires"),
                        ("employ", "employes"), ("ouvriers", "ouvriers"), ("sans", "sans")]:
        if f.startswith(prefix):
            return fid
    if fam:
        print(f"   ! famille inconnue : {fam}")
    return "sans"


print("Chargement open data AN (AMO10, 17e législature)...")
zf = zipfile.ZipFile(io.BytesIO(fetch_zip()))
organes = {}
for n in (x for x in zf.namelist() if "/organe/" in x and x.endswith(".json")):
    o = json.loads(zf.read(n).decode("utf-8")).get("organe", {})
    organes[get(o, "uid")] = (get(o, "codeType"), txt(get(o, "libelleAbrev")), txt(get(o, "libelle")))

annee = date.today().year
deputes = []
noms_groupes = {}
for n in (x for x in zf.namelist() if "/acteur/" in x and x.endswith(".json")):
    a = json.loads(zf.read(n).decode("utf-8")).get("acteur", {})
    nais = txt(get(a, "etatCivil", "infoNaissance", "dateNais"))
    groupe, collabs = None, []
    mandats = get(a, "mandats", "mandat") or []
    if isinstance(mandats, dict):
        mandats = [mandats]
    for m in mandats:
        if get(m, "typeOrgane") == "GP" and get(m, "dateFin") is None:
            ref = get(m, "organes", "organeRef")
            if ref in organes:
                groupe = organes[ref][1] or organes[ref][2]
                noms_groupes[groupe] = organes[ref][2]
        col = get(m, "collaborateurs", "collaborateur")
        if col:
            if isinstance(col, dict):
                col = [col]
            collabs = [{"femme": txt(c.get("qualite")) == "Mme", "idp": idp_flag(txt(c.get("nom")))}
                       for c in col]
    deputes.append({
        "femme": txt(get(a, "etatCivil", "ident", "civ")) == "Mme",
        "age": annee - int(nais[:4]) if nais else None,
        "fam": fam_id(txt(get(a, "profession", "socProcINSEE", "famSocPro"))),
        "idp": idp_flag(txt(get(a, "etatCivil", "ident", "nom"))),
        "groupe": groupe or "NI",
        "collabs": collabs,
    })
print(f"   {len(deputes)} députés, {sum(len(d['collabs']) for d in deputes)} collaborateurs")


# --- Agregats ---
def pct(part, total):
    return round(part / total * 100, 1) if total else None


# Diversité des noms : une part n'est publiée qu'à partir de 30 noms reconnus. En dessous,
# un pourcentage décrirait presque des personnes (14 noms et 7,1 % = un seul député).
MIN_NOMS = 30


def idp_publiable(valeurs):
    return pct(sum(valeurs), len(valeurs)) if len(valeurs) >= MIN_NOMS else None


def agg(sub):
    n = len(sub)
    ages = [d["age"] for d in sub if d["age"] is not None]
    idp = [d["idp"] for d in sub if d["idp"] is not None]
    pcs_counts = Counter(d["fam"] for d in sub)
    cols = [c for d in sub for c in d["collabs"]]
    cols_idp = [c["idp"] for c in cols if c["idp"] is not None]
    return {
        "n": n,
        "femmes_pct": pct(sum(d["femme"] for d in sub), n),
        "age_moyen": round(sum(ages) / len(ages), 1) if ages else None,
        "idp_pct": idp_publiable(idp),
        "idp_n_reconnus": len(idp),
        "pcs": {fid: pct(pcs_counts.get(fid, 0), n) for fid in PCS_LABELS},
        "pcs_n": {fid: pcs_counts.get(fid, 0) for fid in PCS_LABELS},
        "collaborateurs": {
            "n": len(cols),
            "par_depute": round(len(cols) / n, 1) if n else None,
            "femmes_pct": pct(sum(c["femme"] for c in cols), len(cols)),
            "idp_pct": idp_publiable(cols_idp),
            "idp_n_reconnus": len(cols_idp),
        },
    }


groupes = []
for sigle in sorted({d["groupe"] for d in deputes}, key=lambda s: ORDRE.get(s, 99)):
    sub = [d for d in deputes if d["groupe"] == sigle]
    g = {"sigle": sigle, "nom": noms_groupes.get(sigle, sigle),
         "couleur": COULEURS.get(sigle, "#9CA3AF"), **agg(sub)}
    groupes.append(g)

out = {
    "generated": date.today().isoformat(),
    "legislature": 17,
    "titre": "Qui représente qui ? L'Assemblée au miroir de la France",
    "sources": {
        "assemblee": {"label": "Open data Assemblée nationale (députés en exercice, 17e législature)",
                      "url": "https://data.assemblee-nationale.fr/acteurs/deputes-en-exercice"},
        "pcs": {"label": "INSEE, enquête Emploi 2023 (actifs occupés par catégorie socioprofessionnelle)",
                "url": "https://www.insee.fr/fr/statistiques/7767045"},
        "femmes": {"label": "INSEE, population par sexe et âge au 1er janvier 2025",
                   "url": "https://www.insee.fr/fr/statistiques/2381474"},
        "idp": {"label": "Kheddache M., L'Horty Y. (2023), Indice de Diversité Patronymique, rapport TEPP",
                "url": "https://www.tepp.eu/"},
    },
    "references": {"pcs": REF_PCS, "femmes": REF_FEMMES, "idp": REF_IDP},
    "pcs_labels": PCS_LABELS,
    "ensemble": agg(deputes),
    "groupes": groupes,
    "notes": [
        "La catégorie socioprofessionnelle est celle déclarée par le député (nomenclature INSEE fournie par l'AN), figée au moment du mandat.",
        "La référence PCS porte sur les actifs occupés : « sans profession déclarée » n'a pas d'équivalent population.",
        "L'IDP est un proxy attaché au nom, fiable en agrégé, bruité à l'individu ; il est calculé sur les noms reconnus par le référentiel.",
        "Petits groupes : les pourcentages sur moins de 20 personnes sont indicatifs.",
        "Les collaborateurs sont listés par l'AN avec civilité et nom : parité et diversité mesurables, mais ni carrières ni conditions de travail.",
    ],
}
OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"-> {OUT}")

e = out["ensemble"]
print(f"\nEnsemble : {e['n']} deputes, femmes {e['femmes_pct']}%, age {e['age_moyen']}, "
      f"IDP {e['idp_pct']}% ({e['idp_n_reconnus']} reconnus), cadres {e['pcs']['cadres']}%, "
      f"ouvriers {e['pcs_n']['ouvriers']}")
c = e["collaborateurs"]
print(f"Collaborateurs : {c['n']} ({c['par_depute']}/depute), femmes {c['femmes_pct']}%, "
      f"IDP {c['idp_pct']}% ({c['idp_n_reconnus']} reconnus)")
print("\nPar groupe (hemicycle) :")
for g in groupes:
    print(f"   {g['sigle']:8} n={g['n']:3}  femmes {str(g['femmes_pct']):5}%  age {g['age_moyen']}  "
          f"IDP {str(g['idp_pct']):5}%  cadres {str(g['pcs']['cadres']):5}%  ouvriers n={g['pcs_n']['ouvriers']}")
