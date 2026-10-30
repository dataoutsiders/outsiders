# -*- coding: utf-8 -*-
"""
Dossier « PISA 2025 : la France décroche-t-elle ? » (route /international/pisa).

Construit frontend/public/data/showcases/pisa.json : agrégats PAR PAYS seulement, tous tirés
des tableaux publiés par l'OCDE (valeurs plausibles, poids et erreurs types déjà traités par
l'OCDE ; aucune microdonnée). Le dossier porte sur la France seule : la comparaison se fait avec
la moyenne de l'OCDE et avec la moyenne « OCDE-23 » (les 23 pays de l'OCDE dont les résultats
sont comparables à chaque vague depuis 2000), jamais avec un pays en particulier.

Sources (classeurs Excel des annexes, en cache dans python/data/international/pisa/raw/) :
- OCDE, PISA 2025 Results (Volume I), 8 septembre 2026 :
    stat.link/mrq53f  tableaux I.B1.2a.* (scores 2025, tendances 2000-2025, faibles et très performants)
    stat.link/k68msa  tableaux I.B1.2b.* (statut socio-économique ESCS, 2025)
    stat.link/pe3lsg  tableau I.A2.1 (indice de couverture 3, 2003-2025)
- OCDE, PISA 2022 Results (Volume I) : stat.link/wh9d4z (tendances 2000-2022, pour les
  participants absents en 2025).
- Banque mondiale, API WDI : NY.GDP.PCAP.PP.KD (PIB par habitant en PPA, dollars constants 2021).

Choix issus des vérifications du 30 octobre 2026 (docs/international/pisa_2025_dossier.md) :
- Pas de complément manuel des participants sortis de PISA : les rangs historiques sont comptés
  parmi les participants présents dans les tableaux de tendance de l'OCDE, et le dit.
- Pas de comparaison de l'ESCS entre 2022 et 2025 : l'indice a changé de méthode en 2025
  (rapport national anglais du DfE, document de travail EsadeEcPol du 23 septembre 2026).
  Seules les mesures 2025 (une seule vague) sont publiées.
- Significativité : règle de l'OCDE (|différence / erreur type| > 1,96, erreurs types publiées,
  erreur de lien comprise pour les évolutions d'un même pays).

Usage :
    PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe python/tools/build_pisa.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import explore_pisa as E  # noqa: E402  (lecture des tableaux OCDE, listes de pays)

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "frontend" / "public" / "data" / "showcases" / "pisa.json"

DOMS = ["sci", "rea", "mat"]
LIB = {"sci": "Sciences", "rea": "Compréhension de l'écrit", "mat": "Mathématiques"}
FIRST = {"sci": 2006, "rea": 2000, "mat": 2003}
Z = 1.96

NOMS_FR = {
    "Albania": "Albanie", "Argentina": "Argentine", "Armenia": "Arménie", "Australia": "Australie",
    "Austria": "Autriche", "Azerbaijan": "Azerbaïdjan", "B-S-J-Z (China)": "Pékin-Shanghai-Jiangsu-Zhejiang (Chine)",
    "Belgium": "Belgique", "Brazil": "Brésil", "Brunei Darussalam": "Brunei", "Bulgaria": "Bulgarie",
    "Cambodia": "Cambodge", "Canada": "Canada", "Chile": "Chili", "Chinese Taipei": "Taipei chinois",
    "Colombia": "Colombie", "Costa Rica": "Costa Rica", "Croatia": "Croatie", "Cyprus": "Chypre",
    "Czechia": "Tchéquie", "Denmark": "Danemark", "Dominican Republic": "République dominicaine",
    "Dushanbe (Tajikistan)": "Douchanbé (Tadjikistan)", "Ecuador": "Équateur", "El Salvador": "Salvador",
    "Estonia": "Estonie", "Finland": "Finlande", "France": "France", "Georgia": "Géorgie",
    "Germany": "Allemagne", "Greece": "Grèce", "Guatemala": "Guatemala", "Hong Kong (China)": "Hong Kong (Chine)",
    "Hungary": "Hongrie", "Iceland": "Islande", "Indonesia": "Indonésie", "Ireland": "Irlande",
    "Israel": "Israël", "Italy": "Italie", "Japan": "Japon", "Jordan": "Jordanie", "Kazakhstan": "Kazakhstan",
    "Kenya": "Kenya", "Korea": "Corée", "Kosovo": "Kosovo", "Kurdistan Region (Iraq)": "Région du Kurdistan (Irak)",
    "Kyrgyzstan": "Kirghizistan", "Latvia": "Lettonie", "Lebanon": "Liban", "Lithuania": "Lituanie",
    "Luxembourg": "Luxembourg", "Macao (China)": "Macao (Chine)", "Malaysia": "Malaisie", "Malta": "Malte",
    "Mauritius": "Maurice", "Mexico": "Mexique", "Moldova": "Moldavie", "Mongolia": "Mongolie",
    "Montenegro": "Monténégro", "Morocco": "Maroc", "Netherlands": "Pays-Bas", "New Zealand": "Nouvelle-Zélande",
    "North Macedonia": "Macédoine du Nord", "Norway": "Norvège", "Palestinian Authority": "Autorité palestinienne",
    "Panama": "Panama", "Paraguay": "Paraguay", "Peru": "Pérou", "Philippines": "Philippines", "Poland": "Pologne",
    "Portugal": "Portugal", "Qatar": "Qatar", "Romania": "Roumanie", "Rwanda": "Rwanda",
    "Saudi Arabia": "Arabie saoudite", "Serbia": "Serbie", "Singapore": "Singapour",
    "Slovak Republic": "Slovaquie", "Slovenia": "Slovénie", "Spain": "Espagne", "Sweden": "Suède",
    "Switzerland": "Suisse", "Thailand": "Thaïlande", "Türkiye": "Türkiye", "Ukrainian regions": "Régions d'Ukraine",
    "United Arab Emirates": "Émirats arabes unis", "United Kingdom": "Royaume-Uni", "United States": "États-Unis",
    "Uruguay": "Uruguay", "Uzbekistan": "Ouzbékistan", "Viet Nam": "Viêt Nam", "Zambia": "Zambie",
}

SOURCES = {
    "vol1_perf": {"label": "OCDE, PISA 2025 Results (Volume I), annexe B1, tableaux I.B1.2a (8 septembre 2026)",
                  "url": "https://stat.link/mrq53f"},
    "vol1_escs": {"label": "OCDE, PISA 2025 Results (Volume I), annexe B1, tableaux I.B1.2b (statut socio-économique)",
                  "url": "https://stat.link/k68msa"},
    "vol1_couv": {"label": "OCDE, PISA 2025 Results (Volume I), annexe A2, tableau I.A2.1 (couverture)",
                  "url": "https://stat.link/pe3lsg"},
    "vol1_2022": {"label": "OCDE, PISA 2022 Results (Volume I), annexe B1, tableaux I.B1.5 (tendances 2000-2022)",
                  "url": "https://stat.link/wh9d4z"},
    "pib": {"label": "Banque mondiale, PIB par habitant en parité de pouvoir d'achat (NY.GDP.PCAP.PP.KD)",
            "url": "https://data.worldbank.org/indicator/NY.GDP.PCAP.PP.KD"},
    "escs_methode": {"label": "DfE, PISA 2025 National Report for England, section 6.3.1 (révision de l'indice ESCS)",
                     "url": "https://assets.publishing.service.gov.uk/media/6a9ea5415a0c25165ae469d9/pisa-2025-national-report-for-england.pdf"},
    "escs_esade": {"label": "EsadeEcPol et Innovamat, document de travail du 23 septembre 2026 sur l'ESCS 2022-2025",
                   "url": "https://www.esade.edu/ecpol/en/publications/explaining-the-learning-decline-in-pisa-2025-by-socioeconomic-quartiles-through-methodological-changes/"},
}


def r1(x):
    return None if x is None or (isinstance(x, float) and np.isnan(x)) else round(float(x), 1)


def r2(x):
    return None if x is None or (isinstance(x, float) and np.isnan(x)) else round(float(x), 2)


def sig(d, se):
    return bool(abs(d / se) > Z) if (d is not None and se) else None


def nxt(t: pd.DataFrame, col: str) -> str:
    """Colonne de l'erreur type qui suit une colonne de valeur dans un tableau OCDE."""
    return t.columns[list(t.columns).index(col) + 1]


