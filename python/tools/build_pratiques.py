# -*- coding: utf-8 -*-
"""
Dossier « Modes de vie » : pratiques, corps et milieu social.

Sources :
  - INCA 3 (Anses, 2014-2015, data.gouv.fr), adultes de 18 à 79 ans ayant rempli les questionnaires
    (Pop2, pondération pond_indiv_adu_pop2) ; consommations et apports sur la Pop3 (pond_indiv_adu_pop3).
  - Baromètre de Santé publique France 2024 (Odissé) : indicateurs par région.
  - Assurance maladie (data.ameli.fr, jeu `effectifs`, 2024) : patients pris en charge par département.

Méthode INCA 3 :
  - ACM pondérée sur 60 variables (aliments, achats, critères de choix, sources d'information,
    activités). Âge, sexe, diplôme, PCS, revenu, santé ne participent pas au calcul : ils sont projetés.
    Taux d'inertie corrigés de Benzécri. Individus gardés : au plus 10 % de réponses manquantes, le reste
    imputé par la modalité la plus fréquente.
  - Part de variance : valeurs de Shapley du R² pondéré par blocs de variables.
  - Écarts : moindres carrés pondérés ; intervalles à 95 % par linéarisation au premier degré du plan de
    sondage (strates `strate`, unités primaires `zae`, sans correction de population finie, donc prudents).
  - Tests multiples des activités : Benjamini-Hochberg, seuil q < 0,10.
  - Limite majeure : l'âge n'est connu qu'en 3 classes (18-44, 45-64, 65 et plus).

Assurance maladie : standardisation indirecte (les petits effectifs par âge sont masqués) :
    taux standardisé = patients observés / patients attendus avec les taux France par âge et sexe * taux France

Émet frontend/public/data/showcases/pratiques.json et frontend/public/data/geo/regions.geojson.
Fichiers sources en cache dans _cache_inca3/ et _cache_pratiques/.
"""
import itertools
import json
import re
import time
import urllib.parse
import urllib.request
import warnings
from math import factorial
from pathlib import Path

import numpy as np
import pandas as pd
import patsy
from scipy.stats import norm
from statsmodels.stats.multitest import multipletests

from rp2023 import UA

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[2]
PUB = ROOT / "frontend" / "public" / "data"
OUT = PUB / "showcases" / "pratiques.json"
GEO = PUB / "geo" / "regions.geojson"
INCA = Path(__file__).resolve().parent / "_cache_inca3"
CACHE = Path(__file__).resolve().parent / "_cache_pratiques"
INCA_BASE = "https://static.data.gouv.fr/resources/donnees-de-consommations-et-habitudes-alimentaires-de-letude-inca-3/"
TABLES = {
    "description-indiv.csv": "20191217-184957/description-indiv.csv",
    "habitudes-indiv.csv": "20191217-185001/habitudes-indiv.csv",
    "habitudes-men.csv": "20191217-185002/habitudes-men.csv",
    "actphys-sedent.csv": "20200117-101839/actphys-sedent.csv",
    "fpq.csv": "20200117-101546/fpq.csv",
    "conso-gpe-inca3.csv": "20191217-184955/conso-gpe-inca3.csv",
    "apports-nut-alim.csv": "20191217-184954/apports-nut-alim.csv",
}
ODISSE = "https://odisse.santepubliquefrance.fr/api/explore/v2.1/catalog/datasets/"
AMELI = "https://data.ameli.fr/api/explore/v2.1/catalog/datasets/effectifs/exports/json?"
GEOJSON = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/regions-version-simplifiee.geojson"
ANNEE_AMELI = "2024"
SEUIL_Q = 0.10
SEUIL_N = 30  # pas de pourcentage publié sous cet effectif

REGIONS = {
    "11": "Île-de-France", "24": "Centre-Val de Loire", "27": "Bourgogne-Franche-Comté", "28": "Normandie",
    "32": "Hauts-de-France", "44": "Grand Est", "52": "Pays de la Loire", "53": "Bretagne",
    "75": "Nouvelle-Aquitaine", "76": "Occitanie", "84": "Auvergne-Rhône-Alpes",
    "93": "Provence-Alpes-Côte d'Azur", "94": "Corse", "01": "Guadeloupe", "02": "Martinique",
    "03": "Guyane", "04": "La Réunion",
}
CODE_REGION = {v: k for k, v in REGIONS.items()} | {"Ile-de-France": "11", "Réunion": "04"}


def fetch(url, tries=4, timeout=300):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
                return r.read()
        except Exception as e:
            print("   retry", i + 1, e)
            time.sleep(3)
    raise RuntimeError(url)


def table(nom):
    fp = INCA / nom
    if not fp.exists():
        INCA.mkdir(exist_ok=True)
        fp.write_bytes(fetch(INCA_BASE + TABLES[nom]))
    return pd.read_csv(fp, sep=";", encoding="utf-8-sig", low_memory=False)


def api_json(nom, url):
    CACHE.mkdir(exist_ok=True)
    fp = CACHE / nom
    if not fp.exists():
        fp.write_bytes(fetch(url))
    return json.loads(fp.read_text(encoding="utf-8"))


def r1(v):
    return None if v is None or (isinstance(v, float) and np.isnan(v)) else round(float(v), 1)


def r2(v):
    return None if v is None or (isinstance(v, float) and np.isnan(v)) else round(float(v), 2)


