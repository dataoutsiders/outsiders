# 5. Les députés ressemblent aux Français ?
> Carte `assemblee` · verdict « Faux » (`faux`) · dossier `/terrains/assemblee` · fiche préparée le 30/10/2026

Sujet sensible : cette fiche ne contient aucune donnée nominative (ni député, ni collaborateur ; noms de champs et agrégats seulement). L'indice de diversité des noms (IDP) est un indicateur de groupe, jamais une origine.

## Ce qu'affiche la carte

- **Rubrique** : Représentation politique · unité « Députés » · couleur `#4F46E5`.
- **Question** : « Les députés ressemblent aux Français ? »
- **Verdict** : Faux.
- **Chiffre** : **6 / 577**
- **Libellé** : « députés ouvriers, quand les ouvriers sont 18,6 % des personnes en emploi ».
- **Texte** : « 66 % des députés se déclarent cadres ou professions intellectuelles supérieures (22 % des personnes en emploi). Côté noms, 4,2 % des députés portent un nom classé « diversité » (indice IDP), contre 6,4 % de leurs collaborateurs, plus jeunes, et 7 % de la population : un écart à confirmer, sur une vingtaine de députés. »
- **Source citée** : « Open data Assemblée nationale · INSEE », lien vers https://data.assemblee-nationale.fr/acteurs/deputes-en-exercice
- **Bouton** : « Ouvrir le dossier Assemblée » vers `/terrains/assemblee`.
- Historique : libellés corrigés le 29-30/10/2026 (« personnes en emploi » au lieu d'« actifs », écart de noms « à confirmer »), voir `docs/verification_cartes_accueil.md`, section 5.

## Ce que dit le dossier

Page `frontend/src/pages/terrains/TerrainAssemblee.jsx`, titre « Qui représente qui ? L'Assemblée au miroir de la France », 17e législature.

- **Chapeau** : vérifier « les députés ressemblent aux Français » et « tel parti est le parti du peuple » groupe par groupe : profession (nomenclature Insee), sexe, âge, diversité des noms, et portrait des 2 060 collaborateurs parlementaires.
- **Trois chiffres clés** : 66,4 % de cadres et professions intellectuelles supérieures (contre 22,4 % des personnes en emploi) ; 6 / 577 ouvriers (18,6 %) ; IDP 4,2 % (contre 7 % en population).
- **« Des collaborateurs aux députés »** : deux barres population / collaborateurs / députés, pour l'IDP (7 / 6,4 / 4,2) et pour la part de femmes (51,5 / 47,7 / 37,8) ; parité « nette », noms « non établis ».
- **« Le mur des professions »** : sept familles socioprofessionnelles (dont « sans profession déclarée », 43 députés) contre la population en emploi ; employés et ouvriers en rouge.
- **« Groupe par groupe : qui représente qui ? »** : sélecteur de mesure (femmes, IDP, cadres, âge moyen, ouvriers en effectif), barres par groupe triées par valeur décroissante, repère population ; valeurs IDP en italique sous 20 noms reconnus.
- **Encadré « À lire avec ce recul »** (5 notes : profession déclarée et figée, référence = actifs occupés, IDP bruité à l'individu, petits groupes indicatifs, collaborateurs listés sans carrière ni conditions de travail) ; appel vers l'outil de représentativité.

## D'où viennent les chiffres

Chaîne : open data de l'Assemblée nationale (archive AMO10) -> cache `python/tools/_cache_assemblee/amo10.zip` (téléchargé le 05/07/2026, réutilisé tant qu'il existe) -> `python/tools/build_assemblee.py` (référentiel IDP `frontend/public/data/onomastics/surnames.tsv`, repères population écrits en dur dans le script) -> `frontend/public/data/showcases/assemblee.json` (généré le 05/07/2026) -> `TerrainAssemblee.jsx`. Chiffres de la carte écrits en dur dans `Home.jsx`. Ordre de relance : `docs/DEPLOIEMENT.md`, ligne 80 (après `build_onomastics_reference.py`).

Le script lit, pour chaque fichier `json/acteur/*.json` de l'archive : la civilité, la date de naissance, la famille socioprofessionnelle Insee, le nom (pour l'IDP), le groupe politique en cours (mandat de type `GP` sans date de fin) et la liste des collaborateurs (civilité et nom).

