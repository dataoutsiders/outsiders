# Outsiders, présentation complète de l'outil

> **Comprendre la France par ses angles morts.**
> Une plateforme qui rend lisibles des données publiques sous-exploitées, du niveau national jusqu'à la commune.

- **En ligne** : https://dataoutsiders.fr/ (ancienne adresse toujours active : https://outsiders-pu2.pages.dev/)
- **Contact public** : contact@dataoutsiders.fr (redirigé par Cloudflare Email Routing) ; compte technique : dataoutsiders@gmail.com
- **Dernière mise à jour de ce document** : 30 octobre 2026 (soir)
- **Documents liés** : cadrage et sujets (`docs/vision-et-sujets.md`), veille de données ouvertes (`docs/veille-open-data.md`), déploiement (`docs/DEPLOIEMENT.md`), ajouter une unité d'analyse (`docs/AJOUTER_UN_DECOUPAGE.md`), design (`docs/design.md`), vérification des cartes de l'accueil (`docs/verification_cartes_accueil.md`), millésimes (`docs/millesimes_20261030.md`), fiches territoire (`docs/fiches_territoire_20261030.md`), sport (`docs/sport/`), PISA (`docs/international/`), promotion (`docs/promotion/`), idées en réflexion (`docs/idees/`).

---

## 1. En une phrase

Outsiders est un explorateur de données publiques françaises : on choisit **une unité d'analyse** (un territoire, un milieu social, un sexe, une classe d'âge), **un indicateur** (revenu, école, logement, natalité, diversité...) et **un mode de lecture** (carte, fiche, tableau de bord). Tout est pré-calculé et consultable sans compte, et chaque chiffre cite sa source d'origine.

---

## 2. Mission et positionnement

Beaucoup de données publiques françaises (INSEE, Éducation nationale, DVF, état civil, enquêtes ministérielles) sont riches mais peu lues, parce qu'elles arrivent sous forme de gros fichiers techniques. Outsiders les met en forme pour **situer la France** : se comparer dans l'espace (national contre local) et révéler les écarts qu'on ne voit pas au premier regard.

- **Sujet numéro 1 : les inégalités et les discriminations** (âge, sexe, origine, milieu social, territoire). C'est l'axe historique et le plus développé, sans être le seul.
- **Axe unificateur : situer la France**, sur ses différences internes comme dans la comparaison.
- **Discipline anti-fourre-tout** : un sujet n'entre que s'il passe trois tests (donnée sous-exploitée, angle tranché, livrable réutilisable). Pas de greffe hors marque (par exemple, pas de prédiction de scores sportifs).

**Esprit éditorial.** L'outil cherche les **angles morts** : ce que les chiffres dominants laissent dans l'ombre. Cela suppose de déconstruire les évidences (ce qui se présente comme « normal » est souvent socialement situé) sans surinterpréter les données. Clin d'oeil assumé mais léger à la sociologie des marges (Howard Becker, *Outsiders*, 1963), d'où le nom.

---

## 3. La colonne vertébrale : Découpage × Indicateur × Mode

Tout le produit repose sur trois axes orthogonaux.

| Axe | Ce que c'est | Exemples |
|-----|--------------|----------|
| **Découpage (unité)** | Ce qu'est une ligne d'analyse | Territoire, Milieu social, Sexe, Âge |
| **Indicateur** | Ce qu'on mesure | Revenu médian, IPS de l'école, taux de natalité, diversité... |
| **Mode de lecture** | Comment on regarde | Carte (si l'unité est géographique), Fiche, Tableau de bord |

Conséquence concrète : **ajouter une unité d'analyse = activer un découpage**, pas réécrire l'application. Le territoire est le cas particulier qui débloque la carte ; toutes les autres unités passent par un moteur de rendu générique. Piège à garder en tête : le sexe comme **unité** (les lignes sont « femmes » et « hommes ») n'est pas la même chose que le sexe comme **dimension mesurée** d'une autre unité.

---

## 4. Navigation : la home mène par les questions, le menu par les tâches

**La page d'accueil** mène par des **cartes-questions** (idées reçues déconstruites par les données) :
une accroche, un verdict, un chiffre cité et cliquable vers la vue exacte qui le prouve. Objectif :
attirer journalistes, décideurs et curieux par une question concrète, pas par une taxonomie.
Ordre de la page : titre et une phrase, les cartes, puis « Et chez vous ? » (recherche de territoire avec trois
exemples : Marseille, Seine-Saint-Denis, Bretagne), les outils, la newsletter.

**Sur téléphone** (pensé comme une application) :
- les cartes défilent dans un **carrousel horizontal** (une carte entière visible dès l'arrivée, le bord de la
  suivante invite à glisser) ; texte de la carte limité à deux lignes, le reste est dans le fil et le dossier ;
- **le fil** (`/fil`, `pages/Fil.jsx`) : les mêmes cartes en plein écran, une par écran, défilement vertical
  aimanté comme des stories ; boutons « Voir la preuve » et « Partager » (menu de partage du téléphone, ou copie
  du lien) ; `?q=<id>` ouvre le fil sur une carte (lien partagé) ; dernier écran : carte, dossiers, newsletter ;
- une **barre d'onglets** en bas (`components/BarreOnglets.jsx` : Accueil, Le fil, Carte, Territoires,
  Dossiers), cachée à partir de la tablette ; la mise en page réserve sa hauteur ;
