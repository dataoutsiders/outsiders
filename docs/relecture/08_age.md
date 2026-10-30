# 8. Les jeunes ne s'informent plus ?
> Carte `age` · verdict « Faux » (`faux`) · dossier `/explorer/age` · fiche préparée le 30/10/2026

## Ce qu'affiche la carte

- **Rubrique** : Information · unité « Âge » · couleur `#F97316`.
- **Question** : « Les jeunes ne s'informent plus ? »
- **Verdict** : Faux.
- **Chiffre** : **96 %**
- **Libellé** : « des 18-24 ans s'informent au moins une fois par mois, 90 % chaque jour ».
- **Texte** : « Ils ont quitté le journal télévisé, pas l'information : 41 % s'informent chaque jour par la télévision, contre 89 % des 70 ans et plus, et pour 77 % d'entre eux le numérique (réseaux, sites, applis, mais aussi télévision et radio suivies sur écran) est devenu le premier moyen de s'informer. »
- **Source citée** : « Arcom, Les Français et l'information (2024) », lien https://www.arcom.fr/se-documenter/etudes-et-donnees/etudes-bilans-et-rapports-de-larcom/les-francais-et-linformation
- **Bouton** : « Comparer les générations » vers `/explorer/age`.
- Historique : chiffre passé de 77 % à 96 % le 29-30/10/2026 après la vérification (`docs/verification_cartes_accueil.md`, section 7) ; deux indicateurs ajoutés à `age.json` à cette occasion.

## Ce que dit le dossier

`/explorer/age` n'est pas une page écrite à la main : c'est le moteur générique `frontend/src/pages/explorer/UnitView.jsx`, configuré par l'entrée `id: 'age'` de `frontend/src/config/decoupages.js` (lignes 89-116). Deux modes : **tableau de bord** (les 7 tranches d'âge côte à côte, indicateur par indicateur, dégradé de couleur neutre) et **fiche** (`?cat=18-24` : une tranche située parmi les autres).

- **Intro** : « Comment les Français s'informent selon l'âge : le clivage générationnel le plus marqué des données ouvertes (source Arcom 2024). »
- **Note** (`age.json`) : comportements, pas de « bon » ou « mauvais » ; dégradé neutre.
- **Huit indicateurs** en quatre thèmes : « S'informer » (s'informe régulièrement ; s'informe chaque jour), « Mode d'information » (s'informe d'abord en numérique), « Canaux » (chaque jour via la télévision ; chaque jour via les réseaux sociaux), « Plateformes » (TikTok, Instagram, Facebook, parmi les utilisateurs de réseaux sociaux).
- **Sept tranches** : 15-17, 18-24, 25-34, 35-44, 45-59, 60-69, 70 ans et plus.
- Pas de valeur « ensemble des 15 ans et plus » (`references` absent du JSON), pas d'effectifs, pas de marge d'erreur.

Valeurs servies (`frontend/public/data/decoupages/age.json`) :

| tranche | s'informe (mois) | chaque jour | numérique d'abord | TV chaque jour | réseaux chaque jour | TikTok | Instagram | Facebook |
|---|---|---|---|---|---|---|---|---|
| 15-17 | 94,7 | 91,0 | 67,6 | 54,9 | 63,4 | 36,9 | 37,8 | 21,0 |
| 18-24 | 96,1 | 89,8 | 77,4 | 41,2 | 65,9 | 39,7 | 62,8 | 42,7 |
| 25-34 | 98,5 | 94,4 | 71,5 | 53,0 | 69,8 | 19,5 | 40,9 | 58,6 |
| 35-44 | 98,1 | 94,0 | 64,6 | 56,5 | 63,8 | 14,7 | 27,8 | 55,3 |
| 45-59 | 97,7 | 92,8 | 43,0 | 68,5 | 45,5 | 9,7 | 14,7 | 36,1 |
| 60-69 | 96,5 | 94,6 | 26,7 | 77,7 | 31,3 | 4,3 | 11,5 | 29,7 |
| 70 et + | 98,6 | 96,6 | 10,7 | 89,3 | 12,1 | 3,2 | 4,8 | 26,3 |

