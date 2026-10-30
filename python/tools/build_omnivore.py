# -*- coding: utf-8 -*-
"""
Répertoire alimentaire et classes populaires : test de la thèse de l'omnivore (Peterson et Kern, 1996),
INCA 3 (Anses, 2014-2015), prix Insee (prix moyens de vente au détail, moyenne 2014-2015).

Aucune liste d'aliments n'est classée à la main. Deux critères objectifs, testés séparément :
  - majoritaire : consommé au moins une fois par mois par plus de la moitié des adultes ;
  - pas cher    : prix au kilo (ou au litre) sous la médiane des aliments couverts par l'Insee.
La question posée : ce que consomment davantage les classes populaires correspond-il à l'un de ces
critères, aux deux, ou à aucun ? Classes populaires et classes supérieures sont définies de trois façons,
gardées séparées : PCS (ouvriers, employés / cadres, professions intermédiaires ; retraités à part dans
l'enquête, donc écartés), diplôme (primaire-collège / bac +4), revenu par personne (< 900 € / >= 1 850 €).

Tests :
  T1 Ampleur       : le répertoire mensuel s'élargit-il avec le diplôme, à caractéristiques égales ? Et sans
                     les fruits et légumes ?
  T2 Artefact      : mesure indépendante du questionnaire (aliments différents dans les rappels de 24 h).
  T3 Critères      : écart de chaque aliment entre classes, puis lien avec les deux critères, séparément.
  T4 Exclusions    : aliments que les plus diplômés consomment moins (Bryson, 1996).
  T5 Types         : classes latentes, sans a priori.
  T6 Génération    : interaction diplôme × âge.
  T7 Robustesse    : seuil annuel ; sans porc ni alcool ; hors régimes ; seuil médian au lieu de 50 %.

Limites : déclaratif, âge en 3 classes, prix au kilo seulement (28 aliments sur 62, pas de produits
industriels), intervalles de premier degré (strates, unités primaires). Une seule enquête ne permet pas de
tester le récit historique de Peterson.
Émet frontend/public/data/showcases/omnivore.json. Tables dans _cache_inca3/, prix dans _cache_pratiques/.
"""
import json
import warnings
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
import pandas as pd
import patsy
from scipy.stats import norm
from statsmodels.stats.multitest import multipletests

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "frontend" / "public" / "data" / "showcases" / "omnivore.json"
INCA = Path(__file__).resolve().parent / "_cache_inca3"
PRIX_XML = Path(__file__).resolve().parent / "_cache_pratiques" / "ipc-pm.xml"
PRIX_URL = "https://www.bdm.insee.fr/series/sdmx/data/IPC-PM-2015?startPeriod=2014-01&endPeriod=2015-12&detail=full"
SEUIL_Q = 0.05
SEUIL_MAJ = 50.0
SEUIL_N = 30
GRAINE = 7

# Aliments feuilles du questionnaire (sans totaux, sous-totaux ni variantes de saison).
ALIMENTS = {
    "PC_paincomplet": "Pain complet", "PC_cereales_pdj_complet": "Céréales complètes", "PC_cereales_pdj_autre": "Céréales de petit-déjeuner",
    "RP_riz_complet": "Riz complet", "RP_pdt_frites": "Frites", "RP_legumeracine": "Légumes-racines", "RP_tubercule": "Tubercules",
    "LEG_salade": "Salade", "LEG_bettera_tot": "Betterave, carotte", "LEG_concombre": "Concombre", "LEG_tomate_seul": "Tomate",
    "LEG_chou": "Chou", "LEG_artichaut": "Artichaut", "LEG_champignon": "Champignons", "LEG_oignon": "Oignon",
    "LEG_legsecs": "Légumes secs", "LEG_soupe": "Soupe", "LEG_saucetomate": "Sauce tomate",
    "VC_boeuf": "Boeuf", "VC_agneau": "Agneau", "VC_poulet": "Poulet", "VC_lapin": "Lapin", "VC_porc": "Porc",
    "VC_saucisson": "Saucisson", "VC_pate_foie": "Pâté de foie", "VC_pate_autre": "Pâté, terrine", "VC_foie": "Foie",
    "PPM_poissgras_tot": "Poisson gras", "PPM_poissonautre": "Autre poisson", "PPM_surimi": "Surimi", "PPM_crustace": "Crustacés", "PPM_mollusque": "Mollusques",
    "OE_oeuf": "Oeufs", "OE_quiche": "Quiche", "SOJ_soja": "Soja", "PL_lait": "Lait", "PL_fromage_laitcru": "Fromage au lait cru",
    "PL_yaourt_arom": "Yaourt aromatisé", "PL_entremet": "Crème dessert", "PL_yaourtentremet_light": "Laitages allégés", "PL_glace": "Glace",
    "FR_agrume": "Agrumes", "FR_pomme": "Pomme", "FR_raisin": "Raisin", "FR_melon": "Melon", "FR_peche": "Pêche", "FR_fraise": "Fraise", "FR_fruitexotique": "Fruits exotiques",
    "BIS_biscuit": "Biscuits", "BIS_viennoiserie": "Viennoiseries", "BIS_chocolat": "Chocolat", "BIS_bonbon_tot": "Bonbons", "BIS_cacahuete": "Cacahuètes, fruits secs", "BIS_chips": "Chips",
    "BNA_jus_tot": "Jus de fruits", "BNA_soda": "Sodas", "BNA_redbull": "Boissons énergisantes", "BNA_sodaredbull_light": "Sodas allégés",
    "BA_vin": "Vin", "BA_cidre": "Cidre", "BA_biere": "Bière", "BA_aperitif": "Apéritifs, spiritueux",
}
FAMILLES = {"PC": "Céréales", "RP": "Céréales", "LEG": "Légumes", "VC": "Viandes", "PPM": "Produits de la mer", "OE": "Oeufs", "SOJ": "Légumes", "PL": "Laitages",
            "FR": "Fruits", "BIS": "Grignotage", "BNA": "Boissons", "BA": "Alcool"}