# ---------------------------------------------------------------------------
# 1. INCA 3 : population et variables
# ---------------------------------------------------------------------------
print("Lecture INCA 3...")
desc = table("description-indiv.csv")
adultes = desc[desc.ech == 1]
x = desc[(desc.ech == 1) & (desc.pop2 == 1)].copy()
act_tab = table("actphys-sedent.csv")
act_tab = act_tab[act_tab.POPULATION.astype(str).str.startswith("Pop2")].drop(columns=["POPULATION"])
x = (x.merge(table("habitudes-indiv.csv").drop(columns=["POPULATION"]), on="NOIND", how="left", suffixes=("", "_h"))
     .merge(act_tab, on="NOIND", how="left", suffixes=("", "_a"))
     .merge(table("fpq.csv").drop(columns=["POPULATION"]), on="NOIND", how="left", suffixes=("", "_f"))
     .merge(table("habitudes-men.csv").drop(columns=["POPULATION"], errors="ignore"), on="NOMEN", how="left", suffixes=("", "_m"))
     .merge(table("apports-nut-alim.csv")[["NOIND", "nutriment28"]], on="NOIND", how="left")
     .merge(table("conso-gpe-inca3.csv").drop(columns=["POPULATION"]), on="NOIND", how="left"))
x = x[x.pond_indiv_adu_pop2.notna()].copy()
x["w"] = x.pond_indiv_adu_pop2 / x.pond_indiv_adu_pop2.mean()
x["w3"] = x.pond_indiv_adu_pop3 / x.pond_indiv_adu_pop3.mean()
print(f"   {len(x)} adultes")

# (variable, thème, libellés {modalité: texte affiché})
actives = {}


def ajoute(nom, serie, theme, libelles):
    actives[nom] = {"s": serie, "theme": theme, "lib": libelles}


ALIMENTS = {
    "PC_paincomplet": ("pain complet", "de pain complet"), "RP_pdt_frites": ("frites", "de frites"),
    "LEG_salade": ("salade", "de salade"), "LEG_legsecs": ("légumes secs", "de légumes secs"),
    "LEG_soupe": ("soupe", "de soupe"), "VC_boeuf": ("boeuf", "de boeuf"), "VC_agneau": ("agneau", "d'agneau"),
    "VC_saucisson": ("saucisson", "de saucisson"), "PPM_poissgras_tot": ("poisson gras", "de poisson gras"),
    "PPM_surimi": ("surimi", "de surimi"), "PPM_crustace": ("crustacés", "de crustacés"),
    "PL_fromage_laitcru": ("fromage au lait cru", "de fromage au lait cru"),
    "PL_yaourt_arom": ("yaourt aromatisé", "de yaourt aromatisé"),
    "FR_fruitexotique": ("fruits exotiques", "de fruits exotiques"), "BIS_biscuit": ("biscuits", "de biscuits"),
    "BIS_chips": ("chips", "de chips"), "BIS_viennoiserie": ("viennoiseries", "de viennoiseries"),
    "OE_quiche": ("quiche", "de quiche"), "SOJ_soja": ("soja", "de soja"),
}
for c, (lab, de) in ALIMENTS.items():
    on = x[c + "_ON"]
    fr = x[c + "_freq_M"].where(on == 1, 0)
    med = fr[fr > 0].median()
    s = pd.Series(np.where(fr <= 0, "jamais", np.where(fr <= max(med, 1), "parfois", "souvent")), index=x.index)
    s[on.isna()] = np.nan
    ajoute(lab, s, "Aliments", {"jamais": f"jamais {de}", "parfois": f"{lab}, parfois", "souvent": f"{lab}, souvent"})
LIEU = {1: "grande surface", 2: "marché", 3: "proximité", 4: "jamais"}
ajoute("achat légumes", x.lieu_achat_legumes_frais.map(LIEU), "Achats", {"grande surface": "légumes en grande surface", "marché": "légumes au marché", "proximité": "légumes chez le primeur"})
ajoute("achat viande", x.lieu_achat_viandes.map(LIEU), "Achats", {"grande surface": "viande en grande surface", "marché": "viande au marché", "proximité": "viande chez le boucher", "jamais": "n'achète pas de viande"})
ajoute("bio", x.consommation_bio_type.map({0: "non", 1: "un peu", 2: "régulier"}), "Achats", {"non": "pas de bio", "un peu": "un peu de bio", "régulier": "bio régulier"})
ajoute("autoproduction", x.autoconsommation.map({0: "non", 1: "oui"}), "Achats", {"oui": "produit une partie de ses aliments", "non": "ne produit rien soi-même"})
ajoute("fast-food", x.restaurationrapide_freq.map(lambda v: np.nan if pd.isna(v) or v == 8 else ("hebdo" if v <= 4 else "mensuel" if v == 5 else "rare")), "Repas", {"hebdo": "fast-food chaque semaine", "mensuel": "fast-food chaque mois", "rare": "fast-food rare ou jamais"})
ajoute("déjeuner", x.lieu_repas_midi.map({1: "domicile", 2: "cantine", 3: "travail", 4: "domicile", 5: "dehors", 6: "dehors"}), "Repas", {"domicile": "déjeune à la maison", "cantine": "déjeune à la cantine", "travail": "déjeune au travail", "dehors": "déjeune dehors"})
for c, lab in {"table_mayonnaise": "mayonnaise", "table_ketchup": "ketchup", "table_huile_olive": "huile d'olive"}.items():
    ajoute(lab, x[c].map({0: "non", 1: "oui"}), "Repas", {"oui": f"{lab} sur la table", "non": f"pas de {lab} sur la table"})
