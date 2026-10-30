import os
"""
Exploration des variables pour enrichir le chapitre 1
"""
import json

with open(os.path.expanduser('~/Documents/VsCode/outsiders/python/data/francais-information/dictionnaire.json'), 'r', encoding='utf-8') as f:
    dico = json.load(f)

def safe_print(text, max_len=100):
    if text:
        print(text[:max_len])
    else:
        print("N/A")

def explore_var(var_name):
    if var_name in dico:
        print(f"\n{'='*60}")
        print(f"VARIABLE : {var_name}")
        print(f"{'='*60}")
        titre = dico[var_name].get('titre')
        print(f"Titre: ", end="")
        safe_print(titre, 120)
        mods = dico[var_name].get('modalites', {})
        if mods:
            print("Modalites:")
            for k, v in list(mods.items())[:8]:
                v_str = str(v) if v else ""
                print(f"  {k}: {v_str[:70]}")
            if len(mods) > 8:
                print(f"  ... ({len(mods)} modalites au total)")
        return True
    return False

# Variables a explorer
print("=" * 80)
print("EXPLORATION DES VARIABLES POUR LE CHAPITRE 1")
print("=" * 80)

explore_var('INT3_R')
explore_var('L_NEWS1SOURCES_R')
explore_var('MOTIVRS_R')
explore_var('ENGAR_R')
explore_var('CONF1_R')
explore_var('SOURCE_BASE_R1')

# Chercher RSINFO
print("\n" + "=" * 80)
print("RECHERCHE RSINFO")
print("=" * 80)
rsinfo_vars = [k for k in dico.keys() if 'RSINFO' in k.upper()]
for var in rsinfo_vars[:8]:
    titre = dico[var].get('titre')
    print(f"\n{var}:")
    safe_print(titre, 100)

# Chercher MOTIV
print("\n" + "=" * 80)
print("RECHERCHE MOTIV")
print("=" * 80)
motiv_vars = [k for k in dico.keys() if 'MOTIV' in k.upper()]
for var in motiv_vars[:8]:
    titre = dico[var].get('titre')
    print(f"\n{var}:")
    safe_print(titre, 100)

# Chercher SOURCES
print("\n" + "=" * 80)
print("RECHERCHE SOURCES")
print("=" * 80)
source_vars = [k for k in dico.keys() if k.startswith('SOURCES')]
for var in source_vars[:8]:
    titre = dico[var].get('titre')
    if titre:
        print(f"\n{var}:")
        safe_print(titre, 100)

# Chercher TV2
print("\n" + "=" * 80)
print("RECHERCHE TV")
print("=" * 80)
tv_vars = [k for k in dico.keys() if k.startswith('TV')]
for var in tv_vars[:8]:
    titre = dico[var].get('titre')
    if titre:
        print(f"\n{var}:")
        safe_print(titre, 100)

# Chercher questionnaire
print("\n" + "=" * 80)
print("RECHERCHE QUESTIONNAIRE LONG/COURT")
print("=" * 80)
for var in ['CIBLE', 'SOURCE_BASE_R1', 'QUESTIONNAIRE']:
    explore_var(var)
