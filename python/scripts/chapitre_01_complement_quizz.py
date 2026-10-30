"""
Chapitre 1 - Complement 5 : Score au QUIZZ selon source principale et age
Est-on mieux informe selon le support utilise ?

Variables : QUIZZ1_R, QUIZZ2_R, QUIZZ3_R, QUIZZ4_R (1 = bonne reponse)
"""
import pandas as pd
import numpy as np
from scipy import stats
import json
from pathlib import Path

# Chemins
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data" / "francais-information"
OUTPUT_DIR = BASE_DIR / "outputs" / "chapitres"

print("=" * 70)
print("COMPLEMENT 5 : SCORE QUIZZ SELON SOURCE ET AGE")
print("Est-on mieux informe selon le support utilise ?")
print("=" * 70)

# Charger les donnees
df = pd.read_excel(DATA_DIR / "base-info-arcom.xlsx")
# Conversion des poids (format français avec virgules)
if df['POIDS03'].dtype == 'object':
    df['POIDS03'] = df['POIDS03'].str.replace(',', '.').astype(float)
print(f"\n{len(df)} repondants")

# Variables
VAR_AGE = "RS2C_RECODE_AG_R"
VAR_SOURCE = "NEWS1BIS_R"
VAR_POIDS = "POIDS03"
QUIZZ_VARS = ["QUIZZ1_R", "QUIZZ2_R", "QUIZZ3_R", "QUIZZ4_R"]

AGE_LABELS = {
    1: "15-17 ans", 2: "18-24 ans", 3: "25-34 ans",
    4: "35-44 ans", 5: "45-59 ans", 6: "60-69 ans", 7: "70 ans et +"
}

SOURCE_LABELS = {
    2: "TV",
    8: "RS",
    9: "Video",
    # Autres regroupes
}

# Preparation
df[VAR_POIDS] = df[VAR_POIDS].astype(str).str.replace(',', '.').astype(float)
df[VAR_AGE] = pd.to_numeric(df[VAR_AGE], errors='coerce')
df[VAR_SOURCE] = pd.to_numeric(df[VAR_SOURCE], errors='coerce')

# Calculer le score (nombre de bonnes reponses = 1)
for var in QUIZZ_VARS:
    df[var] = pd.to_numeric(df[var], errors='coerce')

df['score_quizz'] = 0
for var in QUIZZ_VARS:
    df['score_quizz'] += (df[var] == 1).astype(int)

# Source simplifiee
df['source_simple'] = df[VAR_SOURCE].map({
    1: "Autres", 2: "TV", 3: "Autres", 4: "Autres",
    5: "Autres", 6: "Autres", 7: "Autres", 8: "RS", 9: "Video"
})

# Base : ceux qui ont repondu au quizz
df_quizz = df[df[QUIZZ_VARS].notna().all(axis=1)].copy()
print(f"Repondants avec quizz complet: {len(df_quizz)}")

# ============================================================
# ANALYSE 1 : Score moyen par age
# ============================================================
print("\n=== SCORE MOYEN PAR AGE ===")

score_age = df_quizz.groupby(VAR_AGE).apply(
    lambda g: np.average(g['score_quizz'], weights=g[VAR_POIDS])
).reset_index()
score_age.columns = ['age', 'score_moyen']

print(f"\n{'Age':<15} | {'Score moyen':>12} | {'n':>6}")
print("-" * 40)
for _, row in score_age.iterrows():
    age = int(row['age'])
    n = len(df_quizz[df_quizz[VAR_AGE] == age])
    print(f"{AGE_LABELS.get(age, str(age)):<15} | {row['score_moyen']:>11.2f}/4 | {n:>6}")

# ============================================================
# ANALYSE 2 : Score moyen par source principale
# ============================================================
print("\n=== SCORE MOYEN PAR SOURCE PRINCIPALE ===")

