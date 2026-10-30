# -*- coding: utf-8 -*-
"""
Atlas - balayage des croisements d'indicateurs, candidats a l'editorialisation.

Parcourt TOUTES les paires d'indicateurs de l'Atlas (registre lu directement dans
frontend/src/config/indicateurs.js, zero duplication) et calcule pour chaque paire :
  - maille departement (n=101)   : Pearson
  - maille commune (~35 000)     : Pearson, Pearson pondere par la population, Spearman
  - signaux : meme groupe (souvent trivial), inversion de signe entre mailles,
    ecart fort entre mailles, divergence Pearson/Spearman (non-lineaire ou outliers)
  - gisement d'outsiders : part de communes tres loin du pronostic (OLS), et les
    plus gros ecarts nommes (pop >= POP_MIN_OUTLIER pour ne pas nommer un hameau)

Selection AUTOMATIQUE des cartes du front (decision 2026-07-04, plus de curation manuelle) :
  - retenu si |r communes pondere| >= R_SELECTION, Spearman de meme signe (robustesse),
    et DIMENSIONS latentes differentes (deux indicateurs de la meme dimension = tautologie :
    cadres x diplomes mesurent le meme monde social). La dimension derive du groupe du
    registre, avec DIM_OVERRIDES pour les exceptions (va_lycee est une performance, pas
    une composition). Tout nouvel indicateur du front est tagge automatiquement.
  - une seule carte par paire de dimensions (la plus forte), les autres en variantes.
  - orientation Y ~ X par PRIORITE_Y (le plus « resultat » en Y, le plus structurel en X).
  - par carte : outliers nationaux nommes des DEUX cotes du pronostic (le front ne peut
    pas les calculer, il ne charge les communes que departement par departement).
  - textes auto (question, lecture) surchargables SANS toucher au code via
    docs/croisements/overrides.json : { "<id-carte>": {"question": .., "lecture": ..,
    "note": .., "masquer": true} }. C'est le levier « on adapte petit a petit ».
    `note` = mise en garde affichee sur la carte (ex. biais frontalier : on explique,
    on ne masque pas, decision S. 2026-07-04).

Sorties :
  - frontend/public/data/atlas/croisements.json   les cartes servies au front
  - docs/croisements/rapport.md                   rapport d'audit (6 sections)
  - docs/croisements/candidats.json               toutes les paires, stats completes

Garde-fou a rappeler sur chaque carte publiee : correlation territoriale, pas
individuelle (sophisme ecologique), et pronostic n'est pas causalite.
"""
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ATLAS = ROOT / "frontend" / "public" / "data" / "atlas"
CONFIG_JS = ROOT / "frontend" / "src" / "config" / "indicateurs.js"
INDEX = ATLAS / "territoires-index.json"
OUT_DIR = ROOT / "docs" / "croisements"

MIN_N_COMMUNES = 300   # sous ce n, la maille commune n'est pas fiable pour la paire
POP_MIN_OUTLIER = 2000  # on ne nomme pas un hameau dans le rapport
Z_OUTLIER = 2.5        # seuil "tres loin du pronostic"
R_FORTE = 0.5
R_NULLE = 0.15
R_SELECTION = 0.3      # seuil de retenue d'un croisement pour les cartes du front

# Dimension latente de chaque indicateur : deux indicateurs de la meme dimension
# mesurent le meme phenomene, leur croisement est tautologique (pas de carte).
GROUPE_TO_DIM = {
    "École": "ecole",
    "Richesse": "richesse",
    "Représentation politique": "politique",
    "Population": "pcs",
    "Logement": "logement",
    "Démographie": "demographie",
    "Santé": "sante",
}
DIM_OVERRIDES = {"va_lycee": "perf-ecole"}  # une performance, pas une composition sociale

# Orientation des cartes : Y = la dimension la plus « resultat », X = la plus structurelle.
PRIORITE_Y = ["perf-ecole", "sante", "ecole", "politique", "richesse", "pcs", "logement", "demographie"]

FRONT_OUT = ATLAS / "croisements.json"
OVERRIDES = OUT_DIR / "overrides.json"


