# 10. Le meilleur taux de réussite fait la meilleure auto-école ?
> Carte `auto-ecoles` · verdict « Faux » · dossier /terrains/auto-ecoles · fiche préparée le 30/10/2026

## Ce qu'affiche la carte

- **Rubrique** : Permis de conduire ; unité « Auto-écoles » ; couleur `#EA580C`.
- **Question** : « Le meilleur taux de réussite fait la meilleure auto-école ? »
- **Verdict** : `faux`.
- **Chiffre** : **44 %**, « des auto-écoles changent de quart de classement une fois leur contexte pris en compte ».
- **Texte** : « Le taux publié dépend pour un quart du département de l'examen (de 36 % en Guadeloupe à 73 % en Haute-Loire) et aussi de la ville : à département égal, une commune dix fois plus peuplée va avec 2,7 points de moins. Comparée à ce que son contexte laisse attendre, près d'une école sur deux change de quart de classement. »
- **Source citée** : « Sécurité routière, taux de réussite des auto-écoles (fichier du 19 février 2026, data.gouv.fr) », lien https://www.data.gouv.fr/fr/datasets/liste-des-auto-ecoles-et-taux-de-reussite-au-permis-de-conduire/
- **Lien** : « Comparer à contexte égal » vers `/terrains/auto-ecoles`.
- La carte figure aussi dans la page Presse (`RESULTATS` de `Presse.jsx`) et parmi les images de partage.

## Ce que dit le dossier

Page `frontend/src/pages/terrains/TerrainAutoEcoles.jsx`, titre « La meilleure auto-école est-elle celle qui a le meilleur taux ? ».

