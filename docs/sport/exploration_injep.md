# Licences sportives de l'INJEP : note d'exploration pour un dossier « Sport »

> Exploration du 29 octobre 2026. Rien n'est publié sur le site : cette note sert à décider ce qui mérite une page.
> Script : `python/tools/explore_sport_injep.py` (étapes A à F, relançable).
> Tables intermédiaires : `python/data/sport/sorties/*.csv` (les noms de fichiers cités plus bas sont dans ce dossier).
> Données brutes : `python/data/sport/` et `python/data/sport/ref/` (environ 2 Go, à ne pas versionner : le `.gitignore` actuel ne couvre que `python/data/*.csv`, pas les sous-dossiers).

---

## (a) Le jeu de données, tel qu'il est vraiment

### Source et ressources

- **Jeu** : « Données géocodées issues du recensement des licences et clubs auprès des fédérations sportives agréées par le ministère chargé des sports », INJEP-MEDES, géocodage par l'Insee.
  Page : https://www.data.gouv.fr/datasets/donnees-geocodees-issues-du-recensement-des-licences-et-clubs-aupres-des-federations-sportives-agreees-par-le-ministere-charge-des-sports
  Métadonnées gardées dans `python/data/sport/dataset_metadata.json` (API data.gouv, dernière mise à jour le 29/12/2025).
