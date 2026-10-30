# Outsiders, brief d'amélioration produit (v2)

> Document destiné à Claude Code. Recalibré après lecture de `projet.md`.
> Outsiders est déjà mature et bien architecturé : ce brief ne part pas de zéro,
> il vient ajouter une signature intellectuelle et corriger un manque, pas
> refaire l'existant.
>
> Fil rouge : **les outsiders, ce sont les territoires qui défient ce que leur
> profil prédit.** Ce n'est pas une idée neuve à plaquer, c'est la
> généralisation d'une lecture déjà présente dans la fiche territoire (IPS bas +
> valeur ajoutée positive = « une école qui compense »). On la sort d'un cas en
> dur pour en faire un mode explorable.
>
> Contraintes structurantes, à ne jamais violer :
> - **Pas de backend en production.** Tout est pré-calculé en JSON statique, ou
>   calculé dans le navigateur. React lit, c'est tout. Aucune route serveur.
> - **Site anonyme.** Aucune signature ni branding personnel.
> - **Pas de tiret cadratin** (règle de style du projet, déjà en vigueur).

---

## 0. Ce qui existe déjà, NE PAS refaire

À lire avant tout, pour éviter de reconstruire l'acquis :

- **Permaliens** : l'état des vues est déjà entièrement dans l'URL
  (`useSearchParams`). Les vues sont déjà partageables. Ne pas réinventer.
- **Croisement de deux indicateurs** : le paramètre `vs` affiche déjà un nuage
  de points dans l'Atlas. Le moteur de résidus est un **upgrade de ce nuage
  existant**, pas une page neuve.
- **Lecture combinée d'indicateurs** : la fiche territoire fait déjà des
  lectures du type « IPS bas mais valeur ajoutée positive ». L'amélioration
  consiste à hiérarchiser, pas à inventer.
- **Tri par inégalité** : la heatmap des unités non géo trie déjà par « Écart »
  (max/min). L'esprit « faire remonter les écarts » est déjà là.
- **Onomastique en navigateur** : déjà fait, déjà validé (IDP candidats ~4,4 %,
  sexe ~99 %), limites déjà affichées. Ne pas déplacer côté serveur.
- **Sources citées, limites affichées, couleurs neutres pour les comportements,
  reproductibilité** : déjà des principes éditoriaux en place.
- **Audit diversité B2B** : déjà inscrit en section 13 de la roadmap.

---

## 1. Le différenciateur (boussole d'arbitrage)

Une carte choroplèthe et un croisement à deux indicateurs, **tout le monde le
fait** (INSEE Statistiques locales, Observatoire des territoires). Le `vs`
actuel est une commodité, pas un hameçon. Ce qui n'existe nulle part pour le
grand public en France, c'est de mettre au centre **l'écart au pronostic** :

- Un IPS élevé devrait produire tel IVAL. Le territoire intéressant n'est pas
  celui qui réussit, c'est celui qui réussit (ou échoue) **contre son
  pronostic**.
- Tu as déjà prouvé que cette lecture accroche, en dur, dans la fiche. Le moteur
  de résidus la rend générique et explorable. Le nom (« outsiders »), la mission
  (« angles morts »), et la fonction s'emboîtent enfin sur une vraie mécanique.

Règle : à chaque choix, privilégier ce qui révèle un **écart, une atypie, une
surprise** plutôt qu'un niveau brut. Le niveau brut, tu le sers déjà très bien.
La surprise, c'est le produit différenciant.

---

## 2. Feuille de route priorisée

### P0, le moteur « Outsiders » (résidus), upgrade du nuage `vs`

Point de départ : le nuage `vs` existe déjà dans l'Atlas. On l'enrichit.

**Ce qu'on ajoute au nuage existant**
1. La **droite d'ajustement** (OLS) sur le nuage X / Y déjà affiché.
2. Le **surlignage des résidus extrêmes** : au-dessus de la droite (Y plus fort
   que prédit) et en dessous (Y plus faible). Ce sont les outsiders.
