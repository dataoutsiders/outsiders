# -*- coding: utf-8 -*-
"""
Exploration « élite » du dossier Sport d'Outsiders : les internationaux des
équipes de France (football, rugby à XV, basket-ball, handball ; hommes et
femmes séparément) et la délégation française aux Jeux olympiques de Paris 2024.

Ce script ne produit rien pour le site. Il écrit :
- des données NOMINATIVES brutes dans python/data/sport/elite/ (à ne jamais
  copier dans frontend/ ni dans la note) ;
- des tables AGRÉGÉES, sans aucun nom de personne, dans
  python/data/sport/sorties/elite_*.csv.
Les résultats sont commentés dans docs/sport/exploration_elite.md.

Sources :
- Wikidata (CC0), service SPARQL https://query.wikidata.org/sparql :
  appartenance (P54) aux équipes nationales, participation (P1344) à
  « France aux Jeux olympiques d'été de 2024 » (Q114244785), sexe (P21),
  date (P569) et lieu (P19) de naissance, code commune Insee du lieu (P374),
  code département Insee (P2586) des entités englobantes (P131), nom de famille (P734).
- Wikipédia en français (CC BY-SA), API MediaWiki : catégories
  « Footballeur international français », etc., et listes de référence
  (« Liste des footballeurs internationaux français », « Liste des sélectionnés
  en équipe de France de rugby à XV », « Liste des joueuses de l'équipe de
  France féminine de football ») : appartenance seulement, et contrôle de complétude.
- Insee, fichier des noms de famille 1891-2000 (noms2008nat_txt.txt, déjà
  utilisé par build_onomastics_reference.py) : référence IDP des naissances
  en France par période.
- INJEP-MEDES, licences 2013 (Licences_2013.csv, tranches 10-14 et 15-19 ans
  par sexe) et clubs 2023 (clubs-data-2023.csv).
- Insee : Filosofi 2023 (revenu_filosofi.py), populations des QPV 2024
  (ref/pop_QPV24.xlsx), estimations de population départementale (ref/).
- Insee, étape « fourchette » : immigrés par sexe et âge au RP 2023
  (DS_RP_TD_IMMI_AGESEXEMPSTA_PRINC, API Melodi) ; série « Population immigrée
  et étrangère par sexe et âge » 1990-2025 et estimations de population par âge
  (DS_ESTIMATION_POPULATION), mises en cache dans ref/immigres/.

Usage :
  PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -I python/tools/explore_sport_elite.py [etapes]
  étapes : collecte, idp, territoires, fourchette (par défaut : toutes)
"""
import json
import math
import re
import sys
import time
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd
import requests
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "python" / "data" / "sport"
ELITE = DATA / "elite"
REF = DATA / "ref"
OUT = DATA / "sorties"
NOMS_FILE = ROOT / "python" / "data" / "municipales" / "noms_famille" / "noms2008nat_txt.txt"
ELITE.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)
# Le dossier elite/ est nominatif : on l'exclut de tout versionnement.
(ELITE / ".gitignore").write_text("*\n", encoding="utf-8")

pd.set_option("display.width", 220)
pd.set_option("display.max_columns", 40)
pd.set_option("display.max_rows", 200)

UA = ("OutsidersExploration/0.1 (https://dataoutsiders.fr ; dataoutsiders@gmail.com) "
      "exploration statistique agregee, requetes en lots")
SPARQL = "https://query.wikidata.org/sparql"
WIKI = "https://fr.wikipedia.org/w/api.php"
SESSION = requests.Session()
SESSION.headers["User-Agent"] = UA

# Équipes A (seniors) : Q Wikidata, catégorie Wikipédia, liste de référence
EQUIPES = {
    "football_H": dict(sport="football", sexe="H", q="Q47774",
                       cat="Footballeur international français",
                       liste="Liste des footballeurs internationaux français"),
    "football_F": dict(sport="football", sexe="F", q="Q751670",
                       cat="Footballeuse internationale française",
                       liste="Liste des joueuses de l'équipe de France féminine de football"),
    "rugby_H": dict(sport="rugby à XV", sexe="H", q="Q518116",
                    cat="Joueur international français de rugby à XV",
                    liste="Liste des sélectionnés en équipe de France de rugby à XV"),
    "rugby_F": dict(sport="rugby à XV", sexe="F", q="Q952932",
                    cat="Joueuse internationale française de rugby à XV", liste=None),
    "basket_H": dict(sport="basket-ball", sexe="H", q="Q499328",
                     cat="Joueur international français de basket-ball", liste=None),
    "basket_F": dict(sport="basket-ball", sexe="F", q="Q1342224",
                     cat="Joueuse internationale française de basket-ball", liste=None),
    "handball_H": dict(sport="handball", sexe="H", q="Q457107",
                       cat="Handballeur international français", liste=None),
    "handball_F": dict(sport="handball", sexe="F", q="Q1003357",
                       cat="Handballeuse internationale française", liste=None),
}
JO2024 = "Q114244785"  # France aux Jeux olympiques d'été de 2024

# Fédérations INJEP correspondantes
FED = {"football": "111", "rugby à XV": "133", "basket-ball": "105", "handball": "115"}


def log(*a):
    print(*a, flush=True)


def save(df: pd.DataFrame, name: str, dossier: Path = OUT):
    p = dossier / name
    df.to_csv(p, index=False, encoding="utf-8")
    log(f"[OK] {p.relative_to(ROOT)} ({len(df)} lignes)")


def normaliser(nom) -> str:
    """Strictement identique à build_onomastics_reference.py / build_showcase_elus.py."""
    if nom is None or (isinstance(nom, float) and math.isnan(nom)):
        return ""
    s = str(nom).upper().strip()
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = s.replace("'", " ").replace("’", " ")
    s = re.sub(r"\s+", " ", s)
    return s.strip()


# ---------------------------------------------------------------------------
# Accès réseau (avec pauses et reprises)
# ---------------------------------------------------------------------------
def sparql(q: str) -> list:
    for i in range(5):
        try:
            r = SESSION.post(SPARQL, data={"query": q, "format": "json"}, timeout=180)
            if r.status_code == 429 or r.status_code >= 500:
                raise RuntimeError(f"HTTP {r.status_code}")
            r.raise_for_status()
            time.sleep(1.0)
            return r.json()["results"]["bindings"]
        except Exception as e:  # noqa: BLE001
            log(f"   [INFO] SPARQL reprise {i + 1} : {e}")
            time.sleep(5 * (i + 1))
    raise RuntimeError("SPARQL en échec")


def wiki(params: dict) -> dict:
    p = dict(params, format="json", formatversion=2)
    for i in range(5):
        try:
            r = SESSION.get(WIKI, params=p, timeout=120)
            r.raise_for_status()
            time.sleep(0.3)
            return r.json()
        except Exception as e:  # noqa: BLE001
            log(f"   [INFO] Wikipédia reprise {i + 1} : {e}")
            time.sleep(5 * (i + 1))
    raise RuntimeError("Wikipédia en échec")


def val(b: dict, k: str):
    return b[k]["value"] if k in b else None


def qid(uri):
    return uri.rsplit("/", 1)[-1] if uri else None


# ---------------------------------------------------------------------------
# 1. COLLECTE
# ---------------------------------------------------------------------------
def membres_wikidata(team_q: str) -> pd.DataFrame:
    q = f"""
    SELECT ?p ?debut ?fin ?sel WHERE {{
      ?p p:P54 ?st . ?st ps:P54 wd:{team_q} .
      OPTIONAL {{ ?st pq:P580 ?debut }} OPTIONAL {{ ?st pq:P582 ?fin }}
      OPTIONAL {{ ?st pq:P1350 ?sel }}
    }}"""
    rows = [dict(qid=qid(val(b, "p")), debut=val(b, "debut"), fin=val(b, "fin"),
                 sel=val(b, "sel")) for b in sparql(q)]
    return pd.DataFrame(rows, columns=["qid", "debut", "fin", "sel"])


