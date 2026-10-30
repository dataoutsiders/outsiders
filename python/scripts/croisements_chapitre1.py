"""
Croisements systematiques pour le Chapitre 1 : Le grand basculement
Genere un Excel avec tous les croisements et leur significativite (Chi2, V de Cramer)
"""
import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path
from datetime import datetime

# Chemins
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data" / "francais-information"
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("CROISEMENTS SYSTEMATIQUES - CHAPITRE 1")
print("=" * 70)

# ============================================================
# 1. CHARGEMENT DES DONNEES
# ============================================================
print("\n1. Chargement des donnees...")
df = pd.read_excel(DATA_DIR / "base-info-arcom.xlsx")
print(f"   {len(df)} repondants")

# Convertir POIDS03
df['POIDS03'] = df['POIDS03'].astype(str).str.replace(',', '.').astype(float)

# ============================================================
# 2. CREATION VARIABLE PCS_5 (recodage CSP + inactifs)
# ============================================================
print("\n   Creation de PCS_5 (CSP recodee avec etudiants/retraites)...")

def recode_pcs(row):
    """
    Recodage PCS en 6 categories :
    - CSP+ : Cadres, prof liberales (RS4=3)
    - CSP milieu : Agriculteurs, Artisans, Prof intermediaires (RS4=1,2,4)
    - CSP- : Employes, Ouvriers (RS4=5,6)
    - Etudiants : RS3=4
    - Retraites : RS3=6
    - Autres inactifs : RS3=3,5,7 (chomeurs 1er emploi, foyer, invalides)
    """
    rs3 = row.get('RS3_R')
    rs4 = row.get('RS4_R')

    # Inactifs en priorite (RS3)
    if rs3 == 4:
        return 'Etudiants'
    elif rs3 == 6:
        return 'Retraites'
    elif rs3 in [3, 5, 7]:
        return 'Autres inactifs'

    # Actifs et chomeurs ayant travaille (RS4)
    if pd.notna(rs4):
        if rs4 == 3:
            return 'CSP+'
        elif rs4 in [1, 2, 4]:
            return 'CSP milieu'
        elif rs4 in [5, 6]:
            return 'CSP-'

    return None  # NSP ou non classe

df['PCS_5'] = df.apply(recode_pcs, axis=1)
print(f"   Distribution PCS_5 :")
print(df['PCS_5'].value_counts(dropna=False))

# ============================================================
# 2b. CREATION VARIABLE CAPITAL_CULTUREL (niveau etudes recod)
# ============================================================
print("\n   Creation de CAPITAL_CULTUREL (niveau etudes recod)...")

def recode_capital_culturel(rs5):
    """
    Recodage niveau etudes en 3 categories :
    - Faible : 1-4 (primaire, college, CAP/BEP)
    - Moyen : 5-6 (bac, BTS/DUT)
    - Eleve : 7-9 (licence et plus)
    """
    if pd.isna(rs5):
        return None
    if rs5 in [1, 2, 3, 4]:
        return 'Faible'
    elif rs5 in [5, 6]:
        return 'Moyen'
    elif rs5 in [7, 8, 9]:
        return 'Eleve'
    return None

df['CAPITAL_CULTUREL'] = df['RS5_R'].apply(recode_capital_culturel)
print(f"   Distribution CAPITAL_CULTUREL :")
print(df['CAPITAL_CULTUREL'].value_counts(dropna=False))

# ============================================================
# 2c. CREATION VARIABLE CAPITAL_ECO (revenus / personnes)
# ============================================================
print("\n   Creation de CAPITAL_ECO (revenus par personne)...")

# Milieu des tranches de revenus RS14_R
REVENUS_MIDPOINT = {
    1: 750,    # < 1500
    2: 2250,   # 1500-3000
    3: 3750,   # 3000-4500
    4: 6000,   # 4500-7500
    5: 8500,   # > 7500
    6: None    # NSP
}

