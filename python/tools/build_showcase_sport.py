# -*- coding: utf-8 -*-
"""
Dossier « Sport » : assemble les résultats de l'exploration des licences sportives (INJEP)
et de l'offre (équipements Data ES, clubs INJEP) en un JSON pour la page /terrains/sport.

Dépend des tables écrites par explore_sport_injep.py puis explore_sport_offre.py dans
python/data/sport/sorties/ (méthode détaillée : docs/sport/exploration_injep.md).
Les fédérations scolaires et universitaires (UNSS, USEP, FFSU...) sont exclues partout.

Sortie : frontend/public/data/showcases/sport.json
"""
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SORTIES = ROOT / "python" / "data" / "sport" / "sorties"
OUT = ROOT / "frontend" / "public" / "data" / "showcases" / "sport.json"


def t(nom):
    return pd.read_csv(SORTIES / f"{nom}.csv", dtype={"dep": str, "fed": str})


r1 = lambda x: None if pd.isna(x) else round(float(x), 1)
r2 = lambda x: None if pd.isna(x) else round(float(x), 2)

# Fédérations multisports (codes INJEP 4xx, et 5xx handisport / sport adapté) : leurs
# licences ne disent pas quel sport est pratiqué (une licence UFOLEP ou FSGT peut être du
# foot, de la gym ou de la randonnée). Elles comptent dans les totaux, jamais dans un
# classement « par sport ».
fed_dep = t("b_dep_federation_2023")
UNISPORT = fed_dep.fed.str[:1].isin(["1", "2"])
MULTISPORT_NOMS = set(fed_dep.loc[~UNISPORT, "sport"]) | set(fed_dep.loc[~UNISPORT, "nomfed"])
familles = t("a_familles_2023").set_index("famille")
lic_hors_scol = familles.drop(index="scolaire et universitaire").licences.sum()
lic_multi = familles.loc[["multisports", "multisports (handi, adapté)"], "licences"].sum()

# 1. Départements : sport le plus pratiqué, sport « signature », licences pour 1 000 habitants.
uni = fed_dep[UNISPORT]
premier = (uni.sort_values(["dep", "licences"], ascending=[True, False])
           .groupby("dep").head(1).set_index("dep"))
# Même règle que l'exploration (>= 20 000 licences nationales, >= 500 dans le département),
# parmi les seules fédérations unisport.
cand = uni[(uni.lic_nat >= 20000) & (uni.licences >= 500)]
signature = (cand.sort_values("indice_specialisation", ascending=False)
             .groupby("dep").head(1).set_index("dep"))
total = t("b_dep_total_2023")
total = total.set_index(total.columns[0])
col_taux = next(c for c in total.columns if "1000" in c)
departements = []
for dep in premier.index:
    departements.append({
        "code": dep,
        "premier": premier.loc[dep, "sport"],
        "premier_pour_1000": r1(premier.loc[dep, "pour_1000"]),
        "signature": signature.loc[dep, "sport"] if dep in signature.index else None,
        "signature_indice": r1(signature.loc[dep, "indice_specialisation"]) if dep in signature.index else None,
        "licences_pour_1000": r1(total.loc[dep, col_taux]) if dep in total.index else None,
    })

# 2. Quartiers prioritaires contre reste de la même commune (2023).
res = t("c_qpv_resume_2023").iloc[0]
qpv = {
    "communes": int(res["communes"]),
    "pop_qpv": int(res["pop_qpv"]),
    "taux_qpv": r1(res["taux_qpv"]), "taux_hors": r1(res["taux_hors_qpv"]),
    "taux_f_qpv": r1(res["taux_f_qpv"]), "taux_f_hors": r1(res["taux_f_hors"]),
    "taux_h_qpv": r1(res["taux_h_qpv"]), "taux_h_hors": r1(res["taux_h_hors"]),
    "part_communes_qpv_mieux": r1(res["part_communes_qpv_sup"] * 100),
}
fed = t("c_qpv_vs_horsqpv_federations_2023")
fed = fed[(fed.Q + fed.H >= 20000) & fed.fed.str[:1].isin(["1", "2"])].sort_values("H", ascending=False)
sports_qpv = [{
    "sport": r.sport, "part_qpv": r1(r.part_Q * 100), "part_hors": r1(r.part_H * 100),
    "taux_qpv": r1(r.taux_Q_pour_1000), "taux_hors": r1(r.taux_H_pour_1000),
    "rapport": r2(r.rapport_taux_Q_sur_H),
} for r in fed.head(16).itertuples()]