def titres_vers_qid(titres: list) -> dict:
    out = {}
    titres = list(dict.fromkeys(t for t in titres if t))
    for i in range(0, len(titres), 50):
        lot = titres[i:i + 50]
        r = wiki({"action": "query", "titles": "|".join(lot), "prop": "pageprops",
                  "ppprop": "wikibase_item", "redirects": 1})
        q = r.get("query", {})
        alias = {}
        for n in q.get("normalized", []):
            alias[n["from"]] = n["to"]
        for n in q.get("redirects", []):
            alias[n["from"]] = n["to"]
        par_titre = {pg["title"]: pg.get("pageprops", {}).get("wikibase_item")
                     for pg in q.get("pages", [])}
        for t in lot:
            cible = t
            for _ in range(3):
                cible = alias.get(cible, cible)
            out[t] = par_titre.get(cible)
    return out


def membres_categorie(cat: str) -> list:
    titres, cont = [], {}
    while True:
        r = wiki(dict({"action": "query", "list": "categorymembers",
                       "cmtitle": f"Catégorie:{cat}", "cmlimit": 500, "cmnamespace": 0}, **cont))
        titres += [m["title"] for m in r["query"]["categorymembers"]]
        if "continue" in r:
            cont = r["continue"]
        else:
            break
    return titres


def lignes_liste(page: str) -> pd.DataFrame:
    """Lignes des tableaux d'une liste de référence : titre lié dans la 1re
    cellule, année de 1re et dernière sélection quand elles sont lisibles."""
    from bs4 import BeautifulSoup
    r = wiki({"action": "parse", "page": page, "prop": "text"})
    soup = BeautifulSoup(r["parse"]["text"], "html.parser")
    rows = []
    for tb in soup.find_all("table", class_="wikitable"):
        trs = tb.find_all("tr")
        entete = [c.get_text(" ", strip=True) for c in trs[0].find_all(["th", "td"])] if trs else []
        for tr in trs[1:]:
            cells = tr.find_all(["td", "th"])
            if len(cells) < 4:
                continue  # intertitres (lettres)
            a = cells[0].find("a")
            titre = None
            if a is not None and a.get("title") and "redlink" not in (a.get("href") or ""):
                titre = a.get("title")
            textes = [c.get_text(" ", strip=True) for c in cells]
            annees = [re.findall(r"(18|19|20)\d\d", t) and re.search(r"((?:18|19|20)\d\d)", t).group(1)
                      for t in textes]
            # colonnes « 1re sélection » / « Premier » et « Dernière » / « Dernier »
            i1 = next((i for i, h in enumerate(entete) if re.search(r"1 ?re|Premi", h)), None)
            i2 = next((i for i, h in enumerate(entete) if re.search(r"Derni", h)), None)
            i3 = next((i for i, h in enumerate(entete) if re.search(r"^N[ée]e?s? en", h)), None)
            rows.append(dict(nom_liste=textes[0], titre=titre,
                             naissance=annees[i3] if i3 is not None and i3 < len(annees) else None,
                             premiere=annees[i1] if i1 is not None and i1 < len(annees) else None,
                             derniere=annees[i2] if i2 is not None and i2 < len(annees) else None))
    return pd.DataFrame(rows)


def details(qids: list) -> pd.DataFrame:
    rows = []
    qids = sorted(set(qids))
    for i in range(0, len(qids), 250):
        lot = " ".join(f"wd:{x}" for x in qids[i:i + 250])
        q = f"""
        SELECT ?p ?pLabel ?humain ?sexe ?naiss ?lieu ?lieuLabel ?insee ?pays ?nomfam ?nomfamLabel
               ?prenomLabel WHERE {{
          VALUES ?p {{ {lot} }}
          OPTIONAL {{ ?p wdt:P31 wd:Q5 . BIND(1 AS ?humain) }}
          OPTIONAL {{ ?p wdt:P21 ?sexe }}
          OPTIONAL {{ ?p wdt:P569 ?naiss }}
          OPTIONAL {{ ?p wdt:P19 ?lieu .
                      OPTIONAL {{ ?lieu wdt:P374 ?insee }}
                      OPTIONAL {{ ?lieu wdt:P17 ?pays }} }}
          OPTIONAL {{ ?p wdt:P734 ?nomfam }}
          OPTIONAL {{ ?p wdt:P735 ?prenom }}
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "fr,en,mul". }}
        }}"""
        for b in sparql(q):
            rows.append(dict(qid=qid(val(b, "p")), libelle=val(b, "pLabel"),
                             humain=val(b, "humain"), sexe=qid(val(b, "sexe")),
                             naissance=val(b, "naiss"), lieu=qid(val(b, "lieu")),
                             lieu_lib=val(b, "lieuLabel"), insee=val(b, "insee"),
                             pays_lieu=qid(val(b, "pays")), nomfam_q=qid(val(b, "nomfam")),
                             nomfam=val(b, "nomfamLabel"), prenom=val(b, "prenomLabel")))
        log(f"   détails {min(i + 250, len(qids))}/{len(qids)}")
    return pd.DataFrame(rows)


def departements_des_lieux(lieux: list) -> dict:
    """Département (code Insee, P2586) par remontée P131, pour les lieux sans P374."""
    out = {}
    lieux = sorted(set(x for x in lieux if x))
    for i in range(0, len(lieux), 200):
        lot = " ".join(f"wd:{x}" for x in lieux[i:i + 200])
        q = f"""
        SELECT ?l ?dep WHERE {{
          VALUES ?l {{ {lot} }}
          ?l wdt:P131* ?d . ?d wdt:P2586 ?dep .
        }}"""
        for b in sparql(q):
            out.setdefault(qid(val(b, "l")), set()).add(val(b, "dep"))
    return {k: sorted(v)[0] for k, v in out.items() if len(v) == 1}


def dep_insee(code: str):
    if not code or not isinstance(code, str):
        return None
    code = code.strip()
    if not re.fullmatch(r"(\d{5}|2[AB]\d{3})", code):
        return None
    if code.startswith("97"):
        return code[:3]
    return code[:2]


def premiere_date(s):
    if not isinstance(s, str):
        return None
    m = re.match(r"^[+-]?(\d{4})", s)
    return int(m.group(1)) if m else None


def collecte():
    log("1. Collecte des membres (Wikidata P54, catégories et listes Wikipédia)")
    src = []
    listes = {}
    for cle, e in EQUIPES.items():
        wd = membres_wikidata(e["q"])
        for r in wd.itertuples():
            src.append(dict(equipe=cle, qid=r.qid, source="wikidata_P54", debut=r.debut,
                            fin=r.fin, sel=r.sel, premiere=None, derniere=None))
        titres = membres_categorie(e["cat"])
        m = titres_vers_qid(titres)
        for t in titres:
            if m.get(t):
                src.append(dict(equipe=cle, qid=m[t], source="categorie_wp"))
        n_liste = None
        if e["liste"]:
            li = lignes_liste(e["liste"])
            n_liste = len(li)
            m2 = titres_vers_qid(li.titre.dropna().tolist())
            li["qid"] = li.titre.map(m2)
            listes[cle] = li
            for r in li.dropna(subset=["qid"]).itertuples():
                src.append(dict(equipe=cle, qid=r.qid, source="liste_wp",
                                premiere=r.premiere, derniere=r.derniere))
        log(f"   {cle} : Wikidata {wd.qid.nunique()}, catégorie {len(titres)}, "
            f"liste {n_liste if n_liste is not None else '-'}")
    # Délégation Paris 2024. Wikidata P1344 vers Q114244785 est vide, et P1344
    # vers une épreuve de 2024 ne donne que 158 Français : on part des liens de
    # l'article « France aux Jeux olympiques d'été de 2024 », filtrés sur les
    # humains dont le pays sportif (P1532) est la France (ou, à défaut de P1532,
    # la nationalité P27), nés en 1955 ou après (écarte dirigeants et anciens).
    r = wiki({"action": "parse", "page": "France aux Jeux olympiques d'été de 2024", "prop": "links"})
    liens = [x["title"] for x in r["parse"]["links"] if x.get("ns") == 0 and x.get("exists")]
    mq = sorted(set(v for v in titres_vers_qid(liens).values() if v))
    jo = []
    for i in range(0, len(mq), 300):
        lot = " ".join(f"wd:{x}" for x in mq[i:i + 300])
        q = f"""
        SELECT ?p (GROUP_CONCAT(DISTINCT ?c; separator='|') AS ?cs)
               (GROUP_CONCAT(DISTINCT ?n; separator='|') AS ?ns) (MIN(?d) AS ?dn) WHERE {{
          VALUES ?p {{ {lot} }} ?p wdt:P31 wd:Q5 .
          OPTIONAL {{ ?p wdt:P1532 ?c }} OPTIONAL {{ ?p wdt:P27 ?n }} OPTIONAL {{ ?p wdt:P569 ?d }}
        }} GROUP BY ?p"""
        for b in sparql(q):
            cs, ns = val(b, "cs") or "", val(b, "ns") or ""
            fr = ("Q142" in cs) or (not cs and "Q142" in ns)
            an = premiere_date(val(b, "dn"))
            if fr and (an is None or an >= 1955):
                jo.append(qid(val(b, "p")))
    for x in jo:
        src.append(dict(equipe="JO2024", qid=x, source="article_wp_jo2024"))
    log(f"   JO 2024 (liens de l'article, filtrés) : {len(set(jo))}")
    q = f"""SELECT (COUNT(DISTINCT ?p) AS ?n) WHERE {{ ?p wdt:P1344 ?e . ?e wdt:P361* wd:Q995653 .
            ?p wdt:P1532 wd:Q142 . ?p wdt:P31 wd:Q5 }}"""
    log(f"   pour mémoire, Wikidata P1344 (épreuves 2024, pays sportif France) : {val(sparql(q)[0], 'n')}")
    src = pd.DataFrame(src)
    save(src, "membres_sources.csv", ELITE)
    for cle, li in listes.items():
        save(li, f"liste_reference_{cle}.csv", ELITE)

    log("2. Détails des personnes (Wikidata)")
    det = details(src.qid.dropna().unique().tolist())
    save(det, "details_bruts.csv", ELITE)
    lieux_sans = det.loc[det.insee.isna() & det.lieu.notna(), "lieu"].unique().tolist()
    log(f"   lieux sans code Insee : {len(lieux_sans)} ; remontée P131 vers un département")
    depmap = departements_des_lieux(lieux_sans)
    json.dump(depmap, open(ELITE / "lieux_departement.json", "w", encoding="utf-8"))


