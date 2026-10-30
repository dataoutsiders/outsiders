# 9. La prépa, la formation la plus difficile d'accès ?
> Carte `selectivite` · Faux · dossier /terrains/selectivite · fiche préparée le 30/10/2026

## Ce qu'affiche la carte

- **Rubrique** : Enseignement supérieur ; unité : Formations ; couleur `#0891B2`.
- **Question** : « La prépa, la formation la plus difficile d'accès ? »
- **Verdict** : Faux.
- **Chiffre** : 4 %
- **Libellé du chiffre** : « de taux d'accès médian dans les formations au BPJEPS (sport), le plus bas de Parcoursup »
- **Texte** : « Le sport, les instituts d'études politiques (10 %) et les arts appliqués (23 %) donnent moins de propositions à leurs candidats que la prépa scientifique (41 %). Le taux d'accès dit combien de candidats reçoivent une proposition, pas le niveau demandé. Et la licence n'accueille plus tous ses candidats partout : seules 33 % en acceptent la totalité, 20 % en Île-de-France, faute de places plus que par sélection. »
- **Source citée** : « MESR, Parcoursup 2025 », lien https://data.enseignementsup-recherche.gouv.fr/explore/dataset/fr-esr-parcoursup/
- **Lien** : « Ouvrir le dossier Sélectivité » -> `/terrains/selectivite`.
- Tous ces chiffres sont **écrits en dur** dans `frontend/src/pages/Home.jsx` (tableau `QUESTIONS`) et repris dans la description SEO (`frontend/src/config/seo.js`) : relancer le script ne met pas la carte à jour.
- La carte n'est pas reprise sur la page Presse (exclue avec Élus et Assemblée, `docs/projet.md` section 5.6).

## Ce que dit le dossier

Page `frontend/src/pages/terrains/TerrainSelectivite.jsx`, titre « Qui peut entrer ? La sélectivité du supérieur », session 2025.

- En-tête : 14 237 formations exploitables, 13,5 millions de vœux ; « la hiérarchie réelle de la sélection ne ressemble pas à sa réputation ».
- Trois chiffres clés : 4 % d'accès au BPJEPS (« la voie la plus fermée de Parcoursup ») ; 33 % des licences acceptent tous leurs candidats ; 5,2 % contre 29,4 % d'admis boursiers (écoles de commerce contre BTS).
- « Le plus dur d'entrer, ce n'est pas la prépa » : classement des 11 familles (`fili`) selon trois mesures au choix.
  - Taux d'accès médian : PASS 34 %, autres formations 38 %, IFSI 40 %, CPGE 43 %, BUT 45 %, EFTS 45 %, LAS 53 %, BTS 57 %, écoles de commerce 63 %, écoles d'ingénieurs 68 %, licence 86 %.
  - Pression (vœux par place) : IFSI 46,9, PASS 41,8, écoles d'ingénieurs 36,4, CPGE 27,8 ... EFTS 6,2.
  - Taux d'acceptation médian (acceptations / candidatures) : PASS 2,0 %, IFSI 2,3 %, écoles d'ingénieurs 2,6 %, CPGE 3,8 % ... EFTS 18,0 %.
