# Croisements de l'Atlas : audit du balayage et selection automatique

> Genere par `python/tools/build_croisements.py`. La selection des cartes du front est
> AUTOMATIQUE (section 0) ; les textes s'adaptent petit a petit via overrides.json.
> Rappels sur toute carte publiee : correlation territoriale, pas individuelle
> (sophisme ecologique) ; pronostic n'est pas causalite ; le r depend de la maille (MAUP).

20 indicateurs, 190 paires. Lecture : r dept = Pearson sur 101
departements ; r communes = Pearson pondere par la population ; Spearman = robustesse
(rangs, non pondere). Score = |r| de reference, penalise x0.4 si meme groupe,
bonifie si inversion de signe entre mailles.

## 0. Selection automatique servie au front (12 cartes)

Criteres : |r communes pondere| >= 0.3, Spearman de meme signe, dimensions
latentes differentes, une carte par paire de dimensions (la plus forte, le reste en
variantes). Pour surcharger un texte ou masquer une carte : `overrides.json` (cle = id).

| id | Question (auto ou surchargee) | r communes | Variantes |
|---|---|---|---|
| `ips_ecole_public__revenu` | Dis-moi le revenu de ta commune, je te dirai le public de ton école ? | +0.87 | 5 |
| `prix_m2__cadres` | L'immobilier flambe-t-il seulement là où vivent les cadres ? | +0.82 | 7 |
| `ips_ecole_public__diplome_sup` | Communes diplômées, écoles au public favorisé ? | +0.72 | 12 |
| `idp__natalite` | Les candidats issus de la diversité se présentent-ils dans les communes les plus jeunes ? | +0.63 | 2 |
| `idp__hlm` | Plus de logement social, plus de candidats issus de la diversité ? | +0.60 | 2 |
| `prix_m2__maisons` | La France des maisons est-elle celle de l'immobilier abordable ? | -0.59 | 2 |
| `cadres__maisons` | Les cadres, en appartement plutôt qu'en pavillon ? | -0.57 | 3 |
| `res_secondaires__ages65` | Les communes de résidences secondaires sont-elles aussi celles des retraités ? | +0.51 | 6 |
| `ips_college_public__hlm` | Plus de HLM dans la commune, collège au public moins favorisé ? | -0.47 | 5 |
| `ips_lycee_public__jeunes` | Dans les communes les plus jeunes, des lycées au public moins favorisé ? | -0.44 | 2 |
| `ips_lycee_public__idp` | Là où les candidats sont plus divers, des lycées au public moins favorisé ? | -0.36 | 1 |
| `cadres__ages65` | « Cadres » baisse quand « 65 ans et plus » monte. Partout ? | -0.33 | 1 |

## 1. Shortlist automatique (top 15 par score)

| Paire | r dept | r communes (pond.) | Spearman | n communes | Signaux |
|---|---|---|---|---|---|
| IPS (écoles) × Revenu médian | +0.82 | +0.87 | +0.76 | 15631 |  |
| IPS (collèges) × Revenu médian | +0.77 | +0.86 | +0.78 | 3509 |  |
| Prix immobilier × Cadres | +0.84 | +0.82 | +0.45 | 33061 |  |
| Prix immobilier × Diplômés du supérieur | +0.85 | +0.77 | +0.58 | 33138 |  |
| IPS (écoles) × Diplômés du supérieur | +0.81 | +0.72 | +0.79 | 15727 |  |
| Revenu médian × Diplômés du supérieur | +0.79 | +0.69 | +0.62 | 30836 |  |
| Prix immobilier × Ouvriers | -0.79 | -0.67 | -0.34 | 33061 |  |
| Revenu médian × Cadres | +0.75 | +0.66 | +0.47 | 30838 |  |
| IPS (écoles) × Ouvriers | -0.63 | -0.66 | -0.65 | 15727 |  |
| IPS (collèges) × Diplômés du supérieur | +0.73 | +0.65 | +0.69 | 3581 |  |
| Revenu médian × Logement social (HLM) | +0.20 | -0.37 | -0.09 | 30836 | inversion-de-signe |
| IPS (lycées) × Revenu médian | +0.64 | +0.64 | +0.54 | 1156 |  |
| IPS (écoles) × Cadres | +0.66 | +0.64 | +0.63 | 15727 |  |
| Diversité des candidats × Taux de natalité | +0.67 | +0.63 | +0.20 | 11417 |  |
| IPS (collèges) × Cadres | +0.57 | +0.61 | +0.58 | 3581 |  |

## 2. Correlations fortes inter-groupes (33) : matiere a « la France que ca dessine »

| Paire | r dept | r communes (pond.) | Spearman | n communes | Signaux |
|---|---|---|---|---|---|
| IPS (écoles) × Revenu médian | +0.82 | +0.87 | +0.76 | 15631 |  |
| IPS (collèges) × Revenu médian | +0.77 | +0.86 | +0.78 | 3509 |  |
| Prix immobilier × Cadres | +0.84 | +0.82 | +0.45 | 33061 |  |
| Prix immobilier × Diplômés du supérieur | +0.85 | +0.77 | +0.58 | 33138 |  |
| IPS (écoles) × Diplômés du supérieur | +0.81 | +0.72 | +0.79 | 15727 |  |
| Revenu médian × Diplômés du supérieur | +0.79 | +0.69 | +0.62 | 30836 |  |
| Prix immobilier × Ouvriers | -0.79 | -0.67 | -0.34 | 33061 |  |
| Revenu médian × Cadres | +0.75 | +0.66 | +0.47 | 30838 |  |
| IPS (écoles) × Ouvriers | -0.63 | -0.66 | -0.65 | 15727 |  |
| IPS (collèges) × Diplômés du supérieur | +0.73 | +0.65 | +0.69 | 3581 |  |
| IPS (écoles) × Cadres | +0.66 | +0.64 | +0.63 | 15727 |  |
| IPS (lycées) × Revenu médian | +0.64 | +0.64 | +0.54 | 1156 |  |
| Diversité des candidats × Taux de natalité | +0.67 | +0.63 | +0.20 | 11417 |  |
| Revenu médian × Employés | -0.77 | -0.62 | -0.21 | 30838 |  |
| IPS (collèges) × Employés | -0.60 | -0.61 | -0.42 | 3581 |  |
| IPS (collèges) × Cadres | +0.57 | +0.61 | +0.58 | 3581 |  |
| IPS (collèges) × Ouvriers | -0.57 | -0.61 | -0.62 | 3581 |  |
| IPS (écoles) × Employés | -0.66 | -0.61 | -0.34 | 15727 |  |
| IPS (lycées) × Diplômés du supérieur | +0.60 | +0.60 | +0.51 | 1193 |  |
| Diversité des candidats × Logement social (HLM) | +0.65 | +0.60 | +0.30 | 11414 |  |
| Prix immobilier × Maisons individuelles | -0.84 | -0.59 | -0.35 | 33139 | ecart-mailles |
| Maisons individuelles × Cadres | -0.78 | -0.57 | -0.19 | 34608 |  |
| Revenu médian × Ouvriers | -0.49 | -0.56 | -0.34 | 30838 |  |
| IPS (lycées) × Cadres | +0.43 | +0.55 | +0.45 | 1193 |  |
| IPS (lycées) × Employés | -0.56 | -0.55 | -0.36 | 1193 |  |
| IPS (écoles) × Prix immobilier | +0.52 | +0.53 | +0.60 | 14842 |  |
| IPS (lycées) × Ouvriers | -0.45 | -0.53 | -0.44 | 1193 |  |
| Diversité des candidats × Maisons individuelles | -0.64 | -0.52 | -0.37 | 11414 |  |
| Diplômés du supérieur × Maisons individuelles | -0.79 | -0.52 | -0.18 | 34688 | ecart-mailles |
| Résidences secondaires × 65 ans et plus | +0.51 | +0.51 | +0.50 | 34688 |  |
| IPS (collèges) × Prix immobilier | +0.47 | +0.51 | +0.51 | 3405 |  |
| Prix immobilier × Employés | -0.47 | -0.50 | -0.05 | 33061 |  |
| Diversité des candidats × Propriétaires | -0.66 | -0.50 | -0.29 | 11414 |  |

