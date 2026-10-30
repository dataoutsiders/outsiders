import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { Loader2, AlertCircle, Car, Info, Download, Search, ArrowRight, Map as MapIcon, GraduationCap, Wifi } from 'lucide-react'
import { useRouteMeta } from '../../lib/meta'
import {
  VARIANTES, VERDICT_LABELS, fromColumnar, groupeMatcher, classer, resumeGroupe, comparables, rechercher,
  toCsv, ordinal, verdict,
} from '../../lib/contexteEgal'
import RangsSlope from '../../components/charts/RangsSlope'
import EcartVolumeChart from '../../components/charts/EcartVolumeChart'
import PointMap from '../../components/charts/PointMap'
import NuageSimple from '../../components/charts/NuageSimple'

const ACCENT = '#EA580C'
const VCOL = { dessus: '#059669', dessous: '#DC2626', norme: '#9CA3AF' }
const VTEXTE = { dessus: '#047857', dessous: '#B91C1C', norme: '#4B5563' }
const NIVEAUX = {
  net: { label: 'Écart net', cls: 'bg-gray-900 text-white' },
  probable: { label: 'Probable', cls: 'bg-gray-200 text-gray-800' },
  indiscernable: { label: 'Non distinguable du hasard', cls: 'border border-gray-300 text-gray-500' },
}
// Familles d'indicateurs départementaux (section « Pourquoi certains départements sont-ils plus sévères ? »).
const FAMILLES = {
  habitat: { label: 'Habitat, taille, âge', color: ACCENT },
  social: { label: 'Milieu social', color: '#6366F1' },
  ecole: { label: 'École', color: '#0891B2' },
}

const fr = (v, d = 1) =>
  v == null ? 'n/d' : Number(v).toLocaleString('fr-FR', { minimumFractionDigits: d, maximumFractionDigits: d })
const f0 = (v) => (v == null ? 'n/d' : Math.round(v).toLocaleString('fr-FR'))
const signe = (v, d = 1) => (v == null ? 'n/d' : `${v > 0 ? '+' : v < 0 ? '−' : ''}${fr(Math.abs(v), d)}`)
const pts = (v) => `${signe(v)} ${Math.abs(v ?? 0) >= 2 ? 'pts' : 'pt'}`
const fmtR = (v) => (v == null ? 'n/d' : signe(v, 2))
const esc = (s) =>
  String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c])

// Carte : fonctions au niveau module (stables) pour ne pas redessiner la couche à chaque rendu.
const couleurVerdict = (v) => VCOL[v] || VCOL.norme
const LEGENDE_VERDICTS = [
  { color: VCOL.dessus, label: "Au-dessus de l'attendu" },
  { color: VCOL.dessous, label: "Sous l'attendu" },
  { color: VCOL.norme, label: "Dans l'attendu" },
]
const infobulleEcart = (p) =>
  `<strong>${esc(p.label)}</strong><br/>${esc(p.commune)}<br/>Taux ${fr(p.t)} % · attendu ${fr(p.att)} %<br/>Écart retenu ${signe(p.e)} pts`
const infobulleBrut = (p) => `<strong>${esc(p.label)}</strong><br/>${esc(p.commune)}<br/>Taux ${fr(p.t)} % (${p.n} candidats)`

function Section({ id, title, description, children, innerRef }) {
  return (
    <section id={id} ref={innerRef} className="mb-14 scroll-mt-24">
      <h2 className="text-2xl font-bold text-gray-900 mb-1">{title}</h2>
      {description && <p className="text-gray-600 mb-5">{description}</p>}
      {children}
    </section>
  )
}

function Pastille({ v }) {
  if (!v) return null
  return (
    <span
      className="inline-block text-[11px] font-semibold px-2 py-0.5 rounded-full whitespace-nowrap"
      style={{ color: VTEXTE[v], backgroundColor: `${VCOL[v]}1F` }}
    >
      {VERDICT_LABELS[v]}
    </span>
  )
}

function Niveau({ n }) {
  const x = NIVEAUX[n] || NIVEAUX.indiscernable
  return <span className={`inline-block text-[11px] font-semibold px-2 py-0.5 rounded-full whitespace-nowrap ${x.cls}`}>{x.label}</span>
}

// Petit intervalle horizontal : point = écart retenu, trait = intervalle à 95 %.
function Intervalle({ e, lo, hi, v, echelle = 25 }) {
  if (e == null) return null
  const W = 110
  const c = W / 2
  const x = (d) => c + (Math.max(-echelle, Math.min(echelle, d)) / echelle) * (c - 4)
  return (
    <svg width={W} height={14} className="inline-block align-middle" aria-hidden="true">
      <line x1={c} x2={c} y1={1} y2={13} stroke="#D1D5DB" />
      <line x1={x(lo)} x2={x(hi)} y1={7} y2={7} stroke={VCOL[v]} strokeWidth={2} strokeOpacity={0.55} />
      <circle cx={x(e)} cy={7} r={3.2} fill={VCOL[v]} />
    </svg>
  )
}

// Barre d'effet centrée sur 0, avec son intervalle à 95 %.
function EffetBarre({ effet, lo, hi, echelle = 10 }) {
  const W = 180
  const c = W / 2
  const x = (d) => c + (Math.max(-echelle, Math.min(echelle, d)) / echelle) * (c - 6)
  const col = effet > 0 ? '#059669' : '#DC2626'
  return (
    <svg width={W} height={18} className="inline-block align-middle shrink-0" aria-hidden="true">
      <line x1={c} x2={c} y1={0} y2={18} stroke="#9CA3AF" />
      <rect x={Math.min(c, x(effet))} y={5} width={Math.abs(x(effet) - c)} height={8} rx={2} fill={col} fillOpacity={0.75} />
      <line x1={x(lo)} x2={x(hi)} y1={9} y2={9} stroke="#111827" strokeWidth={1.2} />
      <line x1={x(lo)} x2={x(lo)} y1={5} y2={13} stroke="#111827" strokeWidth={1.2} />
      <line x1={x(hi)} x2={x(hi)} y1={5} y2={13} stroke="#111827" strokeWidth={1.2} />
    </svg>
  )
}

// Barre de corrélation centrée sur 0 (de −1 à +1).
function BarreR({ r, color }) {
  const W = 110
  const c = W / 2
  const x = c + Math.max(-1, Math.min(1, r ?? 0)) * (c - 2)
  return (
    <svg width={W} height={12} className="inline-block align-middle shrink-0" aria-hidden="true">
      <line x1={c} x2={c} y1={0} y2={12} stroke="#9CA3AF" />
      <rect x={Math.min(c, x)} y={2} width={Math.abs(x - c)} height={8} rx={2} fill={color} fillOpacity={0.8} />
    </svg>
  )
}

const PARTS = [
  { k: 'departement', label: 'Le département', sub: 'sévérité des examens, circulation, profil du département', color: ACCENT, txt: '#fff' },
  { k: 'commune', label: 'La commune', sub: 'taille, âge, logement, diplômes, profil social des collégiens', color: '#FDBA74', txt: '#7C2D12' },
  { k: 'ecole', label: "L'école, et ce que les données ne voient pas", sub: "sa pédagogie, mais aussi le profil de ses candidats, son centre d'examen", color: '#1F2937', txt: '#fff' },
  { k: 'hasard', label: 'Le hasard', sub: 'un taux calculé sur peu de candidats varie beaucoup', color: '#D1D5DB', txt: '#374151' },
]

