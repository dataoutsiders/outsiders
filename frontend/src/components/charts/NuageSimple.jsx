import { useState } from 'react'
import { ols } from '../../lib/residuals'

// Graduations « rondes » (pas de 1, 2 ou 5 × 10^k) entre a et b.
function graduations(a, b, n = 5) {
  const brut = (b - a) / n
  const p = 10 ** Math.floor(Math.log10(brut))
  const pas = [1, 2, 5, 10].map((k) => k * p).find((s) => s >= brut) ?? brut
  const out = []
  for (let v = Math.ceil(a / pas) * pas; v <= b + 1e-9; v += pas) out.push(+v.toFixed(10))
  return out
}

// Graduations d'un axe logarithmique (1, 2, 5 × 10^k) entre 10^a et 10^b.
function graduationsLog(a, b) {
  const out = []
  for (let k = Math.floor(a); k <= Math.ceil(b); k++) {
    for (const m of [1, 2, 5]) {
      const v = m * 10 ** k
      if (Math.log10(v) >= a && Math.log10(v) <= b) out.push(v)
    }
  }
  return out
}

/**
 * Nuage de points simple (SVG) : un point par unité, droite des moindres carrés
 * (lib/residuals), extrêmes nommés, survol pour lire un point. Axe x linéaire ou
 * logarithmique.
 * @param {Array<{id:string, x:number, y:number, label:string}>} points
 */
export default function NuageSimple({
  points, xLabel, yLabel, fmtX = (v) => v.toLocaleString('fr-FR'), fmtY = (v) => v.toLocaleString('fr-FR'),
  logX = false, couleur = '#EA580C', height = 360,
}) {
  const [hover, setHover] = useState(null)
  const pts = points.filter((p) => p.x != null && p.y != null && (!logX || p.x > 0))
  if (pts.length < 3) return null

  const tx = (v) => (logX ? Math.log10(v) : v)
  const fit = ols(pts.map((p) => ({ x: tx(p.x), y: p.y })))
  const W = 640
  const H = height
  const m = { l: 62, r: 14, t: 12, b: 40 } // marge gauche : graduations + titre vertical sans chevauchement
  const xs = pts.map((p) => tx(p.x))
  const ys = pts.map((p) => p.y)
  const dx = (Math.max(...xs) - Math.min(...xs)) * 0.05 || 1
  const dy = (Math.max(...ys) - Math.min(...ys)) * 0.08 || 1
  const [x0, x1] = [Math.min(...xs) - dx, Math.max(...xs) + dx]
  const [y0, y1] = [Math.min(...ys) - dy, Math.max(...ys) + dy]
  const X = (v) => m.l + ((tx(v) - x0) / (x1 - x0)) * (W - m.l - m.r)
  const Y = (v) => m.t + (1 - (v - y0) / (y1 - y0)) * (H - m.t - m.b)
  const ticksX = logX ? graduationsLog(x0, x1) : graduations(x0, x1, 5)
  const ticksY = graduations(y0, y1, 5)

  // On nomme les deux plus hauts, les deux plus bas et les deux plus éloignés de la droite.
  const res = pts.map((p) => ({ ...p, e: fit ? p.y - (fit.a + fit.b * tx(p.x)) : 0 }))
  const nommes = new Set([
    ...[...res].sort((a, b) => b.y - a.y).slice(0, 2),
    ...[...res].sort((a, b) => a.y - b.y).slice(0, 2),
    ...[...res].sort((a, b) => Math.abs(b.e) - Math.abs(a.e)).slice(0, 2),
  ].map((p) => p.id))
  const survol = pts.find((p) => p.id === hover)
  const r = fit ? Math.sign(fit.b) * Math.sqrt(Math.max(0, fit.r2)) : null

  return (
    <div>
      <div className="overflow-x-auto">
        <svg viewBox={`0 0 ${W} ${H}`} className="w-full min-w-[480px]" role="img" aria-label={`${yLabel} selon ${xLabel}`}>
          {ticksY.map((v) => (
            <g key={`y${v}`}>
              <line x1={m.l} x2={W - m.r} y1={Y(v)} y2={Y(v)} stroke="#F1F5F9" />
              <text x={m.l - 6} y={Y(v) + 4} textAnchor="end" fontSize={11} fill="#6B7280">{fmtY(v)}</text>
            </g>
          ))}
          {ticksX.map((v) => (
            <g key={`x${v}`}>
              <line x1={X(v)} x2={X(v)} y1={m.t} y2={H - m.b} stroke="#F1F5F9" />
              <text x={X(v)} y={H - m.b + 15} textAnchor="middle" fontSize={11} fill="#6B7280">{fmtX(v)}</text>
            </g>
          ))}
          <text x={(m.l + W - m.r) / 2} y={H - 4} textAnchor="middle" fontSize={11} fill="#6B7280">{xLabel}</text>
          <text x={12} y={(m.t + H - m.b) / 2} textAnchor="middle" fontSize={11} fill="#6B7280"
            transform={`rotate(-90 12 ${(m.t + H - m.b) / 2})`}>{yLabel}</text>
          {fit && (
            <line
              x1={m.l} y1={Y(fit.a + fit.b * x0)} x2={W - m.r} y2={Y(fit.a + fit.b * x1)}
              stroke="#6B7280" strokeDasharray="5 4" strokeWidth={1.2}
            />
          )}
          {pts.map((p) => (
            <circle
              key={p.id} cx={X(p.x)} cy={Y(p.y)} r={hover === p.id ? 5.5 : 4}
              fill={couleur} fillOpacity={hover && hover !== p.id ? 0.3 : 0.75} stroke="#fff" strokeWidth={0.8}
              onMouseEnter={() => setHover(p.id)} onMouseLeave={() => setHover(null)}
            />
          ))}
          {!survol && res.filter((p) => nommes.has(p.id)).map((p) => (
            <text key={`n${p.id}`} x={X(p.x) + 7} y={Y(p.y) + 4} fontSize={11} fill="#111827">{p.label}</text>
          ))}
          {survol && (
            <text x={X(survol.x) + 8} y={Y(survol.y) - 8} fontSize={12} fontWeight={600} fill="#111827">
              {survol.label} : {fmtY(survol.y)} · {fmtX(survol.x)}
            </text>
          )}
        </svg>
      </div>
      {r != null && (
        <p className="text-sm text-gray-500 text-center">
          Corrélation : <strong>{r.toLocaleString('fr-FR', { maximumFractionDigits: 2, minimumFractionDigits: 2 })}</strong>{' '}
          ({pts.length} points, droite en pointillés)
        </p>
      )}
    </div>
  )
}
