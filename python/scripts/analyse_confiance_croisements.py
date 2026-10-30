# -*- coding: utf-8 -*-
"""
Analyse croisements confiance journalistes/créateurs et attitudes sources
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

# Variables pratiques
df['PRATIQUE_RS'] = (df['NEWS1BIS_R'] == 8).astype(int)
df['PRATIQUE_TV'] = (df['NEWS1BIS_R'] == 1).astype(int)

def cramers_v(ct):
    chi2 = stats.chi2_contingency(ct)[0]
    n = ct.sum().sum()
    min_dim = min(ct.shape) - 1
    return np.sqrt(chi2 / (n * min_dim)) if min_dim > 0 and n > 0 else 0

# Explorer colonnes disponibles
print("\n=== COLONNES INF3 ===")
inf3_cols = [c for c in df.columns if 'INF3' in c]
print(inf3_cols[:20])

print("\n=== COLONNES ATTSOURCES ===")
att_cols = [c for c in df.columns if 'ATTSOURCES' in c]
print(att_cols[:20])

print("\n=== COLONNES VALEURJ ===")
val_cols = [c for c in df.columns if 'VALEURJ' in c]
print(val_cols[:20])

# ============================================================================
# INF3 - CONFIANCE JOURNALISTES vs CREATEURS
# ============================================================================
print("\n" + "=" * 80)
print("CONFIANCE JOURNALISTES vs CREATEURS DE CONTENUS")
print("=" * 80)

# Chercher les colonnes pour journalistes (item 1) et créateurs (item 6)
# Format probable : INF3_R_1 pour journalistes, INF3_R_6 pour créateurs
# ou INF3_R1_1, INF3_R1_6 pour le récap ST Confiance

# Regardons les valeurs
for col in ['INF3_R_1', 'INF3_R_6', 'INF3_R1_1', 'INF3_R1_6']:
    if col in df.columns:
        print(f"\n{col}:")
        print(df[col].value_counts().head())

# Essayons avec les colonnes disponibles
# INF3_R1 = récap ST Confiance, donc 1 = confiance, autre = pas confiance
# Cherchons le format exact

print("\n--- Distribution confiance par pratique ---")

# Si INF3_R_1 existe (confiance journalistes brute)
if 'INF3_R_1' in df.columns:
    # 1-2 = confiance, 3-4 = pas confiance
    df['CONF_JOURNALISTES'] = df['INF3_R_1'].apply(
        lambda x: 'Confiance' if x in [1, 2] else ('Pas confiance' if x in [3, 4] else np.nan)
    )

    print("\n% Confiance journalistes selon pratique:")
    for prat, label in [('PRATIQUE_RS', 'RS principale'), ('PRATIQUE_TV', 'TV principale')]:
        for cat in ['Confiance', 'Pas confiance']:
            subset = df[(df[prat] == 1) & (df['CONF_JOURNALISTES'] == cat)]
            total_prat = df[df[prat] == 1]['POIDS03'].sum()
            n = subset['POIDS03'].sum()
            pct = n / total_prat * 100 if total_prat > 0 else 0
            print(f"  {label} + {cat}: {pct:.1f}%")

if 'INF3_R_6' in df.columns:
    df['CONF_CREATEURS'] = df['INF3_R_6'].apply(
        lambda x: 'Confiance' if x in [1, 2] else ('Pas confiance' if x in [3, 4] else np.nan)
    )

    print("\n% Confiance créateurs selon pratique:")
    for prat, label in [('PRATIQUE_RS', 'RS principale'), ('PRATIQUE_TV', 'TV principale')]:
        for cat in ['Confiance', 'Pas confiance']:
            subset = df[(df[prat] == 1) & (df['CONF_CREATEURS'] == cat)]
            total_prat = df[df[prat] == 1]['POIDS03'].sum()
            n = subset['POIDS03'].sum()
            pct = n / total_prat * 100 if total_prat > 0 else 0
            print(f"  {label} + {cat}: {pct:.1f}%")

# V de Cramer confiance journalistes - pratique RS
if 'INF3_R_1' in df.columns:
    mask = df['INF3_R_1'].notna() & df['PRATIQUE_RS'].notna()
    ct = pd.crosstab(df[mask]['INF3_R_1'], df[mask]['PRATIQUE_RS'],
                     values=df[mask]['POIDS03'], aggfunc='sum').fillna(0)
    v = cramers_v(ct) if ct.shape[0] >= 2 and ct.shape[1] >= 2 else 0
    print(f"\nV de Cramer (Conf journalistes - RS) : {v:.3f}")

if 'INF3_R_6' in df.columns:
    mask = df['INF3_R_6'].notna() & df['PRATIQUE_RS'].notna()
    ct = pd.crosstab(df[mask]['INF3_R_6'], df[mask]['PRATIQUE_RS'],
                     values=df[mask]['POIDS03'], aggfunc='sum').fillna(0)
    v = cramers_v(ct) if ct.shape[0] >= 2 and ct.shape[1] >= 2 else 0
    print(f"V de Cramer (Conf créateurs - RS) : {v:.3f}")

# ============================================================================
# ATTSOURCES - ATTITUDES SUR LES SOURCES
# ============================================================================
print("\n" + "=" * 80)
print("ATTITUDES SUR LES SOURCES D'INFORMATION")
print("=" * 80)

# Items interessants :
# 3 = Il y a rarement une seule vérité
# 6 = Les médias les plus connus sont les plus fiables
# 7 = Les commentaires sur les réseaux sociaux sont souvent très pertinents

ITEMS_ATTSOURCES = {
    3: "Rarement une seule verite",
    6: "Medias connus = fiables",
    7: "Commentaires RS pertinents",
    4: "Anonymes aussi fiables que journalistes"
}

for item_num, label in ITEMS_ATTSOURCES.items():
    col = f'ATTSOURCES_R_{item_num}'
    if col in df.columns:
        print(f"\n--- {label} ({col}) ---")
        print(df[col].value_counts().head())

        # Créer binaire : 1-2 = d'accord, 3-4 = pas d'accord
        df[f'ATT_{item_num}_ACCORD'] = df[col].apply(
            lambda x: 1 if x in [1, 2] else (0 if x in [3, 4] else np.nan)
        )

        # % d'accord selon pratique
        print(f"\n% d'accord selon pratique:")
        for prat, prat_label in [('PRATIQUE_RS', 'RS principale'), ('PRATIQUE_TV', 'TV principale'), (None, 'Ensemble')]:
            if prat:
                subset = df[df[prat] == 1]
            else:
                subset = df
            total = subset['POIDS03'].sum()
            n_accord = subset[subset[f'ATT_{item_num}_ACCORD'] == 1]['POIDS03'].sum()
            pct = n_accord / total * 100 if total > 0 else 0
            print(f"  {prat_label}: {pct:.1f}%")

        # V de Cramer
        mask = df[f'ATT_{item_num}_ACCORD'].notna() & df['PRATIQUE_RS'].notna()
        ct = pd.crosstab(df[mask][f'ATT_{item_num}_ACCORD'], df[mask]['PRATIQUE_RS'],
                         values=df[mask]['POIDS03'], aggfunc='sum').fillna(0)
        v = cramers_v(ct) if ct.shape[0] >= 2 and ct.shape[1] >= 2 else 0
        print(f"  V de Cramer (RS): {v:.3f}")

# ============================================================================
# VALEURJ - VISION DES JOURNALISTES
# ============================================================================
print("\n" + "=" * 80)
print("VISION DES JOURNALISTES (VALEURJ)")
print("=" * 80)

# Chercher les colonnes VALEURJ
for col in val_cols[:10]:
    if col in df.columns:
        print(f"\n{col}:")
        print(df[col].value_counts().head())

# Items VALEURJ (échelle 1-10, 1 = critique, 10 = favorable journalistes)
ITEMS_VALEURJ = {
    1: "Citoyens vs Journalistes",
    2: "N'importe qui vs Pro",
    3: "Nuisent vs Essentiels democratie",
    4: "Pensee dominante vs Diversite",
    5: "Audience vs Qualite"
}

for item_num, label in ITEMS_VALEURJ.items():
    col = f'VALEURJ_R_{item_num}'
    if col in df.columns:
        print(f"\n--- {label} ({col}) ---")

        # Moyenne selon pratique
        for prat, prat_label in [('PRATIQUE_RS', 'RS principale'), ('PRATIQUE_TV', 'TV principale')]:
            subset = df[df[prat] == 1]
            mask = subset[col].notna()
            if mask.sum() > 0:
                mean = np.average(subset[mask][col], weights=subset[mask]['POIDS03'])
                print(f"  {prat_label}: moyenne = {mean:.2f}/10")

        # V de Cramer (avec recodage en 3 catégories)
        df[f'VALEURJ_{item_num}_CAT'] = df[col].apply(
            lambda x: 'Critique' if x <= 4 else ('Neutre' if x <= 6 else 'Favorable') if pd.notna(x) else np.nan
        )

        mask = df[f'VALEURJ_{item_num}_CAT'].notna() & df['PRATIQUE_RS'].notna()
        ct = pd.crosstab(df[mask][f'VALEURJ_{item_num}_CAT'], df[mask]['PRATIQUE_RS'],
                         values=df[mask]['POIDS03'], aggfunc='sum').fillna(0)
        v = cramers_v(ct) if ct.shape[0] >= 2 and ct.shape[1] >= 2 else 0
        print(f"  V de Cramer (RS): {v:.3f}")

# ============================================================================
# RESUME
# ============================================================================
print("\n" + "=" * 80)
print("RESUME : PRISE DE RECUL SELON PRATIQUE")
print("=" * 80)
print("""
Questions clés :
1. Les utilisateurs RS font-ils confiance aux créateurs ? Plus qu'aux journalistes ?
2. Les utilisateurs TV font-ils plus confiance aux journalistes ?
3. Y a-t-il une "prise de recul" (esprit critique) différente selon la source ?
""")
