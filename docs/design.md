# Outsiders - Design Guidelines

**Projet** : Outsiders - Les angles morts des données publiques  
**Style** : Inspiré DSFR mais distinct, sobre, moderne, professionnel  
**Stack** : React + Tailwind CSS + Lucide Icons

---

## Principes de design

### Vision générale
- **Sobre et épuré** : privilégier l'espace blanc et la clarté
- **Professionnel** : crédibilité institutionnelle sans être bureaucratique
- **Lisible** : optimisé pour la lecture longue (analyses détaillées)
- **Accessible** : contrastes forts, structure claire, navigation simple
- **Moderne** : design actuel sans effets superflus

### Inspiration
- DSFR (Design System de l'État français) pour la sobriété et l'accessibilité
- Observable (observablehq.com) pour les visualisations de données
- Sites académiques/think tanks pour la crédibilité intellectuelle

---

## Palette de couleurs

### Couleurs principales

```css
/* Fond et texte */
--bg-primary: #FFFFFF;        /* Blanc pur */
--bg-secondary: #F6F6F6;      /* Gris très clair pour sections alternées */
--bg-card: #FFFFFF;           /* Blanc pour cards */

--text-primary: #161616;      /* Presque noir, excellent contraste */
--text-secondary: #666666;    /* Gris moyen pour textes secondaires */
--text-tertiary: #999999;     /* Gris clair pour métadonnées */

/* Accents */
--accent-primary: #0063CB;    /* Bleu professionnel (distinct du DSFR) */
--accent-secondary: #E1000F;  /* Rouge pour highlights importants */
--accent-hover: #0052A8;      /* Bleu foncé au survol */

/* Bordures et séparateurs */
--border-light: #DDDDDD;      /* Gris clair */
--border-medium: #CCCCCC;     /* Gris moyen */

/* États */
--success: #18753C;           /* Vert foncé */
--warning: #FF8D00;           /* Orange */
--error: #CE0500;             /* Rouge */
```

### Utilisation des couleurs

**Bleu (#0063CB)** : 
- Liens
- Boutons principaux
- Icônes d'actions
- Éléments interactifs

**Rouge (#E1000F)** :
- Highlights dans les citations
- Données importantes à retenir
- Appels à l'action secondaires
- Utiliser avec parcimonie

**Gris** :
- Texte secondaire (dates, sources, métadonnées)
- Bordures
- Fonds alternatifs

---

## Typographie

### Police de caractères

**Recommandation** : **Inter** (Google Fonts)
- Excellente lisibilité web
- Large gamme de graisses (100-900)
- Gratuite et open source
- Chiffres tabulaires disponibles (parfait pour les données)

**Alternative** : Plus Jakarta Sans (si Inter trop commune)

**Police de code** : JetBrains Mono (si besoin d'afficher du code)

### Hiérarchie typographique

```css
/* Titres */
h1: 2.5rem (40px), font-weight: 700, line-height: 1.2
h2: 2rem (32px), font-weight: 600, line-height: 1.3
h3: 1.5rem (24px), font-weight: 600, line-height: 1.4
h4: 1.25rem (20px), font-weight: 600, line-height: 1.4

/* Corps de texte */
body: 1rem (16px), font-weight: 400, line-height: 1.6
large: 1.125rem (18px), font-weight: 400, line-height: 1.6
small: 0.875rem (14px), font-weight: 400, line-height: 1.5

/* Métadonnées */
caption: 0.875rem (14px), font-weight: 400, line-height: 1.4
```

### Règles de lisibilité

- **Max-width pour le texte** : 720px (65-75 caractères par ligne)
- **Line-height** : 1.6-1.7 pour le corps de texte
- **Espacement paragraphes** : 1.5em minimum
- **Espacement titres** : 2em avant, 0.5em après

---

## Icônes

### Librairie : Lucide React

**Installation** :
```bash
npm install lucide-react
```

**Pourquoi Lucide** :
- Style cohérent (outline, moderne)
- Légère et performante
- Large collection (1000+ icônes)
- Excellente intégration React

### Icônes principales du projet

```jsx
import { 
  // Navigation
  FileText,        // Analyses
  Info,           // À propos
  BookOpen,       // Méthodologie
  Users,          // Journalistes
  
  // Analyses et visualisations
  BarChart3,      // Graphiques statistiques
  TrendingUp,     // Évolutions, tendances
  PieChart,       // Distributions
  Target,         // Focus, précision
  Eye,            // Révéler, angles morts
  Search,         // Recherche, investigation
  
  // Profils sociaux
  Users,          // Groupes sociaux
  GraduationCap,  // Diplômes
  Briefcase,      // CSP, travail
  Calendar,       // Âge, génération
  
  // Actions
  Download,       // Télécharger
  ExternalLink,   // Liens externes
  ArrowRight,     // Navigation
  ChevronDown,    // Dérouler
  Filter,         // Filtrer
  
  // Contact et partage
  Mail,           // Contact
  Github,         // Code source
  Linkedin,       // Réseau professionnel
  Twitter,        // Partage
} from 'lucide-react'
```

### Utilisation des icônes

**Tailles** :
- Navigation : 20-24px
- Cards : 32-40px
- Inline text : 16-18px
- Boutons : 18-20px

**Couleurs** :
- Par défaut : couleur du texte parent
- Actions : bleu accent (#0063CB)
- Important : rouge (#E1000F)

**Exemple** :
```jsx
<BarChart3 size={32} className="text-blue-600" />
```

---

## Composants principaux

### 1. Header / Navigation

**Structure** :
```
Logo + Tagline (gauche) | Navigation (droite)
```

**Caractéristiques** :
- Fond blanc
- Bordure inférieure fine
- Sticky au scroll
- Logo texte simple (pas d'image)
- Navigation horizontale avec icônes

**Code exemple** :
```jsx
<header className="sticky top-0 z-50 bg-white border-b border-gray-200">
  <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div className="flex justify-between items-center py-4">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">
          OUTSIDERS
        </h1>
        <p className="text-sm text-gray-600">
          Les angles morts des données publiques
        </p>
      </div>
      <nav className="flex gap-6">
        <a href="/analyses" className="flex items-center gap-2 text-gray-700 hover:text-blue-600 transition-colors">
          <FileText size={20} />
          <span className="font-medium">Analyses</span>
        </a>
        <a href="/methodologie" className="flex items-center gap-2 text-gray-700 hover:text-blue-600 transition-colors">
          <BookOpen size={20} />
          <span className="font-medium">Méthodologie</span>
        </a>
        <a href="/about" className="flex items-center gap-2 text-gray-700 hover:text-blue-600 transition-colors">
          <Info size={20} />
          <span className="font-medium">À propos</span>
        </a>
      </nav>
    </div>
  </div>
</header>
```

### 2. Hero Section (Homepage)

**Caractéristiques** :
- Grande typographie
- Espace généreux (padding vertical important)
- Fond blanc ou gris très clair
- Message clair et direct

**Code exemple** :
```jsx
<section className="bg-gray-50 py-20">
  <div className="max-w-4xl mx-auto px-4 text-center">
    <Eye className="mx-auto mb-6 text-blue-600" size={48} />
    <h1 className="text-5xl font-bold text-gray-900 mb-6">
      Les angles morts des données publiques
    </h1>
    <p className="text-xl text-gray-600 mb-8 leading-relaxed">
      Analyses sociologiques qui déconstruisent les évidences et révèlent
      les hiérarchies invisibles dans les pratiques sociales.
    </p>
    <a 
      href="/analyses" 
      className="inline-flex items-center gap-2 bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors"
    >
      Découvrir les analyses
      <ArrowRight size={20} />
    </a>
  </div>
</section>
```

### 3. Cards (Liste d'analyses)

**Caractéristiques** :
- Fond blanc
- Bordure fine
- Ombre légère au survol
- Icône catégorie
- Métadonnées (date, thème)
- Transition douce

**Code exemple** :
```jsx
<div className="grid md:grid-cols-2 gap-6 max-w-6xl mx-auto px-4 py-12">
  <article className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-all hover:-translate-y-1">
    <BarChart3 className="text-blue-600 mb-4" size={32} />
    
    <div className="flex items-center gap-2 text-sm text-gray-500 mb-3">
      <Calendar size={16} />
      <span>Décembre 2024</span>
      <span>•</span>
      <span>Information & médias</span>
    </div>
    
    <h3 className="text-xl font-semibold text-gray-900 mb-3">
      Les Français et l'information
    </h3>
    
    <p className="text-gray-600 mb-4">
      Dans quelle France informationnelle vivez-vous ? Analyse des 
      pratiques de consommation d'information et des légitimités plurielles.
    </p>
    
    <a 
      href="/analyses/francais-information" 
      className="inline-flex items-center gap-2 text-blue-600 font-medium hover:text-blue-700"
    >
      Lire l'analyse
      <ArrowRight size={16} />
    </a>
  </article>
</div>
```

### 4. Sections de contenu (Page analyse)

**Caractéristiques** :
- Max-width 720px pour lisibilité optimale
- Padding généreux
- Hiérarchie claire des titres
- Citations en retrait avec bordure gauche
- Listes à puces espacées

**Code exemple** :
```jsx
<article className="max-w-3xl mx-auto px-4 py-12">
  <header className="mb-12">
    <div className="flex items-center gap-2 text-sm text-gray-500 mb-4">
      <Calendar size={16} />
      <span>6 décembre 2024</span>
      <span>•</span>
      <span>12 min de lecture</span>
    </div>
    
    <h1 className="text-4xl font-bold text-gray-900 mb-4">
      Dans quelle France informationnelle vivez-vous ?
    </h1>
    
    <p className="text-xl text-gray-600 leading-relaxed">
      Analyse des pratiques de consommation d'information en France
      et des systèmes de légitimité concurrents.
    </p>
  </header>
  
  <div className="prose prose-lg max-w-none">
    <h2>L'accroche</h2>
    <p>Contenu de l'analyse...</p>
    
    <blockquote className="border-l-4 border-blue-600 pl-6 italic text-gray-700">
      Citation ou élément important mis en avant
    </blockquote>
    
    <h2>Les incontournables</h2>
    <p>Suite de l'analyse...</p>
  </div>
</article>
```

### 5. Visualisations de données

**Caractéristiques** :
- Fond blanc ou gris très clair
- Palette cohérente (2-3 couleurs max)
- Titre clair au-dessus
- Source/méthodologie en petit en dessous
- Responsive (adapté mobile)

**Wrapper de visualisation** :
```jsx
<figure className="my-12 bg-gray-50 rounded-lg p-6">
  <figcaption className="text-lg font-semibold text-gray-900 mb-6">
    Sources d'information par CSP
  </figcaption>
  
  <div className="bg-white rounded p-4">
    {/* Recharts/D3/Plotly chart ici */}
  </div>
  
  <figcaption className="mt-4 text-sm text-gray-500">
    Source : "Les Français et l'information 2024", data.gouv.fr
  </figcaption>
</figure>
```

### 6. Footer

**Caractéristiques** :
- Fond gris clair
- Liens organisés par colonnes
- Contact visible
- Licences et mentions légales

**Code exemple** :
```jsx
<footer className="bg-gray-100 border-t border-gray-200 mt-20">
  <div className="max-w-7xl mx-auto px-4 py-12">
    <div className="grid md:grid-cols-3 gap-8">
      <div>
        <h3 className="font-bold text-gray-900 mb-4">Outsiders</h3>
        <p className="text-gray-600 text-sm">
          Analyses sociologiques de données publiques françaises
        </p>
      </div>
      
      <div>
        <h4 className="font-semibold text-gray-900 mb-4">Navigation</h4>
        <ul className="space-y-2 text-sm">
          <li><a href="/analyses" className="text-gray-600 hover:text-blue-600">Analyses</a></li>
          <li><a href="/methodologie" className="text-gray-600 hover:text-blue-600">Méthodologie</a></li>
          <li><a href="/about" className="text-gray-600 hover:text-blue-600">À propos</a></li>
        </ul>
      </div>
      
      <div>
        <h4 className="font-semibold text-gray-900 mb-4">Contact</h4>
        <p className="text-sm text-gray-600 mb-2">
          <Mail size={16} className="inline mr-2" />
          dataoutsiders@gmail.com
        </p>
        <div className="flex gap-4 mt-4">
          <a href="https://github.com/..." className="text-gray-600 hover:text-blue-600">
            <Github size={20} />
          </a>
          <a href="https://linkedin.com/..." className="text-gray-600 hover:text-blue-600">
            <Linkedin size={20} />
          </a>
        </div>
      </div>
    </div>
    
    <div className="border-t border-gray-200 mt-8 pt-8 text-sm text-gray-500 text-center">
      <p>© 2024 Outsiders. Contenu sous licence CC BY 4.0</p>
    </div>
  </div>
</footer>
```

---

## Boutons et éléments interactifs

### Boutons primaires

```jsx
<button className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 active:bg-blue-800 transition-colors">
  Action principale
</button>
```

### Boutons secondaires

```jsx
<button className="bg-white text-gray-700 border border-gray-300 px-6 py-3 rounded-lg font-medium hover:bg-gray-50 transition-colors">
  Action secondaire
</button>
```

### Liens texte

```jsx
<a href="#" className="text-blue-600 hover:text-blue-700 underline underline-offset-4">
  Lien dans le texte
</a>
```

### États des éléments interactifs

- **Hover** : changement de couleur subtil + légère élévation pour cards
- **Active** : couleur plus foncée
- **Focus** : outline bleu pour l'accessibilité
- **Disabled** : opacité réduite (0.5) + curseur "not-allowed"

---

## Layout et espacement

### Container principal

```jsx
<div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
  {/* Contenu */}
</div>
```

### Grid système

**2 colonnes** :
```jsx
<div className="grid md:grid-cols-2 gap-6">
  {/* Cards ou contenu */}
</div>
```

**3 colonnes** :
```jsx
<div className="grid md:grid-cols-3 gap-6">
  {/* Éléments */}
</div>
```

### Espacements standards

```css
/* Padding sections */
py-12 (3rem / 48px)  /* Standard */
py-16 (4rem / 64px)  /* Généreux */
py-20 (5rem / 80px)  /* Hero sections */

/* Margin entre sections */
mb-8  (2rem / 32px)  /* Petit */
mb-12 (3rem / 48px)  /* Standard */
mb-16 (4rem / 64px)  /* Large */

/* Gaps dans grids */
gap-4 (1rem / 16px)  /* Serré */
gap-6 (1.5rem / 24px) /* Standard */
gap-8 (2rem / 32px)  /* Large */
```

---

## Responsive Design

### Breakpoints Tailwind (par défaut)

```css
sm: 640px   /* Mobile landscape */
md: 768px   /* Tablet */
lg: 1024px  /* Desktop */
xl: 1280px  /* Large desktop */
```

### Stratégie mobile-first

**Navigation** :
- Mobile : menu hamburger
- Desktop : navigation horizontale

**Grid** :
- Mobile : 1 colonne
- Tablet : 2 colonnes
- Desktop : 2-3 colonnes

**Typographie** :
- Mobile : titres légèrement réduits
- Desktop : tailles pleines

**Exemple** :
```jsx
<h1 className="text-3xl md:text-4xl lg:text-5xl font-bold">
  Titre responsive
</h1>
```

---

## Accessibilité

### Contrastes

Tous les contrastes doivent respecter WCAG AA minimum :
- Texte normal : ratio 4.5:1 minimum
- Texte large (18px+) : ratio 3:1 minimum
- Éléments interactifs : ratio 3:1 minimum

### Navigation au clavier

- Tous les éléments interactifs doivent être accessibles au Tab
- Focus visible (outline)
- Skip links pour navigation rapide

### Textes alternatifs

- Images : toujours un alt descriptif
- Icônes décoratives : aria-hidden="true"
- Icônes informatives : aria-label

### Structure sémantique

```jsx
<header>...</header>
<nav>...</nav>
<main>
  <article>
    <h1>...</h1>
    <section>...</section>
  </article>
</main>
<footer>...</footer>
```

---

## Animations et transitions

### Principes

- **Subtiles** : pas d'animations flashy
- **Rapides** : 150-300ms maximum
- **Naturelles** : ease-in-out ou ease-out
- **Fonctionnelles** : guider l'utilisateur, pas décorer

### Transitions recommandées

```jsx
/* Hover sur cards */
transition-all duration-300 ease-in-out
hover:shadow-lg hover:-translate-y-1

/* Hover sur liens */
transition-colors duration-200

/* Apparition d'éléments */
opacity-0 animate-fade-in

/* Boutons */
active:scale-95 transition-transform
```

---

## Visualisations de données

### Palette pour graphiques

**Primaire** (pour 1-3 catégories) :
```css
#0063CB  /* Bleu */
#E1000F  /* Rouge */
#18753C  /* Vert */
```

**Étendue** (pour 4+ catégories) :
```css
#0063CB  /* Bleu */
#00A3A3  /* Cyan */
#18753C  /* Vert */
#FF8D00  /* Orange */
#E1000F  /* Rouge */
#6E1E78  /* Violet */
```

**Dégradés** (pour heatmaps) :
```css
Blanc → Bleu clair → Bleu foncé
#FFFFFF → #A8DAFF → #0063CB → #003D7A
```

### Bonnes pratiques

1. **Maximum 5-6 couleurs** par graphique
2. **Légendes claires** avec labels explicites
3. **Axes** : toujours labellisés avec unités
4. **Grilles** : légères, gris clair (#EEEEEE)
5. **Tooltips** : afficher détails au survol
6. **Responsive** : adapter taille et layout

### Exemple Recharts

```jsx
<ResponsiveContainer width="100%" height={400}>
  <BarChart data={data}>
    <CartesianGrid strokeDasharray="3 3" stroke="#EEEEEE" />
    <XAxis dataKey="name" stroke="#666666" />
    <YAxis stroke="#666666" />
    <Tooltip 
      contentStyle={{ 
        backgroundColor: '#FFFFFF', 
        border: '1px solid #DDDDDD',
        borderRadius: '8px' 
      }} 
    />
    <Legend />
    <Bar dataKey="valeur" fill="#0063CB" />
  </BarChart>
</ResponsiveContainer>
```

---

## Performance et optimisation

### Images

- Format WebP en priorité (fallback JPG/PNG)
- Lazy loading pour images below the fold
- Tailles adaptées (pas d'images surdimensionnées)

### Code

- Code splitting par route
- Lazy loading des composants lourds (charts)
- Minification et tree shaking (Vite le fait automatiquement)

### Fonts

- Sous-ensemble de caractères si possible
- font-display: swap pour éviter FOIT
- Préchargement de la police principale

---

## Checklist design

### Avant le développement
- [ ] Palette de couleurs définie
- [ ] Typographie choisie (Inter)
- [ ] Lucide React installé
- [ ] Composants principaux listés
- [ ] Structure des pages définie

### Pendant le développement
- [ ] Contrastes vérifiés (WCAG AA)
- [ ] Navigation au clavier testée
- [ ] Responsive sur 3+ tailles d'écran
- [ ] Transitions douces et subtiles
- [ ] Code sémantique (HTML5)

### Avant la mise en ligne
- [ ] Test sur vrais contenus
- [ ] Performance vérifiée (Lighthouse)
- [ ] Accessibilité validée
- [ ] Cross-browser testé
- [ ] Mobile testé sur vrais devices

---

## Ressources et inspiration

### Design systems à consulter
- **DSFR** : https://gouvfr.atlassian.net/wiki/spaces/DB/overview (pour inspiration uniquement)
- **Tailwind UI** : exemples de composants
- **shadcn/ui** : composants accessibles

### Outils
- **Tailwind CSS** : https://tailwindcss.com/docs
- **Lucide Icons** : https://lucide.dev
- **Recharts** : https://recharts.org
- **Figma** : pour mockups (optionnel)

### Couleurs et accessibilité
- **WebAIM Contrast Checker** : https://webaim.org/resources/contrastchecker/
- **Coolors** : générateur de palettes

### Typographie
- **Google Fonts** : https://fonts.google.com
- **Inter** : https://rsms.me/inter/

---

## Notes finales

Ce guide est un point de départ. L'essentiel est de :

1. **Rester cohérent** : utiliser les mêmes espacements, couleurs, transitions partout
2. **Privilégier la lisibilité** : les analyses sont longues, le confort de lecture est prioritaire
3. **Être sobre** : le contenu (analyses) doit primer sur le design
4. **Tester régulièrement** : sur différents écrans et navigateurs

Le design doit servir le contenu, pas l'inverse. L'objectif est que les lecteurs se concentrent sur tes analyses sociologiques, pas sur des effets visuels.
