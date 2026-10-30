"""
Template pour générer un nouveau chapitre
Copier ce fichier et adapter les variables selon le chapitre

Usage:
    1. Copier ce fichier: generate_chapitre_XX_nom.py
    2. Modifier les constantes CHAPITRE_* en haut
    3. Définir les variables VI et VD
    4. Exécuter le script
"""
import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
import json
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# CONFIGURATION DU CHAPITRE - À MODIFIER
# ============================================================
CHAPITRE_ID = "nom-du-chapitre"
CHAPITRE_NUMERO = 2
CHAPITRE_TITRE = "Titre du chapitre"
CHAPITRE_SOUS_TITRE = "Sous-titre explicatif"
CHAPITRE_QUESTION = "Question principale du chapitre ?"

# ============================================================
# CHEMINS
# ============================================================
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data" / "francais-information"
OUTPUT_DIR = BASE_DIR / "outputs" / "json"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# FONCTIONS UTILITAIRES (ne pas modifier)
# ============================================================

def load_labels_from_datamap(datamap_path):
    """Charge les labels des variables depuis le fichier datamap Excel."""
    texts = pd.read_excel(datamap_path, sheet_name='TEXTS')
    labels = {}
    for var_name in texts['NAME'].unique():
        var_labels = texts[(texts['NAME'] == var_name) & (texts['TYPE'] == 'LABEL')]
        if len(var_labels) > 0:
            labels[var_name] = {}
            for _, row in var_labels.iterrows():
                if pd.notna(row['CODE']):
                    code = int(float(row['CODE']))
                    label = row['FR:L'] if pd.notna(row['FR:L']) else str(code)
                    labels[var_name][code] = label
    return labels


def cramers_v(ct):
    """Calcule V de Cramer sur tableau de contingence pondéré"""
    chi2 = stats.chi2_contingency(ct)[0]
    n = ct.sum().sum()
    min_dim = min(ct.shape) - 1
    return np.sqrt(chi2 / (n * min_dim)) if min_dim > 0 and n > 0 else 0


def get_chi2_stats(df, var1, var2, poids='POIDS03'):
    """Calcule Chi2 et V de Cramer avec pondération"""
    mask = df[var1].notna() & df[var2].notna() & df[poids].notna()
    df_valid = df[mask]
    ct = pd.crosstab(
        df_valid[var1],
        df_valid[var2],
        values=df_valid[poids],
        aggfunc='sum'
    ).fillna(0)
    chi2, p, dof, _ = stats.chi2_contingency(ct)
    v = cramers_v(ct)
    return {'chi2': round(chi2, 1), 'p': p, 'dof': int(dof), 'v_cramer': round(v, 3)}


def get_distribution(df, var_vi, var_vd, labels_map, poids='POIDS03'):
    """Calcule la distribution de var_vd selon les catégories de var_vi."""
    mask = df[var_vi].notna() & df[var_vd].notna() & df[poids].notna()
    df_valid = df[mask]
    distribution = []

    # Ordre des catégories
    csp_order = ['CSP+', 'CSP milieu', 'CSP-']
    capital_order = ['Faible', 'Moyen', 'Eleve']

    categories = df_valid[var_vi].unique()
    if var_vi in ['CAPITAL_CULTUREL', 'CAPITAL_ECO']:
        categories = [c for c in capital_order if c in categories]
    elif var_vi == 'CSP_3':
        categories = [c for c in csp_order if c in categories]
    else:
        categories = sorted(categories)

    for cat in categories:
        subset = df_valid[df_valid[var_vi] == cat]
        total_poids = subset[poids].sum()
        pct_oui = 0
        if total_poids > 0:
            oui_poids = subset[subset[var_vd] == 1][poids].sum()
            pct_oui = (oui_poids / total_poids) * 100

        code_to_label = labels_map.get(var_vi, {})
        if var_vi in labels_map and np.issubdtype(type(cat), np.number) and not pd.isna(cat):
            cat_label = code_to_label.get(int(cat), str(cat))
        else:
            cat_label = str(cat)

        distribution.append({'category': cat_label, 'pct_oui': round(pct_oui, 1)})

    return distribution


