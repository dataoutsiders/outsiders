# Feuille de route : Les Français et l'information (ARCOM 2024)

## Progression

### Preparation des donnees
| Etape | Statut | Date |
|-------|--------|------|
| Preparation des donnees | OK | 2024-12 |
| Dictionnaire des variables | OK | 2024-12 |
| Exploration variables ACM | OK | 2024-12 |
| ACM v1 (sources + interet + confiance) | OK | 2024-12 |

### Chapitres (structure narrative)

La structure suit une logique de livre :
- **Prologue** : chiffres cles accessibles
- **Chapitres** : exploration thematique
- **Epilogue** : synthese ACM + profils-types (classification)

| Chapitre | Titre | Statut | JSON |
|----------|-------|--------|------|
| Prologue | Vue d'ensemble | A faire | prologue.json |
| 1 | Le grand basculement (TV vs RS) | OK | 01-basculement.json |
| 2 | Ceux qui decrochent | A faire | 02-decrochage.json |
| 3 | La crise de confiance | A faire | 03-defiance.json |
| 4 | Verite et croyances | A faire | 04-complotisme.json |
| 5 | L'ere des algorithmes | A faire | 05-algorithmes.json |
| 6 | Savoir vs Croire | A faire | 06-savoir-croire.json |
| Epilogue | Synthese (ACM + Classification) | A faire | epilogue.json |

### Frontend
| Etape | Statut |
|-------|--------|
| Architecture documentee | OK |
| Composants chapitres | A faire |
| Visualisations | A faire |
| Integration JSON | A faire |

---

## Travail realise

### 1. Preparation des donnees

**Scripts crees :**
- `python/scripts/build_dictionnaire.py` : Extrait les labels des variables depuis le datamap
- `python/scripts/explore_variables_acm.py` : Analyse la qualite des variables pour l'ACM

**Fichiers generes :**
- `python/data/francais-information/dictionnaire.json` : 1076 variables avec labels
- `python/outputs/exploration_variables_acm.md` : Rapport detaille sur 24 variables candidates

### 2. ACM v1 - Pratiques d'information

**Script :** `python/scripts/run_acm.py`

**Variables actives utilisees :**
```
NEWS1_R_1  : Frequence TV
NEWS1_R_2  : Frequence Radio
NEWS1_R_3  : Frequence Presse ecrite
NEWS1_R_4  : Frequence Sites/apps medias
NEWS1_R_5  : Frequence Reseaux sociaux
NEWS1_R_6  : Frequence Podcasts
NEWS1_R_7  : Frequence Entourage
INT1_R     : Interet global pour l'info
CONF1_R    : Confiance generale medias
```

**Variables supplementaires (projetees) :**
```
RS1_R              : Genre
RS2C_RECODE_AG_R   : Age (7 tranches)
CSPIND_R           : CSP (CSP+, CSP-, Inactif)
```

**Resultats :**
- 2 854 repondants apres nettoyage (sur 3 346)
- Axe 1 : 7.0% d'inertie
- Axe 2 : 5.2% d'inertie
- Total axes 1+2 : 12.2%

**Interpretation des axes :**

| Axe | Pole negatif | Pole positif |
|-----|--------------|--------------|
| **Axe 1** | "Jamais" sur toutes les sources, pas interesse | Usage quotidien multi-sources, confiance elevee |
| **Axe 2** | Usage occasionnel (1x/sem, 1-3x/mois) | Non-utilisateurs des medias traditionnels |

**Fichiers generes :**
```
python/outputs/acm_modalites.html       <- Carte des modalites (interactif)
python/outputs/acm_individus_age.html   <- Individus colores par age
python/outputs/acm_individus_csp.html   <- Individus colores par CSP
```

---

## Vue d'ensemble des donnees

**Source** : Enquete ARCOM "Les Francais et l'information" (2024)
**Echantillon** : 3 346 repondants (France metropolitaine + DOM-TOM)
**Methode** : CATI + CAWI
**Ponderation** : Variable `POIDS03`

### Variables socio-demographiques

