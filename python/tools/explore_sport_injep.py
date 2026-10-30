# -*- coding: utf-8 -*-
"""
Exploration des licences sportives INJEP (données géocodées, data.gouv.fr)
pour le futur dossier « Sport » d'Outsiders.

Ce script ne produit rien pour le site : il lit les fichiers téléchargés dans
python/data/sport/ et écrit des tables intermédiaires dans
python/data/sport/sorties/. Les résultats sont commentés dans
docs/sport/exploration_injep.md.

Sources lues (toutes téléchargées à la main, voir la note) :
- INJEP-MEDES, recensement des licences, fichiers géocodés par l'Insee :
  lic-data-2019.csv ... lic-data-2023.csv (maille commune x QPV, sexe x âge),
  lic-data-2016/2017/2018.csv et Licences_2013/2014/2015.csv (maille commune).
- Insee, populations municipales des QPV 2024 (pop_QPV24.xlsx, RP 2020).
- Insee, estimations de population par département, sexe et âge quinquennal
  (estim-pop-dep-sexe-aq-1975-2023.xls, converti en
  ref/pop_dep_sexe_aq_2019_2023.csv).
- Atlas Outsiders : population municipale 2021 (RP) et revenu médian Filosofi
  par commune (frontend/public/data/atlas/communes/*.json, lecture seule).

Usage : PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -I python/tools/explore_sport_injep.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "python" / "data" / "sport"
REF = DATA / "ref"
OUT = DATA / "sorties"
ATLAS = ROOT / "frontend" / "public" / "data" / "atlas"
OUT.mkdir(parents=True, exist_ok=True)

pd.set_option("display.width", 220)
pd.set_option("display.max_columns", 40)
pd.set_option("display.max_rows", 200)

# Bandes d'âge des fichiers 2019-2023
BANDES = ["1-4", "5-9", "10-14", "15-19", "20-24", "25-29", "30-34", "35-39",
          "40-44", "45-49", "50-54", "55-59", "60-64", "65-69", "70-74",
          "75-79", "80-99", "NR"]

# Fédérations dont l'adresse est celle du club (pas du licencié) en 2019-2023
ADR_CLUB = {"604", "605"}
# Fédérations non réparties par commune (département seulement)
NON_REPARTIES = {"406", "409", "411"}

SPORTS = {
    "111": "Football", "123": "Tennis", "109": "Équitation", "105": "Basket",
    "115": "Handball", "117": "Judo", "133": "Rugby", "132": "Golf",
    "119": "Natation", "101": "Athlétisme", "128": "Voile",
    "135": "Montagne et escalade", "113": "Gymnastique", "103": "Badminton",
    "129": "Volley", "106": "Boxe", "229": "Karaté", "212": "Savate",
    "261": "Kick-boxing, muay-thaï", "108": "Cyclisme", "124": "Tennis de table",
    "125": "Tir", "121": "Ski", "220": "Échecs", "245": "Randonnée",
    "242": "Pétanque", "241": "Pelote basque", "216": "Course landaise",
    "215": "Course camarguaise", "248": "Rugby à XIII", "137": "Surf",
    "122": "Taekwondo", "118": "Lutte", "110": "Escrime", "139": "Danse",
    "402": "EPGV (gym volontaire)", "413": "UFOLEP", "136": "Roller et skate",
    "127": "Triathlon", "107": "Canoë-kayak", "102": "Aviron",
    "271": "Clubs alpins", "211": "Sport boules", "207": "Balle au tambourin",
    "218": "Cyclotourisme", "221": "Études et sports sous-marins",
    "112": "Sports de glace", "131": "Hockey sur glace", "126": "Tir à l'arc",
}


def famille(code: str) -> str:
    c = str(code)[:1]
    return {"1": "unisport olympique", "2": "unisport non olympique",
            "4": "multisports", "5": "multisports (handi, adapté)",
            "6": "scolaire et universitaire"}.get(c, "autre")


def log(*a):
    print(*a, flush=True)


def save(df: pd.DataFrame, name: str):
    p = OUT / name
    df.to_csv(p, index=False, encoding="utf-8")
    log(f"[OK] {p.relative_to(ROOT)} ({len(df)} lignes)")


# ---------------------------------------------------------------------------
# Chargements
# ---------------------------------------------------------------------------
def load_geo(annee: int) -> pd.DataFrame:
    """Fichier 2019-2023 : une ligne par commune x QPV x fédération."""
    p = DATA / f"lic-data-{annee}.csv"
    d = pd.read_csv(p, sep=";", dtype=str, encoding="utf-8-sig")
    ident = ["com", "lib", "qpv", "nomqpv", "dep", "reg", "statut", "fed", "nomfed"]
    num_cols = list(d.columns[9:])
    newnum = []
    for c in num_cols:
        if c == "Total":
            newnum.append("Total")
            continue
        sexe, reste = c.split(" - ", 1)
        if reste.strip() == "NR":
            b = "NR"
        else:
            parts = reste.replace(" ans", "").split(" à ")
            b = f"{parts[0].strip()}-{parts[1].strip()}"
        newnum.append(f"{sexe}_{b}")
    d.columns = ident + newnum
    for c in newnum:
        d[c] = pd.to_numeric(d[c], errors="raise").astype("float64")
    d["typ"] = np.where(d.qpv.isin(["CSZ", "HZ"]), d.qpv,
                        np.where(d.qpv.str.startswith("NR"), "NR", "QPV"))
    d["F"] = d[[c for c in newnum if c.startswith("F_")]].sum(axis=1)
    d["H"] = d[[c for c in newnum if c.startswith("H_")]].sum(axis=1)
    d["annee"] = annee
    return d


def load_pop_dep() -> pd.DataFrame:
    p = pd.read_csv(REF / "pop_dep_sexe_aq_2019_2023.csv", dtype={"dep": str})
    return p


def pop_nat_bandes(annee: int) -> pd.DataFrame:
    """Population France (métropole + DOM, Insee) par sexe et bande alignée
    sur les bandes de licences (0-4 -> 1-4, 80 et plus -> 80-99)."""
    p = load_pop_dep()
    # somme des départements, Mayotte exclue (hors champ du géocodage)
    p = p[(p.annee == annee) & (p.dep.str.fullmatch(r"\d\d|2A|2B|97[1-4]"))]
    def bande(a):
        a = a.replace(" ans et plus", "").replace(" ans", "")
        if "à" in a:
            lo, hi = [int(x) for x in a.split(" à ")]
        else:
            lo, hi = int(a), 99
        if lo == 0:
            return "1-4"
        if lo >= 80:
            return "80-99"
        return f"{lo}-{hi}"
    p = p.assign(bande=p.age.map(bande))
    p = p.groupby(["sexe", "bande"], as_index=False)["pop"].sum()
    p["sexe"] = p.sexe.map({"Femmes": "F", "Hommes": "H", "Ensemble": "E"})
    return p


_COMMUNES = None


def load_atlas_communes() -> pd.DataFrame:
    """Population municipale 2021 (Insee, base « évolution et structure de la
    population » 2021, arrondissements de Paris, Lyon et Marseille inclus) et
    niveau de vie médian Filosofi 2023 (module revenu_filosofi du site, même
    source que l'Atlas). On ne lit pas les JSON de l'Atlas, qui peuvent être en
    cours de reconstruction."""
    global _COMMUNES
    if _COMMUNES is not None:
        return _COMMUNES
    p = pd.read_csv(REF / "pop2021" / "base-cc-evol-struct-pop-2021.CSV", sep=";", dtype=str,
                    usecols=["CODGEO", "P21_POP"])
    p["pop21"] = pd.to_numeric(p.P21_POP.str.replace(",", "."), errors="coerce")
    p = p.rename(columns={"CODGEO": "com"})[["com", "pop21"]]
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from revenu_filosofi import niveaux_de_vie_medians
    rev = niveaux_de_vie_medians()["com"]
    p["revenu"] = p.com.map(rev)
    # communes absentes de la base population mais présentes dans Filosofi
    _COMMUNES = p
    return p


def load_pop_qpv() -> pd.DataFrame:
    x = pd.read_excel(REF / "pop_QPV24.xlsx", header=None, skiprows=8)
    x.columns = ["qpv", "libqpv", "listeDepcom", "ListeLibDepcom", "listeEPCI2022",
                 "listeDep", "codeReg", "codeUU2020", "pop_qpv"]
    x["listeDepcom"] = x.listeDepcom.astype(str)
    x["mono"] = ~x.listeDepcom.str.contains(",")
    return x


# ---------------------------------------------------------------------------
# A. Description du jeu
# ---------------------------------------------------------------------------
def description(frames: dict):
    rows = []
    for a, d in frames.items():
        num = [c for c in d.columns if c[:2] in ("F_", "H_")]
        tot = d.Total.sum()
        ecart = (d[num].sum(axis=1) - d.Total).abs().sum()
        nonint = int((d[num] % 1 != 0).any(axis=1).sum())
        vals = d[num].to_numpy().ravel()
        vals = vals[vals > 0]
        rows.append({
            "annee": a, "lignes": len(d), "licences_total": tot,
            "nb_federations": d.fed.nunique(),
            "part_hors_champ_geocodage": d.loc[d.statut.str.startswith("2"), "Total"].sum() / tot,
            "part_non_repartie": d.loc[d.typ == "NR", "Total"].sum() / tot,
            "part_qpv": d.loc[d.typ == "QPV", "Total"].sum() / tot,
            "part_hz": d.loc[d.typ == "HZ", "Total"].sum() / tot,
            "part_csz": d.loc[d.typ == "CSZ", "Total"].sum() / tot,
            "prefixe_codes_qpv": ",".join(sorted(d.loc[d.typ == "QPV", "qpv"].str[:2].unique())),
            "nb_qpv": d.loc[d.typ == "QPV", "qpv"].nunique(),
            "part_femmes": d.F.sum() / tot,
            "part_age_nr": (d[[c for c in num if c.endswith("_NR")]].sum().sum()) / tot,
            "ecart_total_vs_somme_cellules": ecart,
            "lignes_valeurs_non_entieres": nonint,
            "part_cellules_positives_egales_1_ou_2": float(np.mean(vals <= 2)),
            "licences_scolaires_6xx": d.loc[d.fed.str.startswith("6"), "Total"].sum(),
            "licences_adr_club_604_605": d.loc[d.fed.isin(ADR_CLUB), "Total"].sum(),
        })
    t = pd.DataFrame(rows)
    save(t, "a_description_millesimes.csv")
    log(t.T)

    # Familles de fédérations 2023
    d = frames[max(frames)]
    fam = d.assign(famille=d.fed.map(famille)).groupby("famille").agg(
        licences=("Total", "sum"), F=("F", "sum"), nb_fed=("fed", "nunique")).reset_index()
    fam["part_femmes"] = fam.F / fam.licences
    save(fam, "a_familles_2023.csv")
    log(fam)

    # Totaux par fédération et année (2019-2023) + part de femmes
    allf = pd.concat([f.groupby(["annee", "fed"]).agg(
        nomfed=("nomfed", "first"), licences=("Total", "sum"), F=("F", "sum")).reset_index()
        for f in frames.values()])
    allf["part_femmes"] = allf.F / allf.licences
    save(allf, "a_federations_2019_2023.csv")


# ---------------------------------------------------------------------------
# B. Géographie : licences pour 1 000 habitants par fédération et département
# ---------------------------------------------------------------------------
def geographie(d: pd.DataFrame, annee: int):
    pop = load_pop_dep()
    pop = pop[(pop.annee == annee) & (pop.sexe == "Ensemble")]
    pop = pop.groupby("dep", as_index=False)["pop"].sum()
    deps = pop[pop.dep.str.fullmatch(r"\d\d|2A|2B|97[1-4]")].rename(columns={"pop": "pop_dep"})
    # champ : fédérations à adresse du licencié, hors scolaires/universitaires
    x = d[(d.statut.str.startswith("1")) & (d.typ != "NR") & (~d.fed.str.startswith("6"))]
    g = x.groupby(["dep", "fed"], as_index=False).agg(licences=("Total", "sum"),
                                                     nomfed=("nomfed", "first"))
    g = g.merge(deps, on="dep", how="inner")
    g["pour_1000"] = g.licences / g.pop_dep * 1000
    nat = g.groupby("fed").agg(lic_nat=("licences", "sum")).reset_index()
    popnat = deps.pop_dep.sum()
    nat["pour_1000_nat"] = nat.lic_nat / popnat * 1000
    g = g.merge(nat, on="fed")
    g["indice_specialisation"] = g.pour_1000 / g.pour_1000_nat  # 1 = moyenne France
    g["sport"] = g.fed.map(SPORTS).fillna(g.nomfed)
    save(g.sort_values(["fed", "dep"]), f"b_dep_federation_{annee}.csv")

    # Total toutes fédérations (hors scolaires) par département
    tot = g.groupby("dep", as_index=False).agg(licences=("licences", "sum"), pop_dep=("pop_dep", "first"))
    tot["pour_1000"] = tot.licences / tot.pop_dep * 1000
    save(tot.sort_values("pour_1000"), f"b_dep_total_{annee}.csv")
    log("Licences (hors scolaires) pour 1 000 hab. par département : min/médiane/max",
        tot.pour_1000.min().round(0), tot.pour_1000.median().round(0), tot.pour_1000.max().round(0))
    log(tot.sort_values("pour_1000").head(5)); log(tot.sort_values("pour_1000").tail(5))

    # Fédération en tête (en nombre) par département
    top = g.sort_values("licences", ascending=False).groupby("dep").head(2)
    top = top.sort_values(["dep", "licences"], ascending=[True, False])
    first = top.groupby("dep").head(1)
    log("Fédération n°1 par département, répartition :", first.sport.value_counts().to_dict())
    log(first[first.fed != "111"][["dep", "sport", "licences", "pour_1000"]])
    save(top, f"b_dep_top2_{annee}.csv")

    # Spécialisations : pour chaque grande fédération (>= 50 000 licences), 3 départements
    grands = nat[nat.lic_nat >= 50000].fed
    sp = (g[g.fed.isin(grands)].sort_values("indice_specialisation", ascending=False)
          .groupby("fed").head(3))
    sp = sp.sort_values(["lic_nat", "indice_specialisation"], ascending=[False, False])
    save(sp[["fed", "sport", "lic_nat", "pour_1000_nat", "dep", "pour_1000", "indice_specialisation"]],
         f"b_specialisations_top3_{annee}.csv")
    log(sp[["sport", "pour_1000_nat", "dep", "pour_1000", "indice_specialisation"]].head(60))

    # Pour chaque département métropolitain, la fédération la plus surreprésentée
    # (parmi celles >= 20 000 licences nationales et >= 500 licences dans le département)
    cand = g[(g.lic_nat >= 20000) & (g.licences >= 500)]
    best = cand.sort_values("indice_specialisation", ascending=False).groupby("dep").head(1)
    save(best.sort_values("dep")[["dep", "sport", "licences", "pour_1000", "pour_1000_nat",
                                  "indice_specialisation"]], f"b_dep_sport_signature_{annee}.csv")

    # Écart interdépartemental des grandes fédérations (rapport P90/P10 des taux, métropole)
    metro = g[~g.dep.str.startswith("97")]
    disp = metro[metro.fed.isin(grands)].groupby(["fed", "sport"]).pour_1000.agg(
        p10=lambda s: s.quantile(0.1), p50="median", p90=lambda s: s.quantile(0.9)).reset_index()
    disp["rapport_p90_p10"] = disp.p90 / disp.p10
    disp = disp.merge(nat, on="fed").sort_values("rapport_p90_p10")
    save(disp, f"b_dispersion_departements_{annee}.csv")
    log(disp)


# ---------------------------------------------------------------------------
# C. QPV contre hors QPV dans les mêmes communes
# ---------------------------------------------------------------------------
def qpv_vs_hz(d: pd.DataFrame, annee: int, avec_pop: bool):
    x = d[(d.statut.str.startswith("1")) & (d.typ.isin(["QPV", "HZ"]))
          & (~d.fed.str.startswith("6")) & (~d.fed.isin(NON_REPARTIES))].copy()
    x["zone"] = np.where(x.typ == "QPV", "Q", "H")
    # communes avec les deux parties
    zc = x.groupby(["com", "zone"]).Total.sum().unstack()
    communes = zc[(zc.Q > 0) & (zc.H > 0)].index
    x = x[x.com.isin(communes)]
    log(f"[INFO] {annee} : {len(communes)} communes avec partie QPV et partie hors QPV")

    cf = x.groupby(["com", "fed", "zone"]).Total.sum().unstack(fill_value=0)
    ct = x.groupby(["com", "zone"]).Total.sum().unstack(fill_value=0)
    cf = cf.join(ct, rsuffix="_tot")
    # Attendu en QPV si la fédération avait le même poids qu'hors QPV dans la même commune
    cf["attendu_Q"] = cf.Q_tot * cf.H / cf.H_tot
    r = cf.groupby(level="fed")[["Q", "H", "attendu_Q"]].sum()
    r["part_Q"] = r.Q / r.Q.sum()
    r["part_H"] = r.H / r.H.sum()
    r["ratio_brut_parts"] = r.part_Q / r.part_H
    r["ratio_standardise_commune"] = r.Q / r.attendu_Q
    r = r.reset_index()
    noms = d.groupby("fed").nomfed.first()
    r["nomfed"] = r.fed.map(noms)
    r["sport"] = r.fed.map(SPORTS).fillna(r.nomfed)
    r = r.sort_values("Q", ascending=False)

    # Filles : part des licences féminines
    fz = x.groupby("zone")[["F", "H"]].sum()
    log(f"[INFO] part de femmes QPV {fz.loc['Q','F']/fz.loc['Q'].sum():.3f} ; hors QPV {fz.loc['H','F']/fz.loc['H'].sum():.3f}")
    ff = x.groupby(["fed", "zone"])[["F", "H"]].sum()
    ff["part_f"] = ff.F / (ff.F + ff.H)
    pf = ff.part_f.unstack()
    r = r.merge(pf.rename(columns={"Q": "part_femmes_Q", "H": "part_femmes_H"}).reset_index(), on="fed", how="left")

    if avec_pop:
        pq = load_pop_qpv()
        # communes dont tous les QPV (du fichier licences) sont mono-communaux et connus
        q_in = x[x.zone == "Q"][["com", "qpv"]].drop_duplicates().merge(
            pq[["qpv", "mono", "pop_qpv", "listeDepcom"]], on="qpv", how="left")
        ok = q_in.groupby("com").apply(
            lambda s: bool(s.mono.fillna(False).all() and (s.listeDepcom == s.name).all()),
            include_groups=False)
        # population de tous les QPV de la commune (y compris ceux sans licence)
        pq_m = pq[pq.mono].groupby("listeDepcom").pop_qpv.sum()
        multi = set()
        for l in pq[~pq.mono].listeDepcom:
            multi.update(l.split(","))
        at = load_atlas_communes().set_index("com")
        good = [c for c in ok[ok].index if c not in multi and c in pq_m.index and c in at.index
                and pd.notna(at.loc[c, "pop21"])]
        popc = pd.DataFrame({"pop_Q": pq_m.reindex(good), "pop_com": at.pop21.reindex(good)})
        popc["pop_H"] = popc.pop_com - popc.pop_Q
        popc = popc[popc.pop_H > 0]
        log(f"[INFO] {len(popc)} communes avec population QPV et hors QPV utilisable "
            f"(QPV mono-communaux) ; pop QPV {popc.pop_Q.sum():,.0f}, hors QPV {popc.pop_H.sum():,.0f}")
        xs = x[x.com.isin(popc.index)]
        lz = xs.groupby(["fed", "zone"]).Total.sum().unstack(fill_value=0)
        lz["taux_Q_pour_1000"] = lz.Q / popc.pop_Q.sum() * 1000
        lz["taux_H_pour_1000"] = lz.H / popc.pop_H.sum() * 1000
        lz["rapport_taux_Q_sur_H"] = lz.taux_Q_pour_1000 / lz.taux_H_pour_1000
        r = r.merge(lz[["taux_Q_pour_1000", "taux_H_pour_1000", "rapport_taux_Q_sur_H"]].reset_index(),
                    on="fed", how="left")
        totq = xs[xs.zone == "Q"].Total.sum() / popc.pop_Q.sum() * 1000
        toth = xs[xs.zone == "H"].Total.sum() / popc.pop_H.sum() * 1000
        fq = xs[xs.zone == "Q"].F.sum() / popc.pop_Q.sum() * 1000
        fh = xs[xs.zone == "H"].F.sum() / popc.pop_H.sum() * 1000
        hq = xs[xs.zone == "Q"].H.sum() / popc.pop_Q.sum() * 1000
        hh = xs[xs.zone == "H"].H.sum() / popc.pop_H.sum() * 1000
        log(f"[INFO] licences pour 1 000 hab. : QPV {totq:.0f}, hors QPV même communes {toth:.0f}, rapport {totq/toth:.2f}")
        log(f"[INFO] licences féminines pour 1 000 hab. : QPV {fq:.0f}, hors QPV {fh:.0f}, rapport {fq/fh:.2f}")
        log(f"[INFO] licences masculines pour 1 000 hab. : QPV {hq:.0f}, hors QPV {hh:.0f}, rapport {hq/hh:.2f}")
        # dispersion entre communes du rapport global (communes >= 1000 hab en QPV)
        pc = xs.groupby(["com", "zone"]).Total.sum().unstack().join(popc)
        pc["rq"] = pc.Q / pc.pop_Q
        pc["rh"] = pc.H / pc.pop_H
        pc["rapport"] = pc.rq / pc.rh
        big = pc[pc.pop_Q >= 1000]
        log(f"[INFO] rapport des taux QPV/hors QPV par commune (pop QPV >= 1000, n={len(big)}) : "
            f"P25 {big.rapport.quantile(.25):.2f} médiane {big.rapport.median():.2f} P75 {big.rapport.quantile(.75):.2f} ; "
            f"part des communes où QPV > hors QPV : {(big.rapport > 1).mean():.3f}")
        save(pc.reset_index(), f"c_qpv_communes_taux_{annee}.csv")
        resume = pd.DataFrame([{"annee": annee, "communes": len(popc), "pop_qpv": popc.pop_Q.sum(),
                                "pop_hors_qpv": popc.pop_H.sum(), "taux_qpv": totq, "taux_hors_qpv": toth,
                                "taux_f_qpv": fq, "taux_f_hors": fh, "taux_h_qpv": hq, "taux_h_hors": hh,
                                "communes_pop_qpv_1000": len(big),
                                "rapport_median_communes": big.rapport.median(),
                                "part_communes_qpv_sup": (big.rapport > 1).mean()}])
        save(resume, f"c_qpv_resume_{annee}.csv")

    save(r, f"c_qpv_vs_horsqpv_federations_{annee}.csv")
    cols = ["sport", "Q", "H", "part_Q", "part_H", "ratio_brut_parts", "ratio_standardise_commune",
            "part_femmes_Q", "part_femmes_H"] + (["taux_Q_pour_1000", "taux_H_pour_1000", "rapport_taux_Q_sur_H"] if avec_pop else [])
    log(r[r.Q >= 1000][cols].round(3).head(45))

    # Âge : profil par bande et sexe, QPV contre hors QPV (mêmes communes)
    ages = [c for c in x.columns if c[:2] in ("F_", "H_") and not c.endswith("_NR")]
    prof = x.groupby("zone")[ages].sum().T
    prof.index.name = "col"
    prof = prof.reset_index()
    prof["sexe"] = prof.col.str[0]
    prof["bande"] = prof.col.str[2:]
    save(prof, f"c_qpv_profil_age_{annee}.csv")
    rr = []
    for sexe in ("F", "H"):
        for z in ("Q", "H"):
            s = prof[prof.sexe == sexe].set_index("bande")[z]
            rr.append({"sexe": sexe, "zone": z, "l_5_9": s["5-9"], "l_10_14": s["10-14"],
                       "l_15_19": s["15-19"], "l_20_24": s["20-24"],
                       "r_15_19_sur_10_14": s["15-19"] / s["10-14"],
                       "r_10_14_sur_5_9": s["10-14"] / s["5-9"]})
    rr = pd.DataFrame(rr)
    log(rr.round(3))
    save(rr, f"c_qpv_retention_{annee}.csv")
    # même chose par fédération (grandes), standardisé par commune : rapport 15-19/10-14
    rows = []
    for fed in r[r.Q >= 2000].fed:
        xf = x[x.fed == fed]
        for sexe in ("F", "H"):
            agg = xf.groupby("zone")[[f"{sexe}_10-14", f"{sexe}_15-19"]].sum()
            if agg.shape[0] < 2:
                continue
            rows.append({"fed": fed, "sport": SPORTS.get(fed, noms.get(fed)), "sexe": sexe,
                         "Q_10_14": agg.loc["Q", f"{sexe}_10-14"], "Q_15_19": agg.loc["Q", f"{sexe}_15-19"],
                         "H_10_14": agg.loc["H", f"{sexe}_10-14"], "H_15_19": agg.loc["H", f"{sexe}_15-19"]})
    rf = pd.DataFrame(rows)
    rf["r_Q"] = rf.Q_15_19 / rf.Q_10_14
    rf["r_H"] = rf.H_15_19 / rf.H_10_14
    save(rf, f"c_qpv_retention_federations_{annee}.csv")
    log(rf.round(3))
    return r


def effet_age_qpv():
    """Ordre de grandeur de l'effet de structure par âge sur le rapport QPV / hors QPV.
    Structure par âge publiée par l'Insee (Insee Première n° 2008, août 2024, RP 2020) :
    moins de 25 ans 39 % en QPV contre 30 % dans les environnements urbains ;
    60 ans ou plus 18 % contre 26 %. On applique les taux nationaux 2023 par grand âge
    (lus dans d_age_sexe_national_2023.csv) à ces deux structures."""
    t = pd.read_csv(OUT / "d_age_sexe_national_2023.csv", dtype={"fed": str})
    def grp(b):
        lo = int(b.split("-")[0])
        return "0-24" if lo < 25 else ("25-59" if lo < 60 else "60+")
    t["g"] = t.bande.map(grp)
    g = t.groupby(["fed", "g"])[["licences", "pop"]].sum()
    g["taux"] = g.licences / g["pop"]
    struct = {"QPV": {"0-24": .39, "25-59": .43, "60+": .18},
              "environnement": {"0-24": .30, "25-59": .44, "60+": .26}}
    rows = []
    for fed in g.index.get_level_values(0).unique():
        tx = g.loc[fed, "taux"]
        e = {k: sum(v[a] * tx.get(a, 0) for a in v) for k, v in struct.items()}
        rows.append({"fed": fed, "sport": SPORTS.get(fed, fed), "taux_attendu_qpv": e["QPV"] * 1000,
                     "taux_attendu_env": e["environnement"] * 1000,
                     "rapport_attendu_par_age": e["QPV"] / e["environnement"]})
    r = pd.DataFrame(rows)
    save(r, "c_qpv_effet_structure_age.csv")
    log(r.round(3))


# ---------------------------------------------------------------------------
# D. Âge et sexe au niveau national (taux par habitant)
# ---------------------------------------------------------------------------
def age_national(d: pd.DataFrame, annee: int):
    pop = pop_nat_bandes(annee)
    x = d[(~d.fed.str.startswith("6")) & (~d.statut.str.startswith("2"))]
    ages = [c for c in x.columns if c[:2] in ("F_", "H_") and not c.endswith("_NR")]
    rows = []
    groupes = {"TOUT (hors scolaires)": x}
    for fed in ["111", "123", "109", "105", "115", "117", "133", "132", "119", "101",
                "128", "135", "113", "139", "103", "129", "106", "229", "402", "245", "242", "108"]:
        groupes[fed] = x[x.fed == fed]
    for k, xf in groupes.items():
        s = xf[ages].sum()
        for col, v in s.items():
            sexe, bande = col[0], col[2:]
            p = pop[(pop.sexe == sexe) & (pop.bande == bande)]["pop"].sum()
            rows.append({"fed": k, "sport": SPORTS.get(k, k), "sexe": sexe, "bande": bande,
                         "licences": v, "pop": p, "pour_1000": v / p * 1000 if p else np.nan})
    t = pd.DataFrame(rows)
    save(t, f"d_age_sexe_national_{annee}.csv")
    piv = t.pivot_table(index=["sport", "sexe"], columns="bande", values="pour_1000")
    piv = piv[[b for b in BANDES if b in piv.columns]]
    piv["pic"] = piv.idxmax(axis=1)
    piv["r_15_19_sur_10_14"] = piv["15-19"] / piv["10-14"]
    piv["r_20_24_sur_15_19"] = piv["20-24"] / piv["15-19"]
    log(piv[["5-9", "10-14", "15-19", "20-24", "30-34", "45-49", "65-69", "pic",
             "r_15_19_sur_10_14", "r_20_24_sur_15_19"]].round(2))
    save(piv.reset_index(), f"d_age_sexe_national_pivot_{annee}.csv")


# ---------------------------------------------------------------------------
# E. Lecture écologique : revenu médian des communes (déciles de population)
# ---------------------------------------------------------------------------
def deciles_revenu(com_lic: pd.DataFrame, pop_col: str, label: str):
    """com_lic : une ligne par commune x fédération avec licences + colonnes de pop."""
    at = load_atlas_communes()
    at = at[at.revenu.notna()]
    base = com_lic.merge(at[["com", "revenu"]], on="com", how="inner")
    cp = base.groupby("com").agg(revenu=("revenu", "first"), pop=(pop_col, "first")).dropna()
    cp = cp[cp["pop"] > 0].sort_values("revenu")
    cp["cum"] = cp["pop"].cumsum() / cp["pop"].sum()
    cp["decile"] = np.minimum((cp.cum * 10).apply(np.ceil).astype(int), 10)
    base = base.merge(cp[["decile"]].reset_index(), on="com")
    bornes = cp.groupby("decile").agg(revenu_min=("revenu", "min"), revenu_max=("revenu", "max"),
                                      pop=("pop", "sum"), communes=("revenu", "size")).reset_index()
    log(f"[INFO] {label} : {len(cp)} communes avec revenu ; bornes des déciles"); log(bornes)
    save(bornes, f"e_bornes_deciles_{label}.csv")
    return base, bornes


def revenu_2023(d: pd.DataFrame):
    x = d[(d.statut.str.startswith("1")) & (d.typ != "NR") & (~d.fed.str.startswith("6"))]
    cl = x.groupby(["com", "fed"], as_index=False).agg(licences=("Total", "sum"), F=("F", "sum"),
                                                       l10=("Total", "size"))
    # bandes d'âge sommées sur les deux sexes
    for b in ["10-14", "15-19", "20-24", "5-9"]:
        s = x.groupby(["com", "fed"])[[f"F_{b}", f"H_{b}"]].sum()
        cl = cl.merge(s.reset_index(), on=["com", "fed"])
    at = load_atlas_communes()
    cl = cl.merge(at[["com", "pop21"]], on="com", how="left")
    base, bornes = deciles_revenu(cl, "pop21", "2023")
    g = base.groupby(["decile", "fed"]).agg(licences=("licences", "sum"), F=("F", "sum")).reset_index()
    g = g.merge(bornes[["decile", "pop"]], on="decile")
    g["pour_1000"] = g.licences / g["pop"] * 1000
    g["sport"] = g.fed.map(SPORTS)
    tot = g.groupby("decile").agg(licences=("licences", "sum"), F=("F", "sum"), pop=("pop", "first")).reset_index()
    tot["pour_1000"] = tot.licences / tot["pop"] * 1000
    tot["part_femmes"] = tot.F / tot.licences
    log("[INFO] licences hors scolaires pour 1 000 hab. par décile de revenu des communes (2023)"); log(tot.round(3))
    save(tot, "e_revenu_total_2023.csv")
    sel = g[g.fed.isin(SPORTS.keys())].pivot_table(index="sport", columns="decile", values="pour_1000")
    sel["rapport_D10_D1"] = sel[10] / sel[1]
    sel = sel.sort_values("rapport_D10_D1")
    log(sel.round(2))
    save(sel.reset_index(), "e_revenu_federations_2023.csv")
    # part des licences par décile (composition) pour le football
    comp = g.pivot_table(index="fed", columns="decile", values="licences")
    comp = comp / comp.sum()
    save(comp.reset_index(), "e_revenu_composition_2023.csv")
    # rapport 15-19 / 10-14 des licences par décile (sans population par âge)
    a = base.groupby("decile")[["F_10-14", "H_10-14", "F_15-19", "H_15-19"]].sum()
    a["r_F"] = a["F_15-19"] / a["F_10-14"]
    a["r_H"] = a["H_15-19"] / a["H_10-14"]
    log(a.round(3))
    save(a.reset_index(), "e_revenu_ratio_ages_2023.csv")


def load_2018():
    p = DATA / "lic-data-2018.csv"
    if not p.exists():
        log("[ERROR] lic-data-2018.csv absent")
        return None
    head = pd.read_csv(p, sep=";", nrows=3, encoding="latin-1", dtype=str)
    log(f"[INFO] colonnes 2018 : {list(head.columns)[:12]} ... ({len(head.columns)} colonnes)")
    d = pd.read_csv(p, sep=";", encoding="latin-1", dtype=str)
    return d


def revenu_age_2018(d18: pd.DataFrame):
    """Taux de licence par âge et sexe selon le revenu de la commune, licences 2018
    et population RP 2017 incluses dans le fichier (même maille commune)."""
    d18 = d18.copy()
    d18.columns = [c.replace("_2018", "").replace("_2017", "") for c in d18.columns]
    d18 = d18[~d18.fed.astype(str).str.startswith("6")]
    bands = ["0_4", "5_9", "10_14", "15_19", "20_29", "30_44", "45_59", "60_74", "75"]
    lic_cols = [f"l_{b}_{s}" for b in bands for s in ("f", "h")]
    pop_cols = [f"pop{s}_{b}" for b in bands for s in ("f", "h")] + ["pop"]
    for c in lic_cols + pop_cols:
        # les grandes communes ont un séparateur de milliers (espace) dans le fichier 2018
        d18[c] = pd.to_numeric(d18[c].astype(str).str.replace(r"\s", "", regex=True), errors="coerce")
    d18["com"] = d18.code_commune.astype(str).str.zfill(5)
    lic = d18.groupby("com")[lic_cols].sum()
    pop = d18.groupby("com")[pop_cols].first()
    cm = lic.join(pop).reset_index()
    cm["fed"] = "ALL"
    cm["licences"] = cm[lic_cols].sum(axis=1)
    base, bornes = deciles_revenu(cm, "pop", "2018")
    g = base.groupby("decile")[lic_cols + pop_cols].sum()
    rows = []
    for dec, r in g.iterrows():
        for s in ("f", "h"):
            for b in bands:
                rows.append({"decile": dec, "sexe": s.upper(), "bande": b.replace("_", "-"),
                             "licences": r[f"l_{b}_{s}"], "pop": r[f"pop{s}_{b}"],
                             "pour_100": r[f"l_{b}_{s}"] / r[f"pop{s}_{b}"] * 100})
    t = pd.DataFrame(rows)
    save(t, "e_revenu_age_sexe_2018.csv")
    piv = t.pivot_table(index=["sexe", "decile"], columns="bande", values="pour_100")
    piv = piv[[b.replace("_", "-") for b in bands]]
    piv["r_15_19_sur_10_14"] = piv["15-19"] / piv["10-14"]
    piv["r_20_29_sur_15_19"] = piv["20-29"] / piv["15-19"]
    log("[INFO] 2018, licences pour 100 habitants par âge, sexe et décile de revenu (hors scolaires)")
    log(piv.round(3))
    save(piv.reset_index(), "e_revenu_age_sexe_2018_pivot.csv")
    # par fédération : football, tennis, équitation, natation, judo, basket
    rows = []
    for fed in ["111", "123", "109", "119", "117", "105", "115", "133", "132"]:
        sub = d18[d18.fed.astype(str) == fed]
        lf = sub.groupby("com")[lic_cols].sum()
        z = lf.join(pop, how="right").fillna({c: 0 for c in lic_cols}).reset_index()
        z = z.merge(base[["com", "decile"]].drop_duplicates(), on="com")
        gg = z.groupby("decile")[lic_cols + pop_cols].sum()
        for dec, r in gg.iterrows():
            for s in ("f", "h"):
                rows.append({"fed": fed, "sport": SPORTS[fed], "decile": dec, "sexe": s.upper(),
                             "t_10_14": r[f"l_10_14_{s}"] / r[f"pop{s}_10_14"] * 100,
                             "t_15_19": r[f"l_15_19_{s}"] / r[f"pop{s}_15_19"] * 100,
                             "t_20_29": r[f"l_20_29_{s}"] / r[f"pop{s}_20_29"] * 100})
    tf = pd.DataFrame(rows)
    tf["r_15_19_sur_10_14"] = tf.t_15_19 / tf.t_10_14
    save(tf, "e_revenu_age_sexe_federations_2018.csv")
    log(tf[tf.decile.isin([1, 5, 10])].round(3))


# ---------------------------------------------------------------------------
# F. Séries temporelles par fédération
# ---------------------------------------------------------------------------
def totaux_anciens():
    """Totaux nationaux par fédération dans les fichiers 2013-2018 (maille commune).
    Avant 2019, les licences non réparties par commune ne sont pas dans les fichiers :
    les totaux sont donc inférieurs aux résultats du recensement (rupture de champ)."""
    out = []
    specs = {2013: "Licences_2013.csv", 2014: "Licences_2014.csv", 2015: "Licences_2015.csv",
             2016: "lic-data-2016.csv", 2017: "lic-data-2017.csv", 2018: "lic-data-2018.csv"}
    for a, f in specs.items():
        p = DATA / f
        if not p.exists():
            log(f"[INFO] {f} absent")
            continue
        raw = p.read_bytes()[:20000]
        try:
            raw.decode("utf-8")
            enc = "utf-8-sig"
        except UnicodeDecodeError:
            enc = "latin-1"
        first = raw.decode(enc, errors="ignore").splitlines()[0]
        sep = ";" if first.count(";") > first.count(",") else ","
        cols = [c.strip().lstrip("﻿") for c in first.split(sep)]
        fedc = [c for c in cols if c.lower().startswith("fed")][0]
        totc = f"l_{a}"
        femc = f"l_f_{a}"
        d = pd.read_csv(p, sep=sep, encoding=enc, usecols=[fedc, totc, femc], dtype=str)
        for c in (totc, femc):
            d[c] = pd.to_numeric(d[c].str.replace(r"\s", "", regex=True), errors="coerce")
        g = d.groupby(fedc)[[totc, femc]].sum().reset_index()
        g.columns = ["fed", "licences", "F"]
        g["annee"] = a
        log(f"[INFO] {f} : {enc}, sép. '{sep}', {g.licences.sum():,.0f} licences, {g.fed.nunique()} fédérations")
        out.append(g)
    return pd.concat(out) if out else pd.DataFrame(columns=["fed", "licences", "F", "annee"])


def series(frames: dict):
    rec = pd.concat([f.groupby(["annee", "fed"])[["Total", "F"]].sum().reset_index().rename(columns={"Total": "licences"})
                     for f in frames.values()])
    old = totaux_anciens()
    allt = pd.concat([old, rec])
    allt["fed"] = allt.fed.astype(str).str.strip()
    piv = allt.pivot_table(index="fed", columns="annee", values="licences", aggfunc="sum")
    piv["sport"] = piv.index.map(SPORTS)
    save(piv.reset_index(), "f_series_federations.csv")
    pf = allt.groupby(["fed", "annee"])[["licences", "F"]].sum()
    pf = (pf.F / pf.licences).unstack()
    pf["sport"] = pf.index.map(SPORTS)
    save(pf.reset_index(), "f_series_part_femmes.csv")
    tot = allt.assign(scol=allt.fed.str.startswith("6")).groupby(["annee", "scol"])[["licences", "F"]].sum().reset_index()
    save(tot, "f_series_totaux.csv")
    log(tot)
    sel = piv[piv.sport.notna()].copy()
    yrs = [c for c in piv.columns if isinstance(c, (int, np.integer))]
    first = min(yrs)
    sel[f"evol_{first}_2023"] = sel[2023] / sel[first] - 1
    sel["evol_2019_2023"] = sel[2023] / sel[2019] - 1
    sel["evol_2021_2023"] = sel[2023] / sel[2021] - 1
    sel = sel.sort_values(2023, ascending=False)
    log(sel[["sport"] + yrs + [f"evol_{first}_2023", "evol_2019_2023"]].round(3).to_string())
    save(sel.reset_index(), "f_series_selection.csv")


# ---------------------------------------------------------------------------
def main():
    etapes = sys.argv[1:] or ["A", "B", "C", "D", "E", "F"]
    frames = {}
    need_all = any(e in etapes for e in ("A", "F"))
    years = [2019, 2020, 2021, 2022, 2023] if need_all else [2023]
    if "C" in etapes and 2022 not in years:
        years = [2022, 2023]
    for a in years:
        log(f"[INFO] lecture {a}")
        frames[a] = load_geo(a)
    d23 = frames[2023]
    if "A" in etapes:
        description(frames)
    if "B" in etapes:
        geographie(d23, 2023)
    if "C" in etapes:
        qpv_vs_hz(d23, 2023, avec_pop=True)
        if 2022 in frames:
            qpv_vs_hz(frames[2022], 2022, avec_pop=False)
    if "D" in etapes:
        age_national(d23, 2023)
        effet_age_qpv()
    if "E" in etapes:
        revenu_2023(d23)
        d18 = load_2018()
        if d18 is not None:
            revenu_age_2018(d18)
    if "F" in etapes:
        series(frames)


if __name__ == "__main__":
    main()
