"""
Analyse des interactions : Est-ce que les effets varient selon l'âge et le diplôme ?

Objectif : Tester si les effets de l'équipement et des valeurs sur l'usage RS/TV
varient selon l'âge et le diplôme (hétérogénéité des effets).

Méthode : Régression logistique avec termes d'interaction
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# CHARGEMENT DES DONNÉES
# =============================================================================

print("=" * 70)
print("ANALYSE DES INTERACTIONS : EQUIPEMENT ET VALEURS -> USAGE RS/TV")
print("=" * 70)

df = pd.read_excel('python/data/francais-information/base-info-arcom.xlsx')
df['POIDS03'] = df['POIDS03'].astype(str).str.replace(',', '.').astype(float)

# =============================================================================
# CRÉATION DES VARIABLES
# =============================================================================

# --- Variables dépendantes : Usage RS et TV ---
news1_cols = [f'NEWS1_R1_{i}' for i in range(1, 10) if f'NEWS1_R1_{i}' in df.columns]

def utilise_source(row, code):
    for col in news1_cols:
        if pd.notna(row[col]) and row[col] == code:
            return 1
    return 0

df['UTILISE_TV'] = df.apply(lambda r: utilise_source(r, 1), axis=1)
df['UTILISE_RS'] = df.apply(lambda r: utilise_source(r, 3), axis=1)

print(f"\nEffectifs : TV={df['UTILISE_TV'].sum()}, RS={df['UTILISE_RS'].sum()}, Total={len(df)}")

# --- Âge en 3 catégories ---
age = df['RS2C_RECODE_AG_R']
df['AGE_3CAT'] = pd.cut(
    age,
    bins=[0, 3.5, 5.5, 8],  # 1-3 = jeunes, 4-5 = moyen, 6-7 = seniors
    labels=['15-34 ans', '35-59 ans', '60+ ans']
)
print(f"\nÂge 3 catégories :\n{df['AGE_3CAT'].value_counts()}")

# --- Diplôme en 3 catégories ---
# RS5_R : 1-4 = sans bac, 5-6 = bac/bac+2, 7-9 = bac+3+
diplome = df['RS5_R']
df['DIPLOME_3CAT'] = pd.cut(
    diplome,
    bins=[0, 4.5, 6.5, 10],
    labels=['< Bac', 'Bac à Bac+2', 'Bac+3 et +']
)
print(f"\nDiplôme 3 catégories :\n{df['DIPLOME_3CAT'].value_counts()}")

# --- Équipement (RS16_R_X : 1 ou 2 = possède, 3 = aucun) ---
df['POSSEDE_TV'] = df['RS16_R_1'].isin([1, 2]).astype(int)
df['POSSEDE_SMARTPHONE'] = df['RS16_R_4'].isin([1, 2]).astype(int)
df['POSSEDE_TABLETTE'] = df['RS16_R_7'].isin([1, 2]).astype(int)
df['POSSEDE_ENCEINTE'] = df['RS16_R_9'].isin([1, 2]).astype(int)
df['POSSEDE_MONTRE'] = df['RS16_R_11'].isin([1, 2]).astype(int)

print(f"\nÉquipement (% possession) :")
for eq in ['POSSEDE_TV', 'POSSEDE_SMARTPHONE', 'POSSEDE_TABLETTE', 'POSSEDE_ENCEINTE', 'POSSEDE_MONTRE']:
    pct = df[eq].mean() * 100
    print(f"  {eq}: {pct:.1f}%")

# --- Confiance sources (INF3_R1 : récap ST Confiance) ---
# Les colonnes INF3_R1_X contiennent 1 si confiance, 0 sinon
# Colonne 1 = journalistes, 6 = créateurs, 9 = proches
inf3_cols = [c for c in df.columns if c.startswith('INF3_R1_')]
print(f"\nColonnes INF3_R1 trouvées : {inf3_cols[:10]}")

# Chercher les bonnes colonnes - INF3_R1_X contient le code de l'item si confiance
# Il faut regarder la valeur dans la colonne (c'est une question multi-choix)
if 'INF3_R1_1' in df.columns:
    # Vérifier le format des données
    print(f"  Valeurs INF3_R1_1: {df['INF3_R1_1'].value_counts().head()}")
    print(f"  Valeurs INF3_R1_6: {df['INF3_R1_6'].value_counts().head() if 'INF3_R1_6' in df.columns else 'N/A'}")

    # Format récap ST Confiance : 1 = cité (confiance), NaN = non cité
    df['CONF_JOURNALISTES'] = df['INF3_R1_1'].notna().astype(int)
    df['CONF_CREATEURS'] = df['INF3_R1_6'].notna().astype(int) if 'INF3_R1_6' in df.columns else 0
    df['CONF_PROCHES'] = df['INF3_R1_9'].notna().astype(int) if 'INF3_R1_9' in df.columns else 0
else:
    print("Attention : colonnes INF3_R1_X non trouvees")
    df['CONF_JOURNALISTES'] = 0
    df['CONF_CREATEURS'] = 0
    df['CONF_PROCHES'] = 0

# --- Attitudes sources (ATTSOURCES_R1 : récap ST D'accord) ---
# Colonne 3 = "Il y a rarement une seule vérité"
if 'ATTSOURCES_R1_3' in df.columns:
    print(f"  Valeurs ATTSOURCES_R1_3: {df['ATTSOURCES_R1_3'].value_counts().head()}")
    df['RAREMENT_UNE_VERITE'] = df['ATTSOURCES_R1_3'].notna().astype(int)
else:
    df['RAREMENT_UNE_VERITE'] = 0

# --- Orientation politique (NOU1_R : 0-10) ---
# Recodage 3 categories : Gauche (1-4 = 0-3), Centre (5-7 = 4-6), Droite (8-11 = 7-10)
# Attention : les labels dans datamap montrent que code 1 = "0", code 6 = "Centre", etc.
pol = df['NOU1_R']
df['POLITIQUE_3CAT'] = 'Centre'
df.loc[pol.isin([1, 2, 3, 4]), 'POLITIQUE_3CAT'] = 'Gauche'  # codes 1-4 = valeurs 0-3
df.loc[pol.isin([8, 9, 10, 11]), 'POLITIQUE_3CAT'] = 'Droite'  # codes 8-11 = valeurs 7-10

print(f"\nPolitique 3 catégories :\n{df['POLITIQUE_3CAT'].value_counts()}")

# --- Politique 5 catégories ---
df['POLITIQUE_5CAT'] = 'Centre'
df.loc[pol.isin([1, 2]), 'POLITIQUE_5CAT'] = 'Extr. gauche'
df.loc[pol.isin([3, 4]), 'POLITIQUE_5CAT'] = 'Gauche'
df.loc[pol.isin([8, 9]), 'POLITIQUE_5CAT'] = 'Droite'
df.loc[pol.isin([10, 11]), 'POLITIQUE_5CAT'] = 'Extr. droite'

print(f"\nPolitique 5 catégories :\n{df['POLITIQUE_5CAT'].value_counts()}")

print(f"\nConfiance (% oui) :")
for conf in ['CONF_JOURNALISTES', 'CONF_CREATEURS', 'CONF_PROCHES', 'RAREMENT_UNE_VERITE']:
    pct = df[conf].mean() * 100
    print(f"  {conf}: {pct:.1f}%")

# =============================================================================
# V DE CRAMER : FORCE D'ASSOCIATION
# =============================================================================

def cramers_v_weighted(x, y, weights):
    """Calcule V de Cramer pondéré"""
    ct = pd.crosstab(x, y, values=weights, aggfunc='sum').fillna(0)
    chi2 = stats.chi2_contingency(ct)[0]
    n = ct.sum().sum()
    min_dim = min(ct.shape) - 1
    return np.sqrt(chi2 / (n * min_dim)) if min_dim > 0 and n > 0 else 0

print("\n" + "=" * 70)
print("V DE CRAMER : FORCE D'ASSOCIATION AVEC USAGE RS")
print("=" * 70)

variables_test = [
    ('AGE_3CAT', 'Âge'),
    ('DIPLOME_3CAT', 'Diplôme'),
    ('POSSEDE_TV', 'Possède TV'),
    ('POSSEDE_SMARTPHONE', 'Possède smartphone'),
    ('POSSEDE_TABLETTE', 'Possède tablette'),
    ('POSSEDE_ENCEINTE', 'Possède enceinte connectée'),
    ('POSSEDE_MONTRE', 'Possède montre connectée'),
    ('CONF_JOURNALISTES', 'Confiance journalistes'),
    ('CONF_CREATEURS', 'Confiance créateurs'),
    ('CONF_PROCHES', 'Confiance proches'),
    ('RAREMENT_UNE_VERITE', 'Rarement une seule vérité'),
    ('POLITIQUE_3CAT', 'Orientation politique'),
]

results_cramer = []
for var, label in variables_test:
    mask = df[var].notna() & df['UTILISE_RS'].notna() & df['POIDS03'].notna()
    if mask.sum() > 100:
        v_rs = cramers_v_weighted(df.loc[mask, var], df.loc[mask, 'UTILISE_RS'], df.loc[mask, 'POIDS03'])
        v_tv = cramers_v_weighted(df.loc[mask, var], df.loc[mask, 'UTILISE_TV'], df.loc[mask, 'POIDS03'])
        results_cramer.append({'Variable': label, 'V_RS': v_rs, 'V_TV': v_tv})
        print(f"{label:30} -> RS: {v_rs:.3f}  |  TV: {v_tv:.3f}")

# =============================================================================
# TEST DES INTERACTIONS
# =============================================================================

print("\n" + "=" * 70)
print("TEST DES INTERACTIONS")
print("=" * 70)

def test_interaction(df, var_dep, var_ind, var_inter, label_ind, label_inter):
    """
    Teste si l'interaction var_ind x var_inter est significative.
    Compare un modèle avec interaction vs sans interaction (test du rapport de vraisemblance).
    """
    # Préparer les données
    cols = [var_dep, var_ind, var_inter, 'POIDS03']
    df_reg = df[cols].dropna().copy()

    if len(df_reg) < 100:
        return None

    # Convertir en dummies
    if df_reg[var_ind].dtype == 'object' or isinstance(df_reg[var_ind].iloc[0], str):
        dummies_ind = pd.get_dummies(df_reg[var_ind], prefix=var_ind, drop_first=True)
    else:
        dummies_ind = pd.DataFrame({var_ind: df_reg[var_ind].values})

    if df_reg[var_inter].dtype == 'object' or isinstance(df_reg[var_inter].iloc[0], str):
        dummies_inter = pd.get_dummies(df_reg[var_inter], prefix=var_inter, drop_first=True)
    else:
        dummies_inter = pd.DataFrame({var_inter: df_reg[var_inter].values})

    # Créer les termes d'interaction
    interaction_terms = pd.DataFrame()
    for col_ind in dummies_ind.columns:
        for col_inter in dummies_inter.columns:
            interaction_terms[f'{col_ind}_X_{col_inter}'] = dummies_ind[col_ind].values * dummies_inter[col_inter].values

    # Modèle sans interaction
    X_no_inter = pd.concat([dummies_ind.reset_index(drop=True), dummies_inter.reset_index(drop=True)], axis=1)
    X_no_inter = sm.add_constant(X_no_inter)

    # Modèle avec interaction
    X_with_inter = pd.concat([X_no_inter.reset_index(drop=True), interaction_terms.reset_index(drop=True)], axis=1)

    y = df_reg[var_dep].values
    weights = df_reg['POIDS03'].values

    try:
        model_no_inter = sm.GLM(y, X_no_inter.astype(float), family=sm.families.Binomial(), freq_weights=weights).fit()
        model_with_inter = sm.GLM(y, X_with_inter.astype(float), family=sm.families.Binomial(), freq_weights=weights).fit()

        # Test du rapport de vraisemblance
        lr_stat = 2 * (model_with_inter.llf - model_no_inter.llf)
        df_diff = len(interaction_terms.columns)
        p_value = 1 - stats.chi2.cdf(lr_stat, df_diff)

        return {
            'var_ind': label_ind,
            'var_inter': label_inter,
            'lr_stat': lr_stat,
            'df': df_diff,
            'p_value': p_value,
            'significatif': p_value < 0.05
        }
    except Exception as e:
        print(f"  Erreur pour {label_ind} x {label_inter}: {e}")
        return None

# Variables à tester
interactions_a_tester = [
    # Equipement x Age
    ('POSSEDE_SMARTPHONE', 'AGE_3CAT', 'Smartphone', 'Âge'),
    ('POSSEDE_TABLETTE', 'AGE_3CAT', 'Tablette', 'Âge'),
    ('POSSEDE_ENCEINTE', 'AGE_3CAT', 'Enceinte connectée', 'Âge'),
    ('POSSEDE_TV', 'AGE_3CAT', 'TV', 'Âge'),

    # Equipement x Diplome
    ('POSSEDE_SMARTPHONE', 'DIPLOME_3CAT', 'Smartphone', 'Diplôme'),
    ('POSSEDE_TABLETTE', 'DIPLOME_3CAT', 'Tablette', 'Diplôme'),
    ('POSSEDE_ENCEINTE', 'DIPLOME_3CAT', 'Enceinte connectée', 'Diplôme'),

    # Valeurs x Age
    ('CONF_JOURNALISTES', 'AGE_3CAT', 'Conf. journalistes', 'Âge'),
    ('CONF_CREATEURS', 'AGE_3CAT', 'Conf. créateurs', 'Âge'),
    ('RAREMENT_UNE_VERITE', 'AGE_3CAT', 'Rarement une vérité', 'Âge'),

    # Valeurs x Diplome
    ('CONF_JOURNALISTES', 'DIPLOME_3CAT', 'Conf. journalistes', 'Diplôme'),
    ('CONF_CREATEURS', 'DIPLOME_3CAT', 'Conf. créateurs', 'Diplôme'),
    ('RAREMENT_UNE_VERITE', 'DIPLOME_3CAT', 'Rarement une vérité', 'Diplôme'),

    # Politique x Age et Diplome
    ('POLITIQUE_3CAT', 'AGE_3CAT', 'Politique', 'Âge'),
    ('POLITIQUE_3CAT', 'DIPLOME_3CAT', 'Politique', 'Diplôme'),
]

print("\n--- INTERACTIONS POUR USAGE RS ---\n")
results_inter_rs = []
for var_ind, var_inter, label_ind, label_inter in interactions_a_tester:
    result = test_interaction(df, 'UTILISE_RS', var_ind, var_inter, label_ind, label_inter)
    if result:
        results_inter_rs.append(result)
        sig = "***" if result['p_value'] < 0.001 else "**" if result['p_value'] < 0.01 else "*" if result['p_value'] < 0.05 else ""
        print(f"{label_ind:20} x {label_inter:10} : LR={result['lr_stat']:6.2f}, p={result['p_value']:.4f} {sig}")

print("\n--- INTERACTIONS POUR USAGE TV ---\n")
results_inter_tv = []
for var_ind, var_inter, label_ind, label_inter in interactions_a_tester:
    result = test_interaction(df, 'UTILISE_TV', var_ind, var_inter, label_ind, label_inter)
    if result:
        results_inter_tv.append(result)
        sig = "***" if result['p_value'] < 0.001 else "**" if result['p_value'] < 0.01 else "*" if result['p_value'] < 0.05 else ""
        print(f"{label_ind:20} x {label_inter:10} : LR={result['lr_stat']:6.2f}, p={result['p_value']:.4f} {sig}")

# =============================================================================
# RÉSUMÉ : QUELLES INTERACTIONS SONT SIGNIFICATIVES ?
# =============================================================================

print("\n" + "=" * 70)
print("RÉSUMÉ : INTERACTIONS SIGNIFICATIVES (p < 0.05)")
print("=" * 70)

print("\n--- Usage RS ---")
sig_rs = [r for r in results_inter_rs if r['significatif']]
if sig_rs:
    for r in sig_rs:
        print(f"  [X] {r['var_ind']} x {r['var_inter']} (p={r['p_value']:.4f})")
else:
    print("  Aucune interaction significative")

print("\n--- Usage TV ---")
sig_tv = [r for r in results_inter_tv if r['significatif']]
if sig_tv:
    for r in sig_tv:
        print(f"  [X] {r['var_ind']} x {r['var_inter']} (p={r['p_value']:.4f})")
else:
    print("  Aucune interaction significative")

# =============================================================================
# SI INTERACTIONS SIGNIFICATIVES : MONTRER LES EFFETS PAR GROUPE
# =============================================================================

print("\n" + "=" * 70)
print("EFFETS STRATIFIÉS PAR ÂGE")
print("=" * 70)

def get_effect_by_group(df, var_dep, var_ind, var_group, label_ind):
    """Calcule l'effet de var_ind sur var_dep pour chaque groupe de var_group"""
    results = []
    for group in df[var_group].dropna().unique():
        mask = (df[var_group] == group) & df[var_ind].notna() & df[var_dep].notna() & df['POIDS03'].notna()
        df_group = df[mask]

        if len(df_group) < 50:
            continue

        # Calculer % usage parmi ceux qui ont vs n'ont pas l'équipement/valeur
        if df_group[var_ind].nunique() == 2:  # Variable binaire
            pct_avec = (df_group[df_group[var_ind] == 1][var_dep] * df_group[df_group[var_ind] == 1]['POIDS03']).sum() / df_group[df_group[var_ind] == 1]['POIDS03'].sum() * 100
            pct_sans = (df_group[df_group[var_ind] == 0][var_dep] * df_group[df_group[var_ind] == 0]['POIDS03']).sum() / df_group[df_group[var_ind] == 0]['POIDS03'].sum() * 100
            diff = pct_avec - pct_sans
            results.append({
                'groupe': group,
                'pct_avec': pct_avec,
                'pct_sans': pct_sans,
                'diff': diff
            })

    return results

