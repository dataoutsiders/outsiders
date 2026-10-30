import { useState } from 'react'
import { ordinal } from '../../lib/contexteEgal'

const COULEUR = (d) => (d > 0 ? '#059669' : d < 0 ? '#DC2626' : '#9CA3AF')
const court = (s, n = 24) => (s.length > n ? `${s.slice(0, n - 1)}…` : s)

/**
 * Deux classements côte à côte : rang brut à gauche, rang de la lecture choisie à
 * droite, une ligne par école (vert = remonte, rouge = recule). Les trois plus fortes
 * remontées et chutes sont nommées ; le survol met une école en avant, le clic la
 * sélectionne.
 * @param {Array<{id, nom, rang, rangBrut}>} items
 */
export default function RangsSlope({ items, labelA = 'Classement au taux brut', labelB = 'À contexte égal', selectedId, onSelect }) {
  const [hover, setHover] = useState(null)
  const N = items.length
  if (N < 2) return null

  const W = 680
  const H = Math.min(920, Math.max(320, N * 7))
  const padT = 34
  const padB = 12
  const xA = 200
  const xB = W - 200
  const y = (r) => padT + ((r - 1) / (N - 1)) * (H - padT - padB)
  const lignes = items.map((x) => ({ ...x, d: x.rangBrut - x.rang })) // d > 0 : l'école remonte
  const nommes = new Set([
    ...[...lignes].sort((a, b) => b.d - a.d).slice(0, 3).filter((x) => x.d > 0).map((x) => x.id),
    ...[...lignes].sort((a, b) => a.d - b.d).slice(0, 3).filter((x) => x.d < 0).map((x) => x.id),
  ])
  const actif = hover ?? selectedId ?? null
  // L'école active est dessinée en dernier pour passer au-dessus des autres.
  const ordre = [...lignes].sort((a, b) => (a.id === actif) - (b.id === actif))

  // Étiquettes nommées : on les écarte verticalement pour que deux rangs voisins ne se chevauchent pas.
  const etale = (rangDe) => {
    const pos = new Map()
    let prec = -Infinity
    for (const x of lignes.filter((l) => nommes.has(l.id)).sort((a, b) => rangDe(a) - rangDe(b))) {
      const yy = Math.max(y(rangDe(x)), prec + 13)
      pos.set(x.id, yy)
      prec = yy
    }
    return pos
  }
  const posA = etale((x) => x.rangBrut)
  const posB = etale((x) => x.rang)

  return (
    <div className="overflow-x-auto">
      <svg
        viewBox={`0 0 ${W} ${H}`}
        className="w-full min-w-[540px]"
        role="img"
        aria-label={`${labelA} comparé au classement ${labelB.toLowerCase()}, ${N} écoles`}
      >
        <text x={xA} y={14} textAnchor="middle" fontSize={12} fontWeight={600} fill="#374151">{labelA}</text>
        <text x={xB} y={14} textAnchor="middle" fontSize={12} fontWeight={600} fill="#374151">{labelB}</text>
        <line x1={xA} x2={xA} y1={padT - 8} y2={H - padB + 4} stroke="#E5E7EB" />
        <line x1={xB} x2={xB} y1={padT - 8} y2={H - padB + 4} stroke="#E5E7EB" />
        {ordre.map((x) => {
          const on = actif === x.id
          const montre = on || (actif == null && nommes.has(x.id))
          const pale = actif != null && !on
          const c = COULEUR(x.d)
          return (
            <g
              key={x.id}
              onMouseEnter={() => setHover(x.id)}
              onMouseLeave={() => setHover(null)}
              onClick={() => onSelect?.(x.id)}
              style={{ cursor: onSelect ? 'pointer' : 'default' }}
            >
              <line x1={xA} y1={y(x.rangBrut)} x2={xB} y2={y(x.rang)} stroke="transparent" strokeWidth={9} />
              <line
                x1={xA} y1={y(x.rangBrut)} x2={xB} y2={y(x.rang)}
                stroke={c}
                strokeOpacity={pale ? 0.1 : montre ? 0.95 : 0.4}
                strokeWidth={on ? 2.6 : montre ? 1.8 : 1.1}
              />
              <circle cx={xA} cy={y(x.rangBrut)} r={on ? 3.6 : 2} fill={c} fillOpacity={pale ? 0.2 : 1} />
              <circle cx={xB} cy={y(x.rang)} r={on ? 3.6 : 2} fill={c} fillOpacity={pale ? 0.2 : 1} />
              {montre && (
                <>
                  <text x={xA - 8} y={(on ? y(x.rangBrut) : posA.get(x.id) ?? y(x.rangBrut)) + 4} textAnchor="end" fontSize={11} fill="#111827">
                    {court(x.nom)} · {ordinal(x.rangBrut)}
                  </text>
                  <text x={xB + 8} y={(on ? y(x.rang) : posB.get(x.id) ?? y(x.rang)) + 4} textAnchor="start" fontSize={11} fill={c} fontWeight={600}>
                    {ordinal(x.rang)} ({x.d > 0 ? `+${x.d}` : x.d === 0 ? '=' : x.d})
                  </text>
                </>
              )}
            </g>
          )
        })}
      </svg>
    </div>
  )
}