## 3. Quasi nulles inter-groupes (58) : chercher ici l'idee recue qui tombe

La machine ne sait pas ce que le public s'attend a trouver correle : c'est dans cette
liste qu'un oeil humain repere le « on aurait jure que oui, et non ».

| Paire | r dept | r communes (pond.) | Spearman | n communes | Signaux |
|---|---|---|---|---|---|
| Taux de natalité × Professions intermédiaires | +0.20 | +0.00 | +0.13 | 34611 |  |
| Revenu médian × Maisons individuelles | -0.58 | -0.01 | -0.06 | 30836 | ecart-mailles |
| Valeur ajoutée (lycées) × Prix immobilier | +0.19 | +0.01 | -0.01 | 1249 |  |
| Diplômés du supérieur × Logement social (HLM) | +0.31 | +0.01 | +0.02 | 34688 | ecart-mailles |
| Valeur ajoutée (lycées) × 65 ans et plus | +0.02 | -0.01 | +0.07 | 1308 |  |
| Résidences secondaires × Employés | +0.28 | -0.02 | -0.07 | 34608 | ecart-mailles |
| Logement social (HLM) × Ouvriers | -0.22 | -0.02 | +0.01 | 34608 |  |
| Valeur ajoutée (lycées) × Propriétaires | -0.11 | -0.02 | +0.08 | 1308 |  |
| Valeur ajoutée (lycées) × Jeunes (0-14 ans) | -0.06 | +0.02 | -0.07 | 1308 |  |
| IPS (écoles) × 65 ans et plus | -0.05 | +0.02 | -0.21 | 15727 |  |
| Valeur ajoutée (lycées) × Maisons individuelles | -0.09 | +0.03 | +0.10 | 1308 |  |
| Valeur ajoutée (lycées) × Résidences secondaires | +0.21 | +0.03 | +0.11 | 1308 |  |
| Logements vacants × Taux de natalité | -0.22 | -0.03 | -0.05 | 34688 |  |
| Diplômés du supérieur × Résidences secondaires | -0.07 | -0.04 | -0.13 | 34688 |  |
| Revenu médian × Professions intermédiaires | +0.06 | +0.04 | +0.38 | 30838 |  |
| Valeur ajoutée (lycées) × Logement social (HLM) | -0.10 | -0.04 | -0.15 | 1308 |  |
| Diversité des candidats × Diplômés du supérieur | +0.46 | +0.04 | +0.13 | 11414 | ecart-mailles |
| Valeur ajoutée (lycées) × Taux de natalité | +0.01 | +0.05 | -0.10 | 1308 |  |
| Valeur ajoutée (lycées) × Ouvriers | -0.23 | +0.05 | +0.06 | 1308 | ecart-mailles |
| Valeur ajoutée (lycées) × Diversité des candidats | +0.04 | +0.05 | -0.15 | 1280 |  |
| Revenu médian × 65 ans et plus | -0.40 | -0.05 | -0.38 | 30839 | ecart-mailles |
| Résidences secondaires × Ouvriers | -0.14 | -0.05 | -0.03 | 34608 |  |
| Propriétaires × Jeunes (0-14 ans) | -0.50 | +0.05 | +0.02 | 34688 | ecart-mailles |
| Taux de natalité × Employés | -0.13 | +0.06 | +0.02 | 34611 |  |
| Maisons individuelles × Employés | +0.41 | +0.06 | -0.09 | 34608 | ecart-mailles |
| Revenu médian × Résidences secondaires | -0.08 | +0.06 | -0.35 | 30836 |  |
| IPS (écoles) × Résidences secondaires | +0.18 | +0.07 | -0.12 | 15727 |  |
| Valeur ajoutée (lycées) × Cadres | -0.02 | -0.07 | -0.09 | 1308 |  |
| Diversité des candidats × Ouvriers | -0.47 | -0.07 | -0.16 | 11417 | ecart-mailles |
| Valeur ajoutée (lycées) × Diplômés du supérieur | +0.04 | -0.07 | -0.06 | 1308 |  |
| Valeur ajoutée (lycées) × Employés | +0.22 | +0.08 | +0.03 | 1308 |  |
| Valeur ajoutée (lycées) × Logements vacants | +0.02 | +0.09 | +0.07 | 1308 |  |
| IPS (collèges) × Maisons individuelles | -0.35 | +0.09 | -0.01 | 3581 | ecart-mailles |
| Résidences secondaires × Cadres | -0.28 | -0.09 | -0.21 | 34608 |  |
| Diversité des candidats × Logements vacants | -0.25 | -0.09 | -0.03 | 11414 |  |
| Valeur ajoutée (lycées) × Revenu médian | -0.07 | -0.10 | -0.02 | 1272 |  |
| Logements vacants × Employés | +0.24 | +0.10 | +0.05 | 34608 |  |
| Logement social (HLM) × Professions intermédiaires | +0.09 | -0.11 | +0.07 | 34608 |  |
| IPS (lycées) × Logements vacants | -0.31 | -0.11 | -0.17 | 1193 |  |
| IPS (écoles) × Jeunes (0-14 ans) | -0.26 | -0.11 | +0.15 | 15727 |  |
| Valeur ajoutée (lycées) × Professions intermédiaires | -0.01 | -0.11 | -0.09 | 1308 |  |
| Propriétaires × Employés | +0.23 | -0.11 | -0.14 | 34608 | inversion-de-signe |
| 65 ans et plus × Professions intermédiaires | -0.33 | -0.11 | -0.23 | 34611 |  |
| Taux de natalité × Ouvriers | -0.28 | -0.11 | +0.04 | 34611 |  |
| IPS (collèges) × Résidences secondaires | +0.28 | +0.12 | +0.07 | 3581 |  |
| Maisons individuelles × Jeunes (0-14 ans) | -0.28 | +0.12 | +0.04 | 34688 | inversion-de-signe |
| Diversité des candidats × Employés | -0.20 | +0.12 | +0.07 | 11417 | inversion-de-signe |
| Diplômés du supérieur × Taux de natalité | +0.27 | +0.12 | +0.11 | 34688 |  |
| 65 ans et plus × Employés | +0.32 | +0.12 | +0.02 | 34611 |  |
| IPS (écoles) × Maisons individuelles | -0.47 | +0.13 | -0.04 | 15727 | inversion-de-signe |
| Maisons individuelles × Professions intermédiaires | -0.19 | +0.13 | -0.09 | 34608 | inversion-de-signe |
| Logement social (HLM) × Cadres | +0.49 | +0.13 | +0.14 | 34608 | ecart-mailles |
| Prix immobilier × Résidences secondaires | +0.07 | +0.13 | -0.26 | 33139 | non-lineaire-ou-outliers |
| Logements vacants × Cadres | -0.35 | -0.14 | -0.24 | 34608 |  |
| IPS (lycées) × Maisons individuelles | -0.21 | -0.14 | -0.13 | 1193 |  |
| Prix immobilier × Logement social (HLM) | +0.39 | +0.15 | +0.27 | 33138 |  |
| Diversité des candidats × Cadres | +0.57 | +0.15 | +0.20 | 11417 | ecart-mailles |
| IPS (collèges) × 65 ans et plus | +0.07 | +0.15 | -0.07 | 3581 |  |