def row(t, name):
    x = t[t["country"] == name]
    if len(x) != 1:
        raise KeyError(name)
    return x.iloc[0]


# ------------------------------------------------------------------------------------------
# Lecture des tableaux
# ------------------------------------------------------------------------------------------
TAB_2025 = {"sci": "Table I.B1.2a.1", "rea": "Table I.B1.2a.2", "mat": "Table I.B1.2a.3"}
TAB_TREND = {"sci": "Table I.B1.2a.36", "rea": "Table I.B1.2a.37", "mat": "Table I.B1.2a.38"}
TAB_TREND22 = {"sci": "Table I.B1.5.6", "rea": "Table I.B1.5.5", "mat": "Table I.B1.5.4"}
TAB_LOWTOP = {"sci": "Table I.B1.2a.33", "rea": "Table I.B1.2a.34", "mat": "Table I.B1.2a.35"}
TAB_ESCS = {"sci": "Table I.B1.2b.2", "rea": "Table I.B1.2b.3", "mat": "Table I.B1.2b.4"}


def scores_2025(d):
    t = E.read_table("mrq53f", TAB_2025[d])
    m = E.pick(t, "Mean score", "Mean")
    x = pd.DataFrame({"country": t["country"], "mean": t[m], "se": t[nxt(t, m)]}).dropna(subset=["mean"])
    return x