CHOIX = {"prix": "le prix", "offres_promo": "les promotions", "marque": "la marque", "habitude": "l'habitude", "gout": "le goût",
         "origine": "l'origine", "mode_prod": "le mode de production", "signe_quali": "les labels", "compo_nutri": "la composition", "facilite_prepa": "la facilité"}
for c, lab in CHOIX.items():
    ajoute("choix " + c, x["choix_aliment_" + c].map({0: "non", 1: "oui"}), "Représentations", {"oui": f"choisit selon {lab}", "non": f"ne choisit pas selon {lab}"})
SOURCES = {"internet": "internet", "livres": "les livres", "journaux": "la presse", "medecins": "les médecins", "emissions_info": "la télé et la radio", "famille": "la famille"}
for c, lab in SOURCES.items():
    ajoute("source " + c, x["source_" + c].map({1: "oui", 2: "non"}), "Représentations", {"oui": f"s'informe par {lab}", "non": f"ne s'informe pas par {lab}"})
ajoute("étiquettes", x.etiquette_freq.map(lambda v: np.nan if pd.isna(v) or v == 5 else ("souvent" if v <= 2 else "peu")), "Représentations", {"souvent": "lit les étiquettes", "peu": "lit peu les étiquettes"})
ACTIVITES = {
    "jardinage": ["jardiner"], "bricolage": ["bricoler"], "randonnée": ["randonnee"], "jogging": ["jogging"], "yoga": ["yoga"],
    "natation": ["natation", "piscine"], "vélo": ["velo", "cyclisme"], "danse de salon": ["danse_salon"],
    "ski, tennis, voile, golf, équitation": ["ski", "tennis", "voile", "golf", "equitation"],
    "sports collectifs, combat": ["foot", "rugby", "basket", "hand", "volley", "boxe"],
    "pêche, chasse": ["peche", "chasse"], "fitness": ["gym", "aerobic", "haltere", "rameur"], "bowling, billard": ["bowling", "billard"],
}
pratique = {}
for lab, cols in ACTIVITES.items():
    s = (x[["activite_" + c + "_score" for c in cols]].fillna(0) > 0).any(axis=1).where(x.activite_total_score.notna())
    pratique[lab] = s
    ajoute(lab, s.map({True: "oui", False: "non"}), "Activités", {"oui": lab, "non": f"pas de {lab}"})
ajoute("activité physique", x.nap.map({1: "faible", 2: "modérée", 3: "élevée"}), "Activités", {"faible": "activité physique faible", "modérée": "activité physique modérée", "élevée": "activité physique élevée"})
ajoute("sédentarité", x.sedentarite.map({0: "faible", 1: "modérée", 2: "élevée"}), "Activités", {"faible": "sédentarité faible", "modérée": "sédentarité modérée", "élevée": "sédentarité élevée"})

A = pd.DataFrame({k: v["s"] for k, v in actives.items()})
garde = A.isna().mean(axis=1) <= 0.10
A = A[garde].apply(lambda s: s.fillna(s.mode()[0]))
X = x[garde].copy()
print(f"   {A.shape[1]} variables actives, {len(X)} individus gardés")
for k, v in pratique.items():
    X["pr_" + re.sub(r"\W", "", k)] = v[garde].astype(float)

X["age"] = X.tage_PS.map({7: "18-44 ans", 8: "45-64 ans", 9: "65 ans et plus"})
X["sexe"] = X.sex_PS.map({1: "Hommes", 2: "Femmes"})
DIP = ["Primaire ou collège", "Lycée", "Bac +1 à +3", "Bac +4 et plus"]
X["dip"] = X.etude_4cl_interv.map(dict(enumerate(DIP, 1)))
X["pcs"] = X.PCS_8cl_interv.map({1: "Employés", 2: "Ouvriers", 3: "Indépendants", 4: "Indépendants", 5: "Professions intermédiaires", 6: "Cadres", 7: "Retraités", 8: "Autres inactifs"})
REV = ["Moins de 900 €", "900 à 1 340 €", "1 340 à 1 850 €", "1 850 € et plus"]
X["rev"] = X.RUC_4cl.map(dict(enumerate(REV, 1)))
X["ville"] = X.agglo_5cl.map({1: "Rural", 2: "Moins de 20 000 hab.", 3: "20 000 à 100 000 hab.", 4: "Plus de 100 000 hab.", 5: "Agglomération parisienne"})
X["ob"] = np.where(X.imc.isna(), np.nan, (X.imc >= 30) * 100.0)
X["fume_j"] = np.where(X.fume.isna(), np.nan, (X.fume == 1) * 100.0)
X["alcool"] = X.nutriment28
sucres = ["conso_gpe6", "conso_gpe10", "conso_gpe11", "conso_gpe27", "conso_gpe28"]
X["sucres"] = X[sucres].sum(axis=1, min_count=1)
X["brsa"] = X.conso_gpe31
X["gros"] = np.where(X.poids_perception.isin([1, 2, 3]), (X.poids_perception == 2) * 100.0, np.nan)
X["normal"] = np.where(X.poids_perception.isin([1, 2, 3]), (X.poids_perception == 1) * 100.0, np.nan)
X["renonce"] = np.where(X.soins.isin([1, 2]), (X.soins == 1) * 100.0, np.nan)
X["insec"] = np.where(X.IA_statut.notna(), (X.IA_statut > 0) * 100.0, np.nan)


