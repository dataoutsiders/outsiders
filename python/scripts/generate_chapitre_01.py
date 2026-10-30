# -*- coding: utf-8 -*-
"""
Génération complète du Chapitre 01 : Le basculement numérique
Tous les JSON pour l'analyse Traditionnel vs Numérique
"""
import json
import pandas as pd
import numpy as np
from pathlib import Path
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# ============================================
# CONFIGURATION
# ============================================
BASE_DIR = Path(__file__).parent.parent.resolve()  # python/
DATA_DIR = BASE_DIR / 'data' / 'francais-information'
OUTPUT_DIR = Path(__file__).parent.parent.parent.resolve() / 'frontend' / 'public' / 'data' / 'enquetes' / 'francais-information' / 'chapitres' / 'chapitre-01-basculement'

# Créer le dossier de sortie
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================
# CHARGEMENT DES DONNÉES
# ============================================
print("Chargement des données...")
df = pd.read_excel(DATA_DIR / 'base-info-arcom.xlsx')
# Conversion des poids (format français avec virgules)
if df['POIDS03'].dtype == 'object':
    df['POIDS03'] = df['POIDS03'].str.replace(',', '.').astype(float)
else:
    df['POIDS03'] = pd.to_numeric(df['POIDS03'], errors='coerce').fillna(1)
print(f"Données chargées : {len(df)} observations")
print(f"Poids: min={df['POIDS03'].min():.2f}, max={df['POIDS03'].max():.2f}, sum={df['POIDS03'].sum():.0f}")

# ============================================
# LABELS
# ============================================
AGE_LABELS = {
    1: '15-17 ans', 2: '18-24 ans', 3: '25-34 ans', 4: '35-44 ans',
    5: '45-59 ans', 6: '60-69 ans', 7: '70 ans et +'
}

DIPLOME_LABELS = {
    1: 'Sans diplôme', 2: 'BEPC/Brevet', 3: 'CAP/BEP', 4: 'Bac',
    5: 'Bac+2', 6: 'Bac+3/4', 7: 'Bac+5 et +'
}

# ============================================
# CONSTRUCTION DE LA VARIABLE PRINCIPALE
# ============================================
print("\nConstruction de la variable Traditionnel/Numérique...")

# NEWS1BIS_R : source principale d'information
# NEWS1_1B_R : Support radio (1=poste/autoradio, 2=smartphone/ordi, 3=autre)
# NEWS1_2B_R : Support TV (1=poste TV, 2=smartphone/ordi)
# NEWS1_3B_R : Support presse (1=numérique, 2=papier)

# TRADITIONNEL PUR : TV/Radio/Presse sur support traditionnel
trad_tv = (df['NEWS1BIS_R'] == 2) & (df['NEWS1_2B_R'] == 1)
trad_radio = (df['NEWS1BIS_R'] == 1) & (df['NEWS1_1B_R'] == 1)
trad_presse = (df['NEWS1BIS_R'] == 3) & (df['NEWS1_3B_R'] == 2)
traditionnel_pur = trad_tv | trad_radio | trad_presse

# NUMÉRIQUE : Sources numériques OU médias trad sur support numérique
num_tv = (df['NEWS1BIS_R'] == 2) & (df['NEWS1_2B_R'] == 2)
num_radio = (df['NEWS1BIS_R'] == 1) & (df['NEWS1_1B_R'].isin([2, 3]))
num_presse = (df['NEWS1BIS_R'] == 3) & (df['NEWS1_3B_R'] == 1)
num_pure_player = (df['NEWS1BIS_R'] == 5)
num_moteur = (df['NEWS1BIS_R'] == 6)
num_portail = (df['NEWS1BIS_R'] == 7)
num_rs = (df['NEWS1BIS_R'] == 8)
num_youtube = (df['NEWS1BIS_R'] == 9)
numerique = num_tv | num_radio | num_presse | num_pure_player | num_moteur | num_portail | num_rs | num_youtube

# Variable binaire
df['BASCULEMENT'] = np.nan
df.loc[traditionnel_pur, 'BASCULEMENT'] = 0  # Traditionnel
df.loc[numerique, 'BASCULEMENT'] = 1  # Numérique

# Effectifs bruts
n_trad = traditionnel_pur.sum()
n_num = numerique.sum()
n_total = n_trad + n_num

# Pourcentages PONDÉRÉS (pour affichage)
poids_trad = df.loc[traditionnel_pur, 'POIDS03'].sum()
poids_num = df.loc[numerique, 'POIDS03'].sum()
poids_total = poids_trad + poids_num
pct_trad_pond = poids_trad / poids_total * 100
pct_num_pond = poids_num / poids_total * 100

print(f"Traditionnel: {n_trad} ({pct_trad_pond:.1f}% pondéré)")
print(f"Numérique: {n_num} ({pct_num_pond:.1f}% pondéré)")

# ============================================
# FONCTIONS UTILITAIRES
# ============================================

def cramers_v_weighted(x, y, weights):
    """Calcule le V de Cramer pondéré"""
    contingency = pd.crosstab(x, y, weights, aggfunc='sum').fillna(0)
    if contingency.shape[0] < 2 or contingency.shape[1] < 2:
        return 0, 0, 1
    chi2, p, dof, expected = stats.chi2_contingency(contingency)
    n = contingency.sum().sum()
    min_dim = min(contingency.shape) - 1
    if min_dim == 0 or n == 0:
        return 0, chi2, p
    v = np.sqrt(chi2 / (n * min_dim))
    return v, chi2, p

def get_distribution_by_var(df, var, vd='BASCULEMENT', weights='POIDS03', labels=None):
    """Calcule le % de numérique par modalité d'une variable"""
    mask = df[var].notna() & df[vd].notna()
    distribution = []

    for val in sorted(df.loc[mask, var].unique()):
        val_mask = mask & (df[var] == val)
        w = df.loc[val_mask, weights]
        y = df.loc[val_mask, vd]
        pct_num = (y * w).sum() / w.sum() * 100
        n = val_mask.sum()

        label = labels.get(int(val), str(int(val))) if labels else str(int(val))

        distribution.append({
            'category': label,
            'code': int(val),
            'pct_numerique': round(pct_num, 1),
            'pct_traditionnel': round(100 - pct_num, 1),
            'n': n
        })

    return distribution

def get_prevalence(df, var, weights='POIDS03'):
    """Calcule la prévalence d'une variable binaire"""
    mask = df[var].notna()
    w = df.loc[mask, weights]
    v = df.loc[mask, var]
    return round((v * w).sum() / w.sum() * 100, 1)

class NumpyEncoder(json.JSONEncoder):
    """Encodeur JSON pour les types numpy"""
    def default(self, obj):
        if isinstance(obj, (np.integer, np.int64, np.int32)):
            return int(obj)
        if isinstance(obj, (np.floating, np.float64, np.float32)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (np.bool_, bool)):
            return bool(obj)
        return super().default(obj)

def save_json(data, filename):
    """Sauvegarde un fichier JSON"""
    path = OUTPUT_DIR / filename
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, cls=NumpyEncoder)
    print(f"  -> {filename} sauvegarde")

# ============================================
# GÉNÉRATION DES JSON
# ============================================

# -----------------------------
# INDEX.JSON - Table des matières
# -----------------------------
print("\nGénération de index.json...")

index_data = {
    'id': 'chapitre-01',
    'titre': 'Le basculement numérique',
    'sousTitre': 'Comment les Français s\'informent-ils vraiment ?',
    'introduction': {
        'accroche': 'La moitié des Français s\'informe désormais principalement via des canaux numériques. Mais qui sont-ils ? Et qu\'est-ce qui distingue vraiment ceux qui ont "basculé" de ceux qui restent fidèles aux médias traditionnels ?',
        'contexte': 'À partir des données de l\'enquête ARCOM 2024, nous analysons les pratiques informationnelles de 3 346 Français pour comprendre les ressorts du basculement numérique.',
        'question': 'Qu\'est-ce qui différencie les "numériques" des "traditionnels" ? L\'âge est-il le seul facteur, ou d\'autres éléments entrent-ils en jeu ?'
    },
    'sommaire': [
        {
            'id': '01a-prenotions',
            'titre': 'Idées reçues',
            'description': 'Ce qu\'on croit savoir sur l\'information des jeunes',
            'icon': 'lightbulb'
        },
        {
            'id': '01b-variable-construite',
            'titre': 'Traditionnel vs Numérique',
            'description': 'Comment nous avons construit notre indicateur',
            'icon': 'build'
        },
        {
            'id': '01c-qui-bascule',
            'titre': 'Qui bascule ?',
            'description': 'Le profil socio-démographique des numériques',
            'icon': 'people'
        },
        {
            'id': '01d-ce-qui-accompagne',
            'titre': 'Ce qui accompagne le basculement',
            'description': 'Équipements, usages et valeurs',
            'icon': 'devices'
        },
        {
            'id': '01e-regression',
            'titre': 'Ce qui compte vraiment',
            'description': 'Régression multivariée : démêler les effets',
            'icon': 'analytics'
        },
        {
            'id': '01f-effets-stratifies',
            'titre': 'Effets différenciés',
            'description': 'L\'âge et le diplôme changent-ils la donne ?',
            'icon': 'layers'
        }
    ],
    'metadata': {
        'n_total': len(df),
        'n_analyse': n_total,
        'pct_numerique': round(pct_num_pond, 1),
        'pct_traditionnel': round(pct_trad_pond, 1)
    }
}

save_json(index_data, 'index.json')

# -----------------------------
# 01A - PRÉNOTIONS
# -----------------------------
print("\nGénération de 01a-prenotions.json...")

# Calculer quelques stats pour les prénotions
mask_jeunes = df['RS2C_RECODE_AG_R'].isin([1, 2, 3]) & df['BASCULEMENT'].notna()
pct_num_jeunes = (df.loc[mask_jeunes, 'BASCULEMENT'] * df.loc[mask_jeunes, 'POIDS03']).sum() / df.loc[mask_jeunes, 'POIDS03'].sum() * 100

mask_seniors = df['RS2C_RECODE_AG_R'].isin([6, 7]) & df['BASCULEMENT'].notna()
pct_num_seniors = (df.loc[mask_seniors, 'BASCULEMENT'] * df.loc[mask_seniors, 'POIDS03']).sum() / df.loc[mask_seniors, 'POIDS03'].sum() * 100

prenotions_data = {
    'id': '01a-prenotions',
    'titre': 'Idées reçues sur l\'information',
    'sousTitre': 'Ce que les données nous apprennent vraiment',
    'description': 'Avant de plonger dans les chiffres, confrontons quelques préjugés courants à la réalité des données.',
    'prenotions': {
        'titre': 'Vrai ou Faux ?',
        'items': [
            {
                'idee': 'Les jeunes ne s\'informent plus',
                'verdict': 'FAUX',
                'realite': f'Les jeunes s\'informent différemment : {pct_num_jeunes:.0f}% des 15-34 ans utilisent principalement des canaux numériques pour s\'informer. Ils n\'ont pas abandonné l\'information, ils ont changé de support.',
                'chiffre': {'valeur': f'{pct_num_jeunes:.0f}', 'unite': '%', 'label': 'des 15-34 ans sont "numériques"'}
            },
            {
                'idee': 'La télévision est morte',
                'verdict': 'FAUX',
                'realite': f'La TV reste la source principale d\'information pour {n_trad/n_total*100:.0f}% des Français, dont {100-pct_num_seniors:.0f}% des 60 ans et plus. Elle domine encore largement chez les seniors.',
                'chiffre': {'valeur': f'{100-pct_num_seniors:.0f}', 'unite': '%', 'label': 'des 60+ restent "traditionnels"'}
            },
            {
                'idee': 'Les réseaux sociaux ont tout remplacé',
                'verdict': 'NUANCÉ',
                'realite': 'Les RS sont la source principale pour seulement 13.5% des Français. Le "numérique" inclut aussi moteurs de recherche (11%), portails (9%), presse en ligne, YouTube... C\'est un écosystème diversifié.',
                'chiffre': {'valeur': '13.5', 'unite': '%', 'label': 'ont les RS comme source principale'}
            },
            {
                'idee': 'C\'est uniquement une question d\'âge',
                'verdict': 'NUANCÉ',
                'realite': 'L\'âge est le facteur le plus fort (V=0.37), mais le diplôme, les usages numériques et certaines valeurs jouent aussi un rôle significatif. Nous allons démêler tout cela.',
                'chiffre': {'valeur': '0.37', 'unite': '', 'label': 'V de Cramer âge/basculement'}
            }
        ]
    }
}

save_json(prenotions_data, '01a-prenotions.json')

