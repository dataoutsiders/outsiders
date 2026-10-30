# -*- coding: utf-8 -*-
"""
Dossier Assemblée : comment votent les députés ? 17e législature, open data de l'Assemblée nationale.

Sources (_cache_votes/) :
  - Scrutins.json.zip : chaque scrutin public, chaque vote nominatif, le groupe au moment du vote, la
    délégation, le demandeur du scrutin, les causes officielles de non-vote ;
  - Dossiers_Legislatifs.json.zip : le texte et sa commission saisie au fond (les sujets, sans tri manuel) ;
  - AMO30 (acteurs, mandats, organes) : dates de mandat, commissions, sexe, âge, profession.
  - Pour les scrutins sans lien vers un dossier dans le fichier officiel : `dossier_ref` de NosParlementaires
    (data.gouv.fr, Licence Ouverte).
  - Atlas (accès aux généralistes par département).

Définitions :
  - position d'un groupe sur un scrutin : pour ou contre majoritaire, si au moins 5 membres ont voté ;
  - accord entre deux groupes : part des scrutins où leurs positions sont identiques ;
  - participation : scrutins où le député a voté / scrutins tenus pendant son mandat, hors cas où il ne
    pouvait pas voter (présidence de séance, Assemblée, gouvernement) ;
  - dissidence : pour ou contre à l'opposé de la position de son groupe.

Aucun classement individuel : les résultats sont agrégés par groupe, sujet ou profil.
Limites : scrutins publics seulement (pas les votes à main levée) ; un député qui ne vote pas n'est pas
forcément absent (commissions, circonscription).
"""
import json
import pickle
import re
import unicodedata
import urllib.request
import warnings
import zipfile
from collections import Counter
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[2]
CACHE = Path(__file__).resolve().parent / "_cache_votes"
PUB = ROOT / "frontend" / "public" / "data"
OUT = PUB / "showcases" / "votes-assemblee.json"
BASE = "https://data.assemblee-nationale.fr/static/openData/repository/17/"
SOURCES = {
    "scrutins.zip": BASE + "loi/scrutins/Scrutins.json.zip",
    "dossiers.zip": BASE + "loi/dossiers_legislatifs/Dossiers_Legislatifs.json.zip",
    "acteurs.zip": BASE + "amo/tous_acteurs_mandats_organes_xi_legislature/AMO30_tous_acteurs_tous_mandats_tous_organes_historique.json.zip",
    "scrutins_an.csv": "https://nosparlementaires.fr/opendata/scrutins_an.csv",
}
SEUIL_GROUPE = 5
GROUPES = ["GDR", "LFI-NFP", "ECOS", "SOC", "LIOT", "DEM", "EPR", "HOR", "DR", "UDDPLR", "RN"]
NOMS_GROUPES = {"GDR": "GDR", "LFI-NFP": "LFI", "ECOS": "Écologistes", "SOC": "PS", "LIOT": "LIOT", "DEM": "MoDem", "EPR": "Ensemble", "HOR": "Horizons", "DR": "Droite républicaine", "UDDPLR": "UDR", "RN": "RN"}
COMMISSIONS = {"finances": "Finances, budget", "sociales": "Affaires sociales, santé", "lois": "Lois, justice, sécurité", "économiques": "Économie, agriculture, logement",
               "culturelles": "Culture, éducation", "développement durable": "Environnement, transports", "étrangères": "Affaires étrangères", "défense": "Défense"}
PERIODES = [("2024-07-01", "2024-12-31", "2e sem. 2024"), ("2025-01-01", "2025-06-30", "1er sem. 2025"), ("2025-07-01", "2025-12-31", "2e sem. 2025"),
            ("2026-01-01", "2026-06-30", "1er sem. 2026"), ("2026-07-01", "2026-12-31", "2e sem. 2026")]
CACHE.mkdir(exist_ok=True)
for nom, url in SOURCES.items():
    if not (CACHE / nom).exists():
        (CACHE / nom).write_bytes(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=280).read())


def liste(x):
    return [] if x is None else [x] if isinstance(x, dict) else x


def normalise(t):
    t = unicodedata.normalize("NFD", str(t).upper())
    return re.sub(r"[^A-Z ]", " ", "".join(c for c in t if unicodedata.category(c) != "Mn")).strip()


