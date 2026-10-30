# 7. La France décroche dans PISA ?
> Carte `pisa` · verdict « Vrai, mais » · dossier /international/pisa · fiche préparée le 30/10/2026

Rappel de la décision de l'usager : le dossier porte sur la France seule, comparée à la moyenne de l'OCDE et à la moyenne « OCDE-23 » ; un pays déjà discuté n'est ni nommé ni mis en avant. Cette fiche ne nomme aucun autre pays.

## Ce qu'affiche la carte

- **Rubrique** : École ; unité « Pays » ; couleur `#6366F1`.
- **Question** : « La France décroche dans PISA ? »
- **Verdict** : `vraiMais`.
- **Chiffre** : **−53 / −33**, « points en maths de 2003 à 2025 : la France, puis la moyenne des 23 pays de l'OCDE présents depuis le début ».
- **Texte** : « La France baisse significativement plus que ces pays, en maths comme en lecture, et l'écart s'est creusé depuis 2018. Mais en 2025 son score ne se distingue pas significativement de la moyenne de l'OCDE, il correspond à ce que laissent attendre sa richesse et le profil social de ses élèves, et une partie de la chute au classement tient à l'arrivée de nouveaux participants. »
- **Source citée** : « OCDE, PISA 2025 Results (Volume I), tableaux de tendance », lien https://stat.link/mrq53f
- **Lien** : « Ouvrir le dossier PISA » vers `/international/pisa`.

## Ce que dit le dossier

Page `frontend/src/pages/international/Pisa.jsx` ; description complète dans `docs/international/pisa_2025_dossier.md`.