- **Fichiers « licences »** (un par millésime) : `lic-data-2016` à `lic-data-2023`, `Licences_2013` à `Licences_2015`, plus 2011 et 2012 (anciens liens, non téléchargés). Environ 200 à 270 Mo chacun.
- **Fichiers « clubs »** : `clubs-data-2016` à `clubs-data-2023` (non exploités ici ; ils donnent l'offre de clubs par commune).
- **Dictionnaires** : `licences-dictionnaire-des-variables.xlsx`, `clubs-dictionnaire-des-variables.xlsx`, `liste-federations.xlsx` (un onglet par millésime, avec les fédérations « non réparties », « non disponibles » ou à « adresse du club »).
- **Dernier millésime géocodé : 2023**, qui correspond à la saison 2022-2023 ou à l'année civile 2023 selon les fédérations. Les résultats nationaux 2024 (non géocodés) sont annoncés sur le site de l'INJEP, qui répondait en erreur 503 le jour de l'exploration.

### Variables et maille (millésimes 2019 à 2023)

| Élément | Constat (vérifié dans les fichiers) |
|---|---|
| Maille | **commune x QPV** : `CSZ` (commune sans QPV), `HZ` (partie hors QPV d'une commune à QPV), code QPV, `NR` (non réparti). Arrondissements pour Paris, Lyon, Marseille. |
| Géographie des QPV | codes `QP` (géographie 2015, 1 400 QPV présents) de 2019 à 2022 ; codes `QN` (géographie 2024, 1 476 QPV présents) en 2023. Rupture en 2023. |
| Sexe | **Oui** : 2 sexes x 17 tranches d'âge quinquennales (1-4 ans, ..., 75-79, 80-99) + âge non renseigné. Pas de colonne « sexe inconnu » : en 2019, 418 757 licences UGSEL et 27 857 FSGT ont un total sans détail par sexe (`a_description_millesimes.csv`, colonne d'écart) ; l'écart est nul en 2022 et 2023. |
| Âge | âge du licencié, tranches du recensement des licences (et non plus du recensement de la population, depuis 2019). Âge non renseigné : 0,01 % des licences en 2023. |
| Lieu | **domicile du licencié** (« recensement au lieu d'habitation de la personne et non au lieu de pratique », description INJEP), sauf **UNSS (604) et USEP (605) : adresse du club** (donc de l'école), et la Fédération des arts énergétiques et martiaux chinois (254) en 2019-2021. |
| Champ | France hors Mayotte. Les licences hors champ du géocodage (Mayotte, Monaco, COM, étranger) sont à part : 1,2 % en 2023. |
| Non réparti | 2,2 % des licences en 2023 (3,7 % en 2019). Trois fédérations ne sont réparties qu'au département : Défense (406), Maccabi (409), Police nationale (411). |
| Secret statistique | **Aucun visible** : 76 % des cellules non nulles valent 1 ou 2 licences. En revanche l'INJEP précise que la répartition communale est une **estimation** (traitement des adresses non géolocalisables). |
| Population | **absente** des fichiers depuis 2019 (il faut l'apporter). Le fichier 2018 contient encore la population RP 2017 par commune, sexe et âge. |
| Unité de compte | **la licence annuelle**, pas la personne : une même personne peut en avoir plusieurs (multi-licences, double appartenance fédération unisport et multisports, licence scolaire en plus). |

Volumes 2023 (`a_description_millesimes.csv`, `a_familles_2023.csv`) : 16 535 056 licences, 117 fédérations, 38,6 % de licences féminines. Dont 9,65 millions en fédérations olympiques unisport, 1,92 million en non olympiques, 1,74 million en multisports (dont handisport et sport adapté), et **3,22 millions en fédérations scolaires et universitaires** (dont 1,93 million UNSS et USEP à adresse de l'école).

### Millésimes antérieurs (2013 à 2018)

Maille commune seulement (pas de QPV, sauf un total « licences en QP » en 2018), tranches d'âge larges (0-4, 5-9, 10-14, 15-19, 20-29, 30-44, ...), sexe présent. **Rupture de champ en 2019** : avant, les licences non réparties ne figurent pas dans les fichiers, donc les totaux sont plus bas que le recensement (et pas de la même façon selon les fédérations : natation 296 709 en 2018, 363 809 en 2019, volley 102 498 puis 144 098). Pièges de lecture rencontrés : fichier 2018 en latin-1 avec des séparateurs de milliers (espaces) dans les populations des grandes communes ; codes fédération réattribués (code 135 : 80 licences en 2013, puis FF de la montagne et de l'escalade depuis 2018) ; certaines fédérations absentes certaines années (karaté 2018 à 2021) ; certaines reconduisent les chiffres de l'année précédente (canoë-kayak 2023 = 2022 = 38 415).

### Limites à afficher en toutes lettres

1. **Une licence n'est pas une pratique.** Le sport hors club (course à pied seul, salle privée, five, street workout) n'est pas compté. Les écarts entre territoires mesurent l'adhésion à un club fédéré, qui dépend de l'offre, du prix et des habitudes.
2. **Multi-licences** : un taux « pour 1 000 habitants » n'est pas une part de pratiquants.
3. **Domicile, pas club** : bon pour les comparaisons sociales (QPV, revenu), sauf UNSS et USEP, qu'il faut exclure de ces comparaisons (fait dans toute la note).
4. **Estimation** communale, non-répartis et hors champ : quelques pourcents du total.
5. **Ruptures** : 2019 (champ et maille), 2021 (saison Covid : -19 % de licences hors scolaires entre 2019 et 2021), 2023 (nouvelle géographie des QPV), codes de fédérations.

---

## (b) Résultats chiffrés

Champ commun, sauf mention : licences 2023, **hors fédérations scolaires et universitaires** (codes 6xx), licences géocodées.

### R1. Géographie : le football est n°1 presque partout, mais chaque territoire a sa signature

- **Chiffre** : le football est la première fédération en nombre de licences dans **95 départements sur 100**. Exceptions : ski dans les Hautes-Alpes et en Savoie, tennis à Paris et dans les Hauts-de-Seine, rugby dans le Gers. Le rugby y compte 30 licences pour 1 000 habitants, 5,5 fois la moyenne nationale (5,5).
- **Signatures nettes** (taux du département rapporté au taux national, `b_specialisations_top3_2023.csv`, `b_dep_sport_signature_2023.csv`) : ski x21 dans les Hautes-Alpes, x20 en Savoie ; rugby x5,5 dans le Gers, x4,4 en Ariège ; voile x4,0 dans les Côtes-d'Armor ; tir x5,2 en Corse-du-Sud ; golf x2,4 dans les Pyrénées-Atlantiques ; tennis x1,9 dans les Hauts-de-Seine et les Yvelines. Sports régionaux : 52 % des licences de pelote basque sont dans les Pyrénées-Atlantiques, 76 % de la course landaise dans les Landes, 70 % de la balle au tambourin dans l'Hérault.
- **Dispersion** (rapport P90/P10 des taux départementaux, métropole, `b_dispersion_departements_2023.csv`) : les sports les plus « nationaux » sont l'équitation (1,5), le judo (1,6) et le football (1,8) ; les plus localisés, le ski (120), le rugby (9,2) et la voile (9,3).
- **Volume total** (`b_dep_total_2023.csv`) : de 103 licences pour 1 000 habitants en Guyane et 111 en Seine-Saint-Denis à 287 dans les Hautes-Alpes (médiane 195). Paris est 3e plus bas (120).
- **Calcul** : licences par département et fédération / population estimée par l'Insee au 1er janvier 2023 (`estim-pop-dep-sexe-aq-1975-2023.xls`, Mayotte exclue).
- **Source** : `lic-data-2023.csv` ; Insee, estimations de population 2023.
- **Solidité** : **établi** pour les rangs et signatures (écarts très larges). Rappel : domicile du licencié, pas lieu de pratique (un Parisien qui skie en Savoie compte à Paris).

### R2. Dans une même commune, on prend presque deux fois moins de licences en QPV

- **Chiffre** : dans les 569 communes où la population de chaque partie est connue, **103 licences pour 1 000 habitants en QPV contre 180 hors QPV** (rapport 0,58). Commune par commune (564 communes ayant au moins 1 000 habitants en QPV), le rapport médian est 0,60 et le QPV fait mieux que le reste de la commune dans **1,6 % des cas** seulement (`c_qpv_resume_2023.csv`, `c_qpv_communes_taux_2023.csv`).
- **Par sexe** : filles et femmes 32 contre 67 pour 1 000 (rapport 0,48) ; garçons et hommes 72 contre 113 (rapport 0,63). Part des licences féminines : 30,3 % en QPV, 36,8 % hors QPV des mêmes communes (2022 : 29,3 % contre 36,3 %).
- **Calcul** : licences des parties QPV et hors QPV, communes ayant les deux ; population des QPV 2024 (Insee, `pop_QPV24.xlsx`, RP 2020), en ne gardant que les communes dont tous les QPV sont mono-communaux (3,39 millions d'habitants en QPV) ; population hors QPV = population municipale 2021 (Insee) moins population des QPV.
- **Effet d'âge** : les QPV sont plus jeunes (39 % de moins de 25 ans contre 30 % dans leur environnement urbain, Insee Première n° 2008, août 2024). Avec les taux nationaux par âge, cette structure devrait **augmenter** le taux des QPV d'environ 11 % (`c_qpv_effet_structure_age.csv`). Le déficit à âge égal est donc plutôt plus fort que 0,58.
- **Solidité** : **établi** pour le sens et l'ordre de grandeur (régularité commune par commune) ; le niveau exact est **probable** (populations de 2020 et 2021 contre licences 2022-2023).

### R3. Le football est bien surreprésenté en QPV, et pas seulement en part

- **En part des licences** : le football pèse **35,4 % des licences en QPV contre 14,8 %** dans le reste des mêmes communes. Une fois neutralisée l'offre locale (on compare chaque QPV au reste de sa propre commune), le rapport est **2,0** (`c_qpv_vs_horsqpv_federations_2023.csv`, colonne `ratio_standardise_commune` ; 2,0 aussi en 2022, géographie 2015).
- **Pour 1 000 habitants** : 35,9 en QPV contre 25,8 hors QPV, soit **x1,39**. C'est l'une des rares fédérations à dépasser 1 avec la lutte (x1,60) et la boxe (x1,23) ; le kick-boxing est à égalité (0,97), le karaté (0,84), le judo (0,78) et le basket (0,75) sont en dessous.
- **Part due à l'âge** : la seule jeunesse des QPV ferait attendre x1,19 pour le football. Reste un surcroît d'environ **17 %** (1,39 / 1,19) à âge comparable, ordre de grandeur seulement.
- **Les sports les plus rares en QPV** (taux QPV / hors QPV) : golf 0,10, voile 0,15, badminton 0,24, EPGV 0,25, équitation 0,27, tennis 0,28, tir 0,29.
- **Lecture** : le football de quartier est une réalité, mais il compense mal : le taux global reste divisé par près de deux. Le football est surreprésenté en part surtout parce que **les autres sports sont absents**.
- **Solidité** : **établi** pour la part et le classement des fédérations ; **probable** pour le x1,39 ; **fragile** pour la correction d'âge (structure Insee pour l'« environnement urbain », pas pour le hors QPV des mêmes communes).

### R4. Le revenu de la commune : tennis, golf, voile, ski montent avec lui ; le football non

- **Chiffre** (communes classées par niveau de vie médian, Filosofi 2023, en déciles de population, `e_revenu_federations_2023.csv`, `e_revenu_total_2023.csv`) : toutes fédérations, de **127 licences pour 1 000 habitants** dans les communes du 1er décile à **246 au 9e** ; le 10e décile retombe à 228 (Paris, communes aisées très urbaines).
- **Rapport D10 / D1** : ski 10,2 ; voile 7,3 ; golf 7,2 ; tennis 3,9 (de 8,5 à 33,4 pour 1 000) ; équitation 3,3. À l'inverse : football 0,77 (stable de D1 à D9, autour de 31 à 38, puis 24 en D10), boxe 0,50, lutte 0,38.
- **Part des licences féminines** : 34,0 % en D1, 36 à 38 % dans les autres déciles.
- **Calcul** : licences de la commune (toutes parties) / population municipale 2021 ; 30 831 communes avec revenu diffusé.
- **Source** : `lic-data-2023.csv` ; Insee, base « évolution et structure de la population » 2021 ; Insee Filosofi 2023 (module `revenu_filosofi.py` du site).
- **Solidité** : **établi** pour les gradients, mais c'est une **corrélation entre communes**, pas entre personnes : un écart peut tenir à l'offre (golfs, ports, stations), à l'urbanisation ou à l'âge des habitants, pas seulement au revenu.

### R5. Le décrochage à l'adolescence est universel ; il est plus fort chez les filles des QPV

- **National** (`d_age_sexe_national_pivot_2023.csv`) : entre 10-14 ans et 15-19 ans, les licences pour 1 000 passent de **463 à 209 chez les filles** (rapport 0,45) et de **696 à 365 chez les garçons** (0,52). Le pic est à 10-14 ans pour presque tous les sports ; il est plus précoce pour la gymnastique, le judo, la natation et le karaté (5-9 ans, rapport 15-19 / 10-14 entre 0,2 et 0,4), plus tardif pour le volley masculin (1,23) et le rugby féminin (1,15).
- **QPV contre hors QPV, mêmes communes** (`c_qpv_retention_2023.csv`) : rapport des licences 15-19 / 10-14 chez les filles **0,37 en QPV contre 0,45 hors QPV** ; chez les garçons **0,53 contre 0,53**. Même résultat en 2022 avec l'ancienne géographie (filles 0,40 contre 0,46 ; garçons 0,55 contre 0,54). Les garçons servent de témoin : la structure par âge des deux zones touche les deux sexes de la même façon.
- **Par sport** (`c_qpv_retention_federations_2023.csv`) : chez les filles, l'écart QPV / hors QPV est net en natation (0,17 contre 0,29), tennis (0,27 contre 0,42), judo (0,18 contre 0,28), karaté et boxe ; il est faible au football (0,44 contre 0,48) et au handball (0,63 contre 0,72).
- **Calcul** : rapport de licences de deux tranches d'âge voisines, sans population par âge des QPV (non trouvée) ; on suppose des effectifs de 10-14 et 15-19 ans proches dans chaque zone.
- **Solidité** : **probable** (répliqué sur deux millésimes et deux géographies, témoin masculin). L'hypothèse « les filles des quartiers décrochent plus tôt » est **confirmée pour le passage 10-14 / 15-19 ans** ; chez les filles, l'écart apparaît même avant (licences 10-14 / 5-9 ans : 0,97 en QPV contre 1,04 hors QPV ; chez les garçons 1,13 contre 1,08).

### R6. « Les classes supérieures arrêtent vers 15 ans » : non, c'est plutôt l'inverse

- **Chiffre** (licences 2018 et population RP 2017 par commune, âge et sexe, toutes deux dans `lic-data-2018.csv`, `e_revenu_age_sexe_2018_pivot.csv`) : rapport du taux de licence à 15-19 ans sur le taux à 10-14 ans, par décile de revenu des communes :
  - filles : **0,50 en D1**, 0,47 en D2, 0,66 en D6 (maximum), **0,58 en D10** ;
  - garçons : **0,59 en D1**, 0,54 en D2, 0,65 en D6, **0,59 en D10**.
- **En niveau**, à 15-19 ans, les filles des communes du 10e décile ont un taux de licence 2,3 fois plus élevé que celles du 1er (32,7 contre 14,4 pour 100).
- **Le décrochage des communes aisées est plus tardif** : entre 15-19 et 20-29 ans, le rapport tombe à 0,31 (filles) et 0,40 (garçons) en D10, le plus bas de tous les déciles. Explication probable, non testée : départ pour les études (le recensement compte les étudiants majeurs là où ils logent) et grandes villes.
- **Par sport** (`e_revenu_age_sexe_federations_2018.csv`) : seul le football masculin décroche plus en D10 (0,54) qu'en D1 (0,61) ; le tennis, la natation et le judo décrochent moins dans les communes aisées.
- **Sur 2023** (sans population par âge communale, `e_revenu_ratio_ages_2023.csv`), le rapport des licences 15-19 / 10-14 baisse avec le décile chez les garçons (0,53 en D1, 0,47 en D10) : à ne pas lire seul, car la part des 18-19 ans dans la population varie selon les communes (effet étudiant) ; c'est pourquoi le calcul 2018 avec population fait foi.
- **Solidité** : **probable**, lecture **écologique** (communes, pas familles). Ce résultat ne dit rien des choix scolaires des familles ; il dit seulement que le décrochage de 15 ans n'est pas plus fort là où le revenu est élevé.

### R7. Dans le temps : le football stagne, les filles entrent dans les sports « masculins »

- **2019-2023** (même champ et même maille, `f_series_selection.csv`) : licences hors scolaires **13,14 millions en 2019, 10,64 en 2021, 13,31 en 2023**. Football **+0,8 %** (2 198 835 puis 2 215 848), tennis +13 %, basket +15 %, rugby +15 %, natation +11 %, golf +6 % (et +8 % en 2021, en plein Covid), voile +29 % (à vérifier : mode de comptage) ; EPGV -15 %, tennis de table -16 %, UFOLEP -7 %, sport boules -14 %.
- **2013-2018** (ancienne série, champ plus étroit) : football +8 %, tennis -10 %, judo -4 %, équitation -8 %, tir +37 %. Le tennis retrouve en 2023 (1,11 million) son niveau de 2013 (1,08 million) ; vérifier si les licences de padel y sont comptées.
- **Féminisation** (`f_series_part_femmes.csv`, parts, peu sensibles aux ruptures de champ) : football **4,9 % de licences féminines en 2013, 10,2 % en 2023** ; rugby 5,1 % puis 13,0 % ; boxe 19 % puis 27 % ; judo 26 % puis 33 %. Équitation 83 % puis 85 %, gymnastique 80 % puis 84 % : les sports déjà féminins le restent ou le deviennent davantage.
- **Solidité** : **établi** pour 2019-2023 et pour les parts féminines ; **fragile** pour toute comparaison qui traverse 2018-2019. L'INJEP conseille de recaler les séries sur ses données agrégées depuis 2002 (non récupérées : site indisponible ce jour).

---

## (c) Idées reçues : ce qui tient, ce qui ne tient pas

| Idée reçue | Verdict | Résultat |
|---|---|---|
| « Dans les quartiers, on fait du foot. » | **Vrai, mais trompeur.** | Le football pèse 2 fois plus dans les licences en QPV (R3), et il est 1,39 fois plus fréquent par habitant ; mais le taux global de licence y est divisé par près de deux (R2). Le foot est surtout ce qui reste quand le reste manque. |
| « Les jeunes des quartiers font du sport de combat. » | **En partie.** | Lutte et boxe sont plus fréquentes par habitant en QPV ; karaté, judo, taekwondo ne le sont pas (R3). |
| « Les filles des quartiers décrochent plus tôt. » | **Vrai** (à 10-19 ans). | Les garçons des QPV gardent leurs licences comme ailleurs ; les filles décrochent plus (R5). Et elles partent de plus bas : 32 licences féminines pour 1 000 contre 67 (R2). |
| « Les classes supérieures arrêtent le sport vers 15 ans pour l'école. » | **Non** (au niveau des communes). | Le décrochage 10-14 / 15-19 n'est pas plus fort dans les communes aisées ; il l'est dans les plus pauvres (R6). Les communes aisées décrochent après 20 ans. |
| « Le football écrase tout. » | **Vrai pour le rang, faux pour le poids.** | N°1 dans 95 départements, mais 2,2 millions de licences sur 13,3 millions (hors scolaires) et stagnation depuis 2019 (R1, R7). |
| « Le tennis et le golf sont des sports de riches. » | **Vrai, au sens écologique.** | Tennis x3,9 et golf x7,2 entre communes du 10e et du 1er décile ; golf x0,10 en QPV (R3, R4). |
| « Le rugby est un sport du Sud-Ouest. » | **Vrai.** | Taux x5,5 dans le Gers ; le rugby y dépasse le football (R1). |
| « Les grandes villes sont sportives. » | **Non, en licences.** | Seine-Saint-Denis et Paris sont parmi les 3 départements au plus faible taux (R1) ; le 10e décile de revenu, très urbain, est sous le 9e (R4). Ce qui est peut-être un effet « pratique hors club ». |

---

## (d) Pistes de pages pour le site

**Dossier « Sport »** (terrain), mené par les questions, dans l'esprit des autres dossiers :

1. **Carte-question « Dans les quartiers, on fait du foot ? »** : verdict « oui, mais parce que le reste manque » ; chiffre : 35 % des licences en QPV contre 15 % dans le reste de la même commune, et 103 licences pour 1 000 habitants contre 180. Visuel : barres appariées QPV / hors QPV par sport, avec le rapport « à offre communale égale ».
2. **Carte-question « Les filles des quartiers décrochent-elles plus tôt ? »** : verdict « oui, les garçons non » ; courbes par âge, quatre séries (filles et garçons, QPV et hors QPV).
3. **Carte-question « Les enfants des beaux quartiers lâchent-ils le sport pour le lycée ? »** : verdict « non, c'est l'inverse », avec la précaution écologique en clair.
4. **Atlas** : nouveaux indicateurs « licences pour 1 000 habitants » (total, football, tennis, rugby, équitation...) à la maille commune, EPCI, département ; croisement `vs` avec le revenu médian pour faire sortir les **outsiders** : communes pauvres très licenciées, communes aisées peu licenciées (lecture « écart au pronostic »). Attention aux petites communes (seuil de population) et à l'unité « licence ».
5. **Signatures sportives des départements** : une carte « quel sport est surreprésenté chez vous ? » (indice de spécialisation), plus parlante que « le football est n°1 partout ».
6. **Unité « Âge » ou « Sexe »** de l'explorateur : courbes de licence par âge et sexe pour 20 sports (table `d_age_sexe_national_pivot_2023.csv`).
7. **Série « Le football féminin a doublé sa part en dix ans »** (4,9 % à 10,2 %), avec le rugby (5,1 % à 13,0 %).

---

## (e) Ce qui manque ou reste à vérifier

- **Population des QPV par âge et sexe** : non trouvée en source officielle facile (le fichier Insee `pop_QPV24` donne la population totale seulement). Avec elle, R2, R3 et R5 deviendraient des taux par âge. Piste : bases infracommunales Insee sur les QPV, ou carroyage Filosofi.
- **QPV pluri-communaux** : 160 QPV sur 1 609 couvrent plusieurs communes ; leurs communes sont exclues des calculs par habitant (pas de population par commune).
- **Décalage de dates** : population QPV 2020, communale 2021, licences 2022-2023, revenu 2023 en géographie 2025 (quelques communes fusionnées perdues).
- **Séries longues** : récupérer les résultats agrégés de l'INJEP depuis 2002 (site indisponible le 29/10/2026) pour vérifier R7 et les révisions ; vérifier le comptage de la voile 2023 et du tennis (padel).
- **Clubs** : les fichiers `clubs-data-*` permettraient de séparer l'effet d'offre (nombre de clubs par habitant) de l'effet de demande dans R2 et R4.
- **Pratique réelle** : confronter avec l'enquête INJEP « Baromètre national des pratiques sportives » (pratique déclarée, avec diplôme et PCS des individus), qui seule permet une lecture individuelle du gradient social.
- **Licences féminines « 1 ou 2 »** : pas de secret, mais beaucoup de petites valeurs estimées ; ne pas publier de taux pour des communes ou QPV de petite taille.

---

## (f) Faisabilité seulement : un indice de diversité des noms (IDP) pour l'élite sportive

Rien n'a été calculé ni téléchargé de nominatif.

**Sources publiques possibles**
- **Équipes de France** : listes de sélection publiées par les fédérations (communiqués de convocation : football, handball, basket, rugby, athlétisme, judo...) ; délégation française aux Jeux olympiques et paralympiques (liste publiée par le CNOSF et le CPSF, environ 570 athlètes à Paris 2024).
- **Championnats professionnels** : effectifs publiés par les ligues (Ligue de football professionnel, Ligue nationale de rugby, Ligue nationale de basket, Ligue nationale de handball, Ligue féminine de basket et de handball, Arkema Première Ligue).
- **Sportifs de haut niveau** : listes ministérielles des sportifs de haut niveau (catégories Élite, Senior, Relève), publiées par arrêté ; vérifier leur forme et leur caractère public actuel avant tout usage.

**Précautions**
- Calcul **en agrégat seulement**, jamais d'étiquette individuelle (même règle que l'outil de représentativité : le proxy est attaché au nom, pas à la personne).
- **Joueurs étrangers** des championnats professionnels : l'IDP mesure la diversité d'origine des noms nés en France ; il faut restreindre aux joueurs sélectionnables en équipe de France ou formés localement, sinon on mesure le recrutement international.
- **Référentiel INSEE des naissances en France** : les noms de joueurs nés et formés à l'étranger sont hors référentiel ; les Antilles et l'outre-mer sont sous-estimés (migrations antérieures à 1950), point sensible en football, athlétisme, handball, basket.
- **Petits effectifs** (23 à 40 joueurs par sélection) : intervalles larges ; préférer des cumuls (plusieurs saisons, plusieurs sports) et une comparaison au vivier (licenciés du même âge, par exemple à partir de R3 sur les QPV, sans que QPV ne vaille origine).
- **Ne pas confondre** diversité des noms, origine et lieu de vie : un QPV n'est pas une origine, et un nom n'est pas une identité.
- **RGPD** : données publiques mais personnelles ; ne conserver que les agrégats, pas les listes.

---

## (g) Offre ou demande ?

> Ajout du 29 octobre 2026. Script : `python/tools/explore_sport_offre.py` (étapes 0, 1, 2 pour les équipements, 3 et 4 pour les clubs, A pour la section h). Tables : `python/data/sport/sorties/g_*.csv`.
> Question : si le tennis, la natation ou l'équitation sont rares dans les QPV, est-ce faute d'équipements à proximité (offre) ou faute de demande (prix, réseaux, goûts, temps) ?

### La source d'offre : Data ES

- **Jeu** : « Recensement des équipements sportifs, espaces et sites de pratiques » (Data ES), ministère chargé des sports, https://www.data.gouv.fr/datasets/recensement-des-equipements-sportifs-espaces-et-sites-de-pratiques . Ressources utilisées : exports « Équipements » (334 342 équipements) et « Installations » (152 191 installations, pour le code commune), téléchargés le 29/10/2026 depuis equipements.sports.gouv.fr dans `python/data/sport/equipements/`. C'est un **stock actuel** (2025-2026) : les équipements fermés avant n'y figurent pas.
- **Champs utiles** (`g_dataes_champs.csv`) :

| Champ | Contenu | Renseigné |
|---|---|---|
| `famille`, `type`, `code` | 29 familles, 185 types (ex. « Court de tennis », « Bassin sportif de natation », « Dojo / Salle d'arts martiaux ») | 100 % |
| `coordonnees_y`, `coordonnees_x` | latitude, longitude (WGS84) | 96,7 % |
| `installation_numero`, puis `insee` (export installations) | commune de l'installation | 99,98 % |
| **`mise_en_service_date`** | **année** de mise en service (pas de mois) | **62,5 %** |
| `mise_en_service_periode` | tranche (« Avant 1945 », ..., « 1995-2004 », « A partir de 2005 ») | 88,3 % |
| `is_date_mise_en_service_known` | indicateur « date connue » (Oui / Non) | 2,0 % (5 923 « Oui ») |
| `creation_dt`, `date_creation_metier` | date de création de la fiche (31/03/2025 pour 98 % des fiches : migration de la base), **pas** une date d'ouverture | 100 % / 0,5 % |
| `derniers_travaux_date`, `homologation_date` | année des derniers travaux, date d'homologation | 21,7 % / 1,5 % |

- **La date de mise en service existe mais elle est fragile** : 28,4 % des années renseignées entre 1950 et 2015 sont des multiples de 5 (20 % attendus sans arrondi), signe d'années approximées ; seules 25 des 455 mises en service datées de 2020 ou 2021 (types retenus) portent l'indicateur « date connue = Oui ». Une « mise en service » peut aussi être une reconstruction (terrain synthétique remplaçant un terrain en herbe).
- **Correspondance type d'équipement vers fédération** (`g_correspondance_equipement_federation.csv`) : tennis, courts de tennis (37 956) ; natation, bassins sportifs et mixtes, bassins ludiques exclus (3 200) ; judo et karaté, dojos (6 341, partagés) ; boxe, salles de boxe (891) ; équitation, équipements équestres (15 200) ; golf, parcours, practices et parcours d'initiation (1 771) ; football, terrains de football et terrains mixtes (38 300) ; rugby, terrains de rugby, de rugby à XIII et mixtes (4 740) ; basket, gymnases et terrains de basket (26 401) ; handball, gymnases et terrains de handball (21 277) ; gymnastique, salles de gymnastique sportive ; tennis de table, salles spécialisées ; athlétisme, stades et pistes. **Limite** : terrains de grands jeux, gymnases et dojos sont partagés entre sports et avec les scolaires ; la distance à un gymnase ne dit rien du créneau disponible pour un club.
- **Contours des QPV** : contours officiels de l'ANCT (data.gouv), géographie 2024 (GeoJSON WGS84) pour le test 1, géographie 2015 (shapefile WGS84) pour le test 2, dans `python/data/sport/qpv_contours/`. Les distances sont calculées **au contour** (0 si l'équipement est dans le quartier), sans bibliothèque SIG (lecture et géométrie programmées dans le script, projection plane locale, erreur négligeable à ces distances).

### Test 1 : à distance égale d'un équipement, le QPV fait-il jeu égal avec sa commune ?

- **Méthode** : 1 048 QPV 2024 contenus dans une seule commune (569 communes, 3,39 millions d'habitants, mêmes communes que R2). Pour chaque QPV et chaque sport : distance du contour à l'équipement le plus proche existant en 2023 (équipements datés après 2023 exclus, non datés gardés). Licences 2023 du QPV comparées à l'**attendu** si le QPV avait le taux par habitant du hors QPV de sa propre commune (rapport observé / attendu, `g_test1_tranches_distance.csv`). Puis modèle de Poisson (décalage = log de l'attendu, erreurs regroupées par commune) avec la tranche de distance, la taille du QPV (log de la population) et le revenu médian de la commune (Filosofi 2023) (`g_test1_poisson.csv`).
- **Chiffres** : rapport observé / attendu selon la distance à l'équipement le plus proche.

| Sport | moins de 500 m | 500 m à 1 km | 1 à 2 km | plus de 2 km | QPV à moins de 500 m |
|---|---|---|---|---|---|
| Tennis | **0,33** | 0,28 | 0,26 | 0,36 | 51 % |
| Natation | **0,63** | 0,56 | 0,49 | 1,03 | 38 % |
| Équitation | **0,38** | 0,30 | 0,30 | 0,28 | 6 % |
| Golf | **0,12** | 0,10 | 0,12 | 0,13 | 2 % |
| Judo | 0,79 | 0,77 | 0,68 | 0,83 | 64 % |
| Gymnastique | 0,58 | 0,46 | 0,45 | 0,54 | 37 % |
| Athlétisme | 0,42 | 0,33 | 0,29 | 0,43 | 69 % |
| Football | 1,32 | 1,18 | 1,23 | 1,20 | 83 % |
| Basket | 0,74 | 0,61 | (10 QPV) | (3 QPV) | 95 % |

- **Modèle contrôlé** (taille du QPV et revenu de la commune), rapport des taux par rapport à « moins de 500 m » : tennis 0,83 (500 m à 1 km) et 0,75 (1 à 2 km) ; natation 0,83, 0,74, 0,73 ; équitation 0,75, 0,72, 0,64 ; gymnastique 0,80, 0,78, 0,75 ; athlétisme 0,84, 0,76, 0,71 ; football 0,89 et 0,88 ; golf, rugby, judo, karaté, basket, handball : pas d'écart net (intervalles à 95 % qui couvrent 1, ou presque tous les QPV dans la même tranche).
- **Lecture** : la proximité compte un peu (de l'ordre de 15 à 35 % de licences en plus quand l'équipement est à moins de 500 m), mais **elle ne comble pas l'écart** : même avec un court à moins de 500 m, un QPV a trois fois moins de licences de tennis par habitant que le reste de sa commune ; avec un équipement équestre proche, 2,6 fois moins ; avec un golf proche, 8 fois moins. Le football, lui, est au-dessus du hors QPV à toutes les distances. Autre signal : plus la commune est aisée, plus l'écart QPV / hors QPV est grand pour le tennis, l'équitation, le golf et le rugby (coefficient du revenu nettement inférieur à 1), et plus il est petit pour le football et la boxe (coefficient supérieur à 1).
- **Solidité** : **probable** pour « la proximité ne suffit pas » (écart massif à moins de 500 m, régulier d'une tranche à l'autre) ; **fragile** pour l'ampleur de l'effet de distance.
- **Limites** : **c'est une corrélation**, les équipements ne sont pas placés au hasard (on construit là où l'on attend des pratiquants, ou là où la politique de la ville finance) ; la distance n'est mesurée que pour le QPV, pas pour le reste de la commune, qui a souvent lui aussi un équipement proche ; un équipement proche n'est pas forcément accessible (club privé, tarif, créneaux, équipement scolaire) ; stock 2025-2026 appliqué aux licences 2023 ; revenu de la commune et non du quartier (pas de revenu par QPV mobilisé ici) ; populations QPV 2020 et communales 2021.

