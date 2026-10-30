"""
Script principal pour lancer les analyses Outsiders.

Architecture:
- Chaque enquête génère ses propres analyses par thème
- Les analyses transversales synthétisent les résultats de toutes les enquêtes

Usage:
    python run_analysis.py                           # Liste les données disponibles
    python run_analysis.py --enquete <id>            # Analyse une enquête
    python run_analysis.py --transversal             # Génère les synthèses transversales
    python run_analysis.py --all                     # Tout analyser
"""
import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

# Ajouter src au path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config import (
    DATA_DIR, EXPORTS_DIR, THEMES_TRANSVERSAUX,
    get_enquete_dir, get_transversal_dir, ensure_export_dirs
)
from data_loader import load_csv, clean_dataframe
from analysis import (
    descriptive_stats, crosstab_analysis, group_comparison,
    run_acm, run_clustering, run_regression
)
from export import export_to_json


# =============================================================================
# REGISTRE DES ENQUÊTES
# =============================================================================

ENQUETES = {
    # À compléter au fur et à mesure des enquêtes ajoutées
    # "francais-information": {
    #     "id": "francais-information",
    #     "titre": "Les Français et l'information",
    #     "source": "data.gouv.fr",
    #     "annee": 2024,
    #     "fichier": "francais_information_2024.csv",
    #     "description": "Enquête sur les pratiques informationnelles des Français",
    #     "variables": {
    #         "genre": "sexe",
    #         "age": "age",
    #         "classe": "csp",
    #         ...
    #     }
    # },
}


# =============================================================================
# ANALYSE D'UNE ENQUÊTE
# =============================================================================

def analyze_enquete(enquete_id: str, df=None):
    """
    Analyse complète d'une enquête selon tous les thèmes.

    Génère dans exports/enquetes/<enquete_id>/:
    - metadata.json : infos sur l'enquête
    - exploration.json : stats descriptives
    - genre.json : analyse H/F
    - classe.json : analyse par CSP/diplôme
    - generations.json : analyse par âge
    - legitimites.json : ACM + clustering
    - universalite.json : déconstruction des normes
    """
    print(f"\n{'='*60}")
    print(f"ANALYSE : {enquete_id}")
    print(f"{'='*60}")

    # Créer le dossier d'export
    export_dir = get_enquete_dir(enquete_id)
    export_dir.mkdir(parents=True, exist_ok=True)

    # Charger les données si non fournies
    if df is None:
        enquete_config = ENQUETES.get(enquete_id)
        if not enquete_config:
            print(f"Enquête '{enquete_id}' non configurée dans ENQUETES")
            return None

        df = load_csv(enquete_config["fichier"])
        df = clean_dataframe(df)

    print(f"Données: {len(df)} observations, {len(df.columns)} variables")

    results = {
        "enquete_id": enquete_id,
        "n_observations": len(df),
        "n_variables": len(df.columns),
        "colonnes": list(df.columns),
    }

    # 1. Métadonnées
    metadata = {
        "id": enquete_id,
        "generated_at": datetime.now().isoformat(),
        "n_observations": len(df),
        "colonnes": list(df.columns),
    }
    if enquete_id in ENQUETES:
        metadata.update(ENQUETES[enquete_id])

    with open(export_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f"  -> metadata.json")

    # 2. Exploration (stats descriptives de toutes les colonnes)
    exploration = {}
    for col in df.columns:
        exploration[col] = descriptive_stats(df, col)

    with open(export_dir / "exploration.json", "w", encoding="utf-8") as f:
        json.dump(exploration, f, ensure_ascii=False, indent=2, default=str)
    print(f"  -> exploration.json")

    return results