# ---- Acteurs, organes ---------------------------------------------------------
print("Acteurs et organes...")
za = zipfile.ZipFile(CACHE / "acteurs.zip")
organes = {}
for n in za.namelist():
    if "/organe/" in n and n.endswith(".json"):
        o = json.loads(za.read(n))["organe"]
        organes[o["uid"]] = {"type": o.get("codeType"), "abrev": o.get("libelleAbrev"), "lib": o.get("libelle")}


def theme_commission(uid):
    o = organes.get(uid) or {}
    if o.get("type") == "COMPER":
        for k, v in COMMISSIONS.items():
            if k in (o.get("lib") or "").lower():
                return v
    return "Autres commissions" if o else None


acteurs = {}
for n in za.namelist():
    if "/acteur/" not in n or not n.endswith(".json"):
        continue
    a = json.loads(za.read(n))["acteur"]
    ms = liste(a.get("mandats", {}).get("mandat"))
    an = [m for m in ms if m.get("typeOrgane") == "ASSEMBLEE" and m.get("legislature") == "17"]
    if not an:
        continue
    uid = a["uid"]["#text"] if isinstance(a["uid"], dict) else a["uid"]
    ec = a.get("etatCivil", {})
    nais = (ec.get("infoNaissance") or {}).get("dateNais")
    el = (an[-1].get("election") or {}).get("lieu") or {}
    fam = ((a.get("profession") or {}).get("socProcINSEE") or {}).get("famSocPro")
    anciens = {m.get("legislature") for m in ms if m.get("typeOrgane") == "ASSEMBLEE" and m.get("legislature") not in (None, "17")}
    acteurs[uid] = {
        "uid": uid, "nom": (ec.get("ident") or {}).get("nom"), "prenom": (ec.get("ident") or {}).get("prenom"), "femme": (ec.get("ident") or {}).get("civ") == "Mme", "nais": nais[:4] if isinstance(nais, str) else None, "fam": fam if isinstance(fam, str) else None,
        "dep": el.get("numDepartement"), "regtype": el.get("regionType"), "nouveau": len(anciens) == 0,
        "mandats": [(m.get("dateDebut"), m.get("dateFin") or "2099-12-31") for m in an],
        "groupes": [(m.get("dateDebut"), m.get("dateFin") or "2099-12-31", (m.get("organes") or {}).get("organeRef")) for m in ms if m.get("typeOrgane") == "GP" and m.get("legislature") == "17"],
        "commissions": [(m.get("dateDebut"), m.get("dateFin") or "2099-12-31", theme_commission((m.get("organes") or {}).get("organeRef"))) for m in ms if m.get("typeOrgane") == "COMPER" and m.get("legislature") == "17"],
    }
print(f"   {len(acteurs)} députés de la 17e législature")
UIDS = sorted(acteurs)
POS = {u: i for i, u in enumerate(UIDS)}

# ---- Dossiers : titre et commission au fond ------------------------------------
print("Dossiers législatifs...")
zd = zipfile.ZipFile(CACHE / "dossiers.zip")


def actes(a, out):
    if isinstance(a, dict):
        if a.get("codeActe") == "AN1-COM-FOND" or (a.get("codeActe") or "").endswith("-COM-FOND"):
            out.append(a.get("organeRef"))
        for v in a.values():
            actes(v, out)
    elif isinstance(a, list):
        for v in a:
            actes(v, out)
    return out


dossiers = {}
for n in zd.namelist():
    if "dossierParlementaire" in n and n.endswith(".json"):
        x = json.loads(zd.read(n))["dossierParlementaire"]
        coms = [c for c in actes(x.get("actesLegislatifs"), []) if c]
        an_coms = [c for c in coms if (organes.get(c) or {}).get("type") in ("COMPER", "COMNL", "COMSPSENAT")]
        dossiers[x["uid"]] = {"titre": (x.get("titreDossier") or {}).get("titre"), "commission": theme_commission(an_coms[0]) if an_coms else None}
print(f"   {len(dossiers)} dossiers")

# ---- Scrutins ------------------------------------------------------------------
PKL = CACHE / "scrutins.pkl"
if PKL.exists():
    S, V, D, G = pickle.loads(PKL.read_bytes())
