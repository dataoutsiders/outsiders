# -*- coding: utf-8 -*-
"""
Semaine de 4 jours vs 4,5 jours : effet sur les résultats scolaires ?

Question : les communes qui ont gardé la semaine de 4,5 jours à l'école primaire
obtiennent-elles de meilleurs résultats au collège que celles passées à 4 jours ?

Le régime scolaire est décidé par la COMMUNE (écoles primaires), on l'apparie donc
aux collèges publics implantés dans cette commune.

Variable de résultat retenue : le score aux EVALUATIONS NATIONALES D'ENTREE EN 6e.
Elle mesure le produit du primaire l'année même où l'élève en sort.
Attention : l'IVAC (valeur ajoutée des collèges) est un mauvais indicateur ici, car
son modèle contrôle déjà le score d'entrée en 6e : tout effet du primaire y est
soustrait par construction. On le calcule quand même, pour le montrer.

Trois analyses :
  A. Transversale, ensemble des collèges publics (régressions en escalier)
  B. Transversale, communes à collège unique (appariement école vers collège propre)
  C. Différence-de-différences sur les communes ayant basculé de 4,5j à 4j
     entre 2020-2021 et 2025-2026, contrôle = communes restées à 4,5j.

Sortie : frontend/public/data/showcases/rythmes-scolaires.json

Sources (data.education.gouv.fr) :
  fr-en-organisation-du-temps-scolaire                 horaires par école
  fr-en-evaluations_nationales_6eme_par_etablissement  scores 6e 2017-2025
  fr-en-ips-ecoles-ap2022 / fr-en-ips-colleges-ap2023  indices de position sociale
  fr-en-indicateurs-valeur-ajoutee-colleges            IVAC (contre-exemple)
  fr-en-annuaire-education                             UAI collège vers code commune
Contexte communal : frontend/public/data/atlas/communes/ (déjà dans le dépôt).
"""
import io
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

H = {"User-Agent": "outsiders/1.0"}
ROOT = Path(__file__).resolve().parents[2]
CACHE = Path(__file__).resolve().parent / "_cache_rythmes"
ATLAS = ROOT / "frontend" / "public" / "data" / "atlas" / "communes"
OUT = ROOT / "frontend" / "public" / "data" / "showcases"
CACHE.mkdir(exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)

API = "https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets"


# ============================================================
# Téléchargement (mis en cache)
# ============================================================
def export_csv(dataset, select, where=None, tries=4):
    """Export CSV d'un jeu Opendatasoft, mis en cache sur disque."""
    path = CACHE / f"{dataset}.csv"
    if path.exists() and path.stat().st_size > 1024:
        return pd.read_csv(path, sep=";", dtype=str, encoding="utf-8-sig")
    params = {"select": select, "delimiter": ";"}
    if where:
        params["where"] = where
    url = f"{API}/{dataset}/exports/csv?" + urllib.parse.urlencode(params)
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=180) as r:
                raw = r.read()
            break
        except Exception as e:
            print("   retry", i + 1, e)
            time.sleep(3)
    else:
        raise RuntimeError(f"echec {dataset}")
    path.write_bytes(raw)
    return pd.read_csv(io.BytesIO(raw), sep=";", dtype=str, encoding="utf-8-sig")


# ============================================================
# 1. Régime scolaire de chaque commune
# ============================================================
def regimes_communaux():
    """Une ligne par commune : régime en 2020-2021 et 2025-2026, nombre d'écoles.

    Le rythme n'est pas donné en clair : une école travaille le mercredi matin
    (semaine de 4,5 jours) si l'heure de début du mercredi est renseignée.
    """
    ots = export_csv("fr-en-organisation-du-temps-scolaire",
                     "code_uai,annee_scolaire,code_commune,commune,code_departement,mercredi_matin_debut")
    ots["s45"] = ots["mercredi_matin_debut"].notna().astype(int)
    g = (ots.groupby(["code_commune", "annee_scolaire"])
            .agg(n_ecoles=("code_uai", "nunique"), part45=("s45", "mean")).reset_index())
    part = g.pivot(index="code_commune", columns="annee_scolaire", values="part45")
    a0, a1 = "2020-2021", "2025-2026"
    com = part.dropna(subset=[a0, a1]).copy()
    com["n_ecoles"] = g[g.annee_scolaire == a1].set_index("code_commune")["n_ecoles"]
    meta = ots.drop_duplicates("code_commune").set_index("code_commune")
    com["nom"] = meta["commune"]
    com["dep"] = meta["code_departement"]

    def classe(r):
        a, b = r[a0], r[a1]
        if a == 0 and b == 0:
            return "4j stable"
        if a == 1 and b == 1:
            return "4,5j stable"
        if a == 1 and b == 0:
            return "bascule 4,5j vers 4j"
        if a == 0 and b == 1:
            return "bascule 4j vers 4,5j"
        return "mixte"

    com["regime"] = com.apply(classe, axis=1)
    com["part45_2020"], com["part45_2025"] = com[a0], com[a1]
    print(f"   {len(com)} communes appariees sur les deux photos")
    for k, v in com.regime.value_counts().items():
        print(f"     {k:22} {v:6}")
    return com[["nom", "dep", "n_ecoles", "part45_2020", "part45_2025", "regime"]]