## 4. Paradoxes d'agregation (50) : le r change avec la maille

Une inversion de signe departements/communes est editorialement forte (« vu de loin
oui, vu de pres non ») mais exige une explication solide avant publication.

| Paire | r dept | r communes (pond.) | Spearman | n communes | Signaux |
|---|---|---|---|---|---|
| Revenu médian × Propriétaires | -0.32 | +0.27 | +0.25 | 30836 | inversion-de-signe |
| IPS (écoles) × Maisons individuelles | -0.47 | +0.13 | -0.04 | 15727 | inversion-de-signe |
| Revenu médian × Logement social (HLM) | +0.20 | -0.37 | -0.09 | 30836 | inversion-de-signe |
| Revenu médian × Maisons individuelles | -0.58 | -0.01 | -0.06 | 30836 | ecart-mailles |
| Propriétaires × Jeunes (0-14 ans) | -0.50 | +0.05 | +0.02 | 34688 | ecart-mailles |
| Logements vacants × Maisons individuelles | +0.44 | -0.07 | +0.04 | 34689 | meme-groupe, ecart-mailles |
| Logements vacants × Propriétaires | +0.32 | -0.17 | -0.07 | 34688 | meme-groupe, inversion-de-signe |
| IPS (écoles) × Propriétaires | -0.08 | +0.41 | +0.25 | 15727 | ecart-mailles |
| Revenu médian × Diversité des candidats | +0.24 | -0.24 | +0.06 | 11280 | inversion-de-signe |
| IPS (collèges) × Maisons individuelles | -0.35 | +0.09 | -0.01 | 3581 | ecart-mailles |
| Jeunes (0-14 ans) × Cadres | +0.23 | -0.22 | +0.13 | 34611 | inversion-de-signe |
| Logement social (HLM) × Employés | -0.18 | +0.25 | +0.16 | 34608 | inversion-de-signe |
| Revenu médian × Taux de natalité | +0.27 | -0.17 | +0.14 | 30839 | inversion-de-signe |
| Diversité des candidats × Cadres | +0.57 | +0.15 | +0.20 | 11417 | ecart-mailles |
| Prix immobilier × Jeunes (0-14 ans) | +0.19 | -0.24 | +0.27 | 33141 | inversion-de-signe |
| Diversité des candidats × Diplômés du supérieur | +0.46 | +0.04 | +0.13 | 11414 | ecart-mailles |
| IPS (collèges) × Propriétaires | +0.03 | +0.44 | +0.35 | 3581 | ecart-mailles |
| Propriétaires × 65 ans et plus | +0.76 | +0.35 | -0.02 | 34688 | ecart-mailles |
| Maisons individuelles × Jeunes (0-14 ans) | -0.28 | +0.12 | +0.04 | 34688 | inversion-de-signe |
| Diversité des candidats × Ouvriers | -0.47 | -0.07 | -0.16 | 11417 | ecart-mailles |
| Logement social (HLM) × 65 ans et plus | -0.75 | -0.36 | -0.07 | 34688 | ecart-mailles |
| Propriétaires × Ouvriers | +0.60 | +0.23 | -0.01 | 34608 | ecart-mailles |
| Logement social (HLM) × Cadres | +0.49 | +0.13 | +0.14 | 34608 | ecart-mailles |
| Prix immobilier × Propriétaires | -0.73 | -0.38 | -0.18 | 33138 | ecart-mailles |
| IPS (écoles) × Logement social (HLM) | -0.08 | -0.43 | -0.17 | 15727 | ecart-mailles |
| Revenu médian × 65 ans et plus | -0.40 | -0.05 | -0.38 | 30839 | ecart-mailles |
| Logement social (HLM) × Jeunes (0-14 ans) | +0.59 | +0.24 | +0.12 | 34688 | ecart-mailles |
| Maisons individuelles × Employés | +0.41 | +0.06 | -0.09 | 34608 | ecart-mailles |
| Jeunes (0-14 ans) × Taux de natalité | +0.93 | +0.59 | +0.48 | 34691 | meme-groupe, ecart-mailles |
| Propriétaires × Employés | +0.23 | -0.11 | -0.14 | 34608 | inversion-de-signe |
| Prix immobilier × Diversité des candidats | +0.54 | +0.21 | +0.25 | 10837 | ecart-mailles |
| Diversité des candidats × Employés | -0.20 | +0.12 | +0.07 | 11417 | inversion-de-signe |
| Maisons individuelles × Professions intermédiaires | -0.19 | +0.13 | -0.09 | 34608 | inversion-de-signe |
| Propriétaires × Cadres | -0.68 | -0.37 | -0.04 | 34608 | ecart-mailles |
| Diplômés du supérieur × Propriétaires | -0.58 | -0.28 | +0.03 | 34688 | ecart-mailles |
| Résidences secondaires × Employés | +0.28 | -0.02 | -0.07 | 34608 | ecart-mailles |
| Diplômés du supérieur × Logement social (HLM) | +0.31 | +0.01 | +0.02 | 34688 | ecart-mailles |
| Revenu médian × Jeunes (0-14 ans) | +0.13 | -0.16 | +0.26 | 30839 | inversion-de-signe |
| Maisons individuelles × Ouvriers | +0.72 | +0.43 | +0.13 | 34608 | ecart-mailles |
| Propriétaires × Professions intermédiaires | -0.10 | +0.18 | +0.04 | 34608 | ecart-mailles |
| Valeur ajoutée (lycées) × Ouvriers | -0.23 | +0.05 | +0.06 | 1308 | ecart-mailles |
| Prix immobilier × Logements vacants | -0.46 | -0.18 | -0.47 | 33139 | ecart-mailles |
| IPS (collèges) × Logement social (HLM) | -0.20 | -0.47 | -0.31 | 3581 | ecart-mailles |
| Maisons individuelles × 65 ans et plus | +0.61 | +0.34 | -0.00 | 34688 | ecart-mailles |
| Diplômés du supérieur × Maisons individuelles | -0.79 | -0.52 | -0.18 | 34688 | ecart-mailles |
| 65 ans et plus × Cadres | -0.59 | -0.33 | -0.17 | 34611 | ecart-mailles |
| Prix immobilier × 65 ans et plus | -0.52 | -0.26 | -0.33 | 33141 | ecart-mailles |
| Jeunes (0-14 ans) × Ouvriers | -0.06 | +0.20 | +0.03 | 34611 | ecart-mailles |
| Prix immobilier × Maisons individuelles | -0.84 | -0.59 | -0.35 | 33139 | ecart-mailles |
| Diplômés du supérieur × Logements vacants | -0.45 | -0.20 | -0.36 | 34688 | ecart-mailles |

