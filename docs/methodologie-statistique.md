# Méthodologie statistique - Outsiders

Documentation de la méthodologie statistique utilisée pour l'analyse des données d'enquête ARCOM 2024.

## Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Données source](#données-source)
3. [Chapitre 1 : Le basculement numérique](#chapitre-1--le-basculement-numérique)
   - [Construction de la variable BASCULEMENT](#construction-de-la-variable-basculement)
   - [Analyse bivariée : V de Cramer](#analyse-bivariée--v-de-cramer)
   - [Régression logistique](#régression-logistique)
   - [Probabilités prédites par variable](#probabilités-prédites-par-variable)
   - [Profils multi-variables](#profils-multi-variables)
4. [Pondération](#pondération)
5. [Composants de visualisation](#composants-de-visualisation)
6. [Structure des fichiers JSON](#structure-des-fichiers-json)

---

## Vue d'ensemble

L'analyse statistique du chapitre 1 suit cette logique :

```
┌─────────────────────────────────────────────────────────────────────┐
│  1. CONSTRUCTION : Variable binaire BASCULEMENT                     │
│     → Traditionnel (TV/Radio/Presse ≥ RS) vs Numérique (RS > autres)│
└─────────────────────────────────────────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────────┐
│  2. DESCRIPTION : V de Cramer                                       │
│     → Force d'association avec les variables socio-démographiques   │
│     → Classement des facteurs les plus discriminants                │
└─────────────────────────────────────────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────────┐
│  3. EFFET NET : Régression logistique multivariée                   │
│     → Contrôle simultané de toutes les variables                    │
│     → Identification des effets significatifs "toutes choses égales"│
└─────────────────────────────────────────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────────┐
│  4. QUANTIFICATION : Probabilités prédites                          │
│     → Par variable : probabilité pour chaque modalité               │
│     → Multi-profil : probabilité pour des combinaisons extrêmes     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Données source

### Fichiers

| Fichier | Description |
|---------|-------------|
| `python/data/francais-information/base-info-arcom.xlsx` | Données brutes (3346 observations) |
| `python/data/francais-information/datamap-info-arcom.xlsx` | Dictionnaire des variables et labels |

### Variable de pondération

```python
# Conversion du format français (virgule) vers float
df['POIDS03'] = df['POIDS03'].astype(str).str.replace(',', '.').astype(float)

# Vérification
# min=0.13, max=4.00, sum≈3346
```

---

## Chapitre 1 : Le basculement numérique

### Construction de la variable BASCULEMENT

La variable `BASCULEMENT` oppose deux modes de consommation de l'information :

- **Traditionnel** (codé 0) : TV, Radio ou Presse ≥ Réseaux Sociaux
- **Numérique** (codé 1) : Réseaux Sociaux > tous les autres médias

```python
# Variables de fréquence d'usage (1=Tous les jours à 6=Jamais)
freq_vars = {
    'TV': 'FREQMEDIA_R_1',
    'Radio': 'FREQMEDIA_R_2',
    'Presse': 'FREQMEDIA_R_3',
    'RS': 'FREQMEDIA_R_6'
}

# Inversion pour que les scores élevés = usage fréquent
for var in freq_vars.values():
    df[f'{var}_INV'] = 7 - df[var]

# Score maximum des médias traditionnels
df['MAX_TRAD'] = df[['FREQMEDIA_R_1_INV', 'FREQMEDIA_R_2_INV', 'FREQMEDIA_R_3_INV']].max(axis=1)

# Variable binaire
df['BASCULEMENT'] = (df['FREQMEDIA_R_6_INV'] > df['MAX_TRAD']).astype(int)
```

**Résultat** : 52.8% Traditionnels, 47.2% Numériques (pondéré)

---

### Analyse bivariée : V de Cramer

Le V de Cramer mesure la force d'association entre deux variables catégorielles.

#### Interprétation

| V de Cramer | Force |
|-------------|-------|
| 0 - 0.10 | Négligeable |
| 0.10 - 0.20 | Faible |
| 0.20 - 0.30 | Modérée |
| 0.30+ | Forte |

#### Variables analysées

| Variable | Code | Description |
|----------|------|-------------|
| Âge | `RS2C_RECODE_AG_R` | 7 tranches (15-17 à 70+) |
| Genre | `RS1_R` | Homme (1), Femme (2) |
| Situation professionnelle | `RS3_R` | Actif, Retraité, Étudiant, etc. |
| CSP | `RS4_R` | 7 modalités (Agriculteur à Ouvrier) |
| Diplôme | `DIPLOME_REGROUPE` | Bas, Moyen, Supérieur |
| Taille d'agglomération | `CC_R` | Rural (1) à Grande ville (5) |
| Revenu | `REVENU_CAT` | Terciles (Bas, Moyen, Haut) |

#### Calcul pondéré

```python
def get_chi2_stats(df, var1, var2, poids='POIDS03'):
    """Calcule Chi2 et V de Cramer avec pondération"""
    ct = pd.crosstab(
        df[var1], df[var2],
        values=df[poids], aggfunc='sum'
    ).fillna(0)

    chi2, p, dof, _ = stats.chi2_contingency(ct)
    n = ct.sum().sum()
    min_dim = min(ct.shape) - 1
    v = np.sqrt(chi2 / (n * min_dim))

    return {'chi2': chi2, 'p': p, 'v_cramer': v}
```

#### Résultats Chapitre 1

| Variable | V de Cramer | Interprétation |
|----------|-------------|----------------|
| Âge | 0.38 | Fort |
| Situation pro. | 0.26 | Modéré |
| CSP | 0.15 | Faible |
| Diplôme | 0.12 | Faible |
| Taille agglo | 0.11 | Faible |
| Revenu | 0.09 | Négligeable |
| Genre | 0.04 | Négligeable |

---

### Régression logistique

#### Objectif

Identifier quelles variables ont un effet **significatif** sur le basculement, en contrôlant simultanément toutes les autres variables.

#### Variables de contrôle (dummies)

```python
# Âge (référence : 25-34 ans)
reg_df['AGE_1'] = (reg_df['AGE'] == 1).astype(int)  # 15-17 ans
reg_df['AGE_2'] = (reg_df['AGE'] == 2).astype(int)  # 18-24 ans
reg_df['AGE_3'] = (reg_df['AGE'] == 3).astype(int)  # 25-34 ans
reg_df['AGE_6'] = (reg_df['AGE'] == 6).astype(int)  # 60-69 ans
reg_df['AGE_7'] = (reg_df['AGE'] == 7).astype(int)  # 70+ ans

# Genre (référence : Homme)
reg_df['FEMME'] = (reg_df['RS1_R'] == 2).astype(int)

# Situation pro (référence : Actif)
reg_df['RETRAITE'] = (reg_df['RS3_R'] == 5).astype(int)

# Diplôme (référence : Moyen)
reg_df['DIPLOME_BAS'] = (reg_df['DIPLOME_REGROUPE'] == 'Bas').astype(int)
reg_df['DIPLOME_SUP'] = (reg_df['DIPLOME_REGROUPE'] == 'Superieur').astype(int)

# Taille agglo (référence : Moyen)
reg_df['RURAL'] = (reg_df['CC_R'] == 1).astype(int)
reg_df['URBAIN'] = (reg_df['CC_R'] == 5).astype(int)

# Revenu - terciles (référence : Moyen)
q33 = df['RS14_R'].quantile(0.33)
q66 = df['RS14_R'].quantile(0.66)
reg_df['REVENU_BAS'] = (reg_df['REVENU_CAT'] == 'Bas').astype(int)
reg_df['REVENU_HAUT'] = (reg_df['REVENU_CAT'] == 'Haut').astype(int)

# CSP (référence : autres CSP)
reg_df['CSP_CADRE'] = (reg_df['RS4_R'] == 3).astype(int)
reg_df['CSP_OUVRIER'] = (reg_df['RS4_R'] == 6).astype(int)
```

#### Modèle

```python
control_vars = [
    'AGE_1', 'AGE_2', 'AGE_3', 'AGE_6', 'AGE_7',
    'FEMME', 'RETRAITE',
    'DIPLOME_BAS', 'DIPLOME_SUP',
    'RURAL', 'URBAIN',
    'REVENU_BAS', 'REVENU_HAUT',
    'CSP_CADRE', 'CSP_OUVRIER'
]

X = reg_df[control_vars]
X = sm.add_constant(X)
y = reg_df['BASCULEMENT']
weights = reg_df['POIDS03']

model = sm.GLM(y, X, family=sm.families.Binomial(), freq_weights=weights)
results = model.fit()
```

#### Résultats significatifs (p < 0.05)

| Variable | Coefficient | p-value | Interprétation |
|----------|-------------|---------|----------------|
| AGE_2 (18-24) | +1.09 | 0.000 | Très significatif positif |
| AGE_3 (25-34) | +0.86 | 0.000 | Très significatif positif |
| AGE_6 (60-69) | -0.54 | 0.016 | Significatif négatif |
| RURAL | -0.39 | 0.014 | Significatif négatif |
| URBAIN | +0.30 | 0.005 | Significatif positif |
| REVENU_HAUT | -0.36 | 0.003 | Significatif négatif |
| CSP_OUVRIER | -0.53 | 0.000 | Très significatif négatif |

#### Variables NON significatives

| Variable | p-value | Conclusion |
|----------|---------|------------|
| FEMME | 0.82 | **Aucune différence genrée** |
| RETRAITE | 0.99 | Effet capté par l'âge |
| DIPLOME_BAS | 0.20 | Pas d'effet net |
| DIPLOME_SUP | 0.48 | Pas d'effet net |
| CSP_CADRE | 0.30 | Pas d'effet net |

---

### Probabilités prédites par variable

#### Principe

Pour chaque variable significative, on calcule la probabilité d'être "Numérique" pour ses modalités extrêmes, **toutes autres variables fixées à leur valeur de référence**.

#### Bug corrigé : Ordre des colonnes

**Problème** : `pd.DataFrame([dict])` ne garantit pas l'ordre des colonnes. Or `statsmodels.predict()` attend les colonnes dans l'ordre exact du modèle.

**Symptôme** : Probabilités inversées (Rural à 62% au lieu de 37%)

**Solution** : Fonction `make_profile()` avec ordre explicite

```python
# Sauvegarder l'ordre des colonnes du modèle
model_columns = list(X.columns)

def make_profile(**kwargs):
    """Crée un DataFrame avec les colonnes dans l'ordre exact du modèle"""
    # Initialiser toutes les variables à 0 (référence)
    profile = {col: 0 for col in model_columns}
    profile['const'] = 1  # Constante toujours à 1

    # Appliquer les valeurs spécifiées
    for k, v in kwargs.items():
        profile[k] = v

    # Créer le DataFrame avec l'ordre garanti
    return pd.DataFrame([[profile[col] for col in model_columns]], columns=model_columns)

# Exemple d'utilisation
prob_jeune = results.predict(make_profile(AGE_2=1))[0] * 100  # 18-24 ans
prob_senior = results.predict(make_profile(AGE_7=1))[0] * 100  # 70+ ans
```

#### Résultats : Effect Cards par variable

| Variable | Modalité Numérique | Prob. | Modalité Traditionnelle | Prob. | Ratio |
|----------|-------------------|-------|------------------------|-------|-------|
| Âge | 18-24 ans | 76.6% | 70+ ans | 12.2% | x6.3 |
| Taille agglo | Grande ville | 59.8% | Rural | 42.7% | x1.4 |
| Revenu | Revenu faible | 56.5% | Revenu élevé | 43.3% | x1.3 |
| CSP | Cadre | 48.5% | Ouvrier | 39.2% | x1.2 |

**Note sur le revenu** : Le résultat contre-intuitif (revenu faible = plus numérique) s'explique par la corrélation avec l'âge. Les jeunes ont des revenus plus bas ET sont plus numériques. L'effet net du revenu, une fois l'âge contrôlé, reste significatif.

---

### Profils multi-variables

#### Principe

Combiner plusieurs caractéristiques pour créer des "profils types" et calculer leur probabilité d'être numérique.

#### Profils définis

| Profil | Caractéristiques | Probabilité |
|--------|-----------------|-------------|
| **Jeune urbain cadre** | AGE_2=1, URBAIN=1, CSP_CADRE=1 | 79.2% |
| **Profil référence** | Toutes variables à 0 | 52.3% |
| **Senior rural** | AGE_7=1, RURAL=1 | 8.6% |

**Note** : Le profil "traditionnel" n'inclut pas de CSP car les 70+ ans sont majoritairement retraités.

#### Calcul

```python
# Profil "Numérique typique" : jeune, urbain, cadre
prob_num = results.predict(make_profile(AGE_2=1, CSP_CADRE=1, URBAIN=1))[0] * 100

# Profil "Traditionnel typique" : senior, rural
prob_trad = results.predict(make_profile(AGE_7=1, RURAL=1))[0] * 100

# Ratio entre profils extrêmes
ratio_profils = round(prob_num / prob_trad, 1)  # ≈ x9.2
```

---

## Pondération

### Application systématique

| Analyse | Méthode |
|---------|---------|
| Tableaux de contingence | `pd.crosstab(..., values=df['POIDS03'], aggfunc='sum')` |
| Régression logistique | `sm.GLM(..., freq_weights=weights)` |
| Pourcentages | `(df[var] * df['POIDS03']).sum() / df['POIDS03'].sum()` |

### Vérification

```python
# Les poids doivent sommer au total d'observations
assert abs(df['POIDS03'].sum() - len(df)) < 1
```

---

## Composants de visualisation

### Fichiers React

| Composant | Usage | Fichier |
|-----------|-------|---------|
| `EffectCardsParVariable` | Probabilités par variable avec barre de progression | `frontend/src/components/visualizations/EffectCardsParVariable.jsx` |
| `EffectCardsProfils` | Cartes des 3 profils multi-variables | `frontend/src/components/visualizations/EffectCardsProfils.jsx` |
| `VCramerBarChart` | Graphique horizontal des V de Cramer | `frontend/src/components/visualizations/VCramerBarChart.jsx` |
| `DistributionBar` | Barre Traditionnel/Numérique | `frontend/src/components/visualizations/DistributionBar.jsx` |
| `ChapterSection` | Container de section avec routing des visualisations | `frontend/src/components/chapter/ChapterSection.jsx` |

### Types de visualisation

```javascript
const chartComponents = {
  grouped_bar: GroupedBarChart,
  horizontal_bar: HorizontalBarChart,
  'horizontal-bar-chart': VCramerBarChart,
  effet_net_cards: EffetNetCards,
  v_cramer_table: VCramerTable,
  distribution_bar: DistributionBar,
  v_cramer_bar: VCramerBarChart,
  effect_cards_profils: EffectCardsProfils,
  effect_cards_par_variable: EffectCardsParVariable,
}
```

---

## Structure des fichiers JSON

### Arborescence

```
frontend/public/data/enquetes/francais-information/chapitres/chapitre-01-basculement/
├── index.json                 # Métadonnées du chapitre
├── 01a-prenotions.json       # Prénotions à déconstruire
├── 01b-variable-construite.json  # Distribution Trad/Num
├── 01c-qui-bascule.json      # Analyse socio-démo + régression
├── 01d-ce-qui-accompagne.json # Équipement, usages, valeurs
├── 01e-regression.json       # Détails de la régression
└── 01f-effets-stratifies.json # Effets par groupe d'âge
```

### Structure de 01c-qui-bascule.json

```json
{
  "id": "01c-qui-bascule",
  "titre": "Qui bascule ?",
  "sousTitre": "Le profil socio-démographique des numériques",
  "description": "...",

  "noteMethodologique": {
    "titre": "Comment lire le V de Cramer",
    "texte": "Le V de Cramer mesure la force du lien..."
  },

  "sections": [
    {
      "id": "v-cramer-overview",
      "titre": "Force des associations",
      "visualisations": [{
        "type": "v_cramer_bar",
        "data": [
          {"variable": "Âge", "v_cramer": 0.38, "var_code": "RS2C_RECODE_AG_R"},
          ...
        ]
      }]
    },
    {
      "id": "effet-net-par-variable",
      "titre": "Effet net par variable",
      "visualisations": [{
        "type": "effect_cards_par_variable",
        "data": [
          {
            "variable": "Âge",
            "var_code": "AGE",
            "modalite_numerique": "18-24 ans",
            "modalite_traditionnelle": "70 ans et +",
            "prob_numerique": 76.6,
            "prob_traditionnelle": 12.2,
            "ratio": 6.3,
            "couleur": "#10B981"
          },
          ...
        ]
      }]
    },
    {
      "id": "probabilites-predites",
      "titre": "Les profils combinés les plus opposés",
      "visualisations": [{
        "type": "effect_cards_profils",
        "data": [
          {
            "id": "numerique",
            "label": "Jeune urbain cadre",
            "description": "18-24 ans, grande ville, cadre",
            "probabilite": 79.2,
            "groupe": "numerique",
            "couleur": "#10B981"
          },
          ...
        ],
        "ratio_max": 9.2
      }]
    }
  ],

  "synthese": {
    "titre": "En résumé",
    "points": [
      "L'âge est le facteur le plus fortement associé au basculement (V=0.38).",
      "La situation professionnelle est également discriminante (V=0.26).",
      "Le diplôme, la CSP et le revenu jouent un rôle plus modéré.",
      "Le genre n'a pas d'effet significatif sur le basculement."
    ]
  }
}
```

---

## Scripts de génération

### Script principal

```
python/scripts/generate_chapitre_01.py
```

### Exécution

```bash
cd outsiders
python python/scripts/generate_chapitre_01.py
```

### Output

```
Chargement des données...
Données chargées : 3346 observations

Construction de la variable Traditionnel/Numérique...
Traditionnel: 1684 (52.8% pondéré)
Numérique: 1614 (47.2% pondéré)

Génération de 01c-qui-bascule.json...
  Coefficients de la régression:
    AGE_2           +1.094 (p=0.0000) ***
    AGE_3           +0.858 (p=0.0000) ***
    URBAIN          +0.304 (p=0.0050) **
    RURAL           -0.387 (p=0.0135) *
    REVENU_HAUT     -0.362 (p=0.0030) **
    CSP_OUVRIER     -0.531 (p=0.0001) ***
    FEMME           +0.022 (p=0.8233)    <- Non significatif

  Probabilités multi-profil:
    Jeune urbain cadre: 79.2%
    Profil référence: 52.3%
    Senior rural: 8.6%

GÉNÉRATION TERMINÉE
```

---

## Résumé des conclusions statistiques

### Ce qui influence le basculement numérique

1. **L'âge** est le facteur dominant (V=0.38). Les 18-24 ans ont 6x plus de chances d'être numériques que les 70+.

2. **Le lieu de résidence** : les urbains sont plus numériques que les ruraux (ratio x1.4).

3. **Le revenu** : contre-intuitivement, les revenus faibles sont associés au numérique (effet de l'âge).

4. **La CSP** : les ouvriers sont moins numériques que les cadres (ratio x1.2).

### Ce qui n'influence PAS le basculement

- **Le genre** : aucune différence significative entre hommes et femmes (p=0.82)
- **Le diplôme** : pas d'effet net une fois l'âge contrôlé
- **Le statut de retraité** : effet capté par l'âge

### Profils extrêmes

Un **jeune urbain cadre** a environ **9x plus de chances** d'être numérique qu'un **senior rural**.
