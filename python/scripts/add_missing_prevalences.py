# -*- coding: utf-8 -*-
"""Ajouter les prévalences manquantes dans le JSON du chapitre 01"""
import json
import pandas as pd
from pathlib import Path

# Charger les données ARCOM
BASE_DIR = Path('python')
DATA_DIR = BASE_DIR / 'data' / 'francais-information'
df = pd.read_excel(DATA_DIR / 'base-info-arcom.xlsx')
# Conversion des poids (format français avec virgules)
if df['POIDS03'].dtype == 'object':
    df['POIDS03'] = df['POIDS03'].str.replace(',', '.').astype(float)

# ============================================
# Créer les variables formats (comme dans generate_chapitre1_json.py)
# ============================================

# Fonction pour vérifier utilisation format (codes 1-3 dans FORMAT_R_1 à FORMAT_R_4)
def utilise_format(row, code):
    for col in ['FORMAT_R_1', 'FORMAT_R_2', 'FORMAT_R_3', 'FORMAT_R_4']:
        if pd.notna(row[col]) and row[col] == code:
            return 1
    return 0

df['FORMAT_JT'] = df.apply(lambda r: utilise_format(r, 1), axis=1)
df['FORMAT_MAGAZINE'] = df.apply(lambda r: utilise_format(r, 2), axis=1)
df['FORMAT_DEBAT'] = df.apply(lambda r: utilise_format(r, 3), axis=1)

# Variables FORMAT3 et FORMAT2 (binaires)
df['FORMAT3_COURT'] = (df['FORMAT3_LR1_FORMAT3_1_R'] == 1).astype(int)
df['FORMAT3_LONG'] = (df['FORMAT3_LR1_FORMAT3_1_R'] == 2).astype(int)
df['FORMAT2_ECRIT'] = (df['FORMAT2_LR1_FORMAT2_1_R'] == 1).astype(int)
df['FORMAT2_VIDEO'] = (df['FORMAT2_LR1_FORMAT2_1_R'] == 2).astype(int)

# ============================================
# Calculer les prévalences pondérées
# ============================================

def calc_prevalence(col_name):
    """Calcule le % pondéré de 1 dans une colonne binaire"""
    mask = df[col_name] == 1
    pct = (df.loc[mask, 'POIDS03'].sum() / df['POIDS03'].sum()) * 100
    return round(pct, 1)

# Mapping var2 -> colonne dans df
VAR_TO_COL = {
    'JT / Flash info': 'FORMAT_JT',
    'Magazines / Reportages': 'FORMAT_MAGAZINE',
    'Talk-shows / Debats': 'FORMAT_DEBAT',
    'Formats courts': 'FORMAT3_COURT',
    'Formats longs': 'FORMAT3_LONG',
    'Format ecrit': 'FORMAT2_ECRIT',
    'Format video': 'FORMAT2_VIDEO',
}

prevalences = {}
print("Prévalences calculées :")
for var2, col in VAR_TO_COL.items():
    prev = calc_prevalence(col)
    prevalences[var2] = prev
    print(f"  {var2}: {prev}%")

# ============================================
# Mettre à jour le JSON
# ============================================

json_path = Path('frontend/public/data/enquetes/francais-information/chapitres/chapitre-01-basculement.json')
with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Mettre à jour la section facteurs-distinctifs
sections = data.get('analyse', {}).get('sections', [])
updated_total = 0

for section in sections:
    if section.get('id') == 'facteurs-distinctifs':
        viz = section['visualisations'][0]
        items = viz['data']

        for item in items:
            var2 = item.get('var2')
            if item.get('prevalence') is None and var2 in prevalences:
                item['prevalence'] = prevalences[var2]
                updated_total += 1

print(f"\nSection facteurs-distinctifs: {updated_total} items mis à jour")

# Vérifier les items toujours sans prévalence
still_missing = set()
for section in sections:
    if section.get('id') == 'facteurs-distinctifs':
        for viz in section.get('visualisations', []):
            for item in viz.get('data', []):
                if item.get('prevalence') is None:
                    still_missing.add(item.get('var2'))

if still_missing:
    print(f"\nToujours sans prévalence ({len(still_missing)}):")
    for v in sorted(still_missing):
        print(f"  - {v}")
else:
    print("\nToutes les prévalences sont maintenant définies!")

# Sauvegarder
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("\nJSON sauvegardé!")