# -----------------------------
# 01B - VARIABLE CONSTRUITE
# -----------------------------
print("\nGénération de 01b-variable-construite.json...")

# Composition détaillée de chaque groupe
composition_trad = [
    {'source': 'TV sur poste', 'n': int(trad_tv.sum()), 'pct': round(trad_tv.sum() / n_trad * 100, 1)},
    {'source': 'Radio sur poste/autoradio', 'n': int(trad_radio.sum()), 'pct': round(trad_radio.sum() / n_trad * 100, 1)},
    {'source': 'Presse papier', 'n': int(trad_presse.sum()), 'pct': round(trad_presse.sum() / n_trad * 100, 1)},
]

composition_num = [
    {'source': 'Réseaux sociaux', 'n': int(num_rs.sum()), 'pct': round(num_rs.sum() / n_num * 100, 1)},
    {'source': 'Moteur de recherche', 'n': int(num_moteur.sum()), 'pct': round(num_moteur.sum() / n_num * 100, 1)},
    {'source': 'Portail d\'actualité', 'n': int(num_portail.sum()), 'pct': round(num_portail.sum() / n_num * 100, 1)},
    {'source': 'Presse numérique', 'n': int(num_presse.sum()), 'pct': round(num_presse.sum() / n_num * 100, 1)},
    {'source': 'YouTube/Twitch', 'n': int(num_youtube.sum()), 'pct': round(num_youtube.sum() / n_num * 100, 1)},
    {'source': 'Pure players', 'n': int(num_pure_player.sum()), 'pct': round(num_pure_player.sum() / n_num * 100, 1)},
    {'source': 'Radio/podcast sur smartphone', 'n': int(num_radio.sum()), 'pct': round(num_radio.sum() / n_num * 100, 1)},
    {'source': 'TV sur smartphone/ordi', 'n': int(num_tv.sum()), 'pct': round(num_tv.sum() / n_num * 100, 1)},
]

# Trier par effectif décroissant
composition_trad.sort(key=lambda x: x['n'], reverse=True)
composition_num.sort(key=lambda x: x['n'], reverse=True)

# Distribution par âge
dist_age = get_distribution_by_var(df, 'RS2C_RECODE_AG_R', labels=AGE_LABELS)

variable_data = {
    'id': '01b-variable-construite',
    'titre': 'Traditionnel vs Numérique',
    'sousTitre': 'Construction de notre indicateur principal',
    'description': 'Pour analyser le basculement, nous avons créé une variable binaire à partir de la source principale d\'information ET du support utilisé.',

    'methodologie': {
        'titre': 'Comment nous avons construit la variable',
        'etapes': [
            {
                'numero': 1,
                'titre': 'Source principale',
                'texte': 'Quelle est votre source PRINCIPALE d\'information ? (question à choix unique)'
            },
            {
                'numero': 2,
                'titre': 'Support utilisé',
                'texte': 'Pour TV, radio et presse : sur quel support ? (poste/papier vs smartphone/ordinateur)'
            },
            {
                'numero': 3,
                'titre': 'Classification',
                'texte': 'Traditionnel = TV sur poste, radio sur poste/autoradio, presse papier. Numérique = tout le reste.'
            }
        ],
        'avantage': 'Cette approche évite l\'ambiguïté des usages mixtes et isole les vrais "traditionnels" des "numériques".'
    },

    'resultats': {
        'titre': 'Résultat : une population coupée en deux',
        'groupes': [
            {
                'id': 'traditionnel',
                'label': 'Traditionnels',
                'n': n_trad,
                'pct': round(pct_trad_pond, 1),
                'couleur': '#6366F1',
                'composition': composition_trad
            },
            {
                'id': 'numerique',
                'label': 'Numériques',
                'n': n_num,
                'pct': round(pct_num_pond, 1),
                'couleur': '#10B981',
                'composition': composition_num
            }
        ]
    },

    'metadata': {
        'n_total': n_total,
        'n_traditionnel': n_trad,
        'n_numerique': n_num
    }
}

save_json(variable_data, '01b-variable-construite.json')

# -----------------------------
# 01C - QUI BASCULE (SOCIO-DEMO)
# -----------------------------
print("\nGénération de 01c-qui-bascule.json...")

# Créer les variables socio-démo
df['AGE'] = df['RS2C_RECODE_AG_R']

# Genre (RS1_R : 1=Homme, 2=Femme)
GENRE_LABELS = {1: 'Homme', 2: 'Femme'}

# Situation professionnelle (RS3_R)
SITUATION_PRO_LABELS = {
    1: 'Actif à temps plein',
    2: 'Actif à temps partiel',
    3: 'Étudiant/Élève',
    4: 'Chômeur',
    5: 'Femme/Homme au foyer',
    6: 'Retraité',
    7: 'En incapacité',
    8: 'Autre inactif'
}

# CSP (RS4_R) - 7 modalités, pas de "Retraité" (c'est dans RS3_R)
CSP_LABELS = {
    1: 'Agriculteur',
    2: 'Artisan/Commerçant',
    3: 'Cadre/Prof. intel.',
    4: 'Prof. intermédiaire',
    5: 'Employé',
    6: 'Ouvrier',
    7: 'NSP/Refus'
}

# Diplôme regroupé en 3 catégories (RS5_R = niveau d'études)
# RS5_R: 1=Sans diplôme, 2=CEP, 3=BEPC/Brevet, 4=CAP/BEP, 5=Bac, 6=Bac+2, 7=Bac+3/4, 8=Bac+5, 9=Doctorat
def recode_diplome(rs5):
    if pd.isna(rs5): return np.nan
    if rs5 in [1, 2, 3, 4]: return 1    # Peu ou pas diplômé
    elif rs5 in [5, 6]: return 2         # Bac / Bac+2
    else: return 3                        # Bac+3 et plus

df['DIPLOME_REGROUPE'] = df['RS5_R'].apply(recode_diplome)
DIPLOME_REGROUPE_LABELS = {1: 'Peu ou pas diplômé', 2: 'Bac / Bac+2', 3: 'Bac+3 et plus'}

# Taille agglo (CC_R)
AGGLO_LABELS = {
    1: 'Commune rurale',
    2: '2 000 - 20 000 hab.',
    3: '20 000 - 100 000 hab.',
    4: '100 000 hab. et +',
    5: 'Agglo. parisienne'
}

# Revenu par personne (RS14_R / RS7_R) catégorisé en 3
def calc_revenu_par_personne(row):
    revenu = row.get('RS14_R')
    nb_pers = row.get('RS7_R')
    if pd.isna(revenu) or pd.isna(nb_pers) or nb_pers == 0:
        return np.nan
    # RS14_R : tranches de revenus (prendre le milieu de chaque tranche)
    revenu_midpoints = {
        1: 500,    # Moins de 1000€
        2: 1250,   # 1000-1499€
        3: 1750,   # 1500-1999€
        4: 2250,   # 2000-2499€
        5: 2750,   # 2500-2999€
        6: 3500,   # 3000-3999€
        7: 4500,   # 4000-4999€
        8: 5500,   # 5000-5999€
        9: 7000,   # 6000€ et +
    }
    rev_value = revenu_midpoints.get(int(revenu), np.nan)
    if pd.isna(rev_value):
        return np.nan
    return rev_value / nb_pers

df['REVENU_PAR_PERS'] = df.apply(calc_revenu_par_personne, axis=1)

# Catégoriser en terciles (basés sur les vrais percentiles)
q33 = df['REVENU_PAR_PERS'].quantile(0.33)
q66 = df['REVENU_PAR_PERS'].quantile(0.66)

def categorize_revenu(val):
    if pd.isna(val): return np.nan
    if val < q33: return 1       # Revenu -
    elif val < q66: return 2     # Revenu moyen
    else: return 3               # Revenu +

df['REVENU_CAT'] = df['REVENU_PAR_PERS'].apply(categorize_revenu)
REVENU_LABELS = {1: 'Revenu -', 2: 'Revenu moyen', 3: 'Revenu +'}

# Calculer V de Cramer pour chaque variable socio-démo
socio_vars = [
    ('AGE', 'Âge', AGE_LABELS),
    ('RS3_R', 'Situation pro.', SITUATION_PRO_LABELS),
    ('RS1_R', 'Genre', GENRE_LABELS),
    ('RS4_R', 'CSP', CSP_LABELS),
    ('DIPLOME_REGROUPE', 'Diplôme', DIPLOME_REGROUPE_LABELS),
    ('CC_R', 'Taille agglo', AGGLO_LABELS),
    ('REVENU_CAT', 'Revenu/pers.', REVENU_LABELS),
]

socio_results = []
for var, label, var_labels in socio_vars:
    if var not in df.columns:
        continue
    mask = df[var].notna() & df['BASCULEMENT'].notna()
    if mask.sum() < 100:
        continue

    v, chi2, p = cramers_v_weighted(df.loc[mask, var], df.loc[mask, 'BASCULEMENT'], df.loc[mask, 'POIDS03'])
    distribution = get_distribution_by_var(df, var, labels=var_labels)

    socio_results.append({
        'variable': label,
        'var_code': var,
        'v_cramer': round(v, 3),
        'chi2': round(chi2, 1),
        'p_value': p,
        'significatif': p < 0.05,
        'distribution': distribution
    })

# Trier par V de Cramer
socio_results.sort(key=lambda x: x['v_cramer'], reverse=True)

# ============================================
# RÉGRESSION LOGISTIQUE POUR PROBABILITÉS PRÉDITES
# ============================================
import statsmodels.api as sm

# Préparer les variables pour la régression
reg_df = df[['BASCULEMENT', 'POIDS03', 'AGE', 'RS1_R', 'RS3_R', 'RS4_R', 'DIPLOME_REGROUPE', 'CC_R', 'REVENU_CAT']].dropna().copy()

# Créer les dummies pour chaque modalité
# Âge : référence = 35-59 ans (codes 4, 5)
for i in range(1, 8):
    reg_df[f'AGE_{i}'] = (reg_df['AGE'] == i).astype(int)

# Genre : référence = Homme
reg_df['FEMME'] = (reg_df['RS1_R'] == 2).astype(int)

# Situation pro : on garde retraité comme variable clé
reg_df['RETRAITE'] = (reg_df['RS3_R'] == 6).astype(int)
reg_df['CHOMEUR'] = (reg_df['RS3_R'] == 4).astype(int)

# Diplôme : référence = Bac/Bac+2
reg_df['DIPLOME_BAS'] = (reg_df['DIPLOME_REGROUPE'] == 1).astype(int)
reg_df['DIPLOME_SUP'] = (reg_df['DIPLOME_REGROUPE'] == 3).astype(int)

# Taille agglo : référence = villes moyennes
reg_df['RURAL'] = (reg_df['CC_R'] == 1).astype(int)
reg_df['URBAIN'] = (reg_df['CC_R'].isin([4, 5])).astype(int)

# Revenu : référence = moyen
reg_df['REVENU_BAS'] = (reg_df['REVENU_CAT'] == 1).astype(int)
reg_df['REVENU_HAUT'] = (reg_df['REVENU_CAT'] == 3).astype(int)

# CSP : référence = Employé (le plus nombreux)
# RS4_R: 1=Agriculteur, 2=Artisan, 3=Cadre, 4=Prof.inter, 5=Employé, 6=Ouvrier, 7=NSP
reg_df['CSP_CADRE'] = (reg_df['RS4_R'] == 3).astype(int)
reg_df['CSP_OUVRIER'] = (reg_df['RS4_R'] == 6).astype(int)
reg_df['CSP_AGRICULTEUR'] = (reg_df['RS4_R'] == 1).astype(int)

# Variables pour la régression (contrôles) - toutes les variables socio-démo
control_vars = ['AGE_1', 'AGE_2', 'AGE_3', 'AGE_6', 'AGE_7', 'FEMME', 'RETRAITE',
                'DIPLOME_BAS', 'DIPLOME_SUP', 'RURAL', 'URBAIN',
                'REVENU_BAS', 'REVENU_HAUT', 'CSP_CADRE', 'CSP_OUVRIER']

X = reg_df[control_vars].astype(float)
X = sm.add_constant(X)
y = reg_df['BASCULEMENT'].astype(float)
weights = reg_df['POIDS03'].astype(float)

effect_cards_par_variable = []
effect_cards_regression = None