else:
    print("Lecture des scrutins (une fois)...")
    zs = zipfile.ZipFile(CACHE / "scrutins.zip")
    noms = [n for n in zs.namelist() if n.endswith(".json")]
    np_ref = pd.read_csv(CACHE / "scrutins_an.csv", dtype=str).set_index("id").dossier_ref.to_dict()
    S = []
    V = np.zeros((len(UIDS), len(noms)), dtype=np.int8)   # 1 pour, 2 contre, 3 abstention, 4 ne pouvait pas voter, 5 autre non-vote
    D = np.zeros((len(UIDS), len(noms)), dtype=bool)      # vote par délégation
    G = np.full((len(UIDS), len(noms)), -1, dtype=np.int16)  # indice du groupe au moment du vote
    org_ids = {}
    for j, n in enumerate(sorted(noms, key=lambda x: int(re.search(r"V(\d+)", x).group(1)))):
        s = json.loads(zs.read(n))["scrutin"]
        o = s.get("objet") or {}
        dl = o.get("dossierLegislatif") or {}
        ref = dl.get("dossierRef") if isinstance(dl, dict) else None
        S.append({"id": s["uid"], "numero": int(s["numero"]), "date": s["dateScrutin"], "type": s["typeVote"]["codeTypeVote"], "sort": (s.get("sort") or {}).get("code"), "titre": s.get("titre"),
                  "demandeur": (s.get("demandeur") or {}).get("texte"), "ref": ref or np_ref.get(s["uid"])})
        for g in liste(s["ventilationVotes"]["organe"]["groupes"].get("groupe")):
            gi = org_ids.setdefault(g["organeRef"], len(org_ids))
            dn = g["vote"]["decompteNominatif"]
            for cle, code in (("pours", 1), ("contres", 2), ("abstentions", 3), ("nonVotants", 5)):
                b = dn.get(cle)
                for v in liste(b.get("votant") if isinstance(b, dict) else b):
                    i = POS.get(v.get("acteurRef"))
                    if i is None:
                        continue
                    c = code
                    if code == 5 and v.get("causePositionVote") in ("MG", "PAN", "PSE"):
                        c = 4
                    V[i, j], G[i, j] = c, gi
                    D[i, j] = v.get("parDelegation") == "true"
    S = pd.DataFrame(S)
    S.attrs["org_ids"] = org_ids
    PKL.write_bytes(pickle.dumps((S, V, D, G)))
org_ids = S.attrs["org_ids"]
ABREV = {i: (organes.get(o) or {}).get("abrev") or o for o, i in org_ids.items()}
print(f"{len(S)} scrutins, {(V > 0).sum()} lignes de vote ; groupes :", Counter(ABREV.values()))
S["dt"] = pd.to_datetime(S.date)
S["dossier"] = S.ref.map(lambda r: (dossiers.get(r) or {}).get("titre"))
S["theme"] = S.ref.map(lambda r: (dossiers.get(r) or {}).get("commission"))
S.loc[S.type == "MOC", "theme"] = "Motions de censure"
print("couverture dossier", round(S.dossier.notna().mean() * 100, 1), "% ; thème", round(S.theme.notna().mean() * 100, 1), "%")
print(S.theme.value_counts(dropna=False).to_dict())
print("par délégation", round(D.sum() / ((V > 0) & (V < 4)).sum() * 100, 1), "%")
print("demandeurs", S.demandeur.fillna("").str.replace(r"Président(e)? du groupe ", "", regex=True).str.slice(0, 40).value_counts().head(14).to_dict())
t = S.dossier.fillna("")
print(t[t.str.contains("soins|médecin|santé|hôpital|territoire", case=False)].value_counts().head(24).to_dict())
ind = S.titre.fillna("").str.contains("désert|installation des médecins|offre de soins|accès aux soins", case=False)
print("titres soins", ind.sum(), S[ind].dossier.value_counts().head(8).to_dict())

# ---- Tableaux de base ---------------------------------------------------------
print("\nAnalyse...")
ABREV2 = {i: {"UDR": "UDDPLR"}.get(a, a) for i, a in ABREV.items()}
carte = np.full(max(ABREV2) + 2, -1, dtype=np.int16)
for i, a in ABREV2.items():
    if a in GROUPES:
        carte[i] = GROUPES.index(a)
