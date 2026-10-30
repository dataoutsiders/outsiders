# -*- coding: utf-8 -*-
"""
Offre ou demande ? Équipements sportifs (Data ES) et licences en QPV.

Complète explore_sport_injep.py (même dossier, mêmes règles) pour le futur
dossier « Sport » d'Outsiders. Ne produit rien pour le site.

Sources (téléchargées dans python/data/sport/) :
- Ministère chargé des sports, Recensement des équipements sportifs, espaces
  et sites de pratiques (Data ES), export « équipements » et « installations »
  (equipements/data-es-equipement.csv, equipements/data-es-installation.csv),
  téléchargés le 29/10/2026 depuis equipements.sports.gouv.fr (lien data.gouv).
- ANCT, contours des QPV 2024 (GeoJSON WGS84) et 2015 (shapefile WGS84),
  dans qpv_contours/.
- INJEP, licences géocodées 2019-2023 (commune x QPV), Insee population des
  QPV 2024, population communale 2021, Filosofi 2023 (via explore_sport_injep).

Test 1 (coupe 2023, géographie 2024) : distance de chaque QPV mono-communal à
l'équipement le plus proche de chaque type ; taux de licences du QPV rapporté
au taux hors QPV de sa commune, par tranche de distance ; modèle de Poisson
avec contrôles (taille du QPV, revenu de la commune).

Test 2 (2019 -> 2022, géographie 2015) : QPV près desquels (moins de 1 km) un
équipement a été mis en service en 2020 ou 2021, contre QPV sans mise en
service ; évolution des licences du sport rapportée à celle du hors QPV de la
commune (différence de différences simple).

Usage : PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -I python/tools/explore_sport_offre.py [1] [2]
"""
import json
import struct
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
import explore_sport_injep as base  # noqa: E402

ROOT = base.ROOT
DATA = base.DATA
OUT = base.OUT
EQ = DATA / "equipements"
QC = DATA / "qpv_contours"
log = base.log
save = base.save
R_TERRE = 6371008.8

# ---------------------------------------------------------------------------
# Correspondance explicite type d'équipement -> fédération
# (famille, type) ; type None = toute la famille
# ---------------------------------------------------------------------------
CORRESPONDANCE = [
    # sport, codes fédération, famille Data ES, types Data ES (None = tous), remarque
    ("Tennis", ["123"], "Court de tennis", None, "courts couverts et découverts"),
    ("Natation", ["119"], "Bassin de natation",
     ["Bassin sportif de natation", "Bassin mixte de natation"], "bassins ludiques exclus"),
    ("Judo", ["117"], "Salle de combat", ["Dojo / Salle d'arts martiaux"], "dojo partagé avec karaté, aïkido..."),
    ("Karaté", ["229"], "Salle de combat", ["Dojo / Salle d'arts martiaux"], "dojo partagé"),
    ("Boxe", ["106"], "Salle de combat", ["Salle de boxe"], ""),
    ("Équitation", ["109"], "Equipement équestre", None, "carrières, manèges, parcours"),
    ("Golf", ["132"], "Parcours de golf", None, "parcours 9 et 18 trous, practices, initiation"),
    ("Football", ["111"], "Terrain de grands jeux", ["Terrain de football", "Terrain mixte"],
     "terrains partagés (scolaires, rugby)"),
    ("Rugby", ["133"], "Terrain de grands jeux", ["Terrain de rugby", "Terrain mixte", "Terrain de rugby à XIII"],
     "terrains mixtes partagés avec le football"),
    ("Basket", ["105"], None, ["Salle multisports (gymnase)", "Terrain de basket-ball", "Terrain de basket-ball 3x3"],
     "gymnases partagés (scolaires, hand, volley...)"),
    ("Handball", ["115"], None, ["Salle multisports (gymnase)", "Terrain de handball"], "gymnases partagés"),
    ("Gymnastique", ["113"], "Salle ou terrain spécialisé", ["Salle de gymnastique sportive"], ""),
    ("Tennis de table", ["124"], "Salle ou terrain spécialisé", ["Salle de tennis de table"], ""),
    ("Athlétisme", ["101"], "Equipement d'athlétisme", ["Stade d’athlétisme", "Stade d'athlétisme",
                                                         "Piste d'athlétisme isolée", "Piste d'athlétisme 2 à 4 couloirs"], ""),
]

TRANCHES = [(-1, 500, "moins de 500 m"), (500, 1000, "500 m à 1 km"),
            (1000, 2000, "1 à 2 km"), (2000, 1e12, "plus de 2 km")]


def tranche(d):
    for lo, hi, lab in TRANCHES:
        if lo < d <= hi:
            return lab
    return TRANCHES[-1][2]


# ---------------------------------------------------------------------------
# Équipements
# ---------------------------------------------------------------------------
def load_equipements() -> pd.DataFrame:
    e = pd.read_csv(EQ / "data-es-equipement.csv", sep=";", dtype=str)
    e["lat"] = pd.to_numeric(e.coordonnees_y, errors="coerce")
    e["lon"] = pd.to_numeric(e.coordonnees_x, errors="coerce")
    e["annee"] = pd.to_numeric(e.mise_en_service_date, errors="coerce")
    inst = pd.read_csv(EQ / "data-es-installation.csv", sep=";", dtype=str,
                       usecols=["numero", "insee"]).rename(columns={"numero": "installation_numero"})
    e = e.merge(inst, on="installation_numero", how="left")
    return e


