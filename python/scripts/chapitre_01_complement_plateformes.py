"""
Chapitre 1 - Complement 1 : Plateformes RS pour s'informer par age
Variable RSINFO_2_LR_R_* (1-13)
"""
import pandas as pd
import numpy as np
from scipy import stats
import json
from pathlib import Path

# Chemins
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data" / "francais-information"
OUTPUT_DIR = BASE_DIR / "outputs" / "chapitres"

print("=" * 70)
print("COMPLEMENT 1 : PLATEFORMES RS POUR S'INFORMER PAR AGE")
print("=" * 70)

# Charger les donnees
df = pd.read_excel(DATA_DIR / "base-info-arcom.xlsx")
# Conversion des poids (format français avec virgules)
if df['POIDS03'].dtype == 'object':
    df['POIDS03'] = df['POIDS03'].str.replace(',', '.').astype(float)
print(f"\n{len(df)} repondants")

# Variables
VAR_AGE = "RS2C_RECODE_AG_R"
VAR_POIDS = "POIDS03"

# Plateformes RS
PLATEFORMES = {
    1: "Facebook",
    2: "Instagram",
    3: "X (Twitter)",
    4: "TikTok",
    5: "Snapchat",
    6: "LinkedIn",
    7: "WhatsApp",
    8: "Telegram",
    9: "YouTube",
    10: "Reddit",
    11: "Discord",
    12: "Twitch",
    13: "Autre"
}

AGE_LABELS = {
    1: "15-17 ans", 2: "18-24 ans", 3: "25-34 ans",
    4: "35-44 ans", 5: "45-59 ans", 6: "60-69 ans", 7: "70 ans et +"
}

# Colonnes RSINFO_2_LR_R_*
rsinfo_cols = [f"RSINFO_2_LR_R_{i}" for i in range(1, 14)]

# Verifier quelles colonnes existent
existing_cols = [c for c in rsinfo_cols if c in df.columns]
print(f"Colonnes trouvees: {len(existing_cols)}")

# Preparation
df[VAR_POIDS] = df[VAR_POIDS].astype(str).str.replace(',', '.').astype(float)
df[VAR_AGE] = pd.to_numeric(df[VAR_AGE], errors='coerce')

# Base : ceux qui ont repondu a au moins une plateforme
df_rs = df[df[existing_cols].notna().any(axis=1)].copy()
print(f"Repondants avec usage RS: {len(df_rs)}")

# ============================================================
# ANALYSE 1 : Usage de chaque plateforme POUR S'INFORMER par age
# ============================================================
print("\n=== USAGE DES PLATEFORMES POUR S'INFORMER PAR AGE ===\n")

results = []
for i, col in enumerate(existing_cols, 1):
    plateforme = PLATEFORMES.get(i, f"Plateforme {i}")

    for age in sorted(df_rs[VAR_AGE].dropna().unique()):
        age = int(age)
        subset = df_rs[df_rs[VAR_AGE] == age]
        total_poids = subset[VAR_POIDS].sum()

        # Ceux qui utilisent cette plateforme pour s'informer (valeur = 1 ou non-null selon codage)
        # Verifier le codage
        utilisateurs = subset[subset[col].notna() & (subset[col] == 1)]
        poids_utilisateurs = utilisateurs[VAR_POIDS].sum()

        pct = poids_utilisateurs / total_poids * 100 if total_poids > 0 else 0

        results.append({
            'plateforme': plateforme,
            'plateforme_id': i,
            'age': age,
            'age_label': AGE_LABELS[age],
            'pct': round(pct, 1),
            'n': len(utilisateurs)
        })

df_results = pd.DataFrame(results)

# Afficher les resultats pour les principales plateformes
principales = ['Facebook', 'Instagram', 'X (Twitter)', 'TikTok', 'YouTube', 'LinkedIn']

print(f"{'Plateforme':<15} | ", end="")
for age in sorted(df_rs[VAR_AGE].dropna().unique()):
    print(f"{AGE_LABELS[int(age)][:7]:>8} |", end="")
print()
print("-" * 85)

for pf in principales:
    pf_data = df_results[df_results['plateforme'] == pf]
    print(f"{pf:<15} | ", end="")
    for age in sorted(df_rs[VAR_AGE].dropna().unique()):
        row = pf_data[pf_data['age'] == int(age)]
        if len(row) > 0:
            pct = row['pct'].values[0]
            print(f"{pct:>7.1f}% |", end="")
        else:
            print(f"{'N/A':>8} |", end="")
    print()

# ============================================================
# ANALYSE 2 : Top plateformes par tranche d'age
# ============================================================
print("\n=== TOP 3 PLATEFORMES PAR TRANCHE D'AGE ===\n")