GM = carte[G]
GM[G < 0] = -1
nS = len(S)
pour = np.stack([((V == 1) & (GM == g)).sum(0) for g in range(len(GROUPES))])
contre = np.stack([((V == 2) & (GM == g)).sum(0) for g in range(len(GROUPES))])
abst = np.stack([((V == 3) & (GM == g)).sum(0) for g in range(len(GROUPES))])
tot = pour + contre + abst
POSI = np.where((tot >= SEUIL_GROUPE) & (pour != contre), np.sign(pour - contre), 0)


def accord(masque):
    A = np.full((len(GROUPES), len(GROUPES)), np.nan)
    for a in range(len(GROUPES)):
        for b in range(len(GROUPES)):
            if a != b:
                ok = masque & (POSI[a] != 0) & (POSI[b] != 0)
                if ok.sum() >= 15:
                    A[a, b] = (POSI[a][ok] == POSI[b][ok]).mean() * 100
    return A


def liste_matrice(A):
    return [[None if np.isnan(x) else int(round(x)) for x in l] for l in A]


tous = np.ones(nS, dtype=bool)
A_all = accord(tous)
print(pd.DataFrame(A_all, index=GROUPES, columns=GROUPES).round(0).to_string())
THEMES = list(COMMISSIONS.values())
par_theme = {}
for t in THEMES:
    m = (S.theme == t).values
    par_theme[t] = {"n": int(m.sum()), "matrice": liste_matrice(accord(m))}
ix = GROUPES.index
PAIRES = [("EPR", "DR"), ("DR", "RN"), ("EPR", "RN"), ("EPR", "SOC"), ("LFI-NFP", "SOC"), ("LFI-NFP", "RN")]
print(pd.DataFrame({f"{a}-{b}": {t: par_theme[t]["matrice"][ix(a)][ix(b)] for t in THEMES} for a, b in PAIRES}).to_string())
evol = []
for deb, fin, lab in PERIODES:
    m = ((S.date >= deb) & (S.date <= fin)).values
    A = accord(m)
    evol.append({"periode": lab, "n": int(m.sum()), "paires": {f"{a}|{b}": None if np.isnan(A[ix(a), ix(b)]) else int(round(A[ix(a), ix(b)])) for a, b in PAIRES}})
print(evol)
# Textes où les deux oppositions se retrouvent le plus souvent (au moins 15 scrutins communs).
dossiers_ac = []
for titre in S.dossier.dropna().unique():
    m = S.dossier.eq(titre).values
    ok = m & (POSI[ix("LFI-NFP")] != 0) & (POSI[ix("RN")] != 0)
    if ok.sum() >= 15:
        dossiers_ac.append({"titre": titre, "n": int(ok.sum()), "lfi_rn": int(round((POSI[ix("LFI-NFP")][ok] == POSI[ix("RN")][ok]).mean() * 100))})
dossiers_ac.sort(key=lambda d: -d["lfi_rn"])
print(dossiers_ac[:8], len(dossiers_ac))
# Cohésion et dissidence
rice = {GROUPES[g]: round(float((np.abs(pour[g] - contre[g])[tot[g] >= SEUIL_GROUPE] / tot[g][tot[g] >= SEUIL_GROUPE]).mean()) * 100, 1) for g in range(len(GROUPES))}
dissid_n = np.zeros(len(UIDS))
exprimes = np.zeros(len(UIDS))
for g in range(len(GROUPES)):
    p = POSI[g]
    fait = ((V == 1) | (V == 2)) & (GM == g) & (p != 0)[None, :]
    contraire = ((V == 1) & (p == -1)[None, :]) | ((V == 2) & (p == 1)[None, :])
    dissid_n += (fait & contraire).sum(1)
    exprimes += fait.sum(1)
print("Cohésion", rice)
# Demandeurs des scrutins
DEM = {"RN": "Rassemblement National", "LFI-NFP": "La France insoumise", "EPR": "Ensemble pour la République", "DR": "Droite Républicaine", "SOC": "Socialistes", "ECOS": "Écologiste",
       "HOR": "Horizons", "UDDPLR": "UDR|Union des droites", "LIOT": "Libertés, Indépendants", "DEM": "Démocrate", "GDR": "Gauche Démocrate"}
dem_txt = S.demandeur.fillna("")
demandes = {g: int(dem_txt.str.contains(m, regex=True).sum()) for g, m in DEM.items()}
demandes["seance"] = int(dem_txt.str.contains("de séance").sum())
print("Demandes", demandes)

