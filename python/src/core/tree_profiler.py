# -*- coding: utf-8 -*-
"""
tree_profiler.py - Arbres de décision et extraction de profils

Fonctions pour construire des arbres de décision interprétables
et en extraire des profils-types lisibles.
"""

import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder
from typing import Dict, List, Optional, Tuple, Any
import warnings
warnings.filterwarnings('ignore')


def build_decision_tree(
    df: pd.DataFrame,
    target: str,
    features: List[str],
    weights: str = 'POIDS',
    max_depth: int = 4,
    min_samples_leaf: int = 50,
    min_samples_split: int = 100,
    categorical_features: Optional[List[str]] = None
) -> Dict:
    """
    Construit un arbre de décision pondéré.
    
    Args:
        df: DataFrame
        target: Variable cible (binaire ou catégorielle)
        features: Variables explicatives
        weights: Colonne des poids
        max_depth: Profondeur max de l'arbre
        min_samples_leaf: Nb min d'observations par feuille
        min_samples_split: Nb min pour splitter un nœud
        categorical_features: Variables catégorielles à encoder
        
    Returns:
        Dict avec le modèle, les encodeurs, l'importance des variables, l'accuracy
    """
    # Préparer les données
    all_cols = [target, weights] + features
    tree_df = df[all_cols].dropna().copy().reset_index(drop=True)
    
    # Encoder les variables catégorielles
    encoders = {}
    X_data = tree_df[features].copy()
    
    if categorical_features:
        for cat_var in categorical_features:
            if cat_var in X_data.columns and X_data[cat_var].dtype == 'object':
                le = LabelEncoder()
                X_data[cat_var] = le.fit_transform(X_data[cat_var])
                encoders[cat_var] = le
    
    # Encoder la cible si nécessaire
    y = tree_df[target]
    target_encoder = None
    if y.dtype == 'object':
        target_encoder = LabelEncoder()
        y = target_encoder.fit_transform(y)
        encoders['_target'] = target_encoder
    else:
        y = y.values
    
    X = X_data.values
    w = tree_df[weights].values
    
    # Entraîner l'arbre
    tree = DecisionTreeClassifier(
        max_depth=max_depth,
        min_samples_leaf=min_samples_leaf,
        min_samples_split=min_samples_split,
        random_state=42
    )
    tree.fit(X, y, sample_weight=w)
    
    # Accuracy pondérée
    predictions = tree.predict(X)
    accuracy = ((predictions == y) * w).sum() / w.sum() * 100
    
    # Importance des variables
    importances = []
    for i, feat in enumerate(features):
        importances.append({
            'variable': feat,
            'importance': round(float(tree.feature_importances_[i]), 4),
            'pct': round(float(tree.feature_importances_[i]) * 100, 1)
        })
    importances.sort(key=lambda x: x['importance'], reverse=True)
    
    return {
        'model': tree,
        'encoders': encoders,
        'features': features,
        'target': target,
        'accuracy': round(accuracy, 1),
        'importances': importances,
        'n_obs': len(tree_df),
        'tree_df': tree_df,
        'X': X,
        'y': y,
        'weights': w
    }


def extract_profiles_from_tree(
    tree_results: Dict,
    profile_definitions: List[Dict],
    labels: Optional[Dict[str, Dict]] = None
) -> List[Dict]:
    """
    Extrait des profils-types à partir de conditions sur les variables.
    
    Args:
        tree_results: Résultat de build_decision_tree
        profile_definitions: Liste de définitions de profils:
            [
                {
                    'id': 'jeunes',
                    'nom': 'Les connectés',
                    'sous_titre': '15-44 ans',
                    'description': 'Description...',
                    'conditions': {'AGE': ('<=', 4)},  # ou {'AGE': ('in', [1,2,3,4])}
                    'icon': 'smartphone',
                    'couleur': '#10B981',
                    'gradient': 'from-emerald-500 to-teal-500'
                },
                ...
            ]
        labels: Dict de labels par variable {var: {code: label}}
        
    Returns:
        Liste de profils avec stats calculées
    """
    tree_df = tree_results['tree_df']
    target = tree_results['target']
    weights = 'POIDS' if 'POIDS' in tree_df.columns else tree_results.get('weights_col', tree_df.columns[-1])
    y = tree_results['y']
    w = tree_results['weights']
    
    # Moyenne globale (pour la cible = 1)
    if len(np.unique(y)) == 2:
        pct_global = (y * w).sum() / w.sum() * 100
    else:
        pct_global = 50  # multiclasse
    
    profiles = []
    
    for pdef in profile_definitions:
        # Appliquer les conditions pour créer le masque
        mask = pd.Series([True] * len(tree_df))
        
        for var, condition in pdef.get('conditions', {}).items():
            if var not in tree_df.columns:
                continue
                
            op, val = condition
            if op == '<=':
                mask &= (tree_df[var] <= val)
            elif op == '>=':
                mask &= (tree_df[var] >= val)
            elif op == '==':
                mask &= (tree_df[var] == val)
            elif op == '!=':
                mask &= (tree_df[var] != val)
            elif op == 'in':
                mask &= tree_df[var].isin(val)
            elif op == 'not_in':
                mask &= ~tree_df[var].isin(val)
        
        if mask.sum() == 0:
            continue
        
        # Calculer les stats du profil
        mask_idx = mask.values
        y_profil = y[mask_idx]
        w_profil = w[mask_idx]
        
        if len(np.unique(y)) == 2:
            pct_vd = (y_profil * w_profil).sum() / w_profil.sum() * 100
        else:
            # Multiclasse : prendre le mode
            pct_vd = 50  # à adapter
        
        # Caractéristiques textuelles
        caracteristiques = pdef.get('caracteristiques', [])
        
        profiles.append({
            'id': pdef['id'],
            'ordre': pdef.get('ordre', 0),
            'nom': pdef['nom'],
            'sousTitre': pdef.get('sous_titre', ''),
            'description': pdef.get('description', ''),
            'icon': pdef.get('icon', 'users'),
            'n': int(mask.sum()),
            'pct_echantillon': round(mask.sum() / len(tree_df) * 100, 0),
            'pct_numerique': round(pct_vd, 0),
            'ecart': round(pct_vd - pct_global, 0),
            'couleur': pdef.get('couleur', '#6366F1'),
            'gradient': pdef.get('gradient', 'from-indigo-500 to-blue-500'),
            'categorie': 'numerique' if pct_vd > pct_global + 10 else ('traditionnel' if pct_vd < pct_global - 10 else 'mixte'),
            'caracteristiques': caracteristiques,
            'insight': pdef.get('insight', '')
        })
    
    # Trier par % de la VD décroissant
    profiles.sort(key=lambda x: x['pct_numerique'], reverse=True)
    
    return profiles