FRUITS_LEGUMES = [c for c in ALIMENTS if c.split("_")[0] in ("LEG", "FR")] + ["RP_legumeracine", "RP_tubercule"]
INTERDITS = ["VC_porc", "VC_saucisson", "VC_pate_foie", "VC_pate_autre", "BA_vin", "BA_cidre", "BA_biere", "BA_aperitif"]
# Aliment -> séries Insee (début de libellé), diviseur vers le kilo ou le litre.
PRIX = {
    "LEG_bettera_tot": (["Carottes (1 kg)"], 1), "LEG_concombre": (["Concombres (1 kg)"], 1), "LEG_tomate_seul": (["Tomates (1 kg)"], 1),
    "LEG_chou": (["Chou-fleur (1 kg)"], 1), "LEG_artichaut": (["Artichauts (1 kg)"], 1), "LEG_champignon": (["Champignons de Paris (1 kg)"], 1), "LEG_oignon": (["Oignons (1 kg)"], 1),
    "VC_boeuf": (["Boeuf : bifteck dans la bavette", "Boeuf : côte avec os", "Boeuf : entrecôte", "Boeuf : faux filet", "Boeuf : rumsteack", "Steaks hachés industriels"], 1),
    "VC_agneau": (["Agneau : côtes découvertes", "Agneau : gigot raccourci"], 1), "VC_lapin": (["Lapin entier"], 1), "VC_porc": (["Porc : rôti dans le filet", "Porc : échine avec os"], 1), "VC_foie": (["Foie de veau frais"], 1),
    "PPM_poissgras_tot": (["Saumon d'élevage"], 1),
    "PPM_poissonautre": (["Cabillaud en tranche", "Filet de merlan", "Lieu noir en tranche", "Limandes", "Merluchon ou colinot", "Roussette", "Soles"], 1),
    "PPM_crustace": (["Crevettes grises", "Crevettes roses tropicales", "Langoustines crues", "Tourteaux"], 1), "PPM_mollusque": (["Moules de bouchots", "Coquilles Saint-Jacques entières"], 1),
    "FR_agrume": (["Oranges (1 kg)", "Clémentines (1 kg)", "Citrons (1 kg)", "Pamplemousses roses (1 kg)"], 1), "FR_pomme": (["Pommes (1 kg)"], 1), "FR_raisin": (["Raisins (1 kg)"], 1),
    "FR_melon": (["Melons (1 kg)"], 1), "FR_peche": (["Pêches, brugnons, nectarines"], 1), "FR_fraise": (["Fraises (1 kg)"], 1), "FR_fruitexotique": (["Kiwi (1 kg)", "Avocat (1 kg)"], 1),
    "PL_lait": (["Lait UHT demi-écrémé"], 1), "PL_yaourt_arom": (["Yaourt fruits au lait entier (250 g)"], 0.25),
    "BA_vin": (["Vin rouge de table"], 1), "BA_biere": (["Bière blonde de luxe en pack"], 1.5), "BA_aperitif": (["Apéritifs anisés"], 1),
}

