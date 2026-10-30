# -*- coding: utf-8 -*-
"""
Analyse des motivations d'utiliser les RS pour s'informer (MOTIVRS_R)
Structure : MOTIVRS_R_1 = 1ere motivation citee (valeur = numero 1-12)
"""
import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path

BASE_DIR = Path('python')
DATA_DIR = BASE_DIR / 'data' / 'francais-information'

print("Chargement des donnees...")
df = pd.read_excel(DATA_DIR / 'base-info-arcom.xlsx')
df['POIDS03'] = df['POIDS03'].astype(str).str.replace(',', '.').astype(float)

AGE_LABELS = {
    1: '15-17 ans', 2: '18-24 ans', 3: '25-34 ans', 4: '35-44 ans',
    5: '45-59 ans', 6: '60-69 ans', 7: '70 ans et +'
}

MOTIVRS_LABELS = {
    1: "Info vient facilement",
    2: "Temps reel",
    3: "Plusieurs sources",
    4: "Opinions des autres",
    5: "Formats courts (video, images)",
    6: "Info pas ailleurs",
    7: "Liberte expression",
    8: "Passe bcp temps sur RS",
    9: "Info qui m'interesse",
    10: "Commenter/discuter",
    11: "Plus fiable qu'ailleurs",
    12: "Autre"
}

# Base : ceux qui ont repondu a la question (au moins 1 motivation)
df_rs = df[df['MOTIVRS_R_1'].notna()].copy()
print(f"Base : {len(df_rs)} utilisateurs RS ayant cite au moins 1 motivation")
total_poids = df_rs['POIDS03'].sum()

# Creer des variables binaires pour chaque motivation
# (cite en 1er, 2eme ou 3eme rang)
for motiv_num in range(1, 13):
    col_name = f"CITE_MOTIV_{motiv_num}"
    df_rs[col_name] = (
        (df_rs['MOTIVRS_R_1'] == motiv_num) |
        (df_rs['MOTIVRS_R_2'] == motiv_num) |
        (df_rs['MOTIVRS_R_3'] == motiv_num)
    ).astype(int)

# =============================================================================
# DISTRIBUTION GLOBALE
# =============================================================================
print("\n" + "="*80)
print("MOTIVATIONS LES PLUS CITEES (rang 1, 2 ou 3)")
print("="*80)

results = []
for motiv_num in range(1, 13):
    col = f"CITE_MOTIV_{motiv_num}"
    n_cite = df_rs[df_rs[col] == 1]['POIDS03'].sum()
    pct = n_cite / total_poids * 100
    results.append({
        'num': motiv_num,
        'label': MOTIVRS_LABELS[motiv_num],
        'pct': pct
    })

results = sorted(results, key=lambda x: -x['pct'])

print(f"\n{'Rang':<5} {'Motivation':<40} {'%':>8}")
print("-" * 55)
for i, r in enumerate(results, 1):
    print(f"{i:<5} {r['label']:<40} {r['pct']:>7.1f}%")

# =============================================================================
# ANALYSE PAR AGE
# =============================================================================
print("\n" + "="*80)
print("MOTIVATIONS SELON L'AGE")
print("="*80)

def cramers_v(ct):
    chi2 = stats.chi2_contingency(ct)[0]
    n = ct.sum().sum()
    min_dim = min(ct.shape) - 1
    return np.sqrt(chi2 / (n * min_dim)) if min_dim > 0 and n > 0 else 0

print(f"\n{'Motivation':<35} | V Cramer | 15-24 | 45-59 | 70+  | Ecart J-V")
print("-" * 85)

