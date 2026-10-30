# Réutilisations à déclarer sur data.gouv.fr

> Préparé le 30/10/2026. À saisir par l'usager, avec le compte Outsiders (dataoutsiders@gmail.com), dans
> « Publier sur data.gouv.fr > Une réutilisation » (https://www.data.gouv.fr/admin/reuses/new/).
> Une réutilisation par dossier, reliée à tous les jeux qu'il utilise : la fiche apparaît alors sur la page
> de chacun de ces jeux, consultée par un public qui cherche justement ces données.
> Type : « Visualisation ». Image : l'image de partage de la page (`frontend/dist/og/<page>.png`, 1200 x 630).
> Ne déclarer qu'après la vérification des cartes de l'accueil et la correction éventuelle des chiffres.

## Ordre recommandé

| Priorité | Dossier | Pourquoi |
|---|---|---|
| 1 | Atlas et fiches territoire | Le cœur du site, reliable à beaucoup de jeux, utile à tout le monde |
| 2 | Qui s'enrichit, qui décroche ? | Nouveau, très local, parlant pour les collectivités |
| 3 | Le sport, miroir des inégalités ? | Jeu INJEP peu réutilisé : visibilité forte |
| 4 | École | IPS et valeur ajoutée, très consultés |
| 5 | Auto-écoles | Jeu très consulté, angle original (contexte égal) |
| Plus tard | Élus, Assemblée, Sélectivité (Parcoursup) | Sujets politiques ou proches du ministère de l'usager : ne pas les mettre en avant pour l'instant |

---

## 1. Atlas et fiches territoire

- **Titre** : Outsiders : la France par ses angles morts, de la commune au pays
- **URL** : https://dataoutsiders.fr/atlas
- **Image** : `og/atlas.png`
- **Description** :
  > Une carte de France qui croise deux indicateurs publics (revenu, école, logement, diplômes, âge, natalité…) et fait remonter les « outsiders » : les territoires qui réussissent ou décrochent par rapport à ce que leur profil laissait attendre. Pour chaque commune, une fiche menée par ce qui la rend inhabituelle, avec son jumeau statistique. Toutes les sources sont citées et le contenu est sous licence CC BY.
- **Jeux à relier** :
  - Indices de position sociale des écoles (à partir de 2022) : https://www.data.gouv.fr/datasets/indices-de-position-sociale-dans-les-ecoles-a-partir-de-2022
  - Indices de position sociale des collèges (à partir de 2023) : https://www.data.gouv.fr/datasets/ips-colleges-a-partir-de-2023
  - Indices de position sociale des lycées (à partir de 2023) : https://www.data.gouv.fr/datasets/ips-lycees-a-partir-de-2023
  - Indicateurs de valeur ajoutée des lycées d'enseignement général et technologique : https://www.data.gouv.fr/datasets/indicateurs-de-valeur-ajoutee-des-lycees-denseignement-general-et-technologique-2
  - Demandes de valeurs foncières : https://www.data.gouv.fr/datasets/demandes-de-valeurs-foncieres
- **Mots clés** : inégalités, territoires, communes, cartographie, école, revenus

## 2. Qui s'enrichit, qui décroche ?

- **Titre** : Qui s'enrichit, qui décroche ? La place de chaque commune dans la hiérarchie des revenus, 2014-2021
- **URL** : https://dataoutsiders.fr/terrains/revenus
- **Image** : `og/terrains-revenus.png`
- **Description** :
  > Partout, les revenus augmentent ; la question est de savoir quelles villes montent dans la hiérarchie des niveaux de vie et lesquelles reculent. De 2014 à 2021 (Insee, Filosofi), les communes limitrophes de Paris montent pendant que la grande couronne pavillonnaire décroche. Classements, carte des intercommunalités et recherche pour 5 000 communes, avec un contrôle sur 2023.
- **Jeux à relier** : les données Filosofi sont publiées sur insee.fr et non comme jeu de données principal sur data.gouv.fr. Relier à défaut : Revenus, pauvreté et niveau de vie, données carroyées 2019 et 2021 : https://www.data.gouv.fr/datasets/revenus-pauvrete-et-niveau-de-vie-donnees-carroyees-2019-et-2021-dispositif-fichier-localise-social-et-fiscal-filosofi
- **Mots clés** : revenus, niveau de vie, gentrification, banlieue, Filosofi, communes

## 3. Le sport, miroir des inégalités ?

- **Titre** : Le sport, miroir des inégalités ? Licences, clubs et équipements dans les quartiers et les territoires
- **URL** : https://dataoutsiders.fr/terrains/sport
- **Image** : `og/terrains-sport.png`
- **Description** :
  > Le foot, sport des quartiers ? Les filles arrêtent-elles plus tôt ? Les quartiers manquent-ils de clubs ou de licenciés ? À partir du recensement des licences et des clubs (INJEP) et des équipements sportifs, comparaison des quartiers prioritaires avec le reste de leur commune, des communes selon leur revenu, et évolution depuis 2013.
- **Jeux à relier** :
  - Données géocodées issues du recensement des licences et clubs (INJEP) : https://www.data.gouv.fr/datasets/donnees-geocodees-issues-du-recensement-des-licences-et-clubs-aupres-des-federations-sportives-agreees-par-le-ministere-charge-des-sports
  - Recensement des équipements sportifs : le jeu national du ministère n'a pas été trouvé par la recherche ; chercher « Data ES » ou « équipements sportifs » au moment de la saisie (l'entrée trouvée, « Recensement des équipements sportifs (RES) », est publiée par Géo2France, à ne relier que si c'est bien le fichier national).
- **Mots clés** : sport, licences, quartiers prioritaires, inégalités, équipements sportifs
- **Attention** : l'encadré « L'élite » de cette page porte sur la diversité des noms. La description ci-dessus n'en parle pas, volontairement.

## 4. École

- **Titre** : L'école trie-t-elle ? Position sociale et valeur ajoutée des établissements
- **URL** : https://dataoutsiders.fr/terrains/ecole
- **Image** : `og/terrains-ecole.png`
- **Description** :
  > Carte des écoles, collèges et lycées selon l'indice de position sociale de leurs élèves, public et privé, et valeur ajoutée des lycées : quels établissements font mieux que ce que leur public laissait attendre ? Recherche par établissement et croisement avec la richesse des communes.
- **Jeux à relier** : les quatre jeux IPS et valeur ajoutée du dossier 1, plus « Indicateurs de valeur ajoutée des lycées d'enseignement professionnel » : https://www.data.gouv.fr/datasets/indicateurs-de-valeur-ajoutee-des-lycees-denseignement-professionnel
- **Mots clés** : école, IPS, mixité sociale, valeur ajoutée, lycées, collèges

## 5. Auto-écoles

- **Titre** : Quelle auto-école forme le mieux, à contexte égal ?
- **URL** : https://dataoutsiders.fr/terrains/auto-ecoles
- **Image** : `og/terrains-auto-ecoles.png`
- **Description** :
  > 7 922 auto-écoles comparées non pas sur leur taux brut de réussite au permis, mais sur ce que leur contexte laissait attendre : le taux publié dépend pour un quart du département de l'examen, et aussi de la ville. Recherche par auto-école et carte.
- **Jeux à relier** : Liste des auto-écoles et taux de réussite au permis de conduire : https://www.data.gouv.fr/datasets/liste-des-auto-ecoles-et-taux-de-reussite-au-permis-de-conduire
- **Mots clés** : permis de conduire, auto-écoles, taux de réussite, contexte

---

## Plus tard, après décision de l'usager

- **Élus** (Municipales 2026 et Répertoire national des élus : https://www.data.gouv.fr/datasets/elections-municipales-2026-listes-candidates-au-premier-tour , https://www.data.gouv.fr/datasets/repertoire-national-des-elus-1) : dossier qui classe la diversité des noms par parti, sujet politique.
- **Assemblée** : données de l'Assemblée nationale, hors data.gouv.fr.
- **Sélectivité (Parcoursup)** : domaine du ministère de l'usager, à ne pas mettre en avant tant qu'il y est en poste.
- **Outil Représentativité** (fichier des prénoms : https://www.data.gouv.fr/datasets/fichier-des-prenoms-depuis-1900) : outil sensible, ne pas le mettre en avant.