| Chiffre de la carte | Calcul | Clé du JSON |
|---|---|---|
| **6 / 577** | Députés dont `profession.socProcINSEE.famSocPro` commence par « Ouvriers » / nombre d'acteurs de l'archive. | `ensemble.pcs_n.ouvriers`, `ensemble.n` |
| **18,6 %** | Constante `REF_PCS["ouvriers"]` : Insee, enquête Emploi 2023, personnes en emploi (France hors Mayotte), https://www.insee.fr/fr/statistiques/7767045 | `references.pcs.ouvriers` |
| **66 %** | 383 députés « Cadres et professions intellectuelles supérieures » / 577 = 66,4 % (le dénominateur garde les 43 « sans profession déclarée » ; 71,7 % des 534 qui déclarent une profession). | `ensemble.pcs.cadres` |
| **22 %** | Constante `REF_PCS["cadres"]` = 22,4 (même source Insee). | `references.pcs.cadres` |
| **4,2 %** | Noms des députés (`etatCivil.ident.nom`) passés au référentiel : 501 reconnus, soit environ 21 noms « diversité ». | `ensemble.idp_pct`, `idp_n_reconnus` |
| **6,4 %** | Noms des collaborateurs (`mandats.mandat[].collaborateurs.collaborateur[].nom`) : 1 697 reconnus sur 2 060. | `ensemble.collaborateurs.idp_pct` |
| **7 %** | Constante `REF_IDP` = 7,0 (rapport TEPP, reprise de `onomastics/meta.json`). | `references.idp` |
| « plus jeunes » | **Aucune donnée** : l'archive ne donne ni âge ni date de naissance des collaborateurs. | (aucune) |
| « une vingtaine de députés » | 4,2 % de 501 = 21. Écart 6,4 contre 4,2 non significatif au seuil de 5 % (test de deux proportions, p d'environ 0,07, recalcul de la vérification du 29/10). | (calcul) |

Autres valeurs du JSON : femmes 37,8 % (civilité « Mme ») ; âge moyen 52,0 ans (année en cours moins année de naissance) ; 2 060 collaborateurs, 3,6 par député, 47,7 % de femmes ; 12 groupes (sigles, couleurs et ordre d'hémicycle écrits en dur dans `GROUPES_META`).

## Les jeux de données

### A. Assemblée nationale, « Députés en exercice » : archive AMO10 (députés actifs, mandats actifs et organes)

- Producteur : Assemblée nationale (portail open data, licence ouverte).
- Page : https://data.assemblee-nationale.fr/acteurs/deputes-en-exercice
- Téléchargement direct utilisé : https://data.assemblee-nationale.fr/static/openData/repository/17/amo/deputes_actifs_mandats_actifs_organes/AMO10_deputes_actifs_mandats_actifs_organes.json.zip (existe aussi en XML).
- Autres formats de la même page : AMO40 « organes divisés » en CSV (`AMO40_deputes_actifs_mandats_actifs_organes_divises.csv.zip`) ; liste simple CSV (`liste_deputes_excel.csv` : identifiant, prénom, nom, région, département, numéro de circonscription, profession, groupe complet et abrégé).
- Millésime utilisé : export du 05/07/2026. Dernier disponible : fichier modifié le 29/10/2026 (574 députés en exercice, 13 sortis et 10 entrés depuis juillet, selon `docs/millesimes_20261030.md`). Mise à jour quotidienne côté AN.
- Fichier local : `python/tools/_cache_assemblee/amo10.zip` (4,9 Mo ; 577 fichiers `acteur`, 7 139 fichiers `organe`, 37 fichiers `deport`). JSON, un fichier par acteur et par organe.
- Géographie : circonscription législative (577), département, région.

Champs d'un acteur (documentation : schéma XML de l'AN, publié sur le portail ; sens déduit des noms de champs et des valeurs) :

| champ | sens | utilisé ? |
|---|---|---|
| `uid` | identifiant de l'acteur (PA...) | non (sert implicitement à lire un fichier par député) |
| `etatCivil.ident.civ` | civilité (M. ou Mme) | oui : part de femmes |
| `etatCivil.ident.nom`, `prenom`, `alpha`, `trigramme` | nom, prénom, nom de tri, trigramme | `nom` oui : IDP (jamais affiché) ; les autres non |
| `etatCivil.infoNaissance.dateNais` | date de naissance | oui : âge (année seulement) |
| `etatCivil.infoNaissance.villeNais`, `depNais`, `paysNais` | lieu de naissance (ville, département, pays ; 26 députés avec un pays autre que la France ou vide) | non |
| `etatCivil.dateDeces` | date de décès (vide) | non |
| `profession.libelleCourant` | profession déclarée, en clair | non |
| `profession.socProcINSEE.catSocPro` | catégorie socioprofessionnelle détaillée (26 modalités présentes : cadres de la fonction publique 182, cadres d'entreprise 117, professions libérales 76, enseignants du primaire 42...) | non |
| `profession.socProcINSEE.famSocPro` | famille socioprofessionnelle (6 familles + « sans profession déclarée » ; 3 vides) | oui : mur des professions, cadres, ouvriers |
| `uri_hatvp` | lien vers les déclarations à la Haute Autorité pour la transparence de la vie publique | non |
| `adresses.adresse[]` | adresses postales, électroniques, sites, réseaux (type, libellé, valeur) | non |
| `mandats.mandat[].typeOrgane` | type d'organe du mandat (ASSEMBLEE, GP groupe politique, COMPER commission permanente, PARPOL parti, GA et GE groupes d'amitié et d'études, ORGEXTPARL organismes extraparlementaires, MISINFO missions, DELEG délégations, BUREAU, GOUVERNEMENT, MINISTERE...) | oui pour `GP` (groupe) ; les autres non |
| `mandats.mandat[].organes.organeRef` | identifiant de l'organe (renvoie à `json/organe/`) | oui pour le groupe |
| `mandats.mandat[].dateDebut`, `dateFin`, `datePublication` | dates du mandat | oui : `dateFin` vide = groupe actuel |
| `mandats.mandat[].infosQualite.codeQualite`, `libQualite`, `libQualiteSex` | qualité dans l'organe (membre, président, vice-président, rapporteur...) | non |
| `mandats.mandat[].legislature`, `preseance`, `nominPrincipale` | législature, ordre protocolaire, nomination principale | non |
| `mandats.mandat[].election.lieu` (`region`, `regionType`, `departement`, `numDepartement`, `numCirco`) et `refCirconscription` | circonscription d'élection | non |
| `mandats.mandat[].election.causeMandat` | cause du mandat (élections générales 511 ; remplacement d'un député nommé au Gouvernement 20 ; incompatibilité 20 ; reprise après le Gouvernement 16 ; partielles...) | non |
| `mandats.mandat[].mandature.premiereElection` | 1 si première élection comme député | non |
| `mandats.mandat[].mandature.datePriseFonction`, `causeFin`, `mandatRemplaceRef`, `placeHemicycle` | prise de fonction, fin, mandat remplacé, place dans l'hémicycle | non |
| `mandats.mandat[].suppleants.suppleant` (`suppleantRef`, dates) | suppléant (renvoi à un autre acteur) | non |
| `mandats.mandat[].collaborateurs.collaborateur[].qualite` | civilité du collaborateur | oui : part de femmes des collaborateurs |
| `...collaborateur[].nom`, `prenom` | nom, prénom | `nom` oui : IDP des collaborateurs (jamais affiché) |
| `...collaborateur[].dateDebut`, `dateFin` | dates du contrat | non (toujours vides dans l'export) |

Champs d'un organe (`json/organe/*.json`) : `uid`, `codeType`, `libelle`, `libelleAbrev` (utilisés pour le nom et le sigle des groupes), plus les dates, la législature, le parent et le secrétariat (non utilisés).

### B. Repères population (Insee), écrits en dur dans `build_assemblee.py`

| repère | valeur | source citée | dernier millésime disponible |
|---|---|---|---|
| familles socioprofessionnelles des personnes en emploi | agriculteurs 1,5 ; artisans 6,7 ; cadres 22,4 ; intermédiaires 25,1 ; employés 25,2 ; ouvriers 18,6 | Insee, enquête Emploi 2023, https://www.insee.fr/fr/statistiques/7767045 (vérifié le 04/07/2026) | enquête Emploi 2025, https://www.insee.fr/fr/statistiques/8733043 |
| part des femmes | 51,5 % de la population | Insee, population par sexe et âge au 1er janvier 2025, https://www.insee.fr/fr/statistiques/2381474 | population au 1er janvier 2026 |
| IDP de la population | 7,0 % | rapport TEPP (Kheddache et L'Horty), https://www.tepp.eu/ | référence figée |

### C. Moteur onomastique (Insee, noms de famille et prénoms)

Identique au dossier Élus (voir `docs/relecture/04_elus.md`, jeux F et G) : fichier des noms 1891-2000, https://www.insee.fr/fr/statistiques/3536630, téléchargement https://www.insee.fr/fr/statistiques/fichier/3536630/noms2008nat_txt.zip, local `python/data/municipales/noms_famille/noms2008nat_txt.txt`, colonnes `NOM` et onze décennies `_1891_1900` à `_1991_2000` ; règle « absent avant 1951 ou multiplié par plus de 15 après » ; noms absents du référentiel exclus du dénominateur (76 députés et 363 collaborateurs non reconnus). Le fichier des prénoms n'intervient pas dans ce dossier.

## Ce qu'on n'exploite pas encore

- **La profession détaillée** (`catSocPro`, `libelleCourant`) : le « 66 % de cadres » cache une forte part de cadres de la fonction publique (182) et d'entreprise (117) ; distinguer public et privé, ou repérer les anciens collaborateurs et permanents politiques dans le libellé, dirait mieux « d'où viennent » les députés.
- **La première élection** (`premiereElection`) : comparer néo-députés et réélus (sexe, âge, profession, IDP au niveau de l'ensemble seulement) teste l'idée d'un renouvellement par le bas.
- **La cause du mandat** (`causeMandat`) : 66 députés siègent après un remplacement, une reprise de mandat ou une élection partielle (ministres, incompatibilités, décès, annulations) ; comparer titulaires élus et suppléants devenus députés.
- **Les fonctions de pouvoir** (`infosQualite` dans les commissions, le bureau, les présidences de groupe) : la parité dans les postes de responsabilité est une mesure de groupe sans risque nominatif si elle reste agrégée à l'Assemblée entière.
- **La circonscription** (`election.lieu`) : comparer le profil des députés au profil social de leur territoire (part d'ouvriers ou de cadres de la région ou du département), plutôt qu'à la France entière.
- **Le parti de rattachement** (`typeOrgane` = `PARPOL`) : différent du groupe ; utile pour les apparentés et les non-inscrits.
- **Le lieu de naissance** (`paysNais`, `depNais`) : un agrégat national (part de députés nés hors de France métropolitaine) serait une mesure différente de l'IDP ; sensible, à ne présenter qu'au niveau de l'Assemblée entière, jamais par groupe.
- **L'âge exact** (`dateNais` complète au lieu de l'année) et la distribution par tranches d'âge contre la population adulte : l'âge moyen seul (52 ans) n'a pas de repère population sur la page.
- **Les fichiers `deport`** (37) : déports déclarés pour conflit d'intérêts, hors sujet du dossier.

## Autres sources possibles

- **Assemblée nationale, archive AMO30 « tous acteurs, tous mandats, tous organes » (historique)** : https://data.assemblee-nationale.fr/static/openData/repository/17/amo/tous_acteurs_mandats_organes_xi_legislature/AMO30_tous_acteurs_tous_mandats_tous_organes_historique.json.zip ; même structure, toutes les législatures depuis la 11e (1997). Permet la série « l'Assemblée se diversifie-t-elle ? » (profession, sexe, âge, IDP par législature), qui répondrait mieux à la question de la carte que la photo actuelle.
- **Datan, « Députés actifs » et « Historique des députés depuis 2002 »** (data.gouv.fr, mis à jour le 28/10/2026) : https://www.data.gouv.fr/datasets/deputes-actifs-de-lassemblee-nationale-informations-et-statistiques (CSV `deputes-active.csv` : législature, civilité, ville de naissance, naissance, âge, groupe, département, circonscription, date de prise de fonction, profession, nombre de mandats, expérience, scores de participation, de loyauté et de majorité) et https://www.data.gouv.fr/datasets/historique-des-deputes-de-lassemblee-nationale-depuis-2002-informations-et-statistiques. Producteur associatif : contrôle croisé utile, pas une source officielle.
- **Répertoire national des élus, fichier des députés** (ministère de l'Intérieur) : https://static.data.gouv.fr/resources/repertoire-national-des-elus-1/20260811-155035/elus-depute-dep.csv ; catégorie socioprofessionnelle au format du Répertoire, comparable aux élus locaux (dossier Élus) ; fichier des sénateurs dans le même jeu, pour étendre au Parlement.
- **Sénat, open data** (data.senat.fr) : profession et âge des sénateurs ; existence des champs à vérifier.
- **Insee, enquête Emploi 2025** (Insee 8733043) : mise à jour des repères PCS ; et **population par âge au 1er janvier 2026** pour un repère adulte (18 ans et plus) au lieu de la population totale.
- **Insee, données par circonscription législative** : profil social des 577 circonscriptions, pour comparer chaque groupe à ses territoires ; existence d'un jeu officiel à jour à vérifier.

## Points de relecture

- **« plus jeunes » n'est pas sourcé** : l'open data ne donne pas l'âge des collaborateurs. C'est une hypothèse plausible, pas une donnée du dossier. À retirer, ou à remplacer par « dont l'âge n'est pas publié ».
- **Données de juillet** : l'export utilisé date du 05/07/2026 ; l'AN en publie un du 29/10/2026 (13 sortis, 10 entrés). Le cache local empêche toute mise à jour automatique : il faut le vider avant de relancer. « 6 / 577 » peut devenir « x / 574 » (députés en exercice) ; le dénominateur 577 suppose tous les sièges pourvus.
- **Repères PCS** : enquête Emploi 2023 alors que 2025 est publiée ; et le repère compare des députés (souvent leur profession d'avant, ou « sans profession ») à des personnes **en emploi**. La note de la page le dit pour « sans profession », pas pour les retraités ni pour la profession ancienne. Formulation actuelle « se déclarent » correcte.
- **66 % sur 577 ou 72 % sur 534** : le choix du dénominateur (avec les 43 sans profession déclarée) minore la part de cadres ; à écrire en note pour éviter une contestation.
- **IDP, petits effectifs par groupe** : la vue « Groupe par groupe » montre l'IDP de groupes de 10 à 20 noms reconnus ; une valeur non nulle y correspond à un seul député, ce qui le rend identifiable par déduction, et des 0,0 % se lisent comme un verdict sur un groupe. Envisager de ne pas afficher l'IDP sous un seuil (par exemple 30 noms, règle du dossier Sport) et de retirer le tri par valeur, qui fait palmarès.
- **Écart députés / collaborateurs non significatif** (p d'environ 0,07) : la carte le dit (« à confirmer ») ; la page le dit (« noms non établis ») ; mais `config/seo.js` (ligne 68) écrit encore « des collaborateurs plus divers que les élus ». À aligner.
- **Repère « 7 % de la population »** : constante non documentée sur la page Méthodologie ; population de référence (âge, année) à préciser. Les députés et collaborateurs sont des adultes : un repère tous âges surestime probablement l'attendu (l'IDP est plus élevé chez les jeunes, voir `04_elus.md`).
- **Noms non reconnus exclus** (13 % des députés, 18 % des collaborateurs) : les noms récents ou rares sortent du calcul, ce qui sous-estime probablement l'IDP, et plus chez les collaborateurs. À mentionner avec le chiffre.
- **Part de femmes** : repère 51,5 % de toute la population (enfants compris) ; un repère « 18 ans et plus » serait plus juste (un peu plus élevé). Âge moyen calculé à l'année près (année en cours moins année de naissance).
- **Verdict** : « Faux » tient sur la profession (6 ouvriers contre 18,6 % attendus, le contraste est massif et robuste) ; le volet noms est fragile et pourrait sortir de la carte pour la garder sur un seul message solide. Chiffre plus parlant possible : « 1 député sur 96 est ouvrier, 1 personne en emploi sur 5 ».