age_results = []
for r in results[:11]:  # Top 11 (excl. Autre)
    motiv_num = r['num']
    col = f"CITE_MOTIV_{motiv_num}"

    # V de Cramer
    mask = df_rs[col].notna() & df_rs['RS2C_RECODE_AG_R'].notna()
    ct = pd.crosstab(
        df_rs[mask]['RS2C_RECODE_AG_R'],
        df_rs[mask][col],
        values=df_rs[mask]['POIDS03'],
        aggfunc='sum'
    ).fillna(0)

    v = cramers_v(ct) if ct.shape[0] >= 2 and ct.shape[1] >= 2 else 0

    # % par age
    pct_by_age = {}
    for age_code in range(1, 8):
        subset = df_rs[df_rs['RS2C_RECODE_AG_R'] == age_code]
        total = subset['POIDS03'].sum()
        n_cite = subset[subset[col] == 1]['POIDS03'].sum()
        pct_by_age[age_code] = n_cite / total * 100 if total > 0 else 0

    # 15-24 ans (moyenne 1 et 2)
    pct_jeunes = (pct_by_age[1] + pct_by_age[2]) / 2
    pct_45_59 = pct_by_age[5]
    pct_70 = pct_by_age[7]
    ecart = pct_jeunes - pct_70

    age_results.append({
        'num': motiv_num,
        'label': r['label'],
        'v_cramer': v,
        'pct_jeunes': pct_jeunes,
        'pct_45_59': pct_45_59,
        'pct_70': pct_70,
        'ecart': ecart,
        'pct_by_age': pct_by_age
    })

    print(f"{r['label']:<35} | {v:>7.3f}  | {pct_jeunes:>5.1f} | {pct_45_59:>5.1f} | {pct_70:>4.1f} | {ecart:>+6.1f}")

# =============================================================================
# TOP DIFFERENCES GENERATIONNELLES
# =============================================================================
print("\n" + "="*80)
print("TOP DIFFERENCES GENERATIONNELLES (15-24 vs 70+)")
print("="*80)

# Plus fort chez les jeunes
print("\n>>> Plus fort chez les JEUNES:")
jeunes_plus = sorted(age_results, key=lambda x: -x['ecart'])[:5]
for r in jeunes_plus:
    if r['ecart'] > 5:
        print(f"  {r['label']}: {r['pct_jeunes']:.0f}% (15-24) vs {r['pct_70']:.0f}% (70+) = +{r['ecart']:.0f} pts")

# Plus fort chez les seniors
print("\n>>> Plus fort chez les SENIORS:")
seniors_plus = sorted(age_results, key=lambda x: x['ecart'])[:5]
for r in seniors_plus:
    if r['ecart'] < -5:
        print(f"  {r['label']}: {r['pct_70']:.0f}% (70+) vs {r['pct_jeunes']:.0f}% (15-24) = {r['ecart']:.0f} pts")

# =============================================================================
# DETAIL AGE POUR LES MOTIVATIONS CLES
# =============================================================================
print("\n" + "="*80)
print("DETAIL PAR AGE - MOTIVATIONS CLES")
print("="*80)

key_motivs = [5, 8, 10, 1, 2]  # Formats courts, temps passe, commenter, facilite, temps reel

for motiv_num in key_motivs:
    r = next((x for x in age_results if x['num'] == motiv_num), None)
    if r:
        print(f"\n{MOTIVRS_LABELS[motiv_num]} (V={r['v_cramer']:.3f}):")
        for age_code in range(1, 8):
            pct = r['pct_by_age'][age_code]
            bar = "=" * int(pct / 2)
            print(f"  {AGE_LABELS[age_code]:<12}: {pct:>5.1f}% {bar}")

print("\n" + "="*80)
print("INTERPRETATION")
print("="*80)
print("""
Les motivations revelent des rapports differents a l'information :

JEUNES (15-24) :
- "Info vient facilement" : consommation passive, flux algorithmique
- "Formats courts" : adaptes au scroll, attention fragmentee
- "Je passe bcp de temps sur RS" : usage intensif, RS = environnement quotidien

SENIORS (70+) :
- "Temps reel" : info immediate, modele JT/chaines info
- "Plusieurs sources" : verification, pluralisme
- "Commenter/discuter" : engagement deliberatif

=> Deux RAPPORTS a l'info : flux passif (jeunes) vs engagement actif (seniors)
""")