# 3. Décrochage à l'adolescence : licences 15-19 ans / 10-14 ans.
ret = t("c_qpv_retention_2023")
retention = {f"{r.sexe}_{r.zone}": r2(r.r_15_19_sur_10_14) for r in ret.itertuples()}
ret_fed = t("c_qpv_retention_federations_2023")
retention_sports = [{
    "sport": r.sport, "sexe": r.sexe, "qpv": r2(r.r_Q), "hors": r2(r.r_H),
} for r in ret_fed.itertuples() if r.sport in ("Football", "Basket", "Tennis", "Judo", "Natation", "Handball", "Équitation", "Danse")]

# 4. Revenu de la commune : licences, abandon à l'adolescence (2018, population par âge), sports.
dec = t("e_revenu_total_2023")
revenu_deciles = [{"decile": int(r.decile), "licences_pour_1000": r1(r.pour_1000),
                   "part_femmes": r1(r.part_femmes * 100)} for r in dec.itertuples()]
ages = t("e_revenu_age_sexe_2018_pivot")
abandon = [{"sexe": r.sexe, "decile": int(r.decile), "r_15_19": r2(r.r_15_19_sur_10_14),
            "r_20_29": r2(r.r_20_29_sur_15_19)} for r in ages.itertuples()]
sp = t("e_revenu_federations_2023").dropna(subset=["rapport_D10_D1"])
sp = sp[(sp["1"] + sp["10"] > 0.5) & ~sp.sport.isin(MULTISPORT_NOMS)]  # sports assez pratiqués, unisport
sp = sp.sort_values("rapport_D10_D1")
sports_revenu = [{"sport": r.sport, "d1": r2(r._2), "d10": r2(r._11), "rapport": r2(r.rapport_D10_D1)}
                 for r in sp.itertuples()]

# 5. Offre : équipements et clubs, quartier contre reste de la commune ; tests.
h = t("h_qpv_equipements_licences_2023")
clubs = t("g_test3_clubs_densite")
col_rc = next((c for c in clubs.columns if "rapport" in c.lower()), None)
rc = dict(zip(clubs.sport, clubs[col_rc])) if col_rc else {}
offre = [{
    "sport": r.sport, "equipements": r2(r.rapport_equipements_Q_sur_H), "clubs": r2(rc.get(r.sport)),
    "licences": r2(r.rapport_licences_Q_sur_H),
    "lic_par_equip_qpv": round(r.licences_par_equip_qpv), "lic_par_equip_hors": round(r.licences_par_equip_hors),
} for r in h.itertuples() if r.sport != "Karaté"]
t3 = t("g_test3_avec_sans_club")
test3 = []
for s, g in t3.groupby("sport"):
    avec = g[g.club.str.startswith("au moins")]
    sans = g[g.club.str.startswith("aucun")]
    if len(avec) and len(sans):
        test3.append({"sport": s, "avec_club": r2(avec.rapport_observe_attendu.iloc[0]),
                      "sans_club": r2(sans.rapport_observe_attendu.iloc[0]), "qpv_avec": int(avec.qpv.iloc[0])})
t4 = t("g_test4_did_clubs")
test4 = [{"sport": r.sport, "arrivees": int(r.n_arrivee_utilisables), "effet_arrivee": r2(r.did_arrivee),
          "ic_bas": r2(r.did_arrivee_ic90_bas), "ic_haut": r2(r.did_arrivee_ic90_haut),
          "departs": int(r.n_depart_utilisables), "effet_depart": r2(r.did_depart)}
         for r in t4.itertuples() if not pd.isna(r.did_arrivee)]

# 6. Dans le temps : licences 2013-2023 (indice) et part des femmes.
series = t("f_series_selection")
annees = [str(a) for a in range(2013, 2024)]
evolution = []
for s in ("Football", "Tennis", "Basket", "Rugby", "Judo", "Équitation", "Natation", "Handball"):
    row = series[series.sport == s]
    if len(row):
        row = row.iloc[0]
        evolution.append({"sport": s, "licences": {a: int(row[a]) for a in annees if not pd.isna(row[a])},
                          "evol_2019_2023": r1(row.evol_2019_2023 * 100)})
pf = t("f_series_part_femmes")
femmes = []
for s in ("Football", "Rugby", "Basket", "Tennis", "Judo", "Handball"):
    row = pf[pf.sport == s]
    if len(row):
        row = row.iloc[0]
        femmes.append({"sport": s, "part": {a: r1(row[a] * 100) for a in annees if not pd.isna(row[a])}})

