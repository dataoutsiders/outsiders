import { useMemo, useState } from 'react'
import {
  ScatterChart, Scatter, XAxis, YAxis, Tooltip, ReferenceLine, ResponsiveContainer, Cell,
} from 'recharts'
import { withResiduals } from '../../lib/residuals'
import { regionOf } from '../../lib/regions'
import { depFromInsee } from '../../lib/territoire'

const norm = (s) => String(s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase()
const round1 = (v) => (Math.round(v * 10) / 10).toLocaleString('fr-FR')
const fmtPop = (v) => {
  const p = Math.pow(10, v)
  return p >= 1e6 ? `${(p / 1e6).toFixed(p >= 1e7 ? 0 : 1)} M` : `${Math.round(p / 1000)} k`
}
const color = (t) => (t > 1 ? '#10B981' : t < -1 ? '#EF4444' : '#cbd5e1')

// Axes disponibles : comment lire la valeur, la placer, et la formater.
const AXES = {
  pop: { label: 'Population', get: (v) => v.pop, plot: (v) => Math.log10(v.pop), tick: (x) => fmtPop(x), show: (v) => `${v.pop.toLocaleString('fr-FR')} hab.`, axis: 'Population' },
  revenu: { label: 'Niveau de vie', get: (v) => v.revenu.p50, plot: (v) => v.revenu.p50, tick: (x) => `${Math.round(x / 1000)} k€`, show: (v) => `${v.revenu.p50.toLocaleString('fr-FR')} €`, axis: 'Niveau de vie médian (€)' },
  inter: { label: 'Écart entre quartiers', get: (v) => v.revenu.p90_p10, plot: (v) => v.revenu.p90_p10, tick: (x) => `×${round1(x)}`, show: (v) => `×${round1(v.revenu.p90_p10)} entre quartiers`, axis: 'Écart entre quartiers (×)' },
  intra: { label: 'Mélange dans un quartier', get: (v) => v.revenu.interne_rd, plot: (v) => v.revenu.interne_rd, tick: (x) => `×${round1(x)}`, show: (v) => `×${round1(v.revenu.interne_rd)} dans un quartier`, axis: 'Mélange dans un quartier (×)' },
}
const X_OPTS = ['pop', 'revenu', 'inter']
const Y_OPTS = ['intra', 'inter']

function Chip({ active, onClick, children }) {
  return (
    <button
      onClick={onClick}
      className={`text-xs font-medium px-2.5 py-1 rounded-full border ${active ? 'bg-blue-600 border-blue-600 text-white' : 'bg-white border-gray-200 text-gray-600 hover:border-gray-300'}`}
    >
      {children}
    </button>
  )
}

/**
 * Nuage « outsiders » configurable : on choisit les axes (population, niveau de
 * vie, écart entre quartiers, mélange dans un quartier), on filtre par territoire
 * (région, département), et on cherche une ville pour la repérer. La droite est
 * le pronostic ; les points qui s'en écartent sont les outsiders.
 */
export default function MixiteScatter({ villes, deps = [], onSelect }) {
  const [xKey, setXKey] = useState('pop')
  const [yKey, setYKey] = useState('intra')
  const [scope, setScope] = useState('france') // 'france' | 'r:<region>' | 'd:<dep>'
  const [q, setQ] = useState('')

  const ax = AXES[xKey]
  const ay = AXES[yKey]

  const options = useMemo(() => {
    const regions = new Set()
    for (const v of villes) {
      const r = regionOf(v.code)
      if (r) regions.add(r)
    }
    return {
      regions: [...regions].sort((a, b) => a.localeCompare(b)),
      deps: [...deps].sort((a, b) => a.nom.localeCompare(b.nom)),
    }
  }, [villes, deps])

  const { points, model, over, under, filtered } = useMemo(() => {
    let list = villes
    if (scope.startsWith('r:')) list = villes.filter((v) => regionOf(v.code) === scope.slice(2))
    else if (scope.startsWith('d:')) list = villes.filter((v) => depFromInsee(v.code) === scope.slice(2))
    const pts = list
      .filter((v) => ax.get(v) != null && ay.get(v) != null && (xKey !== 'pop' || v.pop))
      .map((v) => ({ x: ax.plot(v), y: ay.get(v), v, nom: v.nom, code: v.code }))
    const wr = withResiduals(pts)
    const sorted = wr.model ? [...wr.points].sort((a, b) => b.t - a.t) : []
    return { points: wr.points, model: wr.model, over: sorted.slice(0, 6), under: sorted.slice(-6).reverse(), filtered: list.length }
  }, [villes, scope, xKey, yKey, ax, ay])

  const hit = useMemo(() => {
    if (q.trim().length < 2) return null
    const nq = norm(q.trim())
    return points.find((p) => norm(p.nom).startsWith(nq)) || points.find((p) => norm(p.nom).includes(nq)) || null
  }, [q, points])

  if (!villes.length) return null
  const xs = points.map((p) => p.x)
  const x0 = xs.length ? Math.min(...xs) : 0
  const x1 = xs.length ? Math.max(...xs) : 1

  return (
    <div>
      {/* Contrôles : axes, territoire, recherche */}
      <div className="flex flex-wrap items-center gap-x-2 gap-y-2 mb-3">
        <span className="text-xs text-gray-400">Vertical</span>
        {Y_OPTS.map((k) => <Chip key={k} active={yKey === k} onClick={() => setYKey(k)}>{AXES[k].label}</Chip>)}
        <span className="text-xs text-gray-400 ml-2">Horizontal</span>
        {X_OPTS.map((k) => <Chip key={k} active={xKey === k} onClick={() => setXKey(k)}>{AXES[k].label}</Chip>)}
      </div>
      <div className="flex flex-wrap items-center gap-2 mb-4">
        <select
          value={scope} onChange={(e) => setScope(e.target.value)}
          className="text-sm border border-gray-300 rounded-lg px-2 py-1.5 bg-white max-w-[16rem]"
        >
          <option value="france">France entière</option>
          <optgroup label="Régions">
            {options.regions.map((r) => <option key={r} value={`r:${r}`}>{r}</option>)}
          </optgroup>
          <optgroup label="Départements">
            {options.deps.map((d) => <option key={d.dep} value={`d:${d.dep}`}>{d.nom} ({d.dep})</option>)}
          </optgroup>
        </select>
        <input
          value={q} onChange={(e) => setQ(e.target.value)} placeholder="Repérer une ville…"
          className="text-sm border border-gray-300 rounded-lg px-3 py-1.5 outline-none focus:border-blue-400 flex-1 min-w-[10rem]"
        />
        <span className="text-xs text-gray-400">{filtered} villes</span>
      </div>

      {model ? (
        <ResponsiveContainer width="100%" height={340}>
          <ScatterChart margin={{ top: 10, right: 20, bottom: 25, left: 5 }}>
            <XAxis
              type="number" dataKey="x" domain={['dataMin', 'dataMax']} tick={{ fontSize: 11 }}
              tickFormatter={ax.tick}
              label={{ value: ax.axis, position: 'insideBottom', offset: -12, fontSize: 12 }}
            />
            <YAxis
              type="number" dataKey="y" domain={['dataMin', 'dataMax']} tick={{ fontSize: 11 }}
              tickFormatter={ay.tick}
              label={{ value: ay.axis, angle: -90, position: 'insideLeft', fontSize: 12 }}
            />
            <Tooltip
              cursor={{ strokeDasharray: '3 3' }}
              content={({ payload }) =>
                payload && payload[0] ? (
                  <div className="bg-gray-900 text-white text-xs rounded-lg px-2.5 py-1.5">
                    <div className="font-semibold">{payload[0].payload.nom}</div>
                    <div>{ax.show(payload[0].payload.v)}</div>
                    <div>{ay.show(payload[0].payload.v)}</div>
                  </div>
                ) : null
              }
            />
            <ReferenceLine
              segment={[{ x: x0, y: model.a + model.b * x0 }, { x: x1, y: model.a + model.b * x1 }]}
              stroke="#6b7280" strokeDasharray="5 5"
            />
            <Scatter data={points} onClick={(d) => d && d.code && onSelect(d.code)} style={{ cursor: 'pointer' }}>
              {points.map((p, i) => (
                <Cell key={i} fill={color(p.t)} fillOpacity={0.7} />
              ))}
            </Scatter>
            {hit && (
              <Scatter data={[hit]} shape={(p) => <circle cx={p.cx} cy={p.cy} r={7} fill="#111827" stroke="#fff" strokeWidth={2} />} />
            )}
          </ScatterChart>
        </ResponsiveContainer>
      ) : (
        <p className="py-10 text-center text-sm text-gray-400">Pas assez de villes pour ce territoire.</p>
      )}

      {hit && (
        <p className="text-sm text-gray-700 text-center -mt-1">
          <strong>{hit.nom}</strong> : {ax.show(hit.v)}, {ay.show(hit.v)}.{' '}
          <button onClick={() => onSelect(hit.code)} className="text-blue-600 hover:underline">voir sa fiche</button>
        </p>
      )}
      <p className="text-sm text-gray-500 text-center mt-1">
        La droite est la tendance. Au-dessus, les villes qui font <strong>plus</strong> que la tendance ne le laisse
        attendre ; en dessous, <strong>moins</strong>. Cliquez un point pour ouvrir la fiche.
      </p>
      {over.length > 0 && (
        <div className="grid sm:grid-cols-2 gap-6 mt-4">
          <div>
            <h4 className="text-sm font-semibold text-emerald-700 mb-1">Au-dessus de la tendance</h4>
            {over.map((v) => (
              <button key={v.code} onClick={() => onSelect(v.code)} className="block text-sm text-gray-700 hover:underline text-left">{v.nom}</button>
            ))}
          </div>
          <div>
            <h4 className="text-sm font-semibold text-red-700 mb-1">En dessous de la tendance</h4>
            {under.map((v) => (
              <button key={v.code} onClick={() => onSelect(v.code)} className="block text-sm text-gray-700 hover:underline text-left">{v.nom}</button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
