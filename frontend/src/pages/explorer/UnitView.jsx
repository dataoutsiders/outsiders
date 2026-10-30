import { useEffect, useState, Fragment } from 'react'
import { Link, useNavigate, useParams, useSearchParams } from 'react-router-dom'
import { Loader2, ArrowLeft, ArrowRight } from 'lucide-react'
import ExplorerBar from '../../components/ExplorerBar'
import ToneCallout from '../../components/ToneCallout'
import { DECOUPAGE_BY_ID } from '../../config/decoupages'
import { useRouteMeta } from '../../lib/meta'

// ───────────────────────── Helpers ─────────────────────────
function extent(categories, indId) {
  const vals = categories.map((c) => c.valeurs[indId]).filter((v) => v != null)
  if (!vals.length) return null
  return { min: Math.min(...vals), max: Math.max(...vals) }
}
const normPos = (v, ex) => (ex && ex.max !== ex.min ? (v - ex.min) / (ex.max - ex.min) : 0.5)
const posInRange = (v, ex) => normPos(v, ex) * 100

// Couleur de fond d'une cellule. Indicateurs de bien-être (sens haut/bas) : rouge (défavorable)
// vers vert (favorable). Indicateurs de comportement (sens neutre) : dégradé bleu, faible vers fort.
function cellColor(v, ex, ind) {
  if (v == null) return '#f3f4f6'
  const n = normPos(v, ex)
  if (ind.sens === 'neutre') return `hsl(211, 65%, ${Math.round(92 - n * 24)}%)`
  const fav = ind.sens === 'bas' ? 1 - n : n
  return `hsl(${Math.round(fav * 135)}, 70%, 90%)`
}

// Rapport max/min d'un indicateur (intensité de l'écart), unit-safe.
function ratioOf(categories, indId) {
  const vals = categories.map((c) => c.valeurs[indId]).filter((v) => v != null && v > 0)
  if (vals.length < 2) return 1
  return Math.max(...vals) / Math.min(...vals)
}
const fmtRatio = (r) => '×' + r.toLocaleString('fr-FR', { maximumFractionDigits: r >= 2 ? 1 : 2 })

// Regroupe les indicateurs par thème, en préservant l'ordre d'apparition.
function byTheme(indicateurs) {
  const groups = []
  for (const ind of indicateurs) {
    const t = ind.theme || ''
    let g = groups.find((x) => x.theme === t)
    if (!g) { g = { theme: t, items: [] }; groups.push(g) }
    g.items.push(ind)
  }
  return groups
}

// Numérote les sources uniques (par lien) pour les notes de bas de page.
function buildRefs(d, data) {
  const sources = data.sources || {}
  const refs = []
  const numByUrl = {}
  for (const ind of d.indicateurs) {
    const s = sources[ind.id]
    if (s && s.url && numByUrl[s.url] == null) {
      numByUrl[s.url] = refs.length + 1
      refs.push({ num: refs.length + 1, ...s })
    }
  }
  const numOf = (indId) => {
    const s = sources[indId]
    return s && s.url ? numByUrl[s.url] : null
  }
  return { refs, numOf }
}

// Note de bas de page (numéro en exposant qui renvoie à la bibliographie).
function Fn({ n }) {
  if (!n) return null
  return (
    <sup className="ml-0.5 text-[10px] font-semibold">
      <a href={`#src-${n}`} className="text-blue-600 hover:underline">{n}</a>
    </sup>
  )
}

// Bibliographie : citation complète + lien, par numéro.
function RefsList({ refs }) {
  if (!refs.length) return null
  return (
    <ol className="text-xs text-gray-500 space-y-1.5 mt-6 border-t border-gray-100 pt-4">
      {refs.map((r) => (
        <li key={r.num} id={`src-${r.num}`} className="flex gap-2 scroll-mt-24">
          <span className="font-semibold text-gray-600 shrink-0">{r.num}.</span>
          <span>
            {r.full || r.label}{' '}
            <a href={r.url} target="_blank" rel="noopener noreferrer" className="underline hover:text-gray-700">
              Consulter la source
            </a>
          </span>
        </li>
      ))}
    </ol>
  )
}

