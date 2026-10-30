# 2. La banlieue décroche ?
> Carte `revenus` · Pas partout · dossier `/terrains/revenus` · fiche préparée le 30/10/2026

## Ce qu'affiche la carte

- **Bandeau** : « Niveau de vie » ; unité « Communes ».
- **Question** : La banlieue décroche ?
- **Verdict** : Pas partout (`pasPartout`).
- **Chiffre** : `85 %`.
- **Libellé** : « des habitants de la grande couronne vivent dans une commune qui a reculé ».
- **Texte** : « De 2014 à 2021, les communes limitrophes de Paris montent dans la hiérarchie des revenus (Clichy, Saint-Ouen, Romainville, Montreuil) pendant que la grande couronne pavillonnaire recule, souvent de peu. Le contrôle sur 2023 confirme le mouvement. Une position relative : presque partout, les revenus augmentent en euros. »
- **Source citée** : « Insee, Filosofi 2014 et 2021 (contrôle sur 2023) ». Le lien mène à https://www.insee.fr/fr/statistiques/7756729, « Principaux indicateurs sur les revenus et la pauvreté aux niveaux national et local en 2021 ».
- **Bouton** : « Qui monte, qui recule ? », vers `/terrains/revenus`.

## Ce que dit le dossier

Page `frontend/src/pages/terrains/TerrainRevenus.jsx`, titre « Qui s'enrichit, qui décroche ? ».

- **En-tête** : presque partout les revenus augmentent en euros ; la question est la place dans la hiérarchie. De 2014 à 2021, les communes limitrophes de Paris montent, la grande couronne pavillonnaire recule.
- **Trois chiffres clés, calculés dans la page** :
  - plus forte progression des villes de 20 000 habitants et plus : **+25,1 points** (Clichy) ;
  - **84,8 %** des habitants de la grande couronne dans une commune qui a reculé, arrondi à 85 % sur la carte ;
  - Paris intra-muros : **+3,4 points**.
- **« Le double mouvement »** : évolution moyenne de la position, pondérée par la population, avec le contrôle 2023 entre parenthèses.

  | Anneau | Communes | 2014-2021 | 2014-2023 | Part de la population en hausse |
  |---|---|---|---|---|
  | Paris (20 arrondissements) | 20 | +3,4 | +3,1 | 57,8 % |
  | Petite couronne | 121 | +0,3 | +0,3 | 53,0 % |
  | Grande couronne | 1 110 | -3,3 | -4,3 | 15,2 % |
  | Grandes villes de province (100 000 hab. et plus) | 57 | -1,2 | **-3,7** | 44,9 % |
  | Villes moyennes de province | 236 | -0,4 | -0,3 | 43,9 % |
  | Communes de province de moins de 20 000 hab. | 28 220 | +0,6 | +1,3 | 53,1 % |

  La page rappelle que les gains des uns sont les pertes des autres (mesure relative).
- **Classements** : les 12 villes qui montent et les 12 qui reculent le plus, avec un seuil au choix de 20 000, 50 000 ou 100 000 habitants.
- **Graphique en pente** : rang des villes de 100 000 habitants et plus, 2014 contre 2021.
- **Carte des intercommunalités** : évolution moyenne pondérée, palette divergente, intercommunalités d'au moins 2 communes du champ.
- **Recherche** d'une commune de 2 000 habitants et plus : position 2014, 2021 et 2023, niveau de vie médian, alerte si 2023 contredit 2021.
- **Méthode** :
  - 29 764 communes de métropole présentes aux trois dates ;
  - 878 écartées parce que leur territoire a changé ;
  - Filosofi 2 (2023) non directement comparable selon l'Insee ;
  - concordance 2021 / 2023 de 0,94 sur les villes de 20 000 habitants et plus ;
  - une commune qui monte peut le faire par l'arrivée de ménages aisés : la mesure décrit des communes, pas des trajectoires de ménages.

## D'où viennent les chiffres