def decrire_equipements(e: pd.DataFrame):
    rows = []
    for c in ["numero", "installation_numero", "famille", "type", "code", "coordonnees_y", "coordonnees_x",
              "insee", "mise_en_service_date", "mise_en_service_periode", "is_date_mise_en_service_known",
              "creation_dt", "date_creation_metier", "derniers_travaux_date", "homologation_date", "etat"]:
        s = e[c]
        rows.append({"champ": c, "part_renseignee": s.notna().mean(), "nb_valeurs": s.nunique(),
                     "exemples": " | ".join(s.dropna().astype(str).value_counts().head(4).index)})
    t = pd.DataFrame(rows)
    save(t, "g_dataes_champs.csv")
    log(t)
    # années de mise en service : distribution et entassement sur les années rondes
    a = e.annee.dropna()
    an = a.value_counts().sort_index()
    save(an.rename("equipements").reset_index().rename(columns={"index": "annee"}), "g_dataes_annees_mise_en_service.csv")
    rondes = an[[y for y in an.index if 1950 <= y <= 2015 and y % 5 == 0]].sum()
    tot5015 = an[[y for y in an.index if 1950 <= y <= 2015]].sum()
    log(f"[INFO] date de mise en service renseignée : {e.annee.notna().mean():.3f} ; "
        f"part des années multiples de 5 (1950-2015) : {rondes / tot5015:.3f} (0,20 attendu sans arrondi)")
    log(f"[INFO] indicateur « date connue » renseigné pour {e.is_date_mise_en_service_known.notna().mean():.3f} "
        f"des équipements ; « Oui » : {(e.is_date_mise_en_service_known == 'Oui').sum()}")
    # correspondance appliquée
    rows = []
    for sport, feds, fam, types, rq in CORRESPONDANCE:
        m = selection(e, fam, types)
        sub = e[m]
        rows.append({"sport": sport, "federations": ",".join(feds), "famille_data_es": fam or "(plusieurs)",
                     "types_data_es": " ; ".join(types) if types else "(tous)", "remarque": rq,
                     "equipements": int(m.sum()),
                     "part_date_renseignee": sub.annee.notna().mean(),
                     "mis_en_service_2019": int((sub.annee == 2019).sum()),
                     "mis_en_service_2020": int((sub.annee == 2020).sum()),
                     "mis_en_service_2021": int((sub.annee == 2021).sum()),
                     "mis_en_service_2022": int((sub.annee == 2022).sum())})
    c = pd.DataFrame(rows)
    save(c, "g_correspondance_equipement_federation.csv")
    log(c)


def selection(e, fam, types):
    m = pd.Series(True, index=e.index)
    if fam:
        m &= e.famille == fam
    if types:
        m &= e.type.isin(types)
    return m & e.lat.notna() & e.lon.notna()


# ---------------------------------------------------------------------------
# Contours des QPV (sans bibliothèque SIG : GeoJSON et shapefile lus à la main)
# ---------------------------------------------------------------------------
def lire_qpv_2024():
    g = json.loads((QC / "GEOJSON" / "QP2024_France_Hexagonale_Outre_Mer_WGS84.geojson").read_text(encoding="utf-8"))
    out = {}
    for f in g["features"]:
        p = f["properties"]
        geom = f["geometry"]
        polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
        rings = [np.asarray(r, dtype=float)[:, :2] for poly in polys for r in poly]
        out[p["code_qp"]] = rings
    return out


def lire_qpv_2015():
    shp = (QC / "QP_METROPOLEOUTREMER_WGS84_EPSG4326.shp").read_bytes()
    dbf = (QC / "QP_METROPOLEOUTREMER_WGS84_EPSG4326.dbf").read_bytes()
    n, hl, rl = struct.unpack("<IHH", dbf[4:12])
    champs, i = [], 32
    while dbf[i] != 0x0D:
        champs.append((dbf[i:i + 11].split(b"\x00")[0].decode(), dbf[i + 16]))
        i += 32
    codes = []
    for k in range(n):
        rec = dbf[hl + k * rl + 1: hl + (k + 1) * rl]
        pos, vals = 0, {}
        for name, ln in champs:
            vals[name] = rec[pos:pos + ln].decode("latin-1").strip()
            pos += ln
        codes.append(vals["CODE_QP"])
    out, pos, k = {}, 100, 0
    while pos < len(shp):
        _, clen = struct.unpack(">ii", shp[pos:pos + 8])
        body = shp[pos + 8: pos + 8 + clen * 2]
        stype = struct.unpack("<i", body[:4])[0]
        if stype == 5:
            nparts, npts = struct.unpack("<ii", body[36:44])
            parts = list(struct.unpack(f"<{nparts}i", body[44:44 + 4 * nparts]))
            pts = np.frombuffer(body[44 + 4 * nparts: 44 + 4 * nparts + 16 * npts], dtype="<f8").reshape(-1, 2)
            parts.append(npts)
            out[codes[k]] = [pts[parts[j]:parts[j + 1]].copy() for j in range(nparts)]
        k += 1
        pos += 8 + clen * 2
    return out


def xyz(lat, lon):
    la, lo = np.radians(lat), np.radians(lon)
    return np.c_[np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)] * R_TERRE


def local(lon, lat, lon0, lat0):
    x = (lon - lon0) * np.cos(np.radians(lat0)) * 111320.0
    y = (lat - lat0) * 110574.0
    return x, y