# ------------------------------------------------------------------
# Registre : lu dans indicateurs.js (source de verite unique du front)
# ------------------------------------------------------------------
def parse_indicateurs(js_text):
    m = re.search(r"export const INDICATEURS = \[(.*?)\n\]", js_text, re.S)
    if not m:
        raise RuntimeError("INDICATEURS introuvable dans indicateurs.js")
    blocks = re.split(r"\n  \{", m.group(1))
    inds = []
    for b in blocks:
        def field(key):
            mm = re.search(rf"\b{key}:\s*'([^']*)'", b)
            return mm.group(1) if mm else None
        iid = field("id")
        if not iid:
            continue
        inds.append({
            "id": iid,
            "label": field("label"),
            "groupe": field("groupe"),
            "deptKey": field("deptKey"),
            "communeKey": field("communeKey"),
            "unite": field("unite") or "",
            "source": field("source"),
        })
    if len(inds) < 2:
        raise RuntimeError("registre vide apres parsing")
    return inds


# ------------------------------------------------------------------
# Stats (stdlib uniquement)
# ------------------------------------------------------------------
def pearson(xs, ys, ws=None):
    n = len(xs)
    if n < 3:
        return None
    if ws is None:
        ws = [1.0] * n
    sw = sum(ws)
    if sw <= 0:
        return None
    mx = sum(w * x for w, x in zip(ws, xs)) / sw
    my = sum(w * y for w, y in zip(ws, ys)) / sw
    cov = sum(w * (x - mx) * (y - my) for w, x, y in zip(ws, xs, ys))
    vx = sum(w * (x - mx) ** 2 for w, x in zip(ws, xs))
    vy = sum(w * (y - my) ** 2 for w, y in zip(ws, ys))
    if vx <= 0 or vy <= 0:
        return None
    return cov / math.sqrt(vx * vy)


def ranks(vals):
    order = sorted(range(len(vals)), key=lambda i: vals[i])
    rk = [0.0] * len(vals)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and vals[order[j + 1]] == vals[order[i]]:
            j += 1
        avg = (i + j) / 2 + 1
        for k in range(i, j + 1):
            rk[order[k]] = avg
        i = j + 1
    return rk


def spearman(xs, ys):
    return pearson(ranks(xs), ranks(ys))


def ols_z_residuals(xs, ys):
    """Residus standardises de y ~ x (OLS non pondere). None si degenere."""
    r = pearson(xs, ys)
    if r is None:
        return None
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    vx = sum((x - mx) ** 2 for x in xs)
    if vx <= 0:
        return None
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / vx
    res = [y - (my + slope * (x - mx)) for x, y in zip(xs, ys)]
    sd = math.sqrt(sum(e * e for e in res) / max(1, n - 2))
    if sd <= 0:
        return None
    return [e / sd for e in res]


# ------------------------------------------------------------------
# Chargement des donnees
# ------------------------------------------------------------------
def nom_commune(code, noms):
    """Nom depuis l'index, avec fallback arrondissements PLM (absents de l'index)."""
    if code in noms:
        return noms[code]
    for prefix, ville, base in (("751", "Paris", 75100), ("132", "Marseille", 13200),
                                ("6938", "Lyon", 69380)):
        if code.startswith(prefix):
            n = int(code) - base
            if 1 <= n <= 20:
                return f"{ville} {n}{'er' if n == 1 else 'e'} arr."
    return code


def load_all():
    print("Registre :", CONFIG_JS.name)
    inds = parse_indicateurs(CONFIG_JS.read_text(encoding="utf-8"))
    for ind in inds:
        ind["dimension"] = DIM_OVERRIDES.get(ind["id"]) or GROUPE_TO_DIM.get(ind["groupe"])
        if not ind["dimension"]:
            print(f"   ! groupe inconnu pour {ind['id']} ({ind['groupe']}), dimension = groupe")
            ind["dimension"] = ind["groupe"]
    print(f"   {len(inds)} indicateurs, {len(inds) * (len(inds) - 1) // 2} paires")

    depts = json.loads((ATLAS / "departements.json").read_text(encoding="utf-8"))
    print(f"   {len(depts)} departements")

    communes = {}
    for f in sorted((ATLAS / "communes").glob("*.json")):
        for code, rec in json.loads(f.read_text(encoding="utf-8")).items():
            communes[code] = rec
    print(f"   {len(communes)} communes")

    idx = json.loads(INDEX.read_text(encoding="utf-8"))
    noms_communes = {c[0]: c[1] for c in idx.get("communes", [])}
    noms_deps = {d[0]: d[1] for d in idx.get("deps", [])}
    return inds, depts, communes, noms_communes, noms_deps