def test_effet_net(df, var_vi, var_vd, all_vi_vars, poids='POIDS03'):
    """Teste si var_vi a un effet significatif sur var_vd toutes choses égales."""
    vi_names = [v[0] for v in all_vi_vars]
    cols_needed = [var_vd, poids] + vi_names
    df_reg = df[cols_needed].dropna().copy()

    if len(df_reg) < 100:
        return None, None

    for col in vi_names:
        if df_reg[col].dtype == 'object' or df_reg[col].dtype.name == 'category':
            df_reg[col] = df_reg[col].astype('category').cat.codes

    if df_reg[var_vd].dtype == 'object':
        df_reg[var_vd] = df_reg[var_vd].astype('category').cat.codes

    for col in df_reg.columns:
        df_reg[col] = pd.to_numeric(df_reg[col], errors='coerce')
    df_reg = df_reg.dropna()

    if len(df_reg) < 100:
        return None, None

    df_dummies = pd.DataFrame()
    for vi in vi_names:
        vi_dummies = pd.get_dummies(df_reg[vi].astype(int), drop_first=True, prefix=vi)
        df_dummies = pd.concat([df_dummies, vi_dummies], axis=1)

    df_dummies[var_vd] = df_reg[var_vd].values
    df_dummies[poids] = df_reg[poids].values

    var_vi_cols = [c for c in df_dummies.columns if c.startswith(var_vi + '_')]
    if len(var_vi_cols) == 0:
        return None, None

    X_cols = [c for c in df_dummies.columns if c not in [var_vd, poids]]
    X = df_dummies[X_cols].astype(float)
    X = sm.add_constant(X)
    y = df_dummies[var_vd].astype(float)
    weights = df_dummies[poids].astype(float)

    try:
        model = sm.GLM(y, X, family=sm.families.Binomial(), freq_weights=weights)
        result = model.fit()

        var_vi_indices = [X.columns.get_loc(c) for c in var_vi_cols if c in X.columns]
        if len(var_vi_indices) == 0:
            return None, None

        R = np.zeros((len(var_vi_indices), len(X.columns)))
        for i, idx in enumerate(var_vi_indices):
            R[i, idx] = 1

        wald_test = result.wald_test(R)
        p_value = float(wald_test.pvalue)
        return p_value, result

    except Exception as e:
        print(f"   Erreur régression {var_vi} x {var_vd}: {e}")
        return None, None


