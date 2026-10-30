# -*- coding: utf-8 -*-
"""
json_builder.py - Construction et export des JSON pour le frontend

Fonctions pour créer des structures JSON cohérentes et les sauvegarder.
Assure la cohérence du format entre tous les chapitres et enquêtes.
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from datetime import datetime


class NumpyEncoder(json.JSONEncoder):
    """
    Encodeur JSON personnalisé pour gérer les types numpy et pandas.
    
    Gère: np.int64, np.float64, np.ndarray, np.bool_, pd.Timestamp, etc.
    """
    def default(self, obj):
        if isinstance(obj, (np.integer, np.int64, np.int32)):
            return int(obj)
        if isinstance(obj, (np.floating, np.float64, np.float32)):
            if np.isnan(obj):
                return None
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (np.bool_, bool)):
            return bool(obj)
        if isinstance(obj, pd.Timestamp):
            return obj.isoformat()
        if isinstance(obj, pd.Series):
            return obj.to_dict()
        if isinstance(obj, pd.DataFrame):
            return obj.to_dict(orient='records')
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        return super().default(obj)


def save_json(data: Dict, filepath: Union[str, Path], indent: int = 2) -> None:
    """
    Sauvegarde un dictionnaire en JSON avec l'encodeur numpy.
    
    Args:
        data: Dictionnaire à sauvegarder
        filepath: Chemin du fichier
        indent: Indentation (défaut: 2)
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=indent, cls=NumpyEncoder)
    
    print(f"  ✓ {filepath.name}")


def build_chapter_index(
    chapter_id: str,
    titre: str,
    sous_titre: str,
    introduction: Dict[str, str],
    sommaire: List[Dict],
    metadata: Dict
) -> Dict:
    """
    Construit l'index d'un chapitre (index.json).
    
    Args:
        chapter_id: Identifiant du chapitre (ex: 'chapitre-01')
        titre: Titre principal
        sous_titre: Sous-titre
        introduction: Dict avec 'accroche', 'contexte', 'question'
        sommaire: Liste des sections avec 'id', 'titre', 'description', 'icon'
        metadata: Métadonnées (n_total, dates, etc.)
        
    Returns:
        Dict structuré pour index.json
    """
    return {
        'id': chapter_id,
        'titre': titre,
        'sousTitre': sous_titre,
        'introduction': introduction,
        'sommaire': sommaire,
        'metadata': {
            **metadata,
            'generated_at': datetime.now().isoformat()
        }
    }


def build_section_json(
    section_id: str,
    titre: str,
    sous_titre: str,
    description: str,
    sections: List[Dict],
    note_methodologique: Optional[Dict] = None,
    synthese: Optional[Dict] = None,
    metadata: Optional[Dict] = None
) -> Dict:
    """
    Construit une section standard (01a-xxx.json, 01b-xxx.json, etc.).
    
    Args:
        section_id: Identifiant de la section
        titre: Titre de la section
        sous_titre: Sous-titre
        description: Description introductive
        sections: Liste des sous-sections avec visualisations
        note_methodologique: Note méthodologique optionnelle
        synthese: Points de synthèse optionnels
        metadata: Métadonnées additionnelles
        
    Returns:
        Dict structuré pour le JSON de section
    """
    result = {
        'id': section_id,
        'titre': titre,
        'sousTitre': sous_titre,
        'description': description,
        'sections': sections
    }
    
    if note_methodologique:
        result['noteMethodologique'] = note_methodologique
    
    if synthese:
        result['synthese'] = synthese
    
    if metadata:
        result['metadata'] = metadata
    
    return result


def build_prenotions_section(
    prenotions: List[Dict[str, Any]]
) -> Dict:
    """
    Construit une section "prénotions" (Vrai/Faux).
    
    Args:
        prenotions: Liste de dicts avec:
            - idee: L'idée reçue
            - verdict: 'VRAI', 'FAUX', ou 'NUANCÉ'
            - realite: L'explication
            - chiffre: {'valeur': '...', 'unite': '...', 'label': '...'}
            
    Returns:
        Dict structuré pour la section prénotions
    """
    return {
        'id': '01a-prenotions',
        'titre': 'Idées reçues',
        'sousTitre': 'Ce que les données nous apprennent vraiment',
        'description': 'Avant de plonger dans les chiffres, confrontons quelques préjugés courants à la réalité des données.',
        'prenotions': {
            'titre': 'Vrai ou Faux ?',
            'items': prenotions
        }
    }


def build_variable_construite_section(
    methodologie: Dict,
    groupes: List[Dict],
    n_total: int
) -> Dict:
    """
    Construit la section "variable construite" (méthodologie + résultats).
    
    Args:
        methodologie: Dict avec 'titre', 'etapes', 'avantage'
        groupes: Liste des groupes créés avec 'id', 'label', 'n', 'pct', 'couleur', 'composition'
        n_total: Nombre total d'observations
        
    Returns:
        Dict structuré pour la section variable construite
    """
    return {
        'id': '01b-variable-construite',
        'titre': 'Construction de la variable',
        'sousTitre': 'Comment nous avons catégorisé les individus',
        'description': 'Explication de la construction de notre indicateur principal.',
        'methodologie': methodologie,
        'resultats': {
            'titre': 'Résultat de la classification',
            'groupes': groupes
        },
        'metadata': {
            'n_total': n_total
        }
    }


