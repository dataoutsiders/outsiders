"""
Exploration des variables candidates pour l'ACM
Génère un rapport avec statistiques et recommandations
"""
import pandas as pd
import numpy as np
import json
from pathlib import Path
from datetime import datetime

# Chemins
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data" / "francais-information"
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

# Charger les données
print("Chargement des données...")
df = pd.read_excel(DATA_DIR / "base-info-arcom.xlsx")

# Convertir POIDS03 (format français avec virgules)
if "POIDS03" in df.columns:
    if df["POIDS03"].dtype == 'object':
        df["POIDS03"] = df["POIDS03"].str.replace(',', '.').astype(float)
    else:
        df["POIDS03"] = pd.to_numeric(df["POIDS03"], errors="coerce").fillna(1)

with open(DATA_DIR / "dictionnaire.json", "r", encoding="utf-8") as f:
    dico = json.load(f)

# Variables candidates pour l'ACM
VARIABLES_ACTIVES_CANDIDATES = {
    # Fréquence des sources
    "NEWS1_R_1": "Fréquence TV",
    "NEWS1_R_2": "Fréquence Radio",
    "NEWS1_R_3": "Fréquence Presse écrite",
    "NEWS1_R_4": "Fréquence Sites/apps médias",
    "NEWS1_R_5": "Fréquence Réseaux sociaux",
    "NEWS1_R_6": "Fréquence Podcasts",
    "NEWS1_R_7": "Fréquence Entourage",

    # Intérêt par thématique
    "INT2_R_1": "Intérêt Actualité internationale",
    "INT2_R_2": "Intérêt Actualité nationale",
    "INT2_R_3": "Intérêt Actualité locale",
    "INT2_R_4": "Intérêt Politique",
    "INT2_R_5": "Intérêt Économie",
    "INT2_R_6": "Intérêt Société",
    "INT2_R_7": "Intérêt Environnement",
    "INT2_R_8": "Intérêt Santé",
    "INT2_R_9": "Intérêt Culture",
    "INT2_R_10": "Intérêt Sport",
    "INT2_R_11": "Intérêt People",
    "INT2_R_12": "Intérêt Sciences",

    # Intérêt global
    "INT1_R": "Intérêt global pour l'info",

    # Dynamique
    "DYN1_R": "Dynamique consommation info",

    # Évitement
    "EVITE1_R": "Évitement volontaire info",

    # Confiance
    "CONF1_R": "Confiance générale médias",

    # Propension à payer
    "PAY_R_1": "Paye pour info en ligne",
}

VARIABLES_SUPPLEMENTAIRES = {
    "RS1_R": "Genre",
    "RS2C_RECODE_AG_R": "Âge",
    "CSPIND_R": "CSP",
    "RS5_R": "Niveau d'études",
    "NOU1_R": "Orientation politique (0-10)",
    "FREQ_INTERNET_R": "Fréquence internet",
}


def analyze_variable(df, var_name, var_label, weight_col="POIDS03"):
    """Analyse une variable et retourne les statistiques."""

    if var_name not in df.columns:
        return None

    col = df[var_name]
    weights = df[weight_col] if weight_col in df.columns else pd.Series(1, index=df.index)

    # Stats de base
    n_total = len(col)
    n_missing = col.isna().sum()
    n_valid = n_total - n_missing
    pct_missing = (n_missing / n_total) * 100

    # Distribution des modalités (pondérée)
    valid_mask = col.notna()
    valid_data = df[valid_mask].copy()
    if len(valid_data) == 0:
        return None

    # S'assurer que les poids sont numériques
    valid_weights = pd.to_numeric(valid_data[weight_col], errors="coerce").fillna(1)
    valid_data["_weight"] = valid_weights

    # Calcul pondéré
    weighted_counts = valid_data.groupby(var_name)["_weight"].sum()
    total_weight = weighted_counts.sum()
    if total_weight == 0:
        return None
    weighted_pcts = (weighted_counts / total_weight * 100).round(1)

    # Non pondéré pour comparaison
    raw_counts = col.value_counts().sort_index()

    # Nombre de modalités
    n_modalities = col.nunique()

    # Modalité minimale (problème si < 5%)
    min_pct = weighted_pcts.min()
    min_modality = weighted_pcts.idxmin()

    # Concentration (la modalité max concentre-t-elle trop ?)
    max_pct = weighted_pcts.max()

    # Entropie normalisée (0 = une seule modalité, 1 = distribution uniforme)
    probs = weighted_pcts / 100
    entropy = -np.sum(probs * np.log2(probs + 1e-10))
    max_entropy = np.log2(n_modalities) if n_modalities > 1 else 1
    normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0

    # Labels des modalités depuis le dictionnaire
    modality_labels = {}
    if var_name in dico and dico[var_name]["modalites"]:
        modality_labels = dico[var_name]["modalites"]
    # Chercher aussi dans L_VAR ou C_VAR
    for prefix in ["L_", "C_"]:
        alt_key = prefix + var_name
        if alt_key in dico and dico[alt_key]["modalites"]:
            modality_labels = dico[alt_key]["modalites"]
            break

    return {
        "variable": var_name,
        "label": var_label,
        "n_total": n_total,
        "n_valid": n_valid,
        "n_missing": n_missing,
        "pct_missing": round(pct_missing, 1),
        "n_modalities": n_modalities,
        "min_pct": round(min_pct, 1),
        "min_modality": min_modality,
        "max_pct": round(max_pct, 1),
        "normalized_entropy": round(normalized_entropy, 2),
        "distribution": {
            str(k): {"count": int(raw_counts.get(k, 0)), "pct": float(weighted_pcts.get(k, 0))}
            for k in weighted_pcts.index
        },
        "modality_labels": modality_labels,
    }


