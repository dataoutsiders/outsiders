# Vérification des cartes « Vrai ou faux ? » de la page d'accueil

Vérification du 29/10/2026, tableau `QUESTIONS` de `frontend/src/pages/Home.jsx` (15 cartes). Chaque chiffre a été recherché dans les données publiées par le site (`frontend/public/data/...`), dans la page vers laquelle mène le bouton, dans le script de calcul (`python/tools/build_*.py`) et, quand c'était possible, recalculé ou confronté à la source d'origine (Eurostat par son API, pages Insee, base Arcom, fichiers des municipales). Aucun fichier du site n'a été modifié.

Statuts : **exact** (retrouvé et juste), **à nuancer** (juste mais incomplet ou trompeur tel quel), **faux** (contredit par les données), **introuvable**.

---

## 1. « Riches et pauvres vivent-ils séparés ? » (segregation, verdict « Pas partout »)

| Affirmation | Affiché | Retrouvé | Où | Statut |
|---|---|---|---|---|
| Villes aux quartiers nettement séparés | 1 sur 3 | 341 / 997 = 34 % (typologie « Fracturée ») | `segregation/villes.json`, page `/segregation` | **faux en logique** (chiffre juste, sens faux) |
| Paris mêle les revenus « à hauteur de rue » | | mélange interne au 99e rang (rapport D9/D1 médian des IRIS : 5,3) | `segregation/75056.json` | à nuancer |
| Paris sépare nettement ses grands quartiers | | séparation au 99e rang (dispersion des médianes d'IRIS) | idem | à nuancer |
| Source | Insee, FiLoSoFi (IRIS et carreaux 200 m) | IRIS 2021 et carreaux 2019 | `build_segregation.py` | à nuancer (millésimes absents) |

**Logique.** Le « 1 sur 3 » est un artefact de construction. Dans `build_segregation.py`, la séparation est un **rang centile** parmi les 997 villes de plus de 10 000 habitants, et une ville est « Fracturée » dès que ce rang atteint 66 (`band()` : haut si score >= 66). Le tiers supérieur d'un classement contient par définition un tiers des villes : le chiffre serait 34 % quelle que soit la réalité de la ségrégation en France. Il ne peut donc pas répondre à la question. Par ailleurs, les deux mesures de Paris sont prises au même niveau (l'IRIS, environ 2 000 habitants) : dispersion dans l'IRIS contre écart entre IRIS, pas « la rue » contre « les grands quartiers ».

**Fraîcheur.** IRIS 2021 et carreaux 2019, alors que le reste du site est passé au Filosofi 2023 communal. Vérifier si l'Insee a publié le niveau IRIS 2022 ou 2023.

**Correction proposée**
- chiffre : `× 1,6`
- chiffreLabel : `dans la ville type, l'écart de niveau de vie entre ses quartiers aisés et ses quartiers modestes` (médiane des rapports `p90_p10` de `villes.json`, recalculée : 1,6 ; c'est la valeur `medContrast` affichée par la page ; elle rapporte le 9e décile au 1er décile des carreaux, pas le quartier le plus aisé au plus modeste, comme l'écrit la page)
- texte : `L'écart varie beaucoup d'une ville à l'autre : on classe ici les 997 villes de plus de 10 000 habitants de la plus séparée à la plus mélangée, un classement relatif et non un seuil absolu. Paris figure parmi les plus séparées et, en même temps, parmi celles dont chaque quartier (IRIS, environ 2 000 habitants) mêle le plus des revenus très différents.`
- source : `Insee, FiLoSoFi 2021 (IRIS) et 2019 (carreaux de 200 m)`

---

## 2. « La banlieue décroche ? » (revenus, « Pas partout »)

| Affirmation | Affiché | Retrouvé | Où | Statut |
|---|---|---|---|---|
| Habitants de la grande couronne dans une commune qui a reculé | 85 % | 84,8 % (100 - 15,2) | `evolution-revenus.json`, anneau « Grande couronne » ; page : 84,8 % | exact |
| Proche banlieue qui monte (Clichy, Saint-Ouen, Romainville, Montreuil) | | Clichy +25,1 pts, Saint-Ouen +14,0, Romainville +18,4, Montreuil +10,7 | idem, `villes` | exact |
| « la proche banlieue parisienne monte » | | petite couronne : +0,3 pt en moyenne ; 92 : +2,8 ; 93 : -0,1 ; 94 : -2,1 | recalcul sur `villes` | à nuancer |
| « partout, les revenus augmentent en euros » | | 3 communes sur 5 070 en baisse en euros courants (Villennes-sur-Seine, Bezannes, Rubelles) | recalcul | à nuancer (« presque partout ») |

**Logique.** Le verdict tient. Mais « reculé » compte tout recul, même de 0,1 point de rang : la part des habitants de la grande couronne dont la commune perd plus d'un point est de 67 % (plus de 5 points : 28 %, recalcul sur les communes de 2 000 habitants et plus). Et la montée concerne les Hauts-de-Seine et les communes limitrophes de Paris, pas la petite couronne en bloc (le Val-de-Marne recule).

**Fraîcheur.** La période 2014-2021 est affichée alors que 2023 est dans le fichier (contrôle : -4,3 points pour la grande couronne, recul encore plus net). Envisager de passer le titre à 2014-2023.

**Correction proposée**
- texte : `De 2014 à 2021, les communes limitrophes de Paris montent dans la hiérarchie des revenus (Clichy, Saint-Ouen, Romainville, Montreuil) pendant que la grande couronne pavillonnaire recule, souvent de peu : deux habitants sur trois y vivent dans une commune qui perd plus d'un point. Une position relative : presque partout, les revenus augmentent en euros.`