// Texte d'écart d'un indicateur (sous la barre).
function ecartText(categories, ind) {
  const rows = categories.map((c) => ({ nom: c.nom, v: c.valeurs[ind.id] })).filter((r) => r.v != null)
  if (rows.length < 2) return null
  rows.sort((a, b) => b.v - a.v)
  const hi = rows[0], lo = rows[rows.length - 1]
  if (ind.sens === 'neutre')
    return (<>Le plus : <strong>{hi.nom}</strong> {ind.fmt(hi.v)} · le moins : <strong>{lo.nom}</strong> {ind.fmt(lo.v)}.</>)
  const fav = ind.sens === 'haut' ? hi : lo
  const def = ind.sens === 'haut' ? lo : hi
  return (<>Écart : <strong>{def.nom}</strong> {ind.fmt(def.v)} contre <strong>{fav.nom}</strong> {ind.fmt(fav.v)}.</>)
}

// Barre proportionnelle à la valeur (départ à zéro), pour ne pas exagérer les écarts.
function CompareRow({ nom, couleur, v, max, fmt }) {
  const w = v == null || !max ? 0 : Math.max(2, (v / max) * 100)
  return (
    <div className="flex items-center gap-3 py-1">
      <div className="w-52 shrink-0 text-sm text-gray-700 truncate" title={nom}>{nom}</div>
      <div className="flex-1 h-3.5 bg-gray-100 rounded-full overflow-hidden">
        {v != null && <div className="h-full rounded-full" style={{ width: `${w}%`, backgroundColor: couleur }} />}
      </div>
      <div className="w-24 shrink-0 text-right text-sm font-semibold text-gray-800">{v == null ? 'n/d' : fmt(v)}</div>
    </div>
  )
}

// ───────────────────────── Tableau coloré (heatmap) ─────────────────────────
function HeatmapTable({ d, data, refs, numOf }) {
  const { categories } = data
  const [sortCol, setSortCol] = useState(null) // id de catégorie, ou null = tri par écart
  const groups = byTheme(d.indicateurs)
  const sortGroup = (items) =>
    [...items].sort((a, b) => {
      if (!sortCol) return ratioOf(categories, b.id) - ratioOf(categories, a.id)
      const cat = categories.find((c) => c.id === sortCol)
      return normPos(cat.valeurs[b.id], extent(categories, b.id)) - normPos(cat.valeurs[a.id], extent(categories, a.id))
    })
  const th = 'px-2 py-1.5 text-xs font-semibold'

  return (
    <div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm border-separate" style={{ borderSpacing: '3px 4px' }}>
          <thead>
            <tr>
              <th className={`${th} text-left text-gray-500`}>Indicateur</th>
              {categories.map((c) => (
                <th key={c.id} className={`${th} text-center`}>
                  <button
                    onClick={() => setSortCol(sortCol === c.id ? null : c.id)}
                    className={sortCol === c.id ? 'text-blue-600' : 'text-gray-600 hover:text-blue-600'}
                  >
                    {c.nom}{sortCol === c.id ? ' ↓' : ''}
                  </button>
                </th>
              ))}
              <th className={`${th} text-center`}>
                <button
                  onClick={() => setSortCol(null)}
                  className={!sortCol ? 'text-blue-600' : 'text-gray-600 hover:text-blue-600'}
                  title="Rapport entre la valeur la plus forte et la plus faible"
                >
                  Écart{!sortCol ? ' ↓' : ''}
                </button>
              </th>
            </tr>
          </thead>
          <tbody>
            {groups.map((g) => (
              <Fragment key={g.theme || 'sans-theme'}>
                {g.theme && (
                  <tr>
                    <td colSpan={categories.length + 2} className="pt-3 pb-0.5 px-2 text-[11px] font-semibold uppercase tracking-wide text-gray-400">
                      {g.theme}
                    </td>
                  </tr>
                )}
                {sortGroup(g.items).map((ind) => {
                  const ex = extent(categories, ind.id)
                  return (
                    <tr key={ind.id}>
                      <td className="px-2 py-2 text-gray-800 font-medium" title={ind.aide}>
                        {ind.label}<Fn n={numOf(ind.id)} />
                      </td>
                      {categories.map((c) => {
                        const v = c.valeurs[ind.id]
                        return (
                          <td key={c.id} className="px-2 py-2 text-center font-semibold text-gray-800 rounded" style={{ backgroundColor: cellColor(v, ex, ind) }}>
                            {v == null ? 'n/d' : ind.fmt(v)}
                          </td>
                        )
                      })}
                      <td className="px-2 py-2 text-center text-gray-500 whitespace-nowrap">{fmtRatio(ratioOf(categories, ind.id))}</td>
                    </tr>
                  )
                })}
              </Fragment>
            ))}
          </tbody>
        </table>
      </div>
      <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-gray-400 mt-3">
        <span className="inline-flex items-center gap-1"><span className="w-3 h-3 rounded" style={{ backgroundColor: 'hsl(135,70%,90%)' }} /> favorable</span>
        <span className="inline-flex items-center gap-1"><span className="w-3 h-3 rounded" style={{ backgroundColor: 'hsl(0,70%,90%)' }} /> défavorable</span>
        <span className="inline-flex items-center gap-1"><span className="w-3 h-3 rounded" style={{ backgroundColor: 'hsl(211,65%,80%)' }} /> comportement (faible → fort)</span>
        <span>· couleur par ligne · « Écart » = rapport max/min · cliquez une colonne pour trier</span>
      </div>
      <RefsList refs={refs} />
    </div>
  )
}