def score_variable(stats):
    """
    Score de 0 à 100 pour évaluer si la variable est adaptée à l'ACM.
    Plus le score est élevé, mieux c'est.
    """
    if stats is None:
        return 0

    score = 100
    reasons = []

    # Pénalité pour taux de non-réponse élevé
    if stats["pct_missing"] > 20:
        score -= 30
        reasons.append(f"Taux de non-réponse élevé ({stats['pct_missing']}%)")
    elif stats["pct_missing"] > 10:
        score -= 15
        reasons.append(f"Taux de non-réponse modéré ({stats['pct_missing']}%)")

    # Pénalité pour modalité trop faible
    if stats["min_pct"] < 3:
        score -= 25
        reasons.append(f"Modalité trop rare ({stats['min_pct']}%)")
    elif stats["min_pct"] < 5:
        score -= 10
        reasons.append(f"Modalité faible ({stats['min_pct']}%)")

    # Pénalité pour concentration excessive
    if stats["max_pct"] > 80:
        score -= 30
        reasons.append(f"Trop concentrée ({stats['max_pct']}% sur une modalité)")
    elif stats["max_pct"] > 60:
        score -= 15
        reasons.append(f"Assez concentrée ({stats['max_pct']}%)")

    # Bonus pour bonne entropie (distribution équilibrée)
    if stats["normalized_entropy"] > 0.8:
        score += 10
        reasons.append("Bonne distribution")
    elif stats["normalized_entropy"] < 0.5:
        score -= 10
        reasons.append("Distribution déséquilibrée")

    # Pénalité si trop peu de modalités (binaire = moins riche)
    if stats["n_modalities"] < 3:
        score -= 5
        reasons.append("Variable binaire")

    return max(0, min(100, score)), reasons