try:
    model = sm.GLM(y, X, family=sm.families.Binomial(), freq_weights=weights)
    results = model.fit()

    # Ordre des colonnes tel qu'utilisé dans le modèle
    model_columns = list(X.columns)

    # Fonction utilitaire pour créer un profil avec colonnes dans le bon ordre
    def make_profile(**kwargs):
        """Crée un DataFrame avec les colonnes dans l'ordre du modèle"""
        profile = {col: 0 for col in model_columns}
        profile['const'] = 1
        for k, v in kwargs.items():
            profile[k] = v
        return pd.DataFrame([[profile[col] for col in model_columns]], columns=model_columns)

    # Profil de référence (valeurs moyennes pour les contrôles)
    base_profile = {col: 0 for col in control_vars}
    base_profile['const'] = 1

    # ============================================
    # EFFECT CARDS PAR VARIABLE
    # ============================================

    # 1. ÂGE : 18-24 ans vs 70+ ans
    prob_jeune = results.predict(make_profile(AGE_2=1))[0] * 100
    prob_senior = results.predict(make_profile(AGE_7=1))[0] * 100
    ecart_age = prob_jeune - prob_senior

    # Test de significativité via p-value du coefficient
    p_age = min(results.pvalues.get('AGE_2', 1), results.pvalues.get('AGE_7', 1))

    if p_age < 0.05:
        # Calcul du ratio (plus numérique / moins numérique)
        ratio_age = prob_jeune / prob_senior if prob_senior > 0 else None
        effect_cards_par_variable.append({
            'variable': 'Âge',
            'var_code': 'AGE',
            'modalite_numerique': '18-24 ans',
            'modalite_traditionnelle': '70 ans et +',
            'prob_numerique': round(prob_jeune, 1),
            'prob_traditionnelle': round(prob_senior, 1),
            'ecart': round(ecart_age, 1),
            'ratio': round(ratio_age, 1) if ratio_age else None,
            'significatif': True,
            'couleur': '#EF4444'  # Rouge pour l'âge
        })

    # 2. SITUATION PRO : Actif vs Retraité
    prob_actif = results.predict(make_profile(RETRAITE=0))[0] * 100
    prob_retraite = results.predict(make_profile(RETRAITE=1))[0] * 100
    ecart_sitpro = prob_actif - prob_retraite

    p_retraite = results.pvalues.get('RETRAITE', 1)

    if p_retraite < 0.05:
        ratio_sitpro = prob_actif / prob_retraite if prob_retraite > 0 else None
        effect_cards_par_variable.append({
            'variable': 'Situation pro.',
            'var_code': 'RS3_R',
            'modalite_numerique': 'Actif (réf.)',
            'modalite_traditionnelle': 'Retraité',
            'prob_numerique': round(prob_actif, 1),
            'prob_traditionnelle': round(prob_retraite, 1),
            'ecart': round(ecart_sitpro, 1),
            'ratio': round(ratio_sitpro, 1) if ratio_sitpro else None,
            'significatif': True,
            'couleur': '#F59E0B'  # Orange
        })

    # 3. DIPLÔME : Bac+3+ vs Peu diplômé
    prob_diplome_sup = results.predict(make_profile(DIPLOME_SUP=1))[0] * 100
    prob_diplome_bas = results.predict(make_profile(DIPLOME_BAS=1))[0] * 100
    ecart_diplome = prob_diplome_sup - prob_diplome_bas

    p_diplome = min(results.pvalues.get('DIPLOME_SUP', 1), results.pvalues.get('DIPLOME_BAS', 1))

    if p_diplome < 0.05:
        ratio_diplome = prob_diplome_sup / prob_diplome_bas if prob_diplome_bas > 0 else None
        effect_cards_par_variable.append({
            'variable': 'Diplôme',
            'var_code': 'DIPLOME_REGROUPE',
            'modalite_numerique': 'Bac+3 et plus',
            'modalite_traditionnelle': 'Peu diplômé',
            'prob_numerique': round(prob_diplome_sup, 1),
            'prob_traditionnelle': round(prob_diplome_bas, 1),
            'ecart': round(ecart_diplome, 1),
            'ratio': round(ratio_diplome, 1) if ratio_diplome else None,
            'significatif': True,
            'couleur': '#8B5CF6'  # Violet
        })

    # 4. TAILLE AGGLO : Urbain vs Rural
    prob_urbain = results.predict(make_profile(URBAIN=1))[0] * 100
    prob_rural = results.predict(make_profile(RURAL=1))[0] * 100
    ecart_agglo = prob_urbain - prob_rural

    p_agglo = min(results.pvalues.get('URBAIN', 1), results.pvalues.get('RURAL', 1))

    if p_agglo < 0.05:
        # S'assurer que la modalité "numérique" a bien la probabilité la plus haute
        if prob_urbain >= prob_rural:
            ratio_agglo = prob_urbain / prob_rural if prob_rural > 0 else None
            effect_cards_par_variable.append({
                'variable': 'Taille agglo',
                'var_code': 'CC_R',
                'modalite_numerique': 'Grande ville',
                'modalite_traditionnelle': 'Rural',
                'prob_numerique': round(prob_urbain, 1),
                'prob_traditionnelle': round(prob_rural, 1),
                'ecart': round(abs(ecart_agglo), 1),
                'ratio': round(ratio_agglo, 1) if ratio_agglo else None,
                'significatif': True,
                'couleur': '#3B82F6'  # Bleu
            })
        else:
            # Inverser si rural > urbain (effet de suppression - ne devrait pas arriver)
            ratio_agglo = prob_rural / prob_urbain if prob_urbain > 0 else None
            effect_cards_par_variable.append({
                'variable': 'Taille agglo',
                'var_code': 'CC_R',
                'modalite_numerique': 'Rural',
                'modalite_traditionnelle': 'Grande ville',
                'prob_numerique': round(prob_rural, 1),
                'prob_traditionnelle': round(prob_urbain, 1),
                'ecart': round(abs(ecart_agglo), 1),
                'ratio': round(ratio_agglo, 1) if ratio_agglo else None,
                'significatif': True,
                'couleur': '#3B82F6'  # Bleu
            })

    # 5. GENRE : Homme vs Femme
    prob_homme = results.predict(make_profile(FEMME=0))[0] * 100
    prob_femme = results.predict(make_profile(FEMME=1))[0] * 100
    ecart_genre = prob_homme - prob_femme

    p_genre = results.pvalues.get('FEMME', 1)

    if p_genre < 0.05:
        ratio_genre = prob_homme / prob_femme if prob_femme > 0 else None
        effect_cards_par_variable.append({
            'variable': 'Genre',
            'var_code': 'RS1_R',
            'modalite_numerique': 'Homme',
            'modalite_traditionnelle': 'Femme',
            'prob_numerique': round(prob_homme, 1),
            'prob_traditionnelle': round(prob_femme, 1),
            'ecart': round(ecart_genre, 1),
            'ratio': round(ratio_genre, 1) if ratio_genre else None,
            'significatif': True,
            'couleur': '#EC4899'  # Rose
        })

    # 6. REVENU : Haut vs Bas
    prob_revenu_haut = results.predict(make_profile(REVENU_HAUT=1))[0] * 100
    prob_revenu_bas = results.predict(make_profile(REVENU_BAS=1))[0] * 100
    ecart_revenu = prob_revenu_haut - prob_revenu_bas

    p_revenu = min(results.pvalues.get('REVENU_HAUT', 1), results.pvalues.get('REVENU_BAS', 1))

    if p_revenu < 0.05:
        if prob_revenu_haut >= prob_revenu_bas:
            ratio_revenu = prob_revenu_haut / prob_revenu_bas if prob_revenu_bas > 0 else None
            effect_cards_par_variable.append({
                'variable': 'Revenu',
                'var_code': 'REVENU_CAT',
                'modalite_numerique': 'Revenu élevé',
                'modalite_traditionnelle': 'Revenu faible',
                'prob_numerique': round(prob_revenu_haut, 1),
                'prob_traditionnelle': round(prob_revenu_bas, 1),
                'ecart': round(abs(ecart_revenu), 1),
                'ratio': round(ratio_revenu, 1) if ratio_revenu else None,
                'significatif': True,
                'couleur': '#14B8A6'  # Teal
            })
        else:
            ratio_revenu = prob_revenu_bas / prob_revenu_haut if prob_revenu_haut > 0 else None
            effect_cards_par_variable.append({
                'variable': 'Revenu',
                'var_code': 'REVENU_CAT',
                'modalite_numerique': 'Revenu faible',
                'modalite_traditionnelle': 'Revenu élevé',
                'prob_numerique': round(prob_revenu_bas, 1),
                'prob_traditionnelle': round(prob_revenu_haut, 1),
                'ecart': round(abs(ecart_revenu), 1),
                'ratio': round(ratio_revenu, 1) if ratio_revenu else None,
                'significatif': True,
                'couleur': '#14B8A6'  # Teal
            })

    # 7. CSP : Cadre vs Ouvrier
    prob_cadre = results.predict(make_profile(CSP_CADRE=1))[0] * 100
    prob_ouvrier = results.predict(make_profile(CSP_OUVRIER=1))[0] * 100
    ecart_csp = prob_cadre - prob_ouvrier

    p_csp = min(results.pvalues.get('CSP_CADRE', 1), results.pvalues.get('CSP_OUVRIER', 1))

    if p_csp < 0.05:
        if prob_cadre >= prob_ouvrier:
            ratio_csp = prob_cadre / prob_ouvrier if prob_ouvrier > 0 else None
            effect_cards_par_variable.append({
                'variable': 'CSP',
                'var_code': 'RS4_R',
                'modalite_numerique': 'Cadre',
                'modalite_traditionnelle': 'Ouvrier',
                'prob_numerique': round(prob_cadre, 1),
                'prob_traditionnelle': round(prob_ouvrier, 1),
                'ecart': round(abs(ecart_csp), 1),
                'ratio': round(ratio_csp, 1) if ratio_csp else None,
                'significatif': True,
                'couleur': '#F97316'  # Orange
            })
        else:
            ratio_csp = prob_ouvrier / prob_cadre if prob_cadre > 0 else None
            effect_cards_par_variable.append({
                'variable': 'CSP',
                'var_code': 'RS4_R',
                'modalite_numerique': 'Ouvrier',
                'modalite_traditionnelle': 'Cadre',
                'prob_numerique': round(prob_ouvrier, 1),
                'prob_traditionnelle': round(prob_cadre, 1),
                'ecart': round(abs(ecart_csp), 1),
                'ratio': round(ratio_csp, 1) if ratio_csp else None,
                'significatif': True,
                'couleur': '#F97316'  # Orange
            })

    # Trier par écart décroissant
    effect_cards_par_variable.sort(key=lambda x: abs(x['ecart']), reverse=True)

    # ============================================
    # MULTI-PROFIL (profils extrêmes combinés)
    # ============================================
    # Profil "Numérique typique" : jeune, urbain, cadre
    prob_num = results.predict(make_profile(AGE_2=1, CSP_CADRE=1, URBAIN=1))[0] * 100

    # Profil "Traditionnel typique" : senior, rural (pas de CSP car retraité)
    prob_trad = results.predict(make_profile(AGE_7=1, RURAL=1))[0] * 100

    # Profil de référence (35-59, ville moyenne, employé) = tous à 0
    prob_moyen = results.predict(make_profile())[0] * 100

    effect_cards_regression = {
        'titre': 'Profils combinés',
        'description': 'Probabilité d\'être numérique en combinant toutes les caractéristiques',
        'cards': [
            {
                'id': 'profil_numerique',
                'label': 'Jeune urbain cadre',
                'description': '18-24 ans, grande ville, cadre',
                'probabilite': round(prob_num, 1),
                'groupe': 'numerique',
                'couleur': '#10B981'
            },
            {
                'id': 'profil_moyen',
                'label': 'Profil de référence',
                'description': '35-59 ans, ville moyenne, employé',
                'probabilite': round(prob_moyen, 1),
                'groupe': 'mixte',
                'couleur': '#6B7280'
            },
            {
                'id': 'profil_traditionnel',
                'label': 'Senior rural',
                'description': '70+ ans, zone rurale',
                'probabilite': round(prob_trad, 1),
                'groupe': 'traditionnel',
                'couleur': '#6366F1'
            }
        ],
        'ecart_max': round(prob_num - prob_trad, 1)
    }

    # Debug: afficher les coefficients
    print("  Coefficients de la régression:")
    for var, coef in results.params.items():
        pval = results.pvalues[var]
        sig = '***' if pval < 0.001 else '**' if pval < 0.01 else '*' if pval < 0.05 else ''
        print(f"    {var:15} {coef:+.3f} (p={pval:.4f}) {sig}")

    print(f"\n  Probabilités multi-profil:")
    print(f"    Jeune urbain cadre: {prob_num:.1f}%")
    print(f"    Profil référence: {prob_moyen:.1f}%")
    print(f"    Senior rural ouvrier: {prob_trad:.1f}%")

    print(f"\n  Effect cards générées: {len(effect_cards_par_variable)} variables significatives")
    for card in effect_cards_par_variable:
        print(f"    {card['variable']}: {card['modalite_numerique']} ({card['prob_numerique']}%) vs {card['modalite_traditionnelle']} ({card['prob_traditionnelle']}%) = x{card['ratio']}")

