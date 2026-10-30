# Architecture Frontend - Outsiders

## Vision

Outsiders est une plateforme d'analyses sociologiques qui :
- **Informe** les citoyens curieux avec des visualisations accessibles
- **Outille** les journalistes avec des données citables et vérifiables
- **Eclaire** les décideurs publics avec des indicateurs actionnables

Chaque enquête raconte une histoire, comme un livre, tout en permettant une exploration libre.

---

## Navigation principale

```
Outsiders
├── Accueil
├── Enquêtes
│   └── [Enquête] ← Structure narrative en chapitres
├── Thèmes transversaux ← Grilles d'analyse sociologiques
├── Méthodologie
└── A propos
```

---

## Structure d'une enquête

Chaque enquête suit une structure de livre :

```
/enquetes/{enquete-id}/

├── Prologue
│   ├── Contexte : pourquoi cette enquête ?
│   ├── Methodologie rapide
│   └── Guide de lecture
│
├── Chapitres (questions de recherche)
│   ├── Chapitre 1 : [Titre]
│   ├── Chapitre 2 : [Titre]
│   └── ...
│
├── Epilogue
│   ├── Synthese
│   ├── Limites
│   └── Ouvertures
│
└── Ressources
    ├── Telechargements
    ├── Methodologie
---

## Structure d'un chapitre

Chaque chapitre suit une progression narrative en 4 temps + annexes :

### 1. L'accroche
- Question ou constat qui interpelle
- Chiffre marquant ou paradoxe
- Objectif : capter l'attention

### 2. L'analyse
- Visualisations interactives
- Explication des donnees
- Tests statistiques (Chi2, etc.)

### 3. Les nuances
- Ce qui complexifie le constat initial
- Exceptions, contre-exemples
- Intersections (ex: genre x classe)

### 4. Les implications
- Ce que cela signifie concretement
- Transition vers le chapitre suivant

### 5. Annexes (accordeons depliables)

#### Pour la presse
- **Le chiffre** : donnee cle facilement citable
- **La citation** : phrase de synthese
- **Le graphique** : telechargement HD (PNG, SVG)
- **Le contexte** : mise en garde contre le hors-contexte

#### Pour l'action publique
- **L'indicateur** : metrique suivable dans le temps
- **Le levier** : sur quoi l'action publique peut agir
- **La comparaison** : benchmark (autres pays, historique)
- **Les donnees liees** : liens vers sources officielles (data.gouv, rapports)

---

## Navigation

### Sidebar (sommaire)
- Toujours visible sur desktop
- Repliable sur mobile
- Indique le chapitre actif
- Permet de sauter a n'importe quel chapitre

### Navigation lineaire
- Boutons "Precedent" / "Suivant" en bas de page
- Progression naturelle comme un livre

### Barre de progression (optionnel)
- Indicateur visuel de l'avancement dans l'enquete

---

## Composants React

```
frontend/src/
├── components/
│   ├── layout/
│   │   ├── Header.jsx
│   │   ├── Footer.jsx
│   │   └── Layout.jsx
│   │
│   ├── enquete/
│   │   ├── EnqueteSidebar.jsx      # Sommaire lateral
│   │   ├── EnqueteNav.jsx          # Navigation precedent/suivant
│   │   ├── ChapterLayout.jsx       # Structure d'un chapitre
│   │   ├── ChapterSection.jsx      # Section (accroche, analyse, etc.)
│   │   └── ChapterAnnexes.jsx      # Accordeons presse/politique
│   │
│   ├── visualizations/
│   │   ├── ACMChart.jsx            # Carte ACM interactive
│   │   ├── BarChart.jsx            # Graphique en barres
│   │   ├── HeatMap.jsx             # Tableau croise colore
│   │   ├── DonutChart.jsx          # Camembert/donut
│   │   └── StatCard.jsx            # Chiffre cle en gros
│   │
│   └── ui/
│       ├── Accordion.jsx           # Pour les annexes
│       ├── DownloadButton.jsx      # Telechargement graphiques
│       └── Tooltip.jsx             # Info-bulles
│
├── pages/
│   ├── enquetes/
│   │   ├── EnquetesList.jsx        # Liste des enquetes
│   │   ├── EnqueteHome.jsx         # Page d'accueil enquete (prologue)
│   │   ├── EnqueteChapter.jsx      # Page chapitre
│   │   ├── EnqueteEpilogue.jsx     # Synthese
│   │   └── EnqueteResources.jsx    # Ressources/telechargements
│   │
│   └── ...
│
└── config/
    ├── enquetes.js                 # Metadata enquetes
    └── themes.js                   # Themes transversaux
