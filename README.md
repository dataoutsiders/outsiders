# Outsiders

**Comprendre la France par ses angles morts.**

Explorateur de données publiques françaises, du pays à la commune. Le site ne montre pas seulement le niveau d'un territoire ou d'un groupe : il montre **l'écart à ce que son profil laissait attendre**. Chaque chiffre cite sa source d'origine, tout est consultable sans compte, et le contenu est sous licence CC BY 4.0.

- **En ligne** : https://dataoutsiders.fr/
- **Contact public** : contact@dataoutsiders.fr
- **Présentation complète** (produit, méthodes, sources, pipelines) : [`docs/projet.md`](docs/projet.md)
- **Déploiement et comptes** : [`docs/DEPLOIEMENT.md`](docs/DEPLOIEMENT.md)

Le nom est un clin d'œil à Howard Becker (*Outsiders*, 1963).

---

## Ce que contient le site (30 octobre 2026)

| Entrée | Contenu |
|---|---|
| Accueil | 16 cartes-questions (idée reçue, verdict, chiffre sourcé, lien vers la preuve), vérifiées le 30/10/2026 ; carrousel sur téléphone |
| Le fil (`/fil`) | Les mêmes cartes en plein écran, une par écran, à faire défiler et partager |
| Atlas (`/atlas`) | Carte de France, 20 indicateurs, mailles département, intercommunalité, commune ; croisement de deux indicateurs et « outsiders » (écart à la droite de pronostic) ; code d'intégration |
| Fiches territoire (`/territoires`) | Commune, intercommunalité, département, région : atypies, jumeau statistique, indicateurs situés, rubrique « Dans nos dossiers » |
| Comparer des groupes (`/explorer/...`) | Milieu social, sexe, âge, 30 pays européens |
| Dossiers | France en Europe, PISA 2025, Villes (ségrégation), Revenus 2014-2021, Sport, École, Élus, Assemblée, Sélectivité (Parcoursup), Auto-écoles |
| Outil Représentativité | Diversité des noms, parité, âge d'une liste de noms, calculés dans le navigateur |
| Presse et réutilisation (`/presse`) | Résultats à reprendre avec leur source, formule de citation, code d'intégration, images |
| Newsletter (`/newsletter`) | Inscription (Brevo, sans script tiers sur le site), aussi en bas de l'accueil, sur `/presse` et dans le pied de page |
| Sur téléphone | Barre d'onglets en bas ; site installable comme une application (icône, plein écran) |

---

## Architecture

Pas de serveur en production : des scripts Python téléchargent les données publiques et écrivent des JSON statiques, que le site React lit.

```
Sources publiques (Insee, Éducation nationale, DVF, INJEP, Eurostat, OCDE...)
        ↓   python/tools/build_*.py
JSON pré-calculés  →  frontend/public/data/
        ↓
Site statique (Cloudflare Pages)
```

```
outsiders/
├── frontend/                 React 19, Vite 7, Tailwind 4, Leaflet, recharts, lucide-react
│   ├── src/config/           registres : indicateurs, découpages, seo, dossiersTerritoires
│   ├── src/pages/            accueil, atlas, territoire, explorer, terrains, international, segregation, outils, presse
│   ├── src/lib/              meta (SEO), analytics (GoatCounter), résidus, territoire, jumeau
│   ├── scripts/              post-build : images de partage, pages pré-rendues, plan du site
│   └── public/data/          JSON publiés (ne JAMAIS y laisser de sauvegarde .bak : tout part en ligne)
├── python/tools/             pipelines de données (ordre dans docs/DEPLOIEMENT.md)
├── python/data/              données sources et sorties intermédiaires (non publiées)
├── docs/                     documentation (voir plus bas)
└── _archive/                 sauvegardes datées, hors du dossier publié
```

---

## Installation et commandes

```bash
# Site
cd frontend
npm install
npm run dev          # http://localhost:5173
npx vitest run       # tests (79 au 30/10/2026)
node scripts/generate-icons.mjs   # icônes de l'application (seulement si le dessin change)
npm run deploy       # build + images de partage + pré-rendu + plan du site + publication Cloudflare

# Données (venv à la racine)
.venv\Scripts\python.exe python/tools/<script>.py    # avec PYTHONIOENCODING=utf-8 sous Windows
```

**Sauvegarde** : dépôt Git privé `github.com/dataoutsiders/outsiders`, identité locale « Outsiders » (adresse
anonyme GitHub). Après chaque lot : `git add -A && git commit -m "..." && git push`. Jamais l'identité Git globale
de la machine, jamais la forge professionnelle.

L'ordre des pipelines compte : voir `docs/DEPLOIEMENT.md`, section des données. Piège connu : `build_atlas_epci.py` réécrit `atlas/epci.json` en entier, il faut ensuite relancer les scripts qui y ajoutent leurs indicateurs.

---

## Documentation

| Fichier | Objet |
|---|---|
| `docs/projet.md` | Présentation complète : produit, indicateurs, moteur onomastique, sources, principes, pipelines, suite |
| `docs/DEPLOIEMENT.md` | Comptes, domaine, newsletter (Brevo, DNS), publication, ordre des pipelines |
| `docs/verification_cartes_accueil.md` | Vérification des cartes de l'accueil et corrections du 30/10/2026 |
| `docs/relecture/` | Une fiche par carte (données, liens, toutes les colonnes, pistes) ; sommaire et décisions dans `README.md` |
| `docs/millesimes_20261030.md` | Millésime de chaque source et mises à jour restantes |
| `docs/fiches_territoire_20261030.md` | Fiches à quatre échelles, registre « Dans nos dossiers », valeurs régionales |
| `docs/sport/` | Exploration des licences INJEP, de l'offre et de l'élite |
| `docs/international/` | PISA 2025 : exploration et dossier |
| `docs/promotion/` | Réutilisations à déclarer sur data.gouv.fr |
| `docs/idees/` | Idées en réflexion : presse (Europresse), version payante ; statistiques d'usage et newsletter (faites) |
| `docs/vision-et-sujets.md`, `docs/veille-open-data.md` | Cadrage éditorial, sujets possibles, veille |
| `docs/AJOUTER_UN_DECOUPAGE.md`, `docs/design.md` | Ajouter une unité d'analyse ; charte graphique |

---

## Règles

- Citer la source d'origine de chaque chiffre ; décrire, pas juger ; aucune cause affirmée sans preuve.
- Indice de diversité des noms : indicateur de groupe, jamais une origine ni un résultat individuel ; agrégats seulement.
- Accents obligatoires, pas de tiret cadratin.
- Le projet est anonyme : aucun nom d'auteur dans le site, le code publié ou les métadonnées.

## Licence

Contenus sous licence CC BY 4.0. Données soumises à la licence de leur producteur (le plus souvent la Licence Ouverte d'Etalab).