r_ = lambda f, **k: pd.read_csv(INCA / f, sep=";", encoding="utf-8-sig", low_memory=False, **k)
desc = r_("description-indiv.csv")
adultes = desc[desc.ech == 1]
X = desc[(desc.ech == 1) & (desc.pop2 == 1)].merge(r_("fpq.csv").drop(columns=["POPULATION"]), on="NOIND", how="left")
X = X[X.pond_indiv_adu_pop2.notna()].copy()
X["w"] = X.pond_indiv_adu_pop2 / X.pond_indiv_adu_pop2.mean()
X["w3"] = X.pond_indiv_adu_pop3 / X.pond_indiv_adu_pop3.mean()
DIP = ["Primaire ou collège", "Lycée", "Bac +1 à +3", "Bac +4 et plus"]
REV = ["Moins de 900 €", "900 à 1 340 €", "1 340 à 1 850 €", "1 850 € et plus"]
AGES = ["18-44 ans", "45-64 ans", "65 ans et plus"]
X["age"] = X.tage_PS.map({7: AGES[0], 8: AGES[1], 9: AGES[2]})
X["sexe"] = X.sex_PS.map({1: "Hommes", 2: "Femmes"})
X["dip"] = X.etude_4cl_interv.map(dict(enumerate(DIP, 1)))
X["rev"] = X.RUC_4cl.map(dict(enumerate(REV, 1)))
X["pcs"] = X.PCS_8cl_interv.map({1: "Employés", 2: "Ouvriers", 3: "Indépendants", 4: "Indépendants", 5: "Professions intermédiaires", 6: "Cadres", 7: "Retraités", 8: "Autres inactifs"})
X["ville"] = X.agglo_5cl.map({1: "Rural", 2: "Petite ville", 3: "Ville moyenne", 4: "Grande ville", 5: "Paris"})
X = X.dropna(subset=["dip", "age", "sexe"]).copy()
M = pd.DataFrame({c: np.where(X[c + "_ON"].isna(), np.nan, np.where(X[c + "_ON"] == 1, (X[c + "_freq_M"].fillna(0) >= 1) * 1.0, 0.0)) for c in ALIMENTS}, index=X.index)
Y = pd.DataFrame({c: X[c + "_ON"].astype(float) for c in ALIMENTS}, index=X.index)
garde = M.isna().mean(axis=1) <= 0.10
X, M, Y = X[garde].copy(), M[garde], Y[garde]
F_ = pd.DataFrame({c: X[c + "_freq_M"].where(X[c + "_ON"] == 1, 0).clip(upper=30.4) for c in ALIMENTS})
print(f"{len(X)} adultes, {len(ALIMENTS)} aliments")
X["ampleur"] = M.sum(axis=1)
X["ampleur_an"] = Y.sum(axis=1)
X["sans_fl"] = M.drop(columns=FRUITS_LEGUMES).sum(axis=1)
X["fl"] = M[FRUITS_LEGUMES].sum(axis=1)
X["sans_interdits"] = M.drop(columns=INTERDITS).sum(axis=1)

PSU = adultes[["strate", "zae"]].drop_duplicates()
N_PSU = PSU.groupby("strate").zae.nunique()


def svy(formule, df, poids="w"):
    """Moindres carrés pondérés, variance linéarisée (strates, unités primaires)."""
    y, D = patsy.dmatrices(formule, df, return_type="dataframe", NA_action="drop")
    idx = y.index
    w = df.loc[idx, poids].values
    Dv, yv = D.values, y.values.ravel()
    inv = np.linalg.pinv((Dv * w[:, None]).T @ Dv)
    b = inv @ ((Dv * w[:, None]).T @ yv)
    e = yv - Dv @ b
    u = pd.DataFrame(Dv * (w * e)[:, None], columns=D.columns)
    u["strate"], u["zae"] = df.loc[idx, "strate"].values, df.loc[idx, "zae"].values
    p = Dv.shape[1]
    S = np.zeros((p, p))
    for h, g in u.groupby("strate"):
        z = g.groupby("zae")[list(D.columns)].sum().values
        nh = int(N_PSU.get(h, len(z)))
        if nh < 2:
            continue
        z = np.vstack([z, np.zeros((max(nh - len(z), 0), p))])
        c = z - z.mean(axis=0)
        S += nh / (nh - 1) * c.T @ c
    return pd.Series(b, index=D.columns), pd.Series(np.sqrt(np.diag(inv @ S @ inv)), index=D.columns), len(idx)


def r1(v):
    return None if v is None or np.isnan(v) else round(float(v), 1)


def r2(v):
    return None if v is None or np.isnan(v) else round(float(v), 2)


def coef(b, se, cle):
    k = next(i for i in b.index if cle in i)
    return {"b": r2(b[k]), "ic": r2(1.96 * se[k])}


DT = "C(dip, Treatment('Primaire ou collège'))"
RT = "C(rev, Treatment('Moins de 900 €'))"
TOUT = f"C(age)+C(sexe)+{DT}+{RT}+C(pcs)+C(ville)"
COMPLET = ["age", "sexe", "dip", "rev", "pcs", "ville"]