## 5. Gisements d'outsiders : les paires aux plus gros ecarts au pronostic

### Diplômés du supérieur × Maisons individuelles (r communes -0.22, 4.0% de communes a |z| > 2.5)
- Marseille 3e arr. (13203, 58,029 hab) : en dessous du pronostic (z = -6.1)
- Marseille 2e arr. (13202, 24,378 hab) : en dessous du pronostic (z = -5.8)
- Villeneuve-la-Garenne (92078, 26,021 hab) : en dessous du pronostic (z = -5.8)
- Aubervilliers (93001, 88,365 hab) : en dessous du pronostic (z = -5.8)
- Dugny (93030, 11,700 hab) : en dessous du pronostic (z = -5.8)
- Departements : SEINE-SAINT-DENIS (z = -3.5), ALPES-MARITIMES (z = -2.7), GUYANE (z = -2.2), HAUTE-CORSE (z = -1.8), LOT (z = 1.7)

### Prix immobilier × Maisons individuelles (r communes -0.49, 3.9% de communes a |z| > 2.5)
- Marseille 3e arr. (13203, 58,029 hab) : en dessous du pronostic (z = -6.7)
- Saint-Étienne (42218, 173,136 hab) : en dessous du pronostic (z = -6.5)
- Grigny (91286, 26,842 hab) : en dessous du pronostic (z = -6.3)
- Pointe-à-Pitre (97120, 15,040 hab) : en dessous du pronostic (z = -6.3)
- Belfort (90010, 45,912 hab) : en dessous du pronostic (z = -6.3)
- Departements : TERRITOIRE DE BELFORT (z = -2.7), PARIS (z = 2.7), VENDEE (z = 2.3), SEINE-SAINT-DENIS (z = -2.2), LOIRE (z = -2.2)

### Revenu médian × Résidences secondaires (r communes -0.24, 3.4% de communes a |z| > 2.5)
- Les Belleville (73257, 3,498 hab) : au-dessus du pronostic (z = 6.1)
- Morzine (74191, 2,658 hab) : au-dessus du pronostic (z = 6.0)
- Le Touquet-Paris-Plage (62826, 4,224 hab) : au-dessus du pronostic (z = 5.9)
- Courchevel (73227, 2,290 hab) : au-dessus du pronostic (z = 5.8)
- Megève (74173, 2,893 hab) : au-dessus du pronostic (z = 5.7)

### Prix immobilier × Logement social (HLM) (r communes +0.25, 3.4% de communes a |z| > 2.5)
- Le Grand-Quevilly (76322, 25,789 hab) : au-dessus du pronostic (z = 10.2)
- Dugny (93030, 11,700 hab) : au-dessus du pronostic (z = 9.6)
- Val-de-Reuil (27701, 13,245 hab) : au-dessus du pronostic (z = 9.5)
- Grande-Synthe (59271, 20,239 hab) : au-dessus du pronostic (z = 8.9)
- Pointe-à-Pitre (97120, 15,040 hab) : au-dessus du pronostic (z = 8.4)
- Departements : SEINE-SAINT-DENIS (z = 3.4), MARNE (z = 2.3), SEINE-MARITIME (z = 2.1), VAL-DE-MARNE (z = 2.0), AUBE (z = 1.8)

### Diversité des candidats × Maisons individuelles (r communes -0.46, 3.4% de communes a |z| > 2.5)
- La Grande-Motte (34344, 8,440 hab) : en dessous du pronostic (z = -4.4)
- Apatou (97360, 10,306 hab) : au-dessus du pronostic (z = 4.3)
- Morzine (74191, 2,658 hab) : en dessous du pronostic (z = -4.2)
- Bourg-Saint-Maurice (73054, 7,270 hab) : en dessous du pronostic (z = -4.2)
- Le Grau-du-Roi (30133, 8,588 hab) : en dessous du pronostic (z = -4.1)
- Departements : PARIS (z = -3.4), ALPES-MARITIMES (z = -2.6), SEINE-SAINT-DENIS (z = 2.2), SAVOIE (z = -2.0), RHONE (z = -1.9)