---

## 3. « Le foot, sport des quartiers ? » (sport, « Vrai, mais »)

| Affirmation | Affiché | Retrouvé | Où | Statut |
|---|---|---|---|---|
| Part du foot dans les licences des QPV / reste de la commune | 35 % / 15 % | 35,4 % / 14,8 % | `sport.json`, `sports_qpv` | exact |
| Foot par habitant, QPV / reste | 1,4 fois | 1,39 | idem | exact |
| Licenciés par terrain, QPV / ailleurs | près de trois fois | 210 / 73 = 2,9 | `sport.json`, `offre` | exact, à nuancer |
| Source | INJEP 2023 ; Data ES | millésime 2023 ; lien vers l'INJEP seulement | | exact |

**Logique.** Le calcul tient : l'écart de part (35 contre 15) vient pour l'essentiel du plus faible nombre total de licences dans les quartiers (103 contre 180 pour 1 000 habitants), le reste de la plus forte pratique du foot. Deux formulations dépassent les données. « L'absence des autres sports » : ils sont moins pratiqués en club, pas absents. « Ce n'est pas faute de demande » : les licenciés sont comptés à leur domicile et les terrains à leur adresse ; le ratio ne mesure pas l'usage réel des terrains (un licencié du quartier peut jouer ailleurs).

**Correction proposée**
- texte : `Par habitant, le foot n'y est que 1,4 fois plus fréquent : sa place tient surtout à la moindre pratique en club des autres sports. Et les terrains y sont rares : on compte près de trois fois plus de licenciés résidents par terrain de quartier qu'ailleurs.`

---

## 4. « La politique française se diversifie ? » (elus, « Faux »)

| Affirmation | Affiché | Retrouvé | Où | Statut |
|---|---|---|---|---|
| Rapport candidats / maires | ÷ 3,7 | 4,37 / 1,18 = 3,7 ; **la page du dossier affiche « ÷ 4 »** | `elus-diversite.json` ; `TerrainElus.jsx` l. 158 | à nuancer (incohérent avec la page) |
| Candidats aux municipales 2026 | 888 000 | 888 079 (taux calculé sur 792 854 noms reconnus) | idem | exact |
| IDP des candidats | 4,4 % | 4,37 % | idem | exact |
| Têtes de liste | 2 % | 1,96 % | idem | exact |
| Conseillers élus | 2,7 % | 2,72 % (RNE du 11/08/2026) | idem | exact |
| Maires en fonction | 1,2 % | 1,18 % | idem | exact |
| « À chaque marche du pouvoir, le filtre se resserre » | | têtes de liste 2,0 % puis conseillers 2,7 % : **la série remonte** | idem | **faux** |
| Réponse « Faux » à « se diversifie ? » | | 2020-2026 : hausse à tous les niveaux comparables (voir ci-dessous) | recalcul | **faux** |

**Logique, premier problème : la question porte sur une évolution, la réponse est une photo.** Le filtre est mesuré à une seule date. Les fichiers 2020 du dossier (`python/data/municipales/`) permettent la comparaison. Recalcul avec le même référentiel (`surnames.tsv`) et la même normalisation que `build_showcase_elus.py` :

| Niveau (champ comparable) | 2020 | 2026 | Évolution |
|---|---|---|---|
| Candidats, 9 780 communes ayant des listes les deux années (1 000 habitants et plus) | 5,4 % | 6,2 % | +0,8 pt (+14 %) |
| Têtes de liste, mêmes communes | 2,5 % | 3,3 % | +0,8 pt (+33 %) |
| Élus au premier tour, 29 101 communes pourvues au premier tour les deux années | 1,8 % | 2,2 % | +0,4 pt (+22 %) |
| Élus au premier tour, communes de 1 000 habitants et plus (7 755) | 2,6 % | 3,2 % | +0,6 pt |

Fichiers : `candidatures-2020-t1.txt` (listes de 2020, communes de 1 000 habitants et plus seulement, la loi de 2025 ayant étendu les listes à toutes les communes en 2026), `candidats-elus-2020-t1.txt` et `candidats-elus-t1.csv` (élus au premier tour). La comparaison des **maires** n'est pas faisable avec les fichiers présents : il faudrait l'archive du Répertoire national des élus de 2020 (data.gouv.fr). Limites : seul le premier tour est comparable pour les élus (le second tour de 2020 a eu lieu en juin, sous Covid) ; une partie de la hausse peut venir du renouvellement des générations (le référentiel repère des noms devenus fréquents après 1950, donc plus présents chez les jeunes). Conclusion : **la politique locale se diversifie, lentement, et reste loin des 7 % de la population.** « Faux » est contredit par les données du dossier lui-même.

**Logique, deuxième problème : le « ÷ 3,7 » mélange géographie et sélection.** Les candidats aux noms classés « diversité » se concentrent dans les grandes villes, où il y a beaucoup de listes et beaucoup de candidats, alors que chaque commune n'a qu'un maire, le plus souvent rural. Recalcul commune par commune (2026) :
- moyenne des communes (chaque commune pèse 1) : 2,3 % des candidats, contre 4,4 % en comptant les candidats ;
- conseillers élus : 2,7 %, pour 2,9 % attendus d'après les candidats de leur propre commune : **presque pas de filtre à l'élection** ;
- têtes de liste : 2,0 %, pour 3,0 % parmi les colistiers de leur propre liste : **le vrai filtre est là**, au choix de qui conduit la liste ;
- maires : 1,2 %, pour 2,2 % parmi les candidats de leur commune (÷ 1,9) et 1,3 % parmi les têtes de liste de leur commune.