def gradient(y, df=None, poids="w"):
    """Bac +4 comparé à primaire-collège : brut, à âge et sexe égaux, à tout égal (+ revenu et cadres)."""
    df = X if df is None else df
    d = df.dropna(subset=COMPLET + [y])
    out = {}
    for nom, rhs in [("brut", DT), ("age_sexe", f"C(age)+C(sexe)+{DT}"), ("complet", TOUT)]:
        b, se, n = svy(f"{y} ~ {rhs}", d, poids)
        out[nom] = {**coef(b, se, "Bac +4 et plus"), "n": n}
    out["revenu"] = coef(b, se, "1 850 € et plus")
    return out


def moyennes(y, var, mods, df=None, poids="w"):
    df = X if df is None else df
    res = []
    for m_ in mods:
        s = df[(df[var] == m_) & df[y].notna()]
        if len(s) < SEUIL_N:
            res.append({"label": m_, "v": None, "n": len(s)})
            continue
        b, se, n = svy(f"{y} ~ 1", s, poids)
        res.append({"label": m_, "v": r1(b.iloc[0]), "ic": r2(1.96 * se.iloc[0]), "n": n})
    return res


def spearman_perm(a, b, n=20000):
    a, b = pd.Series(a).rank().values, pd.Series(b).rank().values
    obs = np.corrcoef(a, b)[0, 1]
    rng = np.random.default_rng(GRAINE)
    perm = np.array([np.corrcoef(rng.permutation(a), b)[0, 1] for _ in range(n)])
    return {"r": round(float(obs), 2), "p": round(float((np.abs(perm) >= abs(obs)).mean()), 3)}


# ---- T1 ----------------------------------------------------------------------
print("\nT1 AMPLEUR")
t1 = {"grad": gradient("ampleur"), "niveaux": moyennes("ampleur", "dip", DIP), "ages": moyennes("ampleur", "age", AGES), "revenus": moyennes("ampleur", "rev", REV),
      "total": len(ALIMENTS), "sans_fl": gradient("sans_fl"), "fl": gradient("fl"), "n_fl": len(FRUITS_LEGUMES)}
print("  ", t1["grad"]["brut"], t1["grad"]["age_sexe"], t1["grad"]["complet"], "revenu", t1["grad"]["revenu"])
print("   fruits et légumes", t1["fl"]["complet"], "| sans fruits et légumes", t1["sans_fl"]["age_sexe"], t1["sans_fl"]["complet"], "revenu", t1["sans_fl"]["revenu"])

# ---- T2 ----------------------------------------------------------------------
print("\nT2 MESURE INDÉPENDANTE : rappels de 24 h")
cc = pd.read_csv(INCA / "conso-compo-alim.csv", sep=";", encoding="utf-8-sig", usecols=["NOIND", "R24_num", "R24_nombre", "gpe_INCA3", "aliment_code_INCA3"], low_memory=False)
cc = cc[~cc.gpe_INCA3.isin([29, 30, 41]) & cc.NOIND.isin(X.NOIND)]
dist = cc.groupby("NOIND").agg(r24_aliments=("aliment_code_INCA3", "nunique"), r24_jours=("R24_nombre", "max"))
en = r_("apports-nut-alim.csv")[["NOIND", "nutriment1"]].rename(columns={"nutriment1": "energie"})
idx = X.index
X = X.merge(dist, left_on="NOIND", right_index=True, how="left").merge(en, on="NOIND", how="left")
X.index = idx
d3 = X[X.r24_aliments.notna() & X.w3.notna()].copy()
t2 = {"grad": gradient("r24_aliments", d3, "w3"), "niveaux": moyennes("r24_aliments", "dip", DIP, d3, "w3"), "corr": r2(np.corrcoef(d3.ampleur, d3.r24_aliments)[0, 1]), "moyenne": r1(d3.r24_aliments.mean())}
b, se, n = svy(f"r24_aliments ~ {TOUT}+C(r24_jours)+energie", d3.dropna(subset=COMPLET + ["energie"]), "w3")
t2["net_energie"] = {**coef(b, se, "Bac +4 et plus"), "n": n}
print("  ", t2["grad"]["complet"], "revenu", t2["grad"]["revenu"], "à énergie égale", t2["net_energie"], "corrélation", t2["corr"])

# ---- T3 : les deux critères objectifs ----------------------------------------
print("\nT3 CRITÈRES OBJECTIFS")
prev = pd.Series({c: np.average(M[c].fillna(0), weights=X.w) * 100 for c in ALIMENTS})
if not PRIX_XML.exists():
    import urllib.request
    PRIX_XML.parent.mkdir(exist_ok=True)
    PRIX_XML.write_bytes(urllib.request.urlopen(urllib.request.Request(PRIX_URL, headers={"User-Agent": "Mozilla/5.0"}), timeout=200).read())
insee = {}
for s in ET.parse(PRIX_XML).getroot().iter():
    if s.tag.endswith("Series") and s.attrib.get("FREQ") == "A":
        v = [float(o.attrib["OBS_VALUE"]) for o in s if o.tag.endswith("Obs") and o.attrib.get("OBS_VALUE") not in (None, "", "NaN")]
        if v:
            insee[s.attrib.get("TITLE_FR", "").split(" - ", 1)[-1]] = sum(v) / len(v)
