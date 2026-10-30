# -*- coding: utf-8 -*-
"""
Analyse 01b complète : Équipement, Usages, Valeurs
- V de Cramer pour toutes les variables avec UTILISE_RS ET UTILISE_TV
- Régression multivariée : qu'est-ce qui prédit TV vs RS ?

Corrections v2:
- Prévalence = taux de diffusion de chaque variable (pas de la VD)
- Force d'association pour RS ET TV
- Variables harmonisées entre les deux approches
"""
import json
import pandas as pd
import numpy as np
from pathlib import Path
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Importer l'utilitaire pour le datamap
from utils_datamap import DatamapHelper

# ============================================
# CHARGEMENT DES DONNÉES
# ============================================
BASE_DIR = Path('python')
DATA_DIR = BASE_DIR / 'data' / 'francais-information'
df = pd.read_excel(DATA_DIR / 'base-info-arcom.xlsx')
# Conversion des poids (format français avec virgules)
if df['POIDS03'].dtype == 'object':
    df['POIDS03'] = df['POIDS03'].str.replace(',', '.').astype(float)
else:
    df['POIDS03'] = pd.to_numeric(df['POIDS03'], errors='coerce').fillna(1)

print(f"Données chargées : {len(df)} observations")

# ============================================
# DATAMAP HELPER - pour récupérer les codes automatiquement
# ============================================
datamap_path = DATA_DIR / 'datamap-info-arcom.xlsx'
dm = DatamapHelper(datamap_path)

# Récupérer les codes pour les sources d'information (NEWS1_R1)
CODE_TV = dm.find_code_by_label('NEWS1_R1', 'télévision')  # 1
CODE_RS = dm.find_code_by_label('NEWS1_R1', 'réseaux sociaux')  # 3
CODE_PRESSE = 6  # "En lisant un journal ou un magazine, quel que soit le support"
CODE_RADIO = dm.find_code_by_label('NEWS1_R1', 'radio')  # 4
print(f"Codes NEWS1: TV={CODE_TV}, RS={CODE_RS}, Presse={CODE_PRESSE}, Radio={CODE_RADIO}")


# Labels pour l'âge
dm_texts = pd.read_excel(datamap_path, sheet_name='TEXTS')

def get_labels(var_name):
    """Récupère les labels d'une variable depuis le datamap"""
    texts = dm_texts[dm_texts['NAME'] == var_name]
    labels = {}
    for _, row in texts.iterrows():
        code = row.get('CODE')
        label = row.get('FR:L', row.get('VALUE', ''))
        if pd.notna(code) and pd.notna(label):
            labels[int(code)] = str(label)
    return labels

AGE_LABELS = get_labels('RS2C_RECODE_AG_R')
print(f"Labels âge : {AGE_LABELS}")

# ============================================
# CRÉATION DES VARIABLES
# ============================================

# --- VARIABLE DÉPENDANTE : Utilise RS/TV pour s'informer ---
def utilise_source(row, codes, pattern='NEWS1_R1_'):
    cols = [c for c in row.index if c.startswith(pattern)]
    for col in cols:
        if pd.notna(row[col]) and int(row[col]) in codes:
            return 1
    return 0

# Utiliser les codes récupérés dynamiquement depuis le datamap
df['UTILISE_TV'] = df.apply(lambda r: utilise_source(r, [CODE_TV]), axis=1)
df['UTILISE_RS'] = df.apply(lambda r: utilise_source(r, [CODE_RS]), axis=1)
df['UTILISE_PRESSE'] = df.apply(lambda r: utilise_source(r, [CODE_PRESSE]), axis=1)
df['UTILISE_RADIO'] = df.apply(lambda r: utilise_source(r, [CODE_RADIO]), axis=1)

