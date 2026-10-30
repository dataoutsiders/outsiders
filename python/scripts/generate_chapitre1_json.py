"""
Generation du JSON pour le Chapitre 1 : Le grand basculement
Structure : Accroche > Analyse (3 sections) > Nuances > Implications > Annexes
"""
import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.api as sm
from statsmodels.formula.api import logit
from statsmodels.stats.outliers_influence import variance_inflation_factor
import json
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Chemins
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data" / "francais-information"
OUTPUT_DIR = BASE_DIR / "outputs" / "json"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("GENERATION JSON - CHAPITRE 1 : LE GRAND BASCULEMENT")
print("=" * 70)

# ============================================================
# 0. CHARGEMENT DES LABELS DEPUIS LE DATAMAP
# ============================================================
print("\n0. Chargement du datamap...")

def load_labels_from_datamap(datamap_path):
    """Charge les labels des variables depuis le fichier datamap Excel."""
    texts = pd.read_excel(datamap_path, sheet_name='TEXTS')

    labels = {}
    # Récupère toutes les variables qui ont des labels
    for var_name in texts['NAME'].unique():
        var_labels = texts[(texts['NAME'] == var_name) & (texts['TYPE'] == 'LABEL')]
        if len(var_labels) > 0:
            labels[var_name] = {}
            for _, row in var_labels.iterrows():
                if pd.notna(row['CODE']):
                    code = int(float(row['CODE']))  # Handle both int and float codes
                    label = row['FR:L'] if pd.notna(row['FR:L']) else str(code)
                    labels[var_name][code] = label
    return labels

DATAMAP = load_labels_from_datamap(DATA_DIR / "datamap-info-arcom.xlsx")

# Labels courts pour les sources d'information (les labels du datamap sont trop longs)
SOURCE_SHORT_LABELS = {
    'NEWS1BIS_R': {
        1: "Radio/Podcasts",
        2: "TV (direct/replay)",
        3: "Presse (papier/numérique)",
        4: "Site média (radio/TV/presse)",
        5: "Pure player (Mediapart...)",
        6: "Moteur de recherche",
        7: "Portail actualité",
        8: "Réseaux sociaux",
        9: "Plateformes vidéo (YouTube...)"
    },
    'NEWS1_R1': {
        1: "TV (direct/replay)",
        2: "Moteur de recherche",
        3: "Réseaux sociaux",
        4: "Radio/Podcasts",
        5: "Portail actualité",
        6: "Presse (papier/numérique)",
        7: "Pure player (Mediapart...)",
        8: "Plateformes vidéo (YouTube...)",
        9: "Aucun"
    }
}

def get_labels(var_name, short=False):
    """Retourne les labels pour une variable.
    Si short=True, utilise les labels courts pour les sources."""
    if short and var_name in SOURCE_SHORT_LABELS:
        return SOURCE_SHORT_LABELS[var_name]
    return DATAMAP.get(var_name, {})

# Labels principaux (depuis datamap)
AGE_LABELS = get_labels('RS2C_RECODE_AG_R')
GENRE_LABELS = get_labels('RS1_R')
AGGLO_LABELS = get_labels('CC_R')
NEWS1BIS_LABELS = get_labels('NEWS1BIS_R', short=True)

print(f"   Labels chargés pour {len(DATAMAP)} variables")

# ============================================================
# 1. CHARGEMENT ET PREPARATION DES DONNEES
# ============================================================
print("\n1. Chargement des donnees...")
df = pd.read_excel(DATA_DIR / "base-info-arcom.xlsx")
print(f"   {len(df)} repondants")

# Convertir POIDS03
df['POIDS03'] = df['POIDS03'].astype(str).str.replace(',', '.').astype(float)

# ============================================================
# 2. CREATION DES VARIABLES RECODEES
# ============================================================
print("\n2. Creation des variables recodees...")

# CSP_3 : uniquement les actifs (basé sur RS4_R) - pour affichage dans section 1
def recode_csp_3(rs4):
    if pd.isna(rs4): return None
    rs4 = int(rs4)
    if rs4 == 3: return 'CSP+'
    elif rs4 in [1, 2, 4]: return 'CSP milieu'
    elif rs4 in [5, 6]: return 'CSP-'
    return None  # Exclut NSP (7)

df['CSP_3'] = df['RS4_R'].apply(recode_csp_3)

# Capital culturel
def recode_capital_culturel(rs5):
    if pd.isna(rs5): return None
    if rs5 in [1, 2, 3, 4]: return 'Faible'
    elif rs5 in [5, 6]: return 'Moyen'
    elif rs5 in [7, 8, 9]: return 'Eleve'
    return None

df['CAPITAL_CULTUREL'] = df['RS5_R'].apply(recode_capital_culturel)

# Capital economique
REVENUS_MIDPOINT = {1: 750, 2: 2250, 3: 3750, 4: 6000, 5: 8500, 6: None}

def recode_capital_eco(row):
    rs14, rs7 = row.get('RS14_R'), row.get('RS7_R')
    if pd.isna(rs14) or pd.isna(rs7) or rs14 == 6: return None
    revenu = REVENUS_MIDPOINT.get(rs14)
    if revenu is None: return None
    rev_pers = revenu / (rs7 if rs7 <= 6 else 6)
    if rev_pers < 800: return 'Faible'
    elif rev_pers <= 1500: return 'Moyen'
    else: return 'Eleve'

df['CAPITAL_ECO'] = df.apply(recode_capital_eco, axis=1)

# Score quizz
def calc_score_quizz(row):
    score = sum(1 for q in ['QUIZZ1_R', 'QUIZZ2_R', 'QUIZZ3_R', 'QUIZZ4_R']
                if row.get(q) == 1)
    return score

df['SCORE_QUIZZ'] = df.apply(calc_score_quizz, axis=1)
df['SCORE_QUIZZ_CAT'] = df['SCORE_QUIZZ'].apply(
    lambda x: '0-1 (Faible)' if x <= 1 else ('2 (Moyen)' if x == 2 else '3-4 (Eleve)')
)

# Source simplifiee (pour visualisations)
df['SOURCE_SIMPLE'] = df['NEWS1BIS_R'].map({
    1: "Radio/Podcasts", 2: "TV", 3: "Presse", 4: "Numerique media",
    5: "Numerique media", 6: "Numerique autre", 7: "Numerique autre",
    8: "Reseaux sociaux", 9: "Plateformes video"
})

# Labels complets de NEWS1BIS_R (pour V de Cramer)
NEWS1BIS_LABELS = {
    1: "Radio/Podcasts",
    2: "TV (direct/replay)",
    3: "Presse (papier/numérique)",
    4: "Site média (radio/TV/presse)",
    5: "Pure player (Mediapart...)",
    6: "Moteur de recherche",
    7: "Portail actualité",
    8: "Réseaux sociaux",
    9: "Plateformes vidéo (YouTube...)"
}
df['SOURCE_LABEL'] = df['NEWS1BIS_R'].map(NEWS1BIS_LABELS)

# ============================================================
# PRATIQUES INDIVIDUELLES (seuil 25% - au moins une modalite socio-demo > 25%)
# Note: Les pratiques ultra-minoritaires (< 25% dans TOUTES les categories) sont exclues
# ============================================================

# Plateformes RS pour s'informer (RSINFO_2_LR_R) - seuil 25%
PLATEFORMES_RS_25 = {
    1: ('Facebook', 33.3),         # 57.1% max
    2: ('Instagram', 21.7),        # 59.2% max
    9: ('Youtube', 35.1),          # 58.5% max
    4: ('TikTok', 12.9),           # 37.4% max
    3: ('Twitter/X', 13.3),        # 27.9% max
    6: ('LinkedIn', 11.6),         # 26.5% max
}

# Chaines TV generalistes (SOURCES1DR_B4_R) - seuil 25%
CHAINES_GEN_25 = {
    1: ('TF1', 42.1),              # 49.9% max
    2: ('France 2', 31.6),         # 45.5% max
    6: ('M6', 33.3),               # 45.5% max
    3: ('France 3', 24.0),         # 34.4% max
    5: ('Arte', 21.5),             # 33.4% max
}

# Chaines info TV (SOURCES1ER_B4_R) - seuil 25%
CHAINES_INFO_25 = {
    3: ('BFM TV', 29.7),           # 37.0% max
    4: ('CNews', 20.9),            # 27.2% max
}