# ---------------------------------------------------------------------------
# Construction de la table « personnes » (une ligne par personne)
# ---------------------------------------------------------------------------
def personnes() -> pd.DataFrame:
    det = pd.read_csv(ELITE / "details_bruts.csv", dtype=str)
    depmap = json.load(open(ELITE / "lieux_departement.json", encoding="utf-8"))
    det = det[det.humain == "1"]
    det["annee"] = det.naissance.map(premiere_date)

    def un(g):
        # Plusieurs valeurs possibles (deux lieux, deux dates) : on garde la
        # plus fréquente, et on signale l'ambiguïté.
        out = {}
        for c in ["libelle", "sexe", "lieu", "lieu_lib", "nomfam", "prenom"]:
            v = g[c].dropna()
            out[c] = v.mode().iloc[0] if len(v) else None
        an = g.annee.dropna()
        out["annee"] = int(an.mode().iloc[0]) if len(an) else None
        out["annee_ambigue"] = an.nunique() > 1
        lieux = g.lieu.dropna().unique()
        out["lieu_ambigu"] = len(lieux) > 1
        ins = g.loc[g.lieu == out["lieu"], "insee"].dropna()
        out["insee"] = sorted(ins.unique())[0] if len(ins) else None
        pays = g.loc[g.lieu == out["lieu"], "pays_lieu"].dropna()
        out["pays_lieu"] = pays.mode().iloc[0] if len(pays) else None
        out["prenoms"] = "|".join(sorted(g.prenom.dropna().unique()))
        return pd.Series(out)

    p = det.groupby("qid").apply(un, include_groups=False).reset_index()
    p["dep"] = p.insee.map(dep_insee)
    manque = p.dep.isna() & p.lieu.notna()
    p.loc[manque, "dep"] = p.loc[manque, "lieu"].map(depmap)
    p["sexe"] = p.sexe.map({"Q6581097": "H", "Q6581072": "F"})
    # Né en France (département connu) / hors de France
    p["ne_france"] = p.dep.notna()
    # Nom de famille : P734 si présent ; sinon libellé moins prénom(s) ; sinon dernier mot
    def nom(r):
        if isinstance(r.nomfam, str) and r.nomfam and not re.fullmatch(r"Q\d+", r.nomfam):
            return r.nomfam, "P734"
        lib = r.libelle if isinstance(r.libelle, str) else ""
        lib = re.sub(r"\s*\(.*?\)\s*", " ", lib).strip()
        for pr in sorted((r.prenoms or "").split("|"), key=len, reverse=True):
            if pr and lib.startswith(pr + " "):
                return lib[len(pr) + 1:], "libelle_moins_prenom"
        mots = lib.split()
        return (mots[-1] if mots else None), "dernier_mot"
    nn = p.apply(nom, axis=1, result_type="expand")
    p["nom"] = nn[0]
    p["nom_source"] = nn[1]
    p["nom_norm"] = p.nom.map(normaliser)
    return p


def table_membres() -> pd.DataFrame:
    src = pd.read_csv(ELITE / "membres_sources.csv", dtype=str)
    src["premiere"] = pd.to_numeric(src.premiere, errors="coerce")
    src["debut"] = src.debut.map(premiere_date)
    pers = personnes()
    m = src.groupby(["equipe", "qid"]).agg(
        sources=("source", lambda s: "|".join(sorted(set(s)))),
        premiere=("premiere", "min"), debut=("debut", "min")).reset_index()
    m = m.merge(pers, on="qid", how="inner")
    m["sexe_equipe"] = m.equipe.str.split("_").str[-1]
    # Cohérence de sexe : on écarte les personnes dont le sexe Wikidata contredit
    # l'équipe (erreurs de catégorie ou d'appartenance, en nombre infime).
    incoh = (m.equipe != "JO2024") & m.sexe.notna() & (m.sexe != m.sexe_equipe)
    log(f"   membres écartés pour incohérence de sexe : {int(incoh.sum())}")
    m = m[~incoh].copy()
    m.loc[m.equipe == "JO2024", "sexe_equipe"] = m.sexe
    m["sport"] = m.equipe.map(lambda e: EQUIPES[e]["sport"] if e in EQUIPES else "tous sports (JO 2024)")
    m["annee_selection"] = m.premiere.fillna(m.debut)
    # Quand une liste de référence existe, elle fait foi : on retire les
    # appartenances P54 ou catégories absentes de la liste (sélections B,
    # amateurs, olympiques, ou appartenances erronées), en le comptant.
    avec_liste = m.equipe.map(lambda e: bool(EQUIPES.get(e, {}).get("liste")))
    hors = avec_liste & ~m.sources.str.contains("liste_wp")
    log(f"   membres retirés car absents de la liste de référence : "
        f"{m[hors].groupby('equipe').size().to_dict()}")
    m = m[~hors].copy()
    m["lieu_statut"] = np.select(
        [m.dep.notna(), m.pays_lieu.eq("Q142"), m.lieu.notna()],
        ["département connu", "France, département inconnu", "hors de France"],
        "lieu inconnu")
    save(m, "membres.csv", ELITE)
    return m


# ---------------------------------------------------------------------------
# 2. EFFECTIFS ET COMPLÉTUDE
# ---------------------------------------------------------------------------
JO_REFERENCE = 572  # athlètes de la délégation olympique française, Paris 2024 (CNOSF)


def decennie_libelle(a):
    if pd.isna(a):
        return None
    a = int(a)
    d = (a - 1) // 10 * 10 + 1
    return f"{d}-{d + 9}"


