# -*- coding: utf-8 -*-
"""
Terrain « Selectivite » (sujet G) : qui peut entrer dans le superieur ?

Trois blocs calcules depuis fr-esr-parcoursup (MESR, une ligne par formation) :
  1. classement des filieres par selectivite (taux d'acces median, voeux par place) ;
  2. matrice academie x filiere : a filiere egale, ou l'acces est-il le plus dur ;
  3. ouverture sociale : % d'admis boursiers par filiere + croisement intra-filiere
     (tiers le plus selectif vs tiers le plus ouvert, la nuance CPGE).

Reutilise le cache de validate_parcoursup.py (_cache_parcoursup/parcoursup.csv,
vider pour changer de session).

Sortie : frontend/public/data/showcases/selectivite.json
"""
import json
import urllib.request
from datetime import date
from pathlib import Path

import pandas as pd

SCRIPT_DIR = Path(__file__).parent.resolve()
CACHE = SCRIPT_DIR / "_cache_parcoursup"
CACHE.mkdir(exist_ok=True)
CSV = CACHE / "parcoursup.csv"
BASE = "https://data.enseignementsup-recherche.gouv.fr/api/explore/v2.1/catalog/datasets/"
URL = BASE + "fr-esr-parcoursup/exports/csv"
OUT = SCRIPT_DIR.parent.parent / "frontend" / "public" / "data" / "showcases" / "selectivite.json"

# Evolution longue 2018 -> session courante. Le taux d'acces OFFICIEL (rang du dernier
# appele) n'existe que depuis 2022 et ne peut pas etre recalcule avant : decision S.
# (2026-07-06), pas de pseudo-taux, la serie longue porte les DEUX AUTRES indicateurs
# (pression = voeux/place, taux d'acceptation = acceptations/candidatures), et le taux
# officiel s'affiche la ou il existe. Nommage MESR incoherent : tiret puis underscore.
SESSIONS_EVOL = {
    2018: "fr-esr-parcoursup-2018",
    2019: "fr-esr-parcoursup-2019",
    2020: "fr-esr-parcoursup_2020",
    2021: "fr-esr-parcoursup_2021",
    2022: "fr-esr-parcoursup_2022",
    2023: "fr-esr-parcoursup_2023",
    2024: "fr-esr-parcoursup_2024",
    2025: "fr-esr-parcoursup",
}
FILI_ALIAS_EVOL = {"DUT": "BUT"}   # meme reseau IUT, renomme en 2021
FILI_EXCLUS_EVOL = {"PACES"}       # reforme des etudes de sante : non comparable a PASS
MIN_N_EVOL = 15                    # formations minimum pour un point de serie

MIN_N_DETAIL = 15     # formations minimum pour classer une filiere detaillee
MIN_N_CELLULE = 10    # formations minimum pour une cellule academie x filiere
MIN_N_ACADEMIE = 30   # formations minimum pour garder une academie dans la matrice

FILI_LABELS = {
    "PASS": "PASS (accès santé)",
    "IFSI": "IFSI (soins infirmiers)",
    "CPGE": "Classes préparatoires (CPGE)",
    "EFTS": "Travail social (EFTS)",
    "BUT": "BUT (ex-DUT)",
    "Licence_Las": "Licence accès santé (LAS)",
    "BTS": "BTS",
    "Ecole de Commerce": "Écoles de commerce",
    "Ecole d'Ingénieur": "Écoles d'ingénieurs",
    "Licence": "Licence",
    "Autre formation": "Autres formations",
}
MATRICE_FILIERES = ["BTS", "Licence", "BUT", "CPGE", "IFSI"]
CROISEMENT_FILIERES = ["CPGE", "Ecole d'Ingénieur", "Ecole de Commerce", "BUT", "BTS", "IFSI", "Licence"]


def charge_session(annee, dataset_id):
    """CSV d'une session (cache), colonnes tolerantes : les vieux jeux n'ont pas tout."""
    path = CSV if dataset_id == "fr-esr-parcoursup" else CACHE / f"parcoursup_{annee}.csv"
    if not path.exists():
        print(f"   telechargement session {annee}...")
        req = urllib.request.Request(BASE + dataset_id + "/exports/csv",
                                     headers={"User-Agent": "outsiders/1.0"})
        with urllib.request.urlopen(req, timeout=600) as r:
            path.write_bytes(r.read())
    dispo = pd.read_csv(path, sep=";", nrows=0).columns
    want = [c for c in ["fili", "voe_tot", "capa_fin", "acc_tot", "taux_acces_ens"] if c in dispo]
    s = pd.read_csv(path, sep=";", low_memory=False, usecols=want)
    for c in want:
        if c != "fili":
            s[c] = pd.to_numeric(s[c], errors="coerce")
    if "taux_acces_ens" not in s.columns:
        s["taux_acces_ens"] = float("nan")
    s["fili"] = s["fili"].replace(FILI_ALIAS_EVOL)
    return s[~s["fili"].isin(FILI_EXCLUS_EVOL) & (s["voe_tot"] > 0)]


