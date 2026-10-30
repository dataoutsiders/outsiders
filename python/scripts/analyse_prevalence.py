# -*- coding: utf-8 -*-
"""Analyser la distribution des prévalences dans le chapitre 01"""
import json

with open('frontend/public/data/enquetes/francais-information/chapitres/chapitre-01-basculement.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

sections = data.get('analyse', {}).get('sections', [])
for s in sections:
    if s.get('id') == 'facteurs-distinctifs':
        vizs = s.get('visualisations', [])
        for v in vizs:
            items = v.get('data', [])
            print(f'Nombre total items: {len(items)}')

            # Compter par seuil de prévalence
            for seuil in [5, 10, 15, 20, 25]:
                count = len([i for i in items if (i.get('prevalence') or 0) >= seuil])
                print(f'  Prevalence >= {seuil}%: {count} items')

            # Afficher quelques items avec faible prévalence
            print('\nExemples faible prevalence (<10%):')
            low = sorted([i for i in items if (i.get('prevalence') or 0) < 10], key=lambda x: (x.get('prevalence') or 0))
            for i in low[:15]:
                print(f'  {i.get("var2", "?")}: {i.get("prevalence") or 0}% (V={i.get("v_cramer") or 0:.2f})')

            print(f'\n=> {len(low)} items ont une prevalence < 10%')

            # Items sans prévalence
            no_prev = [i for i in items if i.get('prevalence') is None]
            print(f'=> {len(no_prev)} items sans prevalence definie')