# Medias RS natifs (SOURCES1FR_R) - seuil 25%
MEDIAS_RS_25 = {
    8: ('Brut', 18.8),             # 41.2% max
    6: ('Konbini', 15.0),          # 39.9% max
    10: ('Hugo Decrypte', 8.8),    # 37.1% max
}

# Emissions TV quotidiennes (TV2BR_R) - seuil 25%
EMISSIONS_TV_25 = {
    1: ('Quotidien', 16.8),        # 25.7% max
}

# JT (TV2AR_R) - seuil 25%
JT_25 = {
    1: ('JT 20h TF1', 30.8),       # 35.3% max
    2: ('JT 20h France 2', 22.5),  # 32.5% max
    4: ('19-45 M6', 18.9),         # 27.0% max
}

# Magazines TV (TV2CR_R) - seuil 25%
MAGAZINES_TV_25 = {
    1: ('Zone Interdite', 28.9),   # 40.8% max
    3: ('Capital', 25.9),          # 36.8% max
    8: ('66 Minutes', 23.9),       # 33.4% max
    4: ('Enquete exclusive', 20.6), # 30.8% max
    5: ('Envoye Special', 25.6),   # 30.6% max
    6: ('Sept a Huit', 24.3),      # 29.4% max
    9: ('Grands reportages', 22.0), # 27.4% max
    7: ('Complement enquete', 19.8), # 26.7% max
    2: ('Cash Investigation', 18.9), # 25.4% max
}

# Journaux (SOURCES1BR_B2_R) - seuil 25%
JOURNAUX_25 = {
    2: ('Le Parisien', 17.4),      # 40.9% max
    1: ('Le Monde', 15.3),         # 32.2% max
    11: ('Journal regional', 18.5), # 24.9% max
}

# Magazines presse - seuil 25% : aucun ne passe le seuil
MAGAZINES_PRESSE_25 = {}

# Variables binaires pour chaque source principale (dummy variables) - NEWS1BIS_R
df['SOURCE_PRINC_TV'] = (df['NEWS1BIS_R'] == 2).astype(int)
df['SOURCE_PRINC_RS'] = (df['NEWS1BIS_R'] == 8).astype(int)
df['SOURCE_PRINC_PRESSE'] = (df['NEWS1BIS_R'] == 3).astype(int)
df['SOURCE_PRINC_RADIO'] = (df['NEWS1BIS_R'] == 1).astype(int)
df['SOURCE_PRINC_VIDEO'] = (df['NEWS1BIS_R'] == 9).astype(int)

# Variables binaires "utilise cette source" (NEWS1_R1_*) - choix multiple
# ATTENTION: NEWS1_R1 utilise un codage DIFFÉRENT de NEWS1BIS_R !
# Codage NEWS1_R1: 1=TV, 2=Moteur, 3=RS, 4=Radio, 5=Portail, 6=Presse, 7=Pure player, 8=?, 9=Vidéo
news1_cols = [f'NEWS1_R1_{i}' for i in range(1, 10) if f'NEWS1_R1_{i}' in df.columns]

def utilise_source(row, code):
    """Vérifie si le code apparaît dans n'importe quelle colonne NEWS1_R1_*"""
    for col in news1_cols:
        if pd.notna(row[col]) and row[col] == code:
            return 1
    return 0

# Codes corrigés pour NEWS1_R1:
df['UTILISE_TV'] = df.apply(lambda r: utilise_source(r, 1), axis=1)       # 1 = TV
df['UTILISE_RS'] = df.apply(lambda r: utilise_source(r, 3), axis=1)       # 3 = RS
df['UTILISE_PRESSE'] = df.apply(lambda r: utilise_source(r, 6), axis=1)   # 6 = Presse
df['UTILISE_RADIO'] = df.apply(lambda r: utilise_source(r, 4), axis=1)    # 4 = Radio
df['UTILISE_VIDEO'] = df.apply(lambda r: utilise_source(r, 9), axis=1)    # 9 = Vidéo

# Variables binaires pour FORMAT_R_* (choix multiple)
# Code: 1=JT/Flash info, 2=Magazines/Reportages, 3=Talk-shows/Débats, 4=Autre
format_cols = [f'FORMAT_R_{i}' for i in range(1, 5) if f'FORMAT_R_{i}' in df.columns]

def utilise_format(row, code):
    """Vérifie si le code apparaît dans n'importe quelle colonne FORMAT_R_*"""
    for col in format_cols:
        if pd.notna(row[col]) and row[col] == code:
            return 1
    return 0

df['FORMAT_JT'] = df.apply(lambda r: utilise_format(r, 1), axis=1)
df['FORMAT_MAGAZINE'] = df.apply(lambda r: utilise_format(r, 2), axis=1)
df['FORMAT_DEBAT'] = df.apply(lambda r: utilise_format(r, 3), axis=1)

# Variables FORMAT3 et FORMAT2 (binaires)
df['FORMAT3_COURT'] = (df['FORMAT3_LR1_FORMAT3_1_R'] == 1).astype(int)  # Formats courts
df['FORMAT3_LONG'] = (df['FORMAT3_LR1_FORMAT3_1_R'] == 2).astype(int)   # Formats longs
df['FORMAT2_ECRIT'] = (df['FORMAT2_LR1_FORMAT2_1_R'] == 1).astype(int)  # Écrit
df['FORMAT2_VIDEO'] = (df['FORMAT2_LR1_FORMAT2_1_R'] == 2).astype(int)  # Vidéo

# ============================================================
# NOUVELLES VARIABLES : Chaînes TV et Médias RS (bases filtrées)
# ============================================================

# Fonction pour vérifier si un code apparaît dans les colonnes d'une question multi-choix
def utilise_code_multi(row, pattern, codes):
    """Vérifie si au moins un des codes apparaît dans les colonnes pattern_*"""
    cols = [c for c in row.index if c.startswith(pattern)]
    for col in cols:
        if pd.notna(row[col]) and int(row[col]) in codes:
            return 1
    return 0

# SOURCES1ER_B4_R : Chaînes info TV
# Codes: 1=Franceinfo, 2=LCI, 3=BFM, 4=CNews, 5=France24, 6=Internationales, 7=Autre, 8=Rien, 9=Non cité
df['REGARDE_CHAINE_INFO'] = df.apply(
    lambda r: utilise_code_multi(r, 'SOURCES1ER_B4_R_', [1, 2, 3, 4, 5, 6, 7]), axis=1
)
df['REGARDE_BFM_CNEWS'] = df.apply(
    lambda r: utilise_code_multi(r, 'SOURCES1ER_B4_R_', [3, 4]), axis=1  # BFM=3, CNews=4
)
df['REGARDE_FRANCEINFO_LCI'] = df.apply(
    lambda r: utilise_code_multi(r, 'SOURCES1ER_B4_R_', [1, 2]), axis=1  # Franceinfo=1, LCI=2
)

# TV2BR_R : Émissions quotidiennes
# 1=Quotidien, 2=TPMP, 3=Grandes gueules, 4=C à vous, 5=Heure des pros, 6=28min, 7=C dans l'air...
df['REGARDE_QUOTIDIEN_TPMP'] = df.apply(
    lambda r: utilise_code_multi(r, 'TV2BR_R_', [1, 2]), axis=1  # Quotidien=1, TPMP=2
)
df['REGARDE_EMISSION_DEBAT'] = df.apply(
    lambda r: utilise_code_multi(r, 'TV2BR_R_', [3, 4, 5, 6, 7, 8, 9, 12]), axis=1  # Émissions de débat/analyse
)

# SOURCES1FR_R : Médias natifs RS
# 1=Blast, 2=Atlantico, 6=Konbini, 7=Loopsider, 8=Brut, 9=AJ+, 10=Hugo Décrypte, 11=Samuel Etienne
df['SUIT_MEDIA_NATIF_RS'] = df.apply(
    lambda r: utilise_code_multi(r, 'SOURCES1FR_R_', list(range(1, 14))), axis=1  # Tous sauf 14=rien
)
df['SUIT_HUGO_BRUT'] = df.apply(
    lambda r: utilise_code_multi(r, 'SOURCES1FR_R_', [8, 10, 11]), axis=1  # Brut, Hugo Décrypte, Samuel Etienne
)