def trend_long(d):
    """Moyennes par vague (tableaux 2025, complétés par 2022 pour les participants absents en 2025)."""
    rows = []
    for code, sheet in (("mrq53f", TAB_TREND[d]), ("wh9d4z", TAB_TREND22[d])):
        t = E.read_table(code, sheet)
        for c in t.columns:
            mm = re.match(r".*\|PISA (\d{4})\|Mean score$", c)
            if mm:
                se_c = nxt(t, c)
                for _, r in t.iterrows():
                    rows.append({"country": r["country"], "year": int(mm.group(1)), "mean": r[c], "se": r[se_c],
                                 "src": code})
    x = pd.DataFrame(rows).dropna(subset=["mean"])
    x["prio"] = (x["src"] == "mrq53f").astype(int)
    x = x.sort_values("prio", ascending=False).drop_duplicates(["country", "year"])
    return x.drop(columns=["prio"])


def trend_changes(d):
    """Évolutions publiées par l'OCDE (erreur de lien comprise) : France et OCDE-23."""
    t = E.read_table("mrq53f", TAB_TREND[d])
    out = {}
    for c in t.columns:
        mm = re.match(r"Change in .*\|PISA (\d{4}).*\|Score dif\.$", c)
        if mm:
            y = int(mm.group(1))
            se_c = nxt(t, c)
            out[y] = {k: (float(row(t, n)[c]), float(row(t, n)[se_c]))
                      for k, n in (("fr", "France"), ("ocde23", "OECD average-23"))
                      if pd.notna(row(t, n)[c])}
    return out


def rank_range(df, focus="France"):
    """Rang ponctuel et fourchette (pays significativement au-dessus / en dessous, z = 1,96)."""
    m, e = df["mean"].to_numpy(), df["se"].to_numpy()
    i = list(df["country"]).index(focus)
    z = (m - m[i]) / np.sqrt(e ** 2 + e[i] ** 2)
    return {"rang": int((m > m[i]).sum()) + 1, "min": int((z > Z).sum()) + 1,
            "max": int(len(df) - (z < -Z).sum()), "n": int(len(df))}


