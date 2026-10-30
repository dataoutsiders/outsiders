# -*- coding: utf-8 -*-
"""
regression.py - Régressions et prédictions pour Outsiders

Fonctions pour régressions logistiques pondérées et extraction
des effets nets (probabilités prédites, odds ratios, effect cards).
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
from typing import Dict, List, Optional, Tuple, Any
import warnings
warnings.filterwarnings('ignore')


def run_logistic_regression(
    df: pd.DataFrame,
    target: str,
    features: List[str],
    weights: str = 'POIDS',
    categorical_features: Optional[List[str]] = None,
    reference_categories: Optional[Dict[str, Any]] = None
) -> Dict:
    """
    Exécute une régression logistique pondérée.
    
    Args:
        df: DataFrame
        target: Variable dépendante binaire (0/1)
        features: Liste des variables explicatives
        weights: Colonne des poids
        categorical_features: Variables à transformer en dummies
        reference_categories: Dict {var: valeur_ref} pour définir les catégories de référence
        
    Returns:
        Dict avec coefficients, odds ratios, p-values, pseudo-R2, etc.
        
    Example:
        >>> results = run_logistic_regression(
        ...     df, 'BASCULEMENT', 
        ...     ['AGE', 'DIPLOME', 'USAGE_ALGO'],
        ...     categorical_features=['AGE', 'DIPLOME'],
        ...     reference_categories={'AGE': 4}  # 35-44 ans comme ref
        ... )
    """
    # Préparer les données
    all_cols = [target, weights] + features
    reg_df = df[all_cols].dropna().copy()
    
    # Créer les dummies pour les variables catégorielles
    X = reg_df[features].copy()
    
    if categorical_features:
        for cat_var in categorical_features:
            if cat_var in X.columns:
                # Si une référence est spécifiée, l'utiliser
                ref = reference_categories.get(cat_var) if reference_categories else None
                dummies = pd.get_dummies(X[cat_var], prefix=cat_var, drop_first=False)
                
                if ref is not None:
                    ref_col = f"{cat_var}_{ref}"
                    if ref_col in dummies.columns:
                        dummies = dummies.drop(columns=[ref_col])
                else:
                    # Drop la première par défaut
                    dummies = dummies.iloc[:, 1:]
                
                X = X.drop(columns=[cat_var])
                X = pd.concat([X, dummies], axis=1)
    
    X = X.astype(float)
    X = sm.add_constant(X)
    
    y = reg_df[target].astype(float)
    w = reg_df[weights].astype(float)
    
    # Régression logistique pondérée (GLM binomial)
    model = sm.GLM(y, X, family=sm.families.Binomial(), freq_weights=w)
    results = model.fit()
    
    # Extraire les résultats
    coefficients = []
    for var in results.params.index:
        if var == 'const':
            continue
        coef = results.params[var]
        pval = results.pvalues[var]
        
        coefficients.append({
            'variable': var,
            'coef': round(float(coef), 4),
            'odds_ratio': round(float(np.exp(coef)), 3),
            'std_err': round(float(results.bse[var]), 4),
            'z_value': round(float(results.tvalues[var]), 3),
            'p_value': float(pval),
            'significatif': pval < 0.05,
            'conf_int_low': round(float(np.exp(results.conf_int().loc[var, 0])), 3),
            'conf_int_high': round(float(np.exp(results.conf_int().loc[var, 1])), 3),
        })
    
    # Trier par odds ratio décroissant (en valeur absolue)
    coefficients.sort(key=lambda x: abs(x['coef']), reverse=True)
    
    return {
        'n_obs': int(len(reg_df)),
        'pseudo_r2': round(float(results.pseudo_rsquared()), 4),
        'aic': round(float(results.aic), 1),
        'bic': round(float(results.bic), 1),
        'intercept': round(float(results.params['const']), 4),
        'coefficients': coefficients,
        'model': results,  # Garder le modèle pour les prédictions
        'feature_names': list(X.columns)
    }


def predict_probabilities(
    model_results: Dict,
    profiles: List[Dict[str, Any]]
) -> List[Dict]:
    """
    Calcule les probabilités prédites pour des profils spécifiques.
    
    Args:
        model_results: Résultat de run_logistic_regression
        profiles: Liste de dicts définissant des profils
                  Ex: [{'nom': 'Jeune urbain', 'AGE_2': 1, 'URBAIN': 1, ...}]
                  
    Returns:
        Liste de dicts avec nom du profil et probabilité prédite
        
    Example:
        >>> profiles = [
        ...     {'nom': 'Jeune', 'AGE_2': 1},
        ...     {'nom': 'Senior', 'AGE_7': 1}
        ... ]
        >>> probs = predict_probabilities(reg_results, profiles)
    """
    model = model_results['model']
    feature_names = model_results['feature_names']
    
    results = []
    for profile in profiles:
        # Créer le vecteur de features
        X = pd.DataFrame([[0.0] * len(feature_names)], columns=feature_names)
        X['const'] = 1.0
        
        # Remplir avec les valeurs du profil
        for key, value in profile.items():
            if key != 'nom' and key in X.columns:
                X[key] = value
        
        # Prédire
        prob = model.predict(X)[0] * 100
        
        results.append({
            'nom': profile.get('nom', 'Profil'),
            'probabilite': round(float(prob), 1),
            'profil': {k: v for k, v in profile.items() if k != 'nom'}
        })
    
    return results


def extract_effect_cards(
    df: pd.DataFrame,
    model_results: Dict,
    variables_config: List[Dict],
    weights: str = 'POIDS'
) -> List[Dict]:
    """
    Génère des "effect cards" montrant l'effet net de chaque variable.
    
    Chaque carte compare la probabilité pour la modalité "haute" vs "basse"
    d'une variable, toutes choses égales par ailleurs.
    
    Args:
        df: DataFrame original
        model_results: Résultat de run_logistic_regression
        variables_config: Liste de configs pour chaque variable:
            [
                {
                    'variable': 'Âge',
                    'var_code': 'AGE',
                    'modalite_haute': {'nom': '18-24 ans', 'features': {'AGE_2': 1}},
                    'modalite_basse': {'nom': '70+', 'features': {'AGE_7': 1}},
                    'couleur': '#EF4444'
                },
                ...
            ]
        weights: Colonne des poids
        
    Returns:
        Liste d'effect cards triées par écart décroissant
    """
    model = model_results['model']
    feature_names = model_results['feature_names']
    
    cards = []
    
    for config in variables_config:
        # Profil "haute" (plus numérique)
        X_haute = pd.DataFrame([[0.0] * len(feature_names)], columns=feature_names)
        X_haute['const'] = 1.0
        for feat, val in config['modalite_haute'].get('features', {}).items():
            if feat in X_haute.columns:
                X_haute[feat] = val
        
        # Profil "basse" (plus traditionnel)
        X_basse = pd.DataFrame([[0.0] * len(feature_names)], columns=feature_names)
        X_basse['const'] = 1.0
        for feat, val in config['modalite_basse'].get('features', {}).items():
            if feat in X_basse.columns:
                X_basse[feat] = val
        
        # Prédictions
        prob_haute = model.predict(X_haute)[0] * 100
        prob_basse = model.predict(X_basse)[0] * 100
        ecart = prob_haute - prob_basse
        
        # Vérifier la significativité (via les p-values des coefficients concernés)
        features_haute = list(config['modalite_haute'].get('features', {}).keys())
        features_basse = list(config['modalite_basse'].get('features', {}).keys())
        all_features = features_haute + features_basse
        
        p_values = []
        for coef in model_results['coefficients']:
            if coef['variable'] in all_features:
                p_values.append(coef['p_value'])
        
        significatif = any(p < 0.05 for p in p_values) if p_values else False
        
        if not significatif:
            continue  # Skip les non-significatifs
        
        # Ratio
        ratio = prob_haute / prob_basse if prob_basse > 0 else None
        
        cards.append({
            'variable': config['variable'],
            'var_code': config['var_code'],
            'modalite_numerique': config['modalite_haute']['nom'],
            'modalite_traditionnelle': config['modalite_basse']['nom'],
            'prob_numerique': round(prob_haute, 1),
            'prob_traditionnelle': round(prob_basse, 1),
            'ecart': round(ecart, 1),
            'ratio': round(ratio, 1) if ratio else None,
            'significatif': significatif,
            'couleur': config.get('couleur', '#6366F1')
        })
    
    # Trier par écart décroissant
    cards.sort(key=lambda x: abs(x['ecart']), reverse=True)
    
    return cards


def build_regression_summary(
    reg_results: Dict,
    var_labels: Optional[Dict[str, str]] = None
) -> Dict:
    """
    Construit un résumé lisible des résultats de régression pour le frontend.
    
    Args:
        reg_results: Résultat de run_logistic_regression
        var_labels: Mapping nom technique -> nom lisible
        
    Returns:
        Dict formaté pour affichage
    """
    coefficients = []
    for coef in reg_results['coefficients']:
        var_name = coef['variable']
        label = var_labels.get(var_name, var_name) if var_labels else var_name
        
        # Interpréter l'effet
        or_val = coef['odds_ratio']
        if or_val > 1.5:
            effet = 'Fort effet positif'
        elif or_val > 1.1:
            effet = 'Effet positif modéré'
        elif or_val > 0.9:
            effet = 'Effet faible / non significatif'
        elif or_val > 0.67:
            effet = 'Effet négatif modéré'
        else:
            effet = 'Fort effet négatif'
        
        coefficients.append({
            'variable': var_name,
            'label': label,
            'odds_ratio': coef['odds_ratio'],
            'effet': effet,
            'significatif': coef['significatif'],
            'p_value': coef['p_value'],
            'interpretation': f"Multiplie la probabilité par {coef['odds_ratio']}" if coef['odds_ratio'] >= 1 
                            else f"Divise la probabilité par {round(1/coef['odds_ratio'], 2)}"
        })
    
    return {
        'n_obs': reg_results['n_obs'],
        'pseudo_r2': reg_results['pseudo_r2'],
        'qualite': 'Bon ajustement' if reg_results['pseudo_r2'] > 0.2 else 'Ajustement modéré',
        'coefficients': coefficients
    }