// ─────────────── Classement (beaucoup de catégories : ex. pays) ───────────────
// Percentile favorable de la catégorie repère sur un indicateur : 0 = la mieux placée,
// 1 = la moins bien. null pour les indicateurs de comportement (sens neutre).
function positionRepere(categories, ind, repereId) {
  if (ind.sens === 'neutre') return null
  const vals = categories.map((c) => ({ id: c.id, v: c.valeurs[ind.id] })).filter((x) => x.v != null)
  if (vals.length < 2) return null
  vals.sort((a, b) => (ind.sens === 'haut' ? b.v - a.v : a.v - b.v))
  const i = vals.findIndex((x) => x.id === repereId)
  return i < 0 ? null : i / (vals.length - 1)
}

// Catégories en lignes (triables par indicateur), indicateurs sélectionnés en colonnes.
// Le clic sur une ligne ouvre la fiche ; la catégorie repère est surlignée.
function ClassementTable({ d, data, inds, numOf }) {
  const navigate = useNavigate()
  const { categories, references = {} } = data
  const [sortState, setSortState] = useState({ id: null, asc: false })
  const sortInd = inds.find((i) => i.id === sortState.id) || inds[0]
  if (!sortInd) return null

  // Tri : par défaut le meilleur d'abord (sens favorable), valeur haute d'abord si neutre.
  const dirBase = sortInd.sens === 'bas' ? 1 : -1
  const dir = sortState.asc ? -dirBase : dirBase
  const rows = [...categories].sort((a, b) => {
    const va = a.valeurs[sortInd.id], vb = b.valeurs[sortInd.id]
    if (va == null && vb == null) return 0
    if (va == null) return 1
    if (vb == null) return -1
    return (va - vb) * dir
  })
  const hasRef = Object.keys(references).length > 0 && inds.some((i) => references[i.id] != null)

  const clickCol = (id) =>
    setSortState((s) => (s.id === id || (!s.id && id === inds[0].id) ? { id, asc: !s.asc } : { id, asc: false }))

  return (
    <div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm border-separate" style={{ borderSpacing: '3px 3px' }}>
          <thead>
            <tr>
              <th className="px-2 py-1.5 text-xs font-semibold text-gray-400 text-right">n°</th>
              <th className="px-2 py-1.5 text-xs font-semibold text-gray-500 text-left">{d.rowLabel[0].toUpperCase() + d.rowLabel.slice(1)}</th>
              {inds.map((ind) => {
                const active = ind.id === sortInd.id
                return (
                  <th key={ind.id} className="px-2 py-1.5 text-xs font-semibold text-center">
                    <button
                      onClick={() => clickCol(ind.id)}
                      title={`${ind.label}. ${ind.aide || ''}`}
                      className={active ? 'text-blue-600' : 'text-gray-600 hover:text-blue-600'}
                    >
                      {ind.court || ind.label}
                      <Fn n={numOf(ind.id)} />
                      {active ? (sortState.asc ? ' ↑' : ' ↓') : ''}
                    </button>
                  </th>
                )
              })}
            </tr>
          </thead>
          <tbody>
            {hasRef && (
              <tr className="text-gray-500 italic">
                <td className="px-2 py-1.5 text-right">·</td>
                <td className="px-2 py-1.5">{d.referenceLabel || 'Ensemble'}</td>
                {inds.map((ind) => (
                  <td key={ind.id} className="px-2 py-1.5 text-center bg-gray-50 rounded">
                    {references[ind.id] == null ? 'n/d' : ind.fmt(references[ind.id])}
                  </td>
                ))}
              </tr>
            )}
            {rows.map((c, i) => {
              const repere = c.id === d.categorieRepere
              return (
                <tr
                  key={c.id}
                  onClick={() => navigate(`${d.route}?cat=${c.id}`)}
                  className={`cursor-pointer transition-colors ${repere ? 'font-bold' : 'hover:bg-gray-50'}`}
                >
                  <td className="px-2 py-1.5 text-right text-gray-400">{i + 1}</td>
                  <td className={`px-2 py-1.5 whitespace-nowrap ${repere ? 'text-blue-700' : 'text-gray-800'}`}>
                    <Link to={`${d.route}?cat=${c.id}`} onClick={(e) => e.stopPropagation()} className="hover:underline">
                      {c.nom}
                    </Link>
                  </td>
                  {inds.map((ind) => {
                    const ex = extent(categories, ind.id)
                    const v = c.valeurs[ind.id]
                    return (
                      <td
                        key={ind.id}
                        className={`px-2 py-1.5 text-center rounded ${repere ? 'ring-2 ring-blue-400 ring-inset' : ''}`}
                        style={{ backgroundColor: cellColor(v, ex, ind) }}
                      >
                        {v == null ? 'n/d' : ind.fmt(v)}
                      </td>
                    )
                  })}
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
      <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-gray-400 mt-3">
        <span className="inline-flex items-center gap-1"><span className="w-3 h-3 rounded" style={{ backgroundColor: 'hsl(135,70%,90%)' }} /> favorable</span>
        <span className="inline-flex items-center gap-1"><span className="w-3 h-3 rounded" style={{ backgroundColor: 'hsl(0,70%,90%)' }} /> défavorable</span>
        <span className="inline-flex items-center gap-1"><span className="w-3 h-3 rounded" style={{ backgroundColor: 'hsl(211,65%,80%)' }} /> descriptif (faible → fort)</span>
        <span>· couleur par colonne · le n° suit la colonne triée (meilleur en tête) · cliquez un en-tête pour trier, un {d.rowLabel} pour sa fiche</span>
      </div>
    </div>
  )
}

// ───────────────────────── Tableau de bord d'une unité ─────────────────────────
function UnitDashboard({ d, data }) {
  const { categories, references = {} } = data
  const { refs, numOf } = buildRefs(d, data)
  const [vue, setVue] = useState('tableau')

  // Mode classement (beaucoup de catégories) : quelques indicateurs à la fois, pour un
  // tableau lisible sans défilement, avec présélections selon la position du repère.
  const classement = !!d.tableauClassement
  const [selIds, setSelIds] = useState(
    () => d.indicateursDefaut || d.indicateurs.slice(0, 4).map((i) => i.id),
  )
  const indsActifs = classement ? d.indicateurs.filter((i) => selIds.includes(i.id)) : d.indicateurs
  const toggleInd = (id) =>
    setSelIds((s) => (s.includes(id) ? (s.length > 1 ? s.filter((x) => x !== id) : s) : [...s, id]))

  const repereNom = classement ? categories.find((c) => c.id === d.categorieRepere)?.nom : null
  const presets = (() => {
    if (!classement || !d.categorieRepere) return []
    const forte = [], moyenne = [], faible = []
    for (const ind of d.indicateurs) {
      const p = positionRepere(categories, ind, d.categorieRepere)
      if (p == null) continue
      if (p <= 0.34) forte.push(ind.id)
      else if (p >= 0.66) faible.push(ind.id)
      else moyenne.push(ind.id)
    }
    const tous = d.indicateurs.map((i) => i.id)
    return [
      { label: 'forte', ids: forte },
      { label: 'moyenne', ids: moyenne },
      { label: 'faible', ids: faible },
      { label: 'tout voir', ids: tous },
    ].filter((p) => p.ids.length)
  })()
  const memesIds = (a, b) => a.length === b.length && a.every((x) => b.includes(x))

  return (
    <div className="max-w-4xl mx-auto px-4 py-10">
      <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-2">{d.titre}</h1>
      {d.intro && <p className="text-lg text-gray-600 mb-6 max-w-2xl">{d.intro}</p>}

      {!classement && (
        <div className="flex flex-wrap gap-2 mb-8">
          <span className="text-sm text-gray-400 self-center mr-1">Fiche par {d.rowLabel} :</span>
          {categories.map((c) => (
            <Link key={c.id} to={`${d.route}?cat=${c.id}`} className="px-3 py-1.5 rounded-full text-sm font-medium border border-gray-200 text-gray-700 hover:border-blue-300 hover:text-blue-700">
              {c.nom}
            </Link>
          ))}
        </div>
      )}

      {classement && (
        <div className="mb-6 space-y-3">
          {presets.length > 0 && repereNom && (
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-sm text-gray-500">Voir où {repereNom} est :</span>
              {presets.map((p) => (
                <button
                  key={p.label}
                  onClick={() => setSelIds(p.ids)}
                  className={`px-3 py-1 rounded-full text-sm font-medium border transition-colors ${
                    memesIds(selIds, p.ids)
                      ? 'bg-blue-600 border-blue-600 text-white'
                      : 'border-gray-200 text-gray-600 hover:border-blue-300 hover:text-blue-700'
                  }`}
                >
                  {p.label}
                </button>
              ))}
            </div>
          )}
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-sm text-gray-500">Indicateurs :</span>
            {d.indicateurs.map((ind) => {
              const on = selIds.includes(ind.id)
              return (
                <button
                  key={ind.id}
                  onClick={() => toggleInd(ind.id)}
                  title={ind.aide}
                  className={`px-3 py-1 rounded-full text-sm border transition-colors ${
                    on ? 'bg-gray-800 border-gray-800 text-white' : 'border-gray-200 text-gray-500 hover:border-gray-400'
                  }`}
                >
                  {ind.court || ind.label}
                </button>
              )
            })}
          </div>
          <p className="text-xs text-gray-400">
            Peu d'indicateurs à la fois = un classement lisible. Cliquez un {d.rowLabel} pour ouvrir sa fiche complète.
          </p>
        </div>
      )}

      <div className="inline-flex rounded-lg border border-gray-200 overflow-hidden mb-6 text-sm">
        {[['tableau', 'Tableau'], ['barres', 'Barres']].map(([v, lab]) => (
          <button key={v} onClick={() => setVue(v)} className={`px-4 py-1.5 transition-colors ${vue === v ? 'bg-blue-600 text-white font-medium' : 'bg-white text-gray-600 hover:bg-gray-50'}`}>
            {lab}
          </button>
        ))}
      </div>

      {vue === 'tableau' && classement && (
        <>
          <ClassementTable d={d} data={data} inds={indsActifs} numOf={numOf} />
          <RefsList refs={refs} />
        </>
      )}
      {vue === 'tableau' && !classement && <HeatmapTable d={d} data={data} refs={refs} numOf={numOf} />}

      {vue === 'barres' && (
        <>
          <p className="text-xs text-gray-400 mb-4">
            Barres proportionnelles à la valeur (départ à zéro), triées de la plus haute à la plus basse :
            un petit écart reste un petit écart. La différence exacte est écrite sous chaque indicateur.
          </p>
          {byTheme(indsActifs).map((g) => (
            <div key={g.theme || 'sans-theme'} className="mb-8">
              {g.theme && <h3 className="text-xs font-semibold uppercase tracking-wide text-gray-400 mb-2">{g.theme}</h3>}
              <div className="space-y-6">
                {g.items.map((ind) => {
                  const ex = extent(categories, ind.id)
                  const sorted = [...categories].sort((a, b) => (b.valeurs[ind.id] ?? -Infinity) - (a.valeurs[ind.id] ?? -Infinity))
                  const et = ecartText(categories, ind)
                  return (
                    <section key={ind.id} className="bg-white border border-gray-200 rounded-xl p-5">
                      <div className="flex items-baseline justify-between gap-3 mb-1">
                        <h2 className="text-lg font-bold text-gray-900">{ind.label}<Fn n={numOf(ind.id)} /></h2>
                        {references[ind.id] != null && <span className="text-xs text-gray-400 shrink-0">ensemble : {ind.fmt(references[ind.id])}</span>}
                      </div>
                      <p className="text-sm text-gray-500 mb-3">{ind.aide}</p>
                      <div className="space-y-0.5">
                        {sorted.map((c) => (
                          <CompareRow key={c.id} nom={c.nom} couleur={c.couleur} v={c.valeurs[ind.id]} max={ex ? ex.max : 0} fmt={ind.fmt} />
                        ))}
                      </div>
                      {et && <p className="text-sm text-gray-600 mt-3">{et}</p>}
                    </section>
                  )
                })}
              </div>
            </div>
          ))}
          <RefsList refs={refs} />
        </>
      )}
    </div>
  )
}

// ───────────────────────── Fiche d'une catégorie ─────────────────────────
function UnitFiche({ d, data, cat }) {
  const { categories } = data
  const { refs, numOf } = buildRefs(d, data)
  const c = categories.find((x) => x.id === cat)
  if (!c)
    return (
      <div className="py-20 text-center text-gray-500">
        Catégorie introuvable.{' '}
        <Link to={d.route} className="text-blue-600">Revenir au tableau de bord</Link>.
      </div>
    )

  // Extrêmes favorables / défavorables (indicateurs de bien-être uniquement, pas les comportements).
  const insights = (() => {
    const fav = [], def = []
    for (const ind of d.indicateurs) {
      if (ind.sens === 'neutre') continue
      const ex = extent(categories, ind.id)
      const v = c.valeurs[ind.id]
      if (v == null || !ex || ex.min === ex.max) continue
      const estMax = v === ex.max
      const estMin = v === ex.min
      if ((ind.sens === 'haut' && estMax) || (ind.sens === 'bas' && estMin)) fav.push(ind.label.toLowerCase())
      if ((ind.sens === 'haut' && estMin) || (ind.sens === 'bas' && estMax)) def.push(ind.label.toLowerCase())
    }
    const out = []
    if (def.length) out.push({ tone: 'warn', text: `Position la plus défavorable du panel sur : ${def.join(', ')}.` })
    if (fav.length) out.push({ tone: 'good', text: `Position la plus favorable du panel sur : ${fav.join(', ')}.` })
    return out
  })()

  const groups = byTheme(d.indicateurs)
  const nRenseignes = d.indicateurs.filter((ind) => c.valeurs[ind.id] != null).length

  return (
    <div className="max-w-4xl mx-auto px-4 py-10">
      <Link to={d.route} className="inline-flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-800 mb-4">
        <ArrowLeft size={15} /> {d.titre}
      </Link>
      <h1 className="text-3xl font-bold mb-1" style={{ color: c.couleur }}>{c.nom}</h1>
      <p className="text-gray-500 mb-8">
        {c.precision ? `${c.precision} · ` : ''}{nRenseignes} indicateurs, situés parmi les {d.rowLabelPluriel}
      </p>

      {insights.length > 0 && (
        <section className="mb-8 space-y-3">
          {insights.map((it, i) => (
            <ToneCallout key={i} tone={it.tone}>{it.text}</ToneCallout>
          ))}
        </section>
      )}

      {groups.map((g) => (
        <section key={g.theme || 'sans-theme'} className="mb-8">
          {g.theme && <h2 className="text-xs font-semibold uppercase tracking-wide text-gray-400 mb-2">{g.theme}</h2>}
          <div className="grid sm:grid-cols-2 gap-3">
            {g.items.map((ind) => {
              const ex = extent(categories, ind.id)
              const v = c.valeurs[ind.id]
              const detail = c.detail && c.detail[ind.id]
              const rows = categories.map((x) => x.valeurs[ind.id]).filter((x) => x != null).sort((a, b) => b - a)
              let rang = null
              if (v != null && rows.length) {
                if (v === ex.max) rang = 'la plus élevée'
                else if (v === ex.min) rang = 'la plus basse'
                else rang = `${rows.indexOf(v) + 1}ᵉ sur ${rows.length}`
              }
              return (
                <div key={ind.id} className="bg-white border border-gray-200 rounded-lg p-4">
                  <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0">
                      <div className="font-medium text-gray-900">{ind.label}<Fn n={numOf(ind.id)} /></div>
                      <div className="text-xs text-gray-500">{v == null ? 'non disponible' : rang}</div>
                    </div>
                    <div className="text-2xl font-bold shrink-0" style={{ color: v == null ? '#9CA3AF' : c.couleur }}>
                      {v == null ? 'n/d' : ind.fmt(v)}
                    </div>
                  </div>
                  {v != null && ex && (
                    <div className="relative h-2.5 rounded-full bg-gray-100 my-2">
                      <div
                        className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 w-3.5 h-3.5 rounded-full border-2 border-white shadow"
                        style={{ left: `${posInRange(v, ex)}%`, backgroundColor: c.couleur }}
                      />
                    </div>
                  )}
                  {detail && (
                    <div className="text-[11px] text-gray-500 mt-1">
                      {Object.entries(detail).map(([k, val]) => `${k} : ${ind.fmt(val)}`).join(' · ')}
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </section>
      ))}

      <div className="mb-8">
        <h2 className="text-sm font-semibold text-gray-700 mb-2">Comparer à :</h2>
        <div className="flex flex-wrap gap-2">
          {categories.filter((x) => x.id !== c.id).map((x) => (
            <Link key={x.id} to={`${d.route}?cat=${x.id}`} className="px-3 py-1.5 rounded-full text-sm font-medium border border-gray-200 text-gray-700 hover:border-blue-300 hover:text-blue-700">
              {x.nom}
            </Link>
          ))}
          <Link to={d.route} className="px-3 py-1.5 rounded-full text-sm font-medium text-blue-600 hover:underline inline-flex items-center gap-1">
            Tout comparer <ArrowRight size={14} />
          </Link>
        </div>
      </div>

      <RefsList refs={refs} />
    </div>
  )
}

// ───────────────────────── Page ─────────────────────────
export default function UnitView() {
  const { id } = useParams()
  useRouteMeta(`/explorer/${id}`)
  const [params] = useSearchParams()
  const cat = params.get('cat')
  const d = DECOUPAGE_BY_ID[id]
  const [data, setData] = useState(null)
  const [state, setState] = useState('loading')

  useEffect(() => {
    if (!d || !d.dataUrl) { setState('error'); return }
    setState('loading')
    fetch(d.dataUrl)
      .then((r) => r.json())
      .then((j) => { setData(j); setState('ready') })
      .catch(() => setState('error'))
  }, [d])

  if (!d || d.statut !== 'disponible')
    return (
      <div className="py-20 text-center text-gray-500">
        Découpage inconnu.{' '}
        <Link to="/atlas" className="text-blue-600">Aller à la carte</Link>.
      </div>
    )

  return (
    <>
      <ExplorerBar decoupage={d.id} mode={cat ? 'fiche' : 'tableau'} />
      {state === 'loading' && (
        <div className="py-20 text-center text-gray-400">
          <Loader2 className="animate-spin inline" size={22} /> Chargement…
        </div>
      )}
      {state === 'error' && <div className="py-20 text-center text-red-600">Données indisponibles.</div>}
      {state === 'ready' && (cat ? <UnitFiche d={d} data={data} cat={cat} /> : <UnitDashboard d={d} data={data} />)}
    </>
  )
}
