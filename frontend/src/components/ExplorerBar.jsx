import { Link } from 'react-router-dom'
import { DECOUPAGES, DECOUPAGE_BY_ID, MODE_META } from '../config/decoupages'

/**
 * Bandeau de l'explorateur, partagé par tous les découpages (territoire sur /atlas et
 * /territoires, milieu social sur /explorer/milieu-social, etc.).
 * Rend visible la colonne vertébrale : un DÉCOUPAGE (unité) + un MODE de lecture.
 *
 * @param {string} decoupage  id du découpage courant (ex. 'territoire', 'milieu-social')
 * @param {('carte'|'fiche'|'tableau')} mode  mode affiché par la page hôte
 */
export default function ExplorerBar({ decoupage, mode }) {
  const cur = DECOUPAGE_BY_ID[decoupage]
  return (
    <div className="border-b border-gray-200 bg-gray-50">
      <div className="max-w-5xl mx-auto px-4 py-3 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        {/* Découpage (unité d'analyse) : cliquable pour basculer */}
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-xs font-semibold uppercase tracking-wide text-gray-400">Découpage</span>
          {DECOUPAGES.map((d) => {
            const Icon = d.icon
            const actif = d.id === decoupage
            const dispo = d.statut === 'disponible'
            const cls = `inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-sm ${
              actif
                ? 'border-blue-300 bg-blue-50 text-blue-700 font-medium'
                : dispo
                  ? 'border-gray-200 bg-white text-gray-600 hover:border-blue-300 hover:text-blue-700'
                  : 'border-gray-200 bg-white text-gray-400'
            }`
            const inner = (
              <>
                <Icon size={14} />
                {d.titre}
                {!dispo && <span className="text-[10px] uppercase tracking-wide">bientôt</span>}
              </>
            )
            return dispo && !actif ? (
              <Link key={d.id} to={d.route} className={cls}>
                {inner}
              </Link>
            ) : (
              <span key={d.id} title={dispo ? d.sousTitre : 'Bientôt disponible'} className={cls}>
                {inner}
              </span>
            )
          })}
        </div>

        {/* Mode de lecture du découpage courant */}
        {cur && cur.modeRoutes && (
          <div className="inline-flex rounded-lg border border-gray-200 bg-white overflow-hidden self-start shrink-0">
            {cur.modes.map((m) => {
              const meta = MODE_META[m]
              const Icon = meta.icon
              const actif = mode === m
              return (
                <Link
                  key={m}
                  to={cur.modeRoutes[m]}
                  title={meta.aide}
                  className={`inline-flex items-center gap-1.5 px-3 py-1.5 text-sm transition-colors ${
                    actif ? 'bg-blue-600 text-white font-medium' : 'text-gray-600 hover:bg-gray-50'
                  }`}
                >
                  <Icon size={15} />
                  <span className="hidden sm:inline">{meta.label}</span>
                </Link>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
