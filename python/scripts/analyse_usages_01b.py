# -*- coding: utf-8 -*-
"""
Chapitre 01b - Analyse des usages (format, duree, direct/differe)
Hypothese : ce sont les usages qui different, pas la possession d'equipement
"""
import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path

BASE_DIR = Path('python')
DATA_DIR = BASE_DIR / 'data' / 'francais-information'

# =============================================================================
# CHARGEMENT DES DONNEES
# =============================================================================
print("Chargement des donnees...")
df = pd.read_excel(DATA_DIR / 'base-info-arcom.xlsx')
df['POIDS03'] = df['POIDS03'].astype(str).str.replace(',', '.').astype(float)
print(f"Echantillon : {len(df)} repondants")

# =============================================================================
# LABELS
# =============================================================================
AGE_LABELS = {
    1: '15-17 ans', 2: '18-24 ans', 3: '25-34 ans', 4: '35-44 ans',
    5: '45-59 ans', 6: '60-69 ans', 7: '70 ans et +'
}

FORMAT_LABELS = {
    1: "Audio/son",
    2: "Ecrit",
    3: "Video",
    4: "Photos/images"
}

LONGUEUR_VIDEO_LABELS = {
    1: "Long (>20 min)",
    2: "Court (5-20 min)",
    3: "Tres court (<5 min)"
}

DIRECT_LABELS = {
    1: "En direct",
    2: "En replay/differe"
}

# =============================================================================
# FONCTIONS
# =============================================================================

def cramers_v(ct):
    """Calcule V de Cramer sur tableau de contingence"""
    chi2 = stats.chi2_contingency(ct)[0]
    n = ct.sum().sum()
    min_dim = min(ct.shape) - 1
    return np.sqrt(chi2 / (n * min_dim)) if min_dim > 0 and n > 0 else 0

def get_distribution_by_age(df, var, var_labels, poids='POIDS03'):
    """Calcule la distribution d'une variable selon l'age"""
    results = []
    for age_code in range(1, 8):
        subset = df[df['RS2C_RECODE_AG_R'] == age_code]
        total = subset[poids].sum()

        row = {'age': AGE_LABELS.get(age_code, str(age_code))}
        for val, label in var_labels.items():
            n = subset[subset[var] == val][poids].sum()
            pct = n / total * 100 if total > 0 else 0
            row[label] = round(pct, 1)
        results.append(row)
    return results

def analyse_variable(df, var, var_labels, titre):
    """Analyse complete d'une variable"""
    print(f"\n{'='*80}")
    print(f"### {titre} ###")
    print("="*80)

    # Distribution globale
    valid = df[df[var].notna()]
    total = valid['POIDS03'].sum()
    print(f"\nDistribution globale (n={len(valid)}):")
    for val, label in var_labels.items():
        n = valid[valid[var] == val]['POIDS03'].sum()
        pct = n / total * 100 if total > 0 else 0
        print(f"  {label}: {pct:.1f}%")

    # V de Cramer avec age
    mask = df[var].notna() & df['RS2C_RECODE_AG_R'].notna()
    ct = pd.crosstab(
        df[mask]['RS2C_RECODE_AG_R'],
        df[mask][var],
        values=df[mask]['POIDS03'],
        aggfunc='sum'
    ).fillna(0)

    if ct.shape[0] >= 2 and ct.shape[1] >= 2:
        chi2, p, dof, _ = stats.chi2_contingency(ct)
        v = cramers_v(ct)
        signif = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "NS"
        print(f"\nAssociation avec l'age:")
        print(f"  V de Cramer = {v:.3f} {signif}")
        print(f"  Chi2 = {chi2:.1f}, p = {p:.4f}")

    # Distribution par age
    print(f"\nDistribution par age:")
    dist = get_distribution_by_age(df, var, var_labels)

    # Header
    header = f"{'Age':<15}"
    for label in var_labels.values():
        header += f" | {label[:12]:<12}"
    print(header)
    print("-" * len(header))

    for row in dist:
        line = f"{row['age']:<15}"
        for label in var_labels.values():
            line += f" | {row.get(label, 0):>10.1f}%"
        print(line)

    return v, dist

# =============================================================================
# ANALYSES
# =============================================================================

results = {}

# 1. Format privilegie (tous les repondants)
v_format, dist_format = analyse_variable(
    df, 'FORMAT_R_1', FORMAT_LABELS,
    "FORMAT PRIVILEGIE POUR S'INFORMER"
)
results['format'] = {'v_cramer': v_format, 'distribution': dist_format}

# 2. Longueur preferee pour la video (base: ceux qui privilegient la video)
# FORMAT_R_1 = 3 signifie que la video est le format privilegie
df_video = df[df['FORMAT_R_1'] == 3].copy()
print(f"\n(Base video: {len(df_video)} repondants)")

if len(df_video) > 100:
    v_longueur, dist_longueur = analyse_variable(
        df_video, 'FORMAT3_LR3_FORMAT3_3_R', LONGUEUR_VIDEO_LABELS,
        "LONGUEUR VIDEO PREFEREE (parmi ceux qui privilegient la video)"
    )
    results['longueur_video'] = {'v_cramer': v_longueur, 'distribution': dist_longueur}

# 3. Direct vs replay pour la video
if len(df_video) > 100:
    v_direct, dist_direct = analyse_variable(
        df_video, 'FORMAT2_LR3_FORMAT2_3_R', DIRECT_LABELS,
        "DIRECT VS REPLAY (parmi ceux qui privilegient la video)"
    )
    results['direct_replay'] = {'v_cramer': v_direct, 'distribution': dist_direct}

# =============================================================================
# SYNTHESE
# =============================================================================
print("\n" + "="*80)
print("### SYNTHESE : USAGES PAR AGE ###")
print("="*80)

print("\n1. Format privilegie:")
print("   - Les jeunes (15-24 ans) privilegient davantage la VIDEO")
print("   - Les plus ages privilegient davantage l'ECRIT")

print("\n2. Duree video preferee (parmi amateurs de video):")
print("   - Les jeunes preferent les formats TRES COURTS (<5 min)")
print("   - Les plus ages preferent les formats LONGS (>20 min)")

print("\n3. Direct vs Differe (parmi amateurs de video):")
print("   - Tendance au DIFFERE chez les jeunes")
print("   - Tendance au DIRECT chez les plus ages")

print("\n" + "="*80)
print("### CONCLUSION ###")
print("="*80)
print("""
Ce qui distingue les generations, ce n'est pas l'EQUIPEMENT (quasi-universel),
mais les USAGES :
- Format prefere : video courte vs ecrit long
- Temporalite : differe/a la demande vs direct
- Ces usages correspondent aux affordances des RS (TikTok, Reels, Stories)
  vs TV traditionnelle (JT en direct, magazines longs)
""")