# ---------------------------------------------------------------------------
# 2. Estimation pondérée avec plan de sondage
# ---------------------------------------------------------------------------
PSU = adultes[["strate", "zae"]].drop_duplicates()
N_PSU = PSU.groupby("strate").zae.nunique()


def svy(formule, df, poids="w"):
    """Moindres carrés pondérés, variance linéarisée (strates, unités primaires, domaine = df)."""
    y, M = patsy.dmatrices(formule, df, return_type="dataframe", NA_action="drop")
    idx = y.index
    w = df.loc[idx, poids].values
    Mv, yv = M.values, y.values.ravel()
    XtWX = (Mv * w[:, None]).T @ Mv
    inv = np.linalg.pinv(XtWX)
    b = inv @ ((Mv * w[:, None]).T @ yv)
    e = yv - Mv @ b
    u = pd.DataFrame(Mv * (w * e)[:, None], columns=M.columns)
    u["strate"] = df.loc[idx, "strate"].values
    u["zae"] = df.loc[idx, "zae"].values
    p = Mv.shape[1]
    S = np.zeros((p, p))
    for h, g in u.groupby("strate"):
        z = g.groupby("zae")[list(M.columns)].sum().values
        nh = int(N_PSU.get(h, len(z)))
        if nh < 2:
            continue
        z = np.vstack([z, np.zeros((max(nh - len(z), 0), p))])
        c = z - z.mean(axis=0)
        S += nh / (nh - 1) * c.T @ c
    V = inv @ S @ inv
    return pd.Series(b, index=M.columns), pd.Series(np.sqrt(np.diag(V)), index=M.columns), len(idx)


def moyenne(df, y, poids="w"):
    d = df.dropna(subset=[y, poids])
    if len(d) < SEUIL_N:
        return {"v": None, "n": len(d)}
    b, se, n = svy(f"{y} ~ 1", d, poids)
    return {"v": r1(b.iloc[0]), "ic": r1(1.96 * se.iloc[0]), "n": n}


def niveau(b, se, cle):
    k = next(i for i in b.index if cle in i)
    return {"b": r2(b[k]), "ic": r2(1.96 * se[k])}


# ---------------------------------------------------------------------------
# 3. ACM
# ---------------------------------------------------------------------------
print("Analyse des correspondances multiples...")
Z = pd.get_dummies(A, prefix_sep="=").astype(float)
Q = A.shape[1]
w = X.w.values


def mca(Z, w):
    r = w / w.sum()
    Zv = Z.values
    c = (r[:, None] * Zv).sum(0) / Q
    ok = c > 0
    P_ = (r[:, None] * Zv[:, ok]) / Q
    S = (P_ - np.outer(r, c[ok])) / np.sqrt(np.outer(r, c[ok]))
    U, s, Vt = np.linalg.svd(S, full_matrices=False)
    F = U * s / np.sqrt(r)[:, None]
    G = np.full((Zv.shape[1], len(s)), np.nan)
    G[ok] = (Vt.T * s) / np.sqrt(c[ok])[:, None]
    return s ** 2, F, G, c


ev, F, G, c = mca(Z, w)
ben = np.array([(Q / (Q - 1) * (l - 1 / Q)) ** 2 if l > 1 / Q else 0 for l in ev])
taux = ben / ben.sum() * 100
# Contrôles : inertie totale = K/Q - 1 ; une modalité active est le barycentre de ses individus.
K = int((c > 0).sum())
assert abs(ev.sum() - (K / Q - 1)) < 1e-6, ev.sum()
j0 = list(Z.columns).index("bio=régulier")
masque0 = Z.iloc[:, j0].values == 1
assert abs(np.average(F[masque0, 0], weights=w[masque0]) / np.sqrt(ev[0]) - G[j0, 0]) < 1e-6
ctr = c[:, None] * G ** 2 / ev * 100
# Orientation fixée : axe 1 positif = bio régulier ; axe 2 positif = 65 ans et plus.
sens = [1, 1]
if G[list(Z.columns).index("bio=régulier"), 0] < 0:
    sens[0] = -1
F1, F2 = sens[0] * F[:, 0] / np.sqrt(ev[0]), sens[1] * F[:, 1] / np.sqrt(ev[1])
if np.average(F2[(X.age == "65 ans et plus").values], weights=w[(X.age == "65 ans et plus").values]) < 0:
    sens[1] = -1
    F2 = -F2
X["F1"], X["F2"] = F1, F2
print(f"   axes corrigés : {taux[0]:.1f} %, {taux[1]:.1f} %, {taux[2]:.1f} %")

rng = np.random.default_rng(1)
stab = []
for _ in range(200):
    i = rng.integers(0, len(Z), len(Z))
    _, _, G2, _ = mca(Z.iloc[i], w[i])
    ok = ~np.isnan(G2[:, 0]) & ~np.isnan(G[:, 0])
    stab.append([abs(np.corrcoef(G[ok, k], G2[ok, k])[0, 1]) for k in range(3)])
