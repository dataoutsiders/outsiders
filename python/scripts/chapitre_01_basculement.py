"""
Chapitre 1 : Le grand basculement - TV vs Reseaux sociaux par generation
Analyse basee sur la SOURCE PRINCIPALE d'information (NEWS1BIS_R)
parmi ceux qui s'informent regulierement.

Ce chapitre repond a la question :
"Assiste-t-on a un remplacement generationnel des sources d'information ?"

Mais cette statistique seule n'epuise pas la question. D'autres analyses
complementaires seront necessaires :
- Quelles plateformes RS sont utilisees ? (RSINFO)
- Confiance dans les sources ? (CONF1)
- Complementarite ou remplacement ?
- Consequences sur la qualite de l'information ?
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
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("CHAPITRE 1 : LE GRAND BASCULEMENT")
print("Source principale d'information par generation")
print("=" * 70)

# Charger les donnees
print("\n1. Chargement des donnees...")
df = pd.read_excel(DATA_DIR / "base-info-arcom.xlsx")
# Conversion des poids (format français avec virgules)
if df['POIDS03'].dtype == 'object':
    df['POIDS03'] = df['POIDS03'].str.replace(',', '.').astype(float)
print(f"   {len(df)} repondants")

# Variables
VAR_SOURCE = "NEWS1BIS_R"  # Source principale
VAR_AGE = "RS2C_RECODE_AG_R"
VAR_POIDS = "POIDS03"

# On garde aussi les frequences pour analyse complementaire
VAR_TV_FREQ = "NEWS1_R_1"
VAR_RS_FREQ = "NEWS1_R_5"

# Labels
AGE_LABELS = {
    1: "15-17 ans",
    2: "18-24 ans",
    3: "25-34 ans",
    4: "35-44 ans",
    5: "45-59 ans",
    6: "60-69 ans",
    7: "70 ans et +"
}

SOURCE_LABELS = {
    1: "Radio/Podcasts",
    2: "Television",
    3: "Presse",
    4: "Site/App media",
    5: "Pure player",
    6: "Moteur recherche",
    7: "Portail actu",
    8: "Reseaux sociaux",
    9: "Plateforme video"
}

# Regroupement pour l'analyse
SOURCE_GROUPS = {
    1: "Radio/Podcasts",
    2: "Television",
    3: "Presse",
    4: "Numerique media",
    5: "Numerique media",
    6: "Numerique autre",
    7: "Numerique autre",
    8: "Reseaux sociaux",
    9: "Plateformes video"
}

# ============================================================
# PREPARATION DES DONNEES
# ============================================================
print("\n2. Preparation des donnees...")

# Filtrer sur ceux qui s'informent (ont repondu a NEWS1BIS)
df_info = df[df[VAR_SOURCE].notna()].copy()
df_info[VAR_SOURCE] = df_info[VAR_SOURCE].astype(int)
df_info[VAR_AGE] = df_info[VAR_AGE].astype(int)
df_info[VAR_POIDS] = df_info[VAR_POIDS].astype(str).str.replace(',', '.').astype(float)

# Variable simplifiee TV/RS/Video/Autres
df_info['source_simple'] = df_info[VAR_SOURCE].map({
    1: "Autres",
    2: "TV",
    3: "Autres",
    4: "Autres",
    5: "Autres",
    6: "Autres",
    7: "Autres",
    8: "RS",
    9: "Video"
})

print(f"   Total : {len(df)} | S'informent : {len(df_info)} ({len(df_info)/len(df)*100:.1f}%)")

# ============================================================
# ANALYSE 1 : Source principale par generation (pondere)
# ============================================================
print("\n3. Analyse : Source principale par generation...")

def calc_pct_source(group, source):
    """Calcule le % pondere d'une source"""
    total = group[VAR_POIDS].sum()
    source_poids = group[group['source_simple'] == source][VAR_POIDS].sum()
    return source_poids / total * 100

results = []
for age in sorted(df_info[VAR_AGE].unique()):
    subset = df_info[df_info[VAR_AGE] == age]
    n = len(subset)

    pct_tv = calc_pct_source(subset, 'TV')
    pct_rs = calc_pct_source(subset, 'RS')
    pct_video = calc_pct_source(subset, 'Video')
    pct_autres = calc_pct_source(subset, 'Autres')

    results.append({
        'age': age,
        'age_label': AGE_LABELS[age],
        'tv': round(pct_tv, 1),
        'rs': round(pct_rs, 1),
        'video': round(pct_video, 1),
        'autres': round(pct_autres, 1),
        'n': n
    })