| Variable | Description | Modalites |
|----------|-------------|-----------|
| `RS1_R` | Genre | Homme, Femme, Non binaire |
| `RS2C_RECODE_AG_R` | Age | 7 tranches (15-17 a 70+) |
| `CSPIND_R` | CSP recodee | CSP+, CSP-, Inactive, NSP |
| `RS5_R` | Niveau d'etudes | 9 niveaux (primaire a doctorat) |
| `UDA5_R` / `UDA9_R` | Region | 5 ou 9 zones |
| `RS15_R` | Frequence internet | Plusieurs fois/jour a moins souvent |

### Blocs thematiques

| Bloc | Variables | Description |
|------|-----------|-------------|
| **Interet pour l'info** | INT1, INT2, INT3 | Niveau d'interet global et par thematique |
| **Motivations** | MOTIV | Pourquoi s'informer ? |
| **Sources & modes d'acces** | NEWS1, NEWS1SOURCES | Frequence d'usage des medias |
| **Propension a payer** | PAY | Disposition a payer pour l'info |
| **Reseaux sociaux** | RSINFO | Plateformes utilisees pour s'informer |
| **Formats** | FORMAT | Preferences de format (video, texte, audio) |
| **Dynamique** | DYN1, DYN2, DYN3 | Evolution de la consommation |
| **Evitement** | EVITE1, EVITE2 | News avoidance et strategies |
| **Confiance** | CONF1, INF3 | Confiance dans les infos et sources |
| **Defiance journalisme** | DEFIANCEJ, VALEURJ, ATTENTESJ | Raisons de la defiance |
| **Fake news / Complot** | COMPLOT1, COMPLOT2, INFOFIABLE | Exposition et adhesion |
| **Algorithmes** | CONNAISSALGOA, CONNAISSALGOB | Connaissance et attitudes |
| **Intelligence artificielle** | IA1, CRAINTESALGOIA | Notoriete IA, craintes |
| **Confiance institutions** | CONFINST, DEM | Confiance institutions, democratie |
| **Politique** | NOU1_R, PP3_R | Echelle gauche-droite, vote 2022 |
| **Quizz connaissance** | QUIZZ1-4 | Test de connaissance factuelle |

---

## Problematiques de recherche

### Axe 1 : Cartographie sociale de l'information
> **Question** : Comment les pratiques informationnelles dessinent-elles un espace social ?

**Statut : EN COURS**

L'ACM v1 montre deux dimensions principales :
1. **Intensite de consommation** : des "desengages" aux "hyper-connectes"
2. **Type de rapport aux medias** : occasionnels vs non-utilisateurs traditionnels

**Prochaines iterations :**
- Ajouter les variables INT2 (interet par thematique) pour enrichir
- Projeter les variables politiques (NOU1_R, PP3_R) en supplementaire
- Identifier des clusters/profils-types

---

### Chapitre 1 : La television cede-t-elle sa place aux reseaux sociaux ?

> **Question centrale** : Assiste-t-on a une transformation des pratiques informationnelles, et si oui, est-ce un effet d'age ou une mutation sociale/technologique plus profonde ?

**Statut : EN COURS (structure definie)**

---

#### PARTIE 1 : Les usages (tous supports)

**1.1 Source principale d'information**
- Variable : `NEWS1BIS_R` (source principale declaree)
- Question : Quel support les Francais declarent-ils comme leur source principale ?

**1.2 Frequence d'usage par support**
- Variables : `NEWS1_R_1` a `NEWS1_R_7` (TV, Radio, Presse, Sites/apps, RS, Podcasts, Entourage)
- Questions :
  - Quels supports sont utilises au moins 1x/jour ?
  - Quels supports ne sont jamais utilises ?
  - Distribution des frequences par support

**1.3 Equipement disponible**
- Variables : A identifier (equipement menage, acces internet...)
- Question : De quoi disposent les Francais pour s'informer ?

**1.4 Plateformes specifiques (pour RS)**
- Variables : `RSINFO_2_LR_R_1` a `RSINFO_2_LR_R_13`
- Question : Parmi ceux qui s'informent via RS, quelles plateformes ?

---

#### PARTIE 2 : Facteurs socio-demographiques