- **Cinq cartes vrai / faux en tête** (calculées depuis le JSON) : « La France s'effondre dans PISA ? » (Vrai, mais, −53 en maths depuis 2003, −48 en lecture depuis 2000) ; « Tout le monde baisse, la France suit le mouvement ? » (Pas partout, −53 / −33, carte reprise sur l'accueil) ; « La France dégringole au classement ? » (Vrai, mais, 34ᵉ sur 90 en maths, fourchette 25ᵉ-38ᵉ, contre 15ᵉ sur 36 en 2003) ; « Vu sa richesse, la France devrait faire mieux ? » (Faux, +5 points sur l'attendu en maths) ; « La France perd ses meilleurs élèves en maths ? » (Vrai, mais, 15 % puis 5 % au niveau 5 ou plus).
- **Le niveau** : score 2025 contre la moyenne OCDE (maths 457,7 contre 463,0, écart −5,4, erreur type 3,0, non significatif ; lecture −4,6 ; sciences +1,5) ; courbe France / OCDE-23 ; tableau des évolutions depuis la première vague, 2015, 2018 et 2022, avec significativité.
- **Le rang** : parmi tous les participants, les 38 pays de l'OCDE et l'OCDE-23, avec fourchette calculée par Outsiders ; décomposition des places perdues (19 en maths depuis 2003 : 7 face à l'OCDE-23, 5 face à d'autres participants déjà présents, 7 face à des nouveaux venus).
- **Score attendu** : nuage observé / attendu (PIB par habitant en log + ESCS moyen, 81 pays, R² 0,67 en maths) ; France +4,8 (résidu studentisé 0,15). Encadré : depuis 2018, −37,8 observé pour −24,8 attendu (écart −12,9, 60ᵉ sur 71, dans la dispersion habituelle).
- **Ce que la critique dit de vrai** : écart entre quarts sociaux en maths 94,5 points contre 82,9 (significatif, 11ᵉ plus fort sur 37) ; R² 14,8 % contre 12,0 % ; pente non significativement différente ; aucune comparaison de l'ESCS dans le temps (méthode changée en 2025).
- **Couverture** : indice de couverture 3 de la France 0,88 en 2025, au niveau de la médiane des participants.
- **Méthode et limites** : compétences à 15 ans, pas l'école ; aucune cause ; valeurs plausibles et erreur de lien.

## D'où viennent les chiffres

Chaîne : classeurs Excel des annexes OCDE (téléchargés par `stat.link`, en cache dans `python/data/international/pisa/raw/` : `mrq53f.xlsx`, `k68msa.xlsx`, `pe3lsg.xlsx`, `wh9d4z.xlsx`) + API Banque mondiale (`wb_NY.GDP.PCAP.PP.KD.json`) -> `python/tools/explore_pisa.py` (lecteurs, listes de pays, CSV intermédiaires dans `python/data/international/pisa/*.csv`) -> `python/tools/build_pisa.py` -> `frontend/public/data/showcases/pisa.json` (32 Ko) -> `Pisa.jsx`. La carte de l'accueil recopie en dur le chiffre de la carte 2 du dossier.

Rattachement :

| Chiffre de la carte | Valeur dans `pisa.json` | Origine |
|---|---|---|
| −53 | `evolutions.mat[0].fr.d` = −53,1 (erreur type 6,89, significatif) | tableau I.B1.2a.38, colonne « Change … PISA 2025 − PISA 2003 » (511 puis 458) |
| −33 | `evolutions.mat[0].ocde23.d` = −32,7 (erreur type 5,73) | moyenne des 23 pays reconstituée et contrôlée contre la ligne « OECD average-23 » |
| « baisse significativement plus » | `evolutions.mat[0].ecart` = −20,4, erreur type 3,99 | erreur de lien supposée commune, erreurs d'échantillonnage combinées |
| « en lecture » | `evolutions.rea[0]` : −48,4 contre −33,7, écart −14,7 (significatif) | I.B1.2a.37, depuis 2000 |
| « l'écart s'est creusé depuis 2018 » | maths : −37,8 contre −27,0, écart −10,8 (significatif) ; lecture : −36,3 contre −27,0, écart −9,3 (significatif) | `evolutions.*[2]` |
| « ne se distingue pas de la moyenne OCDE » | `niveau.mat.ecart_ocde` = −5,4, erreur type 3,03 | I.B1.2a.3 |
| « ce que laissent attendre sa richesse et le profil social » | `attendu.mat.france.ecart` = +4,8 | régression MCO PIB + ESCS 2025 |
| « arrivée de nouveaux participants » | `decomposition.mat.long.dont_nouveaux` = 7 sur 19 places | rangs comptés dans les tableaux de tendance |

## Les jeux de données

### OCDE, PISA 2025 Results (Volume I), annexe B1, tableaux I.B1.2a (performance)
- **Producteur** : OCDE ; publication du 8 septembre 2026.
- **Code** : StatLink `mrq53f` (classeur de 50 tableaux).
- **Millésime** : PISA 2025 (dernier cycle ; le suivant est PISA 2029).
- **Page / téléchargement** : https://stat.link/mrq53f (redirige vers le classeur xlsx) ; rapport : https://www.oecd.org/fr/topics/sub-issues/pisa.html (adresse à vérifier).
- **Géographie** : 91 participants (pays et économies), moyenne OCDE, OCDE total, moyennes « OECD average-23 » et autres groupes stables.

| tableau (colonnes) | sens / modalités | utilisé ? |
|---|---|---|
| I.B1.2a.1 à 3 (moyenne, écart type, centiles 10, 25, 50, 75, 90, écart P90−P10) | score 2025 par domaine | oui : moyenne et erreur type (niveau, rangs). Non : dispersion et centiles |
| I.B1.2a.4 | **pensée informatique / résolution de problèmes computationnels**, nouveau domaine 2025 | non : France 497,5 contre 500,0 pour l'OCDE |
| I.B1.2a.5 à 9 | sous-échelles (sciences : expliquer, concevoir, évaluer ; pensée informatique : modéliser, programmer) | non |
| I.B1.2a.10 à 18 | part d'élèves par niveau (sous 1c, 1c, 1b, 1a, 2, 3, 4, 5, 6) | non directement (le dossier prend les tableaux de tendance 33 à 35) |
| I.B1.2a.19 à 24 | corrélations entre domaines, recouvrement des élèves faibles ou très performants | non |
| I.B1.2a.25 à 32 | variance totale, **entre établissements et au sein des établissements**, indice d'inclusion scolaire | non : en maths, variance entre établissements 3 265 en France contre 2 869 en moyenne OCDE ; indice d'inclusion 60,8 % contre 67,7 % |
| I.B1.2a.33 à 35 | élèves faibles (sous le niveau 2) et très performants (5 ou plus), par vague | oui : courbes et carte 5 |
| I.B1.2a.36 à 38 | moyenne par vague, évolution entre 2025 et chaque vague, tendance décennale, tendance curvilinéaire | oui : trajectoires, évolutions, rangs historiques |
| I.B1.2a.39 à 41 | **centiles (10, 25, 50, 75, 90) par vague** | non : en maths, P10 389 puis 334 (−55), P90 628 puis 580 (−48) de 2003 à 2025 |
| I.B1.2a.42 à 44 | variance par vague | non |
| I.B1.2a.45 à 50 | mêmes indicateurs rapportés à **tous les jeunes de 15 ans** (non scolarisés et exclus comptés), 2015-2025 | non |

### OCDE, PISA 2025 Results (Volume I), tableaux I.B1.2b (statut socio-économique)
- **Code** : StatLink `k68msa` (38 tableaux). **Lien** : https://stat.link/k68msa

| tableau | sens / modalités | utilisé ? |
|---|---|---|
| I.B1.2b.1 | ESCS moyen, écart type, moyenne par quart | oui : ESCS moyen (score attendu) |
| I.B1.2b.2 à 5 | R², pente, score par quart national d'ESCS, écart haut − bas, par domaine (dont pensée informatique) | oui : R², pente, quarts, écart (sauf pensée informatique) |
| I.B1.2b.6 à 13 | parts et scores par **déciles et quarts internationaux** d'ESCS | non |
| I.B1.2b.14 à 16 | élèves faibles et très performants selon l'ESCS | non |
| I.B1.2b.17 à 19 | variance de l'ESCS entre et dans les établissements (ségrégation sociale) | non |
| I.B1.2b.20 et 21 | **privation** (matérielle, alimentaire…) selon le quart d'ESCS | non ; la France n'a pas de valeur dans I.B1.2b.20 |
| I.B1.2b.22 à 33 | tendances 2015-2025 par quart d'ESCS | non, volontairement (méthode de l'ESCS changée) |
| I.B1.2b.34 et 35 | part d'élèves sans ESCS ou sans biens du foyer | oui, dans la vérification (2,7 % en 2022, 8,6 % en 2025) |
| I.B1.2b.36 à 38 | scores par quart de **biens du foyer**, 2015-2025 | non |

