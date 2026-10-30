import os
"""
Analyse des deux clivages : générationnel et socio-économique
"""
import json
from collections import defaultdict

# Charger les données
with open(os.path.expanduser(r'~/Documents/VsCode/outsiders/frontend/public/data/enquetes/francais-information/chapitres/chapitre-01-basculement.json'), encoding='utf-8') as f:
    d = json.load(f)

sections = d['analyse']['sections']
for sec in sections:
    if sec.get('id') == 'effets-nets':
        data = sec['visualisations'][0]['data']
        break

print("=" * 70)
print("ANALYSE DES CLIVAGES")
print("=" * 70)

# Regrouper par VI
by_vi = defaultdict(list)
for item in data:
    by_vi[item['label_vi']].append(item)

# 1. CLIVAGE GÉNÉRATIONNEL (Âge)
print("\n1. CLIVAGE GÉNÉRATIONNEL (Âge)")
print("-" * 50)
age_items = by_vi.get('Âge', [])
print(f"   {len(age_items)} associations significatives\n")

jeunes_plus = []  # Ce que les jeunes font PLUS
seniors_plus = []  # Ce que les seniors font PLUS

for item in sorted(age_items, key=lambda x: -x['v_cramer']):
    cat_max = item['cat_max']
    cat_min = item['cat_min']
    vd = item['label_vd']

    # Déterminer si c'est les jeunes ou les seniors qui font plus
    max_cat = cat_max['category']
    if any(x in max_cat.lower() for x in ['15-', '18-', '25-']):
        jeunes_plus.append((vd, item['rapport'], cat_max['pct_oui'], cat_min['pct_oui']))
    else:
        seniors_plus.append((vd, item['rapport'], cat_max['pct_oui'], cat_min['pct_oui']))

print("   JEUNES font PLUS:")
for vd, rapport, pct_max, pct_min in jeunes_plus:
    print(f"     - {vd}: {pct_max:.0f}% vs {pct_min:.0f}% ({rapport}x)")

print("\n   SENIORS font PLUS:")
for vd, rapport, pct_max, pct_min in seniors_plus:
    print(f"     - {vd}: {pct_max:.0f}% vs {pct_min:.0f}% ({rapport}x)")

# 2. CLIVAGE SOCIO-ÉCONOMIQUE (Revenus + Diplôme)
print("\n2. CLIVAGE SOCIO-ÉCONOMIQUE")
print("-" * 50)

revenus_items = by_vi.get('Revenus', [])
diplome_items = by_vi.get("Niveau d'études", [])
print(f"   Revenus: {len(revenus_items)} associations")
print(f"   Diplôme: {len(diplome_items)} associations")

# Analyser les revenus
print("\n   REVENUS:")
eleve_plus_rev = []
faible_plus_rev = []

for item in sorted(revenus_items, key=lambda x: -x['v_cramer']):
    cat_max = item['cat_max']
    vd = item['label_vd']

    if 'Eleve' in cat_max['category'] or 'lev' in cat_max['category']:
        eleve_plus_rev.append((vd, item['rapport']))
    else:
        faible_plus_rev.append((vd, item['rapport']))

print("     Revenus ÉLEVÉS font plus:")
for vd, rapport in eleve_plus_rev[:5]:
    print(f"       - {vd} ({rapport}x)")

print("     Revenus FAIBLES font plus:")
for vd, rapport in faible_plus_rev[:5]:
    print(f"       - {vd} ({rapport}x)")

# Analyser le diplôme
print("\n   DIPLÔME:")
eleve_plus_dip = []
faible_plus_dip = []

for item in sorted(diplome_items, key=lambda x: -x['v_cramer']):
    cat_max = item['cat_max']
    vd = item['label_vd']

    if 'Eleve' in cat_max['category'] or 'lev' in cat_max['category']:
        eleve_plus_dip.append((vd, item['rapport']))
    else:
        faible_plus_dip.append((vd, item['rapport']))

print("     Diplôme ÉLEVÉ fait plus:")
for vd, rapport in eleve_plus_dip[:5]:
    print(f"       - {vd} ({rapport}x)")

print("     Diplôme FAIBLE fait plus:")
for vd, rapport in faible_plus_dip[:5]:
    print(f"       - {vd} ({rapport}x)")

# 3. AUTRES FACTEURS
print("\n3. AUTRES FACTEURS")
print("-" * 50)

for vi in ['Genre', 'Taille agglo.']:
    items = by_vi.get(vi, [])
    if items:
        print(f"\n   {vi.upper()}: {len(items)} associations")
        for item in items:
            print(f"     - {item['label_vd']}: {item['cat_max']['category']} ({item['cat_max']['pct_oui']:.0f}%) vs {item['cat_min']['category']} ({item['cat_min']['pct_oui']:.0f}%)")

print("\n" + "=" * 70)
print("SYNTHÈSE POUR LA CONCLUSION")
print("=" * 70)
print(f"""
CLIVAGE GÉNÉRATIONNEL ({len(age_items)} effets nets):
- Jeunes (15-34): RS, vidéo en ligne, Twitter/X, Instagram, formats courts
- Seniors (50+): TV, radio, presse, formats longs, JT

CLIVAGE SOCIO-ÉCONOMIQUE ({len(revenus_items) + len(diplome_items)} effets nets):
- CSP+/diplômés: presse, formats écrits, formats longs
- CSP-/peu diplômés: TV, formats vidéo, formats courts

Ces deux clivages sont INDÉPENDANTS (contrôlés l'un par l'autre).
""")
