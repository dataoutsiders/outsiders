# 1. Riches et pauvres vivent-ils séparés ?
> Carte `segregation` · Pas partout · dossier `/segregation` · fiche préparée le 30/10/2026

## Ce qu'affiche la carte

- **Bandeau** : « Niveau de vie » ; unité « Villes ».
- **Question** : Riches et pauvres vivent-ils séparés ?
- **Verdict** : Pas partout (`pasPartout`).
- **Chiffre** : `× 1,6`.
- **Libellé** : « dans la ville type, le niveau de vie de ses îlots les plus aisés rapporté à celui des plus modestes ».
- **Texte** : « L'écart varie beaucoup d'une ville à l'autre : la page classe les 997 villes de plus de 10 000 habitants de la plus séparée à la plus mélangée, un classement relatif et non un seuil absolu. Paris figure à la fois parmi les villes dont les quartiers diffèrent le plus et parmi celles où chaque quartier (IRIS, environ 2 000 habitants) mêle le plus des revenus très différents. »
- **Source citée** : « Insee, FiLoSoFi 2021 (carreaux de 200 m et IRIS) ». Le lien mène à https://www.insee.fr/fr/statistiques/8735243, la page « Revenus, pauvreté et niveau de vie en 2021 - Données carroyées ».
- **Bouton** : « Voir l'analyse nationale », vers `/segregation`.

## Ce que dit le dossier

Page `frontend/src/pages/segregation/Segregation.jsx`.

- **En-tête** : la séparation « varie énormément ». Et « contre l'intuition, les grandes villes mélangent souvent plus, à l'échelle de la rue, que bien des petites villes proprement zonées ».
- **Trois chiffres nationaux, calculés dans le navigateur à partir de `villes.json`** :
  - **34 %** des villes sont « fracturées ». La page précise que c'est le tiers où les quartiers sont le plus à part, donc un classement relatif.
  - **× 1,6** entre quartiers : dans la ville type, les carreaux de 200 m les plus aisés (10 % du haut) ont un niveau de vie 1,6 fois celui des plus modestes (10 % du bas).
  - **× 3,8 contre × 3,0** dans un quartier : rapport D9/D1 médian des IRIS, en grande ville (200 000 habitants et plus, **11 villes**) contre petite ville (moins de 30 000 habitants, **720 villes**). Conclusion de la page : « Les grandes villes mélangent plus ».
- **Lecture territoriale** (IRIS agrégés par département, bascule Régions / Départements) : écart entre quartiers en rang national. En tête : Ain (99), Paris (98), Hauts-de-Seine (97), Oise (96), Yvelines (95), Val-de-Marne (94). En queue : Landes, Hautes-Alpes, Vendée, Lot. La page signale que les zones frontalières (Pays de Gex, Bâle) ressortent surestimées.
- **Explorateur** : nuage de points à axes configurables (`MixiteScatter`), filtrable par région ou département, avec les villes « outsiders ».
- **Classement** : les 15 villes les plus « fracturées » et les 15 plus « homogènes », triées par écart entre quartiers.
- **Fiche par ville** (`?ville=<code>`) :
  - **Niveau de vie médian**, avec une étiquette de « Très aisée » à « Très modeste » par rapport à une médiane nationale de 22 040 €.
  - **Deux jauges** : « Mélange dans les quartiers » et « Écart entre quartiers ».
  - **Composition des quartiers** : part des habitants dans des carreaux mixtes, homogènes aisés ou homogènes pauvres.
  - **Carte des carreaux**.
  - **Bloc « Et l'école ? »** : dispersion de l'IPS des collèges comparée à la séparation résidentielle, et écart public / privé.
  - **Tri par âge** : dissimilarité jeunes / seniors.
- **Méthode** : les carreaux à moins de 11 ménages, imputés par l'Insee, sont exclus du calcul des revenus. L'IRIS ne couvre que les communes de 5 000 habitants et plus.

## D'où viennent les chiffres

