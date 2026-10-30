import { Link } from 'react-router-dom'
import { ArrowRight, Layers, Hammer } from 'lucide-react'
import { THEMES } from '../../config/themes'
import { useRouteMeta } from '../../lib/meta'

// Section volontairement hors navigation tant qu'un seul terrain (les élus)
// est mesuré : remettre les liens (Header, Footer, Home) quand les metrics
// des autres terrains seront renseignées dans config/terrains.js.
export default function ThemesList() {
  useRouteMeta('/themes')
  return (
    <div className="py-12 px-4">
      <div className="max-w-5xl mx-auto">
        <div className="flex items-start gap-3 bg-amber-50 border border-amber-200 rounded-xl p-4 mb-8 text-sm text-amber-900">
          <Hammer size={18} className="text-amber-600 shrink-0 mt-0.5" />
          <span>
            Section en construction : un seul terrain (les élus) est mesuré pour l'instant. La
            comparaison prendra son sens quand l'école, le sport et les entreprises seront chiffrés.
          </span>
        </div>
        <header className="mb-10">
          <div className="flex items-center gap-2 text-violet-600 mb-2">
            <Layers size={20} />
            <span className="text-sm font-semibold uppercase tracking-wide">Thèmes</span>
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-3">Les dimensions d'inégalité</h1>
          <p className="text-xl text-gray-600">
            L'inverse des terrains : un seul angle, comparé à travers tous les terrains. Où la
            diversité, la parité ou la jeunesse progressent-elles, et où reculent-elles ?
          </p>
        </header>

        <div className="grid sm:grid-cols-3 gap-6">
          {THEMES.map((t) => {
            const Icon = t.icon
            return (
              <Link
                key={t.id}
                to={`/themes/${t.id}`}
                className="group bg-white rounded-xl border border-gray-200 p-6 shadow-sm hover:shadow-md hover:border-gray-300 transition-all"
              >
                <div className="p-2.5 rounded-lg inline-flex mb-3" style={{ backgroundColor: t.color + '20' }}>
                  <Icon size={22} style={{ color: t.color }} />
                </div>
                <h2 className="font-semibold text-gray-900 group-hover:text-violet-700 transition-colors">
                  {t.titre}
                </h2>
                <p className="text-sm text-gray-600 mt-1 mb-4">{t.description}</p>
                <span className="inline-flex items-center gap-1.5 text-sm font-medium text-violet-600">
                  Comparer les terrains
                  <ArrowRight size={16} className="group-hover:translate-x-0.5 transition-transform" />
                </span>
              </Link>
            )
          })}
        </div>
      </div>
    </div>
  )
}