# ------------------------------------------------------------------
# Analyse d'une paire
# ------------------------------------------------------------------
def analyse_pair(a, b, depts, communes, noms_communes, noms_deps):
    # Maille departement
    dpts = [(d["code"], d.get(a["deptKey"]), d.get(b["deptKey"])) for d in depts]
    dpts = [(c, x, y) for c, x, y in dpts if x is not None and y is not None]
    r_dept = pearson([x for _, x, _ in dpts], [y for _, _, y in dpts]) if len(dpts) >= 10 else None

    # Maille commune
    coms = []
    for code, rec in communes.items():
        x, y = rec.get(a["communeKey"]), rec.get(b["communeKey"])
        if x is not None and y is not None:
            coms.append((code, x, y, rec.get("pop")))
    n_com = len(coms)
    r_com = r_com_w = sp = None
    if n_com >= MIN_N_COMMUNES:
        xs = [x for _, x, _, _ in coms]
        ys = [y for _, _, y, _ in coms]
        r_com = pearson(xs, ys)
        sp = spearman(xs, ys)
        pond = [(x, y, p) for _, x, y, p in coms if p]
        if len(pond) >= MIN_N_COMMUNES:
            r_com_w = pearson([x for x, _, _ in pond], [y for _, y, _ in pond],
                              [p for _, _, p in pond])

    # r de reference : communes pondere si dispo, sinon departements
    r_ref = r_com_w if r_com_w is not None else r_dept

    # Signaux
    signaux = []
    if a["groupe"] == b["groupe"]:
        signaux.append("meme-groupe")
    if r_dept is not None and r_com_w is not None:
        if r_dept * r_com_w < 0 and abs(r_dept) > 0.1 and abs(r_com_w) > 0.1:
            signaux.append("inversion-de-signe")
        elif abs(r_dept - r_com_w) > 0.25:
            signaux.append("ecart-mailles")
    if r_com is not None and sp is not None and abs(r_com - sp) > 0.15:
        signaux.append("non-lineaire-ou-outliers")
    if r_ref is not None and abs(r_ref) >= R_FORTE:
        signaux.append("forte")
    if r_ref is not None and abs(r_ref) <= R_NULLE:
        signaux.append("quasi-nulle")

    # Gisement d'outsiders (communes, OLS b ~ a non pondere, comme le scatter du site)
    outliers, outlier_share = [], None
    if n_com >= MIN_N_COMMUNES and r_com is not None and abs(r_com) >= 0.2:
        zs = ols_z_residuals([x for _, x, _, _ in coms], [y for _, _, y, _ in coms])
        if zs:
            outlier_share = sum(1 for z in zs if abs(z) > Z_OUTLIER) / n_com
            gros = [(coms[i][0], coms[i][1], coms[i][2], coms[i][3], zs[i])
                    for i in range(n_com)
                    if coms[i][3] and coms[i][3] >= POP_MIN_OUTLIER and abs(zs[i]) > Z_OUTLIER]
            gros.sort(key=lambda t: -abs(t[4]))
            outliers = [{
                "code": c, "nom": nom_commune(c, noms_communes),
                "x": x, "y": y, "pop": p, "z": round(z, 1),
            } for c, x, y, p, z in gros[:8]]

    # Outliers departements (utile pour la vue nationale)
    outliers_dept = []
    if r_dept is not None and abs(r_dept) >= 0.2 and len(dpts) >= 10:
        zs = ols_z_residuals([x for _, x, _ in dpts], [y for _, _, y in dpts])
        if zs:
            gros = sorted(zip(dpts, zs), key=lambda t: -abs(t[1]))[:5]
            outliers_dept = [{
                "code": c, "nom": noms_deps.get(c, c), "x": x, "y": y, "z": round(z, 1),
            } for (c, x, y), z in gros if abs(z) > 1.5]

    # Score d'interet, transparent : force de la relation, penalisee si meme groupe
    # (souvent deux mesures du meme monde social), bonifiee si paradoxe d'agregation.
    score = abs(r_ref) if r_ref is not None else 0.0
    if "meme-groupe" in signaux:
        score *= 0.4
    if "inversion-de-signe" in signaux:
        score += 0.3
    if outlier_share:
        score += min(0.1, outlier_share)

    rnd = lambda v: round(v, 3) if v is not None else None
    return {
        "a": a["id"], "b": b["id"],
        "labels": [a["label"], b["label"]],
        "groupes": [a["groupe"], b["groupe"]],
        "sources": [a["source"], b["source"]],
        "dept": {"n": len(dpts), "r": rnd(r_dept)},
        "communes": {"n": n_com, "r": rnd(r_com), "r_pondere": rnd(r_com_w), "spearman": rnd(sp)},
        "r_ref": rnd(r_ref),
        "signaux": signaux,
        "score": round(score, 3),
        "outlier_share": rnd(outlier_share),
        "outliers_communes": outliers,
        "outliers_departements": outliers_dept,
    }