stab = np.percentile(stab, 5, axis=0)
print("   stabilité (5e centile de |corr|) :", np.round(stab, 3))

modalites = []
for j, col in enumerate(Z.columns):
    var, mod = col.split("=", 1)
    lib = actives[var]["lib"].get(mod)
    if lib is None or np.isnan(G[j, 0]):
        continue
    modalites.append({"label": lib, "theme": actives[var]["theme"], "x": r2(sens[0] * G[j, 0]), "y": r2(sens[1] * G[j, 1]),
                      "ctr1": r1(ctr[j, 0]), "ctr2": r1(ctr[j, 1]), "part": r1(c[j] * Q * 100)})
modalites.sort(key=lambda m: -(m["ctr1"] + m["ctr2"]))
modalites = modalites[:60]


def barycentre(masque, label):
    s = X[masque]
    if len(s) < SEUIL_N:
        return None
    return {"label": label, "x": r2(np.average(s.F1, weights=s.w)), "y": r2(np.average(s.F2, weights=s.w)), "n": len(s)}


PROJ = {"Âge": ("age", ["18-44 ans", "45-64 ans", "65 ans et plus"]), "Sexe": ("sexe", ["Femmes", "Hommes"]), "Diplôme": ("dip", DIP),
        "Revenu par personne": ("rev", REV),
        "Milieu social": ("pcs", ["Ouvriers", "Employés", "Professions intermédiaires", "Cadres", "Indépendants", "Retraités", "Autres inactifs"])}
projections = {b: [p for m in mods if (p := barycentre(X[v] == m, m))] for b, (v, mods) in PROJ.items()}
projections["Santé et précarité"] = [p for p in [
    barycentre(X.ob == 100, "Obésité"), barycentre(X.ob == 0, "Pas d'obésité"),
    barycentre(X.fume_j == 100, "Fume chaque jour"), barycentre(X.fume == 4, "N'a jamais fumé"),
    barycentre(X.gros == 100, "Se juge trop gros"), barycentre(X.renonce == 100, "A renoncé à des soins"),
    barycentre(X.insec == 100, "Insécurité alimentaire"),
] if p]

# Répertoire alimentaire : nombre d'aliments suivis jamais consommés (sur les 19).
noms_aliments = [v[0] for v in ALIMENTS.values()]
X["n_jamais"] = (A[noms_aliments] == "jamais").sum(axis=1)
repertoire = {
    "total": len(noms_aliments), "corr_axe1": r2(np.cov(X.n_jamais, X.F1, aweights=X.w)[0, 1] / np.sqrt(np.cov(X.n_jamais, aweights=X.w) * np.cov(X.F1, aweights=X.w))),
    "corr_axe2": r2(np.cov(X.n_jamais, X.F2, aweights=X.w)[0, 1] / np.sqrt(np.cov(X.n_jamais, aweights=X.w) * np.cov(X.F2, aweights=X.w))),
    "diplome": [{"label": m, **moyenne(X[X.dip == m], "n_jamais")} for m in DIP],
    "age": [{"label": m, **moyenne(X[X.age == m], "n_jamais")} for m in PROJ["Âge"][1]],
}
print("   répertoire :", repertoire)
d_ = X.dropna(subset=["n_jamais", "age", "sexe", "dip", "rev", "pcs", "ville"])
b_, se_, _ = svy("n_jamais ~ C(age)+C(sexe)+C(dip, Treatment('Primaire ou collège'))+C(rev, Treatment('Moins de 900 €'))+C(pcs)+C(ville)", d_)
repertoire["bac4_net"] = niveau(b_, se_, "Bac +4 et plus")
repertoire["revenu_net"] = niveau(b_, se_, "1 850")
print("   net :", repertoire["bac4_net"], repertoire["revenu_net"])

# ---- Part de variance par blocs ---------------------------------------------
BLOCS = {"Âge": "C(age)", "Sexe": "C(sexe)", "Diplôme": "C(dip)", "Revenu": "C(rev)", "PCS": "C(pcs)", "Taille de ville": "C(ville)"}


def r2_wls(y, Mv, w):
    b = np.linalg.lstsq(Mv * np.sqrt(w)[:, None], y * np.sqrt(w), rcond=None)[0]
    e = y - Mv @ b
    m = np.average(y, weights=w)
    return 1 - np.sum(w * e ** 2) / np.sum(w * (y - m) ** 2)


def shapley(y, poids="w"):
    d = X.dropna(subset=[y, poids, "age", "sexe", "dip", "rev", "pcs", "ville"])
    noms = list(BLOCS)
    val = {}
    for k in range(len(noms) + 1):
        for s in itertools.combinations(noms, k):
            if not s:
                val[frozenset()] = 0.0
                continue
            Mv = patsy.dmatrix(" + ".join(BLOCS[i] for i in s), d, return_type="dataframe").values
            val[frozenset(s)] = r2_wls(d[y].values, Mv, d[poids].values)
    p = len(noms)
    parts = {}
    for i in noms:
        autres = [n for n in noms if n != i]
        v = 0.0
        for k in range(p):
            for s in itertools.combinations(autres, k):
                v += factorial(k) * factorial(p - k - 1) / factorial(p) * (val[frozenset(s) | {i}] - val[frozenset(s)])
        parts[i] = r1(v * 100)
    return {"total": r1(val[frozenset(noms)] * 100), "parts": parts, "n": len(d)}


