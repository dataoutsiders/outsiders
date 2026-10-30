"""
Analyse des Correspondances Multiples (ACM) sur les pratiques d'information
Génère un graphique interactif (HTML) et une image (PNG)
"""
import pandas as pd
import numpy as np
import prince
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from pathlib import Path

# Chemins
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data" / "francais-information"
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

print("=" * 60)
print("ANALYSE DES CORRESPONDANCES MULTIPLES (ACM)")
print("=" * 60)

# Charger les données
print("\n1. Chargement des donnees...")
df = pd.read_excel(DATA_DIR / "base-info-arcom.xlsx")
print(f"   {len(df)} repondants, {len(df.columns)} variables")

# Charger le dictionnaire pour les labels
with open(DATA_DIR / "dictionnaire.json", "r", encoding="utf-8") as f:
    dico = json.load(f)

# Variables actives pour l'ACM
VARS_ACTIVES = [
    # Sources d'information (fréquence)
    "NEWS1_R_1",  # TV
    "NEWS1_R_2",  # Radio
    "NEWS1_R_3",  # Presse écrite
    "NEWS1_R_4",  # Sites/apps médias
    "NEWS1_R_5",  # Réseaux sociaux
    "NEWS1_R_6",  # Podcasts
    "NEWS1_R_7",  # Entourage
    # Intérêt global
    "INT1_R",
    # Confiance
    "CONF1_R",
]

# Variables supplémentaires (projetées)
VARS_SUPP = [
    "RS1_R",           # Genre
    "RS2C_RECODE_AG_R", # Âge
    "CSPIND_R",        # CSP
]

# Labels pour les variables
VAR_LABELS = {
    "NEWS1_R_1": "TV",
    "NEWS1_R_2": "Radio",
    "NEWS1_R_3": "Presse",
    "NEWS1_R_4": "Sites web",
    "NEWS1_R_5": "Reseaux sociaux",
    "NEWS1_R_6": "Podcasts",
    "NEWS1_R_7": "Entourage",
    "INT1_R": "Interet info",
    "CONF1_R": "Confiance",
    "RS1_R": "Genre",
    "RS2C_RECODE_AG_R": "Age",
    "CSPIND_R": "CSP",
}

# Labels pour les modalités de fréquence (NEWS1)
FREQ_LABELS = {
    1: "Tous les jours",
    2: "Plusieurs fois/sem",
    3: "1 fois/sem",
    4: "1-3 fois/mois",
    5: "Moins souvent",
    6: "Jamais",
}

# Labels intérêt
INT_LABELS = {
    1: "Tres interesse",
    2: "Assez interesse",
    3: "Peu interesse",
    4: "Pas interesse",
}

# Labels confiance
CONF_LABELS = {
    1: "Tout a fait",
    2: "Plutot d'accord",
    3: "Ni/ni",
    4: "Plutot pas",
    5: "Pas du tout",
}

# Labels socio-demo
GENRE_LABELS = {1: "Homme", 2: "Femme"}
AGE_LABELS = {1: "15-17", 2: "18-24", 3: "25-34", 4: "35-44", 5: "45-59", 6: "60-69", 7: "70+"}
CSP_LABELS = {1: "CSP+", 2: "CSP-", 3: "Inactif", 4: "NSP"}


def get_modality_label(var, code):
    """Retourne un label lisible pour une modalité."""
    code = int(float(code)) if not pd.isna(code) else code
    var_short = VAR_LABELS.get(var, var)

    if var.startswith("NEWS1"):
        mod_label = FREQ_LABELS.get(code, str(code))
    elif var == "INT1_R":
        mod_label = INT_LABELS.get(code, str(code))
    elif var == "CONF1_R":
        mod_label = CONF_LABELS.get(code, str(code))
    elif var == "RS1_R":
        mod_label = GENRE_LABELS.get(code, str(code))
    elif var == "RS2C_RECODE_AG_R":
        mod_label = AGE_LABELS.get(code, str(code))
    elif var == "CSPIND_R":
        mod_label = CSP_LABELS.get(code, str(code))
    else:
        mod_label = str(code)

    return f"{var_short}: {mod_label}"


# Préparation des données
print("\n2. Preparation des donnees...")

# Sélectionner et nettoyer les variables actives
df_acm = df[VARS_ACTIVES + VARS_SUPP].copy()

# Convertir en catégoriel (string) pour prince
for col in VARS_ACTIVES + VARS_SUPP:
    df_acm[col] = df_acm[col].astype(str)

# Supprimer les lignes avec valeurs manquantes sur les variables actives
df_acm_clean = df_acm.dropna(subset=VARS_ACTIVES)
df_acm_clean = df_acm_clean[~df_acm_clean[VARS_ACTIVES].isin(['nan', 'None', '']).any(axis=1)]

print(f"   {len(df_acm_clean)} repondants apres nettoyage")

# ACM
print("\n3. Calcul de l'ACM...")
mca = prince.MCA(
    n_components=5,
    n_iter=3,
    copy=True,
    check_input=True,
    engine='sklearn',
    random_state=42
)

# Fit sur les variables actives uniquement
mca = mca.fit(df_acm_clean[VARS_ACTIVES])

# Coordonnées des individus
coords_ind = mca.row_coordinates(df_acm_clean[VARS_ACTIVES])
coords_ind.columns = [f"Dim{i+1}" for i in range(coords_ind.shape[1])]