function Decomposition({ d }) {
  return (
    <div className="bg-white border border-gray-200 rounded-xl p-6">
      <div className="flex h-10 rounded-lg overflow-hidden mb-4" role="img" aria-label="Répartition des écarts de réussite entre écoles">
        {PARTS.map((p) => (
          <div
            key={p.k}
            className="flex items-center justify-center text-sm font-bold"
            style={{ width: `${d[p.k]}%`, backgroundColor: p.color, color: p.txt }}
          >
            {d[p.k] >= 8 ? `${fr(d[p.k], 0)} %` : ''}
          </div>
        ))}
      </div>
      <div className="grid sm:grid-cols-2 gap-x-8 gap-y-2">
        {PARTS.map((p) => (
          <div key={p.k} className="flex items-start gap-2 text-sm">
            <span className="inline-block w-3 h-3 rounded-sm mt-1 shrink-0" style={{ backgroundColor: p.color }} />
            <span>
              <strong className="text-gray-900">{p.label} : {fr(d[p.k], 0)} %</strong>
              <span className="text-gray-500"> ({p.sub})</span>
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}

function DepBars({ deps, national }) {
  const grands = deps.filter((d) => d.ecoles >= 20)
  const colonnes = [
    { titre: 'Les plus sévères', liste: grands.slice(0, 8), color: ACCENT },
    { titre: 'Les plus cléments', liste: grands.slice(-8).reverse(), color: '#0D9488' },
  ]
  const x = (v) => `${Math.max(2, (v / 85) * 100)}%`
  return (
    <div className="grid md:grid-cols-2 gap-6">
      {colonnes.map((c) => (
        <div key={c.titre} className="bg-white border border-gray-200 rounded-xl p-5">
          <h3 className="font-semibold text-gray-900 mb-3">{c.titre}</h3>
          {c.liste.map((d) => (
            <div key={d.code} className="flex items-center gap-3 py-1">
              <div className="w-40 shrink-0 text-sm text-gray-700 truncate" title={`${d.ecoles} écoles, ${f0(d.candidats)} candidats`}>
                {d.nom} <span className="text-gray-400">({d.code})</span>
              </div>
              <div className="flex-1 bg-gray-100 rounded-full h-5 overflow-hidden relative">
                <div className="h-full rounded-full" style={{ width: x(d.taux), backgroundColor: c.color }} />
                <div className="absolute top-0 bottom-0 border-l-2 border-gray-900/50" style={{ left: x(national) }} title="Moyenne nationale" />
              </div>
              <div className="w-14 text-right text-sm font-semibold text-gray-900">{fr(d.taux)} %</div>
            </div>
          ))}
        </div>
      ))}
      <p className="md:col-span-2 text-xs text-gray-400 -mt-3">
        Départements d'au moins 20 auto-écoles. Le trait vertical marque la moyenne nationale ({fr(national)} %).
      </p>
    </div>
  )
}

// Format d'une valeur d'indicateur départemental selon son unité.
function formatIndicateur(ind) {
  if (ind.id === 'pop') return (v) => (v >= 1e6 ? `${fr(v / 1e6, v >= 2e6 ? 0 : 1)} M` : `${f0(v / 1000)} k`)
  if (ind.unite === '%') return (v) => `${fr(v, 0)} %`
  if (ind.unite === 'pts') return (v) => signe(v, 0)
  return (v) => fr(v, 0)
}

function Departements({ data }) {
  const { correlations_dep: corr, departements, stats } = data
  const tri = useMemo(() => corr.filter((c) => c.r != null).sort((a, b) => Math.abs(b.r) - Math.abs(a.r)), [corr])
  const [sel, setSel] = useState(tri[0]?.id)
  const ind = corr.find((c) => c.id === sel) || tri[0]
  const r = (id) => corr.find((c) => c.id === id)?.r
  const metro = departements.filter((d) => d.code.length === 2 && d.ecoles >= stats.min_ecoles_dep)
  const points = metro.map((d) => ({ id: d.code, x: d[ind.id], y: d.taux, label: d.nom }))
  const outreMer = departements.filter((d) => d.code.length === 3).sort((a, b) => a.taux - b.taux)
  const xLabel = `${ind.label}${ind.unite === '%' ? ' (%)' : ind.unite === 'pts' ? ' (points)' : ind.id === 'pop' ? ' (échelle logarithmique)' : ''}`

  return (
    <Section
      title="Pourquoi certains départements sont-ils plus sévères ?"
      description={`Entre départements, la réussite suit d'abord l'habitat : les départements de propriétaires et de maisons réussissent mieux (corrélations de ${fmtR(r('proprietaires'))} et ${fmtR(r('maisons'))}), les plus peuplés et les plus diplômés moins bien. Le profil social des collégiens et la valeur ajoutée des lycées n'y sont pour rien (${fmtR(r('ips_college_public'))} et ${fmtR(r('va_lycee'))}), la réussite au brevet à peine (${fmtR(r('dnb'))}).`}
    >
      <div className="grid md:grid-cols-5 gap-4">
        <div className="md:col-span-2 bg-white border border-gray-200 rounded-xl p-5">
          <h3 className="font-semibold text-gray-900 mb-1">Ce qui va avec la réussite d'un département</h3>
          <p className="text-xs text-gray-500 mb-3">
            Corrélation (de −1 à +1) avec le taux moyen de réussite, sur {stats.deps_correlation} départements de
            métropole. Cliquez un indicateur pour voir le nuage.
          </p>
          <div className="space-y-0.5">
            {tri.map((c) => {
              const on = c.id === ind.id
              return (
                <button
                  key={c.id}
                  onClick={() => setSel(c.id)}
                  aria-pressed={on}
                  className={`w-full flex items-center gap-2 rounded-lg px-2 py-1.5 text-left border transition-colors ${
                    on ? 'bg-orange-50 border-orange-200' : 'border-transparent hover:bg-gray-50'
                  }`}
                >
                  <span className="flex-1 text-sm text-gray-800 leading-tight">{c.label}</span>
                  <BarreR r={c.r} color={FAMILLES[c.famille]?.color || ACCENT} />
                  <span className="w-11 text-right text-sm font-semibold text-gray-900">{fmtR(c.r)}</span>
                </button>
              )
            })}
          </div>
          <div className="flex flex-wrap gap-x-4 gap-y-1 mt-3 text-xs text-gray-500">
            {Object.values(FAMILLES).map((f) => (
              <span key={f.label}>
                <span className="inline-block w-2.5 h-2.5 rounded-sm mr-1.5 align-middle" style={{ backgroundColor: f.color }} />
                {f.label}
              </span>
            ))}
          </div>
        </div>
        <div className="md:col-span-3 bg-white border border-gray-200 rounded-xl p-5">
          <h3 className="font-semibold text-gray-900 mb-2">{ind.label} et réussite au permis</h3>
          <NuageSimple
            points={points}
            xLabel={xLabel}
            yLabel="Réussite au permis (%)"
            logX={ind.id === 'pop'}
            fmtX={formatIndicateur(ind)}
            fmtY={(v) => `${fr(v, 0)} %`}
            couleur={FAMILLES[ind.famille]?.color || ACCENT}
          />
        </div>
      </div>
      <p className="text-sm text-gray-600 mt-4">
        Ces liens restent modestes : à elles deux, la part de maisons et la taille du département ne rendent compte
        que de {fr(stats.r2_dep_urbain, 0)} % des écarts entre départements. Le reste tient à ce que les données
        publiques ne décrivent pas, à commencer sans doute par l'organisation des examens elle-même (inspecteurs,
        centres d'examen).
      </p>
      <p className="text-xs text-gray-400 mt-2">
        Chaque département compte pour un point, quel que soit son nombre de candidats (départements d'au moins{' '}
        {stats.min_ecoles_dep} auto-écoles). Hors du graphique, l'outre-mer :{' '}
        {outreMer.map((d) => `${d.nom} ${fr(d.taux, 0)} %`).join(', ')}.
      </p>
    </Section>
  )
}

function phraseFiche(x, nat, v) {
  const pos = x.t >= nat ? 'au-dessus de' : 'sous'
  const base = `Avec ${fr(x.t)} % de réussite en première présentation, l'école est ${pos} la moyenne nationale (${fr(nat)} %). `
  const ctx =
    x.m === 2
      ? `Dans son contexte (son département, une commune comme la sienne), une école moyenne ferait ${fr(x.a2)} %`
      : `Dans son département, les écoles réussissent en moyenne ${fr(x.a1)} %`
  if (v === 'dessus') return `${base}${ctx} : elle fait mieux que prévu, au-delà de ce que le hasard produit avec ${x.n} candidats.`
  if (v === 'dessous')
    return `${base}${ctx} : elle fait moins bien que prévu, au-delà de ce que le hasard produit avec ${x.n} candidats. L'écart peut tenir à l'école comme à ce que les données ne voient pas (profil des candidats, centre d'examen).`
  return `${base}${ctx} : l'écart reste dans la marge du hasard avec ${x.n} candidats, on ne peut pas dire qu'elle fait mieux ou moins bien que prévu.`
}

function Fiche({ ecole, ecoles, stats, depNoms, com, ipsNiveaux, onSelect }) {
  const nat = stats.taux_national
  const classeDep = useMemo(() => classer(ecoles.filter((x) => x.dep === ecole.dep), 'complet'), [ecoles, ecole.dep])
  const moi = classeDep.find((x) => x.id === ecole.id)
  const v = moi?.verdict ?? verdict(ecole.lo2, ecole.hi2)
  const comps = useMemo(() => comparables(ecole, ecoles, 5), [ecole, ecoles])
  const depNom = depNoms[ecole.dep] || ecole.dep
  const lignes = [
    { label: 'Moyenne nationale', val: nat },
    { label: `Moyenne des écoles du département (${depNom})`, val: ecole.a1, delta: ecole.a1 - nat },
    ...(ecole.m === 2 ? [{ label: 'Attendu dans une commune comme la sienne', val: ecole.a2, delta: ecole.a2 - ecole.a1, fort: true }] : []),
  ]
  const attendu = ecole.m === 2 ? ecole.a2 : ecole.a1

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-6">
      <div className="flex flex-wrap items-start justify-between gap-3 mb-4">
        <div>
          <h3 className="text-xl font-bold text-gray-900">{ecole.nom}</h3>
          <div className="text-sm text-gray-500">
            {ecole.m === 1 ? `En ligne · candidats du département ${depNom} (${ecole.dep})` : `${ecole.commune} · ${depNom} (${ecole.dep})`}
            {' · '}{f0(ecole.n)} candidats en première présentation
          </div>
        </div>
        <Pastille v={v} />
      </div>
      {ecole.m !== 2 && (
        <p className="text-xs text-amber-800 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2 mb-4">
          {ecole.m === 1
            ? "École en ligne : une ligne par département, à l'adresse du siège. Son contexte se limite donc au département."
            : "Commune non rattachée : l'école est comparée à son département seulement."}
        </p>
      )}

      <div className="grid md:grid-cols-2 gap-6">
        <div>
          <div className="text-xs font-semibold uppercase tracking-wide text-gray-400 mb-2">Du taux attendu au taux observé</div>
          <table className="w-full text-sm">
            <tbody>
              {lignes.map((l) => (
                <tr key={l.label} className="border-b border-gray-100">
                  <td className={`py-1.5 pr-2 ${l.fort ? 'font-semibold text-gray-900' : 'text-gray-600'}`}>{l.label}</td>
                  <td className="py-1.5 text-right font-medium text-gray-900 whitespace-nowrap">{fr(l.val)} %</td>
                  <td className="py-1.5 pl-2 text-right text-xs text-gray-400 whitespace-nowrap">{l.delta != null ? pts(l.delta) : ''}</td>
                </tr>
              ))}
              <tr className="border-b border-gray-100">
                <td className="py-1.5 pr-2 font-semibold text-gray-900">Taux observé</td>
                <td className="py-1.5 text-right font-bold text-gray-900 whitespace-nowrap">{fr(ecole.t)} %</td>
                <td className="py-1.5 pl-2 text-right text-xs text-gray-400 whitespace-nowrap">{pts(ecole.t - attendu)}</td>
              </tr>
              <tr>
                <td className="py-2 pr-2 text-gray-600">Écart retenu, hasard pris en compte</td>
                <td colSpan={2} className="py-2 text-right whitespace-nowrap">
                  <span className="font-bold" style={{ color: VTEXTE[v] }}>{pts(ecole.e2)}</span>
                  <span className="text-xs text-gray-400"> [{signe(ecole.lo2)} ; {signe(ecole.hi2)}]</span>
                </td>
              </tr>
            </tbody>
          </table>
          {moi && (
            <p className="text-sm text-gray-600 mt-3">
              Dans son département : <strong>{ordinal(moi.rangBrut)}</strong> sur {classeDep.length} au taux brut,{' '}
              <strong>{ordinal(moi.rang)}</strong> à contexte égal.
            </p>
          )}
          {ecole.m === 2 && com && (
            <p className="text-xs text-gray-500 bg-gray-50 rounded-lg px-3 py-2 mt-3">
              <span className="font-semibold text-gray-700">Ce que le modèle sait de {ecole.commune} :</span>{' '}
              {f0(com.pop)} habitants · {fr(com.diplome_sup, 0)} % de diplômés du supérieur · {fr(com.ages65, 0)} % de
              65 ans et plus · {fr(com.proprietaires, 0)} % de propriétaires · IPS des collèges publics {fr(com.ips, 0)}
              {com.ips_niveau > 0 ? ` (valeur de ${com.ips_niveau === 1 ? "l'" : 'du '}${ipsNiveaux[com.ips_niveau]}, faute de collège public mesuré dans la commune)` : ''}.
            </p>
          )}
        </div>
        <div>
          <div className="text-xs font-semibold uppercase tracking-wide text-gray-400 mb-2">Ce que ça veut dire</div>
          <p className="text-sm text-gray-700 leading-relaxed">{phraseFiche(ecole, nat, v)}</p>
          {ecole.insee && (
            <Link
              to={`/territoires?code=${ecole.insee}`}
              className="inline-flex items-center gap-1.5 mt-3 text-sm font-medium text-blue-600 hover:text-blue-700"
            >
              La fiche de {ecole.commune} : indicateurs, jumeau statistique <ArrowRight size={15} />
            </Link>
          )}
        </div>
      </div>

      {comps.length > 0 && (
        <div className="mt-6">
          <div className="text-xs font-semibold uppercase tracking-wide text-gray-400 mb-2">
            Écoles comparables (même département, contexte le plus proche)
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-xs text-gray-500 text-left">
                  <th className="py-1 font-medium">École</th>
                  <th className="py-1 font-medium text-right">Candidats</th>
                  <th className="py-1 font-medium text-right">Taux</th>
                  <th className="py-1 font-medium text-right">Attendu</th>
                  <th className="py-1 font-medium text-right">Écart retenu</th>
                  <th className="py-1 font-medium text-right">Verdict</th>
                </tr>
              </thead>
              <tbody>
                {comps.map((c) => {
                  const cv = verdict(c.lo2, c.hi2)
                  return (
                    <tr key={c.id} onClick={() => onSelect(c.id)} className="border-t border-gray-100 hover:bg-gray-50 cursor-pointer">
                      <td className="py-1.5 pr-2">
                        <span className="text-gray-900">{c.nom}</span> <span className="text-gray-400">· {c.commune}</span>
                      </td>
                      <td className="py-1.5 text-right text-gray-600 whitespace-nowrap">{f0(c.n)}</td>
                      <td className="py-1.5 text-right text-gray-900 whitespace-nowrap">{fr(c.t)} %</td>
                      <td className="py-1.5 text-right text-gray-600 whitespace-nowrap">{fr(c.a2)} %</td>
                      <td className="py-1.5 text-right font-medium whitespace-nowrap" style={{ color: VTEXTE[cv] }}>{pts(c.e2)}</td>
                      <td className="py-1.5 text-right"><Pastille v={cv} /></td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}

function RechercheEcole({ ecoles, onSelect }) {
  const [q, setQ] = useState('')
  const [open, setOpen] = useState(false)
  const boxRef = useRef(null)
  const res = useMemo(() => rechercher(ecoles, q, 10), [ecoles, q])
  useEffect(() => {
    const onDoc = (e) => { if (boxRef.current && !boxRef.current.contains(e.target)) setOpen(false) }
    document.addEventListener('mousedown', onDoc)
    return () => document.removeEventListener('mousedown', onDoc)
  }, [])
  return (
    <div ref={boxRef} className="relative max-w-xl mb-5">
      <div className="flex items-center gap-2 bg-white border border-gray-300 rounded-xl px-4 py-3 shadow-sm focus-within:border-orange-400">
        <Search size={20} className="text-gray-400 shrink-0" />
        <input
          value={q}
          onChange={(e) => { setQ(e.target.value); setOpen(true) }}
          onFocus={() => setOpen(true)}
          placeholder="Nom de l'auto-école ou commune…"
          className="flex-1 outline-none text-gray-900 placeholder-gray-400 bg-transparent"
          aria-label="Chercher une auto-école"
        />
      </div>
      {open && res.length > 0 && (
        <ul className="absolute z-20 left-0 right-0 mt-2 bg-white border border-gray-200 rounded-xl shadow-lg overflow-hidden">
          {res.map((x) => (
            <li key={x.id}>
              <button
                onClick={() => { onSelect(x.id); setQ(''); setOpen(false) }}
                className="w-full flex items-center gap-3 px-4 py-2.5 text-left hover:bg-gray-50"
              >
                {x.m === 1 ? <Wifi size={16} className="text-gray-400 shrink-0" /> : <Car size={16} className="text-gray-400 shrink-0" />}
                <span className="flex-1 text-gray-900 truncate">{x.nom}</span>
                <span className="text-xs text-gray-400 shrink-0">{x.commune} ({x.dep})</span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

export default function TerrainAutoEcoles() {
  const [data, setData] = useState(null)
  const [state, setState] = useState('loading')
  const [params, setParams] = useSearchParams()
  const [texte, setTexte] = useState(params.get('q') || '')
  const [toutVoir, setToutVoir] = useState(false)
  const ficheRef = useRef(null)

  useEffect(() => {
    fetch('/data/showcases/auto-ecoles.json')
      .then((r) => r.json())
      .then((d) => { setData(d); setState('ready') })
      .catch(() => setState('error'))
  }, [])

  const ecoles = useMemo(() => (data ? fromColumnar(data) : []), [data])
  const parId = useMemo(() => new Map(ecoles.map((x) => [x.id, x])), [ecoles])
  const depNoms = useMemo(() => Object.fromEntries((data?.departements || []).map((d) => [d.code, d.nom])), [data])
  // Profil de chaque commune tel que le modèle le connaît (fiche d'une école).
  const communes = useMemo(() => {
    const c = data?.communes
    if (!c) return {}
    return Object.fromEntries(Object.entries(c.rows).map(([k, r]) => [k, Object.fromEntries(c.cols.map((col, i) => [col, r[i]]))]))
  }, [data])

  const setParam = useCallback(
    (patch) => {
      setParams(
        (prev) => {
          const p = new URLSearchParams(prev)
          for (const [k, v] of Object.entries(patch)) {
            if (v == null || v === '') p.delete(k)
            else p.set(k, v)
          }
          return p
        },
        { replace: true },
      )
    },
    [setParams],
  )

  // Sélection : un groupe par nom (g), un mot libre (q) ou un département (dep, par défaut
  // celui de l'exemple d'introduction).
  const variante = VARIANTES[params.get('v')] ? params.get('v') : 'complet'
  const groupe = data?.groupes.find((g) => g.id === params.get('g')) || null
  const qLibre = params.get('q')
  const depDefaut = data?.exemple?.dep || '75'
  const dep = params.get('dep') && depNoms[params.get('dep')] ? params.get('dep') : depDefaut
  const sel = groupe ? { type: 'groupe', ...groupe } : qLibre ? { type: 'texte', q: qLibre } : { type: 'dep', dep }

  const membres = useMemo(() => {
    if (!ecoles.length) return []
    if (sel.type === 'dep') return ecoles.filter((x) => x.dep === sel.dep)
    const ok = groupeMatcher(sel)
    return ecoles.filter((x) => ok(x.nom))
  }, [ecoles, sel.type, sel.dep, sel.q, sel.exclude]) // eslint-disable-line react-hooks/exhaustive-deps
  const classees = useMemo(() => classer(membres, variante), [membres, variante])
  const resume = useMemo(() => resumeGroupe(classees), [classees])

  const ecoleSel = parId.get(params.get('e')) || null
  useRouteMeta('/terrains/auto-ecoles', ecoleSel ? { title: `${ecoleSel.nom}, ${ecoleSel.commune} : à contexte égal` } : {})

  const ouvrirFiche = (id) => {
    setParam({ e: id })
    setTimeout(() => ficheRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 60)
  }

  const pointsEntonnoir = useMemo(
    () =>
      ecoles
        .filter((x) => x.m === 2)
        .map((x) => ({ id: x.id, n: x.n, ecart: x.t - x.a2, verdict: verdict(x.lo2, x.hi2), nom: x.nom, commune: x.commune })),
    [ecoles],
  )
  const pointsCarte = useMemo(
    () =>
      classees
        .filter((x) => x.lat != null)
        .map((x) => ({
          lat: x.lat, lon: x.lon, value: variante === 'brut' ? x.t : x.verdict, label: x.nom,
          commune: x.commune, t: x.t, n: x.n, att: x.attendu, e: x.ecart,
        })),
    [classees, variante],
  )

  if (state === 'loading')
    return (
      <div className="py-20 text-center text-gray-500">
        <Loader2 className="animate-spin inline" size={22} /> Chargement des données…
      </div>
    )
  if (state === 'error')
    return (
      <div className="py-20 text-center text-red-600">
        <AlertCircle className="inline" size={22} /> Données indisponibles.
      </div>
    )

  const { stats, decomposition, effets_contexte: effets, leviers, en_ligne: enLigne, departements, exemple, source } = data
  const depMin = stats.dep_min_metro || stats.dep_min
  const vv = VARIANTES[variante]
  const titreGroupe =
    sel.type === 'dep'
      ? `Les auto-écoles de ${depNoms[sel.dep]} (${sel.dep})`
      : `Les écoles dont le nom contient « ${sel.q} »${sel.exclude ? `, hors « ${sel.exclude} »` : ''}`
  const groupeEnLigne = membres.length > 0 && membres.every((x) => x.m === 1)
  const visibles = toutVoir ? classees : classees.slice(0, 20)
  const exporter = () => {
    const blob = new Blob([toCsv(classees, variante)], { type: 'text/csv;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    const slug = sel.type === 'dep' ? `dep-${sel.dep}` : (sel.id || sel.q).toLowerCase().replace(/[^a-z0-9]+/g, '-')
    a.href = url
    a.download = `auto-ecoles-${slug}-${variante}.csv`
    a.click()
    setTimeout(() => URL.revokeObjectURL(url), 1000)
  }
  const depsTries = [...departements].sort((a, b) => a.code.localeCompare(b.code))

  return (
    <div className="py-12 px-4">
      <div className="max-w-5xl mx-auto">
        {/* En-tête */}
        <header className="mb-10">
          <div className="flex items-center gap-2 mb-2" style={{ color: ACCENT }}>
            <Car size={20} />
            <span className="text-sm font-semibold uppercase tracking-wide">Dossier · Permis de conduire</span>
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-3">{data.titre}</h1>
          <p className="text-xl text-gray-600">
            {f0(stats.ecoles)} auto-écoles, {f0(stats.candidats)} candidats au permis B : le taux de réussite
            publié par la Sécurité routière dépend pour un quart du département où l'on passe l'examen, et
            aussi de la ville où l'on apprend. Pour savoir qui forme le mieux, il faut comparer chaque école à ce que
            son contexte laisse attendre.
          </p>
        </header>

        {/* Chiffres clés */}
        <div className="grid sm:grid-cols-3 gap-4 mb-14">
          <div className="bg-orange-50 border border-orange-200 rounded-xl p-5">
            <div className="text-3xl font-bold text-orange-700">{fr(depMin.taux, 0)} % → {fr(stats.dep_max.taux, 0)} %</div>
            <div className="text-sm text-orange-900">
              de réussite en première présentation selon le département, de {depMin.nom} à {stats.dep_max.nom}
            </div>
          </div>
          <div className="bg-gray-50 border border-gray-200 rounded-xl p-5">
            <div className="text-3xl font-bold text-gray-900">{fr(stats.r2_complet, 0)} %</div>
            <div className="text-sm text-gray-700">des écarts de réussite entre écoles tiennent au contexte (département et commune)</div>
          </div>
          <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-5">
            <div className="text-3xl font-bold text-emerald-700">{fr(stats.change_quart, 0)} %</div>
            <div className="text-sm text-emerald-900">des écoles changent de quart de classement une fois ce contexte pris en compte</div>
          </div>
        </div>

        {/* 1. Le contexte */}
        <Section
          title="Le taux brut mesure d'abord le contexte"
          description="D'où viennent les écarts de réussite entre auto-écoles ? Une part tient au département (les mêmes inspecteurs et les mêmes centres pour toutes ses écoles), une autre à la commune, le reste à l'école, et au hasard."
        >
          <Decomposition d={decomposition} />
          <div className="mt-6">
            <DepBars deps={departements} national={stats.taux_national} />
          </div>
          <div className="bg-white border border-gray-200 rounded-xl p-5 mt-6">
            <h3 className="font-semibold text-gray-900 mb-1">À département égal, ce que change la commune</h3>
            <p className="text-sm text-gray-500 mb-3">
              Effet estimé sur le taux attendu, toutes choses égales par ailleurs, avec son intervalle à 95 %.
            </p>
            {effets.map((e) => (
              <div key={e.id} className="flex flex-wrap items-center gap-x-4 gap-y-1 py-1.5 border-t border-gray-100 text-sm">
                <div className="flex-1 min-w-[12rem]">
                  <span className="text-gray-900">{e.label}</span> <span className="text-gray-400">({e.variation})</span>
                </div>
                <EffetBarre effet={e.effet} lo={e.lo} hi={e.hi} />
                <div className="w-20 text-right font-semibold text-gray-900">{pts(e.effet)}</div>
                <Niveau n={e.verdict} />
              </div>
            ))}
            <p className="text-xs text-gray-400 mt-3">
              Ces effets se lisent ensemble, chacun les autres étant tenus constants. Plus la ville est grande, plus
              le permis se rate : circulation plus dense, parcours d'examen plus exigeants, mais aussi des candidats
              différents. Un public de collégiens plus favorisé va avec une meilleure réussite ; à profil social
              égal, les communes très diplômées (villes étudiantes, métropoles) réussissent moins bien, sans doute
              un effet de grande ville plus que de diplôme. Le modèle ne dit pas lequel de ces mécanismes joue.
            </p>
          </div>
        </Section>

        {/* 1 bis. Entre départements */}
        <Departements data={data} />

        {/* 2. Le principe */}
        <Section
          title="Comparer à contexte égal"
          description="Pour chaque école, on estime ce qu'une école moyenne obtiendrait dans le même contexte : même département, même type de commune. L'écart entre le taux observé et cet attendu revient à l'école, ou au hasard."
        >
          {exemple && (
            <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-5 mb-5 text-sm text-emerald-950 leading-relaxed">
              <strong>Exemple.</strong> À {exemple.commune} ({exemple.dep_nom}), {exemple.nom} affiche{' '}
              <strong>{fr(exemple.t)} %</strong> de réussite
              {exemple.t <= stats.taux_national - 2
                ? `, sous la moyenne nationale (${fr(stats.taux_national)} %).`
                : `, à peu près la moyenne nationale (${fr(stats.taux_national)} %) : rien de remarquable en apparence.`}{' '}
              Mais dans ce département, les écoles réussissent en moyenne {fr(exemple.a1)} %, et dans une commune
              comme la sienne une école moyenne ferait <strong>{fr(exemple.a2)} %</strong> : elle fait nettement
              mieux que prévu ({pts(exemple.e2)} une fois le hasard pris en compte, sur {f0(exemple.n)} candidats).{' '}
              <button onClick={() => ouvrirFiche(exemple.id)} className="underline font-medium hover:text-emerald-700">
                Voir sa fiche
              </button>
            </div>
          )}
          <div className="bg-white border border-gray-200 rounded-xl p-5">
            <h3 className="font-semibold text-gray-900 mb-1">Chaque école face à son attendu</h3>
            <p className="text-sm text-gray-500 mb-3">
              Un point par école. Plus une école a de candidats, plus son taux est fiable : l'entonnoir marque
              l'écart au-delà duquel le hasard ne suffit plus à l'expliquer. {f0(stats.verdicts.dessus)} écoles
              sont nettement au-dessus de leur attendu, {f0(stats.verdicts.dessous)} nettement en dessous, les
              autres restent dans la marge du hasard.
            </p>
            <EcartVolumeChart points={pointsEntonnoir} p={stats.taux_national / 100} tau={stats.ecart_type_ecoles / 100} />
          </div>
          <p className="text-sm text-gray-500 mt-3">
            C'est le principe de la valeur ajoutée des lycées, que l'Éducation nationale publie chaque année,
            appliqué aux auto-écoles.{' '}
            <Link to="/terrains/ecole" className="text-blue-600 hover:underline">Voir le dossier École</Link>
          </p>
        </Section>

        {/* 3. L'outil : un groupe d'écoles */}
        <Section
          title="Comparer un groupe d'écoles"
          description="Un département, une enseigne, ou tout groupe repéré par un mot de son nom : les écoles classées au taux brut, puis à contexte égal. Une enseigne, un réseau ou une administration peut lire ses écoles de cette façon, chacune face à ce que son contexte laisse attendre."
        >
          <div className="bg-white border border-gray-200 rounded-xl p-5 mb-4 space-y-4">
            <div>
              <div className="text-xs font-semibold uppercase tracking-wide text-gray-400 mb-2">Le groupe</div>
              <div className="flex flex-wrap items-center gap-2">
                <select
                  value={sel.type === 'dep' ? sel.dep : ''}
                  onChange={(e) => setParam({ dep: e.target.value, g: null, q: null })}
                  className="border border-gray-300 rounded-lg px-3 py-1.5 text-sm bg-white"
                  aria-label="Choisir un département"
                >
                  <option value="" disabled>Un département…</option>
                  {depsTries.map((d) => (
                    <option key={d.code} value={d.code}>{d.code} · {d.nom} ({d.ecoles})</option>
                  ))}
                </select>
                <span className="text-sm text-gray-400">ou une enseigne :</span>
                {data.groupes.map((g) => {
                  const on = sel.type === 'groupe' && sel.id === g.id
                  return (
                    <button
                      key={g.id}
                      onClick={() => setParam({ g: g.id, dep: null, q: null })}
                      aria-pressed={on}
                      className={`px-3 py-1.5 rounded-full text-sm font-medium border transition-colors ${
                        on ? 'bg-gray-900 border-gray-900 text-white' : 'border-gray-200 text-gray-600 hover:border-gray-400'
                      }`}
                    >
                      {g.label}{g.enLigne ? ' (en ligne)' : ''} <span className={on ? 'text-gray-300' : 'text-gray-400'}>{g.n}</span>
                    </button>
                  )
                })}
                <form
                  onSubmit={(e) => {
                    e.preventDefault()
                    if (texte.trim().length >= 2) setParam({ q: texte.trim(), g: null, dep: null })
                  }}
                  className="flex items-center gap-1"
                >
                  <input
                    value={texte}
                    onChange={(e) => setTexte(e.target.value)}
                    placeholder="ou un mot du nom"
                    className="border border-gray-300 rounded-lg px-3 py-1.5 text-sm w-40"
                    aria-label="Mot contenu dans le nom des écoles"
                  />
                  <button type="submit" className="px-3 py-1.5 rounded-lg text-sm font-medium bg-gray-100 text-gray-700 hover:bg-gray-200">
                    OK
                  </button>
                </form>
              </div>
              <p className="text-xs text-gray-400 mt-2">
                Les enseignes sont repérées par leur nom (« nom contenant ECF »), pas par une liste
                d'adhérents : quelques écoles du réseau peuvent manquer, des homonymes s'y glisser.
              </p>
            </div>
            <div>
              <div className="text-xs font-semibold uppercase tracking-wide text-gray-400 mb-2">Tenir compte</div>
              <div className="flex flex-wrap gap-2">
                {Object.values(VARIANTES).map((x) => (
                  <button
                    key={x.id}
                    onClick={() => setParam({ v: x.id === 'complet' ? null : x.id })}
                    aria-pressed={variante === x.id}
                    className={`px-3 py-1.5 rounded-full text-sm font-medium border transition-colors ${
                      variante === x.id ? 'text-white' : 'border-gray-200 text-gray-600 hover:border-gray-400'
                    }`}
                    style={variante === x.id ? { backgroundColor: ACCENT, borderColor: ACCENT } : undefined}
                  >
                    {x.label}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {classees.length === 0 ? (
            <p className="text-gray-500 bg-white border border-gray-200 rounded-xl p-6">Aucune école ne correspond à ce groupe.</p>
          ) : (
            <>
              <div className="bg-gray-900 text-white rounded-xl px-5 py-4 mb-4">
                <div className="font-semibold mb-1">{titreGroupe}</div>
                <div className="text-sm text-gray-300">
                  {resume.ecoles} écoles · {f0(resume.candidats)} candidats · taux moyen {fr(resume.taux)} %
                  {vv.e && (
                    <>
                      {' · '}écart moyen {vv.court} <strong className="text-white">{pts(resume.ecart)}</strong>
                      {' · '}{resume.dessus} au-dessus de l'attendu, {resume.dessous} en dessous
                      {resume.ecoles >= 4 && <> · {resume.changentDeQuart} changent de quart de classement</>}
                    </>
                  )}
                </div>
                {groupeEnLigne && (
                  <div className="text-xs text-gray-400 mt-1">
                    Écoles en ligne : chaque ligne est un département, comparé à la moyenne des écoles de ce département.
                  </div>
                )}
              </div>

              {classees.length >= 2 && (
                <div className="bg-white border border-gray-200 rounded-xl p-5 mb-4">
                  <h3 className="font-semibold text-gray-900 mb-1">Qui remonte, qui recule</h3>
                  <p className="text-sm text-gray-500 mb-2">
                    {vv.e
                      ? 'Chaque ligne relie le rang au taux brut au rang une fois le contexte pris en compte. Survolez une ligne, cliquez pour ouvrir la fiche.'
                      : 'Choisissez une lecture qui tient compte du contexte pour voir les écoles changer de place.'}
                  </p>
                  <RangsSlope
                    items={classees}
                    labelB={vv.e ? vv.court.charAt(0).toUpperCase() + vv.court.slice(1) : 'Taux brut'}
                    selectedId={ecoleSel?.id}
                    onSelect={ouvrirFiche}
                  />
                </div>
              )}

              <div className="bg-white border border-gray-200 rounded-xl p-5 mb-4">
                <div className="flex flex-wrap items-center justify-between gap-3 mb-3">
                  <h3 className="font-semibold text-gray-900">Le classement</h3>
                  <button
                    onClick={exporter}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium border border-gray-300 text-gray-700 hover:bg-gray-50"
                  >
                    <Download size={15} /> Exporter (CSV, tableur)
                  </button>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="text-xs text-gray-500 text-left border-b border-gray-200">
                        <th className="py-1.5 pr-2 font-medium">Rang</th>
                        <th className="py-1.5 pr-2 font-medium">École</th>
                        <th className="py-1.5 pr-2 font-medium text-right">Candidats</th>
                        <th className="py-1.5 pr-2 font-medium text-right">Taux</th>
                        {vv.e && <th className="py-1.5 pr-2 font-medium text-right">Attendu</th>}
                        {vv.e && <th className="py-1.5 pr-2 font-medium text-right">Écart retenu</th>}
                        {vv.e && <th className="py-1.5 font-medium text-right">Verdict</th>}
                      </tr>
                    </thead>
                    <tbody>
                      {visibles.map((x) => {
                        const d = x.rangBrut - x.rang
                        return (
                          <tr
                            key={x.id}
                            onClick={() => ouvrirFiche(x.id)}
                            className={`border-b border-gray-50 hover:bg-orange-50/40 cursor-pointer ${ecoleSel?.id === x.id ? 'bg-orange-50' : ''}`}
                          >
                            <td className="py-1.5 pr-2 whitespace-nowrap">
                              <span className="font-semibold text-gray-900">{x.rang}</span>
                              {vv.e && d !== 0 && (
                                <span className="text-xs ml-1" style={{ color: d > 0 ? '#059669' : '#DC2626' }}>
                                  {d > 0 ? `▲${d}` : `▼${-d}`}
                                </span>
                              )}
                            </td>
                            <td className="py-1.5 pr-2">
                              <span className="text-gray-900">{x.nom}</span>{' '}
                              <span className="text-gray-400">· {x.commune}{sel.type !== 'dep' ? ` (${x.dep})` : ''}</span>
                            </td>
                            <td className="py-1.5 pr-2 text-right text-gray-600 whitespace-nowrap">{f0(x.n)}</td>
                            <td className="py-1.5 pr-2 text-right text-gray-900 whitespace-nowrap">{fr(x.t)} %</td>
                            {vv.e && <td className="py-1.5 pr-2 text-right text-gray-600 whitespace-nowrap">{fr(x.attendu)} %</td>}
                            {vv.e && (
                              <td className="py-1.5 pr-2 text-right whitespace-nowrap">
                                <span className="font-medium mr-2" style={{ color: VTEXTE[x.verdict] }}>{signe(x.ecart)}</span>
                                <Intervalle e={x.ecart} lo={x.lo} hi={x.hi} v={x.verdict} />
                              </td>
                            )}
                            {vv.e && <td className="py-1.5 text-right"><Pastille v={x.verdict} /></td>}
                          </tr>
                        )
                      })}
                    </tbody>
                  </table>
                </div>
                {classees.length > 20 && (
                  <button onClick={() => setToutVoir((t) => !t)} className="mt-3 text-sm font-medium text-blue-600 hover:underline">
                    {toutVoir ? 'Réduire' : `Afficher les ${classees.length} écoles`}
                  </button>
                )}
                {vv.e && (
                  <p className="text-xs text-gray-400 mt-3">
                    Écart retenu : écart au taux attendu, rapproché de zéro d'autant plus que l'école a peu de
                    candidats, avec son intervalle à 95 % (trait). Une école n'est dite au-dessus ou en dessous
                    que si l'intervalle ne contient pas zéro. ▲▼ : places gagnées ou perdues par rapport au
                    classement brut.
                  </p>
                )}
              </div>

              {pointsCarte.length > 0 && (
                <div className="bg-white border border-gray-200 rounded-xl p-5">
                  <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                    <MapIcon size={18} className="text-gray-400" /> Sur la carte
                  </h3>
                  <PointMap
                    points={pointsCarte}
                    height={420}
                    label={vv.e ? `Écart à l'attendu (${vv.court})` : 'Taux de réussite'}
                    unit={vv.e ? '' : ' %'}
                    colorFn={vv.e ? couleurVerdict : null}
                    legendItems={vv.e ? LEGENDE_VERDICTS : null}
                    tooltipFn={vv.e ? infobulleEcart : infobulleBrut}
                    fit="metropole"
                    radius={5}
                  />
                  <p className="text-xs text-gray-400 mt-2">
                    Chaque point est placé au centre de la commune de l'école.
                    {classees.some((x) => x.dep.length === 3 && x.lat != null) &&
                      " Les écoles d'outre-mer du groupe sont sur la carte, hors du cadrage initial : dézoomez pour les voir."}
                  </p>
                </div>
              )}
            </>
          )}
        </Section>

        {/* 4. La fiche d'une école */}
        <Section
          innerRef={ficheRef}
          id="fiche"
          title="La fiche d'une école"
          description="Cherchez une auto-école : son taux, ce que son contexte laisse attendre, son écart, et les écoles qui lui ressemblent."
        >
          <RechercheEcole ecoles={ecoles} onSelect={ouvrirFiche} />
          {ecoleSel ? (
            <Fiche
              ecole={ecoleSel}
              ecoles={ecoles}
              stats={stats}
              depNoms={depNoms}
              com={communes[ecoleSel.insee]}
              ipsNiveaux={data.ips_niveaux || []}
              onSelect={ouvrirFiche}
            />
          ) : (
            <p className="text-sm text-gray-400">Aucune école sélectionnée : cherchez-en une, ou cliquez une ligne du classement.</p>
          )}
        </Section>

        {/* 5. Ce qui distingue les écoles */}
        <Section
          title="Qu'est-ce qui distingue les écoles qui font mieux que prévu ?"
          description="Les caractéristiques publiées de chaque école, comparées toutes choses égales par ailleurs : à contexte égal, et chacune en tenant les autres constantes."
        >
          <div className="bg-white border border-gray-200 rounded-xl p-5 mb-4">
            {leviers.map((l) => (
              <div key={l.id} className="flex flex-wrap items-center gap-x-4 gap-y-1 py-1.5 border-b border-gray-100 last:border-0 text-sm">
                <div className="flex-1 min-w-[14rem]">
                  <span className="text-gray-900">{l.label}</span> <span className="text-gray-400">({f0(l.n)} écoles)</span>
                </div>
                <EffetBarre effet={l.effet} lo={l.lo} hi={l.hi} />
                <div className="w-20 text-right font-semibold text-gray-900">{pts(l.effet)}</div>
                <Niveau n={l.verdict} />
              </div>
            ))}
            <p className="text-xs text-gray-400 mt-3">
              Écart moyen au taux attendu, en points, avec son intervalle à 95 %. « Écart net » : l'effet
              dépasse largement ce que le hasard produit ; « probable » : il le dépasse de peu. Ce sont des
              associations, pas des causes : les écoles associatives, par exemple, accueillent souvent des
              publics en insertion, plus éloignés de l'examen.
            </p>
          </div>

          <div className="bg-white border border-gray-200 rounded-xl p-5">
            <h3 className="font-semibold text-gray-900 mb-1 flex items-center gap-2">
              <Wifi size={18} className="text-gray-400" /> Les écoles en ligne font-elles aussi bien ?
            </h3>
            <p className="text-sm text-gray-600 mb-3">
              Comparées aux écoles physiques du même département, les écoles en ligne réussissent{' '}
              <strong>{pts(enLigne.effet)}</strong> [{signe(enLigne.lo)} ; {signe(enLigne.hi)}] en première
              présentation ({f0(enLigne.n_candidats)} candidats).
            </p>
            {enLigne.enseignes.map((x) => (
              <div key={x.label} className="flex flex-wrap items-center gap-x-4 gap-y-1 py-1.5 border-t border-gray-100 text-sm">
                <div className="flex-1 min-w-[14rem]">
                  <span className="text-gray-900">{x.label}</span>{' '}
                  <span className="text-gray-400">({x.departements} départements, {fr(x.taux)} % de réussite)</span>
                </div>
                <EffetBarre effet={x.effet} lo={x.lo} hi={x.hi} echelle={16} />
                <div className="w-20 text-right font-semibold text-gray-900">{pts(x.effet)}</div>
                <Niveau n={x.verdict} />
              </div>
            ))}
            <p className="text-xs text-gray-400 mt-3">
              Leurs candidats ne sont pas ceux des écoles de quartier (budget, autonomie, nombre d'heures de
              conduite) : l'écart décrit un modèle de formation et son public, pas seulement la qualité de
              l'enseignement.
            </p>
          </div>
        </Section>

        {/* 6. La fiche de l'indicateur */}
        <Section title="La fiche de l'indicateur" description="Ce que mesure le chiffre, d'où il vient, comment on le calcule, et ce qu'il ne dit pas.">
          <dl className="bg-white border border-gray-200 rounded-xl divide-y divide-gray-100 text-sm">
            {[
              ['Indicateur', "Taux de réussite à l'épreuve pratique du permis B (voiture) en première présentation."],
              ['Définition', "Part des candidats présentés pour la première fois à l'épreuve de conduite qui la réussissent, pour chaque auto-école."],
              [
                'Source',
                <>
                  <a href={source.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                    {source.label}
                  </a>
                  {source.date_fichier ? `, fichier du ${new Date(source.date_fichier).toLocaleDateString('fr-FR')}` : ''}. La
                  période de référence n'est pas précisée dans le fichier.
                </>,
              ],
              ['Périmètre', `${f0(stats.ecoles)} auto-écoles d'au moins ${stats.min_n} candidats (dont ${f0(stats.lignes_en_ligne)} lignes d'écoles en ligne) ; le modèle est estimé sur les ${f0(stats.n_modele)} écoles d'au moins ${stats.min_n_modele} candidats.`],
              ['Taux attendu', `Régression pondérée par le nombre de candidats : un effet propre à chaque département, plus la taille de la commune, la part des 65 ans et plus, des propriétaires et des diplômés du supérieur (recensement 2023), et le profil social des collégiens (indice de position sociale des collèges publics de la commune, à défaut de l'intercommunalité ou du département). Elle rend compte de ${fr(stats.r2_complet, 0)} % des écarts de réussite entre écoles.`],
              ['Écart retenu', "Taux observé moins taux attendu, rapproché de zéro d'autant plus que l'école a peu de candidats (estimateur bayésien empirique), avec un intervalle à 95 %."],
              [
                'Limites',
                "Première présentation seulement. Le profil des candidats (âge, conduite accompagnée, heures de conduite) n'est pas publié : l'indice de position sociale des collèges décrit les jeunes de la commune, pas les candidats eux-mêmes. Les candidats ne vivent pas tous dans la commune de l'école. Le centre d'examen n'est pas connu, seulement le département. Les écoles en ligne ont une ligne par département et sont comparées au département seulement.",
              ],
            ].map(([k, v]) => (
              <div key={k} className="grid sm:grid-cols-[10rem_1fr] gap-1 sm:gap-4 px-5 py-3">
                <dt className="font-semibold text-gray-900">{k}</dt>
                <dd className="text-gray-600">{v}</dd>
              </div>
            ))}
          </dl>
        </Section>

        <div className="bg-amber-50 border border-amber-200 rounded-xl p-5 mb-8 flex items-start gap-3">
          <Info className="text-amber-600 shrink-0 mt-0.5" size={20} />
          <div className="text-sm text-amber-900 space-y-1">
            <p><strong>À lire avec ce recul.</strong></p>
            <p>
              Un écart à l'attendu signale une école à regarder de plus près, il ne la note pas. Il mêle le travail de
              l'école et ce que les données publiques ne décrivent pas : le profil de ses candidats, le centre où ils
              passent l'examen.
            </p>
            <p>
              Le rattachement des adresses aux communes réussit pour {fr(stats.rattachement)} % des écoles
              physiques ; les autres sont comparées à leur département.
            </p>
          </div>
        </div>

        {/* Pont vers la carte des outsiders */}
        <Link
          to="/atlas"
          className="group flex items-center gap-4 bg-gradient-to-r from-blue-50 to-white border border-blue-200 rounded-xl p-6 hover:shadow-md transition-all mb-4"
        >
          <div className="p-3 rounded-lg bg-blue-100 shrink-0">
            <MapIcon size={24} className="text-blue-600" />
          </div>
          <div className="flex-1">
            <div className="font-semibold text-gray-900 group-hover:text-blue-700 transition-colors">
              Le même principe, appliqué aux territoires : la carte des outsiders
            </div>
            <div className="text-sm text-gray-600">
              Croisez deux indicateurs : la droite de pronostic apparaît, avec les communes et départements qui la démentent.
            </div>
          </div>
          <ArrowRight size={20} className="text-blue-600 shrink-0 group-hover:translate-x-0.5 transition-transform" />
        </Link>
        <Link
          to="/terrains/ecole"
          className="group flex items-center gap-4 bg-gradient-to-r from-violet-50 to-white border border-violet-200 rounded-xl p-6 hover:shadow-md transition-all mb-8"
        >
          <div className="p-3 rounded-lg bg-violet-100 shrink-0">
            <GraduationCap size={24} className="text-violet-600" />
          </div>
          <div className="flex-1">
            <div className="font-semibold text-gray-900 group-hover:text-violet-700 transition-colors">
              La valeur ajoutée des lycées : le dossier École
            </div>
            <div className="text-sm text-gray-600">
              L'Éducation nationale compare ses lycées à ce que leur public laisse attendre : où l'école compense, où elle décroche.
            </div>
          </div>
          <ArrowRight size={20} className="text-violet-600 shrink-0 group-hover:translate-x-0.5 transition-transform" />
        </Link>

        <p className="text-xs text-gray-400">
          Sources :{' '}
          <a href={source.url} target="_blank" rel="noopener noreferrer" className="underline hover:text-gray-600">
            {source.label}
          </a>
          {data.sources_contexte.map((s) => (
            <span key={s.url}>
              {' · '}
              <a href={s.url} target="_blank" rel="noopener noreferrer" className="underline hover:text-gray-600">
                {s.label}
              </a>
            </span>
          ))}
          .{' '}
          <Link to="/methodologie" className="underline hover:text-gray-600">Méthodologie</Link>.
        </p>
      </div>
    </div>
  )
}
