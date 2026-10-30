import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, ArrowRight } from 'lucide-react'
import { THEME_BY_ID } from '../../config/themes'
import { TERRAINS } from '../../config/terrains'
import { useRouteMeta } from '../../lib/meta'

export default function ThemeDetail() {
  const { themeId } = useParams()
  const theme = THEME_BY_ID[themeId]
  useRouteMeta('/themes', theme ? { title: `${theme.titre} : comparaison entre terrains` } : {})

  if (!theme) {
    return (
      <div className="py-12 px-4 max-w-4xl mx-auto text-center">
        <h1 className="text-2xl font-bold text-gray-900 mb-4">Thème introuvable</h1>
        <Link to="/themes" className="inline-flex items-center gap-2 text-violet-600">
          <ArrowLeft size={16} /> Retour aux thèmes
        </Link>
      </div>
    )
  }

  const Icon = theme.icon
  const avecData = TERRAINS.filter((t) => t.metrics?.[themeId] != null)
  const aVenir = TERRAINS.filter((t) => t.angles.includes(themeId) && t.metrics?.[themeId] == null)
  const max = Math.max(theme.id === 'age' ? 80 : 50, ...avecData.map((t) => t.metrics[themeId]))
  const f = (x) => (theme.id === 'age' ? `${x} ans` : `${x.toString().replace('.', ',')} %`)

  return (
    <div className="py-12 px-4">
      <div className="max-w-4xl mx-auto">
        <nav className="mb-6">
          <Link to="/themes" className="inline-flex items-center gap-2 text-gray-600 hover:text-violet-600">
            <ArrowLeft size={16} /> Tous les thèmes
          </Link>
        </nav>

        <header className="mb-10">
          <div className="flex items-start gap-4">
            <div className="p-3 rounded-xl" style={{ backgroundColor: theme.color + '20' }}>
              <Icon size={32} style={{ color: theme.color }} />
            </div>
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-2">{theme.titre}</h1>
              <p className="text-xl text-gray-600">{theme.description}</p>
              <p className="text-sm text-gray-400 mt-1">
                Mesure : {theme.unite} · référence : {theme.reference}
              </p>
            </div>
          </div>
        </header>

        <section className="mb-10">
          <h2 className="text-2xl font-bold text-gray-900 mb-1">Comparaison entre terrains</h2>
          <p className="text-gray-500 mb-6">
            Le même angle, mesuré sur chaque terrain disponible.
          </p>

          {avecData.length > 0 ? (
            <div className="bg-white border border-gray-200 rounded-xl p-6 space-y-4">
              {avecData.map((t) => {
                const v = t.metrics[themeId]
                const w = Math.max(3, (v / max) * 100)
                return (
                  <Link key={t.id} to={t.to} className="block group">
                    <div className="flex items-center justify-between text-sm mb-1">
                      <span className="font-medium text-gray-800 group-hover:text-violet-700">
                        {t.titre} <span className="text-gray-400">· {t.sousTitre}</span>
                      </span>
                      <span className="font-semibold text-gray-900">{f(v)}</span>
                    </div>
                    <div className="h-4 bg-gray-100 rounded-full overflow-hidden">
                      <div
                        className="h-full rounded-full"
                        style={{ width: `${w}%`, backgroundColor: theme.color }}
                      />
                    </div>
                  </Link>
                )
              })}
            </div>
          ) : (
            <p className="text-gray-500 italic">Aucun terrain mesuré sur cet angle pour l'instant.</p>
          )}

          {aVenir.length > 0 && (
            <p className="text-sm text-gray-400 mt-4">
              À venir sur cet angle : {aVenir.map((t) => t.titre).join(', ')}. La comparaison
              s'enrichit à mesure que les terrains s'ajoutent.
            </p>
          )}
        </section>

        <div className="bg-gray-50 border border-gray-200 rounded-xl p-6">
          <p className="text-sm text-gray-600">
            Vous voulez mesurer cet angle sur vos propres données ?{' '}
            <Link to="/outils/representativite" className="text-violet-600 font-medium">
              Ouvrez l'outil
            </Link>{' '}
            et déposez votre fichier de noms.
          </p>
        </div>
      </div>
    </div>
  )
}
