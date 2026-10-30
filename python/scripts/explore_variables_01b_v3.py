"""
Exploration structure RS16 (équipement) - Version 3
"""
import pandas as pd
from pathlib import Path

BASE_DIR = Path('python')
DATA_DIR = BASE_DIR / 'data' / 'francais-information'

df = pd.read_excel(DATA_DIR / 'base-info-arcom.xlsx')
datamap = pd.read_excel(DATA_DIR / 'datamap-info-arcom.xlsx', sheet_name='TEXTS')

df['POIDS03'] = df['POIDS03'].astype(str).str.replace(',', '.').astype(float)

# =============================================================================
# COMPRENDRE RS16_R_X (possession : un, plusieurs, aucun)
# =============================================================================
print("=" * 80)
print("### RS16_R_X : POSSESSION DES ÉQUIPEMENTS ###")
print("=" * 80)

# Labels des équipements
equip_labels = {
    1: 'Téléviseur',
    2: 'Radio/chaîne hifi',
    3: 'Autoradio',
    4: 'Smartphone',
    5: 'Ordinateur fixe',
    6: 'Ordinateur portable',
    7: 'Tablette tactile',
    8: 'Chromecast/Firestick/Apple TV',
    9: 'Enceinte connectée',
    10: 'Casque VR',
    11: 'Montre connectée',
    12: 'Console de jeux'
}

# Labels possession
possession_labels = {1: 'Un(e)', 2: 'Plusieurs', 3: 'Aucun(e)'}

print("\nDistribution possession par équipement:")
for code, label in equip_labels.items():
    var = f'RS16_R_{code}'
    if var in df.columns:
        print(f"\n{label} ({var}):")
        total = df['POIDS03'].sum()
        for poss_code, poss_label in possession_labels.items():
            n = df[df[var] == poss_code]['POIDS03'].sum()
            pct = n / total * 100
            print(f"  {poss_label}: {pct:.1f}%")

# =============================================================================
# TAUX DE POSSESSION (au moins un)
# =============================================================================
print("\n" + "=" * 80)
print("### TAUX DE POSSESSION (au moins un) ###")
print("=" * 80)

print("\nÉquipement                          | Taux possession")
print("-" * 50)
for code, label in equip_labels.items():
    var = f'RS16_R_{code}'
    if var in df.columns:
        # Au moins un = code 1 ou 2
        possede = df[df[var].isin([1, 2])]['POIDS03'].sum()
        total = df[df[var].notna()]['POIDS03'].sum()
        pct = possede / total * 100 if total > 0 else 0
        print(f"{label:35} | {pct:.1f}%")

# =============================================================================
# CROISEMENT ÂGE x SMARTPHONE
# =============================================================================
print("\n" + "=" * 80)
print("### CROISEMENT ÂGE x POSSESSION SMARTPHONE ###")
print("=" * 80)

age_labels = {1: '15-17', 2: '18-24', 3: '25-34', 4: '35-44', 5: '45-59', 6: '60-69', 7: '70+'}

if 'RS16_R_4' in df.columns:
    print("\nPossession smartphone par âge:")
    for age_code, age_label in age_labels.items():
        subset = df[df['RS2C_RECODE_AG_R'] == age_code]
        if len(subset) > 0:
            possede = subset[subset['RS16_R_4'].isin([1, 2])]['POIDS03'].sum()
            total = subset[subset['RS16_R_4'].notna()]['POIDS03'].sum()
            pct = possede / total * 100 if total > 0 else 0
            print(f"  {age_label}: {pct:.1f}%")

# =============================================================================
# CROISEMENT ÂGE x TABLETTE
# =============================================================================
print("\n" + "=" * 80)
print("### CROISEMENT ÂGE x POSSESSION TABLETTE ###")
print("=" * 80)

if 'RS16_R_7' in df.columns:
    print("\nPossession tablette par âge:")
    for age_code, age_label in age_labels.items():
        subset = df[df['RS2C_RECODE_AG_R'] == age_code]
        if len(subset) > 0:
            possede = subset[subset['RS16_R_7'].isin([1, 2])]['POIDS03'].sum()
            total = subset[subset['RS16_R_7'].notna()]['POIDS03'].sum()
            pct = possede / total * 100 if total > 0 else 0
            print(f"  {age_label}: {pct:.1f}%")

# =============================================================================
# CROISEMENT ÂGE x TV
# =============================================================================
print("\n" + "=" * 80)
print("### CROISEMENT ÂGE x POSSESSION TV ###")
print("=" * 80)

if 'RS16_R_1' in df.columns:
    print("\nPossession TV par âge:")
    for age_code, age_label in age_labels.items():
        subset = df[df['RS2C_RECODE_AG_R'] == age_code]
        if len(subset) > 0:
            possede = subset[subset['RS16_R_1'].isin([1, 2])]['POIDS03'].sum()
            total = subset[subset['RS16_R_1'].notna()]['POIDS03'].sum()
            pct = possede / total * 100 if total > 0 else 0
            print(f"  {age_label}: {pct:.1f}%")

# =============================================================================
# COMPRENDRE RS16_R1, RS16_R2, RS16_R3
# =============================================================================
print("\n" + "=" * 80)
print("### STRUCTURE RS16_R1, RS16_R2, RS16_R3 ###")
print("=" * 80)

# Chercher les labels dans le datamap
for var_base in ['RS16_R1', 'RS16_R2', 'RS16_R3']:
    info = datamap[(datamap['NAME'] == var_base) & (datamap['TYPE'] == 'NAME')]
    if len(info) > 0:
        print(f"\n{var_base}: {info['FR:L'].values[0]}")

# Regarder un exemple de valeurs
print("\nExemple RS16_R1_1 (TV ?):")
if 'RS16_R1_1' in df.columns:
    print(df['RS16_R1_1'].value_counts().head(10))

print("\nExemple RS16_R2_4 (smartphone ?):")
if 'RS16_R2_4' in df.columns:
    print(df['RS16_R2_4'].value_counts().head(10))
