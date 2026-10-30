# -*- coding: utf-8 -*-
"""
Atlas - accès aux soins.

Accessibilité potentielle localisée (APL, Drees, millésime 2024, onglet « APL 2024 » de chaque
fichier) : généralistes, chirurgiens-dentistes, kinésithérapeutes, infirmières, sages-femmes, par
commune et arrondissement municipal. Comme le demande la note des fichiers, un APL agrégé
(Paris, Lyon, Marseille entiers, EPCI, département) est la moyenne des APL communaux pondérée par
la population standardisée de la profession.

  apl_mg_60 = part de l'APL aux généralistes qui disparaît si l'on retire les médecins de plus de
              60 ans = (APL - APL des 60 ans ou moins) / APL

Dépassements d'honoraires (Assurance maladie, data.ameli.fr, département) : médecins spécialistes,
hors généralistes, année ANNEE_HONO.

  depassement_spe = dépassements / honoraires sans dépassement * 100
  secteur2_spe    = spécialistes de secteur 2 (Optam ou non) / spécialistes de tous secteurs * 100

Ces deux indicateurs n'existent qu'au département : pas de valeur communale ni EPCI.

Émet aussi _cache_sante/numerateurs-departements.json (numérateurs et dénominateurs par département),
repris par build_territoires_echelles.py pour calculer les régions avec la même définition.
Relancer build_territoires_echelles.py puis build_territoires_index.py ensuite.
"""
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path
import pandas as pd
from rp2023 import UA

H = UA
ROOT = Path(__file__).resolve().parents[2]
ATLAS = ROOT / "frontend" / "public" / "data" / "atlas"
COMMUNES = ATLAS / "communes"
EPCI_MAP = ROOT / "python" / "data" / "municipales" / "communes-epci.json"
CACHE = Path(__file__).resolve().parent / "_cache_sante"
NUMERATEURS = CACHE / "numerateurs-departements.json"

DREES = ("https://data.drees.solidarites-sante.gouv.fr/api/explore/v2.1/catalog/datasets/"
         "530_l-accessibilite-potentielle-localisee-apl/attachments/")
ONGLET = "APL 2024"
# clé atlas -> (pièce jointe Drees, nombre de décimales)
APL = {
    "apl_mg": ("indicateur_d_apl_aux_medecins_generalistes_xlsx", 2),
    "apl_dentistes": ("indicateur_d_apl_aux_chirurgiens_dentistes_xlsx", 1),
    "apl_kines": ("indicateur_d_apl_aux_kinesitherapeutes_xlsx", 1),
    "apl_infirmieres": ("indicateur_d_apl_aux_infirmiers_xlsx", 1),
    "apl_sages_femmes": ("indicateur_d_apl_aux_sages_femmes_xlsx", 1),
}
SEUIL_MG = 2.5  # commune sous-dotée en généralistes (Insee Analyses Auvergne-Rhône-Alpes n° 187)

AMELI = "https://data.ameli.fr/api/explore/v2.1/catalog/datasets/"
ANNEE_HONO = "2025"
SPECIALISTES = "Ensemble des médecins spécialistes (hors généralistes)"

CODE = re.compile(r"^\d[\dAB]\d{3}$")


def fetch(url, tries=4, timeout=300):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=timeout) as r:
                return r.read()
        except Exception as e:
            print("   retry", i + 1, e)
            time.sleep(3)
    raise RuntimeError(url)


def dep_of(c):
    c = str(c)
    return c[:3] if c[:2] in ("97", "98") else c[:2]


def commune_of(c):
    """Paris, Lyon, Marseille entiers pour un arrondissement municipal, sinon la commune."""
    if c.startswith("751"):
        return "75056"
    if c.startswith("6938"):
        return "69123"
    if c.startswith("132"):
        return "13055"
    return c


