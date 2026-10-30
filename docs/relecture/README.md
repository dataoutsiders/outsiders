# Relecture des cartes de l'accueil, une par une

> Fiches préparées le 30/10/2026, une par carte, dans l'ordre du carrousel. Chacune donne : ce qu'affiche la
> carte et ce que dit le dossier, le chemin de chaque chiffre (source, fichier, script, page), **chaque jeu de
> données avec ses liens de téléchargement et toutes ses colonnes** (utilisées ou non), ce qu'on n'exploite
> pas encore, d'autres sources possibles et les points à relire.
> Méthode : l'usager relit une carte, tranche ; on corrige ; carte suivante. Noter la décision en bas de la fiche.

## Déjà corrigé sur le site le 30/10/2026 (relevé pendant la préparation)

- **Assemblée** : la diversité des noms était affichée pour des groupes de moins de 30 noms reconnus (pour deux
  groupes, 14 noms et 7,1 %, soit un seul député, identifiable). Valeurs masquées sous 30 noms (GDR, LIOT, HOR,
  UDDPLR, NI, collaborateurs des NI), règle écrite dans `build_assemblee.py`. « Collaborateurs plus jeunes »
  retiré : l'âge des collaborateurs n'est pas publié.

## Défauts en ligne à corriger lors de la relecture

- **11 Public, privé** : « l'écart le plus grand de métropole » n'est vrai qu'en moyenne simple des collèges ;
  avec les valeurs départementales officielles, la Seine-Saint-Denis est 3e.
- **01 Ségrégation** : sur la fiche d'une ville, la valeur affichée vient d'une mesure (carreaux) et la couleur
  d'une autre (écart entre IRIS) ; le « × 1,6 » de la carte n'est pas la mesure qui classe les villes.
- **03 Sport** : le dossier garde deux formules retirées de la carte (« l'absence des autres sports »,
  « des terrains saturés »).
- **06 Dépense publique et enfants** : rupture de série Eurostat en 2022 (le saut de 22,5 % à 27,1 % n'est pas
  une hausse réelle), à signaler si une évolution est montrée.
- **08 Information des jeunes** : aucun script ne produit `age.json` ; la 2e édition Arcom change les tranches
  d'âge (le repère « 70 ans et plus » disparaît).

## Sommaire et piste principale de chaque fiche

| # | Carte | Piste la plus prometteuse |
|---|---|---|
| [01](01_segregation.md) | Riches et pauvres vivent-ils séparés ? | Un repère absolu plutôt qu'un classement relatif (62 % des habitants des 997 villes en carreau mixte, 9 % en carreau très pauvre) ; concentration de la pauvreté avec des colonnes déjà téléchargées. La ville classée 1re n'a que 8 IRIS |
| [02](02_revenus.md) | La banlieue décroche ? | Repartir du fichier Insee original pour 2014 ; ajouter D1, D9 et le taux de pauvreté pour savoir si une commune monte par l'arrivée des aisés ou le départ des modestes |
| [03](03_sport.md) | Le foot, sport des quartiers ? | Compter les city-stades et terrains à 5 (25 634) dans le ratio par terrain ; chiffre plus parlant : 47 % des licences masculines sont du foot en quartier prioritaire, 21 % ailleurs |
| [04](04_elus.md) | La politique locale se diversifie ? | Comparer 2020 et 2026 à âge égal grâce aux dates de naissance (l'indice monte fortement avec la génération) |
| [05](05_assemblee.md) | Les députés ressemblent aux Français ? | L'archive historique de l'Assemblée (depuis 1997) pour répondre par une évolution, pas une photo ; documenter le repère « 7 % de la population » |
| [06](06_etat-enfants.md) | Beaucoup de dépense publique, des enfants mieux protégés ? | Mesurer l'effet des transferts (pauvreté des enfants 38,6 % avant, 22,8 % après) ; 12-17 ans (31,4 %) et familles monoparentales (48,6 %) |
| [07](07_pisa.md) | La France décroche dans PISA ? | Un chiffre depuis 2018 (−38 contre −27), moins dépendant de l'année de départ que −53 / −33 |
| [08](08_age.md) | Les jeunes ne s'informent plus ? | Questions non exploitées : évitement de l'actualité (environ 22 % des 18-24 ans, à revérifier), évolution des pratiques, défiance envers les médias ; verdict « Faux, mais » plus juste |
| [09](09_selectivite.md) | La prépa, la formation la plus difficile d'accès ? | Isoler les licences non sélectives avec `select_form` (42 % contre 33 % affichés) ; vérifier une possible rupture du taux d'accès entre 2024 et 2025 |
| [10](10_auto-ecoles.md) | Le meilleur taux fait la meilleure auto-école ? | Colonnes non exploitées : passages par candidat, conduite accompagnée et supervisée ; verdict « Faux » discutable (68 % du meilleur quart y restent) |
| [11](11_ecole.md) | Public, privé : les mêmes élèves ? | Indicateurs DEPP de ségrégation entre collèges (élèves défavorisés : 49 % dans le public, 15 % dans le privé en Seine-Saint-Denis) ; corriger « le plus grand de métropole » |
| [12](12_esperance.md) | Face à la santé, tous égaux ? | L'écart selon le diplôme (8 ans chez les hommes) et selon le niveau de vie (13 ans, Insee décembre 2025) ; montrer aussi les femmes |
| [13](13_sante-paradoxe.md) | La France, bon élève de la santé en Europe ? | Espérance de vie à 65 ans (1re des 30, à égalité avec l'Espagne) et mortalité évitable par les soins (6e plus faible) pour appuyer le « vrai » |
| [14](14_sexe.md) | L'égalité femmes-hommes, c'est réglé ? | L'écart de pension par âge (−31 % à 65-69 ans, −49 % après 85 ans) et sa baisse (50 % en 2004, 38 % en 2023) ; si passage à la Drees, changer ensemble définition, montants et source |
| [15](15_hlm.md) | Les HLM sont là où la France est pauvre ? | Part de HLM selon le niveau de vie de la population (environ 25 % pour le cinquième le plus modeste, 10 % pour le plus aisé, calcul à refaire) ; inventaire SRU 2026 |
| [16](16_outsiders.md) | Les lycées des territoires modestes font moins bien que prévu ? | Passer à l'échelle des lycées : 38 % des lycées publics du tiers le plus modeste font mieux que prévu, contre 25 % du tiers le plus favorisé |

## Décisions de relecture

| # | Date | Décision | Fait ? |
|---|---|---|---|
| | | | |