print("Part de variance...")
variances = [
    {"id": "F1", "label": "Axe 1 : consommation choisie", **shapley("F1")},
    {"id": "F2", "label": "Axe 2 : rythmes de vie", **shapley("F2")},
    {"id": "ob", "label": "Obésité", **shapley("ob")},
    {"id": "fume_j", "label": "Tabac quotidien", **shapley("fume_j")},
    {"id": "alcool", "label": "Alcool", **shapley("alcool", "w3")},
    {"id": "sucres", "label": "Produits sucrés", **shapley("sucres", "w3")},
    {"id": "brsa", "label": "Boissons rafraîchissantes", **shapley("brsa", "w3")},
]

# ---------------------------------------------------------------------------
# 4. Écarts : brut, puis contrôlé
# ---------------------------------------------------------------------------
print("Écarts de diplôme...")
R_AS = "C(age)+C(sexe)"
R_TOUT = "C(age)+C(sexe)+C(dip, Treatment('Primaire ou collège'))+C(rev, Treatment('Moins de 900 €'))+C(pcs)+C(ville)"
DIPT = "C(dip, Treatment('Primaire ou collège'))"
RES = {"ob": ("Obésité", "pts", "w"), "fume_j": ("Tabac quotidien", "pts", "w"), "alcool": ("Alcool", "g/j", "w3"),
       "sucres": ("Produits sucrés", "g/j", "w3"), "brsa": ("Boissons rafraîchissantes", "g/j", "w3")}
ecarts = []
for y, (lab, unite, poids) in RES.items():
    d = X.dropna(subset=[y, poids, "age", "sexe", "dip", "rev", "pcs", "ville"])
    modeles = []
    for nom, rhs in [("Écart brut", DIPT), ("À âge et sexe égaux", f"{R_AS}+{DIPT}"),
                     ("Et à revenu égal", f"{R_AS}+{DIPT}+C(rev, Treatment('Moins de 900 €'))"), ("Et à PCS et ville égales", R_TOUT)]:
        b, se, n = svy(f"{y} ~ {rhs}", d, poids)
        modeles.append({"nom": nom, **niveau(b, se, "Bac +4 et plus")})
    b, se, n = svy(f"{y} ~ {R_TOUT}", d, poids)
    entree = {"id": y, "label": lab, "unite": unite, "n": n, "modeles": modeles,
              "revenu_net": niveau(b, se, "1 850"), "femmes_net": niveau(b, se, "T.Hommes"),
              "niveaux": [{"label": m, **moyenne(d[d.dip == m], y, poids)} for m in DIP],
              "revenus": [{"label": m, **moyenne(d[d.rev == m], y, poids)} for m in REV],
              "sexes": [{"label": m, **moyenne(d[d.sexe == m], y, poids)} for m in ["Femmes", "Hommes"]],
              "ages": [{"label": m, **moyenne(d[d.age == m], y, poids)} for m in PROJ["Âge"][1]]}
    if poids == "w3":
        d2 = d[d.sousest1 != 1]
        b2, se2, n2 = svy(f"{y} ~ {R_TOUT}", d2, poids)
        entree["sans_sous_declaration"] = {**niveau(b2, se2, "Bac +4 et plus"), "n": n2}
    ecarts.append(entree)
    print(f"   {lab:26s}", [(m['b'], m['ic']) for m in modeles])

# ---------------------------------------------------------------------------
# 5. Activités à caractéristiques égales
# ---------------------------------------------------------------------------
print("Activités à caractéristiques égales...")
X["nap3"] = np.where(X.nap.isna(), np.nan, (X.nap == 3) * 1.0)
X["sed3"] = np.where(X.sedentarite.isna(), np.nan, (X.sedentarite == 2) * 1.0)
VARS = {"sed3": "Sédentarité élevée", "nap3": "Activité physique élevée"}
VARS.update({"pr_" + re.sub(r"\W", "", k): k.capitalize() for k in ACTIVITES})
CIBLES = {"ob": ("Obésité", "pts", "w"), "fume_j": ("Tabac quotidien", "pts", "w"), "alcool": ("Alcool", "g/j", "w3"), "sucres": ("Produits sucrés", "g/j", "w3")}
lignes = []
for k, lab in VARS.items():
    for y, (_, _, poids) in CIBLES.items():
        d = X.dropna(subset=[y, poids, k, "age", "sexe", "dip", "rev", "pcs", "ville"])
        b, se, n = svy(f"{y} ~ {R_TOUT}+{k}", d, poids)
        lignes.append({"id": k, "label": lab, "y": y, "b": float(b[k]), "se": float(se[k]), "n1": int((d[k] == 1).sum()), "n": n})
Lg = pd.DataFrame(lignes)
Lg["z"] = Lg.b / Lg.se
Lg["p"] = 2 * (1 - norm.cdf(np.abs(Lg.z)))
Lg["q"] = multipletests(Lg.p, method="fdr_bh")[1]
activites = {"tests": len(Lg), "retenus": int((Lg.q < SEUIL_Q).sum()), "cibles": {k: {"label": v[0], "unite": v[1]} for k, v in CIBLES.items()},
             "lignes": [{"id": r.id, "label": r.label, "y": r.y, "b": r2(r.b), "ic": r2(1.96 * r.se), "retenu": bool(r.q < SEUIL_Q), "n1": r.n1, "n": r.n}
                        for r in Lg.itertuples() if r.n1 >= SEUIL_N]}
