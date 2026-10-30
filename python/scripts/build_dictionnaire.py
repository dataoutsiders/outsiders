"""
Construit le dictionnaire des variables à partir du datamap
"""
import pandas as pd
import json
from pathlib import Path

# Chemins
DATA_DIR = Path(__file__).parent.parent / "data" / "francais-information"
DATAMAP_PATH = DATA_DIR / "datamap-info-arcom.xlsx"
OUTPUT_PATH = DATA_DIR / "dictionnaire.json"

# Lire TEXTS
texts = pd.read_excel(DATAMAP_PATH, sheet_name='TEXTS')

# Construire le dictionnaire
dictionnaire = {}

for _, row in texts.iterrows():
    var_name = row['NAME']
    text_type = row['TYPE']
    label = row['FR:L']
    code = row['CODE']

    if pd.isna(var_name) or pd.isna(text_type):
        continue

    if var_name not in dictionnaire:
        dictionnaire[var_name] = {'titre': None, 'modalites': {}}

    if text_type == 'TITLE':
        dictionnaire[var_name]['titre'] = label
    elif text_type == 'LABEL' and not pd.isna(code):
        dictionnaire[var_name]['modalites'][str(int(code))] = label

# Sauvegarder
with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
    json.dump(dictionnaire, f, ensure_ascii=False, indent=2)

print(f"Dictionnaire créé: {len(dictionnaire)} variables")
print(f"Fichier: {OUTPUT_PATH}")
print()

# Afficher des exemples clés
exemples = [
    'RS1_R', 'RS2C_RECODE_AG_R', 'CSPIND_R',  # Socio-demo
    'INT1_R', 'INT2_R', 'INT3_R',  # Intérêt info
    'CONF1_R',  # Confiance
    'EVITE1_R', 'EVITE2_R',  # Évitement
    'COMPLOT1_R', 'COMPLOT2_R',  # Complots
    'DEFIANCEJ_R',  # Défiance journalisme
    'IA1_R',  # IA
]

print("=" * 60)
print("EXEMPLES DE VARIABLES CLÉS")
print("=" * 60)

for var in exemples:
    if var in dictionnaire:
        print(f"\n{var}")
        print(f"  → {dictionnaire[var]['titre']}")
        mods = dictionnaire[var]['modalites']
        if mods:
            for code, label in list(mods.items())[:4]:
                print(f"     {code}: {label}")
            if len(mods) > 4:
                print(f"     ... ({len(mods)} modalités)")