3. **Deux listes cliquables** des outsiders (positifs / négatifs), reliées à la
   carte (survol d'un nom = surbrillance du territoire) et à sa fiche.
4. Une **phrase de lecture** générée, strictement descriptive : « à revenu
   comparable, cette commune obtient une réussite scolaire nettement
   supérieure à ce que sa situation laisse attendre ». Jamais de « parce que ».

**Méthode (les garde-fous de crédibilité, non négociables)**
- OLS simple en v1. Architecturer pour brancher une régression robuste
  (Huber) en v2, car les outliers tirent la droite.
- **Résidus studentisés** (standardisés), pas bruts : la surprise doit être
  comparable d'un point à l'autre.
- **Filtre / pondération population. À ne PAS livrer sans ça.** Sans seuil, les
  outsiders ne seront que de petites communes à forte variance : trois familles
  qui font basculer un indicateur. L'outil aurait l'air intelligent et ne
  remonterait que du bruit. Pour un public socio quanti, c'est la faille qu'un
  pair repère en dix secondes. Seuil paramétrable (défaut suggéré : exclure
  < 1 000 hab.), idéalement pondération par population. Prérequis : disposer du
  champ population par unité dans les JSON chargés.
- Afficher le **R²** de la relation. Si elle est faible, le dire : « cette
  relation explique peu, les écarts sont à lire avec prudence ».
- Le changement de maille (commune / EPCI / département) doit recalculer la
  relation : c'est le MAUP rendu visible, pas un bug.

**v2 (prévoir la place, ne pas faire maintenant)** : résidu partiel contrôlant
une 3ᵉ variable. Ex : « part de femmes élues, à population ET orientation
politique égales ».

### P1, hiérarchiser la fiche territoire par atypies

La fiche situe déjà chaque indicateur par percentile et produit des lectures
combinées. Manque : **mener avec ce qui sort de l'ordinaire**.

- Réutiliser les percentiles déjà calculés pour classer les indicateurs par
  `|écart à la référence|` et **remonter en tête de fiche les 5-6 plus
  atypiques** : « ce qui rend ce territoire inhabituel ».
- Laisser le **groupe de référence** au choix : national, même département, même
  tranche de population, même catégorie urbain / rural. Le caractère atypique
  dépend de à-quoi-on-compare, et le montrer est honnête.
- Le reste de la fiche ne change pas, il passe juste en second rang.

### P1, le jumeau statistique (nouveau)

Fonction « waouh » à faible coût, fort potentiel de partage, 100 % navigateur.

- Plus proche voisin d'un territoire dans l'espace multi-indicateurs
  **standardisé** (z-scores). Distance euclidienne en v1, Mahalanobis si le temps
  le permet (gère les corrélations entre indicateurs).
- Formulation narrative : « la commune la plus proche de X sur N indicateurs est
  Y, à Z km, sauf qu'elles divergent radicalement sur [indicateur d'écart
  maximal] ».
- Variante « anti-jumeau » : le plus dissemblable à population comparable.

### P2, embeds (les permaliens, eux, sont déjà faits)

Permaliens : déjà en place. Ce qui manque, c'est l'intégrabilité.

- Route `/embed/...` rendant une vue épurée, responsive, iframe-able, avec
  attribution et lien source visibles (cohérent CC BY et anonymat).
- Bouton « copier le code d'intégration » sur cartes et graphes.
- Levier de diffusion le moins cher : un journaliste intègre ta carte sourcée
  en deux clics, ta signature circule sans effort. C'est le multiplicateur.

### P2, format dossier

Les Dossiers (Terrains, Thèmes) existent déjà. Si leur format n'est pas encore
du scrollytelling (texte qui défile, visualisation qui réagit), en faire un
**gabarit réutilisable** qui rebranche les composants carte / nuage existants,
sans les redévelopper. Sinon, passer.

---

## 3. Garde-fous spécifiques au moteur de résidus (nouveaux)

Le reste de tes principes (sources, limites, neutralité, reproductibilité) est
déjà en place. Ces trois points sont propres à la fonctionnalité neuve et
doivent être traités comme des fonctionnalités, pas des disclaimers.

- **Erreur écologique.** Une corrélation au niveau commune n'implique rien au
  niveau individuel. La phrase de lecture générée ne doit jamais le laisser
  croire. Formulation type, affichée près du nuage.
- **MAUP.** Les outsiders changent avec la maille. Le recalcul au changement de
  maille rend ce fait visible plutôt que de le cacher.