def completude(m: pd.DataFrame):
    log("3. Effectifs et complétude")
    eff = m.groupby(["equipe", "sport", "sexe_equipe"]).agg(
        n=("qid", "nunique"),
        annee_connue=("annee", lambda s: int(s.notna().sum())),
        dep_connu=("lieu_statut", lambda s: int((s == "département connu").sum())),
        france_sans_dep=("lieu_statut", lambda s: int((s == "France, département inconnu").sum())),
        hors_france=("lieu_statut", lambda s: int((s == "hors de France").sum())),
        lieu_inconnu=("lieu_statut", lambda s: int((s == "lieu inconnu").sum())),
        nom_P734=("nom_source", lambda s: int((s == "P734").sum())),
        naissance_min=("annee", "min"), naissance_max=("annee", "max"),
    ).reset_index()
    src = pd.read_csv(ELITE / "membres_sources.csv", dtype=str)
    par_src = src.groupby(["equipe", "source"]).qid.nunique().unstack(fill_value=0)
    eff = eff.merge(par_src, left_on="equipe", right_index=True, how="left")
    ref = {"football_H": None, "football_F": None, "rugby_H": None, "JO2024": JO_REFERENCE}
    rows = []
    for cle in ["football_H", "football_F", "rugby_H"]:
        li = lignes_liste(EQUIPES[cle]["liste"])
        li["avec_article"] = li.titre.notna()
        ref[cle] = len(li)
        # couverture par décennie de 1re sélection et, si disponible, de naissance
        for col in ["premiere", "naissance"]:
            if li[col].notna().sum() == 0:
                continue
            li["dec"] = pd.to_numeric(li[col], errors="coerce").map(decennie_libelle)
            g = li.groupby("dec").agg(lignes=("avec_article", "size"),
                                      avec_article=("avec_article", "sum")).reset_index()
            for r in g.itertuples():
                rows.append(dict(equipe=cle, axe=("1re sélection" if col == "premiere" else "naissance"),
                                 decennie=r.dec, lignes_liste=r.lignes, avec_article=int(r.avec_article),
                                 couverture_pct=round(100 * r.avec_article / r.lignes, 1)))
    eff["reference"] = eff.equipe.map(ref)
    eff["source_reference"] = eff.equipe.map({
        "football_H": "Wikipédia, Liste des footballeurs internationaux français",
        "football_F": "Wikipédia, Liste des joueuses de l'équipe de France féminine de football",
        "rugby_H": "Wikipédia, Liste des sélectionnés en équipe de France de rugby à XV",
        "JO2024": "CNOSF, 572 athlètes"}).fillna("aucune liste exhaustive publique trouvée")
    # couverture calculée sur l'équipe entière (les deux sexes pour les JO)
    n_equipe = eff.groupby("equipe").n.transform("sum")
    eff["couverture_pct"] = (100 * n_equipe / eff.reference).round(1)
    save(eff, "elite_effectifs.csv")
    save(pd.DataFrame(rows), "elite_completude_listes.csv")
    log(eff[["equipe", "n", "reference", "couverture_pct", "annee_connue", "dep_connu",
             "france_sans_dep", "hors_france", "lieu_inconnu"]].to_string())
    return eff


# ---------------------------------------------------------------------------
# 3. QUESTION 1 : DIVERSITÉ DES NOMS (IDP) CONTRE LES NAISSANCES EN FRANCE
# ---------------------------------------------------------------------------
PERIODES = ["1891_1900", "1901_1910", "1911_1920", "1921_1930", "1931_1940", "1941_1950",
            "1951_1960", "1961_1970", "1971_1980", "1981_1990", "1991_2000"]
Z90 = 1.6449


def reference_idp():
    """Recalcule le drapeau IDP depuis le fichier Insee (même règle et même
    normalisation que build_onomastics_reference.py), et la part des naissances
    en France portant un nom « diversité », par période de naissance."""
    noms = pd.read_csv(NOMS_FILE, sep="\t", encoding="utf-8", dtype=str)
    cols = ["_" + p for p in PERIODES]
    for c in cols:
        noms[c] = pd.to_numeric(noms[c], errors="coerce").fillna(0).astype(np.int64)
    noms["nom_norm"] = noms.NOM.map(normaliser)
    noms = noms[noms.nom_norm != ""]
    agg = noms.groupby("nom_norm", as_index=False)[cols].sum()
    av = agg[cols[:6]].sum(axis=1)
    ap = agg[cols[6:]].sum(axis=1)
    agg["div"] = (av == 0) | ((av > 0) & (ap / av.replace(0, np.nan) > 15))
    # contrôle : identique à l'artefact du site
    tsv = ROOT / "frontend" / "public" / "data" / "onomastics" / "surnames.tsv"
    if tsv.exists():
        site = pd.read_csv(tsv, sep="\t", header=None, names=["nom_norm", "flag"], dtype=str,
                           keep_default_na=False)
        mm = agg.merge(site, on="nom_norm", how="outer", indicator=True)
        diff = ((mm._merge == "both") & (mm["div"].astype(int).astype(str) != mm.flag)).sum()
        log(f"   contrôle surnames.tsv : {len(site)} noms au site, {len(agg)} recalculés, "
            f"{int(diff)} drapeaux différents, {int((mm._merge != 'both').sum())} noms non appariés")
    ref = []
    for p, c in zip(PERIODES, cols):
        tot = agg[c].sum()
        dv = agg.loc[agg["div"], c].sum()
        ref.append(dict(periode=p.replace("_", "-"), naissances=int(tot),
                        naissances_nom_diversite=int(dv), idp_naissances=dv / tot))
    ref = pd.DataFrame(ref)
    flags = dict(zip(agg.nom_norm, agg["div"]))
    return flags, ref


def periode_naissance(a):
    if pd.isna(a):
        return None
    a = int(a)
    if a <= 1900:
        return "1891-1900"
    if a > 2000:
        return "2001 et après"
    d = (a - 1) // 10 * 10 + 1
    return f"{d}-{d + 9}"


GRANDES = {"1891-1900": "avant 1951", "1901-1910": "avant 1951", "1911-1920": "avant 1951",
           "1921-1930": "avant 1951", "1931-1940": "avant 1951", "1941-1950": "avant 1951",
           "1951-1960": "1951-1970", "1961-1970": "1951-1970",
           "1971-1980": "1971-1990", "1981-1990": "1971-1990",
           "1991-2000": "1991 et après", "2001 et après": "1991 et après"}


def wilson(k, n, z=Z90):
    if n == 0:
        return (np.nan, np.nan)
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (max(0.0, c - h), min(1.0, c + h))


def idp(m: pd.DataFrame):
    log("4. Question 1 : IDP par sport, sexe et période de naissance")
    flags, ref = reference_idp()
    save(ref, "elite_idp_reference_naissances.csv")
    refp = dict(zip(ref.periode, ref.idp_naissances))
    refp["2001 et après"] = refp["1991-2000"]  # le fichier Insee s'arrête en 2000
    m = m.copy()
    m["idp"] = m.nom_norm.map(lambda n: (1.0 if flags[n] else 0.0) if n in flags else np.nan)
    m["periode"] = m.annee.map(periode_naissance)
    m["grande_periode"] = m.periode.map(GRANDES)
    m["ref_idp"] = m.periode.map(refp)
    m["champ"] = np.where(m.lieu_statut.isin(["département connu", "France, département inconnu"]),
                          "nés en France", "autres")

    def bloc(g):
        rec = g.dropna(subset=["idp"])
        n, k = len(rec), int(rec.idp.sum())
        lo, hi = wilson(k, n)
        att = rec.ref_idp.mean() if n else np.nan  # attendu à structure de naissance égale
        var = (rec.ref_idp * (1 - rec.ref_idp)).sum()
        zc = (k - rec.ref_idp.sum()) / math.sqrt(var) if var > 0 else np.nan
        return pd.Series(dict(
            n_membres=len(g), n_reconnus=n,
            part_reconnus_pct=round(100 * n / len(g), 1) if len(g) else np.nan,
            idp_pct=round(100 * k / n, 1) if n else np.nan,
            ic90_bas=round(100 * lo, 1) if n else np.nan, ic90_haut=round(100 * hi, 1) if n else np.nan,
            idp_naissances_meme_periode_pct=round(100 * att, 1) if n else np.nan,
            ecart_points=round(100 * (k / n - att), 1) if n else np.nan,
            # rapport non calculé quand la référence est quasi nulle (avant 1951)
            rapport=round((k / n) / att, 2) if n and att >= 0.01 else np.nan,
            z=round(zc, 2) if not pd.isna(zc) else np.nan,
            # borne haute : tous les noms non reconnus comptés « diversité »
            # (les noms absents du fichier Insee sont rares : récents ou régionaux)
            idp_borne_haute_pct=round(100 * (k + len(g) - n) / len(g), 1) if len(g) else np.nan,
            publiable=n >= 30))

    out = {}
    for champ_lib, sub in [("nés en France", m[m.champ == "nés en France"]), ("tous", m)]:
        for niveau, col in [("décennie", "periode"), ("grande période", "grande_periode"), ("ensemble", None)]:
            keys = ["equipe", "sport", "sexe_equipe"] + ([col] if col else [])
            t = sub.dropna(subset=["periode"]).groupby(keys).apply(bloc, include_groups=False).reset_index()
            if col:
                t = t.rename(columns={col: "periode"})
            else:
                t["periode"] = "toutes"
            t.insert(0, "niveau", niveau)
            t.insert(0, "champ", champ_lib)
            out[(champ_lib, niveau)] = t
    tab = pd.concat(out.values(), ignore_index=True)
    # Pas de résultat sous 30 noms reconnus : on masque l'IDP mais on garde l'effectif
    for c in ["idp_pct", "ic90_bas", "ic90_haut", "ecart_points", "rapport", "z", "idp_borne_haute_pct"]:
        tab.loc[~tab.publiable, c] = np.nan
    save(tab, "elite_idp.csv")
    # Part des noms reconnus selon le lieu de naissance (diagnostic)
    diag = m.groupby(["equipe", "lieu_statut"]).agg(n=("qid", "size"),
                                                     reconnus=("idp", lambda s: int(s.notna().sum()))).reset_index()
    diag["part_reconnus_pct"] = (100 * diag.reconnus / diag.n).round(1)
    save(diag, "elite_idp_reconnaissance.csv")
    # Source du nom : part de noms reconnus selon la façon de l'obtenir
    d2 = m.groupby("nom_source").agg(n=("qid", "size"), reconnus=("idp", lambda s: int(s.notna().sum())))
    log(d2.to_string())
    show = tab[(tab.champ == "nés en France") & (tab.niveau != "décennie")]
    log(show[["equipe", "periode", "n_membres", "n_reconnus", "idp_pct", "ic90_bas", "ic90_haut",
              "idp_naissances_meme_periode_pct", "rapport", "z"]].to_string())
    return m


