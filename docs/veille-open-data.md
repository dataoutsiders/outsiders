# Veille des données ouvertes (« Radar open data »)

> Note de cadrage. Créée le 2026-07-03.
> Idée initiale : surveiller (automatiquement ?) les jeux de données ouvertes,
> français et internationaux, et peut-être publier cette veille sur le site.
> À ne pas confondre avec `docs/VEILLE_FRONTEND_OUTSIDERS.md`, qui est une veille
> **technique** (React, dataviz). Ici il s'agit d'une veille de **données**.

## Ça sert à quelque chose ? Oui, à deux conditions

Verdict : **oui, mais pas en mode automatique brut.** data.gouv.fr publie des
milliers de jeux de données, dont l'immense majorité sont administratifs et sans
intérêt éditorial (délibérations, stationnement, horaires...). Un flux brut non
filtré, c'est du bruit, l'inverse de la marque. La valeur n'est pas dans
l'automatisation de la collecte, elle est dans **la curation** : automatiser le
ramassage de candidats, garder un filtre éditorial (humain ou assisté par IA)
pour ne retenir que ce qui porte un angle.

Deux usages, de valeur très différente :

1. **Interne, le plus rentable et sans risque : un moteur à idées d'études.**
   Un backlog vivant de jeux de données pertinents pour les thèmes d'Outsiders
   (inégalités, territoires, représentation, école, santé, comparaison
   internationale), chacun assorti d'une phrase « pourquoi c'est intéressant,
   angle possible ». C'est le carburant des « idées reçues » et des prochains
   sujets. À faire **même si on ne publie jamais rien**.

2. **Public : une page « Radar open data ».** Un flux curé (rythme hebdomadaire,
   une poignée de trouvailles) qui attire les data-curieux et les journalistes,
   renforce le positionnement (« données ouvertes sous-exploitées »), et où
   chaque trouvaille peut devenir un outil ou une étude. Utile **seulement si
   curé** : qualité avant quantité. Un flux bâclé décrédibiliserait le site.

## Ce que ce n'est pas

- Pas un annuaire exhaustif (data.gouv.fr et data.europa.eu le font déjà).
- Pas un flux automatique non filtré (égale bruit).
- Pas un moteur de recherche de données.

Notre valeur ajoutée est **l'éditorialisation** : « voici 5 jeux frais qui
posent une vraie question sur la France, et l'angle pour la traiter ».

## Faisabilité (sources et API)

- **data.gouv.fr** : API `/api/1/datasets/?sort=-last_update` + filtres (tags,
  organisations, badges qualité). Les métriques de réutilisation sont exposées :
  peu réutilisé égale sous-exploité, c'est justement notre cible.
- **data.europa.eu** (portail UE), **Eurostat** (catalogue + API), **OCDE**
  (SDMX), **Banque mondiale** (API REST), **INSEE** (Melodi / BDM).
- Un script `python/tools/veille_opendata.py` interroge les catalogues, filtre
  par liste blanche de thèmes et mots-clés, dédoublonne, score chaque jeu
  (fraîcheur, granularité fine, faible réutilisation), et écrit
  `frontend/public/data/veille.json`. Le site rend une page statique.

## Automatiser le rafraîchissement (options)

Le site est **statique**, sans backend. « Automatisé » signifie donc un job
planifié qui régénère le JSON puis redéploie :

- **A. Manuel d'abord (recommandé pour démarrer).** On lance le script, on relit
  et on édite la sélection (c'est là qu'est le filtre éditorial), puis
  `npm run deploy`. Rythme hebdomadaire. Zéro infrastructure.
- **B. Semi-automatique sur le VPS OVH** (déjà disponible) : un cron lance le
  script puis wrangler deploy ; l'éditorial passe à une revue rapide.
- **C. GitHub Actions (cron).** Nécessite de mettre le dépôt sous git (il ne
  l'est pas aujourd'hui), ce qui serait de toute façon un bon investissement.
- **D. Cloudflare Cron Trigger + Worker** : un worker sert `veille.json`
  dynamiquement depuis KV. Plus « edge », plus de plomberie.

Reco : **A maintenant**, migrer vers **B ou C** si la veille prouve sa valeur.
Ne pas construire l'usine avant d'avoir prouvé le contenu.

## Synergies

- Alimente la home « idées reçues » et la shortlist de sujets
  (`docs/vision-et-sujets.md`).
- Quand un jeu pertinent tombe, nos moteurs (onomastique, Atlas, UnitView)
  permettent d'en tirer une étude rapidement.
- Cohérent avec l'axe « situer la France » : veille française **et**
  internationale.

## Risques et garde-fous

- **Bruit / slop** si non curé : la curation est non négociable.
- **Maintenance** : les API évoluent ; garder peu de sources, robustes.
- **Distraction** : la veille sert les études, elle ne les remplace pas. La
  cadrer dans le temps.
- **Citer la source et la licence** de chaque jeu (règle du projet).

## Prochaine étape proposée

Prototype de l'usage 1 (interne) : `veille_opendata.py` sur data.gouv.fr seul,
liste blanche de thèmes, top 15 « frais + peu réutilisés + granularité fine »,
sortie en Markdown qu'on lit ensemble. Si concluant, on ajoute Eurostat / OCDE
et on décide d'une page publique.