# ============================================================
# 2. Résultats : évaluations d'entrée en 6e, 2017-2025
# ============================================================
def evaluations_6e():
    """Score moyen par collège et par année, standardisé (z-score) par année.

    Les scores sont ancrés autour de 250 chaque année mais l'échelle peut bouger :
    on standardise par année et discipline pour raisonner en écarts-types.
    """
    ev = export_csv("fr-en-evaluations_nationales_6eme_par_etablissement",
                    "annee,uai,libelle_secteur,caracteristique,discipline,effectif,score_moyen",
                    where="caracteristique='Ensemble'")
    ev["annee"] = ev["annee"].astype(str).str[:4].astype(int)
    ev["score"] = pd.to_numeric(ev["score_moyen"], errors="coerce")
    ev["effectif"] = pd.to_numeric(ev["effectif"], errors="coerce")
    ev = ev[ev.score.notna() & (ev.effectif >= 20)].copy()
    ev["disc"] = ev["discipline"].str[:4].map({"Fran": "francais", "Math": "maths"})
    ev = ev[ev.disc.notna()].copy()
    ev["z"] = ev.groupby(["annee", "disc"])["score"].transform(lambda s: (s - s.mean()) / s.std())
    print(f"   {ev.uai.nunique()} colleges, annees {ev.annee.min()}-{ev.annee.max()}")
    return ev


# ============================================================
# 3. Contrôles
# ============================================================
def ips_colleges():
    d = export_csv("fr-en-ips-colleges-ap2023", "rentree_scolaire,uai,secteur,ips")
    d = d[d.rentree_scolaire == "2024-2025"].copy()
    d["ips_col"] = pd.to_numeric(d.ips, errors="coerce")
    return d.drop_duplicates("uai").set_index("uai")["ips_col"]


def ips_ecoles_commune():
    """IPS moyen des écoles publiques de la commune : la composition sociale
    mesurée là où le traitement s'applique."""
    d = export_csv("fr-en-ips-ecoles-ap2022",
                   "rentree_scolaire,uai,code_insee_de_la_commune,secteur,ips")
    d = d[(d.rentree_scolaire == "2024-2025") & (d.secteur.str.lower() == "public")].copy()
    d["ips"] = pd.to_numeric(d.ips, errors="coerce")
    g = d.groupby("code_insee_de_la_commune")["ips"].agg(["mean", "size"])
    print(f"   IPS ecoles primaires : {len(g)} communes")
    return g.rename(columns={"mean": "ips_ecoles", "size": "n_ips_ecoles"})


def contexte_communal():
    """Revenu, population, catégories sociales par commune (atlas du dépôt)."""
    rows = {}
    for f in sorted(ATLAS.glob("*.json")):
        rows.update(json.loads(f.read_text(encoding="utf-8")))
    d = pd.DataFrame.from_dict(rows, orient="index")
    keep = [c for c in ["pop", "revenu", "diplome_sup", "cadres", "ouvriers", "prix_m2"] if c in d]
    print(f"   contexte communal : {len(d)} communes")
    return d[keep].apply(pd.to_numeric, errors="coerce")


def colleges_publics():
    ann = export_csv("fr-en-annuaire-education",
                     "identifiant_de_l_etablissement,type_etablissement,statut_public_prive,"
                     "code_commune,nom_commune")
    c = ann[ann.type_etablissement.str.startswith("Coll", na=False)
            & (ann.statut_public_prive == "Public")].copy()
    c = c.rename(columns={"identifiant_de_l_etablissement": "uai"})[["uai", "code_commune", "nom_commune"]]
    print(f"   {len(c)} colleges publics")
    return c.dropna(subset=["code_commune"]).drop_duplicates("uai")