def distance_contour(px, py, rings_xy):
    """Distance (m) de points à un (multi)polygone : 0 à l'intérieur (pair-impair),
    sinon distance au bord le plus proche."""
    ax = np.concatenate([r[:-1, 0] for r in rings_xy]); ay = np.concatenate([r[:-1, 1] for r in rings_xy])
    bx = np.concatenate([r[1:, 0] for r in rings_xy]); by = np.concatenate([r[1:, 1] for r in rings_xy])
    P = px[:, None]; Q = py[:, None]
    # intérieur (règle pair-impair, valable pour trous et multi-parties)
    cond = (ay[None, :] > Q) != (by[None, :] > Q)
    with np.errstate(divide="ignore", invalid="ignore"):
        xint = ax[None, :] + (Q - ay[None, :]) * (bx - ax)[None, :] / (by - ay)[None, :]
    inside = (cond & (P < xint)).sum(axis=1) % 2 == 1
    dx, dy = (bx - ax)[None, :], (by - ay)[None, :]
    L2 = dx ** 2 + dy ** 2
    with np.errstate(divide="ignore", invalid="ignore"):
        t = np.clip(((P - ax[None, :]) * dx + (Q - ay[None, :]) * dy) / L2, 0, 1)
    t = np.where(L2 > 0, t, 0)
    d = np.sqrt((P - ax[None, :] - t * dx) ** 2 + (Q - ay[None, :] - t * dy) ** 2).min(axis=1)
    return np.where(inside, 0.0, d)


def geom_qpv(rings):
    allp = np.vstack(rings)
    lon0, lat0 = allp[:, 0].mean(), allp[:, 1].mean()
    rx = [np.c_[local(r[:, 0], r[:, 1], lon0, lat0)] for r in rings]
    # centroïde surfacique (parties extérieures et trous signés par la règle du lacet)
    A = cx = cy = 0.0
    for r in rx:
        x, y = r[:, 0], r[:, 1]
        cr = x[:-1] * y[1:] - x[1:] * y[:-1]
        a = cr.sum() / 2
        if abs(a) < 1e-9:
            continue
        A += a
        cx += ((x[:-1] + x[1:]) * cr).sum() / 6
        cy += ((y[:-1] + y[1:]) * cr).sum() / 6
    if abs(A) > 1e-6:
        cx, cy = cx / A, cy / A
    else:
        cx, cy = 0.0, 0.0
    clon = lon0 + cx / (np.cos(np.radians(lat0)) * 111320.0)
    clat = lat0 + cy / 110574.0
    rmax = np.sqrt(((np.vstack(rx) - [cx, cy]) ** 2).sum(axis=1)).max()
    return {"lon0": lon0, "lat0": lat0, "rings_xy": rx, "clon": clon, "clat": clat,
            "rmax": rmax, "surface_m2": abs(A)}


def distances(qpv_rings: dict, eq: pd.DataFrame, codes, rayon_compte=1000.0):
    """Pour chaque QPV de `codes` et chaque sport : distance au plus proche
    (contour et centroïde) et nombre d'équipements à moins de `rayon_compte` du contour."""
    geoms = {c: geom_qpv(qpv_rings[c]) for c in codes if c in qpv_rings}
    rows = []
    for sport, sub in eq.groupby("sport"):
        pts = xyz(sub.lat.values, sub.lon.values)
        tree = cKDTree(pts)
        lat, lon = sub.lat.values, sub.lon.values
        for c, g in geoms.items():
            cpt = xyz(np.array([g["clat"]]), np.array([g["clon"]]))
            d0, _ = tree.query(cpt, k=1)
            d0 = float(d0[0])
            r = max(d0, rayon_compte) + g["rmax"] + 50
            idx = tree.query_ball_point(cpt[0], r * 1.01)
            if not idx:
                rows.append({"qpv": c, "sport": sport, "d_centroide": d0, "d_contour": d0, "n_1km": 0})
                continue
            idx = np.array(idx)
            px, py = local(lon[idx], lat[idx], g["lon0"], g["lat0"])
            dd = distance_contour(px, py, g["rings_xy"])
            rows.append({"qpv": c, "sport": sport, "d_centroide": d0, "d_contour": float(dd.min()),
                         "n_1km": int((dd <= rayon_compte).sum())})
    d = pd.DataFrame(rows)
    meta = pd.DataFrame([{"qpv": c, "surface_m2": g["surface_m2"], "clat": g["clat"], "clon": g["clon"]}
                         for c, g in geoms.items()])
    return d, meta


def equipements_par_sport(e: pd.DataFrame, annee_max=None, annees=None):
    parts = []
    for sport, feds, fam, types, _ in CORRESPONDANCE:
        m = selection(e, fam, types)
        sub = e[m].copy()
        if annee_max is not None:
            sub = sub[~(sub.annee > annee_max)]  # dates inconnues gardées
        if annees is not None:
            sub = sub[sub.annee.isin(annees)]
        sub["sport"] = sport
        parts.append(sub[["numero", "sport", "lat", "lon", "annee", "is_date_mise_en_service_known", "insee"]])
    return pd.concat(parts, ignore_index=True)


FED_SPORT = {f: s for s, feds, *_ in CORRESPONDANCE for f in feds}


# ---------------------------------------------------------------------------
# Licences par QPV et hors QPV
# ---------------------------------------------------------------------------
def licences_qpv(annee: int):
    d = base.load_geo(annee)
    d = d[(d.statut.str.startswith("1")) & (d.typ.isin(["QPV", "HZ"]))]
    d = d[d.fed.isin(FED_SPORT.keys())]
    d["sport"] = d.fed.map(FED_SPORT)
    q = d[d.typ == "QPV"].groupby(["qpv", "com", "sport"]).Total.sum().rename("L_q").reset_index()
    h = d[d.typ == "HZ"].groupby(["com", "sport"]).Total.sum().rename("L_h").reset_index()
    # QPV présents dans une seule commune du fichier licences
    ncom = d[d.typ == "QPV"].groupby("qpv").com.nunique()
    return q, h, set(ncom[ncom == 1].index)


