"""
Génération des effet_net_cards STRATIFIÉES par âge ET par diplôme pour la partie 2 (équipement/valeurs)

Méthodologie :
- Les tests d'interaction ont montré que les effets varient selon l'âge et le diplôme
- On fait des régressions séparées par groupe (3 pour l'âge, 3 pour le diplôme)
- Chaque carte montre l'effet d'une variable pour UN groupe spécifique

Structure du JSON de sortie :
- Chaque item a un champ 'strate_type' ('age' ou 'diplome')
- Chaque item a un champ 'strate_key' (ex: 'jeunes', 'sans_bac')
- Chaque item a un champ 'strate_label' (ex: '15-34 ans', 'Sans Bac')
- Chaque item a un champ 'strate_order' (1, 2, 3)

Sortie : JSON pour le frontend avec structure effet_net_cards_stratifie
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
from scipy import stats
import json
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# CONFIGURATION
# =============================================================================

BASE_DIR = Path('python')
DATA_DIR = BASE_DIR / 'data' / 'francais-information'
OUTPUT_DIR = Path('frontend/public/data/enquetes/francais-information/chapitres/chapitre-01-basculement')

# Groupes d'âge pour la stratification
AGE_GROUPS = {
    'jeunes': {'codes': [1, 2, 3], 'label': '15-34 ans', 'order': 1},
    'moyens': {'codes': [4, 5], 'label': '35-59 ans', 'order': 2},
    'seniors': {'codes': [6, 7], 'label': '60 ans et +', 'order': 3},
}

# Groupes de diplôme pour la stratification
DIPLOME_GROUPS = {
    'sans_bac': {'codes': [1, 2, 3, 4], 'label': 'Sans Bac', 'order': 1},
    'bac_bac2': {'codes': [5, 6], 'label': 'Bac à Bac+2', 'order': 2},
    'bac3_plus': {'codes': [7, 8, 9, 10], 'label': 'Bac+3 et plus', 'order': 3},
}

# Couleurs par type de variable
COLORS = {
    'Équipement': '#F59E0B',  # Orange
    'Confiance': '#EC4899',   # Rose
    'Valeurs': '#8B5CF6',     # Violet
    'Politique': '#3B82F6',   # Bleu
}

# =============================================================================
# CHARGEMENT DES DONNÉES
# =============================================================================

print("=" * 70)
print("GÉNÉRATION DES EFFET_NET_CARDS STRATIFIÉES (ÂGE + DIPLÔME)")
print("=" * 70)

df = pd.read_excel(DATA_DIR / 'base-info-arcom.xlsx')
df['POIDS03'] = df['POIDS03'].astype(str).str.replace(',', '.').astype(float)

# --- Variables dépendantes ---
news1_cols = [f'NEWS1_R1_{i}' for i in range(1, 10) if f'NEWS1_R1_{i}' in df.columns]

def utilise_source(row, code):
    for col in news1_cols:
        if pd.notna(row[col]) and row[col] == code:
            return 1
    return 0

df['UTILISE_TV'] = df.apply(lambda r: utilise_source(r, 1), axis=1)
df['UTILISE_RS'] = df.apply(lambda r: utilise_source(r, 3), axis=1)

# --- Groupe d'âge ---
age = df['RS2C_RECODE_AG_R']
df['AGE_GROUPE'] = None
for key, config in AGE_GROUPS.items():
    df.loc[age.isin(config['codes']), 'AGE_GROUPE'] = key

# --- Groupe de diplôme ---
diplome = df['RS5_R']
df['DIPLOME_GROUPE'] = None
for key, config in DIPLOME_GROUPS.items():
    df.loc[diplome.isin(config['codes']), 'DIPLOME_GROUPE'] = key

# --- Diplôme en 3 catégories (variable de contrôle pour strat âge) ---
df['DIPLOME_3CAT'] = pd.cut(
    diplome,
    bins=[0, 4.5, 6.5, 10],
    labels=['< Bac', 'Bac a Bac+2', 'Bac+3 et +']
)

# --- Âge en 3 catégories (variable de contrôle pour strat diplôme) ---
df['AGE_3CAT'] = None
df.loc[age.isin([1, 2, 3]), 'AGE_3CAT'] = '15-34 ans'
df.loc[age.isin([4, 5]), 'AGE_3CAT'] = '35-59 ans'
df.loc[age.isin([6, 7]), 'AGE_3CAT'] = '60 ans et +'

# --- Revenus (variable de contrôle) ---
if 'RS14_R' in df.columns:
    revenus = df['RS14_R']
    df['REVENUS_3CAT'] = pd.cut(
        revenus,
        bins=[0, 3, 6, 20],
        labels=['Faible', 'Moyen', 'Eleve']
    )
else:
    df['REVENUS_3CAT'] = 'Moyen'  # fallback

# --- Variables d'équipement ---
df['POSSEDE_TV'] = df['RS16_R_1'].isin([1, 2]).astype(int)
df['POSSEDE_SMARTPHONE'] = df['RS16_R_4'].isin([1, 2]).astype(int)
df['POSSEDE_TABLETTE'] = df['RS16_R_7'].isin([1, 2]).astype(int)
df['POSSEDE_ENCEINTE'] = df['RS16_R_9'].isin([1, 2]).astype(int)
df['POSSEDE_MONTRE'] = df['RS16_R_11'].isin([1, 2]).astype(int)

# --- Variables de confiance ---
df['CONF_JOURNALISTES'] = df['INF3_R1_1'].notna().astype(int)
df['CONF_CREATEURS'] = df['INF3_R1_6'].notna().astype(int) if 'INF3_R1_6' in df.columns else 0
df['CONF_PROCHES'] = df['INF3_R1_9'].notna().astype(int) if 'INF3_R1_9' in df.columns else 0

# --- Attitudes ---
df['RAREMENT_UNE_VERITE'] = df['ATTSOURCES_R1_3'].notna().astype(int) if 'ATTSOURCES_R1_3' in df.columns else 0

# --- Politique ---
pol = df['NOU1_R']
df['POLITIQUE_3CAT'] = 'Centre'
df.loc[pol.isin([1, 2, 3, 4]), 'POLITIQUE_3CAT'] = 'Gauche'
df.loc[pol.isin([8, 9, 10, 11]), 'POLITIQUE_3CAT'] = 'Droite'

print(f"Effectifs par groupe d'age : {df['AGE_GROUPE'].value_counts().to_dict()}")
print(f"Effectifs par groupe de diplôme : {df['DIPLOME_GROUPE'].value_counts().to_dict()}")

# =============================================================================
# DÉFINITION DES VARIABLES À TESTER
# =============================================================================

# Variables indépendantes (équipement et valeurs)
VARIABLES_VI = [
    ('POSSEDE_SMARTPHONE', 'Possède un smartphone', 'Équipement'),
    ('POSSEDE_TABLETTE', 'Possède une tablette', 'Équipement'),
    ('POSSEDE_ENCEINTE', 'Possède une enceinte connectée', 'Équipement'),
    ('POSSEDE_MONTRE', 'Possède une montre connectée', 'Équipement'),
    ('POSSEDE_TV', 'Possède une télévision', 'Équipement'),
    ('CONF_JOURNALISTES', 'Fait confiance aux journalistes', 'Confiance'),
    ('CONF_CREATEURS', 'Fait confiance aux créateurs', 'Confiance'),
    ('CONF_PROCHES', 'Fait confiance aux proches', 'Confiance'),
    ('RAREMENT_UNE_VERITE', 'Pense qu\'il y a rarement une seule vérité', 'Valeurs'),
]

# Variables dépendantes
VARIABLES_VD = [
    ('UTILISE_RS', 'Utilise les réseaux sociaux pour s\'informer'),
    ('UTILISE_TV', 'Utilise la télévision pour s\'informer'),
]

# =============================================================================
# FONCTIONS D'ANALYSE
# =============================================================================

def get_effet_net_stratifie(df, var_vi, var_vd, strate_col, strate_key, controles):
    """
    Calcule l'effet net d'une variable VI sur VD pour un groupe de strate spécifique.
    Contrôle par les variables spécifiées.
    """
    # Filtrer par strate
    df_strat = df[df[strate_col] == strate_key].copy()

    # Colonnes nécessaires
    cols = [var_vi, var_vd, 'POIDS03'] + controles
    df_reg = df_strat[cols].dropna()

    if len(df_reg) < 50:
        return None

    # Vérifier que var_vi a de la variance
    if df_reg[var_vi].nunique() < 2:
        return None

    # Calculer les % bruts
    mask_avec = df_reg[var_vi] == 1
    mask_sans = df_reg[var_vi] == 0

    if mask_avec.sum() == 0 or mask_sans.sum() == 0:
        return None

    pct_avec = (df_reg.loc[mask_avec, var_vd] * df_reg.loc[mask_avec, 'POIDS03']).sum() / df_reg.loc[mask_avec, 'POIDS03'].sum() * 100
    pct_sans = (df_reg.loc[mask_sans, var_vd] * df_reg.loc[mask_sans, 'POIDS03']).sum() / df_reg.loc[mask_sans, 'POIDS03'].sum() * 100

    n_avec = mask_avec.sum()
    n_sans = mask_sans.sum()

    # Régression logistique avec contrôles
    try:
        # Créer les dummies pour les contrôles
        df_dummies = pd.DataFrame()
        df_dummies[var_vi] = df_reg[var_vi].values

        for ctrl in controles:
            ctrl_vals = df_reg[ctrl]
            if ctrl_vals.dtype == 'object' or isinstance(ctrl_vals.iloc[0], str) or hasattr(ctrl_vals, 'cat'):
                ctrl_dummies = pd.get_dummies(ctrl_vals.astype(str), prefix=ctrl, drop_first=True)
                df_dummies = pd.concat([df_dummies.reset_index(drop=True), ctrl_dummies.reset_index(drop=True)], axis=1)

        X = df_dummies.astype(float)
        X = sm.add_constant(X)
        y = df_reg[var_vd].values.astype(float)
        weights = df_reg['POIDS03'].values.astype(float)

        model = sm.GLM(y, X, family=sm.families.Binomial(), freq_weights=weights)
        result = model.fit()

        # Extraire le coefficient et la p-value pour var_vi
        coef = result.params[var_vi]
        p_value = result.pvalues[var_vi]
        odds_ratio = np.exp(coef)

        # Calculer les probabilités prédites ajustées
        X_means = X.mean()

        # Prob avec VI = 1
        X_avec = X_means.copy()
        X_avec[var_vi] = 1
        prob_avec = result.predict(X_avec.values.reshape(1, -1))[0] * 100

        # Prob avec VI = 0
        X_sans = X_means.copy()
        X_sans[var_vi] = 0
        prob_sans = result.predict(X_sans.values.reshape(1, -1))[0] * 100

        effet_net = p_value < 0.05

        return {
            'pct_avec_brut': round(pct_avec, 1),
            'pct_sans_brut': round(pct_sans, 1),
            'diff_brute': round(pct_avec - pct_sans, 1),
            'pct_avec_ajuste': round(prob_avec, 1),
            'pct_sans_ajuste': round(prob_sans, 1),
            'diff_ajustee': round(prob_avec - prob_sans, 1),
            'odds_ratio': round(odds_ratio, 2),
            'p_value': round(p_value, 4),
            'effet_net': bool(effet_net),
            'n_avec': int(n_avec),
            'n_sans': int(n_sans),
            'n_total': int(len(df_reg)),
        }

    except Exception as e:
        print(f"  Erreur regression {var_vi} x {var_vd} ({strate_key}): {e}")
        return None


def generate_all_cards(df, variables_vi, variables_vd):
    """
    Génère toutes les cartes stratifiées (par âge ET par diplôme).
    """
    all_cards = []

    # --- Stratification par ÂGE ---
    print("\n" + "=" * 70)
    print("STRATIFICATION PAR ÂGE")
    print("=" * 70)

    controles_age = ['DIPLOME_3CAT', 'REVENUS_3CAT']

    for var_vd, label_vd in variables_vd:
        print(f"\n--- {label_vd} ---")

        for var_vi, label_vi, groupe in variables_vi:
            for age_key, age_config in AGE_GROUPS.items():
                result = get_effet_net_stratifie(
                    df, var_vi, var_vd,
                    'AGE_GROUPE', age_key,
                    controles_age
                )

                if result is None:
                    continue

                card = {
                    'var_vi': var_vi,
                    'var_vd': var_vd,
                    'label_vi': label_vi,
                    'label_vd': label_vd,
                    'groupe_vi': groupe,
                    'color': COLORS.get(groupe, '#6B7280'),

                    # Infos de stratification
                    'strate_type': 'age',
                    'strate_key': age_key,
                    'strate_label': age_config['label'],
                    'strate_order': age_config['order'],

                    # Valeurs
                    **result
                }
                all_cards.append(card)

                sig = "***" if result['p_value'] < 0.001 else "**" if result['p_value'] < 0.01 else "*" if result['p_value'] < 0.05 else ""
                print(f"  {label_vi:35} | {age_config['label']:12} | diff={result['diff_ajustee']:+5.1f}pp | p={result['p_value']:.3f} {sig}")

    # --- Stratification par DIPLÔME ---
    print("\n" + "=" * 70)
    print("STRATIFICATION PAR DIPLÔME")
    print("=" * 70)

    controles_diplome = ['AGE_3CAT', 'REVENUS_3CAT']

    for var_vd, label_vd in variables_vd:
        print(f"\n--- {label_vd} ---")

        for var_vi, label_vi, groupe in variables_vi:
            for dip_key, dip_config in DIPLOME_GROUPS.items():
                result = get_effet_net_stratifie(
                    df, var_vi, var_vd,
                    'DIPLOME_GROUPE', dip_key,
                    controles_diplome
                )

                if result is None:
                    continue

                card = {
                    'var_vi': var_vi,
                    'var_vd': var_vd,
                    'label_vi': label_vi,
                    'label_vd': label_vd,
                    'groupe_vi': groupe,
                    'color': COLORS.get(groupe, '#6B7280'),

                    # Infos de stratification
                    'strate_type': 'diplome',
                    'strate_key': dip_key,
                    'strate_label': dip_config['label'],
                    'strate_order': dip_config['order'],

                    # Valeurs
                    **result
                }
                all_cards.append(card)

                sig = "***" if result['p_value'] < 0.001 else "**" if result['p_value'] < 0.01 else "*" if result['p_value'] < 0.05 else ""
                print(f"  {label_vi:35} | {dip_config['label']:15} | diff={result['diff_ajustee']:+5.1f}pp | p={result['p_value']:.3f} {sig}")

    return all_cards


# =============================================================================
# GÉNÉRATION DES RÉSULTATS
# =============================================================================

cards = generate_all_cards(df, VARIABLES_VI, VARIABLES_VD)

print(f"\n{len(cards)} cartes générées au total")
print(f"  - Stratifiées par âge : {len([c for c in cards if c['strate_type'] == 'age'])}")
print(f"  - Stratifiées par diplôme : {len([c for c in cards if c['strate_type'] == 'diplome'])}")

# =============================================================================
# CRÉATION DU JSON
# =============================================================================

# Trier les cartes
cards_sorted = sorted(cards, key=lambda x: (x['strate_type'], x['var_vd'], x['groupe_vi'], x['label_vi'], x['strate_order']))

# Structurer le JSON - format simplifié avec toutes les cartes
output = {
    "id": "01b-facteurs-stratifie",
    "titre": "Effets stratifiés",
    "sousTitre": "Comment les effets varient selon l'âge et le diplôme",
    "description": "Analyse des facteurs associés à l'usage des réseaux sociaux et de la télévision pour s'informer, stratifiée par groupe d'âge et par niveau de diplôme.",

    "noteMethodologique": {
        "titre": "Pourquoi stratifier ?",
        "texte": "Les tests d'interaction ont montré que les effets de l'équipement et des valeurs varient significativement selon l'âge et le diplôme (p < 0.05). Présenter un effet 'moyen' serait donc trompeur.",
        "controles": "Pour la stratification par âge : contrôle par diplôme et revenus. Pour la stratification par diplôme : contrôle par âge et revenus.",
        "interpretation": "La différence ajustée (pp) représente l'écart de probabilité entre ceux qui ont la caractéristique et ceux qui ne l'ont pas, les autres variables étant contrôlées."
    },

    "groupeColors": COLORS,

    "sections": [
        {
            "id": "effets-stratifies",
            "titre": "Effets stratifiés par âge et diplôme",
            "description": "Utilisez les filtres pour explorer comment les effets varient selon l'âge ou le diplôme, pour l'usage des RS ou de la TV.",
            "visualisations": [
                {
                    "id": "effet-net-stratifie",
                    "type": "effet_net_cards_stratifie",
                    "titre": "Effets nets stratifiés",
                    "data": cards_sorted
                }
            ]
        }
    ],

    "metadata": {
        "source": "Enquête ARCOM 2024 - Les Français et l'information",
        "n_total": len(df),
        "n_par_age": {age_config['label']: int((df['AGE_GROUPE'] == age_key).sum()) for age_key, age_config in AGE_GROUPS.items()},
        "n_par_diplome": {dip_config['label']: int((df['DIPLOME_GROUPE'] == dip_key).sum()) for dip_key, dip_config in DIPLOME_GROUPS.items()},
        "methode": "Régressions logistiques stratifiées, contrôlées par les autres variables socio-démographiques",
        "seuil_significativite": 0.05,
    }
}

# Sauvegarder
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
output_path = OUTPUT_DIR / '01b-facteurs-stratifie.json'

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\n[OK] JSON sauvegardé : {output_path}")

# =============================================================================
# RÉSUMÉ DES RÉSULTATS CLÉS
# =============================================================================

print("\n" + "=" * 70)
print("RÉSUMÉ : VARIATIONS LES PLUS MARQUANTES")
print("=" * 70)

# Calculer la variation pour chaque variable
def calc_variation(cards, var_vi, var_vd, strate_type):
    subset = [c for c in cards if c['var_vi'] == var_vi and c['var_vd'] == var_vd and c['strate_type'] == strate_type]
    if len(subset) < 2:
        return 0
    diffs = [c['diff_ajustee'] for c in subset]
    return max(diffs) - min(diffs)

print("\n--- Variations par ÂGE (RS) ---")
variations_age_rs = []
for var_vi, label_vi, groupe in VARIABLES_VI:
    var = calc_variation(cards, var_vi, 'UTILISE_RS', 'age')
    variations_age_rs.append((label_vi, var))
variations_age_rs.sort(key=lambda x: -x[1])
for label, var in variations_age_rs[:5]:
    print(f"  {label:40} : variation = {var:.1f}pp")

print("\n--- Variations par DIPLÔME (RS) ---")
variations_dip_rs = []
for var_vi, label_vi, groupe in VARIABLES_VI:
    var = calc_variation(cards, var_vi, 'UTILISE_RS', 'diplome')
    variations_dip_rs.append((label_vi, var))
variations_dip_rs.sort(key=lambda x: -x[1])
for label, var in variations_dip_rs[:5]:
    print(f"  {label:40} : variation = {var:.1f}pp")

print("\n--- Variations par ÂGE (TV) ---")
variations_age_tv = []
for var_vi, label_vi, groupe in VARIABLES_VI:
    var = calc_variation(cards, var_vi, 'UTILISE_TV', 'age')
    variations_age_tv.append((label_vi, var))
variations_age_tv.sort(key=lambda x: -x[1])
for label, var in variations_age_tv[:5]:
    print(f"  {label:40} : variation = {var:.1f}pp")

print("\n--- Variations par DIPLÔME (TV) ---")
variations_dip_tv = []
for var_vi, label_vi, groupe in VARIABLES_VI:
    var = calc_variation(cards, var_vi, 'UTILISE_TV', 'diplome')
    variations_dip_tv.append((label_vi, var))
variations_dip_tv.sort(key=lambda x: -x[1])
for label, var in variations_dip_tv[:5]:
    print(f"  {label:40} : variation = {var:.1f}pp")