def recode_capital_eco(row):
    """
    Calcul revenu par personne et recodage en 3 categories :
    - Faible : < 800 euros/pers
    - Moyen : 800-1500 euros/pers
    - Eleve : > 1500 euros/pers
    """
    rs14 = row.get('RS14_R')
    rs7 = row.get('RS7_R')

    if pd.isna(rs14) or pd.isna(rs7) or rs14 == 6:
        return None

    revenu_foyer = REVENUS_MIDPOINT.get(rs14)
    if revenu_foyer is None:
        return None

    nb_personnes = rs7 if rs7 <= 6 else 6
    revenu_par_pers = revenu_foyer / nb_personnes

    if revenu_par_pers < 800:
        return 'Faible'
    elif revenu_par_pers <= 1500:
        return 'Moyen'
    else:
        return 'Eleve'

df['CAPITAL_ECO'] = df.apply(recode_capital_eco, axis=1)
print(f"   Distribution CAPITAL_ECO :")
print(df['CAPITAL_ECO'].value_counts(dropna=False))

# ============================================================
# 2d. CREATION VARIABLE SCORE_QUIZZ (moyenne des 4 quizz)
# ============================================================
print("\n   Creation de SCORE_QUIZZ (moyenne des 4 quizz)...")

def calc_score_quizz(row):
    """
    Calcul du score au quizz (0 a 4 bonnes reponses)
    Modalite 1 = bonne reponse
    """
    score = 0
    nb_reponses = 0
    for q in ['QUIZZ1_R', 'QUIZZ2_R', 'QUIZZ3_R', 'QUIZZ4_R']:
        val = row.get(q)
        if pd.notna(val):
            nb_reponses += 1
            if val == 1:
                score += 1
    if nb_reponses == 0:
        return None
    return score

df['SCORE_QUIZZ'] = df.apply(calc_score_quizz, axis=1)

# Recoder en categories
def recode_score_quizz(score):
    if pd.isna(score):
        return None
    if score <= 1:
        return '0-1 (Faible)'
    elif score == 2:
        return '2 (Moyen)'
    else:
        return '3-4 (Eleve)'

df['SCORE_QUIZZ_CAT'] = df['SCORE_QUIZZ'].apply(recode_score_quizz)
print(f"   Distribution SCORE_QUIZZ (brut) :")
print(df['SCORE_QUIZZ'].value_counts(dropna=False).sort_index())
print(f"   Distribution SCORE_QUIZZ_CAT :")
print(df['SCORE_QUIZZ_CAT'].value_counts(dropna=False))

# ============================================================
# 3. DEFINITION DES VARIABLES
# ============================================================

# Variables socio-demographiques (VI = Variables Independantes)
# Les 3 capitaux + genre et age
VARS_SOCIO = {
    'RS1_R': 'GENRE (H/F)',
    'RS2C_RECODE_AG_R': 'AGE (15-17 / 18-24 / 25-34 / 35-44 / 45-59 / 60-69 / 70+)',
    'PCS_5': 'PCS (CSP+ / Milieu / CSP- / Etud / Retr / Inact)',
    'CAPITAL_CULTUREL': 'CAPITAL CULTUREL (<=Brevet / Bac-BTS / Licence+)',
    'CAPITAL_ECO': 'CAPITAL ECO (Rev/pers: <800 / 800-1500 / >1500)'
}

# Variables consommation info
VARS_CONSO = {
    'INT1_R': 'Interet general pour info (Bcp/Assez/Peu/Pas)',
    'INT2_R_1': 'Interet actu NATIONALE',
    'INT2_R_4': 'Interet actu INTERNATIONALE',
    'NEWS1_R_1': 'Frequence TV (Plrs/j a Jamais)',
    'NEWS1_R_5': 'Frequence RESEAUX SOCIAUX',
    'NBR_NEWS1SOURCES_R1': 'Nb sources info utilisees',
    'NEWS1BIS_R': 'SOURCE PRINCIPALE (TV/Radio/Presse/RS/...)',
    'FORMAT_R_1': 'Prefere format VIDEO',
    'FORMAT_R_2': 'Prefere format TEXTE',
    'FORMAT_R_3': 'Prefere format AUDIO',
    'FORMAT3_LR1_FORMAT3_1_R': 'Format video (detail)',
    'RSINFO_2_LR_R_4': 'Utilise INSTAGRAM pour info',
    'RSINFO_2_LR_R_1': 'Utilise FACEBOOK pour info',
    'RSINFO_2_LR_R_2': 'Utilise TWITTER/X pour info'
}