# ---------------------------------------------------------------------------
# Test 1
# ---------------------------------------------------------------------------
def test1(e):
    import statsmodels.api as sm
    import statsmodels.formula.api as smf

    q, h, mono_lic = licences_qpv(2023)
    pq = base.load_pop_qpv()
    pq = pq[pq.mono & pq.qpv.isin(mono_lic)]
    at = base.load_atlas_communes().set_index("com")
    multi = set()
    for l in base.load_pop_qpv().query("~mono").listeDepcom:
        multi.update(l.split(","))
    popq_com = pq.groupby("listeDepcom").pop_qpv.sum()
    allq = base.load_pop_qpv()
    allq_mono_com = allq[allq.mono].groupby("listeDepcom").pop_qpv.sum()
    coms = [c for c in popq_com.index if c not in multi and c in at.index and pd.notna(at.loc[c, "pop21"])]
    popc = pd.DataFrame({"pop_com": at.pop21.reindex(coms), "pop_Q_tous": allq_mono_com.reindex(coms),
                         "revenu": at.revenu.reindex(coms)})
    popc["pop_H"] = popc.pop_com - popc.pop_Q_tous
    popc = popc[popc.pop_H > 1000]
    pq = pq[pq.listeDepcom.isin(popc.index)].rename(columns={"listeDepcom": "com"})
    log(f"[INFO] test 1 : {len(pq)} QPV mono-communaux dans {pq.com.nunique()} communes, "
        f"{pq.pop_qpv.sum():,.0f} habitants")

    eq = equipements_par_sport(e, annee_max=2023)
    rings = lire_qpv_2024()
    dist, meta = distances(rings, eq, pq.qpv.tolist())
    save(dist, "g_test1_distances_qpv_2024.csv")

    grid = pq[["qpv", "com", "pop_qpv"]].merge(pd.DataFrame({"sport": [c[0] for c in CORRESPONDANCE]}), how="cross")
    grid = grid.merge(q[["qpv", "sport", "L_q"]], on=["qpv", "sport"], how="left").fillna({"L_q": 0})
    grid = grid.merge(h, on=["com", "sport"], how="left").fillna({"L_h": 0})
    grid = grid.merge(popc[["pop_H", "revenu"]], left_on="com", right_index=True)
    grid = grid.merge(dist, on=["qpv", "sport"], how="left").merge(meta[["qpv", "surface_m2"]], on="qpv", how="left")
    grid["taux_h"] = grid.L_h / grid.pop_H
    grid["E"] = grid.pop_qpv * grid.taux_h
    grid["tranche"] = grid.d_contour.map(tranche)
    save(grid, "g_test1_qpv_sport_2023.csv")

    rows, mods = [], []
    ordre = [t[2] for t in TRANCHES]
    for sport, s in grid.groupby("sport"):
        s = s[s.E > 0].copy()
        for t in ordre:
            x = s[s.tranche == t]
            rows.append({"sport": sport, "tranche": t, "qpv": len(x), "pop_qpv": x.pop_qpv.sum(),
                         "licences_qpv": x.L_q.sum(), "attendu_taux_hors_qpv": x.E.sum(),
                         "rapport_observe_attendu": x.L_q.sum() / x.E.sum() if x.E.sum() > 0 else np.nan,
                         "distance_mediane_m": x.d_contour.median()})
        # Poisson, offset = log attendu (taux hors QPV de la commune x population du QPV)
        s["tr"] = pd.Categorical(s.tranche, categories=ordre)
        s["log_pop"] = np.log(s.pop_qpv)
        s["log_rev"] = np.log(s.revenu)
        s = s.dropna(subset=["log_rev"])
        present = [t for t in ordre if (s.tranche == t).sum() >= 10]
        if len(present) < 2:
            continue
        s = s[s.tranche.isin(present)]
        s["tr"] = pd.Categorical(s.tranche, categories=present)
        for spec, f in [("brut", "L_q ~ tr"), ("contrôlé", "L_q ~ tr + log_pop + log_rev")]:
            try:
                m = smf.glm(f, data=s, family=sm.families.Poisson(), offset=np.log(s.E)).fit(
                    cov_type="cluster", cov_kwds={"groups": pd.factorize(s.com)[0]})
            except Exception as ex:  # pragma: no cover
                log(f"[ERROR] {sport} {spec} : {ex}")
                continue
            for name in m.params.index:
                if name.startswith("tr["):
                    lo, hi = m.conf_int().loc[name]
                    mods.append({"sport": sport, "modele": spec, "terme": name.replace("tr[T.", "").rstrip("]"),
                                 "reference": present[0], "irr": np.exp(m.params[name]),
                                 "ic95_bas": np.exp(lo), "ic95_haut": np.exp(hi), "p": m.pvalues[name],
                                 "n_qpv": len(s)})
            if spec == "contrôlé":
                for name in ("log_pop", "log_rev"):
                    mods.append({"sport": sport, "modele": spec, "terme": name, "reference": "",
                                 "irr": np.exp(m.params[name]), "ic95_bas": np.exp(m.conf_int().loc[name][0]),
                                 "ic95_haut": np.exp(m.conf_int().loc[name][1]), "p": m.pvalues[name],
                                 "n_qpv": len(s)})
    t = pd.DataFrame(rows)
    save(t, "g_test1_tranches_distance.csv")
    log(t.round(3).to_string())
    mo = pd.DataFrame(mods)
    save(mo, "g_test1_poisson.csv")
    log(mo.round(3).to_string())
    # Répartition des distances par sport
    rep = grid.groupby("sport").d_contour.describe(percentiles=[.25, .5, .75, .9])
    save(rep.reset_index(), "g_test1_distances_resume.csv")
    log(rep.round(0))