# ---- Participation ------------------------------------------------------------
dates = S.date.values
E = np.zeros(V.shape, dtype=bool)
for u, i in POS.items():
    for deb, fin in acteurs[u]["mandats"]:
        E[i] |= (dates >= (deb or "0")) & (dates <= (fin or "9"))
E &= V != 4
vote = (V >= 1) & (V <= 3) & E
pers = vote & ~D
A_ = pd.DataFrame({"uid": UIDS})
A_["elig"] = E.sum(1)
A_["votes"] = vote.sum(1)
A_["person"] = pers.sum(1)
A_["part"] = A_.votes / A_.elig.replace(0, np.nan) * 100
A_["part_person"] = A_.person / A_.elig.replace(0, np.nan) * 100
A_["deleg"] = (A_.votes - A_.person) / A_.votes.replace(0, np.nan) * 100
A_["dissid"] = dissid_n / np.where(exprimes > 0, exprimes, np.nan) * 100
cnt = np.stack([(GM == g).sum(1) for g in range(len(GROUPES))])
A_["gp"] = [GROUPES[c.argmax()] if c.max() > 0 else None for c in cnt.T]
for k in ("femme", "fam", "dep", "regtype", "nouveau"):
    A_[k] = [acteurs[u][k] for u in UIDS]
A_["age"] = [date.today().year - int(acteurs[u]["nais"]) if acteurs[u]["nais"] else np.nan for u in UIDS]
A_["agec"] = pd.cut(A_.age, [0, 44, 59, 120], labels=["Moins de 45 ans", "45-59 ans", "60 ans et plus"]).astype(str)
A_["pcs"] = A_.fam.fillna("").str.extract(r"^(Agric|Artisans|Cadres|Professions inter|Employ|Ouvriers|Retrait|Sans|Autres)", expand=False).map(
    {"Cadres": "Cadres", "Professions inter": "Professions intermédiaires", "Employ": "Employés", "Ouvriers": "Ouvriers", "Artisans": "Artisans, commerçants", "Agric": "Agriculteurs"}).fillna("Autres")
A_["om"] = A_.dep.fillna("").str.match(r"^(97|98|ZA|ZB|ZC|ZD|ZM|ZN|ZP|ZS|ZW|ZX)")
print("Outre-mer", int(A_.om.sum()), Counter(A_.regtype.fillna("?")), [d for d in A_.dep.dropna().unique() if not d[:2].isdigit() or len(d) > 2][:16])
B = A_[(A_.elig >= 500) & A_.gp.notna()].copy()
print(f"{len(B)} députés avec au moins 500 scrutins pendant leur mandat ; participation médiane {B.part.median():.1f} %, en personne {B.part_person.median():.1f} %")


def agg(v):
    return B.groupby(v).agg(n=("part", "size"), part=("part", "median"), person=("part_person", "median"), deleg=("deleg", "median"), dissid=("dissid", "median")).round(1).reset_index().rename(columns={v: "label"})


for v in ("gp", "femme", "agec", "pcs", "om", "nouveau"):
    print(agg(v).to_string(index=False))
masques = {"Scrutins ordinaires": (S.type == "SPO").values, "Scrutins solennels": (S.type == "SPS").values, "Motions de censure": (S.type == "MOC").values}
par_type = {k: round(float(vote[:, m].sum() / E[:, m].sum() * 100), 1) for k, m in masques.items()}
print("par type", par_type)
# Sa commission ou une autre : même député, deux taux.
theme_arr = S.theme.values
propres, autres = [], []
for u, i in POS.items():
    m_prop = np.zeros(nS, dtype=bool)
    for deb, fin, th in acteurs[u]["commissions"]:
        if th in THEMES:
            m_prop |= (dates >= (deb or "0")) & (dates <= (fin or "9")) & (theme_arr == th)
    m_aut = np.isin(theme_arr, THEMES) & ~m_prop
    a, b = (E[i] & m_prop).sum(), (E[i] & m_aut).sum()
    if a >= 50 and b >= 50:
        propres.append(vote[i][E[i] & m_prop].mean() * 100)
        autres.append(vote[i][E[i] & m_aut].mean() * 100)
commission = {"sa_commission": round(float(np.median(propres)), 1), "autres": round(float(np.median(autres)), 1), "n": len(propres)}
print("commission", commission)

