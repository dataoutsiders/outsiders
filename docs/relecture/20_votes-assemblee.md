# 20. Comment votent les députés ?
> Partie du dossier `/terrains/assemblee` · pas de carte d'accueil · fiche préparée le 30/10/2026
> Le portrait des députés reste dans la [fiche 05](05_assemblee.md).

## Ce que dit le dossier

Cinq parties : qui vote avec qui, avec une matrice par sujet et une carte anonyme des députés ; les alliances selon le sujet ; qui ne vote pas ; le profil à groupe égal ; le territoire et les déserts médicaux.

Messages principaux : trois blocs, et une Droite républicaine à égale distance (77 % avec le RN, 73 % avec Ensemble) ; les alliances changent avec le sujet ; le député médian vote à 23 % des scrutins, mais à 85 % des scrutins solennels ; à groupe égal le profil ne se voit pas dans les votes ; le territoire ne change pas le vote, mais fait venir voter.

## D'où viennent les chiffres

Chaîne : fichiers officiels de l'Assemblée -> `python/tools/build_votes.py` -> `frontend/public/data/showcases/votes-assemblee.json` -> `pages/terrains/AssembleeVotes.jsx`.

| Chiffre | Valeur | Calcul |
|---|---|---|
| Scrutins, votes | 9 335 ; 1 375 596 | d'octobre 2024 à octobre 2026 |
| Accord entre deux groupes | ex. DR et RN 77 % | même position majoritaire, groupes d'au moins 5 votants, au moins 15 scrutins communs |
| Axes de la carte | 28 % et 8 % | décomposition en valeurs singulières, scrutins d'au moins 100 votants où la minorité dépasse 10 % (5 818), députés d'au moins 300 votes (598) |
| Participation médiane | 23 %, dont 19 % sans délégation | 638 députés en mandat pendant au moins 500 scrutins |
| Solennels, ordinaires | 85 % et 24 % | votes / scrutins possibles |
| Sa commission, les autres | 35 % et 21 % | médiane de 621 députés |
| Délégation | 15,4 % des votes | champ officiel `parDelegation` |
| Outre-mer | 10,8 % contre 23,3 % ; −8,4 pts à groupe égal (± 2,7) | 27 députés ; hors Français de l'étranger (classés avec les autres) |
| Désaccord femmes et hommes d'un groupe | 0,4 % (hasard : 0,4 %, de 0,3 à 0,5) | 200 tirages au sort dans chaque groupe |
| Accès aux soins et vote, article 1 | −2,3 pts (± 2,7), non significatif | 236 votants, à groupe égal, pour un écart-type d'accès |
| Accès aux soins et participation | −6,1 pts (± 2,6) | 5 scrutins, à groupe égal, pour un écart-type d'accès |
| Amendements adoptés | Ensemble 52 %, LFI 13 %, RN 12 % | 7 248 amendements, auteur retrouvé pour 94 % |

**Contrôle** : sur les 9 241 scrutins communs avec NosParlementaires, mes comptes de pour, contre et abstention sont identiques à 100 %.

## Les jeux de données

