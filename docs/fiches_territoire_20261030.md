# Fiche territoire : rubrique « Dans nos dossiers », fiches intercommunalité et région (30/10/2026)

Rien n'est déployé. Sauvegardes : chaque fichier de code ou de texte modifié a sa copie `.bak_20261030` à côté (sauf `config/seo.js` et `pages/Home.jsx`, qui en avaient déjà une de ce jour, laissée intacte) ; l'index et les repères nationaux d'avant reconstruction sont dans `_archive/bak_20261030/fiches_territoire/`, hors du dossier publié.

## 1. Ce qui a été fait

1. **Rubrique « Dans nos dossiers »** en bas de chaque fiche (commune, intercommunalité, département, région), à la place des deux liens fixes École et Élus, avec un lien « Tous les dossiers ». Elle ne lit qu'un registre, `frontend/src/config/dossiersTerritoires.js`.
2. **Fiche intercommunalité** : socle des 20 indicateurs (`atlas/epci.json`), atypies par rapport à toutes les intercommunalités ou à celles de taille comparable, jumeau et anti-jumeau parmi les intercommunalités, communes membres (de la plus peuplée à la moins peuplée) avec lien vers leur fiche, rubrique des dossiers.
3. **Fiche région** (13 régions de métropole et 5 d'outre-mer) : socle, atypies par rapport aux autres régions, départements membres, rubrique des dossiers, encadré sur l'origine de chaque valeur.
4. **Navigation** : fil « Fait partie de » (commune vers intercommunalité, département, région ; intercommunalité vers département principal et région ; département vers région) ; recherche étendue aux intercommunalités et aux régions (accueil et `/territoires`) ; pastilles des 18 régions sur `/territoires` sans code ; clic sur une intercommunalité dans l'Atlas (carte et nuage des outsiders) et dans la vue intégrée, qui ouvre désormais sa fiche ; en-tête, `config/seo.js` (description de `/territoires`), Méthodologie (échelles, rubrique), `docs/projet.md`, `docs/DEPLOIEMENT.md`.

## 2. Adressage des niveaux

| Niveau | Adresse | Remarque |
|---|---|---|
| Commune | `/territoires?code=93010` | inchangée |
| Département | `/territoires?code=32` | inchangée |
| Intercommunalité | `/territoires?niveau=epci&code=200054781` | un SIREN de 9 chiffres est aussi reconnu sans `niveau` (`niveauFromCode`) : les liens de l'Atlas restent en `?code=` |
| Région | `/territoires?niveau=region&code=11` | code région Insee ; le paramètre est obligatoire, un code à 2 chiffres sans lui reste un département |

`niveauFromCode(code, niveau)` donne priorité au paramètre explicite ; `ficheHref(niveau, code)` construit les liens. Aucune nouvelle route (`config/seo.js` : seule la description de `/territoires` change). Toutes les URL existantes restent valides (testé).

## 3. Le registre, dossier par dossier

Une échelle n'est déclarée que si la page du dossier montre déjà des résultats à cette échelle ; la précaution affichée est celle du dossier.

| Dossier (fichier lu) | Échelles | Phrase (gabarit) | Lien |
|---|---|---|---|
| Revenus 2014-2021 (`showcases/evolution-revenus.json`, 395 Ko) | commune (5 070 communes de 2 000 hab. et plus, métropole, territoire inchangé ; Paris entier par son anneau « Paris intra-muros ») ; intercommunalité (au moins 2 communes comparées, comme la carte du dossier) | « Dans la hiérarchie des niveaux de vie des communes, X est passée du Ae au Be centile de 2014 à 2021, soit ±N points (contrôle 2023 : Ce) » ; « a peu bougé » sous 2 points, comme le dossier ; avertissement du dossier si le contrôle 2023 va dans l'autre sens. Intercommunalité : évolution moyenne pondérée de la position de ses communes | `/terrains/revenus` (pas de présélection possible par l'URL) |
| Villes, ségrégation (`segregation/villes.json`, 364 Ko ; `segregation/departements.json`, 16 Ko) | commune (997 villes de plus de 10 000 hab.) ; département ; région de métropole | Commune : niveau de vie, « plus aisée que X % des villes », écart entre quartiers, rapport interdécile du quartier type, typologie, IPS des collèges public / privé (bloc « Et l'école ? »). Département : écart entre quartiers, X sur 100 (rang national, donné par le dossier). Région : même calcul que la vue « Régions » du dossier (rangs départementaux pondérés par le nombre d'IRIS) | `/segregation?ville=<code>` (présélection) ; `/segregation` |
| École (`showcases/ecole-ips.json`, 329 Ko) | département | Groupe du cumul des trois étapes (public modeste, entre-soi cumulé, ni l'un ni l'autre) et valeur ajoutée moyenne des lycées | `/terrains/ecole` |
| Élus (`showcases/elus-diversite.json`, 61 Ko) | département seulement | « Parmi les candidats aux élections municipales de 2026, X % portent un nom classé « diversité » (France : 4,4 %) », suivie mot pour mot de la phrase de garde-fou du dossier ; note outre-mer du dossier pour les DOM. Ni rang, ni « plus divers » | `/terrains/elus` |
| Sport (`showcases/sport.json`, 30 Ko) | département | Licences pour 1 000 habitants, sport n° 1, sport « signature » et son indice. Rien de l'encadré « L'élite » | `/terrains/sport` |
| Auto-écoles (extrait `territoires/auto-ecoles-departements.json`, 7 Ko ; le fichier complet pèse 1,2 Mo) | département | Nombre d'écoles et de candidats, taux de réussite moyen et taux national ; précaution « le taux brut mesure d'abord le contexte » | `/terrains/auto-ecoles?dep=<code>` (présélection) |
| Sélectivité (`showcases/selectivite.json`, 25 Ko) | région | Part des licences qui acceptent tous leurs candidats (et France), taux d'accès médian ; précaution sur le taux d'accès | `/terrains/selectivite` |