df_quizz_source = df_quizz[df_quizz['source_simple'].notna()]
score_source = df_quizz_source.groupby('source_simple').apply(
    lambda g: pd.Series({
        'score_moyen': np.average(g['score_quizz'], weights=g[VAR_POIDS]),
        'n': len(g)
    })
).reset_index()

print(f"\n{'Source':<15} | {'Score moyen':>12} | {'n':>6}")
print("-" * 40)
for _, row in score_source.iterrows():
    print(f"{row['source_simple']:<15} | {row['score_moyen']:>11.2f}/4 | {int(row['n']):>6}")

# ============================================================
# ANALYSE 3 : Score par age ET source (croisement)
# ============================================================
print("\n=== SCORE PAR AGE ET SOURCE ===")

# Focus sur TV vs RS
df_tv_rs = df_quizz_source[df_quizz_source['source_simple'].isin(['TV', 'RS'])]

print(f"\n{'Age':<15} | {'TV':>10} | {'RS':>10} | {'Ecart':>10}")
print("-" * 50)

croisement_data = []
for age in sorted(df_tv_rs[VAR_AGE].dropna().unique()):
    age = int(age)
    subset_tv = df_tv_rs[(df_tv_rs[VAR_AGE] == age) & (df_tv_rs['source_simple'] == 'TV')]
    subset_rs = df_tv_rs[(df_tv_rs[VAR_AGE] == age) & (df_tv_rs['source_simple'] == 'RS')]

    score_tv = np.average(subset_tv['score_quizz'], weights=subset_tv[VAR_POIDS]) if len(subset_tv) > 0 else np.nan
    score_rs = np.average(subset_rs['score_quizz'], weights=subset_rs[VAR_POIDS]) if len(subset_rs) > 0 else np.nan

    ecart = score_tv - score_rs if not np.isnan(score_tv) and not np.isnan(score_rs) else np.nan

    croisement_data.append({
        'age': age,
        'age_label': AGE_LABELS[age],
        'score_tv': round(score_tv, 2) if not np.isnan(score_tv) else None,
        'score_rs': round(score_rs, 2) if not np.isnan(score_rs) else None,
        'ecart': round(ecart, 2) if not np.isnan(ecart) else None,
        'n_tv': len(subset_tv),
        'n_rs': len(subset_rs)
    })

    ecart_str = f"{ecart:+.2f}" if not np.isnan(ecart) else "N/A"
    print(f"{AGE_LABELS[age]:<15} | {score_tv:>9.2f} | {score_rs:>9.2f} | {ecart_str:>10}")

# ============================================================
# ANALYSE 4 : Test statistique
# ============================================================
print("\n=== TESTS STATISTIQUES ===")

# ANOVA : score ~ source
groups = [g['score_quizz'].values for name, g in df_quizz_source.groupby('source_simple') if len(g) > 30]
if len(groups) >= 2:
    f_stat, p_anova = stats.f_oneway(*groups)
    print(f"\nANOVA Score ~ Source:")
    print(f"  F = {f_stat:.2f}, p = {p_anova:.4f}")
    print(f"  => {'Significatif' if p_anova < 0.05 else 'Non significatif'}")

# T-test TV vs RS
tv_scores = df_quizz_source[df_quizz_source['source_simple'] == 'TV']['score_quizz']
rs_scores = df_quizz_source[df_quizz_source['source_simple'] == 'RS']['score_quizz']
t_stat, p_ttest = stats.ttest_ind(tv_scores, rs_scores)
print(f"\nT-test TV vs RS:")
print(f"  t = {t_stat:.2f}, p = {p_ttest:.4f}")
print(f"  => {'Significatif' if p_ttest < 0.05 else 'Non significatif'}")

# ============================================================
# ANALYSE 5 : Taux de bonnes reponses par question
# ============================================================
print("\n=== TAUX DE BONNES REPONSES PAR QUESTION ===")

questions = {
    "QUIZZ1_R": "Israel attaque par...",
    "QUIZZ2_R": "Premier ministre UK",
    "QUIZZ3_R": "Fin mandat Macron",
    "QUIZZ4_R": "Inflation 2023"
}