def get_predicted_probabilities(df, var_vi, var_vd, all_vi_vars, labels_map, poids='POIDS03'):
    """Calcule les probabilités prédites ajustées pour chaque catégorie de var_vi."""
    vi_names = [v[0] for v in all_vi_vars]
    if var_vi not in vi_names:
        vi_names = [var_vi] + vi_names

    cols_needed = [var_vd, poids] + vi_names
    missing_cols = [c for c in cols_needed if c not in df.columns]
    if missing_cols:
        return None

    df_reg = df[cols_needed].dropna().copy()
    if len(df_reg) < 100:
        return None

    code_to_label = labels_map.get(var_vi, {})

    # Sauvegarder le mapping AVANT conversion
    cat_mappings = {}
    for col in vi_names:
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

    df_dummies = pd.DataFrame()
    for vi in vi_names:
        vi_dummies = pd.get_dummies(df_reg[vi].astype(int), drop_first=True, prefix=vi)
        df_dummies = pd.concat([df_dummies, vi_dummies], axis=1)

    df_dummies[var_vd] = df_reg[var_vd].values
    df_dummies[poids] = df_reg[poids].values

    X_cols = [c for c in df_dummies.columns if c not in [var_vd, poids]]
    X = df_dummies[X_cols].astype(float)
    X = sm.add_constant(X)
    y = df_dummies[var_vd].astype(float)
    weights = df_dummies[poids].astype(float)

    try:
        model = sm.GLM(y, X, family=sm.families.Binomial(), freq_weights=weights)
        result = model.fit()

        predictions = {}
        X_means = X.mean()
        categories = sorted(df_reg[var_vi].unique())
        vi_cat_mapping = cat_mappings.get(var_vi, {})

        for cat in categories:
            X_pred = X_means.copy()
            for col in X_pred.index:
                if col.startswith(var_vi + '_'):
                    dummy_cat = int(col.split('_')[-1])
                    X_pred[col] = 1.0 if dummy_cat == cat else 0.0

            prob = result.predict(X_pred.values.reshape(1, -1))[0]
            original_value = vi_cat_mapping.get(int(cat), int(cat))

            # Gérer les variables avec valeurs textuelles (CAPITAL_ECO, CSP_3, etc.)
            if isinstance(original_value, str):
                cat_label = original_value
            elif code_to_label:
                cat_label = code_to_label.get(int(original_value), str(original_value))
            else:
                cat_label = str(original_value)

            predictions[cat_label] = round(prob * 100, 1)

        return predictions

    except Exception:
        return None


def get_effet_net_data(df, var_vi, var_vd, label_vi, label_vd, all_vi_vars, labels_map, poids='POIDS03'):
    """Calcule toutes les données pour l'affichage d'un effet net."""
    distribution = get_distribution(df, var_vi, var_vd, labels_map, poids)
    if not distribution:
        return None

    pcts = [d['pct_oui'] for d in distribution]
    min_idx = pcts.index(min(pcts))
    max_idx = pcts.index(max(pcts))
    cat_min = distribution[min_idx]
    cat_max = distribution[max_idx]

    rapport = round(cat_max['pct_oui'] / cat_min['pct_oui'], 1) if cat_min['pct_oui'] > 0 else None
    p_value, _ = test_effet_net(df, var_vi, var_vd, all_vi_vars, poids)
    effet_net = p_value < 0.05 if p_value is not None else None

    predicted_probs = get_predicted_probabilities(df, var_vi, var_vd, all_vi_vars, labels_map, poids)

    distribution_ajustee = None
    cat_min_ajuste = None
    cat_max_ajuste = None
    rapport_ajuste = None
    ecart_ajuste = None

    if predicted_probs:
        distribution_ajustee = []
        for d in distribution:
            cat_label = d['category']
            pct_ajuste = predicted_probs.get(cat_label)
            distribution_ajustee.append({
                'category': cat_label,
                'pct_brut': d['pct_oui'],
                'pct_ajuste': pct_ajuste
            })

        pcts_ajustes = [d['pct_ajuste'] for d in distribution_ajustee if d['pct_ajuste'] is not None]
        if pcts_ajustes:
            min_val = min(pcts_ajustes)
            max_val = max(pcts_ajustes)
            for d in distribution_ajustee:
                if d['pct_ajuste'] == min_val:
                    cat_min_ajuste = {'category': d['category'], 'pct_ajuste': d['pct_ajuste']}
                if d['pct_ajuste'] == max_val:
                    cat_max_ajuste = {'category': d['category'], 'pct_ajuste': d['pct_ajuste']}
            if min_val > 0:
                rapport_ajuste = round(max_val / min_val, 1)
            ecart_ajuste = round(max_val - min_val, 1)

    # Détecter si le max/min brut diffère du max/min ajusté
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
        'cat_min': cat_min,
        'cat_max': cat_max,
        'rapport': rapport,
        'cat_min_ajuste': cat_min_ajuste,
        'cat_max_ajuste': cat_max_ajuste,
        'rapport_ajuste': rapport_ajuste,
        'ecart_ajuste': ecart_ajuste,
        'distribution_ajustee': distribution_ajustee,
        'max_category_differs': max_category_differs,
        'min_category_differs': min_category_differs,
        'p_value': round(p_value, 4) if p_value else None,
        'effet_net': effet_net,
        'distribution': distribution
    }