**Échelles volontairement non reprises** (le dossier ne les montre pas, ou seulement en classement) : Revenus par département (dans le fichier, absent de la page) ; Élus par commune (le dossier ne montre que les 15 extrêmes, un classement) et par intercommunalité (dans le fichier, affiché nulle part) ; Auto-écoles par commune (le dossier montre des écoles, pas un résultat communal) ; Sélectivité par académie (échelle que la fiche n'a pas) ; École par intercommunalité (le fichier alimente le socle de la fiche, pas le dossier).

**Exclusions motivées** (`EXCLUSIONS_TERRITOIRES`, même fichier) : `showcases/ecole-communes.json` (fichier intermédiaire de l'Atlas, lu par aucune page, 3,0 Mo) ; `segregation/colleges-evitement.json` (classement de collèges nommés, pas un résultat par territoire) ; `segregation/<code>.json` (détail cartographique de la fiche ville, ouverte par le lien). Non détectés comme géographiques : `assemblee.json`, `rythmes-scolaires.json`.

**Test** (`src/lib/__tests__/dossiersTerritoires.test.js`, 17 tests) : il échoue si un fichier `public/data/showcases/*.json` ou `public/data/segregation/*.json` contient des données par territoire (clés `communes`, `departements`, `epci`, `regions`, `villes`, `iris` ; listes d'objets à code Insee ; dictionnaires de codes ; fichier d'un seul territoire) sans être dans le registre ou dans les exclusions avec une raison. Il vérifie aussi que chaque fichier lu pèse moins de 1 Mo, que l'extrait Auto-écoles suit le fichier complet, les garde-fous (Élus : département seul, phrase de garde-fou, aucun rang ; Sport : rien de l'élite ; aucun mot de palmarès) et les territoires de contrôle ci-dessous.

## 4. Valeurs régionales

Produites par `python/tools/build_territoires_echelles.py` (`atlas/regions.json`, avec l'origine de chaque valeur, affichée dans la fiche). Contrôle : chaque méthode est d'abord appliquée aux départements et comparée à `atlas/departements.json` ; écart maximal **0,0** pour les 20 indicateurs.

| Indicateur | Valeur régionale | Origine |
|---|---|---|
| Revenu médian | officielle | Insee, Filosofi 2023, lignes `REG` (`MED_SL`). Métropole et La Réunion ; Guadeloupe, Martinique, Guyane, Mayotte non publiées : non affichées |
| Diplômés, logement (5), âges (2), catégories sociales (4) | officielles | Insee, recensement 2023, lignes `REG` des bases déjà utilisées, mêmes séries et mêmes rapports qu'au département. Mayotte absente du RP 2023 : non affichée |
| Natalité | recalculée | naissances domiciliées 2021-2025 des communes de la région / population 2023 de ces communes, comme au département |
| Diversité des candidats | recalculée | noms des candidats 2026 classés « diversité » / noms reconnus, au moins 50, comme au département |
| IPS école, collège, lycée ; valeur ajoutée | recalculées | moyenne des établissements de la région (publics pour l'IPS), même définition qu'au département ; l'Éducation nationale ne publie pas de valeur régionale |
| Prix immobilier | **non affiché** | les statistiques DVF n'ont pas d'échelle région (nation, département, EPCI, commune, section) et une médiane ne se déduit pas de médianes départementales |

Aucune valeur n'est une moyenne de médianes. Les intercommunalités gardent les valeurs de `atlas/epci.json`, déjà produites par la chaîne Atlas (revenu officiel Filosofi par EPCI, recensement et naissances en sommes d'effectifs, IPS en moyenne d'établissements) ; à signaler : le prix et la diversité des candidats y sont des médianes communales (choix antérieur de `build_atlas_epci.py`, non modifié ici).

## 5. Fichiers ajoutés à `frontend/public`, poids, contenu

| Fichier | Poids | Contenu |
|---|---|---|
| `data/atlas/epci-communes.json` | 337 Ko | par SIREN : département principal (le plus peuplé), départements, codes des communes |
| `data/atlas/regions.json` | 9 Ko | 18 régions : code, nom, départements, population, indicateurs, origine de chaque valeur |
| `data/territoires/auto-ecoles-departements.json` | 7 Ko | par département : nom, taux, nombre d'écoles et de candidats |
| `data/atlas/territoires-index.json` (reconstruit) | 1 044 Ko vers 1 130 Ko | + 1 255 intercommunalités `[siren, nom, dép.]` et 18 régions |

`stats-nationales.json` reconstruit à l'identique (octet pour octet). **Aucune donnée nominative** : des codes, des noms de collectivités et des agrégats ; aucun nom de personne, d'établissement ni d'auto-école.

## 6. Contrôles : ce qu'affiche la rubrique

Résultats produits par le registre sur les fichiers publiés (repris en partie dans les tests).

- **Bondy (93010)**. Revenus : « Dans la hiérarchie des niveaux de vie des communes, Bondy a peu bougé de 2014 à 2021 : du 5e au 3e centile (contrôle 2023 : 3e). » (positions 4,5 puis 2,6). Villes : « Ville au niveau de vie « modeste », plus aisée que 5 % des 997 villes étudiées. Entre ses quartiers, les plus aisés ont un niveau de vie 1,5 fois celui des plus modestes ; dans le quartier type, l'écart entre les 10 % du haut et les 10 % du bas est de 3,7. Typologie : contrastée. IPS moyen des collèges : 83 dans le public, 115 dans le privé. » Lien `/segregation?ville=93010`.
- **Paris (75056)**. Revenus : « Paris intra-muros : de 2014 à 2021, la position de ses arrondissements […] a évolué en moyenne de +3,4 points (contrôle 2023 : +3,1 points). » Villes : « très aisée », plus aisée que 97 % des villes, écart entre quartiers 2,1, quartier type 5,3, fracturée, IPS des collèges 115 / 145.
- **Saint-Clar (32370, 1 062 hab.)** : aucun dossier ; la rubrique l'écrit (« Aucun de nos dossiers ne publie de résultat pour ce territoire à cette échelle »). Lectoure (32208, 3 670 hab.) : Revenus, « du 38e au 31e centile, soit −7,1 points (contrôle 2023 : 41e) », avec l'avertissement du dossier (le contrôle va dans l'autre sens).
- **Métropole du Grand Paris (200054781)** : Revenus, « 128 communes comparées, −0,1 point ». Toulouse Métropole : 37 communes, −8,8 points. Fiche : 130 communes membres, Paris en tête, département principal Paris, à cheval sur 6 départements.
- **Gers (32)** : Villes, écart entre quartiers 11 sur 100 (18 IRIS) ; École, entre-soi cumulé, valeur ajoutée −0,4 ; Élus, 1,9 % (France 4,4 %) et phrase de garde-fou ; Sport, « 251,5 licences pour 1 000 habitants en 2023. Sport n° 1 et sport « signature » : rugby (30 licences pour 1 000 hab., 5,4 fois plus pratiqué qu'en moyenne nationale) » ; Auto-écoles, 30 écoles, 2 695 candidats, 71,5 % (France 60,3 %), lien `?dep=32`.
- **Île-de-France (11)** : Villes, 91 sur 100 (3 953 IRIS) ; Sélectivité, « 20 % des 721 formations de licence de la région acceptent tous leurs candidats (France : 33 %) ; taux d'accès médian : 49 % ». Socle : revenu 28 210 €, diplômés 46,7 %, 12,46 millions d'habitants.
- **La Réunion (04)** : Sélectivité seulement (90 % des 31 licences, accès médian 100 %) ; pas de Villes, le dossier regroupe l'outre-mer en une ligne. Socle : revenu 19 110 € (Filosofi publie La Réunion), tous les indicateurs sauf le prix. **Mayotte (06)** : aucun dossier ; socle réduit à l'IPS et à la diversité des candidats (pas de RP 2023 ni de Filosofi).

## 7. Vérification

`npm run build` : réussi (24 images de partage, 24 routes pré-rendues, plan du site). `npx vitest run` : **79 tests** réussis (57 avant ; +17 pour le registre, +5 pour les échelles). Pas de contrôle à l'écran (pas de navigateur) : la relecture visuelle des quatre fiches reste à faire.

## 8. Points à décider

1. **Prix immobilier régional** : absent faute de médiane publiée. Le calculer exigerait les mutations DVF brutes (plusieurs Go) ; à décider.
2. **Sport, fédérations multisports** : le sport « signature » est parfois une fédération (Seine-Saint-Denis : « F Sportive et Gymnique du Travail » ; Haute-Garonne : « Union Nationale Sportive Léo Lagrange »), comme dans le dossier. Écarter les fédérations multisports se ferait dans `build_showcase_sport.py`.
3. **Revenus par l'URL** : le dossier n'accepte pas de commune présélectionnée ; un paramètre `?ville=` dans `TerrainRevenus.jsx` rendrait le lien direct.
4. **Intercommunalités, médianes communales** : prix et diversité des candidats de `atlas/epci.json` sont des médianes de communes (antérieur à ce travail) ; la diversité pourrait être recalculée sur les effectifs, comme pour les régions.
5. **Ordre de la chaîne** : `build_territoires_echelles.py` puis `build_territoires_index.py` sont à relancer après `build_auto_ecoles.py` (noté dans `DEPLOIEMENT.md` ; le test signale un extrait périmé).