# ---------------------------------------------------------------------------
# Test 2
# ---------------------------------------------------------------------------
def test2(e):
    annees = [2019, 2020, 2021, 2022]
    lq, lh = [], []
    mono = None
    for a in annees:
        q, h, m = licences_qpv(a)
        lq.append(q.assign(annee=a)); lh.append(h.assign(annee=a))
        mono = m if mono is None else (mono & m)
    lq = pd.concat(lq); lh = pd.concat(lh)
    rings = lire_qpv_2015()
    codes = sorted(c for c in mono if c in rings)
    log(f"[INFO] test 2 : {len(codes)} QPV (géographie 2015) mono-communaux présents chaque année 2019-2022")

    # Ouvertures (date de mise en service 2020 ou 2021) et équipements récents à exclure des témoins
    ouv = equipements_par_sport(e, annees=[2020, 2021])
    recents = equipements_par_sport(e, annees=[2018, 2019, 2020, 2021, 2022, 2023])
    d_ouv, _ = distances(rings, ouv, codes)
    d_rec, _ = distances(rings, recents, codes)
    d = d_ouv.rename(columns={"d_contour": "d_ouv", "n_1km": "n_ouv_1km"})[["qpv", "sport", "d_ouv", "n_ouv_1km"]].merge(
        d_rec.rename(columns={"d_contour": "d_rec", "n_1km": "n_rec_1km"})[["qpv", "sport", "d_rec", "n_rec_1km"]],
        on=["qpv", "sport"], how="outer")
    d["traite"] = d.n_ouv_1km > 0
    d["temoin"] = d.n_rec_1km.fillna(0) == 0
    save(d, "g_test2_ouvertures_qpv_2015.csv")

    com_of = lq.drop_duplicates("qpv").set_index("qpv").com
    rows, chemins = [], []
    for sport in [c[0] for c in CORRESPONDANCE]:
        ds = d[d.sport == sport]
        tr = ds[ds.traite].qpv.tolist()
        te = ds[(~ds.traite) & ds.temoin].qpv.tolist()
        piv_q = lq[lq.sport == sport].pivot_table(index="qpv", columns="annee", values="L_q", aggfunc="sum").reindex(codes).fillna(0)
        piv_h = lh[lh.sport == sport].pivot_table(index="com", columns="annee", values="L_h", aggfunc="sum")
        if any(a not in piv_q.columns for a in annees) or any(a not in piv_h.columns for a in annees):
            log(f"[INFO] {sport} : fédération absente d'au moins un millésime 2019-2022, test impossible")
            rows.append({"sport": sport, "qpv_traites_1km": len(tr), "remarque": "fédération absente d'un millésime"})
            continue
        hz = piv_h.reindex(com_of.reindex(codes).values)
        hz.index = codes
        ok = (hz[2019] > 0) & (hz[2022] > 0) & (piv_q[2019] > 0)
        def oe(lst):
            lst = [c for c in lst if ok.get(c, False)]
            if not lst:
                return len(lst), np.nan, {}
            obs = piv_q.loc[lst, 2022].sum()
            att = (piv_q.loc[lst, 2019] * hz.loc[lst, 2022] / hz.loc[lst, 2019]).sum()
            path = {a: (piv_q.loc[lst, a].sum() / piv_q.loc[lst, 2019].sum()) /
                       ((piv_q.loc[lst, 2019] * hz.loc[lst, a] / hz.loc[lst, 2019]).sum() / piv_q.loc[lst, 2019].sum())
                    for a in annees}
            return len(lst), obs / att, path
        n_t, r_t, p_t = oe(tr)
        n_c, r_c, p_c = oe(te)
        # intervalle par rééchantillonnage des QPV traités et témoins
        rng = np.random.default_rng(1)
        bt = []
        tr_ok = [c for c in tr if ok.get(c, False)]
        te_ok = [c for c in te if ok.get(c, False)]
        if len(tr_ok) >= 5:
            for _ in range(500):
                a = list(rng.choice(tr_ok, len(tr_ok)))
                b = list(rng.choice(te_ok, len(te_ok)))
                ra = piv_q.loc[a, 2022].sum() / (piv_q.loc[a, 2019] * hz.loc[a, 2022].values / hz.loc[a, 2019].values).sum()
                rb = piv_q.loc[b, 2022].sum() / (piv_q.loc[b, 2019] * hz.loc[b, 2022].values / hz.loc[b, 2019].values).sum()
                bt.append(ra / rb)
        rows.append({"sport": sport, "qpv_traites_1km": len(tr), "qpv_traites_utilisables": n_t,
                     "qpv_temoins_utilisables": n_c,
                     "licences_2019_traites": piv_q.loc[tr_ok, 2019].sum() if tr_ok else 0,
                     "rapport_obs_att_traites": r_t, "rapport_obs_att_temoins": r_c,
                     "did": r_t / r_c if r_c else np.nan,
                     "did_ic90_bas": np.quantile(bt, .05) if bt else np.nan,
                     "did_ic90_haut": np.quantile(bt, .95) if bt else np.nan})
        for a in annees:
            chemins.append({"sport": sport, "annee": a, "traites": p_t.get(a), "temoins": p_c.get(a)})
    t = pd.DataFrame(rows)
    save(t, "g_test2_did.csv")
    log(t.round(3).to_string())
    save(pd.DataFrame(chemins), "g_test2_trajectoires.csv")
    # dates « connues » parmi les ouvertures retenues
    o = ouv.merge(d_ouv[d_ouv.n_1km > 0][["sport"]].drop_duplicates(), on="sport")
    log(f"[INFO] ouvertures 2020-2021 (types retenus, France) : {len(ouv)} ; "
        f"avec indicateur « date connue = Oui » : {(ouv.is_date_mise_en_service_known == 'Oui').sum()}")


# ---------------------------------------------------------------------------
# Volet A : les équipements comme description de l'offre disponible
# ---------------------------------------------------------------------------
PLM = {"75056", "69123", "13055"}  # communes entières : on garde les arrondissements