- le site est une **application web installable** (`public/manifest.webmanifest`, icônes produites par
  `scripts/generate-icons.mjs` : points blancs sur une droite et un point rouge à l'écart). Bouton
  « Installer l'application » (Android, ordinateur) ou consigne iPhone (`components/InstallerApplication.jsx`)
  dans le pied de page et à la fin du fil. Pas de fonctionnement hors connexion (pas de service worker,
  volontairement : pas de chiffres périmés en cache). Ouverture depuis l'application mesurée par
  `/?source=application` ;
- les champs de saisie font 16 px sur téléphone (sinon l'iPhone zoome au toucher, `index.css`).
Mesures faites dans un cadre de 390 x 660 px : la première carte de l'accueil tient au-dessus de la barre
d'onglets, chaque écran du fil tient sans chevaucher la barre du haut ni le compteur.

**Défilement entre les pages** (`components/GestionDefilement.jsx`) : nouvelle page en haut, lien vers une
section (`#ancre`) sur la section sous l'en-tête, retour du navigateur laissé au navigateur. Le saut est
instantané : `index.css` rend le défilement animé, et une animation interrompue par le chargement de la page
laissait l'usager en bas de page. `/territoires` change de page quand `code` ou `niveau` change ; l'Atlas non.

**Le menu** est rangé par tâche, pas par type d'objet. Deux portes :

- **Outils** : des instruments qu'on fait tourner soi-même (la carte / Atlas et la fiche territoire ;
  les comparateurs de groupes milieu social / sexe / âge ; le test de représentativité d'un fichier).
- **Dossiers** : des récits prêts à lire qui s'appuient sur les données : France en Europe, PISA 2025, Villes, Revenus, Sport, École, Élus, Assemblée, Sélectivité, Auto-écoles.
- En méta, à droite : **Méthodologie** et **À propos**. En pied de page : **Presse et réutilisation**, **Newsletter**, **Vrai ou faux, le fil**, **Travailler avec nous**, **Mentions légales**, et l'inscription à la newsletter.

**Vérification des cartes de l'accueil.** Chaque carte a été vérifiée le 30/10/2026 (chiffre retrouvé dans les données, source, logique du verdict, formulation, fraîcheur) et corrigée au besoin : `docs/verification_cartes_accueil.md`. Les cartes sont exportées (`QUESTIONS`, `VERDICTS` dans `pages/Home.jsx`) et relues par la page presse et le fil : un chiffre corrigé l'est partout.

**Relecture carte par carte** (en cours, menée par l'usager) : une fiche par carte dans `docs/relecture/`
(données utilisées, liens de téléchargement, toutes les colonnes disponibles, pistes d'amélioration) ; sommaire,
défauts en ligne restant à corriger et tableau des décisions dans `docs/relecture/README.md`.

*(Les Thèmes, un angle vu sur tous les terrains, existent mais sont masqués de la navigation tant qu'un
seul terrain est mesuré ; ils rouvriront avec un 2e terrain comparable, par exemple le sport.)*

---

## 5. Le produit, écran par écran

### 5.1 Explorer un territoire : l'Atlas (la carte de France)

Route : `/atlas?i=<indicateur>&m=<maille>&dep=<code>&vs=<autre indicateur>`. L'état est **entièrement dans l'URL**, donc chaque vue est un lien partageable.

- **Mailles au niveau national** :
  - **Départements** (choroplèthe) : la vue par défaut ; un clic sur un département descend à ses communes.
  - **EPCI** (intercommunalités, environ 1 250 mailles) : choroplèthe zoomable, sans descente.
  - **Établissements** (points) : uniquement pour les indicateurs scolaires, points zoomables des établissements.
- **Vue départementale** : après un clic sur un département, choroplèthe **par commune** ; un clic sur une commune ouvre sa **fiche territoire**.
- **Croiser deux indicateurs, et révéler les outsiders** : le paramètre `vs` ajoute un nuage de points (par exemple IPS de l'école contre revenu). Une **droite de pronostic** (régression) apparaît, et avec elle les territoires qui s'en **écartent le plus**, au-dessus comme en dessous : ceux qui réussissent ou échouent contre ce que leur profil laissait attendre. Écarts mesurés en résidus studentisés, filtre de population pour écarter le bruit des petites communes, R² affiché, tout calculé dans le navigateur. C'est le coeur distinctif du site : on ne montre pas le niveau brut, on montre l'écart à l'attendu.
- **20 indicateurs** répartis en 6 groupes (voir le catalogue, section 6).
- **Intégrer ailleurs** : un bouton « Intégrer » copie un code `<iframe>` qui pointe vers une vue épurée (`/embed/carte` pour une choroplèthe, `/embed/croisement` pour le nuage des outsiders), avec la source citée et un lien retour. Un journaliste republie une carte sourcée en deux clics.

L'Atlas est **la** carte de France du site : les dossiers ne refont pas de carte départementale, ils renvoient vers l'Atlas.

### 5.2 Explorer un territoire : Territoires (fiche et tableau de bord)

Route : `/territoires?code=<code INSEE>` (commune ou département), `/territoires?niveau=epci&code=<SIREN>` (intercommunalité ; un SIREN de 9 chiffres suffit aussi sans `niveau`), `/territoires?niveau=region&code=<code région Insee>` (région). Navigation commune → intercommunalité → département → région par le fil « Fait partie de ». Rubrique « Dans nos dossiers » : ce que chaque dossier publie sur le territoire, à son échelle, lu dans le registre `src/config/dossiersTerritoires.js` (voir `docs/fiches_territoire_20261030.md`).

- **Sans code** : un **tableau de bord national**. Chaque indicateur est résumé par la médiane des départements, une bande P10 à P90 et les extrêmes, regroupé par thème.
- **Avec un code** (commune, intercommunalité, département ou région) : une **fiche territoire** qui **mène par les atypies**. En tête, un bloc « Ce qui sort de l'ordinaire » remonte les indicateurs où le territoire s'écarte le plus de sa référence, et la **référence est au choix** : la France, son département, ou les communes de sa taille (le caractère atypique dépend de ce à quoi on compare, et le montrer est honnête). Vient ensuite le **jumeau statistique** : la commune qui lui ressemble le plus dans l'espace des indicateurs standardisés (z-scores), sa distance en km, et son anti-jumeau à taille comparable. Puis chaque indicateur **situé par rapport au reste de la France** (jauge de percentile) et un bloc « Ce que ça veut dire » qui combine plusieurs indicateurs (par exemple : IPS bas mais valeur ajoutée positive = « une école qui compense plutôt qu'une école qui échoue » ; prix de l'immobilier très supérieur au revenu = tension immobilière).
- **Dans nos dossiers** : pour le territoire affiché, ce que chaque dossier publie à cette échelle (une ou deux phrases, le chiffre, la précaution du dossier, un lien qui ouvre le dossier sur le territoire quand c'est possible). Un test (`src/lib/__tests__/dossiersTerritoires.test.js`) échoue si un fichier de dossier contenant des données par territoire n'est ni inscrit au registre ni exclu avec un motif. Garde-fous : rien de l'encadré « L'élite » du dossier Sport ; Élus au département seulement, avec la phrase de précaution ; aucun palmarès.
- **Intercommunalité** : socle d'indicateurs, jumeau parmi les intercommunalités, communes membres. **Région** : valeurs officielles de l'Insee à l'échelle régionale, ou recalculées comme au département ; jamais de moyenne de médianes ; pas de prix immobilier (DVF ne publie pas d'échelle régionale).
- Recherche avec autocomplétion insensible aux accents (environ 34 700 communes, 1 255 intercommunalités, 101 départements, 18 régions).

### 5.3 Explorer les autres unités : Milieu social, Sexe, Âge

Route : `/explorer/:id` (un moteur de rendu unique, `UnitView`).

Quatre unités non géographiques sont actives :

- **Milieu social** (catégories socioprofessionnelles) : niveau de vie, taux de pauvreté, chômage, espérance de vie à 35 ans, abstention, part de pratiques numériques d'information.
- **Sexe** (femmes, hommes) : salaire en équivalent temps plein, taux d'emploi 2025 (le taux d'activité 2018 affiché jusqu'au 30/10/2026 a été remplacé), temps partiel, espérance de vie à la naissance, pension de droit direct.
- **Âge** (tranches de 15-17 ans à 70 ans et plus) : comment on s'informe (sources numériques contre traditionnelles, plateformes), à partir de l'enquête ARCOM 2024.
- **Pays** (« Où se situe la France ? », 30 pays : UE27 + Islande, Norvège, Suisse) : dépenses publiques, pauvreté des enfants, espérance de vie, mortalité infantile, décrochage scolaire, Gini, emploi des seniors, heures des temps pleins. Sources Eurostat 2025 (2024 pour la santé), moyenne UE27 affichée en repère. C'est la seconde branche de l'axe « situer la France » (le comparé, après l'interne).

Deux modes de lecture, plus une présentation soignée :

- **Tableau de bord** avec bascule **Tableau (heatmap) / Barres**. Dans la heatmap, les indicateurs sont en lignes, les catégories en colonnes, et la **couleur est calculée par ligne** : des euros, des pourcentages et des années peuvent donc cohabiter. Tri par défaut sur la colonne **« Écart »** (rapport entre le maximum et le minimum) pour faire remonter les inégalités les plus fortes.
- **Fiche** d'une catégorie (`?cat=<id>`) : son rang parmi les catégories, une jauge, et la détection automatique des indicateurs où elle est à l'extrême favorable ou défavorable.
- **Thèmes d'indicateurs** : les indicateurs sont regroupés en sections pour ne pas tout mélanger.
- **Couleur neutre** pour les indicateurs de comportement (par exemple le numérique) : un dégradé de bleu sans jugement de valeur, là où les indicateurs de bien-être utilisent vert (favorable) et rouge (défavorable).
- **Notes de bas de page** : chaque indicateur porte un numéro en exposant qui renvoie à une bibliographie complète en bas de page, avec lien vers la source.

### 5.4 Outils : la Représentativité (moteur onomastique)

Route : `/outils/representativite`.

On colle une liste de noms (par exemple les candidats d'une liste, les membres d'une équipe) et l'outil estime trois choses, **entièrement dans le navigateur** : la **diversité des noms** (indice IDP, indicateur de groupe, pas une origine ; résultat masqué sous 30 noms reconnus), le **sexe** et la **structure d'âge**. Aucun nom n'est envoyé à un serveur (voir section 7).

### 5.5 Dossiers : Terrains et Thèmes

- **Terrains et études** (une population ou une question, vues sous tous les angles) :
  - **France en Europe** (`/international`) : « où se situe la France ? ». Dossier mené par l'analyse :
    3 chiffres en bref, carte d'identité européenne (un dot-plot par indicateur : intervalle des 30 pays,
    point France, repère UE27), quatre histoires (l'État et les enfants, le paradoxe sanitaire, école et
    égalité, le travail), **nuage de pronostic entre pays** (que rapporte la dépense publique ?) et
    **trajectoires France vs moyenne UE27 depuis 1995** (la preuve du décrochage sanitaire : mortalité
    infantile meilleure que l'UE jusqu'en 2012, au-dessus depuis 2015). Le classement interactif et les
    fiches pays restent sur `/explorer/pays`.
  - **Villes / ségrégation** (`/segregation`) : « riches et pauvres vivent-ils séparés ? ». Analyse
    nationale menée par les chiffres (accroche → chiffres nationaux → territoire → explorateur → classement,
    recherche de ville en secondaire). Trois axes par ville, toujours en **valeurs concrètes** : le
    **niveau de vie** (médiane, le cadre), le **mélange dans un quartier** (rapport interdécile D9/D1 des
    IRIS FiLoSoFi : ×3,8 en grande ville contre ×3,0 en petite), et l'**écart entre quartiers**. Plus la
    **composition des quartiers** (mixtes / homogènes aisés / pauvres), l'**âge**, une **carte des carreaux
    de 200 m**, et un bloc « Et l'école ? ». **Lecture territoriale** (tous les IRIS agrégés par
    département) avec bascule Régions / Départements : l'Île-de-France, PACA, le Grand Est en tête. Un
    **explorateur** (nuage outsiders) à axes configurables, filtrable par région ou département, avec
    recherche d'une ville. Finding : contre-intuitivement, les grandes villes mélangent davantage à
    l'échelle du quartier que bien des petites villes zonées.
  - **École** (`/terrains/ecole`) : carte des établissements en points, indice de position sociale et valeur ajoutée par niveau et par secteur (public, privé), recherche par établissement, croisement avec la richesse.
  - **Revenus** (`/terrains/revenus`) : « qui s'enrichit, qui décroche ? ». Position de chaque commune dans la hiérarchie des niveaux de vie, Filosofi 2014 et 2021, contrôle sur 2023 ; les communes limitrophes de Paris montent, la grande couronne pavillonnaire recule ; carte des intercommunalités (palette divergente rouge / vert) ; `?ville=<code>` ouvre une commune.
  - **Sport** (`/terrains/sport`) : « le sport, miroir des inégalités ? ». Licences et clubs INJEP 2023, équipements Data ES, quartiers prioritaires contre reste de leur commune, revenu des communes, évolution depuis 2013, offre et demande. Règle : les licences sont comptées par fédération ; les fédérations multisports (codes 4xx et 5xx, 13 % des licences) comptent dans les totaux mais jamais dans les comparaisons par sport, et « football » désigne la seule FFF, comme dans les statistiques officielles. Encadré « L'élite : qui accède au haut niveau ? » : diversité des noms des internationaux nés en France, en fourchette par rapport à leur génération, et lieux de naissance ; agrégats seulement, rien par joueur, rien sous 30 noms, aucun classement de départements (`docs/sport/exploration_elite.md`).
  - **Auto-écoles** (`/terrains/auto-ecoles`) : taux de réussite au permis comparé à ce que le contexte laisse attendre ; `?dep=<code>` ouvre un département.
  - **PISA 2025** (`/international/pisa`) : « la France décroche-t-elle ? ». France seule, comparée à la moyenne de l'OCDE et aux 23 pays de l'OCDE présents depuis 2000 ; rang toujours avec sa fourchette (calculée par Outsiders) ; score attendu selon la richesse et le profil social ; ce que la critique dit de vrai ; l'indice social n'est pas comparé dans le temps (méthode changée en 2025). Décision : la Turquie n'est ni nommée ni mise en avant (`docs/international/`).
  - **Élus** (`/terrains/elus`) : diversité des noms des candidats et élus aux municipales, **comparaison 2020-2026 dans les mêmes communes** (candidats 5,4 puis 6,2 % ; têtes de liste 2,5 puis 3,3 % ; élus du premier tour 2,6 puis 3,2 %), filtre situé au choix des têtes de liste, effet géographique (÷ 3,7 brut contre ÷ 1,9 commune par commune), classements par parti.
  - **Assemblée** (`/terrains/assemblee`) : « qui représente qui ? ». 577 députés et 2 060 collaborateurs
    parlementaires au miroir de la France : profession (nomenclature INSEE fournie par l'AN), sexe, âge et
    diversité des noms (IDP), groupe par groupe avec repères population (INSEE, TEPP). Findings : 66 % de
    cadres (22 % des personnes en emploi), 6 députés ouvriers ; côté noms, 4,2 % des députés contre 6,4 %
    des collaborateurs : un écart à confirmer (non significatif). Diversité par groupe masquée sous 30 noms reconnus.
  - **Sélectivité** (`/terrains/selectivite`) : « qui peut entrer dans le supérieur ? ». Les 14 000
    formations Parcoursup au crible du taux d'accès : la hiérarchie réelle de la sélection (le sport et
    les arts ferment plus que la prépa), la licence « ouverte à tous » devenue minoritaire (33 %, de 20 %
    en Île-de-France à 100 % outre-mer), la matrice académie × filière (à vœu égal, l'accès dépend de où
    l'on habite), et le gradient social des admis boursiers (écoles de commerce 5 %, BTS 29 %).
  - À venir : entreprises, presse (voir `docs/idees/presse_europresse.md`).
- **Thèmes** (une dimension, vue sur tous les terrains) : diversité, genre, âge. Masqués tant qu'un seul terrain est mesuré.

### 5.6 Presse et réutilisation

Route : `/presse`. Les résultats à reprendre (cartes de l'accueil hors Élus, Assemblée et Sélectivité), chacun avec un bouton qui copie une phrase et sa source ; la formule de citation et la licence ; le mode d'emploi du bouton « Intégrer » avec un exemple de code ; les images de partage téléchargeables ; le contact (« nous répondons par écrit »).

---

## 6. Le catalogue d'indicateurs de l'Atlas

20 indicateurs, tous disponibles aux trois mailles de la carte (département, EPCI, commune), et dans les fiches région sauf le prix. Toutes les valeurs INSEE issues du recensement portent sur le millésime 2023 (géographie au 1er janvier 2026).

| Groupe | Indicateur | Unité | Source |
|--------|-----------|-------|--------|
| **École** | IPS écoles, collèges, lycées (public) | indice | Éducation nationale, IPS |
| **École** | Valeur ajoutée des lycées | points | Éducation nationale, IVAL |
| **Richesse** | Revenu médian (niveau de vie médian) | € / an | Insee, Filosofi 2023 (valeurs officielles commune, département, EPCI ; module `revenu_filosofi.py`) |
| **Richesse** | Prix immobilier au m² | € / m² | Statistiques DVF (Etalab), fichier du 21/10/2026, ventes de juillet 2021 à juin 2026 ; médiane officielle aussi pour les EPCI |
| **Représentation politique** | Diversité des candidats (IDP) | % | Candidatures municipales 2026 + moteur IDP ; EPCI et régions calculés sur l'ensemble de leurs candidats (au moins 50 noms reconnus), jamais en médiane de communes |
| **Population** | Diplômés du supérieur | % | INSEE, recensement (diplômes) |
| **Population** | Cadres, professions intermédiaires, employés, ouvriers | % | INSEE, recensement (emploi) |
| **Logement** | HLM, résidences secondaires, logements vacants, propriétaires, maisons individuelles | % | INSEE, recensement (logement) |
| **Démographie** | Jeunes (0-14 ans), 65 ans et plus | % | INSEE, recensement (population) |
| **Démographie** | Taux de natalité | ‰ | INSEE, état civil (naissances 2021-2025) + recensement |

Le registre technique vit dans `frontend/src/config/indicateurs.js` : chaque indicateur sait où lire sa valeur, comment la formater, à quelles mailles il s'applique, et porte sa source avec un lien cliquable.

---

## 7. Le moteur d'inférence onomastique

Un seul moteur, trois lentilles, **100 % côté navigateur** (les noms ne quittent jamais l'appareil de l'utilisateur).

- **Origine / diversité** : indice IDP (Kheddache et L'Horty, 2023), à partir du fichier INSEE des noms de famille. Un nom est compté comme « issu de la diversité » s'il est absent des naissances en France avant 1950 ou multiplié par 15 après.
- **Sexe** : taux de féminisation, via le fichier INSEE des prénoms.
- **Âge** : structure d'âge, via la période de naissance associée aux prénoms.

**Validation** : l'IDP des candidats municipaux reproduit l'étude d'origine (environ 4,4 %) ; le proxy de sexe atteint environ 99 % de précision sur la part couverte.

**Limites toujours affichées** : le proxy est attaché au nom, pas à la personne (fiable en agrégé, bruité à l'individu) ; le référentiel ne couvre que les naissances en France ; l'IDP capte la migration postérieure à 1950 et sous-estime donc certaines diversités plus anciennes (cas des Antilles, à signaler quand des territoires d'outre-mer apparaissent dans un classement).

---

## 8. Architecture technique

### Principe : tout est pré-calculé

Il n'y a **pas de backend** qui tourne en production. Des scripts Python jouent le rôle de « cuisine » : ils téléchargent les données publiques, calculent les indicateurs, et écrivent des fichiers JSON statiques. Le site React ne fait que lire ces fichiers. C'est rapide, gratuit à héberger, et robuste.

```
Sources publiques (CSV, XLSX, GeoJSON, API)
        ↓   scripts python/tools/*.py (au moment de la mise à jour)
JSON pré-calculés  →  frontend/public/data/
        ↓   React lit les JSON au runtime
Site interactif (cartes, fiches, tableaux)
```

### Frontend

- **React 19**, **Vite 7**, **Tailwind CSS 4** (pas de bibliothèque de composants imposée, pour rester générique côté éditorial et dataviz).
- **react-router-dom 7** ; l'état des vues passe par l'URL (`useSearchParams`), d'où des liens profonds partageables.
- **Leaflet** pour les cartes (choroplèthes et points), insensible au sens d'enroulement des polygones ; **recharts** pour les graphiques.
- **Code-splitting** par route (`lazy` / `Suspense`) : Leaflet et recharts ne sont chargés que sur les pages qui les utilisent.

### Hébergement

- **Cloudflare Pages** (compte dataoutsiders@gmail.com), projet `outsiders`, CDN mondial, gratuit, statique.
- Repli SPA via `frontend/public/_redirects` (`/* /index.html 200`) pour que les liens profonds fonctionnent.
- Déploiement en une commande depuis `frontend/` : **`npm run deploy`** (build Vite puis publication Wrangler). Détails et comptes dans `docs/DEPLOIEMENT.md`.

### Référencement et partage

Chaque route a son **titre**, sa **description** et son **image de partage** (Open Graph), source unique
dans `frontend/src/config/seo.js`. Le site étant une SPA sans serveur, deux scripts post-build génèrent,
à partir de cette config : une **image 1200×630 par route** (`scripts/generate-og.mjs`, satori + resvg,
identité tricolore) et un **fichier HTML par route** avec les bonnes balises (`scripts/prerender-meta.mjs`),
pour que les aperçus soient corrects quand un lien est partagé sur les réseaux. Un hook (`lib/meta.js`)
met aussi le titre à jour au fil de la navigation.

### Sauvegarde et historique (Git)

Depuis le 30/10/2026, le dossier est un dépôt Git, sauvegardé dans le dépôt **privé** GitHub
`dataoutsiders/outsiders`. Identité **locale au dépôt** : « Outsiders » et l'adresse anonyme de GitHub (l'identité
Git globale de la machine est nominative). Hors du dépôt : données brutes (`python/data/`), caches, `_archive/`,
`.bak`, réglages locaux. Après chaque lot de modifications : enregistrement (commit) puis envoi (push).
Détails : `docs/DEPLOIEMENT.md`, §2 et §4 D.

### Statistiques de fréquentation

Mesurées par **GoatCounter** (sans cookies, sans bandeau de consentement, visites `localhost` ignorées),
tableau de bord `outsiders.goatcounter.com` (connexion de l'usager). Les navigations internes de la SPA sont comptées par un hook
dédié (`lib/analytics.js`), sinon seule la page d'entrée le serait. Depuis le 30/10/2026, des **événements** (fonction `trackEvent`)
comptent des actions, jamais des personnes : fiche consultée (`fiche/<niveau>/<code>`), clic vers un dossier depuis une fiche,
croisement choisi dans l'Atlas, code d'intégration copié, phrase, formule, code ou image repris sur `/presse`, analyse lancée
dans l'outil Représentativité (sans son contenu). Les cartes intégrées ailleurs sont comptées comme pages `/embed/...`, avec le
site d'accueil en provenance. Pour ne pas compter ses propres visites : ouvrir une fois `https://dataoutsiders.fr/#toggle-goatcounter`
dans chaque navigateur. Liste à jour : `docs/idees/statistiques_usages.md`. Ajoutés ensuite : `accueil-carte/<id>`,
`accueil-recherche`, `accueil-exemple`, `fil-vue/<id>`, `fil-preuve/<id>`, `fil-partage/<id>`, `onglet/<nom>`,
`application-proposee`, `application-installee`, `newsletter-inscription/<page>`.

### Vie privée

Les calculs sensibles (analyse de noms) se font intégralement dans le navigateur. Aucune donnée personnelle saisie par l'utilisateur n'est transmise ni stockée côté serveur. Seule exception, volontaire : l'adresse donnée pour la newsletter, envoyée directement à Brevo et conservée chez lui jusqu'à la désinscription (voir `docs/DEPLOIEMENT.md`, §5 bis).

### Newsletter

En place depuis le 30/10/2026 : Brevo (formule gratuite), domaine authentifié, liste « Newsletter Outsiders », inscription sans mail de confirmation. Formulaire maison sans script tiers (`components/NewsletterForm.jsx`, `config/newsletter.js`) sur `/newsletter`, l'accueil, `/presse` et le pied de page. Détails, enregistrements DNS et règles d'envoi : `docs/DEPLOIEMENT.md`, §5 bis.

---

## 9. Sources de données

Toutes ouvertes, toujours citées avec un lien vers l'origine (jamais créditées à Outsiders).

- **Éducation nationale** : indice de position sociale (IPS) des écoles, collèges et lycées ; indicateurs de valeur ajoutée des lycées (IVAL).
- **INSEE** : recensement 2023 (diplômes, logement, emploi et catégories socioprofessionnelles, structure de population) ; revenus Filosofi ; état civil (naissances) ; ERFS et enquête Emploi ; mortalité par catégorie sociale.
- **DVF / Etalab** : demandes de valeurs foncières (prix de l'immobilier).
- **Anses** : étude INCA 3 (2014-2015) ; **Santé publique France (Odissé)** : Baromètre 2024 ; **Insee** : prix moyens de vente au détail 2014-2015 ; **Drees** : accessibilité potentielle localisée (APL) 2024 ; **Assurance maladie (data.ameli.fr)** : honoraires et secteurs conventionnels 2025, licence ODbL.
- **Ministère de l'Intérieur (data.gouv.fr)** : candidatures et résultats des municipales 2020 et 2026, répertoire national des élus.
- **INJEP** : recensement des licences et clubs sportifs (données géocodées par l'Insee, 2013-2023) ; **ministère des Sports** : équipements (Data ES) ; **ANCT** : quartiers prioritaires.
- **Assemblée nationale** : députés et collaborateurs ; **Parcoursup** (ministère de l'Enseignement supérieur) ; **Sécurité routière** : taux de réussite des auto-écoles.
- **Eurostat** (2025) ; **OCDE**, PISA 2025 (annexes du volume I) ; **Banque mondiale**, PIB par habitant ; **Drees**, pensions ; **Wikidata / Wikipédia** : listes des internationaux (encadré élite, agrégats seulement).
- **ARCOM** : enquête « Les Français et l'information » 2024 (2e édition disponible, mise à jour à faire).
- Millésime de chaque source et mises à jour restantes : `docs/millesimes_20261030.md`.
- **OpenDataSoft / geo.api.gouv.fr / france-geojson** : contours géographiques (départements, EPCI, communes).

---

## 10. Principes éditoriaux

- **Citer la source d'origine, jamais nous.** Chaque donnée affichée renvoie à sa source par un lien cliquable.
- **Pas de jugement implicite** sur les comportements : couleur neutre quand l'indicateur décrit une pratique, couleur orientée seulement quand il y a un enjeu de bien-être.
- **Afficher les limites** : données déclaratives, photographie à un instant donné, proxys onomastiques bruités à l'individu.
- **Reproductibilité** : les calculs sont des scripts Python versionnés ; la méthodologie est publiée sur le site.
- **Règle de style** : pas de tiret cadratin dans les textes du site ni dans la documentation.
- **Vérifier avant de diffuser** : tout chiffre affiché se retrouve dans les données publiées ; un verdict doit découler des chiffres ; un rang se donne avec sa fourchette ; une différence n'est affirmée que si elle est significative.
- **Sujets sensibles** (diversité des noms, élus, élite sportive) : agrégats seulement, rien par personne, cases de moins de 30 noms masquées, jamais de vocabulaire de « remplacement », jamais de classement présenté comme un palmarès.
- **Anonymat** : aucun nom d'auteur sur le site ni dans les métadonnées ; pas de tarifs ni de prestations affichés.
- **Sauvegardes** : jamais de fichier `.bak` dans `frontend/public/` (tout ce dossier part en ligne) ; les sauvegardes de données vont dans `_archive/`.

---

## 11. Pipelines de données (mise à jour)

Scripts dans `python/tools/`, à lancer dans cet ordre (détails dans `docs/DEPLOIEMENT.md`, section 4B) :

1. `build_onomastics_reference.py` : référentiel IDP, sexe, âge (noms et prénoms INSEE).
2. `build_ecole.py` : IPS et valeur ajoutée, plus `etablissements.tsv` (environ 40 000 établissements géolocalisés).
3. `build_atlas_communes.py` : valeurs par commune et département (école, revenu, prix, diversité IDP).
4. `build_atlas_epci.py` : maille EPCI (contours simplifiés et valeurs agrégées).
5. Indicateurs INSEE du recensement et de l'état civil, fusionnés dans les communes, départements et EPCI :
   - `build_atlas_insee.py` (diplômés du supérieur),
   - `build_atlas_logement.py` (5 indicateurs de logement),
   - `build_atlas_demo.py` (jeunes, 65 ans et plus),
   - `build_atlas_pcs.py` (cadres, professions intermédiaires, employés, ouvriers),
   - `build_atlas_natalite.py` (taux de natalité),
   - `build_atlas_sante.py` (accès aux soins, Drees et Assurance maladie ; les dépassements n'existent qu'au département, `communeKey: null` dans le registre ; hors du jumeau statistique).
6. `build_atlas_population.py` : champ technique de population par territoire (sert au moteur de résidus et au jumeau, pas un indicateur affiché).
7. `build_territoires_index.py` : index de recherche, repères nationaux et tranches de population (à relancer après tout ajout d'indicateur de l'Atlas).
8. `build_atlas_vecteurs.py` : vecteurs communaux du jumeau statistique (communes de 1 000 habitants et plus, avec centroïdes).
9. `build_showcase_elus.py` : dossier Élus.
10. `build_segregation.py` : ségrégation revenu et âge par ville (carreaux FiLoSoFi 200 m via l'API Koumoul ; autonome ; met les carreaux en cache, à vider pour re-télécharger).
11. `build_evolution_revenus.py` : dossier « Qui s'enrichit, qui décroche ? » (position des communes dans la distribution des niveaux de vie, Filosofi 2014 et 2021, contrôle Filosofi 2 de 2023 ; communes au périmètre modifié depuis 2014 écartées ; à lancer après `build_atlas_population.py`).
12. Dossier « Sport » : `explore_sport_injep.py` puis `explore_sport_offre.py` et `explore_sport_elite.py` (licences et clubs INJEP, équipements Data ES, contours QPV, internationaux ; tables dans `python/data/sport/sorties/`, méthode dans `docs/sport/`), puis `build_showcase_sport.py` (→ `showcases/sport.json`, page `/terrains/sport` ; exclut les fédérations multisports des classements par sport).
13. `build_croisements.py` (cartes-croisements de l'Atlas, après tous les `build_atlas_*`), `build_auto_ecoles.py` (dossier Auto-écoles), puis `build_territoires_echelles.py` et `build_territoires_index.py` (fiches intercommunalité et région, extrait Auto-écoles par département ; à relancer après `build_auto_ecoles.py`).
14. Dossiers autonomes : `build_international.py` (Eurostat), `build_pisa.py` (OCDE), `build_assemblee.py`, `build_parcoursup.py`, `build_rythmes.py`, `build_pratiques.py` (dossier Modes de vie : INCA 3, Baromètre 2024, Assurance maladie ; ACM pondérée, intervalles par plan de sondage, standardisation indirecte ; → `showcases/pratiques.json` et `geo/regions.geojson`), `build_omnivore.py` (section « L'omnivore à l'épreuve » : critères objectifs majoritaire et pas cher, prix Insee IPC-PM-2015 ; → `showcases/omnivore.json`).

**Piège** : `build_atlas_epci.py` réécrit `atlas/epci.json` en entier. Après lui, relancer dans l'ordre `build_atlas_insee`, `build_atlas_logement`, `build_atlas_demo`, `build_atlas_pcs`, `build_atlas_natalite`, `build_atlas_sante`, `build_atlas_population`, puis `build_territoires_echelles`, `build_territoires_index`, `build_atlas_vecteurs`, `build_croisements`.

Puis redéployer : `cd frontend ; npm run deploy`.

---

## 12. Carte des principaux fichiers

```
frontend/
  src/
    App.jsx                      routes (lazy)
    config/
      indicateurs.js             registre des 20 indicateurs de l'Atlas
      decoupages.js              unités d'analyse + modes + indicateurs non géo
      terrains.js, themes.js     dossiers
      seo.js                     titre, description, image de partage et plan du site de chaque route
      dossiersTerritoires.js     registre « Dans nos dossiers » des fiches + exclusions motivées
    pages/
      atlas/Atlas.jsx            la carte de France (+ AnalyseBloc, croisement)
      territoire/Territoires.jsx fiche territoire + tableau de bord national
      explorer/UnitView.jsx      moteur générique (milieu social, sexe, âge)
      outils/RepresentativiteTool.jsx   moteur onomastique
      terrains/                  École, Élus, Assemblée, Sélectivité, Auto-écoles, Revenus, Sport
      international/             International (France en Europe), Pisa
      segregation/Segregation.jsx  étude ségrégation (« tape ta ville »)
      Presse.jsx                 page presse et réutilisation
      Newsletter.jsx             inscription à la newsletter (Brevo)
      Fil.jsx                    le fil plein écran (stories)
      Home.jsx                   cartes-questions (QUESTIONS exporté), carrousel sur téléphone
    components/                  Header, Footer, BarreOnglets, GestionDefilement, NewsletterForm,
                                 InstallerApplication, ExplorerBar, ChoroplethMap, PointMap, CarreauxMap...
    lib/                         meta (SEO), analytics (GoatCounter), residuals, territoire, jumeau
    tools/onomastics/engine.js   inférence IDP / sexe / âge (navigateur)
  scripts/                       generate-og.mjs, prerender-meta.mjs, generate-sitemap.mjs (post-build),
                                 generate-icons.mjs (icônes de l'application, à relancer si le dessin change)
  public/manifest.webmanifest    application web installable ; public/icons/, public/favicon.svg
  public/data/                   tous les JSON pré-calculés (dont segregation/)
python/tools/                    pipelines de génération des données (dont build_segregation.py)
docs/                            projet (ce fichier), vision-et-sujets, veille-open-data,
                                 DEPLOIEMENT, AJOUTER_UN_DECOUPAGE, design, vérification des cartes,
                                 millésimes, fiches territoire, sport/, international/, promotion/, idees/,
                                 relecture/ (une fiche par carte de l'accueil)
_archive/                        sauvegardes datées hors du dossier publié
```

---

## 13. Ce qui peut venir ensuite (état au 30 octobre 2026)

**Fait en octobre 2026** : domaine dataoutsiders.fr et adresse de contact ; newsletter (Brevo) ; mentions légales, page 404, plan du site ; recensement 2023 et Filosofi 2023 ; dossiers Revenus, Sport (avec l'encadré élite), PISA ; vérification et correction des cartes de l'accueil ; page presse ; fiches à quatre échelles avec « Dans nos dossiers » ; millésimes à jour ; statistiques d'usage ; version téléphone (carrousel, fil, barre d'onglets, application installable) ; défilement entre pages corrigé ; sauvegarde Git et GitHub ; fiches de relecture des 16 cartes ; Assemblée : diversité masquée sous 30 noms.

**En cours** : relecture des cartes une par une par l'usager (`docs/relecture/README.md`), en commençant par les
défauts encore en ligne (Public-privé « le plus grand écart de métropole », fiche ville de la ségrégation, formules
du dossier Sport, données de l'âge sans script).

**Promotion** (plan validé par l'usager, dans l'ordre) :
1. Déclarer les réutilisations sur data.gouv.fr (textes prêts : `docs/promotion/reutilisations_datagouv.md` ; Élus, Assemblée, Sélectivité et l'outil Représentativité à ne pas mettre en avant).
2. ~~Newsletter~~ **FAIT le 30/10/2026** : compte Brevo créé par l'usager, domaine authentifié, formulaire et liste, inscription sur le site, mentions légales, comptage (`docs/DEPLOIEMENT.md`, §5 bis). Reste : la première newsletter (brouillon préparé, relu et envoyé par l'usager).
3. Générateur de visuels Instagram à partir des cartes-questions (sujets sensibles hors réseaux ou relus).
4. Générateur de « portraits de territoire » (image et texte d'invitation) à partir des fiches, et modèles de messages par public : journalistes, enseignants, chercheurs, créateurs, collectivités (services d'études, agences d'urbanisme, observatoires). Les messages partent de l'usager ; pas de contact sous Outsiders avec les interlocuteurs de son emploi.
5. Fiches communes indexables par les moteurs de recherche.

**Mises à jour de données restantes** (`docs/millesimes_20261030.md`) : Arcom 2e édition ; pensions Drees 2024 (changement de définition à décider) ; Assemblée (13 sortis, 10 entrés) ; population du dossier Sport au recensement 2023 ; brevet du dossier Auto-écoles.

**Idées en réflexion, à reprendre avec l'usager** (`docs/idees/`) : la presse comme donnée (Europresse, statistiques sur corpus permises, pas de rediffusion ; presse régionale et quartiers) ; une éventuelle version payante (préalables : anonymat et cumul d'activités) ; une page publique « Audience ». PISA en version turque : seulement dans un éventuel autre site.

**Autres pistes** : usages audiovisuels (Arcom), « le niveau baisse-t-il ? » avec les évaluations nationales (DEPP), nouvelles unités d'analyse (diplôme, nuance politique), ségrégation (couleurs par région, axe pauvreté, débiaiser les zones frontalières).

Le fil reste le même : une donnée publique sous-exploitée, un angle clair, un livrable réutilisable.