# ============================================================
# 4. Régressions
# ============================================================
SPECS = [
    ("brut", []),
    ("+ IPS du college", ["ips_col"]),
    ("+ IPS des ecoles primaires", ["ips_col", "ips_ecoles"]),
    ("+ taille et revenu commune", ["ips_col", "ips_ecoles", "log_pop", "revenu", "diplome_sup"]),
    ("+ effets fixes departement", ["ips_col", "ips_ecoles", "log_pop", "revenu", "diplome_sup", "FE_DEP"]),
]


def regression(df, y, controls, cluster="code_commune"):
    """MCO de y sur le traitement (4,5j) + contrôles, erreurs-types clusterisées
    par commune : le régime est décidé à la commune, pas au collège."""
    cols = ["traite", cluster, y] + [c for c in controls if c != "FE_DEP"]
    if "FE_DEP" in controls:
        cols = cols + ["dep"]
    d = df[cols].dropna()
    X = pd.DataFrame({"traite": d["traite"]}, index=d.index)
    for c in controls:
        if c == "FE_DEP":
            X = X.join(pd.get_dummies(d["dep"], prefix="dep", drop_first=True, dtype=float))
        else:
            X[c] = d[c]
    X = sm.add_constant(X)
    r = sm.OLS(d[y].astype(float), X.astype(float)).fit(
        cov_type="cluster", cov_kwds={"groups": d[cluster]})
    lo, hi = r.conf_int().loc["traite"]
    return {"n": int(len(d)), "n_communes": int(d[cluster].nunique()),
            "n_traites": int(d.traite.sum()),
            "coef": round(float(r.params["traite"]), 4),
            "ic_bas": round(float(lo), 4), "ic_haut": round(float(hi), 4),
            "p": round(float(r.pvalues["traite"]), 4), "r2": round(float(r.rsquared), 3)}


def escalier(df, y, libelle):
    print(f"\n   {libelle}")
    out = []
    for nom, ctrl in SPECS:
        try:
            res = regression(df, y, ctrl)
        except Exception as e:
            print(f"     {nom:30} echec : {e}")
            continue
        res["specification"] = nom
        res["controles"] = [c for c in ctrl if c != "FE_DEP"]
        out.append(res)
        etoile = "*" if res["p"] < 0.05 else " "
        print(f"     {nom:30} {res['coef']:+.3f} [{res['ic_bas']:+.3f} ; {res['ic_haut']:+.3f}]"
              f" p={res['p']:.3f}{etoile}  n={res['n']}")
    return out


# ============================================================
# 5. Différence-de-différences sur les communes bascule
# ============================================================
def demean(df, col, groupes, iters=8):
    """Absorption d'effets fixes multiples par projections alternées."""
    v = df[col].astype(float).to_numpy().copy()
    for _ in range(iters):
        for g in groupes:
            v = v - pd.Series(v, index=df.index).groupby(df[g]).transform("mean").to_numpy()
    return v


def diff_en_diff(panel):
    """Traités = communes passées de 4,5j à 4j entre 2020-2021 et 2025-2026.
    Contrôle = communes restées à 4,5j. Effets fixes collège et année.

    Logique des cohortes : un élève entrant en 6e en année N a fait son primaire
    de N-5 à N-1. Pour N <= 2021 les deux groupes étaient à 4,5 jours : l'écart
    doit y être nul (test placebo). Pour N >= 2024, le groupe traité a passé une
    partie du primaire à 4 jours.
    """
    d = panel[panel.regime.isin(["bascule 4,5j vers 4j", "4,5j stable"])].copy()
    d["traite_did"] = (d.regime == "bascule 4,5j vers 4j").astype(int)
    d["post"] = (d.annee >= 2024).astype(int)
    d = d[(d.annee <= 2021) | (d.annee >= 2024)]
    res = {}
    for disc in ["francais", "maths"]:
        dd = d[d.disc == disc].dropna(subset=["z"]).copy()
        ok = dd.groupby("uai")["post"].agg(["min", "max"])
        dd = dd[dd.uai.isin(ok[(ok["min"] == 0) & (ok["max"] == 1)].index)].copy()
        if len(dd) < 100:
            continue
        dd["inter"] = dd.traite_did * dd.post
        yv = demean(dd, "z", ["uai", "annee"])
        xv = demean(dd, "inter", ["uai", "annee"])
        X = sm.add_constant(pd.DataFrame({"traite_x_post": xv}, index=dd.index))
        r = sm.OLS(pd.Series(yv, index=dd.index), X).fit(
            cov_type="cluster", cov_kwds={"groups": dd["code_commune"]})
        lo, hi = r.conf_int().loc["traite_x_post"]
        res[disc] = {"coef": round(float(r.params["traite_x_post"]), 4),
                     "ic_bas": round(float(lo), 4), "ic_haut": round(float(hi), 4),
                     "p": round(float(r.pvalues["traite_x_post"]), 4),
                     "n_obs": int(len(dd)), "n_colleges": int(dd.uai.nunique()),
                     "n_colleges_traites": int(dd[dd.traite_did == 1].uai.nunique()),
                     "n_communes": int(dd.code_commune.nunique())}
        print(f"     {disc:9} {res[disc]['coef']:+.3f} "
              f"[{res[disc]['ic_bas']:+.3f} ; {res[disc]['ic_haut']:+.3f}] p={res[disc]['p']:.3f} "
              f"({res[disc]['n_colleges_traites']} colleges traites)")
    return res