def communes_reference():
    """Communes (arrondissements pour Paris, Lyon, Marseille) avec population 2021,
    revenu Filosofi 2023, décile (mêmes bornes que les licences, e_bornes_deciles_2023.csv)
    et taille de la commune entière."""
    c = base.load_atlas_communes().copy()
    c = c[~c.com.isin(PLM) & c.pop21.notna() & (c.pop21 > 0)]
    b = pd.read_csv(OUT / "e_bornes_deciles_2023.csv")
    def dec(r):
        if pd.isna(r):
            return np.nan
        for _, x in b.iterrows():
            if r <= x.revenu_max:
                return int(x.decile)
        return 10
    c["decile"] = c.revenu.map(dec)
    ville = c.com.str[:3].map({"751": "75056", "693": "69123", "132": "13055"})
    entiere = base.load_atlas_communes().set_index("com").pop21
    c["pop_ville"] = np.where(ville.notna() & c.com.str[:2].isin(["75", "69", "13"]) &
                              c.com.str.match(r"^(751\d\d|6938\d|132\d\d)$"),
                              ville.map(entiere), c.pop21)
    bins = [0, 2000, 10000, 50000, 200000, 1e9]
    labs = ["moins de 2 000", "2 000 à 10 000", "10 000 à 50 000", "50 000 à 200 000", "200 000 et plus"]
    c["taille"] = pd.cut(c.pop_ville, bins=bins, labels=labs, right=False)
    return c


def volet_a(e):
    eq = equipements_par_sport(e, annee_max=2023)
    com = communes_reference()
    ne = eq.groupby(["insee", "sport"]).size().rename("equipements").reset_index().rename(columns={"insee": "com"})
    # licences 2023 par commune et sport (domicile, toutes parties de la commune)
    d = base.load_geo(2023)
    d = d[(d.statut.str.startswith("1")) & (d.typ != "NR") & d.fed.isin(FED_SPORT.keys())]
    d["sport"] = d.fed.map(FED_SPORT)
    nl = d.groupby(["com", "sport"]).Total.sum().rename("licences").reset_index()
    sports = [c[0] for c in CORRESPONDANCE]
    grid = com[["com", "pop21", "revenu", "decile", "taille"]].merge(pd.DataFrame({"sport": sports}), how="cross")
    grid = grid.merge(ne, on=["com", "sport"], how="left").merge(nl, on=["com", "sport"], how="left")
    grid[["equipements", "licences"]] = grid[["equipements", "licences"]].fillna(0)
    hors = eq[~eq.insee.isin(com.com)]
    log(f"[INFO] équipements des types retenus non rattachés à une commune de référence : {len(hors)} sur {len(eq)}")
    for var, nom in (("decile", "h_equipements_deciles_revenu.csv"), ("taille", "h_equipements_taille_commune.csv")):
        g = grid.dropna(subset=[var]).groupby([var, "sport"], observed=True).agg(
            equipements=("equipements", "sum"), licences=("licences", "sum"), pop=("pop21", "sum")).reset_index()
        g["equip_pour_10000"] = g.equipements / g["pop"] * 1e4
        g["licences_pour_1000"] = g.licences / g["pop"] * 1e3
        g["licences_par_equipement"] = g.licences / g.equipements
        save(g, nom)
        p1 = g.pivot_table(index="sport", columns=var, values="equip_pour_10000", observed=True)
        p2 = g.pivot_table(index="sport", columns=var, values="licences_pour_1000", observed=True)
        if var == "decile":
            p1["rapport_D10_D1"] = p1[10] / p1[1]
            p2["rapport_D10_D1"] = p2[10] / p2[1]
        log(f"[INFO] équipements pour 10 000 habitants par {var}"); log(p1.round(2))
        log(f"[INFO] licences pour 1 000 habitants par {var}"); log(p2.round(2))

    # Dans le contour des QPV (géographie 2024) contre le reste de la commune
    gq = pd.read_csv(OUT / "g_test1_qpv_sport_2023.csv", dtype={"com": str})
    qpvs = gq.drop_duplicates("qpv")[["qpv", "com", "pop_qpv", "pop_H"]]
    rings = lire_qpv_2024()
    inside = []
    lat, lon = eq.lat.values, eq.lon.values
    for r in qpvs.itertuples():
        g = geom_qpv(rings[r.qpv])
        allp = np.vstack(rings[r.qpv])
        m = ((lon >= allp[:, 0].min()) & (lon <= allp[:, 0].max()) &
             (lat >= allp[:, 1].min()) & (lat <= allp[:, 1].max()))
        if not m.any():
            continue
        idx = np.where(m)[0]
        px, py = local(lon[idx], lat[idx], g["lon0"], g["lat0"])
        dd = distance_contour(px, py, g["rings_xy"])
        for k in idx[dd == 0]:
            inside.append({"qpv": r.qpv, "com_qpv": r.com, "numero": eq.numero.iat[k], "sport": eq.sport.iat[k],
                           "insee_equipement": eq.insee.iat[k]})
    ins = pd.DataFrame(inside)
    save(ins, "h_equipements_dans_qpv_2024.csv")
    log(f"[INFO] équipements des types retenus dans le contour d'un des {len(qpvs)} QPV : "
        f"{ins.numero.nunique()} ; rattachés à une autre commune que celle du QPV : "
        f"{(ins.insee_equipement != ins.com_qpv).sum()}")
    coms = qpvs.com.unique()
    popQ = qpvs.pop_qpv.sum()
    popH = qpvs.drop_duplicates("com").pop_H.sum()
    rows = []
    for sport in sports:
        nq = ins[ins.sport == sport].numero.nunique()
        ncom = int(((eq.sport == sport) & eq.insee.isin(coms)).sum())
        nq_same = ins[(ins.sport == sport) & (ins.insee_equipement == ins.com_qpv)].numero.nunique()
        nh = ncom - nq_same
        s = gq[gq.sport == sport]
        lq = s.L_q.sum()
        lh = s.drop_duplicates("com").L_h.sum()
        rows.append({"sport": sport, "equip_qpv": nq, "equip_hors_qpv": nh,
                     "equip_qpv_pour_10000": nq / popQ * 1e4, "equip_hors_pour_10000": nh / popH * 1e4,
                     "rapport_equipements_Q_sur_H": (nq / popQ) / (nh / popH) if nh else np.nan,
                     "licences_qpv_pour_1000": lq / popQ * 1e3, "licences_hors_pour_1000": lh / popH * 1e3,
                     "rapport_licences_Q_sur_H": (lq / popQ) / (lh / popH) if lh else np.nan,
                     "licences_par_equip_qpv": lq / nq if nq else np.nan,
                     "licences_par_equip_hors": lh / nh if nh else np.nan})
    t = pd.DataFrame(rows)
    t["ecart_licences_sur_ecart_equipements"] = t.rapport_licences_Q_sur_H / t.rapport_equipements_Q_sur_H
    save(t, "h_qpv_equipements_licences_2023.csv")
    log(f"[INFO] {len(qpvs)} QPV, {len(coms)} communes, pop QPV {popQ:,.0f}, hors QPV {popH:,.0f}")
    log(t.round(3).to_string())