# ---------------------------------------------------------------------------
# 4. QUESTION 2 : DÉPARTEMENT DE NAISSANCE CONTRE BASE DE LICENCIÉS
# ---------------------------------------------------------------------------
# Départements accueillant un club de Ligue 1 ou de Ligue 2 en 2023-2024 (tous
# dotés d'un centre de formation ou en voie de l'être) : liste saisie à la main
# depuis la composition des deux championnats, faute d'accès à la liste FFF des
# centres agréés (pages fff.fr refusées au robot). Corse : 2A et 2B -> 20.
DEP_CLUB_PRO_FOOT = {
    "75", "29", "59", "06", "69", "62", "13", "51", "35", "31", "34", "67", "44", "76", "57",
    "56", "63", "89", "49", "42", "12", "14", "53", "22", "64", "38", "33", "20", "80", "74", "10",
}


def dep_code(com: str):
    if not isinstance(com, str) or len(com) < 5:
        return None
    if com.startswith("97"):
        return com[:3]
    if com[:2] in ("2A", "2B"):
        return "20"
    return com[:2]


def com_regroupee(com: str):
    if not isinstance(com, str):
        return com
    if com.startswith("751") and len(com) == 5:
        return "75056"
    if com.startswith("6938"):
        return "69123"
    if com.startswith("132") and com[3:].isdigit() and 201 <= int(com[2:]) <= 216:
        return "13055"
    return com


def licences_jeunes_2013() -> pd.DataFrame:
    """Licences 2013 des 10-19 ans par commune, fédération et sexe, et population
    2011 des 10-19 ans par commune (colonnes du même fichier)."""
    cache = ELITE.parent / "sorties" / "_elite_cache_lic2013.csv"
    if cache.exists():
        return pd.read_csv(cache, dtype={"com": str, "fed": str})
    cols = ["newcog2", "fed_2013", "l_10_14_h_2013", "l_15_19_h_2013", "l_10_14_f_2013",
            "l_15_19_f_2013", "pop_h_10_14_2011", "pop_h_15_19_2011", "pop_f_10_14_2011",
            "pop_f_15_19_2011"]
    d = pd.read_csv(DATA / "Licences_2013.csv", sep=";", dtype=str, encoding="latin-1", usecols=cols)
    for c in cols[2:]:
        d[c] = pd.to_numeric(d[c].str.replace(" ", "").str.replace(",", "."), errors="coerce").fillna(0)
    pop = d.groupby("newcog2")[cols[6:]].first()
    pop = pd.DataFrame({"pop_H": pop[cols[6]] + pop[cols[7]], "pop_F": pop[cols[8]] + pop[cols[9]]})
    d = d[d.fed_2013.isin(FED.values())]
    d = pd.DataFrame({"com": d.newcog2, "fed": d.fed_2013,
                      "lic_H": d[cols[2]] + d[cols[3]], "lic_F": d[cols[4]] + d[cols[5]]})
    d = d.groupby(["com", "fed"], as_index=False).sum()
    pop = pop.reset_index().rename(columns={"newcog2": "com"})
    pop["fed"] = "pop"
    pop = pop.rename(columns={"pop_H": "lic_H", "pop_F": "lic_F"})
    d = pd.concat([d, pop], ignore_index=True)
    d.to_csv(cache, index=False)
    return d


def licences_jeunes_2023() -> pd.DataFrame:
    cache = ELITE.parent / "sorties" / "_elite_cache_lic2023.csv"
    if cache.exists():
        return pd.read_csv(cache, dtype={"com": str, "fed": str})
    cols = ["Code Commune", "Code", "F - 10 à 14 ans", "F - 15 à 19 ans", "H - 10 à 14 ans", "H - 15 à 19 ans"]
    d = pd.read_csv(DATA / "lic-data-2023.csv", sep=";", dtype=str, encoding="utf-8-sig", usecols=cols)
    d = d[d.Code.isin(FED.values())]
    for c in cols[2:]:
        d[c] = pd.to_numeric(d[c], errors="coerce").fillna(0)
    d = pd.DataFrame({"com": d["Code Commune"], "fed": d.Code,
                      "lic_H": d[cols[4]] + d[cols[5]], "lic_F": d[cols[2]] + d[cols[3]]})
    d = d.groupby(["com", "fed"], as_index=False).sum()
    d.to_csv(cache, index=False)
    return d


def covariables_dep() -> pd.DataFrame:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from revenu_filosofi import niveaux_de_vie_medians
    rev = niveaux_de_vie_medians()["dep"]
    rv = pd.Series(rev, name="revenu_median").rename_axis("dep").reset_index()
    rv["dep"] = rv.dep.map(lambda x: "20" if x in ("2A", "2B") else x)
    rv = rv.groupby("dep", as_index=False).revenu_median.mean()
    pop = pd.read_csv(REF / "pop_dep_sexe_aq_2019_2023.csv", dtype={"dep": str})
    pop = pop[(pop.annee == 2023) & (pop.sexe == "Ensemble")]
    pop["dep"] = pop.dep.map(lambda x: "20" if x in ("2A", "2B") else x)
    pop = pop.groupby("dep", as_index=False)["pop"].sum()
    q = pd.read_excel(REF / "pop_QPV24.xlsx", header=None, skiprows=8)
    q.columns = ["qpv", "libqpv", "listeDepcom", "ListeLibDepcom", "listeEPCI2022",
                 "listeDep", "codeReg", "codeUU2020", "pop_qpv"]
    q["dep"] = q.listeDep.astype(str).str.split(",").str[0].str.strip()
    q["dep"] = q.dep.map(lambda x: "20" if x in ("2A", "2B") else x)
    q = q.groupby("dep", as_index=False).pop_qpv.sum()
    clubs = pd.read_csv(DATA / "clubs-data-2023.csv", sep=";", dtype=str, encoding="utf-8-sig",
                        usecols=["Code Commune", "Code", "Total"])
    clubs = clubs[clubs.Code.isin(FED.values())]
    clubs["dep"] = clubs["Code Commune"].map(dep_code)
    clubs["Total"] = pd.to_numeric(clubs.Total, errors="coerce").fillna(0)
    clubs = clubs.groupby(["dep", "Code"]).Total.sum().unstack(fill_value=0)
    clubs.columns = [f"clubs_{c}" for c in clubs.columns]
    cov = pop.merge(rv, on="dep", how="left").merge(q, on="dep", how="left")
    cov["pop_qpv"] = cov.pop_qpv.fillna(0)
    cov["part_qpv_pct"] = 100 * cov.pop_qpv / cov["pop"]
    cov = cov.merge(clubs.reset_index(), on="dep", how="left")
    cov["club_pro_foot"] = cov.dep.isin(DEP_CLUB_PRO_FOOT).astype(int)
    return cov


