# -*- coding: utf-8 -*-
"""
Chapitre 01b - Analyse equipement - pratiques informationnelles
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
# CREATION DES VARIABLES BINAIRES D'EQUIPEMENT
# =============================================================================
print("\n" + "=" * 80)
print("### CREATION DES VARIABLES BINAIRES ###")
print("=" * 80)

equipements = {
    'POSSEDE_TV': ('RS16_R_1', 'Televiseur'),
    'POSSEDE_SMARTPHONE': ('RS16_R_4', 'Smartphone'),
    'POSSEDE_ORDI_PORTABLE': ('RS16_R_6', 'Ordinateur portable'),
    'POSSEDE_TABLETTE': ('RS16_R_7', 'Tablette'),
    'POSSEDE_MONTRE_CONNECTEE': ('RS16_R_11', 'Montre connectee'),
    'POSSEDE_ENCEINTE_CONNECTEE': ('RS16_R_9', 'Enceinte connectee'),
}

for new_var, (source_var, label) in equipements.items():
    if source_var in df.columns:
        # Possede = 1 ou 2 (un ou plusieurs)
        df[new_var] = (df[source_var].isin([1, 2])).astype(int)
        pct = df[df[new_var] == 1]['POIDS03'].sum() / df['POIDS03'].sum() * 100
        print(f"{new_var}: {pct:.1f}% possedent")

# =============================================================================
# CREATION DES VARIABLES BINAIRES DE PRATIQUES
# =============================================================================
print("\n" + "=" * 80)
print("### CREATION DES VARIABLES DE PRATIQUES ###")
print("=" * 80)

# NEWS1BIS_R : source principale
# 2 = TV, 8 = RS
df['PRATIQUE_TV_PRINCIPALE'] = (df['NEWS1BIS_R'] == 2).astype(int)
df['PRATIQUE_RS_PRINCIPALE'] = (df['NEWS1BIS_R'] == 8).astype(int)

pct_tv = df[df['PRATIQUE_TV_PRINCIPALE'] == 1]['POIDS03'].sum() / df['POIDS03'].sum() * 100
pct_rs = df[df['PRATIQUE_RS_PRINCIPALE'] == 1]['POIDS03'].sum() / df['POIDS03'].sum() * 100
print(f"TV comme source principale : {pct_tv:.1f}%")
print(f"RS comme source principale : {pct_rs:.1f}%")

# =============================================================================
# FONCTIONS STATISTIQUES
# =============================================================================

def cramers_v(ct):
    """Calcule V de Cramer sur tableau de contingence"""
    chi2 = stats.chi2_contingency(ct)[0]
    n = ct.sum().sum()
    min_dim = min(ct.shape) - 1
    return np.sqrt(chi2 / (n * min_dim)) if min_dim > 0 and n > 0 else 0

def get_chi2_stats(df, var1, var2, poids='POIDS03'):
    """Calcule Chi2 et V de Cramer avec ponderation"""
    mask = df[var1].notna() & df[var2].notna() & df[poids].notna()
    df_valid = df[mask]

    ct = pd.crosstab(
        df_valid[var1],
        df_valid[var2],
        values=df_valid[poids],
        aggfunc='sum'
    ).fillna(0)

    if ct.shape[0] < 2 or ct.shape[1] < 2:
        return None

    chi2, p, dof, _ = stats.chi2_contingency(ct)
    v = cramers_v(ct)

    return {
        'chi2': round(chi2, 1),
        'p': p,
        'dof': int(dof),
        'v_cramer': round(v, 3)
    }

def get_distribution(df, var_vi, var_vd, poids='POIDS03'):
    """Calcule la distribution de var_vd selon var_vi"""
    results = []
    for val in sorted(df[var_vi].dropna().unique()):
        subset = df[df[var_vi] == val]
        total = subset[poids].sum()
        oui = subset[subset[var_vd] == 1][poids].sum()
        pct = oui / total * 100 if total > 0 else 0
        results.append({'category': int(val), 'pct_oui': round(pct, 1)})
    return results

# =============================================================================
# V DE CRAMER : EQUIPEMENT - PRATIQUES
# =============================================================================
print("\n" + "=" * 80)
print("### V DE CRAMER : EQUIPEMENT <-> PRATIQUES ###")
print("=" * 80)

vi_vars = [
    ('POSSEDE_TV', 'Possede TV'),
    ('POSSEDE_SMARTPHONE', 'Possede smartphone'),
    ('POSSEDE_ORDI_PORTABLE', 'Possede ordi portable'),
    ('POSSEDE_TABLETTE', 'Possede tablette'),
    ('POSSEDE_MONTRE_CONNECTEE', 'Possede montre connectee'),
    ('POSSEDE_ENCEINTE_CONNECTEE', 'Possede enceinte connectee'),
]

vd_vars = [
    ('PRATIQUE_TV_PRINCIPALE', 'TV source principale'),
    ('PRATIQUE_RS_PRINCIPALE', 'RS source principale'),
]

print("\n### EQUIPEMENT -> TV COMME SOURCE PRINCIPALE ###\n")
print(f"{'Equipement':<30} | V Cramer | Chi2    | p-value | Signif")
print("-" * 70)

results_tv = []
for var_vi, label_vi in vi_vars:
    stat = get_chi2_stats(df, var_vi, 'PRATIQUE_TV_PRINCIPALE')
    if stat:
        signif = "***" if stat['p'] < 0.001 else "**" if stat['p'] < 0.01 else "*" if stat['p'] < 0.05 else ""
        print(f"{label_vi:<30} | {stat['v_cramer']:.3f}    | {stat['chi2']:<7.1f} | {stat['p']:.4f}  | {signif}")

        # Distribution
        dist = get_distribution(df, var_vi, 'PRATIQUE_TV_PRINCIPALE')
        results_tv.append({
            'var_vi': var_vi,
            'label_vi': label_vi,
            'v_cramer': stat['v_cramer'],
            'chi2': stat['chi2'],
            'p': stat['p'],
            'pct_non_possede': dist[0]['pct_oui'] if len(dist) > 0 else None,
            'pct_possede': dist[1]['pct_oui'] if len(dist) > 1 else None,
        })

print("\n### EQUIPEMENT -> RS COMME SOURCE PRINCIPALE ###\n")
print(f"{'Equipement':<30} | V Cramer | Chi2    | p-value | Signif")
print("-" * 70)

results_rs = []
for var_vi, label_vi in vi_vars:
    stat = get_chi2_stats(df, var_vi, 'PRATIQUE_RS_PRINCIPALE')
    if stat:
        signif = "***" if stat['p'] < 0.001 else "**" if stat['p'] < 0.01 else "*" if stat['p'] < 0.05 else ""
        print(f"{label_vi:<30} | {stat['v_cramer']:.3f}    | {stat['chi2']:<7.1f} | {stat['p']:.4f}  | {signif}")

        dist = get_distribution(df, var_vi, 'PRATIQUE_RS_PRINCIPALE')
        results_rs.append({
            'var_vi': var_vi,
            'label_vi': label_vi,
            'v_cramer': stat['v_cramer'],
            'chi2': stat['chi2'],
            'p': stat['p'],
            'pct_non_possede': dist[0]['pct_oui'] if len(dist) > 0 else None,
            'pct_possede': dist[1]['pct_oui'] if len(dist) > 1 else None,
        })

# =============================================================================
# TABLEAUX CROISES DETAILLES
# =============================================================================
print("\n" + "=" * 80)
print("### TABLEAUX CROISES DETAILLES ###")
print("=" * 80)

print("\n--- TV source principale selon possession TV ---")
for possede in [0, 1]:
    subset = df[df['POSSEDE_TV'] == possede]
    pct = subset[subset['PRATIQUE_TV_PRINCIPALE'] == 1]['POIDS03'].sum() / subset['POIDS03'].sum() * 100
    label = "Possede TV" if possede == 1 else "Ne possede pas TV"
    print(f"  {label}: {pct:.1f}% utilisent TV comme source principale")

print("\n--- RS source principale selon possession smartphone ---")
for possede in [0, 1]:
    subset = df[df['POSSEDE_SMARTPHONE'] == possede]
    pct = subset[subset['PRATIQUE_RS_PRINCIPALE'] == 1]['POIDS03'].sum() / subset['POIDS03'].sum() * 100
    label = "Possede smartphone" if possede == 1 else "Ne possede pas smartphone"
    print(f"  {label}: {pct:.1f}% utilisent RS comme source principale")

print("\n--- TV source principale selon possession smartphone ---")
for possede in [0, 1]:
    subset = df[df['POSSEDE_SMARTPHONE'] == possede]
    pct = subset[subset['PRATIQUE_TV_PRINCIPALE'] == 1]['POIDS03'].sum() / subset['POIDS03'].sum() * 100
    label = "Possede smartphone" if possede == 1 else "Ne possede pas smartphone"
    print(f"  {label}: {pct:.1f}% utilisent TV comme source principale")

# =============================================================================
# COMPARAISON AVEC L'AGE (pour reference)
# =============================================================================
print("\n" + "=" * 80)
print("### COMPARAISON AVEC L'AGE ###")
print("=" * 80)

stat_age_tv = get_chi2_stats(df, 'RS2C_RECODE_AG_R', 'PRATIQUE_TV_PRINCIPALE')
stat_age_rs = get_chi2_stats(df, 'RS2C_RECODE_AG_R', 'PRATIQUE_RS_PRINCIPALE')

print(f"\nAge -> TV principale   : V = {stat_age_tv['v_cramer']:.3f}")
print(f"Age -> RS principale   : V = {stat_age_rs['v_cramer']:.3f}")

# =============================================================================
# RESUME POUR EFFET NET
# =============================================================================
print("\n" + "=" * 80)
print("### RESUME - CROISEMENTS SIGNIFICATIFS ###")
print("=" * 80)

print("\nCroisements avec V de Cramer > 0.10 :")
print("\nPour TV source principale :")
for r in sorted(results_tv, key=lambda x: -x['v_cramer']):
    if r['v_cramer'] >= 0.10:
        ecart = r['pct_possede'] - r['pct_non_possede'] if r['pct_possede'] and r['pct_non_possede'] else 0
        print(f"  {r['label_vi']}: V={r['v_cramer']:.3f}, ecart={ecart:+.1f} pts")

print("\nPour RS source principale :")
for r in sorted(results_rs, key=lambda x: -x['v_cramer']):
    if r['v_cramer'] >= 0.10:
        ecart = r['pct_possede'] - r['pct_non_possede'] if r['pct_possede'] and r['pct_non_possede'] else 0
        print(f"  {r['label_vi']}: V={r['v_cramer']:.3f}, ecart={ecart:+.1f} pts")
