# -*- coding: utf-8 -*-
"""
Sujet G « Selectivite » - VALIDATION des donnees Parcoursup (n'ecrit rien).

Teste les trois angles sur le jeu fr-esr-parcoursup (MESR, une ligne par formation) :
  1. Quelles disciplines selectionnent le plus ? (taux d'acces, voeux par place)
  2. A discipline egale, la selectivite change-t-elle selon l'academie ?
  3. Ouverture sociale : % d'admis boursiers par type de formation
     (hypothese socio-analyse : les formations « a projet » sont-elles les plus fermees ?)

Usage : python python/tools/validate_parcoursup.py
Cache : python/tools/_cache_parcoursup/parcoursup.csv (~20 Mo)
"""
import urllib.request
from pathlib import Path

import pandas as pd

CACHE = Path(__file__).resolve().parent / "_cache_parcoursup"
CACHE.mkdir(exist_ok=True)
CSV = CACHE / "parcoursup.csv"
URL = ("https://data.enseignementsup-recherche.gouv.fr/api/explore/v2.1/"
       "catalog/datasets/fr-esr-parcoursup/exports/csv")

MIN_FORMATIONS = 15  # en dessous, une filiere detaillee n'est pas classee


def main():
    if not CSV.exists():
        print("Telechargement du CSV Parcoursup (~20 Mo)...")
        req = urllib.request.Request(URL, headers={"User-Agent": "outsiders/1.0"})
        with urllib.request.urlopen(req, timeout=600) as r:
            CSV.write_bytes(r.read())
    print(f"Lecture {CSV.name}...")
    df = pd.read_csv(CSV, sep=";", low_memory=False)
    print(f"   {len(df)} formations, {len(df.columns)} colonnes, sessions : {sorted(df['session'].unique())}")

    for c in ["capa_fin", "voe_tot", "acc_tot", "taux_acces_ens", "pct_bours"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    ok = df["taux_acces_ens"].notna() & df["voe_tot"].notna() & (df["voe_tot"] > 0)
    print(f"   taux d'acces renseigne : {ok.sum()}/{len(df)} ({ok.mean():.0%})")
    d = df[ok].copy()

    # ------------------------------------------------------------------
    print("\n=== 1. Selectivite par filiere agregee (fili) ===")
    print("   (taux d'acces median : % des candidats en position de recevoir une proposition)")
    g = d.groupby("fili").agg(
        n=("fili", "size"),
        taux_median=("taux_acces_ens", "median"),
        voeux=("voe_tot", "sum"),
        places=("capa_fin", "sum"),
    ).sort_values("taux_median")
    for fili, r in g.iterrows():
        vp = r["voeux"] / r["places"] if r["places"] else float("nan")
        print(f"   {str(fili):42.42} n={r['n']:5}  taux acces med {r['taux_median']:5.0f}%  "
              f"voeux/place {vp:5.1f}")

    print("\n=== 1b. Filieres detaillees les plus selectives (form_lib_voe_acc, n >= 15) ===")
    g2 = d.groupby("form_lib_voe_acc").agg(
        n=("form_lib_voe_acc", "size"), taux=("taux_acces_ens", "median"),
    )
    g2 = g2[g2["n"] >= MIN_FORMATIONS].sort_values("taux")
    for lib, r in g2.head(12).iterrows():
        print(f"   {str(lib):58.58} n={r['n']:4}  taux {r['taux']:4.0f}%")

    # ------------------------------------------------------------------
    print("\n=== 2. A filiere egale, l'academie change-t-elle l'acces ? ===")
    for fili in ["BTS", "Licence", "BUT", "IFSI"]:
        sub = d[d["fili"] == fili]
        if not len(sub):
            continue
        ga = sub.groupby("acad_mies")["taux_acces_ens"].median().sort_values()
        ga = ga[sub.groupby("acad_mies").size() >= 30]  # academies avec assez de formations
        if len(ga) < 5:
            continue
        print(f"   {fili:8} : acces le plus dur {ga.index[0]} ({ga.iloc[0]:.0f}%) | "
              f"le plus ouvert {ga.index[-1]} ({ga.iloc[-1]:.0f}%) | ecart {ga.iloc[-1] - ga.iloc[0]:.0f} pts")

    # ------------------------------------------------------------------
    print("\n=== 3. Ouverture sociale : % d'admis boursiers par filiere ===")
    b = d[d["pct_bours"].notna() & (d["acc_tot"] > 0)]
    gb = b.groupby("fili").apply(
        lambda s: (s["pct_bours"] * s["acc_tot"]).sum() / s["acc_tot"].sum(),
        include_groups=False,
    ).sort_values()
    for fili, v in gb.items():
        print(f"   {str(fili):42.42} {v:5.1f}% d'admis boursiers")

    print("\n=== 3b. Croisement selectivite x boursiers (le test de l'epreuve deguisee) ===")
    b2 = b[b["fili"].isin(["CPGE", "Licence", "BTS", "BUT", "Ecole d'Ingénieur", "IFSI"])]
    for fili, s in b2.groupby("fili"):
        tiers = s["taux_acces_ens"].quantile([0.33, 0.66]).values
        sel = s[s["taux_acces_ens"] <= tiers[0]]
        ouv = s[s["taux_acces_ens"] >= tiers[1]]
        pb = lambda x: (x["pct_bours"] * x["acc_tot"]).sum() / x["acc_tot"].sum()
        print(f"   {str(fili):20.20} tiers le + selectif : {pb(sel):4.1f}% boursiers | "
              f"tiers le + ouvert : {pb(ouv):4.1f}%")


if __name__ == "__main__":
    main()