def poisson_ic(o, e, conf=0.90):
    a = (1 - conf) / 2
    lo = stats.chi2.ppf(a, 2 * o) / 2 if o > 0 else 0.0
    hi = stats.chi2.ppf(1 - a, 2 * o + 2) / 2
    return lo / e, hi / e


def poisson_p(o, e):
    p = 2 * min(stats.poisson.cdf(o, e), stats.poisson.sf(o - 1, e))
    return min(1.0, p)


def bh(p):
    p = np.asarray(p, dtype=float)
    n = len(p)
    o = np.argsort(p)
    q = np.empty(n)
    cm = 1.0
    for rang, i in reversed(list(enumerate(o, start=1))):
        cm = min(cm, p[i] * n / rang)
        q[i] = cm
    return q


def modeles(d, vars_, sport, cohorte, annee_lic, variante):
    """Facteurs associés à l'écart observé / attendu : quasi-Poisson, décalage
    log(attendus), variables centrées réduites (sauf l'indicatrice club pro)."""
    import statsmodels.api as sm
    out = []
    X = d[vars_].copy()
    for c in vars_:
        if c != "club_pro_foot":
            X[c] = (X[c] - X[c].mean()) / X[c].std()
    X = sm.add_constant(X)
    base = dict(sport=sport, cohorte=cohorte, annee_licences=annee_lic, variante=variante,
                n_dep=len(d), observes=int(d.observes.sum()))
    for c in vars_:
        r = sm.GLM(d.observes, X[["const", c]], family=sm.families.Poisson(),
                   offset=np.log(d.attendus)).fit(scale="X2")
        ci = r.conf_int(alpha=0.10).loc[c]
        out.append(dict(base, modele="une variable", variable=c,
                        rapport_par_ecart_type=round(math.exp(r.params[c]), 3),
                        ic90_bas=round(math.exp(ci[0]), 3), ic90_haut=round(math.exp(ci[1]), 3),
                        p=round(r.pvalues[c], 4), dispersion=round(r.scale, 2)))
    r = sm.GLM(d.observes, X, family=sm.families.Poisson(), offset=np.log(d.attendus)).fit(scale="X2")
    cis = r.conf_int(alpha=0.10)
    for c in vars_:
        out.append(dict(base, modele="toutes variables", variable=c,
                        rapport_par_ecart_type=round(math.exp(r.params[c]), 3),
                        ic90_bas=round(math.exp(cis.loc[c, 0]), 3), ic90_haut=round(math.exp(cis.loc[c, 1]), 3),
                        p=round(r.pvalues[c], 4), dispersion=round(r.scale, 2)))
    return out


def territoires(m: pd.DataFrame):
    import statsmodels.api as sm
    log("5. Question 2 : départements de naissance contre licenciés")
    l13 = licences_jeunes_2013()
    l13["dep"] = l13.com.map(dep_code)
    l23 = licences_jeunes_2023()
    l23["dep"] = l23.com.map(dep_code)
    cov = covariables_dep()
    m = m[m.equipe != "JO2024"].copy()
    m["dep2"] = m.dep.map(lambda x: "20" if x in ("2A", "2B") else x)
    m["com"] = m.insee.map(com_regroupee)
    lignes, facteurs = [], []
    deps = sorted(set(l13.dep.dropna()) & set(cov.dep))
    pop13 = l13[l13.fed == "pop"].groupby("dep")[["lic_H", "lic_F"]].sum()
    for sport, fed in FED.items():
        for cohorte, amin in [("nés en 1970 et après", 1970), ("nés en 1985 et après", 1985)]:
            for annee_lic, L in [(2013, l13), (2023, l23)]:
                lic = L[L.fed == fed].groupby("dep")[["lic_H", "lic_F"]].sum().reindex(deps).fillna(0)
                sub = m[(m.sport == sport) & (m.annee >= amin) & m.dep2.isin(deps)]
                obs = sub.groupby(["dep2", "sexe_equipe"]).size().unstack(fill_value=0).reindex(deps).fillna(0)
                for s in ["H", "F"]:
                    if s not in obs:
                        obs[s] = 0
                # attendu : licenciés du département x taux national, par sexe, puis somme
                att = sum(lic[f"lic_{s}"] * obs[s].sum() / lic[f"lic_{s}"].sum() for s in ["H", "F"])
                # variante : population des 10-19 ans (2011) au lieu des licenciés
                attp = sum(pop13.reindex(deps)[f"lic_{s}"] * obs[s].sum() / pop13.reindex(deps)[f"lic_{s}"].sum()
                           for s in ["H", "F"])
                o = obs["H"] + obs["F"]
                t = pd.DataFrame({"sport": sport, "cohorte": cohorte, "annee_licences": annee_lic,
                                  "dep": deps, "observes": o.values.astype(int),
                                  "observes_H": obs["H"].values.astype(int), "observes_F": obs["F"].values.astype(int),
                                  "licencies_10_19_H": lic.lic_H.values, "licencies_10_19_F": lic.lic_F.values,
                                  "attendus": att.values, "attendus_pop": attp.values})
                t = t[t.attendus > 0]
                t["rapport"] = t.observes / t.attendus
                ic = [poisson_ic(a, b) for a, b in zip(t.observes, t.attendus)]
                t["ic90_bas"] = [x[0] for x in ic]
                t["ic90_haut"] = [x[1] for x in ic]
                t["p"] = [poisson_p(a, b) for a, b in zip(t.observes, t.attendus)]
                t["q_bh"] = bh(t.p.values)
                t["rapport_pop"] = t.observes / t.attendus_pop
                t["outsider"] = np.select(
                    [(t.q_bh < 0.10) & (t.rapport > 1), (t.q_bh < 0.10) & (t.rapport < 1)],
                    ["plus que la base", "moins que la base"], "")
                disp = ((t.observes - t.attendus) ** 2 / t.attendus).sum() / (len(t) - 1)
                t["surdispersion"] = disp
                # Test corrigé de la surdispersion (quasi-Poisson, approximation normale)
                zq = (t.observes - t.attendus) / np.sqrt(max(disp, 1.0) * t.attendus)
                t["p_quasi"] = 2 * stats.norm.sf(np.abs(zq))
                t["q_quasi"] = bh(t.p_quasi.values)
                t["outsider_robuste"] = np.select(
                    [(t.q_quasi < 0.10) & (t.rapport > 1) & (t.observes >= 5),
                     (t.q_quasi < 0.10) & (t.rapport < 1) & (t.attendus >= 5)],
                    ["plus que la base", "moins que la base"], "")
                lignes.append(t)
                # Facteurs associés : quasi-Poisson, décalage log(attendus)
                d = t.merge(cov, on="dep", how="left")
                d["taux_lic_10_19"] = (d.licencies_10_19_H + d.licencies_10_19_F) / \
                    d.dep.map(pop13.sum(axis=1)) * 1000
                d["clubs_100k"] = d[f"clubs_{fed}"] / d["pop"] * 1e5
                d["log_pop"] = np.log(d["pop"])
                vars_ = ["revenu_median", "part_qpv_pct", "clubs_100k", "taux_lic_10_19", "log_pop"]
                if sport == "football":
                    vars_.append("club_pro_foot")
                d = d.dropna(subset=vars_)
                for variante, dd in [("tous départements", d),
                                     ("sans Paris ni Rhône", d[~d.dep.isin(["75", "69"])])]:
                    facteurs += modeles(dd, vars_, sport, cohorte, annee_lic, variante)
    dep = pd.concat(lignes, ignore_index=True)
    for c in ["attendus", "attendus_pop", "rapport", "ic90_bas", "ic90_haut", "rapport_pop", "surdispersion"]:
        dep[c] = dep[c].round(3)
    for c in ["p", "q_bh", "p_quasi", "q_quasi"]:
        dep[c] = dep[c].round(5)
    save(dep, "elite_departements.csv")
    fac = pd.DataFrame(facteurs)
    save(fac, "elite_facteurs.csv")

    # Seine-Saint-Denis, Paris et petite couronne (maternités voisines)
    focus = []
    for sport in FED:
        for cohorte in dep.cohorte.unique():
            for annee_lic in (2013, 2023):
                t = dep[(dep.sport == sport) & (dep.cohorte == cohorte) & (dep.annee_licences == annee_lic)]
                for lib, codes in [("Seine-Saint-Denis (93)", ["93"]), ("Paris (75)", ["75"]),
                                   ("Paris et petite couronne (75, 92, 93, 94)", ["75", "92", "93", "94"]),
                                   ("Île-de-France", ["75", "77", "78", "91", "92", "93", "94", "95"]),
                                   ("Outre-mer (971 à 974)", ["971", "972", "973", "974"])]:
                    g = t[t.dep.isin(codes)]
                    o, e, ep = int(g.observes.sum()), g.attendus.sum(), g.attendus_pop.sum()
                    lo, hi = poisson_ic(o, e)
                    disp = max(1.0, t.surdispersion.iloc[0])
                    # IC et test corrigés de la surdispersion (quasi-Poisson, échelle log)
                    se = math.sqrt(disp / o) if o > 0 else np.nan
                    qlo = (o / e) * math.exp(-Z90 * se) if o > 0 else np.nan
                    qhi = (o / e) * math.exp(Z90 * se) if o > 0 else np.nan
                    pq = 2 * stats.norm.sf(abs(o - e) / math.sqrt(disp * e))
                    focus.append(dict(sport=sport, cohorte=cohorte, annee_licences=annee_lic, zone=lib,
                                      observes=o, attendus=round(e, 1), rapport=round(o / e, 2),
                                      ic90_bas=round(lo, 2), ic90_haut=round(hi, 2),
                                      p=round(poisson_p(o, e), 5),
                                      surdispersion=round(disp, 2), ic90_quasi_bas=round(qlo, 2),
                                      ic90_quasi_haut=round(qhi, 2), p_quasi=round(pq, 4),
                                      attendus_pop=round(ep, 1), rapport_pop=round(o / ep, 2)))
    focus = pd.DataFrame(focus)
    save(focus, "elite_zones_focus.csv")

    # Quelques communes (comptes seulement, sans aucun nom) : football masculin,
    # nés en 1970 et après, communes avec au moins 5 internationaux.
    l13c = l13.copy()
    l13c["com"] = l13c.com.map(com_regroupee)
    lic_c = l13c[l13c.fed == FED["football"]].groupby("com").lic_H.sum()
    pop_c = l13c[l13c.fed == "pop"].groupby("com").lic_H.sum()
    sub = m[(m.equipe == "football_H") & (m.annee >= 1970) & m.com.notna()]
    taux = len(sub[sub.dep2.isin(deps)]) / l13[(l13.fed == FED["football"]) & l13.dep.isin(deps)].lic_H.sum()
    cc = sub.groupby("com").size().rename("observes").reset_index()
    cc = cc[cc.observes >= 5].copy()
    cc["licencies_foot_10_19_H_2013"] = cc.com.map(lic_c)
    cc["attendus"] = (cc.licencies_foot_10_19_H_2013 * taux).round(2)
    cc["rapport"] = (cc.observes / cc.attendus).round(2)
    cc["pop_H_10_19_2011"] = cc.com.map(pop_c)
    save(cc.sort_values("observes", ascending=False), "elite_communes_cas.csv")

    show = dep[(dep.cohorte == "nés en 1970 et après") & (dep.annee_licences == 2013) & (dep.outsider_robuste != "")]
    log(show[["sport", "dep", "observes", "attendus", "rapport", "ic90_bas", "ic90_haut", "q_quasi",
              "outsider_robuste"]].to_string())
    log(dep.groupby(["sport", "cohorte", "annee_licences"]).agg(
        n=("observes", "sum"), disp=("surdispersion", "first")).to_string())
    log(focus[(focus.annee_licences == 2013)].to_string())
    f2 = fac[(fac.annee_licences == 2013) & (fac.cohorte == "nés en 1970 et après") & (fac.modele == "toutes variables")]
    log(f2.to_string())
    log(cc.to_string())