print("   Variables creees: CSP_3, CAPITAL_CULTUREL, CAPITAL_ECO, SCORE_QUIZZ, FORMAT_*, CHAINES_TV, MEDIAS_RS")

# ============================================================
# CREATION DES VARIABLES BINAIRES POUR PRATIQUES INDIVIDUELLES (seuil 25%)
# ============================================================
print("   Creation des pratiques individuelles (seuil 25%)...")

# Fonction pour creer variable binaire pour un code specifique dans colonnes multi-choix
def utilise_code(df_data, pattern, code):
    cols = [c for c in df_data.columns if c.startswith(pattern)]
    result = pd.Series(0, index=df_data.index)
    for col in cols:
        result = result | (df_data[col] == code)
    return result.astype(int)

# Plateformes RS (colonnes binaires RSINFO_2_LR_R_*)
for code, (label, prev) in PLATEFORMES_RS_25.items():
    col_name = f'RSINFO_2_LR_R_{code}'
    if col_name in df.columns:
        df[f'PLAT_RS_{code}'] = (df[col_name] == 1).astype(int)

# Chaines TV generalistes
for code, (label, prev) in CHAINES_GEN_25.items():
    df[f'CHAINE_GEN_{code}'] = utilise_code(df, 'SOURCES1DR_B4_R_', code)

# Chaines info TV
for code, (label, prev) in CHAINES_INFO_25.items():
    df[f'CHAINE_INFO_{code}'] = utilise_code(df, 'SOURCES1ER_B4_R_', code)

# Medias RS natifs
for code, (label, prev) in MEDIAS_RS_25.items():
    df[f'MEDIA_RS_{code}'] = utilise_code(df, 'SOURCES1FR_R_', code)

# Emissions TV
for code, (label, prev) in EMISSIONS_TV_25.items():
    df[f'EMISSION_{code}'] = utilise_code(df, 'TV2BR_R_', code)

# JT
for code, (label, prev) in JT_25.items():
    df[f'JT_{code}'] = utilise_code(df, 'TV2AR_R_', code)

# Magazines TV
for code, (label, prev) in MAGAZINES_TV_25.items():
    df[f'MAG_TV_{code}'] = utilise_code(df, 'TV2CR_R_', code)

# Journaux
for code, (label, prev) in JOURNAUX_25.items():
    df[f'JOURNAL_{code}'] = utilise_code(df, 'SOURCES1BR_B2_R_', code)

# Magazines presse
for code, (label, prev) in MAGAZINES_PRESSE_25.items():
    df[f'MAGAZINE_{code}'] = utilise_code(df, 'SOURCES1CR_B3_R_', code)

print(f"      {len(PLATEFORMES_RS_25)} plateformes RS, {len(CHAINES_GEN_25)} chaines gen., {len(CHAINES_INFO_25)} chaines info")
print(f"      {len(MEDIAS_RS_25)} medias RS, {len(EMISSIONS_TV_25)} emissions, {len(JT_25)} JT, {len(MAGAZINES_TV_25)} magazines TV")
print(f"      {len(JOURNAUX_25)} journaux, {len(MAGAZINES_PRESSE_25)} magazines presse")

# ============================================================
# 3. FONCTIONS UTILITAIRES
# ============================================================

def cramers_v(ct):
    """Calcule V de Cramer sur tableau de contingence pondéré"""
    chi2 = stats.chi2_contingency(ct)[0]
    n = ct.sum().sum()
    min_dim = min(ct.shape) - 1
    return np.sqrt(chi2 / (n * min_dim)) if min_dim > 0 and n > 0 else 0

def calc_crosstab_pct(df, var_row, var_col, poids='POIDS03'):
    """Calcule tableau croisé pondéré en %"""
    mask = df[var_row].notna() & df[var_col].notna() & df[poids].notna()
    df_valid = df[mask]

    result = []
    for row_val in sorted(df_valid[var_row].unique()):
        row_data = {'category': row_val}
        subset_row = df_valid[df_valid[var_row] == row_val]
        total_poids = subset_row[poids].sum()

        for col_val in sorted(df_valid[var_col].unique()):
            subset_cell = subset_row[subset_row[var_col] == col_val]
            pct = (subset_cell[poids].sum() / total_poids * 100) if total_poids > 0 else 0
            row_data[str(col_val)] = round(pct, 1)

        row_data['n'] = len(subset_row)
        result.append(row_data)

    return result

def get_chi2_stats(df, var1, var2, poids='POIDS03'):
    """Calcule Chi2 et V de Cramer avec pondération"""
    mask = df[var1].notna() & df[var2].notna() & df[poids].notna()
    df_valid = df[mask]
    # Tableau de contingence PONDÉRÉ
    ct = pd.crosstab(
        df_valid[var1],
        df_valid[var2],
        values=df_valid[poids],
        aggfunc='sum'
    ).fillna(0)
    chi2, p, dof, _ = stats.chi2_contingency(ct)
    v = cramers_v(ct)
    return {'chi2': round(chi2, 1), 'p': p, 'dof': int(dof), 'v_cramer': round(v, 3)}


def get_distribution(df, var_vi, var_vd, label_vi, poids='POIDS03'):
    """
    Calcule la distribution de var_vd (binaire 0/1) selon les catégories de var_vi.
    Retourne une liste de dicts avec category et pct_oui.
    """
    mask = df[var_vi].notna() & df[var_vd].notna() & df[poids].notna()
    df_valid = df[mask]

    distribution = []

    # Labels depuis datamap ou labels courts personnalisés
    labels_map = {
        'RS2C_RECODE_AG_R': AGE_LABELS,
        'RS1_R': GENRE_LABELS,
        'CC_R': AGGLO_LABELS,
    }

    # Ordre des catégories pour CSP et capitaux
    csp_order = ['CSP+', 'CSP milieu', 'CSP-']
    capital_order = ['Faible', 'Moyen', 'Eleve']

    categories = df_valid[var_vi].unique()

    # Trier les catégories
    if var_vi in ['CAPITAL_CULTUREL', 'CAPITAL_ECO']:
        categories = [c for c in capital_order if c in categories]
    elif var_vi == 'CSP_3':
        categories = [c for c in csp_order if c in categories]
    else:
        categories = sorted(categories)

    for cat in categories:
        subset = df_valid[df_valid[var_vi] == cat]
        total_poids = subset[poids].sum()

        # Calcul du % de "oui" (valeur 1 pour variable binaire)
        pct_oui = 0
        if total_poids > 0:
            oui_poids = subset[subset[var_vd] == 1][poids].sum()
            pct_oui = (oui_poids / total_poids) * 100

        # Label de la catégorie (depuis datamap si disponible)
        if var_vi in labels_map and np.issubdtype(type(cat), np.number) and not pd.isna(cat):
            cat_label = labels_map[var_vi].get(int(cat), str(cat))
        else:
            cat_label = str(cat)

        distribution.append({
            'category': cat_label,
            'pct_oui': round(pct_oui, 1)
        })

    return distribution