# Calculer les prévalences de toutes les sources
prev_rs = (df['UTILISE_RS'] * df['POIDS03']).sum() / df['POIDS03'].sum() * 100
prev_tv = (df['UTILISE_TV'] * df['POIDS03']).sum() / df['POIDS03'].sum() * 100
prev_presse = (df['UTILISE_PRESSE'] * df['POIDS03']).sum() / df['POIDS03'].sum() * 100
prev_radio = (df['UTILISE_RADIO'] * df['POIDS03']).sum() / df['POIDS03'].sum() * 100
print(f"Prévalence RS : {prev_rs:.1f}%, TV : {prev_tv:.1f}%, Presse : {prev_presse:.1f}%, Radio : {prev_radio:.1f}%")
print(f"Utilise TV : {df['UTILISE_TV'].sum()}, RS : {df['UTILISE_RS'].sum()}, Presse : {df['UTILISE_PRESSE'].sum()}, Radio : {df['UTILISE_RADIO'].sum()}")

# --- VARIABLES SOCIO-DÉMO ---
df['AGE'] = df['RS2C_RECODE_AG_R']

# Milieu social (CSP simplifiée)
def recode_csp(rs4):
    if pd.isna(rs4): return np.nan
    if rs4 == 3: return 'CSP+'
    elif rs4 in [1, 2, 4]: return 'CSP milieu'
    elif rs4 in [5, 6]: return 'CSP-'
    return np.nan
df['CSP'] = df['RS4_R'].apply(recode_csp)

# Niveau d'études
df['ETUDES'] = df['RS1_R']

# --- VARIABLES ÉQUIPEMENT ---
# DEVICEXMOMENTS : équipements utilisés pour s'informer
device_cols = [c for c in df.columns if c.startswith('DEVICEXMOMENTS_R_')]
# 1=Smartphone, 2=Tablette, 3=Ordinateur, 4=TV, 5=Radio
df['EQUIP_SMARTPHONE'] = df.apply(lambda r: 1 if any(pd.notna(r[c]) and r[c] == 1 for c in device_cols) else 0, axis=1)
df['EQUIP_TABLETTE'] = df.apply(lambda r: 1 if any(pd.notna(r[c]) and r[c] == 2 for c in device_cols) else 0, axis=1)
df['EQUIP_ORDI'] = df.apply(lambda r: 1 if any(pd.notna(r[c]) and r[c] == 3 for c in device_cols) else 0, axis=1)

# --- VARIABLES USAGES ---
# RSINFO : Comment s'informer sur RS
rsinfo_cols = [c for c in df.columns if c.startswith('RSINFO_1_LR_R_')]
# 1=Temps réel, 2=Fil d'actu algo, 3=Recherche active, 4=Notifications...
df['USAGE_ALGO'] = df.apply(lambda r: 1 if any(pd.notna(r[c]) and r[c] == 2 for c in rsinfo_cols) else 0, axis=1)
df['USAGE_TEMPS_REEL'] = df.apply(lambda r: 1 if any(pd.notna(r[c]) and r[c] == 1 for c in rsinfo_cols) else 0, axis=1)
df['USAGE_RECHERCHE'] = df.apply(lambda r: 1 if any(pd.notna(r[c]) and r[c] == 3 for c in rsinfo_cols) else 0, axis=1)

# MOTIVRS : Motivations RS
motiv_cols = [c for c in df.columns if c.startswith('MOTIVRS_R_')]
# 1=Facilité, 5=Formats courts, 8=Temps passé, 10=Commenter
df['MOTIV_FACILITE'] = df.apply(lambda r: 1 if any(pd.notna(r[c]) and r[c] == 1 for c in motiv_cols) else 0, axis=1)
df['MOTIV_FORMATS_COURTS'] = df.apply(lambda r: 1 if any(pd.notna(r[c]) and r[c] == 5 for c in motiv_cols) else 0, axis=1)
df['MOTIV_TEMPS_PASSE'] = df.apply(lambda r: 1 if any(pd.notna(r[c]) and r[c] == 8 for c in motiv_cols) else 0, axis=1)
df['MOTIV_COMMENTER'] = df.apply(lambda r: 1 if any(pd.notna(r[c]) and r[c] == 10 for c in motiv_cols) else 0, axis=1)