except Exception as e:
    print(f"  Erreur régression profils: {e}")
    import traceback
    traceback.print_exc()
    effect_cards_regression = None
    effect_cards_par_variable = []

# Créer les options de toggle pour les distributions (triées par V de Cramer)
distribution_options = []
for r in socio_results:
    distribution_options.append({
        'id': r['var_code'],
        'label': r['variable'],
        'v_cramer': r['v_cramer']
    })

# Créer un dictionnaire des distributions par variable
distributions_by_var = {}
for r in socio_results:
    distributions_by_var[r['var_code']] = {
        'type': 'distribution_bar',
        'titre': f'% Numérique par {r["variable"].lower()}',
        'data': r['distribution'],
        'v_cramer': r['v_cramer'],
        'significatif': r['significatif']
    }

# Construire les sections
sections_qui_bascule = [
    {
        'id': 'force-association-socio',
        'titre': 'Force d\'association',
        'description': 'V de Cramer : quelles variables socio-démographiques sont les plus liées au basculement ?',
        'visualisations': [
            {
                'type': 'horizontal-bar-chart',
                'data': [
                    {
                        'variable': r['variable'],
                        'v_cramer': r['v_cramer'],
                        'significatif': r['significatif']
                    } for r in socio_results
                ]
            }
        ]
    },
    {
        'id': 'detail-par-variable',
        'titre': 'Détail par variable',
        'description': 'Explorez la distribution Numérique/Traditionnel pour chaque variable socio-démographique.',
        'toggle': {
            'default': socio_results[0]['var_code'],
            'options': distribution_options
        },
        'visualisations': distributions_by_var
    }
]

# Ajouter les effect cards par variable si disponibles (AVANT le multi-profil)
if effect_cards_par_variable:
    sections_qui_bascule.append({
        'id': 'effets-nets-par-variable',
        'titre': 'Effet net par variable',
        'description': 'Probabilité d\'être numérique pour les modalités extrêmes de chaque variable, toutes choses égales par ailleurs.',
        'visualisations': [
            {
                'type': 'effect_cards_par_variable',
                'data': effect_cards_par_variable
            }
        ],
        'noteMethodologique': {
            'titre': 'Effet net',
            'texte': 'Les probabilités sont calculées à partir d\'une régression logistique qui isole l\'effet de chaque variable en contrôlant les autres. Le ratio indique combien de fois plus probable est le basculement numérique pour la modalité la plus "numérique" par rapport à la plus "traditionnelle".'
        }
    })

# Ajouter le multi-profil (APRÈS les cards par variable)
if effect_cards_regression:
    # Calcul du ratio pour le multi-profil
    prob_max = effect_cards_regression['cards'][0]['probabilite']  # Jeune urbain cadre
    prob_min = effect_cards_regression['cards'][2]['probabilite']  # Senior rural ouvrier
    ratio_profils = round(prob_max / prob_min, 1) if prob_min > 0 else None

    sections_qui_bascule.append({
        'id': 'probabilites-predites',
        'titre': 'Les profils combinés les plus opposés',
        'description': 'Probabilité d\'être numérique en combinant toutes les caractéristiques socio-démographiques.',
        'visualisations': [
            {
                'type': 'effect_cards_profils',
                'titre': effect_cards_regression['titre'],
                'description': effect_cards_regression['description'],
                'data': effect_cards_regression['cards'],
                'ecart_max': effect_cards_regression['ecart_max'],
                'ratio_max': ratio_profils
            }
        ],
        'insight': f'À caractéristiques contrôlées, un jeune urbain cadre a {ratio_profils}x plus de chances d\'être numérique qu\'un senior rural.'
    })

qui_bascule_data = {
    'id': '01c-qui-bascule',
    'titre': 'Qui bascule ?',
    'sousTitre': 'Le profil socio-démographique des numériques',
    'description': 'Quelles caractéristiques sociales sont les plus associées au basculement numérique ?',

    'noteMethodologique': {
        'titre': 'Comment lire le V de Cramer',
        'texte': 'Le V de Cramer mesure la force du lien entre deux variables (0 = aucun lien, 1 = lien parfait). Un V > 0.3 indique une association forte, 0.15-0.3 une association modérée, < 0.15 une association faible.'
    },

    'sections': sections_qui_bascule,

    'synthese': {
        'titre': 'En résumé',
        'points': [
            f'L\'âge est le facteur le plus fortement associé au basculement (V={socio_results[0]["v_cramer"]:.2f}).',
            f'La situation professionnelle est également discriminante (V={[r for r in socio_results if r["var_code"]=="RS3_R"][0]["v_cramer"]:.2f}), notamment le statut de retraité.',
            'Le diplôme, la CSP et le revenu jouent un rôle plus modéré.',
            'Le genre n\'a pas d\'effet significatif sur le basculement : être homme ou femme ne change pas la probabilité d\'être numérique.'
        ]
    },

    'metadata': {
        'variables_analysees': len(socio_results),
        'socio_results': socio_results,
        'effect_cards_regression': effect_cards_regression
    }
}

save_json(qui_bascule_data, '01c-qui-bascule.json')

# -----------------------------
# 01D - CE QUI ACCOMPAGNE
# -----------------------------
print("\nGénération de 01d-ce-qui-accompagne.json...")

# Créer les variables d'équipement, usages, valeurs
# ÉQUIPEMENT
device_cols = [c for c in df.columns if c.startswith('DEVICEXMOMENTS_R_')]
df['EQUIP_SMARTPHONE'] = df.apply(lambda r: 1 if any(pd.notna(r[c]) and r[c] == 1 for c in device_cols) else 0, axis=1)
df['EQUIP_TABLETTE'] = df.apply(lambda r: 1 if any(pd.notna(r[c]) and r[c] == 2 for c in device_cols) else 0, axis=1)
df['EQUIP_ORDI'] = df.apply(lambda r: 1 if any(pd.notna(r[c]) and r[c] == 3 for c in device_cols) else 0, axis=1)

# USAGES RS
rsinfo_cols = [c for c in df.columns if c.startswith('RSINFO_1_LR_R_')]
df['USAGE_ALGO'] = df.apply(lambda r: 1 if any(pd.notna(r[c]) and r[c] == 2 for c in rsinfo_cols) else 0, axis=1)
df['USAGE_TEMPS_REEL'] = df.apply(lambda r: 1 if any(pd.notna(r[c]) and r[c] == 1 for c in rsinfo_cols) else 0, axis=1)
df['USAGE_RECHERCHE'] = df.apply(lambda r: 1 if any(pd.notna(r[c]) and r[c] == 3 for c in rsinfo_cols) else 0, axis=1)

# MOTIVATIONS RS
motiv_cols = [c for c in df.columns if c.startswith('MOTIVRS_R_')]
df['MOTIV_FACILITE'] = df.apply(lambda r: 1 if any(pd.notna(r[c]) and r[c] == 1 for c in motiv_cols) else 0, axis=1)
df['MOTIV_FORMATS_COURTS'] = df.apply(lambda r: 1 if any(pd.notna(r[c]) and r[c] == 5 for c in motiv_cols) else 0, axis=1)
df['MOTIV_TEMPS_PASSE'] = df.apply(lambda r: 1 if any(pd.notna(r[c]) and r[c] == 8 for c in motiv_cols) else 0, axis=1)
df['MOTIV_COMMENTER'] = df.apply(lambda r: 1 if any(pd.notna(r[c]) and r[c] == 10 for c in motiv_cols) else 0, axis=1)

# VALEURS
df['POL_GAUCHE'] = (df['NOU1_R'].isin([1, 2])).astype(int)
df['POL_DROITE'] = (df['NOU1_R'].isin([6, 7])).astype(int)
df['DOUTE_MEDIAS'] = (df['DOUTE_R'] == 1).astype(int)

# CONFIANCE
inf3_cols = [c for c in df.columns if c.startswith('INF3_R1_')]
df['CONF_JOURNALISTES'] = df.apply(lambda r: 1 if any(pd.notna(r[c]) and r[c] == 1 for c in inf3_cols) else 0, axis=1)
df['CONF_CREATEURS'] = df.apply(lambda r: 1 if any(pd.notna(r[c]) and r[c] == 6 for c in inf3_cols) else 0, axis=1)
df['CONF_PROCHES'] = df.apply(lambda r: 1 if any(pd.notna(r[c]) and r[c] == 9 for c in inf3_cols) else 0, axis=1)

# Variables à analyser
variables_accompagnement = [
    # Équipement
    ('EQUIP_SMARTPHONE', 'Smartphone pour s\'informer', 'Équipement'),
    ('EQUIP_TABLETTE', 'Tablette pour s\'informer', 'Équipement'),
    ('EQUIP_ORDI', 'Ordinateur pour s\'informer', 'Équipement'),
    # Usages
    ('USAGE_ALGO', 'Fil d\'actu algorithmique', 'Usage'),
    ('USAGE_TEMPS_REEL', 'Info en temps réel', 'Usage'),
    ('USAGE_RECHERCHE', 'Recherche active', 'Usage'),
    ('MOTIV_FACILITE', 'Motivation: facilité', 'Usage'),
    ('MOTIV_FORMATS_COURTS', 'Motivation: formats courts', 'Usage'),
    ('MOTIV_TEMPS_PASSE', 'Motivation: temps passé sur RS', 'Usage'),
    ('MOTIV_COMMENTER', 'Motivation: commenter', 'Usage'),
    # Valeurs
    ('POL_GAUCHE', 'Orientation gauche', 'Valeurs'),
    ('POL_DROITE', 'Orientation droite', 'Valeurs'),
    ('DOUTE_MEDIAS', 'Doute envers médias', 'Valeurs'),
    ('CONF_JOURNALISTES', 'Confiance journalistes', 'Valeurs'),
    ('CONF_CREATEURS', 'Confiance créateurs', 'Valeurs'),
    ('CONF_PROCHES', 'Confiance proches', 'Valeurs'),
]

GROUPE_COLORS = {
    'Équipement': '#F59E0B',
    'Usage': '#10B981',
    'Valeurs': '#EC4899',
}

accompagnement_results = []
for var, label, groupe in variables_accompagnement:
    if var not in df.columns:
        continue
    mask = df[var].notna() & df['BASCULEMENT'].notna()
    if mask.sum() < 100:
        continue

    v, chi2, p = cramers_v_weighted(df.loc[mask, var], df.loc[mask, 'BASCULEMENT'], df.loc[mask, 'POIDS03'])
    prevalence = get_prevalence(df, var)

    # Distribution (0/1 -> Trad/Num)
    distribution = []
    for val in [0, 1]:
        val_mask = mask & (df[var] == val)
        if val_mask.sum() > 0:
            pct_num = (df.loc[val_mask, 'BASCULEMENT'] * df.loc[val_mask, 'POIDS03']).sum() / df.loc[val_mask, 'POIDS03'].sum() * 100
            distribution.append({
                'category': 'Oui' if val == 1 else 'Non',
                'pct_numerique': round(pct_num, 1)
            })

    accompagnement_results.append({
        'variable': label,
        'var_code': var,
        'groupe': groupe,
        'v_cramer': round(v, 3),
        'prevalence': prevalence,
        'distribution': distribution,
        'color': GROUPE_COLORS.get(groupe, '#6b7280'),
        'significatif': p < 0.05
    })

# Trier par V de Cramer
accompagnement_results.sort(key=lambda x: x['v_cramer'], reverse=True)

ce_qui_accompagne_data = {
    'id': '01d-ce-qui-accompagne',
    'titre': 'Ce qui accompagne le basculement',
    'sousTitre': 'Équipements, usages et valeurs',
    'description': 'Au-delà du profil socio-démographique, quels comportements et attitudes distinguent les numériques des traditionnels ?',

    'sections': [
        {
            'id': 'force-association',
            'titre': 'Force d\'association',
            'description': 'V de Cramer : quelles variables sont les plus liées au basculement ?',
            'noteMethodologique': 'Le taux de diffusion indique le % de personnes ayant chaque caractéristique dans l\'ensemble de la population.',
            'visualisations': [
                {
                    'type': 'horizontal-bar-chart',
                    'data': accompagnement_results
                }
            ]
        }
    ],

    'synthese': {
        'titre': 'Ce que ces associations nous apprennent',
        'points': [
            {
                'titre': 'L\'usage prime sur l\'équipement',
                'texte': 'Ce n\'est pas tant le fait d\'avoir un smartphone qui compte, mais la façon dont on l\'utilise pour s\'informer.'
            },
            {
                'titre': 'L\'algorithme au cœur du basculement',
                'texte': 'Se laisser guider par le fil d\'actualité algorithmique est fortement associé au profil numérique.'
            },
            {
                'titre': 'Des valeurs différentes',
                'texte': 'Les numériques font moins confiance aux journalistes et davantage aux créateurs de contenu.'
            }
        ]
    },

    'metadata': {
        'variables_analysees': len(accompagnement_results)
    }
}

