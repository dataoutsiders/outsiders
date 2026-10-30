# 18. Manger, bouger, fumer : le poids du milieu social
> Dossier `/terrains/pratiques` · pas de carte d'accueil · fiche préparée le 30/10/2026
> La section « L'omnivore à l'épreuve » a sa propre fiche : [19](19_omnivore.md).

## Ce que dit le dossier

Quatre chiffres en tête : −22,6 points de tabac quotidien et −9,3 points d'obésité (bac +4 comparé à primaire-collège, à âge, sexe, revenu, PCS et ville égaux) ; 4,5 contre 2,5 aliments jamais consommés sur 19 ; 24 % contre 6 % des femmes et des hommes de corpulence normale qui se jugent trop gros.

Sections : la carte des pratiques ; ce que le social explique ; obésité, tabac, alcool, sucre ; les activités à caractéristiques égales ; le regard sur son propre corps ; région par région ; département par département ; méthode et limites.

## D'où viennent les chiffres

Chaîne : tables INCA 3, Baromètre et Assurance maladie -> `python/tools/build_pratiques.py` -> `frontend/public/data/showcases/pratiques.json` et `geo/regions.geojson` -> `pages/terrains/TerrainPratiques.jsx`, `charts/PratiquesCarte.jsx`. Inscrit dans `config/dossiersTerritoires.js` (fiches département et région).

| Chiffre | Valeur | Calcul |
|---|---|---|
| Axes de la carte | 46 % et 26 % | ACM pondérée, taux corrigés de Benzécri |
| Stabilité des axes | 0,92 | 5e centile de la corrélation sur 200 rééchantillonnages |
| Obésité, écart brut | −14,6 pts (± 6,2) | moindres carrés pondérés, plan de sondage |
| Obésité, à tout égal | −9,3 pts (± 5,9) | âge, sexe, revenu, PCS, ville |
| Tabac, écart brut | −17,4 pts (± 6,7) | idem |
| Tabac, à âge et sexe égaux | −23,5 pts (± 6,9) | idem |
| Tabac, à tout égal | −22,6 pts (± 8,5) | idem |
| Part expliquée de l'obésité | 5,5 % | R² pondéré, valeurs de Shapley par bloc |
| Sédentarité élevée et obésité | +14,2 pts (± 5,7) | à caractéristiques égales |
| Femmes et hommes à IMC égal | −17,4 pts (± 4,8) pour les hommes | se juger trop gros, âge, diplôme, revenu, IMC égaux |
| Idem à poids et taille égaux | −22,6 pts (± 7,0) | contrôle |
| Idem à poids seul | −40,0 pts (± 4,8) | calculé, non affiché : comparaison trompeuse |
| Troubles addictifs, Creuse | 1,8 % (France 1,2 %) | standardisation indirecte par âge et sexe |

**Contrôles** : inertie totale de l'ACM égale à K/Q − 1 ; une modalité active est bien le barycentre de ses individus (assertions dans le script).

## Les jeux de données

### INCA 3 (Anses)
- **Page** : https://www.data.gouv.fr/fr/datasets/5df9151d634f415c1a9c1df4/
- **Période** : 2014-2015. **Population** : 2 288 adultes en Pop2 (questionnaires), 1 966 d'entre eux en Pop3 (consommations) dans ce dossier.
- **Licence** : non renseignée sur data.gouv.fr.
- **Tables utilisées** : `description-indiv` (185 colonnes), `habitudes-indiv` (389), `habitudes-men` (167), `actphys-sedent` (93), `fpq` (384), `conso-gpe-inca3` (46), `apports-nut-alim` (108). Le détail de chaque colonne est dans la notice utilisateurs du jeu.
- **Variables actives de la carte (60)** : 19 aliments en 3 classes (`fpq`) ; lieux d'achat, bio, autoproduction ; restauration rapide, lieu du déjeuner, sauces à table ; 10 critères de choix (`choix_aliment_*`) ; 6 sources d'information (`source_*`) ; étiquettes ; 13 activités regroupées (`activite_*_score`), niveau d'activité (`nap`), sédentarité.
- **Projetées, hors calcul** : `tage_PS`, `sex_PS`, `etude_4cl_interv`, `PCS_8cl_interv`, `RUC_4cl`, `agglo_5cl`, `imc`, `fume`, `poids_perception`, `soins`, `IA_statut`.
- **Non exploité** : voir plus bas.