# ---------------------------------------------------------------------------
# Volet B : clubs
# ---------------------------------------------------------------------------
def load_clubs(annee: int) -> pd.DataFrame:
    c = pd.read_csv(DATA / f"clubs-data-{annee}.csv", sep=";", dtype=str, encoding="utf-8-sig")
    num = list(c.columns[9:])
    c.columns = ["com", "lib", "qpv", "nomqpv", "dep", "reg", "statut", "fed", "nomfed"] + num
    for x in num:
        c[x] = pd.to_numeric(c[x])
    c["typ"] = np.where(c.qpv.isin(["CSZ", "HZ"]), c.qpv,
                        np.where(c.qpv.str.startswith("NR"), "NR", "QPV"))
    # Avant 2023, pas de distinction des structures actives
    c["n"] = c["Total_actifs"] if "Total_actifs" in c.columns else c["Total"]
    c["annee"] = annee
    return c


def test3():
    import statsmodels.api as sm
    import statsmodels.formula.api as smf
    gq = pd.read_csv(OUT / "g_test1_qpv_sport_2023.csv", dtype={"com": str})
    c = load_clubs(2023)
    c = c[c.statut.str.startswith("1") & c.fed.isin(FED_SPORT.keys())]
    c["sport"] = c.fed.map(FED_SPORT)
    cq = c[c.typ == "QPV"].groupby(["qpv", "sport"]).agg(clubs_q=("n", "sum"), clubs_q_tous=("Total", "sum")).reset_index()
    ch = c[c.typ == "HZ"].groupby(["com", "sport"]).agg(clubs_h=("n", "sum")).reset_index()
    g = gq.merge(cq, on=["qpv", "sport"], how="left").merge(ch, on=["com", "sport"], how="left")
    g[["clubs_q", "clubs_q_tous", "clubs_h"]] = g[["clubs_q", "clubs_q_tous", "clubs_h"]].fillna(0)
    g["club"] = np.where(g.clubs_q > 0, "au moins un club actif", "aucun club actif")
    save(g, "g_test3_qpv_sport_clubs_2023.csv")
    rows, mods, dens = [], [], []
    popQ = g.drop_duplicates("qpv").pop_qpv.sum()
    popH = g.drop_duplicates("com").pop_H.sum()
    for sport, s in g.groupby("sport"):
        sh = s.drop_duplicates("com")
        dens.append({"sport": sport, "clubs_qpv": s.clubs_q.sum(), "clubs_hors_qpv": sh.clubs_h.sum(),
                     "clubs_qpv_pour_10000": s.clubs_q.sum() / popQ * 1e4,
                     "clubs_hors_pour_10000": sh.clubs_h.sum() / popH * 1e4,
                     "rapport_clubs_Q_sur_H": (s.clubs_q.sum() / popQ) / (sh.clubs_h.sum() / popH),
                     "rapport_licences_Q_sur_H": (s.L_q.sum() / popQ) / (sh.L_h.sum() / popH),
                     "part_qpv_avec_club": (s.clubs_q > 0).mean()})
        s = s[s.E > 0].copy()
        for k, x in s.groupby("club"):
            rows.append({"sport": sport, "club": k, "qpv": len(x), "pop_qpv": x.pop_qpv.sum(),
                         "licences_qpv": x.L_q.sum(), "attendu": x.E.sum(),
                         "rapport_observe_attendu": x.L_q.sum() / x.E.sum()})
        s["avec_club"] = (s.clubs_q > 0).astype(int)
        s["log_pop"] = np.log(s.pop_qpv)
        s["log_rev"] = np.log(s.revenu)
        s = s.dropna(subset=["log_rev"])
        if s.avec_club.sum() < 5 or (1 - s.avec_club).sum() < 5:
            continue
        for spec, f in [("brut", "L_q ~ avec_club"), ("contrôlé", "L_q ~ avec_club + log_pop + log_rev")]:
            m = smf.glm(f, data=s, family=sm.families.Poisson(), offset=np.log(s.E)).fit(
                cov_type="cluster", cov_kwds={"groups": pd.factorize(s.com)[0]})
            lo, hi = m.conf_int().loc["avec_club"]
            mods.append({"sport": sport, "modele": spec, "irr_avec_club": np.exp(m.params["avec_club"]),
                         "ic95_bas": np.exp(lo), "ic95_haut": np.exp(hi), "p": m.pvalues["avec_club"],
                         "qpv_avec_club": int(s.avec_club.sum()), "n_qpv": len(s)})
    t = pd.DataFrame(rows); save(t, "g_test3_avec_sans_club.csv"); log(t.round(3).to_string())
    mo = pd.DataFrame(mods); save(mo, "g_test3_poisson.csv"); log(mo.round(3).to_string())
    de = pd.DataFrame(dens); save(de, "g_test3_clubs_densite.csv"); log(de.round(3).to_string())


