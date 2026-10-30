import { useState, useRef, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Wrench, Menu, X, ChevronDown } from 'lucide-react'
import { DECOUPAGES } from '../config/decoupages'

// Navigation rangée par tâche : Outils (ce que la plateforme permet de FAIRE,
// la carte comprise), Dossiers (récits cadrés). Méthodologie / À propos = meta.
//
// La section « Comparer des groupes » se construit à partir des découpages non
// géographiques actifs (config/decoupages.js) ; ceux à venir sont annoncés.
const ACTIFS = DECOUPAGES.filter((d) => d.statut === 'disponible')
const GROUPES_ACTIFS = ACTIFS.filter((d) => !d.aCarte)
const OUTILS_SECTIONS = [
  {
    titre: 'Territoires',
    items: [
      { to: '/atlas', label: 'Carte des outsiders', sub: 'croiser deux indicateurs, repérer les écarts' },
      { to: '/territoires', label: 'Fiche territoire', sub: 'commune, intercommunalité, département ou région' },
    ],
  },
  {
    titre: 'Comparer des groupes, des pays',
    items: GROUPES_ACTIFS.map((d) => ({ to: d.route, label: d.titre, sub: d.sousTitre })),
  },
  {
    titre: 'Vos fichiers',
    items: [
      { to: '/outils/representativite', label: 'Représentativité de noms', sub: 'diversité, parité, âge, dans le navigateur' },
      { to: '/outils', label: 'Tous les outils', sub: null },
    ],
  },
]
const OUTILS_BIENTOT = DECOUPAGES.filter((d) => d.statut === 'a-venir').map((d) => d.titre)
const OUTILS_PATHS = [
  ...new Set([...ACTIFS.flatMap((d) => Object.values(d.modeRoutes || {})), '/outils']),
]

const DOSSIERS_ITEMS = [
  { to: '/international', label: 'France en Europe', sub: 'où se situe la France ? 30 pays comparés' },
  { to: '/international/pisa', label: 'PISA 2025', sub: 'la France décroche-t-elle ?' },
  { to: '/segregation', label: 'Villes', sub: 'riches et pauvres vivent-ils séparés ?' },
  { to: '/terrains/revenus', label: 'Revenus', sub: "qui s'enrichit, qui décroche ?" },
  { to: '/terrains/sport', label: 'Sport', sub: 'le foot, sport des quartiers ?' },
  { to: '/terrains/pratiques', label: 'Modes de vie', sub: 'manger, bouger, fumer : le poids du milieu social' },
  { to: '/terrains/ecole', label: 'École', sub: "l'école trie-t-elle ?" },
  { to: '/terrains/elus', label: 'Élus', sub: 'la diversité, du candidat au maire' },
  { to: '/terrains/assemblee', label: 'Assemblée', sub: 'qui représente qui, groupe par groupe ?' },
  { to: '/terrains/selectivite', label: 'Sélectivité', sub: 'qui peut entrer dans le supérieur ?' },
  { to: '/terrains/auto-ecoles', label: 'Auto-écoles', sub: 'qui forme le mieux, à contexte égal ?' },
  { to: '/terrains', label: 'Tous les terrains', sub: null },
]
const META = [
  { to: '/methodologie', label: 'Méthodologie' },
  { to: '/about', label: 'À propos' },
]

function LinkItem({ to, label, sub, onNavigate }) {
  return (
    <Link to={to} onClick={onNavigate} className="block px-4 py-2 hover:bg-gray-50 transition-colors">
      <div className="text-gray-900 font-medium text-sm">{label}</div>
      {sub && <div className="text-xs text-gray-500">{sub}</div>}
    </Link>
  )
}

