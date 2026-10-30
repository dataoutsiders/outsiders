import { Link, useLocation } from 'react-router-dom'
import { Home, Zap, Map as MapIcon, MapPin, BookOpen } from 'lucide-react'
import { trackEvent } from '../lib/analytics'

// Barre d'onglets du téléphone, à portée de pouce, comme dans une application.
// Cachée à partir de la tablette (l'en-tête suffit) ; le fil plein écran la recouvre.
const ONGLETS = [
  { to: '/', label: 'Accueil', icon: Home, actif: (p) => p === '/' },
  { to: '/fil', label: 'Le fil', icon: Zap, actif: (p) => p === '/fil' },
  { to: '/atlas', label: 'Carte', icon: MapIcon, actif: (p) => p.startsWith('/atlas') },
  { to: '/territoires', label: 'Territoires', icon: MapPin, actif: (p) => p.startsWith('/territoires') },
  {
    to: '/terrains',
    label: 'Dossiers',
    icon: BookOpen,
    actif: (p) => ['/terrains', '/international', '/segregation', '/themes'].some((d) => p.startsWith(d)),
  },
]

export default function BarreOnglets() {
  const { pathname } = useLocation()
  return (
    <nav
      aria-label="Navigation principale"
      className="sm:hidden fixed bottom-0 left-0 right-0 z-50 bg-white/95 backdrop-blur border-t border-gray-200 pb-[env(safe-area-inset-bottom)]"
    >
      <ul className="flex">
        {ONGLETS.map(({ to, label, icon: Icon, actif }) => {
          const on = actif(pathname)
          return (
            <li key={to} className="flex-1">
              <Link
                to={to}
                onClick={() => trackEvent(`onglet/${label}`, 'Barre d’onglets')}
                aria-current={on ? 'page' : undefined}
                className={`flex flex-col items-center justify-center gap-0.5 h-14 text-[11px] font-medium ${
                  on ? 'text-blue-700' : 'text-gray-500'
                }`}
              >
                <Icon size={21} strokeWidth={on ? 2.4 : 1.9} />
                {label}
              </Link>
            </li>
          )
        })}
      </ul>
    </nav>
  )
}
