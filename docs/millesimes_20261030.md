# Millésimes des sources du site : vérification et mises à jour du 30/10/2026

Vérification, source par source, du dernier millésime publié (site du producteur, data.gouv.fr, API Eurostat, Education nationale et MESR), puis mise à jour de ce qui se faisait en changeant le fichier d'entrée sans changer la méthode. Rien n'est déployé.

Sauvegardes : chaque fichier de code ou de texte modifié a sa copie `.bak_20261030` à côté (sauf ceux qui en avaient déjà une de ce jour). Les données régénérées (`atlas/`, `showcases/`, `decoupages/`, `onomastics/`) sont copiées telles qu'avant dans `_archive/bak_20261030/frontend/public/data/`, hors du dossier publié.

Statuts : **mis à jour** ; **déjà à jour** ; **à faire** (avec l'effort) ; **libellé corrigé** (données déjà au dernier millésime, étiquette fausse).

## Tableau des sources

| Source | Millésime utilisé | Dernier millésime publié (date, lien) | Action |
|---|---|---|---|
| Prix immobilier DVF (Atlas, fiche territoire, École) | statistiques DVF d'avril 2026 | statistiques DVF du 21/10/2026, ventes de juillet 2021 à juin 2026, [data.gouv.fr, Statistiques DVF](https://www.data.gouv.fr/datasets/statistiques-dvf) | **mis à jour** : l'ancienne adresse `object.files.data.gouv.fr` restait figée en avril ; nouvelle adresse dans `build_ecole.py` et `build_atlas_communes.py`, chaîne Atlas relancée |
| Eurostat, décrochage, Gini, emploi des 55-64 ans, heures des temps pleins (Pays, France en Europe) | 2024 | 2025 (mises à jour Eurostat du 10/09 au 26/10/2026), [edat_lfse_14](https://ec.europa.eu/eurostat/databrowser/view/edat_lfse_14/default/table?lang=fr), [ilc_di12](https://ec.europa.eu/eurostat/databrowser/view/ilc_di12/default/table?lang=fr), [lfsi_emp_a](https://ec.europa.eu/eurostat/databrowser/view/lfsi_emp_a/default/table?lang=fr), [lfsa_ewhun2](https://ec.europa.eu/eurostat/databrowser/view/lfsa_ewhun2/default/table?lang=fr) | **mis à jour** (`build_international.py`). Manquent en 2025 : Luxembourg (décrochage), Islande et Suisse (Gini) |
| Eurostat, dépenses publiques, pauvreté des enfants | 2025 | 2025 | déjà à jour (mis à jour le 29/10) |
| Eurostat, espérance de vie, mortalité infantile | 2024 | 2024 (2025 non publié) | déjà à jour |
| Niveau de vie par milieu social | ERFS 2021 (Revenus et patrimoine, édition 2024) | ERFS 2024, série 1996-2024 parue le 09/07/2026, [Insee 2489735](https://www.insee.fr/fr/statistiques/2489735) | **mis à jour** (`milieu-social.json`) ; même série, même champ (actifs de 18 ans ou plus ayant déjà travaillé) : les valeurs 2021 du site s'y retrouvent |
| Pauvreté par milieu social | ERFS 2021 | ERFS 2024, parue le 09/07/2026, [Insee 3566521](https://www.insee.fr/fr/statistiques/3566521) | **mis à jour**, même série (2021 identique au site) |
| Chômage par milieu social | enquête Emploi 2024 | enquête Emploi 2025, Emploi, chômage, revenus du travail édition 2026, parue le 02/07/2026, [Insee 8733055](https://www.insee.fr/fr/statistiques/8733055) | **mis à jour**, même tableau |
| Espérance de vie à 35 ans par catégorie sociale | 2020-2022 | 2020-2022 (paru le 16/07/2024, actualisation environ tous les 7 ans), [Insee 2383438](https://www.insee.fr/fr/statistiques/2383438) | déjà à jour |
| Abstention par catégorie sociale | élections de 2022 (Insee Première 1929) | aucune étude Insee sur 2024 trouvée | déjà à jour (prochain cycle 2027) |
| Taux d'emploi par sexe | « 2018 », Femmes et hommes édition 2020 | enquête Emploi 2025, parue le 02/07/2026, [Insee 8733041](https://www.insee.fr/fr/statistiques/8733041) | **mis à jour et corrigé** : le chiffre affiché (68,2 / 75,8) était le **taux d'activité** 2018, pas le taux d'emploi |
| Temps partiel par sexe | 2018 (salariés de 15-64 ans) | 2025, salariés de 15 ans ou plus hors apprentis, parue le 02/07/2026, [Insee 8733075](https://www.insee.fr/fr/statistiques/8733075) | **mis à jour** ; champ d'âge un peu différent (15 ans ou plus), précisé dans l'aide |
| Espérance de vie à la naissance par sexe | Bilan démographique 2024 | Bilan démographique 2025, paru le 13/01/2026, [Insee 8719824](https://www.insee.fr/fr/statistiques/8719824) | **mis à jour** (données provisoires) |
| Salaire en équivalent temps plein par sexe | 2024 (Insee Focus 377) | 2024 | déjà à jour |
| Pension de droit direct par sexe (carte « L'égalité femmes-hommes, c'est réglé ? ») | 2019, Insee Femmes et hommes édition 2022, montants nets, 65 ans ou plus | Drees, Les retraités et les retraites, édition 2026 (données 2024), écart brut de droit direct -37 %, -25 % avec la réversion ; édition 2025 (données 2023) : -38 %, [Drees édition 2025](https://drees.solidarites-sante.gouv.fr/publications-communique-de-presse-documents-de-reference/250731_PANORAMAS-retraites) | **à faire, effort faible à moyen (2 h)** : changement de source et de définition (brut et non net, tous retraités et non 65 ans ou plus) ; choisir la définition, reprendre les montants de la fiche Drees, réécrire la carte et l'aide. Page de l'édition 2026 non retrouvée sur le site de la Drees (vue dans une reprise secondaire) |
| Arcom, Les Français et l'information (`/explorer/age`, numérique par milieu social, carte « Les jeunes ne s'informent plus ? ») | 1re édition, terrain fin 2023, publiée le 14/03/2024 | 2e édition, terrain du 16/06 au 23/07/2025, base anonymisée sur data.gouv.fr le 04/06/2026, [jeu « Les Français et l'information, baromètre »](https://www.data.gouv.fr/datasets/les-francais-et-linformation-barometre) | **à faire, effort moyen (1 jour)** : seules 46 des 160 variables de la base 2024 gardent leur nom (`POIDS03`, `NEWS1BIS_R` disparaissent) ; il faut refaire la correspondance des questions, recalculer `age.json`, l'indicateur numérique de `milieu-social.json` et les chiffres de la carte (96 %, 90 %, 41 %, 89 %, 77 %), et vérifier que les questions sont posées pareil |
| Revenu médian Filosofi (Atlas, École, Auto-écoles, Sport) | Filosofi 2023 | Filosofi 2023 (paru le 06/08/2026), [Insee 8984752](https://www.insee.fr/fr/statistiques/8984752) | déjà à jour |
| Filosofi à l'IRIS (dossier Villes) | 2021 | 2021 : pas de fichier IRIS 2023 publié (Filosofi 2023 diffusé de la commune à la région), pas de millésime 2022 | déjà à jour |
| Filosofi, carreaux de 200 m (dossier Villes, carte de l'accueil) | affiché « 2019 » | 2021, paru le 12/02/2026, [Insee 8735162](https://www.insee.fr/fr/statistiques/8735162) | **libellé corrigé** : l'API Koumoul sert le millésime 2021 depuis le 04/03/2026 et le cache du 04/07/2026 est en 2021 (5 556 carreaux tirés au hasard identiques au fichier Insee 2021) ; source corrigée dans `Home.jsx` et `Segregation.jsx` |
| Filosofi 2014, 2021, 2023 (dossier Revenus) | 2014-2021, contrôle 2023 | idem | déjà à jour |
| Recensement 2023 (Atlas : diplômes, logement, âges, PCS) | RP 2023 | RP 2023 (RP 2024 attendu en 2027) | déjà à jour |
| Naissances (natalité) | 2021-2025, géographie 2026 | idem, [Insee 1893255](https://www.insee.fr/fr/statistiques/1893255) | déjà à jour |
| IPS des écoles | rentrée 2024-2025 | 2024-2025 (jeu modifié le 07/08/2026, pas de 2025-2026), [data.education.gouv.fr](https://data.education.gouv.fr/explore/dataset/fr-en-ips-ecoles-ap2022/) | déjà à jour |
| IPS des collèges et des lycées | rentrée 2025-2026 | 2025-2026 | déjà à jour |
| Valeur ajoutée des lycées (IVAL) | session 2025 | session 2025 (jeux du 10/06/2026) | déjà à jour |
| Auto-écoles, taux de réussite | affiché « fichier de juillet 2025 » | fichier servi le 19/02/2026 (en-tête du serveur), [data.gouv.fr](https://www.data.gouv.fr/datasets/liste-des-auto-ecoles-et-taux-de-reussite-au-permis-de-conduire) | **libellé corrigé** : le cache est identique, octet pour octet, au fichier du 19/02/2026 ; la date venait de la métadonnée data.gouv.fr restée au 01/07/2025. `build_auto_ecoles.py` lit désormais l'en-tête Last-Modified |
| Auto-écoles, contexte communal | recensement 2021 (fichier du 15/09/2026) | recensement 2023 (Atlas mis à jour le 29/10) | **mis à jour** : `build_auto_ecoles.py` relancé sur l'Atlas RP 2023 |
| Brevet par établissement (corrélations du dossier Auto-écoles) | sessions 2019 et 2021 | le jeu `fr-en-dnb-par-etablissement` s'arrête à 2021 ; les sessions 2022 à 2025 sont dans le jeu de la valeur ajoutée des collèges | **à faire, effort faible (1 h)** : changer de jeu et de colonnes, indicateur secondaire |
| Parcoursup (dossier Sélectivité) | session 2025 | session 2025 : le jeu `fr-esr-parcoursup` ne contient que 2025 et aucun jeu 2026 n'existe sur le portail du MESR au 30/10/2026 | déjà à jour (à revoir en fin d'année) |
| Licences sportives INJEP, géocodées (dossier Sport, carte « Le foot, sport des quartiers ? ») | 2023 | 2023 (fichier du 29/12/2025) ; le total 2024 par fédération existe, pas le fichier géocodé (le 2023 est sorti fin décembre 2025) | déjà à jour (à revoir en janvier 2027) |
| Population communale du dossier Sport | RP 2021 (`base-cc-evol-struct-pop-2021`) | RP 2023 | **à faire, effort moyen (demi-journée)** : passer par `rp2023.py` (format long), relancer les explorations sport et revérifier la carte de l'accueil |
| Prénoms Insee (moteur sexe et âge, outil Représentativité) | naissances 1900-2024 | naissances 1900-2025, diffusion de juillet 2026 (effectifs arrondis à 5), [Insee 8595130](https://www.insee.fr/fr/statistiques/8595130) | **mis à jour** (`build_onomastics_reference.py`) |
| Noms de famille Insee (IDP) | noms 1891-2000 | fichier figé, pas de nouvelle édition | déjà à jour |
| Répertoire national des élus (dossier Élus) | 11/08/2026 | 11/08/2026 | déjà à jour |
| Candidatures municipales 2020 et 2026 | | fichiers figés | déjà à jour |
| Assemblée nationale, députés en exercice (dossier sensible) | export du 05/07/2026 | export du 29/10/2026 : 574 députés en exercice, 13 sortis et 10 entrés depuis juillet | **vérifié, non modifié** : relancer `build_assemblee.py` après relecture (les chiffres de la carte « 6 / 577 », 66 %, 4,2 % peuvent bouger) |
| Assemblée, repères population (dossier sensible) | enquête Emploi 2023 (PCS) ; population au 01/01/2025 | enquête Emploi 2025, [Insee 8733043](https://www.insee.fr/fr/statistiques/8733043) ; population au 01/01/2026 | **vérifié, non modifié** : changement de repère à décider avec la relance ci-dessus |
| Évaluations de 6e, rythmes scolaires | 2025 | 2025 | déjà à jour |

Non touchés : encadré Élite du Sport, outil Représentativité (hors libellé « naissances 1900-2025 »), fichiers PISA.

## Chiffres visibles qui ont changé

**Prix immobilier (Atlas, fiche territoire, tableau de bord, dossier École)** : variations de l'ordre de 1 %. Médiane des départements 1 943 puis 1 974 €/m² ; Paris 10 247 puis 10 125 ; Hauts-de-Seine 6 918 puis 6 861 ; Creuse 801 puis 816. Croisement « prix et cadres » : corrélation entre communes +0,79 puis +0,82 ; les communes nommées au-dessus du pronostic restent Paris (6e, 7e), Saint-Tropez. Le jumeau statistique peut changer pour quelques communes.

**Pays et France en Europe (textes calculés)** :

| Indicateur | France avant (2024) | France après (2025) | UE27 avant / après | Rang de la France |
|---|---|---|---|---|
| Décrochage scolaire | 7,9 % | 7,2 % | 9,6 / 9,1 % | 15e / 30 puis 13e / 29 |
| Gini | 30,0 | 30,4 | 29,4 / 29,2 | 17e / 29 puis 18e / 28 |
| Emploi des 55-64 ans | 60,3 % | 61,7 % | 65,2 / 66,4 % | 20e / 30 |
| Heures des temps pleins | 40,0 h | 39,9 h | 40,3 / 40,3 h | 6e / 30 |

Allemagne, décrochage : 13,5 puis 13,1 %. Les messages des textes tiennent.

**Milieu social** (niveau de vie moyen en euros, 2021 puis 2024 ; pauvreté en %, 2021 puis 2024 ; chômage en %, 2024 puis 2025) :

| Catégorie | Niveau de vie | Pauvreté | Chômage |
|---|---|---|---|
| Indépendants | 32 380 → 36 440 | 17,4 → 21,5 | non calculé |
| Cadres | 41 960 → 47 870 | 2,9 → 3,2 | 3,9 → 4,0 |
| Professions intermédiaires | 29 050 → 33 080 | 4,8 → 5,8 | 5,0 → 5,0 |
| Employés | 23 480 → 27 100 | 12,1 → 13,3 | 8,8 → 9,1 (peu qualifiés 11,1 → 11,4) |
| Ouvriers | 22 250 → 25 600 | 13,9 → 15,2 | 10,8 → 11,4 (peu qualifiés 16,8 → 17,1) |
| Ensemble (repère) | 29 170 → 33 850 | 9,2 → 10,1 | 6,7 → 6,9 |

Les euros sont courants (2021 puis 2024) : la hausse reflète surtout l'inflation.

**Sexe** :

| Indicateur | Femmes | Hommes |
|---|---|---|
| Taux d'emploi des 15-64 ans | 68,2 → 66,7 % | 75,8 → 71,9 % (l'ancien chiffre était le taux d'activité 2018) |
| Temps partiel (salariés) | 28,8 → 26,6 % | 7,8 → 8,4 % ; aide : « environ 3 fois » au lieu de « environ 4 fois » |
| Espérance de vie à la naissance | 85,6 → 85,9 ans | 80,0 → 80,3 ans |

**Accueil (`Home.jsx`)** :
- Carte « Le meilleur taux de réussite fait la meilleure auto-école ? » : « 2,8 points de moins » devient « 2,7 points de moins » (contexte RP 2023) ; source « fichier du 19 février 2026 » ; le 44 % est inchangé (43,9 puis 44,2 %), le quart (25,4 %) aussi.
- Carte « Riches et pauvres vivent-ils séparés ? » : source « FiLoSoFi 2021 (carreaux de 200 m et IRIS) », lien vers la page des carreaux 2021 ; chiffres inchangés.
- Les autres cartes ne changent pas (aucune ne cite un chiffre mis à jour).

**Dossier Auto-écoles** : effets de contexte légèrement modifiés (taille de la commune -2,8 puis -2,7 points ; école associative -8,8 puis -8,9) ; profils départementaux en RP 2023 ; date du fichier ; mention « recensement 2023 ».

**Dossier Sport** : lien de la source revenu corrigé (Filosofi 2023, déjà utilisé par le calcul ; population RP 2021 précisée).

**Moteur onomastique** : 42 937 puis 43 455 prénoms ; dernière classe d'âge « 2020-2025 ». Validations inchangées : IDP des candidats 4,4 %, sexe juste à 99,3 % sur 96,7 % des candidats.

## Contrôles

- Chaîne Atlas relancée dans l'ordre de `DEPLOIEMENT.md` (de `build_ecole` à `build_croisements`) : seuls les champs `prix_m2` changent, plus les effectifs des communes qui gagnent ou perdent un prix ; 104 anciens codes de commune (fusions) sortent, 27 codes actuels entrent ; `etablissements.tsv` identique au tri près.
- `npm run build` : réussi (24 routes, sitemap). `npx vitest run` : 57 tests sur 57.

## Reste à faire, par ordre d'intérêt

1. **Arcom 2e édition** (1 jour) : la seule source vieille de deux ans qui alimente une carte de l'accueil.
2. **Pensions** (2 h) : choisir entre la Drees (brut, tous retraités, 2024) et une future édition Insee Femmes et hommes ; réécrire la carte « L'égalité femmes-hommes ».
3. **Assemblée** (à relire avant) : relancer le pipeline sur l'export du 29/10/2026 et passer les repères à l'enquête Emploi 2025.
4. **Sport** : population RP 2023 (demi-journée) ; licences géocodées 2024 attendues vers la fin décembre 2026.
5. **Brevet** dans les corrélations des auto-écoles (1 h).
6. À surveiller : Parcoursup 2026 (fin 2026), Filosofi à l'IRIS 2023, Eurostat espérance de vie et mortalité infantile 2025 (printemps 2027).

Remarque : des copies `.bak_20261030` faites le 29/10 par la vérification des cartes sont dans `frontend/public/data/` (`age.json`, `pays.json`, `elus-diversite.json`) et partent donc dans `dist/` au build : à déplacer avant de publier.