# ------------------------------------------------------------------------------------------
def build():
    data = {"domaines": LIB, "sources": SOURCES}

    # Groupe stable : les 23 pays de l'OCDE présents et comparables à chaque vague depuis 2000.
    # On le reconstitue et on vérifie qu'il redonne la moyenne « OECD average-23 » publiée.
    tl = {d: trend_long(d) for d in DOMS}
    piv_rea = tl["rea"][~tl["rea"]["country"].str.startswith("OECD")].pivot_table(
        index="country", columns="year", values="mean")
    oecd23 = sorted(c for c in piv_rea.dropna().index if c in E.OECD)
    assert len(oecd23) == 23, oecd23
    for d in DOMS:
        x = tl[d]
        for y in sorted(x["year"].unique()):
            v = x[(x["year"] == y) & (x["country"].isin(oecd23))]["mean"]
            pub = x[(x["year"] == y) & (x["country"] == "OECD average-23")]["mean"]
            if len(pub):
                assert len(v) == 23 and abs(v.mean() - pub.iloc[0]) < 0.05, (d, y, len(v), v.mean(), pub.iloc[0])
    print(f"[OK] groupe OCDE-23 reconstitué et vérifié : {', '.join(oecd23)}")
    data["ocde23"] = [NOMS_FR[c] for c in oecd23]

    niveau, trajectoires, evolutions, rangs, decomposition = {}, {}, {}, {}, {}
    for d in DOMS:
        s = scores_2025(d)
        fr, oc = row(s, "France"), row(s, "OECD average")
        o23 = row(s, "OECD average-23") if (s["country"] == "OECD average-23").any() else None
        parts = s[~s["country"].str.startswith("OECD")].reset_index(drop=True)
        ocde = parts[parts["country"].isin(E.OECD)].reset_index(drop=True)
        stab = parts[parts["country"].isin(oecd23)].reset_index(drop=True)
        ec = fr["mean"] - oc["mean"]
        se_ec = float(np.hypot(fr["se"], oc["se"]))
        niveau[d] = {
            "fr": {"score": r1(fr["mean"]), "se": r2(fr["se"])},
            "ocde": {"score": r1(oc["mean"]), "se": r2(oc["se"])},
            "ecart_ocde": r1(ec), "se_ecart": r2(se_ec), "significatif": sig(ec, se_ec),
            "rang_tous": rank_range(parts), "rang_ocde": rank_range(ocde), "rang_ocde23": rank_range(stab),
        }
        if o23 is not None:
            niveau[d]["ocde23"] = {"score": r1(o23["mean"]), "se": r2(o23["se"])}

        # Trajectoires France / OCDE-23 / moyenne OCDE (quand publiée)
        x = tl[d]
        traj = []
        for y in sorted(x[x["country"] == "France"]["year"].unique()):
            g = lambda n: x[(x["year"] == y) & (x["country"] == n)]["mean"]  # noqa: E731
            traj.append({"annee": int(y), "fr": r1(g("France").iloc[0]),
                         "ocde23": r1(g("OECD average-23").iloc[0]) if len(g("OECD average-23")) else None})
        trajectoires[d] = traj

        # Évolutions (publiées) et écart d'évolution France - OCDE-23.
        # L'erreur de lien est commune aux deux évolutions et s'annule dans leur différence :
        # on combine les erreurs d'échantillonnage des deux vagues (France et OCDE-23).
        ch = trend_changes(d)
        ev = []
        for y0 in sorted(ch):
            if y0 not in (FIRST[d], 2015, 2018, 2022) or "fr" not in ch[y0]:
                continue
            (dfr, sefr), (doc, seoc) = ch[y0]["fr"], ch[y0]["ocde23"]
            se_samp = []
            for n in ("France", "OECD average-23"):
                for yy in (y0, 2025):
                    se_samp.append(float(x[(x["year"] == yy) & (x["country"] == n)]["se"].iloc[0]))
            se_diff = float(np.sqrt(sum(v ** 2 for v in se_samp)))
            ev.append({"depuis": y0,
                       "fr": {"d": r1(dfr), "se": r2(sefr), "sig": sig(dfr, sefr)},
                       "ocde23": {"d": r1(doc), "se": r2(seoc), "sig": sig(doc, seoc)},
                       "ecart": {"d": r1(dfr - doc), "se": r2(se_diff), "sig": sig(dfr - doc, se_diff)}})
        evolutions[d] = ev

        # Rangs dans le temps : tous les participants présents dans les tableaux de l'OCDE,
        # et groupe OCDE-23 ; décomposition rang = 1 + stables au-dessus + autres au-dessus.
        p = x[~x["country"].str.startswith("OECD")]
        present = {int(y): set(p[p["year"] == y]["country"]) for y in p["year"].unique()}

        def above_by_group(y, y0):
            """Pays au-dessus de la France en y : OCDE-23, autres déjà présents en y0, arrivés après y0."""
            col = p[p["year"] == y].set_index("country")["mean"]
            above = col[col > col["France"]].index
            st = sum(c in oecd23 for c in above)
            nv = sum(c not in oecd23 and c not in present[y0] for c in above)
            return {"rang": len(above) + 1, "n": int(len(col)), "stables": st,
                    "anciens": len(above) - st - nv, "nouveaux": nv}

        rr = []
        for y in sorted(present):
            if "France" not in present[y]:
                continue
            a = above_by_group(y, FIRST[d])
            rr.append({"annee": y, "rang_tous": a["rang"], "n_tous": a["n"], "rang_ocde23": a["stables"] + 1,
                       "au_dessus_stables": a["stables"], "au_dessus_anciens": a["anciens"],
                       "au_dessus_nouveaux": a["nouveaux"]})
        rangs[d] = rr
        decomposition[d] = {}
        for k, y0 in (("long", FIRST[d]), ("depuis2018", 2018)):
            a0, a1 = above_by_group(y0, y0), above_by_group(2025, y0)
            decomposition[d][k] = {
                "debut": y0, "rang_debut": a0["rang"], "n_debut": a0["n"], "rang_fin": a1["rang"], "n_fin": a1["n"],
                "places": a1["rang"] - a0["rang"],
                "dont_stables": a1["stables"] - a0["stables"],
                "dont_anciens": a1["anciens"] - a0["anciens"],
                "dont_nouveaux": a1["nouveaux"],
                "rang_ocde23_debut": a0["stables"] + 1, "rang_ocde23_fin": a1["stables"] + 1,
            }

    data.update(niveau=niveau, trajectoires=trajectoires, evolutions=evolutions, rangs=rangs,
                decomposition=decomposition)

    # ---------------------------------------------------------------- score attendu
    gdp = E.wb_indicator("NY.GDP.PCAP.PP.KD")
    escs = E.read_table("k68msa", "Table I.B1.2b.1")
    escs = pd.DataFrame({"country": escs["country"], "escs_mean": escs[E.pick(escs, "All students", "Mean index")]})
    attendu = {}
    for d in DOMS:
        s = scores_2025(d)
        s = s[~s["country"].str.startswith("OECD") & ~s["country"].isin(E.SUBNATIONAL)].copy()
        s["iso3"] = s["country"].map(E.ISO3)
        s = s.merge(gdp, on="iso3", how="left").merge(escs, on="country", how="left")
        s["log_gdp"] = np.log(s["NY.GDP.PCAP.PP.KD"])
        res, info = E.fit(s, "mean", ["log_gdp", "escs_mean"], "B")
        # progression 2018-2025 attendue (score de départ, PIB, ESCS)
        p18 = tl[d][tl[d]["year"] == 2018][["country", "mean"]].rename(columns={"mean": "m2018"})
        s2 = s.merge(p18, on="country", how="left")
        s2["d1825"] = s2["mean"] - s2["m2018"]
        res2, info2 = E.fit(s2, "d1825", ["m2018", "log_gdp", "escs_mean"], "P")
        f, f2 = row(res, "France"), row(res2, "France")
        sd = float(res["resid"].std(ddof=0))
        attendu[d] = {
            "n": info["n"], "r2": info["r2"],
            "points": [{"id": E.ISO3.get(r["country"], r["country"]), "nom": NOMS_FR.get(r["country"], r["country"]),
                        "attendu": r1(r["pred"]), "observe": r1(r["mean"]), "fr": r["country"] == "France"}
                       for _, r in res.sort_values("country").iterrows()],
            "france": {"observe": r1(f["mean"]), "attendu": r1(f["pred"]), "ecart": r1(f["resid"]),
                       "rang_ecart": int(f["resid_rank"]), "ecart_type_residus": r1(sd),
                       "resid_stud": r2(f["resid_stud"])},
            "progression_2018": {"n": info2["n"], "r2": info2["r2"], "observe": r1(f2["d1825"]),
                                 "attendu": r1(f2["pred"]), "ecart": r1(f2["resid"]),
                                 "rang_ecart": int(f2["resid_rank"]), "resid_stud": r2(f2["resid_stud"])},
        }
        miss = s[s["NY.GDP.PCAP.PP.KD"].isna() | s["escs_mean"].isna()]["country"].tolist()
        print(f"[INFO] attendu {d} : n={info['n']} R2={info['r2']} ; exclus faute de PIB ou d'ESCS : {miss}")
    data["attendu"] = attendu
    data["pib_annee"] = int(gdp["NY.GDP.PCAP.PP.KD_year"].mode().iloc[0])

    # ---------------------------------------------------------------- origine sociale (2025 seulement)
    social = {}
    for d in DOMS:
        t = E.read_table("k68msa", TAB_ESCS[d])
        cols = {"r2": E.pick(t, "Strength", "%"), "pente": E.pick(t, "Slope", "Score dif."),
                "q1": E.pick(t, "Bottom quarter", "Mean score"), "q4": E.pick(t, "Top quarter", "Mean score"),
                "ecart": E.pick(t, "Top - Bottom", "Score dif.")}
        fr, oc = row(t, "France"), row(t, "OECD average")
        ocde = t[t["country"].isin(E.OECD)]
        o = {}
        for k, c in cols.items():
            se_c = nxt(t, c)
            v = {"fr": r1(fr[c]), "se_fr": r2(fr[se_c]), "ocde": r1(oc[c]), "se_ocde": r2(oc[se_c])}
            diff = fr[c] - oc[c]
            v["sig"] = sig(diff, float(np.hypot(fr[se_c], oc[se_c])))
            if k in ("r2", "pente", "ecart"):
                vals = ocde[c].dropna()
                v["rang_ocde"] = int((vals > fr[c]).sum()) + 1
                v["n_ocde"] = int(len(vals))
            o[k] = v
        social[d] = o
    data["social"] = social

    # ---------------------------------------------------------------- faibles et très performants
    lowtop = {}
    for d in DOMS:
        t = E.read_table("mrq53f", TAB_LOWTOP[d])
        fr, o23, oc = row(t, "France"), row(t, "OECD average-23"), row(t, "OECD average")
        serie = []
        for c in t.columns:
            mm = re.match(r"Proficiency level in PISA (\d{4})\|Below Level 2[^|]*\|%$", c)
            if mm:
                y = int(mm.group(1))
                ctop = [k for k in t.columns if k.startswith(f"Proficiency level in PISA {y}|Level 5") and k.endswith("|%")][0]
                if pd.isna(fr[c]):
                    continue
                serie.append({"annee": y, "fr_faibles": r1(fr[c]), "ocde23_faibles": r1(o23[c]),
                              "fr_forts": r1(fr[ctop]), "ocde23_forts": r1(o23[ctop])})
        y0 = FIRST[d]
        chg = {}
        for lab, pat in (("faibles", "Below Level 2"), ("forts", "Level 5")):
            c = [k for k in t.columns if k.startswith(f"Change between {y0} and 2025") and pat in k and k.endswith("% dif.")][0]
            chg[lab] = {"fr": {"d": r1(fr[c]), "se": r2(fr[nxt(t, c)]), "sig": sig(fr[c], fr[nxt(t, c)])},
                        "ocde23": {"d": r1(o23[c]), "se": r2(o23[nxt(t, c)]), "sig": sig(o23[c], o23[nxt(t, c)])}}
        c25 = {lab: [k for k in t.columns if k.startswith("Proficiency level in PISA 2025") and pat in k and k.endswith("|%")][0]
               for lab, pat in (("faibles", "Below Level 2"), ("forts", "Level 5"))}
        vs = {}
        for lab, c in c25.items():
            diff = fr[c] - oc[c]
            vs[lab] = {"fr": r1(fr[c]), "ocde": r1(oc[c]),
                       "sig": sig(diff, float(np.hypot(fr[nxt(t, c)], oc[nxt(t, c)])))}
        lowtop[d] = {"serie": serie, "depuis": y0, "evolution": chg, "vs_ocde_2025": vs}
    data["faibles_forts"] = lowtop

    # ---------------------------------------------------------------- couverture
    t = E.read_table("pe3lsg", "Table I.A2.1")
    ci = {}
    for c in t.columns:
        mm = re.match(r"PISA (\d{4})\|.*Coverage Index 3", c)
        if mm:
            ci[int(mm.group(1))] = t.set_index("country")[c]
    c25 = ci[2025].dropna().clip(upper=1.0)
    c25 = c25[~c25.index.str.startswith("OECD")]
    oc25 = c25[c25.index.isin(E.OECD)]
    data["couverture"] = {
        "france": [{"annee": y, "ci3": r2(ci[y].get("France"))} for y in sorted(ci) if pd.notna(ci[y].get("France"))],
        "y2025": {"france": r2(c25["France"]), "n": int(len(c25)), "mediane": r2(c25.median()),
                  "min": r2(c25.min()), "max": r2(c25.max()),
                  "n_sous_075": int((c25 < 0.75).sum()), "n_sous_050": int((c25 < 0.5).sum()),
                  "ocde_mediane": r2(oc25.median()), "ocde_min": r2(oc25.min()), "ocde_n": int(len(oc25))},
    }
    # Hypothèse transparente « à couverture égale » pour la France seulement (P10 et P25 du pays)
    cls = pd.read_csv(ROOT / "python" / "data" / "international" / "pisa" / "classement_couverture.csv")
    hyp = {}
    for d in DOMS:
        f = cls[(cls["country"] == "France") & (cls["domain"] == d)].iloc[0]
        hyp[d] = {"brut": int(f["rank_raw"]), "p25": int(f["rank_mean_all15_p25"]), "p10": int(f["rank_mean_all15_p10"]),
                  "n": int(f["n"])}
    data["couverture"]["rangs_hypothese"] = hyp
    return data


def main():
    data = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"[OK] {OUT.relative_to(ROOT)} ({OUT.stat().st_size // 1024} Ko)")
    # Résumé des chiffres affichés, pour relecture
    for d in DOMS:
        n = data["niveau"][d]
        print(f"\n== {LIB[d]} ==")
        print("  2025 France", n["fr"], "OCDE", n["ocde"], "écart", n["ecart_ocde"], "se", n["se_ecart"], "sig", n["significatif"])
        print("  rangs", n["rang_tous"], n["rang_ocde"], n["rang_ocde23"])
        for e in data["evolutions"][d]:
            print("  évolution depuis", e["depuis"], e["fr"], e["ocde23"], e["ecart"])
        print("  décomposition", data["decomposition"][d])
        print("  attendu", data["attendu"][d]["france"], data["attendu"][d]["progression_2018"])
        print("  social", {k: (v["fr"], v["ocde"], v.get("sig"), v.get("rang_ocde"), v.get("n_ocde")) for k, v in data["social"][d].items()})
        ft = data["faibles_forts"][d]
        print("  faibles/forts", ft["evolution"], ft["vs_ocde_2025"])
    print("\n  couverture", data["couverture"])


if __name__ == "__main__":
    sys.exit(main())
