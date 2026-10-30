# Veille frontend appliquée à *Outsiders*

> **Date** : 27 juin 2026
> **Source** : newsletters « This Week in React » (#283-287) + recherche dataviz/Polars 2026, croisées avec la stack réelle d'Outsiders (`%USERPROFILE%\Documents\VsCode\outsiders\frontend\src`).
> **Statut** : note de veille / aide à la décision. Rien n'est implémenté.
> **À noter** : document rangé dans `mip-project/outsiders/` pour centraliser les notes, mais il concerne le dépôt **outsiders** (séparé).

---

## 1. Constat de départ : Outsiders est déjà sur la stack moderne

Contrairement à mip-project (CRA/craco + React 18 + MUI/DSFR, en dette), Outsiders est **déjà là où mip cherche à aller** :

| Brique | Outsiders | Commentaire |
|--------|-----------|-------------|
| React | **19.2** | dernière majeure |
| Build | **Vite 7.2** (ESM) | pas de CRA, rien à fuir |
| CSS | **Tailwind 4.1** (`@tailwindcss/vite`) | à jour, plugin optimal |
| Router | **react-router-dom 7.10** | déjà en v7 |
| Dataviz | **recharts 3.5** + **leaflet 1.9** | à jour |
| Icônes | lucide-react | OK |
| Données | **JSON statiques** dans `/public/data` (fetch direct) + geo.api.gouv.fr | pas de backend applicatif |

**Conséquence** : la veille ne sert pas ici à rattraper un retard, mais à **exploiter ce que la stack permet déjà** et que le code n'utilise pas encore.

---

## 2. Recommandations priorisées

### #1, Activer le React Compiler (le meilleur rapport gain/effort)

Outsiders est le **cas idéal** pour le React Compiler (mémoïsation automatique) :
- **React 19 natif** : pas de polyfill `react-compiler-runtime` (contrairement à mip en React 18), `target` par défaut = 19.
- **Vite** : intégration directe via `babel-plugin-react-compiler` dans `vite.config.js` (ou la nouvelle voie Rust/oxc des dernières versions de Vite, cf. TWiR #286/#287).
- **Le code en a besoin** : **20 `useMemo`/`useCallback` répartis sur 7 fichiers** (Atlas, TerrainEcole, RepresentativiteTool, TerrainElus, ChoroplethMap, PointMap, useChapterData), dont des hacks de dépendances (`useCallback(..., [..., JSON.stringify(sectionIds)])` dans `useChapterData.js`). Le compilateur **rend cette mémoïsation manuelle largement inutile** et optimise les re-renders des vues lourdes en graphes/cartes (Atlas + AnalyseBloc + CroisementScatter).

Mise en place (≈30 min) :
```js
// vite.config.js
import react from '@vitejs/plugin-react'
export default {
  plugins: [react({ babel: { plugins: [['babel-plugin-react-compiler', { target: '19' }]] } })],
}
```
Vérifier d'abord la conformité aux *Rules of React* :
```bash
npx react-compiler-healthcheck@latest
```
Gain attendu : moins de re-renders sur les interactions (sélection d'indicateur, drill département → communes), et **du code plus simple** (on peut retirer la mémoïsation manuelle au fil de l'eau). Coût : léger surcroît de bundle (mémoïsation injectée), négligeable sur une app de cette taille.

> Rappel utile : sur mip-project (React 18 + CRA), le même POC a donné un gain modeste et bruité. Ici, **React 19 + Vite change la donne** (intégration propre, target natif), donc c'est bien plus indiqué.

### #2, Exploiter des fonctionnalités React 19 non utilisées

Le code utilise des patterns « React 18 » (`useState` + `useEffect` + `fetch`). React 19 offre mieux, et c'est gratuit :

- **`use()` + Suspense pour le chargement de données** : `useChapterData` / `useSectionData` (fetch dans un `useEffect` avec états `loading/error` manuels) peuvent devenir un `use(promise)` sous `<Suspense>` + `<ErrorBoundary>` (déjà présent : `components/ErrorBoundary.jsx`). Code plus court, moins d'états manuels.
- **Document metadata natif** : aucun `<title>`/`<meta>` par page (vérifié). Pour un site de **data-journalisme destiné au partage**, c'est un vrai manque : React 19 permet de poser `<title>` et les balises Open Graph **directement dans les composants de page** (Atlas, ThemeDetail…), pour des titres/aperçus corrects quand on partage un lien (l'Atlas encourage justement « copiez le lien pour partager cette vue »). Fort impact, faible effort.
- **`useEffectEvent`** (stabilisé en React 19.2, cf. TWiR #287) : utile pour les effets qui lisent des valeurs fraîches sans les remettre en dépendances (plusieurs `useEffect` de fetch dans Atlas/Terrains).

### #3, Rester à jour (faible effort, hygiène)

- **Vite 7 → 8** : Vite 8.1 est sorti (TWiR #287) avec *Bundled Dev Mode* et bascule Rolldown (builds/HMR plus rapides). Montée de version classique.
- **React Router 7 → 8** : la v8 (TWiR #287) est un *« boring upgrade »* volontaire (ESM-only, *future flags* par défaut). Vous êtes déjà en v7, donc la marche est petite.

### Dataviz (recharts + leaflet)

- **recharts 3.5** est le bon défaut, rien à changer. (cf. paysage dataviz 2026 : recharts reste la référence React pour ce type de dashboards.)
- **Accessibilité** : si Outsiders est public, les graphes SVG recharts demandent un travail a11y manuel (ARIA, navigation clavier). Si la conformité devient un enjeu, **nivo** est la lib la plus accessible *out of the box* ; sinon, garder recharts et ajouter les attributs a11y aux points sensibles.
- **Cartes** : leaflet + GeoJSON chargé depuis geo.api.gouv.fr à la volée convient. Si un jour vous voulez des cartes vectorielles plus riches / gros volumes : **MapLibre GL** ou **deck.gl** (cf. TWiR), mais pas nécessaire au vu de l'usage actuel.

### Sécurité / chaîne d'approvisionnement

Surface **faible** : arbre de dépendances petit et moderne, pas d'`axios`/`lodash`/`xlsx` (les points sensibles de mip). À maintenir par un `npm audit` occasionnel et des bumps réguliers (npm bloque désormais les scripts d'install par défaut, cf. TWiR #284-287).

---

## 3. Ce qui NE s'applique PAS à Outsiders (par honnêteté)

| Sujet (pertinent ailleurs) | Pourquoi pas ici |
|---|---|
| **DuckDB-WASM** (filtrage local) | Outsiders lit des **JSON statiques** servis directement, **pas d'API lente** à court-circuiter. Le moteur DuckDB pèse ~35 Mo : injustifiable sans backend lent ni gros volumes filtrés. À reconsidérer seulement si une analyse croisée sur de gros datasets devient un goulot. |
| **Sortie de CRA / migration Vite** | Déjà sur Vite 7. |
| **cnfast (clsx + tailwind-merge)** | Aucun usage de `clsx`/`tailwind-merge` (className en chaînes simples + objets `style`). |
| **MUI v5/v7, DSFR** | Outsiders est sur Tailwind, pas concerné par les arbitrages MUI/DSFR de mip. |
| **TypeScript 7** | Code en `.jsx` (pas de TS) ; non bloquant, éventuelle migration future si souhaité. |

---

## 4. Récapitulatif priorité / effort / gain

| Action | Effort | Gain | Priorité |
|--------|--------|------|----------|
| **React Compiler** (React 19 + Vite) | Faible | Re-renders ↓ + code simplifié | **Haute** |
| **Document metadata par page** (partage/SEO) | Faible | Aperçus de lien corrects | **Haute** |
| `use()` + Suspense pour le data fetching | Moyen | Code plus simple | Moyenne |
| Vite 7 → 8 | Faible | Builds/HMR plus rapides | Moyenne |
| React Router 7 → 8 | Faible | Rester à jour | Basse |
| a11y des graphes (si public) | Moyen | Conformité | Selon contexte |

**En une phrase** : Outsiders n'a pas de dette de stack ; les deux quick wins à fort effet de levier sont le **React Compiler** (la stack est faite pour) et les **metadata de document React 19** (essentiel pour un site fait pour être partagé).

---

## 5. Sources

- This Week in React #283-287, React Compiler (Rust, intégration Vite/Bun), Vite 8.1, React Router 8.0, React 19.2 (`useEffectEvent`, Activity), supply chain npm.
- Paysage dataviz 2026 (recharts/nivo/visx/ECharts), MapLibre/deck.gl, voir aussi `mip-project/docs/POC_DUCKDB_WASM_TERRITOIRE.md` pour le détail du raisonnement DuckDB.
