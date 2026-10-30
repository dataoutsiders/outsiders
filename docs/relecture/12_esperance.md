# 12. Face à la santé, tous égaux ?
> Carte `esperance` · verdict « Faux » · dossier /explorer/milieu-social · fiche préparée le 30/10/2026

## Ce qu'affiche la carte

- **Rubrique** : Santé ; unité « Milieu social » ; couleur `#EF4444`.
- **Question** : « Face à la santé, tous égaux ? »
- **Verdict** : `faux`.
- **Chiffre** : **+5,3 ans**, « d'espérance de vie pour un homme cadre de 35 ans, comparé à un ouvrier ».
- **Texte** : « À 35 ans, un homme cadre peut espérer vivre encore 48,9 ans, un ouvrier 43,6. Chez les femmes, l'écart est de 3,4 ans. Le milieu social se lit jusque dans les tables de mortalité. »
- **Source citée** : « Insee, mortalité par catégorie sociale 2020-2022 », lien https://www.insee.fr/fr/statistiques/2383438
- **Lien** : « Comparer les milieux sociaux » vers `/explorer/milieu-social`.

## Ce que dit le dossier

Page générique `UnitView` (`/explorer/milieu-social`), configurée dans `frontend/src/config/decoupages.js` (entrée `milieu-social`) et alimentée par `frontend/public/data/decoupages/milieu-social.json`.

- Cinq catégories en colonnes : indépendants, cadres et professions intellectuelles supérieures, professions intermédiaires, employés, ouvriers.
- Six indicateurs en lignes, groupés par thème : niveau de vie (ERFS 2024), taux de pauvreté (ERFS 2024), chômage (enquête Emploi 2025), **espérance de vie à 35 ans (hommes)**, abstention systématique (2022), « s'informe d'abord en numérique » (Arcom 2024).
- Ligne espérance de vie : indépendants 46,4 ; cadres 48,9 ; professions intermédiaires 47,4 ; employés 45,1 ; ouvriers 43,6. Colonne « Écart » (maximum / minimum) et heatmap colorée par ligne.
- Sous-détail (`detail`) pour les indépendants : agriculteurs 47,2 ; artisans, commerçants, chefs d'entreprise 46,4.
- Aide de l'indicateur : « Années restant à vivre en moyenne à 35 ans, chez les hommes. Chez les femmes, l'écart cadres/ouvrières est plus faible (53,0 vs 49,6 ans). »
- Mode Fiche (`?cat=ouvriers`, etc.) : rang de la catégorie et indicateurs où elle est à l'extrême.
- Pas de valeur « Ensemble » en repère pour cet indicateur (`references` ne contient que niveau de vie, pauvreté et chômage).

## D'où viennent les chiffres

Chaîne : tableau Insee (page 2383438, fichier `demo-deces-esp-35-csp-diplome.xlsx`) -> **saisie à la main** dans `frontend/public/data/decoupages/milieu-social.json` (aucun script de construction ; voir `docs/AJOUTER_UN_DECOUPAGE.md`) -> `UnitView` -> carte de l'accueil, dont le texte est écrit en dur dans `Home.jsx`.

| Chiffre de la carte | Valeur | Origine dans le tableau Insee (figure 1, 2020-2022) |
|---|---|---|
| 48,9 ans | `categories[cadres].valeurs.esperance_vie_h` | Cadres, hommes |
| 43,6 ans | `categories[ouvriers].valeurs.esperance_vie_h` | Ouvriers, hommes |
| +5,3 ans | 48,9 − 43,6, calculé à la main | ligne « Écart cadres-ouvriers », hommes : 5,3 |
| 3,4 ans (femmes) | aide de l'indicateur (53,0 − 49,6), pas dans les `valeurs` | ligne « Écart cadres-ouvriers », femmes : 3,4 |

Contrôle du 30/10/2026 : fichier Insee téléchargé, valeurs identiques.

## Les jeux de données

