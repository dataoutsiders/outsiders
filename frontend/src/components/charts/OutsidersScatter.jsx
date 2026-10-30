import { useMemo, useState } from 'react'
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  ZAxis,
  Tooltip,
  ReferenceLine,
  ResponsiveContainer,
  Cell,
} from 'recharts'
import { withResiduals, residCategory } from '../../lib/residuals'

// Couleur selon l'écart au pronostic (vert = au-dessus, rouge = en dessous).
const CAT_COLOR = {
  'pos-fort': '#059669',
  pos: '#6ee7b7',
  neutre: '#cbd5e1',
  neg: '#fca5a5',
  'neg-fort': '#dc2626',
}

const POP_SEUILS = [
  { label: 'Toutes', v: 0 },
  { label: '≥ 1 000 hab.', v: 1000 },
  { label: '≥ 5 000', v: 5000 },
  { label: '≥ 10 000', v: 10000 },
]

const tickK = (v) => (Math.abs(v) >= 1000 ? `${Math.round(v / 1000)}k` : `${v}`)
const sigma = (t) => `${t >= 0 ? '+' : ''}${t.toFixed(1)} σ`
// Minuscule en tête, sauf si le 1er mot est un acronyme (IPS, IDP, HLM...).
const lower = (s) => {
  const str = String(s || '')
  const head = str.split(/[\s(]/)[0]
  if (head.length > 1 && head === head.toUpperCase()) return str
  return str.charAt(0).toLowerCase() + str.slice(1)
}

function Reading({ p, xLabel, yLabel, yFmt, sens }) {
  if (!p) return null
  const obs = yFmt ? yFmt(p.y) : p.y
  const att = yFmt ? yFmt(p.yhat) : Math.round(p.yhat)
  return (
    <span>
      À <strong>{lower(xLabel)}</strong> comparable, <strong>{p.nom}</strong> se situe nettement{' '}
      {sens === 'pos' ? 'au-dessus' : 'en dessous'} du pronostic sur {lower(yLabel)} ({obs} observé
      contre {att} attendu).
    </span>
  )
}

/**
 * Nuage « Outsiders » : upgrade du croisement de deux indicateurs. On ajuste une
 * droite (OLS) et on met en avant les territoires dont la valeur Y s'écarte le
 * plus de son pronostic (résidus studentisés). Tout est calculé dans le
 * navigateur, à la maille courante (changer de maille recalcule la relation).
 *
 * @param points  [{code, nom, x, y, pop}]
 * @param level   'commune' | 'dept' | 'epci'
 * @param mots    {sing, plur} : vocabulaire de l'unité si ce n'est pas un territoire (ex. pays)
 * @param onHover (code|null)  surligne le territoire sur la carte
 * @param onSelect(code)|null  ouvre la fiche du territoire (null = non cliquable)
 */
export default function OutsidersScatter({
  points,
  xLabel,
  xUnit,
  xFmt,
  yLabel,
  yUnit,
  yFmt,
  level = 'dept',
  mots = null,
  onHover = null,
  onSelect = null,
}) {
  const motSing = mots?.sing || (level === 'commune' ? 'commune' : level === 'epci' ? 'intercommunalité' : 'département')
  const motPlur = mots?.plur || (level === 'commune' ? 'communes' : level === 'epci' ? 'intercommunalités' : 'départements')
  // Sans population (unités non territoriales, ex. pays), le filtre de taille n'a pas de sens.
  const hasPop = points.some((p) => p.pop != null)

  // Filtre de taille : sans seuil, les outsiders ne sont que de petites unités à
  // forte variance (le bruit prend l'air de l'intelligence). Défaut : exclure < 1 000 hab.
  const [seuil, setSeuil] = useState(level === 'commune' ? 1000 : 0)
  const [hover, setHover] = useState(null)

  const filtered = useMemo(
    () => points.filter((p) => p.pop == null || p.pop >= seuil),
    [points, seuil],
  )
  const { model, points: pts } = useMemo(() => withResiduals(filtered), [filtered])

  const enriched = useMemo(
    () => pts.map((p) => ({ ...p, cat: residCategory(p.t), tabs: Math.min(4, Math.abs(p.t)) })),
    [pts],
  )

  const positifs = useMemo(
    () => [...enriched].filter((p) => p.t > 0).sort((a, b) => b.t - a.t).slice(0, 6),
    [enriched],
  )
  const negatifs = useMemo(
    () => [...enriched].filter((p) => p.t < 0).sort((a, b) => a.t - b.t).slice(0, 6),
    [enriched],
  )

  if (!model || enriched.length < 5) {
    return (
      <p className="text-sm text-gray-500">
        Pas assez de {motPlur} renseignés à cette maille pour estimer une relation fiable.
      </p>
    )
  }

  const xs = enriched.map((p) => p.x)
  const x0 = Math.min(...xs)
  const x1 = Math.max(...xs)
  const r2pct = Math.round(model.r2 * 100)
  const faible = model.r2 < 0.2

  const setH = (code) => {
    setHover(code)
    onHover && onHover(code)
  }
  const hoveredPt = hover ? enriched.find((p) => p.code === hover) : null

  return (
    <div>
      {/* Filtre de population (uniquement pour les unités territoriales) */}
      {hasPop && (
        <div className="flex flex-wrap items-center gap-2 mb-3 text-sm">
          <span className="text-gray-500">Garder les {motPlur} de</span>
          <div className="inline-flex rounded-lg border border-gray-200 overflow-hidden">
            {POP_SEUILS.map((s) => (
              <button
                key={s.v}
                onClick={() => setSeuil(s.v)}
                className={`px-2.5 py-1 transition-colors ${
                  seuil === s.v ? 'bg-gray-800 text-white font-medium' : 'bg-white text-gray-600 hover:bg-gray-50'
                }`}
              >
                {s.label}
              </button>
            ))}
          </div>
          <span className="text-gray-400">{enriched.length} {motPlur} retenus</span>
        </div>
      )}

      <ResponsiveContainer width="100%" height={380}>
        <ScatterChart margin={{ top: 10, right: 20, bottom: 25, left: 10 }}>
          <XAxis
            type="number"
            dataKey="x"
            domain={['dataMin', 'dataMax']}
            tick={{ fontSize: 11 }}
            tickFormatter={tickK}
            label={{ value: `${xLabel}${xUnit ? ` (${xUnit})` : ''}`, position: 'insideBottom', offset: -12, fontSize: 12 }}
          />
          <YAxis
            type="number"
            dataKey="y"
            domain={['dataMin - 2', 'dataMax + 2']}
            tick={{ fontSize: 11 }}
            label={{ value: yLabel, angle: -90, position: 'insideLeft', fontSize: 12 }}
          />
          <ZAxis type="number" dataKey="tabs" range={[18, 190]} />
          <Tooltip
            cursor={{ strokeDasharray: '3 3' }}
            content={({ payload }) => {
              const p = payload && payload[0] && payload[0].payload
              if (!p) return null
              return (
                <div className="bg-gray-900 text-white text-xs rounded-lg px-2.5 py-1.5">
                  <div className="font-semibold">{p.nom}</div>
                  <div>{yLabel} : {yFmt ? yFmt(p.y) : p.y}</div>
                  <div>{xLabel} : {xFmt ? xFmt(p.x) : p.x}</div>
                  <div className="text-gray-300 mt-0.5">
                    écart au pronostic : {sigma(p.t)} ({yFmt ? yFmt(p.yhat) : Math.round(p.yhat)} attendu)
                  </div>
                </div>
              )
            }}
          />
          {/* Droite d'ajustement (le pronostic) */}
          <ReferenceLine
            segment={[
              { x: x0, y: model.a + model.b * x0 },
              { x: x1, y: model.a + model.b * x1 },
            ]}
            stroke="#6b7280"
            strokeDasharray="5 5"
          />
          <Scatter data={enriched}>
            {enriched.map((p) => (
              <Cell key={p.code} fill={CAT_COLOR[p.cat]} fillOpacity={0.82} />
            ))}
          </Scatter>
          {/* Anneau de surbrillance du territoire survolé dans les listes */}
          {hoveredPt && (
            <Scatter
              data={[hoveredPt]}
              shape={(props) => (
                <circle cx={props.cx} cy={props.cy} r={11} fill="none" stroke="#111827" strokeWidth={2} />
              )}
            />
          )}
        </ScatterChart>
      </ResponsiveContainer>

      {/* Force de la relation + garde-fous */}
      <p className="text-sm text-gray-600 mt-1">
        La droite est le pronostic : à {lower(xLabel)} donné, le {motSing} « attendu ». Cette
        relation rend compte de <strong>{r2pct} %</strong> de la variation (R² = {model.r2.toFixed(2)}).
        {faible && ' Relation faible : les écarts sont à lire avec prudence.'}
      </p>
      <p className="text-xs text-gray-400 mt-1">
        Lecture au niveau {motSing} : un écart agrégé ne dit rien des individus. Les outsiders
        changent avec la maille (départements, intercommunalités, communes), c'est attendu.
      </p>

      {/* Phrases de lecture, strictement descriptives */}
      <div className="grid sm:grid-cols-2 gap-3 mt-4">
        <div className="bg-emerald-50 border border-emerald-100 rounded-xl p-4 text-sm text-emerald-900">
          <Reading p={positifs[0]} xLabel={xLabel} yLabel={yLabel} yFmt={yFmt} sens="pos" />
        </div>
        <div className="bg-red-50 border border-red-100 rounded-xl p-4 text-sm text-red-900">
          <Reading p={negatifs[0]} xLabel={xLabel} yLabel={yLabel} yFmt={yFmt} sens="neg" />
        </div>
      </div>

      {/* Listes d'outsiders, reliées à la carte (survol) et à la fiche (clic) */}
      <div className="grid sm:grid-cols-2 gap-6 mt-5">
        <OutList
          titre={`Au-dessus du pronostic`}
          sous={`${yLabel} plus fort qu'attendu`}
          items={positifs}
          color="#059669"
          yFmt={yFmt}
          onHover={setH}
          onSelect={onSelect}
        />
        <OutList
          titre={`En dessous du pronostic`}
          sous={`${yLabel} plus faible qu'attendu`}
          items={negatifs}
          color="#dc2626"
          yFmt={yFmt}
          onHover={setH}
          onSelect={onSelect}
        />
      </div>
    </div>
  )
}

function OutList({ titre, sous, items, color, yFmt, onHover, onSelect }) {
  return (
    <div onMouseLeave={() => onHover && onHover(null)}>
      <div className="font-semibold text-gray-900" style={{ color }}>{titre}</div>
      <div className="text-xs text-gray-400 mb-2">{sous}</div>
      <div className="space-y-1">
        {items.map((p) => {
          const clickable = !!onSelect
          return (
            <div
              key={p.code}
              onMouseEnter={() => onHover && onHover(p.code)}
              onClick={() => clickable && onSelect(p.code)}
              className={`flex items-center justify-between gap-2 rounded-lg px-2.5 py-1.5 border border-transparent hover:border-gray-200 hover:bg-gray-50 ${
                clickable ? 'cursor-pointer' : ''
              }`}
              title={clickable ? 'Voir la fiche du territoire' : undefined}
            >
              <span className="text-sm text-gray-700 truncate">{p.nom}</span>
              <span className="shrink-0 flex items-center gap-2">
                <span className="text-xs text-gray-400">{yFmt ? yFmt(p.y) : p.y}</span>
                <span
                  className="text-xs font-semibold px-1.5 py-0.5 rounded"
                  style={{ color, backgroundColor: `${color}14` }}
                >
                  {sigma(p.t)}
                </span>
              </span>
            </div>
          )
        })}
        {!items.length && <div className="text-sm text-gray-400">Aucun écart marqué.</div>}
      </div>
    </div>
  )
}