### Test 2 : quand un équipement ouvre près d'un QPV, les licences suivent-elles ?

- **Fenêtre retenue : millésimes 2019 à 2022, géographie QPV 2015**, ouvertures datées 2020 ou 2021. Raisons : 2019 est le premier millésime à la maille QPV ; 2023 change de géographie (codes QN, périmètres redessinés) ; 2018 n'a pas le détail par QPV. On compare les extrémités 2019 (avant) et 2022 (après), deux saisons hors confinement ; 2020 et 2021 (Covid) sont montrés mais pas utilisés pour l'effet. La part de licences non réparties change entre 2019 (3,7 %) et 2022 (2,2 %), mais de la même façon pour traités et témoins.
- **Méthode** : 1 248 QPV 2015 présents dans une seule commune chaque année. **Traités** : QPV avec au moins un équipement du type mis en service en 2020 ou 2021 à moins de 1 km du contour. **Témoins** : QPV sans aucun équipement du type daté de 2018 à 2023 à moins de 1 km. Attendu 2022 d'un QPV = licences 2019 x évolution 2019-2022 du hors QPV de sa commune (ce qui neutralise la tendance communale) ; différence de différences = (observé / attendu des traités) / (observé / attendu des témoins) ; intervalle à 90 % par rééchantillonnage des QPV (`g_test2_did.csv`, trajectoires annuelles dans `g_test2_trajectoires.csv`, liste des QPV traités dans `g_test2_ouvertures_qpv_2015.csv`).
- **Nombre de cas** : 455 mises en service datées 2020-2021 pour les types retenus en France, **peu près d'un QPV** : basket 32 QPV traités, handball 21, football 15, natation 14, judo et karaté 11, gymnastique 6, rugby 4, tennis 2, athlétisme 2, golf 1, tennis de table 1, équitation et boxe 0. Le karaté est absent des fichiers 2019 à 2021 : test impossible.
- **Chiffres** (différence de différences, intervalle à 90 %) :
  - football (15 QPV, 2 868 licences en 2019) : **1,21 [1,08 ; 1,36]** ;
  - natation (10 QPV utilisables, **57 licences** en 2019) : 1,85 [0,97 ; 2,24], trajectoire régulière (1,24 en 2020, 1,50 en 2021, 1,68 en 2022, contre environ 0,93 chez les témoins) ;
  - basket (31 QPV) : 0,98 [0,89 ; 1,09] ; handball (19) : 1,06 [0,79 ; 1,23] ; judo (11) : 0,87 [0,77 ; 1,10] ;
  - tennis (2 QPV), golf (1), rugby (4), gymnastique (3 utilisables), tennis de table (1), athlétisme (1) : **trop peu de cas pour conclure**, chiffres non interprétés.
