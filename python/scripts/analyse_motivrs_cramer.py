# -*- coding: utf-8 -*-
"""
Analyse V de Cramer : MOTIVRS_R (12 motivations) vs BASCULEMENT
Réutilise la logique de generate_chapitre_01.py
"""
import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path

BASE_DIR = Path('python')
DATA_DIR = BASE_DIR / 'data' / 'francais-information'

# ============================================
# CHARGEMENT (copié de generate_chapitre_01.py)
# ============================================
print("Chargement des données...")
df = pd.read_excel(DATA_DIR / 'base-info-arcom.xlsx')
if df['POIDS03'].dtype == 'object':
    df['POIDS03'] = df['POIDS03'].str.replace(',', '.').astype(float)
else:
    df['POIDS03'] = pd.to_numeric(df['POIDS03'], errors='coerce').fillna(1)

# ============================================
# CONSTRUCTION BASCULEMENT (copié de generate_chapitre_01.py)
# ============================================
trad_tv = (df['NEWS1BIS_R'] == 2) & (df['NEWS1_2B_R'] == 1)
trad_radio = (df['NEWS1BIS_R'] == 1) & (df['NEWS1_1B_R'] == 1)
trad_presse = (df['NEWS1BIS_R'] == 3) & (df['NEWS1_3B_R'] == 2)
traditionnel_pur = trad_tv | trad_radio | trad_presse

num_tv = (df['NEWS1BIS_R'] == 2) & (df['NEWS1_2B_R'] == 2)
num_radio = (df['NEWS1BIS_R'] == 1) & (df['NEWS1_1B_R'].isin([2, 3]))
num_presse = (df['NEWS1BIS_R'] == 3) & (df['NEWS1_3B_R'] == 1)
num_pure_player = (df['NEWS1BIS_R'] == 5)
num_moteur = (df['NEWS1BIS_R'] == 6)
num_portail = (df['NEWS1BIS_R'] == 7)
num_rs = (df['NEWS1BIS_R'] == 8)
num_youtube = (df['NEWS1BIS_R'] == 9)
numerique = num_tv | num_radio | num_presse | num_pure_player | num_moteur | num_portail | num_rs | num_youtube

df['BASCULEMENT'] = np.nan
df.loc[traditionnel_pur, 'BASCULEMENT'] = 0
df.loc[numerique, 'BASCULEMENT'] = 1

# Créer AGE (copié de generate_chapitre_01.py)
df['AGE'] = df['RS2C_RECODE_AG_R']

# Créer DIPLOME_REGROUPE
def regroup_diplome(val):
    if pd.isna(val): return np.nan
    if val in [1, 2, 3]: return 'Bas'
    if val in [4, 5]: return 'Moyen'
    return 'Superieur'
df['DIPLOME_REGROUPE'] = df['RS5_R'].apply(regroup_diplome)

print(f"Traditionnel: {(df['BASCULEMENT'] == 0).sum()}")
print(f"Numérique: {(df['BASCULEMENT'] == 1).sum()}")

# ============================================
# LABELS MOTIVRS_R
# ============================================
motivrs_labels = {
    1: "L'info vient facilement à moi",
    2: "Infos en temps réel",
    3: "Grand nombre de sources",
    4: "Opinions des autres",
    5: "Formats courts (vidéo, images)",
    6: "Infos introuvables ailleurs",
    7: "Liberté d'expression",
    8: "Je passe du temps sur RS",
    9: "Infos qui m'intéressent",
    10: "Commenter et discuter",
    11: "RS plus fiables qu'ailleurs",
    12: "Autre"
}

# ============================================
# CRÉER VARIABLES BINAIRES MOTIVRS
# ============================================
motiv_cols = [c for c in df.columns if c.startswith('MOTIVRS_R_')]
print(f"\nColonnes MOTIVRS trouvées: {len(motiv_cols)}")

for code in motivrs_labels.keys():
    df[f'MOTIV_{code}'] = df.apply(
        lambda r: 1 if any(pd.notna(r[c]) and r[c] == code for c in motiv_cols) else 0,
        axis=1
    )

# ============================================
# FONCTION V DE CRAMER
# ============================================
def cramers_v_weighted(x, y, weights):
    ct = pd.crosstab(x, y, values=weights, aggfunc='sum').fillna(0)
    chi2, p, dof, _ = stats.chi2_contingency(ct)
    n = ct.sum().sum()
    min_dim = min(ct.shape) - 1
    if min_dim == 0:
        return 0, 1, 0
    v = np.sqrt(chi2 / (n * min_dim))
    return v, chi2, p

# ============================================
# ANALYSE V DE CRAMER POUR CHAQUE MOTIVATION
# ============================================
print("\n" + "=" * 100)
print("V DE CRAMER : MOTIVRS vs BASCULEMENT (Numérique/Traditionnel)")
print("=" * 100)

