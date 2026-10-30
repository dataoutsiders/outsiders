# 4. La politique locale se diversifie ?
> Carte `elus` · verdict « Vrai, mais » (`vraiMais`) · dossier `/terrains/elus` · fiche préparée le 30/10/2026

Sujet sensible : cette fiche ne contient aucune donnée nominative (noms de colonnes et agrégats seulement). L'indice de diversité des noms (IDP) est un indicateur de groupe, jamais une origine.

## Ce qu'affiche la carte

- **Rubrique** : Représentation politique · unité « Élus » · couleur `#EC4899`.
- **Question** : « La politique locale se diversifie ? »
- **Verdict** : Vrai, mais.
- **Chiffre** : **2,6 → 3,2 %**
- **Libellé** : « de noms classés « diversité » (indice IDP) parmi les conseillers élus au premier tour, de 2020 à 2026, dans les mêmes communes ».
- **Texte** : hausse chez les candidats (5,4 % puis 6,2 %) et les têtes de liste (2,5 % puis 3,3 %), « lente et loin des 7 % de la population » ; « La diversité se perd surtout au choix de qui conduit la liste : 2 % des têtes de liste portent un tel nom, contre 3 % de leurs colistiers » ; garde-fou « Indicateur de groupe calculé sur les noms, pas une origine ».
- **Source citée** : « Municipales 2020 et 2026, candidats et élus du premier tour (data.gouv.fr) », lien vers le jeu « Élections municipales 2026, résultats du premier tour ».
- **Bouton** : « Voir 2020 et 2026 côte à côte » vers `/terrains/elus`.
- Historique : carte réécrite le 29-30/10/2026 après la vérification (`docs/verification_cartes_accueil.md`, section 4). L'ancienne version (« Faux », filtre « ÷ 3,7 » des candidats aux maires) est remplacée par la comparaison 2020-2026.

## Ce que dit le dossier