print(f"\n{'Question':<25} | {'TV':>8} | {'RS':>8} | {'Total':>8}")
print("-" * 55)
for var, label in questions.items():
    taux_tv = (df_quizz_source[df_quizz_source['source_simple'] == 'TV'][var] == 1).mean() * 100
    taux_rs = (df_quizz_source[df_quizz_source['source_simple'] == 'RS'][var] == 1).mean() * 100
    taux_total = (df_quizz[var] == 1).mean() * 100
    print(f"{label:<25} | {taux_tv:>7.1f}% | {taux_rs:>7.1f}% | {taux_total:>7.1f}%")

# ============================================================
# EXPORT JSON
# ============================================================
print("\n=== EXPORT JSON ===")

complement_json = {
    "id": "quizz-connaissance",
    "titre": "Est-on mieux informe selon le support ?",
    "description": "Score au quizz de connaissance (4 questions) selon la source principale d'information et l'age",

    "resultats": {
        "score_par_age": score_age.to_dict('records'),
        "score_par_source": score_source.to_dict('records'),
        "croisement_age_source": croisement_data
    },

    "statistiques": {
        "anova": {
            "F": round(f_stat, 2),
            "p": round(p_anova, 4),
            "significatif": p_anova < 0.05
        },
        "ttest_tv_rs": {
            "t": round(t_stat, 2),
            "p": round(p_ttest, 4),
            "significatif": p_ttest < 0.05,
            "interpretation": "TV vs RS pour le score de connaissance"
        }
    },

    "insights": [],  # A remplir apres analyse

    "metadata": {
        "base": len(df_quizz),
        "questions": list(questions.values())
    }
}

# Determiner les insights
score_tv_moy = score_source[score_source['source_simple'] == 'TV']['score_moyen'].values[0]
score_rs_moy = score_source[score_source['source_simple'] == 'RS']['score_moyen'].values[0]

if score_tv_moy > score_rs_moy + 0.2:
    complement_json["insights"].append({
        "titre": "Les utilisateurs de la TV ont un meilleur score",
        "description": f"Score moyen TV: {score_tv_moy:.2f}/4 vs RS: {score_rs_moy:.2f}/4"
    })
elif score_rs_moy > score_tv_moy + 0.2:
    complement_json["insights"].append({
        "titre": "Les utilisateurs des RS ont un meilleur score",
        "description": f"Score moyen RS: {score_rs_moy:.2f}/4 vs TV: {score_tv_moy:.2f}/4"
    })
else:
    complement_json["insights"].append({
        "titre": "Pas de difference notable entre TV et RS",
        "description": f"Scores proches: TV {score_tv_moy:.2f}/4, RS {score_rs_moy:.2f}/4"
    })

# Sauvegarder
output_file = OUTPUT_DIR / "01-basculement-complement-quizz.json"
with open(output_file, "w", encoding="utf-8") as f:
    def convert(obj):
        if isinstance(obj, dict):
            return {k: convert(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert(i) for i in obj]
        elif isinstance(obj, (np.integer, np.int64)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64)):
            return float(obj)
        elif isinstance(obj, (np.bool_, bool)):
            return bool(obj)
        elif pd.isna(obj):
            return None
        else:
            return obj
    json.dump(convert(complement_json), f, ensure_ascii=False, indent=2)

print(f"JSON genere: {output_file}")

# ============================================================
# RESUME
# ============================================================
print("\n" + "=" * 70)
print("RESUME")
print("=" * 70)
print(f"""
Score moyen global: {df_quizz['score_quizz'].mean():.2f}/4

Par source principale:
  - TV: {score_tv_moy:.2f}/4
  - RS: {score_rs_moy:.2f}/4

Difference statistiquement {'significative' if p_ttest < 0.05 else 'non significative'} (p = {p_ttest:.4f})
""")
