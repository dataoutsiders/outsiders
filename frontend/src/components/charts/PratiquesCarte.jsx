import { useMemo, useState } from 'react'

const W = 780
const H = 640
const M = 14
const THEMES = ['Tout', 'Aliments', 'Achats', 'Repas', 'Représentations', 'Activités']

/** Rectangles de chevauchement ? */
const touche = (a, b) => a.x < b.x + b.w && b.x < a.x + a.w && a.y < b.y + b.h && b.y < a.y + a.h

/**
 * Espace des pratiques : chaque point gris est une pratique (ACM), deux pratiques proches sont
 * fréquentes chez les mêmes personnes. Les groupes sociaux sont projetés par-dessus, sans avoir
 * servi à dessiner la carte. Étiquettes placées sans chevauchement, les autres au survol.
 */
export default function PratiquesCarte({ modalites, projections, couleurs, axes }) {
  const blocs = Object.keys(projections)
  const [bloc, setBloc] = useState(blocs.includes('Diplôme') ? 'Diplôme' : blocs[0])
  const [theme, setTheme] = useState('Tout')
  const [survol, setSurvol] = useState(null)

  const projetes = projections[bloc]
  const { X, Y } = useMemo(() => {
    const tous = [...modalites, ...Object.values(projections).flat()]
    const xs = tous.map((p) => p.x)
    const ys = tous.map((p) => p.y)
    const [x0, x1] = [Math.min(...xs) - 0.12, Math.max(...xs) + 0.12]
    const [y0, y1] = [Math.min(...ys) - 0.1, Math.max(...ys) + 0.1]
    return {
      X: (v) => M + ((v - x0) / (x1 - x0)) * (W - 2 * M),
      Y: (v) => M + (1 - (v - y0) / (y1 - y0)) * (H - 2 * M),
    }
  }, [modalites, projections])

  const visibles = useMemo(
    () => modalites.filter((m) => theme === 'Tout' || m.theme === theme),
    [modalites, theme],
  )

  // Étiquettes : d'abord les groupes projetés, puis les pratiques les plus structurantes.
  const etiquettes = useMemo(() => {
    // Réservés d'emblée : titres d'axes et points, pour qu'aucune étiquette ne les recouvre.
    const boites = [
      { x: M, y: Y(0) - 20, w: 165, h: 18 },
      { x: W - M - 175, y: Y(0) - 20, w: 175, h: 18 },
      { x: X(0), y: M, w: 150, h: 18 },
      { x: X(0), y: H - M - 18, w: 130, h: 18 },
      ...[...visibles, ...projetes].map((p) => ({ x: X(p.x) - 3, y: Y(p.y) - 3, w: 6, h: 6 })),
    ]
    const place = (p, taille, largeurLettre) => {
      const w = p.label.length * largeurLettre
      const h = taille + 3
      const px = X(p.x)
      const py = Y(p.y)
      const essais = [
        { x: px + 8, y: py - h / 2, ancre: 'start' },
        { x: px - 8 - w, y: py - h / 2, ancre: 'end' },
        { x: px - w / 2, y: py - h - 7, ancre: 'middle' },
        { x: px - w / 2, y: py + 7, ancre: 'middle' },
      ]
      for (const e of essais) {
        const b = { x: e.x, y: e.y, w, h }
        if (b.x < 2 || b.x + w > W - 2 || b.y < 2 || b.y + h > H - 2) continue
        const propre = { x: X(p.x) - 3, y: Y(p.y) - 3, w: 6, h: 6 }
        if (boites.some((o) => touche(o, b) && !touche(o, propre))) continue
        boites.push(b)
        return { ...p, tx: e.ancre === 'start' ? e.x : e.ancre === 'end' ? e.x + w : px, ty: e.y + h - 4, ancre: e.ancre }
      }
      return null
    }
    const groupes = projetes.map((p) => place(p, 13, 7.1)).filter(Boolean)
    const pratiques = [...visibles]
      .sort((a, b) => b.ctr1 + b.ctr2 - (a.ctr1 + a.ctr2))
      .map((m) => place(m, 11, 5.6))
      .filter(Boolean)
    return { groupes, pratiques }
  }, [projetes, visibles, X, Y])

  const couleur = couleurs[bloc] || '#374151'
  const ligne = ['Âge', 'Diplôme', 'Revenu par personne'].includes(bloc)

  return (
    <div>
      <div className="flex flex-wrap items-center gap-2 mb-2">
        <span className="text-xs font-semibold uppercase tracking-wide text-gray-400 mr-1">Projeter</span>
        {blocs.map((b) => (
          <button
            key={b}
            type="button"
            aria-pressed={b === bloc}
            onClick={() => setBloc(b)}
            className="px-3 py-1 rounded-full text-sm font-medium border transition-colors"
            style={b === bloc ? { backgroundColor: couleurs[b] || '#374151', borderColor: couleurs[b] || '#374151', color: '#fff' } : { borderColor: '#e5e7eb', color: '#4b5563' }}
          >
            {b}
          </button>
        ))}
      </div>
      <div className="flex flex-wrap items-center gap-2 mb-3">
        <span className="text-xs font-semibold uppercase tracking-wide text-gray-400 mr-1">Pratiques</span>
        {THEMES.map((t) => (
          <button
            key={t}
            type="button"
            aria-pressed={t === theme}
            onClick={() => setTheme(t)}
            className={`px-2.5 py-0.5 rounded-full text-xs font-medium border transition-colors ${t === theme ? 'bg-gray-800 border-gray-800 text-white' : 'border-gray-200 text-gray-600 hover:bg-gray-50'}`}
          >
            {t}
          </button>
        ))}
      </div>

      <div className="overflow-x-auto -mx-1">
        <div className="relative min-w-[640px] px-1">
          <svg viewBox={`0 0 ${W} ${H}`} className="w-full h-auto" role="img" aria-label="Carte factorielle des pratiques. Le détail des deux axes figure sous le graphique.">
            <line x1={X(0)} x2={X(0)} y1={M} y2={H - M} stroke="#E5E7EB" />
            <line y1={Y(0)} y2={Y(0)} x1={M} x2={W - M} stroke="#E5E7EB" />
            <text x={M + 2} y={Y(0) - 6} fontSize="11" fill="#6B7280" fontWeight="600">{axes.gauche}</text>
            <text x={W - M - 2} y={Y(0) - 6} fontSize="11" fill="#6B7280" fontWeight="600" textAnchor="end">{axes.droite}</text>
            <text x={X(0) + 6} y={M + 10} fontSize="11" fill="#6B7280" fontWeight="600">{axes.haut}</text>
            <text x={X(0) + 6} y={H - M - 4} fontSize="11" fill="#6B7280" fontWeight="600">{axes.bas}</text>

            {visibles.map((m) => (
              <g key={m.label}>
                <circle cx={X(m.x)} cy={Y(m.y)} r="3" fill="#9CA3AF" />
                <circle
                  cx={X(m.x)} cy={Y(m.y)} r="9" fill="transparent"
                  onMouseEnter={() => setSurvol(m)} onMouseLeave={() => setSurvol(null)}
                />
              </g>
            ))}
            {etiquettes.pratiques.map((m) => (
              <text key={m.label} x={m.tx} y={m.ty} fontSize="11" fill="#4B5563" textAnchor={m.ancre} pointerEvents="none" stroke="#fff" strokeWidth="3" paintOrder="stroke">
                {m.label}
              </text>
            ))}

            {ligne && (
              <polyline
                points={projetes.map((p) => `${X(p.x)},${Y(p.y)}`).join(' ')}
                fill="none" stroke={couleur} strokeWidth="2" strokeLinejoin="round" strokeLinecap="round"
              />
            )}
            {projetes.map((p) => (
              <circle key={p.label} cx={X(p.x)} cy={Y(p.y)} r="6.5" fill={couleur} stroke="#fff" strokeWidth="2"
                onMouseEnter={() => setSurvol({ ...p, theme: bloc })} onMouseLeave={() => setSurvol(null)} />
            ))}
            {etiquettes.groupes.map((p) => (
              <text key={p.label} x={p.tx} y={p.ty} fontSize="13" fontWeight="700" fill="#111827" textAnchor={p.ancre} pointerEvents="none" stroke="#fff" strokeWidth="3" paintOrder="stroke">
                {p.label}
              </text>
            ))}
          </svg>
          {survol && (
            <div
              className="absolute z-10 pointer-events-none bg-white border border-gray-200 rounded-lg shadow px-3 py-1.5 text-xs text-gray-700 max-w-[220px]"
              style={{ left: `${Math.min(70, (X(survol.x) / W) * 100)}%`, top: `${Math.max(2, (Y(survol.y) / H) * 100 - 9)}%` }}
            >
              <div className="font-semibold text-gray-900">{survol.label}</div>
              <div className="text-gray-500">
                {survol.theme}
                {survol.part != null && ` · ${survol.part.toLocaleString('fr-FR')} % des adultes`}
                {survol.n != null && ` · ${survol.n.toLocaleString('fr-FR')} répondants`}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