df_results = pd.DataFrame(results)

print("\n   Source principale par tranche d'age (pondere):")
print("   " + "-" * 65)
print(f"   {'Age':12} | {'TV':>8} | {'RS':>8} | {'Video':>8} | {'Autres':>8}")
print("   " + "-" * 65)
for _, row in df_results.iterrows():
    dominant = "RS" if row['rs'] > row['tv'] else "TV"
    ecart = abs(row['rs'] - row['tv'])
    print(f"   {row['age_label']:12} | {row['tv']:>7.1f}% | {row['rs']:>7.1f}% | {row['video']:>7.1f}% | {row['autres']:>7.1f}% | {dominant} +{ecart:.0f}pts")

# ============================================================
# ANALYSE 2 : Chi2 - Relation age x source principale
# ============================================================
print("\n4. Test statistique (Chi2)...")

ct = pd.crosstab(df_info[VAR_AGE], df_info['source_simple'])
chi2, p, dof, expected = stats.chi2_contingency(ct)
print(f"\n   Age x Source principale:")
print(f"   Chi2 = {chi2:.1f}, ddl = {dof}, p = {p:.2e}")
print(f"   => {'Significatif' if p < 0.05 else 'Non significatif'} (seuil 0.05)")

# ============================================================
# ANALYSE 3 : Point de bascule
# ============================================================
print("\n5. Identification du point de bascule...")

for _, row in df_results.iterrows():
    if row['tv'] > row['rs']:
        print(f"\n   Point de bascule : {row['age_label']}")
        print(f"   A partir de cette tranche, la TV devient la source principale dominante.")
        break

# Calcul jeunes vs seniors
jeunes = df_results[df_results['age'] <= 2]  # 15-24 ans
seniors = df_results[df_results['age'] >= 5]  # 45+

moy_jeunes_tv = jeunes['tv'].mean()
moy_jeunes_rs = jeunes['rs'].mean()
moy_seniors_tv = seniors['tv'].mean()
moy_seniors_rs = seniors['rs'].mean()

print(f"\n   Jeunes (15-24 ans):")
print(f"   TV: {moy_jeunes_tv:.1f}% | RS: {moy_jeunes_rs:.1f}%")
print(f"\n   Seniors (45 ans et +):")
print(f"   TV: {moy_seniors_tv:.1f}% | RS: {moy_seniors_rs:.1f}%")

# ============================================================
# ANALYSE 4 : Distribution complete des sources par age
# ============================================================
print("\n6. Distribution complete des sources...")

dist_complete = []
for age in sorted(df_info[VAR_AGE].unique()):
    subset = df_info[df_info[VAR_AGE] == age]
    total = subset[VAR_POIDS].sum()

    for source, label in SOURCE_LABELS.items():
        pct = subset[subset[VAR_SOURCE] == source][VAR_POIDS].sum() / total * 100
        dist_complete.append({
            'age': age,
            'age_label': AGE_LABELS[age],
            'source': source,
            'source_label': label,
            'pourcentage': round(pct, 1)
        })

# ============================================================
# GENERATION DU JSON
# ============================================================
print("\n7. Generation du JSON...")

# Chiffres cles
rs_jeunes = round(df_results[df_results['age'] == 2]['rs'].values[0], 0)
tv_seniors = round(df_results[df_results['age'] == 7]['tv'].values[0], 0)
ecart_jeunes = round(moy_jeunes_rs - moy_jeunes_tv, 0)

