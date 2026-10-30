import { useEffect, useMemo, useState } from 'react'
import { useParams, useSearchParams } from 'react-router-dom'
import { Loader2 } from 'lucide-react'
import { INDICATEUR_BY_ID, DEFAULT_INDICATEUR } from '../../config/indicateurs'
import ChoroplethMap from '../../components/charts/ChoroplethMap'
import OutsidersScatter from '../../components/charts/OutsidersScatter'
import { titleCase } from '../../lib/territoire'

const Spin = () => (
  <div className="h-full flex items-center justify-center text-gray-400">
    <Loader2 className="animate-spin" size={22} />
  </div>
)

// Cadre commun : titre, viz, et barre d'attribution (source + lien vers le site).
// Cohérent CC BY et anonymat : on cite la source d'origine et « Outsiders », jamais une personne.
function Frame({ title, color, sourceNode, fullHref, scroll = false, children }) {
  return (
    <div className="h-screen flex flex-col bg-white">
      <div className="px-3 py-2 border-b border-gray-200 shrink-0">
        <div className="text-sm font-bold leading-tight" style={{ color }}>{title}</div>
      </div>
      <div className={`flex-1 min-h-0 p-2 ${scroll ? 'overflow-auto' : ''}`}>{children}</div>
      <div className="px-3 py-1.5 border-t border-gray-200 text-[11px] text-gray-500 flex items-center justify-between gap-3 shrink-0">
        <span className="truncate">Source : {sourceNode}</span>
        <a href={fullHref} target="_blank" rel="noopener noreferrer" className="font-semibold text-gray-700 hover:underline shrink-0">
          via Outsiders ↗
        </a>
      </div>
    </div>
  )
}

function SourceLink({ ind }) {
  if (!ind) return null
  return ind.sourceUrl ? (
    <a href={ind.sourceUrl} target="_blank" rel="noopener noreferrer" className="underline hover:text-gray-700">{ind.source}</a>
  ) : (
    <span>{ind.source}</span>
  )
}

// ── Embed carte : choroplèthe (départements / EPCI / communes d'un département) ──
function EmbedCarte({ params }) {
  const ind = INDICATEUR_BY_ID[params.get('i')] || INDICATEUR_BY_ID[DEFAULT_INDICATEUR]
  const m = params.get('m') || 'dept'
  const dep = params.get('dep')
  const [geo, setGeo] = useState(null)
  const [valueByCode, setValueByCode] = useState(null)

  useEffect(() => {
    let alive = true
    const ok = (g, v) => { if (alive) { setGeo(g); setValueByCode(v) } }
    const fromList = (rows, key) =>
      Object.fromEntries(rows.filter((r) => r[key] != null).map((r) => [r.code, r[key]]))
    async function run() {
      if (dep) {
        const [g, v] = await Promise.all([
          fetch(`https://geo.api.gouv.fr/departements/${dep}/communes?format=geojson&geometry=contour`).then((r) => r.json()),
          fetch(`/data/atlas/communes/${dep}.json`).then((r) => (r.ok ? r.json() : {})),
        ])
        ok(g, Object.fromEntries(Object.entries(v).filter(([, x]) => x[ind.communeKey] != null).map(([c, x]) => [c, x[ind.communeKey]])))
      } else if (m === 'epci') {
        const [d, g] = await Promise.all([
          fetch('/data/atlas/epci.json').then((r) => r.json()),
          fetch('/data/geo/epci.geojson').then((r) => r.json()),
        ])
        ok(g, fromList(d, ind.deptKey))
      } else {
        const [d, g] = await Promise.all([
          fetch('/data/atlas/departements.json').then((r) => r.json()),
          fetch('/data/geo/departements.geojson').then((r) => r.json()),
        ])
        ok(g, fromList(d, ind.deptKey))
      }
    }
    run().catch(() => {})
    return () => { alive = false }
  }, [ind, m, dep])

  const fullHref = `/atlas?i=${ind.id}${m !== 'dept' && !dep ? `&m=${m}` : ''}${dep ? `&dep=${dep}` : ''}`
  return (
    <Frame title={ind.label} color={ind.couleur} sourceNode={<SourceLink ind={ind} />} fullHref={fullHref}>
      {geo && valueByCode ? (
        <ChoroplethMap geo={geo} valueByCode={valueByCode} label={ind.label} unit={ind.unite} format={ind.fmt} height="100%" fitBounds={!!dep} />
      ) : (
        <Spin />
      )}
    </Frame>
  )
}

// ── Embed croisement : nuage « outsiders » (écart au pronostic) ──
function EmbedCroisement({ params }) {
  const ind = INDICATEUR_BY_ID[params.get('i')] || INDICATEUR_BY_ID[DEFAULT_INDICATEUR]
  const vs = INDICATEUR_BY_ID[params.get('vs')]
  const level = params.get('level') === 'epci' ? 'epci' : 'dept'
  const [records, setRecords] = useState(null)

  useEffect(() => {
    const url = level === 'epci' ? '/data/atlas/epci.json' : '/data/atlas/departements.json'
    fetch(url).then((r) => r.json()).then(setRecords).catch(() => setRecords([]))
  }, [level])

  const points = useMemo(() => {
    if (!records || !vs) return []
    const k = ind.deptKey
    const vk = vs.deptKey
    return records
      .filter((d) => d[k] != null && d[vk] != null)
      .map((d) => ({ code: d.code, nom: titleCase(d.nom || d.dep), x: d[vk], y: d[k], pop: d.pop ?? null }))
  }, [records, ind, vs, level])

  const fullHref = `/atlas?i=${ind.id}${vs ? `&vs=${vs.id}` : ''}${level === 'epci' ? '&m=epci' : ''}`
  const openFiche = (code) => window.open(`/territoires?code=${code}`, '_blank', 'noopener')
  const sourceNode = (
    <>
      <SourceLink ind={ind} />{vs && vs.sourceUrl !== ind.sourceUrl ? <> et <SourceLink ind={vs} /></> : null}
    </>
  )

  return (
    <Frame title={vs ? `${ind.label} selon ${vs.label}` : ind.label} color={ind.couleur} sourceNode={sourceNode} fullHref={fullHref} scroll>
      {!records ? (
        <Spin />
      ) : vs && points.length > 4 ? (
        <OutsidersScatter
          points={points}
          xLabel={vs.label}
          xUnit={vs.unite}
          xFmt={vs.fmt}
          yLabel={ind.label}
          yUnit={ind.unite}
          yFmt={ind.fmt}
          level={level}
          onHover={null}
          onSelect={openFiche}
        />
      ) : (
        <div className="text-sm text-gray-500 p-4">Indicateur de croisement manquant ou données insuffisantes.</div>
      )}
    </Frame>
  )
}

export default function Embed() {
  const { type } = useParams()
  const [params] = useSearchParams()
  if (type === 'carte') return <EmbedCarte params={params} />
  if (type === 'croisement') return <EmbedCroisement params={params} />
  return <div className="p-6 text-gray-500">Type d'intégration inconnu.</div>
}