def event_study(panel, ref=2021):
    """Ecart traite-controle annee par annee, effets fixes college et annee.

    C'est le garde-fou du DiD : si les coefficients des annees ANTERIEURES a la
    bascule sont deja non nuls et tendanciels, les deux groupes ne suivaient pas
    la meme trajectoire et l'estimation DiD ne mesure pas un effet du rythme.
    """
    d = panel[panel.regime.isin(["bascule 4,5j vers 4j", "4,5j stable"])].copy()
    d["traite_did"] = (d.regime == "bascule 4,5j vers 4j").astype(int)
    res = {}
    for disc in ["francais", "maths"]:
        dd = d[d.disc == disc].dropna(subset=["z"]).copy()
        annees = [a for a in sorted(dd.annee.unique()) if a != ref]
        cols = []
        for a in annees:
            c = f"t{a}"
            dd[c] = dd.traite_did * (dd.annee == a)
            cols.append(c)
        X = pd.DataFrame({c: demean(dd, c, ["uai", "annee"]) for c in cols}, index=dd.index)
        y = pd.Series(demean(dd, "z", ["uai", "annee"]), index=dd.index)
        r = sm.OLS(y, sm.add_constant(X)).fit(cov_type="cluster", cov_kwds={"groups": dd["code_commune"]})
        coefs = []
        for a, c in zip(annees, cols):
            lo, hi = r.conf_int().loc[c]
            coefs.append({"annee": int(a), "coef": round(float(r.params[c]), 4),
                          "ic_bas": round(float(lo), 4), "ic_haut": round(float(hi), 4),
                          "p": round(float(r.pvalues[c]), 4)})
        coefs.append({"annee": ref, "coef": 0.0, "ic_bas": 0.0, "ic_haut": 0.0, "p": None,
                      "reference": True})
        coefs.sort(key=lambda x: x["annee"])
        # tendance pre-traitement : pente des coefficients des annees <= ref
        pre = [c for c in coefs if c["annee"] <= ref]
        xa = np.array([c["annee"] for c in pre], dtype=float)
        ya = np.array([c["coef"] for c in pre], dtype=float)
        pente = float(np.polyfit(xa, ya, 1)[0])
        # test joint de nullite des coefficients pre-traitement
        pre_cols = [f"t{int(c['annee'])}" for c in pre if not c.get("reference")]
        ftest = r.f_test(" = 0, ".join(pre_cols) + " = 0") if pre_cols else None
        p_joint = float(np.squeeze(ftest.pvalue)) if ftest is not None else None
        res[disc] = {
            "coefficients": coefs, "annee_reference": ref,
            "pente_pre_traitement": round(pente, 4),
            "p_test_joint_pre_traitement": round(p_joint, 4) if p_joint is not None else None,
            "tendances_paralleles": bool(p_joint is not None and p_joint > 0.05),
        }
        verdict = "OK" if res[disc]["tendances_paralleles"] else "VIOLEES"
        print(f"     {disc:9} pente pre-traitement {pente:+.4f}/an, "
              f"test joint p={p_joint:.4f} -> tendances paralleles {verdict}")
    return res