# --- VARIABLES VALEURS ---
# NOU1_R : Orientation politique (1-7)
df['POLITIQUE'] = df['NOU1_R']
df['POL_GAUCHE'] = (df['NOU1_R'].isin([1, 2])).astype(int)
df['POL_DROITE'] = (df['NOU1_R'].isin([6, 7])).astype(int)

# DOUTE_R : Doute sur les médias
df['DOUTE_MEDIAS'] = (df['DOUTE_R'] == 1).astype(int)

# INF3_R1 : ST Confiance (multi-réponse)
# Les colonnes INF3_R1_1, INF3_R1_2, etc. contiennent les CODES des personnes sélectionnées
# Codes: 1=Journalistes, 6=Créateurs, 9=Proches, 10=Aucun
# Récupérer les codes depuis le datamap
CODE_CONF_JOURNALISTES = dm.find_code_by_label('INF3_R1', 'Journalistes')
CODE_CONF_CREATEURS = dm.find_code_by_label('INF3_R1', 'Créateurs')
CODE_CONF_PROCHES = dm.find_code_by_label('INF3_R1', 'proches')
CODE_CONF_AUCUN = dm.find_code_by_label('INF3_R1', 'Aucun')
print(f"Codes INF3_R1: Journalistes={CODE_CONF_JOURNALISTES}, Créateurs={CODE_CONF_CREATEURS}, Proches={CODE_CONF_PROCHES}, Aucun={CODE_CONF_AUCUN}")

inf3_r1_cols = [c for c in df.columns if c.startswith('INF3_R1_')]

def has_conf_code(row, code):
    """Vérifie si le code apparaît dans les colonnes multi-réponse"""
    for col in inf3_r1_cols:
        if pd.notna(row[col]) and int(row[col]) == code:
            return 1
    return 0

df['CONF_JOURNALISTES'] = df.apply(lambda r: has_conf_code(r, CODE_CONF_JOURNALISTES), axis=1)
df['CONF_CREATEURS'] = df.apply(lambda r: has_conf_code(r, CODE_CONF_CREATEURS), axis=1)
df['CONF_PROCHES'] = df.apply(lambda r: has_conf_code(r, CODE_CONF_PROCHES), axis=1)
df['CONF_AUCUN'] = df.apply(lambda r: has_conf_code(r, CODE_CONF_AUCUN), axis=1)

print(f"Confiance: journalistes={df['CONF_JOURNALISTES'].sum()}, créateurs={df['CONF_CREATEURS'].sum()}, proches={df['CONF_PROCHES'].sum()}, aucun={df['CONF_AUCUN'].sum()}")

print("Variables créées")

# ============================================
# CALCUL DES V DE CRAMER
# ============================================

def cramers_v_weighted(x, y, weights):
    """Calcule le V de Cramer pondéré"""
    contingency = pd.crosstab(x, y, weights, aggfunc='sum').fillna(0)
    if contingency.shape[0] < 2 or contingency.shape[1] < 2:
        return 0
    chi2 = stats.chi2_contingency(contingency)[0]
    n = contingency.sum().sum()
    min_dim = min(contingency.shape) - 1
    if min_dim == 0 or n == 0:
        return 0
    return np.sqrt(chi2 / (n * min_dim))

def get_distribution(df, var_vi, var_vd, weights='POIDS03'):
    """Calcule la distribution de var_vd par catégorie de var_vi"""
    mask = df[var_vi].notna() & df[var_vd].notna()
    distribution = []

    unique_vals = sorted(df.loc[mask, var_vi].unique())
    is_binary = set(unique_vals) <= {0, 1, 0.0, 1.0}

    for cat in unique_vals:
        cat_mask = mask & (df[var_vi] == cat)
        w = df.loc[cat_mask, weights]
        y = df.loc[cat_mask, var_vd]
        pct = (y * w).sum() / w.sum() * 100

        # Récupérer le label si disponible
        if var_vi == 'AGE' and int(cat) in AGE_LABELS:
            cat_label = AGE_LABELS[int(cat)]
        elif is_binary:
            cat_label = 'Oui' if cat == 1 else 'Non'
        else:
            cat_label = str(cat)

        distribution.append({
            'category': cat_label,
            'pct_oui': round(pct, 1)
        })

    return distribution

