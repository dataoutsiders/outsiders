# 11. Public, privé : les mêmes élèves ?
> Carte `ecole` · Faux · dossier /terrains/ecole · fiche préparée le 30/10/2026

## Ce qu'affiche la carte

- **Rubrique** : École ; **unité** : Établissements ; couleur violette (`#8B5CF6`).
- **Question** : « Public, privé : les mêmes élèves ? »
- **Verdict** : Faux.
- **Chiffre** : `88 → 122`
- **Libellé du chiffre** : « indice de position sociale moyen des collèges publics et privés de Seine-Saint-Denis (rentrée 2025) »
- **Texte** : « Dans le département le plus défavorisé de métropole, les collèges privés accueillent un public plus favorisé que la moyenne des collèges publics de Paris (115). C'est l'écart entre public et privé le plus grand de métropole : 34 points. »
- **Source citée** : « Éducation nationale, IPS des collèges (rentrée 2025) », lien vers la page de la DEPP https://www.education.gouv.fr/depp/l-indice-de-position-sociale-ips-357755 (la page répond 403 aux robots : lien à vérifier à la main).
- **Bouton** : « Ouvrir le dossier École » vers `/terrains/ecole`.
- La carte est aussi reprise par la page Presse (`/presse`), qui relit `QUESTIONS`.

## Ce que dit le dossier

Page `frontend/src/pages/terrains/TerrainEcole.jsx`, titre « L'école trie-t-elle ? ». Le dossier ne porte pas d'abord sur public et privé : il suit l'IPS aux trois étapes (école, collège, lycée) et la valeur ajoutée des lycées. Ce qu'il affirme :

- **Chiffres clés** : 23 départements « défavorisés aux 3 étapes » (tiers le plus bas de l'IPS public à l'école, au collège et au lycée) ; 25 départements « en entre-soi aux 3 étapes » (tiers le plus haut) ; « 93 ↔ 92, la même région, deux mondes » (texte en dur).
- **Recherche d'établissement** : 40 738 écoles, collèges et lycées ; pour chacun, IPS, rang en percentile parmi les établissements du même niveau (« plus favorisé que N % des collèges »), et pour les lycées la valeur ajoutée et le taux de réussite au bac.
- **Carte des établissements** en points : IPS par niveau et par secteur (public, privé, tous), ou valeur ajoutée des lycées.
- **« L'école suit-elle la ségrégation résidentielle ? »** : nuage des départements, IPS des collèges publics contre revenu médian (Filosofi 2023) ou prix au m² (DVF) ; droite de pronostic et trois départements au-dessus, trois en dessous.
- **« Où l'école trie plus que le quartier ? »** : 12 villes où la ségrégation des collèges dépasse celle des quartiers (données du dossier Ségrégation, `segregation/villes.json`), avec IPS public et privé de la ville.
- **« Les collèges décrochés, et attractifs, de leur quartier »** : collèges publics dont le rang d'IPS s'écarte le plus du rang de revenu de leurs carreaux de 200 m dans un rayon de 700 m (`segregation/colleges-evitement.json`, fichier du 4 juillet, produit par `build_segregation.py`). Ces listes nomment des établissements.
- **Encadré « Défavorisé ne veut pas dire école qui échoue »** : 8 départements défavorisés aux 3 étapes sur 22 (valeur ajoutée connue) ont des lycées à valeur ajoutée positive, contre 8 sur 25 chez les favorisés.
- **« Ce qu'il faut retenir »** :
  - « 0,58, corrélation entre l'école et le revenu du territoire » (texte en dur, voir points de relecture) ;
  - « IPS du collège public vs privé en Seine-Saint-Denis : 88,1 → 122 », « l'écart le plus grand de métropole » ;
  - « 8 sur 22 » (8 sur 25 chez les favorisés).
- **Méthode et limites** : IPS = composition sociale, pas résultats ; la valeur ajoutée (IVAL) mesure la réussite au bac au-delà de l'attendu ; cumul calculé sur le public ; années : écoles 2024-2025, collèges 2025-2026, lycées 2025-2026.

## D'où viennent les chiffres