def bloc_evolution():
    """Series par filiere : pression et taux d'acceptation depuis 2018, taux d'acces
    officiel la ou il existe (2022+). Pas de pseudo-taux recalcule."""
    par_session = {a: charge_session(a, did) for a, did in SESSIONS_EVOL.items()}
    annees = sorted(par_session)
    filis = sorted(set().union(*(set(s["fili"].dropna().unique()) for s in par_session.values())))
    filieres = []
    for fili in filis:
        serie = []
        for a in annees:
            s = par_session[a]
            sf = s[s["fili"] == fili]
            if len(sf) < MIN_N_EVOL:
                continue
            places = sf["capa_fin"].sum()
            acces = sf["taux_acces_ens"].median()
            accept = (sf["acc_tot"] / sf["voe_tot"] * 100).median() if "acc_tot" in sf.columns else float("nan")
            serie.append({
                "a": a,
                "n": int(len(sf)),
                "pression": round(float(sf["voe_tot"].sum() / places), 1) if places else None,
                "acceptation": round(float(accept), 1) if pd.notna(accept) else None,
                "acces": round(float(acces)) if pd.notna(acces) else None,
            })
        if len(serie) >= 4:  # au moins 4 sessions pour parler de trajectoire
            filieres.append({"id": fili, "label": FILI_LABELS.get(fili, fili), "serie": serie})

    # ordre par defaut : la pression qui monte le plus (se ferme) en premier
    def delta_pression(f):
        pts = [p["pression"] for p in f["serie"] if p["pression"] is not None]
        return pts[-1] - pts[0] if len(pts) >= 2 else 0
    filieres.sort(key=delta_pression, reverse=True)

    licence_100 = []
    for a in annees:
        lic = par_session[a]
        lic = lic[(lic["fili"] == "Licence") & lic["taux_acces_ens"].notna()]
        if len(lic) >= MIN_N_EVOL:
            licence_100.append({"a": a, "pct": round(float((lic["taux_acces_ens"] >= 100).mean() * 100))})
    return {"sessions": annees, "filieres": filieres, "licence_pct_100": licence_100}


def pct_boursiers_pondere(s):
    """% d'admis boursiers pondere par le nombre d'admis."""
    m = s["pct_bours"].notna() & (s["acc_tot"] > 0)
    if not m.any():
        return None
    return round(float((s.loc[m, "pct_bours"] * s.loc[m, "acc_tot"]).sum() / s.loc[m, "acc_tot"].sum()), 1)