- **Zéro causalité dans les libellés auto-générés.** Les résidus sont des
  signaux descriptifs (« ça mérite qu'on regarde »), jamais des explications.
  Bannir « parce que », « explique », « dû à » des sorties automatiques.

---

## 4. L'outil Représentativité : placement déjà bon, garder la rigueur

Déjà correctement rangé sous `/outils`, pas en page d'accueil. Bon réflexe : le
« waouh » doit venir de la surprise intellectuelle (résidus, jumeaux), pas d'un
classement de territoires par diversité.

- Garder le traitement en navigateur, et continuer de l'afficher clairement.
- Garder les limites de l'IDP au plus près de l'outil (proxy attaché au nom,
  référentiel naissances en France, sous-estimation des diversités antérieures
  à 1950, cas ultramarins).
- Ne jamais produire de palmarès « territoires les plus / moins divers ».
- L'audit B2B (déjà en roadmap) est probablement ta source de revenu la plus
  naturelle et ne trahit pas l'open data : auditer la composition d'un conseil,
  d'un comité, d'une liste se facture sans rien paywaller.

---

## 5. Présentation : porter le bon cadrage interne vers le site

`projet.md` a un cadrage fort (« angles morts », « situer la France », Becker
assumé en clin d'œil léger). Le texte public « Le projet » est plus plat et
pourrait habiller n'importe quel projet open data. Le moins cher des gains :
**porter le cadrage interne vers la page publique**, pas en inventer un.

- Ouvrir sur la promesse distinctive : on ne montre pas des chiffres, on montre
  **les territoires qui démentent leur pronostic**, les angles morts.
- Reléguer après la promesse les cases déjà supposées acquises par l'audience
  (sources, vie privée, CC BY).
- Rester anonyme : « nous » impersonnel, aucun nom, aucune biographie.
- Réécrire la page **une fois le moteur de résidus en ligne**, pour que le texte
  décrive ce qui existe vraiment.

---

## 6. Notes techniques (corrigées pour l'archi statique)

Archi réelle : React 19 / Vite 7 / Tailwind 4, react-router 7 (état dans
l'URL), Leaflet, recharts, code-splitting par route. **Pas de backend.** JSON
pré-calculés par scripts Python, lus au runtime. Déploiement Cloudflare Pages.

- **Où calculer les résidus ? Dans le navigateur.** Le nuage `vs` charge déjà
  les deux colonnes d'indicateurs pour toutes les unités d'une maille. OLS +
  résidus studentisés sur ~34 700 communes, c'est quelques millisecondes en JS
  pur. Aucune route serveur, aucun pré-calcul combinatoire (190 paires × 3
  mailles serait absurde à pré-cuire). Parfaitement raccord avec « tout dans le
  navigateur ».
- **Prérequis données** : exposer un champ **population** par unité dans les JSON
  de l'Atlas, pour le filtre et la pondération. Le vérifier avant de coder le P0.
- Le jumeau statistique se calcule aussi en navigateur sur les JSON déjà chargés.
- Tests sur cas tordus : indicateur manquant pour une unité, variance nulle,
  maille à peu de points, valeurs aberrantes.
- Côté carte, le rendu Leaflet par polygone est déjà géré ; ne pas régresser sur
  la perf en ajoutant le surlignage des outsiders (réutiliser les couches
  existantes).
- L'onomastique reste strictement en navigateur. Ne pas y toucher.

---

## 7. Ce qu'il ne faut PAS faire

- Pas de backend, pas de route serveur, pas de pré-calcul combinatoire des
  paires : le moteur de résidus vit dans le navigateur.
- Pas de contenu payant : audience de niche, faible consentement, frontal avec
  l'éthos CC BY.
- Pas de signature ni branding personnel (anonymat).
- Pas de reconstruction de l'existant (permaliens, nuage `vs`, lectures
  combinées de fiche, tri par Écart) : on enrichit, on ne refait pas.
- Pas d'empilement d'indicateurs « pour faire plus ». La profondeur de lecture
  est le sujet, pas la largeur du catalogue.
- Pas de palmarès qui « notent » les territoires.
- Pas de langage causal dans les sorties auto-générées.
- Pas de tiret cadratin.

---

## Ordre de bataille suggéré

1. **P0** moteur de résidus : droite + résidus studentisés + filtre population +
   R², en upgrade du nuage `vs`, dans le navigateur. (Vérifier d'abord la
   présence du champ population dans les JSON.)
2. **P1** hiérarchisation de la fiche territoire par atypies (réutilise les
   percentiles existants).
3. **P1** jumeau statistique.
4. **P2** embeds.
5. **P2** gabarit dossier scrollytelling, si pertinent.
6. Réécriture de la page « Le projet » une fois le P0 en ligne, en portant le
   cadrage de `projet.md`.

Le P0 seul, bien fait, suffit à rendre le site singulier. Le reste est du bonus.
Résister à la tentation de tout attaquer en même temps : mieux vaut un moteur de
résidus qui claque que cinq fonctionnalités à moitié finies.