def build_socio_demo_section(
    socio_results: List[Dict],
    effect_cards: Optional[List[Dict]] = None,
    multi_profils: Optional[Dict] = None
) -> Dict:
    """
    Construit la section d'analyse socio-démographique.
    
    Args:
        socio_results: Résultats par variable socio-démo (V de Cramer, distributions)
        effect_cards: Cartes d'effets nets optionnelles
        multi_profils: Profils combinés optionnels
        
    Returns:
        Dict structuré pour la section socio-démo
    """
    # Options de toggle pour les distributions
    distribution_options = [
        {'id': r['var_code'], 'label': r['variable'], 'v_cramer': r['v_cramer']}
        for r in socio_results
    ]
    
    # Distributions par variable
    distributions_by_var = {
        r['var_code']: {
            'type': 'distribution_bar',
            'titre': f"% par {r['variable'].lower()}",
            'data': r['distribution'],
            'v_cramer': r['v_cramer'],
            'significatif': r['significatif']
        }
        for r in socio_results
    }
    
    sections = [
        {
            'id': 'force-association',
            'titre': 'Force d\'association',
            'description': 'V de Cramer : quelles variables sont les plus liées ?',
            'visualisations': [{
                'type': 'horizontal-bar-chart',
                'data': [{'variable': r['variable'], 'v_cramer': r['v_cramer'], 'significatif': r['significatif']} 
                        for r in socio_results]
            }]
        },
        {
            'id': 'detail-par-variable',
            'titre': 'Détail par variable',
            'description': 'Explorez la distribution pour chaque variable.',
            'toggle': {
                'default': socio_results[0]['var_code'] if socio_results else None,
                'options': distribution_options
            },
            'visualisations': distributions_by_var
        }
    ]
    
    if effect_cards:
        sections.append({
            'id': 'effets-nets',
            'titre': 'Effet net par variable',
            'description': 'Probabilités toutes choses égales par ailleurs.',
            'visualisations': [{'type': 'effect_cards_par_variable', 'data': effect_cards}]
        })
    
    if multi_profils:
        sections.append({
            'id': 'profils-combines',
            'titre': 'Profils combinés',
            'description': 'Probabilité en combinant toutes les caractéristiques.',
            'visualisations': [{'type': 'effect_cards_profils', **multi_profils}]
        })
    
    return {
        'id': '01c-qui-bascule',
        'titre': 'Profil socio-démographique',
        'sousTitre': 'Qui appartient à quel groupe ?',
        'description': 'Quelles caractéristiques sociales sont les plus associées ?',
        'noteMethodologique': {
            'titre': 'Comment lire le V de Cramer',
            'texte': 'Le V de Cramer mesure la force du lien (0 = aucun, 1 = parfait). V > 0.3 = association forte, 0.15-0.3 = modérée, < 0.15 = faible.'
        },
        'sections': sections,
        'metadata': {
            'variables_analysees': len(socio_results)
        }
    }


def build_profils_types_section(
    accroche: Dict,
    messages_cles: Dict,
    parcours: Dict,
    profils: List[Dict],
    importances: List[Dict],
    methodologie: Dict,
    metadata: Dict
) -> Dict:
    """
    Construit la section des profils-types (visualisation complète).
    
    Args:
        accroche: Texte d'accroche + chiffres clés
        messages_cles: Messages clés à retenir
        parcours: Parcours décisionnel (arbre simplifié)
        profils: Liste des profils avec leurs stats
        importances: Importance des variables
        methodologie: Note méthodologique
        metadata: Métadonnées (accuracy, n_total, etc.)
        
    Returns:
        Dict structuré pour la section profils-types
    """
    # Comparaison des extrêmes
    if profils and len(profils) >= 2:
        profil_haut = profils[0]
        profil_bas = profils[-1]
        ratio = round(profil_haut['pct_numerique'] / max(profil_bas['pct_numerique'], 1), 1)
        comparaison = {
            'titre': 'D\'un extrême à l\'autre',
            'profil_haut': profil_haut,
            'profil_bas': profil_bas,
            'ratio': ratio,
            'texte': f"Un {profil_haut['nom'].lower()} a {ratio}× plus de chances que {profil_bas['nom'].lower()}."
        }
    else:
        comparaison = None
    
    return {
        'id': '01g-profils-types',
        'titre': 'Les profils-types',
        'sousTitre': 'Qui sont-ils vraiment ?',
        'accroche': accroche,
        'messagesCles': messages_cles,
        'parcours': parcours,
        'profils': {
            'titre': 'Les visages du phénomène',
            'description': 'Plusieurs profils types se dégagent de l\'analyse.',
            'data': profils,
            'comparaison': comparaison
        },
        'variablesImportance': {
            'titre': 'Le poids de chaque facteur',
            'description': 'Sur 100% d\'explication, voici ce que pèse chaque caractéristique.',
            'data': importances
        },
        'methodologie': methodologie,
        'metadata': metadata
    }


# ============================================
# HELPERS POUR FORMATER LES DONNÉES
# ============================================

def format_for_horizontal_bar(
    data: List[Dict],
    value_key: str = 'v_cramer',
    label_key: str = 'variable',
    color_key: Optional[str] = None,
    sort_by_value: bool = True
) -> List[Dict]:
    """Formate des données pour un graphique à barres horizontales."""
    formatted = []
    for item in data:
        entry = {
            'label': item.get(label_key, ''),
            'value': item.get(value_key, 0),
        }
        if color_key and color_key in item:
            entry['color'] = item[color_key]
        formatted.append(entry)
    
    if sort_by_value:
        formatted.sort(key=lambda x: x['value'], reverse=True)
    
    return formatted


def format_for_stacked_bar(
    data: List[Dict],
    categories: List[str],
    group_key: str = 'category'
) -> Dict:
    """Formate des données pour un graphique à barres empilées."""
    return {
        'categories': categories,
        'data': data
    }