save_json(ce_qui_accompagne_data, '01d-ce-qui-accompagne.json')

# -----------------------------
# 01E - RÉGRESSION
# -----------------------------
print("\nGénération de 01e-regression.json...")

try:
    import statsmodels.api as sm

    # Variables pour la régression
    reg_vars = [
        'AGE',
        'DIPLOME_REGROUPE',
        'EQUIP_SMARTPHONE',
        'USAGE_ALGO',
        'USAGE_TEMPS_REEL',
        'MOTIV_FORMATS_COURTS',
        'DOUTE_MEDIAS',
        'CONF_CREATEURS',
        'CONF_JOURNALISTES',
    ]

    # Filtrer données complètes
    reg_df = df[['BASCULEMENT', 'POIDS03'] + reg_vars].dropna()
    print(f"  Observations pour régression : {len(reg_df)}")

    if len(reg_df) > 200:
        # Préparer X avec dummies
        X = reg_df[reg_vars].copy()
        X = pd.get_dummies(X, columns=['AGE', 'DIPLOME_REGROUPE'], drop_first=True)
        X = X.astype(float)
        X = sm.add_constant(X)

        y = reg_df['BASCULEMENT'].astype(float)
        weights = reg_df['POIDS03'].astype(float)

        # Régression
        model = sm.GLM(y, X, family=sm.families.Binomial(), freq_weights=weights)
        result = model.fit()

        # Extraire coefficients
        coefs = result.summary2().tables[1]

        regression_results = {
            'n_obs': len(reg_df),
            'pseudo_r2': round(float(result.pseudo_rsquared()), 3),
            'coefficients': []
        }

        # Labels lisibles
        var_labels = {
            'EQUIP_SMARTPHONE': 'Smartphone pour s\'informer',
            'USAGE_ALGO': 'Fil d\'actu algorithmique',
            'USAGE_TEMPS_REEL': 'Info en temps réel',
            'MOTIV_FORMATS_COURTS': 'Formats courts',
            'DOUTE_MEDIAS': 'Doute envers médias',
            'CONF_CREATEURS': 'Confiance créateurs',
            'CONF_JOURNALISTES': 'Confiance journalistes',
            'AGE_2.0': 'Âge: 18-24 ans',
            'AGE_3.0': 'Âge: 25-34 ans',
            'AGE_4.0': 'Âge: 35-44 ans',
            'AGE_5.0': 'Âge: 45-59 ans',
            'AGE_6.0': 'Âge: 60-69 ans',
            'AGE_7.0': 'Âge: 70 ans et +',
            'DIPLOME_REGROUPE_2.0': 'Diplôme: Bac à Bac+2',
            'DIPLOME_REGROUPE_3.0': 'Diplôme: Bac+3 et +',
        }

        for var in coefs.index:
            if var != 'const':
                coef = float(coefs.loc[var, 'Coef.'])
                pval = float(coefs.loc[var, 'P>|z|'])

                regression_results['coefficients'].append({
                    'variable': var,
                    'label': var_labels.get(var, var),
                    'coef': round(coef, 3),
                    'odds_ratio': round(np.exp(coef), 2),
                    'p_value': round(pval, 4),
                    'significatif': pval < 0.05
                })

        # Trier par odds ratio
        regression_results['coefficients'].sort(key=lambda x: abs(x['coef']), reverse=True)

except Exception as e:
    print(f"  Erreur régression : {e}")
    regression_results = None

regression_data = {
    'id': '01e-regression',
    'titre': 'Ce qui compte vraiment',
    'sousTitre': 'Régression multivariée',
    'description': 'Quand on met toutes les variables en compétition, lesquelles prédisent vraiment le basculement numérique ?',

    'noteMethodologique': {
        'titre': 'Comment lire les odds ratios',
        'texte': 'Un odds ratio > 1 signifie que la variable augmente la probabilité d\'être "numérique". Un OR < 1 la diminue. Exemple : OR = 2 signifie que la probabilité est doublée.',
        'reference': 'Catégorie de référence : 15-17 ans pour l\'âge, Sans Bac pour le diplôme.'
    },

    'sections': [
        {
            'id': 'regression-results',
            'titre': 'Résultats de la régression',
            'regression': regression_results,
        }
    ],

    'interpretation': {
        'titre': 'Ce que montre la régression',
        'points': [
            {
                'variable': 'Âge',
                'effet': 'Fort effet négatif',
                'texte': 'Même en contrôlant les usages et valeurs, l\'âge reste le facteur dominant. Les 70+ ont beaucoup moins de chances d\'être numériques que les 15-17 ans.'
            },
            {
                'variable': 'Usage algorithmique',
                'effet': 'Fort effet positif',
                'texte': 'Se laisser guider par l\'algorithme multiplie fortement la probabilité d\'être numérique.'
            },
            {
                'variable': 'Confiance créateurs',
                'effet': 'Effet positif',
                'texte': 'Faire confiance aux créateurs de contenu plutôt qu\'aux journalistes est associé au profil numérique.'
            }
        ]
    },

    'limiteMethodologique': {
        'titre': 'Corrélation, pas causalité',
        'texte': 'Ces associations ne permettent pas d\'établir de relation causale. L\'usage de l\'algorithme et le basculement numérique vont ensemble, mais on ne peut pas dire que l\'un cause l\'autre.'
    }
}

save_json(regression_data, '01e-regression.json')

# -----------------------------
# 01F - EFFETS STRATIFIÉS
# -----------------------------
print("\nGénération de 01f-effets-stratifies.json...")

# Variables à stratifier
strat_vars = [
    ('EQUIP_SMARTPHONE', 'Smartphone'),
    ('USAGE_ALGO', 'Fil d\'actu algo'),
    ('USAGE_TEMPS_REEL', 'Info temps réel'),
    ('MOTIV_FORMATS_COURTS', 'Formats courts'),
    ('CONF_CREATEURS', 'Confiance créateurs'),
    ('CONF_JOURNALISTES', 'Confiance journalistes'),
    ('DOUTE_MEDIAS', 'Doute médias'),
]

# Strates d'âge
AGE_STRATES = {
    'jeunes': {'codes': [1, 2, 3], 'label': '15-34 ans'},
    'milieu': {'codes': [4, 5], 'label': '35-59 ans'},
    'seniors': {'codes': [6, 7], 'label': '60 ans et +'},
}

# Strates de diplôme
DIPLOME_STRATES = {
    'sans_bac': {'codes': [1], 'label': 'Sans Bac'},
    'bac_bac2': {'codes': [2], 'label': 'Bac à Bac+2'},
    'bac3_plus': {'codes': [3], 'label': 'Bac+3 et +'},
}

stratifie_cards = []

# Stratification par âge
for var, var_label in strat_vars:
    for strate_key, strate_info in AGE_STRATES.items():
        mask = df['AGE'].isin(strate_info['codes']) & df[var].notna() & df['BASCULEMENT'].notna()
        if mask.sum() < 50:
            continue

        v, chi2, p = cramers_v_weighted(df.loc[mask, var], df.loc[mask, 'BASCULEMENT'], df.loc[mask, 'POIDS03'])

        # % numérique si var=1
        var1_mask = mask & (df[var] == 1)
        var0_mask = mask & (df[var] == 0)

        if var1_mask.sum() > 0 and var0_mask.sum() > 0:
            pct_num_oui = (df.loc[var1_mask, 'BASCULEMENT'] * df.loc[var1_mask, 'POIDS03']).sum() / df.loc[var1_mask, 'POIDS03'].sum() * 100
            pct_num_non = (df.loc[var0_mask, 'BASCULEMENT'] * df.loc[var0_mask, 'POIDS03']).sum() / df.loc[var0_mask, 'POIDS03'].sum() * 100
            ecart = pct_num_oui - pct_num_non

            stratifie_cards.append({
                'variable': var_label,
                'var_code': var,
                'strate_type': 'age',
                'strate_key': strate_key,
                'strate_label': strate_info['label'],
                'v_cramer': round(v, 3),
                'pct_num_oui': round(pct_num_oui, 1),
                'pct_num_non': round(pct_num_non, 1),
                'ecart': round(ecart, 1),
                'n': mask.sum(),
                'significatif': p < 0.05
            })

# Stratification par diplôme
for var, var_label in strat_vars:
    for strate_key, strate_info in DIPLOME_STRATES.items():
        mask = df['DIPLOME_REGROUPE'].isin(strate_info['codes']) & df[var].notna() & df['BASCULEMENT'].notna()
        if mask.sum() < 50:
            continue

        v, chi2, p = cramers_v_weighted(df.loc[mask, var], df.loc[mask, 'BASCULEMENT'], df.loc[mask, 'POIDS03'])

        var1_mask = mask & (df[var] == 1)
        var0_mask = mask & (df[var] == 0)

        if var1_mask.sum() > 0 and var0_mask.sum() > 0:
            pct_num_oui = (df.loc[var1_mask, 'BASCULEMENT'] * df.loc[var1_mask, 'POIDS03']).sum() / df.loc[var1_mask, 'POIDS03'].sum() * 100
            pct_num_non = (df.loc[var0_mask, 'BASCULEMENT'] * df.loc[var0_mask, 'POIDS03']).sum() / df.loc[var0_mask, 'POIDS03'].sum() * 100
            ecart = pct_num_oui - pct_num_non

            stratifie_cards.append({
                'variable': var_label,
                'var_code': var,
                'strate_type': 'diplome',
                'strate_key': strate_key,
                'strate_label': strate_info['label'],
                'v_cramer': round(v, 3),
                'pct_num_oui': round(pct_num_oui, 1),
                'pct_num_non': round(pct_num_non, 1),
                'ecart': round(ecart, 1),
                'n': mask.sum(),
                'significatif': p < 0.05
            })

effets_stratifies_data = {
    'id': '01f-effets-stratifies',
    'titre': 'Effets différenciés',
    'sousTitre': 'L\'âge et le diplôme changent-ils la donne ?',
    'description': 'Les facteurs du basculement ont-ils le même effet selon l\'âge ou le niveau de diplôme ?',

    'noteMethodologique': {
        'titre': 'Lecture des cartes',
        'texte': 'Chaque carte montre l\'effet d\'une variable sur le basculement, au sein d\'une strate particulière (ex: chez les 15-34 ans). L\'écart indique la différence de % numérique entre ceux qui ont la caractéristique et ceux qui ne l\'ont pas.'
    },

    'sections': [
        {
            'id': 'stratifie-cards',
            'titre': 'Effets stratifiés',
            'visualisations': [
                {
                    'type': 'effet_net_cards_stratifie',
                    'data': stratifie_cards
                }
            ]
        }
    ],

    'metadata': {
        'n_cards': len(stratifie_cards)
    }
}

save_json(effets_stratifies_data, '01f-effets-stratifies.json')

# -----------------------------
# 01G - PROFILS TYPES (Arbre de décision)
# -----------------------------
print("\nGénération de 01g-profils-types.json...")

from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder

# Préparer les variables pour l'arbre (SANS GENRE car V=0.03)
# Situation pro simplifiée
def recode_sitpro_tree(val):
    if pd.isna(val): return np.nan
    if val == 1: return 'Actif'
    elif val == 6: return 'Retraité'
    elif val == 4: return 'Étudiant'
    else: return 'Autre'

df['SITPRO_TREE'] = df['RS3_R'].apply(recode_sitpro_tree)

# Taille agglo simplifiée
def recode_agglo_tree(val):
    if pd.isna(val): return np.nan
    if val in [4, 5]: return 'Grande ville'
    elif val == 1: return 'Rural'
    else: return 'Ville moyenne'

df['AGGLO_TREE'] = df['CC_R'].apply(recode_agglo_tree)

# Préparer le dataset
vars_tree = ['AGE', 'SITPRO_TREE', 'DIPLOME_REGROUPE', 'AGGLO_TREE', 'REVENU_CAT']
df_tree = df[vars_tree + ['BASCULEMENT', 'POIDS03']].dropna().copy().reset_index(drop=True)