import statsmodels.formula.api as smf


def net(y, df, rhs="C(gp)+femme+age+nouveau+om+C(pcs, Treatment('Cadres'))"):
    d = df.dropna(subset=[y, "age"]).copy()
    d["femme"] = d.femme.astype(float)
    d["nouveau"] = d.nouveau.astype(float)
    d["om"] = d.om.astype(float)
    r = smf.ols(f"{y} ~ {rhs}", d).fit(cov_type="HC1")
    return {k: {"b": round(float(r.params[k]), 2), "ic": round(float(1.96 * r.bse[k]), 2)} for k in r.params.index if not k.startswith("C(gp)") and k != "Intercept"}, int(r.nobs)


print("Participation à groupe égal", net("part", B))
print("Dissidence à groupe égal", net("dissid", B))

# ---- Positions ----------------------------------------------------------------
tv = ((V == 1) | (V == 2) | (V == 3)).sum(0)
cn = (V == 1).sum(0), (V == 2).sum(0)
keep = (tv >= 100) & (np.minimum(*cn) >= 0.1 * (cn[0] + cn[1]))
M_ = np.where(V == 1, 1.0, np.where(V == 2, -1.0, 0.0))[:, keep]
dep_ok = ((V == 1) | (V == 2))[:, keep].sum(1) >= 300
U, Sg, Vt = np.linalg.svd(M_[dep_ok] - M_[dep_ok].mean(axis=0), full_matrices=False)
ax = pd.DataFrame(U[:, :2] * Sg[:2], columns=["a1", "a2"], index=A_.index[dep_ok])
ax["gp"] = A_.gp[dep_ok]
if ax[ax.gp == "RN"].a1.mean() < 0:
    ax["a1"] *= -1
if ax[ax.gp == "RN"].a2.mean() < ax[ax.gp == "EPR"].a2.mean():
    ax["a2"] *= -1
inertie = np.round(Sg[:4] ** 2 / (Sg ** 2).sum() * 100, 1)
print("axes", inertie, keep.sum(), dep_ok.sum())
print(ax.groupby("gp")[["a1", "a2"]].mean().round(0).reindex(GROUPES).T.to_string())
A_["a1"], A_["a2"] = ax.a1, ax.a2
B["a1"], B["a2"] = ax.a1, ax.a2
B["ecart_axe"] = B.a1 - B.groupby("gp").a1.transform("mean")
print("Écart à son groupe sur l'axe gauche-droite", net("ecart_axe", B))

# ---- Profil : à groupe égal, comparé au hasard ----------------------------------
rng = np.random.default_rng(7)
A_idx = A_[A_.gp.notna()]


def divergence(lab):
    """Part des scrutins où deux sous-groupes d'un même groupe ont des positions opposées."""
    dif, n = 0, 0
    for g in GROUPES:
        idx = A_idx.index[(A_idx.gp == g).values & lab.notna().values]
        a = idx[(lab.loc[idx] == True).values]
        b = idx[(lab.loc[idx] == False).values]
        if len(a) < 8 or len(b) < 8:
            continue
        pa, ca = (V[a] == 1).sum(0), (V[a] == 2).sum(0)
        pb, cb = (V[b] == 1).sum(0), (V[b] == 2).sum(0)
        ok = (pa + ca >= 5) & (pb + cb >= 5) & (pa != ca) & (pb != cb)
        dif += (np.sign(pa - ca)[ok] != np.sign(pb - cb)[ok]).sum()
        n += ok.sum()
    return dif / n * 100 if n else np.nan, int(n)


def hasard(lab, tours=200):
    out = []
    for _ in range(tours):
        l2 = lab.copy()
        for g in GROUPES:
            ix_ = A_idx.index[(A_idx.gp == g).values & lab.notna().values]
            l2.loc[ix_] = rng.permutation(lab.loc[ix_].values)
        out.append(divergence(l2)[0])
    return float(np.mean(out)), float(np.percentile(out, 2.5)), float(np.percentile(out, 97.5))


