# 16. Les lycées des territoires modestes font moins bien que prévu ?
> Carte `outsiders` · Faux · dossier /terrains/ecole · fiche préparée le 30/10/2026

## Ce qu'affiche la carte

- **Rubrique** : Reproduction sociale ; **unité** : Départements ; couleur verte (`#10B981`).
- **Question** : « Les lycées des territoires modestes font moins bien que prévu ? »
- **Verdict** : Faux.
- **Chiffre** : `8 sur 22`
- **Libellé du chiffre** : « départements défavorisés aux trois étapes où les lycées font mieux que prévu au bac, autant que chez les favorisés (8 sur 25) »
- **Texte** : « La valeur ajoutée compare la réussite au bac à ce que laisse attendre le profil des élèves. Elle ne suit ni le revenu du territoire, ni les prix de l'immobilier : le lycée qui fait progresser n'est pas forcément là où on l'attend. Les écarts restent souvent faibles, de l'ordre d'un point. »
- **Source citée** : « Éducation nationale, IVAL et IPS (data.gouv.fr) », lien vers le jeu IVAL des lycées généraux et technologiques : https://www.data.gouv.fr/datasets/indicateurs-de-valeur-ajoutee-des-lycees-denseignement-general-et-technologique-2
- **Bouton** : « Comparer les départements » vers `/terrains/ecole`.
- Historique : carte réécrite le 30/10/2026 après vérification (ancienne question « L'argent fait la réussite scolaire ? », verdict « Pas partout », « 8 sur 23 ») ; voir `docs/verification_cartes_accueil.md`, section 15.

## Ce que dit le dossier

Page `frontend/src/pages/terrains/TerrainEcole.jsx`, titre « L'école trie-t-elle ? » (même dossier que la carte `ecole`, voir `11_ecole.md`). Ce qui concerne cette carte :

- **En-tête** : « En suivant les trois étapes, école, collège, lycée, la ségrégation se révèle cumulative. Mais là où le lycée a une forte valeur ajoutée, l'école compense. »
- **Chiffres clés** : 23 départements « défavorisés aux 3 étapes », 25 « en entre-soi aux 3 étapes ».
- **Encadré « Défavorisé ne veut pas dire école qui échoue »** : « Sur les 22 départements défavorisés aux 3 étapes où la valeur ajoutée est connue, 8 ont des lycées à valeur ajoutée positive, autant que dans les départements favorisés (8 sur 25) ; l'école y fait mieux que prévu (meilleur : +7,1). Dans les autres, c'est la double peine : milieu défavorisé et résultats en dessous de l'attendu (pire : -4,6). »
- **« Le cumul des trois étapes »** : deux listes de départements (tiers bas et tiers haut aux trois niveaux d'IPS public), chacun avec ses trois IPS et sa valeur ajoutée de lycée, commentée « l'école compense » (positive) ou « sous-performe » (négative ou nulle).
- **« Ce qu'il faut retenir »** : « 23 dépts défavorisés aux trois étapes à la fois : le désavantage ne se rattrape pas, il s'empile » ; « 0,58, corrélation entre l'école et le revenu du territoire » (texte en dur) ; « 8 sur 22 (8 sur 25 chez les favorisés) : défavorisé n'est pas une fatalité ».
- **Carte des établissements**, vue « Valeur ajoutée » : chaque lycée en un point (3 337 lycées avec une valeur ajoutée).
- **Recherche d'établissement** : pour un lycée, valeur ajoutée et taux de réussite au bac.
- **Méthode et limites** : « La valeur ajoutée couvre les lycées GT + professionnels » ; « le cumul est calculé sur le public » ; années écoles 2024-2025, collèges et lycées 2025-2026.
- Autres sections du dossier (évitement scolaire, collèges décrochés de leur quartier, croisement IPS et revenu) : hors de cette carte, voir `11_ecole.md`.

## D'où viennent les chiffres

**Chaîne** : DEPP (data.education.gouv.fr, republié sur data.gouv.fr) -> téléchargement à chaque exécution, **sans cache local** -> `python/tools/build_ecole.py` (étape 2 de `docs/DEPLOIEMENT.md`, après `build_onomastics_reference.py`) -> `frontend/public/data/showcases/ecole-ips.json` (et `etablissements.tsv`, `ecole-communes.json`) -> `TerrainEcole.jsx` (calcul du « 8 sur 22 » dans le navigateur) ; la carte de l'accueil recopie le chiffre en dur.

**Étapes de `build_ecole.py`**
1. Pour chaque niveau, recherche du jeu sur l'API data.gouv.fr (`q="indice de position sociale écoles|collèges|lycées"`), choix du plus gros fichier CSV de la ressource, lecture avec libellés (`use_labels=true`). Garde la **dernière année** : écoles 2024-2025, collèges 2025-2026, lycées 2025-2026. IPS pris : `IPS` (écoles, collèges), `IPS de l'établissement` (lycées, toutes voies confondues).
2. IVAL : jeux GT et professionnel (recherche data.gouv), dernière session (2025), colonnes « Valeur ajoutée du taux de réussite - Toutes séries » et « Taux de réussite - Toutes séries ». Les deux jeux sont empilés puis **moyennés par UAI** (un lycée polyvalent présent dans les deux jeux reçoit la moyenne simple de sa VA GT et de sa VA pro).
3. Jointure par UAI sur le fichier des lycées IPS (3 662 lycées en 2025-2026 ; 173 sans valeur ajoutée ; 14 lignes IVAL sans IPS, perdues).
4. Par département : IPS moyen (moyenne simple des établissements) public, privé et tous, par niveau ; `va_lycee` = **moyenne simple des VA de tous les lycées du département, publics et privés, GT et pro**, arrondie à 0,1.
5. Départements gardés : ceux qui ont un IPS public aux trois niveaux (101). Pour chaque niveau, `pd.qcut` en **tiers** des 101 départements sur l'IPS public (seuils : écoles 99,9 / 103,8 ; collèges 97,5 / 102,1 ; lycées 99,6 / 104,0). `cumul = "triple-bas"` si le département est dans le tiers bas aux trois niveaux, `"triple-haut"` s'il est dans le tiers haut aux trois, sinon `"mixte"`.
6. Revenu (Filosofi 2023, `MED_SL` par département, via `revenu_filosofi.py`) et prix au m² (DVF, `med_prix_m2_whole_apt_maison`) ajoutés à chaque département.

**Calcul du chiffre (dans `TerrainEcole.jsx`)**
- « défavorisé aux trois étapes » = `cumul === 'triple-bas'` : 23 départements (18 en métropole + 971, 972, 973, 974, 976).
- 22 = ceux qui ont une `va_lycee` (Mayotte n'en a pas).
- 8 = ceux dont `va_lycee > 0` (strictement). Recalcul : 971 (+7,1), 93 (+2,9), 47 (+2,3), 972 (+1,3), 62 (+0,7), 974 (+0,6), 55 (+0,3), 52 (+0,2).
- « 8 sur 25 » : même calcul sur les 25 départements `triple-haut` (tous ont une VA ; trois sont à 0,0 et ne comptent pas).
- Non affiché mais calculable : 14 sur 53 dans les départements « mixtes ».
- Texte de la carte : corrélations entre départements de `va_lycee` avec le revenu (-0,07 sur 97 départements ; -0,04 en métropole) et avec le prix au m² (+0,19 ; +0,18 en métropole) ; « de l'ordre d'un point » : médiane des VA départementales -0,6, quartiles -1,4 et +0,3.

## Les jeux de données

### Indicateurs de valeur ajoutée des lycées d'enseignement général et technologique (IVAL GT)
- **Producteur** : DEPP, ministère chargé de l'Éducation nationale ; Licence ouverte 2.0.
- **Millésime utilisé** : session 2025 du baccalauréat. **Dernier disponible** : session 2025 (jeu modifié le 10/06/2026) ; session 2026 attendue au printemps 2027.
- **Pages** : https://www.data.gouv.fr/datasets/indicateurs-de-valeur-ajoutee-des-lycees-denseignement-general-et-technologique-2 ; https://data.education.gouv.fr/explore/dataset/fr-en-indicateurs-de-resultat-des-lycees-gt_v2/
- **Téléchargement direct** : https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-indicateurs-de-resultat-des-lycees-gt_v2/exports/csv?use_labels=true (séparateur `;`)
- **Documentation** : Guide méthodologique IVAL 2025, https://data.education.gouv.fr/api/v2/catalog/datasets/fr-en-indicateurs-de-resultat-des-lycees-gt_v2/attachments/guide_methodologique_ival_2025pdf
- **Fichier local** : aucun (téléchargé à chaque exécution).
- **Géographie** : établissement (UAI), avec commune, département, académie, région.
- **Lignes** : 32 485 (sessions 2012 à 2025, environ 2 300 lycées par session ; 2 346 en 2025). 88 colonnes.
- **Définition (description du producteur)** : valeur ajoutée = résultat observé moins résultat attendu, compte tenu de facteurs individuels (âge, sexe, niveau scolaire à l'entrée au lycée, profil social) **et** de facteurs de structure de l'établissement (part de filles, part d'élèves en retard, profil social des élèves, note moyenne au brevet). Approche relative. Taux bruts calculés à partir de 20 candidats ; VA et mentions à partir de 40 candidats. Valeurs publiées en points entiers.

| colonne | sens | utilisée ? |
|---|---|---|
| `annee` | session du bac (AAAA) | oui : filtre sur la dernière session |
| `uai` | identifiant de l'établissement | oui : jointure avec l'IPS |
| `libelle_uai` | nom de l'établissement | non |
| `secteur` | public ou privé sous contrat | non (le secteur vient du fichier IPS) |
| `code_commune`, `libelle_commune` | commune | non (prise dans le fichier IPS) |
| `code_departement`, `libelle_departement` | département | non (pris dans le fichier IPS) |
| `libelle_academie` | académie | non |
| `code_region`, `libelle_region` | région | non |
| `presents_total` | élèves présents au bac, toutes séries | non |
| `taux_reu_total` | taux de réussite observé, toutes séries | oui : affiché par lycée dans la recherche (« Réussite bac ») |
| `va_reu_total` | valeur ajoutée du taux de réussite, toutes séries | **oui : base du chiffre de la carte** |
| `taux_acces_2nde` | taux d'accès de la seconde au bac (part des entrants en 2nde qui obtiennent le bac dans le lycée) | non |
| `va_acces_2nde` | valeur ajoutée du taux d'accès 2nde-bac | non |
| `taux_acces_1ere`, `taux_acces_term` | taux d'accès de la première, de la terminale au bac | non |
| `va_acces_1ere`, `va_acces_term` | valeurs ajoutées de ces taux d'accès | non |
| `taux_men_total` | taux de mentions observé, toutes séries | non |
| `va_men_total` | valeur ajoutée du taux de mentions | non |
| `eff_2nde`, `eff_1ere`, `eff_term` | effectifs de seconde, première, terminale | non |
| `presents_l`, `presents_es`, `presents_s` | présents par série de l'ancien bac (L, ES, S, jusqu'en 2020) | non |
| `presents_gnle` | présents en bac général (depuis 2021) | non |
| `presents_sti2d`, `presents_std2a`, `presents_stmg`, `presents_stl`, `presents_st2s`, `presents_s2tmd`, `presents_sthr` | présents par série technologique | non |
| `taux_reu_l` ... `taux_reu_sthr` (11 colonnes, mêmes séries) | taux de réussite observé par série | non |
| `va_reu_l` ... `va_reu_sthr` (11 colonnes) | valeur ajoutée du taux de réussite par série | non |
| `taux_men_l` ... `taux_men_sthr` (11 colonnes) | taux de mentions observé par série | non |
| `va_men_l` ... `va_men_sthr` (11 colonnes) | valeur ajoutée du taux de mentions par série | non |
| `nb_mentions_tb_avecf_g`, `nb_mentions_tb_sansf_g`, `nb_mentions_b_g`, `nb_mentions_ab_g` | nombre de mentions TB avec félicitations, TB, B, AB, voie générale | non |
| `nb_mentions_tb_avecf_t`, `nb_mentions_tb_sansf_t`, `nb_mentions_b_t`, `nb_mentions_ab_t` | mêmes comptes, voie technologique | non |

Repères 2025 (lycées GT) : taux de réussite moyen 96,0 % (médiane 97) ; VA de réussite moyenne -0,2, nulle pour 20 % des lycées, positive pour 38 % ; VA de réussite moyenne +0,7 dans le privé, -0,6 dans le public ; taux d'accès 2nde-bac moyen 85 %.

### Indicateurs de valeur ajoutée des lycées d'enseignement professionnel (IVAL pro)
- **Producteur** : DEPP. **Millésime utilisé** : session 2025. **Dernier disponible** : 2025 (jeu modifié le 10/06/2026).
- **Pages** : https://www.data.gouv.fr/datasets/indicateurs-de-valeur-ajoutee-des-lycees-denseignement-professionnel ; https://data.education.gouv.fr/explore/dataset/fr-en-indicateurs-de-resultat-des-lycees-pro_v2/
- **Téléchargement direct** : https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-indicateurs-de-resultat-des-lycees-pro_v2/exports/csv?use_labels=true
- **Fichier local** : aucun. **Géographie** : établissement (UAI). **Lignes** : 28 258 (2012 à 2025 ; 2 014 en 2025). 88 colonnes.
- Seuils : taux bruts à partir de 10 candidats, VA à partir de 20. Le jeu **est bien lu** par `build_ecole.py` (même libellé de colonne que le GT) : la VA départementale mêle donc bac général, technologique et professionnel.

| colonne | sens | utilisée ? |
|---|---|---|
| `annee`, `uai` | session, identifiant | oui : filtre et jointure |
| `libelle_uai`, `secteur`, `code_commune`, `libelle_commune`, `code_departement`, `libelle_departement`, `libelle_academie`, `code_region`, `libelle_region` | identification et localisation | non |
| `presents_total` | présents au bac professionnel | non |
| `taux_reu_total` | taux de réussite observé | oui : moyenné avec le GT pour les lycées polyvalents, affiché dans la recherche |
| `va_reu_total` | valeur ajoutée du taux de réussite | **oui : moyennée avec la VA GT, entre dans `va_lycee`** |
| `taux_acces_2nde`, `va_acces_2nde` | taux d'accès 2nde-bac et sa VA | non |
| `taux_acces_1ere`, `taux_acces_term`, `va_acces_1ere`, `va_acces_term` | taux d'accès 1re-bac et terminale-bac, et leurs VA | non |
| `taux_men_total`, `va_men_total` | taux de mentions et sa VA | non |
| `eff_2nde`, `eff_1ere`, `eff_term` | effectifs par niveau | non |
| `presents_pluri_techno`, `presents_transfo`, `presents_genie_civil`, `presents_mat_souples`, `presents_meca_elec`, `presents_production` | présents par groupe de spécialités de la production | non |
| `presents_pluri_services`, `presents_echanges`, `presents_communication`, `presents_serv_personnes`, `presents_serv_collec`, `presents_services` | présents par groupe de spécialités des services | non |
| `taux_reu_<spécialité>` (12 colonnes, mêmes groupes) | taux de réussite par groupe de spécialités | non |
| `va_reu_<spécialité>` (12 colonnes) | VA du taux de réussite par groupe de spécialités | non |
| `taux_men_<spécialité>` (12 colonnes) | taux de mentions par groupe de spécialités | non |
| `va_men_<spécialité>` (12 colonnes) | VA du taux de mentions par groupe de spécialités | non |
| `nb_mentions_tb_sansf_p`, `nb_mentions_b_p`, `nb_mentions_ab_p` | nombre de mentions TB, B, AB | non |

Repères 2025 (lycées pro) : taux de réussite moyen 84,7 % ; VA moyenne -0,6, positive pour 43 % des lycées ; +1,8 dans le privé, -1,4 dans le public ; taux d'accès 2nde-bac moyen 63 %.

### Indices de position sociale des lycées (à partir de 2023)
- **Producteur** : DEPP. **Millésime utilisé** : rentrée 2025-2026. **Dernier disponible** : 2025-2026 (jeu modifié le 10/06/2026).
- **Pages** : https://www.data.gouv.fr/datasets/ips-lycees-a-partir-de-2023 ; https://data.education.gouv.fr/explore/dataset/fr-en-ips-lycees-ap2023/
- **Téléchargement direct** : https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-ips-lycees-ap2023/exports/csv?use_labels=true
- **Fichier local** : aucun. **Géographie** : établissement. **Lignes** : 10 905 (rentrées 2023 à 2025 ; 3 662 lycées en 2025-2026 : 1 565 LEGT, 1 097 LP, 1 000 LPO). 48 colonnes.
- Le producteur conseille de **ne pas surinterpréter des écarts d'IPS de 3 points ou moins** entre établissements.

| colonne | sens | utilisée ? |
|---|---|---|
| `rentree_scolaire` | année scolaire | oui : dernière rentrée |
| `code_region`, `code_region_insee`, `region_academique`, `code_academie`, `academie` | région académique, région Insee, académie | non |
| `code_du_departement`, `departement` | département | oui : maille du chiffre |
| `code_insee_de_la_commune`, `nom_de_la_commune` | commune | oui : agrégats communaux et EPCI (Atlas) |
| `uai`, `nom_de_l_etablissement` | identifiant, nom | oui : jointure, recherche |
| `secteur` | public ou privé sous contrat | oui : le classement « trois étapes » porte sur le public |
| `type_de_lycee` | LEGT, LP ou LPO | non |
| `ips_voie_gt` | IPS des élèves de la voie générale et technologique | non |
| `ips_voie_pro` | IPS des élèves de la voie professionnelle | non |
| `ips_post_bac` | IPS des élèves post-bac (BTS, CPGE) | non |
| `ips_etab` | IPS de l'ensemble des élèves de l'établissement | **oui : IPS « lycée » du classement en tiers** |
| `ecart_type_voie_gt`, `ecart_type_voie_pro`, `ecart_type_etablissement` | écart-type de l'IPS (mixité sociale interne) | non |
| `ips_national_legt`, `ips_national_lpo`, `ips_national_lp` et leurs déclinaisons `_prive`, `_public` (9 colonnes) | IPS national de référence par type de lycée et secteur | non |
| `ips_academique_*` (9 colonnes) | mêmes références à l'échelle de l'académie | non |
| `ips_departemental_*` (9 colonnes) | mêmes références à l'échelle du département (moyennes officielles pondérées par les élèves) | non (le site recalcule une moyenne simple des établissements) |

Repère : IPS moyen voie GT 117, voie pro 92 ; écart-type moyen dans un lycée 30.

### Indices de position sociale des collèges (à partir de 2023)
- **Producteur** : DEPP. **Millésime utilisé** : 2025-2026 (dernier, jeu modifié le 01/09/2026).
- **Pages** : https://www.data.gouv.fr/datasets/ips-colleges-a-partir-de-2023 ; https://data.education.gouv.fr/explore/dataset/fr-en-ips-colleges-ap2023/
- **Téléchargement direct** : https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-ips-colleges-ap2023/exports/csv?use_labels=true
- **Fichier local** : aucun. **Géographie** : établissement. **Lignes** : 21 061 (2023 à 2025 ; 7 089 collèges en 2025-2026). 24 colonnes.

| colonne | sens | utilisée ? |
|---|---|---|
| `rentree_scolaire` | année scolaire | oui |
| `code_region`, `region_insee`, `region_academique`, `code_academie`, `academie` | région et académie | non |
| `code_du_departement`, `departement` | département | oui |
| `code_insee_de_la_commune`, `nom_de_la_commune` | commune | oui |
| `uai`, `nom_de_l_etablissement` | identifiant, nom | oui |
| `secteur` | public ou privé sous contrat | oui |
| `ips` | IPS moyen des élèves du collège | oui : IPS « collège » du classement en tiers |
| `ecart_type_de_l_ips` | écart-type de l'IPS des élèves | non |
| `ips_national`, `ips_national_public`, `ips_national_prive` | références nationales | non |
| `ips_academique`, `ips_academique_public`, `ips_academique_prive` | références académiques | non |
| `ips_departemental`, `ips_departemental_public`, `ips_departemental_prive` | références départementales officielles | non |

### Indices de position sociale des écoles (à partir de 2022)
- **Producteur** : DEPP. **Millésime utilisé** : 2024-2025 (dernier ; pas de 2025-2026 au 30/10/2026, jeu modifié le 07/08/2026).
- **Pages** : https://www.data.gouv.fr/datasets/indices-de-position-sociale-dans-les-ecoles-a-partir-de-2022 ; https://data.education.gouv.fr/explore/dataset/fr-en-ips-ecoles-ap2022/
- **Téléchargement direct** : https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-ips-ecoles-ap2022/exports/csv?use_labels=true ; table de passage PCS-IPS en pièce jointe (`IPS-PCS - Table de passage - Septembre 2022.xlsx`).
- **Fichier local** : aucun. **Géographie** : école. **Lignes** : 97 080 (2022 à 2024 ; 32 494 écoles en 2024-2025, dont 29 990 retenues avec un IPS). 23 colonnes.

| colonne | sens | utilisée ? |
|---|---|---|
| `rentree_scolaire` | année scolaire | oui |
| `code_region`, `region`, `code_de_l_academie`, `academie` | région académique, académie | non |
| `code_du_departement`, `departement` | département | oui |
| `code_insee_de_la_commune`, `nom_de_la_commune` | commune | oui |
| `uai`, `nom_de_l_etablissement` | identifiant, nom | oui |
| `secteur` | public ou privé sous contrat | oui |
| `ips` | IPS moyen des élèves de l'école | oui : IPS « école » du classement en tiers |
| `ips_national`, `ips_national_public`, `ips_national_prive` | références nationales | non |
| `ips_academique`, `ips_academique_public`, `ips_academique_prive` | références académiques | non |
| `ips_departemental`, `ips_departemental_public`, `ips_departemental_prive` | références départementales officielles | non |
| `num_ligne` | numéro technique | non |

Pas d'écart-type de l'IPS au niveau des écoles.

### Revenu : Insee, Filosofi 2023 (texte de la carte, « ne suit ni le revenu »)
- **Intitulé** : Indicateurs sur les revenus et la pauvreté au niveau local en 2023 ; **millésime** 2023, dernier publié (06/08/2026).
- **Page** : https://www.insee.fr/fr/statistiques/8984752 ; **téléchargement** : https://www.insee.fr/fr/statistiques/fichier/8984752/FILOSOFI_CC_csv.zip
- **Fichier local** : `python/tools/_cache_filosofi/DS_FILOSOFI_CC_2023_data.csv` (1 123 173 lignes, format long ; métadonnées dans le zip : `DS_FILOSOFI_CC_2023_metadata.csv`).
- **Géographie** : communes, arrondissements municipaux, EPCI, départements, régions, France, et zonages (unités urbaines, aires d'attraction, bassins de vie, zones d'emploi).
- **Dimensions** : `GEO`, `GEO_OBJECT` (COM, ARM, EPCI, DEP, REG, FRANCE, UU2020, AAV2020, BV2022, ZE2020, ARR, OTHER), `FILOSOFI_MEASURE`, `UNIT_MULT`, `UNIT_MEASURE` (EUR_YR, PT, NR), `CONF_STATUS` (F libre, C confidentiel), `OBS_STATUS` (A normale, O valeur manquante), `TIME_PERIOD`, `OBS_VALUE`.

| mesure (`FILOSOFI_MEASURE`) | sens | utilisée ? |
|---|---|---|
| `MED_SL` | niveau de vie médian (euros) | oui : `revenu` du département |
| `D1_SL` ... `D9_SL` (sauf D5), `Q1_SL`, `Q3_SL` | déciles et quartiles du niveau de vie | non (pour cette carte) |
| `IR_D9_D1_SL`, `IQR_SL`, `S80S20_SL`, `GI_SL` | rapport interdécile, écart interquartile, rapport S80/S20, indice de Gini | non |
| `PR_MD60` | taux de pauvreté au seuil de 60 % | non |
| `S_EI_DI`, `S_EI_DI_SAL`, `S_EI_DI_N_SAL`, `S_EI_DI_UNE` | parts des revenus d'activité, salaires, non-salariés, chômage dans le revenu disponible | non |
| `S_RET_PEN_DI`, `S_INC_ASS_DI` | parts des pensions et des revenus du patrimoine | non |
| `S_SOC_BEN_DI`, `S_SOC_BEN_DI_FAM_BEN`, `S_SOC_BEN_DI_HOU_BEN`, `S_SOC_BEN_DI_MIN_SOC` | parts des prestations sociales, familiales, logement, minima sociaux | non |
| `S_DIR_TAX_DI` | part des impôts directs | non |

Aucune valeur pour 971, 972, 973 et 976 au département : 4 départements sans revenu.

### Prix immobilier : Statistiques DVF (texte de la carte, « ni les prix de l'immobilier »)
- **Producteur** : DGFiP, statistiques calculées par data.gouv.fr ; fichier du 21/10/2026, ventes de juillet 2021 à juin 2026 (dernier).
- **Page** : https://www.data.gouv.fr/datasets/statistiques-dvf ; **téléchargement** : https://data-pipeline-open.s3.sbg.io.cloud.ovh.net/dvf/stats_whole_period.csv
- **Fichier local** : aucun pour `build_ecole.py` (le même fichier est en cache pour un autre script : `python/tools/_cache_territoires/stats_whole_period.csv`, 503 703 lignes : nation, 101 départements, 1 353 EPCI, 39 162 communes, 463 086 sections cadastrales).

| colonne | sens | utilisée ? |
|---|---|---|
| `code_geo`, `libelle_geo`, `code_parent`, `echelle_geo` | territoire et échelle | oui : départements et communes |
| `nb_ventes_whole_appartement`, `moy_prix_m2_whole_appartement`, `med_prix_m2_whole_appartement` | ventes et prix au m² des appartements | non |
| `nb_ventes_whole_maison`, `moy_prix_m2_whole_maison`, `med_prix_m2_whole_maison` | idem, maisons | non |
| `nb_ventes_whole_apt_maison`, `moy_prix_m2_whole_apt_maison` | ventes et prix moyen, appartements et maisons | non |
| `med_prix_m2_whole_apt_maison` | prix médian au m², appartements et maisons | oui : `prix_m2` |
| `nb_ventes_whole_local`, `moy_prix_m2_whole_local`, `med_prix_m2_whole_local` | idem, locaux | non |

### Entrées techniques
- **Annuaire de l'éducation** (https://www.data.gouv.fr/datasets/annuaire-de-leducation ; export `fr-en-annuaire-education`, 68 567 lignes, mis à jour le 29/10/2026) : seules `identifiant_de_l_etablissement`, `latitude`, `longitude` sont lues (points de la carte). 72 colonnes, dont `appartenance_education_prioritaire`, `voie_generale`, `voie_technologique`, `voie_professionnelle`, `segpa`, `ulis`, `lycee_des_metiers`, `lycee_agricole`, `post_bac`, `hebergement`, `restauration`, `section_internationale`, `section_europeenne`, `type_contrat_prive`, `libelle_bassin_formation`, non utilisées.
- **Communes vers EPCI** : `python/data/municipales/communes-epci.json` (geo.api.gouv.fr), pour les agrégats intercommunaux de l'Atlas.

## Ce qu'on n'exploite pas encore

- **`va_acces_2nde` (valeur ajoutée du taux d'accès 2nde-bac)** : c'est l'indicateur que la DEPP met en avant pour juger l'accompagnement d'un lycée, car il ne récompense pas un lycée qui fait partir ses élèves fragiles avant le bac. Le taux de réussite au bac est quasi plafonné en GT (96 % en moyenne) : sa VA a peu de marge. Recalcul sur la méthode du site : 9 départements défavorisés sur 22 ont une VA d'accès positive, contre 7 sur 25 chez les favorisés.
- **VA des mentions (`va_men_total`)** : dit si le lycée amène ses élèves au-delà de la simple obtention. Résultat différent : 12 sur 22 chez les défavorisés, 16 sur 25 chez les favorisés. Il nuancerait la carte (les lycées des départements favorisés font mieux que prévu sur les mentions).
- **Séparer GT et professionnel** : la VA départementale mêle deux examens différents. Sur le GT seul, 12 départements défavorisés sur 22 ont une VA positive, contre 8 sur 25.
- **Séparer public et privé** : la VA moyenne est positive dans le privé (+0,7 GT, +1,8 pro) et négative dans le public (-0,6 et -1,4). Or le classement « trois étapes » porte sur le public, et la VA sur public plus privé. Sur le public seul : 7 sur 22 contre 5 sur 25.
- **Pondérer par les élèves (`presents_total`)** : la moyenne simple donne le même poids à un lycée de 40 et de 800 candidats. Pondéré, public seul : 7 sur 22 contre 3 sur 25.
- **La série 2012-2025** : quatorze sessions sont dans le fichier. Le chiffre varie selon l'année (défavorisés contre favorisés : 2022, 5 sur 22 contre 10 sur 25 ; 2024, 11 sur 22 contre 6 sur 25 ; 2025, 8 sur 22 contre 8 sur 25). Une moyenne sur trois sessions, ou la part des départements positifs trois années de suite (6 défavorisés, 3 favorisés pour 2023-2025), serait plus solide qu'une seule session.
- **L'échelle de l'établissement** plutôt que du département : chez les lycées publics GT, 38 % du tiers le plus modeste (IPS de la voie GT) ont une VA positive, contre 25 % du tiers le plus favorisé ; en voie pro, 42 % contre 39 %. Même message que la carte, sur 1 500 lycées au lieu de 47 départements.
- **IPS par voie (`ips_voie_gt`, `ips_voie_pro`)** : l'IPS « lycée » du classement mêle les voies ; un département riche en lycées professionnels paraît plus modeste. L'IPS de la voie GT, rapproché de la VA GT, serait plus cohérent.
- **Écart-type de l'IPS** (collèges, lycées) : mesure la mixité sociale interne ; permettrait de demander si les lycées mixtes font mieux que prévu.
- **Références départementales officielles (`ips_departemental_public`)** : moyennes pondérées par les élèves, alors que le site calcule une moyenne simple des établissements.
- **Effectifs et mentions par série** : réussite selon la série technologique (STMG, ST2S), là où les élèves modestes sont nombreux.

## Autres sources possibles

- **Indicateurs de valeur ajoutée des collèges (IVAC)**, DEPP, sessions 2022 à 2025 du brevet (26 869 lignes) : https://www.data.gouv.fr/datasets/indicateurs-de-valeur-ajoutee-des-colleges. Colonnes : `nb_candidats_g`, `taux_de_reussite_g`, `va_du_taux_de_reussite_g`, `note_a_l_ecrit_g`, `va_de_la_note_g`, `taux_d_acces_6eme_3eme`, `part_presents_3eme_segpa_total`, mentions. Permettrait de tester la même question au collège (étape 2 des « trois étapes ») avec un attendu tiré des évaluations de 6e.
- **Résultats consolidés aux évaluations nationales de début de sixième par établissement**, DEPP : https://www.data.gouv.fr/datasets/resultats-consolides-aux-evaluations-nationales-de-debut-de-sixieme-par-etablissement. Niveau à l'entrée au collège.
- **Évaluations nationales Repères (CP, CE1, CE2, CM1, CM2) par département**, DEPP : par exemple https://www.data.gouv.fr/datasets/les-evaluations-nationales-reperes-cp-par-departement. Niveau à l'école, à la maille de la carte.
- **Réussite au baccalauréat selon l'origine sociale**, DEPP : https://www.data.gouv.fr/datasets/reussite-au-baccalaureat-selon-lorigine-sociale ; et **Réussite au baccalauréat par département** : https://www.data.gouv.fr/datasets/reussite-au-baccalaureat-par-departement. Repère national direct de l'écart social.
- **InserJeunes, voie professionnelle scolaire par établissement**, DEPP et Dares : https://www.data.gouv.fr/datasets/inserjeunes-voie-professionnelle-scolaire-par-etablissement-relevant-du-ministere-de-leducation-nationale (taux d'emploi à 6, 12 et 24 mois, poursuite d'études, avec une valeur ajoutée). Prolonge la question après le bac pro.
- **Établissements de l'éducation prioritaire** : https://www.data.gouv.fr/datasets/etablissements-de-leducation-prioritaire (et colonne `appartenance_education_prioritaire` de l'annuaire). Les lycées n'en relèvent pas, mais les collèges qui les alimentent oui.
- **Indice d'éloignement des collèges depuis 2022** : https://www.data.gouv.fr/datasets/indice-deloignement-des-colleges-depuis-2022. Le « territoire modeste » n'est pas seulement social ; utile pour le rural.
- **Effectifs d'élèves en lycée GT et en lycée professionnel** (par niveau, sexe, langues) : https://www.data.gouv.fr/datasets/effectifs-deleves-par-niveau-sexe-langues-vivantes-1-et-2-les-plus-frequentes-par-lycee-denseignement-general-et-technologique-date-dobservation-au-debut-du-mois-doctobre-chaque-annee. Pour pondérer par les élèves.
- **IPS 2016-2021** (écoles, collèges, lycées) : par exemple https://www.data.gouv.fr/datasets/indices-de-position-sociale-dans-les-lycees-de-france-metropolitaine-et-drom ; rupture de série en 2022 (nouvelle table de passage), comparaison dans le temps à éviter.
- **Parcoursup 2025, vœux et réponses** : https://www.data.gouv.fr/datasets/parcoursup-2025-voeux-de-poursuite-detudes-et-de-reorientation-dans-lenseignement-superieur-et-reponses-des-etablissements-1. Par formation, pas par lycée d'origine : ne permet pas de suivre les élèves d'un lycée ; aucun jeu public par lycée d'origine trouvé.

## Points de relecture

1. **La réponse « Faux » répond à une autre question que celle posée.** Prise au mot (« font moins bien que prévu ? »), la réponse serait plutôt oui : 14 des 22 départements défavorisés ont une VA nulle ou négative. Mais c'est aussi le cas de 17 favorisés sur 25 et de 39 mixtes sur 53 : la moyenne simple des VA est négative presque partout (médiane des départements -0,6). Ce que montrent les données : **pas plus souvent que les autres**. Formulation possible : « Les lycées des territoires modestes font-ils moins bien que prévu que les autres ? » ou un libellé qui dise « ni plus ni moins souvent qu'ailleurs ».
2. **« 8 sur 25 » dépend d'un arrondi.** Trois départements favorisés ont une VA arrondie à 0,0 ; sans arrondi, l'un est positif et le chiffre devient 9 sur 25. Avec un seuil d'un point (VA >= +1), le compte tombe à 4 défavorisés sur 22 et 2 favorisés sur 25.
3. **Le chiffre est fragile d'une session à l'autre** (5 sur 22 en 2022, 11 sur 22 en 2024) et selon la définition (public seul, GT seul, pondéré : de 7 à 12 sur 22). Le **sens** tient dans toutes les variantes testées (les défavorisés ne font jamais moins souvent mieux que prévu que les favorisés), sauf pour les mentions. C'est ce sens qu'il faut afficher, pas le chiffre exact.
4. **Les outre-mer pèsent lourd** : 3 des 8 départements positifs sont en outre-mer (Guadeloupe +7,1, valeur la plus forte de France). En métropole seule : 5 sur 18 (28 %), contre 8 sur 25 (32 %) chez les favorisés. « Autant que » tient encore, de justesse.
5. **Mélange de champs** : le classement « défavorisé » porte sur le public, la VA sur public et privé, GT et pro, en moyenne simple. Le privé ayant une VA positive en moyenne, la part de lycées privés (27 % chez les défavorisés, 34 % chez les favorisés) joue sur le résultat. À dire, ou à corriger dans le calcul.
6. **Absence de lien avec le revenu : en partie construite.** L'IVAL neutralise le profil social des élèves et de l'établissement (description du producteur). Que la VA ne suive ni le revenu (-0,07) ni l'IPS du lycée (-0,07) est attendu ; seul le lien faible avec les prix (+0,19) n'est pas mécanique. Le texte de la carte pourrait dire « par construction, la valeur ajoutée tient compte du profil des élèves ».
7. **Seuils des tiers serrés** : l'écart entre le tiers bas et le tiers haut est de 4 à 5 points d'IPS (lycées : 99,6 à 104,0), alors que la DEPP déconseille d'interpréter des écarts de 3 points ou moins. Des départements proches du seuil peuvent changer de groupe d'une rentrée à l'autre.
8. **« Défavorisé aux trois étapes » mêle trois rentrées** (écoles 2024-2025, collèges et lycées 2025-2026) : sans effet pratique, mais à signaler si l'on écrit « un enfant qui y grandit ».
9. **Contradictions dans le dossier** : « le désavantage ne se rattrape pas, il s'empile » et « double peine » (pour toute VA nulle ou négative, même -0,1) contredisent le message de la carte et surinterprètent des écarts inférieurs à un point. « 0,58, corrélation entre l'école et le revenu » est écrit en dur et ne se retrouve pas : sur les données actuelles, l'IPS public et le revenu médian se corrèlent à 0,82 (écoles), 0,76 (collèges), 0,64 (lycées). La méthode écrit « La valeur ajoutée couvre les lycées GT + professionnels » : exact, mais la source citée par la carte ne pointe que vers le jeu GT.
10. **Chiffre plus parlant possible** : à l'échelle des lycées publics généraux et technologiques, « 38 % des lycées les plus modestes font mieux que prévu au bac, contre 25 % des plus favorisés » (session 2025, tiers d'IPS de la voie GT). Plus robuste (1 500 lycées) et plus concret que 22 départements, sans nommer d'établissement.
11. **Fragilité technique** : `build_ecole.py` n'a pas de cache et choisit le jeu par une recherche plein texte sur data.gouv.fr puis le plus gros CSV : un nouveau jeu au titre proche peut être pris à la place. L'adresse d'export de data.education.gouv.fr est stable et pourrait être écrite en dur.
12. **Fraîcheur** : IVAL et IPS sont au dernier millésime ; à revoir au printemps 2027 (session 2026 des IVAL, IPS des écoles 2025-2026).