# Encoder les variables catégorielles
df_tree_encoded = df_tree.copy()
encoders_tree = {}
for var in ['SITPRO_TREE', 'AGGLO_TREE']:
    le = LabelEncoder()
    df_tree_encoded[var] = le.fit_transform(df_tree[var])
    encoders_tree[var] = le

X_tree = df_tree_encoded[['AGE', 'SITPRO_TREE', 'DIPLOME_REGROUPE', 'AGGLO_TREE', 'REVENU_CAT']].values
y_tree = df_tree_encoded['BASCULEMENT'].values
weights_tree = df_tree_encoded['POIDS03'].values

# Entraîner l'arbre avec poids
tree_model = DecisionTreeClassifier(
    max_depth=4,
    min_samples_leaf=50,
    min_samples_split=100,
    random_state=42
)
tree_model.fit(X_tree, y_tree, sample_weight=weights_tree)

# Calculer l'importance des variables
feature_names_tree = ['Âge', 'Situation pro.', 'Diplôme', 'Taille agglo', 'Revenu']
importances = [
    {'variable': name, 'importance': round(float(imp), 3), 'pct': round(float(imp) * 100, 1)}
    for name, imp in zip(feature_names_tree, tree_model.feature_importances_)
]
importances.sort(key=lambda x: x['importance'], reverse=True)

# Créer les 5 profils simplifiés
profils_data = []
pct_num_global = (y_tree * weights_tree).sum() / weights_tree.sum() * 100

# Profil 1: Jeunes (15-44 ans) - codes 1-4
mask_jeunes = df_tree_encoded['AGE'] <= 4
if mask_jeunes.sum() > 0:
    pct = (y_tree[mask_jeunes] * weights_tree[mask_jeunes]).sum() / weights_tree[mask_jeunes].sum() * 100
    profils_data.append({
        'id': 'jeunes',
        'ordre': 1,
        'nom': 'Les connectés',
        'sousTitre': '15-44 ans',
        'description': 'Qu\'ils soient étudiants, actifs ou en recherche d\'emploi, les moins de 45 ans ont massivement adopté les canaux numériques pour s\'informer.',
        'icon': 'smartphone',
        'n': int(mask_jeunes.sum()),
        'pct_echantillon': round(mask_jeunes.sum() / len(df_tree) * 100, 0),
        'pct_numerique': round(pct, 0),
        'ecart': round(pct - pct_num_global, 0),
        'couleur': '#10B981',
        'gradient': 'from-emerald-500 to-teal-500',
        'categorie': 'numerique',
        'caracteristiques': ['Moins de 45 ans', 'Toutes situations professionnelles', 'Tous niveaux de diplôme'],
        'insight': '7 sur 10 s\'informent principalement en ligne'
    })

# Profil 2: Actifs 45+ grandes villes
sitpro_actif = encoders_tree['SITPRO_TREE'].transform(['Actif'])[0]
agglo_gde = encoders_tree['AGGLO_TREE'].transform(['Grande ville'])[0]
mask_actifs_urbains = (df_tree_encoded['AGE'] > 4) & (df_tree_encoded['SITPRO_TREE'] == sitpro_actif) & (df_tree_encoded['AGGLO_TREE'] == agglo_gde)
if mask_actifs_urbains.sum() > 0:
    pct = (y_tree[mask_actifs_urbains] * weights_tree[mask_actifs_urbains]).sum() / weights_tree[mask_actifs_urbains].sum() * 100
    profils_data.append({
        'id': 'actifs_urbains',
        'ordre': 2,
        'nom': 'Les urbains actifs',
        'sousTitre': '45+ ans, actifs, grandes villes',
        'description': 'Encore dans la vie active et vivant en milieu urbain, ils gardent un pied dans chaque monde : autant connectés que branchés sur les médias traditionnels.',
        'icon': 'building',
        'n': int(mask_actifs_urbains.sum()),
        'pct_echantillon': round(mask_actifs_urbains.sum() / len(df_tree) * 100, 0),
        'pct_numerique': round(pct, 0),
        'ecart': round(pct - pct_num_global, 0),
        'couleur': '#F59E0B',
        'gradient': 'from-amber-500 to-orange-500',
        'categorie': 'mixte',
        'caracteristiques': ['45 ans et plus', 'En activité professionnelle', 'Grandes villes ou Paris'],
        'insight': 'Profil partagé entre les deux mondes'
    })

# Profil 3: Actifs 45+ zones moins denses
mask_actifs_autres = (df_tree_encoded['AGE'] > 4) & (df_tree_encoded['SITPRO_TREE'] == sitpro_actif) & (df_tree_encoded['AGGLO_TREE'] != agglo_gde)
if mask_actifs_autres.sum() > 0:
    pct = (y_tree[mask_actifs_autres] * weights_tree[mask_actifs_autres]).sum() / weights_tree[mask_actifs_autres].sum() * 100
    profils_data.append({
        'id': 'actifs_ruraux',
        'ordre': 3,
        'nom': 'Les ancrés',
        'sousTitre': '45+ ans, actifs, hors grandes villes',
        'description': 'Actifs mais éloignés des grandes métropoles, ils restent davantage attachés aux médias traditionnels, notamment la télévision.',
        'icon': 'home',
        'n': int(mask_actifs_autres.sum()),
        'pct_echantillon': round(mask_actifs_autres.sum() / len(df_tree) * 100, 0),
        'pct_numerique': round(pct, 0),
        'ecart': round(pct - pct_num_global, 0),
        'couleur': '#8B5CF6',
        'gradient': 'from-violet-500 to-purple-500',
        'categorie': 'traditionnel',
        'caracteristiques': ['45 ans et plus', 'En activité professionnelle', 'Zones rurales ou villes moyennes'],
        'insight': 'Le territoire freine le basculement'
    })

# Profil 4: Retraités diplômés (Bac+3)
sitpro_ret = encoders_tree['SITPRO_TREE'].transform(['Retraité'])[0]
mask_ret_dip = (df_tree_encoded['AGE'] > 4) & (df_tree_encoded['SITPRO_TREE'] == sitpro_ret) & (df_tree_encoded['DIPLOME_REGROUPE'] == 3)
if mask_ret_dip.sum() > 0:
    pct = (y_tree[mask_ret_dip] * weights_tree[mask_ret_dip]).sum() / weights_tree[mask_ret_dip].sum() * 100
    profils_data.append({
        'id': 'retraites_diplomes',
        'ordre': 4,
        'nom': 'Les classiques éclairés',
        'sousTitre': 'Retraités diplômés',
        'description': 'Malgré un niveau d\'études élevé, ces retraités préfèrent les médias qu\'ils connaissent depuis toujours. Le diplôme ne suffit pas à faire basculer.',
        'icon': 'book',
        'n': int(mask_ret_dip.sum()),
        'pct_echantillon': round(mask_ret_dip.sum() / len(df_tree) * 100, 0),
        'pct_numerique': round(pct, 0),
        'ecart': round(pct - pct_num_global, 0),
        'couleur': '#6366F1',
        'gradient': 'from-indigo-500 to-blue-500',
        'categorie': 'traditionnel',
        'caracteristiques': ['Retraités', 'Bac+3 et plus', 'Toutes zones géographiques'],
        'insight': 'Le diplôme ne compense pas l\'âge'
    })

# Profil 5: Retraités peu diplômés
mask_ret_nondip = (df_tree_encoded['AGE'] > 4) & (df_tree_encoded['SITPRO_TREE'] == sitpro_ret) & (df_tree_encoded['DIPLOME_REGROUPE'] != 3)
if mask_ret_nondip.sum() > 0:
    pct = (y_tree[mask_ret_nondip] * weights_tree[mask_ret_nondip]).sum() / weights_tree[mask_ret_nondip].sum() * 100
    profils_data.append({
        'id': 'retraites_populaires',
        'ordre': 5,
        'nom': 'Les fidèles',
        'sousTitre': 'Retraités sans diplôme supérieur',
        'description': 'Génération télévision par excellence, ils sont restés fidèles au poste. Seulement 1 sur 10 s\'informe principalement en ligne.',
        'icon': 'tv',
        'n': int(mask_ret_nondip.sum()),
        'pct_echantillon': round(mask_ret_nondip.sum() / len(df_tree) * 100, 0),
        'pct_numerique': round(pct, 0),
        'ecart': round(pct - pct_num_global, 0),
        'couleur': '#EC4899',
        'gradient': 'from-pink-500 to-rose-500',
        'categorie': 'traditionnel',
        'caracteristiques': ['Retraités', 'Sans diplôme du supérieur', 'Toutes zones géographiques'],
        'insight': '9 sur 10 restent fidèles à la télé'
    })

# Trier par % numérique décroissant
profils_data.sort(key=lambda x: x['pct_numerique'], reverse=True)

# Créer le parcours de décision simplifié (pour visualisation)
parcours_decision = {
    'titre': 'Comment l\'analyse classe les Français',
    'description': 'Un arbre de décision révèle les facteurs qui prédisent le mieux si quelqu\'un s\'informe en ligne ou via les médias traditionnels.',
    'etapes': [
        {
            'niveau': 1,
            'question': 'Quel âge avez-vous ?',
            'variable': 'Âge',
            'importance': round(float(tree_model.feature_importances_[0]) * 100, 0),
            'branches': [
                {
                    'condition': 'Moins de 45 ans',
                    'resultat': 'numerique',
                    'pct': profils_data[0]['pct_numerique'] if profils_data else 70,
                    'label': '→ 70% numériques',
                    'couleur': '#10B981'
                },
                {
                    'condition': '45 ans et plus',
                    'resultat': 'suite',
                    'label': '→ Ça dépend...',
                    'couleur': '#6B7280'
                }
            ]
        },
        {
            'niveau': 2,
            'question': 'Êtes-vous encore en activité ?',
            'variable': 'Situation professionnelle',
            'importance': round(float(tree_model.feature_importances_[1]) * 100, 0),
            'condition_parent': '45 ans et plus',
            'branches': [
                {
                    'condition': 'Oui, en activité',
                    'resultat': 'suite',
                    'label': '→ Ça dépend du lieu...',
                    'couleur': '#F59E0B'
                },
                {
                    'condition': 'Non, retraité',
                    'resultat': 'traditionnel',
                    'pct': 15,
                    'label': '→ 85% traditionnels',
                    'couleur': '#6366F1'
                }
            ]
        },
        {
            'niveau': 3,
            'question': 'Où habitez-vous ?',
            'variable': 'Taille d\'agglomération',
            'importance': round(float(tree_model.feature_importances_[3]) * 100, 0),
            'condition_parent': 'Actif de 45+',
            'branches': [
                {
                    'condition': 'Grande ville',
                    'resultat': 'mixte',
                    'pct': 45,
                    'label': '→ 50/50',
                    'couleur': '#F59E0B'
                },
                {
                    'condition': 'Ailleurs',
                    'resultat': 'traditionnel',
                    'pct': 37,
                    'label': '→ 63% traditionnels',
                    'couleur': '#8B5CF6'
                }
            ]
        }
    ]
}

# Chiffres clés pour l'accroche
chiffres_cles = [
    {
        'valeur': '70',
        'unite': '%',
        'label': 'de l\'explication',
        'description': 'L\'âge à lui seul explique 70% du basculement numérique',
        'icon': 'chart-pie',
        'couleur': '#EF4444'
    },
    {
        'valeur': '45',
        'unite': 'ans',
        'label': 'la frontière',
        'description': 'Le seuil qui sépare les deux France de l\'information',
        'icon': 'calendar',
        'couleur': '#F59E0B'
    },
    {
        'valeur': '6×',
        'unite': '',
        'label': 'plus de numériques',
        'description': 'Écart entre les jeunes (70%) et les retraités non-diplômés (12%)',
        'icon': 'trending-up',
        'couleur': '#10B981'
    }
]

