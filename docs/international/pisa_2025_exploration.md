# PISA 2025 : la France à contexte égal (exploration, non publiée)

> Exploration du 29 octobre 2026 pour un éventuel dossier Outsiders. Rien n'est publié, rien n'est dans `frontend/`.
> Code : `python/tools/explore_pisa.py`. Tables : `python/data/international/pisa/` (classeurs OCDE en cache dans `raw/`).
> Toutes les données PISA viennent des **tableaux publiés par l'OCDE** (valeurs plausibles, poids et erreurs types déjà traités par l'OCDE). Aucune microdonnée.

## Sources

| Code | Source exacte | Contenu utilisé |
|------|---------------|-----------------|
| [S1] | OCDE, *PISA 2025 Results (Volume I)*, annexe Excel, [stat.link/mrq53f](https://stat.link/mrq53f), version 1 du 08-09-2026 | Tableaux I.B1.2a.1 à 3 (moyennes, écarts types, percentiles 2025), 33 à 35 (élèves faibles et très performants depuis 2000), 36 à 38 (moyennes depuis 2000), 39 à 44 (percentiles et dispersion), 45 à 50 (bornes « tous les 15 ans ») |
| [S2] | OCDE, *PISA 2025 Results (Volume I)*, annexe Excel, [stat.link/k68msa](https://stat.link/k68msa) | Tableaux I.B1.2b.1 (indice ESCS), 2 à 4 (gradient social 2025), 22 à 27 (quarts sociaux et R² 2015-2025) |
| [S3] | OCDE, *PISA 2025 Results (Volume I)*, annexe A2, [stat.link/pe3lsg](https://stat.link/pe3lsg) | Tableau I.A2.1 (indice de couverture 3, 2003-2025) |
| [S4] | OCDE, *PISA 2022 Results (Volume I)*, annexe Excel, [stat.link/wh9d4z](https://stat.link/wh9d4z) | Tableaux I.B1.5.4 à 6 (moyennes 2000-2022, pour les pays absents en 2025) |
| [S5] | Ministère turc de l'Éducation (MEB), [communiqué PISA 2025](https://www.meb.gov.tr/according-to-the-pisa-2025-results-turkiye-is-the-country-showing-the-greatest-improvement-across-all-domains\haber/41822/en) | Date et heure de publication, rangs turcs, nombre de participants par vague |
| [S6] | Ministère de l'Éducation de Singapour, [annexe des moyennes PISA 2025](https://www.moe.gov.sg/media/newsroom/news/press/2026/75db500e-ed2c-4b2a-8eef-74460c5c74af.pdf) | Contrôle croisé des moyennes arrondies de tous les pays |
| [S7] | Banque mondiale, API WDI : `NY.GDP.PCAP.PP.KD` (PIB par habitant, PPA, dollars constants 2021), `SE.XPD.SECO.PC.ZS` (dépense publique par élève du secondaire, % du PIB par habitant) | Modèle « score attendu » |
| [S8] | IEA, TIMSS 2023, tableaux internationaux repris par [CUHK](https://www.cpr.cuhk.edu.hk/wp-content/uploads/newscentre/pressrelease/Annex-English_TIMSS-2023.pdf) ; MEB, [rapport TIMSS 2019 Türkiye](https://www.meb.gov.tr/timss-2019-turkiye-raporu/haber/22125/tr) | Triangulation pour la Turquie |

Les pages HTML de l'OCDE (notes pays, rapport en ligne) refusent les accès automatisés (HTTP 403) : je n'ai pas pu lire la note pays France ni le texte du rapport. Les classeurs Excel des annexes, eux, sont accessibles et contiennent tous les chiffres.

---

## 0. Faits vérifiés et corrigés

| Affirmation de départ | Verdict | Chiffre vérifié et source |
|---|---|---|
| Publication le 8 septembre 2026 | **Exact** | Classeurs OCDE « Last updated: 08-Sep-2026 » [S1-S3] ; communiqué MEB daté du 8 septembre 2026, 10 h 50 [S5] |
| Turquie 494 en sciences (OCDE 482) | **Exact** | 494,3 contre 481,9 [S1, tableau I.B1.2a.1] |
| Turquie 472 en lecture (OCDE 461) | **Exact** | 472,1 contre 460,9 [S1, I.B1.2a.2] |
| Turquie 462 en maths (OCDE 463) | **Exact** | 461,6 contre 463,0 [S1, I.B1.2a.3] |
| Couverture turque d'environ 72 % des 15 ans | **Exact** | Indice de couverture 3 = 0,722 en 2025 (0,737 en 2022, 0,356 en 2003) [S3, I.A2.1]. Précision : l'indice compte aussi les élèves exclus, pas seulement les jeunes hors école. |
| 91 pays participants | **Exact, à préciser** | 91 « pays et économies » (dont entités infranationales : Pékin-Shanghai-Jiangsu-Zhejiang, Hong Kong, Macao, Taipei, Kurdistan irakien, Douchanbé, 17 régions ukrainiennes). 90 en lecture et en maths : l'Ouzbékistan n'a que les sciences [S1, S6]. |
| « 41 au début » | **Inexact** | 41 est le chiffre de 2003 [S5]. Le premier cycle, en 2000, comptait 32 pays (43 avec les 11 pays testés en 2002). Série MEB : 41 (2003), 57 (2006), 65 (2009 et 2012), 72 (2015), 79 (2018), 81 (2022), 91 (2025) [S5]. |
| Espagne, France et Norvège derrière la Turquie dans les trois domaines | **Vrai sur les moyennes, à nuancer** | France : 483,4 / 456,3 / 457,7 ; Espagne : 477,1 / 451,4 / 457,4 ; Norvège : 470,2 / 452,8 / 451,8 (sciences / lecture / maths) [S1]. **Mais en maths l'écart Turquie-France (3,9 points, erreur type 3,8, z = 1,0) et Turquie-Espagne (4,1 points, z = 1,4) n'est pas statistiquement significatif.** La Norvège porte un astérisque OCDE (normes d'échantillonnage non respectées). Voir `comparaisons_ecarts.csv`. |
| (Ajout) La France sous la moyenne de l'OCDE | **Non significatif** | Écart France - moyenne OCDE : +1,5 en sciences, -4,6 en lecture, -5,4 en maths ; aucun n'est significatif au seuil de 5 % (z = 0,5 ; -1,4 ; -1,8). Test simple qui ignore que la France fait partie de la moyenne. |
| (Ajout) Rang turc 19e / 18e / 28e sur 91 | **Exact** | Recalculé sur [S1] : 19e en sciences, 18e en lecture, 28e en maths, identique au MEB [S5]. |

Autres chiffres de contexte relevés : plus de 760 000 élèves testés, représentant environ 33 millions de jeunes de 15 ans (avant-propos du rapport, cité par le MEB) ; baisse de la moyenne OCDE entre 2015 et 2025 de 28 points en lecture, 22 en maths, 7 en sciences (bianet, citant le rapport).

---

## 1. Classement à couverture égale

**Principe.** L'indice de couverture 3 (CI3) est la part des 15 ans que représente l'échantillon. Les jeunes non couverts (non scolarisés, scolarisés avant la 7e année, exclus) sont en moyenne plus faibles. Deux corrections :

- **Méthode OCDE (borne officielle)** : l'OCDE publie elle-même, pour chaque pays, la médiane de *tous* les 15 ans en supposant que les non-couverts scorent sous la médiane (tableaux I.B1.2a.48 à 50 [S1]). C'est une **borne basse**, qui pénalise au maximum les pays peu couverts.
- **Hypothèse transparente (la mienne)** : moyenne de tous les 15 ans = CI3 × moyenne observée + (1 - CI3) × score du 10e (ou du 25e) centile du pays. **C'est une hypothèse, pas une mesure** : on ne sait pas ce que feraient les non-couverts.

**Résultats (rang parmi les 90 ou 91 participants ; entre parenthèses, rang parmi les 38 pays de l'OCDE).** Fichier `classement_couverture.csv`.

| Domaine | Pays | CI3 | Moyenne brute | Rang brut (fourchette*) | Hyp. P25 | Hyp. P10 | Médiane borne OCDE |
|---|---|---|---|---|---|---|---|
| Sciences | France | 0,88 | 483,4 | 27e (20e-33e) (OCDE 22e) | 474,2 : 28e (23e) | 466,5 : 29e (23e) | 468,9 : 25e (20e) |
| Sciences | Turquie | 0,72 | 494,3 | 19e (14e-21e) (OCDE 14e) | 475,8 : 26e (21e) | 460,0 : 34e (28e) | 444,0 : 37e (30e) |
| Lecture | France | 0,88 | 456,3 | 28e (25e-32e) (OCDE 23e) | 447,2 : 29e (23e) | 439,3 : 27e (21e) | 440,6 : 27e (21e) |
| Lecture | Turquie | 0,72 | 472,1 | 18e (16e-24e) (OCDE 13e) | 454,9 : 25e (20e) | 439,1 : 29e (23e) | 426,2 : 37e (30e) |
| Maths | France | 0,88 | 457,7 | 34e (25e-38e) (OCDE 29e) | 449,3 : 35e (28e) | 442,8 : 35e (28e) | 440,7 : 34e (27e) |
| Maths | Turquie | 0,72 | 461,6 | 28e (24e-35e) (OCDE 23e) | 442,0 : 39e (32e) | 427,5 : 41e (32e) | 407,3 : 45e (34e) |

\* Fourchette : meilleur et pire rang compatibles avec les erreurs types (pays significativement au-dessus ou en dessous, z = 1,96). Méthode simplifiée, proche de l'esprit des « rangs possibles » de l'OCDE.

**Lecture.**
- La France bouge peu (CI3 de 0,88, égal à la médiane des 91 participants) : 1 à 2 places.
- La Turquie perd 7 à 17 places selon l'hypothèse. **À couverture égale, la France repasse devant la Turquie en maths dans toutes les variantes**, reste devant en sciences et en lecture avec l'hypothèse P10 et la borne OCDE, et reste juste derrière avec l'hypothèse P25 (474 contre 476 en sciences).
- Indicateur parlant publié par l'OCDE (tableaux I.B1.2a.45 à 47 [S1]) : part des 15 ans « hors école, exclus ou sous le niveau 2 » (borne haute) : **France 34,7 % en sciences, 40,8 % en lecture, 43,4 % en maths ; Turquie 41,8 %, 45,2 %, 53,6 %.** Rapporté à toute la génération, la Turquie compte plus de jeunes sans les compétences de base que la France.
- Parmi les élèves testés, la Turquie fait mieux que la France **en bas de la distribution** (10e centile en sciences : 371 contre 342 ; en lecture : 353 contre 315), à égalité en haut (90e centile en sciences : 619 contre 615) [S1, I.B1.2a.1 à 3].

**Solidité.** Classement brut : établi. Sens de la correction : établi (c'est arithmétique). Ampleur et rangs corrigés : **fragile**, entièrement dépendants de l'hypothèse sur les non-couverts. La borne OCDE est officielle mais extrême.

---

## 2. Le rang qui baisse : effet de composition ou recul réel ?

**Méthode.** Moyennes de toutes les vagues depuis 2000 (lecture), 2003 (maths), 2006 (sciences), tirées des tableaux de tendance 2025 [S1, I.B1.2a.36 à 38], complétées par ceux de 2022 [S4] pour les pays sortis. **Groupe stable** : participants présents et comparables à chaque vague (27 en lecture, 33 en maths, 46 en sciences ; listes dans `groupe_stable_*.csv`). Le rang de la France se décompose exactement : rang = 1 + pays stables au-dessus + autres pays au-dessus.

Les tableaux de tendance omettent les participants sortis avant 2022 ou jugés non comparables (Liechtenstein, Shanghai, Viet Nam avant 2022, Pékin-Shanghai-Jiangsu-Guangdong en 2015, Russie). La colonne « rang complété » les ajoute **à la main** quand ils dépassaient la France (liste dans le code, **à vérifier** dans les rapports de chaque vague avant toute publication).

| Domaine | Année | Score France | Rang (complété) | Participants officiels | Rang dans le groupe stable | Stables au-dessus | Autres au-dessus |
|---|---|---|---|---|---|---|---|
| Maths | 2003 | 510,8 | 16e | 41 | 15e / 33 | 14 | 1 |
| Maths | 2012 | 495,0 | 25e | 65 | 17e / 33 | 16 | 8 |
| Maths | 2018 | 495,4 | 25e | 79 | 18e / 33 | 17 | 7 |
| Maths | 2025 | 457,7 | 34e | 91 | 25e / 33 | 24 | 9 |
| Lecture | 2000 | 504,7 | 13e | 32 (43) | 13e / 27 | 12 | 0 |
| Lecture | 2018 | 492,6 | 23e | 79 | 15e / 27 | 14 | 8 |
| Lecture | 2025 | 456,3 | 28e | 91 | 18e / 27 | 17 | 10 |
| Sciences | 2006 | 495,2 | 25e | 57 | 23e / 46 | 22 | 2 |
| Sciences | 2018 | 493,0 | 24e | 79 | 22e / 46 | 21 | 2 |
| Sciences | 2025 | 483,4 | 27e | 91 | 24e / 46 | 23 | 3 |

Tableau complet : `rang_france_historique.csv` (toutes les vagues, rang parmi l'OCDE et parmi l'OCDE stable).

**Décomposition.**
- **Maths, 2003-2025** : 18 places perdues, dont **10 face aux pays stables** (recul réel) et **8 face à des nouveaux venus** (effet de composition) : un peu moins de la moitié. **Mais depuis 2018** : 9 places perdues, dont **7 face aux pays stables** ; la chute récente est surtout réelle.
- **Lecture, 2000-2025** : 15 places perdues, dont 5 face aux stables et 10 face aux nouveaux venus : **les deux tiers sont un effet de composition.** Depuis 2018 : 5 places, dont 3 face aux stables.
- **Sciences, 2006-2025** : rang quasi stable (25e puis 27e), 1 place face aux stables.

**Mais le score, lui, baisse vraiment.** Comparé à la moyenne des 23 pays de l'OCDE présents depuis le début (« OCDE-23 » de l'OCDE) [S1] :

| Domaine | France | OCDE-23 | Écart de baisse |
|---|---|---|---|
| Maths 2003-2025 | 510,8 → 457,7 (**-53**) | 502,1 → 469,4 (-33) | France -20 de plus |
| Lecture 2000-2025 | 504,7 → 456,3 (**-48**) | 499,5 → 465,8 (-34) | France -14 de plus |
| Sciences 2006-2025 | 495,2 → 483,4 (-12) | 502,7 → 485,9 (-17) | France -5 de moins |
| Maths 2018-2025 | 495,4 → 457,7 (-38) | 496,4 → 469,4 (-27) | France -11 de plus |

**Solidité.** Décomposition sur le groupe stable : **établi** (données OCDE, arithmétique). Rangs ponctuels : fragiles (fourchettes larges, par exemple 25e-38e en maths en 2025). Le complément manuel des participants sortis : **à vérifier**.

---

## 3. Score attendu : niveau et progression

**Méthode.** Régression entre pays (MCO, erreurs robustes), sur 81 à 83 pays (entités infranationales exclues). Variables : log du PIB par habitant en PPA 2024 [S7], ESCS moyen des élèves [S2, I.B1.2b.1], variantes avec l'indice de couverture, la dépense par élève du secondaire [S7] et une moyenne corrigée de la couverture. Fichiers : `score_attendu_modeles.json`, `score_attendu_residus.csv`.

**Niveau 2025 (écart = observé - attendu ; rang de l'écart parmi les pays).**

| Modèle | R² | France sci / lec / maths | Turquie sci / lec / maths |
|---|---|---|---|
| A : PIB | 0,64-0,67 | +13 / +8 / +3 (31e, 38e, 39e sur 82-83) | +46 / +47 / +30 (6e, 6e, 11e) |
| B : PIB + ESCS | 0,64-0,67 | +13 / +8 / +5 | +50 / +45 / +41 (6e partout) |
| C : B + couverture | idem | +13 / +8 / +5 | +51 / +46 / +41 |
| D : B + dépense par élève (57 pays) | 0,64-0,71 | +9 / +4 / 0 | +65 / +56 / +58 |
| E : B, moyenne corrigée P25 | 0,66-0,69 | +13 / +8 / +5 | +46 / +41 / +34 (7e-8e) |
| F : B, moyenne corrigée P10 | 0,66-0,69 | +13 / +8 / +5 | +41 / +37 / +29 (7e-10e) |

- **France : conforme à l'attendu**, légèrement au-dessus, au milieu du classement des écarts. Ni « sous-performance » ni réussite au regard de sa richesse et du profil social de ses élèves.
- **Turquie : nettement au-dessus de l'attendu (+30 à +65 points), et cela tient même après correction de la couverture** (+29 à +46). C'est le résultat le plus robuste sur la Turquie : sa surperformance relative à son revenu n'est pas un artefact de couverture ; c'est son **dépassement de la France** qui en est en partie un.

**Progression (pour neutraliser l'effet Covid et le niveau de départ).** Variation 2022-2025 et 2018-2025 expliquée par le score de départ (rattrapage), le PIB et l'ESCS.

| Période | France sci / lec / maths : observé (attendu) | Rang de l'écart France | Turquie : écart |
|---|---|---|---|
| 2022-2025 (70-71 pays) | -4 (-4) / -18 (-13) / -16 (-9) | 30e, 48e, 50e | +25 / +25 / +16 (rangs 2e à 6e) |
| 2018-2025 (70-71 pays) | -10 (-4) / -36 (-24) / -38 (-25) | 44e, 52e, **60e sur 71** | +22 / +20 / +23 (rangs 5e à 9e) |

- **La France baisse plus qu'attendu en lecture et en maths**, surtout sur 2018-2025 (-12 et -13 points de plus que prévu). En sciences, elle suit l'attendu.
- R² faibles (0,19 à 0,42) : la progression dépend peu de ces variables.

**Solidité.** Niveau France « conforme à l'attendu » : **probable** (stable dans les six variantes). Surperformance turque : **probable** (robuste aux variantes, mais modèle frustre). Baisse française plus forte qu'attendu depuis 2018 en maths et lecture : **probable**. Variante dépense : **fragile** (données Banque mondiale de 2015-2018 seulement, 57 pays ; PIB et ESCS très corrélés). Aucune lecture causale.

---

## 4. Ce que les données confirment dans la critique

**Origine sociale (2025, 37 pays de l'OCDE ayant l'ESCS) [S2, I.B1.2b.2 à 4].**

| Domaine | France : R² (rang OCDE) | Pente par unité d'ESCS (rang) | Écart quart favorisé - défavorisé (rang) | OCDE |
|---|---|---|---|---|
| Sciences | 13,5 % (11e) | 39 (11e) | 100 (7e) | R² 11,6 %, pente 36, écart 85 |
| Lecture | 10,8 % (7e) | 36 (10e) | 91 (7e) | 9,2 %, 32, 77 |
| Maths | 14,8 % (9e) | 37 (13e) | 95 (11e) | 12,0 %, 35, 83 |

- **Confirmé** : la France reste dans le premier tiers des pays de l'OCDE où l'origine sociale pèse le plus. **Pas « la plus inégalitaire »** : l'Allemagne fait nettement plus (R² 16 à 19 %, écart 112 à 125).
- **Nouveau en 2025, et à double tranchant** : le poids de l'origine sociale a nettement baissé en France (R² en sciences 20,2 % en 2022, 13,5 % en 2025 ; baisse de 6,7 points, erreur type 1,7) [S2, I.B1.2b.25 à 27], plus que la moyenne OCDE-35 (-3 points). **Mais l'écart se réduit surtout par le haut** : en maths, le quart le plus favorisé passe de 552 (2015) à 514 (2025), -38 points, contre -22 pour le quart le plus défavorisé (442 → 420) [S2, I.B1.2b.24]. Ce n'est pas une démocratisation par le bas.

**Élèves faibles (sous le niveau 2) et très performants (niveau 5 ou plus) [S1, I.B1.2a.33 à 35].**

| | France 2003 (2000 en lecture) | France 2025 | OCDE-23 au départ | OCDE-23 2025 |
|---|---|---|---|---|
| Maths, faibles | 16,6 % | **35,7 %** | 20,7 % | 32,2 % |
| Maths, très performants | 15,1 % | **5,2 %** | 15,0 % | 8,5 % |
| Lecture, faibles | 15,2 % | 32,7 % | 18,1 % | 29,5 % |
| Lecture, très performants | 8,5 % | 4,5 % | 9,4 % | 6,1 % |
| Sciences (depuis 2006), faibles | 21,2 % | 25,8 % | 18,1 % | 24,4 % |
| Sciences, très performants | 8,0 % | 6,7 % | 9,2 % | 7,7 % |

- **Confirmé, et c'est le point le plus dur pour la France** : l'effondrement des très bons élèves en maths (de 15 % à 5 %, alors que la France était au niveau de l'OCDE en 2003) et le doublement des élèves faibles. En 2025 la France est proche de la moyenne OCDE pour les faibles (35,7 % contre 34,9 %), mais nettement en dessous pour les très bons (5,2 % contre 7,8 %).
- **Dispersion** : écart type en lecture de 105 (OCDE-23 : 102), en sciences de 104 (99), en maths de 93 (94) [S1, I.B1.2a.42 à 44]. La France est dispersée en lecture et sciences, pas en maths.

**Solidité.** Établi (tableaux OCDE, écarts significatifs). La baisse du R² en 2025 : **probable mais à vérifier** dans le rapport (changement éventuel de construction de l'indice ESCS en 2025, que je n'ai pas pu lire).

---

## 5. La Turquie : ce que disent les données

**Progression.** Sciences 424 (2006) → 494 (2025), lecture 441 (2003) → 472, maths 423 (2003) → 462 [S1, I.B1.2a.36 à 38]. Hausse 2022-2025 : +18, +16, +8. Trajectoire non linéaire : **creux en 2015** (sciences 425, maths 420), puis rebond ; le choix de l'année de départ change beaucoup le récit (depuis 2012 : +31 en sciences seulement).

**Couverture.** CI3 : 0,36 (2003), 0,47 (2006), 0,57 (2009), 0,68 (2012), 0,70 (2015), 0,73 (2018), 0,74 (2022), **0,72 (2025)** [S3]. Deux constats :
- Sur vingt ans, **la couverture a doublé en même temps que les scores montaient**. Intégrer des jeunes jusque-là hors école tire normalement la moyenne vers le bas : la hausse de long terme n'est donc pas un artefact de couverture, plutôt l'inverse.
- Entre 2022 et 2025 la couverture est stable (et même en léger recul) : **le saut récent n'est pas dû à la couverture**, mais le **niveau** reste surévalué par rapport à la France (cf. section 1).

**Dispersion et origine sociale.** L'écart type a augmenté (sciences 79 en 2015, 94,5 en 2025), le haut progressant plus que le bas (sciences, 90e centile +86 points depuis 2015, 10e centile +46) [S1, I.B1.2a.39 et 42]. L'écart entre quarts sociaux s'est creusé (sciences 59 en 2015, 81 en 2025 ; maths 59 → 96) [S2, I.B1.2b.22 à 24], alors qu'il se resserrait dans l'OCDE. Part d'élèves très performants en sciences : 0,3 % (2015) → 7,4 % (2025), au niveau de la moyenne OCDE ; élèves faibles 44,5 % → 19,5 % (meilleur que la France, 25,8 %) [S1, I.B1.2a.33]. Absentéisme : 53 % des élèves turcs ont manqué au moins une journée entière dans les deux semaines précédant le test, contre 22 % en moyenne OCDE (rapport cité par bianet).

**L'hypothèse « alignement de l'examen national LGS sur le format PISA ».** **Non testable avec PISA seul** : PISA n'observe ni la préparation à l'examen ni les programmes. Ce que permet TIMSS (IEA) :
- TIMSS teste des **classes entières** (4e et 8e année), avec une scolarisation quasi complète à ces âges : le biais de couverture est bien plus faible qu'à 15 ans.
- Turquie, 8e année : maths 458 (2015) → 496 (2019) → 509 (2023) ; sciences 493 → 515 → 530. 4e année : maths 483 → 523 → 553 ; sciences 483 → 526 → 570 [S8]. France 2023 : 8e année maths 479, sciences 486 ; 4e année maths 484 [S8].
- **Ce que la triangulation apporte** : la progression turque est confirmée par un test indépendant, sur des échantillons presque exhaustifs, et l'avance sur la France à 13-14 ans (30 points en maths, 44 en sciences sur l'échelle TIMSS) n'est pas un effet de couverture. Les gains sont aussi forts **en 4e année, loin de l'examen LGS** (fin de 8e année) : cela ne réfute pas l'hypothèse d'une culture de l'examen, mais montre que la hausse ne se limite pas aux élèves qui préparent le LGS. TIMSS ne permet pas non plus d'isoler un effet de format.
- PIRLS (lecture, 4e année) : la Turquie n'aurait participé qu'en 2001 et 2021 (de mémoire, à vérifier sur le site de l'IEA), trop peu pour une tendance.

**Solidité.** Progression et couverture : établi. Effet de la couverture sur le saut 2022-2025 : établi (couverture stable). Triangulation TIMSS : probable (échelles différentes, test de programme et non de compétences ; valeurs TIMSS 2019 et 2015 issues du MEB, **à recouper** dans le rapport international IEA). Causes : non établies, et non établissables avec ces données.

---

## 6. Pour un dossier Outsiders

### Cartes-questions possibles (vrai / faux)

1. **« La Turquie a dépassé la France dans les trois matières. »** *Vrai en sciences et en lecture, pas en maths* (écart non significatif). Et à couverture égale, la France repasse devant en maths et revient au contact ailleurs : 28 % des jeunes Turcs de 15 ans ne sont pas dans l'échantillon, contre 12 % des jeunes Français. Chiffre cliquable : CI3 0,72 contre 0,88.
2. **« La France est sous la moyenne de l'OCDE. »** *Faux en 2025* : écart non significatif dans les trois domaines. Mais la moyenne elle-même a reculé.
3. **« La France dégringole dans le classement. »** *À moitié vrai* : en maths, 18 places perdues depuis 2003, dont 8 dues à l'arrivée de nouveaux pays ; en lecture, les deux tiers de la chute sont un effet de composition ; en sciences, le rang est stable. Depuis 2018 en revanche, le recul est réel.
4. **« Tout le monde baisse, la France suit le mouvement. »** *Faux en maths et en lecture* : -53 points en maths depuis 2003, contre -33 pour les pays de l'OCDE présents depuis le début ; depuis 2018, baisse plus forte qu'attendu au vu du niveau de départ. *Vrai en sciences.*
5. **« Vu sa richesse, la France devrait faire mieux. »** *Faux pour le niveau* : la France est à son score attendu. *Vrai pour la trajectoire.*
6. **« L'école française est la plus inégalitaire de l'OCDE. »** *Faux, mais dans le premier tiers* ; l'Allemagne fait plus. Angle mort : l'écart social s'est réduit en 2025 parce que **les enfants favorisés ont reculé**, pas parce que les défavorisés ont progressé.
7. **« La France ne produit plus d'élites en maths. »** *Vrai* : 15 % de très bons élèves en 2003, 5 % en 2025 (OCDE-23 : 8,5 %).
8. **« Le miracle turc n'est qu'un artefact. »** *Faux* : la surperformance turque au regard de son revenu tient après correction de la couverture, et TIMSS la confirme à 10 et 14 ans. Ce qui est un artefact, c'est surtout le dépassement de la France.

### Graphiques

- **Pente « rang brut / rang à couverture égale »** (dot plot, 38 pays de l'OCDE, France et Turquie en couleur), avec la fourchette de rang.
- **Rang de la France parmi tous les participants contre parmi le groupe stable** (deux courbes par domaine depuis 2000), avec la barre empilée « stables au-dessus / nouveaux au-dessus ».
- **Nuage de pronostic entre pays** (score contre PIB par habitant en PPA, droite de régression), dans l'esprit du nuage déjà présent sur `/international` : la France sur la droite, la Turquie très au-dessus.
- **Trajectoires France contre OCDE-23** depuis 2000 (score moyen, et part de très bons élèves en maths).
- **Quarts sociaux en France 2015-2025** : quatre lignes, le quart favorisé qui descend.
- **Turquie : couverture et score sur la même frise** (CI3 de 0,36 à 0,72, sciences de 424 à 494).

### Ce qu'il ne faut pas affirmer

- Aucune cause : ni le LGS, ni le nouveau programme turc, ni les réformes françaises, ni le Covid, ni le téléphone portable. Les données décrivent, elles n'expliquent pas.
- Pas de rang au singulier sans sa fourchette (la France est « entre la 25e et la 38e place » en maths).
- Pas de classement corrigé présenté comme une mesure : c'est une hypothèse, à afficher avec ses variantes.
- Pas de comparaison serrée avec les pays sous astérisque (Norvège, Pays-Bas, États-Unis, Canada, Nouvelle-Zélande, Albanie).
- Pas de chiffre de dépense par élève sans dire qu'il date de 2015-2018.
- Le complément manuel des participants sortis (section 2) et les valeurs TIMSS 2015-2019 sont à recouper avant publication.
- Ne pas présenter la baisse du poids de l'origine sociale comme un progrès sans montrer qu'elle vient du recul des plus favorisés, et sans avoir vérifié qu'aucun changement de méthode de l'indice ESCS en 2025 n'y contribue.

### Reste à faire avant un dossier

1. Lire la note pays France et le chapitre « méthode » du rapport (accès manuel, le site OCDE bloque les robots).
2. Vérifier la comparabilité de l'ESCS 2025 avec 2022.
3. Recouper les participants sortis (Liechtenstein, Shanghai, Viet Nam, B-S-J-G, Russie) dans les volumes I de 2009, 2012 et 2015.
4. Remplacer la dépense Banque mondiale par la dépense cumulée par élève de 6 à 15 ans publiée par l'OCDE si elle figure dans le volume 2025.