Chaîne : API data.gouv.fr (recherche par mots-clés) -> export CSV de data.education.gouv.fr (téléchargé à chaque exécution, **aucun cache local**) -> `python/tools/build_ecole.py` -> `frontend/public/data/showcases/ecole-ips.json`, `ecole-communes.json`, `etablissements.tsv` -> `TerrainEcole.jsx` ; la carte de l'accueil écrit ses chiffres en dur dans `Home.jsx`.

Détail du script :
- `csv_url(q)` interroge `https://www.data.gouv.fr/api/1/datasets/?q=<mots-clés>`, prend le premier jeu dont l'organisation contient « ducation », puis sa plus grosse ressource CSV. Le jeu retenu le 30/10/2026 est bien le bon pour chaque niveau (vérifié), mais le choix dépend du classement de la recherche.
- `load_level` garde la **dernière année** de chaque jeu, renomme les colonnes et classe le secteur : `public` ou, sinon, privé (le privé est donc le seul **privé sous contrat**).
- `wide_rows` calcule, par département, EPCI et commune, la **moyenne simple** des IPS des établissements (`ips_<niveau>_<public|prive|tous>`), sans pondération par le nombre d'élèves.
- Le cumul (`triple-bas`, `triple-haut`, `mixte`) découpe les départements en tiers (`pd.qcut`) sur l'IPS public de chaque niveau.
- `va_lycee` = moyenne simple de la valeur ajoutée du taux de réussite (toutes séries) des lycées du département, **public et privé confondus** ; pour un lycée polyvalent présent dans les deux jeux (GT et pro), les deux valeurs ajoutées sont moyennées.
- `pct` = rang en percentile de l'IPS parmi les établissements du même niveau, public et privé confondus.

Rattachement des chiffres de la carte (recalculé le 30/10/2026 depuis `ecole-ips.json` et `etablissements.tsv`) :

| Chiffre de la carte | Valeur dans les données | Calcul |
|---|---|---|
| 88 | 88,1 | moyenne simple des 131 collèges publics du 93, rentrée 2025-2026 (`ips_college_public`) |
| 122 | 122,0 | moyenne simple des 28 collèges privés sous contrat du 93 (`ips_college_prive`) |
| « département le plus défavorisé de métropole » | 93 : IPS des collèges publics 88,1, le plus bas de métropole (Pas-de-Calais 89,5) ; 1er aussi par le revenu médian selon `verification_cartes_accueil.md` | `ips_college_public`, `revenu` |
| 115 (Paris) | 115,4 | moyenne simple des collèges publics de Paris |
| 34 points, « le plus grand de métropole » | 33,9 ; suivent Hauts-de-Seine 33,2, Essonne 32,3, Yvelines et Val-de-Marne 31,6 ; Guyane (36,9) et La Réunion (34,8) sont au-dessus | `ips_college_prive - ips_college_public` |

Repères utiles, même source : médiane des IPS des collèges privés des départements 116,8 ; écart public-privé médian 17,3 points ; 7 départements de métropole au-dessus de 30 points (dont la Haute-Corse à 30,2). Dans le 93, 16 collèges privés sur 28 dépassent 115,4 ; 2 sont sous 100 ; 17 collèges publics sur 131 dépassent 100.

## Les jeux de données

### IPS des collèges (à partir de 2023) : le jeu de la carte
- **Producteur** : DEPP, ministère de l'Éducation nationale ; Licence Ouverte 2.0.
- **Intitulé** : « Indices de position sociale des collèges (à partir de 2023) », identifiant `fr-en-ips-colleges-ap2023`.
- **Millésime utilisé** : rentrée 2025-2026 (dernier disponible ; jeu modifié le 01/09/2026). Le jeu contient 2023-2024, 2024-2025 et 2025-2026.
- **Pages** : https://data.education.gouv.fr/explore/dataset/fr-en-ips-colleges-ap2023/ ; https://www.data.gouv.fr/datasets/ips-colleges-a-partir-de-2023
- **Téléchargement direct** : https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-ips-colleges-ap2023/exports/csv?use_labels=true
- **Fichier local** : aucun (téléchargé à chaque exécution du script).
- **Géographie** : établissement (UAI), France entière avec DROM ; collèges publics et privés sous contrat.
- **Lignes** : 21 061 (7 089 pour 2025-2026 : 5 405 publics, 1 684 privés).
- **Rupture de série** : séries antérieures dans `fr-en-ips_colleges` (2016-2017 à 2021-2022) et `fr-en-ips-colleges-ap2022` (2022-2023), méthode à vérifier avant tout raccord.