- 7 922 auto-écoles (7 713 physiques, 209 lignes d'écoles en ligne), 962 280 candidats au permis B en première présentation ; taux national pondéré 60,3 %.
- Chiffres clés : **51 % → 73 %** de réussite selon le département, de Paris à la Haute-Loire (la page prend le minimum de métropole, la carte celui de l'outre-mer) ; **35 %** des écarts entre écoles tiennent au contexte (département et commune) ; **44 %** des écoles changent de quart de classement.
- Décomposition des écarts entre écoles : département 25,4 %, commune 9,6 %, école 49,0 %, hasard 16,0 %.
- À département égal, effets de la commune (points de taux attendu, tous « nets ») : population ×10 : -2,7 ; +10 points de diplômés du supérieur : -1,3 ; +10 points de 65 ans et plus : +1,4 ; +10 points de propriétaires : +0,6 ; +10 points d'IPS des collèges publics : +1,4.
- Entre départements de métropole (96 départements d'au moins 10 écoles) : corrélations du taux moyen avec la part de propriétaires (+0,44), de maisons (+0,39), de cadres (-0,38), d'ouvriers (+0,33), la population (-0,32), les 65 ans et plus (+0,30), les diplômés (-0,28), le brevet (+0,23), l'IPS (+0,03), l'IVAL (+0,02). Maisons et taille ne rendent compte que de 16 % des écarts entre départements.
- Exemple nommé d'une école nettement au-dessus de son attendu (jamais d'exemple négatif nommé).
- Entonnoir « chaque école face à son attendu » : 833 écoles nettement au-dessus, 949 nettement en dessous, les autres dans la marge du hasard.
- Outil de comparaison d'un groupe d'écoles (département, enseigne, mot du nom), classement brut puis à contexte égal, fiche par école.
- Leviers à contexte égal : label qualité +0,4 (indiscernable), école associative -8,9 (net, 87 écoles), permis à 1 € par jour -0,6 (indiscernable), conduite accompagnée proposée +1,7 (net), conduite supervisée proposée -2,3 (net), moins de 50 candidats -1,9 (net), 150 et plus +0,6 (probable).
- Écoles en ligne : -7,9 points face aux écoles physiques du même département (56 637 candidats), trois enseignes détaillées (-6 à -14 points).
- Fiche de l'indicateur : « la période de référence n'est pas précisée dans le fichier » ; limites (première présentation seulement, profil des candidats non publié, centre d'examen inconnu, écoles en ligne comparées au département seulement).

## D'où viennent les chiffres

Chaîne : fichier CSV de la Sécurité routière (serveur `autoecoles.securite-routiere.gouv.fr`, référencé sur data.gouv.fr) -> `python/tools/_cache_auto_ecoles/auto-ecoles.csv` -> `python/tools/build_auto_ecoles.py` (qui lit aussi l'Atlas déjà construit : `frontend/public/data/atlas/communes/*.json`, `departements.json`, `epci.json`, `territoires-index.json`, et `python/data/municipales/communes-epci.json`) -> `frontend/public/data/showcases/auto-ecoles.json` (généré le 29/10/2026) -> page `TerrainAutoEcoles.jsx`. Extrait départemental pour les fiches territoire : `build_territoires_echelles.py` -> `territoires/auto-ecoles-departements.json`.

Étapes du script :
1. Lecture du CSV ; garde les écoles avec `B_nombre_1pra` et `B_taux_1pra` renseignés, au moins 10 candidats, département reconnu par geo.api. Écoles en ligne : agrément suffixé `_<dep>` ou `aue_enligne_flag`.
2. Rattachement à la commune Insee (arrondissements PLM par code postal, base La Poste, nom dans le département) : 99,6 % des écoles physiques.
3. Contexte communal tiré de l'Atlas (RP 2023) : `pop` (en log), `diplome_sup`, `ages65`, `proprietaires`, plus l'IPS des collèges publics (commune, à défaut intercommunalité, à défaut département : 6 412 / 962 / 274 écoles).
4. Attendu : régression pondérée par le nombre de candidats, effets fixes département + contexte communal (spécification `ips`), sur les 7 341 écoles d'au moins 20 candidats ; écarts rétrécis (bayésien empirique) et intervalles à 95 %.

Rattachement des chiffres de la carte :
| Chiffre de la carte | Champ du JSON | Calcul |
|---|---|---|
| 44 % | `stats.change_quart` = 44,2 | sur les 7 341 écoles du modèle : quart du taux brut `t` comparé au quart de l'écart rétréci `e2` ; part des écoles dont le quart change |
| « pour un quart du département » | `stats.r2_departement` = 25,4 | R² pondéré de la régression du taux sur les seuls effets fixes département |
| 36 % Guadeloupe | `stats.dep_min` | taux pondéré du département le plus bas parmi ceux d'au moins 20 écoles (outre-mer compris) |
| 73 % Haute-Loire | `stats.dep_max` = 72,9 | idem, le plus haut (la Lozère, 79,9 %, est écartée : 10 écoles) |
| -2,7 points | `effets_contexte[lpop]` (intervalle -3,5 à -1,9) | coefficient de log(population) ramené à une population ×10, à département égal **et** à diplômés, âge, propriétaires et IPS égaux |
| « près d'une école sur deux » | `stats.change_quart` | même chiffre que le 44 % |
| fichier du 19 février 2026 | `source.date_fichier` | en-tête `Last-Modified` du serveur ; vérifié le 30/10/2026 : toujours le 19/02/2026, 5 320 162 octets, identique au cache |

## Les jeux de données

### 1. Liste des auto-écoles et taux de réussite au permis de conduire (Ministère de l'Intérieur, Délégation à la sécurité routière)

- **Intitulé exact** : « Liste des auto-écoles et taux de reussite au permis de conduire » (data.gouv.fr, organisation Ministère de l'intérieur, licence Licence ouverte v2, fréquence déclarée mensuelle).
- **Millésime utilisé** : fichier servi le 19/02/2026 (métadonnée data.gouv.fr de la ressource restée au 01/07/2025). C'est aussi le dernier disponible au 30/10/2026. **La période des taux n'est indiquée nulle part** (ni fichier, ni nomenclature) ; le taux national calculé (60,3 %) est proche du taux 2025 de l'épreuve pratique B cité par des sites tiers (59,9 %), ce qui suggère une année 2025 ou douze mois glissants, à confirmer auprès du producteur.
- **Page officielle** : https://www.data.gouv.fr/datasets/liste-des-auto-ecoles-et-taux-de-reussite-au-permis-de-conduire ; carte officielle https://autoecoles.securite-routiere.gouv.fr/
- **Téléchargement direct** : https://autoecoles.securite-routiere.gouv.fr/sites/default/files/certified-schools/auto-ecoles.csv (le serveur exige un User-Agent de navigateur)
- **Documentation** : nomenclature des en-têtes v2 du 23/02/2024, https://static.data.gouv.fr/resources/liste-des-auto-ecoles-et-taux-de-reussite-au-permis-de-conduire/20240307-144708/nomenclature-des-entetes-v2-23022024.pdf
- **Fichier local** : `python/tools/_cache_auto_ecoles/auto-ecoles.csv` (séparateur `;`, UTF-8 avec BOM, valeurs absentes codées `NC`).
- **Géographie** : un établissement (agrément) par ligne, adresse postale, département ; outre-mer compris (dont 975, 977, 98).
- **Taille** : 11 371 lignes, 82 colonnes ; 8 147 écoles avec un taux B en première présentation.

Sens des colonnes : nomenclature du producteur quand elle existe ; sinon « (déduit) ». Plusieurs colonnes du fichier sont absentes de la nomenclature, et la nomenclature cite trois colonnes `*_nombre_formateurs` qui ne sont pas dans le fichier.

| colonne | sens | utilisée ? |
|---|---|---|
| `raf_numero` | numéro d'agrément de l'auto-école (suffixe `_<dep>` pour les écoles en ligne) | oui : identifiant, repérage des écoles en ligne (229 suffixés) |
| `aue_raisonsociale` | raison sociale | oui : nom affiché, recherche par mot, enseignes |
| `aue_adresse` | adresse | non |
| `aue_codepostal` | code postal | oui : rattachement à la commune |
| `aue_commune` | commune (libellé) | oui : rattachement à la commune |
| `dpt_id` | département | oui : effets fixes, moyennes départementales |
| `aue_siteinternet` | site internet (non documenté, 680 renseignés) | non |
| `aue_permis1euro_flag` | école partenaire du permis à 1 € par jour (4 436 vrais) | oui : levier |
| `aue_labelqualite_flag` | label qualité « Qualité des formations au sein des écoles de conduite » (3 754 vrais) | oui : levier |
| `aue_ecoleasso_flag` | auto-école associative (302 vrais) | oui : levier |
| `aue_aac_flag` | propose l'apprentissage anticipé de la conduite (non documenté, déduit ; 2 353 vrais) | oui : levier |
| `aue_cs_flag` | propose la conduite supervisée (non documenté, déduit ; 7 080 vrais) | oui : levier |
| `aue_enligne_flag` | école en ligne (non documenté ; 231 vrais) | oui : repérage des écoles en ligne |
| `A_flag`, `A1_flag`, `A2_flag`, `B_flag`, `BE_flag`, `C_flag`, `C1_flag`, `CE_flag`, `C1E_flag`, `D_flag`, `D1_flag`, `DE_flag`, `D1E_flag` | catégorie de permis enseignée (B : 11 060 écoles ; A2 : 5 178 ; A1 : 4 795 ; A : 4 716 ; BE : 2 840 ; C : 1 023 ; CE : 967 ; D : 815 ; DE : 377 ; C1 : 395 ; C1E : 356 ; D1 : 154 ; D1E : 137) | non |
| `A_nombre_1pra` | candidats en première présentation, catégorie A | non (toujours `NC`) |
| `A_taux_1pra` | taux de réussite en première présentation, catégorie A | non (toujours `NC`) |
| `A_taux_xpra` | taux toutes présentations, catégorie A (la nomenclature écrit « catégorie B » par erreur) | non (toujours `NC`) |
| `B_nombre_1pra` | candidats en première présentation, catégorie B | oui : effectif, pondération, seuils de 10 et 20 |
| `B_taux_1pra` | taux de réussite en première présentation, catégorie B (fraction de 0 à 1) | oui : l'indicateur |
| `B_taux_1pra_aac` | taux en première présentation des candidats issus de la conduite accompagnée (6 003 renseignés) | non |
| `B_taux_1pra_cs` | taux en première présentation des candidats issus de la conduite supervisée (4 451 renseignés) | non |
| `B_taux_xpra` | taux de réussite toutes présentations, catégorie B (arrondi à 2 décimales, virgule ; 8 213 renseignés ; médiane 0,61) | non |
| `CD_nombre_1pra`, `CD_taux_1pra`, `CD_taux_xpra` | poids lourds et transport en commun (catégories C et D) : candidats et taux | non (toujours `NC`) |
| `optionnel_nombre_examen_total_tout_passage_BC` | nombre d'examens B (épreuve en circulation, déduit), toutes présentations (8 213 renseignés ; 1,57 million au total) | non |
| `optionnel_nombre_examen_total_tout_passage_AC`, `_AP`, `_CEC`, `_CEP` | idem pour la moto (circulation, plateau) et le groupe lourd (déduit) | non (toujours `NC`) |
| `optionnel_taux_reussite_tout_passage_AC`, `_AP`, `_CEC`, `_CEP` | taux toutes présentations correspondants | non (toujours `NC`) |
| `optionnel_nombre_examen_total_1er_passage_AC`, `_AP`, `_CEC`, `_CEP` | examens en première présentation correspondants | non (toujours `NC`) |
| `optionnel_taux_reussite_1er_passage_AC`, `_AP`, `_CEC`, `_CEP` | taux en première présentation correspondants | non (toujours `NC`) |
| `optionnel_nombre_1er_passage_acc_total` | intitulé « nombre », mais contenu identique, ligne à ligne, à `B_taux_1pra_aac` (un taux) | non ; anomalie du producteur |
| `optionnel_nombre_1er_passage_superv_total` | intitulé « nombre », contenu identique à `B_taux_1pra_cs` | non ; anomalie du producteur |
| `<cat>_acc_sourd_mal` (13 catégories A à D1E) | école accueillant les personnes sourdes ou malentendantes pour la catégorie (B : 200 écoles ; autres : 1 à 38) | non |
| `<cat>_acc_handi` (13 catégories) | école équipée pour les personnes handicapées (véhicule aménagé) pour la catégorie (B : 266 ; autres : 0 à 13) | non |

### 2. Recensement de la population 2023 (Insee), via l'Atlas Outsiders

- **Producteur** : Insee. **Millésime** : RP 2023, géographie au 1er janvier 2026 (dernier disponible).
- **Jeux** : `DS_RP_POPULATION_PRINC_2023` (page https://www.insee.fr/fr/statistiques/9005956), `DS_RP_DIPLOMES_PRINC_2023` (9006527), `DS_RP_LOGEMENT_PRINC_2023` (8997194), `DS_RP_EMPLOI_LR_COMP_2023` (9002680) ; téléchargement `https://www.insee.fr/fr/statistiques/fichier/<page>/<nom>_CSV_FR.zip`.
- **Fichiers locaux** : `python/data/insee_maj/` (zips et dossiers `rp2023_*`), lus par `python/tools/rp2023.py` puis `build_atlas_*.py` ; le dossier Auto-écoles ne lit que les JSON de l'Atlas.
- **Format** : CSV « long » (`GEO`, `GEO_OBJECT`, dimensions codées, `RP_MEASURE`, `TIME_PERIOD`, `OBS_VALUE`) ; les colonnes sont détaillées dans les fiches des cartes de l'Atlas. Ici, les variables de l'Atlas :

| variable de l'Atlas (commune) | sens | utilisée ? |
|---|---|---|
| `pop` | population municipale | oui : taille de la commune (log), modèle et tableau départemental |
| `diplome_sup` | part des diplômés du supérieur | oui : modèle |
| `ages65` | part des 65 ans et plus | oui : modèle |
| `proprietaires` | part des résidences principales occupées par leur propriétaire | oui : modèle |
| `cadres`, `ouvriers` | parts dans l'emploi | oui : corrélations départementales ; non dans le modèle retenu (testées par `--explore`) |
| `maisons` | part des maisons | oui : corrélations départementales ; non dans le modèle |
| `jeunes`, `hlm` | moins de 15 ans, logements HLM | non (testées dans la spécification `large`) |
| `employes`, `intermediaires`, `res_secondaires`, `vacants`, `natalite` | autres indicateurs de l'Atlas | non |
| `revenu` | niveau de vie médian Filosofi 2023 | non : le script dit encore « Pas de revenu : la série communale disponible dans l'atlas date de 2014 », ce qui n'est plus vrai |
| `prix_m2`, `idp` | prix DVF, diversité des candidats municipaux | non |

Dans `DS_RP_LOGEMENT_PRINC_2023`, la dimension `CARS` (ménages sans voiture, une, deux ou plus) et `CARPARK` (garage, box, parking) existent dans le fichier déjà téléchargé et ne sont pas reprises dans l'Atlas.

### 3. Indice de position sociale des collèges (Éducation nationale, DEPP), via l'Atlas

- Rentrée 2025 (voir la fiche `11_ecole.md` pour les colonnes) ; page https://www.education.gouv.fr/depp/l-indice-de-position-sociale-ips-357755.
- Utilisé : `ips_college_public` de la commune, de l'intercommunalité ou du département (moyenne des collèges publics). Non utilisés : IPS des écoles, des lycées, des collèges privés (`ips_college_prive`, `ips_college_tous` au département), écart-type de l'IPS.

### 4. Valeur ajoutée des lycées (IVAL), via l'Atlas

- Page https://www.data.gouv.fr/datasets/indicateurs-de-valeur-ajoutee-des-lycees-denseignement-general-et-technologique-2 ; seule la moyenne départementale `va_lycee` sert, dans les corrélations départementales.

### 5. Diplôme national du brevet par établissement (Éducation nationale)

- **Intitulé** : « Diplôme national du brevet par établissement » ; sessions 2006 à 2021 dans le fichier ; sessions 2019 et 2021 utilisées (2020 écartée, contrôle continu). La métadonnée data.gouv.fr est datée du 23/09/2026 : vérifier si des sessions récentes y ont été ajoutées (`docs/millesimes_20261030.md` note que les sessions 2022 à 2025 sont dans le jeu de la valeur ajoutée des collèges).
- **Page** : https://www.data.gouv.fr/fr/datasets/diplome-national-du-brevet-par-etablissement-1/ ; **téléchargement** : https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-dnb-par-etablissement/exports/csv?use_labels=true
- **Fichier local** : `python/tools/_cache_auto_ecoles/dnb-par-etablissement.csv` (139 580 lignes). **Géographie** : établissement (UAI), commune, département, académie, région.

| colonne | sens | utilisée ? |
|---|---|---|
| `Session` | année de la session | oui : filtre 2019 et 2021 |
| `Numero d'etablissement` | UAI | non |
| `Type d'etablissement` | collège, lycée professionnel, lycée, EREA, CFA, autre | oui : filtre collèges |
| `Patronyme` | nom de l'établissement | non |
| `Secteur d'enseignement` | public / privé | non (public et privé mélangés) |
| `Commune`, `Libellé commune` | code et nom de la commune | oui (code) : département |
| `Code département`, `Libellé département`, `Code académie`, `Libellé académie`, `Code région`, `Libellé région` | géographie administrative | non |
| `Inscrits` | inscrits | non |
| `Presents` | présents | oui : dénominateur |
| `Admis` | admis | oui : taux de réussite départemental |
| `Admis sans mention`, `Nombre_d_admis_Mention_AB` | admis sans mention, mention assez bien | non |
| `Admis Mention bien`, `Admis Mention très bien` | mentions bien et très bien | calculées (part des mentions) mais non exportées |
| `Taux de réussite` | taux publié | non (recalculé) |

### 6. Base officielle des codes postaux (La Poste)

- Page https://www.data.gouv.fr/fr/datasets/base-officielle-des-codes-postaux/ (métadonnée du 09/07/2023) ; téléchargement https://data.laposte.fr/data-fair/api/v1/datasets/laposte-hexasmal/raw ; fichier local `_cache_auto_ecoles/laposte-hexasmal.csv` (39 192 lignes, Latin-1).

| colonne | sens | utilisée ? |
|---|---|---|
| `Code_commune_INSEE` | code commune | oui : rattachement |
| `Nom_de_la_commune` | nom de la commune | oui |
| `Code_postal` | code postal | oui |
| `Libellé_d_acheminement` | libellé d'acheminement | oui (troisième essai) |
| `Ligne_5` | ancienne commune ou lieu-dit | oui (deuxième essai) |

### 7. API Géo (geo.api.gouv.fr) et correspondance communes-intercommunalités

- `communes?fields=code,nom,centre` et `communes?type=arrondissement-municipal` (fichiers `communes-centres.json`, `arrondissements-centres.json`) : nom affiché et point de la carte. Champs disponibles non demandés : `codesPostaux`, `siren`, `codeEpci`, `codeDepartement`, `codeRegion`, `population`, `surface`, `contour`, `mairie`, `zone`.
- `departements?fields=code,nom` (`departements.json`) : liste des départements valides.
- `python/data/municipales/communes-epci.json` (34 969 communes : `code`, `codeEpci`, `nom`) : repli de l'IPS sur l'intercommunalité.

## Ce qu'on n'exploite pas encore

- **`B_taux_xpra` et `optionnel_nombre_examen_total_tout_passage_BC`** (toutes présentations) : on peut calculer pour chaque école un **nombre moyen de passages par candidat** (examens toutes présentations / candidats en première présentation ; 1,63 en moyenne nationale) et un taux final. Une école qui présente peu et tard a un bon taux en première présentation ; une école qui présente tôt et souvent en a un moins bon. C'est précisément la question de la carte (le meilleur taux fait-il la meilleure école ?), sous un angle que le contexte géographique ne capte pas.
- **`B_taux_1pra_aac` et `B_taux_1pra_cs`** : taux des candidats issus de la conduite accompagnée et supervisée. Avec `B_taux_1pra`, ils donnent une idée de la **composition du public** (part d'apprentissage anticipé, profil plus jeune et plus préparé), la principale lacune avouée du modèle (« le profil des candidats n'est pas publié »). Comparer les écoles sur le seul taux de la filière traditionnelle, ou ajouter la part de conduite accompagnée comme variable, rendrait la comparaison plus juste.
- **Revenu médian Filosofi 2023** (`revenu` de l'Atlas) : disponible à la commune, écarté par un commentaire devenu faux. Il pourrait remplacer ou compléter l'IPS des collèges (qui décrit des collégiens, pas des candidats de 17 à 25 ans).
- **Ménages sans voiture** (`CARS` du RP logement, déjà sur le disque) : bon candidat pour expliquer l'« effet grande ville » (-2,7 points) : moins d'heures de conduite en famille, moins de conduite accompagnée là où l'on n'a pas de voiture.
- **Catégories enseignées et accessibilité** (`*_flag`, `*_acc_handi`, `*_acc_sourd_mal`) : profil de l'offre (école généraliste moto et poids lourds contre école B seule) comme levier ; carte de l'offre accessible aux personnes handicapées (266 écoles pour le B), sujet d'inégalité territoriale cohérent avec la ligne éditoriale.
- **Part des mentions au brevet** : déjà calculée, jamais exportée ; et le secteur public / privé du brevet, non distingué.

## Autres sources possibles

- **Bilan annuel des examens du permis de conduire** (Délégation à la sécurité routière). Le bilan 2021 est vérifié (41 pages, https://www.securite-routiere.gouv.fr/sites/default/files/2023-04/bilan_2021_0.pdf) : taux en première présentation et toutes présentations par catégorie, et **par département pour le permis B : examinés, taux global, examinés et taux en conduite accompagnée, part de la conduite accompagnée, candidats libres**. Il permettrait de corriger chaque département de sa part de conduite accompagnée et de dater les taux. Les bilans 2024 et 2025 sont cités par des sites tiers (58,2 % puis 59,9 % à l'épreuve pratique B), l'adresse officielle reste à retrouver.
- **Taux de réussite auto-école par auto-école en 2018** (Sécurité routière, déposé sur data.gouv.fr par un compte supprimé) : https://www.data.gouv.fr/datasets/taux-de-reussite-auto-ecole-par-auto-ecole-en-2018 , fichier https://static.data.gouv.fr/resources/taux-de-reussite-auto-ecole-par-auto-ecole-en-2018/20191219-173930/2018-tr-eeac-diffusion.xls (catégories A1, A2, B, B1, BE, C, CE, D). Avec le numéro d'agrément, il offre un **test de stabilité** : une école au-dessus de son attendu en 2018 l'est-elle encore aujourd'hui ? C'est la meilleure façon de savoir si l'écart mesure l'école ou le hasard. Un jeu 2012 existe aussi (dépôt d'un particulier, permis B et code, https://www.data.gouv.fr/datasets/taux-de-reussite-des-auto-ecoles-france-2012).
- **Archives du fichier mensuel** : la fréquence est déclarée mensuelle ; conserver une copie datée à chaque reconstruction donnerait une série maison.
- **Base Sirene** (Insee, https://www.data.gouv.fr/datasets/base-sirene-des-entreprises-et-de-leurs-etablissements-siren-siret) : établissements en activité sous le code NAF 85.53Z « Enseignement de la conduite » : ancienneté, effectif salarié par tranche, catégorie juridique, appartenance à un groupe (même SIREN), pour qualifier l'école au-delà du nom.
- **Répertoire national des associations** (Ministère de l'Intérieur, https://www.data.gouv.fr/datasets/repertoire-national-des-associations) : confirmer et décrire les écoles associatives (objet, date de création), le levier le plus marqué du dossier (-8,9 points).
- **Jeux départementaux** : « Auto-écoles agréées en Loire-Atlantique » (DDTM 44, mis à jour le 28/10/2026, https://www.data.gouv.fr/datasets/auto-ecoles-agreees-en-loire-atlantique) avec les véhicules aménagés et boîtes automatiques ; centres d'examen géolocalisés de quelques départements (Bas-Rhin, Sarthe, Vendée, Haute-Vienne, Vosges, Eure-et-Loir, Côte-d'Or), trop partiels et anciens pour un modèle national mais utiles pour illustrer l'effet du centre d'examen.
- **Aides au permis** : « Auto-écoles partenaires du chèque permis de conduire » (Région Île-de-France), « Aide au permis de conduire (PERM) » (Région Hauts-de-France) : publics aidés, donc profil des candidats.
- **Dérivé tiers à éviter comme source** : « Taux de réussite au permis B par département (1re présentation), France 2025 » (centrestagepermis.fr, sur data.gouv.fr) recalcule le même fichier et le date de 2025, sans citer de source pour la période.
- Pas de jeu officiel ouvert repéré sur le **prix du permis** ni sur les **délais d'attente d'une place d'examen** par département, deux facteurs souvent avancés.

## Points de relecture

- **Le verdict « Faux » est plus fort que les données.** Le taux brut et l'écart à contexte égal sont corrélés à 0,8. Parmi les écoles du quart supérieur au taux brut, 68 % y restent une fois le contexte pris en compte ; seules 3 écoles du quart inférieur brut sont nettement au-dessus de leur attendu, et 1 du quart supérieur nettement en dessous. Les 44 % de changement de quart sont surtout des glissements d'un cran près des bornes (5,3 % sautent deux quarts). « Vrai, mais » ou « Pas toujours » serait plus juste, ou une question reformulée (« Le taux de réussite suffit-il à juger une auto-école ? »).
- **Chiffre plus parlant possible** : « 32 % des écoles du meilleur quart au taux brut n'y sont plus à contexte égal », ou « 1 782 écoles s'écartent nettement de leur attendu, dans un sens ou dans l'autre (22 %) ». À noter : le département seul (sans la commune) fait déjà changer 37 % des écoles de quart ; le rétrécissement bayésien n'ajoute presque rien (43,6 % sans lui).
- **Incohérence carte / dossier** : la carte donne « de 36 % en Guadeloupe à 73 % en Haute-Loire », le dossier « 51 % → 73 %, de Paris à la Haute-Loire ». Le maximum exclut la Lozère (79,9 %, 10 écoles) sans le dire : préciser « parmi les départements d'au moins 20 écoles » ou choisir une seule paire.
- **« du département de l'examen »** : le département est celui de l'école, pas celui où le candidat passe l'examen (inconnu). Et les 25 % sont une part de variance entre écoles, que le dossier attribue aussi à la commune et au public, pas seulement aux examinateurs.
- **« à département égal, une commune dix fois plus peuplée »** : c'est aussi à diplômés, âge, propriétaires et IPS égaux ; « à département et profil social égaux » serait exact.
- **Période des taux inconnue** : la carte date le fichier (19/02/2026) mais pas la période d'examens. Le dossier le dit ; la carte non. Écrire le producteur pour obtenir la période (et l'ajouter à la nomenclature) consoliderait le dossier.
- **Nomenclature du producteur fragile** : colonnes non documentées (`aue_aac_flag`, `aue_cs_flag`, `aue_enligne_flag`, `optionnel_*`, accessibilité), colonnes documentées absentes (`*_nombre_formateurs`), deux colonnes « nombre » qui contiennent des taux. Le sens de `aue_aac_flag` et `aue_cs_flag` est déduit : le levier « conduite supervisée proposée, -2,3 points » repose sur cette déduction.
- **Le levier « école associative »** (-8,9 points) mêle sans doute un public différent (insertion, publics aidés) : le dossier le présente comme levier, la carte n'en dit rien ; le relire avec la même prudence que les écoles en ligne.
- **Commentaire du script périmé** sur le revenu (série 2014) : le revenu Filosofi 2023 est dans l'Atlas ; `docs/millesimes_20261030.md` cite d'ailleurs le dossier Auto-écoles parmi les utilisateurs de Filosofi, ce qui est inexact.
- **Brevet** : sessions 2019 et 2021 seulement, public et privé mélangés, indicateur secondaire (corrélation +0,23) ; mise à jour notée « à faire » dans `docs/millesimes_20261030.md`.
- **Exemple nommé** : le dossier nomme une école en exemple positif ; la carte n'en nomme aucune, c'est cohérent avec la règle « jamais d'exemple négatif nommé ».