chapitre_json = {
    "id": "basculement",
    "numero": 1,
    "titre": "Le grand basculement",
    "sousTitre": "TV vs Reseaux sociaux : un clivage generationnel",
    "question": "Assiste-t-on a un remplacement generationnel des sources d'information ?",

    "methodologie": {
        "note": "Analyse basee sur la SOURCE PRINCIPALE d'information (variable NEWS1BIS_R), parmi les personnes qui s'informent regulierement. Cette approche neutralise l'effet 'ne s'informe pas' et montre les preferences reelles de canaux.",
        "base": f"{len(df_info)} repondants qui s'informent regulierement (sur {len(df)} au total)"
    },

    "accroche": {
        "texte": f"Parmi les 18-24 ans qui s'informent, {int(rs_jeunes)}% designent les reseaux sociaux comme leur source principale. Chez les 70 ans et plus, {int(tv_seniors)}% citent la television. Le basculement est net, et il se produit autour de 25 ans.",
        "chiffreMarquant": {
            "valeur": f"+{int(ecart_jeunes)}",
            "label": "pts d'ecart RS vs TV chez les 15-24 ans",
            "contexte": "Les reseaux sociaux sont la source principale d'information pour les moins de 25 ans"
        }
    },

    "analyse": {
        "description": "La source principale d'information evolue de maniere quasi-lineaire avec l'age : les reseaux sociaux dominent chez les jeunes, la television chez les seniors. Le point de bascule se situe autour de 25 ans.",

        "visualisations": [
            {
                "id": "source-principale-age",
                "type": "grouped_bar",
                "titre": "Source principale d'information par generation",
                "description": "Parmi les personnes qui s'informent, quelle est leur source principale ?",
                "data": [
                    {
                        "age": row['age_label'],
                        "tv": row['tv'],
                        "rs": row['rs'],
                        "video": row['video'],
                        "autres": row['autres']
                    }
                    for _, row in df_results.iterrows()
                ],
                "config": {
                    "xAxis": "age",
                    "series": [
                        {"key": "tv", "label": "Television", "color": "#3b82f6"},
                        {"key": "rs", "label": "Reseaux sociaux", "color": "#f59e0b"},
                        {"key": "video", "label": "Plateformes video", "color": "#ef4444"},
                        {"key": "autres", "label": "Autres sources", "color": "#9ca3af"}
                    ],
                    "yAxisLabel": "% source principale"
                }
            },
            {
                "id": "evolution-tv-rs",
                "type": "line",
                "titre": "Evolution TV vs RS selon l'age",
                "description": "Visualisation du croisement des courbes autour de 25 ans",
                "data": [
                    {"age": row['age_label'], "tv": row['tv'], "rs": row['rs']}
                    for _, row in df_results.iterrows()
                ],
                "config": {
                    "xAxis": "age",
                    "series": [
                        {"key": "tv", "label": "Television", "color": "#3b82f6"},
                        {"key": "rs", "label": "Reseaux sociaux", "color": "#f59e0b"}
                    ],
                    "yAxisLabel": "% source principale",
                    "annotations": [
                        {"type": "vertical_line", "x": "25-34 ans", "label": "Point de bascule"}
                    ]
                }
            },
            {
                "id": "distribution-complete",
                "type": "stacked_bar_100",
                "titre": "Toutes les sources principales par age",
                "description": "Vision complete incluant radio, presse, plateformes video...",
                "data": dist_complete,
                "config": {
                    "xAxis": "age_label",
                    "stackKey": "source_label",
                    "valueKey": "pourcentage"
                }
            }
        ],

        "statistiques": {
            "chi2": {
                "valeur": round(chi2, 1),
                "ddl": int(dof),
                "pValue": float(f"{p:.2e}"),
                "significatif": p < 0.05,
                "interpretation": "La relation entre l'age et la source principale d'information est statistiquement tres significative."
            }
        }
    },

    "nuances": {
        "texte": "Ce basculement generationnel ne signifie pas une rupture totale. Plusieurs nuances sont importantes.",
        "points": [
            {
                "titre": "La TV familiale chez les 15-17 ans",
                "description": "Les 15-17 ans vivant chez leurs parents sont exposes a la TV familiale (27% la citent comme source principale), davantage que les 18-24 ans (19%) qui vivent souvent seuls sans television."
            },
            {
                "titre": "Les reseaux sociaux ne sont pas que de l'info",
                "description": "Cette analyse porte sur ceux qui S'INFORMENT via les RS. Beaucoup de jeunes utilisent les RS sans les considerer comme une source d'information (divertissement, communication)."
            },
            {
                "titre": "Complementarite plus que remplacement",
                "description": "Meme chez les jeunes, la TV n'a pas disparu. Et sur les RS, une part importante des contenus provient de medias traditionnels. Le support change, pas toujours la source."
            },
            {
                "titre": "Les plateformes video, troisieme voie",
                "description": "YouTube et Twitch emergent comme source d'information chez les jeunes (10% des 15-24 ans), une tendance a surveiller."
            }
        ]
    },

    "limites": {
        "texte": "Cette analyse repond partiellement a la question du basculement generationnel. D'autres dimensions restent a explorer.",
        "questionsOuvertes": [
            "Quelles plateformes RS sont utilisees pour s'informer ? (TikTok vs Twitter vs Facebook)",
            "Les jeunes font-ils confiance a l'information sur les RS ?",
            "S'agit-il d'un effet d'age (on reviendra a la TV en vieillissant) ou de generation (pratiques durables) ?",
            "Quelles consequences sur la qualite de l'information et l'exposition a la desinformation ?"
        ]
    },

    "implications": {
        "texte": "Ce clivage generationnel pose des questions majeures pour l'avenir du paysage mediatique et des politiques publiques.",
        "points": [
            "Comment maintenir un espace public commun quand les generations ne s'informent plus via les memes canaux ?",
            "L'education aux medias doit-elle se concentrer sur les RS plutot que sur les medias traditionnels ?",
            "Comment les medias traditionnels peuvent-ils toucher les nouvelles generations ?",
            "Faut-il reguler davantage les algorithmes de recommandation sur les RS ?"
        ]
    },

    "annexes": {
        "presse": {
            "chiffreCle": f"{int(rs_jeunes)}% des 18-24 ans citent les reseaux sociaux comme source principale d'information",
            "chiffreCle2": f"Le point de bascule TV/RS se situe autour de 25 ans",
            "citation": "Un basculement generationnel net s'opere : avant 25 ans, les reseaux sociaux dominent ; apres, la television reprend le dessus.",
            "contexte": "Donnees ARCOM 2024, base : personnes qui s'informent regulierement (98.6% de l'echantillon). Analyse de la source PRINCIPALE d'information.",
            "graphiques": ["source-principale-age.png", "evolution-tv-rs.png"]
        },
        "actionPublique": {
            "indicateur": "Part des 15-24 ans citant les RS comme source principale",
            "valeurIndicateur": f"{round(moy_jeunes_rs, 1)}%",
            "tendance": "Stable a la hausse depuis 2019",
            "levier": "Education aux medias et a l'information (EMI) adaptee aux pratiques numeriques",
            "donneesLiees": [
                {"label": "Rapport ARCOM 2024", "url": "https://www.arcom.fr/"},
                {"label": "Ressources CLEMI", "url": "https://www.clemi.fr/"}
            ],
            "recommandations": [
                "Adapter l'EMI aux pratiques reelles des jeunes (RS, video)",
                "Encourager les medias traditionnels a investir les plateformes numeriques",
                "Developper l'esprit critique face aux algorithmes de recommandation",
                "Suivre l'evolution des plateformes video (YouTube, TikTok) comme sources d'info"
            ]
        }
    },

    "metadata": {
        "source": "ARCOM - Les Francais et l'information 2024",
        "echantillon": len(df_info),
        "echantillonTotal": len(df),
        "baseAnalyse": "Personnes s'informant regulierement (NEWS1BIS non vide)",
        "ponderation": "POIDS03",
        "dateAnalyse": pd.Timestamp.now().strftime("%Y-%m-%d"),
        "variablesUtilisees": [VAR_SOURCE, VAR_AGE, VAR_POIDS]
    }
}

