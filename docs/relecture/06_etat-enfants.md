# 6. Beaucoup de dépense publique, des enfants mieux protégés ?
> Carte `etat-enfants` · verdict « Faux » · dossier /international · fiche préparée le 30/10/2026

## Ce qu'affiche la carte

- **Rubrique** : État-providence ; unité « Pays » ; couleur `#3B82F6`.
- **Question** : « Beaucoup de dépense publique, des enfants mieux protégés ? »
- **Verdict** : `faux`.
- **Chiffre** : **27,5 %**, « des moins de 18 ans menacés de pauvreté ou d'exclusion, dans l'un des deux pays qui dépensent le plus d'Europe ».
- **Texte** : « 57,3 % du PIB de dépenses publiques en 2025, au 2e rang des 30 pays comparés, derrière la Finlande (57,5 %). Et pourtant plus d'un enfant sur quatre est menacé de pauvreté ou d'exclusion, plus que la moyenne européenne (24,3 %) : seuls 4 des 28 pays disponibles font pire. Ce contraste ne dit pas à lui seul ce que vaut la dépense, qui finance d'abord les retraites et la santé. »
- **Source citée** : « Eurostat, dépenses publiques et AROPE moins de 18 ans (2025) », lien vers la vue `ilc_peps01n` du databrowser (le jeu des dépenses, `gov_10a_main`, n'a pas de lien sur la carte).
- **Lien** : « Ouvrir le dossier France en Europe » vers `/international`.

## Ce que dit le dossier

Page `frontend/src/pages/international/International.jsx`, titre « Où se situe la France ? », 8 indicateurs Eurostat, 30 pays (UE27, Islande, Norvège, Suisse), moyenne UE27 en repère.

- **En bref** : « 57,3 % du PIB de dépenses publiques : 2ᵉ des 30 pays comparés » ; « 1 sur 4 enfants menacés de pauvreté ou d'exclusion (27,5 %), plus que la moyenne UE ».
- **Carte d'identité** : un dot-plot par indicateur (France, moyenne UE27, extrêmes). Dépenses publiques : sens « neutre », rang affiché comme « 2ᵉ valeur la plus haute sur 30 ». Pauvreté des enfants : sens « bas », 24ᵉ sur 28.
- **Histoire « L'État et les enfants »** : texte calculé à partir du JSON (rang des dépenses, pays devant, nombre de pays qui font pire), identique à la carte.
- **Nuage « Que rapporte la dépense publique ? »** : dépenses publiques en abscisse, pauvreté des enfants en ordonnée (par défaut), droite de régression, pays qui s'en écartent (`OutsidersScatter`).
- **Trajectoires** : la pauvreté des enfants a une série France / UE27 de 2015 à 2025 (11 points), sélectionnable ; les dépenses publiques depuis 1995.
- Aide de l'indicateur (`decoupages.js`) : AROPE = pauvreté monétaire, privation matérielle et sociale sévère ou très faible intensité de travail du ménage ; 2025 ; Islande et Suisse non disponibles.

## D'où viennent les chiffres

Chaîne : API Eurostat (JSON-stat) -> `python/tools/build_international.py` (interrogation en direct, aucun fichier local) -> `frontend/public/data/decoupages/pays.json` -> `config/decoupages.js` (entrée `pays`) -> `International.jsx` (et `/explorer/pays`).

Paramètres figés dans le script :
- `dep_publiques` : `gov_10a_main`, `unit=PC_GDP`, `sector=S13`, `na_item=TE`, `time=2025`.
- `pauvrete_enfants` : `ilc_peps01n`, `unit=PC`, `sex=T`, `age=Y_LT18`, `time=2025`.
- Séries : mêmes paramètres sans `time`, `geo=FR` et `geo=EU27_2020`, depuis 1995.

Rattachement de chaque chiffre :

| Chiffre de la carte | Valeur dans `pays.json` | Calcul |
|---|---|---|
| 27,5 % | `categories[fr].valeurs.pauvrete_enfants` = 27,5 | valeur Eurostat 2025 arrondie au dixième |
| 24,3 % | `references.pauvrete_enfants` = 24,3 | agrégat `EU27_2020` |
| « 4 des 28 pays font pire » | Espagne 33,8, Bulgarie 33,1, Roumanie 32,4, Grèce 29,6 | `pauvVals.filter(x > frPauv)` dans `International.jsx` ; 28 = 30 moins Islande et Suisse (pas de donnée 2025) |
| 57,3 % | `dep_publiques` France = 57,3 | `gov_10a_main` 2025 |
| 2e rang, Finlande 57,5 % | Finlande 57,5 ; puis Autriche 54,6, Belgique 54,4 | rang compté du plus haut au plus bas (`depRang`) |
| « l'un des deux pays qui dépensent le plus » | écart France / Finlande : 0,2 point ; 3e pays à 2,7 points | texte écrit en dur sur la carte, calculé sur la page |

Contrôle du 30/10/2026 par l'API : valeurs identiques ; la série française de `ilc_peps01n` porte le drapeau **`b` (rupture de série) en 2020 et en 2022**.

## Les jeux de données

### Personnes menacées de pauvreté ou d'exclusion sociale par âge et sexe (Eurostat, EU-SILC)
- **Producteur** : Eurostat, à partir des enquêtes nationales EU-SILC (en France : Insee, enquête SRCV).
- **Code** : `ilc_peps01n` (« Personnes en risque de pauvreté ou d'exclusion sociale par âge et sexe », définition « UE 2030 », série depuis 2015).
- **Millésime utilisé** : 2025 (année d'enquête ; revenus de l'année précédente). Dernier disponible : 2025 (mise à jour Eurostat du 20/10/2026).
- **Page** : https://ec.europa.eu/eurostat/databrowser/view/ilc_peps01n/default/table?lang=fr
- **API** : https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/ilc_peps01n?format=JSON&lang=fr&unit=PC&sex=T&age=Y_LT18&time=2025 (fichier complet : https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/ilc_peps01n?format=TSV&compressed=true)
- **Géographie** : pays de l'UE, AELE, pays candidats selon les années, agrégats UE27 et zone euro ; le site garde 30 pays.

| colonne ou dimension | sens / modalités | utilisée ? |
|---|---|---|
| `freq` | A (annuel) | oui, implicite |
| `unit` | PC (pourcentage), THS_PER (milliers de personnes) | oui : PC. Non : THS_PER (nombre d'enfants concernés : 3 738 000 en France en 2025) |
| `age` | 34 classes : TOTAL, Y_LT6, Y6-11, Y12-17, Y_LT18, Y18-24, Y18-64, Y_GE65, Y_GE75, etc. | oui : Y_LT18. Non : Y_LT6, Y6-11, Y12-17 (âge des enfants), TOTAL (repère toute la population) |
| `sex` | T, M, F | oui : T. Non : filles / garçons (27,9 % et 27,1 % en 2025, écart sans intérêt ici) |
| `geo` | pays et agrégats | oui : 30 pays + EU27_2020 |
| `time` | 2015 à 2025 | oui : 2025 (carte) et série 2015-2025 (trajectoire) |
| statut (drapeaux) | `b` rupture, `e` estimé, `p` provisoire, `u` peu fiable | non : les drapeaux ne sont pas lus par le script |

### Principaux agrégats des administrations publiques (Eurostat, comptes nationaux)
- **Producteur** : Eurostat (comptes nationaux SEC 2010 transmis par les instituts, en France l'Insee).
- **Code** : `gov_10a_main`.
- **Millésime utilisé** : 2025. Dernier disponible : 2025 (mise à jour du 21/10/2026).
- **Page** : https://ec.europa.eu/eurostat/databrowser/view/gov_10a_main/default/table?lang=fr
- **API** : https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/gov_10a_main?format=JSON&lang=fr&unit=PC_GDP&sector=S13&na_item=TE&time=2025
- **Géographie** : pays de l'UE et AELE, agrégats.

| colonne ou dimension | sens / modalités | utilisée ? |
|---|---|---|
| `unit` | PC_GDP (% du PIB), MIO_EUR, MIO_NAC | oui : PC_GDP. Non : montants |
| `sector` | S13 (administrations publiques), S1311 (État), S1312 (États fédérés), S1313 (locales), S1314 (sécurité sociale), S1, S212 | oui : S13. Non : part de la sécurité sociale dans la dépense |
| `na_item` | 121 postes SEC : TE (dépenses totales), TR (recettes totales), B9 (solde), D62PAY (prestations sociales en espèces), D1PAY (rémunérations), D41PAY (intérêts), P51G (investissement), etc. | oui : TE. Non : prestations sociales, intérêts, recettes |
| `geo`, `time` | pays, 1995 à 2025 | oui |

## Ce qu'on n'exploite pas encore

- **L'âge des enfants** (`age` de `ilc_peps01n`) : en 2025, 25,0 % des moins de 6 ans, 25,5 % des 6-11 ans, mais **31,4 % des 12-17 ans** (UE : 23,2 / 23,7 / 25,8). L'écart avec l'Europe se concentre chez les adolescents : chiffre plus précis que la moyenne des moins de 18 ans.
- **Le type de ménage** (`ilc_peps03n`, dimension `hhcomp`) : personnes vivant dans une famille monoparentale, **48,6 % en France contre 44,3 % dans l'UE** (2025, 23e sur 28) ; couple avec un enfant 12,0 % (UE 14,8) ; couple avec trois enfants ou plus 34,7 % (UE 32,4). La pauvreté des enfants français tient beaucoup aux familles monoparentales, ce que la carte ne dit pas. Attention : ce jeu porte sur les personnes du ménage (adultes compris), pas sur les seuls enfants.
- **Le diplôme des parents** (`ilc_peps60n`, dimension `isced11`) : enfants dont les parents ont au plus le brevet, **66,0 %** (UE 62,5) ; parents bacheliers 37,6 % (UE 29,3) ; parents diplômés du supérieur 12,6 % (UE 10,8). La reproduction sociale de la pauvreté infantile, angle cohérent avec le reste du site.
- **L'effet des transferts sociaux** (`ilc_li10` avant transferts, pensions exclues, contre `ilc_li02` après) : taux de pauvreté monétaire des moins de 18 ans, seuil de 60 % de la médiane, **38,6 % avant transferts, 22,8 % après en France** (UE : 32,7 puis 19,6). Les transferts retirent 15,8 points en France contre 13,1 dans l'UE : la dépense sociale réduit plus la pauvreté des enfants qu'ailleurs, mais part d'un niveau avant transferts plus élevé. C'est la réponse la plus directe à « la dépense protège-t-elle ? ».
- **La composante de privation** (`ilc_mdsd11`) : privation matérielle et sociale sévère des moins de 18 ans, 10,0 % en France contre 7,9 % (2025). Distingue la pauvreté de revenu des privations concrètes.
- **Les effectifs** (`unit=THS_PER`) : **3,7 millions d'enfants** en 2025, plus parlant qu'un pourcentage pour un lecteur.
- **Le détail de la dépense** : la carte dit « finance d'abord les retraites et la santé » sans le chiffrer ; voir les jeux ci-dessous.

## Autres sources possibles

- **Dépenses par fonction (COFOG)**, Eurostat `gov_10a_exp`, dimension `cofog99` (80 postes, dont GF10 protection sociale, GF1002 vieillesse, GF1004 famille et enfants, GF07 santé, GF09 enseignement) : en 2024, protection sociale 23,7 % du PIB (UE 19,5), vieillesse 13,4 (UE 10,6), **famille et enfants 2,3 (UE 2,0)**, santé 8,9 (UE 7,3), enseignement 5,1 (UE 4,7). Données françaises provisoires (`p`). https://ec.europa.eu/eurostat/databrowser/view/gov_10a_exp/default/table?lang=fr
- **Prestations de protection sociale par fonction (SESPROS)**, Eurostat `spr_exp_func`, dimension `spfunc` (TOTAL, SICK, DIS, OLD, SRV, FAM, UNE, HOU, EXCL) et 13 unités (dont % du PIB, SPA par habitant) : **prestations famille / enfants 2,23 % du PIB en France contre 2,40 % dans l'UE en 2024, 11e sur 30** ; vieillesse et survie 14,5 % (UE 12,8). Ce chiffre contredit l'image d'une France très dépensière pour les familles ; il exclut les avantages fiscaux (quotient familial) et l'école, d'où l'écart avec COFOG. https://ec.europa.eu/eurostat/databrowser/view/spr_exp_func/default/table?lang=fr
- **Privation spécifique des enfants**, Eurostat `ilc_chmd03` (moins de 16 ans, par diplôme des parents), module triennal : 13,4 % en France en 2024 (UE 13,6), 40,0 % quand les parents ont au plus le brevet. Mesure centrée sur l'enfant (vêtements, livres, loisirs, repas), pas sur le ménage.
- **OCDE, base de données sur la famille** (Family Database, indicateurs CO2.2 pauvreté des enfants, PF1.1 dépenses publiques pour les familles, en espèces, services et avantages fiscaux) : permet d'inclure le quotient familial et de comparer hors Europe. https://www.oecd.org/fr/els/famille/basededonnees.htm (adresse à vérifier).
- **Insee, Revenus fiscaux et sociaux (ERFS)** : taux de pauvreté des enfants selon la définition française (seuil de 60 % de la médiane, revenus fiscaux appariés), plus robuste que SRCV pour la France ; publication annuelle « Les niveaux de vie ».
- **Unicef Innocenti, Report Card 18 (2023)** : pauvreté des enfants dans les pays riches et évolution 2012-2021, avec un classement des politiques. À vérifier pour une édition plus récente.

## Points de relecture

- **Rupture de série** : Eurostat marque la série française d'une rupture en 2020 et en 2022 (drapeau `b`, vérifié par l'API le 30/10/2026). Le saut de 22,5 % (2021) à 27,1 % (2022) ne doit pas être lu comme une hausse réelle ; la trajectoire du dossier relie ces points sans le signaler. Le script ne lit pas les drapeaux.
- **Lien de causalité implicite** : « beaucoup de dépense, des enfants mieux protégés ? » rapproche la dépense publique totale (retraites, santé, intérêts) d'un indicateur sur les enfants. La carte le reconnaît dans sa dernière phrase ; un chiffre de dépense ciblé (famille, ou transferts avant / après) serait plus juste que le total.
- **Chiffre plus parlant possible** : « 31,4 % des 12-17 ans » ou « près d'une personne sur deux dans une famille monoparentale », ou « les transferts sociaux ramènent la pauvreté des enfants de 38,6 % à 22,8 % » (ce dernier nuancerait le verdict « Faux »).
- **Verdict** : le « Faux » porte sur le constat (dépense élevée, pauvreté infantile au-dessus de la moyenne) ; il n'est pas démontré que la dépense « ne protège pas ». À formuler comme un contraste, ce que fait le texte.
- **AROPE n'est pas la pauvreté** : l'indicateur cumule trois critères (revenu, privation, faible intensité de travail). « Menacés de pauvreté ou d'exclusion » est la bonne traduction ; ne pas abréger en « pauvres » ailleurs sur le site.
- **« L'un des deux pays »** : vrai (Finlande 57,5, France 57,3, puis 54,6) ; l'écart avec la Finlande (0,2 point) est dans l'épaisseur des révisions des comptes nationaux.
- **Pays manquants** : Islande et Suisse n'ont pas de valeur 2025 ; le rang est sur 28. La carte le dit.
- **Lien de la source** : la carte ne pointe que vers `ilc_peps01n` ; ajouter `gov_10a_main` si l'on veut que les deux chiffres soient vérifiables en un clic.
- Fragilités relevées par `docs/verification_cartes_accueil.md` (section 6) : toutes corrigées le 30/10/2026, sauf la rupture de série 2022, restée « à vérifier ».
