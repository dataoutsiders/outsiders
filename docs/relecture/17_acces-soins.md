# 17. L'accès aux soins dans l'Atlas et les fiches territoire
> Pas de carte d'accueil · groupe « Santé » de `/atlas` et des fiches `/territoires` · fiche préparée le 30/10/2026

## Ce qu'affiche le site

- **Atlas** : nouveau groupe **Santé**, 8 indicateurs. Six sont disponibles par commune, intercommunalité, département et région ; deux au département et à la région seulement.
- **Fiches territoire** : section Santé et deux alertes dans « Ce que ça veut dire » :
  - *Sous-dotation en généralistes* : accès inférieur ou égal à 2,5 consultations par an et par habitant ;
  - *Accès fragile* : la part de l'accès assurée par des médecins de plus de 60 ans est dans les 15 % les plus élevées.
- **Croisements de l'Atlas** : 3 cartes ajoutées sur les dentistes (maisons individuelles, prix immobilier, cadres), questions rédigées dans `docs/croisements/overrides.json`.
- **Pas de carte d'accueil** pour l'instant.

| Indicateur | Clé | Échelles | Unité |
|---|---|---|---|
| Accès aux généralistes | `apl_mg` | toutes | consultations par an et par habitant |
| Accès porté par les plus de 60 ans | `apl_mg_60` | toutes | % |
| Accès aux dentistes | `apl_dentistes` | toutes | ETP pour 100 000 habitants |
| Accès aux kinésithérapeutes | `apl_kines` | toutes | ETP pour 100 000 habitants |
| Accès aux infirmières | `apl_infirmieres` | toutes | ETP pour 100 000 habitants |
| Accès aux sages-femmes | `apl_sages_femmes` | toutes | ETP pour 100 000 femmes |
| Dépassements des spécialistes | `depassement_spe` | département, région | % des honoraires de base |
| Spécialistes en secteur 2 | `secteur2_spe` | département, région | % |

## D'où viennent les chiffres

Chaîne : fichiers Drees et API Assurance maladie -> `python/tools/build_atlas_sante.py` -> `atlas/communes/*.json`, `departements.json`, `epci.json` -> `build_territoires_echelles.py` (régions) -> `build_territoires_index.py` (repères) -> `build_croisements.py`.

| Chiffre | Valeur | Calcul |
|---|---|---|
| Accès national aux généralistes, tous âges | 3,72 | moyenne pondérée par la population standardisée, comme le demande le fichier |
| Accès national, médecins de 65 ans ou moins | 3,26 | même calcul ; **identique au chiffre publié par la Drees (3,26)** |
| Population sous 2,5 consultations | 18,2 % | population non standardisée, comme le demande le fichier |
| Même calcul, sans les plus de 65 ans | 29,0 % | colonne « 65 ans ou moins » |
| Même calcul, sans les plus de 60 ans | 46,4 % | colonne « 60 ans ou moins » ; sans remplacement, ce n'est pas une prévision |
| Paris, dépassements | 90,1 % | dépassements / honoraires sans dépassement, spécialistes, 2025 |
| Creuse, dépassements | 13,9 % | même calcul |

**Contrôles** : régions recalculées depuis les départements, écart maximal nul. Communes de l'Atlas sans valeur : 99, pour 731 habitants au total. 206 codes du fichier Drees absents de l'Atlas, pour 11 336 habitants : ils comptent dans les moyennes départementales mais n'ont pas de fiche.

## Les jeux de données

### Accessibilité potentielle localisée (Drees)
- **Producteur** : Drees, millésime 2024 (onglets 2022, 2023, 2024 par profession).
- **Page** : https://data.drees.solidarites-sante.gouv.fr/explore/dataset/530_l-accessibilite-potentielle-localisee-apl/
- **Géographie** : communes et arrondissements, France hors Mayotte.
- **Méthode** : consultations ou ETP accessibles à moins de 20 minutes, en tenant compte de l'activité des médecins et de l'âge des habitants.

