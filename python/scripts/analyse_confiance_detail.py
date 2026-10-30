# -*- coding: utf-8 -*-
"""
Analyse détaillée confiance : journalistes vs créateurs, attitudes sources
"""
import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path
import json

BASE_DIR = Path('python')
DATA_DIR = BASE_DIR / 'data' / 'francais-information'

# Charger dictionnaire
with open(DATA_DIR / 'dictionnaire.json', 'r', encoding='utf-8') as f:
    dico = json.load(f)

print("=" * 80)
print("EXPLORATION DES VARIABLES")
print("=" * 80)

# VALEURJ_R
print("\n=== VALEURJ_R ===")
for key, val in dico.items():
    if "VALEURJ" in key:
        titre = (val.get("titre") or "N/A")[:100]
        mods = val.get("modalites") or {}
        print(f"\n{key}: {titre}")
        if mods:
            for k, v in list(mods.items())[:12]:
                print(f"  {k}: {v}")

# INF3_R
print("\n=== INF3_R (confiance personnes sources) ===")
for key, val in dico.items():
    if "INF3_R" in key and len(key) < 12:
        titre = (val.get("titre") or "N/A")[:100]
        mods = val.get("modalites") or {}
        print(f"\n{key}: {titre}")
        if mods:
            for k, v in list(mods.items())[:12]:
                print(f"  {k}: {v}")

# ATTSOURCES_R
print("\n=== ATTSOURCES_R ===")
for key, val in dico.items():
    if "ATTSOURCES" in key:
        titre = (val.get("titre") or "N/A")[:100]
        mods = val.get("modalites") or {}
        print(f"\n{key}: {titre}")
        if mods:
            for k, v in list(mods.items())[:12]:
                print(f"  {k}: {v}")