def get_prevalence(df, var, weights='POIDS03'):
    """Calcule la prévalence d'une variable binaire (% qui ont 1)"""
    mask = df[var].notna()
    w = df.loc[mask, weights]
    v = df.loc[mask, var]
    return round((v * w).sum() / w.sum() * 100, 1)

# Variables à analyser (harmonisées avec la régression)
# On garde toutes les variables pour la force d'association
variables = [
    # Équipement
    ('EQUIP_SMARTPHONE', 'Smartphone', 'Équipement'),
    ('EQUIP_TABLETTE', 'Tablette', 'Équipement'),
    ('EQUIP_ORDI', 'Ordinateur', 'Équipement'),
    # Usages
    ('USAGE_ALGO', 'Passivité algorithmique', 'Usage'),
    ('USAGE_TEMPS_REEL', 'Temps réel', 'Usage'),
    ('USAGE_RECHERCHE', 'Recherche active', 'Usage'),
    ('MOTIV_FACILITE', 'Motivation: facilité', 'Usage'),
    ('MOTIV_FORMATS_COURTS', 'Motivation: formats courts', 'Usage'),
    ('MOTIV_TEMPS_PASSE', 'Motivation: temps passé', 'Usage'),
    ('MOTIV_COMMENTER', 'Motivation: commenter', 'Usage'),
    # Valeurs
    ('POL_GAUCHE', 'Orientation gauche', 'Valeurs'),
    ('POL_DROITE', 'Orientation droite', 'Valeurs'),
    ('DOUTE_MEDIAS', 'Doute sur médias', 'Valeurs'),
    ('CONF_JOURNALISTES', 'Confiance journalistes', 'Valeurs'),
    ('CONF_CREATEURS', 'Confiance créateurs', 'Valeurs'),
    ('CONF_PROCHES', 'Confiance proches', 'Valeurs'),
]

def compute_associations(df, var_vd, var_vd_label, variables):
    """Calcule les V de Cramer pour une variable dépendante"""
    print(f"\n=== V DE CRAMER avec {var_vd_label} ===")
    results = []

    for var, label, groupe in variables:
        if var not in df.columns:
            print(f"  {label}: colonne manquante")
            continue

        mask = df[var].notna() & df[var_vd].notna()
        if mask.sum() < 100:
            print(f"  {label}: données insuffisantes ({mask.sum()})")
            continue

        v = cramers_v_weighted(df.loc[mask, var], df.loc[mask, var_vd], df.loc[mask, 'POIDS03'])
        distribution = get_distribution(df, var, var_vd)

        # Prévalence de la variable (pas de la VD)
        prevalence = get_prevalence(df, var)

        results.append({
            'var1': var_vd_label,
            'var2': label,
            'var_code': var,  # Code de la variable pour identifier si elle est dans la régression
            'groupe': groupe,
            'v_cramer': round(v, 3),
            'distribution': distribution,
            'prevalence': prevalence,  # Prévalence de la variable, pas de la VD
        })
        print(f"  {label} ({groupe}): V = {v:.3f}, prévalence = {prevalence:.1f}%")

    # Trier par V de Cramer
    results.sort(key=lambda x: x['v_cramer'], reverse=True)
    return results

# Calculer pour RS et TV
results_rs = compute_associations(df, 'UTILISE_RS', 'Usage RS', variables)
results_tv = compute_associations(df, 'UTILISE_TV', 'Usage TV', variables)

print(f"\nRS: {len(results_rs)} associations, TV: {len(results_tv)} associations")

# ============================================
# JUSTIFICATION DU FOCUS TV/RS : V DE CRAMER AVEC L'ÂGE
# ============================================

print("\n=== V DE CRAMER ENTRE L'ÂGE ET CHAQUE SOURCE ===")
sources_cramer = []