### Baromètre de Santé publique France 2024 (Odissé)
- **Exemple de page** : https://odisse.santepubliquefrance.fr/explore/dataset/tabagisme-indicateurs-du-barometre-2024
- **Jeux** : tabagisme, alcool, sédentarité (détail région), activité physique (détail région), épisodes dépressifs (détail région).
- **Colonnes** : `indicateur`, `sexe`, `classe_d_age`, `diplome`, `nouvelles_regions`, `pcs`, `situation_professionnelle`, `situation_financiere_percue`, `estimation`, `ic`, `ic_inf`, `ic_sup`, `effectif_brut`, `annee`. Seules les lignes « Tous » sont utilisées.
- **Effectifs** : de 1 300 à 3 900 répondants par région.

### Effectifs de patients (Assurance maladie)
- **Page** : https://www.data.gouv.fr/datasets/62b31f7b128643f46ea1f848
- **Colonnes** : `annee`, `patho_niv1` à `patho_niv3`, `top`, `cla_age_5`, `sexe`, `region`, `dept`, `ntop`, `npop`, `prev`.
- **Utilisé** : 2024, `PSY_ADD_CAT` (troubles addictifs) et `DIA_CAT_CAT` (diabète). Licence ODbL.
- **Pourquoi la standardisation indirecte** : les petits effectifs par âge sont masqués dans la source.

## Ce qu'on n'exploite pas encore

- **Baromètre** : colonnes `diplome` et `pcs`, qui permettraient de refaire les écarts sociaux sur des données de 2024.
- **Assurance maladie** : toutes les autres pathologies, et les années 2015 à 2023.
- **INCA 3** : les apports nutritionnels (54 nutriments), les aliments consommés un à un avec cuisson, marque et bio, la lecture des étiquettes en détail, la cuisine et les habitudes du ménage, l'insécurité alimentaire.
- **Drees** : `er_inegalites_maladies_chroniques`, prévalences par niveau de vie et diplôme.
- **Insee** : espérance de vie par niveau de vie 2020-2024.

## Autres sources possibles

- INCA 2 (2006-2007), pour une évolution, si les variables sont comparables.
- Obépi ou Constances pour l'obésité : pas en open data à ma connaissance, à vérifier.

## Points de relecture

1. **Titre** : « Manger, bouger, fumer : le poids du milieu social » te convient-il ?
2. **Données anciennes** : 2014-2015. C'est dit en tête, mais tout est au présent dans le texte.
3. **Axes de la carte** : j'ai nommé « Répertoire étroit, le prix » et « Répertoire large, la qualité » ; « Plus âgé, à la maison » et « Plus jeune, dehors ». Le mot « qualité » est un jugement de valeur, contraire à ta consigne sur les critères objectifs. À remplacer, par exemple par « origine, labels ».
4. **Âge en 3 classes** : c'est la limite principale de tout « à caractéristiques égales ».
5. **Retraités** : classés à part dans la PCS, donc le poids de la PCS sur l'axe vertical se confond avec l'âge.
6. **Imputation** : 2 % de réponses manquantes remplacées par la modalité la plus fréquente.
7. **Activités** : écarts avec des pratiques rares (danse de salon −11 points, bowling −10) à prendre avec prudence. Faut-il les masquer ?
8. **Corps** : texte corrigé après ta remarque (IMC et non poids). Le paragraphe sur la masse grasse s'appuie sur un fait général, sans source citée ni donnée de l'enquête : faut-il ajouter une référence ?
9. **Vocabulaire** : relire les mots sensibles (« obésité », « trop gros », repris de la question de l'enquête).
10. **« Addictions et pratiques, région par région »** : le titre couvre aussi la dépression, qui n'est ni une addiction ni une pratique. À renommer.
11. **Sucre** : les « produits sucrés » regroupent 5 groupes INCA (gâteaux, entremets, glaces, confiserie, sucre) ; les « boissons rafraîchissantes » incluent les boissons sans sucre. Le groupe ne permet pas de les séparer.
12. **Outre-mer** : absent de la carte régionale (présent dans la liste) ; troubles addictifs très bas, sans doute en partie un effet du recours aux soins.

**Décision de l'usager :**
