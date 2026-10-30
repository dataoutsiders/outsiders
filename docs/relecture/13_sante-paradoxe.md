# 13. La France, bon élève de la santé en Europe ?
> Carte `sante-paradoxe` · verdict « Vrai, mais » · dossier /international · fiche préparée le 30/10/2026

## Ce qu'affiche la carte

- **Rubrique** : Santé ; unité « Pays » ; couleur `#0EA5E9`.
- **Question** : « La France, bon élève de la santé en Europe ? »
- **Verdict** : `vraiMais`.
- **Chiffre** : **24e / 30**, « pour la mortalité infantile : 4,1 ‰, au-dessus de la moyenne européenne (3,5) ».
- **Texte** : « L'espérance de vie française reste dans le haut du classement (83,0 ans, 9e sur 30). Mais la mortalité infantile, meilleure que la moyenne européenne jusqu'en 2014, est passée au-dessus : seuls 6 pays européens font pire. Les comparaisons dépendent en partie de la façon dont chaque pays enregistre les naissances très prématurées. »
- **Source citée** : « Eurostat, mortalité infantile et espérance de vie (2024) », lien vers la vue `demo_minfind` du databrowser.
- **Lien** : « Voir la trajectoire du décrochage » vers `/international` (le bouton n'ouvre pas directement la section `#trajectoires`).

## Ce que dit le dossier

Page `frontend/src/pages/international/International.jsx` (« Où se situe la France ? »).

- **En bref** : « 24ᵉ/30 pour la mortalité infantile, longtemps meilleure que la moyenne européenne ».
- **Carte d'identité** : dot-plots espérance de vie (France 83,0, 9ᵉ sur 30, UE27 81,5, de 75,8 en Bulgarie à 84,2 en Suisse) et mortalité infantile (France 4,1 ‰, 24ᵉ sur 30, UE27 3,5, de 1,4 en Estonie et en Islande à 6,6 en Roumanie).
- **Histoire « Le paradoxe sanitaire »** : « Espérance de vie au 9ᵉ rang sur 30 (83 ans), mais mortalité infantile 24ᵉ sur 30 : meilleure que la moyenne européenne jusqu'en 2014, la France est passée au-dessus en 2015 et l'écart s'est creusé depuis », avec la réserve sur les grands prématurés.
- **Trajectoires** (mortalité infantile par défaut) : France et UE27 depuis 1996 ; légende : « nettement meilleure que la moyenne européenne dans les années 2000, la mortalité infantile française croise la moyenne UE vers 2015, puis remonte (3,5 ‰ en 2012, 4,1 ‰ en 2024) pendant que l'Europe continue de baisser ». Espérance de vie : série France depuis 1998, UE27 depuis 2002.
- **Nuage dépenses × résultat** : on peut mettre l'espérance de vie ou la mortalité infantile en ordonnée face aux dépenses publiques totales.
- Aide de l'indicateur (`decoupages.js`) : « La France, longtemps meilleure que la moyenne européenne, est passée au-dessus en 2015. Les comparaisons dépendent en partie de l'enregistrement des naissances très prématurées. 2024. »

## D'où viennent les chiffres

Chaîne : API Eurostat -> `python/tools/build_international.py` -> `frontend/public/data/decoupages/pays.json` -> `International.jsx` ; la carte de l'accueil recopie en dur les valeurs.

Paramètres : `esperance_vie` = `demo_mlexpec`, `sex=T`, `age=Y_LT1`, `time=2024` ; `mortalite_infantile` = `demo_minfind`, `indic_de=INFMORRT`, `time=2024`.

| Chiffre de la carte | Valeur dans `pays.json` | Calcul |
|---|---|---|
| 4,1 ‰ | mortalité infantile France 2024 | Eurostat |
| 3,5 | `references.mortalite_infantile` | agrégat EU27_2020 |
| 24e / 30 | rang favorable (`rangFrance`, sens « bas ») | 6 pays au-dessus : Roumanie 6,6, Slovaquie 5,9, Luxembourg 5,3, Malte 5,0, Bulgarie 4,5, Danemark 4,3 |
| « seuls 6 pays font pire » | idem | |
| 83,0 ans, 9e sur 30 | espérance de vie France 2024 | **à égalité avec Malte (83,0)** : le rang 9 ou 10 dépend de l'ordre de tri (la France est listée en premier dans le JSON) |
| « jusqu'en 2014 » | série : 2014 France 3,5 / UE 3,6 ; 2015 France 3,7 / UE 3,6 | `series.mortalite_infantile` |

## Les jeux de données

### Espérance de vie par âge et sexe (Eurostat)
- **Producteur** : Eurostat, tables de mortalité calculées à partir des décès et populations transmis par les instituts (Insee pour la France).
- **Code** : `demo_mlexpec`.
- **Millésime utilisé** : 2024 (France provisoire, drapeau `p`). Dernier disponible : 2024 ; 2025 attendu au printemps 2027 (`docs/millesimes_20261030.md`).
- **Page** : https://ec.europa.eu/eurostat/databrowser/view/demo_mlexpec/default/table?lang=fr
- **API** : https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/demo_mlexpec?format=JSON&lang=fr&sex=T&age=Y_LT1&time=2024
- **Géographie** : pays européens et agrégats ; le jeu régional voisin `demo_r_mlifexp` donne les régions NUTS 2.

| colonne ou dimension | sens / modalités | utilisée ? |
|---|---|---|
| `unit` | YR (années) | oui |
| `sex` | T, M, F | oui : T. Non : femmes 85,8 (3e sur 30), hommes 80,2 (13e sur 30) |
| `age` | 97 modalités : moins de 1 an (naissance), 1 an à 94 ans, 85 ans ou plus, 95 ans ou plus | oui : naissance. Non : **65 ans (France 21,9 ans, premier rang des 30, à égalité avec l'Espagne)** |
| `geo`, `time` | pays, séries depuis les années 1960 selon les pays | oui : 2024 et série depuis 1998 |

### Taux de mortalité infantile (Eurostat)
- **Producteur** : Eurostat, à partir de l'état civil (Insee).
- **Code** : `demo_minfind`.
- **Millésime utilisé** : 2024. Dernier disponible : 2024 (mise à jour du 07/10/2026).
- **Page** : https://ec.europa.eu/eurostat/databrowser/view/demo_minfind/default/table?lang=fr
- **API** : https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/demo_minfind?format=JSON&lang=fr&indic_de=INFMORRT&time=2024

| colonne ou dimension | sens / modalités | utilisée ? |
|---|---|---|
| `unit` | RT (taux pour 1 000 naissances vivantes) | oui |
| `indic_de` | INFMORRT (infantile, moins d'un an) ; NEOMORRT (néonatale, moins de 28 jours) ; ENEOMORRT (néonatale précoce, moins de 7 jours) ; LFOEMORRT (mortinatalité) ; PERIMORRT (périnatale) | oui : INFMORRT. Non : néonatale (France 2,9 ‰ en 2024, 17e sur 21 pays renseignés, pas d'agrégat UE), néonatale précoce (2,0 ‰). Mortinatalité et périnatale : **série française arrêtée en 2010**, avec un saut en 2002 (changement de règle d'enregistrement des enfants sans vie) |
| `geo`, `time` | pays, séries longues | oui : 2024 et série depuis 1996 |

## Ce qu'on n'exploite pas encore

- **L'espérance de vie à 65 ans** (`demo_mlexpec`, `age=Y65`) : 21,9 ans en France, **premier rang des 30 pays** (à égalité avec l'Espagne), contre 20,2 dans l'UE. C'est le vrai point fort français, plus parlant que le 9e rang à la naissance.
- **Le sexe** : les Françaises sont 3es sur 30 (85,8 ans), les Français 13es (80,2). La moyenne « deux sexes » cache cet écart.
- **La mortalité néonatale** (`NEOMORRT`) : 2,9 ‰ en France, en hausse depuis 2012 (2,4) ; l'essentiel de la hausse de la mortalité infantile se joue dans le premier mois. Pas d'agrégat UE, comparaison sur 21 pays seulement.
- **La lecture par la fin de vie et par l'accès aux soins** : voir ci-dessous, la mortalité évitable par les soins place la France parmi les meilleurs pays.

## Autres sources possibles

- **Mortalité évitable grâce aux traitements et à la prévention**, Eurostat `hlth_cd_apr` (dimensions `mortalit` TOTAL / PRVT / TRT, `icd10` 98 causes, `sex`, `unit` nombre ou taux standardisé pour 100 000) : en 2023, **mortalité évitable par les traitements 58,8 en France contre 86,8 dans l'UE, 6e plus faible des 30** ; mortalité évitable par la prévention 127,2 contre 150,9, 13e. Mesure la plus proche de la performance du système de soins ; elle irait dans le sens du « Vrai » et nuance le « mais ». https://ec.europa.eu/eurostat/databrowser/view/hlth_cd_apr/default/table?lang=fr
- **Années de vie en bonne santé**, Eurostat `hlth_hlye` (`hlth_hle` : espérance de vie et années en bonne santé à 0, 50 et 65 ans, en années ou en % de l'espérance de vie ; `sex`) : à la naissance, 63,6 ans en France contre 65,2 dans l'UE en 2024 (16e sur 28) ; à 65 ans, 10,9 contre 10,3. Indicateur déclaratif (question sur les limitations d'activité), avec ruptures de série (drapeaux `b`) : comparaisons fragiles, mais la France n'y est pas « bon élève ».
- **Euro-Peristat, European Perinatal Health Report** : la référence pour comparer la mortalité périnatale et néonatale en tenant compte des règles d'enregistrement (seuil de 22 semaines, interruptions médicales de grossesse). Dernière édition à vérifier (données 2015-2019 publiées en 2022). https://www.europeristat.com
- **Insee, Bilan démographique 2025** (Insee Première n° 2087, janvier 2026) : mortalité infantile française 2025 provisoire, avant Eurostat. https://www.insee.fr/fr/statistiques/8719824
- **Inserm / Drees, enquête nationale périnatale et travaux sur la hausse de la mortalité infantile** (analyse de la hausse depuis 2012, publiée dans *The Lancet Regional Health Europe* en 2022) : éléments d'explication (part des grands prématurés, âge des mères, inégalités territoriales, outre-mer). Référence exacte à vérifier.
- **OCDE et Commission européenne, Health at a Glance: Europe** et **profils de santé par pays (State of Health in the EU)** : synthèse comparée (dépenses de santé, accès, résultats), profil France tous les deux ans.
- **Dépenses de santé**, Eurostat `gov_10a_exp` (COFOG GF07 : 8,9 % du PIB en France contre 7,3 en 2024) ou `hlth_sha11_hf` (comptes de la santé) : pour le nuage « que rapporte la dépense ? », une dépense de santé serait plus juste que la dépense publique totale.

## Points de relecture

- **Formulation** : la question (« bon élève de la santé ») porte sur la santé ; les deux chiffres sont des indicateurs de mortalité. Le « Vrai » repose sur l'espérance de vie (9e sur 30), le « mais » sur la mortalité infantile. Ajouter l'espérance de vie à 65 ans ou la mortalité évitable renforcerait le « Vrai » ; ajouter les années en bonne santé renforcerait le « mais ».
- **Égalité avec Malte** : 83,0 ans pour les deux ; la France est 9e ou 10e selon le départage. Écrire « 9e ou 10e » ou « dans le premier tiers ».
- **Dates du décrochage** : la carte dit « jusqu'en 2014 », l'histoire « passée au-dessus en 2015 », la légende de la trajectoire « croise vers 2015 » et `docs/projet.md` « jusqu'en 2012, au-dessus depuis 2015 ». Les séries : 2013 (3,6 / 3,7), 2014 (3,5 / 3,6), 2015 (3,7 / 3,6). Harmoniser sur 2014 / 2015 ; noter que les écarts de 0,1 point sont dans l'arrondi.
- **« Seuls 6 pays font pire »** : parmi eux, le Danemark (4,3) et le Luxembourg (5,3, petits effectifs) ; les écarts de 0,1 à 0,2 ‰ entre pays proches ne sont pas significatifs. Un rang 24e sur 30 surinterprète des différences minimes ; « parmi le tiers le moins bon » serait plus prudent.
- **Enregistrement des naissances** : la réserve est présente. On peut la préciser : les règles d'enregistrement des naissances vivantes très prématurées (en France, critère de viabilité de 22 semaines d'aménorrhée ou 500 g, à vérifier dans la circulaire en vigueur) diffèrent entre pays, ce qui pèse sur la comparaison entre pays sans expliquer la hausse française dans le temps, qui est mesurée avec les mêmes règles depuis 2008 environ (à vérifier).
- **Moyenne UE en hausse en 2024** (3,3 à 3,5) : à vérifier avant de dire que « l'Europe continue de baisser » (légende de la trajectoire).
- **Données provisoires** : les valeurs françaises 2024 d'espérance de vie sont provisoires (`p`).
- **Lien du bouton** : « Voir la trajectoire du décrochage » mène en haut de `/international` ; une ancre `#trajectoires` amènerait au graphique.