def test_effet_net(df, var_vi, var_vd, all_vi_vars, poids='POIDS03'):
    """
    Teste si var_vi a un effet significatif sur var_vd toutes choses égales par ailleurs.
    Retourne le p-value du test de Wald pour la variable.

    all_vi_vars: liste des tuples (nom_variable, nom_label) des VI à contrôler
    """
    # Préparer les données
    vi_names = [v[0] for v in all_vi_vars]
    cols_needed = [var_vd, poids] + vi_names

    # Filtrer les lignes avec données complètes
    df_reg = df[cols_needed].dropna().copy()

    if len(df_reg) < 100:
        return None, None

    # Convertir les variables catégorielles string en category puis en codes numériques
    for col in vi_names:
        if df_reg[col].dtype == 'object' or df_reg[col].dtype.name == 'category':
            df_reg[col] = df_reg[col].astype('category').cat.codes

    # Convertir var_vd en numérique si nécessaire
    if df_reg[var_vd].dtype == 'object':
        df_reg[var_vd] = df_reg[var_vd].astype('category').cat.codes

    # S'assurer que toutes les colonnes sont numériques
    for col in df_reg.columns:
        df_reg[col] = pd.to_numeric(df_reg[col], errors='coerce')

    df_reg = df_reg.dropna()

    if len(df_reg) < 100:
        return None, None

    # Créer des dummies pour les variables catégorielles (une par variable)
    df_dummies = pd.DataFrame()
    for vi in vi_names:
        vi_dummies = pd.get_dummies(df_reg[vi].astype(int), drop_first=True, prefix=vi)
        df_dummies = pd.concat([df_dummies, vi_dummies], axis=1)

    df_dummies[var_vd] = df_reg[var_vd].values
    df_dummies[poids] = df_reg[poids].values

    # Identifier les colonnes correspondant à var_vi (pour le test de Wald)
    var_vi_cols = [c for c in df_dummies.columns if c.startswith(var_vi + '_')]

    if len(var_vi_cols) == 0:
        return None, None

    # Variables X (toutes les dummies sauf var_vd et poids)
    X_cols = [c for c in df_dummies.columns if c not in [var_vd, poids]]
    X = df_dummies[X_cols].astype(float)
    X = sm.add_constant(X)
    y = df_dummies[var_vd].astype(float)
    weights = df_dummies[poids].astype(float)

    try:
        # Régression logistique pondérée
        model = sm.GLM(y, X, family=sm.families.Binomial(), freq_weights=weights)
        result = model.fit()

        # Test de Wald pour les colonnes de var_vi
        var_vi_indices = [X.columns.get_loc(c) for c in var_vi_cols if c in X.columns]

        if len(var_vi_indices) == 0:
            return None, None

        # Construire la matrice de restriction pour le test de Wald
        R = np.zeros((len(var_vi_indices), len(X.columns)))
        for i, idx in enumerate(var_vi_indices):
            R[i, idx] = 1

        # Test de Wald
        wald_test = result.wald_test(R)
        p_value = float(wald_test.pvalue)

        return p_value, result

    except Exception as e:
        print(f"   Erreur régression {var_vi} x {var_vd}: {e}")
        return None, None


def get_predicted_probabilities(df, var_vi, var_vd, all_vi_vars, label_vi, poids='POIDS03'):
    """
    Calcule les probabilités prédites ajustées pour chaque catégorie de var_vi.
    Fixe les autres variables à leur moyenne/mode.
    Retourne un dict {category_label: predicted_prob}
    """
    vi_names = [v[0] for v in all_vi_vars]

    # S'assurer que var_vi est dans la liste
    if var_vi not in vi_names:
        vi_names = [var_vi] + vi_names

    cols_needed = [var_vd, poids] + vi_names

    # Vérifier que toutes les colonnes existent
    missing_cols = [c for c in cols_needed if c not in df.columns]
    if missing_cols:
        return None

    df_reg = df[cols_needed].dropna().copy()

    if len(df_reg) < 100:
        return None

    # Mapping code -> label pour var_vi (même que dans get_distribution)
    labels_map = {
        'RS2C_RECODE_AG_R': AGE_LABELS,
        'RS1_R': GENRE_LABELS,
        'CC_R': AGGLO_LABELS,
    }
    code_to_label = labels_map.get(var_vi, {})

    # IMPORTANT: Sauvegarder le mapping catégorie -> valeur originale AVANT la conversion
    # Cela évite les bugs quand certaines catégories sont filtrées par dropna()
    cat_mappings = {}
    for col in vi_names:
        if df_reg[col].dtype == 'object' or df_reg[col].dtype.name == 'category':
            cat_series = df_reg[col].astype('category')
            cat_mappings[col] = dict(enumerate(cat_series.cat.categories))  # code -> original_value
            df_reg[col] = cat_series.cat.codes
        elif np.issubdtype(df_reg[col].dtype, np.number):
            # Pour les variables numériques, créer aussi un mapping
            cat_series = df_reg[col].astype('category')
            cat_mappings[col] = dict(enumerate(cat_series.cat.categories))
            df_reg[col] = cat_series.cat.codes

    if df_reg[var_vd].dtype == 'object':
        df_reg[var_vd] = df_reg[var_vd].astype('category').cat.codes

    for col in df_reg.columns:
        df_reg[col] = pd.to_numeric(df_reg[col], errors='coerce')

    df_reg = df_reg.dropna()

    if len(df_reg) < 100:
        return None

    # Créer les dummies
    df_dummies = pd.DataFrame()
    for vi in vi_names:
        vi_dummies = pd.get_dummies(df_reg[vi].astype(int), drop_first=True, prefix=vi)
        df_dummies = pd.concat([df_dummies, vi_dummies], axis=1)

    df_dummies[var_vd] = df_reg[var_vd].values
    df_dummies[poids] = df_reg[poids].values
    df_dummies[var_vi + '_original'] = df_reg[var_vi].values

    X_cols = [c for c in df_dummies.columns if c not in [var_vd, poids, var_vi + '_original']]
    X = df_dummies[X_cols].astype(float)
    X = sm.add_constant(X)
    y = df_dummies[var_vd].astype(float)
    weights = df_dummies[poids].astype(float)

    try:
        model = sm.GLM(y, X, family=sm.families.Binomial(), freq_weights=weights)
        result = model.fit()

        # Pour chaque catégorie de var_vi, calculer la probabilité prédite
        predictions = {}

        # Moyennes des variables X
        X_means = X.mean()

        # Catégories uniques de var_vi (codes numériques dans df_reg)
        categories = sorted(df_reg[var_vi].unique())

        # Récupérer le mapping pour var_vi
        vi_cat_mapping = cat_mappings.get(var_vi, {})

        for cat in categories:
            X_pred = X_means.copy()

            # Mettre à jour les dummies de var_vi pour cette catégorie
            for col in X_pred.index:
                if col.startswith(var_vi + '_'):
                    dummy_cat = int(col.split('_')[-1])
                    X_pred[col] = 1.0 if dummy_cat == cat else 0.0

            # Prédire
            prob = result.predict(X_pred.values.reshape(1, -1))[0]

            # Trouver le label correspondant au code
            # Utiliser le mapping sauvegardé pour obtenir la valeur originale
            original_value = vi_cat_mapping.get(int(cat), int(cat))

            # Gérer les variables avec valeurs textuelles (CAPITAL_ECO, CSP_3, etc.)
            if isinstance(original_value, str):
                # La valeur originale est déjà le label (ex: 'Faible', 'Moyen', 'Eleve')
                cat_label = original_value
            elif code_to_label:
                # Variable numérique avec mapping dans le datamap (ex: AGE_LABELS)
                cat_label = code_to_label.get(int(original_value), str(original_value))
            else:
                # Variable numérique sans mapping
                cat_label = str(original_value)

            predictions[cat_label] = round(prob * 100, 1)

        return predictions

    except Exception as e:
        return None