# ------------------------------------------------------------------
# Selection automatique des cartes du front
# ------------------------------------------------------------------
def force_relation(r):
    ar = abs(r)
    return "très forte" if ar >= 0.7 else "forte" if ar >= 0.5 else "nette"


def build_card(p, variantes, by_id, communes, noms_communes):
    a, b = by_id[p["a"]], by_id[p["b"]]
    y, x = (a, b) if PRIORITE_Y.index(a["dimension"]) <= PRIORITE_Y.index(b["dimension"]) else (b, a)

    # Outliers nationaux, orientes y ~ x (le front ne peut pas les calculer)
    pts = []
    for code, rec in communes.items():
        xv, yv = rec.get(x["communeKey"]), rec.get(y["communeKey"])
        if xv is not None and yv is not None:
            pts.append((code, xv, yv, rec.get("pop")))
    zs = ols_z_residuals([q[1] for q in pts], [q[2] for q in pts])
    dessus, dessous = [], []
    if zs:
        named = [(pts[i][0], pts[i][1], pts[i][2], pts[i][3], zs[i]) for i in range(len(pts))
                 if pts[i][3] and pts[i][3] >= POP_MIN_OUTLIER]
        def as_out(t):
            c, xv, yv, pop, z = t
            return {"code": c, "nom": nom_commune(c, noms_communes),
                    "x": xv, "y": yv, "pop": pop, "z": round(z, 1)}
        named.sort(key=lambda t: -t[4])
        dessus = [as_out(t) for t in named[:8] if t[4] >= Z_OUTLIER]
        named.sort(key=lambda t: t[4])
        dessous = [as_out(t) for t in named[:8] if t[4] <= -Z_OUTLIER]

    r = p["communes"]["r_pondere"]
    if r > 0:
        question = f"« {y['label']} » monte avec « {x['label']} ». Partout ?"
        sens = "évoluent ensemble"
    else:
        question = f"« {y['label']} » baisse quand « {x['label']} » monte. Partout ?"
        sens = "évoluent en sens inverse"
    return {
        "id": f"{y['id']}__{x['id']}",
        "y": y["id"], "x": x["id"],
        "dimensions": [y["dimension"], x["dimension"]],
        "r_communes": r, "r_dept": p["dept"]["r"], "n_communes": p["communes"]["n"],
        "force": force_relation(r),
        "question": question,
        "lecture": (f"Entre communes, {y['label']} et {x['label']} {sens} "
                    f"(corrélation {r:+.2f}, relation {force_relation(r)})."),
        "dessus": dessus,
        "dessous": dessous,
        "variantes": [{"a": v["a"], "b": v["b"], "r": v["communes"]["r_pondere"]}
                      for v in variantes],
    }