def convert_to_native(obj):
    """Convertit les types numpy en types Python natifs pour JSON."""
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


# ============================================================
# CHARGEMENT DES DONNÉES
# ============================================================
print("=" * 70)
print(f"GENERATION JSON - CHAPITRE {CHAPITRE_NUMERO} : {CHAPITRE_TITRE.upper()}")
print("=" * 70)

print("\n1. Chargement du datamap et des données...")
DATAMAP = load_labels_from_datamap(DATA_DIR / "datamap-info-arcom.xlsx")
df = pd.read_excel(DATA_DIR / "base-info-arcom.xlsx")
df['POIDS03'] = df['POIDS03'].astype(str).str.replace(',', '.').astype(float)
print(f"   {len(df)} répondants, {len(DATAMAP)} variables avec labels")

# Labels depuis datamap
AGE_LABELS = DATAMAP.get('RS2C_RECODE_AG_R', {})
GENRE_LABELS = DATAMAP.get('RS1_R', {})
AGGLO_LABELS = DATAMAP.get('CC_R', {})

LABELS_MAP = {
    'RS2C_RECODE_AG_R': AGE_LABELS,
    'RS1_R': GENRE_LABELS,
    'CC_R': AGGLO_LABELS,
}

# ============================================================
# VARIABLES À MODIFIER SELON LE CHAPITRE
# ============================================================
print("\n2. Définition des variables...")

# Variables indépendantes pour les analyses descriptives
croisements_vi = [
    ('RS2C_RECODE_AG_R', 'Âge'),
    ('RS1_R', 'Genre'),
    # Ajouter les variables pertinentes pour ce chapitre
]

# Variables indépendantes pour la régression (sans variables corrélées)
croisements_vi_reg = [
    ('RS2C_RECODE_AG_R', 'Âge'),
    ('RS1_R', 'Genre'),
    # Retirer les variables avec VIF > 10
]

# Variables dépendantes (pratiques à analyser)
# Format: (nom_variable, label, groupe, prévalence)
croisements_vd = [
    # Exemple:
    # ('UTILISE_TV', 'TV', 'Source utilisée', 65.9),
]

# Couleurs par groupe
GROUPE_COLORS = {
    # 'Groupe': '#XXXXXX',
}

# ============================================================
# CALCULS
# ============================================================
print("\n3. Calculs statistiques...")

# ... Ajouter les calculs spécifiques au chapitre

# ============================================================
# CONSTRUCTION DU JSON
# ============================================================
print("\n4. Construction du JSON...")

chapitre_json = {
    "id": CHAPITRE_ID,
    "numero": CHAPITRE_NUMERO,
    "titre": CHAPITRE_TITRE,
    "sousTitre": CHAPITRE_SOUS_TITRE,
    "question": CHAPITRE_QUESTION,

    "accroche": {
        "texte": "À compléter...",
        "chiffreMarquant": {
            "valeur": "XX",
            "unite": "%",
            "label": "Description du chiffre"
        }
    },

    "analyse": {
        "sections": [
            # Ajouter les sections
        ]
    },

    "nuances": {
        "titre": "Ce qui complexifie le constat",
        "points": []
    },

    "metadata": {
        "source": "ARCOM - Les Français et l'information 2024",
        "echantillon": len(df),
        "ponderation": "POIDS03",
        "dateGeneration": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
}

# ============================================================
# EXPORT
# ============================================================
print("\n5. Export JSON...")

output_file = OUTPUT_DIR / f"chapitre-{CHAPITRE_NUMERO:02d}-{CHAPITRE_ID}.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(convert_to_native(chapitre_json), f, ensure_ascii=False, indent=2)

print(f"   -> {output_file}")
print("=" * 70)