| colonne | sens | utilisée ? |
|---|---|---|
| rentree_scolaire (« Année scolaire ») | année scolaire des indices | oui : garde la dernière année |
| code_region | code de la région académique | non |
| region_insee | code région Insee | non |
| region_academique | libellé de la région académique | non |
| code_academie | code de l'académie | non |
| academie | libellé de l'académie | non |
| code_du_departement | code du département | oui : agrégat départemental |
| departement | libellé du département | oui : nom affiché |
| code_insee_de_la_commune | code commune Insee | oui : agrégats EPCI et commune |
| nom_de_la_commune | libellé de la commune | oui : recherche et infobulle |
| uai | identifiant de l'établissement | oui : clé de jointure (valeur ajoutée, coordonnées) |
| nom_de_l_etablissement | nom de l'établissement | oui : recherche, carte |
| secteur | public ou privé sous contrat | oui : séparation public / privé |
| ips | IPS moyen des élèves de l'établissement | oui : chiffre de la carte (moyenne simple par département) |
| ecart_type_de_l_ips | écart-type de l'IPS des élèves de l'établissement (mixité interne) | **non** |
| ips_national_prive | IPS national du privé sous contrat (125,5 en 2025-2026) | non |
| ips_national_public | IPS national du public (100,8) | non |
| ips_national | IPS national, public et privé | non |
| ips_academique_prive | IPS académique du privé | non |
| ips_academique_public | IPS académique du public | non |
| ips_academique | IPS académique, ensemble | non |
| ips_departemental_prive | IPS départemental officiel du privé (pondéré par les élèves) | **non** (le site recalcule une moyenne simple) |
| ips_departemental_public | IPS départemental officiel du public | **non** |
| ips_departemental | IPS départemental officiel, ensemble | non |

### IPS des écoles (à partir de 2022)
- **Producteur** : DEPP ; Licence Ouverte 2.0.
- **Intitulé** : « Indices de position sociale des écoles (à partir de 2022) », `fr-en-ips-ecoles-ap2022`.
- **Millésime utilisé** : rentrée 2024-2025, le dernier (pas de 2025-2026 au 30/10/2026 ; jeu modifié le 07/08/2026). Contient 2022-2023 à 2024-2025.
- **Pages** : https://data.education.gouv.fr/explore/dataset/fr-en-ips-ecoles-ap2022/ ; https://www.data.gouv.fr/datasets/indices-de-position-sociale-dans-les-ecoles-a-partir-de-2022
- **Téléchargement direct** : https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-ips-ecoles-ap2022/exports/csv?use_labels=true
- **Fichier local** : aucun. **Géographie** : école (UAI), France entière. **Lignes** : 97 080 (32 494 pour 2024-2025).
- Série antérieure : `fr-en-ips_ecoles_v2` (2016-2017 à 2021-2022).

| colonne | sens | utilisée ? |
|---|---|---|
| rentree_scolaire | année scolaire | oui : dernière année |
| code_region, region | région académique | non |
| code_de_l_academie, academie | académie | non |
| code_du_departement | code du département | oui : agrégat |
| departement | libellé | oui |
| code_insee_de_la_commune | code commune | oui : EPCI, commune |
| nom_de_la_commune | commune | oui : recherche |
| uai | identifiant | oui : clé |
| nom_de_l_etablissement | nom | oui : recherche |
| secteur | public ou privé sous contrat | oui |
| ips | IPS moyen de l'école | oui : dossier (pas la carte) |
| ips_national_prive, ips_national_public, ips_national | valeurs nationales | non |
| ips_academique_prive, ips_academique_public, ips_academique | valeurs académiques | non |
| ips_departemental_prive, ips_departemental_public, ips_departemental | valeurs départementales officielles | non |
| num_ligne | numéro technique | non |

Pas d'écart-type pour les écoles.

