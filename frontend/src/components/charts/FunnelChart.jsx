import { ChevronDown } from 'lucide-react'
import { greyToEmerald, textOn } from '../../lib/colorScale'

/**
 * Entonnoir « filtre invisible » : une bande par étape, largeur ∝ √effectif,
 * couleur + valeur = IDP. Plus on monte vers le pouvoir, plus l'entonnoir se
 * resserre ET plus la diversité chute.
 *
 * @param {Array<{label:string, value:number, n:number}>} data  trié par effectif décroissant
 */
export default function FunnelChart({ data }) {
  if (!data?.length) return null
  const maxN = Math.max(...data.map((d) => d.n))
  const idps = data.map((d) => d.value)
  const minIdp = Math.min(...idps)
  const maxIdp = Math.max(...idps)

  const widthOf = (n) => Math.max(16, Math.sqrt(n / maxN) * 100)
  const tOf = (idp) => (maxIdp === minIdp ? 1 : (idp - minIdp) / (maxIdp - minIdp))

  return (
    <div>
      {data.map((d, i) => {
        const t = tOf(d.value)
        return (
          <div key={d.label}>
            <div className="text-center">
              <div className="flex items-center justify-center gap-2 text-sm mb-1">
                <span className="font-medium text-gray-800">{d.label}</span>
                <span className="text-gray-400">· n = {d.n.toLocaleString('fr-FR')}</span>
              </div>
              <div
                className="mx-auto h-16 rounded-xl flex items-center justify-center transition-all"
                style={{ width: `${widthOf(d.n)}%`, backgroundColor: greyToEmerald(t) }}
              >
                <span className="text-2xl font-bold" style={{ color: textOn(t) }}>
                  {d.value}%
                </span>
              </div>
            </div>
            {i < data.length - 1 && (
              <div className="flex justify-center py-1">
                <ChevronDown size={20} className="text-gray-300" />
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}