profil = []
for nom, lab in [("Femmes et hommes", A_idx.femme.astype(object)), ("Moins de 50 ans et 50 ans et plus", (A_idx.age < 50).where(A_idx.age.notna()).astype(object)),
                 ("Nouveaux élus et anciens", A_idx.nouveau.astype(object)), ("Cadres et autres professions", (A_idx.pcs == "Cadres").astype(object))]:
    v_, n_ = divergence(lab)
    m_, b_, h_ = hasard(lab)
    profil.append({"label": nom, "observe": round(v_, 1), "hasard": round(m_, 1), "bas": round(b_, 1), "haut": round(h_, 1), "n": n_})
    print(profil[-1])

# ---- Territoire : les déserts médicaux -------------------------------------------
atlas = {d["code"]: d.get("apl_mg") for d in json.loads((PUB / "atlas" / "departements.json").read_text(encoding="utf-8"))}
A_["depc"] = A_.dep.fillna("").map(lambda d: d.zfill(2) if len(d) < 2 else d)
A_["apl"] = A_.depc.map(atlas)
dm = S[S.dossier.fillna("").str.contains("déserts médicaux", case=False)]
print("scrutins déserts médicaux", len(dm), "APL renseigné", round(A_.apl.notna().mean() * 100))

# Test sur le texte qui parle le plus directement du territoire : vote et participation selon l'accès aux soins du département.
M_DM = S.dossier.fillna("").str.contains("déserts médicaux", case=False).values
CIBLES_DM = {"VTANR5L17V1214": "Article 1 rétabli (régulation de l'installation)", "VTANR5L17V1607": "Ensemble de la proposition de loi"}
territoire = {"scrutins": int(M_DM.sum()), "votes": []}
A_["apl_z"] = (A_.apl - A_.apl.mean()) / A_.apl.std()
A_["apl_bas"] = A_.apl <= 2.5
A_["tier"] = pd.qcut(A_.apl, 3, labels=["Accès le plus faible", "Accès moyen", "Accès le plus élevé"])
for sid, lab in CIBLES_DM.items():
    j = S.index[S.id == sid][0]
    x = A_.assign(v=V[:, j], g2=[GROUPES[k] if k >= 0 else None for k in GM[:, j]])
    x = x[x.v.isin([1, 2]) & x.g2.notna() & x.apl_z.notna()].copy()
    x["pour"] = (x.v == 1) * 100.0
    r = smf.ols("pour ~ C(g2)+apl_z", x).fit(cov_type="HC1")
    tiers = x.groupby("tier").pour.agg(["mean", "size"]).round(1)
    territoire["votes"].append({"label": lab, "n": int(len(x)), "b": round(float(r.params["apl_z"]), 1), "ic": round(float(1.96 * r.bse["apl_z"]), 1), "pour": round(float(x.pour.mean()), 1),
                                "tiers": [{"label": str(k), "pour": float(v["mean"]), "n": int(v["size"])} for k, v in tiers.iterrows()]})
    print(lab, territoire["votes"][-1], x.groupby("g2").pour.agg(["mean", "size"]).round(0).to_dict("index"))
A_["part_dm"] = vote[:, M_DM].sum(1) / np.where(E[:, M_DM].sum(1) > 0, E[:, M_DM].sum(1), np.nan) * 100
A_["part_aff"] = vote[:, (S.theme == "Affaires sociales, santé").values].sum(1) / np.where(E[:, (S.theme == "Affaires sociales, santé").values].sum(1) > 0, E[:, (S.theme == "Affaires sociales, santé").values].sum(1), np.nan) * 100
Tz = A_[A_.gp.notna() & A_.apl_z.notna() & (A_.elig >= 500)]
for y in ("part_dm", "part_aff"):
    r = smf.ols(f"{y} ~ C(gp)+apl_z", Tz.dropna(subset=[y])).fit(cov_type="HC1")
    territoire[y] = {"b": round(float(r.params["apl_z"]), 1), "ic": round(float(1.96 * r.bse["apl_z"]), 1), "n": int(r.nobs), "moyenne": round(float(Tz[y].mean()), 1)}
print(territoire["part_dm"], territoire["part_aff"], "médiane APL", A_.apl.median())

# Amendements : groupe de l'auteur au moment du scrutin, résultat officiel.
noms_dep = {}
for u in UIDS:
    noms_dep.setdefault(normalise(acteurs[u]["nom"]), []).append(u)
    noms_dep.setdefault(normalise(f'{acteurs[u]["prenom"]} {acteurs[u]["nom"]}'), []).append(u)
