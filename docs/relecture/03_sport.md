# 3. Le foot, sport des quartiers ?
> Carte `sport` · verdict « Vrai, mais » (`vraiMais`) · dossier `/terrains/sport` · fiche préparée le 30/10/2026

## Ce qu'affiche la carte

- **Rubrique** : Sport · unité « Quartiers » · couleur `#F59E0B`.
- **Question** : « Le foot, sport des quartiers ? »
- **Verdict** : Vrai, mais.
- **Chiffre** : **35 %**
- **Libellé** : « des licences des quartiers prioritaires sont du foot, contre 15 % dans le reste de la commune ».
- **Texte** : « Par habitant, le foot n'y est que 1,4 fois plus fréquent : sa place tient surtout à la moindre pratique en club des autres sports. Et les terrains y sont rares : on compte près de trois fois plus de licenciés résidents par terrain de quartier qu'ailleurs. »
- **Source citée** : « INJEP, licences et clubs 2023 ; Data ES », lien vers la page data.gouv.fr du jeu INJEP seulement (pas de lien Data ES).
- **Bouton** : « Les idées reçues sur le sport » vers `/terrains/sport`.
- La carte est aussi reprise sur la page Presse (`Presse.jsx`, liste `RESULTATS`) et son image de partage (`/terrains/sport`).

## Ce que dit le dossier

Page `frontend/src/pages/terrains/TerrainSport.jsx`, titre « Le sport, miroir des inégalités ? », millésime 2023.

