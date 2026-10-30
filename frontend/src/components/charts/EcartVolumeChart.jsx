import { useMemo } from 'react'

const COULEURS = { dessus: '#059669', dessous: '#DC2626', norme: '#9CA3AF' }
const Z95 = 1.96
const TICKS_N = [10, 20, 50, 100, 200, 500, 1000]
const TICKS_E = [-30, -20, -10, 0, 10, 20, 30]

/**
 * Écart à l'attendu selon le nombre de candidats, un point par école.
 * L'entonnoir marque l'écart au-delà duquel le hasard ne suffit plus à l'expliquer
 * (95 %) : il se resserre quand le volume augmente. C'est ce qui empêche de désigner
 * une petite école pour un écart spectaculaire mais fragile.
 *
 * Le seuil reprend la règle de décision du pipeline (écart rétréci, intervalle à 95 %
 * hors de 0), calculé ici pour le taux national p et l'écart-type τ des écoles.
 * @param {Array<{id, n, ecart:number, verdict:string}>} points  ecart en points
 * @param {number} p    taux national (0-1)
 * @param {number} tau  écart-type des écarts propres aux écoles (0-1)
 * @param {Set<string>} [highlight]  écoles à mettre en avant
 */
export default function EcartVolumeChart({ points, p, tau, highlight = null, height = 360 }) {
  const W = 720
  const H = height
  const m = { l: 48, r: 14, t: 12, b: 38 }
  const nMax = Math.max(1000, ...points.map((x) => x.n))
  const lMin = Math.log10(10)
  const lMax = Math.log10(nMax)
  const x = (n) => m.l + ((Math.log10(Math.max(10, n)) - lMin) / (lMax - lMin)) * (W - m.l - m.r)
  const Y = 35
  const y = (e) => m.t + (1 - (Math.max(-Y, Math.min(Y, e)) + Y) / (2 * Y)) * (H - m.t - m.b)

  // Seuil de décision (60 points de n, calcul négligeable à chaque rendu).
  const t2 = tau * tau
  const seuil = (n) => {
    const v = (p * (1 - p)) / n
    return Z95 * Math.sqrt((v * (t2 + v)) / t2) * 100
  }
  const ns = Array.from({ length: 60 }, (_, i) => 10 ** (lMin + (i / 59) * (lMax - lMin)))
  const entonnoir = {
    haut: ns.map((n) => `${x(n).toFixed(1)},${y(seuil(n)).toFixed(1)}`).join(' '),
    bas: ns.map((n) => `${x(n).toFixed(1)},${y(-seuil(n)).toFixed(1)}`).join(' '),
  }

  const fond = highlight ? points.filter((pt) => !highlight.has(pt.id)) : points
  const avant = highlight ? points.filter((pt) => highlight.has(pt.id)) : []

  return (
    <div className="overflow-x-auto">
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full min-w-[520px]" role="img"
        aria-label="Écart de chaque auto-école à son taux attendu, selon son nombre de candidats">
        {TICKS_E.map((e) => (
          <g key={e}>
            <line x1={m.l} x2={W - m.r} y1={y(e)} y2={y(e)} stroke={e === 0 ? '#9CA3AF' : '#F1F5F9'} />
            <text x={m.l - 6} y={y(e) + 4} textAnchor="end" fontSize={11} fill="#6B7280">
              {e > 0 ? `+${e}` : e}
            </text>
          </g>
        ))}
        {TICKS_N.filter((n) => n <= nMax).map((n) => (
          <g key={n}>
            <line x1={x(n)} x2={x(n)} y1={m.t} y2={H - m.b} stroke="#F1F5F9" />
            <text x={x(n)} y={H - m.b + 16} textAnchor="middle" fontSize={11} fill="#6B7280">{n}</text>
          </g>
        ))}
        <text x={(m.l + W - m.r) / 2} y={H - 4} textAnchor="middle" fontSize={11} fill="#6B7280">
          candidats en première présentation (échelle logarithmique)
        </text>
        <text x={12} y={(m.t + H - m.b) / 2} textAnchor="middle" fontSize={11} fill="#6B7280"
          transform={`rotate(-90 12 ${(m.t + H - m.b) / 2})`}>
          écart à l'attendu (points)
        </text>

        {fond.map((pt) => (
          <circle key={pt.id} cx={x(pt.n)} cy={y(pt.ecart)} r={1.7}
            fill={COULEURS[pt.verdict] || COULEURS.norme} fillOpacity={highlight ? 0.14 : 0.45} />
        ))}
        <polyline points={entonnoir.haut} fill="none" stroke="#111827" strokeWidth={1.4} strokeDasharray="5 4" />
        <polyline points={entonnoir.bas} fill="none" stroke="#111827" strokeWidth={1.4} strokeDasharray="5 4" />
        {avant.map((pt) => (
          <circle key={pt.id} cx={x(pt.n)} cy={y(pt.ecart)} r={3.4}
            fill={COULEURS[pt.verdict] || COULEURS.norme} stroke="#fff" strokeWidth={0.8}>
            <title>{`${pt.nom} (${pt.commune}) : ${pt.ecart > 0 ? '+' : ''}${pt.ecart.toLocaleString('fr-FR', { maximumFractionDigits: 1 })} pts, ${pt.n} candidats`}</title>
          </circle>
        ))}
      </svg>
      <div className="flex flex-wrap gap-x-5 gap-y-1 text-xs text-gray-500 mt-1 pl-12">
        <span><span className="inline-block w-2.5 h-2.5 rounded-full mr-1.5 align-middle" style={{ background: COULEURS.dessus }} />nettement au-dessus</span>
        <span><span className="inline-block w-2.5 h-2.5 rounded-full mr-1.5 align-middle" style={{ background: COULEURS.dessous }} />nettement en dessous</span>
        <span><span className="inline-block w-2.5 h-2.5 rounded-full mr-1.5 align-middle" style={{ background: COULEURS.norme }} />dans l'attendu</span>
        <span><span className="inline-block w-5 border-t-2 border-dashed border-gray-900 mr-1.5 align-middle" />seuil du hasard (95 %)</span>
      </div>
    </div>
  )
}