def extract_decision_path(
    tree_results: Dict,
    path_config: List[Dict]
) -> Dict:
    """
    Crée une représentation lisible du parcours de décision.
    
    Args:
        tree_results: Résultat de build_decision_tree
        path_config: Configuration des étapes du parcours:
            [
                {
                    'niveau': 1,
                    'question': 'Quel âge avez-vous ?',
                    'variable': 'Âge',
                    'branches': [
                        {'condition': 'Moins de 45 ans', 'resultat': 'numerique', 'pct': 70, 'couleur': '#10B981'},
                        {'condition': '45 ans et plus', 'resultat': 'suite', 'couleur': '#6B7280'}
                    ]
                },
                ...
            ]
            
    Returns:
        Dict structuré pour affichage du parcours
    """
    importances = tree_results['importances']
    
    # Enrichir avec les importances
    for etape in path_config:
        var_name = etape.get('variable', '')
        for imp in importances:
            if imp['variable'].lower() in var_name.lower() or var_name.lower() in imp['variable'].lower():
                etape['importance'] = imp['pct']
                break
        if 'importance' not in etape:
            etape['importance'] = 0
    
    return {
        'titre': 'Comment l\'analyse classe les individus',
        'description': 'Un arbre de décision révèle les facteurs qui prédisent le mieux le comportement.',
        'etapes': path_config
    }


def auto_generate_profiles(
    tree_results: Dict,
    n_profiles: int = 5,
    target_value: int = 1,
    labels: Optional[Dict[str, Dict]] = None
) -> List[Dict]:
    """
    Génère automatiquement des profils à partir des feuilles de l'arbre.
    
    Identifie les feuilles avec les taux les plus extrêmes (hauts et bas)
    de la variable cible.
    
    Args:
        tree_results: Résultat de build_decision_tree
        n_profiles: Nombre de profils à générer
        target_value: Valeur de la cible pour laquelle calculer le %
        labels: Labels des variables
        
    Returns:
        Liste de profils générés automatiquement
    """
    tree = tree_results['model']
    X = tree_results['X']
    y = tree_results['y']
    w = tree_results['weights']
    features = tree_results['features']
    
    # Identifier les feuilles
    leaf_indices = tree.apply(X)
    unique_leaves = np.unique(leaf_indices)
    
    leaf_stats = []
    for leaf_id in unique_leaves:
        mask = leaf_indices == leaf_id
        y_leaf = y[mask]
        w_leaf = w[mask]
        
        if mask.sum() < 30:  # Ignorer les petites feuilles
            continue
        
        pct = (y_leaf == target_value).astype(float).dot(w_leaf) / w_leaf.sum() * 100
        
        leaf_stats.append({
            'leaf_id': leaf_id,
            'n': int(mask.sum()),
            'pct': pct,
            'mask': mask
        })
    
    # Trier par % et prendre les extrêmes
    leaf_stats.sort(key=lambda x: x['pct'], reverse=True)
    
    selected = leaf_stats[:n_profiles//2] + leaf_stats[-(n_profiles - n_profiles//2):]
    
    profiles = []
    for i, leaf in enumerate(selected):
        # Décrire le chemin vers cette feuille (simplifié)
        pct = leaf['pct']
        categorie = 'numerique' if pct > 60 else ('traditionnel' if pct < 40 else 'mixte')
        
        profiles.append({
            'id': f'profil_{i+1}',
            'nom': f'Profil {i+1}',
            'n': leaf['n'],
            'pct_numerique': round(pct, 0),
            'categorie': categorie,
            'auto_generated': True
        })
    
    return profiles