- **Chapeau** : 13 millions de licences en club (hors sport scolaire), comptées au domicile des licenciés.
- **Trois chiffres en tête** : 103 contre 180 licences pour 1 000 habitants (quartiers prioritaires contre reste de la même commune) ; 35,4 % des licences des quartiers sont du football contre 14,8 % ; « × 2,9 licenciés par terrain de foot dans les quartiers : des terrains saturés ».
- **Le foot partout, ou presque** : carte des départements (licences pour 1 000 habitants, fédérations scolaires exclues) ; le football est premier dans 95 départements sur 100 ; liste des exceptions (ski, tennis, rugby) ; 12 « sports signatures » des départements (indice de spécialisation, fédérations unisport, au moins 20 000 licences nationales et 500 dans le département).
- **Dans les quartiers** : 569 communes, 3,4 millions d'habitants des quartiers ; filles et femmes 31,9 contre 66,9 ; garçons et hommes 71,5 contre 112,7 ; le quartier fait mieux que le reste de sa commune dans 1,6 % des communes ; barres « combien de fois plus ou moins en quartier » pour 16 fédérations unisport (football 1,39 ; lutte et boxe au-dessus de 1 ; golf 0,10, voile 0,15, badminton 0,24, équitation 0,27, tennis 0,28).
- **Trois idées reçues** : « Le foot, c'est le sport des quartiers » (nuance) ; « Les filles des quartiers arrêtent plus tôt » (vrai : 37 % des licences gardées entre 10-14 et 15-19 ans contre 45 % ; garçons 53 % dans les deux cas) ; « Les enfants des milieux aisés arrêtent vers 15 ans » (faux, lecture par commune, licences et population 2018).
- **Riches et pauvres** : de 127 licences pour 1 000 habitants dans les 10 % de communes les plus modestes à 246 au 9e décile (228 au 10e) ; sports des communes aisées (ski, voile, golf, tennis...) et des communes modestes (lutte, boxe, football).
- **Pas de clubs, ou pas de demande ?** : tableau équipements / clubs actifs / licences, quartier contre reste de la commune ; trois encadrés (tennis, natation, judo : l'écart de licences suit l'écart d'offre ; football : « c'est l'inverse de pas de demande » ; sports de gymnase : la salle est là, les licences non) ; « avec ou sans club dans le quartier » (test 3) ; « quand un club arrive » (test 4, fragile).
- **Dans le temps** : licences base 100 en 2013 et part des femmes (football 4,9 % en 2013, 10,2 % en 2023 ; rugby 5,1 % puis 13,0 %).
- **Encadré « L'élite : qui accède au haut niveau ? »** : indice de diversité des noms des internationaux nés en France (football, basket, rugby à XV, délégation de Paris 2024), en fourchette par rapport à leur génération ; internationaux nés à Paris et petite couronne et en outre-mer rapportés à l'attendu d'après les licenciés de 10 à 19 ans (licences 2013). Agrégats seulement, rien sous 30 noms, aucun classement de départements.
- **Méthode et limites** : licence n'est pas pratique ; règle des fédérations multisports (13,1 % des licences hors scolaires, comptées dans les totaux, jamais dans les comparaisons par sport ; « football » = la seule FFF) ; quartier n'est pas une origine ; quartiers en géographie 2024, population des quartiers 2020 et des communes 2021 ; équipements 2025-2026.

## D'où viennent les chiffres

Chaîne : data.gouv.fr (INJEP, Data ES, ANCT, Insee) -> `python/data/sport/` (téléchargements à la main, environ 2,5 Go) -> `python/tools/explore_sport_injep.py` puis `python/tools/explore_sport_offre.py` (tables `python/data/sport/sorties/*.csv`) -> `python/tools/build_showcase_sport.py` -> `frontend/public/data/showcases/sport.json` -> `TerrainSport.jsx`. Les chiffres de la carte sont écrits en dur dans `Home.jsx` (tableau `QUESTIONS`), recopiés du JSON. Ordre de relance : `docs/DEPLOIEMENT.md`, ligne 82.

| Chiffre de la carte | Calcul | Table intermédiaire | Clé du JSON |
|---|---|---|---|
| **35 %** (35,4) et **15 %** (14,8) | `qpv_vs_hz()` : licences 2023 géocodées (`Statut géo` = 1), parties QPV et hors QPV (`HZ`) des communes qui ont les deux, hors fédérations scolaires (6xx) et hors fédérations réparties au seul département (406, 409, 411). Part = licences FFF (code 111) / **toutes** les licences de la zone, **fédérations multisports 4xx et 5xx comprises** au dénominateur. | `c_qpv_vs_horsqpv_federations_2023.csv`, colonnes `part_Q`, `part_H` | `sports_qpv[Football].part_qpv`, `part_hors` |
| **1,4 fois** (1,39) | Taux pour 1 000 habitants sur les **569 communes** dont tous les QPV sont mono-communaux : 35,9 (QPV) contre 25,8 (reste). Population des QPV : Insee `pop_QPV24.xlsx` (RP 2020) ; population du reste = `P21_POP` (RP 2021) moins population des QPV. | même table, `taux_Q_pour_1000`, `taux_H_pour_1000`, `rapport_taux_Q_sur_H` | `sports_qpv[Football].rapport` |
| « moindre pratique en club des autres sports » | 103,4 contre 179,7 licences pour 1 000 habitants, toutes fédérations hors scolaires, mêmes 569 communes. 35,4 / 14,8 = 2,4 = 1,39 (foot plus fréquent) x 1,74 (moins de licences au total). | `c_qpv_resume_2023.csv` | `qpv.taux_qpv`, `qpv.taux_hors` |
| **près de trois fois** (210 / 73 = 2,9) | `explore_sport_offre.py`, étape A : licences FFF 2023 des 1 048 QPV 2024 mono-communaux rapportées aux 578 « Terrain de football » et « Terrain mixte » de Data ES situés **dans le contour** de ces QPV ; reste de la commune : 5 201 terrains. Équipements datés après 2023 retirés, non datés gardés. | `h_qpv_equipements_licences_2023.csv`, colonnes `licences_par_equip_qpv`, `licences_par_equip_hors` | `offre[Football].lic_par_equip_qpv`, `lic_par_equip_hors` |

Remarques sur la chaîne :
- Le 35 % et le 1,4 ne portent pas exactement sur le même champ : la part est calculée sur toutes les communes ayant une partie QPV et une partie hors QPV (561 526 licences en QPV), le taux sur les 569 communes où la population est connue (3,39 millions d'habitants des QPV sur 6,0 millions en géographie 2024). Écart sans effet visible (tennis : 4,2 % en part, 4,1 % en taux rapporté au total), mais à savoir.
- La règle multisports joue ici : au dénominateur, les multisports pèsent 9,7 % des licences en QPV et 12,7 % hors QPV (EPGV, sports pour tous, ASPTT surtout hors QPV). Calculée parmi les seules fédérations unisport, la part du foot serait 39 % contre 17 % (calcul de relecture sur la même table) : la carte est donc plutôt prudente.

## Les jeux de données

### Licences sportives géocodées (INJEP-MEDES, géocodage Insee), millésime 2023

- **Intitulé exact** : « Données géocodées issues du recensement des licences et clubs auprès des fédérations sportives agréées par le ministère chargé des sports ».
- **Producteur** : INJEP, mission des études, de l'observation et des statistiques (MEDES) ; géocodage, indicatrices de zonage et correction des codes communes par l'Insee. Licence ouverte, mise à jour annuelle.
- **Millésime utilisé** : 2023 (saison 2022-2023 ou année civile 2023 selon la fédération), fichier du 29/12/2025 ; aussi 2013 à 2022 pour les séries, 2018 pour l'âge par décile de revenu, 2019 à 2022 pour les tests 2 et 4. **Dernier disponible** : 2023 géocodé ; le total 2024 par fédération existe sur le site de l'INJEP, pas encore géocodé (attendu fin décembre 2026 d'après `docs/millesimes_20261030.md`).
- **Page officielle** : https://www.data.gouv.fr/datasets/donnees-geocodees-issues-du-recensement-des-licences-et-clubs-aupres-des-federations-sportives-agreees-par-le-ministere-charge-des-sports
- **Téléchargement direct** : https://static.data.gouv.fr/resources/donnees-geocodees-issues-du-recensement-des-licences-et-clubs-aupres-des-federations-sportives-agreees-par-le-ministere-charge-des-sports/20251229-163107/lic-data-2023.csv (les autres millésimes sont listés dans `python/data/sport/dataset_metadata.json`).
- **Fichier local** : `python/data/sport/lic-data-2023.csv` (256 Mo, UTF-8 avec BOM, séparateur `;`, 1 014 746 lignes).
- **Géographie** : commune (code commune de l'année N+1, soit 2024 pour le millésime 2023 ; arrondissements à Paris, Lyon, Marseille) x zone QPV (`CSZ` commune sans QPV, `HZ` partie hors QPV d'une commune à QPV, `QN...` QPV 2024, `NR` non réparti). France hors Mayotte. Une ligne par commune x zone x fédération.
- **Dictionnaire** : `python/data/sport/licences-dictionnaire-des-variables.xlsx` (onglet « Méta-données 2019_2023 »).

| colonne | sens | utilisée ? |
|---|---|---|
| `Code Commune` | code commune (géographie N+1) | oui : jointure population, revenu, communes à QPV |
| `Commune` | libellé officiel | non |
| `Code QPV` | `CSZ`, `HZ`, `NR - Non réparti`, `QPxxxxxx` (QPV 2015, millésimes 2019-2022), `QNxxxxxx` (QPV 2024, depuis 2023) | oui : séparer quartier et reste de la commune |
| `Nom QPV` | libellé officiel du QPV | non |
| `Département` | code du département | oui : carte départementale, signatures |
| `Région` | libellé de la région | non |
| `Statut géo` | 1 adresse géocodée ; 2 hors champ (Mayotte, Monaco, COM, étranger) ; 3 non réparti | oui : on ne garde que 1 (part hors champ et non répartis décrite) |
| `Code` | code de la fédération (liste plus bas) | oui : règle 1xx-2xx (unisport), 4xx-5xx (multisports), 6xx (scolaires, exclus) |
| `Fédération` | nom de la fédération | oui : libellés |
| `F - 1 à 4 ans` ... `F - 80 à 99 ans` (16 colonnes) puis `F - NR` | licences féminines par tranche d'âge (1-4, 5-9, 10-14, 15-19, 20-24, 25-29, 30-34, 35-39, 40-44, 45-49, 50-54, 55-59, 60-64, 65-69, 70-74, 75-79, 80-99, âge non renseigné) | oui pour le dossier : part des femmes, décrochage 10-14 / 15-19 ans ; **non pour la carte** (tous âges, deux sexes confondus) |
| `H - 1 à 4 ans` ... `H - 80 à 99 ans` puis `H - NR` | mêmes tranches, licences masculines | idem |
| `Total` | nombre total de licences annuelles | oui : tous les calculs de la carte |

Soit 9 colonnes d'identification, 34 colonnes âge x sexe (17 tranches x 2 sexes), 2 colonnes « âge non renseigné » et `Total` : 46 colonnes. Pas de colonne de population depuis 2019, pas de sexe inconnu.

**Anciens formats (utilisés pour les séries et l'âge 2018)** : `lic-data-2016/2017/2018.csv` et `Licences_2013/2014/2015.csv`, maille commune sans QPV. Le millésime 2018 (dictionnaire, onglet « Méta-données 2018 ») a 74 colonnes : `code_commune`, `libelle`, `region`, `fed_2018`, `nom_fed` ; licences `l_2018` et par tranches larges `l_0_4_2018` ... `l_75_2018` (0-4, 5-9, 10-14, 15-19, 20-29, 30-44, 45-59, 60-74, 75 et plus), puis les mêmes pour les femmes (`l_f_...`) et les hommes (`l_h_...`) ; **`l_qp_2018`, `l_qp_f_2018`, `l_qp_h_2018`** (licences en quartier prioritaire, total et par sexe ; le dictionnaire inverse les libellés femmes et hommes) ; et la **population communale 2017** par mêmes tranches et sexe (`pop_2017`, `pop_0_4_2017` ... `popf_...`, `poph_...`). Utilisé : licences et population par âge et sexe (abandon par décile de revenu). Non utilisé : `l_qp_*` 2018.

**Codes et intitulés des fédérations (liste 2023, `liste-federations.xlsx` ; licences 2023 et part de femmes entre parenthèses, d'après `sorties/a_federations_2019_2023.csv`)**

*Famille 1xx, unisport olympiques (38 fédérations, 9,65 millions de licences ; comparées sport par sport)* : 101 FF d'Athlétisme (307 k, 47 % F) ; 102 FF d'Aviron (45 k) ; 103 FF de Badminton (202 k) ; 105 FF de Basketball (594 k, 34 % F) ; 106 FF de Boxe (65 k) ; 107 FF de Canoë-Kayak et Sports de Pagaie (38 k) ; 108 FF de Cyclisme (108 k) ; 109 FF d'Équitation (675 k, 85 % F) ; 110 FF d'Escrime (54 k) ; **111 FF de Football (2 216 k, 10 % F)** ; 112 FF des Sports de Glace (29 k) ; 113 FF de Gymnastique (324 k, 84 % F) ; 114 FF d'Haltérophilie, Musculation (21 k) ; 115 FF de Handball (532 k) ; 116 FF de Hockey (17 k) ; 117 FF de Judo, Jujitsu, Kendo et DA (529 k) ; 118 FF de Lutte (28 k) ; 119 FF de Natation (402 k) ; 120 FF de Pentathlon Moderne (3 k) ; 121 FF de Ski (95 k) ; 122 FF de Taekwondo et DA (50 k) ; 123 FF de Tennis (1 107 k, 30 % F) ; 124 FF de Tennis de Table (177 k) ; 125 FF de Tir (256 k) ; 126 FF de Tir à l'Arc (74 k) ; 127 FF de Triathlon et Disciplines Enchaînées (61 k) ; 128 FF de Voile (312 k) ; 129 FF de Volley (148 k) ; 131 FF de Hockey sur Glace (23 k) ; 132 FF de Golf (445 k) ; 133 FF de Rugby (375 k, 13 % F) ; 135 FF de la Montagne et de l'Escalade (115 k) ; 136 FF de Roller et Skateboard (69 k) ; 137 FF de Surf (15 k) ; 138 FF de Baseball, Softball (13 k) ; 139 FF de Danse (88 k) ; 140 FF de Football Américain (19 k) ; 141 FF de Squash (19 k).

*Famille 2xx, unisport non olympiques (54 fédérations, 1,92 million ; comparées sport par sport)* : 201 Aéromodélisme ; 202 FF Aéronautique ; 203 Aérostation ; 204 Aïkido, Aïkibudo et Affinitaires ; 205 Aïkido et Budo ; 206 Sport Automobile ; 207 Jeu de Balle au Tambourin ; 208 Ballon au Poing ; 209 Ball-Trap ; 210 Billard ; 211 Sport Boules ; 212 Savate, Boxe Française et DA (54 k) ; 213 Bowling et Sport de Quilles ; 214 Char à Voile ; 215 Course Camarguaise ; 216 Course Landaise ; 217 Course d'Orientation ; 218 Cyclotourisme (107 k) ; 220 Échecs (68 k) ; 221 Études et Sports Sous-Marins (133 k) ; 224 Hélicoptère ; 226 Javelot Tir sur Cible ; 227 Jeu de Paume ; 228 Joute et Sauvetage Nautique ; **229 Karaté et DA (244 k)** ; 231 Longue Paume ; 233 Motocyclisme (67 k) ; 234 Motonautique ; 237 Parachutisme ; 241 Pelote Basque ; 242 Pétanque et Jeu Provençal (282 k) ; 243 Planeur Ultraléger Motorisé ; 244 Pulka et Traîneau à Chiens ; 245 Randonnée Pédestre (231 k) ; 248 Rugby à XIII ; 249 Sauvetage et Secourisme ; 250 Ski Nautique et Wakeboard ; 251 Spéléologie ; 254 Arts Énergétiques et Martiaux Chinois (adresse du club en 2019-2021) ; 255 Sports de Traîneau, Ski VTT Joëring et Canicross ; 256 Twirling Bâton ; 257 Vol en Planeur ; 258 Vol Libre ; 260 Polo ; **261 Kick Boxing, Muay Thaï et DA (60 k)** ; 263 Double Dutch ; 264 Flying Disc ; 265 Pêche Sportive en Apnée ; 266 FF de Force ; 267 Pêches Sportives ; 268 Boxe Américaine et DA ; 269 Voitures Radio Commandées ; 270 Sports et Loisirs Canins ; 271 Clubs Alpins et de Montagne (103 k).

*Famille 4xx, multisports (18 fédérations avec licences, 1,67 million ; dans les totaux seulement)* : 402 FF d'Éducation Physique et de Gymnastique Volontaire (412 k, 91 % F) ; 403 FF Sports pour Tous (140 k) ; 404 FF de la Retraite Sportive (88 k) ; 405 FF du Sport Travailliste ; 406 F des Clubs de la Défense (135 k, réparti au département seulement) ; 407 F Nationale du Sport en Milieu Rural ; 408 F Sportive et Culturelle de France (138 k) ; 409 FF Maccabi (département seulement) ; **410 F Sportive et Gymnique du Travail, FSGT (169 k)** ; 411 F Sportive de la Police Nationale (département seulement) ; **413 UFOLEP (300 k)** ; 415 FF Omnisports des Personnels de l'Éducation Nationale ; 417 Union Nationale Sportive Léo Lagrange ; 418 FF du Sport d'Entreprise ; 420 F Sportive des ASPTT (126 k) ; 422 FF des Clubs Omnisports ; 424 UCPA Sport Loisirs ; 425 UCPA Sport Vacances. Sans licences en 2023 : 421 FF des Sports Populaires, 423 F Nationale des Offices Municipaux des Sports, 426 F Sportive LGBT+.

*Famille 5xx, handisport et sport adapté (77 600 licences ; dans les totaux seulement)* : 501 FF Handisport ; 503 FF du Sport Adapté.

*Famille 6xx, scolaires et universitaires (3,22 millions ; exclues partout)* : 601 FF du Sport Universitaire ; 602 UGSEL (enseignement catholique, 1 134 k) ; 603 Union Nationale des Clubs Universitaires ; 604 UNSS (1 161 k, adresse du club) ; 605 USEP (768 k, adresse du club).

### Clubs sportifs géocodés (INJEP-MEDES, géocodage Insee), millésime 2023

- Même jeu et même page que les licences. **Téléchargement direct** : https://static.data.gouv.fr/resources/donnees-geocodees-issues-du-recensement-des-licences-et-clubs-aupres-des-federations-sportives-agreees-par-le-ministere-charge-des-sports/20251229-163249/clubs-data-2023.csv
- **Fichier local** : `python/data/sport/clubs-data-2023.csv` (121 700 lignes) ; aussi 2019 à 2022 (test 4). Dictionnaire : `clubs-dictionnaire-des-variables.xlsx`.
- **Géographie** : commune x zone QPV, à l'**adresse du club** (souvent le siège).

| colonne | sens | utilisée ? |
|---|---|---|
| `Code Commune`, `Commune`, `Code QPV`, `Nom QPV`, `Département`, `Région`, `Statut géo`, `Code`, `Fédération` | comme pour les licences | oui (commune, QPV, fédération) |
| `Clubs_actifs` | clubs (associations affiliées) ayant au moins une licence annuelle (2023 seulement) | non séparément (agrégé dans `Total_actifs`) |
| `EPA_actifs` | établissements professionnels agréés (privés ou commerciaux, par exemple centres équestres) actifs | non séparément |
| `Total_actifs` | clubs + EPA actifs | oui : tests 3 et densité de clubs du tableau « offre » (pas la carte) |
| `Clubs` | clubs, actifs ou non | non |
| `EPA` | EPA, actifs ou non | non |
| `Total` | clubs + EPA, actifs ou non | oui : test 4 (2019-2022, pas de distinction active) |

### Data ES, équipements sportifs (ministère chargé des Sports), état du 29/10/2026

- **Intitulé exact** : « Recensement des équipements sportifs, espaces et sites de pratiques » (Data ES). Mise à jour quotidienne ; plus de 330 000 lieux de pratique accessibles au public.
- **Page officielle** : https://www.data.gouv.fr/datasets/recensement-des-equipements-sportifs-espaces-et-sites-de-pratiques et https://equipements.sports.gouv.fr/
- **Téléchargement direct** : https://equipements.sports.gouv.fr/api/explore/v2.1/catalog/datasets/data-es-equipement/exports/csv (équipements) ; https://equipements.sports.gouv.fr/api/explore/v2.1/catalog/datasets/data-es-installation/exports/csv (installations). Ressources non téléchargées : « Data ES - Activités » (`.../data-es-activite/exports/csv`, 575 160 lignes), « Data ES - Complet », archives « Fiches équipements » et « Fiches installations » du 1er trimestre 2020 (https://static.data.gouv.fr/resources/recensement-des-equipements-sportifs-espaces-et-sites-de-pratiques/20210121-111044/2020-equipements.zip et `.../20210121-105104/2020-installations.zip`), guide méthodologique de l'enquêteur.
- **Fichiers locaux** : `python/data/sport/equipements/data-es-equipement.csv` (334 342 équipements, 182 Mo) et `data-es-installation.csv` (152 307 installations).
- **Millésime** : stock 2025-2026 (pas d'historique ; les fiches ont été migrées le 31/03/2025), appliqué aux licences 2023.
- **Géographie** : point (WGS84) par équipement ; code commune par l'installation.
- **Sens** : libellés et descriptions de l'API du producteur (`/api/explore/v2.1/catalog/datasets/data-es-equipement`).

Équipements (74 colonnes) :

| colonne | sens | utilisée ? |
|---|---|---|
| `installation_numero` | identifiant de l'installation (lieu à une adresse, un ou plusieurs équipements) | oui : jointure pour le code commune |
| `numero` | identifiant de l'équipement | non (comptage) |
| `nom` | nom usuel de l'équipement | non |
| `famille`, `type`, `code` | famille (29), type (185) et code du type | oui : correspondance type vers fédération ; football = « Terrain de football » + « Terrain mixte » |
| `coordonnees`, `coordonnees_y`, `coordonnees_x` | coordonnées WGS84 ; latitude ; longitude | oui (`_y`, `_x`) : point dans le contour du QPV, distances |
| `mise_en_service_date` | année d'ouverture au public (62,5 % renseignée, années rondes surreprésentées) | oui : retrait des équipements postérieurs à 2023, test 2 |
| `mise_en_service_periode` | tranche de mise en service (« ne pas prendre en compte » selon le producteur) | non |
| `is_date_mise_en_service_known` | date de mise en service connue (Oui / Non), 2 % renseigné | décrit seulement |
| `creation_dt`, `maj_date`, `maj_lien`, `date_creation_metier` | création et modification de la fiche (dates antérieures au 31/03/2025 à ignorer) | non (décrits) |
| `proprietaire_principal_nom`, `proprietaire_principal_type`, `proprietaire_secondaire_type`, `autres_proprietaires` | propriétaire du bâti, du sol (commune 90 % des terrains de foot, EPCI, établissement scolaire, association, privé commercial...) | non |
| `gestionnaire_type`, `co_gestionnaire_type`, `gestion_dsp` | gestionnaire, co-gestionnaire, délégation de service public | non |
| `arrete_ouverture`, `erp_type`, `erp_cat` | arrêté d'ouverture au public, type et catégorie d'établissement recevant du public | non |
| `homologation_date`, `homologation_periode`, `is_date_homologation_known` | homologation préfectorale (grandes enceintes) | non |
| `derniers_travaux_date`, `derniers_travaux_periode`, `derniers_travaux_type`, `is_date_derniers_travaux_known` | année et nature des derniers gros travaux | non |
| `chauffage_energie` | énergie de chauffage | non |
| `aire_longueur`, `aire_largeur`, `aire_hauteur`, `aire_surface` | dimensions de l'aire d'évolution (m, m²) | non |
| `aire_eclairage` | éclairage artificiel (usage en soirée) | non |
| `aire_couloirs_nb` | nombre de subdivisions (couloirs, pistes, terrains) | non |
| `aire_nature_sol` | type de sol (gazon naturel, synthétique, stabilisé...) | non |
| `nature` | couvert, découvert, site naturel... | non |
| `places_tibune_nb`, `vestiaires_sportifs_nb`, `vestiaires_arbitres_nb`, `douches`, `sanitaires` | tribunes, vestiaires, douches, sanitaires | non |
| `acces_handi_mobilite`, `acces_handi_sensoriel` | accessibilité handicap | non |
| `is_pdesi_pdipr` | inscription au plan départemental des espaces, sites et itinéraires | non |
| `bassin_longueur`, `bassin_largeur`, `bassin_surface`, `bassin_profondeur_min`, `bassin_profondeur_max` | caractéristiques des bassins | non |
| `piste_longueur` | longueur de piste | non |
| `sae_hauteur`, `sae_surface`, `sae_couloirs_nb` | structures artificielles d'escalade | non |
| `pas_de_tir_type` | type de pas de tir | non |
| `website`, `observations` | site internet, remarques | non |
| `utilisateurs` | usagers : clubs sportifs, ligues, comités, fédérations ; scolaires, universités ; individuels, familles ; autres associations | non |
| `acces_libre` | accessible à tous en permanence, non clos (44 % des terrains de football, 61 % des city-stades) | non |
| `ouverture_saisonniere` | utilisé une partie de l'année seulement | non |
| `equip_nb` | numéro d'incrémentation technique | non |
| `rnb_id` | identifiant du Référentiel national des bâtiments | non |
| `autres_locaux`, `amenagements_confort` | club-house, locaux annexes ; sauna, hammam... | non |
| `activites` | activités pratiquées sur l'équipement (détail dans la ressource « Activités ») | non |
| `zone_dsi`, `etat`, `aot_cot`, `annee_fin_aot` | zonage technique, état de la fiche (validé, en cours), autorisation d'occupation temporaire et son échéance | non |

Installations (46 colonnes) : `numero` (utilisée, jointure) ; `insee` (utilisée, code commune) ; non utilisées : `creation_date`, `maj_date`, `maj_lien`, `nom`, `siret`, `adresse`, `commune`, `cp`, `coordonnees`, `install_particuliere` (établissement scolaire, complexe sportif, piscine, base de loisirs...), `acces_handi`, **`uai`** (code de l'établissement scolaire), `acces_transp_commun` (transport en commun à moins de 10 minutes à pied), `observations`, `moderation_maj_date`, `moderation_creation_date`, **`hs`** (hors service : 320 installations, non filtrées), `install_nb`, `epci_code`, `epci_nom`, `dep_code`, `dep_nom`, `reg_code`, `reg_nom`, `code_bdv`, `lib_bdv` (bassin de vie), `arr_code`, `arr_name`, `dens_niveau`, `dens_lib` (grille de densité Insee), `dep_code_filled`, `aca_nom`, `zrr_simp`, `bloc_adresse`, `com_name`, `adresse_new`, `commune_new`, `cp_new`, `insee_new`, `date_creation_metier`, `etat`, `reg_slug`, `dep_slug`, `com_slug`.

Activités (12 colonnes, non téléchargée) : `aps_name` (activité), `aps_discipline`, `aps_code`, `aps_niveau` (niveau maximal pratiqué), `equip_numero` (lien vers l'équipement), `aps_pratique`, `creation_dt`, `maj_date`, `maj_lien`, `date_creation_metier`, `id_unique_activite`, `etat`.

### Contours et liste des quartiers prioritaires (ANCT), géographie 2024 et 2015

- **Intitulé** : « Quartiers prioritaires de la politique de la ville (QPV) », Agence nationale de la cohésion des territoires.
- **Page officielle** : https://www.data.gouv.fr/datasets/quartiers-prioritaires-de-la-politique-de-la-ville-qpv
- **Téléchargement direct** : https://static.data.gouv.fr/resources/quartiers-prioritaires-de-la-politique-de-la-ville-qpv/20260115-204323/qpv-2024-geojson.zip ; liste 2024 : https://static.data.gouv.fr/resources/quartiers-prioritaires-de-la-politique-de-la-ville-qpv/20260721-095036/listeqp2024-cog2025.csv ; contours 2015 : https://static.data.gouv.fr/resources/quartiers-prioritaires-de-la-politique-de-la-ville-qpv/20180110-144945/qp-politiquedelaville-shp.zip ; **correspondance QP 2015 / QP 2024 (non utilisée)** : https://static.data.gouv.fr/resources/quartiers-prioritaires-de-la-politique-de-la-ville-qpv/20260116-105522/liste-correspondance-qp2024-qp2015.csv
- **Fichiers locaux** : `python/data/sport/qpv_contours/GEOJSON/QP2024_France_Hexagonale_Outre_Mer_WGS84.geojson` (1 584 quartiers), `QP_METROPOLEOUTREMER_WGS84_EPSG4326.*` (1 514 quartiers 2015), `ref/listeqp2024-cog2025.csv`, `ref/liste-1514qp2015.xlsx`.

| colonne | sens | utilisée ? |
|---|---|---|
| `fid` | numéro technique | non |
| `code_qp` | code du QPV 2024 (`QN...`) | oui : jointure avec les licences |
| `lib_qp` | nom du quartier | non |
| `insee_reg`, `lib_reg`, `insee_dep`, `lib_dep` | région, département | non |
| `insee_com`, `lib_com` | commune principale | oui (contrôle mono-communal) |
| `siren_epci`, `lib_epci` | intercommunalité | non |
| géométrie | contour du quartier | oui : équipements dans le contour, distances |
| 2015 : `CODE_QP`, `NOM_QP`, `COMMUNE_QP` | code, nom, communes du QPV 2015 | oui : tests 2 et 4 |

### Population municipale des quartiers prioritaires 2024 (Insee)

- **Intitulé** : « Populations municipales des quartiers prioritaires 2024 », France entière, mis en ligne le 10/07/2025, source recensement de la population (population au 1er janvier 2020).
- **Page** : Insee (fichier `pop_QPV24.xlsx`, lien de téléchargement non inscrit dans le code) ; à retrouver sur insee.fr, rubrique quartiers de la politique de la ville.
- **Fichier local** : `python/data/sport/ref/pop_QPV24.xlsx` (1 609 quartiers, 6,02 millions d'habitants ; 1 449 mono-communaux, 4,80 millions).

| colonne | sens | utilisée ? |
|---|---|---|
| `codeQPV` | code du QPV 2024 | oui |
| `libQPV` | nom | non |
| `listeDepcom` | liste des communes du QPV | oui : sélection des QPV mono-communaux |
| `ListeLibDepcom` | noms des communes | non |
| `listeEPCI2022` | intercommunalités de rattachement | non |
| `listeDep` | départements | non |
| `codeReg` | région | non |
| `codeUU2020` | unité urbaine 2020 | non |
| `popMuniQPV` | population municipale du quartier | oui : dénominateur des taux en QPV |

Pas de population par âge ni par sexe dans ce fichier : c'est la raison pour laquelle la carte ne peut pas corriger l'effet d'âge.

### Population communale 2021 (Insee, base « évolution et structure de la population »)

- **Intitulé** : « Évolution et structure de la population en 2021 », base communale du recensement (`base-cc-evol-struct-pop-2021`). **Dernier disponible** : RP 2023 (déjà utilisé ailleurs par le site via `rp2023.py`, mise à jour du dossier Sport « à faire » d'après `docs/millesimes_20261030.md`).
- **Fichier local** : `python/data/sport/ref/base-cc-evol-struct-pop-2021_csv.zip`, décompressé dans `ref/pop2021/` (34 963 communes et arrondissements, 321 colonnes ; métadonnées `meta_base-cc-evol-struct-pop-2021.CSV`). Lien de téléchargement non inscrit dans le code.
- **Logique de nommage** : préfixe `P` (exploitation principale) ou `C` (complémentaire) + année (`21`, `15`, `10`) + variable.

| famille de colonnes | sens | utilisée ? |
|---|---|---|
| `CODGEO` | code commune ou arrondissement | oui |
| `P21_POP` | population 2021 | oui : dénominateur (reste de la commune = commune moins QPV), déciles de revenu |
| `P21_POP0014` ... `P21_POP90P`, `P21_POPH`, `P21_H0014` ... `P21_H65P`, `P21_POPF`, `P21_F0014` ... `P21_F65P` | population par grande tranche d'âge (0-14, 15-29, 30-44, 45-59, 60-74, 75-89, 90 et plus ; 0-19, 20-64, 65 et plus) et par sexe | non |
| `P21_POP01P`, `P21_POP01P_IRAN1` ... `IRAN7`, `P21_POP0114_IRAN2P` ... `P21_POP55P_IRAN3P` | lieu de résidence un an auparavant (même logement, autre logement de la commune, autre commune...) par âge | non |
| `C21_POP15P`, `C21_POP15P_CS1` ... `CS8`, idem `C21_H15P_*`, `C21_F15P_*`, `C21_POP1524_*`, `C21_POP2554_*`, `C21_POP55P_*` | population de 15 ans ou plus par catégorie socioprofessionnelle (agriculteurs, artisans, cadres, professions intermédiaires, employés, ouvriers, retraités, autres inactifs), par sexe et âge | non |
| `P15_*`, `C15_*` | mêmes variables en 2015 | non |
| `P10_*`, `C10_*` | 2010 : population 15-64 ans, actifs, actifs occupés, chômeurs, inactifs, étudiants, retraités, emplois au lieu de travail par secteur et catégorie | non |

### Revenus des communes, Filosofi 2023 (Insee)

- **Intitulé** : « Revenus et pauvreté des ménages en 2023 », base communale (fichier `FILOSOFI_CC_csv.zip`), paru le 06/08/2026, à jour.
- **Page** : https://www.insee.fr/fr/statistiques/8984752 ; **téléchargement direct** : https://www.insee.fr/fr/statistiques/fichier/8984752/FILOSOFI_CC_csv.zip
- **Fichier local** : `python/tools/_cache_filosofi/DS_FILOSOFI_CC_2023_data.csv` (1 123 173 lignes, format long), lu par `python/tools/revenu_filosofi.py`.
- **Géographie** : `GEO_OBJECT` = COM, ARM, EPCI, DEP, REG, FRANCE, UU2020, AAV2020, BV2022, ZE2020, ARR, OTHER.
- **Colonnes** : `GEO` (code), `GEO_OBJECT` (type de territoire), `FILOSOFI_MEASURE` (mesure), `UNIT_MULT`, `UNIT_MEASURE`, `CONF_STATUS` (secret), `OBS_STATUS`, `TIME_PERIOD`, `OBS_VALUE` (valeur). Utilisées : `GEO`, `GEO_OBJECT`, `FILOSOFI_MEASURE`, `OBS_VALUE`.

| mesure (`FILOSOFI_MEASURE`) | sens | utilisée ? |
|---|---|---|
| `MED_SL` | niveau de vie médian | oui : déciles de revenu des communes, contrôle des tests 1 et 3 (pas la carte) |
| `D1_SL` ... `D9_SL`, `Q1_SL`, `Q3_SL` | déciles et quartiles du niveau de vie | non |
| `IQR_SL`, `IR_D9_D1_SL`, `S80S20_SL`, `GI_SL` | écart interquartile, rapport interdécile, rapport S80/S20, indice de Gini | non |
| `PR_MD60` | taux de pauvreté au seuil de 60 % | non |
| `S_EI_DI`, `S_EI_DI_SAL`, `S_EI_DI_N_SAL`, `S_EI_DI_UNE` | part des revenus d'activité, salaires, revenus non salariaux, indemnités de chômage dans le revenu disponible | non |
| `S_RET_PEN_DI`, `S_INC_ASS_DI` | part des pensions et retraites, des revenus du patrimoine | non |
| `S_SOC_BEN_DI`, `S_SOC_BEN_DI_FAM_BEN`, `S_SOC_BEN_DI_HOU_BEN`, `S_SOC_BEN_DI_MIN_SOC` | part des prestations sociales, familiales, logement, minima sociaux | non |
| `S_DIR_TAX_DI` | part des impôts directs | non |

### Estimations de population par département, sexe et âge (Insee)

- **Intitulé** : « Estimations de population par département, sexe et âge quinquennal, 1975-2023 » (`estim-pop-dep-sexe-aq-1975-2023.xls`), converti en `ref/pop_dep_sexe_aq_2019_2023.csv`.
- **Colonnes du fichier converti** : `annee`, `dep`, `sexe` (Ensemble, Femmes, Hommes), `age` (tranches quinquennales, 0 à 4 ans ... 95 ans et plus), `pop`. Utilisées : toutes, pour la carte départementale (licences pour 1 000 habitants) et les courbes nationales par âge ; aucune pour la carte de l'accueil.

### Encadré « L'élite » (rappel, sans détail)

Sources : Wikidata et Wikipédia en français (appartenance aux équipes de France, date et lieu de naissance), Insee fichier des noms de famille (référentiel de l'indice), Insee recensement 2023 (part des immigrés par âge et sexe, `ref/immigres/`), licences INJEP 2013 (vivier de 10 à 19 ans). Sorties publiées : `elite_noms` (fourchette par équipe et période de naissance, nombre de noms reconnus) et `elite_zones` (deux zones, rapport observé / attendu). Rien de cet encadré ne sert à la carte de l'accueil ; l'exploration nominative n'est pas reprise ici.

## Ce qu'on n'exploite pas encore

- **Âge et sexe des licences en QPV pour la carte elle-même** : les colonnes `H - ...` et `F - ...` permettent de dire de qui l'on parle. Calcul de relecture sur `c_qpv_vs_horsqpv_federations_2023.csv` : en QPV, **47 % des licences masculines sont à la FFF, contre 21 %** dans le reste de la commune ; chez les femmes 10 % contre 4 %. « Sport des garçons des quartiers » est plus juste que « sport des quartiers ». Par tranche d'âge (5-14 ans), le chiffre serait encore plus parlant.
- **Série 2019-2023 en géographie QPV** : les millésimes 2019 à 2022 donnent les licences par QPV 2015 ; avec la table de correspondance QP 2015 / QP 2024 de l'ANCT (non utilisée), on pourrait dire si la part du foot en quartier monte ou baisse.
- **`l_qp_*` du millésime 2018** : un total de licences en quartier (avec sexe), qui prolongerait la série d'une année.
- **`Clubs_actifs` et `EPA_actifs` séparés** : l'offre commerciale (EPA) pèse dans l'équitation, le golf, la forme ; la séparer dirait si le déficit des quartiers tient aux structures privées.
- **Types Data ES écartés de la correspondance football** : 25 634 « Multisports/City-stades » et 300 « Terrain de foot 5x5 » ne sont pas comptés comme terrains de football. Or le city-stade est le terrain de foot de proximité typique des quartiers ; le « près de trois fois plus de licenciés par terrain » en dépend directement.
- **`acces_libre`, `utilisateurs`, `proprietaire_principal_type`, `install_particuliere`, `uai`** : distinguer terrains en accès libre, terrains scolaires et terrains de club répondrait mieux à « les terrains y sont rares ».
- **`aire_nature_sol` et `aire_eclairage`** : un terrain synthétique éclairé accueille beaucoup plus de créneaux qu'un terrain en herbe ; la capacité, plus que le nombre, mesure la saturation.
- **`hs` (hors service)** : 320 installations hors service ne sont pas filtrées ; effet probablement faible, à vérifier.
- **Ressource « Activités » de Data ES** : activités déclarées sur chaque équipement (dont le football sur les gymnases et city-stades) ; meilleure correspondance équipement vers sport que la table faite à la main.
- **Archives Data ES du 1er trimestre 2020** : un stock daté, qui comparé au stock 2026 donnerait les ouvertures et fermetures réelles, plus sûres que `mise_en_service_date` (62 % renseignée, années arrondies).
- **Population par âge et catégorie sociale du RP** (`P21_POP0014`, `C21_POP15P_CS*`) : standardiser par âge les comparaisons par revenu, ou ranger les communes par part de cadres plutôt que par revenu médian.
- **Filosofi `PR_MD60` et `D1_SL`** : ranger les communes par taux de pauvreté plutôt que par médiane colle mieux à la notion de quartier prioritaire.

## Autres sources possibles

- **Insee, « Données sur les quartiers 2015 de la politique de la ville »** (https://www.insee.fr/fr/statistiques/2500477, page vérifiée) : indicateurs par QPV 2015, dont population par âge ; permettrait des taux par âge en QPV pour les millésimes 2019-2022. Pour la géographie 2024, le Système d'information géographique de la politique de la ville de l'ANCT (https://sig.ville.gouv.fr/, en ligne) diffuse des indicateurs par quartier ; disponibilité de la population par âge et sexe en géographie 2024 à vérifier. C'est le manque qui empêche de corriger l'effet d'âge du « 1,4 fois ».
- **INJEP, Baromètre national des pratiques sportives** (enquête déclarative, éditions récentes) : pratique hors club, avec diplôme et catégorie sociale de la personne ; seule source pour une lecture individuelle. Site injep.fr en erreur 503 le 30/10/2026.
- **INJEP, recensement des licences 2024** (totaux par fédération, non géocodés) : actualiser les totaux et la série ; même indisponibilité du site ce jour.
- **Ministère chargé des Sports, « Relations géographiques distantes des licences 2013 des fédérations sportives à leur club »** (https://www.data.gouv.fr/datasets/relations-geographiques-distantes-des-licences-2013-des-federations-sportives-a-leur-club) : lien domicile du licencié vers commune du club, mais pour trois fédérations seulement (golf, voile, études et sports sous-marins) ; n'aide pas pour le football.
- **pass Sport, activations journalières 2022 à 2024** (https://www.data.gouv.fr/datasets/pass-sport-activations-journalieres) : âge, genre, organisme de rattachement et date d'activation ; pas de commune ni de fédération, donc d'intérêt limité pour la carte.
- **OpenStreetMap** (objets `leisure=pitch`, `sport=soccer`) : recense aussi les terrains de quartier, city-stades et five que Data ES classe à part ou ignore ; utile pour contrôler le compte des terrains dans les contours des QPV.
- **Agence nationale du sport, plan « 5 000 terrains de sport »** : liste des terrains financés évoquée dans la note d'exploration ; non trouvée sur data.gouv.fr le 30/10/2026 (recherche « terrains de sport » sans résultat national).

## Points de relecture

1. **« sont du foot »** : il s'agit des licences de la seule Fédération française de football (futsal compris, foot loisir FSGT ou UFOLEP exclu). Formulation possible : « des licences sportives des quartiers prioritaires sont des licences de football (FFF) ». La FSGT est implantée dans des communes populaires d'Île-de-France : le foot réel des quartiers est un peu sous-compté.
2. **Chiffre plus parlant** : « près d'une licence masculine sur deux » (47 % contre 21 %) dirait mieux qui joue au foot ; ou mettre en avant 103 contre 180 licences pour 1 000 habitants, qui est le vrai résultat (le foot est surtout ce qui reste).
3. **Effet d'âge absent de la carte** : la jeunesse des quartiers ferait attendre 1,19 fois plus de football ; à âge comparable, le surcroît n'est que d'environ 17 %. Le dossier le dit (« l'âge plus jeune des quartiers en explique une bonne part »), la carte non.
4. **« Les terrains y sont rares »** : dépend du comptage. City-stades et foot à 5 exclus, terrains comptés dans le seul contour des QPV (souvent dessiné serré, les stades sont fréquemment juste en bordure), licenciés comptés à leur domicile. « Près de trois fois plus de licenciés résidents par terrain » est exact sur ces conventions ; « rares » l'est moins. Envisager « on compte deux fois moins de terrains de football par habitant dans le contour des quartiers », plus factuel (0,48).
5. **Dossier pas aligné sur la carte corrigée** : l'encadré « Le foot, c'est le sport des quartiers » écrit encore « Sa place tient surtout à l'absence des autres sports » (formule retirée de la carte le 30/10) ; l'encadré football dit « c'est l'inverse de pas de demande » ; le chiffre de tête dit « des terrains saturés ». Trois formulations qui dépassent les données selon `docs/verification_cartes_accueil.md`.
6. **Champs différents pour 35 % et 1,4** : toutes les communes à QPV ayant licences dans les deux parties pour la part, 569 communes (3,4 millions d'habitants sur 6,0 millions en QPV) pour le taux. Sans effet visible, à mentionner en méthode si l'on cite les deux ensemble.
7. **Populations décalées** : QPV au 1er janvier 2020, communes 2021, licences 2022-2023 ; passage au RP 2023 noté « à faire » dans `docs/millesimes_20261030.md`. Les licences géocodées 2024 sont attendues fin décembre 2026 : la carte sera à revérifier en janvier 2027.
8. **Source de la carte** : le lien ne mène qu'à l'INJEP ; ajouter Data ES (et l'Insee pour la population) si la place le permet.
9. **Encadré « L'élite »** : le texte sur Paris et la petite couronne cite nommément un international (lieu de naissance et commune où il a grandi) pour illustrer l'effet maternité. Cela va contre la règle affichée juste en dessous (« aucun résultat par joueur ») ; une formulation générale suffirait.
10. **Données Data ES** : stock 2025-2026 appliqué aux licences 2023, dates de mise en service fragiles, 320 installations hors service non filtrées ; sans effet sur 35 % et 1,4, possible effet marginal sur le 2,9.
