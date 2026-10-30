import { useEffect, useMemo, useRef, useState } from 'react'
import { Search, Building2, MapPin, Loader2, Layers, Map as MapIcon } from 'lucide-react'
import { titleCase } from '../lib/territoire'

/**
 * Recherche d'un territoire (commune, intercommunalité, département ou région) sur l'index national.
 * `onSelect(code, niveau, territoire)` : le niveau ('commune' | 'epci' | 'dept' | 'region') sert à
 * construire l'adresse de la fiche (ficheHref de lib/territoire.js).
 *
 * Deux usages :
 *  - contrôlé : le parent fournit `searchable` (Territoires.jsx, qui a déjà
 *    besoin de l'index brut pour ses libellés) ;
 *  - autonome : sans prop `searchable`, le composant charge l'index à la
 *    première interaction (la home ne paie le 1 Mo que si on s'en sert).
 */

const norm = (s) =>
  String(s || '')
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .toLowerCase()

// Transforme l'index brut (territoires-index.json) en liste cherchable.
export function buildSearchable(index) {
  const regions = (index.regions || []).map(([c, n]) => ({ code: c, nom: n, niveau: 'region' }))
  const deps = index.deps.map(([c, n]) => ({ code: c, nom: titleCase(n), niveau: 'dept' }))
  const coms = index.communes.map(([c, n, dep]) => ({ code: c, nom: n, dep, niveau: 'commune' }))
  const epci = (index.epci || []).map(([c, n, dep]) => ({ code: c, nom: n, dep, niveau: 'epci' }))
  return [...regions, ...deps, ...coms, ...epci].map((t) => ({ ...t, key: norm(t.nom) }))
}

const ICONE = { commune: Building2, epci: Layers, dept: MapPin, region: MapIcon }
function sousTitre(t) {
  if (t.niveau === 'commune') return `dépt ${t.dep}`
  if (t.niveau === 'epci') return t.dep ? `intercommunalité · dépt ${t.dep}` : 'intercommunalité'
  if (t.niveau === 'region') return 'région'
  return 'département'
}

// Cache module : l'index n'est téléchargé qu'une fois par session.
let indexPromise = null
function loadSearchable() {
  if (!indexPromise) {
    indexPromise = fetch('/data/atlas/territoires-index.json')
      .then((r) => r.json())
      .then(buildSearchable)
      .catch(() => {
        indexPromise = null // on repermettra un essai plus tard
        return []
      })
  }
  return indexPromise
}

export default function TerritoireSearch({
  searchable: searchableProp,
  onSelect,
  autoFocus = false,
  placeholder = 'Cherchez une commune, une intercommunalité, un département ou une région…',
}) {
  const lazy = searchableProp === undefined
  const [own, setOwn] = useState(null)
  const searchable = lazy ? own : searchableProp
  const [q, setQ] = useState('')
  const [open, setOpen] = useState(false)
  const boxRef = useRef(null)

  const ensureIndex = () => {
    if (lazy && !own) loadSearchable().then(setOwn)
  }

  useEffect(() => {
    const onDoc = (e) => { if (boxRef.current && !boxRef.current.contains(e.target)) setOpen(false) }
    document.addEventListener('mousedown', onDoc)
    return () => document.removeEventListener('mousedown', onDoc)
  }, [])

  const results = useMemo(() => {
    if (!searchable || q.trim().length < 1) return []
    const nq = norm(q.trim())
    const starts = [], incl = []
    for (const t of searchable) {
      const i = t.key.indexOf(nq)
      if (i === 0) starts.push(t)
      else if (i > 0) incl.push(t)
    }
    return [...starts, ...incl].slice(0, 10)
  }, [q, searchable])

  return (
    <div ref={boxRef} className="relative" onPointerEnter={ensureIndex}>
      <div className="flex items-center gap-2 bg-white border border-gray-300 rounded-xl px-4 py-3 shadow-sm focus-within:border-blue-400">
        <Search size={20} className="text-gray-400 shrink-0" />
        <input
          autoFocus={autoFocus}
          value={q}
          onChange={(e) => { setQ(e.target.value); setOpen(true) }}
          onFocus={() => { setOpen(true); ensureIndex() }}
          placeholder={lazy || searchable ? placeholder : 'Chargement de l\'index…'}
          disabled={!lazy && !searchable}
          className="flex-1 outline-none text-gray-900 placeholder-gray-400 bg-transparent"
        />
      </div>
      {open && q.trim().length > 0 && !searchable && (
        <div className="absolute z-20 left-0 right-0 mt-2 bg-white border border-gray-200 rounded-xl shadow-lg px-4 py-3 text-sm text-gray-400 flex items-center gap-2">
          <Loader2 className="animate-spin" size={15} /> Chargement de l'index des territoires…
        </div>
      )}
      {open && results.length > 0 && (
        <ul className="absolute z-20 left-0 right-0 mt-2 bg-white border border-gray-200 rounded-xl shadow-lg overflow-hidden">
          {results.map((t) => (
            <li key={`${t.niveau}-${t.code}`}>
              <button
                onClick={() => { onSelect(t.code, t.niveau, t); setQ(''); setOpen(false) }}
                className="w-full flex items-center gap-3 px-4 py-2.5 text-left hover:bg-gray-50"
              >
                {(() => { const Icone = ICONE[t.niveau] || MapPin; return <Icone size={16} className="text-gray-400 shrink-0" /> })()}
                <span className="flex-1 text-gray-900 truncate">{t.nom}</span>
                <span className="text-xs text-gray-400 shrink-0">{sousTitre(t)}</span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
