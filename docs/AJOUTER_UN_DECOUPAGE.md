# Ajouter un découpage (unité d'analyse)

> Un « découpage » est l'unité d'analyse de l'explorateur : ce qu'est une ligne. Aujourd'hui :
> **territoire** (commune / département, cas spécial avec carte) et **milieu social** (CSP).
> Génération et genre suivront. Ce guide explique comment brancher une unité **non géographique**
> (genre, génération, niveau de diplôme, parti...). Exemple de référence : `milieu-social`.

## Le modèle

Tout se ramène à : **Découpage (unité) × Indicateur × Mode de lecture.**
- Le **territoire** est le cas spécial : il a une carte et lit des fichiers communes ; il vit sur
  ses pages dédiées `/atlas` et `/territoires`. On n'y touche pas.
- Tout découpage **non géographique** passe par le **moteur générique** `UnitView`
  (`frontend/src/pages/explorer/UnitView.jsx`), route `/explorer/:id`. Il affiche deux modes :
  **Tableau de bord** (toutes les catégories comparées, par indicateur) et **Fiche**
  (`?cat=...`, une catégorie située parmi les autres). Pas de carte.

Brancher une nouvelle unité non géographique = **2 fichiers**, aucun code de rendu à écrire.

## Étape 1 : le fichier de données

`frontend/public/data/decoupages/<id>.json` (ex. `milieu-social.json`). Chiffres **réels et
sourcés** (INSEE en priorité ; chaque indicateur porte sa source et son année). Forme :

```json
{
  "id": "<id>",
  "note": "Phrase de cadrage (périmètre, limites).",
  "references": { "<indicateur>": 29170 },          // valeur d'ensemble (facultatif, affichée en repère)
  "sources":    { "<indicateur>": "Insee, ... AAAA" },
  "categories": [
    {
      "id": "ouvriers",
      "nom": "Ouvriers",
      "precision": "texte facultatif",
      "couleur": "#EF4444",
      "valeurs": { "<indicateur>": 22250, "autre": 13.9 },
      "detail":  { "<indicateur>": { "Ouvriers non qualifiés": 24 } }   // facultatif : CSP/sous-groupes fins
    }
  ]
}
```

Règles : les **mêmes catégories** pour tous les indicateurs (jeu de lignes commun) ; `null` quand une
valeur n'existe pas ; `detail` pour une granularité plus fine, affichée en sous-note sans casser la
comparaison.

## Étape 2 : la config

Dans `frontend/src/config/decoupages.js`, sur l'entrée du découpage :
- passer `statut` à `'disponible'` ;
- `aCarte: false` ;
- `route: '/explorer/<id>'`, `dataUrl: '/data/decoupages/<id>.json'` ;
- `modes: ['tableau', 'fiche']`,
  `modeRoutes: { tableau: '/explorer/<id>', fiche: '/explorer/<id>' }` ;
- `rowLabel` / `rowLabelPluriel` (ex. « catégorie » / « catégories ») ;
- `intro` (sous-titre de la page) ;
- `indicateurs: [{ id, label, unite, fmt, sens, aide }]` où `fmt` est une fonction d'affichage
  (ex. `(v) => v + ' %'`) et `sens` vaut `'haut'` (valeur haute = favorable) ou `'bas'`. `id` doit
  correspondre aux clés de `valeurs` dans le JSON.

## C'est tout

`/explorer/<id>` s'affiche via `UnitView`, et **la barre d'explorateur + le menu Explorer l'exposent
automatiquement** (ils se construisent depuis `DECOUPAGES`). Rien d'autre à câbler : pas de route à
ajouter (la route `/explorer/:id` est générique dans `App.jsx`), pas de composant à écrire.

Vérifier : `cd frontend ; npm run build`, puis `npm run dev` et ouvrir `/explorer/<id>` (tableau) et
`/explorer/<id>?cat=<categorie>` (fiche).

## Rappels

- **Jamais de tiret cadratin** dans les textes (voir mémoire projet).
- Le territoire reste hors de ce moteur (carte + percentile sur la distribution nationale).
- Idées d'unités à venir : genre (femmes / hommes), génération (classes d'âge), niveau de diplôme
  (sans diplôme ... bac+5), nuance politique. Le diplôme est plus pertinent comme **unité** que comme
  indicateur d'une autre unité (sinon il est circulaire avec la CSP).