# 7. L'élite (exploration docs/sport/exploration_elite.md, script explore_sport_elite.py).
# Diversité des noms des internationaux nés en France, en fourchette : rapport à la
# génération à l'adolescence (immigrés présents vers 17 ans comptés « diversité ») jusqu'au
# rapport aux seules naissances en France. Agrégats seulement, aucun nom.
EQUIPES = [("football_H", "Football, hommes"), ("basket_H", "Basket, hommes"),
           ("football_F", "Football, femmes"), ("rugby_H", "Rugby à XV, hommes"),
           ("JO2024_H", "Jeux de 2024, hommes (tous sports)"), ("JO2024_F", "Jeux de 2024, femmes (tous sports)")]
fo = t("elite_idp_fourchette")
fo = fo[fo.niveau == "grande période"]
fo["cle"] = [e if e != "JO2024" else f"JO2024_{s}" for e, s in zip(fo.equipe, fo.sexe_equipe)]
elite_noms = []
for cle, lib in EQUIPES:
    ligne = {"equipe": lib}
    for periode, k in (("1971-1990", "p1971"), ("1991 et après", "p1991")):
        if cle.startswith("JO2024") and k == "p1971":
            continue  # la délégation 2024 sert de repère pour la génération récente seulement
        g = fo[(fo.cle == cle) & (fo.periode == periode)]
        if len(g) and not pd.isna(g.iloc[0].rapport_bas_ado):
            r = g.iloc[0]
            ligne[k] = {"bas": r2(r.rapport_bas_ado), "haut": r2(r.rapport_haut), "idp": r1(r.idp_pct),
                        "n": int(r.n_reconnus), "ref_naissances": r1(r.ref_basse_naissances_pct),
                        "ref_ado": r1(r.ref_haute_ado_pct), "bas_max": r2(r.rapport_bas)}
    elite_noms.append(ligne)

zo = t("elite_zones_focus")
zo = zo[(zo.cohorte == "nés en 1970 et après") & (zo.annee_licences == 2013)]
elite_zones = []
for zone, lib in (("Paris et petite couronne (75, 92, 93, 94)", "Paris et petite couronne"),
                  ("Outre-mer (971 à 974)", "Outre-mer (Antilles, Guyane, Réunion)")):
    ligne = {"zone": lib}
    for sport in ("football", "rugby à XV", "basket-ball", "handball"):
        g = zo[(zo.zone == zone) & (zo.sport == sport)]
        if len(g):
            r = g.iloc[0]
            signif = not pd.isna(r.ic90_quasi_bas) and r.ic90_quasi_bas > 1
            ligne[sport] = {"rapport": r2(r.rapport), "observes": int(r.observes), "attendus": r1(r.attendus),
                            "significatif": bool(signif)}
    elite_zones.append(ligne)

out = {
    "titre": "Le sport, miroir des inégalités ?",
    "elite_noms": elite_noms,
    "elite_zones": elite_zones,
    "millesime": 2023,
    "multisport": {"licences": int(lic_multi), "part": r1(lic_multi / lic_hors_scol * 100)},
    "departements": departements,
    "qpv": qpv,
    "sports_qpv": sports_qpv,
    "retention": retention,
    "retention_sports": retention_sports,
    "revenu_deciles": revenu_deciles,
    "abandon_revenu_2018": abandon,
    "sports_revenu": sports_revenu,
    "offre": offre,
    "test3": test3,
    "test4": test4,
    "evolution": evolution,
    "femmes": femmes,
    "sources": [
        {"label": "INJEP-MEDES, recensement des licences et clubs sportifs (données géocodées par l'Insee)",
         "url": "https://www.data.gouv.fr/datasets/donnees-geocodees-issues-du-recensement-des-licences-et-clubs-aupres-des-federations-sportives-agreees-par-le-ministere-charge-des-sports"},
        {"label": "Ministère chargé des sports, recensement des équipements sportifs (Data ES)",
         "url": "https://equipements.sports.gouv.fr/"},
        {"label": "ANCT, contours et population des quartiers prioritaires",
         "url": "https://www.data.gouv.fr/datasets/quartiers-prioritaires-de-la-politique-de-la-ville-qpv"},
        {"label": "Insee, Filosofi 2023 (revenu des communes) et recensement de la population 2021",
         "url": "https://www.insee.fr/fr/statistiques/8984752"},
    ],
}
OUT.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print(f"-> {OUT.name} ({OUT.stat().st_size / 1e3:.0f} ko) : {len(departements)} départements, "
      f"{len(sports_qpv)} sports QPV, {len(offre)} sports offre, {len(test3)} test 3, {len(test4)} test 4")
