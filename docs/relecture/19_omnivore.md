# 19. L'omnivore à l'épreuve
> Section du dossier `/terrains/pratiques` · pas de carte d'accueil · fiche préparée le 30/10/2026

## Ce que dit la section

**La thèse tient dans sa version faible.** Les plus diplômés ont un répertoire plus large, ne rejettent presque rien et cumulent. Mais ce n'est pas une conquête d'aliments rares ou coûteux, et à caractéristiques égales l'élargissement passe surtout par les fruits et légumes.

**Les classes populaires ne correspondent à aucun des deux critères, majoritaire ou pas cher** : leur répertoire a la même composition que celui des classes supérieures, il est simplement plus court.

## D'où viennent les chiffres

Chaîne : INCA 3 et prix Insee -> `python/tools/build_omnivore.py` -> `frontend/public/data/showcases/omnivore.json` -> `SectionOmnivore` dans `pages/terrains/TerrainPratiques.jsx`.

| Question | Résultat | Calcul |
|---|---|---|
| Répertoire et diplôme | +2,8 aliments (± 1,7) | bac +4 / primaire-collège, à âge, sexe, revenu, PCS, ville égaux |
| Répertoire et revenu | +2,0 (± 1,6) | 1 850 € et plus / moins de 900 €, à diplôme égal |
| Mesure indépendante | +5,9 aliments différents (± 1,6) | rappels de 24 h, à caractéristiques égales ; +4,6 à énergie égale |
| Aliments majoritaires | +2,7 (± 1,3) | nombre consommé chaque mois |
| Aliments minoritaires | +0,1 (± 0,6) | idem |
| Aliments pas chers | +1,0 (± 0,4) | idem, 14 aliments |
| Aliments chers | +0,7 (± 0,5) | idem, 14 aliments |
| Fruits et légumes | +1,8 (± 0,7) | idem |
| Sans fruits et légumes | +1,0 (± 1,3), non significatif | idem ; +2,3 (± 0,9) à âge et sexe égaux seulement |
| Exclusions | 1 baisse, 20 hausses, 41 sans écart net | 62 aliments, correction de Benjamini-Hochberg |

**Classes populaires (à âge et sexe égaux)**

| | PCS | Diplôme | Revenu |
|---|---|---|---|
| Majoritaires : moins / plus / sans écart | 27 / 2 / 14 | 28 / 2 / 13 | 19 / 1 / 23 |
| Pas chers : moins / plus / sans écart | 11 / 0 / 3 | 12 / 1 / 1 | 8 / 0 / 6 |
| Lien écart et part de consommateurs | −0,31 (p = 0,015) | −0,36 (p = 0,005) | −0,31 (p = 0,016) |
| Lien écart et prix | +0,09 (p = 0,67) | +0,13 (p = 0,50) | −0,10 (p = 0,61) |

**Classes latentes (4 types)** : Répertoire large 33 %, Légumes, poisson, soupe 27 %, Sodas, desserts, sucreries 29 %, Répertoire resserré 11 %. Stabilité entre moitiés d'échantillon : 0,95. Le répertoire large va de 26 % (primaire-collège) à 53 % (bac +4) ; +18,4 points à caractéristiques égales (± 9,7).

## Les jeux de données

### INCA 3 (Anses)
Voir la [fiche 18](18_modes-de-vie.md). Tables propres à ce test : `fpq` (62 aliments feuilles, sans totaux ni variantes de saison ; `<aliment>_ON` et `<aliment>_freq_M`), `conso-compo-alim` (204 Mo, aliments distincts relevés dans les rappels ; colonnes `NOIND`, `R24_num`, `R24_nombre`, `gpe_INCA3`, `aliment_code_INCA3`).

### Prix moyens de vente au détail (Insee)
- **Page** : https://www.insee.fr/fr/plan-du-site/famille-bdm/103157792
- **Téléchargement** : `https://www.bdm.insee.fr/series/sdmx/data/IPC-PM-2015?startPeriod=2014-01&endPeriod=2015-12&detail=full`
- **Utilisé** : séries annuelles, moyenne 2014-2015, pour correspondre à la période d'INCA 3.
- **Couverture** : 28 aliments sur 62, surtout frais. Ni frites, ni sodas, ni biscuits, ni chips.
- **Correspondance aliment et séries** : dictionnaire `PRIX` de `build_omnivore.py`. Elle est faite à la main et à relire : c'est le seul endroit où un jugement entre dans le critère de prix. Exemples : boeuf = moyenne de 6 morceaux ; fruits exotiques = kiwi et avocat ; yaourt aromatisé = yaourt aux fruits ; poisson gras = saumon d'élevage.

## Ce qu'on n'exploite pas encore

- La **dose** : on compte la présence mensuelle d'un aliment, pas les quantités (les fréquences sont utilisées pour le prix moyen pondéré).
- Le **bio** et les **marques** dans `conso-compo-alim`, qui diraient si un même aliment est acheté différemment selon le milieu.
- **INCA 2** (2006-2007), seule piste pour une évolution.

## Autres sources possibles

- **Ciqual** (Anses) : pour le prix à la calorie, indispensable car les deux classements diffèrent. Le site répondait en erreur 503 le 30/10/2026.
- **Open Prices** (Open Food Facts) : prix de produits industriels, saisis par des contributeurs ; couverture et qualité à vérifier.

## Points de relecture

1. **Seuil « majoritaire »** : plus de 50 % de consommateurs chaque mois donne **43 aliments sur 62**. Le critère est peu sélectif. Une médiane (68 %) le serait plus. Les résultats ne changent pas de sens (+2,2 ± 0,9 au-dessus de la médiane), mais lequel préfères-tu ?
2. **Fréquence ou populaire** : « majoritaire » mesure ce qui est répandu partout, pas ce qui est propre aux milieux populaires. C'est voulu : le test montre justement que les deux diffèrent.
3. **Plafond** : un aliment déjà consommé par 95 % des gens laisse peu de place à un écart. Le lien négatif entre écart et part de consommateurs peut en partie venir de là, pour les aliments rares (plancher).
4. **Classes populaires** : trois définitions séparées, retraités exclus de la définition par PCS. Est-ce la bonne définition ? Faut-il un groupe intermédiaire ?
5. **« Prescription nutritionnelle ou éclectisme »** : l'hypothèse sur les fruits et légumes est une lecture, pas un résultat.
6. **Mot « snob »** : repris de Peterson. Garder ?
7. **Prix** : au kilo, pas à la calorie. Limite signalée sur la page.
8. **Bourdieu** : l'intro le résume en une phrase (« on se situe aussi par ce qu'on refuse »). À vérifier, c'est ton terrain.
9. **Classes latentes** : 4 types par choix de lisibilité ; le critère BIC en préfère davantage. Les noms sont descriptifs : conviennent-ils ?
10. **Références** : Peterson et Kern 1996, Bryson 1996 (ASR 61, vérifiées par DOI), Warde, Martens et Olsen 1999.

**Décision de l'usager :**