def test4():
    annees = [2019, 2020, 2021, 2022]
    lq, lh, cl = [], [], []
    mono = None
    for a in annees:
        q, h, m = licences_qpv(a)
        lq.append(q.assign(annee=a)); lh.append(h.assign(annee=a))
        mono = m if mono is None else (mono & m)
        c = load_clubs(a)
        c = c[c.statut.str.startswith("1") & c.fed.isin(FED_SPORT.keys()) & (c.typ == "QPV")]
        c["sport"] = c.fed.map(FED_SPORT)
        cl.append(c.groupby(["qpv", "sport"]).n.sum().rename("clubs").reset_index().assign(annee=a))
    lq = pd.concat(lq); lh = pd.concat(lh); cl = pd.concat(cl)
    codes = sorted(mono)
    com_of = lq.drop_duplicates("qpv").set_index("qpv").com
    nr = pd.DataFrame([{"annee": a, "part_clubs_non_repartis": (lambda c: c.loc[c.typ == "NR", "Total"].sum() / c.Total.sum())(load_clubs(a))}
                       for a in annees])
    save(nr, "g_test4_clubs_non_repartis.csv"); log(nr)
    rows, chemins = [], []
    for sport in [c[0] for c in CORRESPONDANCE]:
        piv_q = lq[lq.sport == sport].pivot_table(index="qpv", columns="annee", values="L_q", aggfunc="sum")
        piv_h = lh[lh.sport == sport].pivot_table(index="com", columns="annee", values="L_h", aggfunc="sum")
        pc = cl[cl.sport == sport].pivot_table(index="qpv", columns="annee", values="clubs", aggfunc="sum")
        if any(a not in piv_q.columns for a in annees):
            rows.append({"sport": sport, "remarque": "fédération absente d'un millésime de licences"})
            continue
        piv_q = piv_q.reindex(codes).fillna(0)
        pc = pc.reindex(index=codes, columns=annees).fillna(0)
        hz = piv_h.reindex(com_of.reindex(codes).values)
        hz.index = codes
        okh = (hz[annees] > 0).all(axis=1)
        groupes = {
            "arrivée": (pc[2020] == 0) & (pc[2022] >= 1),
            "témoin sans club": (pc[[2020, 2021, 2022]] == 0).all(axis=1),
            "départ": (pc[2020] >= 1) & (pc[2022] == 0),
            "témoin avec club": (pc[[2020, 2021, 2022]] >= 1).all(axis=1),
        }
        res = {}
        for k, msk in groupes.items():
            base_ok = okh & (piv_q[2020] > 0)
            lst = [c for c in codes if msk.get(c, False) and base_ok.get(c, False)]
            res[k] = lst
            if not lst:
                continue
            L20 = piv_q.loc[lst, 2020]
            for a in annees:
                obs = piv_q.loc[lst, a].sum()
                att = (L20 * hz.loc[lst, a] / hz.loc[lst, 2020]).sum()
                chemins.append({"sport": sport, "groupe": k, "annee": a, "qpv": len(lst), "obs_sur_att": obs / att})
        def ratio(lst):
            L20 = piv_q.loc[lst, 2020]
            return piv_q.loc[lst, 2022].sum() / (L20 * hz.loc[lst, 2022] / hz.loc[lst, 2020]).sum()
        rng = np.random.default_rng(1)
        out = {"sport": sport}
        for trait, temoin, nom in (("arrivée", "témoin sans club", "arrivee"), ("départ", "témoin avec club", "depart")):
            a, b = res[trait], res[temoin]
            out[f"n_{nom}"] = int(((groupes[trait]) ).sum())
            out[f"n_{nom}_utilisables"] = len(a)
            out[f"n_temoins_{nom}"] = len(b)
            out[f"licences_2020_{nom}"] = piv_q.loc[a, 2020].sum() if a else 0
            if len(a) >= 5 and len(b) >= 5:
                ra, rb = ratio(a), ratio(b)
                bt = [ratio(list(rng.choice(a, len(a)))) / ratio(list(rng.choice(b, len(b)))) for _ in range(500)]
                out[f"did_{nom}"] = ra / rb
                out[f"did_{nom}_ic90_bas"] = np.quantile(bt, .05)
                out[f"did_{nom}_ic90_haut"] = np.quantile(bt, .95)
                # pré-tendance 2019 -> 2020 (licences 2019 rapportées à l'attendu calé sur 2020)
                def pre(lst):
                    L20 = piv_q.loc[lst, 2020]
                    return piv_q.loc[lst, 2019].sum() / (L20 * hz.loc[lst, 2019] / hz.loc[lst, 2020]).sum()
                out[f"pre_2019_{nom}"] = pre(a) / pre(b)
        rows.append(out)
    t = pd.DataFrame(rows); save(t, "g_test4_did_clubs.csv"); log(t.round(3).to_string())
    save(pd.DataFrame(chemins), "g_test4_trajectoires.csv")


def main():
    etapes = sys.argv[1:] or ["0", "1", "2", "A", "3", "4"]
    e = load_equipements()
    if "0" in etapes:
        decrire_equipements(e)
    if "1" in etapes:
        test1(e)
    if "2" in etapes:
        test2(e)
    if "A" in etapes:
        volet_a(e)
    if "3" in etapes:
        test3()
    if "4" in etapes:
        test4()


if __name__ == "__main__":
    main()
