# -*- coding: utf-8 -*-
"""
chapter_config.py - Configuration d'un chapitre

Classe de configuration qui définit tous les paramètres d'un chapitre :
- Variables à analyser
- Labels et mappings
- Sections à générer
- Profils à extraire
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from pathlib import Path


@dataclass
class ChapterConfig:
    """
    Configuration complète d'un chapitre.
    
    Attributes:
        chapter_id: Identifiant unique (ex: '01-basculement')
        titre: Titre principal
        sous_titre: Sous-titre
        data_path: Chemin vers les données source
        output_dir: Répertoire de sortie pour les JSON
        
        # Colonnes
        weights_col: Nom de la colonne des poids
        target_col: Nom de la variable dépendante principale
        target_labels: Labels de la VD {0: 'Traditionnel', 1: 'Numérique'}
        
        # Variables socio-démo
        socio_vars: Liste des variables socio-démo à analyser
        socio_labels: Dict des labels par variable
        
        # Variables d'accompagnement (équipement, usages, valeurs)
        accomp_vars: Variables d'accompagnement
        accomp_labels: Labels correspondants
        
        # Profils
        profile_definitions: Définitions des profils à extraire
        
        # Sections à générer
        sections_to_generate: Liste des sections à générer
        
    Example:
        >>> config = ChapterConfig(
        ...     chapter_id='01-basculement',
        ...     titre='Le basculement numérique',
        ...     data_path='data/arcom-2024.xlsx',
        ...     target_col='BASCULEMENT',
        ...     socio_vars=[
        ...         ('AGE', 'Âge', AGE_LABELS),
        ...         ('DIPLOME', 'Diplôme', DIPLOME_LABELS),
        ...     ]
        ... )
    """
    # Identité
    chapter_id: str
    titre: str
    sous_titre: str = ""
    
    # Chemins
    data_path: Path = None
    output_dir: Path = None
    
    # Colonnes principales
    weights_col: str = 'POIDS03'
    target_col: str = None
    target_labels: Dict[int, str] = field(default_factory=lambda: {0: 'Non', 1: 'Oui'})
    
    # Introduction
    introduction: Dict[str, str] = field(default_factory=dict)
    
    # Variables socio-démo : List[(var_col, label, labels_dict)]
    socio_vars: List[tuple] = field(default_factory=list)
    
    # Variables d'accompagnement : List[(var_col, label, groupe)]
    accomp_vars: List[tuple] = field(default_factory=list)
    
    # Définitions des profils
    profile_definitions: List[Dict] = field(default_factory=list)
    
    # Sections à générer
    sections_to_generate: List[str] = field(default_factory=lambda: [
        'index',
        'prenotions',
        'variable_construite',
        'qui_bascule',
        'ce_qui_accompagne',
        'regression',
        'effets_stratifies',
        'profils_types'
    ])
    
    # Prénotions
    prenotions: List[Dict] = field(default_factory=list)
    
    # Construction de la VD
    vd_construction: Dict = field(default_factory=dict)
    
    # Config régression
    regression_features: List[str] = field(default_factory=list)
    regression_categorical: List[str] = field(default_factory=list)
    regression_references: Dict[str, Any] = field(default_factory=dict)
    
    # Config arbre
    tree_features: List[str] = field(default_factory=list)
    tree_categorical: List[str] = field(default_factory=list)
    tree_max_depth: int = 4
    
    # Effect cards config
    effect_cards_config: List[Dict] = field(default_factory=list)
    
    def __post_init__(self):
        """Convertit les chemins en Path si nécessaire."""
        if self.data_path and not isinstance(self.data_path, Path):
            self.data_path = Path(self.data_path)
        if self.output_dir and not isinstance(self.output_dir, Path):
            self.output_dir = Path(self.output_dir)


# ============================================
# LABELS STANDARDS RÉUTILISABLES
# ============================================

# Labels d'âge standards (7 tranches ARCOM/INSEE)
AGE_LABELS_7 = {
    1: '15-17 ans',
    2: '18-24 ans', 
    3: '25-34 ans',
    4: '35-44 ans',
    5: '45-59 ans',
    6: '60-69 ans',
    7: '70 ans et +'
}

# Labels d'âge regroupés (3 tranches)
AGE_LABELS_3 = {
    1: '15-34 ans',
    2: '35-59 ans',
    3: '60 ans et +'
}

# Labels diplôme (7 niveaux)
DIPLOME_LABELS_7 = {
    1: 'Sans diplôme',
    2: 'BEPC/Brevet',
    3: 'CAP/BEP',
    4: 'Bac',
    5: 'Bac+2',
    6: 'Bac+3/4',
    7: 'Bac+5 et +'
}

# Labels diplôme regroupés (3 niveaux)
DIPLOME_LABELS_3 = {
    1: 'Peu ou pas diplômé',
    2: 'Bac / Bac+2',
    3: 'Bac+3 et plus'
}

# Labels genre
GENRE_LABELS = {
    1: 'Homme',
    2: 'Femme'
}

# Labels CSP
CSP_LABELS = {
    1: 'Agriculteur',
    2: 'Artisan/Commerçant',
    3: 'Cadre/Prof. intellectuelle',
    4: 'Profession intermédiaire',
    5: 'Employé',
    6: 'Ouvrier',
    7: 'NSP/Refus'
}

# Labels taille agglo
AGGLO_LABELS = {
    1: 'Commune rurale',
    2: '2 000 - 20 000 hab.',
    3: '20 000 - 100 000 hab.',
    4: '100 000 hab. et +',
    5: 'Agglomération parisienne'
}

# Labels situation professionnelle
SITUATION_PRO_LABELS = {
    1: 'Actif à temps plein',
    2: 'Actif à temps partiel',
    3: 'Étudiant/Élève',
    4: 'Chômeur',
    5: 'Femme/Homme au foyer',
    6: 'Retraité',
    7: 'En incapacité',
    8: 'Autre inactif'
}

# Couleurs standards pour les visualisations
COULEURS = {
    'rouge': '#EF4444',
    'orange': '#F59E0B',
    'jaune': '#FCD34D',
    'vert': '#10B981',
    'teal': '#14B8A6',
    'bleu': '#3B82F6',
    'indigo': '#6366F1',
    'violet': '#8B5CF6',
    'rose': '#EC4899',
    'gris': '#6B7280'
}

# Gradients Tailwind
GRADIENTS = {
    'numerique': 'from-emerald-500 to-teal-500',
    'traditionnel': 'from-indigo-500 to-blue-500',
    'mixte': 'from-amber-500 to-orange-500',
    'jeune': 'from-pink-500 to-rose-500',
    'senior': 'from-violet-500 to-purple-500'
}