prix = {}
for c, (noms, div) in PRIX.items():
    vals = [next((v for k, v in insee.items() if k.startswith(n_)), None) for n_ in noms]
    vals = [v for v in vals if v is not None]
    if vals:
        prix[c] = sum(vals) / len(vals) / div
prix = pd.Series(prix)
med_prix = prix.median()
MAJ = [c for c in ALIMENTS if prev[c] > SEUIL_MAJ]
MINO = [c for c in ALIMENTS if prev[c] <= SEUIL_MAJ]
PAS_CHERS = [c for c in prix.index if prix[c] < med_prix]
CHERS = [c for c in prix.index if prix[c] >= med_prix]
print(f"   {len(MAJ)} majoritaires sur {len(ALIMENTS)} ; {len(prix)} aliments avec prix, médiane {med_prix:.2f} €/kg")
X["pc_lo"] = X.pcs.isin(["Ouvriers", "Employés"]) * 1.0
X["groupe_pcs"] = X.pcs.map({"Ouvriers": "lo", "Employés": "lo", "Cadres": "hi", "Professions intermédiaires": "hi"})
X["groupe_diplome"] = X.dip.map({DIP[0]: "lo", DIP[3]: "hi"})
X["groupe_revenu"] = X.rev.map({REV[0]: "lo", REV[3]: "hi"})
DEFS = {"pcs": ("groupe_pcs", "PCS", "Ouvriers et employés", "Cadres et professions intermédiaires"),
        "diplome": ("groupe_diplome", "Diplôme", "Primaire ou collège", "Bac +4 et plus"),
        "revenu": ("groupe_revenu", "Revenu par personne", "Moins de 900 €", "1 850 € et plus")}
# Écart de chaque aliment : classes populaires moins classes supérieures, à âge et sexe égaux.
ecarts = {}
for d_id, (col_g, *_ ) in DEFS.items():
    rows = []
    for c in ALIMENTS:
        X["y_"] = M[c] * 100
        s = X[X[col_g].notna()].dropna(subset=["y_", "age", "sexe"]).copy()
        s["lo"] = (s[col_g] == "lo") * 1.0
        b, se, n = svy("y_ ~ C(age)+C(sexe)+lo", s)
        rows.append({"id": c, "b": float(b["lo"]), "se": float(se["lo"]), "n": n})
    e = pd.DataFrame(rows).set_index("id")
    e["p"] = 2 * (1 - norm.cdf(np.abs(e.b / e.se)))
    e["q"] = multipletests(e.p, method="fdr_bh")[1]
    ecarts[d_id] = e


def bilan(e, vrai, faux):
    return {"oui": r1(e.loc[vrai, "b"].mean()), "non": r1(e.loc[faux, "b"].mean()), "n_oui": len(vrai), "n_non": len(faux)}


def surrep(e, liste):
    s = e.loc[liste]
    return {"plus": int(((s.b > 0) & (s.q < SEUIL_Q)).sum()), "moins": int(((s.b < 0) & (s.q < SEUIL_Q)).sum()), "nul": int((s.q >= SEUIL_Q).sum()), "total": len(liste)}