# Variables equipement
VARS_EQUIP = {
    'RS16_R_1': 'Possede SMARTPHONE'
}

# Variables valeurs
VARS_VALEURS = {
    'DEM_R_1': 'Confiance DEMOCRATIE',
    'CONFINST_R_1': 'Confiance INSTITUTIONS',
    'VA1_R_1': 'Valeurs (item 1)'
}

# Variables effets (quizz)
VARS_EFFETS = {
    'QUIZZ1_R': 'Quizz: Attaque Israel (Hamas)',
    'QUIZZ2_R': 'Quizz: PM anglais (Sunak)',
    'QUIZZ3_R': 'Quizz: Fin mandat Macron (2027)',
    'QUIZZ4_R': 'Quizz: Inflation 2023 (4.9%)',
    'SCORE_QUIZZ_CAT': 'SCORE QUIZZ GLOBAL (0-1 / 2 / 3-4)'
}

# Tous les blocs
BLOCS = {
    'Consommation info': VARS_CONSO,
    'Equipement': VARS_EQUIP,
    'Valeurs': VARS_VALEURS,
    'Effets (Quizz)': VARS_EFFETS
}

# ============================================================
# 3. FONCTIONS D'ANALYSE (avec pondération POIDS03)
# ============================================================

VAR_POIDS = 'POIDS03'

def cramers_v_weighted(contingency_table):
    """Calcule le V de Cramer sur un tableau de contingence pondéré"""
    # Le Chi2 de scipy fonctionne sur des effectifs réels (pondérés)
    chi2 = stats.chi2_contingency(contingency_table)[0]
    n = contingency_table.sum().sum()
    min_dim = min(contingency_table.shape) - 1
    if min_dim == 0 or n == 0:
        return 0
    return np.sqrt(chi2 / (n * min_dim))

def interpret_cramer(v):
    """Interprete la force du V de Cramer"""
    if v < 0.1:
        return "Négligeable"
    elif v < 0.2:
        return "Faible"
    elif v < 0.3:
        return "Modérée"
    elif v < 0.4:
        return "Moyenne"
    else:
        return "Forte"

def analyze_crosstab(df, var1, var2, var1_label, var2_label):
    """Analyse un croisement entre deux variables avec pondération"""
    # Filtrer les valeurs valides (inclure le poids)
    mask = df[var1].notna() & df[var2].notna() & df[VAR_POIDS].notna()
    df_valid = df[mask].copy()

    if len(df_valid) < 30:
        return None

    # Tableau de contingence PONDÉRÉ
    try:
        ct = pd.crosstab(
            df_valid[var1],
            df_valid[var2],
            values=df_valid[VAR_POIDS],
            aggfunc='sum'
        ).fillna(0)

        # Vérifier qu'on a assez de cellules
        if ct.shape[0] < 2 or ct.shape[1] < 2:
            return None

        # Chi2 sur tableau pondéré
        chi2, p, dof, expected = stats.chi2_contingency(ct)

        # V de Cramer sur tableau pondéré
        v = cramers_v_weighted(ct)

        # N pondéré (somme des poids)
        n_pondere = df_valid[VAR_POIDS].sum()

        return {
            'Variable 1': var1,
            'Label 1': var1_label,
            'Variable 2': var2,
            'Label 2': var2_label,
            'N': len(df_valid),
            'N pondéré': round(n_pondere, 0),
            'Chi2': round(chi2, 2),
            'ddl': dof,
            'p-value': p,
            'Significatif': 'Oui' if p < 0.05 else 'Non',
            'V Cramer': round(v, 3),
            'Force': interpret_cramer(v)
        }
    except Exception as e:
        print(f"   Erreur {var1} x {var2}: {e}")
        return None

