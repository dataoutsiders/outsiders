# Prompt d'amélioration pour Outsiders

## Contexte

Tu travailles sur **Outsiders**, une plateforme d'analyses sociologiques. Le projet est fonctionnel mais nécessite des améliorations de qualité et de maintenabilité.

**Stack technique :**
- Frontend : React + Vite + Tailwind CSS v4
- Backend : Python (scripts de génération de JSON)
- Données : JSON statiques dans `frontend/public/data/`

**Répertoires :**
- React : `%USERPROFILE%\Documents\VsCode\Outsiders\frontend\`
- Python : `%USERPROFILE%\Documents\VsCode\Outsiders\python\`

---

## Améliorations à réaliser

### 1. Gestion des erreurs React

**Problème** : Si un JSON est malformé ou manquant, l'application crash sans message clair.

**Solution** : 
- Intégrer le composant `ErrorBoundary.jsx` (déjà créé dans `src/components/`)
- Wrapper chaque section dans un ErrorBoundary
- Ajouter des messages d'erreur lisibles

**Fichier à modifier** : `src/pages/enquetes/EnqueteChapter.jsx`

```jsx
// Importer
import ErrorBoundary from '../../components/ErrorBoundary'

// Dans renderSection(), wrapper chaque composant :
return (
  <ErrorBoundary 
    key={sectionId}
    errorMessage={`Erreur lors du chargement de "${sectionId}"`}
  >
    <ChapterSection data={data} />
  </ErrorBoundary>
)
```

---

### 2. Améliorer l'accessibilité des visualisations

**Problème** : Les cartes profils utilisent uniquement la couleur pour différencier les catégories (pas accessible pour daltoniens).

**Solution** : Ajouter des patterns ou des icônes distinctives.

**Fichiers à modifier** :
- `src/components/visualizations/ProfilsTypes.jsx`
- `src/components/visualizations/EffectCardsParVariable.jsx`

**Exemple pour ProfilsTypes.jsx** :
```jsx
// Ajouter un indicateur textuel ou une icône en plus de la couleur
<div className="flex items-center gap-2">
  <span 
    className="w-3 h-3 rounded-full" 
    style={{ backgroundColor: profil.couleur }}
    aria-hidden="true"
  />
  <span className="sr-only">{profil.categorie}</span>
  {profil.categorie === 'numerique' && <span>📱</span>}
  {profil.categorie === 'traditionnel' && <span>📺</span>}
  {profil.categorie === 'mixte' && <span>⚖️</span>}
</div>
```

---

### 3. Lazy loading des sections

**Problème** : Toutes les sections sont chargées en même temps, même celles non visibles.

**Solution** : Utiliser `IntersectionObserver` pour charger les sections au scroll.

**Créer** : `src/hooks/useLazyLoad.js`

```jsx
import { useState, useEffect, useRef } from 'react'

export function useLazyLoad(options = {}) {
  const [isVisible, setIsVisible] = useState(false)
  const ref = useRef(null)

  useEffect(() => {
    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) {
        setIsVisible(true)
        observer.disconnect()
      }
    }, { rootMargin: '100px', ...options })

    if (ref.current) {
      observer.observe(ref.current)
    }

    return () => observer.disconnect()
  }, [])

  return [ref, isVisible]
}
```

**Utilisation dans EnqueteChapter.jsx** :
```jsx
function LazySection({ sectionId, renderFn }) {
  const [ref, isVisible] = useLazyLoad()
  
  return (
    <div ref={ref} id={sectionId} className="scroll-mt-24 min-h-[200px]">
      {isVisible ? renderFn() : <SectionSkeleton />}
    </div>
  )
}
```

---

### 4. Améliorer le système de configuration des chapitres

**Problème** : L'ordre des sections est codé en dur dans `EnqueteChapter.jsx` (`CHAPTER_SECTIONS`).

**Solution** : Utiliser le fichier `config/chapters.js` (déjà créé) et l'intégrer.

**Fichier à modifier** : `src/pages/enquetes/EnqueteChapter.jsx`

```jsx
import { getChapterConfig } from '../../config/chapters'