- Les 15 filières détaillées les plus fermées (`form_lib_voe_acc`, 15 formations au moins) : BPJEPS 4 %, Sciences politiques 10 %, Formations Bac + 5 13 %, DN MADE 23 %, BUT Service 32 %, DE sanitaire 34 %, CPES 34 %, DNA 35 %, DCG 38 %, prépa scientifique 41 %, Licence STAPS 42 %, CMI 42 %, prépa littéraire 42 %, FCIL 44 %, DE social 45 %.
- « Qui se ferme, qui s'ouvre ? (2018 -> 2025) » : séries par famille. Exemples : pression sur la licence de 5,9 (2018) à 10,7 (2025) ; taux d'accès médian de la CPGE de 73 % (2022) à 43 % (2025), de la licence de 95 % à 86 % ; part des licences totalement ouvertes 28 % (2022) puis 33 % (2025).
- « La licence est-elle encore ouverte à tous ? » : 33 % acceptent tous leurs candidats, 27 % en refusent plus de la moitié ; par région de 20 % (Île-de-France, accès médian 49 %) à 100 % (Guadeloupe).
- « À filière égale, où est-ce plus dur ? » : matrice 31 académies × 5 filières (BTS, Licence, BUT, CPGE, IFSI). Écarts : BTS 66 points (Mayotte 10 %, Limoges 76 %), licence 57 (Créteil 43 %, Rennes 100 %), BUT 57 (Paris 12 %, Amiens 69 %), CPGE 49 (Paris 26 %, Guadeloupe 75 %), IFSI 38 (Aix-Marseille 28 %, Orléans-Tours 66 %).
- « Où vont les boursiers ? » : part d'admis boursiers par famille (écoles de commerce 5,2 %, écoles d'ingénieurs 7,3 %, CPGE 10,4 % ... BTS 29,4 %) ; à l'intérieur d'une filière, tiers le plus sélectif contre tiers le plus ouvert (CPGE 9,2 % contre 12,4 % ; BTS 34,7 % contre 23,4 %).
- Encadré « À lire avec ce recul » : 8 notes de méthode (taux d'accès = longueur de la file d'attente, auto-censure invisible, « autres formations » de composition changeante, taux officiel seulement depuis 2022, BUT = DUT, PACES exclue, 2020 année covid).
- Les fiches région de `/territoires` reprennent la part de licences totalement ouvertes par région (`frontend/src/config/dossiersTerritoires.js`).

## D'où viennent les chiffres

Chaîne : jeu MESR `fr-esr-parcoursup` (session 2025) -> export CSV par l'API Opendatasoft -> `python/tools/_cache_parcoursup/parcoursup.csv` (téléchargé le 05/07/2026, 12,9 Mo) -> `python/tools/build_parcoursup.py` (après exploration par `validate_parcoursup.py`, qui n'écrit rien) -> `frontend/public/data/showcases/selectivite.json` (généré le 06/07/2026) -> `TerrainSelectivite.jsx`. Les sessions 2018 à 2024 (`parcoursup_2018.csv` à `parcoursup_2024.csv`) ne servent qu'au bloc « évolution ». Le cache est à vider à chaque nouvelle session (`docs/DEPLOIEMENT.md`).

Filtre commun : formations dont `taux_acces_ens` est renseigné et `voe_tot` > 0 (14 237 lignes sur 14 252).

