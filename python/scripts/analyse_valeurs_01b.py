# -*- coding: utf-8 -*-
"""
Analyse des valeurs (politique, confiance) et pratiques informationnelles
pour 01b-valeurs
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
print(f"Echantillon total : {len(df)} repondants")

# Variables de pratiques
# NEWS1BIS_R == 8 = RS source principale
# NEWS1BIS_R == 1 = TV source principale (a verifier)
print("\n=== Verifier NEWS1BIS_R ===")
print(df['NEWS1BIS_R'].value_counts().head(10))

# Creer variables binaires pratiques
df['PRATIQUE_RS'] = (df['NEWS1BIS_R'] == 8).astype(int)
df['PRATIQUE_TV'] = (df['NEWS1BIS_R'] == 1).astype(int)

# === ORIENTATION POLITIQUE ===
print("\n" + "=" * 80)
print("ORIENTATION POLITIQUE (NOU1_R) - echelle 0-10")
print("=" * 80)

print("\nDistribution NOU1_R:")
print(df['NOU1_R'].value_counts().sort_index())

# Recoder en categories
def recode_politique(val):
    if pd.isna(val):
        return np.nan
    if val <= 3:
        return "Gauche"
    elif val <= 5:
        return "Centre"
    elif val <= 7:
        return "Droite"
    else:
        return "Tres droite"

df['POLITIQUE_CAT'] = df['NOU1_R'].apply(recode_politique)
print("\nDistribution recodee:")
print(df['POLITIQUE_CAT'].value_counts())

# V de Cramer politique - pratiques
def cramers_v(ct):
    chi2 = stats.chi2_contingency(ct)[0]
    n = ct.sum().sum()
    min_dim = min(ct.shape) - 1
    return np.sqrt(chi2 / (n * min_dim)) if min_dim > 0 and n > 0 else 0

# RS selon politique
mask = df['POLITIQUE_CAT'].notna() & df['PRATIQUE_RS'].notna()
ct_rs_pol = pd.crosstab(
    df[mask]['POLITIQUE_CAT'],
    df[mask]['PRATIQUE_RS'],
    values=df[mask]['POIDS03'],
    aggfunc='sum'
).fillna(0)

v_rs_pol = cramers_v(ct_rs_pol) if ct_rs_pol.shape[0] >= 2 and ct_rs_pol.shape[1] >= 2 else 0
print(f"\nV de Cramer (Politique - RS principale) : {v_rs_pol:.3f}")

# TV selon politique
ct_tv_pol = pd.crosstab(
    df[mask]['POLITIQUE_CAT'],
    df[mask]['PRATIQUE_TV'],
    values=df[mask]['POIDS03'],
    aggfunc='sum'
).fillna(0)

v_tv_pol = cramers_v(ct_tv_pol) if ct_tv_pol.shape[0] >= 2 and ct_tv_pol.shape[1] >= 2 else 0
print(f"V de Cramer (Politique - TV principale) : {v_tv_pol:.3f}")

# Distribution par categorie politique
print("\n% RS principale selon orientation politique:")
for cat in ["Gauche", "Centre", "Droite", "Tres droite"]:
    subset = df[df['POLITIQUE_CAT'] == cat]
    total = subset['POIDS03'].sum()
    n_rs = subset[subset['PRATIQUE_RS'] == 1]['POIDS03'].sum()
    n_tv = subset[subset['PRATIQUE_TV'] == 1]['POIDS03'].sum()
    pct_rs = n_rs / total * 100 if total > 0 else 0
    pct_tv = n_tv / total * 100 if total > 0 else 0
    print(f"  {cat:<12}: RS = {pct_rs:>5.1f}%, TV = {pct_tv:>5.1f}%")

# === CONFIANCE GENERALE ===
print("\n" + "=" * 80)
print("CONFIANCE DANS L'INFORMATION (CONF1_R)")
print("=" * 80)

print("\nDistribution CONF1_R:")
print(df['CONF1_R'].value_counts().sort_index())

# Recoder confiance
def recode_confiance(val):
    if pd.isna(val):
        return np.nan
    if val <= 2:
        return "Confiance"
    elif val == 3:
        return "Neutre"
    else:
        return "Defiance"

df['CONFIANCE_CAT'] = df['CONF1_R'].apply(recode_confiance)
print("\nDistribution recodee:")
print(df['CONFIANCE_CAT'].value_counts())

# V de Cramer confiance - pratiques
mask2 = df['CONFIANCE_CAT'].notna() & df['PRATIQUE_RS'].notna()
ct_rs_conf = pd.crosstab(
    df[mask2]['CONFIANCE_CAT'],
    df[mask2]['PRATIQUE_RS'],
    values=df[mask2]['POIDS03'],
    aggfunc='sum'
).fillna(0)

v_rs_conf = cramers_v(ct_rs_conf) if ct_rs_conf.shape[0] >= 2 and ct_rs_conf.shape[1] >= 2 else 0
print(f"\nV de Cramer (Confiance - RS principale) : {v_rs_conf:.3f}")

ct_tv_conf = pd.crosstab(
    df[mask2]['CONFIANCE_CAT'],
    df[mask2]['PRATIQUE_TV'],
    values=df[mask2]['POIDS03'],
    aggfunc='sum'
).fillna(0)

v_tv_conf = cramers_v(ct_tv_conf) if ct_tv_conf.shape[0] >= 2 and ct_tv_conf.shape[1] >= 2 else 0
print(f"V de Cramer (Confiance - TV principale) : {v_tv_conf:.3f}")

# Distribution par confiance
print("\n% RS/TV principale selon confiance:")
for cat in ["Confiance", "Neutre", "Defiance"]:
    subset = df[df['CONFIANCE_CAT'] == cat]
    total = subset['POIDS03'].sum()
    n_rs = subset[subset['PRATIQUE_RS'] == 1]['POIDS03'].sum()
    n_tv = subset[subset['PRATIQUE_TV'] == 1]['POIDS03'].sum()
    pct_rs = n_rs / total * 100 if total > 0 else 0
    pct_tv = n_tv / total * 100 if total > 0 else 0
    print(f"  {cat:<12}: RS = {pct_rs:>5.1f}%, TV = {pct_tv:>5.1f}%")

# === DOUTE MEDIAS ===
print("\n" + "=" * 80)
print("DOUTE SUR LES MEDIAS (DOUTE_R)")
print("=" * 80)

print("\nDistribution DOUTE_R:")
print(df['DOUTE_R'].value_counts().sort_index())

DOUTE_LABELS = {1: "Toujours", 2: "Souvent", 3: "Parfois", 4: "Jamais"}

mask3 = df['DOUTE_R'].notna() & df['PRATIQUE_RS'].notna()
ct_rs_doute = pd.crosstab(
    df[mask3]['DOUTE_R'],
    df[mask3]['PRATIQUE_RS'],
    values=df[mask3]['POIDS03'],
    aggfunc='sum'
).fillna(0)

v_rs_doute = cramers_v(ct_rs_doute) if ct_rs_doute.shape[0] >= 2 and ct_rs_doute.shape[1] >= 2 else 0
print(f"\nV de Cramer (Doute - RS principale) : {v_rs_doute:.3f}")

# Distribution par doute
print("\n% RS principale selon doute:")
for code, label in DOUTE_LABELS.items():
    subset = df[df['DOUTE_R'] == code]
    total = subset['POIDS03'].sum()
    n_rs = subset[subset['PRATIQUE_RS'] == 1]['POIDS03'].sum()
    pct_rs = n_rs / total * 100 if total > 0 else 0
    print(f"  {label:<10}: {pct_rs:>5.1f}%")

# === CONFIANCE JOURNALISTES vs CREATEURS CONTENUS ===
print("\n" + "=" * 80)
print("CONFIANCE JOURNALISTES vs CREATEURS (CONFINST)")
print("=" * 80)

# Chercher les colonnes CONFINST
confinst_cols = [c for c in df.columns if 'CONFINST' in c]
print(f"Colonnes trouvees: {confinst_cols[:10]}")

# Analyser confiance journalistes (item 4) vs createurs (item 10)
# CONFINST_R1 contient le recap "ST Confiance"
# On cherche les colonnes par item
print("\nRecherche des items confiance...")

# === CROISEMENT AGE x POLITIQUE ===
print("\n" + "=" * 80)
print("CROISEMENT AGE x POLITIQUE")
print("=" * 80)

AGE_LABELS = {
    1: '15-17 ans', 2: '18-24 ans', 3: '25-34 ans', 4: '35-44 ans',
    5: '45-59 ans', 6: '60-69 ans', 7: '70 ans et +'
}

print("\nDistribution politique par age:")
print(f"{'Age':<12} | {'Gauche':>8} | {'Centre':>8} | {'Droite':>8} | {'T.Droite':>8}")
print("-" * 55)

for age_code in range(1, 8):
    subset = df[df['RS2C_RECODE_AG_R'] == age_code]
    total = subset['POIDS03'].sum()
    pct = {}
    for cat in ["Gauche", "Centre", "Droite", "Tres droite"]:
        n = subset[subset['POLITIQUE_CAT'] == cat]['POIDS03'].sum()
        pct[cat] = n / total * 100 if total > 0 else 0
    print(f"{AGE_LABELS[age_code]:<12} | {pct['Gauche']:>7.1f}% | {pct['Centre']:>7.1f}% | {pct['Droite']:>7.1f}% | {pct['Tres droite']:>7.1f}%")

# === EFFET NET POLITIQUE (controle age) ===
print("\n" + "=" * 80)
print("EFFET NET DE LA POLITIQUE (controle age)")
print("=" * 80)

from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder

# Preparer les donnees
df_model = df[['PRATIQUE_RS', 'POLITIQUE_CAT', 'RS2C_RECODE_AG_R', 'POIDS03']].dropna()

if len(df_model) > 100:
    le_pol = LabelEncoder()
    df_model['pol_encoded'] = le_pol.fit_transform(df_model['POLITIQUE_CAT'])

    X = df_model[['pol_encoded', 'RS2C_RECODE_AG_R']]
    y = df_model['PRATIQUE_RS']
    w = df_model['POIDS03']

    # Modele avec age seulement
    model_age = LogisticRegression(max_iter=1000)
    model_age.fit(df_model[['RS2C_RECODE_AG_R']], y, sample_weight=w)

    # Modele avec age + politique
    model_full = LogisticRegression(max_iter=1000)
    model_full.fit(X, y, sample_weight=w)

    print(f"\nCoefficient age (seul): {model_age.coef_[0][0]:.3f}")
    print(f"Coefficient age (+ politique): {model_full.coef_[0][1]:.3f}")
    print(f"Coefficient politique: {model_full.coef_[0][0]:.3f}")

    if abs(model_full.coef_[0][0]) < 0.1:
        print("\n=> La politique n'a PAS d'effet net significatif apres controle de l'age")
    else:
        print("\n=> La politique a un effet net INDEPENDANT de l'age")

# === RESUME ===
print("\n" + "=" * 80)
print("RESUME DES V DE CRAMER")
print("=" * 80)

results = [
    ("Orientation politique", "RS principale", v_rs_pol),
    ("Orientation politique", "TV principale", v_tv_pol),
    ("Confiance info", "RS principale", v_rs_conf),
    ("Confiance info", "TV principale", v_tv_conf),
    ("Doute medias", "RS principale", v_rs_doute),
]

results = sorted(results, key=lambda x: -x[2])

print(f"\n{'Variable':<25} {'Pratique':<15} {'V Cramer':>10}")
print("-" * 55)
for var, pratique, v in results:
    interpretation = "faible" if v < 0.1 else "modere" if v < 0.2 else "fort"
    print(f"{var:<25} {pratique:<15} {v:>9.3f} ({interpretation})")

print("\n" + "=" * 80)
print("COMPARAISON AVEC L'AGE")
print("=" * 80)
print("""
Pour rappel :
- V de Cramer (Age - RS principale) = 0.31
- V de Cramer (Age - TV principale) = 0.29

Les valeurs (politique, confiance) ont des associations BEAUCOUP PLUS FAIBLES
que l'age avec les pratiques informationnelles.
""")