```
Insee, Filosofi 2021 carreaux 200 m ──(API Koumoul, 1 requête par ville)──> python/tools/_cache_segregation/<code>.json
Insee, Filosofi 2021 IRIS (DISP)    ──(téléchargement zip)───────────────> python/tools/_cache_segregation/iris_filosofi.zip
atlas/communes-vecteurs.json (liste et population des communes > 10 000 hab., RP 2023)
showcases/etablissements.tsv (IPS des collèges, produit par build_ecole.py)
atlas/territoires-index.json (noms des départements)
        └──> python/tools/build_segregation.py
               ├─> frontend/public/data/segregation/villes.json (997 villes, index léger)
               ├─> frontend/public/data/segregation/<code>.json (fiche + carreaux)
               ├─> frontend/public/data/segregation/departements.json (98 départements)
               └─> frontend/public/data/segregation/colleges-evitement.json
                      └──> Segregation.jsx (/segregation) et Home.jsx (carte)
```

**Rattachement des chiffres de la carte**

| Élément de la carte | Calcul | Valeur retrouvée |
|---|---|---|
| × 1,6 | Pour chaque ville, `revenu.p90_p10` = P90 / P10 du niveau de vie moyen des carreaux non imputés (`ind_snv_avg`), pondérés par leurs habitants (`ind`) : fonction `wquantile` de `compute_city`. La page prend la médiane de ces 997 rapports (`medContrast`). | 1,6 (de 1,21 à 2,56 ; 1er décile 1,39, 9e décile 1,88) |
| 997 villes | Communes de plus de 10 000 habitants de `communes-vecteurs.json`, sans les arrondissements de Paris, Lyon et Marseille, avec au moins 5 carreaux non imputés | 997. Sur 1 044 candidates, 47 manquent : Guadeloupe et Guyane (pas de carreaux), et des communes nouvelles créées après 2020 (le code commune des carreaux est en géographie 2020) |
| « de la plus séparée à la plus mélangée » | Tri par `revenu.separation`, rang centile de `sep_cv` = coefficient de variation des médianes d'IRIS (`DISP_MED21`) de la ville | Tri par séparation entre IRIS, pas par mélange |
| Paris parmi les plus séparées | `separation` = 99 (`sep_cv` 0,277, 864 IRIS) | Exact |
| Paris parmi les plus mélangées dans le quartier | `melange_interne` = 99 (médiane des `DISP_RD21` de ses IRIS = 5,3) | Exact |
| Fracturées 34 % (page) | `band(separation) == 'haut'`, soit un rang de 66 ou plus : un tiers des villes par construction | 341 sur 997 |
| × 3,8 contre × 3,0 (page) | Médiane de `interne_rd` des villes de 200 000 habitants et plus, contre celles de moins de 30 000 | 3,8 (11 villes) ; 3,0 (720 villes) |

**À retenir : la carte cite une mesure (× 1,6, carreaux) et parle d'un classement fondé sur une autre (dispersion des médianes d'IRIS).** Les deux sont liées : la corrélation entre `p90_p10` et le rang de séparation est de 0,71. Elles ne se confondent pas : Paris est au 99e rang de séparation avec un `p90_p10` de 2,14, loin du maximum de 2,56. Dans la fiche ville, la jauge « Écart entre quartiers » affiche la valeur `× p90_p10` (carreaux) avec la longueur et la couleur du rang `separation` (IRIS).

## Les jeux de données

### Jeu 1. Insee, Filosofi 2021, données carroyées à 200 m (via Koumoul)

- **Producteur** : Insee, dispositif Filosofi (sources DGFiP, Cnaf, Cnav, CCMSA). Réexposé par Koumoul (`data-fair`, jeu `filosofi-carreaux-200m`, 2 324 577 lignes, données mises à jour le 04/03/2026).
- **Intitulé** : « Données au carreau de 200 m (y compris données imputées) », revenus de 2021.
- **Millésime utilisé** : 2021, d'après `docs/millesimes_20261030.md` (le cache du 04/07/2026 est en 2021). Dernier publié : 2021, paru le 12/02/2026. Attention : la fiche Koumoul pointe encore vers la page Insee du millésime 2019 (7655475), alors que sa description parle bien des revenus de 2021.
- **Pages** :
  - Insee, présentation : https://www.insee.fr/fr/statistiques/8735243
  - Insee, fichiers 200 m : https://www.insee.fr/fr/statistiques/8735162
  - Koumoul : https://opendata.koumoul.com/datasets/filosofi-carreaux-200m
- **Téléchargement direct** :
  - Insee : https://www.insee.fr/fr/statistiques/fichier/8735162/Filosofi2021_carreaux_200m_csv.zip (existent aussi `_gpkg.zip` et `_shp.zip`)
  - API Koumoul utilisée : `https://opendata.koumoul.com/data-fair/api/v1/datasets/filosofi-carreaux-200m/lines?qs=lcog_geo:(<code>)&select=...`