| Colonne | Sens | Utilisée ? |
|---|---|---|
| Code commune INSEE, Commune | identifiant | oui |
| APL aux médecins généralistes | tous âges | oui : `apl_mg` |
| APL ... de 65 ans ou moins | sans les plus de 65 ans | contrôle et 29,0 % |
| APL ... de 62 ans ou moins | sans les plus de 62 ans | non |
| APL ... de 60 ans ou moins | sans les plus de 60 ans | oui : `apl_mg_60` |
| Population standardisée | selon l'âge, poids des moyennes | oui |
| Population totale 2022 | décomptes de population | oui |
| APL aux dentistes, kinés, infirmières, sages-femmes | ETP pour 100 000, professionnels de 65 ans ou moins | oui |
| Population féminine (sages-femmes) | dénominateur | non |

Autre pièce du jeu, non exploitée : « Indicateurs d'APL moyens par dixièmes de population » (inégalités d'accès : les 10 % les mieux dotés ont 4,28 fois l'accès des 10 % les moins dotés en 2024).

### Honoraires et secteurs conventionnels (Assurance maladie)
- **Pages** : https://data.ameli.fr/explore/dataset/honoraires/ et https://data.ameli.fr/explore/dataset/demographie-secteurs-conventionnels/
- **Licence** : ODbL, acceptée par l'usager le 30/10/2026.
- **Année** : 2025. **Géographie** : département ; `999` = total de région.
- **Champ retenu** : « Ensemble des médecins spécialistes (hors généralistes) ».

| Colonne | Sens | Utilisée ? |
|---|---|---|
| `annee`, `profession_sante`, `region`, `departement` | clés | oui |
| `hono_sans_depassement_totaux`, `depassements_totaux` | montants | oui |
| `taux_depassement_s2`, `taux_depassement_s2_optam`, `taux_depassement_s2_non_optam` | taux en secteur 2 | non |
| `depassements_moyens`, `hono_sans_depassement_moyens` | par praticien | non |
| `secteur_conventionnel`, `effectif` | 1, 3, 4, 5 retenus ; le secteur 2 se détaille en 3 et 4 | oui |

## Ce qu'on n'exploite pas encore

- L'évolution 2022-2024 de l'accès (onglets déjà présents dans les fichiers).
- Les dépassements profession par profession (38 professions).
- Le seuil « 62 ans ou moins », et les taux d'Optam.
- Les autres jeux Ameli : densités, primo-installés, zones sous-dotées, patients sans médecin traitant.

## Autres sources possibles

- **Délais de rendez-vous** : enquête Drees, à voir si elle est disponible au niveau local.
- **Pathologies** : déjà utilisées pour addictions et diabète (fiche 18), à élargir.

## Points de relecture

1. **Seuil de 2,5** : vient d'une publication Insee Auvergne-Rhône-Alpes (n° 187). Le présenter comme « le seuil sous lequel l'Insee parle de commune sous-dotée » est-il assez prudent ? Ce n'est pas le zonage officiel des ARS.
2. **Tous âges ou 65 ans et moins** : `apl_mg` prend tous les médecins, alors que la Drees met en avant les 65 ans ou moins (3,26). J'ai choisi l'offre réelle. À confirmer.
3. **Libellé « Accès porté par les plus de 60 ans »** : compréhensible ?
4. **Dépassements** : compter par département d'exercice du médecin, pas de résidence du patient. Paris attire des patients d'ailleurs. La mention suffit-elle ?
5. **Prix du détail** : l'accès ne dit rien des délais réels ni du fait qu'un médecin accepte de nouveaux patients.
6. **Couleur des flèches** dans « Ce qui sort de l'ordinaire » : vert si haut, rouge si bas. Or une valeur haute d'« Accès porté par les plus de 60 ans » n'est pas favorable.
7. **Jumeau statistique** : la santé en est volontairement exclue, pour ne pas changer les résultats existants.
8. **Légende des cartes** : le correctif (une décimale si l'étendue est faible) touche toutes les cartes concernées, pas seulement la santé.
9. **Carte d'accueil possible** : « 18 % des habitants sous le seuil, 46 % sans les médecins de plus de 60 ans ». À créer ?

**Décision de l'usager :**