results = []
for code, label in motivrs_labels.items():
    var = f'MOTIV_{code}'
    mask = df[var].notna() & df['BASCULEMENT'].notna()

    if mask.sum() < 100:
        continue

    v, chi2, p = cramers_v_weighted(df.loc[mask, var], df.loc[mask, 'BASCULEMENT'], df.loc[mask, 'POIDS03'])

    # % numérique pour ceux qui citent vs ne citent pas
    mask_oui = mask & (df[var] == 1)
    mask_non = mask & (df[var] == 0)

    if mask_oui.sum() > 0 and mask_non.sum() > 0:
        pct_num_oui = (df.loc[mask_oui, 'BASCULEMENT'] * df.loc[mask_oui, 'POIDS03']).sum() / df.loc[mask_oui, 'POIDS03'].sum() * 100
        pct_num_non = (df.loc[mask_non, 'BASCULEMENT'] * df.loc[mask_non, 'POIDS03']).sum() / df.loc[mask_non, 'POIDS03'].sum() * 100
        ecart = pct_num_oui - pct_num_non
        n_oui = mask_oui.sum()

        results.append({
            'code': code,
            'label': label,
            'v_cramer': v,
            'p_value': p,
            'pct_num_oui': pct_num_oui,
            'pct_num_non': pct_num_non,
            'ecart': ecart,
            'n_oui': n_oui,
            'significatif': p < 0.05
        })

# Trier par V de Cramer décroissant
results = sorted(results, key=lambda x: x['v_cramer'], reverse=True)

print(f"\n{'Code':<5} {'Motivation':<35} {'V':<7} {'%Num SI OUI':<12} {'%Num SI NON':<12} {'Écart':<8} {'N':<6}")
print("-" * 95)
for r in results:
    sig = "***" if r['p_value'] < 0.001 else "**" if r['p_value'] < 0.01 else "*" if r['p_value'] < 0.05 else ""
    print(f"{r['code']:<5} {r['label']:<35} {r['v_cramer']:.3f}   {r['pct_num_oui']:>6.1f}%      {r['pct_num_non']:>6.1f}%      {r['ecart']:>+5.1f}   {r['n_oui']:<6} {sig}")

# ============================================
# TOP 5 POUR ANALYSE STRATIFIÉE
# ============================================
print("\n" + "=" * 100)
print("TOP 5 MOTIVATIONS - À STRATIFIER PAR ÂGE ET DIPLÔME")
print("=" * 100)

top5 = results[:5]
for r in top5:
    print(f"\n{r['code']}. {r['label']} (V={r['v_cramer']:.3f})")
    print(f"   - Ceux qui citent cette motivation: {r['pct_num_oui']:.1f}% numeriques")
    print(f"   - Ceux qui ne citent pas: {r['pct_num_non']:.1f}% numeriques")
    print(f"   - Ecart: {r['ecart']:+.1f} points")

# ============================================
# ANALYSE STRATIFIÉE PAR ÂGE
# ============================================
print("\n" + "=" * 100)
print("ANALYSE STRATIFIÉE PAR ÂGE (Top 5 motivations)")
print("=" * 100)

AGE_STRATES = {
    'jeunes': {'label': '15-34 ans', 'codes': [1, 2, 3]},
    'milieu': {'label': '35-59 ans', 'codes': [4, 5]},
    'seniors': {'label': '60+ ans', 'codes': [6, 7]}
}

for r in top5:
    var = f"MOTIV_{r['code']}"
    print(f"\n{r['label']}:")
    for strate_key, strate_info in AGE_STRATES.items():
        mask = df['AGE'].isin(strate_info['codes']) & df[var].notna() & df['BASCULEMENT'].notna()
        if mask.sum() < 50:
            continue

        mask_oui = mask & (df[var] == 1)
        mask_non = mask & (df[var] == 0)

        if mask_oui.sum() > 10 and mask_non.sum() > 10:
            pct_oui = (df.loc[mask_oui, 'BASCULEMENT'] * df.loc[mask_oui, 'POIDS03']).sum() / df.loc[mask_oui, 'POIDS03'].sum() * 100
            pct_non = (df.loc[mask_non, 'BASCULEMENT'] * df.loc[mask_non, 'POIDS03']).sum() / df.loc[mask_non, 'POIDS03'].sum() * 100
            ecart = pct_oui - pct_non
            print(f"   {strate_info['label']:<12}: {ecart:>+5.1f} pts  (OUI={pct_oui:.0f}%, NON={pct_non:.0f}%)")

# ============================================
# ANALYSE STRATIFIÉE PAR DIPLÔME
# ============================================
print("\n" + "=" * 100)
print("ANALYSE STRATIFIÉE PAR DIPLÔME (Top 5 motivations)")
print("=" * 100)

DIPLOME_STRATES = {
    'bas': {'label': 'Peu diplômé', 'codes': ['Bas']},
    'moyen': {'label': 'Bac/Bac+2', 'codes': ['Moyen']},
    'sup': {'label': 'Bac+3+', 'codes': ['Superieur']}
}

for r in top5:
    var = f"MOTIV_{r['code']}"
    print(f"\n{r['label']}:")
    for strate_key, strate_info in DIPLOME_STRATES.items():
        mask = df['DIPLOME_REGROUPE'].isin(strate_info['codes']) & df[var].notna() & df['BASCULEMENT'].notna()
        if mask.sum() < 50:
            continue

        mask_oui = mask & (df[var] == 1)
        mask_non = mask & (df[var] == 0)

        if mask_oui.sum() > 10 and mask_non.sum() > 10:
            pct_oui = (df.loc[mask_oui, 'BASCULEMENT'] * df.loc[mask_oui, 'POIDS03']).sum() / df.loc[mask_oui, 'POIDS03'].sum() * 100
            pct_non = (df.loc[mask_non, 'BASCULEMENT'] * df.loc[mask_non, 'POIDS03']).sum() / df.loc[mask_non, 'POIDS03'].sum() * 100
            ecart = pct_oui - pct_non
            print(f"   {strate_info['label']:<12}: {ecart:>+5.1f} pts  (OUI={pct_oui:.0f}%, NON={pct_non:.0f}%)")
