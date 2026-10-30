# L'élite sportive : qui devient international, et d'où vient-il ? Note d'exploration

> Exploration du 29 octobre 2026. Rien n'est publié sur le site : cette note sert à décider ce qui mérite une page du dossier « Sport ».
> Script : `python/tools/explore_sport_elite.py` (étapes `collecte`, `idp`, `territoires`, relançable).
> Tables agrégées, sans aucun nom de personne : `python/data/sport/sorties/elite_*.csv`.
> Données nominatives brutes : `python/data/sport/elite/` (exclues de tout versionnement par un `.gitignore` local ; ne jamais les copier dans `frontend/` ni dans une note).
> Note mère : `docs/sport/exploration_injep.md` (licences INJEP), en particulier la section (f).

---

## (a) Les données

### Sources et requêtes

1. **Wikidata** (licence CC0), service SPARQL, requêtes en lots de 200 à 300 identifiants avec un User-Agent descriptif :
   - appartenance (P54) aux huit équipes A : football masculine (Q47774) et féminine (Q751670), rugby à XV masculine (Q518116) et féminine (Q952932), basket-ball masculine (Q499328) et féminine (Q1342224), handball masculine (Q457107) et féminine (Q1003357), avec les qualificatifs début (P580), fin (P582) et sélections (P1350) ;
   - pour chaque personne : nature humaine (P31 = Q5), sexe (P21), date (P569) et lieu (P19) de naissance, code commune Insee du lieu (P374), pays du lieu (P17), nom de famille (P734), prénoms (P735) ; pour les lieux sans code Insee, remontée des entités englobantes (P131) jusqu'à un code de département (P2586).