# Construire le JSON final
profils_types_data = {
    'id': '01g-profils-types',
    'titre': '5 profils face à l\'info',
    'sousTitre': 'Qui sont les Français selon leur façon de s\'informer ?',

    'accroche': {
        'texte': 'Et si votre façge suffisait à prédire comment vous vous informez ? Notre algorithme a analysé les données de 3 300 Français. Résultat : <strong>l\'âge explique à lui seul 70% du basculement vers le numérique</strong>. Le reste — diplôme, revenus, lieu de vie — ne pèse que 30%.',
        'chiffres': chiffres_cles
    },

    'messagesCles': {
        'titre': 'Ce que révèle l\'analyse',
        'messages': [
            {
                'icon': 'birthday-cake',
                'titre': 'L\'âge domine tout',
                'texte': 'Avoir moins de 45 ans est le meilleur prédicteur du basculement numérique. Ni le diplôme, ni les revenus, ni le lieu de vie ne pèsent autant.'
            },
            {
                'icon': 'briefcase',
                'titre': 'La retraite, point de bascule',
                'texte': 'Parmi les plus de 45 ans, être encore en activité professionnelle multiplie par 3 les chances de s\'informer en ligne.'
            },
            {
                'icon': 'map-pin',
                'titre': 'Le territoire, facteur secondaire',
                'texte': 'Vivre en grande ville augmente légèrement la probabilité d\'être numérique, mais uniquement chez les actifs de 45 ans et plus.'
            }
        ]
    },

    'parcours': parcours_decision,

    'profils': {
        'titre': 'Les 5 visages de l\'information',
        'description': 'De l\'hyper-connecté au téléspectateur fidèle, cinq profils types se dégagent de l\'analyse.',
        'data': profils_data,
        'comparaison': {
            'titre': 'D\'un extrême à l\'autre',
            'profil_haut': profils_data[0] if profils_data else None,
            'profil_bas': profils_data[-1] if profils_data else None,
            'ratio': round(profils_data[0]['pct_numerique'] / profils_data[-1]['pct_numerique'], 1) if profils_data and profils_data[-1]['pct_numerique'] > 0 else None,
            'texte': f"Un jeune a {round(profils_data[0]['pct_numerique'] / max(profils_data[-1]['pct_numerique'], 1), 0):.0f} fois plus de chances de s'informer en ligne qu'un retraité peu diplômé." if profils_data else ""
        }
    },

    'variablesImportance': {
        'titre': 'Le poids de chaque facteur',
        'description': 'Sur 100% d\'explication, voici ce que pèse chaque caractéristique sociale.',
        'data': importances,
        'insight': 'À eux seuls, l\'âge et la situation professionnelle expliquent près de 90% du phénomène.'
    },

    'methodologie': {
        'titre': 'Comment avons-nous fait ?',
        'texte': 'Nous avons utilisé une méthode statistique appelée <strong>arbre de décision</strong> — la même technique que celle utilisée par les banques pour évaluer les crédits ou par les médecins pour établir un diagnostic. Cette analyse cherche les questions les plus efficaces pour distinguer les "numériques" des "traditionnels".',
        'precision': {
            'valeur': round(((tree_model.predict(X_tree) == y_tree) * weights_tree).sum() / weights_tree.sum() * 100, 0),
            'label': 'de précision',
            'description': 'L\'arbre classe correctement 7 Français sur 10'
        },
        'limites': 'Ces profils sont des tendances moyennes. Il existe bien sûr des retraités très connectés et des jeunes attachés à la télévision !'
    },

    'metadata': {
        'n_total': len(df_tree),
        'n_profils': len(profils_data),
        'accuracy': round(((tree_model.predict(X_tree) == y_tree) * weights_tree).sum() / weights_tree.sum() * 100, 1),
        'pct_num_global': round(pct_num_global, 1)
    }
}

# Correction de la typo dans l'accroche
profils_types_data['accroche']['texte'] = 'Et si votre âge suffisait à prédire comment vous vous informez ? Notre analyse statistique porte sur les données de 3 300 Français. Résultat : <strong>l\'âge explique à lui seul 70% du basculement vers le numérique</strong>. Le reste — diplôme, revenus, lieu de vie — ne pèse que 30%.'

save_json(profils_types_data, '01g-profils-types.json')
print(f"  -> {len(profils_data)} profils générés")

# Mettre à jour l'index avec la nouvelle section
index_data['sommaire'].append({
    'id': '01g-profils-types',
    'titre': '5 profils face à l\'info',
    'description': 'Les visages types du basculement numérique',
    'icon': 'users'
})
save_json(index_data, 'index.json')

# -----------------------------
# 01H - PROFILS AU SEIN DES NUMÉRIQUES
# -----------------------------
print("\nGénération de 01h-profils-numeriques.json...")

# Créer TYPE_NUMERIQUE basé sur NEWS1BIS_R et les supports
def get_type_numerique(row):
    source = row['NEWS1BIS_R']
    if pd.isna(source):
        return np.nan

    # LE SCROLL : RS + YouTube
    if source == 8:  # Réseaux sociaux
        return 'Scroll'
    if source == 9:  # YouTube/Twitch
        return 'Scroll'

    # LA REQUÊTE : Moteurs + Portails
    if source == 6:  # Moteurs de recherche
        return 'Requete'
    if source == 7:  # Portails
        return 'Requete'

    # LA SOURCE : Médias identifiés sur support numérique
    if source == 2 and row.get('NEWS1_2B_R') == 2:  # TV sur smartphone/ordi
        return 'Source'
    if source == 1 and row.get('NEWS1_1B_R') in [2, 3]:  # Radio sur smartphone
        return 'Source'
    if source == 3 and row.get('NEWS1_3B_R') == 1:  # Presse numérique
        return 'Source'
    if source == 5:  # Pure players
        return 'Source'

    return np.nan

df['TYPE_NUMERIQUE'] = df.apply(get_type_numerique, axis=1)

# Filtrer sur les numériques uniquement
df_num = df[df['TYPE_NUMERIQUE'].notna()].copy().reset_index(drop=True)
n_numeriques = len(df_num)

# Effectifs par type
n_scroll = (df_num['TYPE_NUMERIQUE'] == 'Scroll').sum()
n_requete = (df_num['TYPE_NUMERIQUE'] == 'Requete').sum()
n_source = (df_num['TYPE_NUMERIQUE'] == 'Source').sum()

# Composition détaillée de chaque type
composition_types = {
    'Scroll': [
        {'source': 'Réseaux sociaux', 'n': int((df_num['NEWS1BIS_R'] == 8).sum())},
        {'source': 'YouTube / Twitch', 'n': int((df_num['NEWS1BIS_R'] == 9).sum())}
    ],
    'Requete': [
        {'source': 'Moteurs de recherche', 'n': int((df_num['NEWS1BIS_R'] == 6).sum())},
        {'source': 'Portails d\'actualité', 'n': int((df_num['NEWS1BIS_R'] == 7).sum())}
    ],
    'Source': [
        {'source': 'Presse en ligne', 'n': int(((df_num['NEWS1BIS_R'] == 3) & (df_num['NEWS1_3B_R'] == 1)).sum())},
        {'source': 'Pure players', 'n': int((df_num['NEWS1BIS_R'] == 5).sum())},
        {'source': 'Radio sur smartphone', 'n': int(((df_num['NEWS1BIS_R'] == 1) & (df_num['NEWS1_1B_R'].isin([2,3]))).sum())},
        {'source': 'TV sur smartphone', 'n': int(((df_num['NEWS1BIS_R'] == 2) & (df_num['NEWS1_2B_R'] == 2)).sum())}
    ]
}

# Préparer les variables pour l'arbre
df_num['AGE_NUM'] = df_num['RS2C_RECODE_AG_R']

def recode_diplome_num(rs5):
    if pd.isna(rs5): return np.nan
    if rs5 in [1, 2, 3, 4]: return 1  # Sans Bac
    elif rs5 in [5, 6]: return 2       # Bac/Bac+2
    else: return 3                      # Bac+3+
df_num['DIPLOME_NUM'] = df_num['RS5_R'].apply(recode_diplome_num)

def recode_agglo_num(val):
    if pd.isna(val): return np.nan
    if val in [4, 5]: return 'Grande ville'
    elif val == 1: return 'Rural'
    else: return 'Ville moyenne'
df_num['AGGLO_NUM'] = df_num['CC_R'].apply(recode_agglo_num)

# Dataset pour l'arbre
vars_tree_num = ['AGE_NUM', 'DIPLOME_NUM', 'AGGLO_NUM']
df_tree_num = df_num[vars_tree_num + ['TYPE_NUMERIQUE', 'POIDS03']].dropna().copy().reset_index(drop=True)

# Encoder
from sklearn.preprocessing import LabelEncoder
le_target_num = LabelEncoder()
df_tree_num['TARGET'] = le_target_num.fit_transform(df_tree_num['TYPE_NUMERIQUE'])

le_agglo_num = LabelEncoder()
df_tree_num['AGGLO_ENC'] = le_agglo_num.fit_transform(df_tree_num['AGGLO_NUM'])

X_num = df_tree_num[['AGE_NUM', 'DIPLOME_NUM', 'AGGLO_ENC']].values
y_num = df_tree_num['TARGET'].values
weights_num = df_tree_num['POIDS03'].values

# Arbre multi-classes
tree_num = DecisionTreeClassifier(
    max_depth=4,
    min_samples_leaf=30,
    min_samples_split=60,
    random_state=42
)
tree_num.fit(X_num, y_num, sample_weight=weights_num)

# Importance des variables
feature_names_num = ['Âge', 'Diplôme', 'Territoire']
importances_num = [
    {'variable': name, 'importance': round(float(imp), 3), 'pct': round(float(imp) * 100, 1)}
    for name, imp in zip(feature_names_num, tree_num.feature_importances_)
]
importances_num.sort(key=lambda x: x['importance'], reverse=True)

# Calculer les stats par type
def calc_stats_type(type_name):
    mask = df_tree_num['TYPE_NUMERIQUE'] == type_name
    w = df_tree_num.loc[mask, 'POIDS03']
    total_w = w.sum()

    # % jeunes (15-34)
    pct_jeunes = df_tree_num.loc[mask & (df_tree_num['AGE_NUM'] <= 3), 'POIDS03'].sum() / total_w * 100
    # % diplômés (Bac+3)
    pct_diplomes = df_tree_num.loc[mask & (df_tree_num['DIPLOME_NUM'] == 3), 'POIDS03'].sum() / total_w * 100
    # % grandes villes
    pct_urbain = df_tree_num.loc[mask & (df_tree_num['AGGLO_NUM'] == 'Grande ville'), 'POIDS03'].sum() / total_w * 100

    return {
        'pct_jeunes': round(pct_jeunes, 0),
        'pct_diplomes': round(pct_diplomes, 0),
        'pct_urbain': round(pct_urbain, 0)
    }

stats_scroll = calc_stats_type('Scroll')
stats_requete = calc_stats_type('Requete')
stats_source = calc_stats_type('Source')

# Créer les 3 types avec descriptions
types_numeriques = [
    {
        'id': 'scroll',
        'nom': 'Le scroll',
        'sousTitre': 'Réseaux sociaux et YouTube',
        'description': 'L\'information vient à eux, portée par l\'algorithme. Ils scrollent leur fil d\'actualité sans forcément chercher quelque chose de précis.',
        'icon': 'scroll',
        'n': n_scroll,
        'pct': round(n_scroll / n_numeriques * 100, 0),
        'couleur': '#EC4899',
        'gradient': 'from-pink-500 to-rose-500',
        'composition': composition_types['Scroll'],
        'stats': stats_scroll,
        'profil_type': 'Jeune, souvent étudiant, tous milieux',
        'insight': f"{stats_scroll['pct_jeunes']:.0f}% ont moins de 35 ans"
    },
    {
        'id': 'requete',
        'nom': 'La requête',
        'sousTitre': 'Moteurs de recherche et portails',
        'description': 'Ils tapent une recherche, cliquent sur un résultat. L\'information est une réponse à une question qu\'ils se posent.',
        'icon': 'search',
        'n': n_requete,
        'pct': round(n_requete / n_numeriques * 100, 0),
        'couleur': '#F59E0B',
        'gradient': 'from-amber-500 to-orange-500',
        'composition': composition_types['Requete'],
        'stats': stats_requete,
        'profil_type': 'Actif, 35-59 ans, diplôme intermédiaire',
        'insight': 'Le profil médian du numérique'
    },
    {
        'id': 'source',
        'nom': 'La source',
        'sousTitre': 'Médias identifiés en version numérique',
        'description': 'Ils vont directement sur le site du Monde, écoutent France Info sur leur téléphone, ou sont abonnés à Mediapart. Ils ont choisi leurs sources.',
        'icon': 'newspaper',
        'n': n_source,
        'pct': round(n_source / n_numeriques * 100, 0),
        'couleur': '#10B981',
        'gradient': 'from-emerald-500 to-teal-500',
        'composition': composition_types['Source'],
        'stats': stats_source,
        'profil_type': 'Diplômé, urbain, souvent 45+',
        'insight': f"{stats_source['pct_diplomes']:.0f}% ont un Bac+3 ou plus"
    }
]

# Créer les 6 profils détaillés
profils_numeriques = []