```

---

## Structure des donnees JSON

```
frontend/public/data/
└── enquetes/
    └── francais-information/
        │
        ├── meta.json
        │   {
        │     "id": "francais-information",
        │     "titre": "Les Francais et l'information",
        │     "source": "ARCOM",
        │     "annee": 2024,
        │     "echantillon": 3346,
        │     "chapitres": [
        │       { "id": "carte", "titre": "La carte des pratiques", "sousTitre": "..." },
        │       { "id": "basculement", "titre": "Le grand basculement", "sousTitre": "..." },
        │       ...
        │     ]
        │   }
        │
        ├── prologue.json
        │   {
        │     "contexte": "...",
        │     "methodologie": { "echantillon": 3346, "methode": "CATI+CAWI", ... },
        │     "guidePrealable": "..."
        │   }
        │
        ├── chapitres/
        │   ├── 01-carte.json
        │   │   {
        │   │     "id": "carte",
        │   │     "titre": "La carte des pratiques",
        │   │     "question": "Comment les pratiques informationnelles dessinent un espace social ?",
        │   │     "accroche": {
        │   │       "texte": "Il n'existe pas UNE facon de s'informer...",
        │   │       "chiffreMarquant": { "valeur": "4", "label": "profils-types identifies" }
        │   │     },
        │   │     "analyse": {
        │   │       "sections": [...],
        │   │       "visualisations": [
        │   │         { "type": "acm", "data": {...}, "config": {...} }
        │   │       ]
        │   │     },
        │   │     "nuances": {...},
        │   │     "implications": {...},
        │   │     "annexes": {
        │   │       "presse": {
        │   │         "chiffreCle": "67% des hyper-connectes ont moins de 35 ans",
        │   │         "citation": "...",
        │   │         "graphiques": ["acm-modalites.png", "profils.png"]
        │   │       },
        │   │       "actionPublique": {
        │   │         "indicateur": "Part des citoyens desengages",
        │   │         "levier": "Education aux medias",
        │   │         "donneesLiees": ["https://data.gouv.fr/..."]
        │   │       }
        │   │     }
        │   │   }
        │   │
        │   ├── 02-basculement.json
        │   ├── 03-decrochage.json
        │   ├── 04-defiance.json
        │   ├── 05-complotisme.json
        │   └── 06-algorithmes.json
        │
        ├── epilogue.json
        │
        └── ressources.json
```

---

## Enquete ARCOM : Structure narrative

### Logique de progression

```
PROLOGUE : Vue d'ensemble accessible (chiffres cles, pas technique)
    ↓
CHAPITRES : Exploration thematique (une question = un chapitre)
    ↓
EPILOGUE : Synthese multivariee (ACM + Classification = profils-types)
```

L'ACM et la classification arrivent en conclusion pour :
- Synthetiser toutes les dimensions explorees
- Proposer des profils-types actionnables pour les politiques publiques
- Eviter de perdre le lecteur avec de la technique des le debut

### Chapitres prevus

| # | ID | Titre | Question | Analyse principale |
|---|-----|-------|----------|-------------------|
| - | prologue | Prologue | - | Chiffres cles, contexte |
| 1 | basculement | Le grand basculement | Assiste-t-on a un remplacement generationnel TV → RS ? | Tris croises, Chi2 |
| 2 | decrochage | Ceux qui decrochent | Qui sont les "decrocheurs" et pourquoi abandonnent-ils ? | Regression logistique |
| 3 | defiance | La crise de confiance | La defiance est-elle un marqueur de classe ou politique ? | Tris croises, regression |
| 4 | complotisme | Verite et croyances | Qui adhere aux theories complotistes ? | Tris croises |
| 5 | algorithmes | L'ere des algorithmes | Comment les Francais percoivent-ils algos et IA ? | Tris croises |
| 6 | savoir-croire | Savoir vs Croire | Y a-t-il un decalage sentiment/connaissance reelle ? | Score vs perception |
| - | epilogue | Synthese | Qui sont les Francais face a l'info ? | ACM + Classification (profils-types) |

### Profils-types attendus (epilogue)

La classification en conclusion permettra d'identifier des profils actionnables :

| Profil (exemple) | Description | Levier politique |
|------------------|-------------|------------------|
| Les engages confiants | Multi-sources, confiance, interet | Maintenir l'engagement |
| Les selectifs mefiants | RS uniquement, defiance medias | Education aux medias |
| Les decrocheurs | Evitement, desinteret | Strategies de reconnexion |
| Les vulnerables | Peu informes, complotisme | Prevention ciblee |

Ces profils seront affines apres l'analyse des donnees.

---

## Routes React Router

```javascript
// App.jsx
<Routes>
  {/* Pages generales */}
  <Route path="/" element={<Home />} />
  <Route path="/methodologie" element={<Methodologie />} />
  <Route path="/about" element={<About />} />

  {/* Enquetes */}
  <Route path="/enquetes" element={<EnquetesList />} />
  <Route path="/enquetes/:enqueteId" element={<EnqueteHome />} />
  <Route path="/enquetes/:enqueteId/prologue" element={<EnquetePrologue />} />
  <Route path="/enquetes/:enqueteId/chapitre/:chapitreId" element={<EnqueteChapter />} />
  <Route path="/enquetes/:enqueteId/epilogue" element={<EnqueteEpilogue />} />
  <Route path="/enquetes/:enqueteId/ressources" element={<EnqueteResources />} />

  {/* Themes transversaux (existant) */}
  <Route path="/themes" element={<ThemesList />} />
  <Route path="/themes/:themeId" element={<ThemeDetail />} />
</Routes>
```

---

## Responsive design

### Desktop (> 1024px)
- Sidebar sommaire visible a gauche
- Contenu principal au centre
- Annexes en accordeons

### Tablet (768px - 1024px)
- Sidebar repliable (hamburger)
- Contenu pleine largeur
- Annexes en accordeons

### Mobile (< 768px)
- Navigation par menu hamburger
- Sommaire en overlay
- Visualisations adaptees (scroll horizontal si besoin)
- Annexes en accordeons pleine largeur

---

## Prochaines etapes

1. [ ] Finaliser les analyses Python pour chaque chapitre
2. [ ] Generer les JSON selon la structure definie
3. [ ] Implementer les composants de base (ChapterLayout, Sidebar, Nav)
4. [ ] Implementer les visualisations (ACM, BarChart, etc.)
5. [ ] Connecter les donnees JSON aux composants
6. [ ] Tester et ajuster le responsive
7. [ ] Ajouter les annexes presse/action publique

---

## Notes

- Les chapitres peuvent evoluer au fil de l'exploration des donnees
- La structure est pensee pour etre reutilisable sur d'autres enquetes
- Les annexes "action publique" seront enrichies une fois l'enquete finalisee