def get_crosstab_details(df, var1, var2):
    """Retourne le tableau croisé détaillé avec effectifs pondérés et %"""
    mask = df[var1].notna() & df[var2].notna() & df[VAR_POIDS].notna()
    df_valid = df[mask].copy()

    if len(df_valid) < 30:
        return None

    # Tableau effectifs pondérés
    ct_n = pd.crosstab(
        df_valid[var1],
        df_valid[var2],
        values=df_valid[VAR_POIDS],
        aggfunc='sum',
        margins=True,
        margins_name='Total'
    ).fillna(0).round(0)

    # Tableau % ligne (pondéré)
    ct_pct = pd.crosstab(
        df_valid[var1],
        df_valid[var2],
        values=df_valid[VAR_POIDS],
        aggfunc='sum',
        normalize='index'
    ).fillna(0) * 100
    ct_pct = ct_pct.round(1)

    return ct_n, ct_pct

# ============================================================
# 4. EXECUTION DES CROISEMENTS
# ============================================================
print("\n2. Execution des croisements...")

# Verifier quelles variables existent
print("\n   Verification des variables...")
all_vars = list(VARS_SOCIO.keys()) + list(VARS_CONSO.keys()) + list(VARS_EQUIP.keys()) + list(VARS_VALEURS.keys()) + list(VARS_EFFETS.keys())
missing = [v for v in all_vars if v not in df.columns]
if missing:
    print(f"   /!\\ Variables manquantes : {missing}")
    # Retirer les variables manquantes
    for m in missing:
        for bloc in [VARS_SOCIO, VARS_CONSO, VARS_EQUIP, VARS_VALEURS, VARS_EFFETS]:
            if m in bloc:
                del bloc[m]

# Filtrer genre (enlever non-binaires pour comparaison H/F)
if 'RS1_R' in df.columns:
    # Garder seulement 1 (Homme) et 2 (Femme)
    df_analyse = df[df['RS1_R'].isin([1, 2])].copy()
    print(f"   Apres filtre genre (H/F) : {len(df_analyse)} repondants")
else:
    df_analyse = df.copy()

# Liste pour stocker tous les resultats
all_results = []

# Croisements : socio-demo x autres variables
print("\n   Croisements socio-demo x autres variables...")
for bloc_name, bloc_vars in BLOCS.items():
    print(f"   - {bloc_name}...")
    for var_socio, label_socio in VARS_SOCIO.items():
        if var_socio not in df_analyse.columns:
            continue
        for var_dep, label_dep in bloc_vars.items():
            if var_dep not in df_analyse.columns:
                continue
            result = analyze_crosstab(df_analyse, var_socio, var_dep, label_socio, label_dep)
            if result:
                result['Bloc'] = bloc_name
                result['Type'] = 'Socio x ' + bloc_name
                all_results.append(result)

# Croisements : usage x equipement
print("   - Usage x Equipement...")
for var_conso, label_conso in VARS_CONSO.items():
    if var_conso not in df_analyse.columns:
        continue
    for var_equip, label_equip in VARS_EQUIP.items():
        if var_equip not in df_analyse.columns:
            continue
        result = analyze_crosstab(df_analyse, var_conso, var_equip, label_conso, label_equip)
        if result:
            result['Bloc'] = 'Usage x Equipement'
            result['Type'] = 'Usage x Equipement'
            all_results.append(result)

# Croisements : usage x valeurs
print("   - Usage x Valeurs...")
for var_conso, label_conso in VARS_CONSO.items():
    if var_conso not in df_analyse.columns:
        continue
    for var_val, label_val in VARS_VALEURS.items():
        if var_val not in df_analyse.columns:
            continue
        result = analyze_crosstab(df_analyse, var_conso, var_val, label_conso, label_val)
        if result:
            result['Bloc'] = 'Usage x Valeurs'
            result['Type'] = 'Usage x Valeurs'
            all_results.append(result)