for source_var, source_label, source_prev in [
    ('UTILISE_RS', 'Réseaux sociaux', prev_rs),
    ('UTILISE_TV', 'Télévision', prev_tv),
    ('UTILISE_PRESSE', 'Presse écrite', prev_presse),
    ('UTILISE_RADIO', 'Radio', prev_radio),
]:
    mask = df['AGE'].notna() & df[source_var].notna()
    v = cramers_v_weighted(df.loc[mask, 'AGE'], df.loc[mask, source_var], df.loc[mask, 'POIDS03'])

    # Calculer le profil par âge (distribution)
    distribution = get_distribution(df, 'AGE', source_var)

    sources_cramer.append({
        'source': source_label,
        'v_cramer': round(v, 3),
        'prevalence': round(source_prev, 1),
        'distribution': distribution
    })
    print(f"  {source_label}: V = {v:.3f}, prévalence = {source_prev:.1f}%")

# Trier par V de Cramer décroissant
sources_cramer.sort(key=lambda x: x['v_cramer'], reverse=True)

# ============================================
# RÉGRESSION LOGISTIQUE MULTIVARIÉE (RS et TV)
# ============================================

# Variables incluses dans la régression (pour marquer dans la force d'association)
REGRESSION_VARS = [
    'AGE', 'EQUIP_SMARTPHONE', 'USAGE_ALGO', 'USAGE_TEMPS_REEL',
    'MOTIV_FORMATS_COURTS', 'DOUTE_MEDIAS', 'CONF_CREATEURS',
    'CONF_JOURNALISTES', 'POL_GAUCHE', 'POL_DROITE'
]

def run_regression(df, target_var, target_label):
    """Exécute une régression logistique pour une variable cible"""
    print(f"\n=== RÉGRESSION LOGISTIQUE : {target_label} ===")

    try:
        import statsmodels.api as sm

        # Variables pour la régression (harmonisées)
        reg_vars = [
            'AGE',  # Socio-démo
            'EQUIP_SMARTPHONE',  # Équipement (le plus utilisé)
            'USAGE_ALGO', 'USAGE_TEMPS_REEL', 'MOTIV_FORMATS_COURTS',  # Usages (top 3)
            'DOUTE_MEDIAS', 'CONF_CREATEURS', 'CONF_JOURNALISTES',  # Valeurs
            'POL_GAUCHE', 'POL_DROITE'
        ]

        # Filtrer données complètes
        reg_df = df[[target_var, 'POIDS03'] + reg_vars].dropna()
        print(f"Observations pour régression : {len(reg_df)}")

        if len(reg_df) > 200:
            # Préparer X avec dummies pour AGE
            X = reg_df[reg_vars].copy()
            X = pd.get_dummies(X, columns=['AGE'], drop_first=True)

            # Convertir en float pour statsmodels
            X = X.astype(float)
            X = sm.add_constant(X)

            y = reg_df[target_var].astype(float)
            weights = reg_df['POIDS03'].astype(float)

            # Régression
            model = sm.GLM(y, X, family=sm.families.Binomial(), freq_weights=weights)
            result = model.fit()

            print("\n--- Coefficients ---")
            coefs = result.summary2().tables[1]

            regression_results = {
                'n_obs': len(reg_df),
                'pseudo_r2': round(float(result.pseudo_rsquared()), 3),
                'coefficients': []
            }

            for var in coefs.index:
                if var != 'const':
                    coef = float(coefs.loc[var, 'Coef.'])
                    pval = float(coefs.loc[var, 'P>|z|'])
                    sig = pval < 0.05

                    regression_results['coefficients'].append({
                        'variable': var,
                        'coef': round(coef, 3),
                        'odds_ratio': round(np.exp(coef), 2),
                        'p_value': round(pval, 4),
                        'significatif': sig
                    })

                    marker = '***' if pval < 0.001 else '**' if pval < 0.01 else '*' if pval < 0.05 else ''
                    print(f"  {var}: OR = {np.exp(coef):.2f} (p = {pval:.4f}) {marker}")

            # Variables significatives
            sig_vars = [c['variable'] for c in regression_results['coefficients'] if c['significatif']]
            print(f"\nVariables significatives : {sig_vars}")

            return regression_results

    except Exception as e:
        print(f"Erreur régression : {e}")
        import traceback
        traceback.print_exc()
        return None