### OCDE, PISA 2025 Results (Volume I), annexe A2 (couverture)
- **Code** : StatLink `pe3lsg`. **Lien** : https://stat.link/pe3lsg

| tableau | sens / modalités | utilisé ? |
|---|---|---|
| I.A2.1 | par vague 2003-2025 : population de 15 ans, scolarisés en 7e année ou plus, effectif pondéré, indice de couverture 3 | oui : encadré couverture |
| I.A2.2 | niveau CITE modal des élèves de 15 ans | non |
| I.A2.3 | répartition des élèves par année d'études (7e à 12e) | non : utile pour la France (part d'élèves en retard au collège) |

### OCDE, PISA 2022 Results (Volume I), tableaux I.B1.5
- **Code** : StatLink `wh9d4z` (50 tableaux). **Lien** : https://stat.link/wh9d4z
- **Utilisé** : I.B1.5.4 à 6 (moyennes par vague) pour les participants absents en 2025.
- **Non utilisés** : I.B1.5.19 à 37 (quarts sociaux 2012-2022, distributions des élèves défavorisés et favorisés) ; **I.B1.5.38 à 48 (garçons, filles, écarts de sexe 2012-2022)**.

### Banque mondiale, PIB par habitant en PPA
- **Code** : `NY.GDP.PCAP.PP.KD` (dollars internationaux constants 2021), année 2024. **Lien** : https://data.worldbank.org/indicator/NY.GDP.PCAP.PP.KD ; API : https://api.worldbank.org/v2/country/all/indicator/NY.GDP.PCAP.PP.KD?format=json
- **Utilisé** : variable du score attendu. Aussi en cache, non utilisé dans le dossier final : `SE.XPD.SECO.PC.ZS` (dépense par élève du secondaire, en % du PIB par habitant).

## Ce qu'on n'exploite pas encore

