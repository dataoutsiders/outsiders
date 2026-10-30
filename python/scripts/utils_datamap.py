# -*- coding: utf-8 -*-
"""
Utilitaires pour récupérer les codes depuis le datamap ARCOM
Évite de coder en dur les numéros de modalités
"""
import pandas as pd
from pathlib import Path

class DatamapHelper:
    def __init__(self, datamap_path):
        self.dm_vars = pd.read_excel(datamap_path, sheet_name='VARIABLES')
        self.dm_texts = pd.read_excel(datamap_path, sheet_name='TEXTS')

    def find_code_by_label(self, var_name, label_search, exact=False):
        """
        Trouve le code d'une modalité en cherchant dans le libellé

        Args:
            var_name: Nom de la variable (ex: 'NEWS1_R1', 'INF3_R')
            label_search: Texte à chercher dans le libellé (ex: 'réseaux sociaux', 'Créateurs')
            exact: Si True, cherche correspondance exacte

        Returns:
            int ou None: Le code trouvé
        """
        texts = self.dm_texts[self.dm_texts['NAME'].str.startswith(var_name, na=False)]

        for _, row in texts.iterrows():
            label = str(row.get('FR:L', row.get('VALUE', ''))).lower()
            search = label_search.lower()

            if exact:
                if label == search:
                    return int(row['CODE'])
            else:
                if search in label:
                    return int(row['CODE'])

        return None

    def find_column_by_label(self, var_prefix, label_search):
        """
        Pour les variables multi-colonnes (INF3_R_1, INF3_R_2, etc.)
        Trouve le numéro de colonne correspondant au libellé

        Args:
            var_prefix: Préfixe de la variable (ex: 'INF3_R')
            label_search: Texte à chercher (ex: 'Créateurs')

        Returns:
            str ou None: Le nom complet de la colonne (ex: 'INF3_R_6')
        """
        # Chercher dans _COLUMNS pour les variables à choix multiples
        col_name = f"{var_prefix}_COLUMNS"
        texts = self.dm_texts[self.dm_texts['NAME'] == col_name]

        for _, row in texts.iterrows():
            label = str(row.get('FR:L', row.get('VALUE', ''))).lower()
            if label_search.lower() in label:
                code = int(row['CODE'])
                return f"{var_prefix}_{code}"

        return None

    def get_all_codes(self, var_name):
        """
        Retourne tous les codes et libellés d'une variable

        Returns:
            dict: {code: libellé}
        """
        texts = self.dm_texts[self.dm_texts['NAME'].str.startswith(var_name, na=False)]
        codes = {}

        for _, row in texts.iterrows():
            code = row.get('CODE')
            label = row.get('FR:L', row.get('VALUE', ''))
            if pd.notna(code) and pd.notna(label):
                codes[int(code)] = str(label)

        return codes

    def print_codes(self, var_name):
        """Affiche tous les codes d'une variable pour debug"""
        codes = self.get_all_codes(var_name)
        print(f"\n=== Codes pour {var_name} ===")
        for code, label in sorted(codes.items()):
            print(f"  {code}: {label}")


# Test
if __name__ == '__main__':
    DATA_DIR = Path('python/data/francais-information')
    dm = DatamapHelper(DATA_DIR / 'datamap-info-arcom.xlsx')

    # Trouver le code pour RS dans NEWS1
    print("\n=== Recherche des codes ===")

    code_rs = dm.find_code_by_label('NEWS1_R1', 'réseaux sociaux')
    print(f"Code RS (NEWS1_R1): {code_rs}")

    code_tv = dm.find_code_by_label('NEWS1_R1', 'télévision')
    print(f"Code TV (NEWS1_R1): {code_tv}")

    # Trouver la colonne pour créateurs dans INF3
    col_createurs = dm.find_column_by_label('INF3_R', 'Créateurs')
    print(f"Colonne Créateurs (INF3): {col_createurs}")

    col_journalistes = dm.find_column_by_label('INF3_R', 'Journalistes')
    print(f"Colonne Journalistes (INF3): {col_journalistes}")

    # Afficher tous les codes
    dm.print_codes('NEWS1_R1')
    dm.print_codes('INF3_R_COLUMNS')