function NavMenu({ label, isOpen, onToggle, onNavigate, active, sections, items, bientot }) {
  return (
    <div className="relative">
      <button
        onClick={onToggle}
        aria-expanded={isOpen}
        className={`flex items-center gap-1.5 font-medium transition-colors ${
          active ? 'text-blue-600' : 'text-gray-700 hover:text-blue-600'
        }`}
      >
        {label}
        <ChevronDown size={16} className={`transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>
      {isOpen && (
        <div className="absolute left-0 top-full mt-2 w-64 bg-white border border-gray-200 rounded-xl shadow-lg py-2 z-50">
          {sections
            ? sections.map((s, si) => (
                <div key={si} className={si > 0 ? 'mt-1 pt-1.5 border-t border-gray-100' : ''}>
                  <div className="px-4 pb-1 text-xs font-semibold uppercase tracking-wide text-gray-400">{s.titre}</div>
                  {s.items.map((it, i) => (
                    <LinkItem key={i} {...it} onNavigate={onNavigate} />
                  ))}
                </div>
              ))
            : items.map((it, i) => <LinkItem key={i} {...it} onNavigate={onNavigate} />)}
          {bientot && bientot.length > 0 && (
            <div className="border-t border-gray-100 mt-1.5 pt-2 px-4 text-xs text-gray-400">
              Bientôt : {bientot.join(', ')}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function Header() {
  const location = useLocation()
  const path = location.pathname
  const [openMenu, setOpenMenu] = useState(null) // 'outils' | 'dossiers' | null
  const [mobileOpen, setMobileOpen] = useState(false)
  const navRef = useRef(null)

  const isActive = (p) => path.startsWith(p)
  const close = () => setOpenMenu(null)
  const outilsActive = OUTILS_PATHS.some(isActive)
  const dossiersActive = isActive('/terrains') || isActive('/themes')

  // Fermer les déroulants au clic extérieur ou avec Échap.
  useEffect(() => {
    const onDoc = (e) => {
      if (navRef.current && !navRef.current.contains(e.target)) setOpenMenu(null)
    }
    const onKey = (e) => {
      if (e.key === 'Escape') setOpenMenu(null)
    }
    document.addEventListener('mousedown', onDoc)
    document.addEventListener('keydown', onKey)
    return () => {
      document.removeEventListener('mousedown', onDoc)
      document.removeEventListener('keydown', onKey)
    }
  }, [])

  const linkCls = (p) =>
    `font-medium transition-colors ${isActive(p) ? 'text-blue-600' : 'text-gray-700 hover:text-blue-600'}`

  return (
    <header className="sticky top-0 z-50 bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-3 sm:py-4">
          {/* Logo */}
          <Link to="/" className="group" onClick={() => { close(); setMobileOpen(false) }}>
            <h1 className="text-2xl font-bold text-gray-900 group-hover:text-blue-600 transition-colors">
              OUTSIDERS
            </h1>
            <p className="hidden sm:block text-sm text-gray-600">Comprendre la France par ses angles morts</p>
          </Link>

          {/* Navigation desktop */}
          <nav ref={navRef} className="hidden lg:flex items-center gap-6">
            <NavMenu
              label={<span className="inline-flex items-center gap-1.5"><Wrench size={17} /> Outils</span>}
              isOpen={openMenu === 'outils'}
              onToggle={() => setOpenMenu(openMenu === 'outils' ? null : 'outils')}
              onNavigate={close}
              active={outilsActive}
              sections={OUTILS_SECTIONS}
              bientot={OUTILS_BIENTOT}
            />
            <NavMenu
              label="Dossiers"
              isOpen={openMenu === 'dossiers'}
              onToggle={() => setOpenMenu(openMenu === 'dossiers' ? null : 'dossiers')}
              onNavigate={close}
              active={dossiersActive}
              items={DOSSIERS_ITEMS}
            />
            <span className="w-px h-5 bg-gray-200" />
            {META.map((m) => (
              <Link key={m.to} to={m.to} className={`text-sm ${linkCls(m.to)}`}>
                {m.label}
              </Link>
            ))}
          </nav>

          {/* Bouton menu mobile */}
          <button className="lg:hidden p-2 text-gray-700" onClick={() => setMobileOpen(!mobileOpen)}>
            {mobileOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>

        {/* Menu mobile */}
        {mobileOpen && (
          <nav className="lg:hidden py-4 border-t border-gray-200">
            <div className="space-y-4" onClick={() => setMobileOpen(false)}>
              <div>
                <div className="px-4 text-xs font-semibold uppercase tracking-wide text-gray-400 mb-1">Outils</div>
                {OUTILS_SECTIONS.map((s, si) => (
                  <div key={si} className="mb-1">
                    <div className="px-6 text-[11px] uppercase tracking-wide text-gray-400">{s.titre}</div>
                    {s.items.map((it, i) => (
                      <Link key={i} to={it.to} className="block px-8 py-1.5 text-gray-700 hover:bg-gray-50 rounded-lg">
                        {it.label}
                      </Link>
                    ))}
                  </div>
                ))}
                {OUTILS_BIENTOT.length > 0 && (
                  <div className="px-6 text-xs text-gray-400">Bientôt : {OUTILS_BIENTOT.join(', ')}</div>
                )}
              </div>
              <div>
                <div className="px-4 text-xs font-semibold uppercase tracking-wide text-gray-400 mb-1">Dossiers</div>
                {DOSSIERS_ITEMS.map((it, i) => (
                  <Link key={i} to={it.to} className="block px-6 py-2 text-gray-700 hover:bg-gray-50 rounded-lg">
                    {it.label}
                  </Link>
                ))}
              </div>
              <div className="border-t border-gray-100 pt-3">
                {META.map((m) => (
                  <Link key={m.to} to={m.to} className="block px-4 py-2 text-gray-700 hover:bg-gray-50 rounded-lg">
                    {m.label}
                  </Link>
                ))}
              </div>
            </div>
          </nav>
        )}
      </div>
    </header>
  )
}

export default Header