2. **Wikipédia en français** (CC BY-SA), API MediaWiki, pour l'appartenance seulement : catégories « Footballeur international français », « Footballeuse internationale française », « Joueur international français de rugby à XV », etc., et trois listes de référence (« Liste des footballeurs internationaux français », « Liste des sélectionnés en équipe de France de rugby à XV », « Liste des joueuses de l'équipe de France féminine de football »). Quand une liste existe, **elle fait foi** : les appartenances Wikidata ou catégories absentes de la liste sont retirées (14 en football masculin, 14 en football féminin, 6 en rugby : sélections B, amateurs, olympiques ou erreurs).
3. **Délégation de Paris 2024** : la piste prévue (P1344 vers « France aux Jeux olympiques d'été de 2024 », Q114244785) est **vide** dans Wikidata, et P1344 vers une épreuve de 2024 ne donne que 158 Français. On part donc des liens de l'article Wikipédia « France aux Jeux olympiques d'été de 2024 », filtrés sur les humains dont le pays sportif (P1532) est la France (à défaut, la nationalité), nés en 1955 ou après.

### Effectifs et complétude (`elite_effectifs.csv`, `elite_completude_listes.csv`)

| Équipe | Personnes | Référence | Couverture | Département de naissance connu | Né hors de France | Lieu inconnu |
|---|---:|---|---:|---:|---:|---:|
| Football, hommes | 956 | 956 (liste Wikipédia) | 100 % | 814 | 138 | 1 |
| Football, femmes | 233 | 336 (liste Wikipédia) | 69 % | 219 | 5 | 8 |
| Rugby à XV, hommes | 1 104 | 1 214 (liste Wikipédia) | 91 % | 1 002 | 58 | 29 |
| Rugby à XV, femmes | 182 | aucune | ? | 82 | 3 | 87 |
| Basket-ball, hommes | 319 | aucune | ? | 269 | 34 | 15 |
| Basket-ball, femmes | 168 | aucune | ? | 144 | 15 | 9 |
| Handball, hommes | 171 | aucune | ? | 142 | 12 | 13 |
| Handball, femmes | 149 | aucune | ? | 124 | 12 | 12 |
| JO Paris 2024 (tous sports) | 545 (296 H, 249 F) | 572 athlètes (CNOSF) | 95 % | 467 | 40 | 37 |

Ce qui manque, et où :

- **Football masculin : complet** contre la liste Wikipédia (956 sur 956, tous avec un article et un élément Wikidata). Wikidata seul (P54) en donnait 949 justes et 13 de trop. La liste n'a pas été recoupée directement avec la Fédération française de football (pages fff.fr refusées au robot).
- **Rugby à XV masculin : 91 %**. Les 110 manquants sont des joueurs sans article, presque tous **sélectionnés avant 1941** (couverture de 66 à 71 % pour les premières sélections de 1901 à 1940, 91 % pour 1941-1950, 100 % depuis 1951).
- **Football féminin : 69 %**. Les manquantes sont les **générations nées de 1951 à 1980** (couverture de 42 à 61 % par décennie de naissance), complètes depuis 1981.
- **Basket-ball et handball : aucune liste exhaustive publique trouvée** (le guide de presse de la FFBB, qui contient une rubrique « Les internationaux », est refusé au robot). Les catégories Wikipédia donnent un plancher ; leur biais attendu est le même qu'ailleurs : les anciens peu sélectionnés manquent. Wikidata seul est inutilisable (13 basketteurs internationaux sur plusieurs centaines).
- **Rugby féminin** : 182 joueuses, mais **lieu de naissance inconnu pour 87** : inutilisable pour la question 2.
- **JO 2024** : 545 pour 572, mais la méthode (liens d'un article) peut garder quelques non-athlètes (entraîneurs ou dirigeants français nés après 1955) et perdre des athlètes sans article.

### Limites générales

- **Biais de notoriété** : Wikipédia et Wikidata couvrent mieux les joueurs récents et les plus sélectionnés.
- **Erreurs de lieu ou de date** dans Wikidata : non contrôlées une à une (contrôle par échantillon à faire, voir e).
- **Nom de famille** : P734 pour 79 % des personnes ; sinon libellé moins le prénom (19 %) ou dernier mot (2 %).
- **Lieu de naissance = lieu d'état civil** (souvent la maternité), pas le lieu où l'on a grandi.

---

## (b) Question 1 : la diversité des noms par sport et dans le temps

### Méthode et garde-fous

- **Indicateur** : IDP (Kheddache et L'Horty, 2023), un nom compte « diversité » s'il est absent des naissances en France avant 1950 ou multiplié par plus de 15 après. Le drapeau est **recalculé** à partir du fichier Insee des noms de famille par période de naissance 1891-2000 (`noms2008nat_txt.txt`), avec la même normalisation que le site : **0 différence** avec `surnames.tsv` sur 218 676 noms.
- **Garde-fou 1 : comparaison à la même période.** Chaque équipe et chaque décennie de naissance des joueurs est comparée à **la part des naissances en France de la même décennie** portant un nom « diversité », calculée sur le même fichier (`elite_idp_reference_naissances.csv`) :

| Naissances en France | 1891-1950 | 1951-1960 | 1961-1970 | 1971-1980 | 1981-1990 | 1991-2000 |
|---|---:|---:|---:|---:|---:|---:|
| IDP des naissances | 0,02 à 0,3 % | 1,3 % | 3,7 % | 6,8 % | 8,3 % | 9,4 % |

- **Garde-fou 2 : le biais de l'indice, à écrire en toutes lettres.** L'IDP ne voit pas les migrations antérieures à 1950 : les noms italiens, polonais, espagnols, portugais, arméniens, et ceux des Antilles et de La Réunion, présents en France avant 1950, comptent « non diversité ». La hausse dans le temps est donc **en partie mécanique** (la référence passe de presque 0 à 9,4 %). Avant 1951, le rapport à la référence n'a pas de sens et n'est pas calculé. Le fichier Insee s'arrête aux naissances de 2000 : les joueurs nés après 2000 sont comparés aux naissances de 1991-2000 (référence probablement sous-estimée).
- **Noms non reconnus** : le fichier Insee ne contient que les noms portés par au moins une trentaine de naissances entre 1891 et 2000 ; les noms rares ou récents en sont absents. 10 à 20 % des internationaux nés en France ont un nom non reconnu (35 % en football masculin pour les naissances depuis 1991). Ils sont exclus du taux, comme dans l'outil du site ; la référence des naissances les exclut aussi, ce qui garde la comparaison cohérente, mais **le taux de l'équipe est plutôt un plancher**. La colonne `idp_borne_haute_pct` donne l'autre extrême (tous les non-reconnus comptés « diversité »).
- **Garde-fou 3 : agrégats seulement**, par sport, sexe et période de naissance ; intervalle de Wilson à 90 % ; **aucun résultat sous 30 noms reconnus** (case masquée). Champ principal : internationaux **nés en France** (pour comparer à des naissances en France) ; le champ « tous » est dans le fichier.
- `z` : écart à l'attendu (somme des références individuelles) en écarts types ; au-delà de 2 en valeur absolue, l'écart est peu compatible avec le hasard.

### Résultats (`elite_idp.csv`, nés en France)

**Par grande période de naissance** (IDP de l'équipe, intervalle à 90 %, contre les naissances de la même période) :

| Équipe | 1951-1970 | 1971-1990 | 1991 et après |
|---|---|---|---|
| Football, hommes | 5,9 % [3,2-10,5] contre 2,5 % (x2,4) | 19,3 % [13,8-26,2] contre 7,6 % (x2,5) | 42,9 % [31,9-54,6] contre 9,4 % (x4,5) |
| Football, femmes | 3,8 % [1,3-10,8] contre 2,5 % | 13,8 % [8,6-21,3] contre 7,8 % (x1,8) | 17,2 % [10,6-26,8] contre 9,4 % (x1,8) |
| Rugby à XV, hommes | 0 % [0-1,8] contre 2,6 % | 4,1 % [2,3-7,2] contre 7,5 % (x0,55) | 7,8 % [4,5-13,4] contre 9,4 % (x0,83) |
| Rugby à XV, femmes | moins de 30 noms | 7,3 % [3,0-17,0] contre 7,9 % | 8,3 % [3,4-19,1] contre 9,4 % |
| Basket-ball, hommes | 2,1 % [0,5-8,8] contre 2,7 % | 19,4 % [12,7-28,5] contre 7,5 % (x2,6) | 24,2 % [14,2-38,2] contre 9,4 % (x2,6) |
| Basket-ball, femmes | moins de 30 noms | 14,3 % [7,6-25,3] contre 7,7 % (x1,9) | moins de 30 noms |
| Handball, hommes | 0 % [0-6,8] contre 3,2 % | 1,8 % [0,4-7,7] contre 7,5 % (x0,24) | moins de 30 noms |
| Handball, femmes | moins de 30 noms | 13,0 % [7,2-22,3] contre 7,7 % (x1,7) | 20,9 % [12,6-32,7] contre 9,4 % (x2,2) |
| JO 2024, femmes (tous sports) | | | 11,6 % [8,2-16,3] contre 9,4 % (x1,2) |
| JO 2024, hommes (tous sports) | | | 7,4 % [4,7-11,3] contre 9,4 % (x0,8) |

**Par décennie, football et rugby masculins** (cases d'au moins 30 noms reconnus) :

| Naissance | Football H : IDP [IC 90 %] | Rugby H : IDP [IC 90 %] | Naissances en France |
|---|---|---|---:|
| 1951-1960 | 3,3 % [1,1-9,4] | 0 % [0-3,7] | 1,3 % |
| 1961-1970 | 8,6 % [4,3-16,7] | 0 % [0-3,2] | 3,7 % |
| 1971-1980 | 9,1 % [4,5-17,5] | 0 % [0-2,5] | 6,8 % |
| 1981-1990 | 29,6 % [20,6-40,6] | 9,1 % [5,2-15,4] | 8,3 % |
| 1991-2000 | 42,1 % [29,9-55,4] | 8,9 % [5,1-15,1] | 9,4 % |

Lecture (la diversité des noms mesure une origine **probable des noms**, attachée au nom et non à la personne ; un nom n'est pas une identité) :

- **Football masculin : surreprésentation nette et croissante**, de 2 à 4 fois la part des naissances de la même période ; l'écart se creuse pour les générations nées depuis 1981 (z de 5,7 et 6,9). **Établi** pour le sens et l'ordre de grandeur ; le niveau exact reste fragile pour les naissances depuis 1991 (35 % de noms non reconnus, borne haute à 62 %).
- **Basket masculin** : environ 2,6 fois les naissances depuis 1971 (z de 2,9 et 3,7 par grande période, 2,3 et 3,0 par décennie). **Probable**.
- **Football, handball et basket féminins** : 1,7 à 2,2 fois les naissances (z de 1,5 à 2,6). **Probable** pour l'ensemble, **fragile** décennie par décennie.
- **Rugby à XV masculin** : **au niveau des naissances ou en dessous** (aucun nom « diversité » parmi les 106 joueurs reconnus nés de 1971 à 1980, contre 6,8 % attendus ; parité pour les générations 1981-2000). **Probable**. Même lecture pour le rugby féminin (parité, fragile).
- **Handball masculin** : en dessous des naissances pour les générations 1951-1990 (**fragile** : 30 à 55 noms par case). Ce résultat est aussi celui où le biais de l'indice pèse le plus : plusieurs générations du handball masculin comptent des joueurs originaires des Antilles, dont les noms sont « non diversité » pour l'IDP.
- **Délégation de Paris 2024, tous sports** : **proche des naissances** (femmes 11,6 %, hommes 7,4 %, contre 9,4 % ; z de 1,0 et -0,9). **Probable** : la surreprésentation n'est pas un trait de « l'élite sportive » en général, mais de quelques sports.

### Une fourchette plutôt qu'un rapport unique (`elite_idp_fourchette.csv`)

**Objection.** La référence « naissances en France » ignore les enfants arrivés de l'étranger avec lesquels les joueurs ont grandi : la génération qui vit en France compte plus de noms « diversité » que celle qui y est née. On encadre donc la référence entre deux bornes.

- **Référence basse** (rapport le plus élevé) : l'IDP des naissances en France de la décennie, déjà calculé.
- **Référence haute** (rapport le plus prudent) : la génération telle qu'elle vit en France, en comptant **tous** les immigrés de la génération comme portant un nom « diversité » (hypothèse volontairement maximale) : `ref_haute = IDP_naissances x (1 - s) + s`, où `s` est la part des immigrés (personnes nées étrangères à l'étranger, définition Insee) dans la génération.
- **Source de `s`** : Insee, recensement de la population 2023, jeu `DS_RP_TD_IMMI_AGESEXEMPSTA_PRINC` (thème « Étrangers - Immigrés », lu par l'API Melodi, France hors Mayotte) : part des immigrés par sexe et tranche d'âge (`elite_idp_parts_immigres.csv`). Chaque année de naissance reçoit la part de la tranche où tombe son âge au 1er janvier 2023, avec le sexe de l'équipe ; la référence d'une case est la moyenne sur ses joueurs.
- **Variante plus proche de l'adolescence** : recensement le plus proche de l'année des 17 ans (1990, 1999, 2007, 2012, 2017, 2021 à 2023), d'après la série Insee « Population immigrée et étrangère par sexe et âge » (structure par âge des immigrés) rapportée aux estimations de population par âge (Insee, `DS_ESTIMATION_POPULATION`) ; deux sexes ensemble.
- **Rapports** : rapport haut = IDP de l'équipe / référence basse ; rapport bas = IDP de l'équipe / référence haute ; **rapport bas prudent** = borne basse de l'intervalle à 90 % de l'IDP de l'équipe / référence haute.

**Part des immigrés retenue par décennie de naissance** (`elite_idp_parts_par_decennie.csv`) :

| Naissance | Âge en 2023 | RP 2023, hommes | RP 2023, femmes | Variante : recensement le plus proche des 17 ans |
|---|---|---:|---:|---:|
| 1951-1960 | 62-71 | 11,3 % | 9,9 % | non calculée (pas de recensement de la série avant 1990) |
| 1961-1970 | 52-61 | 12,3 % | 11,6 % | non calculée |
| 1971-1980 | 42-51 | 14,5 % | 15,5 % | 4,4 % |
| 1981-1990 | 32-41 | 14,5 % | 15,5 % | 4,2 % |
| 1991-2000 | 22-31 | 12,6 % | 13,2 % | 5,2 % |
| 2001-2010 | 12-21 | 6,7 % | 6,5 % | 5,6 % |

Les générations nées avant 1951 ont plus de 72 ans en 2023 : le recensement ne donne pour elles que la tranche ouverte « 55 ans ou plus », et le rapport n'a de toute façon pas de sens avant 1951 (référence quasi nulle). Rien n'est calculé pour elles.

**Fourchette des rapports** (nés en France ; cases d'au moins 30 noms reconnus) :

| Équipe et naissance | IDP [IC 90 %] | Réf. basse (naissances) | Réf. haute (RP 2023) | Rapport haut | Rapport bas | Rapport bas prudent | Borne haute « non reconnus » |
|---|---|---:|---:|---:|---:|---:|---:|
| Football H, 1971-1990 | 19,3 % [13,8-26,2] | 7,6 % | 21,0 % | x2,55 | x0,92 | x0,66 | 27,9 % |
| Football H, 1981-1990 | 29,6 % [20,6-40,6] | 8,3 % | 21,7 % | x3,55 | x1,37 | x0,95 | 37,7 % |
| Football H, 1991 et après | 42,9 % [31,9-54,6] | 9,4 % | 20,1 % | x4,54 | x2,13 | x1,58 | 62,7 % |
| Basket H, 1971-1990 | 19,4 % [12,7-28,5] | 7,5 % | 20,9 % | x2,59 | x0,93 | x0,61 | 26,0 % |
| Basket H, 1991 et après | 24,2 % [14,2-38,2] | 9,4 % | 20,9 % | x2,57 | x1,16 | x0,68 | 45,7 % |
| Football F, 1971-1990 | 13,8 % [8,6-21,3] | 7,8 % | 22,1 % | x1,77 | x0,62 | x0,39 | 22,5 % |
| Football F, 1991 et après | 17,2 % [10,6-26,8] | 9,4 % | 20,6 % | x1,83 | x0,84 | x0,51 | 30,4 % |
| Handball F, 1991 et après | 20,9 % [12,6-32,7] | 9,4 % | 20,3 % | x2,22 | x1,03 | x0,62 | 33,3 % |
| Rugby H, 1971-1990 | 4,1 % [2,3-7,2] | 7,5 % | 21,0 % | x0,55 | x0,20 | x0,11 | 12,7 % |
| Rugby H, 1991 et après | 7,8 % [4,5-13,4] | 9,4 % | 20,7 % | x0,83 | x0,38 | x0,22 | 25,4 % |
| JO 2024 F, 1991 et après | 11,6 % [8,2-16,3] | 9,4 % | 19,6 % | x1,23 | x0,59 | x0,42 | 25,1 % |
| JO 2024 H, 1991 et après | 7,4 % [4,7-11,3] | 9,4 % | 19,7 % | x0,78 | x0,38 | x0,24 | 20,1 % |

Les autres cases (basket et handball féminins, handball masculin, décennies) sont dans le fichier. La variante « recensement le plus proche des 17 ans » (colonnes `_ado`) donne des rapports bas intermédiaires : football H x2,94 pour les nés depuis 1991 (prudent x2,19) et x1,67 pour 1971-1990 ; basket H x1,61 et x1,75 ; football F x1,24 et x1,21 ; rugby H x0,36 et x0,55 ; JO 2024 x0,80 (femmes) et x0,52 (hommes).

**Lecture.**

- **Seul le football masculin des générations nées depuis 1981 reste au-dessus de la parité même dans l'hypothèse la plus défavorable** : x2,1 à x4,5 pour les nés depuis 1991 (x1,6 au plus prudent), x1,4 à x3,6 pour les nés de 1981 à 1990 (le plus prudent touche la parité). **Établi** pour les nés depuis 1991 : le football masculin récent compte plus de noms « diversité » que la génération qui vit en France, quelle que soit la référence.
- **Football masculin 1971-1990, basket masculin, football et handball féminins** : la fourchette va d'environ la parité (x0,6 à x1,2) à x1,8 à x2,6. La surreprésentation par rapport aux naissances **ne résiste pas** à l'hypothèse maximale : on peut écrire « plus que les naissances en France de leur génération », pas « plus que la génération qui vit en France ». **Fragile** dans sa forme forte.
- **Rugby masculin** : en dessous dans tous les cas (x0,2 à x0,55 pour 1971-1990, x0,4 à x0,8 depuis 1991). **Établi** pour le sens.
- **Délégation de Paris 2024** : de x0,6 à x1,2 (femmes) et de x0,4 à x0,8 (hommes), soit au niveau de la génération ou en dessous. **Probable**.

**Limites de la borne haute (à écrire avec le tableau).**

1. Elle **surestime** la part des immigrés avec lesquels les joueurs ont grandi : le RP 2023 compte aussi les immigrés arrivés adultes, après l'adolescence des joueurs. La variante au recensement le plus proche des 17 ans donne des parts environ trois fois plus faibles (4 à 6 % contre 12 à 15 %).
2. Elle **surestime** encore en comptant tous les immigrés « diversité », alors qu'une partie porte des noms européens déjà présents en France avant 1950 (Italie, Espagne, Belgique, Allemagne), « non diversité » pour l'IDP.
3. Tranches d'âge **grossières** : l'Insee ne diffuse les immigrés que par moins de 15 ans, 15-24, 25-54 et 55 ans ou plus ; chaque génération reçoit la moyenne de sa tranche.
4. Les descendants d'immigrés nés en France sont **déjà** dans la référence basse ; la borne haute ne les compte pas deux fois.
5. Elle ne corrige ni le biais d'origine de l'indice (migrations antérieures à 1950, outre-mer) ni celui des noms non reconnus, rappelé dans la dernière colonne.

La référence juste est entre les deux bornes, sans doute plus près de la basse pour la période où les joueurs étaient adolescents (variante au recensement le plus proche des 17 ans), mais ces données ne permettent pas de l'établir.

### Cadrage pour le texte

La bonne question n'est pas « qui est là » mais **par quelles filières on accède au haut niveau**, et ces filières diffèrent d'un sport à l'autre :

- le football se pratique partout, à bas coût, et son recrutement de haut niveau passe par la détection précoce et les centres de formation des clubs professionnels, qui puisent largement dans les quartiers populaires des grandes agglomérations ; le sport y est décrit comme l'une des rares voies d'ascension sociale perçues comme accessibles (Julien Bertrand, *La Fabrique des footballeurs*, La Dispute, 2012 ; Stéphane Beaud, *Traîtres à la nation ? Un autre regard sur la grève des Bleus*, La Découverte, 2011) ;
- le rugby reste ancré dans des territoires (Sud-Ouest) et des milieux sociaux plus intermédiaires, avec une formation longtemps passée par les clubs locaux et le sport scolaire ;
- mise en regard avec la base, déjà dans la note mère : le football est la fédération la plus surreprésentée dans les QPV (R3), et les licences de tennis, golf ou voile montent avec le revenu des communes quand celles du football non (R4).

À proscrire : tout vocabulaire de « remplacement » ou de « grand remplacement », toute lecture en termes de « part d'étrangers » (presque tous les joueurs comptés ici sont nés en France), tout résultat par joueur.

---

## (c) Question 2 : d'où viennent les internationaux, et la base de licenciés l'explique-t-elle ?

### Méthode

- **Observés** : internationaux nés dans un département (code Insee du lieu de naissance ; Corse regroupée en « 20 » ; Paris, Lyon et Marseille au niveau de la commune), hommes et femmes ensemble, **nés en 1970 et après** (variante : nés en 1985 et après). Rugby féminin pris tel quel (lieu inconnu pour près de la moitié).
- **Attendus** : licenciés de 10 à 19 ans du sport dans le département, **par sexe**, multipliés par le taux national de ce sexe, puis additionnés. Licences **2013** (plus ancien millésime géocodé avec âge et sexe : les joueurs nés de 1970 à 2000 avaient 10 à 19 ans entre 1980 et 2019, soit un **décalage de 0 à 33 ans**) ; variante licences 2023. Variante sans licences : attendus d'après la population des 10-19 ans (2011).
- **Test** : intervalle de Poisson exact à 90 % ; mais les départements sont **surdispersés** (variance 1,6 fois l'attendu en rugby, 3 à 3,9 fois en football, basket et handball) : on corrige en quasi-Poisson, puis pour 96 départements testés à la fois (Benjamini-Hochberg, seuil 10 %). Est « outsider robuste » un département qui passe ces deux corrections avec au moins 5 observés.
- **Facteurs** : modèle quasi-Poisson de l'écart observé / attendu sur le revenu médian du département (Filosofi 2023), la part de la population en QPV (2024), la densité de clubs du sport (clubs INJEP 2023 pour 100 000 habitants), le taux de licence des 10-19 ans, la taille du département, et pour le football la présence d'un club de Ligue 1 ou de Ligue 2 en 2023-2024 (indicateur saisi à la main, à défaut de la liste FFF des centres de formation agréés, inaccessible au robot). 96 départements (métropole, Corse regroupée, et La Réunion, seul département d'outre-mer avec un revenu Filosofi diffusé).

### Les départements outsiders (`elite_departements.csv`)

Nés en 1970 et après, licences 2013 :

| Sport | Département | Observés | Attendus | Rapport | IC 90 % (Poisson) |
|---|---|---:|---:|---:|---|
| Football | Paris | 24 | 4,0 | x6,0 | 4,2-8,5 |
| Football | Rhône | 30 | 8,3 | x3,6 | 2,6-4,9 |
| Basket | Paris | 19 | 2,2 | x8,5 | 5,6-12,5 |
| Basket | Guadeloupe | 8 | 1,5 | x5,5 | 2,7-9,9 |
| Basket | Guyane | 5 | 0,6 | x8,4 | 3,3-17,7 |
| Handball | Paris | 14 | 0,9 | x14,9 | 9,0-23,3 |

Paris ressort dans les quatre sports (dans 3 spécifications sur 4 pour le rugby) ; la Guadeloupe aussi en handball dans deux spécifications ; les Yvelines (handball) et le Val-de-Marne (basket) dans une seule. **Aucun département ne ressort de façon robuste « en dessous » de sa base** : les attendus départementaux sont trop petits. Parmi les plus bas, sans que ce soit établi : en football, l'Ille-et-Vilaine (1 observé pour 6,3 attendus), le Haut-Rhin (1 pour 5,6), le Bas-Rhin (3 pour 8,5) ; en rugby, la Loire-Atlantique (0 pour 5,0) et La Réunion (0 pour 4,4), face aux Hautes-Pyrénées, Pyrénées-Orientales, Var et Pyrénées-Atlantiques (x1,7 à x2,3).

**Lecture : Paris et le Rhône sont d'abord un effet de maternité.** Les enfants des communes voisines naissent souvent dans les maternités de Paris ou de Lyon, et l'état civil retient la ville de la maternité ; en même temps, Paris a peu de licenciés par habitant. Le même excès parisien apparaît en rugby (x2,7), sport où Paris n'est pas un vivier connu. Un exemple notoire : Kylian Mbappé a grandi à Bondy (Seine-Saint-Denis) mais il est né à Paris ; il compte donc pour Paris. À l'inverse, Bondy accueille la maternité de l'hôpital Jean-Verdier, et 4 internationaux de football nés en 1970 et après y ont leur naissance enregistrée, sans qu'on sache où ils ont grandi. D'autres exemples notoires vont dans le même sens : Zinédine Zidane est né à Marseille, Thierry Henry aux Ulis (Essonne). C'est pourquoi la seule lecture solide se fait sur des **zones regroupées**.

### La Seine-Saint-Denis et le cœur de l'agglomération parisienne (`elite_zones_focus.csv`)

Football, hommes et femmes, nés en 1970 et après :

| Zone | Observés | Attendus (licences 2013) | Rapport | IC 90 % corrigé | Rapport à la population des 10-19 ans |
|---|---:|---:|---:|---|---:|
| Seine-Saint-Denis (93) | 14 | 6,8 | x2,05 | 0,95-4,40 | x1,57 |
| Paris (75) | 24 | 4,0 | x6,0 | 3,4-10,8 | x2,5 |
| Paris et petite couronne (75, 92, 93, 94) | 65 | 21,3 | x3,05 | 2,1-4,4 | x1,9 |
| Île-de-France | 93 | 46,1 | x2,0 | 1,5-2,7 | x1,4 |
| Outre-mer (971 à 974) | 16 | 11,9 | x1,35 | 0,7-2,8 | x1,15 |

**Réponse sur la Seine-Saint-Denis : probablement oui, sans pouvoir le prouver au seul niveau du département.** Elle compte deux fois plus d'internationaux de football nés sur son sol que ses licenciés ne le laissent attendre (14 pour 6,8 ; 11 pour 4,0 chez les nés depuis 1985), mais une fois la surdispersion prise en compte, l'intervalle touche 1 (p = 0,12). Ce qui est **établi**, c'est l'excès du **cœur de l'agglomération pris ensemble** (Paris et petite couronne : trois fois l'attendu par les licences, près de deux fois l'attendu par la population jeune), dans lequel la Seine-Saint-Denis pèse, mais dont on ne peut pas séparer les départements à cause des maternités. Cet excès n'est pas propre au football : le même cœur d'agglomération donne x1,7 en rugby, x3,3 en basket et x2,4 en handball. L'outre-mer, lui, se distingue en **basket (x4,4) et handball (x3,6)**, pas en football (x1,35, non significatif), et presque pas en rugby (1 observé pour 7,2 attendus). Les variantes (licences 2023, nés depuis 1985) donnent les mêmes ordres de grandeur.

### Facteurs associés (`elite_facteurs.csv`)

Rapport de taux pour un écart type de plus, toutes variables ensemble, nés en 1970 et après, licences 2013 ; entre parenthèses, le même modèle **sans Paris ni le Rhône** :

| Variable | Football | Rugby à XV | Basket | Handball |
|---|---|---|---|---|
| Taux de licence des 10-19 ans | **0,72** (**0,77**) | 1,21 (**1,26**) | **0,64** (0,92) | **0,77** (0,88) |
| Part de la population en QPV | **1,18** (**1,17**) | **1,17** (**1,15**) | **1,19** (**1,18**) | **1,31** (**1,31**) |
| Revenu médian du département | **1,17** (**1,13**) | **1,19** (1,10) | **1,48** (**1,24**) | **1,48** (**1,32**) |
| Clubs du sport pour 100 000 habitants | 0,91 (0,91) | 1,26 (1,21) | 1,35 (0,96) | 1,28 (1,30) |
| Club de Ligue 1 ou 2 (oui / non) | **1,53** (**1,34**) | | | |

En gras : intervalle à 90 % qui exclut 1.

- **Par licencié, les départements urbains denses produisent plus d'internationaux** : en football et en basket, plus le taux de licence des jeunes est élevé, moins chaque licence « rapporte » d'internationaux (en football, cela résiste au retrait de Paris et du Rhône) ; la part de population en QPV va dans le même sens dans les quatre sports, de x1,15 à x1,31 par écart type, et **résiste au retrait de Paris et du Rhône**. **Probable** (effets modestes, intervalles larges, lecture écologique).
- **Le revenu départemental** est positif lui aussi, en même temps que la part en QPV : ce sont les départements métropolitains à la fois riches et inégaux (Paris, Hauts-de-Seine, Rhône, Bouches-du-Rhône) qui tirent ce résultat, et il faiblit sans Paris ni le Rhône (disparaît en rugby). Ce n'est pas un effet du revenu des familles. **Fragile** comme facteur propre.
- **La densité de clubs n'explique rien** une fois le reste pris en compte.
- **Présence d'un club professionnel de football** : x1,5 (x1,3 sans Paris ni le Rhône, p = 0,08, intervalle à 90 % de 1,01 à 1,78). **Fragile** : un centre de formation recrute dans toute sa région, souvent au-delà, et les joueurs naissent avant d'y entrer ; l'Ille-et-Vilaine, qui accueille l'un des centres les mieux classés, est parmi les plus basses en naissances d'internationaux.
- **Rugby** : le rugby suit beaucoup mieux sa base de licenciés (surdispersion 1,6 contre 3 à 3,9 ailleurs, aucun département outsider hors Paris) ; les associations vont dans le même sens mais sont plus faibles, ce qui est cohérent avec un recrutement territorial par les clubs.

Lecture écologique au département : elle ne dit rien des individus, et ne sépare pas la densité de la détection (les recruteurs des clubs professionnels sont concentrés dans les grandes agglomérations), le niveau de la concurrence locale, l'effet de maternité et la mobilité des familles.

### Limites à écrire

1. **Lieu de naissance n'est pas lieu de vie** : maternités de la ville voisine (Paris, Lyon, Bondy), déménagements dans l'enfance.
2. **Décalage des licences** : 2013 est le plus ancien millésime géocodé avec âge et sexe ; il a 0 à 33 ans d'écart avec la jeunesse des joueurs. Les licences 2011-2012 (anciens liens INJEP) n'ont pas été téléchargées.
3. **Petits effectifs** : de 0 à 30 internationaux par département et par sport ; surdispersion forte.
4. **Complétude inégale** : basket et handball sans référence ; rugby féminin sans lieux.
5. **Plusieurs tests** : 96 départements x 4 sports x 4 spécifications ; seuls les écarts qui résistent aux corrections sont présentés comme établis.

---

## (d) Ce qui est publiable, et sous quelle forme

**Publiable (encadré dans le dossier « Sport », agrégats seulement, avec les garde-fous en clair) :**

- Un graphique « diversité des noms des internationaux contre leur génération », **par sport et par grande période** : football masculin, rugby masculin, basket masculin, football féminin, et la délégation de Paris 2024 en point de comparaison, la référence étant affichée en **fourchette** (naissances en France / génération vivant en France, immigrés comptés au maximum) et non en rapport unique. Avec obligatoirement : le biais des migrations antérieures à 1950, la part de noms non reconnus, l'intervalle, et le cadrage « filières d'accès ». Formulation sûre : « le football masculin des générations récentes compte plus de noms de la diversité que sa génération, quelle que soit la référence ; les autres sports d'équipe, plus que les naissances en France, mais pas forcément plus que la génération qui vit en France ; le rugby, moins ».
- Le constat « tous sports confondus, la délégation olympique ressemble aux naissances ; c'est le football (et à un moindre degré le basket) qui s'en écarte, le rugby non ».
- Au territoire : le **cœur de l'agglomération parisienne** (x3 par rapport aux licences en football, aussi en basket et en handball), l'**outre-mer en basket et en handball**, et le résultat « par licencié, l'urbain dense produit davantage », avec l'effet de maternité expliqué.

**Pas publiable :**

- Une carte ou un classement des départements « outsiders » : la plupart des écarts sont du bruit ou des effets de maternité.
- La Seine-Saint-Denis seule présentée comme un fait établi : la formuler comme « probable, et noyée dans le cœur de l'agglomération ».
- Tout résultat communal (sauf l'illustration de l'effet de maternité, en comptes et sans nom), tout résultat par joueur, tout croisement nom et lieu de naissance d'un joueur.
- L'IDP par décennie pour le basket, le handball et le rugby féminins (cases sous 30 noms).
- Le rugby féminin à la question 2.

---

## (e) Ce qui reste à vérifier

1. **Références officielles** : nombre d'internationaux A de la FFBB et de la FFHB (guides de presse) et de la FFF, à demander ou à consulter à la main.
2. **Contrôle par échantillon** des lieux et dates de naissance Wikidata (par exemple 50 joueurs tirés au hasard contre les fiches des fédérations).
3. **Lieu de formation plutôt que lieu de naissance** : le premier club (P54 des clubs de jeunes dans Wikidata, ou rubrique « club formateur » des fiches) répondrait mieux à la question des filières et neutraliserait l'effet de maternité ; couverture à mesurer.
4. **Licences plus anciennes** : télécharger les millésimes 2011 et 2012 et, si l'INJEP les a, des séries départementales des années 1990-2000.
5. **Liste des centres de formation agréés** (FFF, DTN) pour remplacer l'indicateur « club de Ligue 1 ou 2 ».
6. **Délégation olympique** : nettoyer la liste (non-athlètes) et ajouter Tokyo 2020 et Rio 2016 pour avoir des cases par sport.
7. **Part des immigrés par âge détaillé** : le fichier détail du recensement (individus, âge détaillé, indicateur immigré) donnerait une part par année de naissance et au moment de l'adolescence, à la place des quatre tranches diffusées.
8. **Référence IDP pour les naissances après 2000** : le fichier Insee s'arrête en 2000 ; vérifier s'il existe un millésime plus récent.