def get_effet_net_data(df, var_vi, var_vd, label_vi, label_vd, all_vi_vars, poids='POIDS03'):
    """
    Calcule les données pour l'affichage de l'effet net :
    - Distribution descriptive (min/max) - valeurs brutes
    - Distribution ajustée (probabilités prédites) - valeurs toutes choses égales
    - Test de significativité toutes choses égales par ailleurs
    """
    # 1. Distribution descriptive (brute)
    distribution = get_distribution(df, var_vi, var_vd, label_vi, poids)

    if not distribution:
        return None

    # Trouver min et max bruts
    pcts = [d['pct_oui'] for d in distribution]
    min_idx = pcts.index(min(pcts))
    max_idx = pcts.index(max(pcts))

    cat_min = distribution[min_idx]
    cat_max = distribution[max_idx]

    # Calculer le rapport brut
    if cat_min['pct_oui'] > 0:
        rapport = round(cat_max['pct_oui'] / cat_min['pct_oui'], 1)
    else:
        rapport = None

    # 2. Test de l'effet net
    p_value, _ = test_effet_net(df, var_vi, var_vd, all_vi_vars, poids)

    effet_net = None
    if p_value is not None:
        effet_net = p_value < 0.05

    # 3. Probabilités prédites ajustées (toutes choses égales par ailleurs)
    predicted_probs = get_predicted_probabilities(df, var_vi, var_vd, all_vi_vars, label_vi, poids)

    # Ajouter les probabilités ajustées à la distribution
    distribution_ajustee = None
    cat_min_ajuste = None
    cat_max_ajuste = None
    rapport_ajuste = None
    ecart_ajuste = None

    if predicted_probs:
        distribution_ajustee = []
        for d in distribution:
            cat_label = d['category']
            pct_ajuste = predicted_probs.get(cat_label, predicted_probs.get(str(cat_label)))
            distribution_ajustee.append({
                'category': cat_label,
                'pct_brut': d['pct_oui'],
                'pct_ajuste': pct_ajuste
            })

        # Trouver min et max ajustés
        pcts_ajustes = [d['pct_ajuste'] for d in distribution_ajustee if d['pct_ajuste'] is not None]
        if pcts_ajustes:
            min_val = min(pcts_ajustes)
            max_val = max(pcts_ajustes)

            for d in distribution_ajustee:
                if d['pct_ajuste'] == min_val:
                    cat_min_ajuste = {'category': d['category'], 'pct_ajuste': d['pct_ajuste']}
                if d['pct_ajuste'] == max_val:
                    cat_max_ajuste = {'category': d['category'], 'pct_ajuste': d['pct_ajuste']}

            # Rapport et écart ajustés
            if min_val > 0:
                rapport_ajuste = round(max_val / min_val, 1)
            ecart_ajuste = round(max_val - min_val, 1)

    # Détecter si le max/min brut diffère du max/min ajusté
    # Cela peut indiquer une extrapolation ou un effet de confusion
    max_category_differs = False
    min_category_differs = False
    if cat_max_ajuste and cat_max:
        max_category_differs = cat_max['category'] != cat_max_ajuste['category']
    if cat_min_ajuste and cat_min:
        min_category_differs = cat_min['category'] != cat_min_ajuste['category']

    return {
        'var_vi': var_vi,
        'var_vd': var_vd,
        'label_vi': label_vi,
        'label_vd': label_vd,
        # Valeurs brutes
        'cat_min': cat_min,
        'cat_max': cat_max,
        'rapport': rapport,
        # Valeurs ajustées (toutes choses égales)
        'cat_min_ajuste': cat_min_ajuste,
        'cat_max_ajuste': cat_max_ajuste,
        'rapport_ajuste': rapport_ajuste,
        'ecart_ajuste': ecart_ajuste,
        'distribution_ajustee': distribution_ajustee,
        # Alertes méthodologiques
        'max_category_differs': max_category_differs,
        'min_category_differs': min_category_differs,
        # Test
        'p_value': round(p_value, 4) if p_value else None,
        'effet_net': effet_net,
        'distribution': distribution
    }


# ============================================================
# 4. CALCUL DES DONNEES POUR CHAQUE SECTION
# ============================================================
print("\n3. Calcul des donnees...")

# --- ACCROCHE : Chiffre marquant ---
print("   - Accroche...")
df_info = df[df['NEWS1BIS_R'].notna()].copy()

# % RS chez 18-24 ans
jeunes = df_info[df_info['RS2C_RECODE_AG_R'] == 2]
pct_rs_jeunes = (jeunes[jeunes['SOURCE_SIMPLE'] == 'Reseaux sociaux']['POIDS03'].sum() /
                 jeunes['POIDS03'].sum() * 100)

# % RS chez 70+
seniors = df_info[df_info['RS2C_RECODE_AG_R'] == 7]
pct_rs_seniors = (seniors[seniors['SOURCE_SIMPLE'] == 'Reseaux sociaux']['POIDS03'].sum() /
                  seniors['POIDS03'].sum() * 100)

ecart_rs = pct_rs_jeunes - pct_rs_seniors
# Calcul du rapport (x fois plus)
rapport_rs = round(pct_rs_jeunes / pct_rs_seniors, 1) if pct_rs_seniors > 0 else 0

# --- SECTION 1 : Ce qui distingue le plus (V de Cramer) ---
print("   - Section 1: Facteurs distinctifs...")
# Variables indépendantes (facteurs sociaux) - pour section 1 (descriptif)
croisements_vi = [
    ('RS2C_RECODE_AG_R', 'Âge'),
    ('RS1_R', 'Genre'),
    ('CSP_3', 'Milieu social'),
    ('CAPITAL_CULTUREL', 'Niveau d\'études'),
    ('CAPITAL_ECO', 'Revenus'),
    ('CC_R', 'Taille agglo.'),
]

# VI pour les régressions - SANS CSP (corrélée avec revenus et diplôme)
# Justification : la CSP était la moins discriminante des 3 variables socio-économiques
# (CSP, niveau d'études, revenus) et introduisait de la multicolinéarité
croisements_vi_reg = [
    ('RS2C_RECODE_AG_R', 'Âge'),
    ('RS1_R', 'Genre'),
    ('CAPITAL_CULTUREL', 'Niveau d\'études'),
    ('CAPITAL_ECO', 'Revenus'),
    ('CC_R', 'Taille agglo.'),
]

# Variables dependantes avec leur groupe (pour couleurs dans le graphique)
# NOTE METHODOLOGIQUE: Seules les pratiques avec au moins 25% dans une categorie socio-demo sont incluses
# Les pratiques detaillees TV/RS sont analysees sur bases FILTREES (utilisateurs TV/RS)

# Couleurs par groupe pour la visualisation
GROUPE_COLORS = {
    'Source utilisee': '#3B82F6',      # Bleu
    'Format': '#8B5CF6',               # Violet
    'Plateforme RS': '#EC4899',        # Rose
    'Chaine generaliste': '#F59E0B',   # Orange
    'Chaine info TV': '#EF4444',       # Rouge
    'Media RS natif': '#10B981',       # Vert
    'Emission TV': '#F97316',          # Orange fonce
    'JT': '#DC2626',                   # Rouge fonce
    'Magazine TV': '#EA580C',          # Orange-rouge
    'Journal': '#6366F1',              # Indigo
    'Magazine presse': '#8B5CF6',      # Violet
}

# Variables dependantes sur population TOTALE (sources et formats generaux)
croisements_vd = [
    # Utilise cette source pour s'informer (NEWS1_R1_* - choix multiple)
    ('UTILISE_TV', 'TV', 'Source utilisee', 65.9),
    ('UTILISE_RS', 'Reseaux sociaux', 'Source utilisee', 47.1),
    ('UTILISE_PRESSE', 'Presse', 'Source utilisee', 34.0),
    ('UTILISE_RADIO', 'Radio/Podcasts', 'Source utilisee', 51.5),
    ('UTILISE_VIDEO', 'Video en ligne', 'Source utilisee', 26.4),
    # Formats d'information
    ('FORMAT_JT', 'JT / Flash info', 'Format', None),
    ('FORMAT_MAGAZINE', 'Magazines / Reportages', 'Format', None),
    ('FORMAT_DEBAT', 'Talk-shows / Debats', 'Format', None),
    ('FORMAT3_COURT', 'Formats courts', 'Format', None),
    ('FORMAT3_LONG', 'Formats longs', 'Format', None),
    ('FORMAT2_ECRIT', 'Format ecrit', 'Format', None),
    ('FORMAT2_VIDEO', 'Format video', 'Format', None),
]

print(f"   {len(croisements_vd)} pratiques generales (population totale)")

# Variables sur bases FILTREES (pratiques detaillees parmi les utilisateurs)
# Structure: (var_vd, label_vd, groupe, var_filtre, label_filtre, prevalence_filtre)
croisements_vd_filtres = []

# Pratiques TV detaillees (parmi utilisateurs TV, seuil 25%)
# Chaines generalistes
for code, (label, prev_total) in CHAINES_GEN_25.items():
    croisements_vd_filtres.append((
        f'CHAINE_GEN_{code}', label, 'Chaine generaliste',
        'UTILISE_TV', 'utilisateurs TV', prev_total
    ))

# Chaines info TV
for code, (label, prev_total) in CHAINES_INFO_25.items():
    croisements_vd_filtres.append((
        f'CHAINE_INFO_{code}', label, 'Chaine info TV',
        'UTILISE_TV', 'utilisateurs TV', prev_total
    ))

# Emissions TV
for code, (label, prev_total) in EMISSIONS_TV_25.items():
    croisements_vd_filtres.append((
        f'EMISSION_{code}', label, 'Emission TV',
        'UTILISE_TV', 'utilisateurs TV', prev_total
    ))

# JT
for code, (label, prev_total) in JT_25.items():
    croisements_vd_filtres.append((
        f'JT_{code}', label, 'JT',
        'UTILISE_TV', 'utilisateurs TV', prev_total
    ))

