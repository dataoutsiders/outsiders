# -*- coding: utf-8 -*-
"""
Exploration PISA 2025 : la France à contexte égal (rien n'est publié).

Sources (toutes publiques) :
- OCDE, PISA 2025 Results (Volume I), annexes Excel publiées le 8 septembre 2026 :
    stat.link/mrq53f  (tableaux I.B1.2a.* : scores, percentiles, tendances, faibles/forts)
    stat.link/k68msa  (tableaux I.B1.2b.* : statut socio-économique ESCS)
    stat.link/pe3lsg  (tableau I.A2.1 : indice de couverture 3, 2003-2025)
- OCDE, PISA 2022 Results (Volume I), annexe stat.link/wh9d4z (tendances 2000-2022,
  pour les pays absents en 2025).
- Banque mondiale, API WDI : PIB par habitant en PPA (NY.GDP.PCAP.PP.KD),
  dépense publique par élève du secondaire en % du PIB par habitant (SE.XPD.SECO.PC.ZS).

Tous les chiffres PISA viennent des tableaux publiés par l'OCDE (valeurs plausibles,
poids et erreurs types déjà traités par l'OCDE). Aucune microdonnée n'est utilisée.

Usage :
    PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe python/tools/explore_pisa.py
Sorties : python/data/international/pisa/*.csv (+ raw/*.xlsx en cache).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import requests
import openpyxl
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "python" / "data" / "international" / "pisa"
RAW = OUT / "raw"
OUT.mkdir(parents=True, exist_ok=True)
RAW.mkdir(parents=True, exist_ok=True)

STATLINKS = {
    "mrq53f": "PISA 2025 Vol. I, tableaux I.B1.2a (performance)",
    "k68msa": "PISA 2025 Vol. I, tableaux I.B1.2b (statut socio-économique)",
    "pe3lsg": "PISA 2025 Vol. I, annexe A2 (couverture)",
    "wh9d4z": "PISA 2022 Vol. I, tableaux I.B1.5 (tendances 2000-2022)",
}

DOMAINS = {"sci": "sciences", "rea": "lecture", "mat": "mathématiques"}

# 38 membres de l'OCDE en 2025 (noms tels qu'écrits dans les tableaux, après nettoyage)
OECD = {
    "Australia", "Austria", "Belgium", "Canada", "Chile", "Colombia", "Costa Rica",
    "Czechia", "Denmark", "Estonia", "Finland", "France", "Germany", "Greece", "Hungary",
    "Iceland", "Ireland", "Israel", "Italy", "Japan", "Korea", "Latvia", "Lithuania",
    "Luxembourg", "Mexico", "Netherlands", "New Zealand", "Norway", "Poland", "Portugal",
    "Slovak Republic", "Slovenia", "Spain", "Sweden", "Switzerland", "Türkiye",
    "United Kingdom", "United States",
}

# Entités infranationales ou partielles : exclues du modèle « score attendu »
SUBNATIONAL = {
    "B-S-J-Z (China)", "B-S-J-G (China)", "Dushanbe (Tajikistan)", "Kurdistan Region (Iraq)",
    "Ukrainian regions", "Baku (Azerbaijan)", "Hong Kong (China)", "Macao (China)",
    "Chinese Taipei", "Palestinian Authority", "Shanghai-China",
}

ALIASES = {
    "Czech Republic": "Czechia", "Turkey": "Türkiye", "Turkiye": "Türkiye",
    "Ukrainian regions (18 of 27)": "Ukrainian regions",
    "Ukrainian regions (17 of 27)": "Ukrainian regions",
    "Republic of North Macedonia": "North Macedonia", "Moldova, Republic of": "Moldova",
}

ISO3 = {
    "Albania": "ALB", "Argentina": "ARG", "Armenia": "ARM", "Australia": "AUS", "Austria": "AUT",
    "Azerbaijan": "AZE", "Belgium": "BEL", "Brazil": "BRA", "Brunei Darussalam": "BRN",
    "Bulgaria": "BGR", "Cambodia": "KHM", "Canada": "CAN", "Chile": "CHL", "Colombia": "COL",
    "Costa Rica": "CRI", "Croatia": "HRV", "Cyprus": "CYP", "Czechia": "CZE", "Denmark": "DNK",
    "Dominican Republic": "DOM", "Ecuador": "ECU", "El Salvador": "SLV", "Estonia": "EST",
    "Finland": "FIN", "France": "FRA", "Georgia": "GEO", "Germany": "DEU", "Greece": "GRC",
    "Guatemala": "GTM", "Hungary": "HUN", "Iceland": "ISL", "Indonesia": "IDN", "Ireland": "IRL",
    "Israel": "ISR", "Italy": "ITA", "Japan": "JPN", "Jordan": "JOR", "Kazakhstan": "KAZ",
    "Kenya": "KEN", "Korea": "KOR", "Kosovo": "XKX", "Kyrgyzstan": "KGZ", "Latvia": "LVA",
    "Lebanon": "LBN", "Lithuania": "LTU", "Luxembourg": "LUX", "Malaysia": "MYS", "Malta": "MLT",
    "Mauritius": "MUS", "Mexico": "MEX", "Moldova": "MDA", "Mongolia": "MNG", "Montenegro": "MNE",
    "Morocco": "MAR", "Netherlands": "NLD", "New Zealand": "NZL", "North Macedonia": "MKD",
    "Norway": "NOR", "Panama": "PAN", "Paraguay": "PRY", "Peru": "PER", "Philippines": "PHL",
    "Poland": "POL", "Portugal": "PRT", "Qatar": "QAT", "Romania": "ROU", "Rwanda": "RWA",
    "Saudi Arabia": "SAU", "Serbia": "SRB", "Singapore": "SGP", "Slovak Republic": "SVK",
    "Slovenia": "SVN", "Spain": "ESP", "Sweden": "SWE", "Switzerland": "CHE", "Thailand": "THA",
    "Türkiye": "TUR", "United Arab Emirates": "ARE", "United Kingdom": "GBR",
    "United States": "USA", "Uruguay": "URY", "Uzbekistan": "UZB", "Viet Nam": "VNM",
    "Zambia": "ZMB", "Uzbekistan ": "UZB",
}


# --------------------------------------------------------------------------------------
# Téléchargement et lecture des tableaux OCDE
# --------------------------------------------------------------------------------------
def fetch_statlink(code: str) -> Path:
    path = RAW / f"{code}.xlsx"
    if not path.exists():
        r = requests.get(f"https://stat.link/{code}", timeout=120)
        r.raise_for_status()
        if r.content[:2] != b"PK":
            raise RuntimeError(f"{code} : réponse non Excel")
        path.write_bytes(r.content)
        print(f"[INFO] téléchargé {code} -> {path.name} ({len(r.content)} octets)")
    return path


_WB: dict[str, openpyxl.Workbook] = {}


def clean_name(x) -> str:
    s = str(x).replace(" ", " ").strip()
    s = re.sub(r"[\*†‡]+$", "", s).strip()
    s = re.sub(r"\s*\d+$", "", s).strip() if not s.startswith("OECD average") else s
    s = ALIASES.get(s, s)
    if s.startswith("Ukrainian regions"):
        s = "Ukrainian regions"
    return s


def read_table(code: str, sheet: str) -> pd.DataFrame:
    """Lit un tableau OCDE : en-têtes multi-lignes aplatis 'niveau1|niveau2|niveau3'."""
    if code not in _WB:
        _WB[code] = openpyxl.load_workbook(fetch_statlink(code), read_only=True, data_only=True)
    rows = list(_WB[code][sheet].iter_rows(values_only=True))
    # première ligne de données : libellé en colonne A et au moins une valeur numérique
    first = None
    for i, r in enumerate(rows):
        if i > 4 and r and r[0] is not None and any(isinstance(v, (int, float)) for v in r[1:]):
            first = i
            break
    header_rows = rows[5:first]
    ncol = max(len(r) for r in rows[: first + 5])
    levels = []
    for hr in header_rows:
        hr = list(hr) + [None] * (ncol - len(hr))
        filled, last = [], None
        for v in hr:
            if v is not None and str(v).strip():
                last = re.sub(r"\s+", " ", str(v)).strip()
            filled.append(last)
        levels.append(filled)
    # le dernier niveau (Mean/S.E.) n'est pas propagé : on le relit brut
    last_raw = list(header_rows[-1]) + [None] * (ncol - len(header_rows[-1]))
    cols = ["country"]
    for j in range(1, ncol):
        parts = [lv[j] for lv in levels[:-1] if lv[j]]
        parts.append(str(last_raw[j]).strip() if last_raw[j] is not None else "")
        name = "|".join(parts)
        if name in cols or not parts[-1]:
            name = f"{name}#{j}"  # colonnes vides ou doublons
        cols.append(name)
    data = []
    for r in rows[first:]:
        if r[0] is None:
            continue
        name = str(r[0])
        if name.startswith(("Note", "Information", "1.", "2.", "3.", "*", "Source")) or len(name) > 60:
            continue
        vals = list(r) + [None] * (ncol - len(r))
        if not any(isinstance(v, (int, float)) for v in vals[1:]):
            continue  # lignes de section (« OECD », « Partners »)
        data.append(vals[:ncol])
    df = pd.DataFrame(data, columns=cols)
    df["flag_std"] = df["country"].astype(str).str.contains(r"\*")
    df["country"] = df["country"].map(clean_name)
    for c in df.columns[1:]:
        if c == "flag_std":
            continue
        df[c] = pd.to_numeric(df[c], errors="coerce")  # m, c, w -> NaN
    return df


def pick(df: pd.DataFrame, *patterns: str) -> str:
    """Retourne la première colonne dont le nom contient tous les motifs."""
    for c in df.columns:
        if all(p.lower() in c.lower() for p in patterns):
            return c
    raise KeyError(f"colonne introuvable : {patterns}")


# --------------------------------------------------------------------------------------
# 1. Scores 2025 et couverture
# --------------------------------------------------------------------------------------
def build_scores_2025() -> pd.DataFrame:
    sheets = {"sci": "Table I.B1.2a.1", "rea": "Table I.B1.2a.2", "mat": "Table I.B1.2a.3"}
    out = []
    for d, sh in sheets.items():
        t = read_table("mrq53f", sh)
        o = pd.DataFrame({
            "country": t["country"], "domain": d, "flag_std": t["flag_std"],
            "mean": t[pick(t, "Mean score", "Mean")], "se": t[pick(t, "Mean score", "S.E.")],
            "sd": t[pick(t, "Standard deviation", "S.D.")],
            "p10": t[pick(t, "10th", "Score")], "p25": t[pick(t, "25th", "Score")],
            "p50": t[pick(t, "Median", "Score")], "p75": t[pick(t, "75th", "Score")],
            "p90": t[pick(t, "90th", "Score")],
        })
        out.append(o)
    s = pd.concat(out)
    s = s[~s["country"].str.startswith("OECD")].dropna(subset=["mean"])
    cov = build_coverage()
    s = s.merge(cov[cov["year"] == 2025][["country", "ci3"]], on="country", how="left")
    s["oecd"] = s["country"].isin(OECD)
    s.to_csv(OUT / "scores_2025.csv", index=False, float_format="%.2f")
    return s


def build_coverage() -> pd.DataFrame:
    t = read_table("pe3lsg", "Table I.A2.1")
    rows = []
    for c in t.columns:
        m = re.match(r"PISA (\d{4})\|.*Coverage Index 3", c)
        if m:
            for _, r in t.iterrows():
                rows.append({"country": r["country"], "year": int(m.group(1)), "ci3": r[c]})
    cov = pd.DataFrame(rows).dropna()
    cov.to_csv(OUT / "couverture_ci3.csv", index=False, float_format="%.3f")
    return cov


# --------------------------------------------------------------------------------------
# 2. Classement brut et à couverture égale
# --------------------------------------------------------------------------------------
def rank_ranges(df: pd.DataFrame, col="mean", se="se") -> pd.DataFrame:
    """Rang ponctuel + fourchette (pays significativement au-dessus / en dessous, z=1,96)."""
    df = df.copy()
    df["rank"] = df[col].rank(ascending=False, method="min").astype(int)
    best, worst = [], []
    m, e = df[col].to_numpy(), df[se].to_numpy()
    for i in range(len(df)):
        z = (m - m[i]) / np.sqrt(e ** 2 + e[i] ** 2)
        best.append(int((z > 1.96).sum()) + 1)
        worst.append(len(df) - int((z < -1.96).sum()))
    df["rank_best"], df["rank_worst"] = best, worst
    return df


def build_coverage_ranking(s: pd.DataFrame) -> pd.DataFrame:
    # Bornes OCDE : médiane de tous les 15 ans (les non-couverts supposés sous la médiane)
    med_sheets = {"sci": "Table I.B1.2a.48", "rea": "Table I.B1.2a.49", "mat": "Table I.B1.2a.50"}
    low_sheets = {"sci": "Table I.B1.2a.45", "rea": "Table I.B1.2a.46", "mat": "Table I.B1.2a.47"}
    meds, lows = [], []
    for d in DOMAINS:
        t = read_table("mrq53f", med_sheets[d])
        meds.append(pd.DataFrame({"country": t["country"], "domain": d,
                                  "median_all15_lb": t[pick(t, "PISA 2025", "Median", "Score")]}))
        t = read_table("mrq53f", low_sheets[d])
        cols = [c for c in t.columns if c.startswith("Proficiency levels in PISA 2025")]
        low = [c for c in cols if "Not in secondary" in c and c.endswith("|%")][0]
        top = [c for c in cols if "Level 5" in c and c.endswith("|%")][0]
        lows.append(pd.DataFrame({"country": t["country"], "domain": d,
                                  "low_all15_ub": t[low], "top_all15_lb": t[top]}))
    s = s.merge(pd.concat(meds), on=["country", "domain"], how="left")
    s = s.merge(pd.concat(lows), on=["country", "domain"], how="left")
    c = s["ci3"].clip(upper=1.0)
    # Hypothèse transparente : les non-couverts auraient le score du 10e (ou 25e) centile du pays
    s["mean_all15_p10"] = c * s["mean"] + (1 - c) * s["p10"]
    s["mean_all15_p25"] = c * s["mean"] + (1 - c) * s["p25"]
    res = []
    for d in DOMAINS:
        x = s[s["domain"] == d].copy()
        x = rank_ranges(x)
        x = x.rename(columns={"rank": "rank_raw"})
        x["n"] = len(x)
        for k in ["mean_all15_p10", "mean_all15_p25", "median_all15_lb"]:
            ok = x[k].notna()
            x.loc[ok, "rank_" + k] = x.loc[ok, k].rank(ascending=False, method="min")
        x["n_with_ci3"] = x["ci3"].notna().sum()
        x["rank_oecd_raw"] = x["mean"].where(x["oecd"]).rank(ascending=False, method="min")
        x["rank_oecd_p10"] = x["mean_all15_p10"].where(x["oecd"]).rank(ascending=False, method="min")
        x["rank_oecd_p25"] = x["mean_all15_p25"].where(x["oecd"]).rank(ascending=False, method="min")
        x["rank_oecd_medlb"] = x["median_all15_lb"].where(x["oecd"]).rank(ascending=False, method="min")
        res.append(x)
    r = pd.concat(res)
    r.to_csv(OUT / "classement_couverture.csv", index=False, float_format="%.2f")
    return r


# --------------------------------------------------------------------------------------
# 3. Rang de la France : tous participants contre groupe stable
# --------------------------------------------------------------------------------------
def build_trends() -> pd.DataFrame:
    t25 = {"sci": "Table I.B1.2a.36", "rea": "Table I.B1.2a.37", "mat": "Table I.B1.2a.38"}
    t22 = {"sci": "Table I.B1.5.6", "rea": "Table I.B1.5.5", "mat": "Table I.B1.5.4"}
    rows = []
    for src, tabs in (("2025", t25), ("2022", t22)):
        code = "mrq53f" if src == "2025" else "wh9d4z"
        for d, sh in tabs.items():
            t = read_table(code, sh)
            for c in t.columns:
                m = re.match(r".*\|PISA (\d{4})\|Mean score$", c)
                if m:
                    se_c = t.columns[list(t.columns).index(c) + 1]
                    for _, r in t.iterrows():
                        rows.append({"country": r["country"], "domain": d, "year": int(m.group(1)),
                                     "mean": r[c], "se": r[se_c], "source": src})
    tr = pd.DataFrame(rows).dropna(subset=["mean"])
    # priorité aux tableaux 2025 (révisés), complétés par ceux de 2022 pour les pays sortis
    tr = tr.sort_values("source", ascending=False).drop_duplicates(["country", "domain", "year"])
    tr = tr.sort_values(["domain", "country", "year"])
    tr.to_csv(OUT / "tendances_scores.csv", index=False, float_format="%.2f")
    return tr


OFFICIAL_N = {2003: 41, 2006: 57, 2009: 65, 2012: 65, 2015: 72, 2018: 79, 2022: 81, 2025: 91}

# Participants passés absents des tableaux de tendance 2022 et 2025 (sortis de PISA ou
# résultats jugés non comparables) et dont le score dépassait celui de la France.
# Valeurs des rapports OCDE de chaque vague, saisies à la main : À VÉRIFIER avant publication.
SUPPLEMENT_ABOVE_FRANCE = {
    # (domaine, année) : [entités au-dessus de la France]
    ("rea", 2003): ["Liechtenstein"], ("mat", 2003): ["Liechtenstein"],
    ("rea", 2006): ["Liechtenstein"], ("mat", 2006): ["Liechtenstein"], ("sci", 2006): ["Liechtenstein"],
    ("rea", 2009): ["Shanghai-China", "Liechtenstein"], ("mat", 2009): ["Shanghai-China", "Liechtenstein"],
    ("sci", 2009): ["Shanghai-China", "Liechtenstein"],
    ("rea", 2012): ["Shanghai-China", "Liechtenstein", "Viet Nam"],
    ("mat", 2012): ["Shanghai-China", "Liechtenstein", "Viet Nam"],
    ("sci", 2012): ["Shanghai-China", "Liechtenstein", "Viet Nam"],
    ("mat", 2015): ["B-S-J-G (China)", "Viet Nam", "Russia"],
    ("sci", 2015): ["B-S-J-G (China)", "Viet Nam"],
}


def build_rank_history(tr: pd.DataFrame) -> pd.DataFrame:
    out = []
    for d in DOMAINS:
        x = tr[(tr["domain"] == d) & (~tr["country"].str.startswith("OECD"))]
        years = sorted(x["year"].unique())
        start = years[0]
        piv = x.pivot_table(index="country", columns="year", values="mean")
        stable = piv.dropna().index  # présents et comparables à chaque vague depuis la première
        stable_oecd = [c for c in stable if c in OECD]
        for y in years:
            col = piv[y].dropna()
            if "France" not in col:
                continue
            fr = col["France"]
            above = col[col > fr]
            out.append({
                "domain": d, "year": y, "france": round(fr, 1),
                "n_all": len(col), "rank_all": len(above) + 1,
                "n_stable": len(stable), "rank_stable": int((col[stable] > fr).sum()) + 1,
                "above_stable": int((col[stable] > fr).sum()),
                "above_other": int(len(above) - (col[stable] > fr).sum()),
                "n_oecd": int(col.index.isin(OECD).sum()),
                "rank_oecd": int((col[col.index.isin(OECD)] > fr).sum()) + 1,
                "n_stable_oecd": len(stable_oecd),
                "rank_stable_oecd": int((col[stable_oecd] > fr).sum()) + 1,
                "first_year": start,
                "n_official": OFFICIAL_N.get(y),
                "rank_all_complete": len(above) + 1 + len(SUPPLEMENT_ABOVE_FRANCE.get((d, y), [])),
            })
        pd.Series(sorted(stable)).to_csv(OUT / f"groupe_stable_{d}.csv", index=False, header=["country"])
    h = pd.DataFrame(out)
    h.to_csv(OUT / "rang_france_historique.csv", index=False)
    return h


# --------------------------------------------------------------------------------------
# 4. Score attendu (niveau et progression)
# --------------------------------------------------------------------------------------
def wb_indicator(code: str, years="2015:2024") -> pd.DataFrame:
    cache = RAW / f"wb_{code}.json"
    if not cache.exists():
        url = f"https://api.worldbank.org/v2/country/all/indicator/{code}?format=json&date={years}&per_page=20000"
        r = requests.get(url, timeout=120)
        r.raise_for_status()
        cache.write_text(r.text, encoding="utf-8")
    js = json.loads(cache.read_text(encoding="utf-8"))[1]
    df = pd.DataFrame([{"iso3": e["countryiso3code"], "year": int(e["date"]), "value": e["value"]}
                       for e in js if e["value"] is not None])
    # dernière valeur disponible
    df = df.sort_values("year").groupby("iso3").tail(1)
    return df.rename(columns={"value": code, "year": code + "_year"})


def build_escs_table() -> pd.DataFrame:
    t = read_table("k68msa", "Table I.B1.2b.1")
    e = pd.DataFrame({"country": t["country"], "escs_mean": t[pick(t, "All students", "Mean index")],
                      "escs_sd": t[pick(t, "Variability", "S.D.")]})
    grad = []
    for d, sh in {"sci": "Table I.B1.2b.2", "rea": "Table I.B1.2b.3", "mat": "Table I.B1.2b.4"}.items():
        g = read_table("k68msa", sh)
        grad.append(pd.DataFrame({
            "country": g["country"], "domain": d,
            "r2_escs": g[pick(g, "Strength", "%")], "slope_escs": g[pick(g, "Slope", "Score dif.")],
            "q1": g[pick(g, "Bottom quarter", "Mean score")], "q4": g[pick(g, "Top quarter", "Mean score")],
            "gap_q4_q1": g[pick(g, "Top - Bottom", "Score dif.")],
            "resilient_pct": g[pick(g, "resilient", "%")],
        }))
    gr = pd.concat(grad).merge(e, on="country", how="left")
    gr.to_csv(OUT / "escs_2025.csv", index=False, float_format="%.3f")
    return gr


def fit(df: pd.DataFrame, y: str, xs: list[str], label: str) -> tuple[pd.DataFrame, dict]:
    d = df.dropna(subset=[y] + xs).copy()
    X = sm.add_constant(d[xs])
    m = sm.OLS(d[y], X).fit(cov_type="HC1")
    d["pred"] = m.predict(X)
    d["resid"] = d[y] - d["pred"]
    infl = m.get_influence()
    d["resid_stud"] = infl.resid_studentized_external
    d["resid_rank"] = d["resid"].rank(ascending=False, method="min").astype(int)
    d["model"] = label
    info = {"model": label, "n": int(m.nobs), "r2": round(m.rsquared, 3),
            "coefs": {k: round(v, 2) for k, v in m.params.items()},
            "pvalues": {k: round(v, 4) for k, v in m.pvalues.items()}}
    return d, info


def build_expected(s: pd.DataFrame, escs: pd.DataFrame, tr: pd.DataFrame):
    gdp = wb_indicator("NY.GDP.PCAP.PP.KD")
    spend = wb_indicator("SE.XPD.SECO.PC.ZS")
    base = s[~s["country"].isin(SUBNATIONAL)].copy()
    base["iso3"] = base["country"].map(ISO3)
    base = base.merge(gdp, on="iso3", how="left").merge(spend, on="iso3", how="left")
    base = base.merge(escs[["country", "domain", "escs_mean"]], on=["country", "domain"], how="left")
    c = base["ci3"].clip(upper=1.0)
    base["mean_all15_p10"] = c * base["mean"] + (1 - c) * base["p10"]
    base["mean_all15_p25"] = c * base["mean"] + (1 - c) * base["p25"]
    base["log_gdp"] = np.log(base["NY.GDP.PCAP.PP.KD"])
    base["spend_ppp"] = base["SE.XPD.SECO.PC.ZS"] / 100 * base["NY.GDP.PCAP.PP.KD"]
    base["log_spend"] = np.log(base["spend_ppp"])
    # progression 2022-2025 et 2018-2025
    p = tr.pivot_table(index=["country", "domain"], columns="year", values="mean").reset_index()
    p.columns = [str(c) for c in p.columns]
    base = base.merge(p[["country", "domain", "2018", "2022"]], on=["country", "domain"], how="left")
    base["d_2022_2025"] = base["mean"] - base["2022"]
    base["d_2018_2025"] = base["mean"] - base["2018"]
    specs = [
        ("niveau_A_pib", "mean", ["log_gdp"]),
        ("niveau_B_pib_escs", "mean", ["log_gdp", "escs_mean"]),
        ("niveau_C_pib_escs_couv", "mean", ["log_gdp", "escs_mean", "ci3"]),
        ("niveau_D_pib_escs_depense", "mean", ["log_gdp", "escs_mean", "log_spend"]),
        ("niveau_E_couv_corrigee_p25", "mean_all15_p25", ["log_gdp", "escs_mean"]),
        ("niveau_F_couv_corrigee_p10", "mean_all15_p10", ["log_gdp", "escs_mean"]),
        ("progres_2022_2025", "d_2022_2025", ["2022", "log_gdp", "escs_mean"]),
        ("progres_2018_2025", "d_2018_2025", ["2018", "log_gdp", "escs_mean"]),
    ]
    allres, infos = [], []
    for d in DOMAINS:
        x = base[base["domain"] == d]
        for label, y, xs in specs:
            r, info = fit(x, y, xs, label)
            info["domain"] = d
            for c in ["France", "Türkiye"]:
                rr = r[r["country"] == c]
                if len(rr):
                    info[c] = {"obs": round(float(rr[y].iloc[0]), 1),
                               "attendu": round(float(rr["pred"].iloc[0]), 1),
                               "ecart": round(float(rr["resid"].iloc[0]), 1),
                               "rang_ecart": f"{int(rr['resid_rank'].iloc[0])}/{len(r)}"}
            infos.append(info)
            allres.append(r[["country", "domain", "model", y, "pred", "resid", "resid_stud",
                             "resid_rank"]].rename(columns={y: "observe"}))
    pd.concat(allres).to_csv(OUT / "score_attendu_residus.csv", index=False, float_format="%.2f")
    base.to_csv(OUT / "score_attendu_base.csv", index=False, float_format="%.3f")
    (OUT / "score_attendu_modeles.json").write_text(json.dumps(infos, ensure_ascii=False, indent=1),
                                                    encoding="utf-8")
    return infos, base


# --------------------------------------------------------------------------------------
# 5. Ce que les données confirment : origine sociale, faibles et forts
# --------------------------------------------------------------------------------------
FOCUS = ["France", "Türkiye", "Germany", "Spain", "Italy", "United Kingdom", "Belgium",
         "Netherlands", "Portugal", "Poland", "Finland", "Estonia", "Japan", "Canada",
         "Switzerland", "Sweden", "OECD average", "OECD average-23", "OECD average-35"]


def build_confirm():
    # R2 ESCS 2015-2025
    r2 = []
    for d, sh in {"sci": "Table I.B1.2b.25", "rea": "Table I.B1.2b.26", "mat": "Table I.B1.2b.27"}.items():
        t = read_table("k68msa", sh)
        for y in (2015, 2018, 2022, 2025):
            c = [c for c in t.columns if c.startswith("Percentage of variance") and f"PISA {y}|%" in c][0]
            r2 += [{"country": a, "domain": d, "year": y, "r2": b} for a, b in zip(t["country"], t[c])]
    r2 = pd.DataFrame(r2)
    r2.to_csv(OUT / "escs_r2_tendance.csv", index=False, float_format="%.2f")
    # écart quart favorisé - quart défavorisé et scores par quart, 2015-2025
    q = []
    for d, sh in {"sci": "Table I.B1.2b.22", "rea": "Table I.B1.2b.23", "mat": "Table I.B1.2b.24"}.items():
        t = read_table("k68msa", sh)
        for y in (2015, 2018, 2022, 2025):
            for lab, pat in (("q1", "Bottom quarter of ESCS"), ("q4", "Top quarter of ESCS"),
                             ("gap", "Top - Bottom quarter")):
                cs = [c for c in t.columns if c.startswith(f"PISA {y}|{pat}")]
                c = cs[0]
                q += [{"country": a, "domain": d, "year": y, "var": lab, "value": b}
                      for a, b in zip(t["country"], t[c])]
    q = pd.DataFrame(q).pivot_table(index=["country", "domain", "year"], columns="var",
                                    values="value").reset_index()
    q.to_csv(OUT / "escs_quarts_tendance.csv", index=False, float_format="%.2f")
    # faibles et forts 2000-2025
    lt = []
    for d, sh in {"sci": "Table I.B1.2a.33", "rea": "Table I.B1.2a.34", "mat": "Table I.B1.2a.35"}.items():
        t = read_table("mrq53f", sh)
        for c in t.columns:
            m = re.match(r"Proficiency level in PISA (\d{4})\|(Below Level 2|Level 5 or above)[^|]*\|%$", c)
            if m:
                lab = "low" if m.group(2).startswith("Below") else "top"
                lt += [{"country": a, "domain": d, "year": int(m.group(1)), "var": lab, "pct": b}
                       for a, b in zip(t["country"], t[c])]
    lt = pd.DataFrame(lt).pivot_table(index=["country", "domain", "year"], columns="var",
                                      values="pct").reset_index()
    lt.to_csv(OUT / "faibles_forts_tendance.csv", index=False, float_format="%.2f")
    # dispersion (écart type, P90-P10) dans le temps
    disp = []
    for d, sh in {"sci": "Table I.B1.2a.42", "rea": "Table I.B1.2a.43", "mat": "Table I.B1.2a.44"}.items():
        t = read_table("mrq53f", sh)
        for c in t.columns:
            m = re.match(r"PISA (\d{4})\|Standard deviation\|S\.D\.$", c)
            if m:
                disp += [{"country": a, "domain": d, "year": int(m.group(1)), "sd": b}
                         for a, b in zip(t["country"], t[c])]
    pd.DataFrame(disp).to_csv(OUT / "dispersion_tendance.csv", index=False, float_format="%.2f")
    pct = []
    for d, sh in {"sci": "Table I.B1.2a.39", "rea": "Table I.B1.2a.40", "mat": "Table I.B1.2a.41"}.items():
        t = read_table("mrq53f", sh)
        for c in t.columns:
            m = re.match(r"PISA (\d{4})\|(10th|25th|Median|75th|90th)[^|]*\|Score$", c)
            if m:
                pct += [{"country": a, "domain": d, "year": int(m.group(1)), "pct": m.group(2), "score": b}
                        for a, b in zip(t["country"], t[c])]
    pct = pd.DataFrame(pct).pivot_table(index=["country", "domain", "year"], columns="pct",
                                        values="score").reset_index()
    pct.to_csv(OUT / "percentiles_tendance.csv", index=False, float_format="%.2f")
    return r2, q, lt, pct


# --------------------------------------------------------------------------------------
def main():
    pd.set_option("display.width", 220)
    pd.set_option("display.max_columns", 30)
    s = build_scores_2025()
    print("\n[INFO] 2025 :", s.groupby("domain")["country"].nunique().to_dict(), "participants par domaine")
    sel = s[s["country"].isin(["France", "Türkiye", "Spain", "Norway"])]
    print(sel.pivot_table(index="country", columns="domain", values="mean").round(1))
    print(sel.groupby("country")["ci3"].first())

    # Écarts Türkiye - pays et France - moyenne OCDE, avec test z (erreurs types OCDE)
    comp = []
    t = s[s["country"] == "Türkiye"].set_index("domain")
    for c in ["France", "Spain", "Norway"]:
        x = s[s["country"] == c].set_index("domain")
        for d in DOMAINS:
            diff = t.loc[d, "mean"] - x.loc[d, "mean"]
            se = float(np.hypot(t.loc[d, "se"], x.loc[d, "se"]))
            comp.append({"comparaison": f"Türkiye - {c}", "domain": d, "ecart": round(diff, 1),
                         "se": round(se, 1), "z": round(diff / se, 2), "significatif_5pct": abs(diff / se) > 1.96})
    oecd_avg = {}
    for d, sh in {"sci": "Table I.B1.2a.1", "rea": "Table I.B1.2a.2", "mat": "Table I.B1.2a.3"}.items():
        tt = read_table("mrq53f", sh)
        row = tt[tt["country"] == "OECD average"].iloc[0]
        oecd_avg[d] = (row[pick(tt, "Mean score", "Mean")], row[pick(tt, "Mean score", "S.E.")])
    fr = s[s["country"] == "France"].set_index("domain")
    for d in DOMAINS:
        diff = fr.loc[d, "mean"] - oecd_avg[d][0]
        se = float(np.hypot(fr.loc[d, "se"], oecd_avg[d][1]))
        comp.append({"comparaison": "France - moyenne OCDE", "domain": d, "ecart": round(diff, 1),
                     "se": round(se, 1), "z": round(diff / se, 2), "significatif_5pct": abs(diff / se) > 1.96})
    comp = pd.DataFrame(comp)
    comp.to_csv(OUT / "comparaisons_ecarts.csv", index=False)
    print(comp.to_string())

    r = build_coverage_ranking(s)
    cols = ["country", "domain", "mean", "ci3", "rank_raw", "rank_best", "rank_worst", "n",
            "mean_all15_p10", "rank_mean_all15_p10", "mean_all15_p25", "rank_mean_all15_p25",
            "median_all15_lb", "rank_median_all15_lb", "low_all15_ub", "top_all15_lb",
            "rank_oecd_raw", "rank_oecd_p10", "rank_oecd_p25", "rank_oecd_medlb"]
    print("\n== Classement brut et à couverture égale ==")
    print(r[r["country"].isin(["France", "Türkiye", "Spain", "Norway"])][cols].round(1).to_string())

    tr = build_trends()
    h = build_rank_history(tr)
    print("\n== Rang de la France : tous contre groupe stable ==")
    print(h.to_string())

    escs = build_escs_table()
    infos, base = build_expected(s, escs, tr)
    print("\n== Score attendu ==")
    for i in infos:
        print(i["domain"], i["model"], "n=", i["n"], "R2=", i["r2"], "| FR", i.get("France"),
              "| TR", i.get("Türkiye"))

    r2, q, lt, pct = build_confirm()
    print("\n== R2 ESCS ==")
    print(r2[r2["country"].isin(["France", "Türkiye", "OECD average-35", "Germany", "Spain"])]
          .pivot_table(index=["country", "domain"], columns="year", values="r2").round(1))
    print("\n== Faibles / forts France et OCDE-23 ==")
    print(lt[lt["country"].isin(["France", "OECD average-23", "Türkiye"])]
          .pivot_table(index=["country", "domain", "var"] if False else ["country", "domain"],
                       columns="year", values=["low", "top"]).round(1).to_string())


if __name__ == "__main__":
    sys.exit(main())