# ---------------------------------------------------------------------------
# 6. FOURCHETTE DE RÉFÉRENCE : naissances en France contre génération vivant
#    en France (immigrés comptés « diversité », hypothèse maximale)
# ---------------------------------------------------------------------------
MELODI = "https://api.insee.fr/melodi/data/"
IMMI_DIR = REF / "immigres"
IMMI_XLSX = "https://www.insee.fr/fr/statistiques/fichier/2381759/demo-etran-pop-sexe-age.xlsx"
# Tranches d'âge diffusées par l'Insee pour les immigrés (RP 2023 et série 1990-2025)
TRANCHES = [("Y_LT15", 0, 14), ("Y15T24", 15, 24), ("Y25T54", 25, 54), ("Y_GE55", 55, 200)]


def melodi(ds: str, params: dict, cache: str) -> list:
    IMMI_DIR.mkdir(parents=True, exist_ok=True)
    p = IMMI_DIR / cache
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    r = SESSION.get(MELODI + ds, params=dict(params, maxResult=20000), timeout=300)
    r.raise_for_status()
    obs = r.json()["observations"]
    p.write_text(json.dumps(obs, ensure_ascii=False), encoding="utf-8")
    return obs


def parts_immigres_rp2023() -> dict:
    """Part des immigrés par tranche d'âge et sexe, France hors Mayotte, RP 2023
    (Insee, jeu DS_RP_TD_IMMI_AGESEXEMPSTA_PRINC, API Melodi)."""
    obs = melodi("DS_RP_TD_IMMI_AGESEXEMPSTA_PRINC", {"GEO": "FRANCE-F", "EMPSTA_ENQ": "_T"},
                 "rp2023_immi_age_sexe_france.json")
    v = {}
    for o in obs:
        d = o["dimensions"]
        v[(d["SEX"], d["AGE"], d["IMMI"])] = o["measures"]["OBS_VALUE_NIVEAU"]["value"]
    out = {}
    for sexe in ["F", "M", "_T"]:
        for t, _, _ in TRANCHES:
            out[(sexe, t)] = v[(sexe, t, "1")] / v[(sexe, t, "_T")]
    return out


def parts_immigres_series() -> dict:
    """Variante : part des immigrés par tranche d'âge aux recensements 1990 à 2023
    (Insee, « Population immigrée et étrangère par sexe et âge », structure par
    âge des immigrés) rapportée aux estimations de population au 1er janvier
    (Insee, DS_ESTIMATION_POPULATION, API Melodi). Deux sexes ensemble seulement."""
    p = IMMI_DIR / "demo-etran-pop-sexe-age.xlsx"
    if not p.exists():
        IMMI_DIR.mkdir(parents=True, exist_ok=True)
        r = requests.get(IMMI_XLSX, headers={"User-Agent": "Mozilla/5.0 (outsiders)"}, timeout=180)
        r.raise_for_status()
        p.write_bytes(r.content)
    x = pd.read_excel(p, header=None)
    annees = {}
    for j in range(1, x.shape[1], 2):
        lib = str(x.iat[3, j])
        m_ = re.match(r"(\d{4})", lib)
        if m_ and "(p)" not in lib:
            annees[int(m_.group(1))] = j
    lignes = {str(x.iat[i, 0]).strip(): i for i in range(x.shape[0])}
    i_nb = lignes["Nombre (en milliers)"]
    i_t = {"Y_LT15": lignes["Moins de 15 ans"],
           "Y15T24": next(v for k, v in lignes.items() if k.startswith("15 ")),
           "Y25T54": next(v for k, v in lignes.items() if k.startswith("25 ")),
           "Y_GE55": lignes["55 ans ou plus"]}
    out = {}
    for an, j in annees.items():
        obs = melodi("DS_ESTIMATION_POPULATION", {"GEO": "FRANCE-F", "TIME_PERIOD": str(an),
                                                   "EP_MEASURE": "POP_JAN_1ST", "SEX": "_T"},
                     f"estim_pop_france_{an}.json")
        pop = {}
        for o in obs:
            a = o["dimensions"]["AGE"]
            val_ = o["measures"]["OBS_VALUE_NIVEAU"]["value"]
            mm = re.fullmatch(r"Y(\d+)T(\d+)", a)
            if mm and int(mm.group(2)) - int(mm.group(1)) == 4:
                pop[int(mm.group(1))] = val_
            elif a == "Y_LT5":
                pop[0] = val_
            elif a == "Y_GE95":
                pop[95] = val_
        nb = float(x.iat[i_nb, j]) * 1000
        for t, lo, hi in TRANCHES:
            pt = sum(v for a0, v in pop.items() if lo <= a0 <= hi)
            out[(an, t)] = nb * float(x.iat[i_t[t], j]) / 100 / pt
    return out


