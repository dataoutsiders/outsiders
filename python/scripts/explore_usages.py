# -*- coding: utf-8 -*-
"""Explorer les variables d'usage pour 01b"""
import json
import pandas as pd
from pathlib import Path

BASE_DIR = Path('python')
DATA_DIR = BASE_DIR / 'data' / 'francais-information'

# Charger le dictionnaire
with open(DATA_DIR / 'dictionnaire.json', 'r', encoding='utf-8') as f:
    dico = json.load(f)

# === MOTIVRS ===
print("=" * 80)
print("MOTIVRS - Motivations d'utiliser les RS pour s'informer")
print("=" * 80)
for key, val in dico.items():
    if "MOTIVRS" in key:
        titre = (val.get("titre") or "N/A")[:100]
        mods = val.get("modalites") or {}
        print(f"\n{key}: {titre}")
        if mods:
            for k, v in list(mods.items())[:15]:
                print(f"  {k}: {v}")

print("\n" + "=" * 80)

print("=== FORMAT ===")
for key, val in dico.items():
    if "FORMAT" in key:
        titre = (val.get("titre") or "N/A")[:100]
        mods = val.get("modalites") or {}
        print(f"{key}: {titre}")
        if mods:
            for k, v in list(mods.items())[:5]:
                print(f"  {k}: {v}")

print("\n=== RSINFO_1 (comportements sur RS) ===")
for key, val in dico.items():
    if "RSINFO_1" in key:
        titre = (val.get("titre") or "N/A")[:80]
        mods = val.get("modalites") or {}
        print(f"{key}: {titre}")
        if mods:
            for k, v in list(mods.items())[:5]:
                print(f"  {k}: {v}")

print("\n=== RSINFO_2 ===")
for key, val in dico.items():
    if "RSINFO_2" in key:
        titre = (val.get("titre") or "N/A")[:80]
        mods = val.get("modalites") or {}
        print(f"{key}: {titre}")
        if mods:
            for k, v in list(mods.items())[:5]:
                print(f"  {k}: {v}")

# Explorer aussi les variables de temporalite (direct/differe)
print("\n=== Chercher direct/differe/replay/video ===")
for key, val in dico.items():
    titre = (val.get("titre") or "").lower()
    if any(mot in titre for mot in ["direct", "replay", "rattrapage", "differe", "video", "court"]):
        mods = val.get("modalites") or {}
        t = (val.get("titre") or "N/A")[:80]
        print(f"{key}: {t}")
        if mods:
            for k, v in list(mods.items())[:3]:
                print(f"  {k}: {v}")