### Scrutins (Assemblée nationale)
- **Page** : https://data.assemblee-nationale.fr/travaux-parlementaires/votes
- **Téléchargement** : `https://data.assemblee-nationale.fr/static/openData/repository/17/loi/scrutins/Scrutins.json.zip`
- **Champs utilisés** : `uid`, `numero`, `dateScrutin`, `typeVote.codeTypeVote` (SPO ordinaire, SPS solennel, MOC motion de censure), `sort.code`, `titre`, `demandeur.texte`, `objet.dossierLegislatif.dossierRef`, `ventilationVotes` par groupe : `organeRef`, puis `decompteNominatif` (`pours`, `contres`, `abstentions`, `nonVotants`) avec `acteurRef`, `parDelegation`, `causePositionVote` (MG gouvernement, PAN présidence de l'Assemblée, PSE présidence de séance).
- **Non utilisés** : `seanceRef`, `sessionRef`, `lieuVote`, `numPlace`, `nombreMembresGroupe`, `positionMajoritaire`, `miseAuPoint` (rectifications de vote), `syntheseVote`.

### Dossiers législatifs (Assemblée nationale)
- **Page** : https://data.assemblee-nationale.fr/travaux-parlementaires/dossiers-legislatifs
- **Téléchargement** : `.../17/loi/dossiers_legislatifs/Dossiers_Legislatifs.json.zip`
- **Utilisés** : `titreDossier.titre` et l'acte `*-COM-FOND` (commission saisie au fond).

### Acteurs, mandats, organes (Assemblée nationale)
- **Téléchargement** : `.../17/amo/tous_acteurs_mandats_organes_xi_legislature/AMO30_tous_acteurs_tous_mandats_tous_organes_historique.json.zip`
- **Utilisés** : civilité, date de naissance, `famSocPro`, mandats (dates, département), groupes, commissions.

### NosParlementaires
- **Page** : https://www.data.gouv.fr/datasets/votes-et-activite-des-parlementaires-francais-17e-legislature-nosparlementaires
- **Usage limité** : `dossier_ref` pour les scrutins sans lien vers un dossier dans le fichier officiel (seuls 38 % l'ont), et contrôle des comptes.

### Accès aux généralistes
Voir la [fiche 17](17_acces-soins.md) : `apl_mg` par département.

## Ce qu'on n'exploite pas encore

- **Le Sénat** : 2 176 scrutins et 756 812 votes depuis 2017, chez NosParlementaires.
- **Les mises au point** : un député qui rectifie son vote après coup, signal intéressant.
- **Le lieu et l'heure** : la séance permettrait de relier la participation au moment du vote.
- **Les amendements déposés** (open data de l'Assemblée) : les votes publics n'en montrent qu'une partie.
- **Le temps** : l'accord par semestre est calculé (`evolution`) mais non affiché.
- **La 16e législature**, pour comparer.

## Autres sources possibles

- **HATVP** : déclarations d'intérêts, à manier avec beaucoup de précaution.
- **Circonscriptions** : un lien circonscription-communes permettrait de tester le territoire plus finement que le département.

## Points de relecture

1. **Pas de classement individuel** : décision prise par moi, et écrite sur la page. Tu demandais « qui ne participe pas ». Les votes sont publics et d'autres sites publient ces classements. Je pense qu'il faut rester aux agrégats, mais c'est ton choix éditorial.
2. **« Trois blocs »** : formule de synthèse, à valider.
3. **Noms des groupes** : « Ensemble » pour Ensemble pour la République, « UDR » pour UDDPLR, « PS » pour Socialistes et apparentés. Le reste du dossier emploie les sigles (EPR, SOC) : à harmoniser.
4. **982 scrutins non classés par sujet (10,5 %)** : ils viennent surtout de textes passés par une commission spéciale ou une autre instance, dont la loi de simplification (438), les violences sexuelles et sexistes (230), la protection des enfants (140). Ils sont exclus de la lecture par sujet : à rattacher à la main à une commission, ou à laisser de côté ?
5. **Sujet = commission au fond** : un texte peut toucher plusieurs sujets. La loi de finances compte tout entière en « Finances ».
6. **Délégation** : j'écris « par un député absent de l'hémicycle ». À vérifier : la délégation concerne-t-elle toujours une absence de l'hémicycle ?
7. **Participation** : seuil de 500 scrutins pendant le mandat. Les députés en fonction d'un groupe ou de la présidence d'une commission ne sont pas isolés.
8. **Motions de censure** : seuls les votes pour sont comptés ; la participation de 28 % n'a donc pas de sens et n'est pas affichée.
9. **Déserts médicaux** : une seule loi, cinq scrutins, mesure au département. Le vote final n'a que 105 votants. À présenter comme une piste, pas un résultat établi.
10. **Prudence sur l'accord** : scrutins demandés, surtout par le RN (2 740) et LFI (2 166). Les votes à main levée, souvent consensuels, n'y sont pas.
11. **Profil** : le test porte sur les positions opposées. Il ne dit rien des amendements déposés ni des prises de parole.
12. **Âge** : calculé en 2026 pour tous, y compris pour les députés sortis.
13. **Amendements** : un seul auteur retenu, le premier cité. Les amendements identiques comptent une fois.

**Décision de l'usager :**