### Espérance de vie à 35 ans par catégorie socioprofessionnelle et diplôme (Insee)
- **Producteur** : Insee, à partir de l'**échantillon démographique permanent** (EDP, panel d'environ 4 % de la population reliant état civil, recensements et fichiers fiscaux).
- **Intitulé** : « Espérance de vie à 35 ans par catégorie socioprofessionnelle et diplôme. Données de 1976-1984 à 2020-2022 », paru le 16/07/2024.
- **Millésime utilisé** : 2020-2022. Dernier disponible : 2020-2022 (actualisation tous les 7 ans environ, voir `docs/millesimes_20261030.md`).
- **Page** : https://www.insee.fr/fr/statistiques/2383438
- **Téléchargement** : https://www.insee.fr/fr/statistiques/fichier/2383438/demo-deces-esp-35-csp-diplome.xlsx (xlsx, 2 feuilles ; vérifié le 30/10/2026)
- **Publication associée** : Insee Première « Les écarts d'espérance de vie entre cadres et ouvriers : 5 ans chez les hommes, 3 ans chez les femmes » (2024).
- **Géographie** : France entière, sans ventilation territoriale. Champ : France métropolitaine jusqu'en 2000-2008, France hors Mayotte à partir de 2009-2013.

Feuille « Figure 1 » (par catégorie socioprofessionnelle) :

| colonne ou dimension | sens / modalités | utilisée ? |
|---|---|---|
| Catégorie socioprofessionnelle | agriculteurs ; artisans, commerçants, chefs d'entreprise ; cadres ; professions intermédiaires ; employés ; ouvriers ; inactifs non retraités ; ensemble ; écart cadres-ouvriers | oui : les six catégories d'actifs (agriculteurs et artisans regroupés sous « indépendants », valeur des artisans). Non : inactifs non retraités (34,0 ans pour les hommes), ensemble (45,3 hommes, 50,8 femmes) |
| Sexe | femmes, hommes | oui : hommes dans les valeurs ; femmes seulement dans l'aide (cadres 53,0, ouvrières 49,6) |
| Période | 1976-1984, 1983-1991, 1991-1999, 2000-2008, 2009-2013, 2017-2019, 2020-2022 | oui : 2020-2022. Non : les six périodes antérieures |
| Écart 2020-2022 et 1976-1984 | gain par catégorie et sexe | non |

Feuille « Figure 2 » (par diplôme) :

| colonne ou dimension | sens / modalités | utilisée ? |
|---|---|---|
| Diplôme | supérieur au bac ; bac ; CAP, BEP ; brevet, CEP ; sans diplôme ; ensemble ; écart supérieur au bac - sans diplôme | non |
| Sexe | femmes, hommes | non |
| Période | 1991-1999, 2000-2008, 2009-2013, 2017-2019, 2020-2022 | non |

Valeurs 2020-2022 utiles à la relecture :

| | Femmes | Hommes |
|---|---|---|
| Cadres | 53,0 | 48,9 |
| Professions intermédiaires | 52,3 | 47,4 |
| Agriculteurs | 50,5 | 47,2 |
| Artisans, commerçants, chefs d'entreprise | 51,7 | 46,4 |
| Employés | 51,2 | 45,1 |
| Ouvriers | 49,6 | 43,6 |
| Inactifs non retraités | 45,8 | 34,0 |
| Ensemble | 50,8 | 45,3 |
| Diplôme supérieur au bac | 52,6 | 48,5 |
| Sans diplôme | 47,2 | 40,5 |
| Écart cadres-ouvriers | 3,4 | 5,3 |
| Écart diplôme supérieur - sans diplôme | 5,4 | 8,0 |

Écart cadres-ouvriers chez les hommes, par période : 6,0 (1976-1984), 6,4, 7,0 (1991-1999), 6,3, 6,2, 5,9 (2017-2019), 5,3 (2020-2022). Chez les femmes : 3,1, 3,4, 2,6, 3,0, 3,3, 3,5, 3,4.

## Ce qu'on n'exploite pas encore