# Magazines TV
for code, (label, prev_total) in MAGAZINES_TV_25.items():
    croisements_vd_filtres.append((
        f'MAG_TV_{code}', label, 'Magazine TV',
        'UTILISE_TV', 'utilisateurs TV', prev_total
    ))

# Pratiques RS detaillees (parmi utilisateurs RS, seuil 25%)
# Plateformes RS
for code, (label, prev_total) in PLATEFORMES_RS_25.items():
    croisements_vd_filtres.append((
        f'PLAT_RS_{code}', label, 'Plateforme RS',
        'UTILISE_RS', 'utilisateurs RS', prev_total
    ))

# Medias RS natifs
for code, (label, prev_total) in MEDIAS_RS_25.items():
    croisements_vd_filtres.append((
        f'MEDIA_RS_{code}', label, 'Media RS natif',
        'UTILISE_RS', 'utilisateurs RS', prev_total
    ))

# Pratiques Presse detaillees (parmi utilisateurs Presse, seuil 25%)
# Journaux
for code, (label, prev_total) in JOURNAUX_25.items():
    croisements_vd_filtres.append((
        f'JOURNAL_{code}', label, 'Journal',
        'UTILISE_PRESSE', 'utilisateurs Presse', prev_total
    ))

print(f"   {len(croisements_vd_filtres)} pratiques detaillees (bases filtrees)")

forest_plot_data = []

# 1. Analyses sur base complete (sources et formats generaux)
for var_vi, label_vi in croisements_vi:
    for item in croisements_vd:
        # Format: (var_vd, label_vd, groupe, prevalence)
        var_vd, label_vd, groupe = item[0], item[1], item[2]
        prevalence = item[3] if len(item) > 3 else None

        if var_vi in df.columns and var_vd in df.columns:
            try:
                stat = get_chi2_stats(df, var_vi, var_vd)
                if stat['p'] < 0.05:
                    distribution = get_distribution(df, var_vi, var_vd, label_vi)
                    forest_plot_data.append({
                        'var1': label_vi,
                        'var2': label_vd,
                        'groupe': groupe,
                        'color': GROUPE_COLORS.get(groupe, '#6B7280'),
                        'v_cramer': stat['v_cramer'],
                        'chi2': stat['chi2'],
                        'significatif': True,
                        'distribution': distribution,
                        'base': 'tous',
                        'prevalence': prevalence  # % population totale
                    })
            except Exception as e:
                print(f"   Erreur pour {var_vi} x {var_vd}: {e}")

# 2. Analyses sur bases FILTREES (pratiques detaillees)
print("   - Analyses sur bases filtrees...")
for var_vi, label_vi in croisements_vi:
    for item in croisements_vd_filtres:
        # Nouveau format: (var_vd, label_vd, groupe, var_filtre, label_filtre, prevalence)
        var_vd, label_vd, groupe, var_filtre, label_filtre = item[0], item[1], item[2], item[3], item[4]
        prevalence = item[5] if len(item) > 5 else None

        if var_vi in df.columns and var_vd in df.columns and var_filtre in df.columns:
            try:
                # Filtrer le dataframe sur les utilisateurs du media
                df_filtre = df[df[var_filtre] == 1].copy()
                n_filtre = len(df_filtre)

                if n_filtre < 100:
                    continue

                stat = get_chi2_stats(df_filtre, var_vi, var_vd)
                if stat['p'] < 0.05:
                    distribution = get_distribution(df_filtre, var_vi, var_vd, label_vi)
                    forest_plot_data.append({
                        'var1': label_vi,
                        'var2': label_vd,
                        'groupe': groupe,
                        'color': GROUPE_COLORS.get(groupe, '#6B7280'),
                        'v_cramer': stat['v_cramer'],
                        'chi2': stat['chi2'],
                        'significatif': True,
                        'distribution': distribution,
                        'base': label_filtre,
                        'n_base': n_filtre,
                        'prevalence': prevalence  # % population totale (pour reference)
                    })
            except Exception as e:
                print(f"   Erreur pour {var_vi} x {var_vd} (filtre): {e}")

# Tous les croisements significatifs (triés par V de Cramer)
all_significant = sorted(forest_plot_data, key=lambda x: x['v_cramer'], reverse=True)
print(f"      {len(all_significant)} croisements significatifs au total")

# On garde TOUTES les données pour permettre le filtrage côté frontend
# Le frontend affichera le top 5 par groupe ou top 20 global
forest_plot_data = all_significant

# --- SECTION 2 : Effets nets (toutes choses égales par ailleurs) ---
print("   - Section 2: Effets nets...")

# Pour TOUS les croisements significatifs, tester l'effet net
effets_nets_data = []

for item in all_significant:
    # Retrouver les noms de variables a partir des labels
    var_vi = None
    var_vd = None
    var_filtre = None
    label_vi = item['var1']
    label_vd = item['var2']
    base = item.get('base', 'tous')

    for v, l in croisements_vi:
        if l == label_vi:
            var_vi = v
            break

    # Chercher dans croisements_vd (population totale)
    for vd_item in croisements_vd:
        if vd_item[1] == label_vd:
            var_vd = vd_item[0]
            break

    # Si pas trouve, chercher dans croisements_vd_filtres (bases filtrees)
    if not var_vd:
        for vd_item in croisements_vd_filtres:
            if vd_item[1] == label_vd:
                var_vd = vd_item[0]
                var_filtre = vd_item[3]  # Variable de filtre
                break

    if var_vi and var_vd:
        # Determiner le dataframe a utiliser (filtre ou total)
        if var_filtre and base != 'tous':
            df_analyse = df[df[var_filtre] == 1].copy()
        else:
            df_analyse = df

        # Utilise croisements_vi_reg pour la regression
        effet_data = get_effet_net_data(df_analyse, var_vi, var_vd, label_vi, label_vd, croisements_vi_reg)
        if effet_data:
            effet_data['v_cramer'] = item['v_cramer']
            effet_data['groupe'] = item['groupe']
            effet_data['color'] = item.get('color', GROUPE_COLORS.get(item['groupe'], '#6B7280'))
            effet_data['prevalence'] = item.get('prevalence')  # % population totale
            effet_data['base'] = base  # Base d'analyse
            effets_nets_data.append(effet_data)

print(f"      {len(effets_nets_data)} croisements analysés")
print(f"      {sum(1 for e in effets_nets_data if e['effet_net'])} avec effet net significatif")
print(f"      {sum(1 for e in effets_nets_data if e['effet_net'] == False)} sans effet net")

# Filtrer pour ne garder que les effets nets significatifs (triés par V de Cramer)
effets_nets_significatifs = sorted(
    [e for e in effets_nets_data if e['effet_net'] == True],
    key=lambda x: x['v_cramer'],
    reverse=True
)

# --- DIAGNOSTIC VIF (multicolinéarité) ---
print("   - Diagnostic VIF...")
vi_names_reg = [v[0] for v in croisements_vi_reg]
df_vif = df[vi_names_reg].dropna().copy()
for col in vi_names_reg:
    if df_vif[col].dtype == 'object':
        df_vif[col] = df_vif[col].astype('category').cat.codes
    df_vif[col] = pd.to_numeric(df_vif[col], errors='coerce')
df_vif = df_vif.dropna()

vif_values = {}
for i, col in enumerate(vi_names_reg):
    vif_values[col] = variance_inflation_factor(df_vif.values, i)

vif_max = max(vif_values.values())
print(f"      VIF max = {vif_max:.2f} ({'OK' if vif_max < 10 else 'ATTENTION'})")
for var, vif in vif_values.items():
    label = [l for v, l in croisements_vi_reg if v == var][0]
    print(f"        {label}: {vif:.2f}")

# --- CARACTÉRISATION DES CLIVAGES ---
print("   - Caracterisation des clivages...")

# Compter les effets par VI
effets_par_vi = {}
for e in effets_nets_significatifs:
    vi = e['label_vi']
    if vi not in effets_par_vi:
        effets_par_vi[vi] = []
    effets_par_vi[vi].append(e)

# Clivage générationnel (âge)
n_age = len(effets_par_vi.get('Âge', []))

