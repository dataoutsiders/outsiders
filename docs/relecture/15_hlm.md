# 15. Les HLM sont là où la France est pauvre ?
> Carte `hlm` · Pas partout · dossier `/atlas?i=hlm&vs=revenu` · fiche préparée le 30/10/2026

## Ce qu'affiche la carte

- **Question** : « Les HLM sont là où la France est pauvre ? »
- **Surtitre** : Logement ; **unité** : Départements
- **Verdict** : Pas partout (`pasPartout`, était « Faux » avant la vérification du 29/10/2026)
- **Chiffre** : `24 % vs 8 %`
- **Libellé** : « de logements HLM dans les Hauts-de-Seine, département parmi les plus riches, contre la Creuse »
- **Texte** : « Le logement social suit d'abord la ville : les départements urbains en comptent le plus, qu'ils soient aisés comme les Hauts-de-Seine ou modestes comme la Seine-Saint-Denis (31 %). C'est à l'intérieur de chaque département que les HLM se concentrent dans les communes modestes. La relation change selon l'échelle, un piège classique des moyennes territoriales. »
- **Source citée** : « INSEE, recensement 2023 (logement) », lien https://www.insee.fr/fr/statistiques/8997194
- **Bouton** : « Voir le croisement sur la carte », vers `/atlas?i=hlm&vs=revenu`
- Reprise aussi par la page Presse (`Presse.jsx`, liste `RESULTATS`).

## Ce que dit le dossier

Il n'y a pas de dossier rédigé : le bouton ouvre l'Atlas, indicateur « Logement social (HLM) », croisé avec « Revenu médian », à la maille par défaut (départements).

- Choroplèthe des départements : part de logement social parmi les résidences principales (RP 2023).
- Aide de l'indicateur (`config/indicateurs.js`) : « Part des résidences principales louées vides dans le parc social (HLM). Recensement 2023. »
- Bloc « en bref » : médiane des départements, 5 plus hauts et 5 plus bas.
- Nuage « Croiser avec un autre indicateur » (x = revenu médian, y = HLM), droite de pronostic, R², outsiders en résidus studentisés (`lib/residuals.js`). Recalcul sur les données servies : 97 départements (sans Guadeloupe, Martinique, Guyane, faute de revenu ; sans Mayotte, faute des deux), pente +0,5 point de HLM par 1 000 € de revenu médian, **R² = 0,04**. Outsiders au-dessus : Seine-Saint-Denis (t = +4,3), Val-de-Marne (+2,6), Marne (+2,2), Val-d'Oise (+2,1), Seine-Maritime (+2,0) ; en dessous, aucun écart marqué (Ariège, Aveyron, Gers, Lot vers -1,4).
- Le renversement « à l'intérieur de chaque département » n'est visible que si l'on clique sur un département (nuage des communes, filtre par défaut aux communes de 1 000 habitants et plus).
- Ailleurs dans le site : `atlas/croisements.json` ne contient pas de carte-croisement « HLM et revenu » ; la relation n'y figure qu'en variante (« revenu » et « hlm », r = -0,373 entre communes) de la carte « prix et maisons ». Croisements voisins : « IPS des collèges et HLM » (r = -0,47 entre communes, -0,20 entre départements), « diversité des candidats et HLM » (+0,60).

## D'où viennent les chiffres

**Chaîne HLM** : Insee, RP 2023, base « Logement » (`DS_RP_LOGEMENT_PRINC_2023`) -> `python/data/insee_maj/DS_RP_LOGEMENT_PRINC_2023.zip`, décompressé dans `python/data/insee_maj/rp2023_logement/` -> `python/tools/rp2023.py` (lecture par morceaux) + `python/tools/build_atlas_logement.py` -> champ `hlm` de `frontend/public/data/atlas/departements.json`, `atlas/communes/<dep>.json`, `atlas/epci.json` -> page Atlas (`pages/atlas/Atlas.jsx`, `AnalyseBloc.jsx`, `components/charts/OutsidersScatter.jsx`).