def lire_apl(cle, piece):
    """Une ligne par commune : apl, population standardisée, population (+ APL des 60 ans ou moins)."""
    fichier = CACHE / f"{piece}.xlsx"
    if not fichier.exists():
        fichier.write_bytes(fetch(DREES + piece))
    brut = pd.read_excel(fichier, sheet_name=ONGLET, header=None, dtype=object)
    entete = next(i for i in brut.index if str(brut.iat[i, 0]).startswith("Code commune"))
    titres = [str(t).strip() for t in brut.iloc[entete]]
    df = brut.iloc[entete + 1:].copy()
    df.columns = titres
    df = df[df[titres[0]].astype(str).str.match(CODE)]
    apls = [t for t in titres if t.startswith("APL aux")]
    poids = next(t for t in titres if "standardisée" in t)
    out = pd.DataFrame({
        "code": df[titres[0]].astype(str),
        "apl": pd.to_numeric(df[apls[0]], errors="coerce"),
        "poids": pd.to_numeric(df[poids], errors="coerce"),
        "pop": pd.to_numeric(df["Population totale 2022"], errors="coerce"),
    })
    if cle == "apl_mg":
        out["apl60"] = pd.to_numeric(df[next(t for t in apls if "60 ans" in t)], errors="coerce")
    print(f"   {cle:<17} {len(out)} lignes | colonnes : {apls[0]} / {poids}")
    return out.dropna(subset=["apl", "poids"]).set_index("code")


def num_den(df, groupes, colonne="apl"):
    """Numérateur et dénominateur de la moyenne pondérée de `colonne`, par groupe."""
    return (df[colonne] * df["poids"]).groupby(groupes).sum(), df["poids"].groupby(groupes).sum()


def ameli(jeu, select):
    where = f"annee=date'{ANNEE_HONO}' and profession_sante='{SPECIALISTES}'"
    q = urllib.parse.urlencode({"where": where, "select": select, "limit": -1})
    return json.loads(fetch(f"{AMELI}{jeu}/exports/json?{q}"))


def nombre(x):
    """Nombre de l'API (« NS » = non significatif)."""
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


CACHE.mkdir(exist_ok=True)
comm_epci = {c["code"]: c.get("codeEpci") for c in json.loads(EPCI_MAP.read_text(encoding="utf-8"))}
com_vals, dep_vals, ep_vals, dep_nd = {}, {}, {}, {}

# ---- APL ---------------------------------------------------------------
print(f"Lecture APL Drees, onglet {ONGLET}...")
for cle, (piece, dec) in APL.items():
    df = lire_apl(cle, piece)
    df["commune"] = [commune_of(c) for c in df.index]
    df["dep"] = [dep_of(c) for c in df.index]
    df["epci"] = df["commune"].map(comm_epci)
    vals = df["apl"].round(dec).to_dict()
    vals.update((num_den(df, df["commune"])[0] / num_den(df, df["commune"])[1]).round(dec)
                .loc[["75056", "69123", "13055"]].to_dict())
    com_vals[cle] = vals
    dn, dd = num_den(df, df["dep"])
    dep_vals[cle] = (dn / dd).round(dec).to_dict()
    dep_nd[cle] = {d: [float(dn[d]), float(dd[d])] for d in dn.index}
    en, ed = num_den(df[df["epci"].notna()], df["epci"].dropna())
    ep_vals[cle] = (en / ed).round(dec).to_dict()

    if cle == "apl_mg":
        # Sous-dotation : d'après la note des fichiers, un décompte de population se fait en population
        # non standardisée.
        sous = df.loc[df["apl"] <= SEUIL_MG, "pop"].sum() / df["pop"].sum() * 100
        print(f"   population sous {SEUIL_MG} consultations : {sous:.1f} % ; "
              f"APL national {(df.apl * df.poids).sum() / df.poids.sum():.2f}")
        hors = pd.DataFrame({"apl": df["apl"] - df["apl60"], "den": df["apl"], "poids": df["poids"]})
        calc = lambda g: ((hors.apl * hors.poids).groupby(g).sum(), (hors.den * hors.poids).groupby(g).sum())
        part = lambda g: (lambda n, d: (n / d * 100)[d > 0].round(1))(*calc(g))
        cle60 = "apl_mg_60"
        vals60 = part(df.index.to_series()).to_dict()
        vals60.update(part(df["commune"]).loc[["75056", "69123", "13055"]].to_dict())
        com_vals[cle60] = vals60
        dep_vals[cle60] = part(df["dep"]).to_dict()
        n60, d60 = calc(df["dep"])
        dep_nd[cle60] = {d: [float(n60[d]), float(d60[d])] for d in n60.index if d60[d] > 0}
        ep_vals[cle60] = part(df["epci"]).to_dict()