# Coordonnées des modalités
coords_mod = mca.column_coordinates(df_acm_clean[VARS_ACTIVES])
coords_mod.columns = [f"Dim{i+1}" for i in range(coords_mod.shape[1])]

# Inertie expliquée
inertia_pct = mca.percentage_of_variance_
print(f"\n   Inertie expliquee:")
print(f"   - Axe 1: {inertia_pct[0]:.1f}%")
print(f"   - Axe 2: {inertia_pct[1]:.1f}%")
print(f"   - Axes 1+2: {sum(inertia_pct[:2]):.1f}%")

# Ajouter les variables supplémentaires aux coordonnées des individus
for var in VARS_SUPP:
    coords_ind[var] = df_acm_clean[var].values

# Créer les labels lisibles pour les modalités
mod_labels = []
for idx in coords_mod.index:
    # Le format est "variable_modalité"
    parts = idx.rsplit('_', 1)
    if len(parts) == 2:
        var_base = parts[0]
        # Retrouver la variable originale
        for v in VARS_ACTIVES:
            if idx.startswith(v.replace('_R', '')) or v in idx or idx.startswith(v):
                var_base = v
                break
        mod_code = parts[-1]
        label = get_modality_label(var_base, mod_code)
    else:
        label = idx
    mod_labels.append(label)

coords_mod['label'] = mod_labels

# Identifier la variable d'origine pour colorer
def get_var_group(idx):
    for v in VARS_ACTIVES:
        if idx.startswith(v) or v.replace('_R', '') in idx:
            return VAR_LABELS.get(v, v)
    return "Autre"

coords_mod['variable'] = [get_var_group(idx) for idx in coords_mod.index]

print("\n4. Generation des graphiques...")

# === GRAPHIQUE 1 : Modalités ===
fig_mod = px.scatter(
    coords_mod,
    x="Dim1",
    y="Dim2",
    text="label",
    color="variable",
    title=f"ACM - Carte des modalites (Axes 1-2: {sum(inertia_pct[:2]):.1f}% d'inertie)",
    labels={"Dim1": f"Dimension 1 ({inertia_pct[0]:.1f}%)",
            "Dim2": f"Dimension 2 ({inertia_pct[1]:.1f}%)"},
    width=1200,
    height=800,
)

fig_mod.update_traces(
    textposition='top center',
    marker=dict(size=12),
    textfont=dict(size=10)
)

fig_mod.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
fig_mod.add_vline(x=0, line_dash="dash", line_color="gray", opacity=0.5)

# Sauvegarder
fig_mod.write_html(OUTPUT_DIR / "acm_modalites.html")
print(f"   -> acm_modalites.html")

# === GRAPHIQUE 2 : Individus colorés par âge ===
fig_ind = px.scatter(
    coords_ind,
    x="Dim1",
    y="Dim2",
    color="RS2C_RECODE_AG_R",
    title=f"ACM - Individus par age",
    labels={"Dim1": f"Dimension 1 ({inertia_pct[0]:.1f}%)",
            "Dim2": f"Dimension 2 ({inertia_pct[1]:.1f}%)",
            "RS2C_RECODE_AG_R": "Age"},
    width=1000,
    height=700,
    opacity=0.5,
)

fig_ind.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
fig_ind.add_vline(x=0, line_dash="dash", line_color="gray", opacity=0.5)

fig_ind.write_html(OUTPUT_DIR / "acm_individus_age.html")
print(f"   -> acm_individus_age.html")

# === GRAPHIQUE 3 : Individus colorés par CSP ===
fig_csp = px.scatter(
    coords_ind,
    x="Dim1",
    y="Dim2",
    color="CSPIND_R",
    title=f"ACM - Individus par CSP",
    labels={"Dim1": f"Dimension 1 ({inertia_pct[0]:.1f}%)",
            "Dim2": f"Dimension 2 ({inertia_pct[1]:.1f}%)",
            "CSPIND_R": "CSP"},
    width=1000,
    height=700,
    opacity=0.5,
)

fig_csp.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
fig_csp.add_vline(x=0, line_dash="dash", line_color="gray", opacity=0.5)

fig_csp.write_html(OUTPUT_DIR / "acm_individus_csp.html")
print(f"   -> acm_individus_csp.html")

# === Résumé de l'interprétation ===
print("\n" + "=" * 60)
print("INTERPRETATION PRELIMINAIRE")
print("=" * 60)

# Contributions des modalités à l'axe 1
print("\n** Axe 1 - Modalites extremes:")
dim1_sorted = coords_mod.sort_values('Dim1')
print("   Gauche (negatif):")
for _, row in dim1_sorted.head(5).iterrows():
    print(f"      {row['label']}: {row['Dim1']:.2f}")
print("   Droite (positif):")
for _, row in dim1_sorted.tail(5).iterrows():
    print(f"      {row['label']}: {row['Dim1']:.2f}")

print("\n** Axe 2 - Modalites extremes:")
dim2_sorted = coords_mod.sort_values('Dim2')
print("   Bas (negatif):")
for _, row in dim2_sorted.head(5).iterrows():
    print(f"      {row['label']}: {row['Dim2']:.2f}")
print("   Haut (positif):")
for _, row in dim2_sorted.tail(5).iterrows():
    print(f"      {row['label']}: {row['Dim2']:.2f}")

print("\n" + "=" * 60)
print(f"Graphiques generes dans: {OUTPUT_DIR}")
print("Ouvrir acm_modalites.html dans un navigateur pour explorer")
print("=" * 60)
