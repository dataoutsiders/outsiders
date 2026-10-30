# -*- coding: utf-8 -*-
"""
Chapitre 01b - Effets nets equipement -> pratiques
Avec probabilites predites ajustees
"""
import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.api as sm
from pathlib import Path

BASE_DIR = Path('python')
DATA_DIR = BASE_DIR / 'data' / 'francais-information'

# =============================================================================
# CHARGEMENT DES DONNEES
# =============================================================================
print("Chargement des donnees...")
df = pd.read_excel(DATA_DIR / 'base-info-arcom.xlsx')
df['POIDS03'] = df['POIDS03'].astype(str).str.replace(',', '.').astype(float)
print(f"Echantillon : {len(df)} repondants")

# =============================================================================
# CREATION DES VARIABLES
# =============================================================================

# Variables binaires d'equipement
equipements = {
    'POSSEDE_TV': ('RS16_R_1', 'Televiseur'),
    'POSSEDE_SMARTPHONE': ('RS16_R_4', 'Smartphone'),
    'POSSEDE_ORDI_PORTABLE': ('RS16_R_6', 'Ordinateur portable'),
    'POSSEDE_TABLETTE': ('RS16_R_7', 'Tablette'),
    'POSSEDE_MONTRE_CONNECTEE': ('RS16_R_11', 'Montre connectee'),
    'POSSEDE_ENCEINTE_CONNECTEE': ('RS16_R_9', 'Enceinte connectee'),
}

for new_var, (source_var, label) in equipements.items():
    if source_var in df.columns:
        df[new_var] = (df[source_var].isin([1, 2])).astype(int)

# Variables de pratiques (VD)
df['PRATIQUE_TV_PRINCIPALE'] = (df['NEWS1BIS_R'] == 2).astype(int)
df['PRATIQUE_RS_PRINCIPALE'] = (df['NEWS1BIS_R'] == 8).astype(int)

# Variable de capital economique (a creer)
# RS14_R = revenus du foyer, RS7_R = nombre de personnes
# On simplifie en utilisant RS14_R directement
df['CAPITAL_ECO'] = pd.cut(
    df['RS14_R'],
    bins=[0, 2, 4, 6],
    labels=['Faible', 'Moyen', 'Eleve']
)

# =============================================================================
# LABELS
# =============================================================================
AGE_LABELS = {
    1: '15-17 ans', 2: '18-24 ans', 3: '25-34 ans', 4: '35-44 ans',
    5: '45-59 ans', 6: '60-69 ans', 7: '70 ans et +'
}

EQUIP_LABELS = {
    0: 'Ne possede pas',
    1: 'Possede'
}

# =============================================================================
# VARIABLES DE CONTROLE
# =============================================================================
# On controle : age, capital economique
controle_vars = [
    ('RS2C_RECODE_AG_R', 'Age'),
    ('CAPITAL_ECO', 'Capital economique'),
]

# =============================================================================
# FONCTIONS
# =============================================================================

def test_effet_net(df, var_vi, var_vd, controle_vars, poids='POIDS03'):
    """
    Teste si var_vi a un effet significatif sur var_vd
    en controlant les autres variables.
    Retourne p-value du test de Wald et le modele.
    """
    vi_names = [var_vi] + [v[0] for v in controle_vars]
    cols_needed = [var_vd, poids] + vi_names

    df_reg = df[cols_needed].dropna().copy()

    if len(df_reg) < 100:
        return None, None, len(df_reg)

    # Convertir en codes numeriques
    for col in vi_names:
        if df_reg[col].dtype == 'object' or df_reg[col].dtype.name == 'category':
            df_reg[col] = df_reg[col].astype('category').cat.codes

    # Creer des dummies
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

        # Test de Wald pour var_vi
        var_vi_cols = [c for c in X.columns if c.startswith(var_vi + '_')]
        if len(var_vi_cols) == 0:
            # Variable binaire, pas de dummy supplementaire si drop_first
            # On cherche la colonne directement
            var_vi_cols = [c for c in X.columns if var_vi in c]

        if len(var_vi_cols) > 0:
            var_vi_indices = [X.columns.get_loc(c) for c in var_vi_cols]
            R = np.zeros((len(var_vi_indices), len(X.columns)))
            for i, idx in enumerate(var_vi_indices):
                R[i, idx] = 1
            wald_test = result.wald_test(R)
            p_value = float(wald_test.pvalue)
        else:
            p_value = 1.0

        return p_value, result, len(df_reg)
    except Exception as e:
        print(f"  Erreur regression: {e}")
        return None, None, len(df_reg)