def select_croisements(pairs, inds, communes, noms_communes):
    """Toutes les paires robustes inter-dimensions, dedupliquees par paire de dimensions."""
    by_id = {i["id"]: i for i in inds}
    ok = []
    for p in pairs:
        a, b = by_id[p["a"]], by_id[p["b"]]
        r, s = p["communes"]["r_pondere"], p["communes"]["spearman"]
        if a["dimension"] == b["dimension"]:
            continue  # tautologique
        if r is None or abs(r) < R_SELECTION:
            continue  # relation trop faible pour porter une carte
        if s is None or r * s <= 0:
            continue  # fragile : les rangs ne confirment pas
        ok.append(p)

    groupes = {}
    for p in ok:
        key = tuple(sorted((by_id[p["a"]]["dimension"], by_id[p["b"]]["dimension"])))
        groupes.setdefault(key, []).append(p)

    cards = []
    for ps in groupes.values():
        ps.sort(key=lambda p: -abs(p["communes"]["r_pondere"]))
        cards.append(build_card(ps[0], ps[1:], by_id, communes, noms_communes))
    cards.sort(key=lambda c: -abs(c["r_communes"]))

    # Surcharges editoriales (textes adaptes petit a petit, sans toucher au code)
    if OVERRIDES.exists():
        ov = json.loads(OVERRIDES.read_text(encoding="utf-8"))
        cards = [c for c in cards if not ov.get(c["id"], {}).get("masquer")]
        for c in cards:
            for champ in ("question", "lecture", "note"):
                if ov.get(c["id"], {}).get(champ):
                    c[champ] = ov[c["id"]][champ]
    return cards


# ------------------------------------------------------------------
# Rapport de curation
# ------------------------------------------------------------------
def fmt_r(v):
    return "" if v is None else f"{v:+.2f}"


def ligne(p):
    sig = ", ".join(s for s in p["signaux"] if s not in ("forte", "quasi-nulle")) or ""
    return (f"| {p['labels'][0]} × {p['labels'][1]} | {fmt_r(p['dept']['r'])} "
            f"| {fmt_r(p['communes']['r_pondere'])} | {fmt_r(p['communes']['spearman'])} "
            f"| {p['communes']['n']} | {sig} |")


ENTETE_TABLE = ("| Paire | r dept | r communes (pond.) | Spearman | n communes | Signaux |\n"
                "|---|---|---|---|---|---|")