## D'où viennent les chiffres

Chaîne : data.gouv.fr (Arcom) -> `python/data/francais-information/base-info-arcom.xlsx` (base anonymisée 2024) -> **aucun script de production retrouvé** pour `age.json` (ni dans `python/tools/`, ni dans `docs/DEPLOIEMENT.md`) : les six premiers indicateurs viennent de travaux d'analyse antérieurs (`python/scripts/generate_chapitre_01.py` pour la définition « numérique », `python/scripts/chapitre_01_complement_plateformes.py` pour les plateformes), les deux indicateurs « s'informe » ont été recalculés à la main le 29/10/2026 -> `frontend/public/data/decoupages/age.json` -> `UnitView.jsx`. Chiffres de la carte écrits en dur dans `Home.jsx`. Les définitions ci-dessous ont été recalculées pour cette fiche et retrouvent exactement les valeurs du JSON (pondération `POIDS03`, convertie de la virgule décimale).

| Chiffre de la carte | Calcul | Clé du JSON |
|---|---|---|
| **96 %** | 18-24 ans (`RS2C_RECODE_AG_R` = 2, 283 répondants) dont au moins un des huit modes `NEWS1_R_1` à `NEWS1_R_8` vaut 1 à 4 (plusieurs fois par jour, au moins une fois par jour, par semaine, par mois). Base : toute la tranche. 96,1 %. | `categories[18-24].valeurs.s_informe` |
| **90 %** | Même chose avec 1 ou 2 (au moins une fois par jour). 89,8 %. | `s_informe_jour` |
| **41 %** | `NEWS1_R_2` (télévision en direct ou en replay, quel que soit l'écran) vaut 1 ou 2. 41,2 %. | `via_tv` |
| **89 %** | Même calcul, 70 ans et plus (`RS2C_RECODE_AG_R` = 7, 508 répondants). 89,3 %. | `categories[70+].valeurs.via_tv` |
| **77 %** | Parmi ceux qui ont un mode principal (`NEWS1BIS_R` renseigné), part dont ce mode est numérique : sites ou applis de médias en ligne, moteurs, portails, réseaux sociaux, plateformes vidéo (`NEWS1BIS_R` 5 à 9), **ou** télévision, radio, presse suivies sur smartphone, ordinateur ou tablette (`NEWS1_2B_R` = 2, `NEWS1_1B_R` = 2 ou 3, `NEWS1_3B_R` = 1). Définition de `generate_chapitre_01.py`, variable `BASCULEMENT`. 77,4 %. | `numerique` |

Les trois indicateurs « Plateformes » : `RSINFO_2_LR_R_k` = 1 (s'informe sur ce réseau), rapporté aux répondants ayant répondu pour au moins un réseau (k = 4 TikTok, 2 Instagram, 1 Facebook). « Réseaux chaque jour » : `NEWS1_R_7` vaut 1 ou 2. Le même indicateur « numérique » alimente aussi `milieu-social.json` (par catégorie sociale, `RS4_R`).

## Les jeux de données

### A. Arcom, « Les Français et l'information », 1re édition (base 2024)

- Producteur : Arcom (Autorité de régulation de la communication audiovisuelle et numérique) ; institut indiqué dans la datamap (fichier « VL701 ARCOM-Base finale-data 20240111 »).
- Page data.gouv.fr (jeu « Les Français et l'information, baromètre », qui réunit les deux éditions) : https://www.data.gouv.fr/datasets/les-francais-et-linformation-barometre
- Page Arcom de l'étude : https://www.arcom.fr/se-documenter/etudes-et-donnees/etudes-bilans-et-rapports-de-larcom/les-francais-et-linformation
- Téléchargements directs (édition 2024) :
  - base anonymisée (xlsx) : https://static.data.gouv.fr/resources/etude-sur-les-francais-et-linformation/20240430-162835/les-francais-et-l-information-arcom-2024-base-anonymisee.xlsx (existe aussi en `.txt`) ;
  - datamap : https://static.data.gouv.fr/resources/etude-sur-les-francais-et-linformation/20240426-162303/les-francais-et-l-information-arcom-2024-datamap.xlsx ;
  - guide d'utilisation : https://static.data.gouv.fr/resources/etude-sur-les-francais-et-linformation/20240426-161624/les-francais-et-l-information-guide-d-utilisation-des-donnees.pdf ;
  - questionnaire : https://static.data.gouv.fr/resources/les-francais-et-linformation-2024/20250513-101337/les-francais-et-l-information-questionnaire-vdef.pdf
- Millésime utilisé : terrain fin 2023, redressement du 05/01/2024, rapport publié le 14/03/2024.
- Fichiers locaux : `python/data/francais-information/base-info-arcom.xlsx` (5,3 Mo, **3 346 répondants, 1 076 colonnes**), `datamap-info-arcom.xlsx` (onglets LEVELS, VARIABLES, TEXTS, Précisions méthodologiques), `dictionnaire.json` (212 entrées : titre de chaque question et libellés des modalités, tiré de la datamap ; reconstruit par `python/scripts/build_dictionnaire.py`).
- Géographie : France entière, 15 ans et plus ; 3 010 interrogés en ligne en métropole, 203 en ligne en outre-mer, 133 par téléphone (personnes peu ou pas internautes). Variables géographiques : région en 9 et en 5 zones, territoire d'outre-mer, taille d'agglomération (pas de département ni de commune).
- Deux questionnaires : long (2 949 répondants intéressés par l'information politique et générale) et court (397) ; une grande partie des questions d'opinion n'est posée qu'au questionnaire long.
- Effectifs par tranche d'âge : 15-17 ans 105 ; 18-24 ans 283 ; 25-34 ans 414 ; 35-44 ans 513 ; 45-59 ans 953 ; 60-69 ans 570 ; 70 ans et plus 508.

**Colonnes, par thème.** Les 1 076 colonnes déclinent environ 110 questions : une racine (par exemple `NEWS1_R`) suivie d'un numéro d'item (`_1`, `_2`...) et, souvent, de récapitulatifs (`_R1` « au moins une fois par jour », `_R2` « par semaine », « ST Oui », « Top 1 »...). Sens tiré de `dictionnaire.json` et de la datamap.

**1. Identification, pondération, mode d'enquête**

| variables | ce qu'elles mesurent | utilisée ? |
|---|---|---|
| `RECORD`, `UUID` | identifiants anonymes du répondant | non |
| `CIBLE`, `SOURCE_BASE_R1`, `INTER`, `CONTACT` | cible (métropole, outre-mer), mode (téléphone, en ligne métropole, en ligne outre-mer), variables techniques | non |
| `POIDS03` | poids de redressement du 05/01/2024 | oui : tous les pourcentages |
| `VERSION_QUESTIO_R` | questionnaire long ou court (selon l'intérêt pour l'information générale) | non (à prendre en compte pour les questions d'opinion) |

**2. Profil (signalétique)**

| variables | ce qu'elles mesurent | utilisée ? |
|---|---|---|
| `RS1_R` | genre (homme, femme, non binaire) | non ici (découpage Sexe du site : autre source) |
| `RS2C_RECODE_AG_R` | âge en 7 tranches | oui : les lignes du tableau |
| `RS3_R` | situation professionnelle (actif, chômeur, étudiant, au foyer, retraité...) | non |
| `RS4_R`, `CSPIND_R` | profession en 6 groupes ; CSP+ / CSP- / inactifs | oui pour `milieu-social.json` (numérique par milieu social), non ici |
| `RS5_R` | niveau d'études (10 modalités) | non |
| `UDA9_R`, `UDA5_R`, `DPT_DOM_R`, `CC_R` | région en 9 ou 5 zones, territoire d'outre-mer, taille d'agglomération | non |
| `RS7_R`, `RS14_R` | taille du foyer, revenu mensuel net du foyer en 5 tranches | non |
| `ILLECTRO_R`, `RS15_R`, `FREQ_INTERNET_R` | dernière utilisation d'internet (téléphone), fréquence d'usage d'internet | non |
| `RS16_R_*`, `RS16_R1_*` à `RS16_R3_*` | équipement média (télévision, radio, autoradio, smartphone, ordinateurs, tablette, boîtier, enceinte connectée...) : un, plusieurs, aucun | non |

**3. Intérêt pour l'information et sentiment d'être informé**

| variables | ce qu'elles mesurent | utilisée ? |
|---|---|---|
| `INT1_R` | intérêt global pour l'information (très, assez, peu, pas du tout) | non |
| `INT2_R_1` à `_12`, `INT2_R1_*` à `INT2_R6_*` | intérêt par thème (international, national, local, politique, économie, société, environnement, santé, culture, sport...) | non |
| `INT3_R_*`, `INT3_R1_*` à `INT3_R7` | sentiment d'être bien informé sur les thèmes qui intéressent | non |
| `MOTIV_R_1` à `_14`, `MOTIV_R1`, `MOTIV_R2_*` | motivations pour s'informer (comprendre le monde, se faire une opinion, en discuter, se divertir...), top 3 | non |

**4. Modes, fréquence et supports d'information (cœur des indicateurs du site)**

| variables | ce qu'elles mesurent | utilisée ? |
|---|---|---|
| `NEWS1_R_1` à `_8` | fréquence d'information par mode : radio ou podcasts ; télévision (direct ou replay) ; journal ou magazine ; site ou appli d'un média uniquement en ligne ; moteur de recherche ; portail d'actualité ; réseaux sociaux ; plateformes vidéo (de « plusieurs fois par jour » à « jamais ») | oui : s'informe (mois, jour), télévision chaque jour (`_2`), réseaux chaque jour (`_7`) |
| `NEWS1_R1_*`, `NEWS1_R2_*` | récapitulatifs « au moins une fois par jour », « par semaine » | non (recalculés depuis `NEWS1_R_*`) |
| `NEWS1_1B_R`, `NEWS1_2B_R`, `NEWS1_3B_R` | support de la radio (poste ou écran), de la télévision (poste ou écran), de la presse (papier ou numérique) | oui : définition « numérique » |
| `NEWS1BIS_R` | mode d'information **principal** (9 modalités) | oui : « numérique d'abord » |
| `NEWS1SOURCES_LR6_R` à `LR9_R`, `NEWS1SOURCES_R_*`, `NBR_NEWS1SOURCES_*` | sur moteurs, portails, réseaux et plateformes vidéo : information produite par des médias, par d'autres (créateurs, anonymes) ou les deux | non |
| `DEVICEXMOMENTS_R_*`, `DEVICEXMOMENTS_R1_*_*` | moments de la journée où l'on s'informe, par écran ou support | non |
| `FORMAT_R_*`, `FORMAT2_*`, `FORMAT3_*` | formats préférés (audio, écrit, vidéo, image), longueur (très court à long), direct ou replay | non |
| `PAY_R_*`, `PAY_R1_*` | a payé pour s'informer dans l'année (achat au numéro, abonnement presse, kiosque, site, newsletter...) | non |
| `AGREG_R_*`, `AGREG_R1_*` à `R3_*`, `NOTIF_R` | agrégateurs d'actualité installés et consultés ; notifications activées | non |

**5. Réseaux sociaux et plateformes**

| variables | ce qu'elles mesurent | utilisée ? |
|---|---|---|
| `RSINFO_1_LR_R_1` à `_14` | usage général de chaque réseau ou plateforme (Facebook, Instagram, X, TikTok, Snapchat, LinkedIn, WhatsApp, Telegram, YouTube, Twitch, Reddit, Discord...) | non |
| `RSINFO_2_LR_R_1` à `_13`, `RSINFO_2_LR_R2_*` à `R4_*` | s'informe via ce réseau (base : ses utilisateurs, ou totale selon le récapitulatif) | oui : TikTok, Instagram, Facebook |
| `MOTIVRS_R_1` à `_12` | raisons de s'informer sur les réseaux (l'information vient à moi, temps réel, opinions des autres, formats courts...) | non |
| `ENGAR_R_*`, `ENGAR_R2_*` à `R4_*` | commente, partage, like en s'informant en ligne | non |
| `CONNAISSALGOA_R_*`, `CONNAISSALGOB_R_*` | connaissance du fonctionnement des algorithmes (vrai ou faux) et acceptation | non |
| `CRAINTESALGOIA_R_1` à `_8` | craintes sur les réseaux (fausses informations, violence, données, bulle...) | non |
| `SELECT_R` | préfère une sélection par une rédaction ou par un algorithme | non |
| `IA1_R` | connaissance des usages de l'IA pour créer des contenus | non |

**6. Médias consultés (marques)** : `SOURCES1AR_B1_R_*` (radios), `SOURCES1A_DOMR_R_*` (médias d'outre-mer), `SOURCES1BR_B2_R_*` (quotidiens), `SOURCES1CR_B3_R_*` (magazines), `SOURCES1DR_B4_R_*` (chaînes de télévision), `SOURCES1ER_B4_R_*` (chaînes d'information), `SOURCES1FR_R_*` (médias en ligne et créateurs : pure players, médias vidéo, créateurs de contenus), `TV2AR_R_*`, `TV2BR_R_*`, `TV2CR_R_*` (journaux télévisés, émissions quotidiennes, magazines d'information regardés régulièrement). Questionnaire long. **Non utilisés.**

**7. Évolution des pratiques et évitement de l'information**

| variables | ce qu'elles mesurent | utilisée ? |
|---|---|---|
| `DYN1_R` | s'informe plus, autant, moins qu'avant, ou « a complètement arrêté de suivre l'actualité » | non |
| `DYN2_R_1` à `_10` | raisons de s'informer moins (moins de temps, toujours la même chose, actualité trop négative, défiance, impuissance...) | non |
| `DYN3_R_1` à `_8` | raisons de s'informer plus | non |
| `EVITE1_R` | a évité volontairement l'actualité ces derniers mois (souvent, parfois, jamais) | non |
| `EVITE2_R_1` à `_9` | façons d'éviter (changer de chaîne, couper les notifications, éviter les discussions...) | non |
| `INF1_R_1` à `_4` | préférences : chercher l'information ou la recevoir, sérieux ou décalé, rapide ou approfondi, neutre ou engagé | non |

**8. Confiance, fiabilité, journalistes**

| variables | ce qu'elles mesurent | utilisée ? |
|---|---|---|
| `CONF1_R` | « on peut faire confiance à la plupart des informations » | non |
| `INF3_R_*`, `INF3_R1_*` | confiance selon la source (journalistes, experts, politiques, célébrités, créateurs de contenus, associations, anonymes, proches) | non |
| `ATTSOURCES_R_*`, `INFOFIABLEDEF_R_*`, `INFOFIABLE_R` | rapport à la vérité des informations ; ce qui rend une information fiable ; facilité d'accès à une information fiable | non |
| `OP2_R_*`, `OP2_R1`, `OP2_R2_*` | ce qui forge l'opinion (grands médias, réseaux, inconnus, proches) | non |
| `VALEURJ_R_*`, `ATTENTESJ_R_*`, `DOUTE_R`, `DEFIANCEJ_R_*` | image du journalisme, attentes envers les journalistes, doute sur la fiabilité des médias et ses raisons | non |
| `COMPLOT1_R_*`, `COMPLOT2_R_*` | a entendu, puis croit, huit affirmations complotistes ou fausses | non |

**9. Valeurs, opinions, rapport à la démocratie**

| variables | ce qu'elles mesurent | utilisée ? |
|---|---|---|
| `OPTI_R_*` | optimisme pour soi, la France, l'Union européenne, le climat, internet, les médias | non |
| `ATTA_R_*` | attachement (pays, commune, règles démocratiques, liberté d'expression, laïcité, droit de vote...) | non |
| `DEM_R_*`, `CONFINST_R_*` | fonctionnement de la démocratie et liberté des médias ; confiance dans les institutions et professions (politiques, juges, police, journalistes, enseignants, maire, scientifiques...) | non |
| `PERS_R_*`, `INFLUENCE_R` | traits d'ouverture au débat ; être sollicité pour son avis sur l'actualité | non |
| `VA1_R_*` | opinions sur huit sujets clivants | non |
| `NOU1_R`, `PP3_R` | positionnement gauche-droite, vote au premier tour de la présidentielle 2022 | non |

**10. Connaissance de l'actualité** : `QUIZZ1_R` à `QUIZZ4_R` (quatre questions d'actualité : bonne réponse, mauvaises réponses, « ne sait pas ») ; `QUESTION_OUVERTE` (verbatim). **Non utilisés.**

### B. Arcom, « Les Français et l'information », 2e édition (base 2026, terrain 2025) : non utilisée

- Même page data.gouv.fr : https://www.data.gouv.fr/datasets/les-francais-et-linformation-barometre
- Téléchargements directs :
  - base anonymisée (CSV, `;`, 14,8 Mo, 1 251 colonnes) : https://static.data.gouv.fr/resources/les-francais-et-linformation-barometre/20260604-074907/2026-les-francais-et-linformation-2eme-edition-arcom-base-anonymisee-complete.csv
  - datamap : https://static.data.gouv.fr/resources/les-francais-et-linformation-barometre/20260604-074939/2026-les-francais-et-linformation-2eme-edition-arcom-datamap.xlsx
  - guide d'utilisation : https://static.data.gouv.fr/resources/les-francais-et-linformation-barometre/20260130-154542/2026-les-francais-et-information-2eme-edition-arcom-guide-dutilisation-des-donnees.pdf
- Terrain du 16/06 au 23/07/2025, base publiée le 04/06/2026 (`docs/millesimes_20261030.md`). Non téléchargée dans le dépôt ; datamap et en-tête lus pour cette fiche.
- Changements qui touchent directement la carte :
  - **tranches d'âge différentes** : 15-17, 18-24, 25-34, **35-49, 50-64, 65 ans et plus** (`RS2C_RECODE_AGE`) : le repère « 70 ans et plus » (89 %) n'existera plus, il faudra écrire « 65 ans et plus » ;
  - **pondération renommée** : `WEIGHT_2025_20250801` et `WEIGHT2023_2025MIX` (ce dernier laisse penser à un poids prévu pour comparer les deux vagues : à confirmer dans le guide) ; `POIDS03` disparaît ;
  - **question du mode principal reformulée** : `NEWS1BIS` devient « mode d'information **préféré** » (et non plus « principal »), avec des récapitulatifs « ST réseaux et plateformes », « ST télévision, radio, presse », « ST en ligne » : la série « numérique d'abord » n'est pas directement comparable ;
  - `NEWS1` garde ses modalités de fréquence (de « plusieurs fois par jour » à « jamais ») : les indicateurs « s'informe » (96 %, 90 %) et « télévision chaque jour » (41 %) sont reproductibles, sous réserve de vérifier la liste des modes ;
  - **nouveaux thèmes** : YouTube pour s'informer (`YT1` à `YT5` : fréquence, compte, types et provenance des contenus, durée, abonnement à des médias), **IA conversationnelles** pour s'informer (`IA1_NEW` à `IA5` : fréquence, raisons, vérification et partage), médias et actionnaires (`MEN1`, `MEN2`, `QUIZZMEN`), régulation de l'information (`REG1`, `REG2`), attentes envers les créateurs de contenus, fiabilité perçue des sources (`INF4`), fréquence et confiance par média (`SOURCE1BIS`, `SOURCES1TER`), nombre moyen de sources ;
  - thèmes conservés : intérêt, motivations, réseaux, formats, paiement, agrégateurs, notifications, marques médias, évolution des pratiques (`DYN1` à `DYN3`), évitement (`EVITE1`, `EVITE2`), confiance, journalistes, valeurs, positionnement politique, quiz (nouvelles questions).

## Ce qu'on n'exploite pas encore

Ordres de grandeur ci-dessous : recalcul rapide pondéré (`POIDS03`) pour cette fiche, à revérifier avant tout usage ; effectifs de base entre parenthèses pour les 18-24 ans.

- **L'évitement volontaire de l'actualité** (`EVITE1_R`, questionnaire long) : 22 % des 18-24 ans évitent « souvent » l'actualité, contre 8 à 10 % des 60 ans et plus (238 répondants). C'est la vraie nuance de la question « ne s'informent plus ? » : ils s'informent, mais beaucoup s'en protègent ; les raisons (`DYN2_R`, `EVITE2_R`) disent pourquoi (actualité trop négative, impuissance, défiance).
- **L'évolution déclarée** (`DYN1_R`) : environ 22 % des 18-24 ans disent s'informer moins qu'avant, autant que les autres âges ; 6 % disent avoir arrêté de suivre l'actualité (1 à 3 % chez les 60 ans et plus). Un chiffre direct pour la question, avec son effectif faible.
- **La défiance** (`DOUTE_R`) : environ 62 % des 18-24 ans doutent « toujours ou souvent » de la fiabilité des médias, contre 37 % des 70 ans et plus. Et `INF3_R` (confiance selon la source : journalistes, créateurs de contenus, proches) pour savoir à qui ils font confiance.
- **D'où vient l'information vue en ligne** (`NEWS1SOURCES_*`) : sur les réseaux et plateformes vidéo, information produite par des médias ou non ; nuance essentielle au « numérique d'abord », qui mêle médias sur écran et créateurs.
- **L'intérêt et le sentiment d'être informé** (`INT1_R`, `INT3_R`) : l'intérêt déclaré des 18-24 ans (environ 76 % intéressés) est au niveau des 25-59 ans ; seuls les 15-17 ans (environ 60 %) et les 70 ans et plus (environ 68 %) sont plus bas.
- **La connaissance de l'actualité** (`QUIZZ1_R` à `QUIZZ4_R`) : sur une question (fin du mandat présidentiel), les 18-24 ans répondent juste aussi souvent que les autres (environ 55 %). Les quiz donnent un indicateur de résultat, pas seulement de pratique.
- **La télévision jamais** (`NEWS1_R_2` = 6) : environ 21 % des 18-24 ans ne s'informent jamais par la télévision (3 % des 70 ans et plus) : plus parlant que « 41 % chaque jour » pour dire le décrochage du journal télévisé.
- **Les marques et émissions** (`SOURCES1*`, `TV2*`) : quels médias les jeunes consultent réellement (médias vidéo en ligne, créateurs, chaînes d'information) ; à présenter en agrégats par tranche d'âge, sans classement de marques.
- **Le paiement** (`PAY_R_*`) et les formats (`FORMAT*`) : économie et forme de l'information selon l'âge.
- **Les croisements âge × milieu** (`RS5_R` diplôme, `CSPIND_R`, `RS14_R` revenu) : le clivage est-il générationnel ou social ? Le site a déjà un découpage Milieu social alimenté par la même base.
- **Une valeur « ensemble »** (`references` dans `age.json`) : afficher la moyenne des 15 ans et plus en repère, comme pour d'autres découpages.

## Autres sources possibles

- **Arcom, 2e édition** (jeu B ci-dessus) : à intégrer en priorité (`docs/millesimes_20261030.md` : effort estimé à un jour ; seules 46 des 160 variables de 2024 gardent leur nom). Donne en plus YouTube et les IA conversationnelles.
- **Arcom, « Les Français et l'information », rapport et graphiques** (page Arcom citée par la carte) : chiffres publiés par l'Arcom, pour vérifier que le recalcul du site et la publication officielle concordent.
- **Arcom et ministère de la Culture, baromètre du numérique ou « Référentiel des usages numériques »**, et **Credoc, Baromètre du numérique** (avec l'Arcep, l'Arcom et l'ANCT) : usages des écrans et des réseaux par âge, sur un échantillon plus large ; existence et millésime à vérifier.
- **Reuters Institute, Digital News Report** (annuel, volet France) : série longue sur l'évitement de l'information et les sources des jeunes ; données agrégées publiques, pas de base individuelle ouverte (à vérifier).
- **Médiamétrie** (audiences des journaux télévisés par âge) : chiffres en partie publics, pas d'open data ; utile en contexte seulement.
- **Insee, enquête « Technologies de l'information et de la communication auprès des ménages »** (TIC ménages) : usage d'internet pour lire l'actualité par âge, série annuelle ; disponibilité des tableaux à vérifier.

## Points de relecture

- **Échantillon des 18-24 ans** : 283 répondants (105 pour les 15-17 ans). Marge d'erreur, hors effet de la pondération : environ ± 2 points sur 96 %, ± 6 points sur 41 %, ± 5 points sur 77 %. La carte et la vue n'indiquent ni effectif ni marge ; « 41 % contre 89 % » reste nettement significatif, mais les écarts fins entre tranches voisines (par exemple 15-17 contre 18-24) ne le sont pas.
- **Définition large de « s'informer »** : déclaratif, au moins un mode parmi huit, réseaux sociaux et moteurs compris, « au moins une fois par mois ». La carte le dit (« au moins une fois par mois ») ; le risque est de lire « 96 % s'informent » comme une pratique active. Le chiffre « chaque jour » (90 %) est plus robuste et dit la même chose : on pourrait le mettre en avant.
- **« Ils ont quitté le journal télévisé »** : la mesure est « s'informer par la télévision au moins une fois par jour », pas le journal télévisé ; 60 % des 18-24 ans s'informent par la télévision au moins une fois par semaine (vérification du 29/10). Formulation à adoucir (« la télévision n'est plus leur rendez-vous quotidien ») ou à étayer par `TV2AR_R` (journaux télévisés regardés régulièrement, questionnaire long).
- **« Numérique » englobe la télévision sur écran** : la parenthèse de la carte le dit ; le libellé de l'indicateur dans la vue aussi. Mais « 77 % numérique » peut être lu comme « réseaux sociaux » : un chiffre « réseaux et plateformes vidéo comme mode principal » serait plus net (recalculable avec `NEWS1BIS_R` 8 et 9).
- **Repère « 70 ans et plus »** : n'existe plus dans la 2e édition (65 ans et plus) ; à prévoir dans la formulation.
- **Millésime** : terrain fin 2023, la carte dit « 2024 » (date de publication) ; la 2e édition (terrain 2025) existe depuis juin 2026. Seule source de l'accueil vieille de deux ans.
- **Reproductibilité** : aucun script `python/tools/build_age.py` ; `age.json` a été produit par des travaux d'analyse et des recalculs à la main. À écrire avant le passage à la 2e édition (définitions exactes en tête de cette fiche).
- **Outre-mer et téléphone** : les calculs portent sur toute la base (métropole, outre-mer, téléphone) avec `POIDS03` ; c'est cohérent si le poids est national, à confirmer dans le guide d'utilisation.
- **Chiffre plus parlant possible** : « 9 jeunes sur 10 s'informent chaque jour » (90 %), avec en contrepoint « 1 sur 5 évite souvent l'actualité » (`EVITE1_R`, à vérifier) : réponse « Faux, mais » plus juste qu'un « Faux » sec.