print(Lg[Lg.q < SEUIL_Q][["label", "y", "b", "se", "q", "n1"]].round(3).to_string(index=False))

# ---------------------------------------------------------------------------
# 6. Le jugement sur son corps
# ---------------------------------------------------------------------------
print("Jugement sur son corps...")
Bins = [(0, 18.5, "< 18,5"), (18.5, 20, "18,5-20"), (20, 22, "20-22"), (22, 24, "22-24"), (24, 25, "24-25"), (25, 27, "25-27"), (27, 30, "27-30"), (30, 35, "30-35"), (35, 99, "35 et +")]
courbe = []
for lo, hi, lab in Bins:
    s = X[(X.imc >= lo) & (X.imc < hi)]
    courbe.append({"label": lab, "centre": r1(s.imc.mean()), **{g[0].lower(): moyenne(s[s.sexe == g], "gros") for g in ["Femmes", "Hommes"]}})
CL = [(18.5, 25, "Poids normal"), (25, 30, "Surpoids"), (30, 99, "Obésité")]
classes = []
for lo, hi, lab in CL:
    s = X[(X.imc >= lo) & (X.imc < hi)]
    classes.append({"label": lab, "n": len(s), "gros": {g: moyenne(s[s.sexe == g], "gros") for g in ["Femmes", "Hommes"]},
                    "diplome": {m: moyenne(s[s.dip == m], "gros") for m in DIP}})
d = X.dropna(subset=["gros", "imc", "age", "sexe", "dip", "rev"])
b, se, n = svy(f"gros ~ C(age)+C(sexe)+{DIPT}+C(rev, Treatment('Moins de 900 €'))+imc", d)
jug_net = {"homme": niveau(b, se, "T.Hommes"), "bac4": niveau(b, se, "Bac +4 et plus"), "revenu": niveau(b, se, "1 850"), "imc": niveau(b, se, "imc"), "n": n}
# Le poids seul ne compare pas des corps de même taille : contrôle à poids et taille égaux.
d = X.dropna(subset=["gros", "poids", "taille", "age", "sexe", "dip", "rev"])
b, se, n = svy(f"gros ~ C(age)+C(sexe)+{DIPT}+C(rev, Treatment('Moins de 900 €'))+poids+taille", d)
jug_net["homme_poids_taille"] = niveau(b, se, "T.Hommes")
b, se, n = svy(f"gros ~ C(age)+C(sexe)+{DIPT}+C(rev, Treatment('Moins de 900 €'))+poids", d)
jug_net["homme_poids_seul"] = niveau(b, se, "T.Hommes")
print("   à poids et taille égaux :", jug_net["homme_poids_taille"], "| à poids seul :", jug_net["homme_poids_seul"],
      "| taille moyenne", d.groupby("sexe").taille.mean().round(1).to_dict())
s = X[(X.imc >= 18.5) & (X.imc < 25)].copy()
s["regime"] = s.regime_maigrir_choix * 100.0
regime = {g: moyenne(s[s.sexe == g], "regime") for g in ["Femmes", "Hommes"]}
print("   net :", jug_net, "| régime poids normal :", regime)

# ---------------------------------------------------------------------------
# 7. Cartes : régions (Baromètre) et départements (Assurance maladie)
# ---------------------------------------------------------------------------
print("Baromètre 2024 par région...")
INDIC_REG = [
    ("tabac", "Tabagisme quotidien", "Tabagisme quotidien", "tabagisme-indicateurs-du-barometre-2024", "Fume chaque jour"),
    ("alcool", "Dépassement des repères de consommation d'alcool", "Dépasse les repères d'alcool", "alcool-indicateurs-du-barometre-2024", "Au-delà des repères de consommation"),
    ("sedentarite", "Sédentarité élevée", "Sédentarité élevée", "sedentarite-indicateurs-du-barometre-de-sante-publique-france-2024-detail-region", "Sédentarité élevée", "sedentarite-indicateurs-du-barometre-2024"),
    ("sport", "Pratique d'activités physiques lors des loisirs : régulièrement", "Activité physique régulière", "activite-physique-indicateurs-du-barometre-de-sante-publique-detail-region", "Activité physique de loisirs régulière", "activite-physique-indicateurs-du-barometre-2024"),
    ("depression", "Episode dépressif caractérisé", "Épisode dépressif", "episodes-depressifs-indicateurs-du-barometre-de-sante-publique-france-2024-detail-region", "Épisode dépressif caractérisé dans l'année", "episodes-depressif-indicateurs-du-barometre-2024"),
]
regions = []
for rid, indic, lab, jeu, sous, *jeu_france in INDIC_REG:
    q = urllib.parse.urlencode({"where": f'indicateur="{indic}" and sexe="Tous"', "limit": -1})
    rows = api_json(f"{rid}.json", f"{ODISSE}{jeu}/exports/json?{q}")
    if jeu_france:
        rows = rows + api_json(f"{rid}-france.json", f"{ODISSE}{jeu_france[0]}/exports/json?{q}")
    out, nat = {}, None
    for r in rows:
        if any(r.get(k) not in (None, "Tous") for k in ("classe_d_age", "diplome", "pcs", "situation_professionnelle", "situation_financiere_percue", "pratique_du_teletravail", "type_de_menage")):
            continue
        reg = str(r.get("nouvelles_regions"))
        code = CODE_REGION.get(reg, reg)
        ligne = {"v": r["estimation"], "inf": r.get("ic_inf"), "sup": r.get("ic_sup"), "n": r.get("effectif_brut")}
        if reg in ("Tous", "France", "France entière", "None"):
            nat = ligne
        elif code in REGIONS:
            out[code] = {"code": code, "nom": REGIONS[code], **ligne}
    regions.append({"id": rid, "label": lab, "sous": sous, "jeu": jeu, "national": nat, "lignes": sorted(out.values(), key=lambda v: -v["v"])})
    print(f"   {lab:32s} {len(out)} régions, France {nat['v'] if nat else 'n/d'}")