# Croisements : usage x effets (quizz)
print("   - Usage x Effets (Quizz)...")
for var_conso, label_conso in VARS_CONSO.items():
    if var_conso not in df_analyse.columns:
        continue
    for var_eff, label_eff in VARS_EFFETS.items():
        if var_eff not in df_analyse.columns:
            continue
        result = analyze_crosstab(df_analyse, var_conso, var_eff, label_conso, label_eff)
        if result:
            result['Bloc'] = 'Usage x Effets'
            result['Type'] = 'Usage x Effets'
            all_results.append(result)

print(f"\n   Total croisements : {len(all_results)}")

# ============================================================
# 5. CREATION DU DATAFRAME RESULTATS
# ============================================================
print("\n3. Creation du DataFrame resultats...")

df_results = pd.DataFrame(all_results)

# Trier par V de Cramer decroissant
df_results = df_results.sort_values('V Cramer', ascending=False)

# Ajouter un rang
df_results['Rang'] = range(1, len(df_results) + 1)

# Reordonner les colonnes
cols_order = ['Rang', 'Type', 'Bloc', 'Variable 1', 'Label 1', 'Variable 2', 'Label 2',
              'N', 'N pondéré', 'Chi2', 'ddl', 'p-value', 'Significatif', 'V Cramer', 'Force']
df_results = df_results[cols_order]

# ============================================================
# 6. EXPORT EXCEL
# ============================================================
print("\n4. Export Excel...")

output_file = OUTPUT_DIR / f"croisements_chapitre1_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"

with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    # Onglet 1 : Synthese triee par V de Cramer
    df_results.to_excel(writer, sheet_name='Synthese', index=False)

    # Onglet 2 : Significatifs seulement
    df_signif = df_results[df_results['Significatif'] == 'Oui'].copy()
    df_signif.to_excel(writer, sheet_name='Significatifs', index=False)

    # Onglet 3 : Top 20 (les plus parlants)
    df_top = df_results.head(20).copy()
    df_top.to_excel(writer, sheet_name='Top 20', index=False)

    # Onglet par bloc
    for bloc_name in df_results['Bloc'].unique():
        df_bloc = df_results[df_results['Bloc'] == bloc_name].copy()
        sheet_name = bloc_name[:31]  # Excel limite a 31 caracteres
        df_bloc.to_excel(writer, sheet_name=sheet_name, index=False)

    # Onglet : Variables utilisees
    vars_info = []
    for var, label in {**VARS_SOCIO, **VARS_CONSO, **VARS_EQUIP, **VARS_VALEURS, **VARS_EFFETS}.items():
        exists = var in df.columns
        n_valid = df[var].notna().sum() if exists else 0
        n_unique = df[var].nunique() if exists else 0
        vars_info.append({
            'Variable': var,
            'Label': label,
            'Existe': 'Oui' if exists else 'Non',
            'N valides': n_valid,
            'N modalites': n_unique
        })
    df_vars = pd.DataFrame(vars_info)
    df_vars.to_excel(writer, sheet_name='Variables', index=False)

print(f"   -> {output_file}")

# ============================================================
# 7. RESUME CONSOLE
# ============================================================
print("\n" + "=" * 70)
print("RESUME")
print("=" * 70)

print(f"\nTotal croisements : {len(df_results)}")
print(f"Significatifs (p < 0.05) : {len(df_signif)} ({len(df_signif)/len(df_results)*100:.1f}%)")

print("\n--- TOP 10 (V de Cramer) ---")
print(f"{'Rang':<5} {'V Cramer':<10} {'Force':<12} {'Var1':<20} {'Var2':<25}")
print("-" * 75)
for _, row in df_results.head(10).iterrows():
    print(f"{row['Rang']:<5} {row['V Cramer']:<10} {row['Force']:<12} {row['Label 1'][:18]:<20} {row['Label 2'][:23]:<25}")

print("\n--- CROISEMENTS PAR BLOC ---")
for bloc in df_results['Bloc'].unique():
    n = len(df_results[df_results['Bloc'] == bloc])
    n_sig = len(df_results[(df_results['Bloc'] == bloc) & (df_results['Significatif'] == 'Oui')])
    print(f"   {bloc}: {n} croisements, {n_sig} significatifs")

print(f"\n-> Excel genere : {output_file}")
print("=" * 70)