- **Le diplôme** : chez les hommes, 8,0 ans d'écart entre diplômés du supérieur et sans diplôme, contre 5,3 entre cadres et ouvriers ; 5,4 ans chez les femmes. Écart plus fort et plus facile à comprendre (chacun connaît son diplôme), sans le problème des catégories qui mélangent des métiers très différents.
- **Les femmes dans les valeurs** : la ligne ne montre que les hommes ; une seconde ligne « femmes » (ou une bascule de sexe) éviterait de reléguer la moitié de la population dans une info-bulle.
- **Les inactifs non retraités** : 34,0 ans pour les hommes, 11,3 ans de moins que l'ensemble. L'écart le plus fort du tableau ; à manier avec précaution (effet de sélection : on est inactif parce qu'on est malade).
- **La tendance longue** : l'écart cadres-ouvriers chez les hommes a culminé à 7,0 ans en 1991-1999 et se réduit depuis (5,3) ; chez les femmes il stagne autour de 3 ans. Nuance utile au verdict : l'inégalité est forte mais elle recule pour les hommes.
- **L'effet de la période Covid** : 2020-2022 couvre l'épidémie ; de 2017-2019 à 2020-2022, l'espérance de vie des cadres hommes baisse de 0,8 an et celle des ouvriers de 0,2, ce qui réduit l'écart. À signaler avant de commenter la baisse de 5,9 à 5,3.
- **L'ensemble en repère** : 45,3 ans pour les hommes, à ajouter dans `references` comme pour les autres indicateurs.

## Autres sources possibles

- **Espérance de vie par niveau de vie (Insee Première n° 2085, décembre 2025, période 2020-2024)** : 13 ans d'écart à la naissance chez les hommes entre les 5 % les plus modestes et les 5 % les plus aisés (environ 72 et 85 ans), 9 ans chez les femmes (80,1 et 88,7) ; écart en hausse depuis 2012-2016 ; risque de décès à 50 ans sept fois plus élevé chez les hommes les plus modestes ; effets régionaux à niveau de vie égal. https://www.insee.fr/fr/statistiques/8679561 (édition précédente, 2012-2016 : https://www.insee.fr/fr/statistiques/3319895). Chiffre plus frappant que la CSP et cohérent avec les indicateurs de revenu du site ; vérifier que les vingtiles de niveau de vie sont téléchargeables.
- **Espérance de vie sans incapacité par catégorie sociale** (Drees et Ined, travaux d'Emmanuelle Cambois) : les cadres vivent plus longtemps et plus longtemps sans incapacité ; la double peine des ouvriers. Publication la plus récente à vérifier sur le site de la Drees.
- **Eurostat, espérance de vie par niveau d'éducation** (`demo_mlexpecedu`) : la France n'y figure pas (vérifié par l'API le 30/10/2026), donc pas de comparaison européenne par diplôme pour la France.
- **Insee, Bilan démographique** (espérance de vie à la naissance et à 60 ans par sexe, annuel) : repère d'ensemble, déjà utilisé par le découpage Sexe.
- **Santé publique France, Drees : état de santé de la population** (renoncement aux soins, maladies chroniques par catégorie sociale, enquête EHIS) : élargirait « face à la santé » au-delà de la mortalité.

## Points de relecture

- **Formulation** : « Face à la santé » ; le chiffre mesure la mortalité (espérance de vie), pas la santé ni l'accès aux soins. « Face à la mort » ou « Face à la durée de vie » serait plus exact, ou garder la question et parler de « durée de vie » dans le texte.
- **Chiffre plus parlant possible** : « 8 ans d'écart selon le diplôme » (hommes) ou « 13 ans entre les plus modestes et les plus aisés » (niveau de vie, 2020-2024, à la naissance). Le +5,3 reste le plus solide pour une carte « milieu social ».
- **Sexe** : la carte précise désormais « un homme cadre » et donne l'écart féminin (correction du 30/10/2026) ; la page n'affiche toujours que les hommes.
- **Indépendants** : la colonne « Indépendants » affiche 46,4, valeur des seuls artisans, commerçants et chefs d'entreprise ; les agriculteurs (47,2) ne sont qu'en sous-détail. Le regroupement est imposé par les autres indicateurs (ERFS), mais il faudrait le dire dans l'aide ou afficher une moyenne pondérée.
- **Catégorie attribuée** : dans l'EDP, la catégorie est celle déclarée au recensement (y compris pour les retraités, leur ancienne profession) ; les personnes sans profession déclarée sont dans « inactifs ». Ce n'est pas une cause : la sélection par la santé joue (on quitte un métier pénible parce qu'on est malade).
- **Période Covid** : 2020-2022 n'est pas une période « normale » ; l'écart masculin est passé de 5,9 (2017-2019) à 5,3. Ne pas présenter la baisse comme un progrès sans cette réserve.
- **Fraîcheur** : 2020-2022 est le dernier millésime ; prochaine actualisation dans plusieurs années.
- **Source** : le libellé « mortalité par catégorie sociale 2020-2022 » pourrait citer l'intitulé exact (« Espérance de vie à 35 ans par catégorie socioprofessionnelle et diplôme ») et l'EDP.