# Montrer les effets de l'équipement par groupe d'âge
print("\n--- Effet SMARTPHONE -> Usage RS, par age ---")
effects = get_effect_by_group(df, 'UTILISE_RS', 'POSSEDE_SMARTPHONE', 'AGE_3CAT', 'Smartphone')
for e in sorted(effects, key=lambda x: str(x['groupe'])):
    print(f"  {e['groupe']:12} : avec={e['pct_avec']:5.1f}%, sans={e['pct_sans']:5.1f}%, diff={e['diff']:+5.1f}pp")

print("\n--- Effet TABLETTE -> Usage RS, par age ---")
effects = get_effect_by_group(df, 'UTILISE_RS', 'POSSEDE_TABLETTE', 'AGE_3CAT', 'Tablette')
for e in sorted(effects, key=lambda x: str(x['groupe'])):
    print(f"  {e['groupe']:12} : avec={e['pct_avec']:5.1f}%, sans={e['pct_sans']:5.1f}%, diff={e['diff']:+5.1f}pp")

print("\n--- Effet ENCEINTE CONNECTEE -> Usage RS, par age ---")
effects = get_effect_by_group(df, 'UTILISE_RS', 'POSSEDE_ENCEINTE', 'AGE_3CAT', 'Enceinte')
for e in sorted(effects, key=lambda x: str(x['groupe'])):
    print(f"  {e['groupe']:12} : avec={e['pct_avec']:5.1f}%, sans={e['pct_sans']:5.1f}%, diff={e['diff']:+5.1f}pp")