// Dans le composant :
const chapterConfig = getChapterConfig(enqueteId, chapitreId)
const sectionIds = chapterConfig?.sections?.map(s => s.id) || CHAPTER_SECTIONS[chapitreId] || []
```

---

### 5. Ajouter des indicateurs de chargement plus élégants

**Problème** : Le skeleton de chargement est basique.

**Solution** : Créer un composant `ChapterSkeleton` plus réaliste.

**Créer** : `src/components/chapter/ChapterSkeleton.jsx`

```jsx
function ChapterSkeleton() {
  return (
    <div className="animate-pulse space-y-8 py-8">
      {/* Header */}
      <div className="space-y-3">
        <div className="h-8 bg-gray-200 rounded-lg w-2/3" />
        <div className="h-4 bg-gray-200 rounded w-1/2" />
      </div>
      
      {/* Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[1, 2, 3].map(i => (
          <div key={i} className="h-32 bg-gray-100 rounded-xl" />
        ))}
      </div>
      
      {/* Content */}
      <div className="space-y-4">
        <div className="h-4 bg-gray-200 rounded w-full" />
        <div className="h-4 bg-gray-200 rounded w-5/6" />
        <div className="h-4 bg-gray-200 rounded w-4/6" />
      </div>
      
      {/* Chart placeholder */}
      <div className="h-64 bg-gray-100 rounded-xl" />
    </div>
  )
}

export default ChapterSkeleton
```

---

### 6. Ajouter la gestion du dark mode

**Problème** : Pas de mode sombre.

**Solution** : Utiliser les classes Tailwind `dark:` et un toggle.

**Étapes** :
1. Modifier `tailwind.config.js` : `darkMode: 'class'`
2. Créer un hook `useTheme.js`
3. Ajouter un toggle dans le Header
4. Ajouter les variantes `dark:` aux composants principaux

**Créer** : `src/hooks/useTheme.js`

```jsx
import { useState, useEffect } from 'react'

export function useTheme() {
  const [theme, setTheme] = useState(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('theme') || 'light'
    }
    return 'light'
  })

  useEffect(() => {
    const root = document.documentElement
    if (theme === 'dark') {
      root.classList.add('dark')
    } else {
      root.classList.remove('dark')
    }
    localStorage.setItem('theme', theme)
  }, [theme])

  const toggleTheme = () => setTheme(t => t === 'light' ? 'dark' : 'light')

  return { theme, toggleTheme }
}
```

---

### 7. Optimiser le hook useChapterData

**Fichier** : `src/hooks/useChapterData.js` (déjà créé)

**Amélioration** : Ajouter du cache pour éviter de recharger les mêmes données.

```jsx
// Ajouter un cache simple en mémoire
const cache = new Map()

export function useChapterData(enqueteId, chapitreId, sectionIds = []) {
  const cacheKey = `${enqueteId}/${chapitreId}`
  
  // Vérifier le cache avant de fetch
  useEffect(() => {
    if (cache.has(cacheKey)) {
      const cached = cache.get(cacheKey)
      setIndex(cached.index)
      setSections(cached.sections)
      setLoading(false)
      return
    }
    // ... reste du code de fetch
    // À la fin, mettre en cache :
    cache.set(cacheKey, { index: indexData, sections: loadedSections })
  }, [...])
}
```

---

### 8. Ajouter des tests

**Créer la structure de tests** :

```
frontend/
├── src/
│   └── __tests__/
│       ├── components/
│       │   └── ErrorBoundary.test.jsx
│       └── hooks/
│           └── useChapterData.test.js
├── vitest.config.js
```

**Installer Vitest** :
```bash
npm install -D vitest @testing-library/react @testing-library/jest-dom jsdom
```

**Exemple de test** (`ErrorBoundary.test.jsx`) :
```jsx
import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import ErrorBoundary from '../../components/ErrorBoundary'

const ThrowError = () => { throw new Error('Test error') }

describe('ErrorBoundary', () => {
  it('affiche le fallback en cas d\'erreur', () => {
    render(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>
    )
    expect(screen.getByText(/quelque chose s'est mal passé/i)).toBeInTheDocument()
  })
})
```

---

## Ordre de priorité suggéré

1. **Gestion des erreurs** (impact utilisateur immédiat)
2. **Skeleton de chargement** (UX)
3. **Configuration chapitres** (maintenabilité)
4. **Lazy loading** (performance)
5. **Accessibilité** (inclusivité)
6. **Dark mode** (confort)
7. **Cache** (performance)
8. **Tests** (qualité long terme)

---

## Commandes

```bash
cd %USERPROFILE%\Documents\VsCode\Outsiders\frontend

# Développement
npm run dev

# Build
npm run build

# Tests (après installation de Vitest)
npm test
```

---

## Notes importantes

- Ne pas casser le code existant qui fonctionne
- Tester chaque modification avant de passer à la suivante
- Les fichiers `ErrorBoundary.jsx`, `chapters.js`, `useChapterData.js` existent déjà mais ne sont pas intégrés
- Garder le style Tailwind cohérent avec l'existant