| Chiffre de la carte | Calcul | Clé du JSON |
|---|---|---|
| 4 % (BPJEPS) | médiane de `taux_acces_ens` sur les 79 lignes où `form_lib_voe_acc` = « BPJEPS » ; première des filières détaillées d'au moins 15 formations triées par médiane | `stats.plus_dure`, `detaillees[0]` |
| 10 % (instituts d'études politiques) | idem, `form_lib_voe_acc` = « Sciences politiques », 46 lignes | `detaillees[1]` |
| 23 % (arts appliqués) | idem, « DN MADE », 321 lignes | `detaillees[3]` |
| 41 % (prépa scientifique) | idem, « Classe préparatoire scientifique », 490 lignes | `detaillees[9]` |
| 33 % des licences | part des lignes `fili` = « Licence » (3 051) dont `taux_acces_ens` >= 100 | `licence.pct_100` |
| 20 % en Île-de-France | idem, lignes où `region_etab_aff` = « Ile-de-France » (721) | `licence.regions[0]` |
| « faute de places plus que par sélection » | interprétation, aucune variable ne la mesure | aucune |

Autres calculs du dossier : vœux par place = somme `voe_tot` / somme `capa_fin` ; taux d'acceptation = médiane de `acc_tot` / `voe_tot` ; part de boursiers = moyenne de `pct_bours` pondérée par `acc_tot` ; matrice = médiane de `taux_acces_ens` par `acad_mies` × `fili` (cellule à 10 formations, académie à 30) ; évolution = mêmes calculs par session, `DUT` renommé `BUT`, `PACES` exclue, série gardée si 15 formations et 4 sessions au moins.

## Les jeux de données

### Parcoursup 2025, vœux de poursuite d'études et de réorientation dans l'enseignement supérieur et réponses des établissements (MESR, SIES)

- **Producteur** : ministère de l'Enseignement supérieur, de la Recherche et de l'Espace, SIES (département des études statistiques sur l'enseignement supérieur). Licence Ouverte 2.0.
- **Millésime utilisé** : session 2025 (campagne du 15 janvier au 10 septembre 2025), jeu mis à jour le 09/03/2026 « pour ajouter le taux d'accès et le rang de certaines formations préalablement non disponibles ». Le cache local (05/07/2026) intègre cette mise à jour.
- **Dernier millésime disponible** : 2025. Aucun jeu 2026 sur le portail au 30/10/2026 (vérifié dans le catalogue ; `docs/millesimes_20261030.md`) ; la session 2026 paraît en général en fin d'année ou en début d'année suivante.
- **Page officielle** : https://data.enseignementsup-recherche.gouv.fr/explore/dataset/fr-esr-parcoursup/
- **Téléchargement direct** : https://data.enseignementsup-recherche.gouv.fr/api/explore/v2.1/catalog/datasets/fr-esr-parcoursup/exports/csv (séparateur `;`)
- **Métadonnées et sens des colonnes** : https://data.enseignementsup-recherche.gouv.fr/api/explore/v2.1/catalog/datasets/fr-esr-parcoursup (champ `fields`, libellés repris ci-dessous) ; description longue sur la page officielle (onglet Informations).
- **Fichier local** : `python/tools/_cache_parcoursup/parcoursup.csv`
- **Géographie** : une ligne par formation (hors apprentissage) ; établissement localisé par commune, département, académie, région et coordonnées GPS.
- **Taille** : 14 252 lignes, 118 colonnes ; 1 015 200 candidats dont 652 800 néo-bacheliers.
- **Sessions antérieures** (même structure à quelques colonnes près, nommage incohérent tiret / soulignement) : `fr-esr-parcoursup_2024` (14 079 lignes), `_2023` (13 869), `_2022` (13 644), `_2021` (13 396), `_2020` (12 760), `fr-esr-parcoursup-2019` (11 577), `fr-esr-parcoursup-2018` (10 697) ; même adresse de page et d'export en remplaçant l'identifiant. Fichiers locaux `parcoursup_<année>.csv`.

**Logique de nommage.** Préfixe = objet compté : `voe` / `nb_voe` vœux (candidats), `nb_cla` candidats classés, `prop` propositions, `acc` admis (ayant accepté), `pct` pourcentage d'admis. Suffixe de phase : `_pp` phase principale, `_pc` phase complémentaire. Suffixe de public : `_bg` néo-bacheliers généraux, `_bt` technologiques, `_bp` professionnels, `_at` autres candidats (réorientation, reprise d'études), `_brs` dont boursiers, `_f` dont femmes, `_internat` (CPGE).

#### Identification et localisation (17 colonnes)

| colonne | sens | utilisée ? |
|---|---|---|
| `session` | année de la session | oui : affichage de la session |
| `contrat_etab` | statut de l'établissement (public, privé sous contrat, privé enseignement supérieur, privé hors contrat) | non |
| `cod_uai` | code UAI de l'établissement | non |
| `g_ea_lib_vx` | nom de l'établissement | non |
| `dep`, `dep_lib` | code et nom du département de l'établissement | non |
| `region_etab_aff` | région de l'établissement | oui : licences ouvertes par région |
| `acad_mies` | académie de l'établissement | oui : matrice académie × filière |
| `ville_etab` | commune de l'établissement (absente en 2018-2020) | non |
| `g_olocalisation_des_formations` | coordonnées GPS de la formation | non |
| `lien_form_psup` | lien vers la fiche de la formation sur Parcoursup | non |
| `cod_aff_form` | identifiant de la formation dans Parcoursup | non |
| `tri` | type d'établissement d'accueil (1_universités, 2_Lycées, 3_Autres formations) | non |
| `list_com` | liste d'appel commune à plusieurs formations ou propre à la formation | non |
| `detail_forma2` | concours communs et banques d'épreuves (par exemple « Réseau ScPo, concours commun ») | non |
| `etablissement_id_paysage`, `composante_id_paysage` | identifiants du référentiel Paysage | non |

#### Nomenclature de la formation (8 colonnes)

| colonne | sens | utilisée ? |
|---|---|---|
| `fili` | filière très agrégée (11 modalités : BTS, Licence, Autre formation, CPGE, BUT, Ecole d'Ingénieur, Licence_Las, IFSI, PASS, Ecole de Commerce, EFTS) | oui : classement, matrice, boursiers, évolution |
| `form_lib_voe_acc` | filière de formation agrégée (53 modalités : BPJEPS, DN MADE, Classe préparatoire scientifique...) | oui : 15 filières détaillées les plus fermées (source des chiffres 4, 10, 23, 41 %) |
| `fil_lib_voe_acc` | filière détaillée bis (438 modalités : MPSI, PCSI, mention du BPJEPS, grade licence ou master des IEP...) | non |
| `lib_for_voe_ins` | filière de formation (3 150 libellés) | non |
| `lib_comp_voe_ins` | filière détaillée (libellé complet avec l'établissement) | non |
| `detail_forma` | filière très détaillée (option, parcours) | non |
| `select_form` | sélectivité juridique : « formation sélective » / « formation non sélective » | **non** (voir « Ce qu'on n'exploite pas ») |
| `capa_fin` | capacité d'accueil de la formation | oui : vœux par place |

#### Vœux des candidats (17 colonnes)

| colonne | sens | utilisée ? |
|---|---|---|
| `voe_tot` | effectif total des candidats | oui : filtre, pression, taux d'acceptation |
| `voe_tot_f` | dont candidates | non |
| `nb_voe_pp` | candidats en phase principale | non |
| `nb_voe_pp_internat` | dont candidats ayant postulé en internat | non |
| `nb_voe_pp_bg`, `_bt`, `_bp`, `_at` | candidats en phase principale : néo-bacheliers généraux, technologiques, professionnels, autres | non |
| `nb_voe_pp_bg_brs`, `_bt_brs`, `_bp_brs` | dont boursiers, par série | non |
| `nb_voe_pc`, `nb_voe_pc_bg`, `_bt`, `_bp`, `_at` | candidats en phase complémentaire, total et par série | non |

#### Candidats classés (11 colonnes)

| colonne | sens | utilisée ? |
|---|---|---|
| `nb_cla_pp`, `nb_cla_pc` | candidats classés par l'établissement en phase principale, complémentaire | non |
| `nb_cla_pp_internat`, `nb_cla_pp_pasinternat` | classés en internat, hors internat (CPGE) | non |
| `nb_cla_pp_bg`, `_bt`, `_bp`, `_at` | classés par série | non |
| `nb_cla_pp_bg_brs`, `_bt_brs`, `_bp_brs` | dont boursiers | non |

#### Propositions d'admission (8 colonnes)

| colonne | sens | utilisée ? |
|---|---|---|
| `prop_tot` | candidats ayant reçu une proposition | non (converti en nombre mais jamais employé) |
| `prop_tot_bg`, `_bt`, `_bp`, `_at` | propositions par série de terminale | non |
| `prop_tot_bg_brs`, `_bt_brs`, `_bp_brs` | dont boursiers | non |

#### Admis, effectifs (28 colonnes)

| colonne | sens | utilisée ? |
|---|---|---|
| `acc_tot` | admis (ayant accepté la proposition) | oui : taux d'acceptation, pondération des boursiers |
| `acc_tot_f` | dont admises | non |
| `acc_pp`, `acc_pc` | admis en phase principale, complémentaire | non |
| `acc_debutpp`, `acc_datebac`, `acc_finpp` | admis ayant reçu leur proposition à l'ouverture, avant le bac, avant la fin de la phase principale | non |
| `acc_internat` | admis en internat | non |
| `acc_brs` | admis boursiers néo-bacheliers | non |
| `acc_neobac` | admis néo-bacheliers | non |
| `acc_bg`, `acc_bt`, `acc_bp`, `acc_at` | admis par série, autres | non |
| `acc_mention_nonrenseignee`, `acc_sansmention`, `acc_ab`, `acc_b`, `acc_tb`, `acc_tbf` | admis néo-bacheliers par mention au bac (TB hors félicitations, TB avec félicitations depuis 2021) | non |
| `acc_bg_mention`, `acc_bt_mention`, `acc_bp_mention` | admis avec mention, par série | non |
| `acc_term`, `acc_term_f` | admis issus du même lycée (BTS, CPGE), dont femmes | non |
| `acc_aca_orig`, `acc_aca_orig_idf` | admis issus de la même académie (Paris, Créteil, Versailles réunies pour la seconde) | non |

#### Admis, pourcentages (21 colonnes)

| colonne | sens | utilisée ? |
|---|---|---|
| `pct_bours` | % d'admis néo-bacheliers boursiers | oui : gradient social, croisement intra-filière |
| `pct_acc_debutpp`, `pct_acc_datebac`, `pct_acc_finpp` | % d'admis ayant reçu leur proposition à l'ouverture, avant le bac, avant la fin de la phase principale | non |
| `pct_f` | % de femmes parmi les admis | non |
| `pct_aca_orig`, `pct_aca_orig_idf` | % d'admis néo-bacheliers de la même académie | non |
| `pct_etab_orig` | % d'admis issus du même lycée (BTS, CPGE) | non |
| `pct_neobac` | % de néo-bacheliers parmi les admis | non |
| `pct_mention_nonrenseignee`, `pct_sansmention`, `pct_ab`, `pct_b`, `pct_tb`, `pct_tbf` | répartition des admis néo-bacheliers par mention | non |
| `pct_bg`, `pct_bt`, `pct_bp` et `pct_bg_mention`, `pct_bt_mention`, `pct_bp_mention` | % d'admis par série, dont avec mention | non |

#### Rangs et taux d'accès (11 colonnes)

| colonne | sens | utilisée ? |
|---|---|---|
| `lib_grp1`, `lib_grp2`, `lib_grp3` | groupes de classement définis par la formation (« Tous les candidats », « Autres candidats », quotas...) | non |
| `ran_grp1`, `ran_grp2`, `ran_grp3` | rang du dernier appelé de chaque groupe (peut dépasser le nombre de classés en liste commune) | non |
| `taux_acces_ens` | taux d'accès : candidats dont le rang est inférieur ou égal au rang du dernier appelé de leur groupe, rapportés aux candidats ayant validé un vœu en phase principale (hors GDD ; candidats scolarisés en France ou européens) ; « ne peut être recalculé » d'après le producteur | oui : mesure centrale de la carte et du dossier |
| `part_acces_gen`, `part_acces_tec`, `part_acces_pro` | répartition par type de bac des candidats qui étaient en position de recevoir une proposition | non |

#### Colonnes propres aux sessions anciennes (bloc évolution)

| colonne | sessions | sens | utilisée ? |
|---|---|---|---|
| `regr_forma` | 2018 à 2020 | regroupement de formations | non |
| `rang_der_max` | 2018, 2019 | rang du dernier appelé (maximum) | non |
| `lib_grp4`, `ran_grp4`, `lib_grp5`, `ran_grp5` | 2020 | quatrième et cinquième groupes de classement | non |
| `taux_adm_psup`, `taux_adm_psup_gen`, `_techno`, `_pro` | 2020, 2021 | « indicateur Parcoursup du taux d'accès » défini comme ratio entre le dernier appelé et le dernier classé, avec déclinaison par série | non (définition différente de `taux_acces_ens`) |

Colonnes absentes des premières sessions : `taux_acces_ens` et `part_acces_*` (avant 2022), `ville_etab` et `lib_for_voe_ins` (avant 2021), `select_form` et `lib_comp_voe_ins` (avant 2020), `prop_tot_*`, groupes et `cod_aff_form` (avant 2020).

## Ce qu'on n'exploite pas encore

Chiffres ci-dessous recalculés sur le cache local le 30/10/2026, à vérifier par l'usager avant tout emploi.

- **`select_form` (sélective ou non)** : c'est la colonne qui manque le plus. Les 3 051 « licences » du calcul comptent 647 licences juridiquement sélectives (doubles licences, cursus renforcés), dont 1,7 % seulement acceptent tous leurs candidats. Sur les 2 404 licences non sélectives, **42 % acceptent tous leurs candidats (30 % en Île-de-France)**, contre 33 % et 20 % affichés. Séparer les deux rendrait juste la phrase « faute de places plus que par sélection », qui ne vaut que pour les licences non sélectives.
- **Pondération par les candidats ou les places** : la médiane par formation donne le même poids à une formation de 4 places et à une de 200. Pondéré par les vœux, le taux d'accès est de 5,7 % au BPJEPS et de 30,8 % en prépa scientifique (au lieu de 41 %) : les grandes prépas sont plus fermées. Pour les licences non sélectives, celles qui acceptent tous leurs candidats ne reçoivent que 18 % des vœux mais offrent 34 % des places. Une mesure « chances d'un candidat » serait plus fidèle à la question.
- **`capa_fin` des petites filières** : la capacité médiane d'un BPJEPS sur Parcoursup est de **4 places** (moyenne 5,6) pour 153 candidats ; celle d'un IEP de 12. Le « plus bas de Parcoursup » est d'abord un effet de toutes petites jauges, à dire.
- **Mentions des admis (`acc_tb`, `acc_tbf`, `acc_neobac`, `pct_*` de mention)** : elles mesurent le niveau demandé, que la carte dit ne pas mesurer. Part d'admis néo-bacheliers avec mention TB ou TB avec félicitations : Sciences politiques 86 %, prépa scientifique 48 %, prépa littéraire 44 %, DN MADE 16 %, BPJEPS 2 % (59 % sans mention). Les deux classements (accès et niveau) côte à côte répondraient directement à « la plus difficile d'accès ».
- **Boursiers à chaque étape (`nb_voe_pp_*_brs`, `nb_cla_pp_*_brs`, `prop_tot_*_brs`, `acc_brs`)** : comparer la part de boursiers parmi les candidats, les classés, les propositions et les admis sépare l'auto-sélection de la sélection. Écoles de commerce : 3,5 % de boursiers parmi les candidats néo-bacheliers, 3,3 % parmi les propositions, 5,0 % parmi les admis ; CPGE : 9,2 %, 10,0 %, 10,3 %. Le faible taux de boursiers vient de qui candidate, pas du tri par l'établissement. Au passage, `acc_brs / acc_neobac` donne la part exacte (le dossier pondère `pct_bours` par `acc_tot`, qui inclut les non néo-bacheliers : écart de quelques dixièmes).
- **`part_acces_gen`, `_tec`, `_pro`** : composition par type de bac de ceux qui pouvaient recevoir une proposition, à rapprocher de `nb_voe_pp_bg/bt/bp` pour un taux d'accès par voie (bacheliers professionnels en BTS, technologiques en BUT).
- **`fil_lib_voe_acc` (niveau détaillé)** : à 15 formations au moins, les plus fermées sont une mention de BPJEPS (2 %), le BTS audiovisuel option image (4 %), les IEP grade master (5 %), BTS mode (8 %), orthophonie (10,5 %), architecture (11 %). Côté prépa : MP2I 25 %, MPSI 33 %, PCSI 41,5 %, TSI 59 %. Un exemple comme « MP2I 25 % » nuance utilement le « 41 % ».
- **`pct_aca_orig`, `acc_aca_orig_idf`** : recrutement local (prépa scientifique 64 % de la même académie, IEP 16 %, BTS 82 %) ; utile pour la matrice académique (l'accès « dépend de où l'on habite » se lit aussi par qui vient d'ailleurs).
- **`pct_acc_debutpp`, `acc_datebac`** : rythme des propositions (36 % des admis en prépa scientifique ont reçu leur proposition dès l'ouverture, 74 % en école de commerce) ; mesure de l'attente, complémentaire du taux d'accès.
- **`contrat_etab`** : public / privé ; écarts de taux d'accès et de boursiers entre BTS publics et privés, entre écoles de commerce consulaires et privées.
- **`pct_f`, `acc_tot_f`, `voe_tot_f`** : sélectivité selon le sexe (filles 31 % des admis en prépa scientifique, 86 % en IFSI) ; pont possible avec le thème « genre ».
- **`ran_grp*`, `lib_grp*`** : les groupes de quotas (bacheliers technologiques, boursiers) donnent des rangs distincts ; ils permettraient de voir les filières où un quota élargit l'accès.
- **Sessions 2020-2021 (`taux_adm_psup` et déclinaisons par série)** : indicateur d'accès publié avant 2022, mais défini autrement (dernier appelé / dernier classé) ; à citer comme tel plutôt que de dire qu'aucun taux n'existe avant 2022.

## Autres sources possibles

| Jeu | Producteur | Lien | Ce qu'il apporte |
|---|---|---|---|
| Parcoursup apprentissage, vœux et réponses des établissements (sessions 2022 à 2025, 39 032 lignes) | MESR, SIES | https://data.enseignementsup-recherche.gouv.fr/explore/dataset/fr-esr-parcoursup-apprentissage/ | Formations en apprentissage, exclues du jeu utilisé (beaucoup de BTS, BPJEPS, licences pro). Colonnes `nb_ref_classe` (vœux refusés après examen du dossier) et `nb_ref_place` (refusés faute de places) : la seule mesure directe de « sélection » contre « manque de places », et `nb_rech_con` (en recherche de contrat). |
| Parcoursup 2025 : propositions d'admission des bacheliers généraux selon leurs enseignements de spécialité (17 211 lignes, 27/05/2026) | MESR, SIES | https://data.enseignementsup-recherche.gouv.fr/explore/dataset/fr-esr-parcoursup-enseignements-de-specialite-bacheliers-generaux-3/ | Taux de proposition par doublette de spécialités et par formation (série 2021-2024 dans le jeu `...-2`) : « accès » vu du côté du lycéen, et non de la formation. |
| Cartographie des formations Parcoursup (157 497 lignes) | MESR | https://data.enseignementsup-recherche.gouv.fr/explore/dataset/fr-esr-cartographie_formations_parcoursup/ | Offre de formations par année, avec apprentissage (`app`), internat (`int`), aménagements ; utile pour l'offre par territoire. |
| MonMaster 2024 et 2025, vœux et réponses (16 257 lignes) ; MonMaster 2023 | MESR, SIES | https://data.enseignementsup-recherche.gouv.fr/explore/dataset/fr-esr-mon_master/ | La même question à l'entrée en master : candidats, classés, propositions par origine (licence générale, pro, BUT), académie, sexe. Prolonge le dossier au deuxième filtre. |
| Taux de poursuite des néo-bacheliers dans le supérieur par académie (mis à jour le 22/10/2026) | MESR, SIES | https://data.enseignementsup-recherche.gouv.fr/explore/dataset/fr-esr-taux-poursuite-enseignement-superieur-par-academie/ | Flux réels des bacheliers par voie et genre vers université, IUT, CPGE et STS publiques ou privées, dans ou hors de leur académie : complète la matrice académique par la mobilité effective. |
| Effectifs d'étudiants inscrits en CPGE (mis à jour le 06/03/2026) | MESR, SIES | https://data.enseignementsup-recherche.gouv.fr/explore/dataset/fr-esr-effectifs-d-etudiants-inscrits-en-classes-preparatoires-aux-grandes-ecole/ | Inscrits par établissement, filière, sexe, commune : ce que deviennent les admis (vérifier la capacité réelle des prépas). |
| InserSup, insertion professionnelle des diplômés (1 036 781 lignes, 29/07/2026) | MESR, SIES | https://data.enseignementsup-recherche.gouv.fr/explore/dataset/fr-esr-insersup/ | Débouchés par diplôme : relier difficulté d'accès et rendement du diplôme (une porte étroite mène-t-elle à un meilleur emploi ?). |
| Effectifs d'étudiants inscrits, atlas régional (12/10/2026) | MESR, SIES | https://data.enseignementsup-recherche.gouv.fr/explore/dataset/fr-esr-atlas_regional-effectifs-d-etudiants-inscrits_agregeables/ | Inscrits par formation et territoire, pour rapporter les places Parcoursup à la population étudiante locale. |
| APB, vœux et admissions (jusqu'en 2017) | MESR | https://data.enseignementsup-recherche.gouv.fr/explore/dataset/fr-esr-apb_voeux-et-admissions/ | Avant Parcoursup : remonter la série au-delà de 2018 (avec rupture de procédure). |
| Parcours et réussite des bacheliers en licence, en DUT, en PACES (anciens, 2017) | MESR, SIES | https://data.enseignementsup-recherche.gouv.fr/explore/dataset/fr-esr-parcours-et-reussite-des-bacheliers-en-licence/ | Réussite après l'entrée, mais millésimes anciens : à n'utiliser qu'en contexte. |

## Points de relecture

- **Le chiffre de licence est faussé par les licences sélectives.** « Seules 33 % (20 % en Île-de-France) en acceptent la totalité, faute de places plus que par sélection » mélange 2 404 licences non sélectives et 647 sélectives. Sur les seules non sélectives : 42 % et 30 %. La phrase « faute de places » n'est juste que pour ces dernières. Même correction à porter dans le dossier (chiffre clé, section licence, fiches région).
- **Rupture probable du taux d'accès entre 2024 et 2025.** Le taux médian de la prépa scientifique passe de 57 % (2024) à 41 % (2025), celui de la CPGE de 62,5 % à 43 %, alors que vœux, rangs du dernier appelé et propositions par vœu (34,1 % puis 33,5 %) ne bougent presque pas. En 2025 le taux publié coïncide avec `ran_grp1 / nb_voe_pp`, ce qui n'était pas le cas en 2024, et le jeu 2025 a été republié le 09/03/2026. Le producteur dit le calcul « identique », mais la baisse ressemble à un changement de mode de calcul plutôt qu'à une fermeture : vérifier avant de citer l'évolution « la CPGE se ferme » (73 -> 43 %) et avant de garder « 41 % » comme repère. Le verdict tient dans les deux cas (en 2024 : BPJEPS 7 %, IEP 10 %, DN MADE 22 %, prépa scientifique 57 %).
- **Le BPJEPS n'est pas une formation du supérieur.** C'est un brevet professionnel d'éducateur sportif de niveau bac (ministère des Sports), présent sur Parcoursup avec 79 formations de 4 places en médiane ; l'entrée passe aussi par des tests d'exigences préalables hors de la plateforme. « Sport » dans le texte peut être lu comme STAPS (42 %). Suggestion : « le brevet d'éducateur sportif (BPJEPS) » et une mention des petites jauges.
- **« Instituts d'études politiques (10 %) »** : 46 lignes pour 17 établissements, dont 18 lignes Sciences Po Paris (campus × grade licence ou master) et 8 du réseau ScPo. La médiane est tirée par Sciences Po Paris ; formulation possible : « Sciences Po et les IEP ».
- **Médiane par formation** : à dire ou à remplacer par un taux pondéré par les candidats (prépa scientifique 31 % pondéré, contre 41 % en médiane).
- **Chiffre plus parlant possible** : « 86 % des admis à Sciences Po ont eu mention très bien, 48 % en prépa scientifique, 2 % au BPJEPS » montre en un chiffre la différence entre porte étroite et niveau demandé, que la carte énonce sans la mesurer.
- **Formulation** : la question (« la plus difficile d'accès ») et la phrase « le taux d'accès dit combien de candidats reçoivent une proposition, pas le niveau demandé » sont issues de la correction du 30/10/2026 (`docs/verification_cartes_accueil.md`, section 8) ; la vérification a jugé les chiffres exacts, mais n'a pas regardé `select_form` ni la rupture 2024-2025.
- **« Le plus bas de Parcoursup »** : vrai parmi les filières agrégées d'au moins 15 formations ; les écoles vétérinaires (6 formations, 7,5 %) et le DEJEPS (2 formations, 9,5 %) sont sous l'IEP mais au-dessus du BPJEPS. À ce seuil près, exact.
- **Apprentissage absent** : le jeu utilisé exclut l'apprentissage (39 032 lignes dans un jeu à part sur 2022-2025) ; à mentionner dans la source ou à intégrer.
- **Fraîcheur** : session 2025 = dernière disponible au 30/10/2026 ; surveiller la session 2026 (fin 2026, début 2027) et vider `_cache_parcoursup/` avant de relancer. Les chiffres de la carte et du SEO sont en dur : à reprendre à la main.
- **Note du dossier à corriger** : « le taux d'accès officiel n'existe que depuis 2022 et ne peut pas être recalculé avant (il repose sur le rang du dernier appelé, non publié) ». Le rang du dernier appelé est publié depuis 2018 (`rang_der_max`, puis `ran_grp*`) et un indicateur de taux d'accès de Parcoursup existe en 2020-2021 (`taux_adm_psup`), défini autrement. La décision de ne pas raccorder les séries reste défendable, mais la justification écrite est inexacte.
