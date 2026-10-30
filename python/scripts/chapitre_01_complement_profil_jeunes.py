"""
Chapitre 1 - Complement 6 : Profil socio-demographique des jeunes qui privilegient les RS
Qui sont les jeunes (15-24 ans) qui utilisent les RS comme source principale ?

Variables : RS1_R (genre), CSPIND_R (CSP), RS5_R (niveau etudes)
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
print("COMPLEMENT 6 : PROFIL SOCIO-DEMO DES JEUNES RS")
print("Qui sont les 15-24 ans qui privilegient les reseaux sociaux ?")
print("=" * 70)

# Charger les donnees
df = pd.read_excel(DATA_DIR / "base-info-arcom.xlsx")
# Conversion des poids (format français avec virgules)
if df['POIDS03'].dtype == 'object':
    df['POIDS03'] = df['POIDS03'].str.replace(',', '.').astype(float)
print(f"\n{len(df)} repondants")

# Variables
VAR_AGE = "RS2C_RECODE_AG_R"
VAR_SOURCE = "NEWS1BIS_R"
VAR_GENRE = "RS1_R"
VAR_CSP = "CSPIND_R"
VAR_ETUDES = "RS5_R"
VAR_POIDS = "POIDS03"

# Labels
GENRE_LABELS = {1: "Homme", 2: "Femme", 3: "Non binaire"}
CSP_LABELS = {1: "CSP+", 2: "CSP-", 3: "Inactif", 4: "NSP"}

# Preparation
df[VAR_POIDS] = df[VAR_POIDS].astype(str).str.replace(',', '.').astype(float)
for var in [VAR_AGE, VAR_SOURCE, VAR_GENRE, VAR_CSP, VAR_ETUDES]:
    df[var] = pd.to_numeric(df[var], errors='coerce')

# Source simplifiee
df['source_simple'] = df[VAR_SOURCE].map({
    1: "Autres", 2: "TV", 3: "Autres", 4: "Autres",
    5: "Autres", 6: "Autres", 7: "Autres", 8: "RS", 9: "Video"
})

# Base : jeunes (15-24 ans) avec source principale connue
df_jeunes = df[(df[VAR_AGE].isin([1, 2])) & (df['source_simple'].notna())].copy()
print(f"Jeunes 15-24 ans avec source: {len(df_jeunes)}")

# Repartition des sources chez les jeunes
print("\n=== REPARTITION DES SOURCES CHEZ LES 15-24 ANS ===")
source_counts = df_jeunes.groupby('source_simple')[VAR_POIDS].sum()
source_pct = source_counts / source_counts.sum() * 100
for source in ['TV', 'RS', 'Video', 'Autres']:
    if source in source_pct:
        n = len(df_jeunes[df_jeunes['source_simple'] == source])
        print(f"  {source:<10}: {source_pct[source]:>5.1f}% (n={n})")

# ============================================================
# ANALYSE 1 : Genre et source principale chez les jeunes
# ============================================================
print("\n=== GENRE ET SOURCE PRINCIPALE (15-24 ans) ===")

df_genre = df_jeunes[df_jeunes[VAR_GENRE].isin([1, 2])]  # Exclure non-binaires (trop peu)

# Parmi les RS, quel % de femmes ?
genre_source = pd.crosstab(df_genre['source_simple'], df_genre[VAR_GENRE], normalize='index') * 100

print(f"\n{'Source':<10} | {'Hommes':>10} | {'Femmes':>10}")
print("-" * 35)
for source in ['TV', 'RS', 'Video', 'Autres']:
    if source in genre_source.index:
        h = genre_source.loc[source, 1] if 1 in genre_source.columns else 0
        f = genre_source.loc[source, 2] if 2 in genre_source.columns else 0
        print(f"{source:<10} | {h:>9.1f}% | {f:>9.1f}%")

# Chi2
ct_genre = pd.crosstab(df_genre['source_simple'], df_genre[VAR_GENRE])
chi2_genre, p_genre, _, _ = stats.chi2_contingency(ct_genre)
print(f"\nChi2 Genre x Source: {chi2_genre:.1f}, p = {p_genre:.4f}")

# ============================================================
# ANALYSE 2 : CSP et source principale chez les jeunes
# ============================================================
print("\n=== CSP ET SOURCE PRINCIPALE (15-24 ans) ===")

df_csp = df_jeunes[df_jeunes[VAR_CSP].isin([1, 2, 3])]  # Exclure NSP

# Crosstab
csp_source = pd.crosstab(df_csp['source_simple'], df_csp[VAR_CSP], normalize='index') * 100

print(f"\n{'Source':<10} | {'CSP+':>10} | {'CSP-':>10} | {'Inactif':>10}")
print("-" * 50)
for source in ['TV', 'RS', 'Video', 'Autres']:
    if source in csp_source.index:
        csp_plus = csp_source.loc[source, 1] if 1 in csp_source.columns else 0
        csp_moins = csp_source.loc[source, 2] if 2 in csp_source.columns else 0
        inactif = csp_source.loc[source, 3] if 3 in csp_source.columns else 0
        print(f"{source:<10} | {csp_plus:>9.1f}% | {csp_moins:>9.1f}% | {inactif:>9.1f}%")

# Chi2
ct_csp = pd.crosstab(df_csp['source_simple'], df_csp[VAR_CSP])
chi2_csp, p_csp, _, _ = stats.chi2_contingency(ct_csp)
print(f"\nChi2 CSP x Source: {chi2_csp:.1f}, p = {p_csp:.4f}")

# ============================================================
# ANALYSE 3 : Inverse - Source preferee selon le profil
# ============================================================
print("\n=== SOURCE PREFEREE SELON LE PROFIL (15-24 ans) ===")

# Par genre : quelle source preferent les hommes vs femmes ?
print("\nPar genre:")
for genre in [1, 2]:
    subset = df_genre[df_genre[VAR_GENRE] == genre]
    source_pct_g = subset.groupby('source_simple')[VAR_POIDS].sum()
    source_pct_g = source_pct_g / source_pct_g.sum() * 100
    top_source = source_pct_g.idxmax()
    print(f"  {GENRE_LABELS[genre]}: {top_source} ({source_pct_g[top_source]:.1f}%)")

# Par CSP
print("\nPar CSP:")
for csp in [1, 2, 3]:
    subset = df_csp[df_csp[VAR_CSP] == csp]
    if len(subset) > 20:
        source_pct_c = subset.groupby('source_simple')[VAR_POIDS].sum()
        source_pct_c = source_pct_c / source_pct_c.sum() * 100
        top_source = source_pct_c.idxmax()
        pct_rs = source_pct_c.get('RS', 0)
        print(f"  {CSP_LABELS[csp]}: {top_source} ({source_pct_c[top_source]:.1f}%) | RS = {pct_rs:.1f}%")

# ============================================================
# ANALYSE 4 : Comparaison jeunes RS vs jeunes TV
# ============================================================
print("\n=== COMPARAISON JEUNES RS vs JEUNES TV ===")

jeunes_rs = df_jeunes[df_jeunes['source_simple'] == 'RS']
jeunes_tv = df_jeunes[df_jeunes['source_simple'] == 'TV']

print(f"\nEffectifs: RS = {len(jeunes_rs)}, TV = {len(jeunes_tv)}")

# % femmes
pct_femmes_rs = (jeunes_rs[VAR_GENRE] == 2).mean() * 100
pct_femmes_tv = (jeunes_tv[VAR_GENRE] == 2).mean() * 100
print(f"\n% Femmes: RS = {pct_femmes_rs:.1f}%, TV = {pct_femmes_tv:.1f}%")

# % CSP+
pct_csp_plus_rs = (jeunes_rs[VAR_CSP] == 1).mean() * 100
pct_csp_plus_tv = (jeunes_tv[VAR_CSP] == 1).mean() * 100
print(f"% CSP+: RS = {pct_csp_plus_rs:.1f}%, TV = {pct_csp_plus_tv:.1f}%")

# % Inactifs (etudiants)
pct_inactif_rs = (jeunes_rs[VAR_CSP] == 3).mean() * 100
pct_inactif_tv = (jeunes_tv[VAR_CSP] == 3).mean() * 100
print(f"% Inactifs: RS = {pct_inactif_rs:.1f}%, TV = {pct_inactif_tv:.1f}%")

# ============================================================
# EXPORT JSON
# ============================================================
print("\n=== EXPORT JSON ===")

complement_json = {
    "id": "profil-jeunes-rs",
    "titre": "Qui sont les jeunes qui s'informent via les RS ?",
    "description": "Profil socio-demographique des 15-24 ans selon leur source principale d'information",

    "base": {
        "total_jeunes": len(df_jeunes),
        "jeunes_rs": len(jeunes_rs),
        "jeunes_tv": len(jeunes_tv)
    },

    "comparaison_rs_tv": {
        "pct_femmes": {
            "RS": round(pct_femmes_rs, 1),
            "TV": round(pct_femmes_tv, 1)
        },
        "pct_csp_plus": {
            "RS": round(pct_csp_plus_rs, 1),
            "TV": round(pct_csp_plus_tv, 1)
        },
        "pct_inactifs": {
            "RS": round(pct_inactif_rs, 1),
            "TV": round(pct_inactif_tv, 1)
        }
    },

    "statistiques": {
        "chi2_genre": {
            "valeur": round(chi2_genre, 1),
            "p": round(p_genre, 4),
            "significatif": bool(p_genre < 0.05)
        },
        "chi2_csp": {
            "valeur": round(chi2_csp, 1),
            "p": round(p_csp, 4),
            "significatif": bool(p_csp < 0.05)
        }
    },

    "insights": []
}

# Generer les insights
if abs(pct_femmes_rs - pct_femmes_tv) > 5:
    if pct_femmes_rs > pct_femmes_tv:
        complement_json["insights"].append({
            "titre": "Les RS, source plus feminine",
            "description": f"Les jeunes femmes sont plus nombreuses parmi les utilisateurs RS ({pct_femmes_rs:.0f}%) que TV ({pct_femmes_tv:.0f}%)"
        })
    else:
        complement_json["insights"].append({
            "titre": "La TV, source plus feminine",
            "description": f"Les jeunes femmes sont plus nombreuses parmi les utilisateurs TV ({pct_femmes_tv:.0f}%) que RS ({pct_femmes_rs:.0f}%)"
        })

if abs(pct_csp_plus_rs - pct_csp_plus_tv) > 5:
    if pct_csp_plus_rs > pct_csp_plus_tv:
        complement_json["insights"].append({
            "titre": "Les RS, source des CSP+",
            "description": f"Les CSP+ sont plus representes parmi les jeunes RS ({pct_csp_plus_rs:.0f}%) que TV ({pct_csp_plus_tv:.0f}%)"
        })

# Sauvegarder
output_file = OUTPUT_DIR / "01-basculement-complement-profil-jeunes.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(complement_json, f, ensure_ascii=False, indent=2)

print(f"JSON genere: {output_file}")

# ============================================================
# RESUME
# ============================================================
print("\n" + "=" * 70)
print("RESUME")
print("=" * 70)
print(f"""
Parmi les 15-24 ans:
  - RS comme source principale: {len(jeunes_rs)} personnes ({len(jeunes_rs)/len(df_jeunes)*100:.1f}%)
  - TV comme source principale: {len(jeunes_tv)} personnes ({len(jeunes_tv)/len(df_jeunes)*100:.1f}%)

Profil compare:
  - Femmes: RS {pct_femmes_rs:.1f}% vs TV {pct_femmes_tv:.1f}%
  - CSP+: RS {pct_csp_plus_rs:.1f}% vs TV {pct_csp_plus_tv:.1f}%
  - Inactifs: RS {pct_inactif_rs:.1f}% vs TV {pct_inactif_tv:.1f}%

Chi2 Genre: p = {p_genre:.4f} ({'significatif' if p_genre < 0.05 else 'non significatif'})
Chi2 CSP: p = {p_csp:.4f} ({'significatif' if p_csp < 0.05 else 'non significatif'})
""")