### IPS des lycées (à partir de 2023)
- **Producteur** : DEPP ; Licence Ouverte 2.0.
- **Intitulé** : « Indices de position sociale des lycées (à partir de 2023) », `fr-en-ips-lycees-ap2023`.
- **Millésime utilisé** : rentrée 2025-2026 (dernier). Contient 2023-2024 à 2025-2026.
- **Pages** : https://data.education.gouv.fr/explore/dataset/fr-en-ips-lycees-ap2023/ ; https://www.data.gouv.fr/datasets/ips-lycees-a-partir-de-2023
- **Téléchargement direct** : https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-ips-lycees-ap2023/exports/csv?use_labels=true
- **Fichier local** : aucun. **Géographie** : lycée (UAI). **Lignes** : 10 905 (3 662 pour 2025-2026). Série antérieure : `fr-en-ips_lycees` (2016-2021).

| colonne | sens | utilisée ? |
|---|---|---|
| rentree_scolaire | année scolaire | oui |
| code_region, code_region_insee, region_academique | région | non |
| code_academie, academie | académie | non |
| code_du_departement, departement | département | oui |
| code_insee_de_la_commune, nom_de_la_commune | commune | oui |
| uai, nom_de_l_etablissement | établissement | oui |
| secteur | public ou privé sous contrat | oui |
| type_de_lycee | LEGT, LP ou LPO | **non** |
| ips_voie_gt | IPS des élèves de la voie générale et technologique | **non** |
| ips_voie_pro | IPS des élèves de la voie professionnelle | **non** |
| ips_post_bac | IPS des élèves post-bac (BTS, prépa) | **non** |
| ips_etab | IPS de l'ensemble des élèves | oui : dossier |
| ecart_type_voie_gt, ecart_type_voie_pro, ecart_type_etablissement | écarts-types (mixité interne) | non |
| ips_national_{legt, lpo, lp} et leurs variantes `_prive` / `_public` (9 colonnes) | valeurs nationales par type de lycée et secteur | non |
| ips_academique_{legt, lpo, lp} et variantes (9 colonnes) | valeurs académiques | non |
| ips_departemental_{legt, lpo, lp} et variantes (9 colonnes) | valeurs départementales officielles | non |

### Valeur ajoutée des lycées généraux et technologiques (IVAL GT)
- **Producteur** : DEPP ; Licence Ouverte 2.0.
- **Intitulé** : « Indicateurs de valeur ajoutée des lycées d'enseignement général et technologique », `fr-en-indicateurs-de-resultat-des-lycees-gt_v2`.
- **Millésime utilisé** : session 2025 (dernière ; jeu du 10/06/2026). Lignes : 32 485 (toutes sessions).
- **Pages** : https://data.education.gouv.fr/explore/dataset/fr-en-indicateurs-de-resultat-des-lycees-gt_v2/ ; https://www.data.gouv.fr/datasets/indicateurs-de-valeur-ajoutee-des-lycees-denseignement-general-et-technologique-2
- **Téléchargement direct** : https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-indicateurs-de-resultat-des-lycees-gt_v2/exports/csv?use_labels=true
- **Fichier local** : aucun. **Géographie** : lycée (UAI), public et privé sous contrat.

Environ 90 colonnes, nommées `<mesure>_<série>`. Mesures : `presents` (élèves présents), `taux_reu` (taux de réussite observé), `va_reu` (valeur ajoutée du taux de réussite), `taux_men` / `va_men` (taux de mentions et sa valeur ajoutée). Séries : `total`, `l`, `es`, `s` (anciennes séries), `gnle` (voie générale), `sti2d`, `std2a`, `stmg`, `stl`, `st2s`, `s2tmd`, `sthr`.

| colonne ou famille | sens | utilisée ? |
|---|---|---|
| annee | session du bac | oui : dernière session |
| uai | identifiant | oui : clé |
| libelle_uai, secteur, code_commune, libelle_commune, code_departement, libelle_departement, libelle_academie, code_region, libelle_region | identification et géographie | non (prises dans les IPS) |
| presents_total | élèves présents, toutes séries | non |
| taux_reu_total | taux de réussite, toutes séries | oui : « Réussite bac N % » dans la recherche |
| va_reu_total | valeur ajoutée du taux de réussite | oui : `va` et `va_lycee` |
| taux_acces_2nde, taux_acces_1ere, taux_acces_term | taux d'accès au bac depuis la seconde, la première, la terminale | **non** |
| va_acces_2nde, va_acces_1ere, va_acces_term | leurs valeurs ajoutées | **non** |
| taux_men_total, va_men_total | taux de mentions et valeur ajoutée | **non** |
| presents_*, taux_reu_*, va_reu_*, taux_men_*, va_men_* par série (11 séries) | mêmes mesures par série | non |
| eff_2nde, eff_1ere, eff_term | effectifs par niveau | non |
| nb_mentions_tb_avecf_g, nb_mentions_tb_sansf_g, nb_mentions_b_g, nb_mentions_ab_g et équivalents `_t` | nombres de mentions, voies générale et technologique | non |