def trajectoire(panel):
    """Écart annuel moyen à IPS comparable, par régime, 2017-2025.
    Sert de contrôle visuel des tendances parallèles avant la bascule."""
    out = []
    for disc in ["francais", "maths"]:
        for an in sorted(panel.annee.unique()):
            d = panel[(panel.disc == disc) & (panel.annee == an)].dropna(subset=["z", "ips_col"])
            if len(d) < 200:
                continue
            X = sm.add_constant(d[["ips_col"]].astype(float))
            d = d.assign(resid=sm.OLS(d["z"].astype(float), X).fit().resid)
            ref = d.loc[d.regime == "4,5j stable", "resid"].mean()
            for reg in ["4,5j stable", "bascule 4,5j vers 4j", "4j stable"]:
                s = d.loc[d.regime == reg, "resid"]
                if len(s) < 20:
                    continue
                out.append({"discipline": disc, "annee": int(an), "regime": reg,
                            "ecart_a_45j": round(float(s.mean() - ref), 4), "n": int(len(s))})
    return out


# ============================================================
# 6. IVAC : la démonstration du contre-exemple
# ============================================================
def sur_ivac(base):
    ivac = export_csv("fr-en-indicateurs-valeur-ajoutee-colleges",
                      "session,uai,secteur,nb_candidats_g,taux_de_reussite_g,"
                      "va_du_taux_de_reussite_g,note_a_l_ecrit_g,va_de_la_note_g")
    ivac["session"] = ivac["session"].astype(str).str[:4]
    ivac = ivac[(ivac.session == "2025") & (ivac.secteur == "PU")].copy()
    libelles = {"note_a_l_ecrit_g": "note brute a l'ecrit du DNB",
                "va_de_la_note_g": "valeur ajoutee de cette note (IVAC)",
                "taux_de_reussite_g": "taux de reussite brut",
                "va_du_taux_de_reussite_g": "valeur ajoutee du taux (IVAC)"}
    for c in libelles:
        ivac[c] = pd.to_numeric(ivac[c], errors="coerce")
    d = base.merge(ivac, on="uai")
    res = {}
    print("\n   Sur les resultats du DNB, session 2025 (unites d'origine)")
    for c, lib in libelles.items():
        d2 = d.dropna(subset=[c])
        if len(d2) < 200:
            continue
        brut = regression(d2, c, [])
        net = regression(d2, c, ["ips_col", "ips_ecoles", "log_pop", "revenu", "diplome_sup", "FE_DEP"])
        res[c] = {"libelle": lib, "brut": brut, "controle": net}
        print(f"     {lib:38} brut {brut['coef']:+.2f}  |  controle {net['coef']:+.2f} (p={net['p']:.3f})")
    return res