- `hlm` = `RP_LOCHLMV / RP x 100`, avec `RP_LOCHLMV` = OCS `DW_MAIN`, TSH `221` « Locataire de logement parc social vide », mesure `DWELLINGS`, année 2023 ; `RP` = OCS `DW_MAIN`. Département et intercommunalité : somme des effectifs communaux, puis ratio (pas de moyenne de pourcentages).
- Le script note lui-même que c'est « l'équivalent le plus proche, pas strictement identique » de l'ancienne variable `P21_RP_LOCHLMV` (« HLM loué vide ») : le RP 2023 parle de parc social, sans modalité HLM distincte.

**Chaîne revenu** : Insee, Filosofi 2023, « Indicateurs sur les revenus et la pauvreté au niveau local » -> `python/tools/_cache_filosofi/DS_FILOSOFI_CC_2023_data.csv` (copie avec métadonnées dans `python/data/insee_maj/filosofi2023/`) -> `python/tools/revenu_filosofi.py` (`niveaux_de_vie_medians('MED_SL')`) -> `build_atlas_communes.py` (champ `revenu`) puis `build_atlas_epci.py` -> mêmes JSON. Au département, c'est la médiane officielle de l'Insee (niveau `DEP`), pas une médiane de médianes.

**Population** (`pop`, filtre de taille du nuage) : `build_atlas_population.py`, RP 2023 population (page Insee 9005956).

**Chiffres de la carte, recalculés sur `atlas/departements.json`**

| Chiffre | Valeur | Calcul |
|---|---|---|
| Hauts-de-Seine | 23,8 % (affiché 24 %) | `hlm` du 92 ; revenu médian 33 790 €, 1er des 97 départements renseignés (Paris 33 650 €) |
| Creuse | 7,8 % (affiché 8 %) | `hlm` du 23 ; revenu médian 23 210 €, 4e plus bas de métropole (après Seine-Saint-Denis, Aude, Pyrénées-Orientales) ; taux de pauvreté 19,5 % |
| Seine-Saint-Denis | 31,0 % | `hlm` du 93, 1er de France ; revenu médian le plus bas de métropole (21 250 €) |
| Corrélation entre départements (vérification du 29/10) | +0,25 | Pearson HLM x revenu médian, 96 départements de métropole ; 0,21 avec La Réunion (97) ; rangs (Spearman) 0,28 ; pondérée par la population 0,12 |
| Corrélation dans les départements | médiane -0,21, négative dans 81 sur 97 | Pearson HLM x revenu entre communes de chaque département (départements de 5 communes renseignées ou plus) ; la plus forte dans les Hauts-de-Seine (-0,86), Paris par arrondissement (-0,84), Val-de-Marne (-0,81), Seine-Saint-Denis (-0,75) ; positive surtout dans l'Ouest (Ille-et-Vilaine +0,30) |

Autres repères recalculés : entre toutes les communes renseignées (30 836), r = -0,13 ; communes de 2 000 habitants et plus (5 463), r = -0,39 ; entre intercommunalités (1 237), r = -0,04. Département le moins doté : Ariège, 4,5 %. 16 721 communes sur 34 688 affichent 0,0 % (aucun ou presque aucun locataire du parc social recensé).

## Les jeux de données

### Jeu 1. Insee, recensement de la population 2023, base « Logement », exploitation principale (`DS_RP_LOGEMENT_PRINC_2023`)

- **Producteur** : Insee. **Intitulé** : « Logements en 2023 : recensement de la population, base de données thématique » (format long codé).
- **Millésime utilisé** : RP 2023 (enquêtes annuelles 2021 à 2025), géographie au 1er janvier 2026. Le fichier contient aussi 2012 et 2017. **Dernier disponible** : 2023 (RP 2024 attendu en 2027, `docs/millesimes_20261030.md`).
- **Page officielle** : https://www.insee.fr/fr/statistiques/8997194
- **Téléchargement direct** : https://www.insee.fr/fr/statistiques/fichier/8997194/DS_RP_LOGEMENT_PRINC_2023_CSV_FR.zip (98 Mo compressé)
- **Fichiers locaux** : `python/data/insee_maj/DS_RP_LOGEMENT_PRINC_2023.zip` ; `python/data/insee_maj/rp2023_logement/DS_RP_LOGEMENT_PRINC_2023_data.csv` (1,22 Go) et `..._metadata.csv` (41 847 lignes, dont 41 769 codes géographiques).
- **Géographie** : France, régions, départements, communes, arrondissements municipaux, EPCI, arrondissements, aires d'attraction des villes 2020, unités urbaines 2020, zones d'emploi 2020, bassins de vie 2022. Pas d'IRIS dans ce fichier.
- **Volume** : 285 lignes par territoire et toutes années confondues (relevé sur le premier territoire du fichier), soit environ 12 millions de lignes (estimation, fichier non lu en entier).