```
Filosofi 2014 (republication Le Figaro, data.gouv.fr) ──> _cache_filosofi/filosofi_2014_communes.csv
Filosofi 2021 (Insee 7756729)                          ──> _cache_filosofi/base-cc-filosofi-2021-geo2025_csv.zip
Filosofi 2 2023 (Insee 8984752, via revenu_filosofi.py) ──> _cache_filosofi/DS_FILOSOFI_CC_2023_data.csv
Mouvements de communes (Insee 8377162)                  ──> _cache_filosofi/v_mvt_commune_2025.csv
Population RP 2023 (atlas/communes/*.json, champ pop, build_atlas_population.py)
Commune -> EPCI (python/data/municipales/communes-epci.json, geo.api.gouv.fr)
        └──> python/tools/build_evolution_revenus.py
               └──> frontend/public/data/showcases/evolution-revenus.json
                      └──> TerrainRevenus.jsx (/terrains/revenus) et Home.jsx (carte)
```

**Calcul** :

1. Pour chaque année (2014, 2021, 2023), les communes sont triées par niveau de vie médian.
2. La position d'une commune est la part cumulée de la population (RP 2023 pour les trois années) des communes au revenu plus faible, de 0 à 100.
3. Évolution = position 2021 moins position 2014. Le contrôle = position 2023 moins position 2014.

**Rattachement des chiffres de la carte**

| Élément | Calcul | Valeur retrouvée |
|---|---|---|
| 85 % | `100 - anneaux['Grande couronne'].part_pop_en_hausse` = part de la population des communes des départements 77, 78, 91 et 95 dont `d` (2021 - 2014) est négatif ou nul | 84,8 % (communes de 2 000 habitants et plus seulement : 85,7 %) |
| Clichy, Saint-Ouen, Romainville, Montreuil montent | `villes[].position_2021 - position_2014` | +25,1 ; +14,0 ; +18,4 ; +10,7 (2023 : +33,2 ; +21,6 ; +18,1 ; ...) |
| « souvent de peu » | Part de la population de la grande couronne dont la commune perd plus de 1 point : 67,5 % ; plus de 5 points : 28,5 % | Recalcul du 30/10 sur les communes de 2 000 habitants et plus |
| « Le contrôle sur 2023 confirme » | `evolution_2023` de la grande couronne = -4,3 ; 83,8 % des habitants dans une commune en recul en 2014-2023 ; corrélation 0,94 | Exact |
| « presque partout, les revenus augmentent en euros » | 3 communes sur 5 070 (2 000 habitants et plus) en baisse en euros courants, 2014-2021 ; hausse médiane +12,7 % | Exact |

## Les jeux de données

### Jeu 1. Filosofi 2014, niveau de vie médian par commune

- **Producteur** : Insee (Filosofi 2014). **Le site lit une republication du Figaro** sur data.gouv.fr (2017), qui ne garde que trois colonnes.
- **Page utilisée** : https://www.data.gouv.fr/datasets/niveau-de-vie-des-francais-par-commune
- **Téléchargement utilisé** : https://static.data.gouv.fr/resources/niveau-de-vie-des-francais-par-commune/20171031-164656/FRANCE_COMMUNE_NIVEAU_DE_VIE-FIGARO.csv
- **Original Insee** : « Revenus et pauvreté des ménages en 2014 », https://www.insee.fr/fr/statistiques/3126432. Téléchargement : https://www.insee.fr/fr/statistiques/fichier/3126432/filo-revenu-pauvrete-menage-2014.zip, fichier `base-cc-filosofi-2014.xls`, onglets COM, EPCI, ARR, DEP, REG, METRO, AU2010, UU2010, ZE2010.
- **Vérifié le 30/10** : les 32 974 médianes renseignées du fichier du Figaro sont identiques à la colonne `MED14` de l'onglet COM de l'Insee. Les deux fichiers ont 36 621 lignes. On peut donc passer à l'original sans changer un chiffre.
- **Fichier local** : `python/tools/_cache_filosofi/filosofi_2014_communes.csv` (36 621 lignes).
- **Géographie** : communes, géographie au 01/01/2015 (la docstring du script indique 2016). Champ : métropole, Martinique et La Réunion.

