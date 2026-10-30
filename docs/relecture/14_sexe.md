# 14. L'égalité femmes-hommes, c'est réglé ?
> Carte `sexe` · verdict « Faux » · dossier /explorer/sexe · fiche préparée le 30/10/2026

## Ce qu'affiche la carte

- **Rubrique** : Travail ; unité « Genre » ; couleur `#EC4899`.
- **Question** : « L'égalité femmes-hommes, c'est réglé ? »
- **Verdict** : `faux`.
- **Chiffre** : **−39 %**, « de pension de droit direct pour les femmes de 65 ans ou plus (981 € nets contre 1 600 €, en 2019) ».
- **Texte** : « L'écart de salaire (13 % en équivalent temps plein) paraît se réduire ; le temps partiel et les carrières interrompues contribuent à le creuser au moment de la retraite. Les pensions de réversion ramènent l'écart sur la pension totale à 24 %. »
- **Source citée** : « Insee, Femmes et hommes, l'égalité en question (édition 2022, données 2019) », lien https://www.insee.fr/fr/statistiques/6047747
- **Lien** : « Voir tous les écarts » vers `/explorer/sexe`.

## Ce que dit le dossier

Page générique `UnitView` (`/explorer/sexe`), configurée dans `frontend/src/config/decoupages.js` (entrée `sexe`, titre « Sexe », intro « Femmes et hommes comparés sur le salaire, l'emploi, la retraite et l'espérance de vie ») et alimentée par `frontend/public/data/decoupages/sexe.json`.

| Indicateur (thème) | Femmes | Hommes | Source affichée |
|---|---|---|---|
| Salaire net en équivalent temps plein (Revenu) | 2 514 € | 2 891 € | Insee Focus n° 377 (2024), secteur privé |
| Taux d'emploi des 15-64 ans (Emploi) | 66,7 % | 71,9 % | Insee, enquête Emploi 2025 |
| Temps partiel, salariés hors apprentis (Emploi) | 26,6 % | 8,4 % | Insee, enquête Emploi 2025 |
| Espérance de vie à la naissance (Santé) | 85,9 ans | 80,3 ans | Insee, Bilan démographique 2025 (provisoire) |
| Pension de retraite, droit direct (Retraite) | 981 € | 1 600 € | Insee, Femmes et hommes (2019) |