def tranche(age):
    for t, lo, hi in TRANCHES:
        if lo <= age <= hi:
            return t
    return None


def part_cohorte_rp2023(an_naiss, sexe, parts):
    """Âge révolu au 1er janvier 2023 ; None au-delà de 72 ans (générations
    d'avant 1951), où seule la tranche ouverte « 55 ans ou plus » existe."""
    age = 2022 - int(an_naiss)
    if age > 72:
        return None
    return parts[(sexe, tranche(age))]


def part_cohorte_ado(an_naiss, parts):
    """Variante : recensement le plus proche de l'année des 17 ans ; None si
    cette année précède 1987 (premier recensement de la série : 1990)."""
    cible = int(an_naiss) + 17
    dispo = sorted(set(a for a, _ in parts))
    if cible < dispo[0] - 3:
        return None
    an = min(dispo, key=lambda a: (abs(a - cible), a))
    t = tranche(an - 1 - int(an_naiss))
    return parts[(an, t)] if t else None


def fourchette(m: pd.DataFrame):
    log("6. Fourchette de référence (naissances en France / génération avec immigrés)")
    flags, ref = reference_idp()
    refp = dict(zip(ref.periode, ref.idp_naissances))
    refp["2001 et après"] = refp["1991-2000"]
    p23 = parts_immigres_rp2023()
    pser = parts_immigres_series()
    rows = [dict(source="RP 2023", annee=2023, sexe=s, tranche=t, part_immigres_pct=round(100 * v, 2))
            for (s, t), v in p23.items()]
    rows += [dict(source="série 1990-2023", annee=a, sexe="_T", tranche=t,
                  part_immigres_pct=round(100 * v, 2)) for (a, t), v in sorted(pser.items())]
    save(pd.DataFrame(rows), "elite_idp_parts_immigres.csv")

    m = m.copy()
    m["idp"] = m.nom_norm.map(lambda n: (1.0 if flags[n] else 0.0) if n in flags else np.nan)
    m["periode"] = m.annee.map(periode_naissance)
    m["grande_periode"] = m.periode.map(GRANDES)
    m = m[m.lieu_statut.isin(["département connu", "France, département inconnu"]) & m.periode.notna()].copy()
    m["ref_basse"] = m.periode.map(refp)
    sx = m.sexe_equipe.map({"H": "M", "F": "F"}).fillna("_T")
    m["s_rp2023"] = [part_cohorte_rp2023(a, s, p23) for a, s in zip(m.annee, sx)]
    m["s_ado"] = [part_cohorte_ado(a, pser) for a in m.annee]
    m["s_rp2023"] = pd.to_numeric(m.s_rp2023)
    m["s_ado"] = pd.to_numeric(m.s_ado)
    m["ref_haute"] = m.ref_basse * (1 - m.s_rp2023) + m.s_rp2023
    m["ref_haute_ado"] = m.ref_basse * (1 - m.s_ado) + m.s_ado

    def bloc(g):
        n_tot = len(g)
        rec = g.dropna(subset=["idp"])
        n, k = len(rec), int(rec.idp.sum())
        lo, hi = wilson(k, n)
        idp_ = k / n if n else np.nan
        rb = rec.ref_basse.mean()
        rh = rec.ref_haute.mean() if rec.ref_haute.notna().all() else np.nan
        rha = rec.ref_haute_ado.mean() if rec.ref_haute_ado.notna().all() else np.nan
        s = rec.s_rp2023.mean() if rec.s_rp2023.notna().all() else np.nan
        sa = rec.s_ado.mean() if rec.s_ado.notna().all() else np.nan
        bh_ = (k + n_tot - n) / n_tot if n_tot else np.nan
        ok = n >= 30 and rb >= 0.01

        def r(a, b):
            return round(a / b, 2) if ok and not pd.isna(b) and b > 0 else np.nan
        return pd.Series(dict(
            n_membres=n_tot, n_reconnus=n,
            idp_pct=round(100 * idp_, 1) if n >= 30 else np.nan,
            ic90_bas=round(100 * lo, 1) if n >= 30 else np.nan,
            ic90_haut=round(100 * hi, 1) if n >= 30 else np.nan,
            idp_borne_haute_non_reconnus_pct=round(100 * bh_, 1) if n >= 30 else np.nan,
            part_immigres_rp2023_pct=round(100 * s, 1) if not pd.isna(s) else np.nan,
            ref_basse_naissances_pct=round(100 * rb, 1),
            ref_haute_rp2023_pct=round(100 * rh, 1) if not pd.isna(rh) else np.nan,
            rapport_haut=r(idp_, rb),
            rapport_bas=r(idp_, rh),
            rapport_bas_prudent=r(lo, rh),
            rapport_haut_ic=r(hi, rb),
            part_immigres_ado_pct=round(100 * sa, 1) if not pd.isna(sa) else np.nan,
            ref_haute_ado_pct=round(100 * rha, 1) if not pd.isna(rha) else np.nan,
            rapport_bas_ado=r(idp_, rha),
            rapport_bas_prudent_ado=r(lo, rha),
            publiable=bool(ok)))

    out = []
    for niveau, col in [("décennie", "periode"), ("grande période", "grande_periode"), ("ensemble", None)]:
        keys = ["equipe", "sport", "sexe_equipe"] + ([col] if col else [])
        t = m.groupby(keys).apply(bloc, include_groups=False).reset_index()
        t = t.rename(columns={col: "periode"}) if col else t.assign(periode="toutes")
        t.insert(0, "niveau", niveau)
        out.append(t)
    tab = pd.concat(out, ignore_index=True)
    tab = tab[tab.publiable.astype(bool)].drop(columns="publiable")
    save(tab, "elite_idp_fourchette.csv")
    log(tab[["niveau", "equipe", "periode", "n_reconnus", "idp_pct", "ic90_bas", "ic90_haut",
             "part_immigres_rp2023_pct", "ref_basse_naissances_pct", "ref_haute_rp2023_pct",
             "rapport_haut", "rapport_bas", "rapport_bas_prudent", "part_immigres_ado_pct",
             "rapport_bas_ado", "rapport_bas_prudent_ado"]].to_string())
    # parts retenues par décennie de naissance (hommes, femmes, ensemble)
    dec = []
    for d0 in range(1951, 2011, 10):
        ans = range(d0, d0 + 10)
        va = [part_cohorte_ado(a, pser) for a in ans]
        for s in ["M", "F", "_T"]:
            v = [part_cohorte_rp2023(a, s, p23) for a in ans]
            dec.append(dict(decennie=f"{d0}-{d0 + 9}", sexe=s,
                            age_en_2023=f"{2022 - d0 - 9}-{2022 - d0}",
                            part_rp2023_pct=round(100 * np.mean(v), 1) if None not in v else np.nan,
                            part_ado_pct=round(100 * np.mean(va), 1) if None not in va else np.nan))
    dec = pd.DataFrame(dec)
    save(dec, "elite_idp_parts_par_decennie.csv")
    log(dec.to_string())


if __name__ == "__main__":
    etapes = sys.argv[1:] or ["collecte", "idp", "territoires", "fourchette"]
    if "collecte" in etapes:
        collecte()
    m = table_membres()
    if "idp" in etapes or "territoires" in etapes:
        completude(m)
    if "idp" in etapes:
        idp(m)
    if "territoires" in etapes:
        territoires(m)
    if "fourchette" in etapes:
        fourchette(m)