Le filtre propre à la compétition électorale est donc d'environ ÷ 1,9, et il se joue surtout à la désignation des têtes de liste ; le reste du ÷ 3,7 tient à la géographie.

**Formulation.** « portent un nom issu de la diversité » se lit comme une origine. Le garde-fou du site (indicateur de groupe calculé sur les noms, pas une origine) n'apparaît pas sur la carte. Même problème hors de la carte : `config/indicateurs.js` l. 117 parle de « La diversité d'origine dans la représentation politique », et `config/seo.js` l. 108 reprend le filtre 4,4 % puis 1,2 %. La page du dossier écrit « la diversité chute à chaque palier du pouvoir », contredit par sa propre série (2,0 puis 2,7).

**Correction proposée A (recommandée, suppose d'ajouter la comparaison 2020 au dossier)**
- question : `La politique locale se diversifie ?`
- verdict : `vraiMais`
- chiffre : `1,8 → 2,2 %`
- chiffreLabel : `de noms classés « diversité » parmi les conseillers élus au premier tour, de 2020 à 2026, dans les mêmes communes`
- texte : `La hausse est réelle mais lente, et reste loin des 7 % de la population. Elle bute surtout sur le choix de qui conduit la liste : 2 % des têtes de liste portent un tel nom, contre 3 % de leurs colistiers. Maires élus en 2026 : 1,2 %. L'indice IDP est un indicateur de groupe calculé sur les noms, pas une origine.`

**Correction proposée B (immédiate, chiffres déjà dans le fichier, la page devra afficher le chiffre des colistiers)**
- question : `Les maires ressemblent-ils à leurs candidats ?`
- verdict : `faux`
- chiffre : `4,4 % → 1,2 %`
- chiffreLabel : `de noms classés « diversité » (indice IDP), des candidats aux municipales 2026 aux maires élus`
- texte : `Une partie de l'écart tient à la géographie : ces candidats se concentrent dans les grandes villes, où les listes sont nombreuses, alors que chaque commune n'a qu'un maire. Mais le filtre existe aussi dans les listes : 2 % des têtes de liste portent un tel nom, contre 3 % de leurs colistiers. Conseillers élus : 2,7 %. L'indice IDP est un indicateur de groupe calculé sur les noms, pas une origine.`
- Dans les deux cas, aligner la page du dossier (« ÷ 4 », « à chaque étage », « à chaque palier ») et `seo.js`.

---

## 5. « Les députés ressemblent aux Français ? » (assemblee, « Faux »)

| Affirmation | Affiché | Retrouvé | Où | Statut |
|---|---|---|---|---|
| Députés ouvriers | 6 / 577 | 6 | `assemblee.json` | exact |
| Ouvriers parmi « les actifs » | 18,6 % | 18,6 % des **personnes en emploi** 2023 | Insee 7767045 (vérifié) | à nuancer (libellé) |
| Députés cadres et prof. intellectuelles sup. | 66 % | 383 / 577 = 66,4 % (71,7 % des 534 qui déclarent une profession) | idem | exact |
| Cadres parmi les actifs | 22 % | 22,4 % des personnes en emploi | Insee | exact (libellé) |
| IDP des collaborateurs | 6,4 % | 6,4 % (1 697 noms reconnus) | idem | exact |
| IDP des députés | 4,2 % | 4,2 % (501 noms reconnus, soit environ 21 députés) | idem | exact |
| Population | 7 % | référence du référentiel IDP | `onomastics/meta.json` | exact |

**Logique.** Le verdict tient pour la profession. Pour les noms, « la diversité s'arrête à la porte du mandat » est trop fort : l'écart 6,4 % contre 4,2 % n'est pas significatif au seuil usuel (test de deux proportions, p d'environ 0,07, sur une vingtaine de députés) et les collaborateurs sont plus jeunes, ce qui augmente mécaniquement l'IDP. La profession des députés est celle qu'ils déclarent (souvent l'ancienne).

**Correction proposée**
- chiffreLabel : `députés ouvriers, quand les ouvriers sont 18,6 % des personnes en emploi`
- texte : `66 % des députés se déclarent cadres ou professions intellectuelles supérieures (22 % des personnes en emploi). Côté noms, 4,2 % des députés portent un nom classé « diversité » (indice IDP), contre 6,4 % de leurs collaborateurs, plus jeunes, et 7 % de la population : un écart à confirmer sur une vingtaine de députés.`

---

## 6. « Champion des dépenses publiques, champion de la protection ? » (etat-enfants, « Faux »)

| Affirmation | Affiché | Retrouvé | Où | Statut |
|---|---|---|---|---|
| Dépenses publiques, % du PIB | 56,8 % | 56,8 % en 2023 ; **57,0 % en 2024, 57,3 % en 2025** | `pays.json` ; API Eurostat `gov_10a_main` | à nuancer (périmé) |
| « record des 30 pays », « le pays qui dépense le plus d'Europe » | | vrai en 2023 ; **2e derrière la Finlande en 2024 (57,9 %) et 2025 (57,5 %)** | API Eurostat | **faux à ce jour** |
| Enfants menacés de pauvreté ou d'exclusion | 26,2 % | 26,2 % en 2024 ; **27,5 % en 2025** | `pays.json` (série) ; `ilc_peps01n` | à nuancer (périmé) |
| Moyenne UE | 24,2 % | 24,2 % (2024) ; 24,3 % (2025) | idem | exact |
| « Seuls 6 pays font pire » | 6 | 6 sur 29 en 2024 ; 4 sur 28 en 2025 | idem | exact pour 2024 |

**Logique.** Le titre de champion des dépenses ne vaut plus avec les données 2024 et 2025, que le site contient déjà dans sa série (`pays.json`). Sur le fond, la « protection » est mesurée par un seul indicateur, celui des enfants ; « dans le pays qui dépense le plus » suggère un lien de cause entre dépense totale (dont retraites et santé) et pauvreté des enfants que les données ne montrent pas. Le verdict « Faux » se défend sur le constat (beaucoup de dépense, plus d'enfants menacés que la moyenne) si on le formule comme un contraste et non comme une inefficacité. À signaler : saut de la série française entre 2021 (22,5 %) et 2022 (27,1 %) ; vérifier s'il s'agit d'une rupture de série de l'enquête SRCV avant de commenter une tendance.

**Correction proposée (millésime 2025)**
- chiffreLabel : `enfants menacés de pauvreté ou d'exclusion, dans l'un des deux pays qui dépensent le plus d'Europe`
- texte : `57,3 % du PIB de dépenses publiques en 2025, au 2e rang des 30 pays comparés derrière la Finlande. Et pourtant 27,5 % des moins de 18 ans sont menacés de pauvreté ou d'exclusion, plus que la moyenne européenne (24,3 %). Seuls 4 des 28 pays disponibles font pire. Ce contraste ne dit pas à lui seul ce que vaut la dépense : elle finance d'abord les retraites et la santé.`
- source : `Eurostat, dépenses publiques et AROPE moins de 18 ans (2025)` ; mettre à jour le millésime de la vue `/international`.

---

## 7. « Les jeunes ne s'informent plus ? » (age, « Faux »)

| Affirmation | Affiché | Retrouvé | Où | Statut |
|---|---|---|---|---|
| « 77 % des 18-24 ans s'informent, d'abord via le numérique » | 77 % | 77,4 % = part dont le **principal** mode d'information est numérique (télévision ou radio regardées sur écran comprises), parmi ceux qui s'informent | `age.json` ; recalcul sur `base-info-arcom.xlsx` (définition de `generate_chapitre_01.py`) | à nuancer (mal lisible) |
| Part des 18-24 ans qui s'informent | (non affiché) | 96 % déclarent s'informer régulièrement | recalcul Arcom | |
| 18-24 ans s'informant via la télévision | 41 % | 41,2 % **au moins une fois par jour** (60 % au moins une fois par semaine) | recalcul Arcom | à nuancer |
| 70 ans et plus | 89 % | 89,3 % au moins une fois par jour | idem | exact (libellé) |
| Source | Arcom 2024 | enquête publiée le 14/03/2024 | | exact |

**Logique.** La question (« ne s'informent plus ? ») appelle la part qui s'informe : 96 %, et ce chiffre est dans la base. Le 77 % tel qu'écrit se lit « 77 % s'informent », donc « 23 % ne s'informent pas », ce qui est faux. Le « 41 % via la télévision » sans « chaque jour » laisse croire que 59 % ne la regardent jamais pour s'informer.

**Correction proposée**
- chiffre : `96 %`
- chiffreLabel : `des 18-24 ans déclarent s'informer régulièrement`
- texte : `Ils ont quitté le journal télévisé, pas l'information : 41 % s'informent chaque jour par la télévision, contre 89 % des 70 ans et plus, et pour 77 % d'entre eux le numérique (réseaux, sites, applis, mais aussi télévision et radio sur écran) est devenu le premier moyen de s'informer.` (ajouter le 96 % à la vue `/explorer/age`, règle du site oblige)

---

## 8. « La prépa, formation la plus sélective ? » (selectivite, « Faux »)

| Affirmation | Affiché | Retrouvé | Où | Statut |
|---|---|---|---|---|
| Taux d'accès du BPJEPS | 4 % | 4 % = **médiane** des 79 formations | `selectivite.json` | exact (libellé) |
| Sciences Po | 10 % | « Sciences politiques », 46 formations | idem | exact (libellé) |
| Arts appliqués | 23 % | DN MADE, 321 formations | idem | exact |
| Prépa scientifique | 41 % | 41 % (490 formations) | idem | exact |
| Licences acceptant tous leurs candidats | 33 % ; 20 % en Île-de-France | 33 % ; 20 % | idem | exact |
| Source | Parcoursup 2025 | session 2025 | | exact |

**Logique.** Juste au sens du taux d'accès. Mais le taux d'accès mesure la part des candidats qui reçoivent une proposition, pas le niveau exigé : les candidats en prépa se sont déjà triés eux-mêmes et multiplient les vœux. La question « la plus sélective » appelle cette précision. Pour la licence, un taux inférieur à 100 % traduit d'abord une capacité dépassée (la licence classe quand les places manquent), pas forcément une sélection sur dossier.

**Fraîcheur.** Vérifier si les données de la session 2026 sont publiées.

**Correction proposée**
- question : `La prépa, la formation la plus difficile d'accès ?`
- chiffreLabel : `de taux d'accès médian dans les formations au BPJEPS (sport), le plus bas de Parcoursup`
- texte : `Le sport, les instituts d'études politiques (10 %) et les arts appliqués (23 %) donnent moins de propositions à leurs candidats que la prépa scientifique (41 %). Le taux d'accès dit combien de candidats reçoivent une proposition, pas le niveau demandé. Et la licence n'accueille plus tous ses candidats partout : seules 33 % en acceptent la totalité, 20 % en Île-de-France, faute de places plus que par sélection.`

---

## 9. « Le meilleur taux de réussite fait la meilleure auto-école ? » (auto-ecoles, « Faux »)

| Affirmation | Affiché | Retrouvé | Où | Statut |
|---|---|---|---|---|
| Écoles qui changent de quart de classement | 44 % | 43,9 % | `auto-ecoles.json` | exact |
| Guadeloupe / Haute-Loire | 36 % / 73 % | 36,0 % / 72,9 % | idem | exact |
| Commune dix fois plus peuplée | -2,8 points | -2,8 (intervalle -3,5 à -2,0) | idem | exact, à nuancer |
| « dépend d'abord du département » | | département 25 % des écarts ; **école 49 %** ; commune 10 % ; hasard 16 % | `decomposition` | **à nuancer** |
| Source | Sécurité routière (data.gouv.fr) | fichier du 01/07/2025 | | exact (millésime absent) |

**Logique.** Verdict solide. Mais la décomposition du dossier montre que l'école elle-même (avec ce que les données ne voient pas : profil des candidats, centre d'examen) pèse deux fois plus que le département. « Coûte 2,8 points » est causal : c'est un écart à autres caractéristiques égales.

**Correction proposée**
- texte : `Le taux publié dépend pour un quart du département de l'examen (de 36 % en Guadeloupe à 73 % en Haute-Loire) et aussi de la ville : à département égal, une commune dix fois plus peuplée va avec 2,8 points de moins. Comparée à ce que son contexte laisse attendre, près d'une école sur deux change de quart de classement.`
- source : `Sécurité routière, taux de réussite des auto-écoles (fichier de juillet 2025, data.gouv.fr)`

---

## 10. « Public, privé : les mêmes élèves ? » (ecole, « Faux »)

| Affirmation | Affiché | Retrouvé | Où | Statut |
|---|---|---|---|---|
| IPS moyen des collèges publics / privés, Seine-Saint-Denis | 88 → 122 | 88,1 / 122,0 (rentrée 2025, moyenne simple des collèges) | `ecole-ips.json` | exact |
| Département le plus défavorisé de métropole | | 1er par l'IPS moyen et par le revenu médian | idem, `atlas/departements.json` | exact |
| Privé « comparable aux beaux quartiers » | | 122 : au-dessus de la médiane des collèges privés des départements (116,8) et des collèges publics de Paris (115,4) | idem | à nuancer (vague) |
| « Un écart invisible dans les moyennes nationales » | | l'écart public-privé existe partout (plus de 30 points dans 6 départements) ; le 93 a le plus grand de métropole (34 points) | idem | **à nuancer** |

**Correction proposée**
- chiffreLabel : `indice de position sociale moyen des collèges publics et privés de Seine-Saint-Denis (rentrée 2025)`
- texte : `Dans le département le plus défavorisé de métropole, les collèges privés accueillent un public plus favorisé que la moyenne des collèges publics de Paris (115). C'est l'écart entre public et privé le plus grand de métropole : 34 points.`
- source : `Éducation nationale, IPS des collèges (rentrée 2025)`

---

## 11. « Face à la santé, tous égaux ? » (esperance, « Faux »)

| Affirmation | Affiché | Retrouvé | Où | Statut |
|---|---|---|---|---|
| Écart cadre / ouvrier à 35 ans | +5,3 ans | 48,9 - 43,6 = 5,3, **hommes** | `milieu-social.json` ; page Insee 2383438 (vérifiée) | à nuancer (sexe omis) |
| Cadre / ouvrier | 48,9 / 43,6 | idem, hommes, 2020-2022 | idem | exact |

**Logique.** Juste, à condition de dire qu'il s'agit des hommes ; chez les femmes l'écart est de 3,4 ans (53,0 contre 49,6). Sans cette précision, le chiffre est faux pour la moitié de la population.

**Correction proposée**
- chiffreLabel : `d'espérance de vie pour un homme cadre de 35 ans, comparé à un ouvrier`
- texte : `À 35 ans, un homme cadre peut espérer vivre encore 48,9 ans, un ouvrier 43,6. Chez les femmes, l'écart est de 3,4 ans. Le milieu social se lit jusque dans les tables de mortalité.`

---

## 12. « Le meilleur système de santé du monde ? » (sante-paradoxe, « Vrai, mais »)

| Affirmation | Affiché | Retrouvé | Où | Statut |
|---|---|---|---|---|
| Rang mortalité infantile | 25e / 30 | 25e en 2023 ; **24e en 2024** | `pays.json` ; API Eurostat | exact pour 2023 |
| Mortalité infantile France / UE | 4,0 ‰ / 3,3 | 2023 ; **2024 : 4,1 / 3,5** | idem | à nuancer (périmé) |
| Espérance de vie | 82,9 ans, 9e / 30 | 2023 ; **2024 : 83,0 ans, 10e** | idem | à nuancer (périmé) |
| « seuls 5 pays font pire » | 5 | 5 en 2023 ; 6 en 2024 | idem | exact pour 2023 |
| Estonie | 1,7 ‰ | 1,7 en 2023 ; 2024 : 1,4 (Estonie et Islande) | idem | exact pour 2023 |

**Logique.** « Vrai, mais » valide l'idée que la France aurait le meilleur système de santé, ce que les chiffres ne montrent pas (9e ou 10e sur 30 pour l'espérance de vie, qui ne mesure d'ailleurs pas seulement le système de soins). Pour la mortalité infantile, les comparaisons internationales dépendent en partie de l'enregistrement des naissances très prématurées : à mentionner. « Longtemps une fierté nationale » : la France était sous la moyenne européenne jusque vers 2014, sans jamais être en tête (l'aide de `decoupages.js` l. 138 écrit « longtemps en tête », à corriger aussi).

**Correction proposée (millésime 2024)**
- question : `La France, bon élève de la santé en Europe ?`
- verdict : `vraiMais`
- chiffre : `24e / 30`
- chiffreLabel : `pour la mortalité infantile : 4,1 ‰, au-dessus de la moyenne européenne (3,5)`
- texte : `L'espérance de vie française reste dans le haut du classement (83,0 ans, 10e sur 30). Mais la mortalité infantile, longtemps meilleure que la moyenne européenne, est passée au-dessus : seuls 6 pays européens font pire. Les comparaisons dépendent en partie de la façon dont chaque pays enregistre les naissances très prématurées.`
- source : `Eurostat, mortalité infantile et espérance de vie (2024)`

---

## 13. « L'égalité femmes-hommes, c'est réglé ? » (sexe, « Faux »)

| Affirmation | Affiché | Retrouvé | Où | Statut |
|---|---|---|---|---|
| Écart de « pension de retraite » | -39 % | -38,7 % sur la **pension de droit direct**, retraités de 65 ans ou plus, 2019, montants nets | `sexe.json` ; page Insee 6047747 (vérifiée) | **à nuancer** |
| 981 € contre 1 600 € | | droit direct seul ; pension totale : 1 272 € contre 1 674 €, **soit -24 %** | Insee 6047747, figure 1 | à nuancer |
| Écart de salaire en EQTP | 13 % | 1 - 2 514 / 2 891 = 13,0 % (secteur privé, 2024) | `sexe.json`, Insee Focus 377 | exact |

**Logique.** Le verdict tient, mais « pension de retraite » désigne couramment la pension totale, dont l'écart est de 24 % (la réversion le réduit). La carte doit dire « de droit direct ». La donnée date de 2019 : la Drees publie des montants plus récents (« Les retraités et les retraites »), à reprendre. « Le temps partiel et les carrières interrompues le transforment en fossé » : ce sont des causes documentées, mais pas démontrées par les chiffres affichés ; écrire « contribuent à ».

**Correction proposée**
- chiffreLabel : `de pension de droit direct pour les femmes de 65 ans ou plus (981 € nets contre 1 600 €, en 2019)`
- texte : `L'écart de salaire (13 % en équivalent temps plein) paraît se réduire ; le temps partiel et les carrières interrompues contribuent à le creuser au moment de la retraite. Les pensions de réversion ramènent l'écart sur la pension totale à 24 %.`
- source : `Insee, Femmes et hommes, l'égalité en question (édition 2022, données 2019)`

---

## 14. « Les HLM sont là où la France est pauvre ? » (hlm, « Faux »)

| Affirmation | Affiché | Retrouvé | Où | Statut |
|---|---|---|---|---|
| HLM Hauts-de-Seine / Creuse | 24 % vs 8 % | 23,8 % / 7,8 % (RP 2023) | `atlas/departements.json` | exact |
| Hauts-de-Seine « parmi les plus riches » | | 1er par le revenu médian | idem | exact |
| « les départements urbains **et aisés** en comptent le plus » | | 1er : Seine-Saint-Denis (31 %), le plus modeste de métropole ; puis Val-de-Marne, Hauts-de-Seine, Marne, Val-d'Oise | idem | **faux** |
| Lien positif entre départements, négatif dans les départements | | corrélation HLM-revenu entre départements : +0,25 ; dans les départements, médiane -0,21 (négative dans 81 sur 96) | recalcul `atlas/communes/*.json` | exact, à nuancer |

**Logique.** Le renversement d'échelle est réel, mais faible au niveau départemental (+0,25). Le département le plus pauvre de métropole est celui qui a le plus de HLM : « Faux » est trop net, le bon verdict est « Pas partout » (ou « ça dépend de l'échelle »). Le logement social suit la ville, qu'elle soit aisée ou modeste.

**Correction proposée**
- verdict : `pasPartout`
- texte : `Le logement social suit d'abord la ville : les départements urbains en comptent le plus, qu'ils soient aisés comme les Hauts-de-Seine ou modestes comme la Seine-Saint-Denis (31 %). C'est à l'intérieur de chaque département que les HLM se concentrent dans les communes modestes. La relation change selon l'échelle, un piège classique des moyennes territoriales.`

---

## 15. « L'argent fait la réussite scolaire ? » (outsiders, « Pas partout »)

| Affirmation | Affiché | Retrouvé | Où | Statut |
|---|---|---|---|---|
| Départements défavorisés aux trois étapes où les lycées dépassent leur pronostic | 8 sur 23 | 8 sur **22** (Mayotte n'a pas de valeur ajoutée) ; dont 3 en outre-mer ; 4 au-dessus de +1 point seulement | `ecole-ips.json` | à nuancer |
| « un tiers » | | 36 % | idem | exact |
| La valeur ajoutée ne suit ni le revenu, ni l'immobilier, ni les CSP | | corrélations entre départements : revenu -0,04 ; prix +0,18 ; cadres +0,02 ; ouvriers -0,18 | recalcul | exact, mais **mécanique** |

**Logique.** Trois problèmes. (1) La question parle d'argent, la mesure est l'IPS des écoles, collèges et lycées publics (profil social, pas revenu). (2) La valeur ajoutée des lycées (IVAL) compare la réussite au bac à celle attendue compte tenu de l'origine sociale et du niveau des élèves : son indépendance vis-à-vis des CSP est en grande partie voulue par sa construction, ce n'est pas une découverte. (3) Le « tiers » n'a pas de point de comparaison : la part est de 32 % dans les départements favorisés aux trois étapes (8 sur 25) et de 26 % dans les autres. Le constat utile est justement que les départements défavorisés ne font pas moins bien que prévu. « Relégation scolaire » est un terme chargé.

**Correction proposée**
- question : `Les lycées des territoires modestes font moins bien que prévu ?`
- verdict : `faux`
- chiffre : `8 sur 22`
- chiffreLabel : `départements défavorisés aux trois étapes où les lycées font mieux que prévu au bac, autant que dans les départements favorisés (8 sur 25)`
- texte : `La valeur ajoutée compare la réussite au bac à ce que laisse attendre le profil des élèves. Elle ne suit ni le revenu du territoire, ni les prix de l'immobilier : le lycée qui fait progresser n'est pas forcément là où on l'attend. Les écarts restent souvent faibles, de l'ordre d'un point.`

---

## Synthèse

**Cartes sûres (retouches de libellé seulement)** : 11 (espérance de vie, préciser « hommes »), 3 (sport), 9 (auto-écoles), 10 (public, privé), 8 (Parcoursup), 2 (revenus).

**Cartes à corriger avant diffusion, par ordre de gravité**
1. **Élus** (4) : verdict « Faux » contredit par les fichiers 2020 du dossier (hausse à tous les niveaux comparables) ; « à chaque marche le filtre se resserre » contredit par les chiffres de la carte (2,0 puis 2,7 %) ; ÷ 3,7 surtout géographique (le filtre propre est d'environ ÷ 1,9, au choix des têtes de liste) ; ÷ 3,7 sur la carte contre ÷ 4 sur la page ; « nom issu de la diversité » sans garde-fou.
2. **État-providence** (6) : « record », « le pays qui dépense le plus » est faux avec les données 2024 et 2025 (Finlande devant), déjà présentes dans la série du site ; AROPE 2025 disponible (27,5 %).
3. **Ségrégation** (1) : « 1 sur 3 » est vrai par construction (tiers supérieur d'un classement), il ne dit rien de la France.
4. **Retraites** (13) : -39 % présenté comme l'écart de « pension de retraite » alors que c'est le droit direct ; l'écart sur la pension totale est de 24 % ; données 2019.
5. **Information des jeunes** (7) : 77 % se lit « 77 % s'informent » ; le bon chiffre pour la question est 96 % ; « 41 % via la télévision » omet « chaque jour ».
6. **HLM** (14) : « départements urbains et aisés » faux (la Seine-Saint-Denis est en tête) ; verdict à passer en « Pas partout ».
7. **Santé en Europe** (12) : « Vrai, mais » valide « meilleur système du monde » sans appui ; millésime 2024 disponible.
8. **Réussite scolaire** (15) : question sur l'argent, mesure sur l'IPS ; absence de lien avec les CSP en partie mécanique ; 8 sur 22 et non 23 ; pas de point de comparaison.
9. **Assemblée** (5) : « la diversité s'arrête à la porte du mandat » non significatif ; « actifs » au lieu de « personnes en emploi ».

**Ce qui reste incertain**
- Existence de millésimes plus récents pour : FiLoSoFi IRIS (2022 ou 2023), licences INJEP 2024, Parcoursup 2026, Arcom 2025, pensions Drees (données 2023 ou 2024) ; non vérifiés en ligne.
- Rupture possible de la série française AROPE en 2022.
- La comparaison 2020-2026 des maires demande l'archive 2020 du Répertoire national des élus ; celle des élus ne couvre que les communes pourvues au premier tour les deux années.
- Valeurs `rdGrandes` et `rdPetites` de la page Ségrégation non vérifiées à l'écran.

---

## Corrections appliquées le 30/10/2026

Toutes les corrections ci-dessus ont été appliquées, avec l'option A pour la carte Élus. Copies de sauvegarde en `.bak_20261030` à côté de chaque fichier modifié. Rien n'est déployé. Build (`npm run build`) et tests (`npx vitest run`, 57 sur 57) passent.

Une précision par rapport au rapport : avec le millésime 2024, la France est 9e sur 30 pour l'espérance de vie (83,0 ans, à égalité avec Malte), et non 10e.

| Carte | Avant | Après |
|---|---|---|
| 1. Ségrégation | « 1 sur 3 des villes ont des quartiers riches et pauvres nettement séparés » (vrai par construction) | « × 1,6 » : dans la ville type, niveau de vie des îlots les plus aisés rapporté aux plus modestes (chiffre de la page, non construit) ; classement présenté comme relatif ; Paris décrit au niveau IRIS ; millésimes 2019 et 2021 dans la source |
| 2. Revenus | « la proche banlieue parisienne monte », « partout, les revenus augmentent » | « les communes limitrophes de Paris montent », recul « souvent de peu », contrôle 2023 cité, « presque partout » |
| 3. Sport | « l'absence des autres sports », « ce n'est pas faute de demande » | « la moindre pratique en club des autres sports », « près de trois fois plus de licenciés résidents par terrain » |
| 4. Élus | « La politique française se diversifie ? » Faux, ÷ 3,7, « à chaque marche le filtre se resserre », « nom issu de la diversité » | « La politique locale se diversifie ? » Vrai, mais ; « 2,6 → 3,2 % » d'élus au premier tour, mêmes communes, 2020 à 2026 ; candidats 5,4 → 6,2 %, têtes de liste 2,5 → 3,3 % ; filtre situé au choix des têtes de liste (2 % contre 3 % des colistiers) ; garde-fou « indicateur de groupe, pas une origine » |
| 5. Assemblée | « des actifs », « la diversité s'arrête à la porte du mandat » | « des personnes en emploi », « se déclarent cadres », écart de noms « à confirmer, sur une vingtaine de députés » |
| 6. État-providence | « Champion des dépenses publiques… », 56,8 %, « record », 26,2 %, « 6 pays font pire » (2023-2024) | « Beaucoup de dépense publique, des enfants mieux protégés ? » ; 27,5 % d'enfants menacés ; 57,3 % du PIB, 2e derrière la Finlande (57,5 %) ; 4 pays sur 28 font pire ; dépense qui finance d'abord retraites et santé (millésime 2025) |
| 7. Information des jeunes | « 77 % des 18-24 ans s'informent », « 41 % via la télévision » | « 96 % s'informent au moins une fois par mois, 90 % chaque jour » ; « 41 % chaque jour par la télévision » ; 77 % = premier moyen numérique, écrans compris |
| 8. Sélectivité | « la plus sélective », « taux d'accès au BPJEPS », « Sciences Po » | « la plus difficile d'accès », « taux d'accès médian », « instituts d'études politiques », ce que mesure le taux d'accès, licence « faute de places plus que par sélection » |
| 9. Auto-écoles | « dépend d'abord du département », « coûte 2,8 points » | « dépend pour un quart du département », « va avec 2,8 points de moins », millésime du fichier |
| 10. École | « comparable à celui des beaux quartiers », « invisible dans les moyennes nationales » | « plus favorisé que la moyenne des collèges publics de Paris (115) », « l'écart le plus grand de métropole : 34 points », rentrée 2025 |
| 11. Espérance de vie | « un cadre de 35 ans » | « un homme cadre de 35 ans », écart de 3,4 ans chez les femmes |
| 12. Santé en Europe | « Le meilleur système de santé du monde ? » Vrai, mais ; 25e / 30, 4,0 ‰, UE 3,3, 9e (2023) | « La France, bon élève de la santé en Europe ? » Vrai, mais ; 24e / 30, 4,1 ‰, UE 3,5, espérance de vie 9e (2024) ; mention de l'enregistrement des grands prématurés |
| 13. Retraites | « −39 % de pension de retraite » | « −39 % de pension de droit direct, femmes de 65 ans ou plus, 2019 » ; pension totale −24 % ; « contribuent à » |
| 14. HLM | Faux ; « départements urbains et aisés » | Pas partout ; « les départements urbains, aisés ou modestes (Seine-Saint-Denis, 31 %) » |
| 15. Réussite scolaire | « L'argent fait la réussite scolaire ? » Pas partout ; « 8 sur 23 » ; « relégation » | « Les lycées des territoires modestes font moins bien que prévu ? » Faux ; « 8 sur 22, autant que chez les favorisés (8 sur 25) » ; écarts « de l'ordre d'un point » ; bouton vers /terrains/ecole, qui affiche la comparaison |

**Données mises à jour**
- `python/tools/build_international.py` relancé : dépenses publiques et pauvreté des enfants en 2025 (Islande et Suisse manquent pour la pauvreté), espérance de vie et mortalité infantile en 2024 ; `pays.json` réécrit (note « millésimes 2024-2025 »).
- `python/tools/build_showcase_elus.py` relancé : `elus-diversite.json` reçoit `filtre` (comparaison commune par commune) et `evolution` (2020 et 2026, mêmes communes, sources data.gouv.fr).
- `age.json` : deux indicateurs ajoutés, « S'informe régulièrement » et « S'informe chaque jour », recalculés sur la base Arcom (pondération POIDS03).

**Pages alignées**
- `/terrains/elus` : entonnoir retiré ; tableau 2020 et 2026 avec sources ; section « Où se perd la diversité ? » (géographie et sélection, ÷ 3,7 brut contre ÷ 1,9 commune par commune) ; chiffre clé « 2,6 → 3,2 % » au lieu de « ÷ 4 » ; légende des partis corrigée ; garde-fou explicite.
- `/international` : rang de la France sur les dépenses calculé (plus de « record » écrit en dur), pauvreté des enfants avec le nombre de pays qui font pire, mortalité infantile « jusqu'en 2014 », mention des grands prématurés, millésimes 2024-2025.
- `/explorer/pays` et `/explorer/age` (`config/decoupages.js`) : aides mises à jour (2e derrière la Finlande, « longtemps meilleure que la moyenne européenne », définitions Arcom « au moins une fois par jour », numérique écrans compris).
- `/segregation` : « fracturées » présenté comme le tiers relatif ; définition du × 1,6 corrigée (déciles des carreaux, pas « le quartier le plus aisé »).
- `/terrains/ecole` : « 8 sur 22 » avec la comparaison aux départements favorisés ; texte public-privé sans « invisible » ni attribution causale.
- `/terrains/assemblee` : « personnes en emploi » ; section « Des collaborateurs aux députés » (parité nette, noms non établis).
- `/terrains/revenus` et `/terrains/auto-ecoles` : phrases d'en-tête alignées.
- `config/seo.js` (élus, international, pays, âge, sélectivité, revenus) et `config/indicateurs.js` (« diversité des noms », garde-fou).

**Reste à décider**
- Le vocabulaire « relégation » demeure ailleurs dans `/terrains/ecole` et dans `CroisementScatter.jsx`.
- La comparaison des maires 2020 et 2026 suppose une archive du répertoire des élus postérieure au second tour de 2020.
- Les millésimes plus récents restent à vérifier : FiLoSoFi IRIS, licences INJEP, Parcoursup 2026, Arcom, pensions de la Drees.
