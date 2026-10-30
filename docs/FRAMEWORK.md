# Framework Outsiders - Documentation

## Vue d'ensemble

Ce framework permet de créer des analyses sociologiques interactives à partir de données d'enquête. Il se compose de deux parties :

1. **Backend Python** : Calculs statistiques et génération de JSON
2. **Frontend React** : Affichage interactif des résultats

---

## Architecture Python

### Structure des dossiers

```
python/
├── src/
│   ├── core/                    # Fonctions réutilisables
│   │   ├── __init__.py
│   │   ├── weighted_stats.py    # Stats pondérées (V de Cramer, Chi2...)
│   │   ├── regression.py        # Régressions logistiques
│   │   ├── tree_profiler.py     # Arbres de décision et profils
│   │   └── json_builder.py      # Construction et export JSON
│   │
│   ├── chapters/                # Chapitres par enquête
│   │   ├── __init__.py
│   │   ├── base_chapter.py      # Classe de base
│   │   ├── chapter_config.py    # Configuration et labels
│   │   └── chapitre_01_*.py     # Chapitres spécifiques
│   │
│   └── analysis.py              # Fonctions legacy
│
├── data/                        # Données sources
├── exports/                     # JSON générés
└── requirements.txt
```

### Utilisation des modules core

#### weighted_stats.py

```python
from src.core.weighted_stats import cramers_v_weighted, get_distribution_by_var

# V de Cramer pondéré
v, chi2, p = cramers_v_weighted(df['AGE'], df['NUMERIQUE'], df['POIDS'])
print(f"V de Cramer = {v:.3f}, p = {p:.4f}")

# Distribution par modalité
dist = get_distribution_by_var(df, 'AGE', 'NUMERIQUE', 'POIDS', AGE_LABELS)
# Retourne: [{'category': '15-24 ans', 'pct_vd': 72.3, 'n': 450}, ...]
```

#### regression.py

```python
from src.core.regression import run_logistic_regression, extract_effect_cards

# Régression logistique pondérée
results = run_logistic_regression(
    df, 
    target='BASCULEMENT',
    features=['AGE', 'DIPLOME', 'USAGE_ALGO'],
    weights='POIDS',
    categorical_features=['AGE', 'DIPLOME'],
    reference_categories={'AGE': 4}  # 35-44 ans comme référence
)

# Extraire les effect cards
cards = extract_effect_cards(df, results, EFFECT_CONFIG)
```

#### tree_profiler.py

```python
from src.core.tree_profiler import build_decision_tree, extract_profiles_from_tree

# Construire l'arbre
tree = build_decision_tree(
    df,
    target='BASCULEMENT',
    features=['AGE', 'DIPLOME', 'AGGLO'],
    max_depth=4
)

# Extraire des profils
profiles = extract_profiles_from_tree(tree, PROFILE_DEFINITIONS)
```

#### json_builder.py

```python
from src.core.json_builder import save_json, build_chapter_index

# Sauvegarder un JSON
save_json(data, 'output/chapitre-01/index.json')

# Construire un index de chapitre
index = build_chapter_index(
    chapter_id='chapitre-01',
    titre='Le basculement numérique',
    sous_titre='Comment les Français s\'informent-ils ?',
    introduction={...},
    sommaire=[...],
    metadata={...}
)
```

---

## Architecture React

### Structure des dossiers

```
frontend/src/
├── components/
│   ├── chapter/                 # Composants de chapitre
│   │   ├── ChapterLayout.jsx
│   │   ├── ChapterIndex.jsx
│   │   ├── ChapterPrenotions.jsx
│   │   ├── ChapterSection.jsx
│   │   └── ChapterProfilsTypes.jsx
│   │
│   ├── visualizations/          # Composants de visualisation
│   │   ├── HorizontalBarChart.jsx
│   │   ├── DistributionBar.jsx
│   │   ├── EffectCardsParVariable.jsx
│   │   └── ProfilsTypes.jsx
│   │
│   └── ErrorBoundary.jsx        # Gestion des erreurs
│
├── config/
│   ├── chapters.js              # Configuration des chapitres
│   ├── enquetes.js              # Liste des enquêtes
│   └── themes.js                # Thèmes transversaux
│
├── hooks/
│   └── useChapterData.js        # Hook de chargement des données
│
└── pages/
    └── enquetes/
        ├── EnqueteChapter.jsx   # Page de chapitre
        └── EnqueteDetail.jsx    # Page d'enquête
```