Page `frontend/src/pages/terrains/TerrainElus.jsx`, titre « La diversité des élus, du candidat au maire », bandeau « Démonstration » (vitrine de l'outil de représentativité).

- **Chapeau** : 888 079 candidats des municipales 2026, comparés à 2020 ; deux constats (progression lente, perte au choix de la tête de liste) ; garde-fou explicite.
- **Trois chiffres clés** : IDP des candidats 4,4 % (contre 7 % en population) ; 48,7 % de femmes parmi les candidats ; 2,6 → 3,2 % chez les conseillers élus au premier tour, mêmes communes de 1 000 habitants et plus.
- **« De 2020 à 2026 : une progression lente »** : tableau à trois lignes (candidats, têtes de liste, conseillers élus au premier tour) avec effectifs 2020 et 2026 et écart en points ; note sur le second tour de 2020 (juin, Covid), sur l'effet de génération, sur l'absence de comparaison des maires ; liens vers les trois jeux data.gouv.fr.
- **« Où se perd la diversité ? »** : écart brut candidats → maires (÷ 3,7) décomposé en géographie (2,3 % en moyenne des communes) et sélection (÷ 1,9 commune par commune) ; trois barres « observé » contre « attendu » (têtes de liste contre candidats de leur liste, conseillers contre candidats de leur commune, maires contre candidats de leur commune).
- **« La carte de la diversité »** : renvoi vers l'Atlas (`/atlas?i=idp`).
- **« Où la diversité est-elle la plus forte ? »** : les 12 départements les plus hauts et les 12 plus bas (outre-mer signalés par un astérisque).
- **« Les communes aux extrêmes »** : top 15 et bottom 15 des 2 928 communes d'au moins 50 candidats reconnus.
- **« La diversité selon le parti »** : IDP des candidats par nuance de liste (au moins 200 candidats reconnus) et repère pour les têtes de liste (au moins 10 têtes reconnues).
- **Encadré outre-mer et limite de l'IDP** ; appel vers l'outil `/outils/representativite` ; pied de page vers les listes candidates 2026 et le Répertoire national des élus.

## D'où viennent les chiffres

Chaîne : data.gouv.fr (ministère de l'Intérieur) et Insee -> `python/data/municipales/` (fichiers téléchargés à la main) -> `python/tools/build_onomastics_reference.py` (référentiel `frontend/public/data/onomastics/surnames.tsv`) -> `python/tools/build_showcase_elus.py` -> `frontend/public/data/showcases/elus-diversite.json` (généré le 29/10/2026) -> `TerrainElus.jsx`. Les chiffres de la carte sont écrits en dur dans `Home.jsx`. Ordre de relance : `docs/DEPLOIEMENT.md`, lignes 64 et 79.

Règle commune à tous les taux : nom normalisé (majuscules, sans accents, apostrophes en espaces) puis recherché dans `surnames.tsv` ; « diversité » si le drapeau vaut 1, « non » si 0, **exclu du dénominateur** s'il est absent du référentiel (89 % des candidats 2026 reconnus, 90,6 % des conseillers du Répertoire).

| Chiffre de la carte | Calcul | Clé du JSON |
|---|---|---|
| **2,6 → 3,2 %** | Élus du premier tour : `candidats-elus-2020-t1.txt` (colonne `Nom`) contre `candidats-elus-t1.csv` (colonne `NOMPSN`). Champ : communes de métropole présentes dans les listes 2020 (1 000 habitants et plus) et 2026, **et** pourvues au premier tour les deux années : 7 755 communes ; 160 757 élus en 2020, 162 481 en 2026. Clé commune = département + 3 derniers chiffres du code commune. | `evolution.lignes[2].idp_2020`, `idp_2026` |
| **5,4 % puis 6,2 %** | Candidats : `candidatures-2020-t1.txt` (`Nom candidat`) contre `municipales-2026.csv` (`Nom sur le bulletin de vote`), mêmes 9 780 communes ; 510 547 et 495 108 candidats. | `evolution.lignes[0]` |
| **2,5 % puis 3,3 %** | Têtes de liste : 2020 = `N° candidat` égal à 1 ; 2026 = `Tête de liste` = OUI ; mêmes 9 780 communes ; 19 662 et 18 810 têtes. | `evolution.lignes[1]` |
| **7 % de la population** | Constante `population_baseline_pct` = 7,0 écrite dans `build_onomastics_reference.py`, reprise du rapport TEPP (Kheddache et L'Horty). Pas recalculée par le site. | `onomastics/meta.json` |
| **2 %** des têtes de liste | 2026, **toutes les communes** : 1,96 % des 49 911 têtes de liste au nom reconnu. | `filtre.tetes` (2,0) |
| **3 %** de leurs colistiers | Pour chaque tête de liste, taux IDP de **toute sa liste** (tête comprise), puis moyenne sur les têtes : 3,0 %. | `filtre.tetes_attendu_liste` |

Autres chiffres du dossier, même script : 4,4 % des candidats (`national.idp`), 2,7 % des conseillers et 1,2 % des maires du Répertoire national des élus du 11/08/2026 (`funnel`), ÷ 3,7 brut et ÷ 1,9 commune par commune (`filtre.rapport_brut`, `filtre.rapport_commune`), 103 départements, 2 928 communes, 1 255 intercommunalités colorées (`epci.valueByCode`, jointure par `communes-epci.json`), 22 nuances.

## Les jeux de données

### A. Élections municipales 2026, listes candidates au premier tour (ministère de l'Intérieur)

- Page : https://www.data.gouv.fr/datasets/elections-municipales-2026-listes-candidates-au-premier-tour
- Téléchargement direct : https://static.data.gouv.fr/resources/elections-municipales-2026-listes-candidates-au-premier-tour/20260313-152615/municipales-2026-candidatures-france-entiere-tour-1-2026-03-13.csv
- Millésime : données du 13/03/2026 (fichier figé ; données « sous réserve des recours et rectifications »). Autres ressources du jeu non utilisées : Polynésie française (deux fichiers), conseils d'arrondissement de Paris, Lyon et Marseille.
- Fichiers locaux : `python/data/municipales/municipales-2026.csv` et `candidatures-2026-t1.csv` (identiques octet pour octet, 145 Mo, 888 079 lignes). Séparateur `;`, UTF-8, champs entre guillemets.
- Géographie : toutes les communes (la loi de 2025 étend le scrutin de liste à toutes les communes), y compris l'outre-mer ; clé = `Code circonscription` (code commune Insee à 5 caractères).

| colonne | sens | utilisée ? |
|---|---|---|
| `Code département` | code du département | oui : clé commune, regroupement par département |
| `Département` | libellé du département | oui : libellé des classements départementaux |
| `Code circonscription` | code Insee de la commune (5 caractères) | oui : clé commune, jointure intercommunalité |
| `Circonscription` | nom de la commune | oui : libellé des classements communaux |
| `Numéro de panneau` | numéro de la liste dans la commune | oui : clé de liste (filtre « têtes de liste contre leur liste ») |
| `Libellé abrégé de liste` | nom court de la liste | non |
| `Libellé de la liste` | nom complet de la liste | non |
| `Code nuance de liste` | nuance attribuée par le ministère (LDVD, LDVG, LDIV, LUG, LRN, LFI...) ; vide pour 65 % des candidats (petites communes non nuancées) | non (le script groupe sur le libellé, pas sur le code) |
| `Nuance de liste` | libellé de la nuance | oui : section « selon le parti » (au moins 200 candidats reconnus) |
| `Tête de liste` | OUI pour le candidat qui conduit la liste (49 911) | oui : têtes de liste |
| `Ordre` | rang du candidat sur la liste | non |
| `Sexe` | M ou F (68 vides) | oui : part de femmes (48,7 %) |
| `Nom sur le bulletin de vote` | nom du candidat | oui : seule entrée de l'IDP (jamais affichée) |
| `Prénom sur le bulletin de vote` | prénom | non sur cette page (sert à valider le proxy « sexe par le prénom » dans `build_onomastics_reference.py`) |
| `Nationalité` | nationalité déclarée (Française 881 699 ; environ 6 300 ressortissants de l'Union : belges, portugais, allemands, néerlandais, italiens...) | non |
| `Code personnalité` | qualité particulière du candidat (député, sénateur, président de conseil départemental ou régional, ministre, député européen...) ; 616 renseignés | non |
| `CC` | OUI si candidat aussi au conseil communautaire (134 676) | non |

### B. Élections municipales 2026, résultats du premier tour : candidats élus (ministère de l'Intérieur)

- Page : https://www.data.gouv.fr/datasets/elections-municipales-2026-resultats-du-premier-tour
- Téléchargement direct (élus) : https://static.data.gouv.fr/resources/elections-municipales-2026-resultats-du-premier-tour/20260320-164100/municipales-2026-candidats-elus-france-entiere-tour-1-2026-03-20.csv
- Même jeu, non utilisés par le dossier mais présents en local : résultats par commune (`resultats-communes.csv`, ressource `municipales-2026-resultats-communes-2026-03-20.csv`) et par bureau de vote (`resultats-bv-communes.csv`).
- Millésime : fichier du 20/03/2026.
- Fichier local : `python/data/municipales/candidats-elus-t1.csv` (35 Mo, 469 376 élus). Séparateur `;`, UTF-8.
- Géographie : commune (code département + code commune).

| colonne | sens | utilisée ? |
|---|---|---|
| `NOMPSN` | nom de l'élu | oui : IDP 2026 des élus du premier tour |
| `PREPSN` | prénom | non |
| `DATNAIPSN` | date de naissance (renseignée pour tous) | non |
| `SEXPSN` | sexe (M 243 567, F 225 809) | non |
| `CODPRO` | code profession déclarée (42 modalités, nomenclature du ministère de l'Intérieur) | non |
| `EFFECTIF_LEGAL` | nombre de sièges du conseil municipal (taille légale du conseil) | non |
| `CODDPT` | code département | oui : clé commune |
| `CODCOM` | code commune | oui : clé commune |
| `IND_ELU_EPCI` | élu ou non conseiller communautaire (OUI, NON, vide) | non |
| `CODE_NUANCE_DE_LISTE` | nuance de la liste de l'élu (vide pour 85 %) | non |
| `CODE_PERSONNALITE` | qualité particulière (député, sénateur...) | non |
| `TOUR_ELECTION` | « élu T1 » | non (constant) |

Fichiers de second tour 2026 présents en local mais **non utilisés** : `candidatures-2026-t2.csv` (123 857 candidats, mêmes colonnes que A), `candidats-elus-2026-t2.csv` (42 068 élus, mêmes colonnes que B), `resultats-communes-2026-t2.csv` ; jeux https://www.data.gouv.fr/datasets/elections-municipales-2026-listes-candidates-au-second-tour et https://www.data.gouv.fr/datasets/elections-municipales-2026-resultats-du-second-tour (élus du second tour : https://static.data.gouv.fr/resources/elections-municipales-2026-resultats-du-scond-tour/20260323-180122/municipales-2026-candidats-elus-france-entiere-tour-2-2026-03-23.csv).

### C. Élections municipales 2020, candidatures au premier tour (ministère de l'Intérieur)

- Page : https://www.data.gouv.fr/datasets/elections-municipales-2020-candidatures-au-1er-tour
- Téléchargement direct : https://static.data.gouv.fr/resources/elections-municipales-2020-candidatures-au-1er-tour/20200304-105123/livre-des-listes-et-candidats.txt (aussi en `.xlsx` ; ressource sœur « livre des candidats scrutin plurinominal » pour les communes de moins de 1 000 habitants, non téléchargée).
- Millésime : 04/03/2020 (fichier figé).
- Fichier local : `python/data/municipales/candidatures-2020-t1.txt` (65 Mo, environ 546 000 lignes). Tabulation, latin-1, **deux lignes d'en-tête** à sauter (avertissement : seules les listes des communes de 3 500 habitants et plus et des chefs-lieux d'arrondissement sont nuancées).
- Géographie : communes de 1 000 habitants et plus (scrutin de liste).

| colonne | sens | utilisée ? |
|---|---|---|
| `Code du département` | code du département (sans zéro initial) | oui : clé commune |
| `Libellé du département` | libellé | non |
| `Code commune` | code commune à 3 chiffres (sans le département) | oui : clé commune |
| `Libellé commune` | nom de la commune | non |
| `N° Panneau Liste` | numéro de la liste | non |
| `Libellé abrégé liste` | nom court de la liste | non |
| `Libellé Etendu Liste` | nom complet | non |
| `Nuance Liste` | nuance (communes de 3 500 habitants et plus) | non |
| `N° candidat` | rang sur la liste (1 = tête de liste) | oui : têtes de liste 2020 |
| `Sexe candidat` | M ou F | non |
| `Nom candidat` | nom | oui : IDP des candidats 2020 |
| `Prénom candidat` | prénom | non |
| `Nationalité` | nationalité | non |
| `Candidat au conseil communautaire` | O ou vide | non |

### D. Élections municipales 2020, candidats élus au premier tour (ministère de l'Intérieur)

- Page : https://www.data.gouv.fr/datasets/elections-municipales-2020-liste-des-candidats-elus-au-t1-et-liste-des-communes-entierement-pourvues
- Téléchargement direct : https://static.data.gouv.fr/resources/election-municipales-2020-liste-des-candidats-elus-au-t1-et-liste-des-communes-entierement-pourvues/20200605-144249/liste-des-candidats-elus-lors-du-t1-des-elections-municipales-de-2020.txt
- Autres ressources du jeu non utilisées : liste des communes entièrement pourvues au premier tour (`.txt`, `.xls`) ; **maires au 17/06/2020** (`maires-au-17-06-2020-vf.xlsx`), qui mêle maires élus en 2014 et en 2020 (raison avancée par la page pour ne pas comparer les maires).
- Millésime : 05/06/2020.
- Fichier local : `python/data/municipales/candidats-elus-2020-t1.txt` (21 Mo, 431 587 élus). Tabulation, latin-1.
- Géographie : toutes les communes pourvues au premier tour.

| colonne | sens | utilisée ? |
|---|---|---|
| `Code dpt` | code du département | oui : clé commune |
| `Code commune` | code commune à 3 chiffres | oui : clé commune |
| `Libellé de la commune` | nom | non |
| `Nom` | nom de l'élu | oui : IDP des élus 2020 |
| `Prénom` | prénom | non |
| `Date de naissance` | date de naissance (JJ/MM/AAAA) | non |
| `Election au CC` | élu conseiller communautaire | non |

### E. Répertoire national des élus (ministère de l'Intérieur)

- Page : https://www.data.gouv.fr/datasets/repertoire-national-des-elus-1 (mise à jour trimestrielle ; licence ouverte).
- Téléchargements directs utilisés : https://static.data.gouv.fr/resources/repertoire-national-des-elus-1/20260811-155100/elus-maire-mai.csv et https://static.data.gouv.fr/resources/repertoire-national-des-elus-1/20260811-154802/elus-conseiller-municipal-cm.csv
- Millésime : mise à jour du 11/08/2026 (la dernière au 30/10/2026 ; la page précise que des mises à jour post-renouvellement sont encore en cours).
- Fichiers locaux (renommés) : `python/data/municipales/rne/elus-maires-2026-08.csv` (34 826 maires) et `elus-conseillers-municipaux-2026-08.csv` (511 225 conseillers). Séparateur `;`, UTF-8, dates au format AAAA-MM-JJ.
- Géographie : commune ; collectivités à statut particulier signalées (Paris, outre-mer du Pacifique...).
- Autres fichiers du même jeu, non téléchargés : conseillers communautaires, d'arrondissement, départementaux, régionaux, membres d'assemblée (Corse, Guyane, Martinique), députés, sénateurs, représentants au Parlement européen, conseillers des Français de l'étranger.

| colonne (fichier conseillers ; le fichier maires a les mêmes moins `Libellé de la fonction` et `Code nationalité`) | sens | utilisée ? |
|---|---|---|
| `Code du département` | code du département | oui : clé commune (filtre commune par commune) |
| `Libellé du département` | libellé | non |
| `Code de la collectivité à statut particulier` | code de la collectivité (Paris, Nouvelle-Calédonie, Polynésie...) | non |
| `Libellé de la collectivité à statut particulier` | libellé | non |
| `Code de la commune` | code commune | oui : clé commune |
| `Libellé de la commune` | nom | non |
| `Nom de l'élu` | nom | oui : IDP des conseillers (2,7 %) et des maires (1,2 %) |
| `Prénom de l'élu` | prénom | non |
| `Code sexe` | M ou F | oui : féminisation des maires (22,9 %) et des conseillers (48,1 %), calculée mais non affichée sur la page |
| `Date de naissance` | date de naissance (renseignée pour tous ; quelques années aberrantes, avant 1930) | non |
| `Code de la catégorie socio-professionnelle` | profession déclarée, code à 2 chiffres (42 modalités) | non |
| `Libellé de la catégorie socio-professionnelle` | libellé (« Ancien cadre », « Cadre administratif et commercial d'entreprise »...) | non |
| `Date de début du mandat` | date du mandat (15 ou 22 mars 2026 pour l'essentiel) | non |
| `Libellé de la fonction` | Maire, 1er adjoint, 2e adjoint... ; vide pour les conseillers sans fonction | non |
| `Date de début de la fonction` | date de prise de la fonction | non |
| `Code nationalité` | FR, BE, PT, NL, DE... (environ 2 800 ressortissants de l'Union) | non |

### F. Moteur onomastique : fichier des noms de famille (Insee)

- Page : https://www.insee.fr/fr/statistiques/3536630 (« Fichier des noms »).
- Téléchargement direct : https://www.insee.fr/fr/statistiques/fichier/3536630/noms2008nat_txt.zip
- Millésime : édition 2008 (naissances 1891-2000), fichier figé, pas de nouvelle édition.
- Fichier local : `python/data/municipales/noms_famille/noms2008nat_txt.txt` (218 983 lignes, archive `noms_famille_nat.zip`). Tabulation, UTF-8.
- Géographie : France entière. **Existe aussi par département** (`noms2008dep_txt.zip`, même page), non téléchargé.

| colonne | sens | utilisée ? |
|---|---|---|
| `NOM` | nom de famille | oui : clé du référentiel après normalisation (les variantes qui se normalisent pareil sont additionnées) |
| `_1891_1900` à `_1941_1950` (6 colonnes) | nombre de naissances en France portant ce nom, par décennie, avant 1951 | oui : somme « avant » |
| `_1951_1960` à `_1991_2000` (5 colonnes) | naissances par décennie, 1951-2000 | oui : somme « après » |

Règle IDP (Kheddache et L'Horty, rapport TEPP n° 2024-1, PDF local `python/data/municipales/indicediversitepatronymique1.pdf`) : un nom est « diversité » s'il est absent des naissances avant 1951 ou si les naissances 1951-2000 dépassent 15 fois celles d'avant. Résultat : 218 676 noms normalisés, 16 642 marqués « diversité » (7,6 % du référentiel), écrits dans `surnames.tsv` (deux colonnes : nom normalisé, drapeau 0 ou 1). Un nom absent du fichier (apparu après 2000, rare, composé, mal orthographié) est exclu du calcul.

### G. Moteur onomastique : fichier des prénoms (Insee)

- Page : https://www.insee.fr/fr/statistiques/8595130 (édition de juillet 2026, naissances 1900-2025, effectifs arrondis à 5) ; page générique sur data.gouv.fr : https://www.data.gouv.fr/datasets/fichier-des-prenoms-depuis-1900
- Téléchargement direct : https://www.insee.fr/fr/statistiques/fichier/8595130/prenoms-2025-nat_csv.zip (existent aussi par région et par département, non utilisés).
- Fichiers locaux : `python/data/municipales/prenoms/prenoms-2025-nat.csv` (724 645 lignes, utilisé) ; `prenoms-2024-nat.csv` (édition précédente, colonnes sans `rang`).
- Rôle : n'entre pas dans les chiffres de la carte ; sert à l'outil de représentativité (sexe et âge probables d'après le prénom) et à valider le proxy « sexe » sur la colonne `Sexe` des candidats.

| colonne | sens | utilisée ? |
|---|---|---|
| `sexe` | 1 garçon, 2 fille | oui : table sexe par prénom (`firstnames.json`) |
| `prenom` | prénom (agrégat `_PRENOMS_RARES` exclu) | oui : clé normalisée |
| `periode` | année de naissance | oui : distribution par décennie (âge probable) |
| `valeur` | nombre de naissances (arrondi à 5) | oui : poids |
| `rang` | rang du prénom dans l'année | non |

### H. Fichiers annexes du dossier

- `python/data/municipales/communes-epci.json` (code commune, code intercommunalité, nom) et `frontend/public/data/geo/epci.geojson` : jointure et noms des intercommunalités pour la carte de l'Atlas. Origine non documentée dans le script (probablement l'API Géo de l'État) : à vérifier.

## Ce qu'on n'exploite pas encore

- **L'âge des élus et des candidats élus** (`Date de naissance` du Répertoire, `DATNAIPSN` et `Date de naissance` des fichiers d'élus 2020 et 2026). C'est la réponse directe à la limite écrite sur la page (« une partie de la hausse peut tenir au renouvellement des générations ») : comparer 2020 et 2026 **à âge égal** (par décennie de naissance) dirait quelle part de la hausse est un effet de génération. Ordre de grandeur d'un recalcul rapide sur le Répertoire (non vérifié, agrégats) : 0,8 % chez les conseillers nés dans les années 1940, 2,0 % dans les années 1960, 3,5 % dans les années 1980, 4,6 % dans les années 2000. L'écart est fort : il pèse aussi dans le « filtre » vers les maires, plus âgés que leurs candidats.
- **Les adjoints** (`Libellé de la fonction`) : un palier intermédiaire entre conseillers sans fonction (2,9 % en ordre de grandeur) et maires (1,2 %) ; recalcul rapide : 2,6 % pour les adjoints. Permettrait de dire où se joue la marche, sans recourir aux maires seuls.
- **Le rang sur la liste** (`Ordre`) : position des noms « diversité » dans les listes (places éligibles ou fin de liste), indicateur plus fin que « tête de liste ou non ».
- **Le second tour 2026** (fichiers déjà en local) : compléter les élus 2026 sans s'en tenir au premier tour ; utile pour une photo 2026 complète (la comparaison à 2020 resterait au premier tour).
- **Le sexe croisé avec l'IDP** (`Sexe`, `Code sexe`) : la parité est imposée sur les listes ; la question « les femmes au nom « diversité » sont-elles plus ou moins souvent têtes de liste ? » reste un agrégat de groupe.
- **La profession déclarée** (`CODPRO` des élus, catégorie socio-professionnelle du Répertoire) : représentation sociale des conseils municipaux, dans l'esprit du dossier Assemblée (part de cadres et d'ouvriers chez les élus locaux contre la population de la commune).
- **La taille de la commune** (`EFFECTIF_LEGAL`, ou population Insee) : présenter l'évolution 2020-2026 par strate de commune donnerait une lecture « géographie » plus simple que la moyenne des communes.
- **La nationalité** (`Nationalité`, `Code nationalité`) : environ 6 300 candidats et 2 800 conseillers ressortissants de l'Union, autre mesure (juridique, non onomastique) de l'ouverture des listes ; permet aussi de vérifier qu'ils ne déforment pas l'IDP.
- **L'élection au conseil communautaire** (`CC`, `IND_ELU_EPCI`, `Election au CC`) et le fichier des conseillers communautaires du Répertoire : ajouter le palier intercommunal, où se décident beaucoup de compétences.
- **Les têtes de liste de 2014** : `resultats-communes-2014-t1-1000plus.txt` (en local) donne les têtes de liste des communes de 1 000 habitants et plus en 2014 ; une série 2014-2020-2026 des têtes de liste est faisable avec le même référentiel.
- **Le fichier des noms par département** (Insee, `noms2008dep`) : construire un repère « population » par département au lieu du seul 7 % national, ce qui rendrait la carte départementale lisible en écart à l'attendu plutôt qu'en niveau.
- **Les résultats électoraux** (voix par liste, `resultats-communes*.csv`) : piste à n'ouvrir qu'avec prudence (aucune lecture causale, agrégats seulement, aucun classement), par exemple la part des sièges obtenus par les listes selon le profil de leur tête de liste.

## Autres sources possibles

- **Répertoire national des élus, archives** : les versions antérieures du jeu (onglet historique de la page data.gouv.fr) permettraient de comparer les maires et adjoints de 2020 (après le second tour de juin 2020) à ceux de 2026, ce que la page dit impossible aujourd'hui. Existence d'une version de l'été 2020 à vérifier dans l'historique des ressources.
- **Répertoire national des élus, autres mandats** (même jeu) : conseillers départementaux, régionaux, sénateurs, députés ; même méthode pour une échelle complète des mandats.
- **Maires au 17/06/2020** (jeu D) : point de départ d'une comparaison des maires, à condition d'isoler ceux élus en 2020 (croisement avec les élus du premier tour et du second tour 2020).
- **Municipales 2020, second tour** (data.gouv.fr, ministère de l'Intérieur, jeu « résultats du second tour » de juin 2020) : compléter les élus 2020 ; existence et colonnes à vérifier.
- **Insee, recensement, thème « Immigrés et étrangers »** : part d'immigrés par commune ou département, repère local plus juste que 7 % national pour lire l'écart entre candidats et population ; disponibilité au niveau communal et définition à vérifier (et l'IDP n'est pas la même notion que le statut d'immigré).
- **Base communale Insee déjà en local** (`python/data/municipales/dossier_complet.csv`, recensement 2022) : âge et structure sociale des communes, pour une lecture « candidats contre population de leur commune » sur le sexe, l'âge et la catégorie sociale ; elle ne contient pas de variable d'immigration.

## Points de relecture

- **Deux champs différents dans la même carte.** Le chiffre (2,6 → 3,2 %) et les deux séries du texte portent sur les communes de 1 000 habitants et plus présentes les deux années ; la phrase « 2 % des têtes de liste contre 3 % de leurs colistiers » porte sur **toutes** les communes en 2026. À signaler (« en 2026, toutes communes ») ou à recalculer sur le même champ.
- **« Colistiers » inclut la tête de liste** dans le calcul (taux de toute la liste). L'écart réel tête / colistiers est donc un peu plus grand ; libellé à ajuster (« contre 3 % des candidats de leur liste ») ou calcul à corriger.
- **Effet de génération non mesuré** alors que les données le permettent (dates de naissance) : la hausse de 0,6 point peut tenir en grande partie au rajeunissement. Un chiffre « à âge égal » serait plus solide pour un verdict « Vrai ».
- **Noms non reconnus exclus** (11 % des candidats) : les noms les plus récents (apparus après 2000) ou rares ne sont pas dans le fichier Insee et sortent du dénominateur. Le biais va probablement vers une sous-estimation de l'IDP et peut varier entre 2020 et 2026 ; le taux de reconnaissance par année n'est pas publié dans le JSON. À ajouter comme contrôle.
- **Repère « 7 % de la population »** : constante reprise du rapport TEPP, non recalculée ; la population de référence (âge, année) n'est documentée ni sur la page ni dans `Methodologie.jsx`. Les élus sont des adultes, plus âgés que la population : le repère tous âges surestime probablement l'attendu. Vérifier dans le rapport (PDF local) et préciser.
- **Premier tour 2020 sous Covid** : abstention record ; les communes pourvues au premier tour en 2020 ne sont pas forcément comparables à celles de 2026 (la page le dit pour le second tour, pas pour la sélection des communes).
- **Classements nominatifs de lieux** : la page affiche « Les 12 plus divers / moins divers » (départements) et « Top 15 / Bottom 15 » (communes) et trie les nuances par IDP. Ce sont des lieux et des partis, pas des personnes, mais la présentation « top / bottom » se lit comme un palmarès, contraire à l'esprit des garde-fous. Envisager une carte seule, ou des classes, sans rang.
- **Nuances** : le script groupe sur le libellé (`Nuance de liste`), alors que le dictionnaire `NUANCE_LABELS` attend des codes ; il ne sert donc à rien (sans effet sur les chiffres). Les nuances ne couvrent que 35 % des candidats (communes nuancées) : à écrire sous le graphique.
- **Source affichée sur la carte** : elle pointe vers les résultats du premier tour 2026 seulement ; les candidatures 2026 et les fichiers 2020 sont cités sur la page mais pas sur la carte.
- **Répertoire national des élus** : mise à jour du 11/08/2026, « certaines mises à jour encore en cours » selon le producteur ; vérifier à la prochaine mise à jour trimestrielle que 1,2 % (maires) et 2,7 % (conseillers) tiennent.
- **Doublons de fichiers** : `municipales-2026.csv` et `candidatures-2026-t1.csv` sont identiques ; le commentaire du script mentionne des noms de fichiers du Répertoire différents des noms locaux (renommage à la main) : rien de faux, mais à documenter pour la relance.
- **Chiffre plus parlant possible** : « + 0,6 point en six ans » est exact mais abstrait ; « au rythme actuel, il faudrait N mandats pour atteindre le repère population » serait parlant, mais suppose un repère adulte fiable et une tendance linéaire : à n'écrire qu'avec ces réserves. Alternative sobre : « 1 conseiller élu sur 31 en 2026 contre 1 sur 38 en 2020 ».