**Colonnes du fichier**

| colonne | sens | utilisée ? |
|---|---|---|
| `GEO` | code du territoire | oui : jointure commune, département, EPCI |
| `GEO_OBJECT` | niveau géographique (modalités ci-dessus) | oui : `COM` et `ARM` seulement ; département et EPCI recalculés par somme des communes |
| `OCS` | catégorie de logement | oui (voir modalités) |
| `L_STAY` | durée de séjour (ancienneté d'emménagement) | non |
| `TDW` | type de logement | oui : `1` Maison pour l'indicateur `maisons` (pas pour `hlm`) |
| `CARS` | nombre de voitures du ménage | non |
| `RP_MEASURE` | mesure du recensement | oui : `DWELLINGS` seulement |
| `CARPARK` | garage, box, parking | non |
| `NOR` | nombre de pièces | non |
| `TSH` | statut d'occupation | oui : `221` pour `hlm`, `100` pour `proprietaires` |
| `BUILD_END` | période d'achèvement | non |
| `NRG_SRC` | combustible principal | non |
| `FREQ` | fréquence (A, annuel) | non (constante) |
| `OBS_STATUS` | statut de l'observation : A normale, K incluse dans une autre catégorie, W inclut une autre catégorie | non (à surveiller) |
| `TIME_PERIOD` | année : 2012, 2017, 2023 | oui : 2023 seulement |
| `OBS_VALUE` | valeur (effectif pondéré, avec décimales) | oui |

**Modalités des dimensions (fichier `_metadata.csv`)**

| dimension | modalités | utilisée ? |
|---|---|---|
| `OCS` Catégorie de logement | `DW_MAIN` résidences principales ; `DW_SEC_DW_OCC` résidences secondaires et logements occasionnels ; `DW_VAC` logements vacants ; `_T` total | `DW_MAIN` : dénominateur et numérateur de `hlm` ; les autres pour `res_secondaires`, `vacants`, `maisons` |
| `TSH` Statut d'occupation | `100` propriétaire ; `200` locataire ; `211` locataire d'un logement du parc privé vide ; `221` locataire d'un logement du parc social vide ; `212_222` locataire d'un logement meublé (privé ou social) ; `300` logé gratuitement ; `_T` total | `221` (hlm), `100` (proprietaires) ; non : `200`, `211`, `212_222`, `300` |
| `RP_MEASURE` Mesure | `DWELLINGS` logements (ménages) ; `DWELLINGS_POPSIZE` population des ménages ; `DWELLING_L_STAY` durée (ancienneté d'emménagement cumulée, en années) ; `DWELLINGS_ROOMS` nombre de pièces (cumulé) | `DWELLINGS` seulement |
| `TDW` Type de logement | `1` maison ; `2` appartement ; `3T6` autres logements de métropole ; `_T` | `1` pour `maisons` |
| `NOR` Nombre de pièces | `R1`, `R2`, `R3`, `R4`, `R_GE5`, `_T` | non |
| `L_STAY` Durée de séjour | `Y_LT2` moins de 2 ans ; `Y2T4` ; `Y5T9` ; `Y10T19` ; `Y20T29` ; `Y_GE30` 30 ans ou plus ; `_T` | non |
| `BUILD_END` Période d'achèvement | `Y_LT1919`, `Y1919T1945`, `Y_LT1946`, `Y1946T1970`, `Y1946T1990`, `Y1971T1990`, `Y1991T2005`, `Y1991T2009`, `Y2006TAAAA`, `Y_LT2010`, `Y_LT2015`, `Y_LT2021`, `_T` (tranches qui varient selon l'année) | non |
| `CARS` Voitures du ménage | `C0` aucune ; `C1` une ; `C_GE1` au moins une ; `C_GE2` deux ou plus ; `_T` | non |
| `CARPARK` Garage, box, parking | `1` oui ; `0` non ; `_T` | non |
| `NRG_SRC` Combustible | `ELC` électricité ; `TOWN_GAS` gaz de ville, réseau de chaleur ; `BOT_GAS` gaz en bouteilles ou citerne ; `OIL` fioul ; `OTH` autres (bois, solaire, géothermie) ; `_Z` hors logement ordinaire ou hors métropole ; `_T` | non |

**Croisements réellement publiés** (relevés sur un territoire, année 2023) : `OCS x TSH` (avec les trois mesures `DWELLINGS`, `DWELLINGS_POPSIZE`, `DWELLING_L_STAY`), `OCS x TDW`, `OCS x TDW x BUILD_END`, `OCS x BUILD_END`, `OCS x L_STAY` (logements, population, pièces), `OCS x NRG_SRC`, `OCS x NOR`, `OCS x CARS`, `OCS x CARPARK`, `OCS x TDW` en pièces. **Le statut d'occupation n'est croisé qu'avec la catégorie de logement** : pas de « HLM par type, taille ou âge du logement » dans ce fichier. En revanche, pour `TSH = 221`, on a le nombre de ménages, la population des ménages et l'ancienneté cumulée, en 2012, 2017 et 2023.

### Jeu 2. Insee, Filosofi 2023, « Indicateurs sur les revenus et la pauvreté au niveau local en 2023 » (`DS_FILOSOFI_CC_2023`)

- **Producteur** : Insee (dispositif Filosofi 2, sources fiscales et sociales). **Millésime utilisé** : 2023, géographie au 1er janvier 2025. **Dernier disponible** : 2023 (paru le 06/08/2026). Filosofi 2022 n'existe pas ; l'Insee prévient que 2023 n'est pas directement comparable à 2012-2021.
- **Page officielle** : https://www.insee.fr/fr/statistiques/8984752
- **Téléchargement direct** : https://www.insee.fr/fr/statistiques/fichier/8984752/FILOSOFI_CC_csv.zip
- **Fichiers locaux** : `python/tools/_cache_filosofi/DS_FILOSOFI_CC_2023_data.csv` (58 Mo, 1 123 172 lignes) ; `python/data/insee_maj/FILOSOFI_CC_csv.zip` et `python/data/insee_maj/filosofi2023/` (données et métadonnées).
- **Géographie** : France, régions, départements, communes, arrondissements municipaux, EPCI, arrondissements, AAV, unités urbaines, zones d'emploi, bassins de vie, autres territoires.

**Colonnes du fichier**

| colonne | sens | utilisée ? |
|---|---|---|
| `GEO` | code du territoire | oui |
| `GEO_OBJECT` | niveau géographique | oui : `COM`, `ARM`, `DEP`, `EPCI` |
| `FILOSOFI_MEASURE` | mesure (liste ci-dessous) | oui : `MED_SL` seulement |
| `UNIT_MULT` | puissance de 10 (0, unités) | non |
| `UNIT_MEASURE` | unité : `EUR_YR` euros par an, `PT` pourcentage, `NR` nombre | non |
| `CONF_STATUS` | `F` libre, `C` confidentiel (secret statistique) | non (les cases vides sont écartées) |
| `OBS_STATUS` | `A` normale, `O` valeur manquante | non |
| `TIME_PERIOD` | 2023 | non (constante) |
| `OBS_VALUE` | valeur | oui |

**Mesures (`FILOSOFI_MEASURE`) et couverture réelle** (nombre de territoires avec une valeur)

| mesure | sens | couverture | utilisée ? |
|---|---|---|---|
| `MED_SL` | niveau de vie médian (euros) | 30 794 communes + 45 arrondissements, 97 départements, 1 235 EPCI | oui : indicateur `revenu` |
| `PR_MD60` | taux de pauvreté au seuil de 60 % de la médiane | 5 242 communes + 45 arrondissements, 97 départements, 1 235 EPCI | non |
| `D1_SL` à `D9_SL` (sans D5) | 1er à 9e décile du niveau de vie | départements, régions, France seulement | non |
| `Q1_SL`, `Q3_SL`, `IQR_SL` | quartiles et écart interquartile | idem | non |
| `IR_D9_D1_SL` | rapport interdécile D9/D1 | idem | non |
| `S80S20_SL` | rapport des masses de niveau de vie des 20 % les plus aisés et des 20 % les plus modestes | idem | non |
| `GI_SL` | indice de Gini | idem | non |
| `S_EI_DI`, `S_EI_DI_SAL`, `S_EI_DI_N_SAL`, `S_EI_DI_UNE` | part des revenus d'activité, des salaires, des revenus non salariés, des indemnités de chômage dans le revenu disponible | idem | non |
| `S_RET_PEN_DI` | part des pensions, retraites et rentes | idem | non |
| `S_INC_ASS_DI` | part des revenus du patrimoine et autres | idem | non |
| `S_SOC_BEN_DI` et ses composantes `_FAM_BEN`, `_HOU_BEN`, `_MIN_SOC` | part des prestations sociales, dont familiales, **logement**, minima sociaux | idem | non |
| `S_DIR_TAX_DI` | part des impôts directs | idem | non |

Pour mémoire, le fichier Filosofi 2021 en cache (`_cache_filosofi/base-cc-filosofi-2021-geo2025_csv.zip`) contient en plus `NUM_HH` (ménages), `NUM_PER` (personnes), `NUM_CU` (unités de consommation) et `S_HH_TAX` (part des ménages imposés), absents du 2023.

### Jeu 3. Champs dérivés servis au navigateur (`frontend/public/data/atlas/departements.json`, 101 lignes)

| champ | sens | utilisé par la carte ? |
|---|---|---|
| `code`, `dep` | code et nom du département | oui |
| `hlm` | part des résidences principales occupées par un locataire du parc social vide (%) | oui |
| `revenu` | niveau de vie médian Filosofi 2023 | oui (axe x) |
| `pop` | population RP 2023 | oui (filtre de taille, pas au département) |
| `proprietaires`, `res_secondaires`, `vacants`, `maisons` | autres indicateurs logement du même script | non (mais choisissables dans l'Atlas) |
| `prix_m2` | prix médian DVF | non |
| `ips_*`, `va_lycee`, `cumul`, `ips_moyen` | indicateurs scolaires | non |
| `diplome_sup`, `cadres`, `intermediaires`, `employes`, `ouvriers`, `jeunes`, `ages65`, `natalite`, `idp_candidats` | recensement, état civil, élus | non |

## Ce qu'on n'exploite pas encore

- **`PR_MD60`, taux de pauvreté (Filosofi 2023)**, disponible au département et à l'EPCI. C'est la mesure qui répond littéralement à « là où la France est pauvre ». Recalcul : entre départements, HLM et taux de pauvreté sont corrélés à **+0,25** (métropole +0,23), soit le même signe qu'avec le revenu médian (+0,21) ; entre EPCI, **+0,28** contre -0,04 avec le revenu médian. Dans les départements urbains, revenu médian élevé et pauvreté élevée coexistent : la réponse dépend autant de la mesure de la pauvreté que de l'échelle. Les Hauts-de-Seine ont 13,5 % de pauvres, la Creuse 19,5 %, la Seine-Saint-Denis 29,5 %.
- **`D1_SL`, 1er décile (départements)** : r = -0,28 avec les HLM. Le parc social suit mieux le bas de la distribution que la médiane.
- **`S_SOC_BEN_DI_HOU_BEN`, part des prestations logement dans le revenu** (départements) : r = +0,22 ; utile pour distinguer l'aide à la personne (APL, souvent dans le parc privé) de l'aide à la pierre (HLM).
- **`TSH = 211`, locataires du parc privé vide, et `212_222`, meublés** : les ménages modestes logent aussi dans le parc privé (notamment dans les départements ruraux et les villes moyennes). Un indicateur « locataires du privé » ou « locataires, tous parcs » montrerait où vit la pauvreté hors HLM.
- **`RP_MEASURE = DWELLINGS_POPSIZE` pour `TSH = 221`** : la part de la **population** (et non des ménages) qui vit en logement social. Les ménages du parc social sont plus grands en moyenne : la part de personnes est plus élevée que la part de logements.
- **`RP_MEASURE = DWELLING_L_STAY` pour `TSH = 221`** : ancienneté moyenne d'emménagement des locataires du parc social (durée cumulée / ménages). Indice de faible rotation du parc, donc d'accès difficile.
- **`TIME_PERIOD` 2012 et 2017** : l'évolution de la part de HLM sur onze ans (effet de la loi SRU, rattrapage des communes déficitaires) est déjà dans le fichier, sans téléchargement supplémentaire. Attention : vérifier que la modalité `221` a le même contenu en 2012.
- **Niveaux `UU2020` (unités urbaines) et `AAV2020`** : permettraient de tester directement « le logement social suit la ville » (part de HLM par taille d'unité urbaine ou par couronne d'aire d'attraction), au lieu de l'affirmer.
- **Chiffre plus parlant possible** (calcul approché, à refaire proprement avec les effectifs du RP) : en classant les communes par niveau de vie médian et en les regroupant en cinq tranches de population égale, la part de HLM est d'environ **25 % dans le cinquième le plus modeste** (médiane communale sous 22 710 €) contre **10 % dans le cinquième le plus aisé** (au-dessus de 29 010 €), et de 11 % dans les trois tranches du milieu. Approximation : HLM pondéré par la population municipale et non par le nombre de résidences principales.

## Autres sources possibles

- **RPLS, répertoire des logements locatifs des bailleurs sociaux** (SDES, ministère de la Transition écologique), état du parc au 1er janvier, annuel ; jeu mis à jour le 23/10/2026 sur data.gouv.fr. Page : https://www.data.gouv.fr/datasets/donnees-detaillees-au-logement-du-repertoire-des-logements-locatifs-des-bailleurs-sociaux-rpls ; fichier CSV : https://data.statistiques.developpement-durable.gouv.fr/dido/api/v1/datafiles/f3c2f2cb-8fb1-40fd-8733-964247744c9a/csv ; dictionnaire : https://data.statistiques.developpement-durable.gouv.fr/dido/api/files/c6a10559-a936-4bee-9be0-a2fc7d36e18e. Une ligne par logement (adresse, situation en QPV, type, pièces, surface, année de construction, mode d'entrée, financement initial PLAI / PLUS / PLS, conventionnement, DPE). Apporte : le décompte administratif (et non déclaratif) du parc, y compris vacant ; la **nature du parc** (PLAI très social contre PLS intermédiaire) ; la part en QPV ; l'âge du parc. Fichier volumineux ; le SDES publie aussi chaque année « Le parc locatif social au 1er janvier » avec des tableaux par commune (à vérifier pour le millésime 2026).
- **Communes et inventaire SRU** (ministère de la Transition écologique), 2 208 communes du périmètre SRU au 1er janvier 2026, inventaire au 1er janvier 2025, publié le 11/08/2026. Page : https://www.data.gouv.fr/datasets/communes-et-inventaire-sru ; CSV : https://static.data.gouv.fr/resources/communes-et-inventaire-sru/20260811-123753/donnees-sru-data-gouv-2026.csv (séparateur `;`, encodage Windows). Colonnes : `hexagone_drom`, région, département, `Code_INSEE_commune`, nom, `Population_municipale_01_01_2026`, EPCI et `EPCI_SRU`, unité urbaine et `UU_SRU`, `Commune_isolée_article_L_302_5_CCH`, `Commune_sru_au_01_01_2026` et `_2025`, `Nombre_lls_ Inventaire_au_01_01_2025`, `Taux_SRU_au_01_01_2025`, `Taux_cible_commune` (20 ou 25 %), `commune_deficitaire_au_01-01-2025`, `Commune_carencee_2023_2025`, `Commune_exemptee_2026_2028`, `Prelevement_net_2026_dont_majoration`. Apporte : la dimension politique (communes aisées déficitaires ou carencées qui paient plutôt que construire), au coeur de la question « où sont les HLM ». Millésimes antérieurs (2024, 2025) sur la même page : évolution possible.
- **Quartiers prioritaires de la politique de la ville 2024** (ANCT), mis à jour le 06/10/2026. Page : https://www.data.gouv.fr/datasets/quartiers-prioritaires-de-la-politique-de-la-ville-qpv ; liste : https://static.data.gouv.fr/resources/quartiers-prioritaires-de-la-politique-de-la-ville-qpv/20260721-095036/listeqp2024-cog2025.csv ; périmètres : https://static.data.gouv.fr/resources/quartiers-prioritaires-de-la-politique-de-la-ville-qpv/20260115-204323/qpv-2024-geojson.zip. Apporte : les QPV sont délimités sur le revenu (carroyage) ; croisés avec RPLS (champ QPV), ils diraient quelle part du parc social est dans les quartiers pauvres.
- **Filosofi à l'IRIS 2021** (Insee, déjà téléchargé par `build_segregation.py`) : https://www.insee.fr/fr/statistiques/fichier/8229323/BASE_TD_FILO_IRIS_2021_DISP_CSV.zip. Avec un RP logement à l'IRIS (base infracommunale « Logement » du RP, à vérifier pour 2023), le renversement d'échelle pourrait être montré jusqu'au quartier.
- **Demande de logement social, Système national d'enregistrement** (ministère chargé du logement) : https://www.data.gouv.fr/datasets/demande-de-logement-social, qui renvoie vers https://www.demande-logement-social.gouv.fr/statistiques/ (fiche data.gouv.fr non mise à jour depuis 2024). Apporte : demandes en attente rapportées aux attributions (tension), par commune ou EPCI selon les tableaux ; montre où le parc manque plutôt qu'où il est.

## Points de relecture

1. **« Logements HLM »** : la mesure est la part des **résidences principales** occupées par un **locataire du parc social loué vide**, déclarée par le ménage au recensement. Ce n'est ni le nombre de logements HLM (RPLS, qui compte aussi les vacants), ni le taux SRU (qui compte aussi foyers et logements conventionnés privés). Le script lui-même signale une correspondance non stricte avec l'ancienne variable « HLM ». Libellé possible : « de résidences principales louées dans le parc social ».
2. **La Creuse n'est pas l'extrême** : 7,8 % mais l'Ariège est à 4,5 % ; la Creuse est 4e plus modeste de métropole par le revenu médian. Le libellé ne dit pas pourquoi la Creuse : ajouter « l'un des plus modestes » pour que la comparaison se lise.
3. **Le lien du bouton montre l'inverse de la thèse principale** : il ouvre le nuage des départements (R² = 0,04, la Seine-Saint-Denis en outsider au-dessus). Le renversement « à l'intérieur de chaque département » demande un clic que rien n'indique. Pistes : renvoyer vers `/atlas?i=hlm&vs=revenu&dep=92` (r = -0,86 entre communes) ou ajouter une phrase d'invitation sur la carte.
4. **« Là où la France est pauvre » dépend de la mesure** : avec le revenu médian la relation départementale est faiblement positive (les départements aisés ont un peu plus de HLM) ; avec le taux de pauvreté elle est aussi positive (les départements pauvres en ont un peu plus). Les deux disent la même chose : le parc social est urbain, et les départements urbains cumulent hauts revenus et pauvreté. La carte gagnerait à le dire, ou à prendre le taux de pauvreté pour coller à la question.
5. **Faiblesse des corrélations** : +0,25 entre départements est faible ; -0,21 en médiane dans les départements est modeste aussi, sauf en Île-de-France (de -0,72 à -0,86). Dans l'Ouest (Ille-et-Vilaine, Morbihan, Charente-Maritime), la relation est positive : les HLM y sont dans les villes-centres, plus riches que leur campagne. « C'est à l'intérieur de chaque département que les HLM se concentrent dans les communes modestes » vaut pour 81 départements sur 97, pas tous : écrire « dans la plupart des départements ».
6. **Source citée incomplète** : la carte croise le revenu (Filosofi 2023) mais ne cite que le recensement.
7. **Outre-mer** : Guadeloupe, Martinique, Guyane ont une valeur HLM mais pas de revenu Filosofi 2023 ; Mayotte n'a ni l'un ni l'autre. Le nuage compte 97 départements, avec La Réunion (17,7 %, 19 110 €) en point isolé.
8. **Communes sans HLM** : près de la moitié des communes (16 721 sur 34 688) affichent 0,0 % ; une corrélation entre communes est dominée par cette masse de zéros, d'où l'intérêt du filtre de taille (r = -0,39 au-dessus de 2 000 habitants).
9. Le croisement HLM x revenu n'existe pas comme carte-croisement dans `croisements.json` (seulement en variante, r = -0,373 entre communes, sous un seuil de population propre à ce script) : chiffre différent de ceux de la carte, à ne pas confondre si on les cite ensemble.