top_par_age = {}
for age in sorted(df_rs[VAR_AGE].dropna().unique()):
    age = int(age)
    age_data = df_results[df_results['age'] == age].sort_values('pct', ascending=False)
    top3 = age_data.head(3)[['plateforme', 'pct']].values.tolist()
    top_par_age[age] = top3
    print(f"{AGE_LABELS[age]}:")
    for rank, (pf, pct) in enumerate(top3, 1):
        print(f"  {rank}. {pf}: {pct}%")
    print()

# ============================================================
# ANALYSE 3 : Evolution generationnelle par plateforme
# ============================================================
print("\n=== PROFIL GENERATIONNEL DES PLATEFORMES ===\n")

# Calculer le "profil" de chaque plateforme
profil_plateformes = []
for pf in PLATEFORMES.values():
    pf_data = df_results[df_results['plateforme'] == pf]
    if len(pf_data) > 0:
        # Moyenne ponderee par age (jeunes = 1-2, seniors = 5-7)
        jeunes = pf_data[pf_data['age'].isin([1, 2, 3])]['pct'].mean()
        seniors = pf_data[pf_data['age'].isin([5, 6, 7])]['pct'].mean()
        ecart = jeunes - seniors

        profil_plateformes.append({
            'plateforme': pf,
            'jeunes_moy': round(jeunes, 1),
            'seniors_moy': round(seniors, 1),
            'ecart': round(ecart, 1),
            'profil': 'Jeunes' if ecart > 5 else 'Seniors' if ecart < -5 else 'Mixte'
        })

df_profil = pd.DataFrame(profil_plateformes).sort_values('ecart', ascending=False)

print(f"{'Plateforme':<15} | {'Jeunes':>8} | {'Seniors':>8} | {'Ecart':>8} | Profil")
print("-" * 60)
for _, row in df_profil.iterrows():
    print(f"{row['plateforme']:<15} | {row['jeunes_moy']:>7.1f}% | {row['seniors_moy']:>7.1f}% | {row['ecart']:>+7.1f} | {row['profil']}")

# ============================================================
# EXPORT JSON
# ============================================================
print("\n=== EXPORT JSON ===")

complement_json = {
    "id": "plateformes-rs",
    "titre": "Quelles plateformes pour s'informer ?",
    "description": "Parmi ceux qui utilisent les reseaux sociaux, quelles plateformes utilisent-ils pour s'informer ?",

    "visualisations": [
        {
            "id": "plateformes-par-age",
            "type": "heatmap",
            "titre": "Usage des plateformes RS pour s'informer par generation",
            "data": df_results[df_results['plateforme'].isin(principales)].to_dict('records'),
            "config": {
                "xAxis": "age_label",
                "yAxis": "plateforme",
                "valueKey": "pct",
                "colorScale": "blues"
            }
        },
        {
            "id": "profil-plateformes",
            "type": "bar_divergent",
            "titre": "Profil generationnel des plateformes",
            "description": "Ecart d'usage entre jeunes (15-34) et seniors (45+)",
            "data": df_profil.to_dict('records'),
            "config": {
                "yAxis": "plateforme",
                "valueKey": "ecart",
                "sortBy": "ecart"
            }
        }
    ],

    "insights": [
        {
            "titre": "TikTok et Snapchat : exclusivement jeunes",
            "description": "Ces plateformes sont quasi-absentes chez les plus de 45 ans pour s'informer."
        },
        {
            "titre": "Facebook : la plateforme des seniors",
            "description": "Facebook reste la plateforme la plus utilisee pour s'informer chez les 45+."
        },
        {
            "titre": "YouTube : transversal",
            "description": "YouTube est utilise pour s'informer a tous les ages, avec un leger avantage jeune."
        }
    ],

    "topParAge": top_par_age,

    "metadata": {
        "base": len(df_rs),
        "question": "S'informer via ce reseau social ou cette plateforme"
    }
}

# Sauvegarder
output_file = OUTPUT_DIR / "01-basculement-complement-plateformes.json"
with open(output_file, "w", encoding="utf-8") as f:
    # Convertir les types numpy
    def convert(obj):
        if isinstance(obj, dict):
            return {k: convert(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert(i) for i in obj]
        elif isinstance(obj, (np.integer, np.int64)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64)):
            return float(obj)
        else:
            return obj

    json.dump(convert(complement_json), f, ensure_ascii=False, indent=2)

print(f"JSON genere: {output_file}")

print("\n" + "=" * 70)
print("RESUME")
print("=" * 70)
print("""
Principales observations:
- TikTok/Snapchat : plateformes 'jeunes' pour l'info
- Facebook : domine chez les seniors pour l'info
- YouTube : usage transversal
- LinkedIn : profil 25-44 ans (actifs)
""")