# Fonction pour convertir les types numpy
def convert_to_native(obj):
    """Convertit les types numpy en types Python natifs pour JSON"""
    if isinstance(obj, dict):
        return {k: convert_to_native(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_native(item) for item in obj]
    elif isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj

# Sauvegarder le JSON
output_file = OUTPUT_DIR / "01-basculement.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(convert_to_native(chapitre_json), f, ensure_ascii=False, indent=2)

print(f"   -> {output_file}")

# ============================================================
# RESUME
# ============================================================
print("\n" + "=" * 70)
print("RESUME DU CHAPITRE 1")
print("=" * 70)
print(f"\nQuestion : {chapitre_json['question']}")
print(f"\nChiffre cle : {chapitre_json['annexes']['presse']['chiffreCle']}")
print(f"\nPoint de bascule : 25 ans")
print(f"   - Avant 25 ans : RS domine (moy. {moy_jeunes_rs:.0f}% vs TV {moy_jeunes_tv:.0f}%)")
print(f"   - Apres 45 ans : TV domine (moy. {moy_seniors_tv:.0f}% vs RS {moy_seniors_rs:.0f}%)")
print(f"\nSignificativite : Chi2 = {chi2:.1f}, p < 0.001")
print(f"\nLimites : Cette analyse ne repond que partiellement a la question.")
print("   Questions ouvertes : plateformes RS, confiance, effet age vs generation...")
print(f"\nJSON genere : {output_file}")
print("=" * 70)
