# -*- coding: utf-8 -*-
"""
Core - Fonctions statistiques réutilisables pour Outsiders
"""

from .weighted_stats import (
    cramers_v_weighted,
    chi2_weighted,
    get_distribution_by_var,
    get_prevalence,
    weighted_mean,
    weighted_crosstab
)

from .regression import (
    run_logistic_regression,
    predict_probabilities,
    extract_effect_cards
)

from .tree_profiler import (
    build_decision_tree,
    extract_profiles_from_tree,
    extract_decision_path
)

from .json_builder import (
    NumpyEncoder,
    save_json,
    build_section_json,
    build_chapter_index
)

__all__ = [
    # weighted_stats
    'cramers_v_weighted',
    'chi2_weighted', 
    'get_distribution_by_var',
    'get_prevalence',
    'weighted_mean',
    'weighted_crosstab',
    # regression
    'run_logistic_regression',
    'predict_probabilities',
    'extract_effect_cards',
    # tree_profiler
    'build_decision_tree',
    'extract_profiles_from_tree',
    'extract_decision_path',
    # json_builder
    'NumpyEncoder',
    'save_json',
    'build_section_json',
    'build_chapter_index',
]