familles = pd.Series({c: FAMILLES[c.split("_")[0]] for c in prix.index})
criteres = {}
for d_id, (col_g, nom, lo, hi) in DEFS.items():
    e = ecarts[d_id]
    ep = e.loc[prix.index]
    dm = ep.b - ep.b.groupby(familles).transform("mean")
    dp = np.log(prix) - np.log(prix).groupby(familles).transform("mean")
    # Les deux critères à la fois : gap ~ part de consommateurs + log prix, p par permutation.
    Z = np.column_stack([np.ones(len(ep)), (prev[prix.index] - prev[prix.index].mean()) / prev[prix.index].std(), (np.log(prix) - np.log(prix).mean()) / np.log(prix).std()])
    beta = np.linalg.lstsq(Z, ep.b.values, rcond=None)[0]
    rng = np.random.default_rng(GRAINE)
    perm = np.array([np.linalg.lstsq(Z, rng.permutation(ep.b.values), rcond=None)[0] for _ in range(20000)])
    p_ = [(np.abs(perm[:, i]) >= abs(beta[i])).mean() for i in (1, 2)]
    croise = {}
    for nom_c, a_, b_ in [("majoritaire_pas_cher", [c for c in PAS_CHERS if c in MAJ], None), ("majoritaire_cher", [c for c in CHERS if c in MAJ], None),
                          ("minoritaire_pas_cher", [c for c in PAS_CHERS if c in MINO], None), ("minoritaire_cher", [c for c in CHERS if c in MINO], None)]:
        croise[nom_c] = {"n": len(a_), "b": r1(e.loc[a_, "b"].mean()) if a_ else None, "aliments": [ALIMENTS[c] for c in a_]}
    criteres[d_id] = {
        "nom": nom, "lo": lo, "hi": hi, "n": int(e.n.max()),
        "majoritaire": {**bilan(e, MAJ, MINO), "spearman": spearman_perm(prev[e.index], e.b), "repartition": surrep(e, MAJ), "repartition_mino": surrep(e, MINO)},
        "pas_cher": {**bilan(e, PAS_CHERS, CHERS), "spearman": spearman_perm(prix, ep.b), "intra_famille": spearman_perm(dp, dm), "repartition": surrep(e, PAS_CHERS), "repartition_chers": surrep(e, CHERS)},
        "ensemble": {"b_part": r2(beta[1]), "p_part": round(float(p_[0]), 3), "b_prix": r2(beta[2]), "p_prix": round(float(p_[1]), 3), "croise": croise},
    }
    c_ = criteres[d_id]
    print(f"   {nom} ({lo} moins {hi}) : majoritaires {c_['majoritaire']['oui']} / autres {c_['majoritaire']['non']}, r part {c_['majoritaire']['spearman']} ; pas chers {c_['pas_cher']['oui']} / chers {c_['pas_cher']['non']}, r prix {c_['pas_cher']['spearman']}, intra {c_['pas_cher']['intra_famille']}")
    print(f"      répartition majoritaires {c_['majoritaire']['repartition']} autres {c_['majoritaire']['repartition_mino']} | pas chers {c_['pas_cher']['repartition']} chers {c_['pas_cher']['repartition_chers']}")
    print(f"      ensemble {c_['ensemble']['b_part']} (p {c_['ensemble']['p_part']}), prix {c_['ensemble']['b_prix']} (p {c_['ensemble']['p_prix']}) ; croisé", {k: (v["n"], v["b"]) for k, v in croise.items()})

# Composition du répertoire de chacun.
X["n_maj"], X["n_mino"] = M[MAJ].sum(axis=1), M[MINO].sum(axis=1)
X["n_pas_chers"], X["n_chers"] = M[PAS_CHERS].sum(axis=1), M[CHERS].sum(axis=1)
X["part_maj"] = X.n_maj / X.ampleur * 100
n_prix = M[list(prix.index)].sum(axis=1)
X["part_pas_chers"] = (X.n_pas_chers / n_prix * 100).where(n_prix > 0)
X["prix_moyen"] = (M[list(prix.index)] * prix).sum(axis=1) / n_prix.where(n_prix > 0)
Fp = F_[list(prix.index)]
X["prix_freq"] = (Fp * prix).sum(axis=1) / Fp.sum(axis=1).where(Fp.sum(axis=1) > 0)
INDIV = {"n_maj": "Aliments majoritaires consommés", "n_mino": "Autres aliments consommés", "part_maj": "Part d'aliments majoritaires dans le répertoire (%)",
         "n_pas_chers": "Aliments pas chers consommés", "n_chers": "Aliments chers consommés", "part_pas_chers": "Part d'aliments pas chers (%)",
         "prix_moyen": "Prix moyen des aliments du répertoire (€/kg)", "prix_freq": "Prix moyen, pondéré par la fréquence (€/kg)"}
composition = {}
for d_id, (col_g, nom, lo, hi) in DEFS.items():
    lignes = []
    for y, lab in INDIV.items():
        s = X[X[col_g].notna()].dropna(subset=[y, "age", "sexe"]).copy()
        s["lo"] = (s[col_g] == "lo") * 1.0
        b, se, n = svy(f"{y} ~ C(age)+C(sexe)+lo", s)
        moy = {g: np.average(v[y], weights=v.w) for g, v in s.groupby(col_g)}
        lignes.append({"id": y, "label": lab, "lo": r2(moy["lo"]), "hi": r2(moy["hi"]), "b": r2(b["lo"]), "ic": r2(1.96 * se["lo"])})
    composition[d_id] = lignes
    print(f"   Composition, {nom} :", [(l["id"], l["lo"], l["hi"], l["b"], l["ic"]) for l in lignes])
table_aliments = [{"id": c, "label": ALIMENTS[c], "famille": FAMILLES[c.split("_")[0]], "part": r1(prev[c]), "majoritaire": c in MAJ,
                   "prix": round(float(prix[c]), 2) if c in prix.index else None, "pas_cher": (c in PAS_CHERS) if c in prix.index else None,
                   "ecarts": {d: {"b": r1(ecarts[d].loc[c, "b"]), "ic": r1(1.96 * ecarts[d].loc[c, "se"]), "net": bool(ecarts[d].loc[c, "q"] < SEUIL_Q)} for d in DEFS}} for c in ALIMENTS]