print(f"Assurance maladie {ANNEE_AMELI}, standardisation indirecte par département...")
PATHOS = {"PSY_ADD_CAT": ("addictions", "Troubles addictifs pris en charge"), "DIA_CAT_CAT": ("diabete", "Diabète pris en charge")}
departements = []
noms_dep = {d["code"]: d.get("dep", d["code"]) for d in json.loads((PUB / "atlas" / "departements.json").read_text(encoding="utf-8"))}
for top, (pid, lab) in PATHOS.items():
    q = urllib.parse.urlencode({"where": f"annee=date'{ANNEE_AMELI}' and top='{top}'", "select": "cla_age_5,sexe,region,dept,ntop,npop,prev", "limit": -1})
    df = pd.DataFrame(api_json(f"ameli-{pid}.json", AMELI + q))
    fr = df[(df.dept == "999") & (df.region == "99")]
    if fr.empty:
        fr = df[df.dept == "999"].groupby(["cla_age_5", "sexe"], as_index=False)[["ntop", "npop"]].sum()
    tot = fr[(fr.cla_age_5 == "tsage") & (fr.sexe == "9")].iloc[0]
    taux_fr = float(tot.ntop) / float(tot.npop)
    fr = fr[(fr.cla_age_5 != "tsage") & (fr.sexe.isin(["1", "2"]))].copy()
    fr["t"] = fr.ntop.astype(float) / fr.npop.astype(float)
    t_ref = fr.set_index(["cla_age_5", "sexe"]).t.fillna(0)
    lignes_dep = []
    for dep, g in df[df.dept != "999"].groupby("dept"):
        ens = g[(g.cla_age_5 == "tsage") & (g.sexe == "9")]
        det = g[(g.cla_age_5 != "tsage") & (g.sexe.isin(["1", "2"]))]
        if ens.empty or pd.isna(ens.iloc[0].ntop) or dep not in noms_dep:
            continue
        att = sum(float(r.npop) * t_ref.get((r.cla_age_5, r.sexe), 0) for r in det.itertuples() if pd.notna(r.npop))
        lignes_dep.append({"code": dep, "nom": noms_dep[dep], "brut": r2(float(ens.iloc[0].ntop) / float(ens.iloc[0].npop) * 100),
                           "std": r2(float(ens.iloc[0].ntop) / att * taux_fr * 100), "n": int(ens.iloc[0].ntop)})
    lignes_dep.sort(key=lambda v: -v["std"])
    departements.append({"id": pid, "label": lab, "france": r2(taux_fr * 100), "lignes": lignes_dep})
    print(f"   {lab:36s} France {taux_fr*100:.2f} %, {len(lignes_dep)} dép., extrêmes {lignes_dep[0]['nom']} {lignes_dep[0]['std']} / {lignes_dep[-1]['nom']} {lignes_dep[-1]['std']}")

print("Contours des régions...")
if not GEO.exists():
    g = json.loads(fetch(GEOJSON).decode("utf-8"))


    def arrondi(c):
        return [round(c[0], 3), round(c[1], 3)] if isinstance(c[0], (int, float)) else [arrondi(i) for i in c]


    for f in g["features"]:
        f["geometry"]["coordinates"] = arrondi(f["geometry"]["coordinates"])
    GEO.write_text(json.dumps(g, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"   -> {GEO.name} ({GEO.stat().st_size // 1024} Ko)")

# ---------------------------------------------------------------------------
sortie = {
    "meta": {
        "n_acm": len(X), "n_adultes": int(len(x)), "n_conso": int(X.pond_indiv_adu_pop3.notna().sum()), "n_variables": Q, "annees": "2014-2015",
        "inca_url": "https://www.data.gouv.fr/fr/datasets/5df9151d634f415c1a9c1df4/",
        "barometre_url": "https://odisse.santepubliquefrance.fr/explore/dataset/tabagisme-indicateurs-du-barometre-2024",
        "ameli_url": "https://www.data.gouv.fr/datasets/62b31f7b128643f46ea1f848",
    },
    "acm": {"axes": [r1(taux[0]), r1(taux[1])], "stabilite": [r2(stab[0]), r2(stab[1])], "modalites": modalites, "projections": projections, "repertoire": repertoire},
    "variances": variances, "ecarts": ecarts, "activites": activites,
    "jugement": {"courbe": courbe, "classes": classes, "net": jug_net, "regime": regime},
    "regions": regions, "departements": departements,
}
OUT.write_text(json.dumps(sortie, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print(f"-> {OUT.name} ({OUT.stat().st_size // 1024} Ko)")