def build_report(pairs, n_inds, cards):
    inter = [p for p in pairs if "meme-groupe" not in p["signaux"]]
    lines = []
    w = lines.append
    w("# Croisements de l'Atlas : audit du balayage et selection automatique")
    w("")
    w("> Genere par `python/tools/build_croisements.py`. La selection des cartes du front est")
    w("> AUTOMATIQUE (section 0) ; les textes s'adaptent petit a petit via overrides.json.")
    w("> Rappels sur toute carte publiee : correlation territoriale, pas individuelle")
    w("> (sophisme ecologique) ; pronostic n'est pas causalite ; le r depend de la maille (MAUP).")
    w("")
    w(f"{n_inds} indicateurs, {len(pairs)} paires. Lecture : r dept = Pearson sur 101")
    w("departements ; r communes = Pearson pondere par la population ; Spearman = robustesse")
    w("(rangs, non pondere). Score = |r| de reference, penalise x0.4 si meme groupe,")
    w("bonifie si inversion de signe entre mailles.")
    w("")

    w(f"## 0. Selection automatique servie au front ({len(cards)} cartes)")
    w("")
    w(f"Criteres : |r communes pondere| >= {R_SELECTION}, Spearman de meme signe, dimensions")
    w("latentes differentes, une carte par paire de dimensions (la plus forte, le reste en")
    w("variantes). Pour surcharger un texte ou masquer une carte : `overrides.json` (cle = id).")
    w("")
    w("| id | Question (auto ou surchargee) | r communes | Variantes |")
    w("|---|---|---|---|")
    for c in cards:
        w(f"| `{c['id']}` | {c['question']} | {c['r_communes']:+.2f} | {len(c['variantes'])} |")
    w("")

    w("## 1. Shortlist automatique (top 15 par score)")
    w("")
    w(ENTETE_TABLE)
    for p in sorted(pairs, key=lambda p: -p["score"])[:15]:
        w(ligne(p))
    w("")

    fortes = sorted([p for p in inter if "forte" in p["signaux"]],
                    key=lambda p: -abs(p["r_ref"] or 0))
    w(f"## 2. Correlations fortes inter-groupes ({len(fortes)}) : matiere a « la France que ca dessine »")
    w("")
    w(ENTETE_TABLE)
    for p in fortes:
        w(ligne(p))
    w("")

    nulles = sorted([p for p in inter if "quasi-nulle" in p["signaux"]],
                    key=lambda p: abs(p["r_ref"] or 0))
    w(f"## 3. Quasi nulles inter-groupes ({len(nulles)}) : chercher ici l'idee recue qui tombe")
    w("")
    w("La machine ne sait pas ce que le public s'attend a trouver correle : c'est dans cette")
    w("liste qu'un oeil humain repere le « on aurait jure que oui, et non ».")
    w("")
    w(ENTETE_TABLE)
    for p in nulles:
        w(ligne(p))
    w("")

    paradoxes = [p for p in pairs
                 if "inversion-de-signe" in p["signaux"] or "ecart-mailles" in p["signaux"]]
    w(f"## 4. Paradoxes d'agregation ({len(paradoxes)}) : le r change avec la maille")
    w("")
    w("Une inversion de signe departements/communes est editorialement forte (« vu de loin")
    w("oui, vu de pres non ») mais exige une explication solide avant publication.")
    w("")
    w(ENTETE_TABLE)
    for p in sorted(paradoxes, key=lambda p: -abs((p["dept"]["r"] or 0) - (p["communes"]["r_pondere"] or 0))):
        w(ligne(p))
    w("")

    gisements = sorted([p for p in inter if p["outlier_share"]],
                       key=lambda p: -p["outlier_share"])[:10]
    w("## 5. Gisements d'outsiders : les paires aux plus gros ecarts au pronostic")
    w("")
    for p in gisements:
        w(f"### {p['labels'][0]} × {p['labels'][1]} "
          f"(r communes {fmt_r(p['communes']['r'])}, {p['outlier_share']:.1%} de communes a |z| > {Z_OUTLIER})")
        for o in p["outliers_communes"][:5]:
            sens = "au-dessus" if o["z"] > 0 else "en dessous"
            w(f"- {o['nom']} ({o['code']}, {o['pop']:,} hab) : {sens} du pronostic (z = {o['z']})")
        if p["outliers_departements"]:
            w("- Departements : " + ", ".join(
                f"{o['nom']} (z = {o['z']})" for o in p["outliers_departements"]))
        w("")

    w("## 6. Table complete")
    w("")
    w(ENTETE_TABLE)
    for p in sorted(pairs, key=lambda p: -abs(p["r_ref"] or 0)):
        w(ligne(p))
    w("")
    return "\n".join(lines)


# ------------------------------------------------------------------
def main():
    inds, depts, communes, noms_communes, noms_deps = load_all()
    pairs = []
    for i in range(len(inds)):
        for j in range(i + 1, len(inds)):
            pairs.append(analyse_pair(inds[i], inds[j], depts, communes,
                                      noms_communes, noms_deps))
    print(f"   {len(pairs)} paires analysees")

    cards = select_croisements(pairs, inds, communes, noms_communes)
    print(f"   {len(cards)} cartes retenues (une par paire de dimensions)")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "candidats.json").write_text(
        json.dumps({"indicateurs": inds, "paires": pairs}, ensure_ascii=False, indent=1),
        encoding="utf-8")
    print(f"   -> {OUT_DIR / 'candidats.json'}")

    rapport = build_report(pairs, len(inds), cards)
    (OUT_DIR / "rapport.md").write_text(rapport, encoding="utf-8")
    print(f"   -> {OUT_DIR / 'rapport.md'}")

    FRONT_OUT.write_text(
        json.dumps({
            "seuils": {"r_min": R_SELECTION, "z_outlier": Z_OUTLIER, "pop_min": POP_MIN_OUTLIER},
            "croisements": cards,
        }, ensure_ascii=False, indent=1),
        encoding="utf-8")
    print(f"   -> {FRONT_OUT}")

    print("\nCartes servies au front :")
    for c in cards:
        print(f"   {c['r_communes']:+.2f}  {c['id']}"
              f"  (dessus {len(c['dessus'])}, dessous {len(c['dessous'])},"
              f" variantes {len(c['variantes'])})")


if __name__ == "__main__":
    main()