am = S[S.titre.fillna("").str.match(r"^l.amendement")].copy()


def auteur_groupe(r):
    m = re.search(r"de (?:M\.|Mme) ([^,]+?)(?= et l.amendement| et | à l.article| à l.|  | après | avant | de suppression| rétablissant|$)", r.titre)
    if not m:
        return None
    u = noms_dep.get(normalise(m.group(1)))
    if not u or len(set(u)) != 1:
        return None
    for deb, fin, org in acteurs[u[0]]["groupes"]:
        if (deb or "0") <= r.date <= (fin or "9"):
            a = (organes.get(org) or {}).get("abrev")
            return {"UDR": "UDDPLR"}.get(a, a)
    return None


am["gp"] = [auteur_groupe(r) for r in am.itertuples()]
print("amendements", len(am), "auteur retrouvé", round(am.gp.notna().mean() * 100, 1))
adoptes = am.groupby("gp")["sort"].agg(lambda s: (s == "adopté").mean() * 100)
n_am = am.groupby("gp").size()
print(adoptes.round(1).reindex(GROUPES).to_dict(), n_am.reindex(GROUPES).to_dict())

# ---- Sortie ---------------------------------------------------------------------
tab = agg("gp").set_index("label")
groupes_sortie = []
for g in GROUPES:
    groupes_sortie.append({"id": g, "nom": NOMS_GROUPES[g], "n": int(tab.n[g]), "participation": float(tab.part[g]), "en_personne": float(tab.person[g]), "dissidence": float(tab.dissid[g]), "cohesion": rice[g],
                           "demandes": demandes[g], "amendements": round(float(adoptes.get(g, np.nan)), 1), "n_amendements": int(n_am.get(g, 0))})


def lignes(v, seuil=30):
    t_ = agg(v)
    return [{"label": str(r.label), "n": int(r.n), "participation": float(r.part), "en_personne": float(r.person), "dissidence": float(r.dissid)} for r in t_.itertuples() if r.n >= seuil]


neto, n_net = net("part", B)
netd, _ = net("dissid", B)
points = ax.dropna(subset=["gp"]).sample(frac=1, random_state=3)
sortie = {
    "n_scrutins": nS, "n_votes": int(((V >= 1) & (V <= 3)).sum()), "debut": S.date.min(), "fin": S.date.max(), "groupes_ordre": GROUPES, "noms": NOMS_GROUPES,
    "matrice": liste_matrice(A_all), "themes": par_theme, "paires": [[a, b] for a, b in PAIRES], "evolution": evol, "convergences": dossiers_ac[:6],
    "axes": {"inertie": [float(inertie[0]), float(inertie[1])], "points": [[round(float(r.a1), 1), round(float(r.a2), 1), r.gp] for r in points.itertuples()],
             "centres": {g: [round(float(ax[ax.gp == g].a1.mean()), 1), round(float(ax[ax.gp == g].a2.mean()), 1)] for g in GROUPES}},
    "groupes": groupes_sortie, "scrutins_seance": demandes["seance"], "part_delegation": round(float(D.sum() / ((V > 0) & (V < 4)).sum() * 100), 1),
    "participation": {"mediane": round(float(B.part.median()), 1), "en_personne": round(float(B.part_person.median()), 1), "n": len(B), "types": par_type, "commission": commission,
                      "femmes": lignes("femme"), "ages": lignes("agec"), "professions": lignes("pcs"), "outre_mer": lignes("om", 20), "anciennete": lignes("nouveau"),
                      "net_femme": neto["femme"], "net_age_10ans": {"b": round(neto["age"]["b"] * 10, 1), "ic": round(neto["age"]["ic"] * 10, 1)}, "net_nouveau": neto["nouveau"], "net_outre_mer": neto["om"]},
    "profil": [{k: (float(v) if isinstance(v, (np.floating, float)) else v) for k, v in p.items()} for p in profil],
    "dissidence_net": {"femme": netd["femme"], "nouveau": netd["nouveau"], "outre_mer": netd["om"]},
    "territoire": territoire, "themes_noms": THEMES,
}
OUT.write_text(json.dumps(sortie, ensure_ascii=False, separators=(",", ":"), default=float), encoding="utf-8")
print(f"-> {OUT.name} ({OUT.stat().st_size // 1024} Ko)")