- Heatmap colorée par ligne, colonne « Écart » (maximum / minimum : ×1,63 pour la pension), mode Fiche par sexe.
- Note du JSON : « Femmes et hommes (sexe administratif). […] Les millésimes diffèrent selon l'indicateur (de 2019 à 2025). »
- Aide de la pension : « Pension moyenne de droit direct, hors réversion (la pension de réversion réduit l'écart). » Ni l'âge (65 ans ou plus), ni le net, ni l'année n'y figurent ; l'année est dans le libellé de la source.
- Pas de valeur de référence (`references` absent).

## D'où viennent les chiffres

Chaîne : publications Insee (pages web et classeurs xlsx) -> **saisie à la main** dans `frontend/public/data/decoupages/sexe.json` (aucun script) -> `UnitView` -> carte de l'accueil, dont le texte est écrit en dur dans `Home.jsx`.

| Chiffre de la carte | Origine |
|---|---|
| 981 € et 1 600 € | Insee, fiche « Retraites et minimum vieillesse », figure 1 : pension nette mensuelle moyenne de droit direct, retraités de 65 ans ou plus, 2019 (Drees, modèle ANCETRE 2019) |
| −39 % | (981 − 1 600) / 1 600 = −38,7 %, arrondi, calcul Outsiders |
| 24 % (pension totale) | même figure : pension totale (droit direct + réversion + majoration pour trois enfants) 1 272 € contre 1 674 €, écart −24 % publié par l'Insee |
| 13 % (salaire EQTP) | Insee Focus n° 377, figure 2 : 1 − 2 514 / 2 891 = 13,0 % |
| « paraît se réduire » | non chiffré sur la carte ni sur la page ; Focus 377 : écart EQTP de 22,1 % en 1995 à 14,0 % en 2024 (salaire annuel) |

Contrôle du 30/10/2026 : classeur Insee `IREF_FH22-F17.xlsx` téléchargé, valeurs identiques.

## Les jeux de données

### Retraites et minimum vieillesse (Insee, Femmes et hommes, l'égalité en question, édition 2022)
- **Producteur** : Insee, d'après la Drees (modèle ANCETRE, enquêtes annuelles auprès des caisses de retraite EACR, échantillon interrégimes de retraités EIR).
- **Millésime utilisé** : données 2019 (édition parue le 03/03/2022). Pas d'édition plus récente de cette fiche Insee repérée.
- **Page** : https://www.insee.fr/fr/statistiques/6047747
- **Téléchargement** : https://www.insee.fr/fr/statistiques/fichier/6047747/IREF_FH22-F17.xlsx (vérifié le 30/10/2026)
- **Géographie** : France (retraités résidant en France ou à l'étranger pour la figure 1).

| colonne ou dimension | sens / modalités | utilisée ? |
|---|---|---|
| Figure 1, sexe | femmes, hommes | oui |
| Figure 1, composante | pension de retraite totale ; droit direct ; réversion ; majoration pour 3 enfants ou plus | oui : droit direct (chiffre), totale (texte, 24 %). Non : réversion (256 € contre 23 €), majoration |
| Figure 1, âge | 65-69, 70-74, 75-79, 80-84, 85 ans ou plus, ensemble 65 ans ou plus | oui : ensemble. Non : **par âge, l'écart de droit direct va de −31 % (65-69 ans : 1 126 € contre 1 628 €) à −49 % (85 ans ou plus : 765 € contre 1 499 €)** |
| Figure 1, montants | nets mensuels, 2019, non corrigés de la mortalité différentielle | oui |
| Figure 2, série 2004-2019 | écart en %, droit direct et pension totale, résidents en France ou résidents en France et à l'étranger, montants **bruts** | non : résidents en France, droit direct 50,1 % (2004) puis 40,5 % (2019) ; pension totale 37,0 puis 29,8 % |
| Figure 3 | âge de liquidation des retraités nés en 1950, par sexe | non : femmes 60,8 ans, hommes 59,9 ; 18,5 % des femmes liquident à 65 ans contre 9,4 % des hommes |

### Écart de salaire entre femmes et hommes en 2024 (Insee Focus n° 377)
- **Producteur** : Insee (bases tous salariés, déclarations sociales nominatives) ; paru le 26/02/2026.
- **Millésime** : 2024 (dernier disponible).
- **Page** : https://www.insee.fr/fr/statistiques/8743657 ; **données** : https://www.insee.fr/fr/statistiques/fichier/8743657/if377.xlsx
- **Champ** : salariés du secteur privé, hors agriculture et particuliers employeurs.

| colonne ou dimension | sens / modalités | utilisée ? |
|---|---|---|
| Salaire mensuel net moyen en EQTP, par sexe | figure 2 | oui : 2 514 et 2 891 € |
| Séries 1995-2024 (figure 1) | revenu salarial, salaire EQTP, volume de travail, en euros constants | non : revenu salarial (tous temps de travail) **écart 21,8 %** ; EQTP 14,0 % ; volume de travail 9,1 % ; en 1995 : 33,7 / 22,1 / 14,9 % |
| Par catégorie socioprofessionnelle | cadres, professions intermédiaires, employés, ouvriers | non : 14,8 / 11,2 / 1,9 / 11,7 % |
| Par âge | moins de 25 ans à 60 ans ou plus | non : 3,2 % avant 25 ans, **24,1 % à 60 ans ou plus** |
| Par taille d'entreprise et par secteur | 7 tailles, 8 secteurs | non |
| À poste comparable | même emploi, même établissement | non : **3,6 %** |
| Vingt professions les plus fréquentes, par sexe | figure 3 | non |
| Part des femmes par centième de salaire | figure 4 | non : 42 % des EQTP, 24 % au-dessus du 99e centile |
| Encadré situation familiale (2022) | nombre d'enfants, âge du plus jeune | non : écart EQTP 5,8 % sans enfant, 28,2 % avec trois enfants ou plus |

### Enquête Emploi 2025 (Insee, Emploi, chômage, revenus du travail, édition 2026)
- **Fiches** : « Caractéristiques des personnes en emploi » https://www.insee.fr/fr/statistiques/8733041 (taux d'emploi) et « Temps partiel » https://www.insee.fr/fr/statistiques/8733075 ; parues le 02/07/2026.
- **Utilisé** : taux d'emploi des 15-64 ans et part de temps partiel des salariés, par sexe.
- **Non utilisé (à relever sur les fiches)** : ventilations par âge, diplôme, catégorie, et pour le temps partiel la part de temps partiel subi et les motifs (garde d'enfants).

### Bilan démographique 2025 (Insee Première n° 2087)
- **Page** : https://www.insee.fr/fr/statistiques/8719824 ; espérance de vie à la naissance par sexe, provisoire. **Non utilisé** : espérance de vie à 60 ans par sexe.

### Les retraités et les retraites (Drees, Panoramas), source de remplacement en suspens
- **Édition 2025** (parue le 31/07/2025, données fin 2023) : écart de pension de droit direct de **38 %** pour les résidents en France (majoration pour enfants comprise), contre 50 % en 2004 ; **25 %** avec la réversion. Fiches utiles : 05 « Le niveau des pensions », 06 « Les écarts de pensions de droit direct entre générations », 03 « Les effectifs de retraités de droit dérivé », 11 « Les durées de carrière ». https://drees.solidarites-sante.gouv.fr/publications-communique-de-presse-documents-de-reference/250731_PANORAMAS-retraites
- **Édition 2026** (données 2024) : −37 % en droit direct, −25 % avec la réversion selon `docs/millesimes_20261030.md` ; page non retrouvée sur le site de la Drees, vue dans une reprise secondaire.
- **Changement de définition** : la Drees publie des montants **bruts**, sur **l'ensemble des retraités** (et non les 65 ans ou plus), résidents en France. Le chiffre de la carte (net, 65 ans ou plus, résidents en France ou à l'étranger, 2019) n'est pas comparable terme à terme.
- **Téléchargement** : les classeurs xlsx des fiches n'ont pas pu être lus le 30/10/2026 (requête rejetée par le site de la Drees en téléchargement automatique) ; leurs colonnes sont à relever à la main. Les données de l'EACR et d'ANCETRE sont annoncées en open data (data.drees), sans lien sur la page.

## Ce qu'on n'exploite pas encore

- **L'écart par âge, donc par génération** (figure 1) : −31 % à 65-69 ans contre −49 % à 85 ans ou plus. L'écart moyen de −39 % mélange des générations très différentes ; les plus jeunes retraitées sont nettement moins pénalisées. Phrase utile : « l'écart se réduit de génération en génération, mais reste de près d'un tiers chez les jeunes retraitées ». La fiche 06 de la Drees suit les générations de façon plus rigoureuse.
- **La tendance** (figure 2) : de 50 % à 40,5 % d'écart de droit direct entre 2004 et 2019 (brut, résidents en France), puis 38 % en 2023 selon la Drees. Le verdict « Faux » tient, mais l'écart recule régulièrement.
- **Le revenu salarial** (Focus 377) : 21,8 % d'écart tous temps de travail confondus, contre 13 à 14 % en EQTP. C'est le chiffre qui relie le salaire à la retraite (la pension dépend du revenu effectivement perçu, pas d'un équivalent temps plein).
- **L'écart à poste comparable** (3,6 %) et **l'effet des enfants** (5,8 % sans enfant, 28,2 % avec trois enfants ou plus) : répondent directement à « d'où vient l'écart ? » sans phrase causale non chiffrée.
- **L'âge** côté salaires : l'écart passe de 3 % avant 25 ans à 24 % après 60 ans (coupe transversale : effet d'âge et de génération mêlés).
- **Le temps partiel subi** et les motifs du temps partiel (enquête Emploi) : étayeraient « le temps partiel contribue à creuser l'écart ».

## Autres sources possibles

- **Eurostat, écart de pension entre femmes et hommes** (`ilc_pnp13`, dimensions `age` : 65-74, 65-79, 65 ans ou plus ; `unit` : pourcentage) : France 26,4 % en 2025 (65-79 ans, toutes pensions, EU-SILC), UE 24,2 % ; en 2024, 19e sur 29 pays (du plus faible au plus fort écart). Permet de situer la France en Europe ; rupture française en 2022 (`b`). https://ec.europa.eu/eurostat/databrowser/view/ilc_pnp13/default/table?lang=fr
- **Eurostat, écart de rémunération non ajusté** (`earn_gr_gpgr2`, par secteur NACE) : France 11,8 % en 2024 (provisoire), UE 11,1 %. Définition horaire brute, différente de l'EQTP de l'Insee.
- **Eurostat, taux de remplacement agrégé des pensions par sexe** (`ilc_pnp3`).
- **Drees, data.drees** : séries de l'EACR (montants par régime, sexe, génération) et du modèle ANCETRE, à rechercher sur https://data.drees.solidarites-sante.gouv.fr
- **Conseil d'orientation des retraites (COR), rapport annuel** : indicateurs de suivi, dont le rapport de pension femmes / hommes par génération, avec projections. https://www.cor-retraites.fr
- **Insee, Femmes et hommes, l'égalité en question** : une édition plus récente que 2022 n'a pas été repérée ; à vérifier sur insee.fr avant de trancher entre Insee et Drees.
- **Insee, enquête Emploi du temps** (2025-2026, résultats à vérifier) : partage du travail domestique et parental, cause documentée des carrières interrompues.

## Points de relecture

- **Mise à jour en suspens** : choisir entre garder la donnée Insee 2019 (net, 65 ans ou plus) et passer à la Drees (édition 2025 données 2023, ou 2026 données 2024 : brut, ensemble des retraités, −38 % ou −37 %). Le chiffre de la carte bougerait peu (−39 à −37 ou −38 %), mais le libellé, les montants, l'aide de l'indicateur et la source doivent changer ensemble. Ne pas mélanger un montant net et un écart brut.
- **Kicker « Travail »** : le chiffre porte sur la retraite ; « Retraite » ou « Revenus » serait plus juste.
- **Unité « Genre »** : le découpage s'appelle « Sexe » et la note parle de sexe administratif ; aligner le libellé de la carte.
- **« Paraît se réduire »** : non étayé par un chiffre sur la carte ni sur la page ; la série du Focus 377 (22,1 % en 1995, 14,0 % en 2024 en EQTP annuel) le permettrait. Attention aux deux mesures EQTP de la même publication : 13,0 % (mensuel net, figure 2) et 14,0 % (annuel, figure 1).
- **Causalité** : « le temps partiel et les carrières interrompues contribuent à le creuser » est documenté par la littérature mais pas montré par les chiffres affichés ; les écarts « à poste comparable » et selon le nombre d'enfants (Focus 377) donneraient une base chiffrée.
- **Chiffre plus parlant possible** : « −31 % pour les femmes de 65 à 69 ans, −49 % après 85 ans » (montre à la fois l'ampleur et le recul), ou « 22 % de revenu salarial en moins » côté travail.
- **Champ de la pension** : 65 ans ou plus ayant au moins un droit direct, résidents en France ou à l'étranger ; les retraitées ne touchant qu'une réversion sont exclues. L'aide de l'indicateur ne le dit pas.
- **Hétérogénéité des millésimes** sur la page (2019 à 2025) : signalée dans la note ; la pension est la plus ancienne.
- **Espérance de vie** : « le seul indicateur où les femmes sont devant » (aide) ; la pension étant versée plus longtemps aux femmes, un écart de pension cumulé sur la retraite serait plus faible que l'écart mensuel (la note Insee rappelle que les données ne sont pas corrigées de la mortalité différentielle).