### IPS (collèges) × Diversité des candidats (r communes -0.27, 3.3% de communes a |z| > 2.5)
- Villetaneuse (93079, 12,530 hab) : au-dessus du pronostic (z = 6.1)
- Arnouville (95019, 15,023 hab) : au-dessus du pronostic (z = 5.1)
- Sarcelles (95585, 59,173 hab) : au-dessus du pronostic (z = 5.0)
- Goussainville (95280, 31,301 hab) : au-dessus du pronostic (z = 4.9)
- Clichy-sous-Bois (93014, 29,354 hab) : au-dessus du pronostic (z = 4.9)
- Departements : MAYOTTE (z = 6.4), SEINE-SAINT-DENIS (z = 3.7), VAL-DE-MARNE (z = 2.7), HAUTS-DE-SEINE (z = 2.5), VAL-D'OISE (z = 2.1)

### IPS (lycées) × Diversité des candidats (r communes -0.30, 3.2% de communes a |z| > 2.5)
- Sarcelles (95585, 59,173 hab) : au-dessus du pronostic (z = 3.8)
- Goussainville (95280, 31,301 hab) : au-dessus du pronostic (z = 3.7)
- Les Mureaux (78440, 34,632 hab) : au-dessus du pronostic (z = 3.7)
- Clichy-sous-Bois (93014, 29,354 hab) : au-dessus du pronostic (z = 3.7)
- Arnouville (95019, 15,023 hab) : au-dessus du pronostic (z = 3.6)
- Departements : MAYOTTE (z = 5.9), SEINE-SAINT-DENIS (z = 3.6), VAL-DE-MARNE (z = 2.6), HAUTS-DE-SEINE (z = 2.5), VAL-D'OISE (z = 2.1)

### IPS (lycées) × Prix immobilier (r communes +0.35, 3.1% de communes a |z| > 2.5)
- Neuilly-sur-Seine (92051, 59,538 hab) : au-dessus du pronostic (z = 5.5)
- Levallois-Perret (92044, 68,092 hab) : au-dessus du pronostic (z = 4.7)
- Chamonix-Mont-Blanc (74056, 8,705 hab) : au-dessus du pronostic (z = 4.4)
- Gassin (83065, 2,687 hab) : au-dessus du pronostic (z = 4.3)
- Vincennes (94080, 48,193 hab) : au-dessus du pronostic (z = 4.2)
- Departements : PARIS (z = 5.6), HAUTS-DE-SEINE (z = 3.1), SEINE-SAINT-DENIS (z = 2.3), VAL-DE-MARNE (z = 2.2), ALPES-MARITIMES (z = 1.7)

### IPS (écoles) × Logement social (HLM) (r communes -0.25, 3.0% de communes a |z| > 2.5)
- Le Grand-Quevilly (76322, 25,789 hab) : au-dessus du pronostic (z = 7.8)
- Dugny (93030, 11,700 hab) : au-dessus du pronostic (z = 7.3)
- Val-de-Reuil (27701, 13,245 hab) : au-dessus du pronostic (z = 6.7)
- Villeneuve-la-Garenne (92078, 26,021 hab) : au-dessus du pronostic (z = 6.3)
- Grande-Synthe (59271, 20,239 hab) : au-dessus du pronostic (z = 6.1)

### IPS (lycées) × Revenu médian (r communes +0.58, 3.0% de communes a |z| > 2.5)
- Neuilly-sur-Seine (92051, 59,538 hab) : au-dessus du pronostic (z = 7.8)
- Saint-Cloud (92064, 29,855 hab) : au-dessus du pronostic (z = 5.1)
- Le Vésinet (78650, 15,554 hab) : au-dessus du pronostic (z = 4.7)
- Étiolles (91225, 3,105 hab) : au-dessus du pronostic (z = 4.4)
- La Garenne-Colombes (92035, 30,197 hab) : au-dessus du pronostic (z = 4.4)
- Departements : HAUTS-DE-SEINE (z = 3.7), PARIS (z = 3.3), HAUTE-SAVOIE (z = 3.2), HAUT-RHIN (z = 2.1), YVELINES (z = 1.8)

## 6. Table complete