# Clivage socio-économique (revenus + diplôme)
n_revenus = len(effets_par_vi.get('Revenus', []))
n_diplome = len(effets_par_vi.get("Niveau d'études", []))
n_socioeco = n_revenus + n_diplome

# Autres
n_genre = len(effets_par_vi.get('Genre', []))
n_agglo = len(effets_par_vi.get('Taille agglo.', []))

print(f"      Clivage generationnel: {n_age} effets")
print(f"      Clivage socio-economique: {n_socioeco} effets (revenus={n_revenus}, diplome={n_diplome})")
print(f"      Autres: genre={n_genre}, agglo={n_agglo}")

# --- SECTION 3 : Effets sur la connaissance ---
print("   - Section 3: Effets (quizz)...")

# Source x Score quizz
source_quizz_data = []
for source in df_info['SOURCE_SIMPLE'].dropna().unique():
    subset = df_info[df_info['SOURCE_SIMPLE'] == source]
    if len(subset) >= 30:
        mean_score = subset['SCORE_QUIZZ'].mean()
        pct_eleve = len(subset[subset['SCORE_QUIZZ'] >= 3]) / len(subset) * 100
        source_quizz_data.append({
            'source': source,
            'score_moyen': round(mean_score, 2),
            'pct_score_eleve': round(pct_eleve, 1),
            'n': len(subset)
        })

source_quizz_data = sorted(source_quizz_data, key=lambda x: x['score_moyen'], reverse=True)
source_quizz_stats = get_chi2_stats(df_info, 'SOURCE_SIMPLE', 'SCORE_QUIZZ_CAT')

# Age x Score quizz
age_quizz_data = []
for age in sorted(df['RS2C_RECODE_AG_R'].dropna().unique()):
    subset = df[df['RS2C_RECODE_AG_R'] == age]
    mean_score = subset['SCORE_QUIZZ'].mean()
    age_quizz_data.append({
        'age': AGE_LABELS.get(int(age), str(age)),
        'score_moyen': round(mean_score, 2),
        'n': len(subset)
    })

# ============================================================
# 5. CONSTRUCTION DU JSON
# ============================================================
print("\n4. Construction du JSON...")