print("\n--- Effet CONFIANCE CREATEURS -> Usage RS, par age ---")
effects = get_effect_by_group(df, 'UTILISE_RS', 'CONF_CREATEURS', 'AGE_3CAT', 'Conf. créateurs')
for e in sorted(effects, key=lambda x: str(x['groupe'])):
    print(f"  {e['groupe']:12} : avec={e['pct_avec']:5.1f}%, sans={e['pct_sans']:5.1f}%, diff={e['diff']:+5.1f}pp")

print("\n--- Effet POSSEDE TV -> Usage TV, par age ---")
effects = get_effect_by_group(df, 'UTILISE_TV', 'POSSEDE_TV', 'AGE_3CAT', 'TV')
for e in sorted(effects, key=lambda x: str(x['groupe'])):
    print(f"  {e['groupe']:12} : avec={e['pct_avec']:5.1f}%, sans={e['pct_sans']:5.1f}%, diff={e['diff']:+5.1f}pp")

print("\n" + "=" * 70)
print("CONCLUSION")
print("=" * 70)
print("""
Si des interactions sont significatives, cela signifie que l'effet varie selon le groupe.
-> Il faut stratifier ou presenter les resultats par groupe.

Si aucune interaction n'est significative, l'effet est homogène.
-> Une regression globale avec controles suffit.
""")
