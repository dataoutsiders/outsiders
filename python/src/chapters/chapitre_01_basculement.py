# -*- coding: utf-8 -*-
import os
"""
chapitre_01_basculement.py - Le basculement numérique (ARCOM 2024)

Exemple de chapitre utilisant le framework refactorisé.
Ce fichier montre comment utiliser les modules core/ pour créer un chapitre.

Usage:
    python -m src.chapters.chapitre_01_basculement
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Ajouter le chemin parent pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.weighted_stats import cramers_v_weighted, get_distribution_by_var
from src.core.regression import run_logistic_regression, extract_effect_cards
from src.core.tree_profiler import build_decision_tree, extract_profiles_from_tree
from src.core.json_builder import save_json, NumpyEncoder
from src.chapters.chapter_config import (
    AGE_LABELS_7, DIPLOME_LABELS_3, GENRE_LABELS, 
    CSP_LABELS, AGGLO_LABELS, SITUATION_PRO_LABELS,
    COULEURS
)


# ============================================
# CONFIGURATION DU CHAPITRE
# ============================================

CONFIG = {
    'data_path': Path(os.path.expanduser(r'~/Documents/Positron/Outsiders/Informations/base-info-arcom.xlsx')),
    'output_dir': Path(os.path.expanduser(r'~/Documents/Positron/Outsiders/Informations/output/chapitre-01-basculement')),
    'weights_col': 'POIDS03',
    'target_col': 'BASCULEMENT',
}

# Variables socio-démo à analyser
SOCIO_VARS = [
    ('RS2C_RECODE_AG_R', 'Âge', AGE_LABELS_7),
    ('RS3_R', 'Situation pro.', SITUATION_PRO_LABELS),
    ('RS1_R', 'Genre', GENRE_LABELS),
    ('RS4_R', 'CSP', CSP_LABELS),
    ('CC_R', 'Taille agglo', AGGLO_LABELS),
]


# ============================================
# FONCTIONS PRINCIPALES
# ============================================

def load_and_prepare_data():
    """Charge les données et construit la variable cible."""
    print("Chargement des données...")
    df = pd.read_excel(CONFIG['data_path'])
    
    # Convertir les poids
    if df['POIDS03'].dtype == 'object':
        df['POIDS03'] = df['POIDS03'].str.replace(',', '.').astype(float)
    
    print(f"  → {len(df)} observations chargées")
    
    # Construire BASCULEMENT
    print("Construction de la variable BASCULEMENT...")
    
    # Traditionnel
    trad_tv = (df['NEWS1BIS_R'] == 2) & (df['NEWS1_2B_R'] == 1)
    trad_radio = (df['NEWS1BIS_R'] == 1) & (df['NEWS1_1B_R'] == 1)
    trad_presse = (df['NEWS1BIS_R'] == 3) & (df['NEWS1_3B_R'] == 2)
    traditionnel = trad_tv | trad_radio | trad_presse
    
    # Numérique
    num_tv = (df['NEWS1BIS_R'] == 2) & (df['NEWS1_2B_R'] == 2)
    num_radio = (df['NEWS1BIS_R'] == 1) & (df['NEWS1_1B_R'].isin([2, 3]))
    num_presse = (df['NEWS1BIS_R'] == 3) & (df['NEWS1_3B_R'] == 1)
    numerique = num_tv | num_radio | num_presse | df['NEWS1BIS_R'].isin([5, 6, 7, 8, 9])
    
    df['BASCULEMENT'] = np.nan
    df.loc[traditionnel, 'BASCULEMENT'] = 0
    df.loc[numerique, 'BASCULEMENT'] = 1
    
    n_trad = traditionnel.sum()
    n_num = numerique.sum()
    print(f"  → Traditionnel: {n_trad} | Numérique: {n_num}")
    
    return df


def analyze_socio_demo(df):
    """Analyse les variables socio-démographiques."""
    print("\nAnalyse socio-démographique...")
    
    results = []
    for var_col, var_label, var_labels in SOCIO_VARS:
        if var_col not in df.columns:
            continue
            
        mask = df[var_col].notna() & df['BASCULEMENT'].notna()
        if mask.sum() < 100:
            continue
        
        # V de Cramer
        v, chi2, p = cramers_v_weighted(
            df.loc[mask, var_col],
            df.loc[mask, 'BASCULEMENT'],
            df.loc[mask, 'POIDS03']
        )
        
        # Distribution
        distribution = get_distribution_by_var(
            df, var_col, 'BASCULEMENT', 'POIDS03', var_labels
        )
        
        results.append({
            'variable': var_label,
            'var_code': var_col,
            'v_cramer': round(v, 3),
            'chi2': round(chi2, 1),
            'p_value': p,
            'significatif': p < 0.05,
            'distribution': distribution
        })
        
        print(f"  → {var_label}: V = {v:.3f}")
    
    results.sort(key=lambda x: x['v_cramer'], reverse=True)
    return results


def generate_chapter(df, socio_results):
    """Génère tous les JSON du chapitre."""
    print("\nGénération des JSON...")
    
    output_dir = CONFIG['output_dir']
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Index
    index_data = {
        'id': 'chapitre-01',
        'titre': 'Le basculement numérique',
        'sousTitre': 'Comment les Français s\'informent-ils vraiment ?',
        'sommaire': [
            {'id': '01a-prenotions', 'titre': 'Idées reçues', 'icon': 'lightbulb'},
            {'id': '01c-qui-bascule', 'titre': 'Qui bascule ?', 'icon': 'people'},
        ],
        'metadata': {
            'n_total': len(df),
            'n_analyse': df['BASCULEMENT'].notna().sum()
        }
    }
    save_json(index_data, output_dir / 'index.json')
    
    # 2. Qui bascule (socio-démo)
    qui_bascule = {
        'id': '01c-qui-bascule',
        'titre': 'Qui bascule ?',
        'sousTitre': 'Le profil socio-démographique des numériques',
        'sections': [
            {
                'id': 'force-association',
                'titre': 'Force d\'association (V de Cramer)',
                'visualisations': [{
                    'type': 'horizontal-bar-chart',
                    'data': [{'variable': r['variable'], 'v_cramer': r['v_cramer']} 
                            for r in socio_results]
                }]
            }
        ],
        'metadata': {'variables_analysees': len(socio_results)}
    }
    save_json(qui_bascule, output_dir / '01c-qui-bascule.json')
    
    print(f"\n✓ Fichiers générés dans {output_dir}")


# ============================================
# MAIN
# ============================================

def main():
    """Point d'entrée principal."""
    print("="*50)
    print("CHAPITRE 01 : Le basculement numérique")
    print("="*50)
    
    # 1. Charger et préparer les données
    df = load_and_prepare_data()
    
    # 2. Analyser
    socio_results = analyze_socio_demo(df)
    
    # 3. Générer les JSON
    generate_chapter(df, socio_results)
    
    print("\n" + "="*50)
    print("TERMINÉ")
    print("="*50)


if __name__ == '__main__':
    main()