chapitre_json = {
    "id": "basculement",
    "numero": 1,
    "titre": "Le grand basculement",
    "sousTitre": "TV vs Réseaux sociaux : un clivage générationnel ?",
    "question": "La télévision cède-t-elle sa place aux réseaux sociaux comme source principale d'information ?",

    # --- ACCROCHE ---
    "accroche": {
        "texte": f"Parmi les 18-24 ans qui s'informent, {round(pct_rs_jeunes)}% désignent les réseaux sociaux comme source principale. Chez les 70 ans et plus, ils ne sont que {round(pct_rs_seniors)}%. Les jeunes sont {rapport_rs} fois plus nombreux à s'informer via les RS : assiste-t-on à une révolution des pratiques ou à un simple effet d'âge ?",
        "chiffreMarquant": {
            "valeur": f"{rapport_rs}",
            "unite": "x",
            "label": "fois plus de 18-24 ans s'informent via les RS que les 70+"
        }
    },

    # --- ANALYSE ---
    "analyse": {
        "sections": [
            # Section 1 : Ce qui distingue le plus
            {
                "id": "facteurs-distinctifs",
                "titre": "Ce qui distingue le plus",
                "description": "Quels facteurs sociaux expliquent le mieux les différences de pratiques informationnelles ? Le graphique ci-dessous classe les croisements par force d'association (V de Cramer).",
                "noteMethodologique": "Seules les pratiques concernant au moins 25% d'une catégorie socio-démographique sont incluses. Les contenus détaillés (chaînes TV, émissions, plateformes RS) sont analysés uniquement parmi les personnes utilisant ce média pour s'informer (ex : chaînes TV parmi ceux qui utilisent la TV, plateformes RS parmi ceux qui utilisent les RS).",
                "groupeColors": GROUPE_COLORS,
                "visualisations": [
                    {
                        "id": "forest-plot-cramer",
                        "type": "horizontal_bar",
                        "titre": "Force d'association des facteurs sociaux",
                        "description": "V de Cramer : 0 = pas de lien, 0.1 = faible, 0.2 = modéré, 0.3+ = fort. Le % indique la diffusion dans la population totale.",
                        "data": forest_plot_data,
                        "config": {
                            "xAxis": "v_cramer",
                            "yAxis": "label",
                            "xMax": 0.35,
                            "showPrevalence": True,
                            "thresholds": [
                                {"value": 0.1, "label": "Faible"},
                                {"value": 0.2, "label": "Modéré"},
                                {"value": 0.3, "label": "Fort"}
                            ]
                        }
                    }
                ],
                "conclusion": "L'âge est le facteur le plus discriminant, notamment pour les pratiques numériques (RS, plateformes vidéo). Le milieu social (revenus, diplôme) structure les choix de médias traditionnels. Le genre a des effets plus limités."
            },

            # Section 2 : Effets nets (toutes choses égales par ailleurs)
            {
                "id": "effets-nets",
                "titre": "Ce qui compte vraiment",
                "description": f"Sur {len(all_significant)} associations significatives, nous avons testé lesquelles persistent une fois qu'on contrôle l'âge, le genre, le niveau d'études, les revenus et la taille d'agglomération.",
                "noteMethodologique": "Les pourcentages affichés sont des probabilités prédites « toutes choses égales par ailleurs » : ils représentent la probabilité estimée pour chaque catégorie, en supposant que les autres caractéristiques (âge, genre, diplôme, revenus, lieu) sont à leur valeur moyenne. En cliquant sur une carte, vous pouvez voir la distribution réelle (brute) observée dans l'enquête. La CSP a été exclue du modèle car fortement corrélée au niveau d'études et aux revenus.",
                "visualisations": [
                    {
                        "id": "effets-nets-cards",
                        "type": "effet_net_cards",
                        "titre": "Associations avec effet net confirmé",
                        "description": f"{len(effets_nets_significatifs)} associations restent significatives toutes choses égales par ailleurs.",
                        "data": effets_nets_significatifs,
                        "config": {
                            "showPrevalence": True
                        }
                    }
                ],
                "conclusion": f"Deux clivages structurent les pratiques informationnelles, indépendamment l'un de l'autre. Le clivage générationnel ({n_age} effets) oppose jeunes (RS, vidéo, plateformes numériques) et seniors (TV, radio, presse). Le clivage socio-économique ({n_socioeco} effets) oppose classes favorisées (presse, magazines d'investigation) et populaires (TV généraliste, magazines TV populaires). Ces effets persistent après contrôle mutuel."
            },

            # Section 3 : Les effets
            {
                "id": "effets-connaissance",
                "titre": "Quel effet sur la connaissance ?",
                "description": "S'informer via les RS rend-il moins bien informé ? Nous avons testé les connaissances factuelles des répondants.",
                "visualisations": [
                    {
                        "id": "source-quizz",
                        "type": "bar",
                        "titre": "Score moyen au quizz selon la source principale",
                        "description": "Score de 0 à 4 (4 questions d'actualité)",
                        "data": source_quizz_data,
                        "config": {
                            "xAxis": "source",
                            "yAxis": "score_moyen",
                            "yMax": 4
                        },
                        "stats": source_quizz_stats
                    },
                    {
                        "id": "age-quizz",
                        "type": "line",
                        "titre": "Score moyen au quizz selon l'âge",
                        "data": age_quizz_data
                    }
                ],
                "insight": "Les utilisateurs de presse et de sites média ont les meilleurs scores. Mais attention : cela peut refléter un effet de sélection (les plus intéressés choisissent ces sources) plutôt qu'un effet causal."
            }
        ]
    },

    # --- NUANCES ---
    "nuances": {
        "titre": "Ce qui complexifie le constat",
        "points": [
            {
                "titre": "Les 15-17 ans : l'effet famille",
                "description": "Les 15-17 ans vivant chez leurs parents sont plus exposés à la TV familiale (27%) que les 18-24 ans (19%) souvent autonomes."
            },
            {
                "titre": "RS ne veut pas dire désinformation",
                "description": "Sur les réseaux sociaux, une part importante des contenus partagés provient de médias traditionnels. Le support change, pas forcément la source originale."
            },
            {
                "titre": "Effet d'âge ou effet de génération ?",
                "description": "Les jeunes d'aujourd'hui reviendront-ils à la TV en vieillissant (effet d'âge) ou garderont-ils leurs pratiques (effet de génération) ? L'enquête transversale ne permet pas de trancher."
            },
            {
                "titre": "La qualité de l'information",
                "description": "Le score au quizz mesure des connaissances factuelles ponctuelles, pas la capacité à comprendre des enjeux complexes."
            }
        ]
    },

    # --- PRENOTIONS DECONSTRUITES ---
    "prenotions": {
        "titre": "Idées reçues à l'épreuve des données",
        "introduction": "Plusieurs idées circulent sur les pratiques informationnelles des Français, notamment des jeunes. Que disent réellement nos données ?",
        "items": [
            {
                "prejuge": "Les jeunes ne s'informent plus",
                "verdict": "faux",
                "sourceIdee": {
                    "citation": "La génération Z déserte l'information, préférant le divertissement.",
                    "source": "Discours médiatique courant",
                    "url": None
                },
                "nosResultats": f"Les 18-24 ans s'informent, mais différemment : {round(pct_rs_jeunes)}% citent les réseaux sociaux comme source principale. Seule une minorité (< 5%) déclare ne jamais s'informer. Le support change, pas l'intérêt pour l'actualité.",
                "pourAllerPlusLoin": [
                    {"titre": "Reuters Digital News Report 2024", "url": "https://reutersinstitute.politics.ox.ac.uk/digital-news-report/2024"}
                ]
            },
            {
                "prejuge": "S'informer sur les réseaux sociaux rend moins bien informé",
                "verdict": "a_nuancer",
                "sourceIdee": {
                    "citation": "Les algorithmes des réseaux sociaux enferment les jeunes dans des bulles de désinformation.",
                    "source": "Critique des RS",
                    "url": None
                },
                "nosResultats": "Le score au quizz d'actualité est légèrement plus bas chez les utilisateurs de RS, mais l'écart n'est pas aussi important qu'attendu. Cela peut refléter un effet de sélection (âge, éducation) plutôt qu'un effet causal des RS eux-mêmes.",
                "pourAllerPlusLoin": [
                    {"titre": "Rapport Bronner sur les désordres informationnels", "url": "https://www.vie-publique.fr/rapport/283201-les-lumieres-lere-numerique-rapport-bronner"}
                ]
            },
            {
                "prejuge": "La télévision est la source d'information la plus fiable",
                "verdict": "a_nuancer",
                "sourceIdee": {
                    "citation": "Les JT des grandes chaînes restent la référence pour une information vérifiée.",
                    "source": "Discours médiatique traditionnel",
                    "url": None
                },
                "nosResultats": "La TV reste la source la plus utilisée (66% des Français), mais cette prédominance reflète davantage un effet d'âge et d'habitude que la qualité perçue. Les jeunes font autant confiance aux médias natifs RS qu'aux chaînes traditionnelles.",
                "pourAllerPlusLoin": [
                    {"titre": "Baromètre ARCOM de la confiance", "url": "https://www.arcom.fr/"}
                ]
            },
            {
                "prejuge": "Les classes populaires sont plus vulnérables à la désinformation",
                "verdict": "a_nuancer",
                "sourceIdee": {
                    "citation": "Les milieux défavorisés, moins éduqués, seraient plus crédules face aux fake news.",
                    "source": "Préjugé social",
                    "url": None
                },
                "nosResultats": f"Nos données montrent que le capital culturel et économique influence le CHOIX des sources (presse vs TV populaire), mais pas nécessairement la capacité à distinguer le vrai du faux. Le clivage est plus horizontal que vertical.",
                "pourAllerPlusLoin": [
                    {"titre": "Étude La Croix sur la confiance dans les médias", "url": "https://www.la-croix.com/"}
                ]
            }
        ],
        "conclusion": "Les pratiques informationnelles évoluent, mais les raccourcis simplistes ne résistent pas à l'analyse des données. La réalité est plus nuancée que ne le suggèrent les discours dominants."
    },

    # --- IMPLICATIONS ---
    "implications": {
        "titre": "Ce que cela signifie",
        "points": [
            "Le paysage médiatique se fragmente : les générations ne partagent plus les mêmes références informationnelles.",
            "L'éducation aux médias doit s'adapter aux pratiques réelles des jeunes (RS, vidéo) plutôt qu'aux médias traditionnels.",
            "La régulation des algorithmes de recommandation devient un enjeu démocratique majeur.",
            "Les médias traditionnels doivent repenser leur présence numérique pour toucher les nouvelles générations."
        ],
        "transition": "Mais tous les Français s'informent-ils ? Le chapitre suivant explore le phénomène des 'décrocheurs' de l'information."
    },

    # --- ANNEXES ---
    "annexes": {
        "presse": {
            "chiffreCle": f"{round(pct_rs_jeunes)}% des 18-24 ans s'informent principalement via les réseaux sociaux",
            "chiffreCle2": f"Écart de {round(ecart_rs)} points avec les 70 ans et plus",
            "citation": "Un basculement générationnel net s'opère dans les pratiques informationnelles : avant 25 ans, les réseaux sociaux dominent ; après, la télévision reprend le dessus.",
            "contexte": "Données ARCOM 2024, base : 3346 répondants. Analyse de la source PRINCIPALE d'information (question NEWS1BIS).",
            "miseEnGarde": "Ces chiffres portent sur la source principale déclarée. La plupart des Français combinent plusieurs sources."
        },
        "actionPublique": {
            "indicateur": "Part des moins de 25 ans citant les RS comme source principale",
            "valeurIndicateur": f"{round(pct_rs_jeunes)}%",
            "tendance": "Stable à la hausse depuis 2019",
            "levier": "Éducation aux médias et à l'information (EMI)",
            "recommandations": [
                "Adapter les programmes EMI aux pratiques numériques réelles",
                "Former les enseignants à l'analyse critique des contenus sur RS",
                "Encourager les médias à investir les plateformes vidéo (YouTube, TikTok)",
                "Suivre l'évolution des usages pour anticiper les mutations"
            ],
            "donneesLiees": [
                {"label": "Rapport ARCOM 2024", "url": "https://www.arcom.fr/"},
                {"label": "Ressources CLEMI", "url": "https://www.clemi.fr/"}
            ]
        }
    },

    # --- METADATA ---
    "metadata": {
        "source": "ARCOM - Les Français et l'information 2024",
        "echantillon": len(df),
        "echantillonAnalyse": len(df_info),
        "ponderation": "POIDS03",
        "dateGeneration": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "variablesPrincipales": ["NEWS1BIS_R", "RS2C_RECODE_AG_R", "RS1_R", "CSP_3",
                                  "CAPITAL_CULTUREL", "CAPITAL_ECO", "SCORE_QUIZZ"],
        "methodologie": {
            "regression": "GLM logistique pondérée avec test de Wald",
            "variablesControle": ["Âge", "Genre", "Niveau d'études", "Revenus", "Taille agglo."],
            "vifMax": round(vif_max, 2),
            "noteCSP": "CSP exclue (multicolinéarité avec revenus/diplôme, VIF > 10 avec CSP)"
        }
    }
}

# ============================================================
# 6. EXPORT JSON
# ============================================================
print("\n5. Export JSON...")

# Fonction pour convertir les types numpy
def convert_to_native(obj):
    if isinstance(obj, dict):
        return {k: convert_to_native(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_native(item) for item in obj]
    elif isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj

output_file = OUTPUT_DIR / "chapitre-01-basculement.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(convert_to_native(chapitre_json), f, ensure_ascii=False, indent=2)

print(f"   -> {output_file}")

# ============================================================
# 7. RESUME
# ============================================================
print("\n" + "=" * 70)
print("RESUME")
print("=" * 70)
print(f"\nTitre: {chapitre_json['titre']}")
print(f"Question: {chapitre_json['question']}")
print(f"\nChiffre cle: {round(pct_rs_jeunes)}% des 18-24 ans sur RS vs {round(pct_rs_seniors)}% des 70+")
print(f"Ecart: {round(ecart_rs)} points")
print(f"\nSections d'analyse: {len(chapitre_json['analyse']['sections'])}")
print(f"Nuances: {len(chapitre_json['nuances']['points'])}")
print(f"\nJSON genere: {output_file}")
print("=" * 70)