**2.1 Age**
- Variable : `RS2C_RECODE_AG_R` (7 tranches)
- Question : Y a-t-il un effet generationnel ?

**2.2 Sexe**
- Variable : `RS1_R`
- Question : Hommes et femmes s'informent-ils differemment ?

**2.3 Milieu social**
- Variables : `CSPIND_R` (CSP), `RS5_R` (niveau etudes)
- Question : L'origine sociale influence-t-elle les pratiques ?

**2.4 Budget / Revenus**
- Variables : A identifier
- Question : Le budget contraint-il les choix ?

**2.5 Zone geographique**
- Variables : `UDA5_R`, `UDA9_R`, taille d'agglomeration
- Question : Rural vs urbain, differences regionales ?

---

#### PARTIE 3 : Facteurs culturels

**3.1 Rapport a l'information**
- Variables : `INT1_R` (interet general), `INT2_R` (par thematique), `INT3_R` (sentiment d'etre informe)
- Question : Le rapport a l'info influence-t-il le support ?

**3.2 Type d'information selon le support**
- Variables : `INT2_R_*` (interet par theme) x `NEWS1BIS_R`
- Question : Certains supports sont-ils associes a certains types d'info ?

**3.3 Motivations**
- Variables : `MOTIVRS_R_*` (motivations RS), `MOTIV_R_*` (motivations generales)
- Question : Pourquoi choisit-on tel ou tel support ?

**3.4 Confiance**
- Variable : `CONF1_R`
- Question : La confiance varie-t-elle selon le support ?

---

#### PARTIE 4 : Facteurs axiologiques (valeurs)

**4.1 Positionnement politique**
- Variables : `NOU1_R` (echelle gauche-droite), `PP3_R` (vote 2022)
- Question : Le choix de support est-il lie aux valeurs politiques ?

**4.2 Rapport aux institutions**
- Variables : `CONFINST_R_*`, `DEM_R`
- Question : Defiance institutionnelle et choix de support ?

**4.3 Adhesion complotiste**
- Variables : `COMPLOT1_R`, `COMPLOT2_R`
- Question : Les "complotistes" ont-ils des pratiques specifiques ?

---

#### PARTIE 5 : Effet du support sur la connaissance

**5.1 Score au quizz**
- Variables : `QUIZZ1_R` a `QUIZZ4_R`
- Question : Est-on mieux informe selon le support utilise ?

**5.2 Croisement support x quizz x age**
- Question : L'effet du support sur la connaissance varie-t-il selon l'age ?

---

#### CONCLUSION : Effet d'age ou transformation sociale ?

**Methode** : Croiser les resultats des parties 1-5 pour distinguer :
- **Effet de cohorte** : les jeunes d'aujourd'hui garderont-ils leurs pratiques en vieillissant ?
- **Effet d'age** : les pratiques changent-elles avec l'age (cycle de vie) ?
- **Transformation structurelle** : mutation technologique/sociale qui touche toutes les generations ?

---

**Analyses deja realisees :**
- `chapitre_01_basculement.py` : Source principale par age (NEWS1BIS_R)
- `chapitre_01_complement_plateformes.py` : Plateformes RS par age
- `chapitre_01_complement_quizz.py` : Score quizz par source et age
- `chapitre_01_complement_profil_jeunes.py` : Profil socio-demo des jeunes RS

**Analyses a faire :**
- Frequence d'usage quotidien par support
- Equipement disponible
- Croisements zone geographique
- Facteurs culturels (INT2, MOTIV)
- Facteurs axiologiques (NOU1, PP3, COMPLOT)

---

### Axe 3 : Qui decroche de l'information ?
> **Question** : Qui sont les "decrocheurs" et pourquoi abandonnent-ils ?

**Statut : A FAIRE**

**Variables** :
- DYN1_R (dynamique : plus/moins/arret)
- EVITE1_R, EVITE2_R (evitement volontaire)
- x socio-demo + NOU1_R (politique)

**Analyses prevues** :
- Profil des decrocheurs (regression logistique)
- Raisons du decrochage (DYN2)
- Lien avec positionnement politique

---

### Axe 4 : La defiance - Fracture sociale ou politique ?
> **Question** : La defiance envers les medias est-elle un marqueur de classe ou de positionnement politique ?

**Statut : A FAIRE**

**Variables** :
- CONF1_R (confiance generale)
- DEFIANCEJ_R (raisons de la defiance)
- x CSPIND_R, RS5_R, NOU1_R, PP3_R

---

### Axe 5 : Complotisme et legitimites
> **Question** : Qui adhere aux theories complotistes ?

**Statut : A FAIRE**

**Variables** :
- COMPLOT1_R, COMPLOT2_R (exposition et adhesion)
- x RS5_R, CSPIND_R, NOU1_R, PP3_R, CONF1_R

---

### Axe 6 : Algorithmes et IA
> **Question** : Comment les Francais percoivent-ils le role des algorithmes et de l'IA ?

**Statut : A FAIRE**

**Variables** :
- CONNAISSALGOA_R, CONNAISSALGOB_R (connaissance algos)
- IA1_R (notoriete IA generative)
- CRAINTESALGOIA_R (craintes)
- x age, CSP, niveau d'etudes

---

### Axe 7 : Savoir vs Croire
> **Question** : Y a-t-il un decalage entre le sentiment d'etre informe et le niveau reel de connaissance ?

**Statut : A FAIRE**

**Variables** :
- INT3_R (sentiment d'etre bien informe)
- QUIZZ1-4 (connaissance prouvee)
- x sources utilisees, CSP, age

---

## Livrables attendus

### Pour le site web (JSON)

```
frontend/public/data/enquetes/francais-information/
├── overview.json              # Statistiques generales
├── acm.json                   # Coordonnees ACM + profils
├── sources-generations.json
├── decrochage.json
├── defiance.json
├── complotisme.json
├── algorithmes-ia.json
└── savoir-croire.json
```

### Visualisations

1. **ACM interactive** : Carte des pratiques avec zoom sur profils
2. **Graphiques comparatifs** : Barres/donuts par generation, CSP
3. **Heatmaps** : Croisements sources x socio-demo
4. **Regressions** : Forest plots des facteurs explicatifs

---

## Conventions d'écriture

### Accents obligatoires
**IMPORTANT** : Tous les textes destinés à l'affichage (JSON, config, composants) doivent utiliser les accents français :
- ✅ "Les Français et l'information"
- ❌ "Les Francais et l'information"
- ✅ "enquête", "médias", "générations", "défiance"
- ❌ "enquete", "medias", "generations", "defiance"

Cette règle s'applique à :
- Les fichiers JSON générés par Python
- Les fichiers de configuration frontend (enquetes.js, themes.js)
- Les labels et descriptions dans les composants React

---

## Notes methodologiques

### Ponderation
Toutes les analyses doivent utiliser `POIDS03` pour le redressement.

### Gestion des non-reponses
- Exclure les NSP/refus des analyses principales
- Analyser separement le profil des non-repondants si significatif

### Seuils de significativite
- Chi2 : p < 0.05
- Regressions : IC 95%
- ACM : contribution > moyenne pour interpretation

### Reproductibilite
- Tout le code Python versionne
- Seeds fixes pour clustering (random_state=42)
- Exports JSON horodates

---

## Pour reprendre le travail

### Lancer l'environnement

```bash
# Activer l'environnement virtuel
.venv\Scripts\activate

# Verifier les packages
pip list
```

### Scripts disponibles

```bash
# Construire le dictionnaire (deja fait)
python python/scripts/build_dictionnaire.py

# Explorer les variables pour l'ACM
python python/scripts/explore_variables_acm.py

# Lancer l'ACM
python python/scripts/run_acm.py
```

### Visualiser les resultats

Ouvrir dans un navigateur :
- `python/outputs/acm_modalites.html`
- `python/outputs/acm_individus_age.html`
- `python/outputs/acm_individus_csp.html`

### Prochaine etape suggeree

1. **Enrichir l'ACM** : Ajouter les variables INT2 (interet par thematique)
2. **Projeter les variables politiques** : NOU1_R en supplementaire
3. **Identifier des clusters** : K-means sur les coordonnees ACM
4. **Commencer les tris croises** : TV vs RS par generation
