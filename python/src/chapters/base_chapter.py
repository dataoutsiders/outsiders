# -*- coding: utf-8 -*-
"""
base_chapter.py - Classe de base pour générer un chapitre

Fournit une structure commune pour tous les chapitres avec :
- Chargement des données
- Génération des sections standards
- Export des JSON
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod

from ..core.weighted_stats import (
    cramers_v_weighted,
    get_distribution_by_var,
    get_prevalence
)
from ..core.regression import (
    run_logistic_regression,
    extract_effect_cards,
    predict_probabilities
)
from ..core.tree_profiler import (
    build_decision_tree,
    extract_profiles_from_tree,
    extract_decision_path
)
from ..core.json_builder import (
    save_json,
    build_chapter_index,
    build_section_json,
    build_prenotions_section,
    build_variable_construite_section,
    build_socio_demo_section,
    build_profils_types_section
)
from .chapter_config import ChapterConfig


class BaseChapter(ABC):
    """
    Classe de base pour la génération d'un chapitre.
    
    Hériter de cette classe et implémenter les méthodes abstraites
    pour créer un nouveau chapitre.
    
    Example:
        >>> class Chapitre01Basculement(BaseChapter):
        ...     def build_target_variable(self, df):
        ...         # Logique spécifique
        ...         return df
        ...     
        ...     def get_prenotions(self):
        ...         return [...]
        >>> 
        >>> chapter = Chapitre01Basculement(config)
        >>> chapter.generate_all()
    """
    
    def __init__(self, config: ChapterConfig):
        """
        Initialise le chapitre avec sa configuration.
        
        Args:
            config: Configuration du chapitre (ChapterConfig)
        """
        self.config = config
        self.df = None
        self.generated_data = {}
        
    def load_data(self) -> pd.DataFrame:
        """
        Charge les données source.
        
        Returns:
            DataFrame chargé
        """
        if self.config.data_path is None:
            raise ValueError("data_path non défini dans la configuration")
        
        path = self.config.data_path
        
        if path.suffix == '.xlsx':
            self.df = pd.read_excel(path)
        elif path.suffix == '.csv':
            self.df = pd.read_csv(path)
        elif path.suffix == '.pkl':
            self.df = pd.read_pickle(path)
        else:
            raise ValueError(f"Format non supporté : {path.suffix}")
        
        # Convertir les poids si nécessaire (format français avec virgules)
        weights_col = self.config.weights_col
        if weights_col in self.df.columns:
            if self.df[weights_col].dtype == 'object':
                self.df[weights_col] = self.df[weights_col].str.replace(',', '.').astype(float)
            else:
                self.df[weights_col] = pd.to_numeric(self.df[weights_col], errors='coerce').fillna(1)
        
        print(f"Données chargées : {len(self.df)} observations")
        return self.df
    
    @abstractmethod
    def build_target_variable(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Construit la variable dépendante principale.
        
        À implémenter dans chaque chapitre selon sa logique propre.
        
        Args:
            df: DataFrame source
            
        Returns:
            DataFrame avec la colonne target ajoutée
        """
        pass
    
    def get_prenotions(self) -> List[Dict]:
        """
        Retourne les prénotions à tester.
        
        Peut être surchargée ou utiliser self.config.prenotions.
        
        Returns:
            Liste des prénotions
        """
        return self.config.prenotions
    
    def analyze_socio_demo(self) -> List[Dict]:
        """
        Analyse les variables socio-démographiques.
        
        Returns:
            Liste des résultats par variable (V de Cramer, distributions)
        """
        if self.df is None:
            raise ValueError("Données non chargées. Appeler load_data() d'abord.")
        
        target = self.config.target_col
        weights = self.config.weights_col
        
        results = []
        
        for var_tuple in self.config.socio_vars:
            var_col, var_label, var_labels = var_tuple
            
            if var_col not in self.df.columns:
                print(f"  ⚠ Variable {var_col} non trouvée")
                continue
            
            mask = self.df[var_col].notna() & self.df[target].notna()
            if mask.sum() < 100:
                continue
            
            # V de Cramer
            v, chi2, p = cramers_v_weighted(
                self.df.loc[mask, var_col],
                self.df.loc[mask, target],
                self.df.loc[mask, weights]
            )
            
            # Distribution
            distribution = get_distribution_by_var(
                self.df, var_col, target, weights, var_labels
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
        
        # Trier par V de Cramer décroissant
        results.sort(key=lambda x: x['v_cramer'], reverse=True)
        
        self.generated_data['socio_results'] = results
        return results
    
    def run_regression(self) -> Dict:
        """
        Exécute la régression logistique.
        
        Returns:
            Résultats de la régression
        """
        if self.df is None:
            raise ValueError("Données non chargées.")
        
        results = run_logistic_regression(
            self.df,
            target=self.config.target_col,
            features=self.config.regression_features,
            weights=self.config.weights_col,
            categorical_features=self.config.regression_categorical,
            reference_categories=self.config.regression_references
        )
        
        self.generated_data['regression_results'] = results
        return results
    
    def extract_effect_cards(self) -> List[Dict]:
        """
        Génère les effect cards à partir de la régression.
        
        Returns:
            Liste des effect cards
        """
        if 'regression_results' not in self.generated_data:
            self.run_regression()
        
        cards = extract_effect_cards(
            self.df,
            self.generated_data['regression_results'],
            self.config.effect_cards_config,
            self.config.weights_col
        )
        
        self.generated_data['effect_cards'] = cards
        return cards
    
    def build_tree_and_profiles(self) -> Dict:
        """
        Construit l'arbre de décision et extrait les profils.
        
        Returns:
            Dict avec arbre, profils, importances
        """
        if self.df is None:
            raise ValueError("Données non chargées.")
        
        # Construire l'arbre
        tree_results = build_decision_tree(
            self.df,
            target=self.config.target_col,
            features=self.config.tree_features,
            weights=self.config.weights_col,
            max_depth=self.config.tree_max_depth,
            categorical_features=self.config.tree_categorical
        )
        
        # Extraire les profils
        profiles = extract_profiles_from_tree(
            tree_results,
            self.config.profile_definitions
        )
        
        self.generated_data['tree_results'] = tree_results
        self.generated_data['profiles'] = profiles
        
        return {
            'tree': tree_results,
            'profiles': profiles,
            'importances': tree_results['importances'],
            'accuracy': tree_results['accuracy']
        }
    
    def generate_index_json(self) -> Dict:
        """
        Génère le fichier index.json du chapitre.
        
        Returns:
            Dict de l'index
        """
        # Sommaire basé sur les sections à générer
        sommaire = []
        
        section_mapping = {
            'prenotions': ('01a-prenotions', 'Idées reçues', 'Ce qu\'on croit savoir', 'lightbulb'),
            'variable_construite': ('01b-variable-construite', 'Construction de la variable', 'Notre indicateur principal', 'build'),
            'qui_bascule': ('01c-qui-bascule', 'Qui ?', 'Le profil socio-démographique', 'people'),
            'ce_qui_accompagne': ('01d-ce-qui-accompagne', 'Quoi d\'autre ?', 'Équipements, usages, valeurs', 'devices'),
            'regression': ('01e-regression', 'Ce qui compte vraiment', 'Régression multivariée', 'analytics'),
            'effets_stratifies': ('01f-effets-stratifies', 'Effets différenciés', 'Interactions entre variables', 'layers'),
            'profils_types': ('01g-profils-types', 'Les profils-types', 'Les visages du phénomène', 'users'),
        }
        
        for section in self.config.sections_to_generate:
            if section in section_mapping:
                sec_id, titre, desc, icon = section_mapping[section]
                sommaire.append({
                    'id': sec_id,
                    'titre': titre,
                    'description': desc,
                    'icon': icon
                })
        
        # Métadonnées
        target = self.config.target_col
        weights = self.config.weights_col
        
        if self.df is not None and target in self.df.columns:
            mask = self.df[target].notna()
            n_total = len(self.df)
            n_analyse = mask.sum()
            
            # % par groupe
            pct_by_group = {}
            for val, label in self.config.target_labels.items():
                val_mask = mask & (self.df[target] == val)
                pct = self.df.loc[val_mask, weights].sum() / self.df.loc[mask, weights].sum() * 100
                pct_by_group[label.lower()] = round(pct, 1)
        else:
            n_total = 0
            n_analyse = 0
            pct_by_group = {}
        
        index_data = build_chapter_index(
            chapter_id=f"chapitre-{self.config.chapter_id}",
            titre=self.config.titre,
            sous_titre=self.config.sous_titre,
            introduction=self.config.introduction,
            sommaire=sommaire,
            metadata={
                'n_total': n_total,
                'n_analyse': n_analyse,
                **pct_by_group
            }
        )
        
        self.generated_data['index'] = index_data
        return index_data
    
    def generate_all(self, save: bool = True) -> Dict[str, Dict]:
        """
        Génère tous les JSON du chapitre.
        
        Args:
            save: Si True, sauvegarde les fichiers
            
        Returns:
            Dict de tous les JSON générés
        """
        print(f"\n{'='*50}")
        print(f"GÉNÉRATION : {self.config.titre}")
        print(f"{'='*50}")
        
        # 1. Charger les données
        print("\n1. Chargement des données...")
        self.load_data()
        
        # 2. Construire la variable cible
        print("\n2. Construction de la variable cible...")
        self.df = self.build_target_variable(self.df)
        
        # 3. Générer chaque section
        all_json = {}
        
        if 'index' in self.config.sections_to_generate:
            print("\n3. Génération de l'index...")
            all_json['index'] = self.generate_index_json()
        
        if 'qui_bascule' in self.config.sections_to_generate:
            print("\n4. Analyse socio-démographique...")
            self.analyze_socio_demo()
        
        if 'regression' in self.config.sections_to_generate:
            print("\n5. Régression logistique...")
            self.run_regression()
            self.extract_effect_cards()
        
        if 'profils_types' in self.config.sections_to_generate:
            print("\n6. Arbre de décision et profils...")
            self.build_tree_and_profiles()
        
        # Sauvegarder si demandé
        if save and self.config.output_dir:
            print(f"\n7. Sauvegarde dans {self.config.output_dir}...")
            self.config.output_dir.mkdir(parents=True, exist_ok=True)
            
            for name, data in self.generated_data.items():
                if isinstance(data, dict):
                    filename = f"{data.get('id', name)}.json"
                    save_json(data, self.config.output_dir / filename)
        
        print(f"\n{'='*50}")
        print("GÉNÉRATION TERMINÉE")
        print(f"{'='*50}")
        
        return self.generated_data
