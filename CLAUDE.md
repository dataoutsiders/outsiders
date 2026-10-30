# CLAUDE.md - Instructions pour Claude Code

## Contexte du projet Outsiders

**Outsiders** est une plateforme d'analyses sociologiques de données publiques françaises. Le projet combine :
- **Python** (Positron) : Calculs statistiques, génération de JSON pré-calculés
- **React** (VS Code) : Interface de visualisation interactive

### Architecture

```
Positron (Python)                    VS Code (React)
─────────────────                    ───────────────
Données brutes (.xlsx, .csv)         
       ↓                             
Scripts d'analyse (generate_*.py)    
       ↓                             
JSON pré-calculés ──────────────────→ frontend/public/data/
                                            ↓
                                     Composants React
                                            ↓
                                     Site web interactif
```

### Répertoires clés

- `%USERPROFILE%\Documents\Positron\Outsiders\` → Analyses Python
- `%USERPROFILE%\Documents\VsCode\Outsiders\` → Application React
- `python/src/core/` → Modules réutilisables (stats pondérées, régression, arbres)
- `frontend/src/components/chapter/` → Composants de rendu des chapitres
- `frontend/src/components/visualizations/` → Composants de visualisation

---

## Comment créer un nouveau chapitre

### Étape 1 : Créer le script Python de génération

Créer un fichier dans `Positron/Outsiders/[NomEnquete]/generate_chapitre_XX.py`

**Structure type :**

```python
# -*- coding: utf-8 -*-
"""
Génération du Chapitre XX : [Titre]
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
SCRIPT_DIR = Path(__file__).parent.resolve()
DATA_DIR = SCRIPT_DIR
OUTPUT_DIR = SCRIPT_DIR / 'output' / 'chapitre-XX-[slug]'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================
# CHARGEMENT DES DONNÉES
# ============================================
print("Chargement des données...")
df = pd.read_excel(DATA_DIR / 'base-xxx.xlsx')

# Convertir les poids si format français (virgules)
if df['POIDS'].dtype == 'object':
    df['POIDS'] = df['POIDS'].str.replace(',', '.').astype(float)

# ============================================
# LABELS (à adapter selon l'enquête)
# ============================================
AGE_LABELS = {1: '15-24 ans', 2: '25-34 ans', ...}
# etc.

# ============================================
# FONCTIONS UTILITAIRES
# ============================================
# Utiliser les fonctions de python/src/core/ OU copier les fonctions essentielles :

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

def get_distribution_by_var(df, var, vd, weights, labels=None):
    """Calcule le % de VD=1 par modalité"""
    mask = df[var].notna() & df[vd].notna()
    distribution = []
    for val in sorted(df.loc[mask, var].unique()):
        val_mask = mask & (df[var] == val)
        w = df.loc[val_mask, weights]
        y = df.loc[val_mask, vd]
        pct = (y * w).sum() / w.sum() * 100
        label = labels.get(int(val), str(int(val))) if labels else str(int(val))
        distribution.append({
            'category': label,
            'code': int(val),
            'pct_numerique': round(pct, 1),
            'pct_traditionnel': round(100 - pct, 1),
            'n': int(val_mask.sum())
        })
    return distribution

class NumpyEncoder(json.JSONEncoder):
    """Encodeur JSON pour types numpy"""
    def default(self, obj):
        if isinstance(obj, (np.integer,)): return int(obj)
        if isinstance(obj, (np.floating,)): return float(obj)
        if isinstance(obj, np.ndarray): return obj.tolist()
        if isinstance(obj, (np.bool_,)): return bool(obj)
        return super().default(obj)

def save_json(data, filename):
    """Sauvegarde un fichier JSON"""
    path = OUTPUT_DIR / filename
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, cls=NumpyEncoder)
    print(f"  -> {filename}")

# ============================================
# CONSTRUCTION DE LA VARIABLE PRINCIPALE
# ============================================
print("Construction de la variable...")
# [Logique spécifique au chapitre]
df['MA_VARIABLE'] = ...

# ============================================
# GÉNÉRATION DES JSON
# ============================================

# 1. INDEX.JSON (obligatoire)
print("Génération de index.json...")
index_data = {
    'id': 'chapitre-XX',
    'titre': '[Titre du chapitre]',
    'sousTitre': '[Sous-titre]',
    'introduction': {
        'accroche': '[Question accrocheuse]',
        'contexte': '[Contexte de l\'analyse]',
        'question': '[Question de recherche]'
    },
    'sommaire': [
        {'id': 'XXa-section', 'titre': '[Titre]', 'description': '[Desc]', 'icon': 'lightbulb'},
        # Ajouter les autres sections...
    ],
    'metadata': {
        'n_total': len(df),
        'n_analyse': int(df['MA_VARIABLE'].notna().sum()),
        # Autres métadonnées...
    }
}
save_json(index_data, 'index.json')

# 2. SECTIONS (XXa, XXb, XXc, etc.)
# Voir les exemples dans generate_chapitre_01.py

print("GÉNÉRATION TERMINÉE")
```

### Étape 2 : Exécuter le script Python

```bash
cd %USERPROFILE%\Documents\Positron\Outsiders\[NomEnquete]
python generate_chapitre_XX.py
```

### Étape 3 : Copier les JSON vers le frontend

Les JSON générés dans `output/chapitre-XX-[slug]/` doivent être copiés vers :
```
VsCode/Outsiders/frontend/public/data/enquetes/[enquete-id]/chapitres/chapitre-XX-[slug]/
```

### Étape 4 : Configurer le chapitre dans React

Modifier `frontend/src/pages/enquetes/EnqueteChapter.jsx` :

```javascript
// Ajouter dans CHAPTER_SECTIONS
const CHAPTER_SECTIONS = {
  '01-basculement': [...],  // existant
  'XX-[slug]': [            // nouveau
    'XXa-section1',
    'XXb-section2',
    // etc.
  ]
}

// Ajouter dans renderSection() si composant spécifique nécessaire
switch (sectionId) {
  case 'XXa-section1':
    return <ChapterMonComposant key={sectionId} data={data} />
  // ...
}
```

### Étape 5 : Créer les composants de visualisation si nécessaire

Si le chapitre nécessite une nouvelle visualisation, créer un composant dans :
`frontend/src/components/visualizations/`

---

## Structure des JSON

### index.json (obligatoire)

```json
{
  "id": "chapitre-XX",
  "titre": "Titre principal",
  "sousTitre": "Sous-titre",
  "introduction": {
    "accroche": "Question qui intrigue",
    "contexte": "D'où viennent les données",
    "question": "Ce qu'on cherche à comprendre"
  },
  "sommaire": [
    {
      "id": "XXa-section",
      "titre": "Titre section",
      "description": "Brève description",
      "icon": "lightbulb"
    }
  ],
  "metadata": {
    "n_total": 3346,
    "n_analyse": 3298
  }
}
```

### Section standard (XXa-xxx.json)

```json
{
  "id": "XXa-section",
  "titre": "Titre de la section",
  "sousTitre": "Sous-titre",
  "description": "Introduction de la section",
  
  "sections": [
    {
      "id": "sous-section-1",
      "titre": "Force d'association",
      "description": "Explication",
      "visualisations": [
        {
          "type": "horizontal-bar-chart",
          "data": [
            {"variable": "Âge", "v_cramer": 0.37, "significatif": true},
            {"variable": "Diplôme", "v_cramer": 0.15, "significatif": true}
          ]
        }
      ]
    }
  ],
  
  "noteMethodologique": {
    "titre": "Comment lire ces résultats",
    "texte": "Explication méthodologique"
  },
  
  "synthese": {
    "titre": "En résumé",
    "points": ["Point 1", "Point 2", "Point 3"]
  },
  
  "metadata": {
    "variables_analysees": 7
  }
}
```

### Section prénotions (XXa-prenotions.json)

```json
{
  "id": "XXa-prenotions",
  "titre": "Idées reçues",
  "prenotions": {
    "titre": "Vrai ou Faux ?",
    "items": [
      {
        "idee": "Les jeunes ne s'informent plus",
        "verdict": "FAUX",
        "realite": "Explication avec données",
        "chiffre": {
          "valeur": "72",
          "unite": "%",
          "label": "des 15-34 ans sont numériques"
        }
      }
    ]
  }
}
```

### Section profils-types (XXg-profils-types.json)

```json
{
  "id": "XXg-profils-types",
  "titre": "Les profils-types",
  
  "accroche": {
    "texte": "Texte avec <strong>HTML</strong> possible",
    "chiffres": [
      {"valeur": "70", "unite": "%", "label": "de l'explication", "couleur": "#EF4444"}
    ]
  },
  
  "messagesCles": {
    "titre": "Ce que révèle l'analyse",
    "messages": [
      {"icon": "cake", "titre": "L'âge domine", "texte": "Explication"}
    ]
  },
  
  "parcours": {
    "titre": "Comment l'analyse classe",
    "etapes": [
      {
        "niveau": 1,
        "question": "Quel âge avez-vous ?",
        "branches": [
          {"condition": "< 45 ans", "resultat": "numerique", "couleur": "#10B981"}
        ]
      }
    ]
  },
  
  "profils": {
    "titre": "Les 5 visages",
    "data": [
      {
        "id": "jeunes",
        "nom": "Les connectés",
        "sousTitre": "15-44 ans",
        "description": "Description du profil",
        "icon": "smartphone",
        "n": 1500,
        "pct_echantillon": 45,
        "pct_numerique": 72,
        "couleur": "#10B981",
        "gradient": "from-emerald-500 to-teal-500",
        "caracteristiques": ["Caractéristique 1", "Caractéristique 2"],
        "insight": "Message clé sur ce profil"
      }
    ]
  },
  
  "variablesImportance": {
    "titre": "Le poids de chaque facteur",
    "data": [
      {"variable": "Âge", "importance": 0.7, "pct": 70}
    ]
  },
  
  "methodologie": {
    "titre": "Comment avons-nous fait ?",
    "texte": "Explication de la méthode",
    "precision": {"valeur": 72, "label": "de précision"}
  }
}
```

---

## Types de visualisations disponibles

| Type dans JSON | Composant React | Usage |
|----------------|-----------------|-------|
| `horizontal-bar-chart` | HorizontalBarChart | V de Cramer, barres horizontales |
| `distribution_bar` | DistributionBar | % par modalité (barres empilées) |
| `effect_cards_par_variable` | EffectCardsParVariable | Comparaison modalités extrêmes |
| `effect_cards_profils` | EffectCardsProfils | Profils combinés |
| `effet_net_cards_stratifie` | EffetNetCardsStratifie | Effets par strate |

---

## Conventions de nommage

### Fichiers JSON
- `index.json` : Toujours présent, décrit le chapitre
- `XXa-xxx.json` : XX = numéro chapitre, a/b/c = ordre, xxx = slug

### Couleurs standards
```javascript
rouge: '#EF4444'    // Négatif, attention
orange: '#F59E0B'   // Mixte, neutre
vert: '#10B981'     // Positif, numérique
bleu: '#3B82F6'     // Information
indigo: '#6366F1'   // Traditionnel
violet: '#8B5CF6'   // Secondaire
rose: '#EC4899'     // Accent
```

### Icônes (Lucide React)
`lightbulb`, `build`, `people`, `devices`, `analytics`, `layers`, `users`, `smartphone`, `tv`, `book`, `home`, `building`

---

## Checklist nouveau chapitre

- [ ] Script Python créé et testé
- [ ] JSON générés dans `output/`
- [ ] JSON copiés vers `frontend/public/data/`
- [ ] `CHAPTER_SECTIONS` mis à jour dans `EnqueteChapter.jsx`
- [ ] Composants spécifiques créés si nécessaire
- [ ] Test local avec `npm run dev`

---

## Commandes utiles

```bash
# Frontend
cd %USERPROFILE%\Documents\VsCode\Outsiders\frontend
npm run dev          # Lancer le serveur de dev
npm run build        # Build pour production

# Python (dans Positron)
python generate_chapitre_XX.py
```