### Ajouter un nouveau chapitre

1. **Configurer dans `chapters.js`** :

```javascript
export const CHAPTERS_CONFIG = {
  'mon-enquete': {
    '01-intro': {
      id: '01-intro',
      titre: 'Introduction',
      sections: [
        { id: '01a-contexte', type: 'default' },
        { id: '01b-resultats', type: 'socio-demo' },
      ]
    }
  }
}
```

2. **Générer les JSON** (Python) et les placer dans :
```
frontend/public/data/enquetes/mon-enquete/chapitres/chapitre-01-intro/
├── index.json
├── 01a-contexte.json
└── 01b-resultats.json
```

3. **C'est tout !** Le routing se fait automatiquement via `/enquetes/mon-enquete/chapitre/01-intro`

### Types de sections disponibles

| Type | Composant | Usage |
|------|-----------|-------|
| `prenotions` | ChapterPrenotions | Vrai/Faux avec chiffres |
| `variable-construite` | ChapterVariableConstruite | Méthodologie + résultats |
| `socio-demo` | ChapterSection | V de Cramer + distributions |
| `profils-types` | ChapterProfilsTypes | Profils avec cartes |
| `default` | ChapterSection | Section générique |

---

## Workflow de création d'une analyse

### 1. Préparer les données (Python)

```python
# Charger
df = pd.read_excel('data/enquete.xlsx')

# Construire la variable cible
df['MA_VARIABLE'] = ...

# Analyser
socio_results = analyze_socio_demo(df)
reg_results = run_logistic_regression(...)
```

### 2. Générer les JSON

```python
# Sauvegarder
save_json(index_data, 'output/index.json')
save_json(section_data, 'output/01a-section.json')
```

### 3. Copier vers le frontend

```bash
cp -r output/* frontend/public/data/enquetes/mon-enquete/chapitres/
```

### 4. Configurer le chapitre (si nouveau)

Éditer `frontend/src/config/chapters.js`

### 5. Tester

```bash
cd frontend && npm run dev
```

---

## Conventions

### Nommage des fichiers JSON

- `index.json` : Index du chapitre
- `01a-prenotions.json` : Section avec préfixe numéro + lettre
- Le préfixe définit l'ordre d'affichage

### Structure d'un JSON de section

```json
{
  "id": "01a-prenotions",
  "titre": "Idées reçues",
  "sousTitre": "Ce que les données nous apprennent",
  "description": "Introduction de la section",
  "sections": [
    {
      "id": "sous-section-1",
      "titre": "Titre",
      "visualisations": [...]
    }
  ],
  "noteMethodologique": {...},
  "synthese": {...},
  "metadata": {...}
}
```

### Couleurs standards

```javascript
const COULEURS = {
  rouge: '#EF4444',
  orange: '#F59E0B', 
  vert: '#10B981',
  bleu: '#3B82F6',
  indigo: '#6366F1',
  violet: '#8B5CF6',
  rose: '#EC4899'
}
```

---

## Déploiement sur Vercel

### Configuration

1. Créer un fichier `vercel.json` à la racine :

```json
{
  "buildCommand": "cd frontend && npm run build",
  "outputDirectory": "frontend/dist",
  "framework": "vite"
}
```

2. Connecter le repo GitHub à Vercel

3. Les JSON dans `public/data/` sont servis statiquement

### Variables d'environnement

Aucune requise pour le moment (tout est statique).

---

## Prochaines améliorations suggérées

- [ ] Tests unitaires Python (pytest)
- [ ] Tests React (Vitest)
- [ ] Lazy loading des sections
- [ ] Mode sombre
- [ ] Export PDF des chapitres
- [ ] API backend pour requêtes dynamiques