for d_id in DEFS:
    e = ecarts[d_id].sort_values("b")
    s_ = e[e.q < SEUIL_Q]
    print(f"   {d_id} : plus consommés par les classes populaires :", [(ALIMENTS[c], round(s_.b[c], 1), "maj" if c in MAJ else "min", f"{prix[c]:.1f}€" if c in prix.index else "-") for c in s_.index[::-1] if s_.b[c] > 0])
    print(f"   {d_id} : moins consommés :", [(ALIMENTS[c], round(s_.b[c], 1), "maj" if c in MAJ else "min", f"{prix[c]:.1f}€" if c in prix.index else "-") for c in s_.index if s_.b[c] < 0][:16])

# ---- T4 : à tout égal --------------------------------------------------------
lignes = []
for c, lab in ALIMENTS.items():
    X["y_"] = M[c] * 100
    b, se, n = svy(f"y_ ~ {TOUT}", X.dropna(subset=COMPLET + ["y_"]))
    k = next(i for i in b.index if "Bac +4 et plus" in i)
    lignes.append({"id": c, "label": lab, "b": float(b[k]), "se": float(se[k])})
L = pd.DataFrame(lignes)
L["p"] = 2 * (1 - norm.cdf(np.abs(L.b / L.se)))
L["q"] = multipletests(L.p, method="fdr_bh")[1]
L = L.sort_values("b", ascending=False)
sig = L[L.q < SEUIL_Q]
t4 = {"hausse": int((sig.b > 0).sum()), "baisse": int((sig.b < 0).sum()), "nul": int((L.q >= SEUIL_Q).sum()),
      "aliments": [{"label": r.label, "b": r1(r.b), "ic": r1(1.96 * r.se), "net": bool(r.q < SEUIL_Q)} for r in L.itertuples()]}
print(f"\nT4 À TOUT ÉGAL : {t4['hausse']} en hausse, {t4['baisse']} en baisse, {t4['nul']} sans écart net ; baisses : {list(sig[sig.b < 0].label)}")

# ---- T5 : classes latentes ---------------------------------------------------
print("\nT5 TYPES")
A0 = np.nan_to_num(M.values)
masque = ~M.isna().values
w = X.w.values
col = list(M.columns)


def em(K, graine, A0, masque, w, iters=300):
    rng = np.random.default_rng(graine)
    marg = (w[:, None] * A0 * masque).sum(0) / (w[:, None] * masque).sum(0)
    th = np.clip(marg + rng.normal(0, 0.15, (K, A0.shape[1])), 0.02, 0.98)
    pi = np.ones(K) / K
    ll_av = -np.inf
    for _ in range(iters):
        lp = np.log(pi)[None, :] + (A0 * masque) @ np.log(th).T + ((1 - A0) * masque) @ np.log(1 - th).T
        m_ = lp.max(axis=1, keepdims=True)
        ls = m_.ravel() + np.log(np.exp(lp - m_).sum(axis=1))
        r = np.exp(lp - ls[:, None])
        ll = (w * ls).sum()
        Nk = (w[:, None] * r).sum(0)
        pi = Nk / Nk.sum()
        th = np.clip(((r * w[:, None]).T @ (A0 * masque) + 0.5) / ((r * w[:, None]).T @ masque.astype(float) + 1.0), 0.005, 0.995)
        if ll - ll_av < 1e-3:
            break
        ll_av = ll
    return ll, pi, th, r


bics = {}
for K in (3, 4, 5, 6, 8):
    ll = max((em(K, GRAINE + s, A0, masque, w) for s in range(10)), key=lambda t: t[0])
    bics[K] = ll
    print(f"   K={K} BIC {-2 * ll[0] + (K - 1 + K * A0.shape[1]) * np.log(len(A0)):.0f}")
_, pi4, th4, r4 = bics[4]
X["cl"] = r4.argmax(axis=1)
ordre = list(np.argsort(-th4.sum(axis=1)))
idx_chers = [col.index(c) for c in CHERS]
ages_cl = {k: np.average((X.cl == k) & (X.age == AGES[2]), weights=X.w) / max(np.average(X.cl == k, weights=X.w), 1e-9) for k in range(4)}
a, b_ = ordre[1], ordre[2]
vieux, jeune = (a, b_) if ages_cl[a] > ages_cl[b_] else (b_, a)
NOMS = {ordre[0]: "Répertoire large", vieux: "Légumes, poisson, soupe", jeune: "Sodas, desserts, sucreries", ordre[3]: "Répertoire resserré"}
t5 = []
moy_all = (w[:, None] * A0).sum(0) / w.sum()
for k in [ordre[0], vieux, jeune, ordre[3]]:
    X["y_"] = (X.cl == k) * 100.0
    ecart = th4[k] - moy_all
    t5.append({"nom": NOMS[k], "part": r1(pi4[k] * 100), "ampleur": r1(th4[k].sum()), "majoritaires": r1(th4[k, [col.index(c) for c in MAJ]].sum()), "autres": r1(th4[k, [col.index(c) for c in MINO]].sum()),
               "diplomes": moyennes("y_", "dip", DIP), "ages": moyennes("y_", "age", AGES), "net": gradient("y_")["complet"],
               "plus": [ALIMENTS[col[i]] for i in np.argsort(-ecart)[:5]], "moins": [ALIMENTS[col[i]] for i in np.argsort(ecart)[:5]]})
    print("  ", NOMS[k], t5[-1]["part"], "%, ampleur", t5[-1]["ampleur"], [n_["v"] for n_ in t5[-1]["diplomes"]], "net", t5[-1]["net"], "âges", [n_["v"] for n_ in t5[-1]["ages"]])