def get_predicted_probabilities(df, var_vi, var_vd, controle_vars, poids='POIDS03'):
    """
    Calcule les probabilites predites ajustees pour chaque categorie de var_vi.
    Les autres variables sont fixees a leur moyenne.
    """
    vi_names = [var_vi] + [v[0] for v in controle_vars]
    cols_needed = [var_vd, poids] + vi_names

    df_reg = df[cols_needed].dropna().copy()

    if len(df_reg) < 100:
        return None

    # Sauvegarder le mapping avant conversion
    cat_mappings = {}
    for col in vi_names:
        if df_reg[col].dtype == 'object' or df_reg[col].dtype.name == 'category':
            cat_series = df_reg[col].astype('category')
            cat_mappings[col] = dict(enumerate(cat_series.cat.categories))
            df_reg[col] = cat_series.cat.codes
        else:
            # Variable numerique
            cat_mappings[col] = {int(v): int(v) for v in df_reg[col].unique()}

    # Creer des dummies
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
    except:
        return None

    # Predictions pour chaque categorie de var_vi
    predictions = {}
    X_means = X.mean()
    categories = sorted(df_reg[var_vi].unique())

    for cat in categories:
        X_pred = X_means.copy()

        # Mettre a jour les dummies de var_vi pour cette categorie
        for col in X_pred.index:
            if col.startswith(var_vi + '_'):
                dummy_cat = int(col.split('_')[-1])
                X_pred[col] = 1.0 if dummy_cat == cat else 0.0

        prob = result.predict(X_pred.values.reshape(1, -1))[0]

        # Obtenir le label
        original_value = cat_mappings[var_vi].get(int(cat), int(cat))
        if var_vi in ['POSSEDE_TV', 'POSSEDE_SMARTPHONE', 'POSSEDE_ORDI_PORTABLE',
                      'POSSEDE_TABLETTE', 'POSSEDE_MONTRE_CONNECTEE', 'POSSEDE_ENCEINTE_CONNECTEE']:
            cat_label = EQUIP_LABELS.get(int(original_value), str(original_value))
        else:
            cat_label = str(original_value)

        predictions[cat_label] = round(prob * 100, 1)

    return predictions


def get_distribution_brute(df, var_vi, var_vd, poids='POIDS03'):
    """Calcule la distribution brute (non ajustee)"""
    results = {}
    for val in sorted(df[var_vi].dropna().unique()):
        subset = df[df[var_vi] == val]
        total = subset[poids].sum()
        oui = subset[subset[var_vd] == 1][poids].sum()
        pct = oui / total * 100 if total > 0 else 0

        if var_vi in ['POSSEDE_TV', 'POSSEDE_SMARTPHONE', 'POSSEDE_ORDI_PORTABLE',
                      'POSSEDE_TABLETTE', 'POSSEDE_MONTRE_CONNECTEE', 'POSSEDE_ENCEINTE_CONNECTEE']:
            label = EQUIP_LABELS.get(int(val), str(val))
        else:
            label = str(val)

        results[label] = round(pct, 1)
    return results


# =============================================================================
# ANALYSE DES EFFETS NETS
# =============================================================================
print("\n" + "=" * 80)
print("### EFFETS NETS : EQUIPEMENT -> PRATIQUES ###")
print("### Controle : Age + Capital economique ###")
print("=" * 80)

vi_equipements = [
    ('POSSEDE_TV', 'Possede TV'),
    ('POSSEDE_SMARTPHONE', 'Possede smartphone'),
    ('POSSEDE_ORDI_PORTABLE', 'Possede ordi portable'),
    ('POSSEDE_MONTRE_CONNECTEE', 'Possede montre connectee'),
    ('POSSEDE_ENCEINTE_CONNECTEE', 'Possede enceinte connectee'),
]

vd_pratiques = [
    ('PRATIQUE_TV_PRINCIPALE', 'TV source principale'),
    ('PRATIQUE_RS_PRINCIPALE', 'RS source principale'),
]

results_all = []

