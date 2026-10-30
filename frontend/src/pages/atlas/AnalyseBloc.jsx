import { useState } from 'react'
import { Code2, Check } from 'lucide-react'
import OutsidersScatter from '../../components/charts/OutsidersScatter'
import { INDICATEURS } from '../../config/indicateurs'
import { titleCase } from '../../lib/territoire'
import { trackEvent } from '../../lib/analytics'

function Classement({ titre, items, max, fmt, color }) {
  return (
    <div className="bg-white border border-gray-200 rounded-xl p-5">
      <h3 className="font-semibold text-gray-900 mb-3">{titre}</h3>
      <div className="space-y-1.5">
        {items.map((r) => (
          <div key={r.code} className="flex items-center gap-3">
            <div className="w-40 shrink-0 text-sm text-gray-700 truncate">{titleCase(r.nom)}</div>
            <div className="flex-1 h-3 bg-gray-100 rounded-full overflow-hidden">
              <div
                className="h-full rounded-full"
                style={{ width: `${Math.max(3, (r.v / max) * 100)}%`, backgroundColor: color }}
              />
            </div>
            <div className="w-24 shrink-0 text-right text-sm font-semibold text-gray-800">{fmt(r.v)}</div>
          </div>
        ))}
      </div>
    </div>
  )
}

/**
 * Analyse modulaire d'un indicateur, à la maille courante (départements OU communes
 * du département drillé), + croisement optionnel avec un autre indicateur.
 */
export default function AnalyseBloc({
  records,
  ind,
  vsInd,
  onSetVs,
  level = 'dept',
  niveauNom = 'France',
  onHoverOutsider = null,
  onSelectOutsider = null,
}) {
  const [embedded, setEmbedded] = useState(false)
  const keyOf = (i) => (level === 'commune' ? i.communeKey : i.deptKey)
  const mot = level === 'commune' ? 'communes' : level === 'epci' ? 'intercommunalités' : 'départements'
  const k = keyOf(ind)
  // Indicateurs disponibles à cette maille, seuls proposés au croisement.
  const croisables = INDICATEURS.filter(
    (i) => i.id !== ind.id && (level === 'commune' ? i.communeKey : level === 'epci' ? i.epci : true),
  )

  const recs = records
    .filter((d) => d[k] != null)
    .map((d) => ({ nom: d.nom || d.dep, code: d.code, v: d[k] }))
  if (!recs.length) return null

  const sorted = [...recs].sort((a, b) => b.v - a.v)
  const vals = recs.map((r) => r.v).sort((a, b) => a - b)
  const median = vals[Math.floor(vals.length / 2)]
  const max = Math.max(...vals)

  // Code d'intégration (iframe) du nuage de croisement, pour les mailles dept/EPCI.
  const copyEmbed = () => {
    const q = new URLSearchParams({ i: ind.id, vs: vsInd.id })
    if (level === 'epci') q.set('level', 'epci')
    const src = `${window.location.origin}/embed/croisement?${q.toString()}`
    trackEvent(`integrer-graphique/${ind.id}/${vsInd.id}`, 'Intégrer un nuage de croisement')
    const code = `<iframe src="${src}" width="100%" height="720" style="border:0;border-radius:12px" loading="lazy" title="Outsiders, ${ind.label} selon ${vsInd.label}"></iframe>`
    navigator.clipboard?.writeText(code).then(() => {
      setEmbedded(true)
      setTimeout(() => setEmbedded(false), 1800)
    })
  }

  const vk = vsInd ? keyOf(vsInd) : null
  const comparePoints =
    vsInd && vk
      ? records
          .filter((d) => d[k] != null && d[vk] != null)
          .map((d) => ({
            code: d.code,
            nom: titleCase(d.nom || d.dep),
            x: d[vk],
            y: d[k],
            pop: d.pop ?? null,
          }))
      : []

  return (
    <section className="max-w-5xl mx-auto px-4 mt-12">
      <h2 className="text-2xl font-bold text-gray-900 mb-1">{ind.label} : en bref</h2>
      <p className="text-sm text-gray-400 mb-1">
        Vue : {niveauNom} · {recs.length} {mot} renseignés
      </p>
      <p className="text-gray-600 mb-6 max-w-3xl">{ind.aide}</p>

      <div className="flex flex-wrap gap-4 mb-8">
        <div className="bg-gray-50 border border-gray-200 rounded-xl px-5 py-3">
          <div className="text-2xl font-bold" style={{ color: ind.couleur }}>
            {ind.fmt(median)}
          </div>
          <div className="text-xs text-gray-500">médiane des {mot}</div>
        </div>
      </div>

      {/* Croisement avec un autre indicateur (à la même maille) */}
      <div className="mb-10">
        <h3 className="font-semibold text-gray-900 mb-1">Croiser avec un autre indicateur</h3>
        <p className="text-sm text-gray-500 mb-2 max-w-3xl">
          La droite donne le pronostic : la valeur « attendue » d'un territoire vu l'autre
          indicateur. Les outsiders sont ceux qui s'en écartent le plus, au-dessus ou en dessous.
        </p>
        <div className="flex flex-wrap gap-2 mb-4">
          {croisables.map((i) => {
            const active = vsInd?.id === i.id
            return (
              <button
                key={i.id}
                onClick={() => onSetVs(active ? null : i.id)}
                className="px-3 py-1.5 rounded-full text-sm font-medium border transition-colors"
                style={
                  active
                    ? { backgroundColor: i.couleur, borderColor: i.couleur, color: '#fff' }
                    : { borderColor: '#e5e7eb', color: '#4b5563' }
                }
              >
                {i.label}
              </button>
            )
          })}
        </div>
        {vsInd && comparePoints.length > 4 && (
          <div className="bg-white border border-gray-200 rounded-xl p-6">
            {level !== 'commune' && (
              <div className="flex justify-end -mt-2 mb-1">
                <button
                  onClick={copyEmbed}
                  className="inline-flex items-center gap-1.5 text-xs text-gray-400 hover:text-gray-700"
                  title="Copier le code pour intégrer ce graphique sur un autre site"
                >
                  {embedded ? <Check size={13} className="text-emerald-600" /> : <Code2 size={13} />}
                  {embedded ? 'Code copié' : 'Intégrer ce graphique'}
                </button>
              </div>
            )}
            <OutsidersScatter
              points={comparePoints}
              xLabel={vsInd.label}
              xUnit={vsInd.unite}
              xFmt={vsInd.fmt}
              yLabel={ind.label}
              yUnit={ind.unite}
              yFmt={ind.fmt}
              level={level}
              onHover={onHoverOutsider}
              onSelect={onSelectOutsider}
            />
          </div>
        )}
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <Classement titre={`Les 5 ${mot} les plus élevés`} items={sorted.slice(0, 5)} max={max} fmt={ind.fmt} color={ind.couleur} />
        <Classement titre={`Les 5 ${mot} les plus bas`} items={sorted.slice(-5).reverse()} max={max} fmt={ind.fmt} color={ind.couleur} />
      </div>

      <p className="text-xs text-gray-400 mt-4">
        Source :{' '}
        {ind.sourceUrl ? (
          <a href={ind.sourceUrl} target="_blank" rel="noopener noreferrer" className="underline hover:text-gray-600">
            {ind.source}
          </a>
        ) : (
          ind.source
        )}
        .
      </p>
    </section>
  )
}