def main():
    if not CSV.exists():
        print("Telechargement du CSV Parcoursup...")
        req = urllib.request.Request(URL, headers={"User-Agent": "outsiders/1.0"})
        with urllib.request.urlopen(req, timeout=600) as r:
            CSV.write_bytes(r.read())
    df = pd.read_csv(CSV, sep=";", low_memory=False)
    for c in ["capa_fin", "voe_tot", "prop_tot", "acc_tot", "taux_acces_ens", "pct_bours"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    session = int(df["session"].iloc[0])
    d = df[df["taux_acces_ens"].notna() & (df["voe_tot"] > 0)].copy()
    print(f"{len(d)} formations exploitables, session {session}")

    # ------------------------------------------------------------------
    # 1. Filieres agregees, classees de la plus selective a la plus ouverte.
    # Trois lectures complementaires (demande S., 2026-07-06) :
    #  - taux d'acces (officiel) : part des candidats en position de recevoir une
    #    proposition (rang du dernier appele). LA mesure de la porte d'entree.
    #  - pression : voeux par place (la demande).
    #  - taux d'acceptation : acceptations / candidatures. Mesure la CONVERSION,
    #    melange selectivite et attractivite (un candidat n'accepte qu'un voeu).
    d["acceptation"] = (d["acc_tot"] / d["voe_tot"] * 100).where(d["acc_tot"].notna())
    filieres = []
    for fili, s in d.groupby("fili"):
        places = s["capa_fin"].sum()
        filieres.append({
            "id": fili,
            "label": FILI_LABELS.get(fili, fili),
            "n": int(len(s)),
            "taux_median": round(float(s["taux_acces_ens"].median())),
            "voeux_par_place": round(float(s["voe_tot"].sum() / places), 1) if places else None,
            "taux_acceptation": round(float(s["acceptation"].median()), 1),
            "pct_boursiers": pct_boursiers_pondere(s),
        })
    filieres.sort(key=lambda x: x["taux_median"])

    # 1b. Filieres detaillees les plus selectives
    det = d.groupby("form_lib_voe_acc").agg(
        n=("form_lib_voe_acc", "size"), taux=("taux_acces_ens", "median"))
    det = det[det["n"] >= MIN_N_DETAIL].sort_values("taux").head(15)
    detaillees = [{"label": lib, "n": int(r["n"]), "taux_median": round(float(r["taux"]))}
                  for lib, r in det.iterrows()]

    # ------------------------------------------------------------------
    # 2. Matrice academie x filiere (taux d'acces median, cellules >= MIN_N_CELLULE)
    acads_ok = d.groupby("acad_mies").size()
    acads_ok = set(acads_ok[acads_ok >= MIN_N_ACADEMIE].index)
    rows = []
    for acad, s in d[d["acad_mies"].isin(acads_ok)].groupby("acad_mies"):
        row = {"academie": acad, "n": int(len(s))}
        vals = []
        for fili in MATRICE_FILIERES:
            sf = s[s["fili"] == fili]
            v = round(float(sf["taux_acces_ens"].median())) if len(sf) >= MIN_N_CELLULE else None
            row[fili] = v
            if v is not None:
                vals.append(v)
        # moyenne affichable seulement si l'academie a au moins 2 filieres renseignees
        # (sinon Mayotte, BTS seul, trierait en tete sur une seule cellule)
        row["moyenne"] = round(sum(vals) / len(vals)) if len(vals) >= 2 else None
        rows.append(row)
    rows.sort(key=lambda r: r["moyenne"] if r["moyenne"] is not None else 999)

    # Ecart max par filiere (le chiffre « a filiere egale, tout change »)
    ecarts = {}
    for fili in MATRICE_FILIERES:
        vals = [(r[fili], r["academie"]) for r in rows if r[fili] is not None]
        if len(vals) >= 5:
            lo, hi = min(vals), max(vals)
            ecarts[fili] = {"dur": {"academie": lo[1], "taux": lo[0]},
                            "ouvert": {"academie": hi[1], "taux": hi[0]},
                            "ecart": hi[0] - lo[0]}

    # ------------------------------------------------------------------
    # 2b. La licence est-elle encore ouverte a tous ? (demande S., 2026-07-04)
    # Part des licences qui acceptent tous leurs candidats (taux d'acces >= 100),
    # ensemble et par region : la ou la licence « non selective » ne l'est plus.
    lic = d[d["fili"] == "Licence"]
    regions_lic = []
    for reg, s in lic.groupby("region_etab_aff"):
        if len(s) < 10:
            continue
        regions_lic.append({
            "region": reg,
            "n": int(len(s)),
            "pct_100": round(float((s["taux_acces_ens"] >= 100).mean() * 100)),
            "taux_median": round(float(s["taux_acces_ens"].median())),
        })
    regions_lic.sort(key=lambda r: r["pct_100"])
    licence = {
        "n": int(len(lic)),
        "pct_100": round(float((lic["taux_acces_ens"] >= 100).mean() * 100)),
        "pct_sous_50": round(float((lic["taux_acces_ens"] < 50).mean() * 100)),
        "regions": regions_lic,
    }

    # ------------------------------------------------------------------
    # 3. Croisement selectivite x boursiers, intra-filiere
    croisement = []
    for fili in CROISEMENT_FILIERES:
        s = d[(d["fili"] == fili) & d["pct_bours"].notna() & (d["acc_tot"] > 0)]
        if len(s) < 60:
            continue
        t1, t2 = s["taux_acces_ens"].quantile([0.33, 0.66])
        croisement.append({
            "id": fili,
            "label": FILI_LABELS.get(fili, fili),
            "selectif": pct_boursiers_pondere(s[s["taux_acces_ens"] <= t1]),
            "ouvert": pct_boursiers_pondere(s[s["taux_acces_ens"] >= t2]),
        })

    # ------------------------------------------------------------------
    # 4. Evolution 2022 -> 2025 : qui se ferme, qui s'ouvre
    print("Evolution par session...")
    evolution = bloc_evolution()

    # ------------------------------------------------------------------
    plus_dure = detaillees[0]
    ecart_bts = ecarts.get("BTS")
    bours_tries = sorted((f for f in filieres if f["pct_boursiers"] is not None),
                         key=lambda f: f["pct_boursiers"])
    out = {
        "generated": date.today().isoformat(),
        "session": session,
        "titre": "Qui peut entrer ? La sélectivité du supérieur",
        "source": {
            "label": f"MESR, Parcoursup {session} (vœux et admissions par formation)",
            "url": "https://data.enseignementsup-recherche.gouv.fr/explore/dataset/fr-esr-parcoursup/",
        },
        "stats": {
            "n_formations": int(len(d)),
            "n_voeux": int(d["voe_tot"].sum()),
            "plus_dure": plus_dure,
            "ecart_bts": ecart_bts,
            "boursiers_min": bours_tries[0],
            "boursiers_max": bours_tries[-1],
        },
        "filieres": filieres,
        "detaillees": detaillees,
        "licence": licence,
        "evolution": evolution,
        "matrice": {"filieres": MATRICE_FILIERES,
                    "labels": {f: FILI_LABELS.get(f, f) for f in MATRICE_FILIERES},
                    "rows": rows, "ecarts": ecarts,
                    "seuil_cellule": MIN_N_CELLULE},
        "croisement": croisement,
        "notes": [
            "Le taux d'accès (mesure officielle) est la part des candidats en position de recevoir une proposition, d'après le rang du dernier appelé : c'est la longueur de la file d'attente, pas le niveau exigé.",
            "Le taux d'acceptation (acceptations / candidatures) mesure la conversion d'une candidature en inscription : il mélange sélectivité et attractivité, chaque candidat n'acceptant qu'un seul de ses vœux.",
            "La pression (vœux par place) mesure la demande : une pression forte peut venir du manque de places comme de l'attractivité.",
            "Toutes ces mesures reposent sur les candidatures exprimées : l'auto-censure (ne pas oser candidater) est invisible. Une filière qui « s'ouvre » peut reculer en attractivité comme gagner en auto-censure.",
            "« Autres formations » change de composition au fil des intégrations à Parcoursup : son évolution reflète surtout l'arrivée de nouveaux types de formations.",
            "« Boursiers » : néo-bacheliers boursiers du secondaire, parmi les admis.",
            f"Filières détaillées classées à partir de {MIN_N_DETAIL} formations ; cellules académie × filière à partir de {MIN_N_CELLULE} formations.",
            f"Classements et matrice : session {session}. Évolution : la pression et le taux d'acceptation remontent à 2018 ; le taux d'accès officiel n'existe que depuis 2022 et ne peut pas être recalculé avant (il repose sur le rang du dernier appelé, non publié). BUT = DUT avant 2021 ; PACES exclue (réforme des études de santé) ; session 2020 marquée par le covid.",
        ],
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"-> {OUT}")
    print(f"   {len(filieres)} filières, matrice {len(rows)} académies × {len(MATRICE_FILIERES)}, "
          f"{len(croisement)} croisements")
    print(f"   plus dure : {plus_dure['label']} ({plus_dure['taux_median']}%), "
          f"écart BTS {ecart_bts['ecart']} pts ({ecart_bts['dur']['academie']} vs {ecart_bts['ouvert']['academie']})")
    print(f"   licences acceptant tous leurs candidats : {licence['pct_100']}% "
          f"(de {licence['regions'][0]['pct_100']}% en {licence['regions'][0]['region']} "
          f"à {licence['regions'][-1]['pct_100']}% en {licence['regions'][-1]['region']})")
    print("   evolution (pression : voeux/place, hausse = se ferme) :")
    for f in evolution["filieres"]:
        pts = [(p["a"], p["pression"]) for p in f["serie"] if p["pression"] is not None]
        acc = [(p["a"], p["acceptation"]) for p in f["serie"] if p["acceptation"] is not None]
        if len(pts) < 2:
            continue
        print(f"      {f['label']:38.38} pression {pts[0][1]:5.1f} ({pts[0][0]}) -> {pts[-1][1]:5.1f} ({pts[-1][0]})"
              + (f"  | acceptation {acc[0][1]:.0f}% -> {acc[-1][1]:.0f}%" if len(acc) >= 2 else ""))
    l100 = evolution["licence_pct_100"]
    print(f"   licences 100% ouvertes (taux officiel) : {' -> '.join(str(x['pct']) + '%' for x in l100)}")


if __name__ == "__main__":
    main()
