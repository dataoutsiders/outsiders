import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  Tooltip,
  ReferenceLine,
  ResponsiveContainer,
  Cell,
} from 'recharts'
import { ols } from '../../lib/residuals'

const COLOR = { 'triple-bas': '#EF4444', 'triple-haut': '#10B981', mixte: '#9CA3AF' }

// Ajustement OLS partagé (lib/residuals) ; la corrélation se déduit de R².
function fit(points) {
  const m = ols(points)
  if (!m) return null
  return { a: m.a, b: m.b, corr: Math.sign(m.b) * Math.sqrt(m.r2) }
}

function Dot({ label, x, y, xUnit }) {
  return (
    <div className="bg-gray-900 text-white text-xs rounded-lg px-2.5 py-1.5">
      <div className="font-semibold">{label}</div>
      <div>IPS {y}</div>
      <div>
        {x.toLocaleString('fr-FR')} {xUnit}
      </div>
    </div>
  )
}

/**
 * Nuage de points : un département = un point. x = revenu ou prix, y = IPS.
 * @param {Array<{x:number, y:number, label:string, cumul:string}>} points
 */
export default function CroisementScatter({ points, xLabel, xUnit, yLabel = 'IPS collège', note = null, height = 360 }) {
  const f = fit(points)
  const xs = points.map((p) => p.x)
  const x0 = Math.min(...xs)
  const x1 = Math.max(...xs)

  return (
    <div>
      <ResponsiveContainer width="100%" height={height}>
        <ScatterChart margin={{ top: 10, right: 20, bottom: 25, left: 10 }}>
          <XAxis
            type="number"
            dataKey="x"
            domain={['dataMin', 'dataMax']}
            tick={{ fontSize: 11 }}
            tickFormatter={(v) => (v >= 1000 ? `${Math.round(v / 1000)}k` : v)}
            label={{ value: xLabel, position: 'insideBottom', offset: -12, fontSize: 12 }}
          />
          <YAxis
            type="number"
            dataKey="y"
            domain={['dataMin - 2', 'dataMax + 2']}
            tick={{ fontSize: 11 }}
            label={{ value: yLabel, angle: -90, position: 'insideLeft', fontSize: 12 }}
          />
          <Tooltip
            cursor={{ strokeDasharray: '3 3' }}
            content={({ payload }) =>
              payload && payload[0] ? <Dot {...payload[0].payload} xUnit={xUnit} /> : null
            }
          />
          {f && (
            <ReferenceLine
              segment={[
                { x: x0, y: f.a + f.b * x0 },
                { x: x1, y: f.a + f.b * x1 },
              ]}
              stroke="#6b7280"
              strokeDasharray="5 5"
            />
          )}
          <Scatter data={points}>
            {points.map((p, i) => (
              <Cell key={i} fill={COLOR[p.cumul] || COLOR.mixte} fillOpacity={0.8} />
            ))}
          </Scatter>
        </ScatterChart>
      </ResponsiveContainer>
      {f && (
        <p className="text-sm text-gray-500 text-center -mt-2">
          Corrélation : <strong>{f.corr.toFixed(2)}</strong>, {' '}
          {note ||
            "l'école suit la richesse résidentielle sans la copier. Rouge = public modeste aux 3 étapes, vert = entre-soi."}
        </p>
      )}
    </div>
  )
}
