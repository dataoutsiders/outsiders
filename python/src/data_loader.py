"""
Chargement et nettoyage des données
"""
import pandas as pd
from pathlib import Path


DATA_DIR = Path(__file__).parent.parent / "data"


def load_csv(filename: str, **kwargs) -> pd.DataFrame:
    """Charge un fichier CSV depuis le dossier data/"""
    filepath = DATA_DIR / filename
    return pd.read_csv(filepath, **kwargs)


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Nettoyage basique d'un DataFrame"""
    # Supprimer les colonnes entièrement vides
    df = df.dropna(axis=1, how='all')
    # Supprimer les lignes entièrement vides
    df = df.dropna(axis=0, how='all')
    return df


def convert_french_decimal(series: pd.Series) -> pd.Series:
    """
    Convertit une série avec des décimales françaises (virgules) en float.
    Gère les formats: "1,5" -> 1.5
    """
    if series.dtype == 'object':
        return series.str.replace(',', '.').astype(float)
    return pd.to_numeric(series, errors='coerce')


def load_arcom_data(weights_col: str = 'POIDS03') -> pd.DataFrame:
    """
    Charge les données ARCOM avec conversion correcte des poids.

    Args:
        weights_col: Nom de la colonne de poids (défaut: POIDS03)

    Returns:
        DataFrame avec poids correctement convertis
    """
    filepath = DATA_DIR / 'francais-information' / 'base-info-arcom.xlsx'
    df = pd.read_excel(filepath)

    # Conversion des poids (format français avec virgules)
    if weights_col in df.columns:
        df[weights_col] = convert_french_decimal(df[weights_col])
        # Remplacer les NaN par 1 (poids neutre)
        df[weights_col] = df[weights_col].fillna(1)

    return df