def generate_report(results_actives, results_supp):
    """Génère le rapport Markdown."""

    report = []
    report.append("# Exploration des variables pour l'ACM")
    report.append(f"\n*Généré le {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n")

    # Explication des indicateurs
    report.append("## Guide de lecture\n")
    report.append("""
### Indicateurs utilisés

| Indicateur | Signification | Seuils recommandés |
|------------|---------------|-------------------|
| **% non-réponse** | Part des répondants sans réponse valide | < 10% idéal, > 20% problématique |
| **% modalité min** | Part de la modalité la moins fréquente | > 5% idéal, < 3% problématique |
| **% modalité max** | Part de la modalité la plus fréquente | < 60% idéal, > 80% problématique |
| **Entropie normalisée** | Mesure de l'équilibre de la distribution (0=concentrée, 1=uniforme) | > 0.7 idéal |
| **Score ACM** | Score synthétique (0-100) | > 70 = OK, 50-70 = attention, < 50 = problématique |

### Interprétation

- **Modalité trop rare** (< 5%) : Risque de créer un axe "artificiel" tiré par quelques individus atypiques
- **Variable trop concentrée** (> 80% sur une modalité) : N'apporte pas assez de variance, peu discriminante
- **Entropie faible** : La variable ne différencie pas bien les individus
- **Score ACM** : Synthèse des critères ci-dessus. À utiliser comme guide, pas comme règle absolue.
""")

    # Variables actives
    report.append("\n## Variables actives candidates\n")
    report.append("*Ces variables définiraient les axes de l'ACM*\n")

    # Trier par score
    scored = [(r, *score_variable(r)) for r in results_actives if r]
    scored.sort(key=lambda x: x[1], reverse=True)

    # Tableau récapitulatif
    report.append("### Récapitulatif\n")
    report.append("| Variable | Label | Score | Modalités | % NR | % Min | % Max | Entropie | Avis |")
    report.append("|----------|-------|-------|-----------|------|-------|-------|----------|------|")

    for stats, score, reasons in scored:
        avis = "✅" if score >= 70 else "⚠️" if score >= 50 else "❌"
        report.append(
            f"| `{stats['variable']}` | {stats['label'][:25]} | {score} | {stats['n_modalities']} | "
            f"{stats['pct_missing']}% | {stats['min_pct']}% | {stats['max_pct']}% | "
            f"{stats['normalized_entropy']} | {avis} |"
        )

    # Détail par variable
    report.append("\n### Détail des distributions\n")

    for stats, score, reasons in scored:
        report.append(f"#### {stats['variable']} - {stats['label']}")
        report.append(f"\n**Score ACM : {score}/100** " + ("✅" if score >= 70 else "⚠️" if score >= 50 else "❌"))

        if reasons:
            report.append("\n*Remarques :* " + ", ".join(reasons))

        report.append(f"\n- Réponses valides : {stats['n_valid']:,} ({100-stats['pct_missing']:.0f}%)")
        report.append(f"- Non-réponses : {stats['n_missing']:,} ({stats['pct_missing']}%)")
        report.append(f"- Entropie normalisée : {stats['normalized_entropy']}")

        report.append("\n| Code | Label | N | % |")
        report.append("|------|-------|---|---|")

        for code, data in sorted(stats["distribution"].items(), key=lambda x: int(float(x[0])) if x[0].replace('.','').isdigit() else 0):
            label = stats["modality_labels"].get(str(int(float(code))), "-") if code.replace('.','').isdigit() else "-"
            label = label[:40] if label else "-"
            flag = " ⚠️" if data["pct"] < 5 else ""
            report.append(f"| {code} | {label} | {data['count']:,} | {data['pct']}%{flag} |")

        report.append("")

    # Variables supplémentaires
    report.append("\n## Variables supplémentaires\n")
    report.append("*Ces variables seront projetées sur les axes sans les influencer*\n")

    report.append("| Variable | Label | Modalités | % NR | Distribution |")
    report.append("|----------|-------|-----------|------|--------------|")

    for stats in results_supp:
        if stats:
            dist_summary = ", ".join([f"{k}:{v['pct']}%" for k, v in list(stats["distribution"].items())[:4]])
            report.append(
                f"| `{stats['variable']}` | {stats['label']} | {stats['n_modalities']} | "
                f"{stats['pct_missing']}% | {dist_summary}... |"
            )

    # Recommandations
    report.append("\n## Recommandations\n")

    good_vars = [s[0]["variable"] for s in scored if s[1] >= 70]
    medium_vars = [s[0]["variable"] for s in scored if 50 <= s[1] < 70]
    bad_vars = [s[0]["variable"] for s in scored if s[1] < 50]

    report.append("### Variables recommandées (score ≥ 70)\n")
    if good_vars:
        report.append("```")
        report.append("\n".join(good_vars))
        report.append("```")
    else:
        report.append("*Aucune variable avec un score ≥ 70*")

    report.append("\n### Variables à surveiller (score 50-69)\n")
    if medium_vars:
        report.append("Ces variables peuvent être incluses mais attention aux modalités rares.\n")
        report.append("```")
        report.append("\n".join(medium_vars))
        report.append("```")

    report.append("\n### Variables problématiques (score < 50)\n")
    if bad_vars:
        report.append("Envisager de recoder ou exclure.\n")
        report.append("```")
        report.append("\n".join(bad_vars))
        report.append("```")

    return "\n".join(report)


# Main
print("Analyse des variables actives candidates...")
results_actives = []
for var, label in VARIABLES_ACTIVES_CANDIDATES.items():
    stats = analyze_variable(df, var, label)
    if stats:
        results_actives.append(stats)
        print(f"  OK {var}")
    else:
        print(f"  -- {var} (non trouvee)")

print("\nAnalyse des variables supplémentaires...")
results_supp = []
for var, label in VARIABLES_SUPPLEMENTAIRES.items():
    stats = analyze_variable(df, var, label)
    if stats:
        results_supp.append(stats)
        print(f"  OK {var}")
    else:
        print(f"  -- {var} (non trouvee)")

print("\nGénération du rapport...")
report = generate_report(results_actives, results_supp)

output_path = OUTPUT_DIR / "exploration_variables_acm.md"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(report)

print(f"\nRapport genere : {output_path}")
