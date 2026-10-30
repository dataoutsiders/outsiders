# -*- coding: utf-8 -*-
"""
weighted_stats.py - Statistiques pondérées pour données d'enquête

Fonctions pour calculer des statistiques en tenant compte des poids
de sondage (redressement). Indispensable pour les enquêtes INSEE, ARCOM, etc.
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Optional, Dict, List, Tuple, Union


def cramers_v_weighted(
    x: pd.Series, 
    y: pd.Series, 
    weights: pd.Series
) -> Tuple[float, float, float]:
    """
    Calcule le V de Cramer pondéré entre deux variables catégorielles.
    
    Le V de Cramer mesure la force d'association entre deux variables
    catégorielles (0 = aucune association, 1 = association parfaite).
    
    Args:
        x: Première variable catégorielle
        y: Deuxième variable catégorielle  
        weights: Poids de sondage
        
    Returns:
        Tuple (v_cramer, chi2, p_value)
        
    Example:
        >>> v, chi2, p = cramers_v_weighted(df['AGE'], df['USAGE'], df['POIDS'])
        >>> print(f"V de Cramer = {v:.3f}, p = {p:.4f}")
    """
    # Tableau de contingence pondéré
    contingency = pd.crosstab(x, y, weights, aggfunc='sum').fillna(0)
    
    if contingency.shape[0] < 2 or contingency.shape[1] < 2:
        return 0.0, 0.0, 1.0
    
    # Test du Chi2
    chi2, p, dof, expected = stats.chi2_contingency(contingency)
    
    # Calcul du V de Cramer
    n = contingency.sum().sum()
    min_dim = min(contingency.shape) - 1
    
    if min_dim == 0 or n == 0:
        return 0.0, chi2, p
        
    v = np.sqrt(chi2 / (n * min_dim))
    
    return float(v), float(chi2), float(p)


def chi2_weighted(
    x: pd.Series,
    y: pd.Series,
    weights: pd.Series
) -> Dict:
    """
    Test du Chi2 pondéré avec détails complets.
    
    Args:
        x, y: Variables catégorielles
        weights: Poids de sondage
        
    Returns:
        Dict avec chi2, p_value, dof, tableau de contingence, résidus
    """
    contingency = pd.crosstab(x, y, weights, aggfunc='sum').fillna(0)
    
    if contingency.shape[0] < 2 or contingency.shape[1] < 2:
        return {
            'chi2': 0.0,
            'p_value': 1.0,
            'dof': 0,
            'significatif': False,
            'contingency': contingency.to_dict()
        }
    
    chi2, p, dof, expected = stats.chi2_contingency(contingency)
    
    # Résidus standardisés (utiles pour interpréter quelles cellules contribuent)
    residuals = (contingency - expected) / np.sqrt(expected)
    
    return {
        'chi2': float(chi2),
        'p_value': float(p),
        'dof': int(dof),
        'significatif': p < 0.05,
        'contingency': contingency.to_dict(),
        'expected': pd.DataFrame(expected, 
                                  index=contingency.index, 
                                  columns=contingency.columns).to_dict(),
        'residuals': residuals.to_dict()
    }


def get_distribution_by_var(
    df: pd.DataFrame,
    var: str,
    vd: str,
    weights: str = 'POIDS',
    labels: Optional[Dict] = None,
    vd_value: int = 1
) -> List[Dict]:
    """
    Calcule la distribution d'une variable dépendante par modalité d'une variable explicative.
    
    Typiquement utilisé pour : "Quel % de [VD=1] dans chaque catégorie de [var] ?"
    
    Args:
        df: DataFrame
        var: Variable explicative (ex: 'AGE')
        vd: Variable dépendante binaire (ex: 'BASCULEMENT')
        weights: Nom de la colonne des poids
        labels: Dict de mapping code -> label (ex: {1: '15-24 ans', 2: '25-34 ans'})
        vd_value: Valeur de la VD pour laquelle calculer le % (défaut: 1)
        
    Returns:
        Liste de dicts avec category, code, pct_vd, pct_not_vd, n
        
    Example:
        >>> dist = get_distribution_by_var(df, 'AGE', 'NUMERIQUE', 'POIDS', AGE_LABELS)
        >>> for d in dist:
        ...     print(f"{d['category']}: {d['pct_vd']}% numériques")
    """
    mask = df[var].notna() & df[vd].notna()
    distribution = []
    
    for val in sorted(df.loc[mask, var].unique()):
        val_mask = mask & (df[var] == val)
        w = df.loc[val_mask, weights]
        y = df.loc[val_mask, vd]
        
        # % avec VD = vd_value
        pct_vd = (y == vd_value).astype(float).multiply(w).sum() / w.sum() * 100
        n = val_mask.sum()
        
        # Label
        if labels:
            label = labels.get(int(val), str(int(val)))
        else:
            label = str(int(val)) if pd.notna(val) else 'NA'
        
        distribution.append({
            'category': label,
            'code': int(val) if pd.notna(val) else None,
            'pct_vd': round(pct_vd, 1),
            'pct_not_vd': round(100 - pct_vd, 1),
            'n': int(n)
        })
    
    return distribution


def get_prevalence(
    df: pd.DataFrame,
    var: str,
    weights: str = 'POIDS',
    value: int = 1
) -> float:
    """
    Calcule la prévalence pondérée d'une variable binaire.
    
    Args:
        df: DataFrame
        var: Variable binaire
        weights: Colonne des poids
        value: Valeur pour laquelle calculer la prévalence (défaut: 1)
        
    Returns:
        Prévalence en % (0-100)
    """
    mask = df[var].notna()
    w = df.loc[mask, weights]
    v = df.loc[mask, var]
    return round((v == value).astype(float).multiply(w).sum() / w.sum() * 100, 1)


def weighted_mean(
    df: pd.DataFrame,
    var: str,
    weights: str = 'POIDS',
    by: Optional[str] = None
) -> Union[float, Dict[str, float]]:
    """
    Calcule la moyenne pondérée d'une variable numérique.
    
    Args:
        df: DataFrame
        var: Variable numérique
        weights: Colonne des poids
        by: Variable de groupement (optionnel)
        
    Returns:
        Moyenne pondérée, ou dict de moyennes par groupe
    """
    if by is None:
        mask = df[var].notna()
        return float(np.average(df.loc[mask, var], weights=df.loc[mask, weights]))
    else:
        results = {}
        for group_val in df[by].dropna().unique():
            mask = (df[by] == group_val) & df[var].notna()
            if mask.sum() > 0:
                results[str(group_val)] = float(
                    np.average(df.loc[mask, var], weights=df.loc[mask, weights])
                )
        return results


def weighted_crosstab(
    df: pd.DataFrame,
    row_var: str,
    col_var: str,
    weights: str = 'POIDS',
    normalize: str = 'all',
    row_labels: Optional[Dict] = None,
    col_labels: Optional[Dict] = None
) -> Dict:
    """
    Tableau croisé pondéré avec options de normalisation.
    
    Args:
        df: DataFrame
        row_var: Variable en ligne
        col_var: Variable en colonne
        weights: Colonne des poids
        normalize: 'all' (% total), 'index' (% ligne), 'columns' (% colonne), None (effectifs)
        row_labels, col_labels: Dicts de mapping code -> label
        
    Returns:
        Dict avec le tableau, les totaux lignes/colonnes, le total général
    """
    # Tableau de base
    ct = pd.crosstab(
        df[row_var], 
        df[col_var], 
        df[weights], 
        aggfunc='sum'
    ).fillna(0)
    
    # Normalisation
    if normalize == 'all':
        ct_norm = ct / ct.sum().sum() * 100
    elif normalize == 'index':
        ct_norm = ct.div(ct.sum(axis=1), axis=0) * 100
    elif normalize == 'columns':
        ct_norm = ct.div(ct.sum(axis=0), axis=1) * 100
    else:
        ct_norm = ct
    
    # Appliquer les labels
    if row_labels:
        ct_norm.index = [row_labels.get(i, str(i)) for i in ct_norm.index]
    if col_labels:
        ct_norm.columns = [col_labels.get(c, str(c)) for c in ct_norm.columns]
    
    return {
        'table': ct_norm.round(1).to_dict(),
        'row_totals': ct.sum(axis=1).to_dict(),
        'col_totals': ct.sum(axis=0).to_dict(),
        'grand_total': float(ct.sum().sum()),
        'normalize': normalize
    }


def compare_groups(
    df: pd.DataFrame,
    var: str,
    group_var: str,
    weights: str = 'POIDS',
    group_labels: Optional[Dict] = None
) -> Dict:
    """
    Compare une variable entre groupes avec moyennes pondérées et tests.
    
    Args:
        df: DataFrame
        var: Variable à comparer (numérique ou binaire)
        group_var: Variable de groupement
        weights: Colonne des poids
        group_labels: Labels des groupes
        
    Returns:
        Dict avec moyennes par groupe, écarts, V de Cramer si catégoriel
    """
    results = {
        'groups': [],
        'overall_mean': None,
        'v_cramer': None,
        'significatif': None
    }
    
    mask = df[var].notna() & df[group_var].notna()
    
    # Moyenne globale
    results['overall_mean'] = weighted_mean(df[mask], var, weights)
    
    # Par groupe
    for group_val in sorted(df.loc[mask, group_var].unique()):
        g_mask = mask & (df[group_var] == group_val)
        g_mean = weighted_mean(df[g_mask], var, weights)
        
        label = group_labels.get(group_val, str(group_val)) if group_labels else str(group_val)
        
        results['groups'].append({
            'code': int(group_val) if pd.notna(group_val) else None,
            'label': label,
            'mean': round(g_mean, 2),
            'ecart': round(g_mean - results['overall_mean'], 2),
            'n': int(g_mask.sum())
        })
    
    # V de Cramer si la variable est catégorielle/binaire
    if df[var].nunique() <= 10:
        v, chi2, p = cramers_v_weighted(df.loc[mask, group_var], df.loc[mask, var], df.loc[mask, weights])
        results['v_cramer'] = round(v, 3)
        results['chi2'] = round(chi2, 1)
        results['p_value'] = p
        results['significatif'] = p < 0.05
    
    return results