# Profil 1: Jeunes (15-24) -> Scroll
mask1 = df_tree_num['AGE_NUM'] <= 2
n1 = mask1.sum()
pct_scroll1 = df_tree_num.loc[mask1 & (df_tree_num['TYPE_NUMERIQUE']=='Scroll'), 'POIDS03'].sum() / df_tree_num.loc[mask1, 'POIDS03'].sum() * 100
profils_numeriques.append({
    'id': 'scrolleurs',
    'nom': 'Les scrolleurs',
    'description': '15-24 ans : TikTok, Instagram, YouTube... L\'info arrive dans le flux.',
    'regle': 'Âge ≤ 24 ans',
    'n': int(n1),
    'prediction': 'Scroll',
    'pct_prediction': round(pct_scroll1, 0),
    'couleur': '#EC4899'
})

# Profil 2: 25-44 non diplômés -> Mixte
mask2 = (df_tree_num['AGE_NUM'] > 2) & (df_tree_num['AGE_NUM'] <= 4) & (df_tree_num['DIPLOME_NUM'] <= 2)
n2 = mask2.sum()
pct_scroll2 = df_tree_num.loc[mask2 & (df_tree_num['TYPE_NUMERIQUE']=='Scroll'), 'POIDS03'].sum() / df_tree_num.loc[mask2, 'POIDS03'].sum() * 100
pct_req2 = df_tree_num.loc[mask2 & (df_tree_num['TYPE_NUMERIQUE']=='Requete'), 'POIDS03'].sum() / df_tree_num.loc[mask2, 'POIDS03'].sum() * 100
profils_numeriques.append({
    'id': 'partages',
    'nom': 'Les partagés',
    'description': '25-44 ans sans diplôme supérieur : entre scroll et recherche active.',
    'regle': '25-44 ans, sans Bac+3',
    'n': int(n2),
    'prediction': 'Scroll/Requête',
    'pct_prediction': round(max(pct_scroll2, pct_req2), 0),
    'couleur': '#8B5CF6'
})

# Profil 3: 25-44 diplômés -> Requête
mask3 = (df_tree_num['AGE_NUM'] > 2) & (df_tree_num['AGE_NUM'] <= 4) & (df_tree_num['DIPLOME_NUM'] > 2)
n3 = mask3.sum()
pct_req3 = df_tree_num.loc[mask3 & (df_tree_num['TYPE_NUMERIQUE']=='Requete'), 'POIDS03'].sum() / df_tree_num.loc[mask3, 'POIDS03'].sum() * 100
profils_numeriques.append({
    'id': 'chercheurs_diplomes',
    'nom': 'Les chercheurs diplômés',
    'description': '25-44 ans diplômés : Google est leur ami, ils cherchent l\'info.',
    'regle': '25-44 ans, Bac+3 et plus',
    'n': int(n3),
    'prediction': 'Requête',
    'pct_prediction': round(pct_req3, 0),
    'couleur': '#F59E0B'
})

# Profil 4: 45+ non diplômés -> Requête
mask4 = (df_tree_num['AGE_NUM'] > 4) & (df_tree_num['DIPLOME_NUM'] <= 2)
n4 = mask4.sum()
pct_req4 = df_tree_num.loc[mask4 & (df_tree_num['TYPE_NUMERIQUE']=='Requete'), 'POIDS03'].sum() / df_tree_num.loc[mask4, 'POIDS03'].sum() * 100
profils_numeriques.append({
    'id': 'googlers',
    'nom': 'Les googlers',
    'description': '45+ sans diplôme supérieur : Google et les portails Orange, Yahoo...',
    'regle': '45 ans et plus, sans Bac+3',
    'n': int(n4),
    'prediction': 'Requête',
    'pct_prediction': round(pct_req4, 0),
    'couleur': '#F59E0B'
})

# Profil 5: 45+ diplômés grande ville -> Source
mask5 = (df_tree_num['AGE_NUM'] > 4) & (df_tree_num['DIPLOME_NUM'] > 2) & (df_tree_num['AGGLO_NUM'] == 'Grande ville')
n5 = mask5.sum()
pct_source5 = df_tree_num.loc[mask5 & (df_tree_num['TYPE_NUMERIQUE']=='Source'), 'POIDS03'].sum() / df_tree_num.loc[mask5, 'POIDS03'].sum() * 100 if mask5.sum() > 0 else 0
profils_numeriques.append({
    'id': 'connaisseurs',
    'nom': 'Les connaisseurs',
    'description': '45+ diplômés urbains : Le Monde, Mediapart, France Info... Ils ont leurs sources.',
    'regle': '45+ ans, Bac+3, grande ville',
    'n': int(n5),
    'prediction': 'Source',
    'pct_prediction': round(pct_source5, 0),
    'couleur': '#10B981'
})

# Profil 6: 45+ diplômés hors grande ville -> Requête
mask6 = (df_tree_num['AGE_NUM'] > 4) & (df_tree_num['DIPLOME_NUM'] > 2) & (df_tree_num['AGGLO_NUM'] != 'Grande ville')
n6 = mask6.sum()
pct_req6 = df_tree_num.loc[mask6 & (df_tree_num['TYPE_NUMERIQUE']=='Requete'), 'POIDS03'].sum() / df_tree_num.loc[mask6, 'POIDS03'].sum() * 100 if mask6.sum() > 0 else 0
profils_numeriques.append({
    'id': 'pragmatiques',
    'nom': 'Les pragmatiques',
    'description': '45+ diplômés hors métropole : diplômés mais Google reste le réflexe.',
    'regle': '45+ ans, Bac+3, hors grande ville',
    'n': int(n6),
    'prediction': 'Requête',
    'pct_prediction': round(pct_req6, 0),
    'couleur': '#F59E0B'
})

# Parcours de décision simplifié
parcours_num = {
    'titre': 'Comment se répartissent les numériques ?',
    'description': 'Trois questions suffisent à prédire quel type de numérique vous êtes.',
    'etapes': [
        {
            'niveau': 1,
            'question': 'Quel âge avez-vous ?',
            'importance': importances_num[0]['pct'] if importances_num[0]['variable'] == 'Âge' else 0,
            'branches': [
                {'condition': 'Moins de 25 ans', 'resultat': 'scroll', 'label': '→ SCROLL', 'couleur': '#EC4899'},
                {'condition': '25 ans et plus', 'resultat': 'suite', 'label': '→ Ça dépend...', 'couleur': '#6B7280'}
            ]
        },
        {
            'niveau': 2,
            'question': 'Quel est votre niveau de diplôme ?',
            'importance': importances_num[1]['pct'] if len(importances_num) > 1 else 0,
            'branches': [
                {'condition': 'Sans Bac+3', 'resultat': 'requete', 'label': '→ REQUÊTE', 'couleur': '#F59E0B'},
                {'condition': 'Bac+3 et plus', 'resultat': 'suite', 'label': '→ Ça dépend...', 'couleur': '#6B7280'}
            ]
        },
        {
            'niveau': 3,
            'question': 'Où habitez-vous ?',
            'importance': importances_num[2]['pct'] if len(importances_num) > 2 else 0,
            'branches': [
                {'condition': 'Grande ville', 'resultat': 'source', 'label': '→ SOURCE', 'couleur': '#10B981'},
                {'condition': 'Ailleurs', 'resultat': 'requete', 'label': '→ REQUÊTE', 'couleur': '#F59E0B'}
            ]
        }
    ]
}

# Accuracy de l'arbre
accuracy_num = ((tree_num.predict(X_num) == y_num) * weights_num).sum() / weights_num.sum() * 100

# Construire le JSON
profils_numeriques_data = {
    'id': '01h-profils-numeriques',
    'titre': '3 façons de s\'informer en ligne',
    'sousTitre': 'Tous numériques, mais pas de la même manière',

    'accroche': {
        'texte': 'Parmi ceux qui s\'informent principalement en ligne, trois comportements bien distincts émergent : <strong>le scroll</strong> (l\'info vient à moi), <strong>la requête</strong> (je cherche l\'info), et <strong>la source</strong> (je choisis mon média).',
        'chiffres': [
            {
                'valeur': str(round(n_scroll / n_numeriques * 100, 0)),
                'unite': '%',
                'label': 'scrollent',
                'description': 'RS et YouTube',
                'couleur': '#EC4899'
            },
            {
                'valeur': str(round(n_requete / n_numeriques * 100, 0)),
                'unite': '%',
                'label': 'cherchent',
                'description': 'Google et portails',
                'couleur': '#F59E0B'
            },
            {
                'valeur': str(round(n_source / n_numeriques * 100, 0)),
                'unite': '%',
                'label': 'choisissent',
                'description': 'Médias identifiés',
                'couleur': '#10B981'
            }
        ]
    },

    'types': {
        'titre': 'Les 3 comportements numériques',
        'description': 'Chaque type correspond à une façon différente d\'accéder à l\'information en ligne.',
        'data': types_numeriques,
        'comparaison': {
            'titre': 'Qui fait quoi ?',
            'axes': [
                {'label': '% de 15-34 ans', 'scroll': stats_scroll['pct_jeunes'], 'requete': stats_requete['pct_jeunes'], 'source': stats_source['pct_jeunes']},
                {'label': '% de Bac+3', 'scroll': stats_scroll['pct_diplomes'], 'requete': stats_requete['pct_diplomes'], 'source': stats_source['pct_diplomes']},
                {'label': '% grandes villes', 'scroll': stats_scroll['pct_urbain'], 'requete': stats_requete['pct_urbain'], 'source': stats_source['pct_urbain']}
            ]
        }
    },

    'parcours': parcours_num,

    'profils': {
        'titre': '6 profils de numériques',
        'description': 'En combinant âge, diplôme et territoire, six profils types se dessinent.',
        'data': profils_numeriques
    },

    'variablesImportance': {
        'titre': 'Ce qui détermine votre type',
        'description': 'Au sein des numériques, l\'âge reste déterminant, mais le diplôme prend plus d\'importance.',
        'data': importances_num,
        'insight': 'L\'âge prédit le scroll, le diplôme prédit la source.'
    },

    'messagesCles': {
        'titre': 'Ce qu\'il faut retenir',
        'messages': [
            {
                'icon': 'sparkles',
                'titre': 'Jeune = scroll',
                'texte': 'Avant 25 ans, l\'info arrive par le fil d\'actualité des réseaux sociaux ou YouTube. On ne la cherche pas, on la reçoit.'
            },
            {
                'icon': 'academic-cap',
                'titre': 'Diplômé = source directe',
                'texte': 'Les Bac+3 et plus, surtout en grande ville, vont directement sur les sites des médias qu\'ils ont choisis.'
            },
            {
                'icon': 'globe',
                'titre': 'Le territoire fait la différence',
                'texte': 'À diplôme égal, les urbains vont plus vers les médias identifiés, les autres vers Google.'
            }
        ]
    },

    'methodologie': {
        'titre': 'Comment avons-nous construit ces types ?',
        'texte': 'Nous avons regroupé les 8 sources numériques en 3 familles selon la logique d\'accès à l\'information : passive (scroll), active (requête), ou délibérée (source). Un arbre de décision identifie ensuite les profils sociodémographiques associés à chaque type.',
        'precision': {
            'valeur': round(accuracy_num, 0),
            'label': 'de précision',
            'description': f'L\'arbre classe correctement {round(accuracy_num, 0):.0f}% des numériques dans le bon type'
        }
    },

    'metadata': {
        'n_numeriques': n_numeriques,
        'n_scroll': n_scroll,
        'n_requete': n_requete,
        'n_source': n_source,
        'accuracy': round(accuracy_num, 1)
    }
}

save_json(profils_numeriques_data, '01h-profils-numeriques.json')
print(f"  -> 3 types, 6 profils générés")

# Mettre à jour l'index
index_data['sommaire'].append({
    'id': '01h-profils-numeriques',
    'titre': '3 façons de s\'informer en ligne',
    'description': 'Scroll, requête ou source : les visages du numérique',
    'icon': 'device-mobile'
})
save_json(index_data, 'index.json')

# -----------------------------
# RÉSUMÉ FINAL
# -----------------------------
print("\n" + "="*50)
print("GÉNÉRATION TERMINÉE")
print("="*50)
print(f"Fichiers générés dans {OUTPUT_DIR}:")
print("  - index.json")
print("  - 01a-prenotions.json")
print("  - 01b-variable-construite.json")
print("  - 01c-qui-bascule.json")
print("  - 01d-ce-qui-accompagne.json")
print("  - 01e-regression.json")
print("  - 01f-effets-stratifies.json")
print("  - 01g-profils-types.json")
print("  - 01h-profils-numeriques.json")
