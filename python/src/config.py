"""
Configuration centrale du projet Outsiders
"""
from pathlib import Path

# Chemins
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
EXPORTS_DIR = BASE_DIR / "exports"

# Structure des exports
EXPORTS_ENQUETES_DIR = EXPORTS_DIR / "enquetes"
EXPORTS_TRANSVERSAL_DIR = EXPORTS_DIR / "transversal"

# Thèmes transversaux
THEMES_TRANSVERSAUX = {
    # === RAPPORTS SOCIAUX (variables de différenciation) ===
    "genre": {
        "id": "genre",
        "titre": "Genre",
        "description": "Différences et inégalités entre hommes et femmes",
        "question": "Comment les pratiques varient-elles selon le genre ?",
        "icon": "users",
    },
    "classe": {
        "id": "classe",
        "titre": "Classe sociale",
        "description": "Distinction, contrainte et position sociale",
        "question": "Comment la position sociale structure-t-elle les pratiques ?",
        "icon": "layers",
    },
    "generations": {
        "id": "generations",
        "titre": "Générations",
        "description": "Différences et transmissions entre générations",
        "question": "Effet d'âge ou effet de génération ? Vraies ruptures ou faux débats ?",
        "icon": "calendar",
    },
    "doubles-peines": {
        "id": "doubles-peines",
        "titre": "Doubles peines",
        "description": "Quand les désavantages se cumulent et se multiplient",
        "question": "Comment les inégalités se cumulent-elles ? Qui subit plusieurs handicaps à la fois ?",
        "icon": "git-merge",
    },

    # === GRILLES D'ANALYSE (prismes conceptuels) ===
    "universalite": {
        "id": "universalite",
        "titre": "Universalité",
        "description": "Déconstruire ce qui se présente comme universel, normal, évident",
        "question": "Qu'est-ce qui passe pour 'naturel' alors que c'est socialement situé ?",
        "icon": "eye",
    },
    "legitimites": {
        "id": "legitimites",
        "titre": "Légitimités",
        "description": "Les échelles de légitimité et leur hiérarchie",
        "question": "Quels systèmes de valeur coexistent ? Comment s'affrontent-ils ?",
        "icon": "scale",
    },
    "france": {
        "id": "france",
        "titre": "Portrait de la France",
        "description": "Ce qui caractérise la France dans ses pratiques sociales",
        "question": "Qu'est-ce qui fait la spécificité française ?",
        "icon": "map-pin",
    },
}

# Variables d'analyse standard
VARIABLES_GENRE = ["sexe", "genre", "sex"]
VARIABLES_AGE = ["age", "tranche_age", "age_group", "generation"]
VARIABLES_CLASSE = ["csp", "pcs", "diplome", "niveau_etudes", "revenu", "profession"]
VARIABLES_TERRITOIRE = ["region", "taille_agglo", "rural_urbain"]


def get_enquete_dir(enquete_id: str) -> Path:
    """Retourne le chemin du dossier d'export pour une enquête."""
    return EXPORTS_ENQUETES_DIR / enquete_id


def get_transversal_dir() -> Path:
    """Retourne le chemin du dossier transversal."""
    return EXPORTS_TRANSVERSAL_DIR


def ensure_export_dirs():
    """Crée les dossiers d'export s'ils n'existent pas."""
    EXPORTS_ENQUETES_DIR.mkdir(parents=True, exist_ok=True)
    EXPORTS_TRANSVERSAL_DIR.mkdir(parents=True, exist_ok=True)