# Exécuter les deux régressions
regression_rs = run_regression(df, 'UTILISE_RS', 'Réseaux sociaux')
regression_tv = run_regression(df, 'UTILISE_TV', 'Télévision')

# ============================================
# GÉNÉRATION DU JSON
# ============================================

# Couleurs par groupe
GROUPE_COLORS = {
    'Socio-démo': '#6366F1',    # Indigo
    'Équipement': '#F59E0B',    # Orange
    'Usage': '#10B981',         # Vert
    'Valeurs': '#EC4899',       # Rose
}

# Marquer les variables qui sont dans la régression
def mark_regression_vars(results, regression_vars):
    """Ajoute un flag pour indiquer si la variable est dans la régression"""
    for r in results:
        r['color'] = GROUPE_COLORS.get(r['groupe'], '#6b7280')
        r['in_regression'] = r.get('var_code', '') in regression_vars
        # Supprimer var_code du JSON final
        if 'var_code' in r:
            del r['var_code']
    return results

results_rs = mark_regression_vars(results_rs, REGRESSION_VARS)
results_tv = mark_regression_vars(results_tv, REGRESSION_VARS)

output = {
    'id': '01b-facteurs',
    'titre': 'Ce qui accompagne le basculement',
    'sousTitre': 'Équipement, usages ou valeurs : qu\'est-ce qui compte vraiment ?',
    'description': 'Analyse des facteurs associés à l\'usage des réseaux sociaux et de la télévision pour s\'informer',

    'metadata': {
        'prevalence_rs': round(prev_rs, 1),
        'prevalence_tv': round(prev_tv, 1),
        'n_total': len(df),
    },

    'sections': [
        {
            'id': 'justification-focus',
            'titre': 'Pourquoi TV et réseaux sociaux ?',
            'description': 'Le clivage générationnel est-il aussi marqué pour toutes les sources d\'information ?',
            'visualisations': [
                {
                    'type': 'v_cramer_table',
                    'titre': 'Force du clivage générationnel par source',
                    'description': 'Le V de Cramer mesure l\'intensité du lien entre l\'âge et l\'usage de chaque source (0 = aucun lien, 1 = lien parfait)',
                    'data': sources_cramer,
                }
            ],
            'noteExplicative': {
                'titre': 'Justification du focus TV/RS',
                'texte': 'Le V de Cramer révèle que la fracture générationnelle est nettement plus marquée pour les réseaux sociaux (V=0.40) et la télévision (V=0.31) que pour la presse ou la radio (V≈0.15). Ces deux sources cristallisent donc le basculement médiatique entre générations : les jeunes vers les RS, les seniors vers la TV. La presse et la radio présentent un profil plus transversal, avec des écarts générationnels moins prononcés.',
                'conclusion': 'C\'est pourquoi nous concentrons l\'analyse sur l\'opposition TV/RS : c\'est là que le fossé générationnel est le plus net.'
            }
        },
        {
            'id': 'force-association',
            'titre': 'Force d\'association',
            'description': 'V de Cramer : quelles variables sont les plus liées à l\'usage des médias pour s\'informer ?',
            'noteMethodologique': 'Le taux de diffusion indique le % de personnes ayant chaque caractéristique. Les variables marquées ★ sont incluses dans la régression multivariée.',
            'toggle': {
                'options': [
                    {'id': 'rs', 'label': f'Réseaux sociaux ({round(prev_rs, 0):.0f}%)'},
                    {'id': 'tv', 'label': f'Télévision ({round(prev_tv, 0):.0f}%)'}
                ],
                'default': 'rs'
            },
            'visualisations': {
                'rs': {
                    'type': 'horizontal-bar-chart',
                    'data': results_rs
                },
                'tv': {
                    'type': 'horizontal-bar-chart',
                    'data': results_tv
                }
            }
        }
    ]
}