Colonnes du fichier du Figaro : `CODGEO` (code commune, utilisé), `LIBGEO` (nom, utilisé pour l'affichage), `MED14` (médiane du niveau de vie, utilisée).

Colonnes de l'original Insee (`base-cc-filosofi-2014.xls`, onglet COM), d'après l'onglet « Variables » :

| colonne | sens | utilisée ? |
|---|---|---|
| CODGEO, LIBGEO | code et libellé de la commune | oui (via le fichier du Figaro) |
| NBMENFISC14 | nombre de ménages fiscaux | non |
| NBPERSMENFISC14 | nombre de personnes dans les ménages fiscaux | non (le poids vient du RP 2023) |
| MED14 | médiane du niveau de vie (€) | oui : position 2014 |
| PIMP14 | part des ménages fiscaux imposés (%) | non |
| TP6014 | taux de pauvreté, ensemble (%) | non |
| TP60AGE114 à TP60AGE614 | taux de pauvreté par âge du référent (moins de 30 ans, 30-39, 40-49, 50-59, 60-74, 75 ans ou plus) | non |
| TP60TOL114, TP60TOL214 | taux de pauvreté des propriétaires, des locataires | non |
| PRA14 | part des revenus d'activité | non |
| PTSAC14 | dont salaires, traitements ou chômage | non |
| PBEN14 | dont activités non salariées | non |
| PPEN14 | part des pensions, retraites et rentes | non |
| PPAT14 | part des revenus du patrimoine et autres | non |
| PPSOC14 | part des prestations sociales | non |
| PPFAM14, PPMINI14, PPLOGT14 | dont prestations familiales, minima sociaux, prestations logement | non |
| PIMPOT14 | part des impôts | non |
| D114, D914 | 1er et 9e décile du niveau de vie (€) | non |
| RD14 | rapport interdécile D9/D1 | non |

La même page Insee propose aussi `indic-struct-distrib-revenu-2014-COMMUNES.zip` (https://www.insee.fr/fr/statistiques/3126151). On y trouve tous les déciles et les quartiles, ainsi que des ventilations par âge, taille et type de ménage, statut d'occupation et origine du revenu, pour les communes renseignées (32 974).

### Jeu 2. Filosofi 2021, base communale

- **Intitulé** : « Principaux indicateurs sur les revenus et la pauvreté aux niveaux national et local en 2021 », géographie 2025.
- **Page** : https://www.insee.fr/fr/statistiques/7756729
- **Téléchargement** : https://www.insee.fr/fr/statistiques/fichier/7756729/base-cc-filosofi-2021-geo2025_csv.zip
- **Fichier local** : `python/tools/_cache_filosofi/base-cc-filosofi-2021-geo2025_csv.zip`, avec `DS_FILOSOFI_CC_data.csv` (833 400 lignes) et `DS_FILOSOFI_CC_metadata.csv`.
- **Format** : format long codé de l'Insee.
- **Géographie (`GEO_OBJECT`)** : COM (34 804 communes, médiane renseignée pour 31 212), ARM (arrondissements municipaux), EPCI, ARR, DEP, REG, FRANCE, AAV2020, UU2020, ZE2020, BV2022, OTHER.

**Dimensions**

| dimension | modalités | utilisée ? |
|---|---|---|
| GEO, GEO_OBJECT | code et niveau géographique (voir ci-dessus) | oui : COM et ARM |
| TIME_PERIOD | 2021 | oui |
| UNIT_MEASURE | PT (pourcentage), EUR_YR (euros par an), _Z (nombre), PS (personnes) | non |
| UNIT_MULT | 0 (unités) | non |
| CONF_STATUS | F (libre), C (confidentiel) | non |
| OBS_STATUS | A (normale), O (valeur manquante) | non |
| OBS_VALUE | valeur | oui |

**Mesures (`FILOSOFI_MEASURE`, 20 modalités)**

| code | libellé Insee | utilisée ? |
|---|---|---|
| MED_SL | niveau de vie médian (€) | **oui** : position 2021 |
| D1_SL | 1er décile du niveau de vie (€) | non |
| D9_SL | 9e décile du niveau de vie (€) | non |
| IR_D9_D1_SL | rapport interdécile D9/D1 | non |
| PR_MD60 | taux de pauvreté au seuil de 60 % (%) | non |
| NUM_HH | nombre de ménages | non |
| NUM_PER | nombre de personnes | non |
| NUM_CU | nombre d'unités de consommation | non |
| S_HH_TAX | part des ménages imposés (%) | non |
| S_EI_DI | part des revenus d'activité dans le revenu disponible | non |
| S_EI_DI_SAL | part des salaires | non |
| S_EI_DI_N_SAL | part des revenus des activités non salariées | non |
| S_EI_DI_UNE | part des indemnités de chômage | non |
| S_RET_PEN_DI | part des pensions, retraites et rentes | non |
| S_INC_ASS_DI | part des revenus du patrimoine et autres | non |
| S_SOC_BEN_DI | part de l'ensemble des prestations sociales | non |
| S_SOC_BEN_DI_FAM_BEN | part des prestations familiales | non |
| S_SOC_BEN_DI_HOU_BEN | part des prestations logement | non |
| S_SOC_BEN_DI_MIN_SOC | part des minima sociaux | non |
| S_DIR_TAX_DI | part des impôts directs | non |

### Jeu 3. Filosofi 2 (2023), base communale (contrôle)

- **Intitulé** : « Indicateurs sur les revenus et la pauvreté au niveau local en 2023 ». Paru le 06/08/2026, géographie 2025. Dernier millésime publié : 2023 (Filosofi 2022 n'existe pas).
- **Page** : https://www.insee.fr/fr/statistiques/8984752
- **Téléchargement** : https://www.insee.fr/fr/statistiques/fichier/8984752/FILOSOFI_CC_csv.zip
- **Fichier local** : `python/tools/_cache_filosofi/DS_FILOSOFI_CC_2023_data.csv` (1 123 173 lignes). Le fichier de métadonnées n'est pas gardé en cache ; il est relu dans le zip le 30/10.
- **Géographie** : mêmes niveaux qu'en 2021. COM : 34 768 communes, médiane renseignée pour 30 794.

**Dimensions** : GEO, GEO_OBJECT, TIME_PERIOD (2023), UNIT_MEASURE (EUR_YR, PT, NR), UNIT_MULT, CONF_STATUS (F, C), OBS_STATUS (A, O), OBS_VALUE.

**Mesures (27 modalités)** : par rapport à 2021, il n'y a plus de nombres de ménages, de personnes et d'unités de consommation, ni de part de ménages imposés. Toute la distribution apparaît.

| code | libellé Insee | utilisée ? |
|---|---|---|
| MED_SL | niveau de vie médian (€) | **oui** : position 2023 (contrôle) ; c'est aussi le revenu de l'Atlas |
| D1_SL, D2_SL, D3_SL, D4_SL, D6_SL, D7_SL, D8_SL, D9_SL | déciles 1 à 9 du niveau de vie (€) | non |
| Q1_SL, Q3_SL | 1er et 3e quartile (€) | non |
| IQR_SL | écart interquartile (€) | non |
| IR_D9_D1_SL | rapport interdécile D9/D1 | non |
| S80S20_SL | rapport S80/S20 | non |
| GI_SL | indice de Gini | non |
| PR_MD60 | taux de pauvreté au seuil de 60 % | non (utilisé ailleurs dans l'Atlas, pas ici) |
| S_EI_DI, S_EI_DI_SAL, S_EI_DI_N_SAL, S_EI_DI_UNE | revenus d'activité, salaires, non-salariés, chômage (% du revenu disponible) | non |
| S_RET_PEN_DI | pensions, retraites et rentes | non |
| S_INC_ASS_DI | patrimoine et autres revenus | non |
| S_SOC_BEN_DI, S_SOC_BEN_DI_FAM_BEN, S_SOC_BEN_DI_HOU_BEN, S_SOC_BEN_DI_MIN_SOC | prestations sociales, dont familiales, logement, minima sociaux | non |
| S_DIR_TAX_DI | impôts directs | non |

### Jeu 4. Insee, mouvements de communes

- **Page** : https://www.insee.fr/fr/information/8377162 (code officiel géographique 2025)
- **Téléchargement** : https://www.insee.fr/fr/statistiques/fichier/8377162/v_mvt_commune_2025.csv
- **Fichier local** : `python/tools/_cache_filosofi/v_mvt_commune_2025.csv`, 13 534 lignes.

| colonne | sens | utilisée ? |
|---|---|---|
| MOD | type d'événement. Codes présents : 10 changement de nom ; 20 création ; 21 rétablissement ; 30 suppression ; 31 fusion simple ; 32 création de commune nouvelle ; 33 fusion-association ; 34 transformation de fusion-association en fusion simple ; 35 suppression de commune déléguée ; 41 changement de code dû à un changement de département ; 50 changement de code dû à un transfert de chef-lieu ; 70 transformation de commune associée en commune déléguée ; 71 rétablissement de commune déléguée | oui : tous les codes sauf 10 et 70 font écarter la commune |
| DATE_EFF | date d'effet | oui : à partir du 01/01/2014 |
| TYPECOM_AV, TYPECOM_AP | type de commune avant, après (COM, COMA, COMD, ARM) | non |
| COM_AV, COM_AP | code commune avant, après | oui |
| TNCC_AV, NCC_AV, NCCENR_AV, LIBELLE_AV (et _AP) | type de nom en clair, nom en majuscules, nom enrichi, libellé | non |

### Jeux secondaires

- **Population** : population municipale RP 2023 (Insee, DS_RP_POPULATION_PRINC, page 9005956), lue dans `atlas/communes/<dep>.json`. Elle pondère les **trois** années.
- **Commune -> intercommunalité** : `python/data/municipales/communes-epci.json` (34 969 communes, geo.api.gouv.fr), pour la carte des intercommunalités.
- **Contours des intercommunalités** : `frontend/public/data/geo/epci.geojson` (`build_atlas_epci.py`).

## Ce qu'on n'exploite pas encore

- **Taux de pauvreté** : `TP6014` en 2014, `PR_MD60` en 2021 et 2023. « Décrocher » se lit aussi dans la pauvreté. Une commune peut monter en médiane tout en gardant une pauvreté élevée : c'est le cas typique des communes qui se gentrifient.
- **D1 et D9 aux trois dates** (`D114` / `D914`, `D1_SL` / `D9_SL`) : une commune monte-t-elle par le haut (arrivée de hauts revenus, D9 qui s'envole) ou par le bas (départ des plus modestes, D1 qui monte) ? Cela répondrait directement à la limite écrite dans la page (« l'arrivée de ménages plus aisés suffit »).
- **Rapport interdécile (`RD14`, `IR_D9_D1_SL`)** : les communes qui montent deviennent-elles plus inégales ? C'est un lien naturel avec la carte ségrégation.
- **Population fiscale de chaque année** (`NBPERSMENFISC14`, `NUM_PER` 2021). Le site pondère 2014 avec la population de 2023 : une commune qui a beaucoup grandi pèse trop en 2014. Pondérer chaque année par sa propre population serait plus exact. En 2023, `NUM_PER` n'existe plus et il faudrait garder le RP.
- **Composition du revenu** (prestations, pensions, patrimoine). La grande couronne recule-t-elle parce qu'elle vieillit (part des pensions en hausse) ? Hypothèse à tester avec `PPEN14` / `S_RET_PEN_DI`.
- **Autres niveaux géographiques du même fichier** :
  - DEP et EPCI officiels : médianes vraies au lieu de moyennes pondérées de positions communales ;
  - unités urbaines (UU2020) et aires d'attraction (AAV2020) : « banlieue » au sens de l'Insee (couronne d'une AAV, banlieue d'une unité urbaine) au lieu d'un découpage par départements franciliens.
- **Toutes les grandes villes** : la question parle de « la banlieue », et le dossier ne traite les banlieues de province que par la taille des communes. Avec les AAV, on pourrait comparer pôle et couronne pour Lyon, Marseille, Lille, Toulouse.

## Autres sources possibles

- **Insee, millésimes annuels de Filosofi 2012 à 2021** (une base communale par année sur insee.fr) : une trajectoire annuelle au lieu de deux points, utile pour repérer les communes dont la montée est récente.
- **DGFiP, impôt sur le revenu par collectivité territoriale (IRCOM)**, https://www.data.gouv.fr/datasets/limpot-sur-le-revenu-par-collectivite-territoriale-ircom (mis à jour le 26/05/2026).
  - Revenu fiscal de référence par commune et par tranche, chaque année, jusqu'aux revenus les plus récents.
  - Série homogène qui enjambe la rupture Filosofi / Filosofi 2. Mais ce sont des revenus déclarés par foyer fiscal, pas des niveaux de vie.
- **Recensement, catégories socioprofessionnelles par commune** (RP 2013 et RP 2023, déjà utilisé par l'Atlas pour 2023) : la part de cadres et d'ouvriers aux deux dates. Elle dit si la montée vient d'un changement de population, ce que Filosofi ne permet pas de voir.
- **Recensement, migrations résidentielles** (commune de résidence un an auparavant) : flux d'arrivées et de départs, pour vérifier la gentrification.
- **DVF, prix au m² par commune** (déjà dans l'Atlas pour 2021-2026) : la hausse des prix précède souvent la montée des revenus. Croiser l'évolution des prix et celle de la position.
- **Insee, zonage en aires d'attraction des villes 2020 et unités urbaines 2020** (pages du zonage sur insee.fr) : pour définir la « banlieue » sans s'en tenir à l'Île-de-France.

## Points de relecture

1. **« La banlieue » ou « la grande couronne » ?**
   - La carte répond avec la seule grande couronne francilienne.
   - Plusieurs des plus forts reculs de communes de 20 000 habitants et plus sont en **Seine-Saint-Denis**, petite couronne pavillonnaire de l'est (deux communes à environ -20 et -17 points).
   - Le Val-de-Marne recule (-2,1 en moyenne). La petite couronne n'est à +0,3 que grâce aux Hauts-de-Seine (+2,8).
   - Le texte (« communes limitrophes de Paris ») l'évite, mais le titre « La banlieue » invite à une lecture en bloc. La banlieue des grandes villes de province n'est pas traitée.
2. **Grandes villes de province** : le contrôle 2023 montre un recul net (-3,7, contre -1,2 en 2021). C'est un fait saillant que ni la carte ni la page ne commentent.
3. **« Reculé » compte tout recul**, même de 0,1 point. 85 % pour tout recul ; 67 % pour un recul de plus de 1 point ; 28 % pour plus de 5 points. « Souvent de peu » le dit. Le chiffre de plus de 1 point serait plus solide.
4. **Source 2014 de seconde main** : le fichier du Figaro est identique à l'original Insee (vérifié), mais le dossier cite « fichier communal republié sur data.gouv.fr ». Passer à `base-cc-filosofi-2014.xls` de l'Insee (page 3126432) donne une source primaire et apporte D1, D9 et le taux de pauvreté.
5. **Poids de population** : RP 2023 pour 2014, 2021 et 2023. C'est sans effet sur le tri, mais cela change les positions (la part cumulée). Les communes en forte croissance, souvent périurbaines, sont surpondérées en 2014. À mentionner dans la méthode, ou à corriger avec `NBPERSMENFISC14` et `NUM_PER`.
6. **Rupture de 2023** : bien signalée. La concordance de 0,94 porte sur les villes de 20 000 habitants et plus ; elle n'est pas mesurée pour les petites communes, qui forment l'essentiel de la grande couronne. 11 villes sur 481 de 20 000 habitants et plus changent de sens entre les deux périodes (avec au moins 2 points de mouvement en 2021).
7. **Titre de période** : la page dit « 2014-2021 » alors que 2023 est disponible et donne un recul plus net de la grande couronne (-4,3). La vérification du 29/10 suggérait de passer à 2014-2023. C'est à arbitrer, puisque l'Insee juge les deux dispositifs non directement comparables.
8. **En euros** : hausse médiane de 12,7 % en euros courants de 2014 à 2021, à mettre en regard de l'inflation de la période (Insee, indice des prix) si l'on veut écrire « les revenus augmentent ». En euros constants, la hausse est plus faible.
9. **Champ** : métropole seulement. Les communes à revenu secret (petites communes) et les 878 communes au territoire modifié sont écartées. Le champ couvre 62,9 millions d'habitants.