def analyze_enquete_theme(enquete_id: str, theme: str, df, var_config: dict):
    """
    Analyse une enquête selon un thème spécifique.

    Args:
        enquete_id: ID de l'enquête
        theme: 'genre', 'classe', 'generations', etc.
        df: DataFrame des données
        var_config: Configuration des variables pour ce thème
    """
    export_dir = get_enquete_dir(enquete_id)

    results = {
        "theme": theme,
        "enquete_id": enquete_id,
        "config": var_config,
    }

    # Analyses selon le thème
    if theme == "genre" and "variable" in var_config:
        var = var_config["variable"]
        results["distribution"] = df[var].value_counts().to_dict()
        # Croisements avec d'autres variables
        for target_var in var_config.get("croiser_avec", []):
            if target_var in df.columns:
                results[f"croisement_{target_var}"] = crosstab_analysis(df, var, target_var)

    elif theme == "classe" and "variable" in var_config:
        var = var_config["variable"]
        results["distribution"] = df[var].value_counts().to_dict()
        for target_var in var_config.get("croiser_avec", []):
            if target_var in df.columns:
                results[f"croisement_{target_var}"] = crosstab_analysis(df, var, target_var)

    elif theme == "generations" and "variable" in var_config:
        var = var_config["variable"]
        results["distribution"] = df[var].value_counts().to_dict()

    elif theme == "legitimites":
        # ACM + clustering
        vars_acm = var_config.get("variables_acm", [])
        vars_acm = [v for v in vars_acm if v in df.columns]
        if len(vars_acm) >= 3:
            results["acm"] = run_acm(df, vars_acm)
            results["clustering"] = run_clustering(df, vars_acm, n_clusters=5)

    # Sauvegarder
    with open(export_dir / f"{theme}.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    print(f"  -> {theme}.json")

    return results


# =============================================================================
# ANALYSES TRANSVERSALES
# =============================================================================

def generate_transversal():
    """
    Génère les analyses transversales à partir de toutes les enquêtes.

    Chaque thème transversal agrège les résultats de toutes les enquêtes
    pour permettre une lecture comparative.
    """
    print(f"\n{'='*60}")
    print("ANALYSES TRANSVERSALES")
    print(f"{'='*60}")

    transversal_dir = get_transversal_dir()
    transversal_dir.mkdir(parents=True, exist_ok=True)

    # Exporter la config des thèmes
    themes_config = {
        "themes": THEMES_TRANSVERSAUX,
        "generated_at": datetime.now().isoformat(),
    }
    with open(transversal_dir / "themes.json", "w", encoding="utf-8") as f:
        json.dump(themes_config, f, ensure_ascii=False, indent=2)
    print(f"  -> themes.json")

    # Pour chaque thème, agréger les résultats des enquêtes
    for theme_id, theme_config in THEMES_TRANSVERSAUX.items():
        theme_results = {
            "theme": theme_config,
            "enquetes": {},
            "generated_at": datetime.now().isoformat(),
        }

        # Collecter les analyses de chaque enquête pour ce thème
        enquetes_dir = get_enquete_dir("").parent
        if enquetes_dir.exists():
            for enquete_dir in enquetes_dir.iterdir():
                if enquete_dir.is_dir():
                    theme_file = enquete_dir / f"{theme_id}.json"
                    if theme_file.exists():
                        with open(theme_file, "r", encoding="utf-8") as f:
                            theme_results["enquetes"][enquete_dir.name] = json.load(f)

        # Sauvegarder la synthèse transversale
        with open(transversal_dir / f"{theme_id}.json", "w", encoding="utf-8") as f:
            json.dump(theme_results, f, ensure_ascii=False, indent=2)
        print(f"  -> {theme_id}.json")

    return themes_config


# =============================================================================
# UTILITAIRES
# =============================================================================

def list_data_files():
    """Liste les fichiers de données disponibles."""
    csv_files = list(DATA_DIR.glob("*.csv"))
    if not csv_files:
        print(f"\nAucun fichier CSV dans {DATA_DIR}")
        print("Placez vos données CSV dans ce dossier.")
        return []

    print(f"\nFichiers de données disponibles ({DATA_DIR}):")
    for f in csv_files:
        print(f"  - {f.name}")
    return csv_files


def list_enquetes():
    """Liste les enquêtes configurées."""
    if not ENQUETES:
        print("\nAucune enquête configurée.")
        print("Ajoutez des enquêtes dans ENQUETES (run_analysis.py)")
        return

    print("\nEnquêtes configurées:")
    for eid, config in ENQUETES.items():
        print(f"  - {eid}: {config.get('titre', 'Sans titre')}")


def list_themes():
    """Liste les thèmes transversaux."""
    print("\nThèmes transversaux:")
    for tid, config in THEMES_TRANSVERSAUX.items():
        print(f"  - {tid}: {config['titre']}")
        print(f"    {config['description']}")


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Analyses Outsiders - Sociologie des données publiques",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  python run_analysis.py --list-data          # Liste les CSV disponibles
  python run_analysis.py --list-themes        # Liste les thèmes transversaux
  python run_analysis.py --enquete info       # Analyse une enquête
  python run_analysis.py --transversal        # Génère les synthèses
  python run_analysis.py --all                # Tout analyser
        """
    )

    parser.add_argument("--list-data", action="store_true",
                        help="Liste les fichiers de données disponibles")
    parser.add_argument("--list-enquetes", action="store_true",
                        help="Liste les enquêtes configurées")
    parser.add_argument("--list-themes", action="store_true",
                        help="Liste les thèmes transversaux")
    parser.add_argument("--enquete", type=str,
                        help="Analyse une enquête spécifique")
    parser.add_argument("--transversal", action="store_true",
                        help="Génère les analyses transversales")
    parser.add_argument("--all", action="store_true",
                        help="Lance toutes les analyses")

    args = parser.parse_args()

    # Créer les dossiers
    ensure_export_dirs()

    if args.list_data:
        list_data_files()
        return

    if args.list_enquetes:
        list_enquetes()
        return

    if args.list_themes:
        list_themes()
        return

    if args.enquete:
        analyze_enquete(args.enquete)
        return

    if args.transversal:
        generate_transversal()
        return

    if args.all:
        # Analyser toutes les enquêtes configurées
        for enquete_id in ENQUETES:
            analyze_enquete(enquete_id)
        # Générer les transversales
        generate_transversal()
        return

    # Par défaut, afficher l'aide et les listes
    parser.print_help()
    print("\n" + "="*60)
    list_data_files()
    list_enquetes()
    list_themes()


if __name__ == "__main__":
    main()