# ============================================================
# Assemblage
# ============================================================
def main():
    print("Regime scolaire par commune...")
    com = regimes_communaux()

    print("Evaluations d'entree en 6e...")
    ev = evaluations_6e()

    print("Controles...")
    col = colleges_publics()
    ipsc = ips_colleges()
    ipse = ips_ecoles_commune()
    ctx = contexte_communal()

    base = (col.join(com, on="code_commune", how="inner")
               .join(ipse, on="code_commune")
               .join(ctx, on="code_commune"))
    base["ips_col"] = base["uai"].map(ipsc)
    base["log_pop"] = np.log(pd.to_numeric(base["pop"], errors="coerce").clip(lower=1))
    base["n_col_commune"] = base.groupby("code_commune")["uai"].transform("size")
    base = base[base.regime.isin(["4j stable", "4,5j stable", "bascule 4,5j vers 4j"])].copy()
    base["traite"] = (base.regime == "4,5j stable").astype(int)
    print(f"   socle : {len(base)} colleges publics dans {base.code_commune.nunique()} communes")

    panel = base.merge(ev[["uai", "annee", "disc", "z", "score", "effectif"]], on="uai", how="inner")

    an_max = int(panel.annee.max())
    coupe = (panel[panel.annee == an_max]
             .pivot_table(index="uai", columns="disc", values="z")
             .join(base.set_index("uai")).reset_index())

    resultats = {}
    for disc in ["francais", "maths"]:
        cible = coupe[coupe[disc].notna()].copy()
        cible["y"] = cible[disc]
        resultats[disc] = {
            "ensemble": escalier(cible, "y", f"A. Ensemble des colleges publics, {disc} {an_max}"),
            "college_unique": escalier(cible[cible.n_col_commune == 1].copy(), "y",
                                       f"B. Communes a college unique, {disc} {an_max}"),
        }

    print("\n   C. Difference-de-differences (bascule 4,5j vers 4j contre 4,5j stable)")
    did = diff_en_diff(panel)

    print("\n   Validite du DiD : tendances anterieures a la bascule")
    event = event_study(panel)
    for disc, r in event.items():
        if disc in did:
            did[disc]["tendances_paralleles"] = r["tendances_paralleles"]
            did[disc]["interpretation"] = (
                "Effet interpretable comme causal sous reserve des autres hypotheses."
                if r["tendances_paralleles"] else
                "NON INTERPRETABLE comme un effet du rythme : les deux groupes divergeaient "
                "deja avant la bascule (tendances paralleles rejetees).")

    print("\n   Trajectoire annuelle...")
    traj = trajectoire(panel)

    ivac = sur_ivac(base)

    desc = []
    for reg, g in coupe.groupby("regime"):
        desc.append({
            "regime": reg, "n_colleges": int(len(g)),
            "n_communes": int(g.code_commune.nunique()),
            "n_colleges_commune_unique": int((g.n_col_commune == 1).sum()),
            "ips_college": round(float(g.ips_col.mean()), 1),
            "ips_ecoles_primaires": round(float(g.ips_ecoles.mean()), 1),
            "population_mediane": int(g["pop"].median()) if g["pop"].notna().any() else None,
            "revenu_median": int(g.revenu.median()) if g.revenu.notna().any() else None,
            "ecoles_par_commune_mediane": float(g.n_ecoles.astype(float).median()),
            "score_francais_z": round(float(g.francais.mean()), 3),
            "score_maths_z": round(float(g.maths.mean()), 3),
        })

    payload = {
        "meta": {
            "titre": "Semaine de 4 jours ou 4,5 jours : quel effet sur les resultats ?",
            "annee_resultats": an_max,
            "unite": "ecart-type du score d'entree en 6e (1 ecart-type vaut environ 16 points)",
            "lecture": "Un coefficient positif signifie de meilleurs resultats dans les "
                       "communes restees a 4,5 jours.",
            "avertissements": [
                "Les donnees de rythme scolaire ne sont publiees que pour 2020-2021 et "
                "2025-2026 : le retour massif aux 4 jours (2017-2018) n'est pas observable.",
                "La carte scolaire des colleges ne suit pas les limites communales ; "
                "l'echantillon a college unique limite ce bruit sans le supprimer.",
                "L'IVAC controle le score d'entree en 6e : il ne peut pas capter un effet "
                "du primaire, il est presente ici comme contre-exemple.",
            ],
            "sources": [
                {"nom": "Organisation du temps scolaire",
                 "url": "https://data.education.gouv.fr/explore/dataset/fr-en-organisation-du-temps-scolaire/"},
                {"nom": "Evaluations nationales de 6e par etablissement",
                 "url": "https://data.education.gouv.fr/explore/dataset/fr-en-evaluations_nationales_6eme_par_etablissement/"},
                {"nom": "IPS des ecoles",
                 "url": "https://data.education.gouv.fr/explore/dataset/fr-en-ips-ecoles-ap2022/"},
                {"nom": "IPS des colleges",
                 "url": "https://data.education.gouv.fr/explore/dataset/fr-en-ips-colleges-ap2023/"},
                {"nom": "Indicateurs de valeur ajoutee des colleges",
                 "url": "https://data.education.gouv.fr/explore/dataset/fr-en-indicateurs-valeur-ajoutee-colleges/"},
                {"nom": "Annuaire de l'education",
                 "url": "https://data.education.gouv.fr/explore/dataset/fr-en-annuaire-education/"},
            ],
        },
        "couverture": {
            "communes_appariees": int(len(com)),
            "communes_par_regime": {k: int(v) for k, v in com.regime.value_counts().items()},
            "colleges_publics_analyses": int(len(base)),
            "annees_evaluations": [int(panel.annee.min()), int(panel.annee.max())],
        },
        "groupes": desc,
        "transversal": resultats,
        "difference_en_differences": did,
        "event_study": event,
        "trajectoire": traj,
        "ivac_contre_exemple": ivac,
    }

    dest = OUT / "rythmes-scolaires.json"
    dest.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n-> {dest.name} ({dest.stat().st_size / 1024:.0f} Ko)")
    print("TERMINE.")


if __name__ == "__main__":
    main()