for var_vd, label_vd in vd_pratiques:
    print(f"\n{'='*80}")
    print(f"### VD : {label_vd} ###")
    print("="*80)

    for var_vi, label_vi in vi_equipements:
        print(f"\n--- {label_vi} -> {label_vd} ---")

        # Distribution brute
        dist_brute = get_distribution_brute(df, var_vi, var_vd)
        print(f"\nDistribution brute:")
        for cat, pct in dist_brute.items():
            print(f"  {cat}: {pct}%")

        # Test effet net
        p_value, model, n = test_effet_net(df, var_vi, var_vd, controle_vars)

        if p_value is not None:
            effet_net = p_value < 0.05
            signif = "***" if p_value < 0.001 else "**" if p_value < 0.01 else "*" if p_value < 0.05 else "NS"
            print(f"\nEffet net (p-value Wald): {p_value:.4f} {signif}")
            print(f"Effet net confirme: {'OUI' if effet_net else 'NON'}")
            print(f"N analyse: {n}")

            # Probabilites predites ajustees
            pred_ajustees = get_predicted_probabilities(df, var_vi, var_vd, controle_vars)

            if pred_ajustees:
                print(f"\nProbabilites predites ajustees (age et capital eco fixes a la moyenne):")
                for cat, pct in pred_ajustees.items():
                    print(f"  {cat}: {pct}%")

                # Calcul de l'ecart
                if 'Possede' in pred_ajustees and 'Ne possede pas' in pred_ajustees:
                    ecart_ajuste = pred_ajustees['Possede'] - pred_ajustees['Ne possede pas']
                    print(f"\nEcart ajuste: {ecart_ajuste:+.1f} pts")

                    # Comparaison avec ecart brut
                    if 'Possede' in dist_brute and 'Ne possede pas' in dist_brute:
                        ecart_brut = dist_brute['Possede'] - dist_brute['Ne possede pas']
                        print(f"Ecart brut: {ecart_brut:+.1f} pts")
                        print(f"Reduction due aux controles: {abs(ecart_brut) - abs(ecart_ajuste):.1f} pts")

                # Stocker les resultats
                results_all.append({
                    'var_vi': var_vi,
                    'label_vi': label_vi,
                    'var_vd': var_vd,
                    'label_vd': label_vd,
                    'pct_brut_non': dist_brute.get('Ne possede pas'),
                    'pct_brut_oui': dist_brute.get('Possede'),
                    'pct_ajuste_non': pred_ajustees.get('Ne possede pas'),
                    'pct_ajuste_oui': pred_ajustees.get('Possede'),
                    'p_value': p_value,
                    'effet_net': effet_net,
                    'n': n
                })
        else:
            print(f"\nRegression impossible (n={n})")

# =============================================================================
# TABLEAU RECAPITULATIF
# =============================================================================
print("\n" + "=" * 80)
print("### TABLEAU RECAPITULATIF ###")
print("=" * 80)

print("\n### TV COMME SOURCE PRINCIPALE ###")
print(f"{'Equipement':<25} | {'Brut':<15} | {'Ajuste':<15} | {'p-value':<10} | Effet net")
print("-" * 85)

for r in results_all:
    if r['var_vd'] == 'PRATIQUE_TV_PRINCIPALE':
        brut = f"{r['pct_brut_non']:.0f}% -> {r['pct_brut_oui']:.0f}%"
        ajuste = f"{r['pct_ajuste_non']:.0f}% -> {r['pct_ajuste_oui']:.0f}%"
        effet = "OUI" if r['effet_net'] else "NON"
        print(f"{r['label_vi']:<25} | {brut:<15} | {ajuste:<15} | {r['p_value']:.4f}    | {effet}")

print("\n### RS COMME SOURCE PRINCIPALE ###")
print(f"{'Equipement':<25} | {'Brut':<15} | {'Ajuste':<15} | {'p-value':<10} | Effet net")
print("-" * 85)

for r in results_all:
    if r['var_vd'] == 'PRATIQUE_RS_PRINCIPALE':
        brut = f"{r['pct_brut_non']:.0f}% -> {r['pct_brut_oui']:.0f}%"
        ajuste = f"{r['pct_ajuste_non']:.0f}% -> {r['pct_ajuste_oui']:.0f}%"
        effet = "OUI" if r['effet_net'] else "NON"
        print(f"{r['label_vi']:<25} | {brut:<15} | {ajuste:<15} | {r['p_value']:.4f}    | {effet}")

# =============================================================================
# INTERPRETATION
# =============================================================================
print("\n" + "=" * 80)
print("### INTERPRETATION ###")
print("=" * 80)

print("""
LECTURE DES RESULTATS :
- 'Brut' : pourcentage observe dans les donnees (Ne possede pas -> Possede)
- 'Ajuste' : probabilite predite a age et capital economique moyens
- 'Effet net' : OUI si l'equipement a un effet independant de l'age et du capital eco

Si l'ecart ajuste est proche de l'ecart brut : l'equipement a un effet propre
Si l'ecart ajuste est reduit : l'effet est en partie du a l'age ou au capital eco
""")
