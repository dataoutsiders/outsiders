import os
"""
Script pour corriger les accents dans le JSON du chapitre 1
"""
import json
from pathlib import Path

# Chemin du JSON
json_path = Path(os.path.expanduser("~/Documents/VsCode/outsiders/frontend/public/data/enquetes/francais-information/chapitres/chapitre-01-basculement.json"))

print(f"Lecture de {json_path}...")
with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Dictionnaire de remplacement
REPLACEMENTS = {
    # Mots courants
    'Francais': 'Français',
    'francais': 'français',
    'television': 'télévision',
    'Television': 'Télévision',
    'reseaux sociaux': 'réseaux sociaux',
    'Reseaux sociaux': 'Réseaux sociaux',
    'medias': 'médias',
    'Medias': 'Médias',
    'generation': 'génération',
    'generationnel': 'générationnel',
    'defiance': 'défiance',
    'desinformation': 'désinformation',
    'democratie': 'démocratie',
    'Democratie': 'Démocratie',
    'enquete': 'enquête',
    'interet': 'intérêt',
    'Interet': 'Intérêt',
    'ecart': 'écart',
    'cede': 'cède',
    'frequence': 'fréquence',
    'Frequence': 'Fréquence',
    'societe': 'société',
    'realite': 'réalité',
    'verite': 'vérité',
    'aines': 'aînés',
    'permeables': 'perméables',
    'desertent': 'désertent',
    'decrocher': 'décrocher',
    'lineaire': 'linéaire',
    'evolue': 'évolue',
    'mediatique': 'médiatique',
    'numerique': 'numérique',
    'Numerique': 'Numérique',
    'regularite': 'régularité',
    'regulierement': 'régulièrement',
    'eleve': 'élevé',
    'Eleve': 'Élevé',
    'etudes': 'études',
    'Etudes': 'Études',
    'etudiants': 'étudiants',
    'Etudiants': 'Étudiants',
    'retraites': 'retraités',
    'Retraites': 'Retraités',
    'donnees': 'données',
    'Donnees': 'Données',
    'echantillon': 'échantillon',
    'methodologie': 'méthodologie',
    'differenci': 'différenci',
    'reference': 'référence',
    'creer': 'créer',
    'createurs': 'créateurs',
    'education': 'éducation',
    'Education': 'Éducation',
    'elements': 'éléments',
    'evenement': 'événement',
    'evenements': 'événements',
    'economique': 'économique',
    'Economique': 'Économique',
    'repondants': 'répondants',
    'categories': 'catégories',
    'categorie': 'catégorie',
    'cles': 'clés',
    'cle': 'clé',
    'systeme': 'système',
    'prenotions': 'prénotions',
    'Prenotions': 'Prénotions',
    'prejuge': 'préjugé',
    'idees recues': 'idées reçues',
    'debat': 'débat',
    'premiere': 'première',
    'quatrieme': 'quatrième',
    'meme': 'même',
    # Avec apostrophes
    "l'age": "l'âge",
    "d'age": "d'âge",
    # Cas spéciaux
    'A retenir': 'À retenir',
    'A nuancer': 'À nuancer',
}

def fix_accents(text):
    """Applique les remplacements sur une chaîne"""
    if not isinstance(text, str):
        return text
    for old, new in REPLACEMENTS.items():
        text = text.replace(old, new)
    return text

def fix_dict(obj):
    """Parcourt récursivement et corrige les accents"""
    if isinstance(obj, dict):
        return {k: fix_dict(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [fix_dict(item) for item in obj]
    elif isinstance(obj, str):
        return fix_accents(obj)
    return obj

# Appliquer les corrections
print("Correction des accents...")
data = fix_dict(data)

# Sauvegarder
print(f"Sauvegarde...")
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Accents corrigés avec succès !")