- **Solidité** : **fragile** partout. Le football est le seul résultat dont l'intervalle exclut 1, mais sur 15 QPV, sans possibilité de vérifier la tendance avant l'ouverture (un seul millésime avant), avec des dates de mise en service peu sûres (une partie peut être des reconstructions de terrains). La natation va dans le même sens mais sur des effectifs minuscules. Les équipements partagés (gymnases, dojos) ne montrent rien.
- **Pour aller plus loin** : une vraie expérience naturelle demanderait des dates d'ouverture vérifiées (délibérations municipales, programmes de rénovation urbaine, plan « 5 000 terrains de sport » de l'Agence nationale du sport, dont les terrains sont listés) et des licences au QPV sur plus d'années en géographie 2024 (2023, puis 2024 et 2025 quand ils seront géocodés).

### Test 3 : le QPV qui abrite un club du sport a-t-il plus de licenciés ?

- **Source** : fichiers « clubs » du même jeu INJEP (`clubs-data-2019.csv` à `clubs-data-2023.csv`, dictionnaire `clubs-dictionnaire-des-variables.xlsx`, relu). Maille commune x QPV comme les licences, géographie QPV 2015 jusqu'en 2022 et 2024 en 2023, code commune de l'année N+1 pour le millésime N. Variables : `Clubs` (associations affiliées), `EPA` (établissements professionnels agréés, par exemple centres équestres commerciaux), `Total` ; en 2023 seulement, `Clubs_actifs`, `EPA_actifs`, `Total_actifs` (au moins une licence annuelle). Les clubs sont localisés à **leur adresse** (le dictionnaire ne précise pas laquelle : siège, lieu de pratique ou domicile d'un dirigeant), les licences au domicile du licencié. Clubs non répartis : 12,0 % en 2019, 3,6 % en 2020, 3,4 % en 2021, 2,6 % en 2022 (`g_test4_clubs_non_repartis.csv`).
- **Méthode** (coupe 2023, mêmes 1 048 QPV et 569 communes que le test 1) : par QPV et par sport, présence d'au moins une structure active de la fédération (club ou EPA, `Total_actifs`) dans le QPV. Rapport licences observées / attendues au taux du reste de la commune, QPV avec et sans club (`g_test3_avec_sans_club.csv`) ; modèle de Poisson avec la taille du QPV et le revenu de la commune, erreurs regroupées par commune (`g_test3_poisson.csv`) ; densité de clubs QPV / hors QPV à côté de l'écart de licences (`g_test3_clubs_densite.csv`).
- **Chiffres** :

| Sport | QPV avec club | Licences / attendu, avec club | sans club | Effet « club » contrôlé (IC 95 %) | Clubs pour 10 000 hab. QPV / hors QPV | Licences QPV / hors QPV |
|---|---|---|---|---|---|---|
| Tennis | 9 % | 0,45 | 0,29 | 1,39 (1,08 à 1,79) | 0,43 | 0,28 |
| Équitation | 4 % | 0,47 | 0,28 | 1,64 (1,35 à 2,00) | 0,25 | 0,27 |
| Golf | 2 % | 0,11 | 0,12 | 0,86 (0,57 à 1,30) | 0,21 | 0,10 |
| Natation | 7 % | 0,82 | 0,62 | 1,47 (1,14 à 1,90) | 0,87 | 0,68 |
| Judo | 14 % | 0,96 | 0,74 | 1,40 (1,25 à 1,56) | 0,83 | 0,78 |
| Handball | 8 % | 0,94 | 0,51 | 1,71 (1,43 à 2,05) | 0,84 | 0,56 |
| Basket | 10 % | 0,96 | 0,69 | 1,38 (1,22 à 1,57) | 0,74 | 0,75 |
| Rugby | 4 % | 0,67 | 0,47 | 1,35 (1,05 à 1,75) | 0,46 | 0,45 |
| Boxe | 9 % | 1,70 | 1,09 | 1,52 (1,24 à 1,86) | 1,02 | 1,23 |
| Football | 19 % | 1,39 | 1,26 | 1,11 (1,04 à 1,18) | 0,87 | 1,39 |

- **Lecture** : les QPV qui abritent un club du sport ont 30 à 70 % de licenciés de plus, à commune, taille et revenu donnés (sauf golf et tennis de table, non significatifs, et football, +11 %). Mais **même avec un club dans le quartier**, le tennis reste à 0,45 du taux du reste de la commune et l'équitation à 0,47. Les clubs sont plus rares en QPV pour les sports distinctifs (tennis : 2,3 fois moins de clubs par habitant ; équitation : 4 fois moins), et l'écart de licences de tennis (0,28) est plus grand que l'écart de clubs (0,43).
- **Solidité** : **probable** pour l'association (régulière sur 12 sports sur 14) ; rien de causal.
- **Limites** : **causalité inverse** probable (un club naît et survit là où il y a des pratiquants) ; adresse du club pas forcément lieu de pratique ; un club dans le QPV n'est pas forcément fréquenté par ses habitants ; un club hors du QPV peut être à 200 m ; structures actives seulement en 2023.

### Test 4 : quand un club arrive ou quitte un QPV, les licences suivent-elles ?

- **Fenêtre retenue : 2020 -> 2022, géographie QPV 2015**, contrôle de pré-tendance 2019 -> 2020. 2019 n'est pas pris comme année de départ car 12 % des clubs y sont non répartis (contre 3,6 % en 2020) : une partie des « arrivées » 2019 -> 2022 serait un artefact de géocodage. 2020 (saison 2019-2020, interrompue en mars) sert de base ; 2021 (Covid) est montré sans servir à l'effet. Avant 2023, les clubs inactifs sont comptés.
- **Méthode** : 1 248 QPV 2015 mono-communaux. **Arrivée** : 0 structure de la fédération dans le QPV en 2020, au moins 1 en 2022 ; témoins : 0 en 2020, 2021 et 2022. **Départ** : au moins 1 en 2020, 0 en 2022 ; témoins : au moins 1 chaque année. Attendu 2022 = licences 2020 x évolution du hors QPV de la commune ; différence de différences = (observé / attendu des traités) / (observé / attendu des témoins), intervalle à 90 % par rééchantillonnage ; pré-tendance = même calcul sur 2019 (`g_test4_did_clubs.csv`, `g_test4_trajectoires.csv`).
- **Nombre de cas** (QPV utilisables) : arrivées : football 152, basket 74, judo 48, gymnastique 47, athlétisme 46, tennis 45, boxe 43, natation 28, handball 18, tennis de table 17, équitation 16, golf 8, rugby 7. Départs : football 169, judo 118, basket 70, tennis 60, gymnastique 43, boxe 39, équitation 38, tennis de table 33, athlétisme 28, natation 24, handball 19, rugby 10, golf 9 ; les témoins des départs sont peu nombreux (7 à 74 QPV ayant un club chaque année). Karaté : absent des licences 2019 à 2021, test impossible.
- **Chiffres** (différence de différences, intervalle à 90 %) :
  - arrivées : football 1,03 (0,99 à 1,06) ; judo 1,04 (0,93 à 1,14) ; basket 0,92 (0,86 à 1,00) ; athlétisme 1,10 (1,00 à 1,20) ; gymnastique 0,91 (0,83 à 1,03) ; boxe 1,09 (0,94 à 1,25) ; natation 1,11 (0,95 à 1,48) ; tennis 1,37 (0,86 à 2,18) ; handball 1,25 (0,95 à 1,68) ; équitation 0,89 (0,75 à 1,04) ;
  - départs : football 0,96 (0,92 à 1,00) ; judo 0,97 (0,82 à 1,17) ; basket 0,94 (0,80 à 1,08) ; tennis 0,85 (0,70 à 1,04) ; boxe 0,81 (0,66 à 1,06) ; équitation 0,92 (0,78 à 1,07) ;
  - pré-tendances 2019 -> 2020 proches de 1 pour les effectifs importants (football 0,99, basket 0,99, judo 1,01, tennis 1,07), mauvaises pour les petits groupes (natation, départs : 1,93).
- **Lecture** : sur deux saisons, l'arrivée ou le départ d'un club dans un QPV ne s'accompagne **d'aucun mouvement net** des licences des habitants pour les sports où les cas sont nombreux (football, judo, basket : effets compris entre -8 % et +4 %). Pour le tennis, la natation et le handball, les points estimés vont dans le sens attendu (arrivée +11 à +37 %, départ -15 % pour le tennis) mais les intervalles couvrent 1.
- **Solidité** : **fragile** (fenêtre courte et perturbée par le Covid, clubs inactifs comptés avant 2023, une « arrivée » peut être un simple changement d'adresse de siège).
- **Limites** : adresse du club souvent celle du siège, parfois chez un dirigeant ; les licenciés d'un club ne vivent pas forcément dans le QPV où il est domicilié ; causalité inverse ; deux saisons ne suffisent pas à voir l'effet d'un club sur des enfants qui s'inscrivent progressivement.

### Ce qu'on peut en conclure, prudemment (révisé avec les équipements et les clubs)

1. **L'offre est réellement plus rare dans les QPV pour les sports distinctifs** (section h, descriptif, **établi**) : dans le contour des quartiers, 4 fois moins de courts de tennis par habitant que dans le reste de la commune, 18 fois moins d'équipements équestres, 30 fois moins de golfs, 1,6 fois moins de bassins ; 2,3 fois moins de clubs de tennis, 4 fois moins de structures équestres.
2. **Pour le tennis, la natation et les sports de dojo, l'écart de licences est du même ordre que l'écart d'équipements** dans le quartier (tennis 0,28 contre 0,25 ; natation 0,68 contre 0,62 ; judo 0,78 contre 0,84). L'offre manquante pourrait donc rendre compte d'une bonne partie de l'écart **en moyenne**.
3. **Mais l'offre proche ne suffit pas à le combler** : avec un court à moins de 500 m, le QPV reste à 0,33 du reste de sa commune (test 1) ; avec un club de tennis dans le quartier, à 0,45 (test 3). Les QPV mieux dotés font mieux (+30 à +70 % avec un club, corrélation), sans rejoindre le reste de la commune. Et quand l'offre change (ouvertures 2020-2021, arrivées et départs de clubs 2020-2022), les licences ne bougent pas de façon mesurable, sauf peut-être pour les terrains de football (tests 2 et 4, **fragiles**).
4. **Pour les sports de gymnase** (handball, gymnastique, athlétisme, tennis de table), l'écart de licences est **plus grand** que l'écart d'équipements : la salle est là (gymnase dans le quartier 0,8 à 0,9 fois autant que dans le reste de la commune), les licences moins. Ce qui manque n'est pas le bâtiment (créneaux, encadrement, coût, demande : non mesurés).
5. **Le football fait exception** : moins de terrains par habitant dans le quartier (0,48), mais plus de licences (1,39) ; l'offre y suit ou précède une demande déjà forte.
6. **En résumé** : offre et demande ne s'opposent pas. L'offre est plus rare en QPV pour les sports distinctifs, et sa présence va avec plus de licences ; mais à offre locale donnée, il reste un écart important que ces données ne permettent pas d'attribuer (prix, places en club, réseaux, goûts, temps des parents). Aucun de ces résultats n'est causal.

---

## (h) Ce qui est disponible : équipements et clubs

> Section descriptive (pas un test). Script : `explore_sport_offre.py`, étape A. Tables `h_*.csv`. Équipements : Data ES, types retenus selon la correspondance de la section g, **stock 2025-2026** dont on retire les équipements datés après 2023 (les non datés sont gardés). Licences : 2023.

### h1. Équipements et licences selon le revenu de la commune

Mêmes déciles de population que R4 (niveau de vie médian Filosofi 2023, bornes de `e_bornes_deciles_2023.csv`), population municipale 2021, arrondissements pour Paris, Lyon et Marseille (`h_equipements_deciles_revenu.csv`).

| Sport | Équipements pour 10 000 hab. D1 | D5 | D10 | Rapport D10 / D1 équipements | Rapport D10 / D1 licences |
|---|---|---|---|---|---|
| Tennis (courts) | 3,5 | 5,6 | 6,3 | **1,8** | **3,9** |
| Équitation | 0,7 | 2,4 | 2,6 | 3,9 | 3,3 |
| Golf | 0,11 | 0,19 | 0,49 | 4,5 | 7,2 |
| Natation (bassins sportifs et mixtes) | 0,57 | 0,55 | 0,32 | **0,56** | **1,37** |
| Dojos (judo, karaté) | 0,95 | 0,94 | 0,84 | 0,89 | 1,58 (judo) |
| Gymnases et terrains (basket) | 4,1 | 4,2 | 2,9 | 0,71 | 1,24 |
| Terrains de football | 3,9 | 6,8 | 3,0 | 0,76 | 0,77 |
| Terrains de rugby | 0,58 | 0,82 | 0,37 | 0,64 | 1,48 |
| Athlétisme | 1,26 | 0,99 | 0,59 | 0,47 | 1,63 |

- **Lecture** : seuls le tennis, l'équitation et le golf ont **plus d'équipements par habitant dans les communes aisées** ; pour les bassins, gymnases, dojos et stades, c'est l'inverse ou c'est plat. Pour le tennis, l'écart de licences entre communes riches et pauvres (x3,9) est **deux fois plus fort** que l'écart de courts (x1,8) ; pour la natation, les communes aisées ont moins de bassins par habitant mais plus de licences.
- **Taille de la commune** (`h_equipements_taille_commune.csv`) : le nombre d'équipements par habitant baisse avec la taille pour presque tous les sports (terrains de football : 10,7 pour 10 000 habitants dans les communes de moins de 2 000 habitants, 1,3 dans celles de 200 000 et plus ; courts de tennis : 7,6 puis 2,2 ; équitation : 4,6 puis 0,16), alors que les licences de tennis, de natation et de golf sont plus élevées dans les grandes villes. Un taux « par habitant » d'équipements mesure donc beaucoup la ruralité ; les déciles extrêmes de revenu sont très urbains.
- **Solidité** : **établi** (comptages descriptifs) ; la comparaison entre déciles mélange revenu et urbanisation.

### h2. Dans le contour des QPV contre le reste de la commune

- **Champ** : les 1 048 QPV de la **géographie 2024** contenus dans une seule commune, 569 communes ; population de référence : population municipale des QPV au 1er janvier 2020 (Insee, `pop_QPV24`) pour les QPV, population municipale 2021 de la commune moins celle de ses QPV pour le reste (3,39 millions contre 14,74 millions d'habitants). Équipement « dans le QPV » : point situé dans le contour officiel ANCT (test pair-impair sur le polygone). 3 342 équipements des types retenus sont dans un de ces QPV, dont 9 rattachés par Data ES à une commune voisine (`h_equipements_dans_qpv_2024.csv`).
- **Chiffres** (`h_qpv_equipements_licences_2023.csv`, et clubs actifs 2023 de `g_test3_clubs_densite.csv`), rapports QPV / reste de la commune, par habitant :

| Sport | Équipements | Clubs actifs | Licences | Lecture |
|---|---|---|---|---|
| Tennis | 0,25 | 0,43 | 0,28 | écart de licences proche de l'écart d'équipements |
| Natation | 0,62 | 0,87 | 0,68 | idem |
| Judo (dojos) | 0,84 | 0,83 | 0,78 | idem |
| Karaté (dojos) | 0,84 | 0,81 | 0,84 | idem |
| Boxe (salles) | 1,23 | 1,02 | 1,23 | idem, au-dessus de 1 |
| Équitation | 0,05 | 0,25 | 0,27 | licences bien moins en retrait que les équipements (pratique hors du quartier) |
| Golf | 0,03 | 0,21 | 0,10 | idem |
| Rugby | 0,22 | 0,46 | 0,45 | idem |
| Football | 0,48 | 0,87 | 1,39 | licences au-dessus malgré moins de terrains |
| Basket | 0,87 | 0,74 | 0,75 | licences plus en retrait que les gymnases |
| Handball | 0,78 | 0,84 | 0,56 | idem |
| Gymnastique | 0,64 | 0,74 | 0,52 | idem |
| Athlétisme | 0,62 | 0,68 | 0,40 | idem |
| Tennis de table | 0,68 | 0,40 | 0,37 | idem |

- **Lecture** : trois familles. (1) Tennis, natation, dojos, boxe : l'écart de licences **ressemble** à l'écart d'équipements dans le quartier. (2) Équitation, golf, rugby : les équipements sont presque absents des QPV (grands terrains, hors de la ville dense), mais les habitants ont des licences un peu plus souvent que ne le laisserait croire l'équipement du quartier. (3) Sports de gymnase : la salle est souvent dans le quartier, les licences beaucoup moins.
- **Solidité** : **établi** pour les comptages ; l'interprétation (« l'écart de licences dépasse ou non l'écart d'équipements ») est **probable**, puisque les habitants pratiquent aussi hors de leur quartier.

### Limites communes aux équipements et aux clubs

- **Stock 2025-2026** de Data ES, appliqué aux licences 2023 (équipements fermés depuis absents, dates de mise en service incomplètes).
- **Équipements partagés** : gymnases, terrains de grands jeux, dojos servent à plusieurs sports, aux scolaires et au public libre ; un même gymnase compte pour le basket et pour le handball.
- **Équipements scolaires** : nombre de gymnases et de terrains appartiennent à des collèges et lycées ; leur ouverture aux clubs est inconnue.
- **Accès réel inconnu** : tarif, créneaux, liste d'attente, encadrement, statut privé (clubs de tennis et centres équestres) ne figurent pas dans les données.
- **Clubs** : adresse souvent celle du siège ; un club dans un QPV n'est pas forcément fréquenté par ses habitants ; inactifs comptés avant 2023.