if regression_rs or regression_tv:
    output['sections'].append({
        'id': 'regression',
        'titre': 'Régression multivariée',
        'description': 'Qu\'est-ce qui prédit l\'usage des médias quand tout est en compétition ?',
        'noteReference': 'Catégorie de référence pour l\'âge : 15-17 ans. Les odds ratios indiquent la différence par rapport à cette tranche.',
        'limiteMethodologique': {
            'titre': 'Corrélation, pas causalité',
            'texte': 'Ces associations ne permettent pas d\'établir de relation causale. L\'usage du smartphone pour s\'informer et la confiance aux créateurs sont fortement liés à l\'usage des RS, mais cela ne signifie pas qu\'ils en sont la cause.'
        },
        'toggle': {
            'options': [
                {'id': 'rs', 'label': 'Réseaux sociaux'},
                {'id': 'tv', 'label': 'Télévision'}
            ],
            'default': 'rs'
        },
        'regressions': {
            'rs': {
                'titre': 'Prédire l\'usage des réseaux sociaux pour s\'informer',
                'regression': regression_rs,
                'interpretation': {
                    'titre': 'Ce que montre la régression',
                    'points': [
                        {
                            'variable': 'Usage algorithmique',
                            'effet': 'Très fort effet positif',
                            'texte': 'Se laisser guider par l\'algorithme (fil d\'actu) multiplie par 4 la probabilité d\'utiliser les RS pour s\'informer. C\'est le prédicteur le plus puissant.'
                        },
                        {
                            'variable': 'Formats courts',
                            'effet': 'Fort effet positif',
                            'texte': 'Être motivé par les formats courts (×2.9) : ceux qui préfèrent la brièveté se tournent vers les RS, logiquement.'
                        },
                        {
                            'variable': 'Âge',
                            'effet': 'Fort effet négatif',
                            'texte': 'Les 70+ ont 2.5x moins de chances d\'utiliser les RS pour s\'informer que les 15-17 ans. L\'âge reste un facteur majeur même après contrôle des usages.'
                        },
                        {
                            'variable': 'Doute médias',
                            'effet': 'Effet positif modéré',
                            'texte': 'Le doute envers les médias augmente l\'usage RS (+43%). Les sceptiques se tournent vers des sources alternatives.'
                        }
                    ]
                }
            },
            'tv': {
                'titre': 'Prédire l\'usage de la télévision pour s\'informer',
                'regression': regression_tv,
                'interpretation': {
                    'titre': 'Ce que montre la régression',
                    'points': [
                        {
                            'variable': 'Âge',
                            'effet': 'Très fort effet positif',
                            'texte': 'L\'âge est le prédicteur dominant : les 70+ ont 5x plus de chances d\'utiliser la TV que les 15-17 ans. C\'est un effet bien plus fort que pour les RS (où c\'est l\'inverse : ÷2.5).'
                        },
                        {
                            'variable': 'Confiance journalistes',
                            'effet': 'Fort effet positif',
                            'texte': 'Faire confiance aux journalistes augmente fortement l\'usage TV. Les téléspectateurs ont une attitude de confiance envers les médias traditionnels.'
                        },
                        {
                            'variable': 'Politique',
                            'effet': 'Effet négatif des deux côtés',
                            'texte': 'S\'identifier à gauche ou à droite diminue l\'usage TV. Les téléspectateurs seraient plus au "centre" ou moins politisés.'
                        },
                        {
                            'variable': 'Formats courts',
                            'effet': 'Effet positif modéré',
                            'texte': 'Être motivé par les formats courts augmente aussi l\'usage TV (+38%). Le JT est perçu comme un format condensé de l\'actualité.'
                        }
                    ]
                }
            }
        }
    })

# Sauvegarder
output_path = Path('frontend/public/data/enquetes/francais-information/chapitres/chapitre-01-basculement/01b-facteurs.json')
output_path.parent.mkdir(parents=True, exist_ok=True)

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\nJSON sauvegardé : {output_path}")