| Paire | r dept | r communes (pond.) | Spearman | n communes | Signaux |
|---|---|---|---|---|---|
| Diplômés du supérieur × Cadres | +0.95 | +0.94 | +0.54 | 34608 | meme-groupe |
| IPS (collèges) × IPS (écoles) | +0.96 | +0.93 | +0.89 | 3564 | meme-groupe |
| Propriétaires × Maisons individuelles | +0.83 | +0.89 | +0.63 | 34688 | meme-groupe |
| IPS (écoles) × Revenu médian | +0.82 | +0.87 | +0.76 | 15631 |  |
| IPS (collèges) × Revenu médian | +0.77 | +0.86 | +0.78 | 3509 |  |
| Prix immobilier × Cadres | +0.84 | +0.82 | +0.45 | 33061 |  |
| Diplômés du supérieur × Ouvriers | -0.82 | -0.81 | -0.51 | 34608 | meme-groupe |
| Cadres × Ouvriers | -0.77 | -0.80 | -0.45 | 34611 | meme-groupe |
| Logement social (HLM) × Propriétaires | -0.72 | -0.79 | -0.58 | 34688 | meme-groupe |
| Prix immobilier × Diplômés du supérieur | +0.85 | +0.77 | +0.58 | 33138 |  |
| IPS (collèges) × IPS (lycées) | +0.94 | +0.75 | +0.69 | 1143 | meme-groupe |
| IPS (écoles) × Diplômés du supérieur | +0.81 | +0.72 | +0.79 | 15727 |  |
| IPS (écoles) × IPS (lycées) | +0.90 | +0.70 | +0.60 | 1199 | meme-groupe |
| 65 ans et plus × Taux de natalité | -0.87 | -0.69 | -0.49 | 34691 | meme-groupe |
| Revenu médian × Diplômés du supérieur | +0.79 | +0.69 | +0.62 | 30836 |  |
| Prix immobilier × Ouvriers | -0.79 | -0.67 | -0.34 | 33061 |  |
| Revenu médian × Cadres | +0.75 | +0.66 | +0.47 | 30838 |  |
| IPS (écoles) × Ouvriers | -0.63 | -0.66 | -0.65 | 15727 |  |
| IPS (collèges) × Diplômés du supérieur | +0.73 | +0.65 | +0.69 | 3581 |  |
| IPS (écoles) × Cadres | +0.66 | +0.64 | +0.63 | 15727 |  |
| Cadres × Employés | -0.71 | -0.64 | -0.23 | 34611 | meme-groupe |
| Revenu médian × Prix immobilier | +0.69 | +0.64 | +0.56 | 29295 | meme-groupe |
| IPS (lycées) × Revenu médian | +0.64 | +0.64 | +0.54 | 1156 |  |
| Logement social (HLM) × Maisons individuelles | -0.55 | -0.63 | -0.48 | 34688 | meme-groupe |
| Diversité des candidats × Taux de natalité | +0.67 | +0.63 | +0.20 | 11417 |  |
| Jeunes (0-14 ans) × 65 ans et plus | -0.85 | -0.63 | -0.77 | 34691 | meme-groupe |
| Revenu médian × Employés | -0.77 | -0.62 | -0.21 | 30838 |  |
| IPS (collèges) × Employés | -0.60 | -0.61 | -0.42 | 3581 |  |
| IPS (collèges) × Cadres | +0.57 | +0.61 | +0.58 | 3581 |  |
| IPS (collèges) × Ouvriers | -0.57 | -0.61 | -0.62 | 3581 |  |
| IPS (écoles) × Employés | -0.66 | -0.61 | -0.34 | 15727 |  |
| Diplômés du supérieur × Employés | -0.73 | -0.61 | -0.21 | 34608 | meme-groupe |
| IPS (lycées) × Diplômés du supérieur | +0.60 | +0.60 | +0.51 | 1193 |  |
| Diversité des candidats × Logement social (HLM) | +0.65 | +0.60 | +0.30 | 11414 |  |
| Jeunes (0-14 ans) × Taux de natalité | +0.93 | +0.59 | +0.48 | 34691 | meme-groupe, ecart-mailles |
| Prix immobilier × Maisons individuelles | -0.84 | -0.59 | -0.35 | 33139 | ecart-mailles |
| Maisons individuelles × Cadres | -0.78 | -0.57 | -0.19 | 34608 |  |
| Revenu médian × Ouvriers | -0.49 | -0.56 | -0.34 | 30838 |  |
| IPS (lycées) × Cadres | +0.43 | +0.55 | +0.45 | 1193 |  |
| IPS (lycées) × Employés | -0.56 | -0.55 | -0.36 | 1193 |  |
| IPS (écoles) × Prix immobilier | +0.52 | +0.53 | +0.60 | 14842 |  |
| IPS (lycées) × Ouvriers | -0.45 | -0.53 | -0.44 | 1193 |  |
| Diversité des candidats × Maisons individuelles | -0.64 | -0.52 | -0.37 | 11414 |  |
| Diplômés du supérieur × Maisons individuelles | -0.79 | -0.52 | -0.18 | 34688 | ecart-mailles |
| Résidences secondaires × 65 ans et plus | +0.51 | +0.51 | +0.50 | 34688 |  |
| IPS (collèges) × Prix immobilier | +0.47 | +0.51 | +0.51 | 3405 |  |
| Prix immobilier × Employés | -0.47 | -0.50 | -0.05 | 33061 |  |
| Diversité des candidats × Propriétaires | -0.66 | -0.50 | -0.29 | 11414 |  |
| Logement social (HLM) × Taux de natalité | +0.65 | +0.49 | +0.14 | 34688 |  |
| Diversité des candidats × 65 ans et plus | -0.63 | -0.48 | -0.17 | 11417 |  |
| IPS (collèges) × Logement social (HLM) | -0.20 | -0.47 | -0.31 | 3581 | ecart-mailles |
| Propriétaires × Taux de natalité | -0.69 | -0.46 | -0.09 | 34688 |  |
| IPS (collèges) × Propriétaires | +0.03 | +0.44 | +0.35 | 3581 | ecart-mailles |
| IPS (lycées) × Jeunes (0-14 ans) | -0.41 | -0.44 | -0.21 | 1193 |  |
| Résidences secondaires × Jeunes (0-14 ans) | -0.44 | -0.43 | -0.47 | 34688 |  |
| IPS (écoles) × Logement social (HLM) | -0.08 | -0.43 | -0.17 | 15727 | ecart-mailles |
| Maisons individuelles × Ouvriers | +0.72 | +0.43 | +0.13 | 34608 | ecart-mailles |
| Maisons individuelles × Taux de natalité | -0.47 | -0.42 | -0.03 | 34688 |  |
| IPS (lycées) × Logement social (HLM) | -0.29 | -0.42 | -0.29 | 1193 |  |
| IPS (écoles) × Propriétaires | -0.08 | +0.41 | +0.25 | 15727 | ecart-mailles |
| Diversité des candidats × Jeunes (0-14 ans) | +0.54 | +0.41 | +0.14 | 11417 |  |
| IPS (lycées) × Taux de natalité | -0.35 | -0.39 | -0.24 | 1193 |  |
| Prix immobilier × Propriétaires | -0.73 | -0.38 | -0.18 | 33138 | ecart-mailles |
| IPS (écoles) × Logements vacants | -0.37 | -0.37 | -0.41 | 15727 |  |
| Revenu médian × Logement social (HLM) | +0.20 | -0.37 | -0.09 | 30836 | inversion-de-signe |
| Propriétaires × Cadres | -0.68 | -0.37 | -0.04 | 34608 | ecart-mailles |
| IPS (collèges) × Taux de natalité | -0.28 | -0.36 | -0.15 | 3581 |  |
| Logement social (HLM) × 65 ans et plus | -0.75 | -0.36 | -0.07 | 34688 | ecart-mailles |
| Employés × Ouvriers | +0.28 | +0.36 | -0.04 | 34611 | meme-groupe |
| IPS (lycées) × Diversité des candidats | -0.44 | -0.36 | -0.14 | 1193 | non-lineaire-ou-outliers |
| Propriétaires × 65 ans et plus | +0.76 | +0.35 | -0.02 | 34688 | ecart-mailles |
| Résidences secondaires × Taux de natalité | -0.41 | -0.35 | -0.34 | 34688 |  |
| Maisons individuelles × 65 ans et plus | +0.61 | +0.34 | -0.00 | 34688 | ecart-mailles |
| IPS (collèges) × Diversité des candidats | -0.31 | -0.34 | -0.10 | 3234 | non-lineaire-ou-outliers |
| 65 ans et plus × Cadres | -0.59 | -0.33 | -0.17 | 34611 | ecart-mailles |
| IPS (lycées) × Prix immobilier | +0.34 | +0.32 | +0.32 | 1144 |  |
| Diplômés du supérieur × 65 ans et plus | -0.48 | -0.32 | -0.27 | 34688 |  |
| IPS (écoles) × Professions intermédiaires | +0.16 | +0.30 | +0.43 | 15727 |  |
| IPS (collèges) × Logements vacants | -0.34 | -0.29 | -0.37 | 3581 |  |
| Logement social (HLM) × Résidences secondaires | -0.53 | -0.29 | -0.26 | 34688 | meme-groupe |
| Diplômés du supérieur × Propriétaires | -0.58 | -0.28 | +0.03 | 34688 | ecart-mailles |
| Logements vacants × Professions intermédiaires | -0.35 | -0.28 | -0.21 | 34608 |  |
| Revenu médian × Propriétaires | -0.32 | +0.27 | +0.25 | 30836 | inversion-de-signe |
| IPS (collèges) × Jeunes (0-14 ans) | -0.36 | -0.27 | +0.00 | 3581 |  |
| IPS (écoles) × Diversité des candidats | -0.24 | -0.26 | -0.00 | 8840 |  |
| IPS (écoles) × Taux de natalité | -0.18 | -0.26 | +0.01 | 15727 |  |
| Prix immobilier × 65 ans et plus | -0.52 | -0.26 | -0.33 | 33141 | ecart-mailles |
| Logement social (HLM) × Employés | -0.18 | +0.25 | +0.16 | 34608 | inversion-de-signe |
| Revenu médian × Diversité des candidats | +0.24 | -0.24 | +0.06 | 11280 | inversion-de-signe |
| IPS (collèges) × Professions intermédiaires | +0.09 | +0.24 | +0.44 | 3581 |  |
| Logement social (HLM) × Jeunes (0-14 ans) | +0.59 | +0.24 | +0.12 | 34688 | ecart-mailles |
| Revenu médian × Logements vacants | -0.30 | -0.24 | -0.39 | 30836 |  |
| Prix immobilier × Jeunes (0-14 ans) | +0.19 | -0.24 | +0.27 | 33141 | inversion-de-signe |
| Logements vacants × Ouvriers | +0.34 | +0.23 | +0.22 | 34608 |  |
| Logements vacants × Jeunes (0-14 ans) | -0.28 | -0.23 | -0.17 | 34688 |  |
| Propriétaires × Ouvriers | +0.60 | +0.23 | -0.01 | 34608 | ecart-mailles |
| Professions intermédiaires × Ouvriers | -0.18 | -0.23 | -0.36 | 34611 | meme-groupe |
| Jeunes (0-14 ans) × Cadres | +0.23 | -0.22 | +0.13 | 34611 | inversion-de-signe |
| Prix immobilier × Diversité des candidats | +0.54 | +0.21 | +0.25 | 10837 | ecart-mailles |
| 65 ans et plus × Ouvriers | +0.36 | +0.21 | -0.02 | 34611 |  |
| Diversité des candidats × Résidences secondaires | -0.30 | -0.20 | -0.25 | 11414 |  |
| Jeunes (0-14 ans) × Ouvriers | -0.06 | +0.20 | +0.03 | 34611 | ecart-mailles |
| Diplômés du supérieur × Logements vacants | -0.45 | -0.20 | -0.36 | 34688 | ecart-mailles |
| IPS (lycées) × Propriétaires | +0.16 | +0.19 | +0.16 | 1193 |  |
| Taux de natalité × Cadres | +0.41 | +0.19 | +0.08 | 34611 |  |
| Prix immobilier × Logements vacants | -0.46 | -0.18 | -0.47 | 33139 | ecart-mailles |
| Prix immobilier × Taux de natalité | +0.41 | +0.18 | +0.21 | 33141 |  |
| Logements vacants × 65 ans et plus | +0.39 | +0.18 | +0.21 | 34688 |  |
| Jeunes (0-14 ans) × Professions intermédiaires | +0.30 | +0.18 | +0.21 | 34611 |  |
| Prix immobilier × Professions intermédiaires | -0.01 | -0.18 | +0.30 | 33061 |  |
| Propriétaires × Professions intermédiaires | -0.10 | +0.18 | +0.04 | 34608 | ecart-mailles |
| Jeunes (0-14 ans) × Employés | -0.07 | +0.17 | +0.00 | 34611 |  |
| Résidences secondaires × Professions intermédiaires | -0.01 | -0.17 | -0.26 | 34608 |  |
| IPS (lycées) × 65 ans et plus | +0.19 | +0.17 | +0.08 | 1193 |  |
| Logements vacants × Propriétaires | +0.32 | -0.17 | -0.07 | 34688 | meme-groupe, inversion-de-signe |
| IPS (lycées) × Professions intermédiaires | +0.10 | +0.17 | +0.24 | 1193 |  |
| IPS (lycées) × Résidences secondaires | +0.33 | +0.17 | +0.28 | 1193 |  |
| Revenu médian × Taux de natalité | +0.27 | -0.17 | +0.14 | 30839 | inversion-de-signe |
| Résidences secondaires × Propriétaires | +0.24 | +0.16 | +0.07 | 34688 | meme-groupe |
| Revenu médian × Jeunes (0-14 ans) | +0.13 | -0.16 | +0.26 | 30839 | inversion-de-signe |
| Diversité des candidats × Professions intermédiaires | -0.03 | -0.16 | +0.09 | 11417 |  |
| Diplômés du supérieur × Jeunes (0-14 ans) | +0.09 | -0.15 | +0.20 | 34688 |  |
| IPS (collèges) × 65 ans et plus | +0.07 | +0.15 | -0.07 | 3581 |  |
| Diversité des candidats × Cadres | +0.57 | +0.15 | +0.20 | 11417 | ecart-mailles |
| Prix immobilier × Logement social (HLM) | +0.39 | +0.15 | +0.27 | 33138 |  |
| IPS (lycées) × Maisons individuelles | -0.21 | -0.14 | -0.13 | 1193 |  |
| Logements vacants × Cadres | -0.35 | -0.14 | -0.24 | 34608 |  |
| Prix immobilier × Résidences secondaires | +0.07 | +0.13 | -0.26 | 33139 | non-lineaire-ou-outliers |
| Logement social (HLM) × Cadres | +0.49 | +0.13 | +0.14 | 34608 | ecart-mailles |
| Maisons individuelles × Professions intermédiaires | -0.19 | +0.13 | -0.09 | 34608 | inversion-de-signe |
| IPS (écoles) × Maisons individuelles | -0.47 | +0.13 | -0.04 | 15727 | inversion-de-signe |
| 65 ans et plus × Employés | +0.32 | +0.12 | +0.02 | 34611 |  |
| Diplômés du supérieur × Taux de natalité | +0.27 | +0.12 | +0.11 | 34688 |  |
| Diversité des candidats × Employés | -0.20 | +0.12 | +0.07 | 11417 | inversion-de-signe |
| Maisons individuelles × Jeunes (0-14 ans) | -0.28 | +0.12 | +0.04 | 34688 | inversion-de-signe |
| IPS (collèges) × Résidences secondaires | +0.28 | +0.12 | +0.07 | 3581 |  |
| Taux de natalité × Ouvriers | -0.28 | -0.11 | +0.04 | 34611 |  |
| 65 ans et plus × Professions intermédiaires | -0.33 | -0.11 | -0.23 | 34611 |  |
| Propriétaires × Employés | +0.23 | -0.11 | -0.14 | 34608 | inversion-de-signe |
| IPS (écoles) × Jeunes (0-14 ans) | -0.26 | -0.11 | +0.15 | 15727 |  |
| Valeur ajoutée (lycées) × Professions intermédiaires | -0.01 | -0.11 | -0.09 | 1308 |  |
| IPS (lycées) × Logements vacants | -0.31 | -0.11 | -0.17 | 1193 |  |
| Logement social (HLM) × Professions intermédiaires | +0.09 | -0.11 | +0.07 | 34608 |  |
| IPS (collèges) × Valeur ajoutée (lycées) | -0.06 | -0.10 | -0.02 | 1190 | meme-groupe |
| Logements vacants × Employés | +0.24 | +0.10 | +0.05 | 34608 |  |
| Cadres × Professions intermédiaires | +0.01 | -0.10 | +0.15 | 34611 | meme-groupe |
| Valeur ajoutée (lycées) × Revenu médian | -0.07 | -0.10 | -0.02 | 1272 |  |
| Diplômés du supérieur × Professions intermédiaires | +0.14 | +0.10 | +0.36 | 34608 | meme-groupe |
| Professions intermédiaires × Employés | -0.01 | -0.09 | -0.25 | 34611 | meme-groupe |
| IPS (écoles) × Valeur ajoutée (lycées) | -0.06 | -0.09 | -0.02 | 1301 | meme-groupe |
| Diversité des candidats × Logements vacants | -0.25 | -0.09 | -0.03 | 11414 |  |
| IPS (collèges) × Maisons individuelles | -0.35 | +0.09 | -0.01 | 3581 | ecart-mailles |
| Résidences secondaires × Cadres | -0.28 | -0.09 | -0.21 | 34608 |  |
| Valeur ajoutée (lycées) × Logements vacants | +0.02 | +0.09 | +0.07 | 1308 |  |
| Résidences secondaires × Logements vacants | -0.25 | -0.08 | +0.09 | 34689 | meme-groupe, non-lineaire-ou-outliers |
| IPS (lycées) × Valeur ajoutée (lycées) | -0.07 | -0.08 | -0.01 | 1176 | meme-groupe |
| Valeur ajoutée (lycées) × Employés | +0.22 | +0.08 | +0.03 | 1308 |  |
| Valeur ajoutée (lycées) × Diplômés du supérieur | +0.04 | -0.07 | -0.06 | 1308 |  |
| Diversité des candidats × Ouvriers | -0.47 | -0.07 | -0.16 | 11417 | ecart-mailles |
| Logements vacants × Maisons individuelles | +0.44 | -0.07 | +0.04 | 34689 | meme-groupe, ecart-mailles |
| Valeur ajoutée (lycées) × Cadres | -0.02 | -0.07 | -0.09 | 1308 |  |
| IPS (écoles) × Résidences secondaires | +0.18 | +0.07 | -0.12 | 15727 |  |
| Revenu médian × Résidences secondaires | -0.08 | +0.06 | -0.35 | 30836 |  |
| Résidences secondaires × Maisons individuelles | +0.04 | +0.06 | +0.12 | 34689 | meme-groupe, non-lineaire-ou-outliers |
| Maisons individuelles × Employés | +0.41 | +0.06 | -0.09 | 34608 | ecart-mailles |
| Taux de natalité × Employés | -0.13 | +0.06 | +0.02 | 34611 |  |
| Revenu médian × 65 ans et plus | -0.40 | -0.05 | -0.38 | 30839 | ecart-mailles |
| Résidences secondaires × Ouvriers | -0.14 | -0.05 | -0.03 | 34608 |  |
| Propriétaires × Jeunes (0-14 ans) | -0.50 | +0.05 | +0.02 | 34688 | ecart-mailles |
| Valeur ajoutée (lycées) × Diversité des candidats | +0.04 | +0.05 | -0.15 | 1280 |  |
| Valeur ajoutée (lycées) × Taux de natalité | +0.01 | +0.05 | -0.10 | 1308 |  |
| Valeur ajoutée (lycées) × Ouvriers | -0.23 | +0.05 | +0.06 | 1308 | ecart-mailles |
| Valeur ajoutée (lycées) × Logement social (HLM) | -0.10 | -0.04 | -0.15 | 1308 |  |
| Diversité des candidats × Diplômés du supérieur | +0.46 | +0.04 | +0.13 | 11414 | ecart-mailles |
| Revenu médian × Professions intermédiaires | +0.06 | +0.04 | +0.38 | 30838 |  |
| Diplômés du supérieur × Résidences secondaires | -0.07 | -0.04 | -0.13 | 34688 |  |
| Logements vacants × Taux de natalité | -0.22 | -0.03 | -0.05 | 34688 |  |
| Valeur ajoutée (lycées) × Résidences secondaires | +0.21 | +0.03 | +0.11 | 1308 |  |
| Valeur ajoutée (lycées) × Maisons individuelles | -0.09 | +0.03 | +0.10 | 1308 |  |
| IPS (écoles) × 65 ans et plus | -0.05 | +0.02 | -0.21 | 15727 |  |
| Valeur ajoutée (lycées) × Jeunes (0-14 ans) | -0.06 | +0.02 | -0.07 | 1308 |  |
| Valeur ajoutée (lycées) × Propriétaires | -0.11 | -0.02 | +0.08 | 1308 |  |
| Logement social (HLM) × Ouvriers | -0.22 | -0.02 | +0.01 | 34608 |  |
| Résidences secondaires × Employés | +0.28 | -0.02 | -0.07 | 34608 | ecart-mailles |
| Valeur ajoutée (lycées) × 65 ans et plus | +0.02 | -0.01 | +0.07 | 1308 |  |
| Diplômés du supérieur × Logement social (HLM) | +0.31 | +0.01 | +0.02 | 34688 | ecart-mailles |
| Valeur ajoutée (lycées) × Prix immobilier | +0.19 | +0.01 | -0.01 | 1249 |  |
| Revenu médian × Maisons individuelles | -0.58 | -0.01 | -0.06 | 30836 | ecart-mailles |
| Taux de natalité × Professions intermédiaires | +0.20 | +0.00 | +0.13 | 34611 |  |
| Logement social (HLM) × Logements vacants | -0.17 | -0.00 | -0.03 | 34688 | meme-groupe |