### Valeur ajoutée des lycées professionnels (IVAL pro)
- **Producteur** : DEPP. **Intitulé** : « Indicateurs de valeur ajoutée des lycées d'enseignement professionnel », `fr-en-indicateurs-de-resultat-des-lycees-pro_v2`.
- **Millésime utilisé** : session 2025. Lignes : 28 258.
- **Pages** : https://data.education.gouv.fr/explore/dataset/fr-en-indicateurs-de-resultat-des-lycees-pro_v2/ ; https://www.data.gouv.fr/datasets/indicateurs-de-valeur-ajoutee-des-lycees-denseignement-professionnel
- **Téléchargement direct** : https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-indicateurs-de-resultat-des-lycees-pro_v2/exports/csv?use_labels=true

Même structure que le GT (`presents`, `taux_reu`, `va_reu`, `taux_men`, `va_men`, `taux_acces`, `va_acces`, `eff_*`, `nb_mentions_*_p`), avec des spécialités à la place des séries : `pluri_techno`, `transfo`, `genie_civil`, `mat_souples`, `meca_elec`, `production`, `pluri_services`, `echanges`, `communication`, `serv_personnes`, `serv_collec`, `services`. Seuls `annee`, `uai`, `taux_reu_total` et `va_reu_total` sont utilisés.

### Annuaire de l'éducation
- **Producteur** : ministère de l'Éducation nationale. **Intitulé** : « Annuaire de l'éducation », `fr-en-annuaire-education`, mis à jour en continu (29/10/2026). 68 567 lignes.
- **Page** : https://data.education.gouv.fr/explore/dataset/fr-en-annuaire-education/
- **Téléchargement utilisé** : https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-annuaire-education/exports/csv?select=identifiant_de_l_etablissement,latitude,longitude
- **Fichier local** : aucun. Taux de géolocalisation obtenu : 99,3 %.

