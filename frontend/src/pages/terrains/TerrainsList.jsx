import { Link } from 'react-router-dom'
import { ArrowRight, Landmark } from 'lucide-react'
import { TERRAINS } from '../../config/terrains'
import { useRouteMeta } from '../../lib/meta'

const ANGLE_LABEL = {
  diversite: 'Diversité',
  genre: 'Genre',
  age: 'Âge',
  ecole: 'École',
  college: 'Collège',
  lycee: 'Lycée',
}

export default function TerrainsList() {
  useRouteMeta('/terrains')
  return (
    <div className="py-12 px-4">
      <div className="max-w-5xl mx-auto">
        <header className="mb-10">
          <div className="flex items-center gap-2 text-emerald-600 mb-2">
            <Landmark size={20} />
            <span className="text-sm font-semibold uppercase tracking-wide">Terrains</span>
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-3">Les terrains d'enquête</h1>
          <p className="text-xl text-gray-600">
            Une population, analysée sous tous les angles à la fois : diversité, genre, âge.
            Chaque terrain est une étude complète sur données publiques.
          </p>
        </header>

        <div className="grid sm:grid-cols-2 gap-6">
          {TERRAINS.map((t) => {
            const Icon = t.icon
            const dispo = t.statut === 'disponible'
            const inner = (
              <>
                <div className="flex items-center gap-3 mb-3">
                  <div className="p-2.5 rounded-lg" style={{ backgroundColor: t.color + '20' }}>
                    <Icon size={22} style={{ color: t.color }} />
                  </div>
                  <div>
                    <h2 className="font-semibold text-gray-900">{t.titre}</h2>
                    <p className="text-xs text-gray-500">{t.sousTitre}</p>
                  </div>
                </div>
                <p className="text-sm text-gray-600 mb-4">{t.description}</p>
                <div className="flex flex-wrap gap-1.5 mb-4">
                  {t.angles.map((a) => (
                    <span
                      key={a}
                      className="px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-600"
                    >
                      {ANGLE_LABEL[a] || a}
                    </span>
                  ))}
                </div>
                {dispo ? (
                  <span className="inline-flex items-center gap-1.5 text-sm font-medium text-emerald-600">
                    Voir l'étude
                    <ArrowRight size={16} className="group-hover:translate-x-0.5 transition-transform" />
                  </span>
                ) : (
                  <span className="inline-block text-xs font-medium text-gray-400">Bientôt</span>
                )}
              </>
            )
            return dispo ? (
              <Link
                key={t.id}
                to={t.to}
                className="group bg-white rounded-xl border border-gray-200 p-6 shadow-sm hover:shadow-md hover:border-gray-300 transition-all"
              >
                {inner}
              </Link>
            ) : (
              <div key={t.id} className="bg-gray-50 rounded-xl border border-dashed border-gray-200 p-6 opacity-80">
                {inner}
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