- **Fichiers locaux** : `python/tools/_cache_segregation/<code commune>.json`, un fichier par ville (1 017 fichiers).
- **Géographie** : carreaux de 200 m (grille Inspire, projection LAEA). Couverture : métropole, Martinique et La Réunion.
- **Champ** : ménages fiscaux. Un carreau de moins de 11 ménages a des valeurs imputées (`i_est_200`).

Colonnes du jeu (dictionnaire de la fiche Koumoul, qui reprend celui de l'Insee) :

| colonne | sens | utilisée ? |
|---|---|---|
| idcar_200m | identifiant Inspire du carreau de 200 m | oui (demandée, non exploitée) |
| idcar_1km | carreau de 1 km d'appartenance | non |
| idcar_nat | carreau de niveau naturel d'appartenance | non |
| i_est_200 | carreau imputé (moins de 11 ménages) | oui : carreaux exclus du calcul des revenus (29 % des carreaux d'une ville en médiane, jusqu'à 92 %) |
| i_est_1km | carreau de 1 km imputé | non |
| lcog_geo | code de la ou des communes du carreau (géographie 2020, triées par surface d'intersection) | oui : sélection des carreaux d'une ville |
| ind | nombre d'individus | oui : poids des quantiles, population couverte, composition |
| men | nombre de ménages | oui : taux de pauvreté, composition des quartiers |
| men_pauv | nombre de ménages pauvres | oui : taux de pauvreté de la ville ; carreau « aisé » si moins de 10 % de ménages pauvres, « pauvre » à partir de 40 % |
| men_1ind | ménages d'une personne | non |
| men_5ind | ménages de 5 personnes ou plus | non |
| men_prop | ménages propriétaires | non |
| men_fmp | ménages monoparentaux | non |
| ind_snv | somme des niveaux de vie winsorisés | non (on lit la moyenne calculée par Koumoul) |
| men_surf | somme des surfaces des logements | non |
| men_coll | ménages en logement collectif | non |
| men_mais | ménages en maison | non |
| log_av45 | logements construits avant 1945 | non |
| log_45_70 | logements construits de 1945 à 1969 | non |
| log_70_90 | logements construits de 1970 à 1989 | non |
| log_ap90 | logements construits depuis 1990 | non |
| log_inc | logements à date de construction inconnue | non |
| log_soc | logements sociaux | non |
| ind_0_3, ind_4_5, ind_6_10, ind_11_17 | individus de 0 à 17 ans, en 4 tranches | oui : groupe « jeunes » du tri par âge |
| ind_18_24, ind_25_39, ind_40_54, ind_55_64 | individus de 18 à 64 ans, en 4 tranches | oui : groupe « actifs » (entropie) |
| ind_65_79, ind_80p | individus de 65 ans ou plus, en 2 tranches | oui : groupe « seniors » |
| ind_inc | individus d'âge inconnu | non |
| ind_snv_avg (Koumoul) | niveau de vie moyen winsorisé des individus (ind_snv / ind) | oui : P10, P50, P90, Gini spatial, carte, évitement scolaire |
| men_pauv_pourc (Koumoul) | part de ménages pauvres | non (recalculée) |
| men_surf_avg (Koumoul) | surface moyenne des logements | non |
| men_prop_pourc (Koumoul) | part de propriétaires | non |
| men_fmp_pourc (Koumoul) | part de familles monoparentales | non |
| ind_0_17_pourc, ind_18_64_pourc, ind_65p_pourc (Koumoul) | parts de jeunes, d'adultes, de seniors | non |
| _geopoint (Koumoul) | centroïde « lat,lon » | oui : carte, rayon de 0,7 km autour des collèges |
| geometry, _geoshape, _geocorners, _id, _i, _rand (Koumoul) | géométrie et champs techniques | non |

### Jeu 2. Insee, Filosofi 2021 à l'IRIS, revenus disponibles (DISP)

- **Intitulé** : « Revenus, pauvreté et niveau de vie en 2021 (Iris) », base `BASE_TD_FILO_IRIS_2021_DISP`.
- **Millésime utilisé** : 2021. Dernier publié : 2021. Filosofi 2023 n'est diffusé que de la commune à la région, et il n'y a pas de millésime 2022.
- **Page** : https://www.insee.fr/fr/statistiques/8229323
- **Téléchargement direct** : https://www.insee.fr/fr/statistiques/fichier/8229323/BASE_TD_FILO_IRIS_2021_DISP_CSV.zip (version xlsx : `..._DISP_XSLX.zip`).
- **Fichier local** : `python/tools/_cache_segregation/iris_filosofi.zip`, avec `BASE_TD_FILO_IRIS_2021_DISP.csv` et `meta_BASE_TD_FILO_IRIS_2021_DISP.csv`.
- **Géographie** : IRIS (environ 2 000 habitants), 16 025 lignes dans 1 887 communes. Valeurs numériques pour 14 490 IRIS. Les autres sont marqués `so`, `ns` (non significatif) ou `nd` (non diffusé). En pratique, l'IRIS ne couvre que les communes de 5 000 habitants et plus.

| colonne | sens (dictionnaire `meta_...csv`) | utilisée ? |
|---|---|---|
| IRIS | code IRIS (commune ou arrondissement + numéro) | oui : rattachement à la commune |
| DISP_TP6021 | taux de pauvreté au seuil de 60 % (%) | non |
| DISP_INCERT21 | incertitude sur le taux de pauvreté (1 : IRIS de 1 000 à moins de 10 000 ménages, à l'unité ; 2 : 500 à moins de 1 000 ménages, à l'entier impair le plus proche) | non |
| DISP_Q121, DISP_MED21, DISP_Q321 | 1er quartile, médiane, 3e quartile du niveau de vie (€) | MED oui : `sep_cv` (séparation), `iris_p90p10`, niveau départemental ; Q1 et Q3 non |
| DISP_EQ21 | écart interquartile rapporté à la médiane | non |
| DISP_D121 à DISP_D921 (sauf D5) | déciles 1 à 9 du niveau de vie (€) | non |
| DISP_RD21 | rapport interdécile D9/D1 | oui : mélange interne (`interne_rd`) |
| DISP_S80S2021 | rapport S80/S20 | non |
| DISP_GI21 | indice de Gini | non |
| DISP_PACT21 | part des revenus d'activité (%) | non |
| DISP_PTSA21 | dont salaires et traitements | non |
| DISP_PCHO21 | dont indemnités de chômage | non |
| DISP_PBEN21 | dont revenus des activités non salariées | non |
| DISP_PPEN21 | part des pensions, retraites et rentes | non |
| DISP_PPAT21 | part des revenus du patrimoine et autres | non |
| DISP_PPSOC21 | part de l'ensemble des prestations sociales | non |
| DISP_PPFAM21 | dont prestations familiales | non |
| DISP_PPMINI21 | dont minima sociaux | non |
| DISP_PPLOGT21 | dont prestations logement | non |
| DISP_PIMPOT21 | part des impôts (négative) | non |
| DISP_NOTE21 | note de précaution (0 : rien ; 1 : nombre de ménages en forte évolution, plus ou moins 10 % ; 5 : données non diffusées pour anomalies) | non (165 IRIS en note 1, 82 en note 5) |

### Jeu 3. Insee, Filosofi 2021 à l'IRIS, revenus déclarés (DEC), non utilisé

- **Téléchargement** : https://www.insee.fr/fr/statistiques/fichier/8229323/BASE_TD_FILO_IRIS_2021_DEC_CSV.zip (même page). Mêmes 16 025 IRIS.
- **Colonnes** :
  - DEC_PIMP21 : part des ménages fiscaux imposés ;
  - DEC_TP6021 : taux de bas revenus déclarés ;
  - DEC_INCERT21 ;
  - quartiles, médiane et déciles DEC_Q1 à DEC_D9 ;
  - DEC_EQ21, DEC_RD21, DEC_S80S2021, DEC_GI21 ;
  - parts de revenus DEC_PACT, PTSA, PCHO, PBEN, PPEN, PAUT ;
  - DEC_NOTE21.
- **Intérêt** : la distribution avant redistribution. On peut y mesurer combien les prestations réduisent l'écart entre quartiers.

### Jeux secondaires (produits par d'autres scripts du site)

- **`atlas/communes-vecteurs.json`** : liste des communes avec la population RP 2023 (Insee, DS_RP_POPULATION_PRINC) et 14 indicateurs standardisés. Seuls `code`, `nom` et `pop` servent ici, pour choisir les villes de plus de 10 000 habitants.
- **`showcases/etablissements.tsv`** : IPS des collèges publics et privés (Éducation nationale, rentrée 2025), produit par `build_ecole.py`. Il sert au bloc « Et l'école ? » et à `colleges-evitement.json`. Le collège est rattaché à la ville par son nom de commune normalisé (rapprochement approximatif). 524 villes sur 997 n'ont pas de bloc école (moins de 3 collèges).

## Ce qu'on n'exploite pas encore

- **Logements sociaux par carreau (`log_soc`)**, **propriétaires (`men_prop`)**, **logement collectif contre maison (`men_coll`, `men_mais`)**. On pourrait dire si les carreaux pauvres sont des carreaux HLM, et si la séparation tient au statut d'occupation. Cela ferait le lien avec la carte HLM de l'accueil.
- **Familles monoparentales (`men_fmp`) et ménages d'une personne (`men_1ind`)**. La séparation résidentielle des familles monoparentales est un angle peu traité.
- **Âge du bâti (`log_av45` à `log_ap90`)** : il distinguerait les centres anciens, les grands ensembles 1945-1975 et le périurbain récent. Ce serait une explication « urbanistique » des écarts entre quartiers.
- **Déciles complets de l'IRIS (D1 à D9)** :
  - le D1 de l'IRIS le plus pauvre comparé au D9 de l'IRIS le plus riche donnerait un écart « extrême » parlant ;
  - on pourrait aussi décomposer l'inégalité de la ville en une part entre quartiers et une part dans les quartiers (Theil approché). Ce serait une vraie mesure de ségrégation, au lieu de deux rangs juxtaposés.
- **Taux de pauvreté de l'IRIS (`DISP_TP6021`)** : part des pauvres de la ville qui vivent dans les IRIS les plus pauvres (concentration de la pauvreté), ou indice de dissimilarité pauvres / non-pauvres. C'est la mesure classique de la ségrégation, plus lisible qu'un coefficient de variation.
- **Composition du revenu de l'IRIS (`DISP_PPSOC21`, `DISP_PPMINI21`, `DISP_PPAT21`)** : quartiers de prestations contre quartiers de patrimoine. Les revenus du patrimoine séparent souvent plus que les salaires.
- **Revenus déclarés (fichier DEC)** : séparation avant et après redistribution.
- **Note de précaution (`DISP_NOTE21`)** : à utiliser au moins pour écarter les 82 IRIS en note 5 (anomalies). Le script ne les exclut pas explicitement, mais leurs valeurs sont vides, ce qui revient au même.
- **Dans le calcul actuel** : pondérer `sep_cv` par la population des IRIS. Le calcul est aujourd'hui non pondéré, et l'IRIS n'a pas de nombre de ménages dans ce fichier : il faudrait le croiser avec le RP à l'IRIS.

## Autres sources possibles

- **Insee, fichier complet des carreaux 2021** (https://www.insee.fr/fr/statistiques/8735162). Mêmes variables que Koumoul, sans dépendre d'un tiers. Il contient tous les carreaux, y compris ceux à cheval sur deux communes. Dans le jeu Koumoul, un carreau partagé entre deux communes est rattaché aux deux (`lcog_geo` liste plusieurs codes).
- **Insee, bases infracommunales (IRIS) du recensement**, par exemple :
  - « Population en 2021 » (`base-ic-evol-struct-pop-2021`, https://www.insee.fr/fr/statistiques/8268806) ;
  - « Logement en 2021 » (`base-ic-logement-2021`, https://www.insee.fr/fr/statistiques/8268838) ;
  - (millésime 2022 éventuellement paru, à vérifier).
  - **Apport** : catégories socioprofessionnelles, immigrés, diplômes, HLM par IRIS. On en tirerait une ségrégation par catégorie sociale (dissimilarité cadres / ouvriers) indépendante du revenu, et comparable à la littérature.
- **Contours des IRIS (IGN)**, https://www.data.gouv.fr/datasets/contours-iris-r-2 (mis à jour le 30/04/2026). Ils permettraient une carte par IRIS au lieu des points de carreaux, et des indices spatiaux (voisinage).
- **Quartiers prioritaires de la politique de la ville 2024 (ANCT, SIG Ville, https://sig.ville.gouv.fr)**. Republications vérifiées sur data.gouv.fr, par exemple https://www.data.gouv.fr/datasets/quartiers-prioritaires-politique-de-la-ville-anct-26avril2024. Ils permettraient de dire quelle part des habitants pauvres d'une ville vit en QPV.
- **DGFiP, impôt sur le revenu par collectivité territoriale (IRCOM)**, https://www.data.gouv.fr/datasets/limpot-sur-le-revenu-par-collectivite-territoriale-ircom (mis à jour le 26/05/2026). Échelle communale seulement : il n'enrichit pas l'infracommunal, mais donne une série annuelle récente.
- **DVF (prix au m² par section cadastrale ou IRIS)** : séparation par les prix, plus récente que Filosofi 2021.

## Points de relecture

1. **Deux mesures différentes sous un même mot.** Le × 1,6 (carreaux, P90/P10) n'est pas la mesure qui classe les villes (dispersion des médianes d'IRIS). Ni la carte ni la page ne le disent. La fiche ville affiche la valeur de l'une avec la couleur de l'autre. Il faudrait aligner : soit classer sur le × carreaux, soit afficher sur la carte un chiffre tiré de l'IRIS.
2. **« De la plus séparée à la plus mélangée »** confond les deux axes du dossier : le classement porte sur la séparation entre quartiers, le « mélange » est l'autre axe. Dans la page, la colonne de droite s'intitule « Les plus homogènes » alors que la typologie réserve « Homogène » à une autre case (peu séparée et peu mélangée). Proposition : « de la plus séparée à celle dont les quartiers se ressemblent le plus ».
3. **« Îlots »** : le mot désigne en statistique publique les îlots IRIS. Ici ce sont des carreaux de 200 m, et le P90 / P10 est pondéré par les habitants (10 % des habitants, pas 10 % des carreaux). Proposition : « les carreaux de 200 m où vivent les 10 % d'habitants les plus aisés ».
4. **× 1,6 paraît faible** au lecteur, parce qu'il compare des moyennes de carreaux (lissées). Chiffres plus parlants possibles, tirés des fichiers en cache :
   - dans les 997 villes, **62 % des habitants vivent dans un carreau mixte, 29 % dans un carreau quasi sans pauvres (moins de 10 % de ménages pauvres), 9 % dans un carreau à forte pauvreté (40 % ou plus)**. Moyenne pondérée par la population couverte, recalculée le 30/10 ; les seuils sont ceux du site ;
   - ou le rapport des médianes entre l'IRIS le plus aisé et le plus modeste (`iris_p90p10`, 2,2 à Paris).
5. **Robustesse de la séparation dans les petites villes.**
   - La médiane est de 7 IRIS par ville, et 204 villes en ont moins de 5 (minimum : 2 pour calculer `sep_cv`).
   - La ville classée **première** (« la plus fracturée ») a 8 IRIS. Plusieurs villes du haut du classement en ont entre 6 et 10.
   - Un coefficient de variation sur 6 valeurs est très instable. Prévoir un seuil (par exemple 10 IRIS) ou un intervalle.
6. **Grandes contre petites villes** : le × 3,8 repose sur 11 villes de 200 000 habitants et plus. En outre, l'IRIS est plus peuplé et plus hétérogène dans les grandes villes : une part de l'écart peut tenir au découpage. « À l'échelle de la rue » reste dans l'en-tête de la page, alors que la mesure est l'IRIS (environ 2 000 habitants).
7. **Imputation** : les carreaux imputés sont exclus (29 % des carreaux en médiane, plus de la moitié dans 231 villes). Le P10 et le P90 portent donc sur les zones denses. Dans les petites villes, le × carreaux décrit surtout le centre.
8. **Couverture** :
   - pas de Guadeloupe, de Guyane ni de Mayotte (pas de carreaux), et des communes nouvelles postérieures à 2020 manquent (47 villes de plus de 10 000 habitants absentes) ;
   - la lecture territoriale ne couvre que les communes de 5 000 habitants et plus, alors que la page dit « tous les IRIS ». Exemple : l'Ain, premier département, compte 71 IRIS, surtout dans le Pays de Gex.
9. **Millésimes** : carreaux 2021 et IRIS 2021, cohérents entre eux. La médiane nationale de référence (22 040 €) est en 2021, alors que le reste du site est en Filosofi 2023 : à préciser si la fiche ville est lue à côté de l'Atlas.
10. **Verdict « Pas partout »** : défendable. Mais la question appelle un constat national (oui, en partie), et le chiffre ne dit pas à partir de quand une ville est « séparée ». Le texte le reconnaît (« classement relatif »). Un repère absolu serait plus utile, comme la part des pauvres vivant dans un carreau à forte pauvreté.