| colonne ou famille | sens | utilisée ? |
|---|---|---|
| identifiant_de_l_etablissement | UAI | oui : jointure |
| latitude, longitude | coordonnées WGS84 | oui : carte en points |
| nom_etablissement, type_etablissement, statut_public_prive | identification, type, statut | non |
| type_contrat_prive, code_type_contrat_prive | type de contrat du privé (sous contrat d'association, simple, hors contrat) | **non** |
| appartenance_education_prioritaire | REP ou REP+ | **non** |
| code_nature, libelle_nature | type d'établissement détaillé | non |
| ecole_maternelle, ecole_elementaire, voie_generale, voie_technologique, voie_professionnelle, post_bac | offre de formation | non |
| restauration, hebergement, ulis, segpa, apprentissage | services et dispositifs | non |
| section_arts, section_cinema, section_theatre, section_sport, section_internationale, section_europeenne | sections | **non** |
| lycee_agricole, lycee_militaire, lycee_des_metiers, greta | labels et réseaux | non |
| adresse_1 à 3, code_postal, code_commune, nom_commune, telephone, fax, web, mail, fiche_onisep, siren_siret | coordonnées | non |
| code_departement, code_academie, code_region et libellés | géographie administrative | non |
| position, coordx_origine, coordy_origine, epsg_origine, precision_localisation | localisation et sa précision | non |
| nom_circonscription, code_circonscription, code_zone_animation_pedagogique, libelle_zone_animation_pedagogique, code_bassin_formation, libelle_bassin_formation | découpages internes de l'Éducation nationale | non |
| rpi_concentre, rpi_disperse, pial, etablissement_mere, type_rattachement_etablissement_mere, multi_uai | réseaux et rattachements | non |
| date_ouverture, date_maj_ligne, etat, ministere_tutelle | gestion | non |

### Revenu médian : Insee, Filosofi 2023 (croisement du dossier, pas la carte)
- **Intitulé** : « Indicateurs sur les revenus et la pauvreté au niveau local en 2023 » ; page https://www.insee.fr/fr/statistiques/8984752 ; téléchargement https://www.insee.fr/fr/statistiques/fichier/8984752/FILOSOFI_CC_csv.zip
- **Fichier local** : `python/tools/_cache_filosofi/DS_FILOSOFI_CC_2023_data.csv` (format long, 1,1 million de lignes), lu par `revenu_filosofi.py`.
- **Colonnes** : `GEO` (code), `GEO_OBJECT` (COM, ARM, DEP, EPCI, REG, FRANCE, AAV2020, UU2020, ZE2020, BV2022...), `FILOSOFI_MEASURE`, `UNIT_MULT`, `UNIT_MEASURE`, `CONF_STATUS`, `OBS_STATUS`, `TIME_PERIOD`, `OBS_VALUE`. Mesures : `MED_SL` (niveau de vie médian, **seule utilisée**), déciles `D1_SL` à `D9_SL`, quartiles, `IR_D9_D1_SL`, `S80S20_SL`, `GI_SL` (Gini), `PR_MD60` (taux de pauvreté), parts des revenus (`S_EI_DI` activité, `S_RET_PEN_DI` pensions, `S_SOC_BEN_DI` prestations, `S_DIR_TAX_DI` impôts, etc.).
- Le taux de pauvreté (`PR_MD60`) serait un meilleur pendant de l'IPS que le revenu médian pour le nuage du dossier.

### Prix au m² : Statistiques DVF (croisement du dossier)
- **Producteur** : Etalab (DGFiP). Page https://www.data.gouv.fr/datasets/statistiques-dvf ; téléchargement https://data-pipeline-open.s3.sbg.io.cloud.ovh.net/dvf/stats_whole_period.csv (fichier du 21/10/2026, ventes de juillet 2021 à juin 2026).
- **Fichier local** : aucun pour ce script (une copie existe dans `python/tools/_cache_territoires/stats_whole_period.csv`).
- **Colonnes** : `code_geo`, `libelle_geo`, `code_parent`, `echelle_geo` (utilisées pour le filtre), `nb_ventes_whole_*`, `moy_prix_m2_whole_*`, `med_prix_m2_whole_*` pour appartement, maison, apt_maison, local. Seule `med_prix_m2_whole_apt_maison` est utilisée.

### Autres entrées techniques
- Centroïdes des communes : https://geo.api.gouv.fr/communes?fields=code,centre&format=json (points de `ecole-communes.json`).
- Rattachement commune -> EPCI : `python/data/municipales/communes-epci.json` (geo.api.gouv.fr).

## Ce qu'on n'exploite pas encore

1. **Valeurs départementales officielles** (`ips_departemental_public`, `ips_departemental_prive`) : elles sont pondérées par les élèves, là où le site fait une moyenne simple des collèges. Pour le 93 en 2025-2026 : 88,1 public et **123,1** privé (écart 35,0) ; Paris public **116,9**. Avec ces valeurs, le 93 n'a plus l'écart le plus grand de métropole : Hauts-de-Seine 37,0 (117,1 contre 154,1) et Val-de-Marne 36,0 sont devant, puis le 93 (35,0), le Bas-Rhin (34,2) et le Val-d'Oise (34,1). Citer la valeur du producteur éviterait de recalculer et changerait la formulation.
2. **Évolution** sur les trois rentrées du jeu : dans le 93, le privé passe de 121,1 à 122,1 puis 123,1 (valeurs officielles) quand le public reste à 88,3, 88,1, 88,1 ; l'écart s'est creusé de 2 points en deux ans. Même tendance dans le 92 (152,8 à 154,1) et le 94 (138,2 à 141,5). Les séries 2016-2021 et 2022 permettent un recul plus long, sous réserve de raccord méthodologique.
3. **Écart-type de l'IPS** (`ecart_type_de_l_ips`) : il dit si un collège mêle les milieux. Moyenne nationale 31,1 dans le public, 29,2 dans le privé ; dans le 93, 28,6 dans le public et 31,2 dans le privé (moyennes simples). Nuance utile : les collèges privés du 93 ne sont pas homogènes.
4. **La dispersion à l'intérieur du département** : dans le 93, les collèges privés vont de 98,5 à 146,8 et les publics de 71,7 à 132,8 ; 16 privés sur 28 dépassent la moyenne des publics parisiens, 2 sont sous 100. Montrer le chevauchement évite de faire croire à deux blocs.
5. **Lycées par voie et par type** (`ips_voie_gt`, `ips_voie_pro`, `ips_post_bac`, `type_de_lycee`) : comparer public et privé à voie égale (le privé compte plus de voie générale) enlèverait un effet de structure.
6. **Valeur ajoutée par secteur** : dans `etablissements.tsv`, la valeur ajoutée moyenne des lycées privés est de +1,1 point, celle des publics de -1,0 (moyennes simples, 3 337 lycées). C'est la question suivante naturelle (« de meilleurs élèves, et de meilleurs résultats à profil égal ? »), avec la limite que l'IVAL ne voit que ce que l'IPS et les notes antérieures mesurent. Le `va_lycee` départemental mélange aujourd'hui public et privé alors que le cumul est calculé sur le public.
7. **Accès au bac et mentions** (`taux_acces_2nde`, `va_acces_2nde`, `va_men_total`) : le taux d'accès de la seconde au bac capte le tri en cours de scolarité (élèves réorientés ou partis), point sensible dans la comparaison public-privé.
8. **Éducation prioritaire et type de contrat** (annuaire : `appartenance_education_prioritaire`, `type_contrat_prive`) : comparer le privé au public hors REP, et préciser que le hors contrat n'a pas d'IPS.
9. **Pondération par les effectifs** : le jeu « Effectifs d'élèves en collège » donne `nombre_eleves_total` par UAI ; il permettrait d'écrire « X % des collégiens du 93 sont dans le privé ».

## Autres sources possibles

- **DEPP, « Indicateurs de ségrégation sociale entre collèges dans les départements »** (`fr-en-indicateur_segregation_sociale_colleges`, 2014 à 2025, 132 lignes par an : départements, académies, France) : https://data.education.gouv.fr/explore/dataset/fr-en-indicateur_segregation_sociale_colleges/ . Colonnes : nombre de collèges retenus (`nb_coll_calcul`, `_pu_`, `_pr_`), `poids_prive_calcul` (part des élèves dans le privé), proportions d'élèves de PCS très favorisée, favorisée, moyenne, défavorisée, au total, dans le public (`p_*_pu`) et dans le privé (`p_*_pr`), indices d'entropie (total, public, privé, entre public et privé) et **contribution de l'écart public-privé** à la ségrégation (`contrib_interpupr`). C'est la source la plus directe pour la question de la carte, et en langage clair. Pour le 93 en 2025 : **49,3 % d'élèves de milieu défavorisé dans les collèges publics contre 14,6 % dans le privé** ; 11,5 % de très favorisés dans le public contre 42,4 % dans le privé (33,5 % en 2014) ; 13,7 % des collégiens dans le privé ; l'écart public-privé explique 44,8 % de la ségrégation entre collèges du département. Sur l'écart de part de défavorisés, le 93 est 1er de métropole (34,7 points, devant Pas-de-Calais 33,9 et Bas-Rhin 33,2) ; sur l'écart de très favorisés, ce sont les Hauts-de-Seine (44,9 points). Vérifier si « 2025 » désigne la rentrée 2025.
- **DEPP, « Effectifs d'élèves en collège »** (`fr-en-college-effectifs-niveau-sexe-lv`, 58 556 lignes) : effectifs par UAI, secteur, REP / REP+, niveau, sexe, langues. Pondération et part du privé.
- **DEPP, « Indicateurs de valeur ajoutée des collèges »** (`fr-en-indicateurs-valeur-ajoutee-colleges`, sessions 2022 à 2025) : taux de réussite et note à l'écrit du brevet, leur valeur ajoutée, taux d'accès de la 6e à la 3e, part de 3e Segpa, mentions ; secteur PU / PR. Permet la même comparaison qu'au lycée, au collège, l'étage de la carte.
- **« Diplôme national du brevet par établissement »** (`fr-en-dnb-par-etablissement`) : s'arrête à la session 2021 ; remplacé en pratique par le jeu précédent.
- **« Boursiers par département »** (`fr-en-boursiers-par-departement`) : nombre de boursiers et de boursiers au dernier échelon par formation et secteur ; une mesure de pauvreté plus parlante que l'IPS.
- **« Indice d'éloignement des collèges depuis 2022 »** (`fr-en-indice_eloignement_college_ap2022`) : isolement géographique ; utile pour ne pas comparer un privé urbain à un public rural.
- **« Carte scolaire des collèges publics »** (`fr-en-carte-scolaire-colleges-publics`, 499 680 tronçons de rues) : secteur de chaque collège public ; base plus juste que le rayon de 700 m du bloc « collèges décrochés ».
- **IPS des EREA** (`fr-en-ips-erea-ap2022`) : 77 établissements, marginal.
- **Cour des comptes, « L'enseignement privé sous contrat »** (rapport public thématique, 2023) : https://www.ccomptes.fr/fr/publications/lenseignement-prive-sous-contrat ; repères publiés sur l'écart d'IPS entre public et privé, utile pour situer le chiffre du site.

## Points de relecture

- **« L'écart le plus grand de métropole : 34 points »** : vrai seulement avec la moyenne simple des collèges, et de justesse (33,9 contre 33,2 pour les Hauts-de-Seine). Avec les valeurs départementales officielles de la DEPP, le 93 est 3e de métropole (35,0, derrière le 92 à 37,0 et le 94 à 36,0). Deux sorties : citer « l'un des plus grands écarts », ou passer à la part d'élèves défavorisés (49 % contre 15 %), où le 93 est bien 1er de métropole.
- **Chiffre plus parlant** : « 49 % d'enfants de milieux défavorisés dans les collèges publics de Seine-Saint-Denis, 15 % dans le privé » se lit sans connaître l'IPS. L'IPS reste abstrait (qu'est-ce que 122 ?) ; s'il est gardé, rappeler le repère national (public 100,8, privé 125,5 en 2025-2026).
- **Moyenne simple contre valeur officielle** : 122,0 (site) contre 123,1 (DEPP) pour le privé du 93 ; 115,4 contre 116,9 pour le public de Paris. Les chiffres de la carte ne sont donc pas ceux que le lecteur trouvera chez le producteur.
- **« Privé » = privé sous contrat** : le hors contrat n'a pas d'IPS. À dire dans le libellé ou le texte.
- **Formulation de la question** : « les mêmes élèves ? » appelle « non » partout ; la carte montre le cas extrême. Préciser que l'écart existe dans tous les départements (médiane 17 points) et que le 93 en est l'illustration la plus forte aiderait à ne pas lire un cas isolé.
- **Lien de la source** : la page de la DEPP renvoie 403 aux robots ; vérifier qu'elle est toujours en ligne, et envisager de pointer plutôt vers le jeu `fr-en-ips-colleges-ap2023`.
- **Dossier, chiffre « 0,58 »** : écrit en dur, provenance introuvable. Recalcul du 30/10/2026 : entre départements, corrélation revenu médian et IPS de 0,82 (écoles publiques), 0,76 (collèges publics), 0,77 (moyenne des trois) ; entre communes, 0,74 (écoles), 0,78 (collèges), 0,585 (lycées publics). Par ailleurs, l'interprétation « à 0,58, l'école ajoute sa propre ségrégation » n'est pas démontrée par une corrélation.
- **Dossier, textes en dur** : « 93 ↔ 92 » et « département le plus pauvre de métropole » (le dossier dit « pauvre », la carte « défavorisé »).
- **Dossier, `va_lycee`** : mélange public et privé, et moyenne GT et pro pour les lycées polyvalents, alors que le cumul est calculé sur le public.
- **Dossier, vocabulaire** : « relégation » reste ailleurs dans le dossier et dans `CroisementScatter.jsx` (relevé dans `verification_cartes_accueil.md`) ; les listes « collèges décrochés » nomment des établissements à partir d'un indicateur exploratoire.
- **Reproductibilité** : aucun cache local ; le script choisit le jeu par une recherche data.gouv.fr. Une nouvelle publication (par exemple un jeu départemental mieux classé) peut changer la source sans alerte.
- **Fraîcheur** : collèges et lycées 2025-2026, à jour ; écoles 2024-2025, dernière disponible. Le prochain millésime des collèges (2026-2027) devrait paraître vers septembre 2027, d'après le rythme du jeu (modifié le 01/09/2026).
