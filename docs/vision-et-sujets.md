# Outsiders, Vision, sujets & cadrage

> Document de travail. Garde le cap et évite le fourre-tout qui a tué la v1.
> Dernière maj : 2026-07-04 (sections J, croisements éditorialisés de l'Atlas, et K, pont socio-analyse).

## 1. Le cap

**Comprendre la France par ses angles morts.** Outsiders (clin d'œil à Becker) exploite des
**données ouvertes sous-exploitées** pour éclairer ce qui échappe au regard dominant. L'inégalité
de représentation n'est **qu'un sujet parmi d'autres**.

**Question unificatrice : *situer la France*.** Chaque sujet répond à « où en est la France, vue de
cet angle mort ? », soit :
- **en interne**, fractures territoriales / sociales (commune, département, bassin) ;
- **en comparé**, la France vs OCDE / UE / monde.

## 2. La discipline (anti-fourre-tout)

Tout nouveau sujet doit passer **trois tests**, sinon c'est un one-shot :
1. **Donnée riche et sous-exploitée** (peu de réutilisations, granularité fine, mise à jour vivante).
2. **Angle tranché**, une question qui dérange ou surprend, pas une description.
3. **Livrable réutilisable**, un **outil** (« tape ta commune / ton établissement / ton prénom »)
   *ou* une **carte / comparaison frappante** qu'on peut décliner.

On ajoute **2-3 sujets, pas 10**.

## 3. Architecture du site

Un étage au-dessus de la structure actuelle :

```
SUJETS (questions sur la France)
  └─ chaque sujet = TERRAINS × THÈMES  +  OUTILS
       Terrain = une population × tous les angles
       Thème   = un angle × tous les terrains
       Outil   = un instrument « apporte tes données »
```

- **Sujet #1 : Inégalités de représentation**, *fait* : moteur onomastique (IDP / sexe / âge,
  100% navigateur) + terrain « Les élus » (funnel, carte départements/EPCI, partis).
- La home présentera **plusieurs questions** (sujets), inégalités étant la première.

## 4. Shortlist des prochains sujets

| Sujet | Donnée (vérifiée sur data.gouv) | Angle | Livrable |
|---|---|---|---|
| **L'école trie-t-elle ?** ★ | IPS écoles/collèges/lycées (7-12 réutil. seulement) | ségrégation scolaire, cumul des 3 étapes | carte + « tape ton établissement » |
| **Où se situe la France ?** ★ | APIs Eurostat / OCDE / Banque mondiale | rang de la France par indicateur | comparateur international (2ᵉ moteur) |
| La France des distances | Base permanente des équipements (INSEE) | accès aux services, déserts | « tape ta commune » |
| Combien vaut ta rue ? | DVF (valeurs foncières) | prix au m², gentrification | carte / outil |
| Sociologie des prénoms | Fichier prénoms INSEE (déjà en main) | « ton prénom dit quoi ? » | outil viral, quasi gratuit |

Deux piliers à garder : **interne** (l'école) + **international** (le comparateur).

---

## 5. Sujet en cours : **L'École** (école + collège + lycée)

### Question
**L'école française trie-t-elle, et où ?** Surtout : **qui cumule les trois étapes**,
école → collège → lycée, du côté défavorisé (triple peine / relégation) ou favorisé
(entre-soi qui se renforce) ?

### Données (open data, à recouper)
- **IPS** (Indice de Position Sociale) **écoles / collèges / lycées**, Éducation nationale.
  *Vérifié en direct (2026-06) : les 3 fichiers existent, frais, 7-12 réutilisations.* C'est le
  **dénominateur commun** aux 3 niveaux : composition sociale de chaque établissement.
- **Résultats & valeur ajoutée** :
  - Collèges : **résultats du DNB** par établissement (+ valeur ajoutée).
  - Lycées : **IVAL** (Indicateurs de Valeur Ajoutée des Lycées), réussite au bac, accès, mentions.
  - (Écoles : résultats peu publics au niveau établissement ; on se limite à l'IPS.)
- **Annuaire de l'éducation** (`fr-en-annuaire-education`), géoloc + **code commune** de chaque
  établissement → indispensable pour agréger par commune/département.
- **Croisements territoriaux** (commune/dépt) : **FiLoSoFi** (revenu médian, taux de pauvreté),
  **DVF** (prix immobilier), **BPE** (services). *À vérifier : ressources exactes.*

### Approche analytique
1. **Distinguer deux choses** (méthodo cruciale) :
   - **IPS = composition sociale** (l'« entrée »), pas un résultat.
   - **Valeur ajoutée (IVAL/DNB-VA) = ce que l'établissement *apporte*** au-delà de sa composition.
   - → ne pas confondre « établissement défavorisé » et « établissement qui échoue ».
2. **Le cumul des 3 étapes**, unité = **commune** (si les 3 niveaux existent) sinon **bassin /
   département** (fallback assumé, robuste). Pour chaque territoire :
   - IPS moyen (ou % d'établissements à bas IPS) à chaque niveau ;
   - repérer les territoires **bas / bas / bas** (relégation cumulée) et **haut / haut / haut**
     (entre-soi cumulé).
3. **L'effet d'amplification**, la ségrégation **s'aggrave-t-elle** d'un niveau à l'autre ?
   (hypothèse : le collège est plus ségrégé que l'école, fuite vers le privé, sectorisation ;
   le lycée re-trie par filières). Mesurer l'**écart d'IPS** entre établissements qui se creuse
   le long de la trajectoire.
4. **Le croisement**, superposer la ségrégation scolaire à la ségrégation **résidentielle**
   (revenu/pauvreté FiLoSoFi, prix DVF) : l'école **suit-elle** ou **dépasse-t-elle** la
   ségrégation du territoire ?

### Livrables visés
- **Carte** de la ségrégation scolaire (départements → communes → établissements), avec toggle
  école / collège / lycée (réutilise `ChoroplethMap`).
- **Outil « tape ton établissement / ta commune »** : IPS, résultats, valeur ajoutée, position vs
  département et national.
- **Le « cumul »** : classement des territoires triple-peine / triple-avantage.

### Pièges à afficher
- IPS ≠ résultat ≠ valeur ajoutée (toujours préciser ce qu'on montre).
- Secteur **privé** : composition très différente, fausse les moyennes communales si non distingué.
- Petits effectifs ruraux ; années scolaires comparables ; établissements fermés/fusionnés.

### État (2026-06-27), terrain construit (v1, par département)
- Page `/terrains/ecole` en ligne : carte (toggle école/collège/lycée + **valeur ajoutée IVAL**) +
  classement du cumul (triple-bas / triple-haut). Données : `public/data/showcases/ecole-ips.json`
  (101 dépts, IPS 3 niveaux + va_lycee). Le fichier IPS porte déjà commune/dépt/secteur/GPS → pas
  besoin de l'annuaire.
- **Résultats** : triple-bas = Outre-mer + 93 + croissant Nord/Est ; triple-haut = 78/92/75 +
  arc alpin/Ouest. **IVAL** : sur 22 dépts en relégation, seuls 6 « compensent » (VA>0) ;
  Seine-St-Denis +5,4 (compense), Ardennes −7,3 (double peine). IVAL = l'angle qui distingue
  « territoire défavorisé » d'« école qui sous-performe ».

### Reste à faire sur l'École
Descendre à la **commune/établissement** (outil « tape ton établissement »), ajouter le **privé**
(vue public/privé), croiser avec **FiLoSoFi/DVF** (ségrégation scolaire vs résidentielle).

---

## 6. Nouvelles pistes (maj 2026-07-03)

Propositions arbitrées avec S. Trois tests toujours valables (donnée sous-exploitée / angle tranché /
livrable réutilisable). On développe, on ne se disperse pas.

### A. « Qui représente qui ? » : l'Assemblée (puis gouvernement / Sénat ?)

- **Idée reçue** : « les députés ressemblent aux Français » ; « tel parti est le parti du peuple ».
- **Mesure** : pour chaque député, âge, sexe, diversité du nom (moteur IDP) **et PCS / profession**,
  agrégés **par groupe politique / parti**, comparés à la population (Insee). Le cœur du sujet =
  **le croisement par parti** : qui surreprésente les cadres, qui les retraités, où sont les ouvriers
  (quasi absents partout ?), la diversité selon le bord.
- **Données** : open data Assemblée nationale (acteurs / organes / mandats : date de naissance, sexe,
  **profession** déclarée, groupe). La profession se recode vers une PCS (table de correspondance ;
  champ semi-libre à nettoyer, piège à afficher).
- **Réutilise** : moteur onomastique + patron du dossier Élus (funnel / part parmi). Nouveau :
  agrégation par parti + recodage PCS.
- **Pièges** : profession déclarée n'égale pas PCS Insee stricte ; petits effectifs par petit groupe ;
  profession figée au moment du mandat.
- **Extensions** : gouvernement, Sénat, exécutifs locaux, dans le temps.
- **VALIDÉ (2026-07-04) : la donnée est meilleure que prévu, feu vert.**
  `python/tools/validate_assemblee.py` (open data AN, AMO10 17e législature, cache local) :
  **577 députés, 100 % de couverture** sur nom (pour l'IDP), sexe, date de naissance, profession
  déclarée et groupe politique actif, et **99 % sur la catégorie INSEE** : l'AN fournit
  `socProcINSEE.catSocPro/famSocPro` directement, **le recodage PCS redouté n'est plus un piège**
  (reste : 2 libellés à normaliser, 40 « sans profession déclarée » à traiter honnêtement, et la
  profession est figée au moment du mandat). Groupes propres (RN 122, EPR 91, LFI-NFP 71, SOC 68,
  DR 48, ECOS 38, DEM 37, HOR 35, LIOT 23, UDDPLR 17, GDR 17, NI 10). Premiers chiffres :
  **66 % de cadres et professions intellectuelles supérieures** (383/577), **6 ouvriers** (1 %),
  32 employés, 15 agriculteurs, femmes 38 %, âge moyen 52 ans. Prochaine étape :
  `build_assemblee.py` (IDP sur les noms + agrégats par groupe + références population INSEE)
  puis le terrain (patron Élus).
- **PIPELINE LIVRÉ (2026-07-04)** : `python/tools/build_assemblee.py` →
  `showcases/assemblee.json`. Par groupe (ordre hémicycle, couleurs) : n, femmes, âge, IDP
  (référentiel surnames.tsv, même normalisation que le moteur), PCS famille INSEE, et le
  **portrait des 2 060 collaborateurs parlementaires** (idée S. : listés par l'AN avec civilité
  et nom → parité et IDP mesurables ; carrières/conditions de travail NON mesurables, dit dans
  les notes). Références vérifiées et sourcées : PCS actifs occupés enquête Emploi 2023
  (cadres 22,4 %, ouvriers 18,6 %), femmes 51,5 % (INSEE 2025), IDP population 7,0 % (TEPP).
  **Résultats saillants** : Assemblée IDP 4,2 % vs **collaborateurs 6,4 %** (quasi population :
  la diversité s'arrête à la porte du mandat) ; collaborateurs 47,7 % de femmes vs députés
  37,8 % ; cadres de 52,9 % (GDR, UDR) à **91,3 % (LIOT)** ; **6 ouvriers** (3 LFI, 3 RN) ;
  IDP par groupe : LFI-NFP 10,8 %, SOC 8,9 %, GDR 7,1 %, EPR 5,3 %, HOR 3,4 %, **0,0 % pour
  RN, DR, DEM, LIOT, NI** ; femmes : EPR 48,4 % vs UDR 17,6 % ; âge : LFI 44,6 ans vs LIOT 59,8.
  Reste : le terrain `/terrains/assemblee` (patron Élus) qui met ça en scène.
- **TERRAIN LIVRÉ & déployé (2026-07-04)** : `pages/terrains/TerrainAssemblee.jsx` sur
  **`/terrains/assemblee`** (patron Élus). Sections : 3 chiffres clés → **« la diversité s'arrête
  à la porte du mandat »** (population → collaborateurs → députés, IDP et femmes, l'accroche) →
  **« le mur des professions »** (PCS Assemblée vs actifs occupés, repère ▲ population) →
  **« groupe par groupe »** (chips femmes / IDP / cadres / âge / ouvriers, barres aux couleurs de
  l'hémicycle, repère population, italique si < 20 noms reconnus) → notes méthodo (limites IDP,
  profession déclarée, collaborateurs = portrait pas histoire) → CTA outil représentativité.
  Nav : entrée Dossiers, terrain sur la home et /terrains (metrics remplies : un 2e terrain
  mesuré, les Thèmes peuvent rouvrir un jour), carte-question home « Les députés ressemblent aux
  Français ? FAUX, 6/577 ouvriers », SEO. **Extensions notées** : gouvernement / Sénat / dans le
  temps ; trajectoire « collaborateur devenu député » possible via l'historique AMO30.

### B. « Où se situe la France ? » : comparateur international (déjà shortlisté, priorité)

- Les **pays deviennent une unité** du moteur générique UnitView (comme milieu-social / sexe / âge) :
  quasi aucun code neuf, un JSON `decoupages/pays.json` + un registre d'indicateurs.
- **Idées reçues à tester** : impôts et dépenses publiques, pauvreté des enfants, décrochage scolaire,
  mobilité sociale, temps de travail, inégalités (Gini). Angle : là où la France est **vraiment**
  atypique, souvent l'inverse du cliché.
- **Données** : Eurostat (API), OCDE (SDMX), Banque mondiale (API). Choisir 6 à 8 indicateurs solides.
- **Pièges** : comparabilité des définitions entre pays ; années de référence ; ne pas classer
  naïvement (intervalles, pas un palmarès faux-précis).
- **VALIDÉ (2026-07-04) : l'API Eurostat répond, feu vert tuyau.** `python/tools/validate_eurostat.py`
  (stdlib, décode le JSON-stat 2.0, n'écrit rien) récupère en direct 2 indicateurs témoins, 2024 :
  décrochage scolaire `edat_lfse_14` (34 pays, France 17e à 7,9 %, Allemagne 13,5 % : première idée
  reçue qui tombe) et Gini `ilc_di12` (32 pays, France 18e à 30,0). Leçons pour le pipeline : figer
  TOUTES les dimensions hors `geo` (le script signale celles qui restent libres), écarter les
  agrégats (EU27_2020, EA21...). Prochaine étape : choisir les 6-8 indicateurs, puis
  `build_international.py` → `decoupages/pays.json` (unité du moteur UnitView).

#### Shortlist proposée (2026-07-04, 10 candidats testés en direct, à trancher par S.)

Valeurs réelles Eurostat 2023-2024, récupérées par `validate_eurostat.py` (le script porte les
10 paramétrages exacts). **8 retenus proposés**, organisés en 4 paires qui se répondent :

| # | Indicateur (dataset) | France | Lecture du rang |
|---|---|---|---|
| 1 | Dépenses publiques, % PIB (`gov_10a_main`) | **56,8 %** | championne d'Europe (30/30) |
| 2 | Enfants menacés de pauvreté/exclusion, AROPE (`ilc_peps01n`) | **26,2 %** | 8 pays seulement font pire (32) |
| 3 | Espérance de vie à la naissance (`demo_mlexpec`) | **82,9 ans** | 11e meilleure sur 38 |
| 4 | Mortalité infantile (`demo_minfind`) | **4,0 ‰** | 12 pays seulement font pire (41) |
| 5 | Décrochage scolaire 18-24 ans (`edat_lfse_14`) | **7,9 %** | milieu (17/34), Allemagne 13,5 % |
| 6 | Gini des revenus (`ilc_di12`) | **30,0** | milieu (18/32), 17 pays plus égalitaires |
| 7 | Emploi des seniors 55-64 ans (`lfsi_emp_a`) | **60,3 %** | sous la médiane (15/34) |
| 8 | Heures hebdo effectives des temps pleins (`lfsa_ewhun2`) | **40,0 h** | 6e semaine la plus courte sur 34 |

Les paires éditoriales : **1-2** (l'État qui dépense le plus laisse plus d'un enfant sur quatre
menacé de pauvreté ou d'exclusion), **3-4** (espérance de vie au sommet, mortalité infantile
déclassée : le paradoxe sanitaire), **5-6** (l'école ne fabrique pas plus de décrocheurs que les
voisins ; le pays « égalitaire » est moyen), **7-8** (la semaine de temps plein est quasi standard
à 40 h ; c'est l'emploi des seniors, le temps partiel et l'année qui font l'écart, piège de
comparabilité à afficher).

**En réserve** : NEET 15-29 ans (`lfsi_neet_a`, France 12,7 %, 8 pays font pire ; doublonne avec
5 et 7 sur le thème) et coût du logement > 40 % du revenu (`ilc_lvho07a`, France 7,0 %, milieu,
peu tranché). **Phase 2 hors Eurostat (OCDE)** : mobilité sociale, heures travaillées annuelles,
PISA. **Pièges actés** : le champ de pays varie selon le dataset (30 à 41) → fixer un référentiel
commun (UE27 + AELE + Royaume-Uni + candidats notables) pour des rangs comparables ; afficher des
familles de rang (tête / milieu / queue), pas un palmarès faux-précis.

#### LIVRÉ (2026-07-04) : l'unité Pays est en production

Shortlist validée par S., pipeline construit et déployé le jour même :

- **`python/tools/build_international.py`** : les 8 indicateurs via l'API Eurostat →
  `frontend/public/data/decoupages/pays.json`. **Référentiel = UE27 + Islande, Norvège, Suisse
  (30 pays)** : le Royaume-Uni ne publie plus dans Eurostat depuis le Brexit (écarté), les pays
  candidats ont trop de trous. Moyenne **UE27 écrite en `references`** (le repère affiché par le
  moteur), valeurs manquantes en `null` (seule l'Islande manque, sur les 2 jeux ILC). Le script
  échoue fort si la France manque quelque part.
- **Front : zéro code de rendu**, conformément à AJOUTER_UN_DECOUPAGE.md : une entrée `pays` dans
  `config/decoupages.js` (France en première colonne, 8 indicateurs en 4 thèmes-paires, sens
  `neutre` pour dépenses publiques et heures : pas de jugement implicite) + l'entrée SEO
  `/explorer/pays`. En ligne sur **`/explorer/pays`** (tableau) et `/explorer/pays?cat=fr` (fiche
  France : ses extrêmes détectés automatiquement).
- **Repères France vs UE27 au premier chargement** : dépenses 56,8 % vs 48,9 ; pauvreté des
  enfants 26,2 % vs 24,2 ; espérance de vie 82,9 vs 81,2 ; mortalité infantile 4,0 vs 3,3 ;
  décrochage 7,9 vs 9,6 ; Gini 30,0 vs 29,4 ; emploi des seniors 60,3 vs 65,2 ; heures des temps
  pleins 40,0 vs 40,3.
- **Reste à faire** : cartes-questions home tirées des paires (l'État et les enfants ; le paradoxe
  sanitaire) ; familles de rang dans la fiche ; phase 2 OCDE (mobilité sociale, heures annuelles).

#### LIVRÉ (2026-07-04, soir) : le dossier « France en Europe », 3e pilier

Suites de la v1, toutes déployées le jour même :

- **Cartes home** : les 2 cartes internationales (État/enfants « FAUX 1 sur 4 » ; santé « VRAI,
  MAIS 25e/30 ») + visibilité corrigée (menu « Comparer des groupes, des pays », cartes outil).
- **Tableau refondu en mode `tableauClassement`** (retour S. : illisible en 30 colonnes) : pays en
  lignes, indicateurs en colonnes (4 par défaut, chips), présélections **« Voir où la France est :
  forte / moyenne / faible »** calculées sur les rangs réels, tri par colonne (meilleur en tête),
  ligne « Moyenne UE27 » insérée dans le classement, lignes cliquables vers les fiches (les 30
  chips supprimées). Mode générique (config), réutilisable pour toute unité à nombreuses catégories.
- **Page `/international` « Où se situe la France ? »** (analysis-first, pattern /segregation) :
  En bref (3 chiffres calculés au chargement), **carte d'identité européenne** (un dot-plot par
  indicateur : intervalle des 30 pays, point France, repère UE27, rang coloré), les **4 histoires**
  en cartes, le **nuage de pronostic international** (OutsidersScatter réutilisé, patch générique
  `mots` + masquage du filtre population : « que rapporte la dépense publique ? », dépenses × 
  pauvreté/espérance/décrochage...), les **trajectoires France vs UE27 depuis 1995**
  (`fetch_series()` dans build_international.py → `series` dans pays.json). Preuve du décrochage
  sanitaire vérifiée dans la donnée : mortalité infantile meilleure que l'UE jusqu'en 2012,
  croisement vers 2015, 3,5 ‰ (2012) → 4,1 ‰ (2024) pendant que l'UE baisse. Nav : entrée
  Dossiers « France en Europe », CTA des cartes home vers le dossier, explorateur/fiches en bas de page.
- **Reste** : phase 2 OCDE (mobilité sociale, heures annuelles, PISA) ; embed iframe des vues
  internationales pour les journalistes ; og:image dédiée si le dossier prend de l'audience.

### C. « Riches et pauvres vivent-ils séparés ? » : ségrégation résidentielle (nouveau, pas déjà fait)

- **Accroche (validée avec S., 2026-07-03)** : **« Quelles villes font cohabiter riches et pauvres,
  et lesquelles les séparent ? »** C'est l'entrée du sujet : un classement des villes de la plus mixte
  à la plus séparée, chacun pouvant chercher la sienne (« tape ta ville »). Idée reçue à casser : la
  mixité supposée des grandes villes / de certains quartiers.
- **Vérifié dans le code (2026-07-03)** : le site ne mesure la ségrégation résidentielle que **par
  ricochet** (corrélation école↔revenu de 0,58 dans le dossier École). **Aucune mesure directe** de
  l'entre-soi par le revenu. Le sujet est donc libre.
- **Deux niveaux de la question** (à distinguer nettement) :
  1. **Entre communes** d'une même agglomération : les communes riches et les communes pauvres
     sont-elles séparées ? Se fait vite avec le **revenu communal FiLoSoFi déjà en base** (Atlas).
     Répond surtout à « quelles agglomérations sont fracturées ».
  2. **À l'intérieur d'une ville** (quartiers) : une même commune mélange-t-elle les revenus, ou
     juxtapose-t-elle quartiers riches et quartiers pauvres ? C'est **l'angle le plus original et le
     plus fidèle à l'accroche**, mais il exige une maille **infra-communale** : **IRIS** ou surtout les
     **données carroyées FiLoSoFi (carreaux 200 m)**, jeu INSEE riche, granulaire, vivant et
     sous-exploité (coche les trois tests). C'est une **nouvelle brique de données** à construire.
- **Mesure** : indice de **dissimilarité** ou d'**entropie / mixité** du revenu sur les unités
  infra-urbaines d'une ville (IRIS ou carreaux) ; par ville, un score de mixité 0 à 1. Réutilise la
  carto (points / choroplèthe fine) + le patron « classement + tape ta ville ».
- **Angle** : l'entre-soi se mesure ; les villes « mixtes » le sont-elles vraiment, ou côtoient-elles
  sans se mélanger ?
- **Pièges** : MAUP (la maille change le résultat, à afficher), IRIS absent en rural, secret
  statistique FiLoSoFi sur petites mailles, carreaux lourds à manipuler (agréger côté Python).

#### Méthode retenue (données vérifiées 2026-07-03)

- **Jeu de données** : **FiLoSoFi 2019, carreaux 200 m** (INSEE, `insee.fr/fr/statistiques/7655475`,
  aussi sur data.gouv). 34 variables PAR carreau, dont **revenu** `ind_snv` (somme des niveaux de vie),
  **effectifs** `ind` / `men`, et **structure d'âge** `ind_0_3, ind_4_5, ind_6_10, ind_11_17,
  ind_18_24, ind_25_39, ind_40_54, ind_55_64, ind_65_79, ind_80p`. Un seul fichier couvre revenu ET âge.
  Carreaux à < 11 ménages imputés (drapeau `i_est_200`), à garder mais signaler. Le fichier national est
  lourd (dizaines/centaines de Mo) : agrégation en Python. Pas de code commune natif → **jointure
  spatiale** carreau→commune (réutilise les contours communes déjà en projet).
- **Unité « ville »** : la **commune** (recherche « tape ta ville ») ; extension possible unité urbaine.
- **Score de ségrégation par le revenu (indicateurs pluriels)**, en classant chaque carreau par niveau
  de vie moyen `ind_snv / ind` :
  1. **Dissimilarité (Duncan)** quintile bas vs quintile haut (seuils nationaux) : 0 = mélangé, 1 = séparé. **Score phare.**
  2. **Isolement** des bas revenus (entre-soi des pauvres).
  3. **Écart quartier riche / quartier pauvre** : ratio P90/P10 des niveaux de vie moyens des carreaux de la ville (très lisible).
  4. (option) **Theil / entropie**.
- **Score de ségrégation par l'âge** (mêmes carreaux), groupes **jeunes 0-17 / actifs 18-64 /
  seniors 65+** : dissimilarité jeunes↔seniors, entropie des 3 groupes, isolement des seniors.
  Question : la ville mélange-t-elle les âges, ou juxtapose-t-elle quartiers « familles » et quartiers « âgés » (villes étudiantes, littoral retraité, périurbain familial) ?
- **Livrables** : (1) **classement des villes** (seuil de population, ex. > 10 000 hab pour la
  robustesse) de la plus mixte à la plus séparée, pour revenu ET âge ; (2) **fiche « tape ta ville »**
  avec les scores + sous-indices + **mini-carte des carreaux** colorés par niveau de vie (la preuve
  visuelle du damier) ; (3) accroche : les grandes villes « mixtes » ne le sont pas forcément.
- **Pipeline** : `python/tools/build_segregation.py` → `frontend/public/data/segregation/`
  (`villes.json` classement + `<code>.json` par ville). **Validation d'abord sur 2-3 villes témoins**
  (une supposée mixte, une supposée séparée) avant le run national.

#### Accès aux données : API Koumoul (validé 2026-07-03, simplifie tout)

La réexposition **Koumoul** du jeu (`opendata.koumoul.com/data-fair/api/v1/datasets/filosofi-carreaux-200m/lines`)
porte, par carreau, **`lcog_geo` = le code commune** (+ `_geopoint`, `ind_snv_avg` déjà calculé).
Conséquence : **pas de jointure spatiale ni de téléchargement national** pour la validation, on filtre
par commune via `qs=lcog_geo:"<code>"` (paginer avec `next`, `size` plafonné à 10000). **Cas PLM** :
Paris/Lyon/Marseille portent le code d'**arrondissement** (751xx / 6938x / 132xx), pas le code commune,
donc requêter `lcog_geo:(... OR ...)`. **Revenu fiable = carreaux non imputés** (`i_est_200=false`) : les
imputés (< 11 ménages) ont un `ind_snv_avg` lissé qui sous-estimerait la ségrégation.

#### Validation preuve de concept (2026-07-03, données réelles via API)

Indices calculés en direct (revenu pondéré par population sur carreaux non imputés ; D âge = dissimilarité
jeunes 0-17 vs seniors 65+ sur tous les carreaux) :

| Ville | carreaux | pop | P90/P10 revenu | Gini spatial | D âge |
|---|---|---|---|---|---|
| Neuilly-sur-Seine | 65 | 42 k | 1,37 | 0,062 | 0,11 |
| Grenoble | 318 | 129 k | 1,68 | 0,103 | 0,22 |
| Rennes | 769 | 180 k | 1,96 | 0,130 | 0,26 |
| Paris | 1 575 | 1,64 M | 2,14 | 0,154 | 0,14 |
| Marseille | 2 692 | 638 k | 2,20 | 0,157 | 0,24 |

Lecture : Marseille la plus fracturée par le revenu (clivage nord/sud), Neuilly la moins (uniformément
riche = la nuance « mixité interne ≠ diversité sociale »), Rennes la plus triée par l'âge (ville
étudiante). La méthode discrimine et reproduit la sociologie connue sans hard-code. **Feu vert méthode.**

#### Règle non négociable : COMPRÉHENSIBLE (demande S., 2026-07-03)

Un « indice de dissimilarité de 0,157 » ne parle à personne. Le livrable public traduit toujours en
langage clair ; le jargon reste dans une note méthodo repliable. Traductions retenues :

- **Score de mixité 0-100** par dimension (revenu, âge), 100 = quartiers parfaitement mélangés,
  0 = totalement séparés, + **label verbal** (ex. Très mixte / Plutôt mixte / Contrastée / Très séparée).
- **Rang national auto-calibré** : « {ville} est plus séparée que 92 % des villes » (percentile issu du
  run national, se calibre tout seul, très lisible). C'est la sortie compréhensible qui vient APRÈS le
  run national.
- **Phrase concrète** à partir du P90/P10 : « le quartier le plus aisé y gagne 2,2× plus que le plus
  modeste ». Pour l'âge : « les âges s'y mélangent » vs « quartiers jeunes et quartiers âgés séparés ».
- **La mini-carte des carreaux** colorés par niveau de vie = la preuve visuelle immédiate, plus parlante
  que tout chiffre.
- Les indices techniques (Gini, dissimilarité, Theil) restent calculés et cités, mais **en second plan**.

#### LIVRÉ EN PRODUCTION (2026-07-04) : ce qui remplace la méthode ci-dessus

La méthode finale a évolué pendant la construction (les sections « Méthode retenue » et « Validation »
ci-dessus décrivent des étapes intermédiaires). État réellement en ligne sur **`/segregation`** :

- **Mesure du revenu = dissimilarité de Duncan pauvres / non-pauvres** par carreau (via `men_pauv`/`men`,
  et non plus le Gini des revenus moyens) : elle capte la mixité INTRA-quartier, que la moyenne masquait.
  Le Gini/P90-P10 restent affichés en second plan.
- **Typologie honnête à 2 axes** (diversité × séparation), pas un score « mixité » ambigu :
  **Fracturée / Mixte / Contrastée / Uniformément aisée / Uniformément modeste** (seuils : pauvreté
  < 11 % = aisée, > 35 % = modeste ; sinon dissimilarité percentile 33/66). Distingue enfin une ville
  uniformément modeste (La Courneuve) d'une uniformément aisée (Neuilly), toutes deux peu « fracturées ».
- **Composition des quartiers** (demande S.) : part des habitants en quartiers **mixtes** (10-40 % de
  pauvres) / **homogènes aisés** (< 10 %) / **homogènes pauvres** (≥ 40 %). Très concret (barre empilée).
- **FINDING contre-intuitif** : la catégorie **Mixte** est dominée par les GRANDES villes (Paris, Lyon,
  Toulouse), à l'échelle du carreau de 200 m, pauvres et non-pauvres s'y entremêlent plus que dans bien
  des petites villes proprement zonées (cité d'un côté, pavillons de l'autre). Biais de taille vérifié
  FAIBLE (corr pop↔séparation r = -0,12).
- **Caveats affichés dans la méthodo** : « non-pauvres » ≠ « riches » (en ville populaire = ménages
  modestes) ; mesure à l'échelle 200 m ; légère sensibilité à la taille des petites villes.
- **Livré** : `python/tools/build_segregation.py` (stdlib, cache, PLM géré) → 997 villes ;
  page `pages/segregation/Segregation.jsx` + `components/charts/CarreauxMap.jsx` ; nav Dossiers « Villes » ;
  carte-question home (verdict « Pas partout », aligné sur la donnée) ; og:image + GoatCounter couvrent la route.
- **Reste v2** : indice débiaisé de la taille (petit échantillon), vrai axe riches-vs-pauvres (pas
  seulement pauvres/non-pauvres), maille « unité urbaine », calibrage fin des seuils.

#### ÉTAT FINAL déployé (2026-07-04) : ce qui supersède tout ce qui précède

Après plusieurs itérations avec S., la version en ligne sur **`/segregation`** est un **modèle à 3 axes
+ lecture territoriale + explorateur**, avec la règle « toujours un chiffre concret » :

- **Revenu, 3 axes** (la dissimilarité pauvres/non-pauvres du 2-axes est abandonnée, elle confondait
  « pauvre » et « non-riche ») :
  1. **Niveau de vie** (médiane, le CADRE : évite de prendre Neuilly, aux quartiers internement très
     inégaux mais riches, pour de la « mixité »).
  2. **Mélange DANS un quartier** = rapport interdécile D9/D1 des IRIS (FiLoSoFi 2021, CSV téléchargé/caché) :
     les 10 % aisés d'un quartier gagnent ×N les 10 % modestes. National ~×3,1 ; grandes villes ×3,8 vs
     petites ×3,0 (les grandes mélangent plus). Corrige l'angle mort de `men_pauv` (Neuilly interdécile 7,6).
  3. **Écart ENTRE quartiers** = CV des médianes IRIS (séparation) ; affiché en × P90/P10 concret.
  Typologie courte Fracturée/Mélangée/Contrastée/Homogène + phrase auto cadrée par le niveau.
- **Fiche ville** : jauges avec le **× réel en gros** (interdécile / P90-P10), plus le « rang » abstrait ;
  composition des quartiers (mixtes / homogènes aisés / homogènes pauvres) ; carte des carreaux ; âge ;
  bloc « Et l'école ? » → dossier École.
- **Lecture territoriale (unité = territoire, pas que communes)** : `departements.json` agrège **tous les
  IRIS par département** (couverture complète, `build_departements()`, noms via territoires-index.json) ;
  section « Où, en France, riches et pauvres se séparent le plus ? » avec **bascule Régions / Départements**
  (régions = départements pondérés par nb d'IRIS). Géographie crédible : Île-de-France 91, PACA, Grand Est,
  Hauts-de-France en tête ; Bretagne / Pays de la Loire au fond. Caveat frontalier affiché (Pays de Gex, Bâle).
- **Explorateur (nuage outsiders)** `components/charts/MixiteScatter.jsx` : **axes configurables par chips**
  (Y : mélange interne / écart entre quartiers ; X : population / niveau de vie / écart entre quartiers),
  **filtre par territoire** (France / région / département, recalcule la droite de pronostic),
  **recherche d'une ville** (la repère par un point noir + ses valeurs). Tous les axes en valeurs concrètes.
- **Page analysis-first** : accroche → **En bref** (3 stats : 34 % fracturées, ×1,6 entre quartiers, ×3,8 vs
  ×3,0 dans un quartier) → territorial → explorateur → classement des villes → **recherche reléguée en bas**.
  Home : carte thème « Niveau de vie » / unité « Villes », CTA « Voir l'analyse nationale ».
- **Fichiers** : `build_segregation.py` émet `villes.json` + `<code>.json` + `colleges-evitement.json`
  + `departements.json` ; modes `ecole` (évitement établissement) et `terr` (agrégat départemental).
- **TODO notés** : **colorer les points du nuage par région** (quand vue France) ; 4ᵉ axe (ex. taux de
  pauvreté) ; débiaiser le frontalier ; drill cliquable région→département→villes.

### F. École × ségrégation résidentielle : les lieux d'évitement scolaire (idée S., 2026-07-04)

Croiser la **ségrégation résidentielle** (nouveau jeu) avec l'**IPS des écoles** (dossier École) pour
repérer où l'**école trie plus que le logement** = proxy d'évitement scolaire / carte scolaire concentrante.
Trois indicateurs faisables avec l'existant : (1) **écart public/privé** d'IPS vs profil du quartier (le plus
direct, fuite vers le privé ; on a déjà SSD public 88 / privé 122) ; (2) **nuage ségrégation scolaire (écart
d'IPS entre écoles publiques) vs ségrégation résidentielle** par ville → outliers au-dessus = suspects
(logique « écart au pronostic » de l'Atlas) ; (3) **écart école↔quartier** par établissement (IPS très sous
le revenu du secteur = favorisés partis). **Limite forte** : on repère l'anomalie, on ne PROUVE pas le
mécanisme (privé / dérogation / sectorisation) sans la carte scolaire (non disponible) ; le split
public/privé aide à attribuer. Autres réserves : IPS = composition sociale (pas revenu, mais corrélé) ;
secteur réel ≠ IRIS (rapprochement approximatif). Prolonge le dossier École (corr école↔revenu 0,58 déjà là).
**LIVRÉ & déployé (2026-07-04)** : `build_segregation.py` calcule par ville, à partir de
`etablissements.tsv` (collèges pu/pr), la dispersion d'IPS des collèges + l'écart public/privé, son
percentile national et l'**écart école − logement** (+ = école plus triée). Affiché dans le **dossier
École** (`/terrains/ecole`, section « Où l'école trie plus que le quartier ? », lit `villes.json`,
liens croisés vers /segregation) ; la fiche ségrégation a un pont « Et l'école ? » → dossier École.
Résultats crédibles (Carvin école 77e vs logement 8e, Villiers-le-Bel IPS pub 70/privé 114 ;
Paris/Neuilly négatifs). **Décision IA (2026-07-04)** : pour éviter le doublon, l'évitement vit dans le
dossier École (hub scolaire = public/privé + évitement), PAS de carte-question home dédiée ; la carte
« L'argent fait la réussite » reclassée kicker « Reproduction sociale » ; les pages ségrégation/école
mènent par l'analyse nationale, recherche de ville en secondaire.

**Niveau ÉTABLISSEMENT ajouté (2026-07-04, idée S.)** : `build_colleges_evitement()` compare chaque
**collège public** à son quartier immédiat (revenu moyen des carreaux 200 m à moins de 700 m) → résidu =
rang national d'IPS − rang national du revenu local (**débiaisé par les rangs** pour tuer l'effet plafond
de l'IPS ; la version linéaire mettait à tort Paris 16e en tête). `colleges-evitement.json` = top 20
**décrochés** (IPS bien sous leur quartier = évitement, ex. Paris 18e gentrifié) + top 20 **attractifs**
(publics sélectifs/internationaux au-dessus de leur quartier, ex. Marseille Cité internationale +86).
Affiché dans le dossier École (section « Les collèges décrochés, et attractifs, de leur quartier »).
**Réserve** : revenu ≠ IPS (zones frontalières surestimées) ; secteur réel > 700 m. Complémentaire du
niveau ville (public/privé = fuite vers le privé ; établissement = décrochage local, gentrification).

### D. Frontière Coulmont (à respecter)

Baptiste Coulmont couvre déjà, en référence, le **prénom individuel** relié à l'âge, à la classe
sociale (mention au bac) et au vote. **Ne pas refaire** un outil « ton prénom dit ton âge / ta classe ».
Notre terrain distinctif est la **représentativité collective** (une liste, un parti, une institution :
« qui représente qui »), pas le prénom d'un individu. La ligne « Sociologie des prénoms » de la
shortlist (section 4) est donc **reléguée et reframée** dans ce sens.

### E. Veille des données ouvertes

Idée transverse de S. : surveiller (automatiquement ?) les jeux de données ouvertes FR et
internationaux, et peut-être publier cette veille. Détail et avis franc dans
**`docs/veille-open-data.md`**. En bref : utile **surtout comme moteur à idées d'études** (interne),
et publiquement seulement **si curé** (la curation, pas l'automatisation brute, fait la valeur).

### G. Sélectivité : quelles disciplines et quels territoires sélectionnent le plus ? (idée S., 2026-07-04)

**Parcoursup** (data.gouv, vœux + taux d'accès par formation) et **MonMaster** (candidatures/admissions
en master). **Angle** : quelles disciplines/formations sélectionnent le plus (taux d'accès, candidats par
place) ? Et surtout, **quels territoires sont les plus / les moins sélectifs par discipline** (accès
inégal selon où on habite : à filière égale, entre-t-on plus facilement dans telle académie ?).
**Livrable** : classement/carte de la sélectivité par discipline × territoire (académie/département),
« tape ta filière / ton académie ». **Unité** : formation, discipline, territoire. Cohérent avec l'axe
inégalités d'accès. Réserve : sélectivité ≠ qualité ; attention aux effectifs par formation×territoire.

**Enrichissement (2026-07-04, pont socio-analyse, voir section K)** : Parcoursup publie le **taux de
boursiers par formation**. Croiser **type de pédagogie × ouverture sociale** : les formations qui se
présentent comme « à projet / autonomie / interdisciplinaires » sont-elles les plus fermées socialement ?
Hypothèse issue du projet socio-analyse (« le dispositif innovant comme épreuve déguisée » : les
pédagogies libératrices sélectionnent les étudiants déjà dotés du soi exploratoire). Angle plus tranché
que la seule sélectivité territoriale ; opérationnalisation : typologie de formations (CPGE, BUT,
université, écoles « à projet ») × taux d'accès × part de boursiers admis.

**VALIDÉ (2026-07-04) : les trois angles tiennent, feu vert.** `python/tools/validate_parcoursup.py`
(jeu `fr-esr-parcoursup` MESR, session 2025, 14 252 formations, une ligne par formation, taux d'accès
officiel `taux_acces_ens` renseigné à 100 %, cache local ~20 Mo) :

1. **Disciplines** : hiérarchie contre-intuitive. Le plus sélectif de France n'est pas la CPGE (43 %
   de taux d'accès médian) mais **BPJEPS sport 4 %**, **Sciences Po 10 %**, **DN MADE arts/design
   23 %** ; **PASS 34 %** et **IFSI 40 %** (46,9 vœux par place, plus demandé que la CPGE) devant la
   prépa scientifique (41 %). Licence non sélective : 86 %.
2. **Territoires, à filière égale** : écarts massifs. BTS : Paris 27 % vs Limoges 76 % (50 pts) ;
   Licence : Créteil 43 % vs Poitiers 100 % ; BUT : Créteil 19 % vs Nancy-Metz 68 %. **Créteil est
   l'académie la plus dure partout** : à vœu égal, l'accès dépend de où l'on habite.
3. **Boursiers** : gradient social parfait par filière : École de commerce 5,2 % d'admis boursiers,
   École d'ingénieur 7,3 %, **CPGE 10,4 %** ... **BTS 29,4 %**. Le croisement sélectivité × boursiers
   INTRA-filière est plus subtil : dans les BTS/BUT/IFSI, le tiers le plus sélectif a PLUS de
   boursiers (géographie urbaine : les formations tendues sont là où vivent les boursiers, Créteil),
   alors qu'en CPGE c'est l'inverse (9,2 % dans le tiers le plus sélectif vs 12,4 %) : au sommet, la
   sélectivité se referme socialement. À afficher tel quel, c'est la nuance qui rend le sujet honnête.

Pièges notés : le taux d'accès mesure la position de recevoir une proposition (pas le niveau exigé) ;
sessions par millésime (2025 seul dans ce jeu, les années passées sont des jeux séparés) ; petites
formations bruyantes (seuils d'effectifs) ; « boursiers » = néo-bacheliers boursiers du secondaire.

**LIVRÉ & déployé (2026-07-04) : dossier autonome `/terrains/selectivite`** (décision S. : autonome,
pas une extension du dossier École, mais pont vers lui en bas de page). Pipeline
`python/tools/build_parcoursup.py` → `showcases/selectivite.json` (réutilise le cache CSV de la
validation) ; page `TerrainSelectivite.jsx` : 3 chiffres clés → classement des filières (agrégées +
15 détaillées les plus fermées) → **« la licence est-elle encore ouverte à tous ? » (demande S. en
cours de route)** : seules **33 % des licences acceptent tous leurs candidats** (27 % en refusent plus
de la moitié), par région de 20 % (Île-de-France, licence médiane à 49 % d'accès) à 100 %
(Guadeloupe) → **matrice académie × filière** (31 académies × 5 filières, couleur par colonne,
cellules ≥ 10 formations, moyenne ≥ 2 filières pour éviter l'artefact Mayotte ; Paris 29 %,
Créteil 34 %, Versailles 35 % en tête des plus dures) → boursiers (gradient par filière + croisement
intra-filière avec la nuance CPGE) → notes méthodo → pont dossier École. Nav : menu Dossiers,
terrain home + /terrains, carte-question home « La prépa, formation la plus sélective ? FAUX, 4 % »,
SEO. **Extensions notées** : sessions passées (jeux séparés) pour l'évolution ; MonMaster (même
angle au niveau master) ; carte GPS des formations (coordonnées dans le jeu).

**ÉVOLUTION + 3 MESURES LIVRÉES (2026-07-06, demandes S.)** :

- **Trois lectures de la porte d'entrée** (sélecteur sur le classement des filières), suite à la
  question de S. sur la définition : (1) **taux d'accès officiel** `taux_acces_ens` = part des
  candidats en position de recevoir une proposition, d'après le rang du dernier appelé (ce n'est
  ni propositions/candidatures ni acceptations/candidatures) ; (2) **pression** = vœux par place ;
  (3) **taux d'acceptation** = acceptations/candidatures, ajouté au pipeline, à lire comme une
  CONVERSION qui mélange sélectivité et attractivité (un candidat n'accepte qu'un seul vœu).
  Note méthodo ajoutée (demande S.) : toutes ces mesures reposent sur les candidatures exprimées,
  **l'auto-censure est invisible** ; une filière qui « s'ouvre » peut perdre en attractivité comme
  gagner en auto-censure.
- **Évolution 2022 → 2025** (le taux d'accès officiel n'existe que depuis 2022 ; garder UNE
  métrique plutôt que d'allonger la série en en changeant) : bloc `evolution` dans le pipeline
  (4 sessions en cache, filières communes aux 4 sessions seulement), section « Qui se ferme, qui
  s'ouvre ? » (classement des deltas cliquable + courbe par filière). **Résultats** : la **CPGE se
  ferme de 30 points** (73 % → 43 %), LAS -18, **Licence -9** (95 % → 86 %), BUT -6, BTS et écoles
  d'ingénieurs -4 ; s'ouvrent : **EFTS +5, IFSI +4** (attractivité en berne ou auto-censure), PASS +1.
  Nuance licence intégrée à sa section : la fermeture vient du milieu (médiane 95 → 86) alors que
  la part de licences totalement ouvertes remonte légèrement (28 % → 33 %).
- **SÉRIE LONGUE 2018 → 2025 (2026-07-06, décision S.)** : le taux d'accès officiel ne peut pas
  être recalculé avant 2022 (rang du dernier appelé non publié) → **pas de pseudo-taux : la série
  longue porte les deux autres indicateurs** (pression = vœux/place, taux d'acceptation), le taux
  officiel s'affichant là où il existe. 8 sessions en cache, `DUT→BUT` aliasé, **PACES exclue**
  (réforme santé non comparable), notes : session 2020 covid, « Autres formations » change de
  composition, auto-censure invisible. **UI (retour S.)** : UN état de mesure partagé pilote le
  classement ET l'évolution (chips synchronisées aux deux endroits) ; matrice et licence restent
  volontairement en taux d'accès. **Résultats de la série longue (pression)** : CPGE 15,1 → 27,8
  vœux/place depuis 2018 (presque doublée), **Licence 5,9 → 10,7** (doublée aussi), PASS 17,8 →
  41,8 depuis 2020, commerce 9,2 → 17,0 ; se détendent : IFSI 60,9 → 46,9 (mais toujours la plus
  forte pression), EFTS 8,8 → 6,2. Acceptation licence : 15 % → 10 %.

### H. Usages audiovisuels (ARCOM) : musique, IPTV illicite, tendances audio-vidéo (idée S., 2026-07-04)

Prolonge l'enquête ARCOM « Les Français et l'information » (déjà utilisée pour le découpage Âge). Jeux :
**consommation illicite d'IPTV 2024** (`data.gouv.fr/datasets/consommation-illicite-de-contenus-audiovisuels-en-iptv-2024`)
et **baromètre tendances audio-vidéo** (`data.gouv.fr/datasets/tendances-audio-video-barometre`).
**Angles** : qui pirate (IPTV illicite), qui écoute quoi et comment (streaming vs TV vs radio), tendances.
**Livrable** : peut alimenter le découpage **Âge** (nouveaux indicateurs) ou un thème « médias / audiovisuel ».
Réserve : enquêtes déclaratives ; vérifier la granularité (national vs par profil).

### I. « Le niveau baisse-t-il ? » avec des données historiques (idée S., 2026-07-04)

Question classique et sur-étudiée, donc l'intérêt est d'**aller plus loin par la désagrégation** : le
niveau baisse-t-il vraiment, et si oui **sur quelles disciplines** (maths ? français ?), **quel territoire**,
**garçons ou filles**, **quel milieu social** ? Données : historiques DEPP / évaluations nationales /
résultats brevet-bac dans le temps / séries type « dictée » ou tests standardisés / PISA (international).
**Angle tranché** : la moyenne cache des dynamiques opposées selon discipline/sexe/milieu. **Livrable** :
analyse longitudinale avec ces croisements. Réserve : comparabilité des épreuves dans le temps (réformes),
effet de composition ; ne pas surinterpréter. Croise l'axe international (B) et Reproduction sociale.

### J. Atlas : croisements éditorialisés, le « mode destinations » (proposition IA validée, 2026-07-04)

**Diagnostic.** L'Atlas propose 20 indicateurs librement croisables deux à deux = **190 paires
possibles**, dont l'immense majorité est triviale (deux mesures du même monde social) ou fallacieuse.
Demander à l'utilisateur de choisir la paire, c'est lui transférer le travail éditorial que le site fait
partout ailleurs. Incohérence avec la leçon de /segregation (analysis-first, recherche reléguée en bas,
règle COMPRÉHENSIBLE) : l'Atlas est resté « outil d'abord », c'est lui l'anomalie.

**Principe (analogie du comparateur de vols en mode « Explore / Partout »)** : ne pas demander une
destination, montrer **ce qui vaut le voyage parmi ce qui est disponible**. Concrètement :

- **6 à 10 croisements curés**, présentés en **cartes-questions** (le format validé de la home) : une
  question (« Là où il y a des HLM, les revenus sont-ils plus bas ? »), un verdict, un chiffre concret,
  et un clic qui ouvre le nuage **pré-configuré** (droite de pronostic + 2-3 outsiders déjà annotés).
- **Deux familles de cartes** : les corrélations **fortes non triviales** (groupes différents, sources
  différentes) et surtout les corrélations **attendues mais absentes** (l'idée reçue qui tombe, la
  signature Outsiders). Troisième famille possible : les **paradoxes d'agrégation** (le r s'inverse
  entre départements et communes), très forts mais à n'utiliser qu'avec une explication solide.
- **Le croisement libre ne disparaît pas, il descend** : le sélecteur complet devient le « mode
  explorateur » en bas de page (même geste que la recherche de ville sur /segregation).
- Même logique pour l'entrée de l'Atlas : 4-5 questions d'appel d'abord, les 20 variables en second niveau.

**Pipeline** (curation assistée, sélection humaine) :

1. `python/tools/build_croisements.py` **(livré 2026-07-04)** : balaye les 190 paires aux deux mailles
   (101 départements ; ~36 400 communes). Par paire : Pearson départements, Pearson communes pondéré
   population, Spearman (robustesse), signaux (même groupe, inversion de signe entre mailles, écart de
   mailles, divergence Pearson/Spearman), gisement d'outsiders (part de communes à |z| > 2,5 du pronostic
   OLS + les plus gros écarts nommés, pop ≥ 2 000, arrondissements PLM gérés). Le registre d'indicateurs
   est **lu directement dans `frontend/src/config/indicateurs.js`** (zéro duplication, zéro dérive).
   Sorties : `docs/croisements/rapport.md` (rapport de curation en 6 sections) + `candidats.json`.
2. **Curation humaine** dans le rapport : choisir les cartes, écrire questions et verdicts.
3. **Phase 2 (à faire)** : `frontend/src/config/croisements.js` (la sélection curée : paire, question,
   verdict, outliers annotés) + composant cartes-questions sur la page Atlas ; reléguer le sélecteur
   libre en bas.

**Premiers résultats du balayage (2026-07-04)** : 31 corrélations fortes inter-groupes (IPS écoles ×
revenu +0,87 en communes pondéré ; prix immobilier × cadres +0,79) ; 60 quasi nulles inter-groupes où
chercher l'idée reçue (ex. valeur ajoutée des lycées : corrélée à RIEN, ni revenu ni prix ni PCS, un
message en soi : « le bon lycée n'est pas là où on croit ») ; 16 inversions de signe, les plus nettes
autour du revenu, dont
**revenu × HLM** (+0,41 entre départements, -0,34 entre communes : les départements riches ont plus de
HLM parce qu'urbains, mais dans un département les communes HLM sont les plus modestes) et
**revenu × propriétaires** (-0,41 dépts, +0,24 communes). Outsiders crédibles (stations de ski sur
revenu × résidences secondaires ; Sarcelles/Clichy-sous-Bois sur IPS × diversité des candidats ;
Neuilly/Levallois sur IPS lycées × prix).

**Pièges à afficher sur chaque carte publiée** : corrélation territoriale ≠ corrélation individuelle
(sophisme écologique) ; pronostic ≠ causalité (le vocabulaire « pronostic / écart au pronostic » est
bien choisi précisément parce qu'il ne dit pas « cause ») ; le r dépend de la maille (MAUP) ; les paires
même-groupe sont presque toujours triviales (pénalisées x0,4 dans le score du script).

#### DÉCISION & LIVRÉ (2026-07-04, demande S.) : sélection AUTOMATIQUE, ceci supersède la curation manuelle

« Trop de choses pour que je puisse choisir » : la curation manuelle des 6-10 croisements est
abandonnée. On prend **tous les croisements significatifs et non tautologiques**, on montre pour
chacun les territoires **largement au-dessus** du pronostic et ceux **très en dessous**, et **on
adapte petit à petit**. Implémentation en ligne :

- **Tautologie objectivée par des dimensions latentes** (7) : école / perf-école (va_lycee) /
  richesse / politique / PCS / logement / démographie, dérivées du groupe du registre
  (`GROUPE_TO_DIM` + exceptions dans `build_croisements.py`). Deux indicateurs de la même
  dimension = même phénomène mesuré deux fois = pas de carte.
- **Critères de retenue** : |r communes pondéré| ≥ 0,3, Spearman de même signe (robustesse),
  dimensions différentes ; puis **une carte par paire de dimensions** (la plus forte, les autres
  en variantes) → **12 cartes** au run du 2026-07-04, de IPS écoles × revenu (+0,87) à
  diplômés × 65 ans et plus (-0,30). Navigable sans choisir.
- **Orientation** : Y = la dimension la plus « résultat » (perf-école > école > politique >
  richesse > PCS > logement > démographie), X = la plus structurelle. Les listes « au-dessus /
  en dessous du pronostic » sont **neutres** : qui « confirme le stéréotype », c'est la masse SUR
  la droite ; les deux côtés sont des parcours différents (au-dessus = mieux que prévu, en
  dessous = moins bien, quand Y est désirable). Le jugement se met dans les textes, pas dans la structure.
- **Outliers nationaux précalculés** côté Python (top 8 par côté, pop ≥ 2 000, |z| ≥ 2,5, PLM
  nommés) : le front ne peut PAS les calculer, il ne charge les communes que département par
  département. Sortie front : `frontend/public/data/atlas/croisements.json`.
- **Le levier « petit à petit » : `docs/croisements/overrides.json`** : par id de carte,
  surcharger `question` / `lecture` / `note` ou `masquer: true`, puis relancer le script. Aucun
  code à toucher. `note` = mise en garde affichée sur la carte (encadré ambre). **Décision S.
  (2026-07-04) : le biais frontalier s'EXPLIQUE, on ne masque pas** ; première note posée sur
  IPS × revenu (les « en dessous » sont frontaliers de Genève : revenus suisses, IPS normal,
  l'écart dit « frontière », pas « école qui décroche »).
- **Front livré** : `pages/atlas/CroisementsSuggeres.jsx` (grille de cartes-questions : question,
  lecture, 3 communes par côté cliquables vers leur fiche, sources cliquables, caveat sophisme
  écologique) inséré entre la carte et le bloc d'analyse ; un clic ouvre le nuage préconfiguré
  (paramètres `i` + `vs`, vue nationale, défilement). 6 cartes visibles, les autres repliées.
  Build + 42 tests vitest OK.
- **Reste à faire** : affiner questions/verdicts via overrides au fil de l'eau ; envisager
  l'entrée de l'Atlas par 4-5 questions d'appel (sélecteur en second) ; variantes d'une carte
  accessibles dans l'UI (aujourd'hui dans le JSON seulement).

### K. Pont avec le projet socio-analyse : machine à angles, pas source de données (2026-07-04)

Le projet socio-analyse (`VsCode/socio-analyse/MEMENTO.md`) est un capital **conceptuel et qualitatif**
(emanet, légitimité vernaculaire, critique du connexionnisme). Règle arbitrée : **aucun de ces concepts
ne passe le test n°1** (pas de donnée qui mesure l'emanet), donc **jamais de quantification directe**,
ce serait le fourre-tout que ce document s'interdit. Les deux projets restent distincts.

Ce que socio-analyse apporte à Outsiders, c'est **des questions testables et des garde-fous de cadrage** :

- **Pont fort** : « le dispositif innovant comme épreuve déguisée » → enrichit le sujet G
  (Parcoursup : pédagogie « à projet » × taux de boursiers, voir section G).
- **Pont de cadrage** : « pluralité des régimes de légitimité culturelle » → pour le sujet H (ARCOM),
  ne pas écrire « les jeunes n'écoutent plus » (lecture déficitaire) mais « ils consomment sous un
  autre régime ».
- **Boussole éditoriale transverse** : la thèse « la non-nomination rend les alternatives impensables »
  est exactement ce que fait Outsiders quand il nomme les idées reçues et rend des verdicts. À garder
  en tête au moment de choisir angles et titres, pas comme sujet autonome.