# ---- Dépassements ------------------------------------------------------
print(f"Honoraires et secteurs des spécialistes, {ANNEE_HONO} (Assurance maladie)...")
hono = ameli("honoraires", "departement,depassements_totaux,hono_sans_depassement_totaux")
dep_nd["depassement_spe"] = {}
for r in hono:
    n, d = nombre(r["depassements_totaux"]), nombre(r["hono_sans_depassement_totaux"])
    if r["departement"] != "999" and n is not None and d:
        dep_nd["depassement_spe"][r["departement"]] = [n, d]
sect = {}
for r in ameli("demographie-secteurs-conventionnels", "departement,secteur_conventionnel,effectif"):
    # Le secteur 2 se détaille en 3 (Optam) et 4 (hors Optam) ; 5 = non conventionnés.
    if r["departement"] != "999" and r["secteur_conventionnel"] in ("1", "3", "4", "5") and r["effectif"] is not None:
        sect.setdefault(r["departement"], {})[r["secteur_conventionnel"]] = r["effectif"]
dep_nd["secteur2_spe"] = {d: [s.get("3", 0) + s.get("4", 0), sum(s.values())] for d, s in sect.items() if sum(s.values())}
for cle in ("depassement_spe", "secteur2_spe"):
    dep_vals[cle] = {d: round(n / m * 100, 1) for d, (n, m) in dep_nd[cle].items()}
    print(f"   {cle:<17} {len(dep_vals[cle])} départements")

NUMERATEURS.write_text(json.dumps(dep_nd, ensure_ascii=False), encoding="utf-8")

# ---- Fusion atlas ------------------------------------------------------
print("Fusion dans l'atlas...")
vus, atlas_codes = set(), set()
for fp in sorted(COMMUNES.glob("*.json")):
    data = json.loads(fp.read_text(encoding="utf-8"))
    atlas_codes |= set(data)
    changed = False
    for code in data:
        for cle, vals in com_vals.items():
            if code in vals and pd.notna(vals[code]):
                data[code][cle] = vals[code]
                vus.add(code)
                changed = True
    if changed:
        fp.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

deps = json.loads((ATLAS / "departements.json").read_text(encoding="utf-8"))
for d in deps:
    for cle, vals in dep_vals.items():
        if d["code"] in vals:
            d[cle] = vals[d["code"]]
(ATLAS / "departements.json").write_text(json.dumps(deps, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

epci = json.loads((ATLAS / "epci.json").read_text(encoding="utf-8"))
for e in epci:
    for cle, vals in ep_vals.items():
        if e["code"] in vals:
            e[cle] = vals[e["code"]]
(ATLAS / "epci.json").write_text(json.dumps(epci, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

apl_codes = set(com_vals["apl_mg"])
print(f"-> {len(vus)} communes renseignées sur {len(atlas_codes)} de l'atlas")
print(f"   atlas sans APL : {len(atlas_codes - apl_codes)} {sorted(atlas_codes - apl_codes)[:15]}")
print(f"   APL hors atlas : {len(apl_codes - atlas_codes)} {sorted(apl_codes - atlas_codes)[:15]}")
for cle, vals in dep_vals.items():
    print(f"   {cle:<17} Paris={vals.get('75')} Creuse={vals.get('23')} Seine-St-Denis={vals.get('93')}")
