# -*- coding: utf-8 -*-
"""Explorer les variables d'orientation politique et confiance pour 01b-valeurs"""
import json
import pandas as pd
from pathlib import Path

BASE_DIR = Path('python')
DATA_DIR = BASE_DIR / 'data' / 'francais-information'

# Charger le dictionnaire
with open(DATA_DIR / 'dictionnaire.json', 'r', encoding='utf-8') as f:
    dico = json.load(f)

# === RECHERCHE DES VARIABLES ===
print("=" * 80)
print("RECHERCHE : ORIENTATION POLITIQUE")
print("=" * 80)
keywords_pol = ['POLIT', 'GAUCHE', 'DROIT', 'ORIENT', 'PROX', 'PARTI']
for key, val in dico.items():
    titre = (val.get("titre") or "").upper()
    if any(kw in key.upper() or kw in titre for kw in keywords_pol):
        t = (val.get("titre") or "N/A")[:100]
        mods = val.get("modalites") or {}
        print(f"\n{key}: {t}")
        if mods:
            for k, v in list(mods.items())[:10]:
                print(f"  {k}: {v}")

print("\n" + "=" * 80)
print("RECHERCHE : CONFIANCE MEDIAS")
print("=" * 80)
keywords_conf = ['CONF', 'FIAB', 'CRED', 'FAKE', 'FAUS', 'DESINFO']
for key, val in dico.items():
    titre = (val.get("titre") or "").upper()
    if any(kw in key.upper() or kw in titre for kw in keywords_conf):
        t = (val.get("titre") or "N/A")[:100]
        mods = val.get("modalites") or {}
        print(f"\n{key}: {t}")
        if mods:
            for k, v in list(mods.items())[:10]:
                print(f"  {k}: {v}")

print("\n" + "=" * 80)
print("RECHERCHE : OPINIONS / JUGEMENTS")
print("=" * 80)
keywords_op = ['OPIN', 'JUGEM', 'PENSEZ', 'CRAINTE', 'PEUR']
for key, val in dico.items():
    titre = (val.get("titre") or "").upper()
    if any(kw in key.upper() or kw in titre for kw in keywords_op):
        t = (val.get("titre") or "N/A")[:100]
        mods = val.get("modalites") or {}
        print(f"\n{key}: {t}")
        if mods:
            for k, v in list(mods.items())[:8]:
                print(f"  {k}: {v}")