- **Le choix de 2003 comme point de départ** : la France était en 2003 à 511, au-dessus de l'OCDE-23 (502). De 2006 à 2018, elle suit la moyenne des 23 à quelques points près (−5, −5, −4, −3, −1) ; l'écart s'ouvre après 2018 (−12 en 2025). En lecture, même dessin : à égalité en 2018 (492,6 contre 492,8), −9,5 en 2025. Le « décrochage relatif » est donc d'abord un phénomène d'après 2018 ; le chiffre −53 / −33 mélange une chute 2003-2006 et ce décrochage récent.
- **Les centiles par vague** (I.B1.2a.41) : la baisse touche tout le spectre (P10 −55, P90 −48 en maths depuis 2003). Répond à « qui décroche ? » sans passer par l'ESCS.
- **La variance entre établissements** (I.B1.2a.29) : en France, une part plus forte des écarts de score se joue entre établissements que dans la moyenne de l'OCDE (indice d'inclusion 60,8 % contre 67,7 %). Lien direct avec le dossier École et la ségrégation scolaire. Prudence : à 15 ans, les élèves français sont répartis entre collège et lycée, ce qui gonfle mécaniquement la part « entre établissements » (le tableau 29 applique une restriction au niveau CITE modal, le 30 non : comparer les deux).
- **La pensée informatique** (I.B1.2a.4) : nouveau domaine 2025, France 497,5 contre 500 en moyenne OCDE ; pas de tendance possible, mais montre un domaine où la France est dans la moyenne.
- **Les jeunes de 15 ans dans leur ensemble** (I.B1.2a.45 à 50) : neutralise les écarts de couverture entre pays sans hypothèse maison.
- **L'année d'études** (I.A2.3) : part des élèves de 15 ans encore au collège, en lien avec le redoublement.
- **Les écarts filles / garçons** : absents des classeurs 2025 en cache (à chercher dans un autre volume ou dans la base de données PISA 2025) ; tendance 2012-2022 disponible dans `wh9d4z` (I.B1.5.38 à 48).

## Autres sources possibles

- **TIMSS 2023** (IEA, résultats publiés en décembre 2024) : mathématiques et sciences en CM1 et en 4e ; la France y figurait parmi les derniers pays européens en CM1 (à vérifier dans la note DEPP de décembre 2024). Mesure scolaire (programmes), à l'inverse de PISA (compétences à 15 ans). https://timss2023.org ; note DEPP correspondante.
- **PIRLS 2021** (IEA) : compréhension de l'écrit en CM1, tendances depuis 2001. https://pirls2021.org
- **PIAAC, Enquête sur les compétences des adultes, cycle 2** (OCDE, résultats de décembre 2024) : littératie et numératie des 16-65 ans ; permet de vérifier si le décrochage se retrouve chez les jeunes adultes.
- **DEPP, évaluations nationales** (évaluations repères CP, CE1, 6e, 4e ; cycle CEDRE) et notes d'information PISA 2025 (NI 2026-40, déjà citée en contrôle) : séries françaises sur des échantillons plus grands.
- **Base de données PISA 2025** (microdonnées, OCDE) : permettrait des calculs maison (sexe, statut migratoire, secteur public ou privé), au prix d'un traitement des valeurs plausibles et des poids répliqués. À vérifier : date de mise en ligne.
- **PISA Data Explorer / OECD Data Explorer** : interface de l'OCDE pour extraire des tableaux à la demande.

## Points de relecture

- **Formulation** : « décroche » est juste depuis 2018 (écart significatif en maths et en lecture) ; « baisse significativement plus que ces pays » est vrai depuis 2003 mais dépend du point de départ (2003, année haute pour la France). Chiffre peut-être plus parlant et moins dépendant de l'année de base : « −38 contre −27 en maths depuis 2018 » ou « à égalité avec ces pays en 2018, 12 points derrière en 2025 ».
- **Depuis 2022** : l'écart France / OCDE-23 n'est pas significatif (maths −5,4, lecture −1,4) : le décrochage relatif s'est produit entre 2018 et 2022 surtout. Ne pas laisser entendre qu'il s'accélère.
- **Sciences** : la carte ne parle que de maths et lecture ; en sciences, la France ne baisse pas significativement depuis 2006 et pas plus que l'OCDE-23. À garder en tête si la carte est reprise ailleurs.
- **« Ce que laissent attendre sa richesse et le profil social »** : le modèle est le nôtre (PIB + ESCS 2025, MCO) ; l'ESCS 2025 a changé de méthode et la part d'élèves français sans ESCS a triplé (8,6 %). Le résidu (+4,8) est faible devant la dispersion (30,6) : formulation correcte (« correspond »), sans plus.
- **Nouveaux participants** : 7 places sur 19 ; les rangs historiques ne comptent pas les participants sortis (réserve écrite sur la page). La fourchette de rang est la nôtre (tests deux à deux), pas celle de l'OCDE.
- **Source** : le lien `stat.link/mrq53f` télécharge un classeur Excel ; pour un lecteur, un lien vers la page du rapport serait plus lisible.
- **Unité « Pays »** : la carte est rangée avec les comparaisons européennes ; PISA compare 91 participants et des moyennes de l'OCDE, à dire si le kicker est revu.
- **Décision de l'usager** : aucun pays nommé sur la carte ; vérifié.