rng = np.random.default_rng(GRAINE)
stab = []
for _ in range(5):
    p = rng.permutation(len(A0))
    ths = [max((em(4, GRAINE + 100 + s, A0[q], masque[q], w[q]) for s in range(6)), key=lambda t: t[0])[2] for q in (p[: len(p) // 2], p[len(p) // 2:])]
    stab.append(np.mean(np.corrcoef(ths[0], ths[1])[:4, 4:].max(axis=1)))
t5_stab = r2(float(np.mean(stab)))
print("   stabilité :", t5_stab)

# ---- T6, T7 ------------------------------------------------------------------
t6 = {}
for a_ in AGES:
    s = X[X.age == a_].dropna(subset=["rev", "pcs", "ville"])
    b, se, n = svy(f"ampleur ~ C(sexe)+{DT}+{RT}+C(pcs)+C(ville)", s)
    t6[a_] = {**coef(b, se, "Bac +4 et plus"), "n": n}
d6 = X.dropna(subset=COMPLET).copy()
d6["bac4"], d6["jeune"], d6["senior"] = (d6.dip == DIP[3]) * 1.0, (d6.age == AGES[0]) * 1.0, (d6.age == AGES[2]) * 1.0
b, se, n = svy(f"ampleur ~ {TOUT}+bac4:jeune+bac4:senior", d6)
t6["interaction"] = {"jeune": {"b": r2(b["bac4:jeune"]), "ic": r2(1.96 * se["bac4:jeune"])}, "senior": {"b": r2(b["bac4:senior"]), "ic": r2(1.96 * se["bac4:senior"])}}
print("\nT6", t6)
regimes = X[["regime_vegetarien", "regime_allergie", "regime_maigrir_med", "regime_maigrir_choix", "regime_autre_med"]].fillna(0).sum(axis=1) > 0
MED = [c for c in ALIMENTS if prev[c] >= prev.median()]
X["n_med"] = M[MED].sum(axis=1)
t7 = {"annuel": gradient("ampleur_an")["complet"], "sans_porc_alcool": gradient("sans_interdits")["complet"], "hors_regimes": gradient("ampleur", X[~regimes])["complet"],
      "n_maj": gradient("n_maj")["complet"], "n_mino": gradient("n_mino")["complet"], "n_pas_chers": gradient("n_pas_chers")["complet"], "n_chers": gradient("n_chers")["complet"],
      "n_au_dessus_mediane": gradient("n_med")["complet"], "mediane": r1(prev.median())}
print("T7", t7)

# ---- Verdict -----------------------------------------------------------------
g_a, g_r, g_s = t1["grad"]["complet"], t2["grad"]["complet"], t1["sans_fl"]["complet"]
conserve = {k: t7[k]["b"] + t7[k]["ic"] >= 0 for k in ("n_maj", "n_pas_chers")}
verdict = {"ampleur": bool(g_a["b"] > g_a["ic"]), "rappels": bool(g_r["b"] > g_r["ic"]), "hors_fruits_legumes": bool(g_s["b"] > g_s["ic"]), "conserve_majoritaires": bool(conserve["n_maj"]),
           "conserve_pas_chers": bool(conserve["n_pas_chers"]), "exclusions": t4["baisse"]}
print("\nVERDICT", verdict)
sortie = {"n": int(len(X)), "n_rappels": int(len(d3)), "seuil_majoritaire": SEUIL_MAJ, "prix_median": round(float(med_prix), 2), "n_majoritaires": len(MAJ), "n_prix": len(prix),
          "t1": t1, "t2": t2, "criteres": criteres, "composition": composition, "aliments": table_aliments, "t4": t4, "t5": {"classes": t5, "stabilite": t5_stab}, "t6": t6, "t7": t7, "verdict": verdict}
OUT.write_text(json.dumps(sortie, ensure_ascii=False, separators=(",", ":"), default=float), encoding="utf-8")
print(f"-> {OUT.name} ({OUT.stat().st_size // 1024} Ko)")
