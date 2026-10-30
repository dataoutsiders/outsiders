import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { GraduationCap, ArrowRight, AlertTriangle, Info } from 'lucide-react'
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, ScatterChart, Scatter,
  ReferenceLine, LabelList, ZAxis,
} from 'recharts'
import { useRouteMeta } from '../../lib/meta'
import { VERDICTS } from '../Home'

/**
 * Dossier « PISA 2025 : la France décroche-t-elle ? ».
 * Données : public/data/showcases/pisa.json (python/tools/build_pisa.py), agrégats par pays
 * tirés des tableaux publiés par l'OCDE. Le dossier porte sur la France seule : elle est
 * comparée à la moyenne de l'OCDE et à la moyenne des 23 pays de l'OCDE présents depuis le
 * début (« OCDE-23 »), jamais à un pays en particulier. Aucun autre pays n'est nommé ni
 * mis en évidence dans les graphiques.
 * RÈGLE : une différence n'est affirmée que si elle est significative au sens de l'OCDE
 * (|écart / erreur type| > 1,96) ; un rang est toujours donné avec sa fourchette.
 */

const FR = '#2563EB'
const REF = '#9CA3AF'
const ACCENT = '#4F46E5'
const DOMS = ['mat', 'rea', 'sci']
const COURT = { mat: 'Maths', rea: 'Lecture', sci: 'Sciences' }
const DANS = { mat: 'en maths', rea: 'en lecture', sci: 'en sciences' }

const nf = (v, d = 0) => (v == null ? 'n/d' : v.toLocaleString('fr-FR', { minimumFractionDigits: d, maximumFractionDigits: d }))
const sg = (v, d = 0) => (v == null ? 'n/d' : `${v > 0 ? '+' : v < 0 ? '−' : ''}${nf(Math.abs(v), d)}`)
const pts = (v) => `${sg(v)} point${Math.abs(Math.round(v)) > 1 ? 's' : ''}`
const ptsD = (v) => `${sg(v, 1)} point${Math.abs(v) >= 2 ? 's' : ''}`
const rangTxt = (r) => `${r.rang}ᵉ sur ${r.n}`
const fourchette = (r) => (r.min === r.max ? `${r.min}ᵉ` : `entre la ${r.min}ᵉ et la ${r.max}ᵉ place`)

function Section({ id, kicker, title, children, intro }) {
  return (
    <section id={id} className="scroll-mt-20 mb-14">
      {kicker && <div className="text-xs font-semibold uppercase tracking-wide text-indigo-600 mb-1">{kicker}</div>}
      <h2 className="text-2xl font-bold text-gray-900 mb-2">{title}</h2>
      {intro && <p className="text-gray-600 mb-5 max-w-3xl">{intro}</p>}
      {children}
    </section>
  )
}

function DomaineToggle({ value, onChange }) {
  return (
    <div className="flex flex-wrap items-center gap-2 mb-4" role="group" aria-label="Domaine évalué">
      {DOMS.map((d) => (
        <button
          key={d}
          onClick={() => onChange(d)}
          aria-pressed={value === d}
          className={`px-3 py-1 rounded-full text-sm border transition-colors ${
            value === d ? 'bg-indigo-600 border-indigo-600 text-white' : 'border-gray-200 text-gray-600 hover:border-indigo-300'
          }`}
        >
          {COURT[d]}
        </button>
      ))}
    </div>
  )
}

function Legende({ items }) {
  return (
    <div className="flex flex-wrap items-center gap-4 text-xs text-gray-500 mb-2">
      {items.map(([label, color, dashed]) => (
        <span key={label} className="inline-flex items-center gap-1.5">
          <span className="w-5 inline-block" style={{ borderTop: `${dashed ? '2px dashed' : '3px solid'} ${color}` }} />
          {label}
        </span>
      ))}
    </div>
  )
}

function Sig({ ok }) {
  return ok ? (
    <span className="text-[11px] font-medium text-gray-700" title="Différence statistiquement significative au seuil de 5 % (règle de l'OCDE)">significatif</span>
  ) : (
    <span className="text-[11px] text-gray-400" title="Différence non significative au seuil de 5 % : elle peut tenir au hasard de l'échantillon">non significatif</span>
  )
}

// ───────────────────────────── Cartes vrai / faux ─────────────────────────────
function Carte({ c }) {
  const v = VERDICTS[c.verdict]
  return (
    <article className="relative flex flex-col bg-white border border-gray-200 rounded-2xl p-5 shadow-sm">
      <span
        className="absolute top-5 right-5 -rotate-3 select-none border-2 rounded-md px-2 py-0.5 text-xs font-black uppercase tracking-widest"
        style={{ borderColor: v.couleur, color: v.couleur }}
      >
        {v.label}
      </span>
      <h3 className="text-lg font-bold text-gray-900 leading-snug mb-3 pr-24">{c.question}</h3>
      <div className="mb-2">
        <span className="text-3xl font-black tracking-tight text-indigo-600">{c.chiffre}</span>
        <span className="block text-sm text-gray-500 mt-1">{c.chiffreLabel}</span>
      </div>
      <p className="text-sm text-gray-600 leading-relaxed flex-1">{c.texte}</p>
      <a
        href={`#${c.ancre}`}
        className="mt-3 inline-flex items-center gap-1 text-sm font-medium text-indigo-600 hover:text-indigo-700 self-start"
      >
        Voir le détail <ArrowRight size={15} />
      </a>
    </article>
  )
}

// ───────────────────────────── Graphiques ─────────────────────────────
function TooltipBox({ title, lines }) {
  return (
    <div className="bg-gray-900 text-white text-xs rounded-lg px-2.5 py-1.5">
      <div className="font-semibold">{title}</div>
      {lines.map((l) => <div key={l}>{l}</div>)}
    </div>
  )
}

function Trajectoire({ data }) {
  return (
    <ResponsiveContainer width="100%" height={280}>
      <LineChart data={data} margin={{ top: 10, right: 15, bottom: 5, left: 0 }}>
        <XAxis dataKey="annee" tick={{ fontSize: 11 }} />
        <YAxis tick={{ fontSize: 11 }} domain={['auto', 'auto']} width={40} />
        <Tooltip
          content={({ payload, label }) =>
            payload?.length ? (
              <TooltipBox
                title={`PISA ${label}`}
                lines={[`France : ${nf(payload[0].payload.fr)}`, `Moyenne OCDE-23 : ${nf(payload[0].payload.ocde23)}`]}
              />
            ) : null
          }
        />
        <Line type="monotone" dataKey="ocde23" stroke={REF} strokeWidth={2} strokeDasharray="6 4" dot={false} />
        <Line type="monotone" dataKey="fr" stroke={FR} strokeWidth={2.5} dot={{ r: 3 }} />
      </LineChart>
    </ResponsiveContainer>
  )
}

function Rangs({ data }) {
  return (
    <ResponsiveContainer width="100%" height={260}>
      <LineChart data={data} margin={{ top: 10, right: 15, bottom: 5, left: 0 }}>
        <XAxis dataKey="annee" tick={{ fontSize: 11 }} />
        <YAxis reversed tick={{ fontSize: 11 }} domain={[1, 'dataMax']} allowDecimals={false} width={32} />
        <Tooltip
          content={({ payload, label }) => {
            if (!payload?.length) return null
            const r = payload[0].payload
            return (
              <TooltipBox
                title={`PISA ${label}`}
                lines={[
                  `Parmi tous les participants : ${r.rang_tous}ᵉ sur ${r.n_tous}`,
                  `Parmi les 23 pays de l'OCDE présents depuis le début : ${r.rang_ocde23}ᵉ`,
                ]}
              />
            )
          }}
        />
        <Line type="monotone" dataKey="rang_tous" stroke={FR} strokeWidth={2.5} dot={{ r: 3 }} />
        <Line type="monotone" dataKey="rang_ocde23" stroke={ACCENT} strokeWidth={2} strokeDasharray="6 4" dot={{ r: 2 }} />
      </LineChart>
    </ResponsiveContainer>
  )
}

function BarrePlaces({ dec }) {
  const parts = [
    ['Pays de l’OCDE présents depuis le début (solde des dépassements)', dec.dont_stables, ACCENT],
    ['Autres participants déjà présents (solde des dépassements)', dec.dont_anciens, '#94A3B8'],
    ['Nouveaux venus (ou sans résultat comparable au départ) classés devant', dec.dont_nouveaux, '#CBD5E1'],
  ]
  const total = parts.reduce((a, [, v]) => a + Math.max(0, v), 0) || 1
  return (
    <div>
      <div className="flex h-5 rounded-full overflow-hidden bg-gray-100" aria-hidden>
        {parts.map(([l, v, c]) => (v > 0 ? <div key={l} style={{ width: `${(v / total) * 100}%`, backgroundColor: c }} /> : null))}
      </div>
      <ul className="mt-2 space-y-0.5 text-xs text-gray-600">
        {parts.map(([l, v, c]) => (
          <li key={l} className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-sm inline-block shrink-0" style={{ backgroundColor: c }} />
            <span className="font-semibold w-8 text-right">{sg(v)}</span> {l}
          </li>
        ))}
      </ul>
    </div>
  )
}

function NuageAttendu({ points }) {
  const autres = points.filter((p) => !p.fr)
  const fr = points.filter((p) => p.fr)
  const vals = points.flatMap((p) => [p.attendu, p.observe])
  const lo = Math.floor(Math.min(...vals) / 20) * 20
  const hi = Math.ceil(Math.max(...vals) / 20) * 20
  const tip = ({ payload }) => {
    if (!payload?.length) return null
    const p = payload[0].payload
    return (
      <TooltipBox
        title={p.nom}
        lines={[`Score observé : ${nf(p.observe)}`, `Score attendu : ${nf(p.attendu)}`, `Écart : ${pts(p.observe - p.attendu)}`]}
      />
    )
  }
  return (
    <ResponsiveContainer width="100%" height={380}>
      <ScatterChart margin={{ top: 10, right: 20, bottom: 30, left: 5 }}>
        <XAxis
          type="number" dataKey="attendu" domain={[lo, hi]} tick={{ fontSize: 11 }}
          label={{ value: 'Score attendu (PIB par habitant et profil social des élèves)', position: 'bottom', offset: 10, fontSize: 12, fill: '#6B7280' }}
        />
        <YAxis
          type="number" dataKey="observe" domain={[lo, hi]} tick={{ fontSize: 11 }} width={45}
          label={{ value: 'Score observé', angle: -90, position: 'insideLeft', fontSize: 12, fill: '#6B7280' }}
        />
        <ZAxis range={[40, 40]} />
        <ReferenceLine segment={[{ x: lo, y: lo }, { x: hi, y: hi }]} stroke="#94A3B8" strokeDasharray="4 4" />
        <Tooltip content={tip} cursor={false} />
        <Scatter data={autres} fill="#CBD5E1" />
        <Scatter data={fr} fill={FR} shape={(p) => <circle cx={p.cx} cy={p.cy} r={7} fill={FR} stroke="#fff" strokeWidth={2} />}>
          <LabelList dataKey="nom" position="right" style={{ fontSize: 12, fontWeight: 700, fill: FR }} />
        </Scatter>
      </ScatterChart>
    </ResponsiveContainer>
  )
}

function FaiblesForts({ data }) {
  return (
    <ResponsiveContainer width="100%" height={260}>
      <LineChart data={data} margin={{ top: 10, right: 15, bottom: 5, left: 0 }}>
        <XAxis dataKey="annee" tick={{ fontSize: 11 }} />
        <YAxis tick={{ fontSize: 11 }} unit=" %" width={48} domain={[0, 'auto']} />
        <Tooltip
          content={({ payload, label }) => {
            if (!payload?.length) return null
            const r = payload[0].payload
            return (
              <TooltipBox
                title={`PISA ${label}`}
                lines={[
                  `Élèves en difficulté : France ${nf(r.fr_faibles, 1)} %, OCDE-23 ${nf(r.ocde23_faibles, 1)} %`,
                  `Très bons élèves : France ${nf(r.fr_forts, 1)} %, OCDE-23 ${nf(r.ocde23_forts, 1)} %`,
                ]}
              />
            )
          }}
        />
        <Line type="monotone" dataKey="ocde23_faibles" stroke="#FCA5A5" strokeWidth={2} strokeDasharray="6 4" dot={false} />
        <Line type="monotone" dataKey="fr_faibles" stroke="#DC2626" strokeWidth={2.5} dot={{ r: 3 }} />
        <Line type="monotone" dataKey="ocde23_forts" stroke="#93C5FD" strokeWidth={2} strokeDasharray="6 4" dot={false} />
        <Line type="monotone" dataKey="fr_forts" stroke={FR} strokeWidth={2.5} dot={{ r: 3 }} />
      </LineChart>
    </ResponsiveContainer>
  )
}

function Encadre({ tone = 'info', titre, children }) {
  const warn = tone === 'warn'
  const Icon = warn ? AlertTriangle : Info
  return (
    <div className={`flex items-start gap-3 border rounded-xl p-4 ${warn ? 'bg-amber-50 border-amber-200 text-amber-900' : 'bg-blue-50 border-blue-200 text-blue-900'}`}>
      <Icon className={`${warn ? 'text-amber-600' : 'text-blue-600'} shrink-0 mt-0.5`} size={20} />
      <div className="text-sm leading-relaxed">
        {titre && <div className="font-semibold mb-1">{titre}</div>}
        {children}
      </div>
    </div>
  )
}

// ─────────────────────────────────── Page ───────────────────────────────────
export default function Pisa() {
  useRouteMeta('/international/pisa')
  const [data, setData] = useState(null)
  const [erreur, setErreur] = useState(false)
  const [dom, setDom] = useState('mat')

  useEffect(() => {
    fetch('/data/showcases/pisa.json')
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then(setData)
      .catch(() => setErreur(true))
  }, [])

  const cartes = useMemo(() => {
    if (!data) return []
    const ev = (d, y) => data.evolutions[d].find((e) => e.depuis === y)
    const m03 = ev('mat', 2003)
    const m18 = ev('mat', 2018)
    const r00 = ev('rea', 2000)
    const s06 = ev('sci', 2006)
    const t = data.trajectoires.mat
    const nonSig = DOMS.every((d) => !data.niveau[d].significatif)
    const att = data.attendu
    const dm = data.decomposition.mat
    const ffm = data.faibles_forts.mat
    const s0 = ffm.serie[0]
    const s1 = ffm.serie[ffm.serie.length - 1]
    return [
      {
        question: "La France s'effondre dans PISA ?",
        verdict: 'vraiMais',
        chiffre: `${sg(m03.fr.d)} points`,
        chiffreLabel: `en mathématiques de 2003 à 2025 (${nf(t[0].fr)} puis ${nf(t[t.length - 1].fr)}), ${sg(r00.fr.d)} en lecture depuis 2000`,
        texte: `Le recul est réel et significatif en maths et en lecture ; en sciences, la baisse depuis 2006 (${sg(s06.fr.d)}) n'est pas significative. ${nonSig ? "Mais en 2025, dans aucun des trois domaines le score ne se distingue significativement de la moyenne de l'OCDE, qui a reculé elle aussi." : "Et la moyenne de l'OCDE a reculé elle aussi."}`,
        ancre: 'niveau',
      },
      {
        question: 'Tout le monde baisse, la France suit le mouvement ?',
        verdict: 'pasPartout',
        chiffre: `${sg(m03.fr.d)} / ${sg(m03.ocde23.d)}`,
        chiffreLabel: "points en maths depuis 2003 : la France, puis la moyenne des 23 pays de l'OCDE présents depuis le début",
        texte: `En maths comme en lecture, la France baisse significativement plus que ces pays, et l'écart s'est creusé depuis 2018 (${sg(m18.fr.d)} contre ${sg(m18.ocde23.d)} en maths). En sciences, elle suit le mouvement : ${sg(s06.fr.d)} contre ${sg(s06.ocde23.d)} depuis 2006, une différence non significative.`,
        ancre: 'niveau',
      },
      {
        question: 'La France dégringole au classement ?',
        verdict: 'vraiMais',
        chiffre: `${data.niveau.mat.rang_tous.rang}ᵉ sur ${data.niveau.mat.rang_tous.n}`,
        chiffreLabel: `en maths en 2025 (${fourchette(data.niveau.mat.rang_tous)}), contre ${dm.long.rang_debut}ᵉ sur ${dm.long.n_debut} en 2003`,
        texte: `Sur ${dm.long.places} places perdues, ${dm.long.dont_nouveaux} tiennent à des participants absents du classement de 2003. Parmi les 23 pays de l'OCDE présents depuis le début, la France passe de la ${dm.long.rang_ocde23_debut}ᵉ à la ${dm.long.rang_ocde23_fin}ᵉ place. Depuis 2018, aucun nouveau venu n'explique la chute : les ${dm.depuis2018.places} places perdues sont un recul réel.`,
        ancre: 'rang',
      },
      {
        question: 'Vu sa richesse, la France devrait faire mieux ?',
        verdict: 'faux',
        chiffre: `${sg(att.mat.france.ecart)} points`,
        chiffreLabel: "en maths entre le score observé et le score attendu d'après le PIB par habitant et le profil social des élèves",
        texte: `${sg(att.sci.france.ecart)} en sciences, ${sg(att.rea.france.ecart)} en lecture : la France est au niveau attendu, au milieu des pays. Sa trajectoire est moins bonne : depuis 2018, elle a perdu ${nf(-att.mat.progression_2018.observe)} points en maths quand ${nf(-att.mat.progression_2018.attendu)} étaient attendus, un écart qui reste dans la dispersion habituelle entre pays.`,
        ancre: 'attendu',
      },
      {
        question: 'La France perd ses meilleurs élèves en maths ?',
        verdict: 'vraiMais',
        chiffre: `${nf(s0.fr_forts, 0)} % → ${nf(s1.fr_forts, 0)} %`,
        chiffreLabel: `d'élèves très performants en maths (niveau 5 ou plus), de ${s0.annee} à ${s1.annee}`,
        texte: `Leur part a fondu plus vite que dans les 23 pays de l'OCDE présents depuis le début (${nf(s0.ocde23_forts, 0)} % puis ${nf(s1.ocde23_forts, 1)} %) : en 2025, elle est significativement sous la moyenne de l'OCDE (${nf(ffm.vs_ocde_2025.forts.ocde, 1)} %), et la part d'élèves en difficulté a doublé (${nf(s0.fr_faibles, 0)} % puis ${nf(s1.fr_faibles, 0)} %). Mais pas en sciences, où ces deux parts n'ont pas bougé significativement depuis 2006.`,
        ancre: 'critique',
      },
    ]
  }, [data])

  if (erreur) return <div className="py-20 text-center text-gray-500">Données indisponibles pour le moment.</div>
  if (!data) return <div className="py-20 text-center text-gray-400">Chargement…</div>

  const n = data.niveau[dom]
  const ev = data.evolutions[dom]
  const dec = data.decomposition[dom]
  const att = data.attendu[dom]
  const soc = data.social[dom]
  const ff = data.faibles_forts[dom]
  const couv = data.couverture
  const src = data.sources
  const debut = ev[0].depuis
  const e18 = ev.find((e) => e.depuis === 2018)
  const hyp = couv.rangs_hypothese[dom]

  return (
    <div className="py-10">
      <div className="max-w-4xl mx-auto px-4">
        {/* En-tête */}
        <div className="flex items-center gap-2 text-indigo-600 mb-2">
          <GraduationCap size={20} />
          <span className="text-sm font-semibold uppercase tracking-wide">Dossier · PISA 2025</span>
        </div>
        <h1 className="text-4xl font-bold text-gray-900 mb-3">PISA 2025 : la France décroche-t-elle ?</h1>
        <p className="text-lg text-gray-600 max-w-3xl mb-3">
          Tous les trois ans, l'enquête PISA de l'OCDE évalue les élèves de 15 ans en
          mathématiques, en lecture et en sciences. Les résultats publiés le 8 septembre 2026 ont
          relancé deux récits opposés : « la France s'effondre » et « tout le monde baisse ». Les
          tableaux de l'OCDE permettent de trier : ce qui est un recul réel, ce qui tient à la
          façon de classer, ce qui n'est pas mesurable.
        </p>
        <p className="text-sm text-gray-500 max-w-3xl mb-8">
          La France est comparée à la moyenne de l'OCDE et à celle des 23 pays de l'OCDE présents
          et comparables depuis la première enquête (moyenne « OCDE-23 » publiée par l'OCDE). Une
          différence n'est affirmée que si elle est statistiquement significative.
        </p>

        {/* Cartes vrai / faux */}
        <div className="grid sm:grid-cols-2 gap-5 mb-14">
          {cartes.map((c) => <Carte key={c.question} c={c} />)}
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4">
        {/* Choix du domaine, commun à tout le dossier */}
        <div className="border-y border-gray-100 pt-3 pb-1 mb-8">
          <div className="flex flex-wrap items-center gap-3">
            <span className="text-sm text-gray-500 mb-4">Domaine (vaut pour tout le dossier) :</span>
            <DomaineToggle value={dom} onChange={setDom} />
          </div>
        </div>

        {/* 1. Le niveau ou le rang */}
        <Section
          id="niveau"
          kicker="1. Le niveau"
          title="Un score en baisse, mais dans la moyenne de l'OCDE"
          intro={`En 2025, la France obtient ${nf(n.fr.score)} points ${DANS[dom]}, contre ${nf(n.ocde.score)} en moyenne dans l'OCDE : un écart de ${ptsD(n.ecart_ocde)}, ${n.significatif ? 'statistiquement significatif' : "trop faible pour être distingué du hasard de l'échantillon (non significatif)"}.`}
        >
          <div className="bg-white border border-gray-200 rounded-xl p-5 mb-4">
            <h3 className="font-semibold text-gray-900 mb-1">Score moyen depuis {debut}</h3>
            <Legende items={[['France', FR], ["Moyenne des 23 pays de l'OCDE présents depuis le début", REF, true]]} />
            <Trajectoire data={data.trajectoires[dom]} />
          </div>
          <div className="overflow-x-auto mb-3">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-500 border-b border-gray-200">
                  <th className="py-2 pr-3 font-medium">Évolution jusqu'en 2025</th>
                  <th className="py-2 pr-3 font-medium">France</th>
                  <th className="py-2 pr-3 font-medium">OCDE-23</th>
                  <th className="py-2 font-medium">Écart France - OCDE-23</th>
                </tr>
              </thead>
              <tbody>
                {ev.map((e) => (
                  <tr key={e.depuis} className="border-b border-gray-100">
                    <td className="py-2 pr-3 text-gray-700">depuis {e.depuis}</td>
                    <td className="py-2 pr-3"><span className="font-semibold text-gray-900">{sg(e.fr.d)}</span> <Sig ok={e.fr.sig} /></td>
                    <td className="py-2 pr-3"><span className="font-semibold text-gray-900">{sg(e.ocde23.d)}</span> <Sig ok={e.ocde23.sig} /></td>
                    <td className="py-2"><span className="font-semibold text-gray-900">{sg(e.ecart.d)}</span> <Sig ok={e.ecart.sig} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="text-xs text-gray-400 max-w-3xl">
            Évolutions en points de score, publiées par l'OCDE avec leur erreur type (erreur de
            lien comprise). Pour l'écart entre la France et l'OCDE-23, l'erreur de lien, commune aux
            deux, s'annule ; la France fait partie des 23 pays, ce qui rend la comparaison un peu
            prudente.
          </p>
        </Section>

        <Section
          id="rang"
          kicker="2. Le rang"
          title="Le rang chute plus que le score"
          intro="Un rang dépend de qui est classé. PISA comptait 32 pays en 2000, 91 participants en 2025 : chaque arrivée mieux placée fait reculer la France sans qu'elle ait changé. Comparer le rang parmi tous les participants à celui parmi les pays présents depuis le début sépare les deux effets."
        >
          <DomaineToggle value={dom} onChange={setDom} />
          <div className="grid sm:grid-cols-3 gap-4 mb-5">
            {[
              ['Parmi tous les participants', n.rang_tous],
              ["Parmi les 38 pays de l'OCDE", n.rang_ocde],
              ['Parmi les 23 pays présents depuis le début', n.rang_ocde23],
            ].map(([l, r]) => (
              <div key={l} className="bg-gray-50 border border-gray-200 rounded-xl px-5 py-4">
                <div className="text-3xl font-black text-indigo-600 mb-1">{rangTxt(r)}</div>
                <div className="text-sm text-gray-600">{l}</div>
                <div className="text-xs text-gray-400 mt-1">rang possible : {r.min}ᵉ à {r.max}ᵉ</div>
              </div>
            ))}
          </div>
          <div className="bg-white border border-gray-200 rounded-xl p-5 mb-4">
            <h3 className="font-semibold text-gray-900 mb-1">Rang de la France {DANS[dom]}, vague par vague</h3>
            <Legende items={[['Parmi tous les participants classés', FR], ["Parmi les 23 pays de l'OCDE présents depuis le début", ACCENT, true]]} />
            <Rangs data={data.rangs[dom]} />
          </div>
          <div className="grid sm:grid-cols-2 gap-5 mb-4">
            {[['long', `De ${dec.long.debut} à 2025`], ['depuis2018', 'De 2018 à 2025']].map(([k, titre]) => {
              const x = dec[k]
              return (
                <div key={k} className="bg-white border border-gray-200 rounded-xl p-5">
                  <h3 className="font-semibold text-gray-900 mb-1">{titre}</h3>
                  <p className="text-sm text-gray-600 mb-3">
                    {x.places > 0
                      ? `${x.places} place${x.places > 1 ? 's' : ''} perdue${x.places > 1 ? 's' : ''} (${x.rang_debut}ᵉ sur ${x.n_debut}, puis ${x.rang_fin}ᵉ sur ${x.n_fin}).`
                      : `Rang stable (${x.rang_debut}ᵉ puis ${x.rang_fin}ᵉ).`}{' '}
                    Parmi les 23 pays présents depuis le début : {x.rang_ocde23_debut}ᵉ puis {x.rang_ocde23_fin}ᵉ.
                  </p>
                  <BarrePlaces dec={x} />
                </div>
              )
            })}
          </div>
          <p className="text-sm text-gray-600 max-w-3xl mb-3">
            {dom === 'sci'
              ? `En sciences, le rang bouge peu${dec.long.rang_ocde23_fin < dec.long.rang_ocde23_debut ? `, et la France gagne même ${dec.long.rang_ocde23_debut - dec.long.rang_ocde23_fin} place${dec.long.rang_ocde23_debut - dec.long.rang_ocde23_fin > 1 ? 's' : ''} parmi les pays présents depuis le début` : ''} : les quelques places perdues au classement général tiennent aux autres participants.`
              : `${DANS[dom][0].toUpperCase() + DANS[dom].slice(1)}, ${dec.long.dont_nouveaux * 2 > dec.long.places ? 'plus de la moitié' : 'une partie'} de la chute de long terme tient à la composition du classement (${dec.long.dont_nouveaux} places sur ${dec.long.places} face à des participants absents au départ). ${dec.depuis2018.dont_nouveaux === 0 ? 'Depuis 2018, en revanche, aucun nouveau venu ne passe devant : le recul est réel, et il se lit aussi parmi les pays présents depuis le début.' : `Depuis 2018, ${dec.depuis2018.dont_nouveaux} des ${dec.depuis2018.places} places perdues tiennent à des nouveaux venus.`}`}
          </p>
          <p className="text-xs text-gray-400 max-w-3xl">
            Rangs comptés parmi les participants dont les résultats figurent dans les tableaux de
            tendance de l'OCDE (éditions 2025 et 2022). Les participants sortis de PISA, dont
            certains devançaient la France, n'y figurent plus : les rangs des premières vagues sont
            donc un peu flatteurs et la perte de places un peu surestimée. « Nouveaux venus » inclut
            les pays déjà présents mais sans résultat jugé comparable par l'OCDE à la première
            vague. Le rang possible de 2025 est calculé par nos soins à partir des erreurs types
            publiées : un pays n'est compté devant ou derrière la France que si l'écart est
            significatif.
          </p>
        </Section>

        {/* 3. Score attendu */}
        <Section
          id="attendu"
          kicker="3. Ce qu'on peut attendre de la France"
          title="Un niveau conforme à sa richesse et à ses élèves"
          intro={`Un pays riche, dont les élèves viennent de familles plus diplômées, obtient en moyenne de meilleurs scores. En tenant compte du PIB par habitant et du profil social moyen des élèves, la France obtient ${pts(att.france.ecart)} ${DANS[dom]} par rapport à son score attendu (${nf(att.france.observe)} contre ${nf(att.france.attendu)}) : ${att.france.rang_ecart}ᵉ écart sur ${att.n} pays, un écart faible au regard de la dispersion entre pays (${nf(att.france.ecart_type_residus)} points d'écart type).`}
        >
          <DomaineToggle value={dom} onChange={setDom} />
          <div className="bg-white border border-gray-200 rounded-xl p-5 mb-4">
            <h3 className="font-semibold text-gray-900 mb-1">Score observé et score attendu, {att.n} pays, {COURT[dom].toLowerCase()}</h3>
            <p className="text-xs text-gray-500 mb-2">
              Au-dessus de la diagonale : mieux que l'attendu ; en dessous : moins bien. Survolez un
              point pour lire le pays.
            </p>
            <NuageAttendu points={att.points} />
          </div>
          <Encadre titre={att.progression_2018.ecart < 0 ? 'La trajectoire, elle, est moins bonne que prévu' : 'La trajectoire depuis 2018'}>
            Entre 2018 et 2025, la France perd {nf(-att.progression_2018.observe)} points {DANS[dom]}.
            Compte tenu de son niveau de 2018 (les pays partis haut baissent en général davantage),
            de son PIB et du profil social de ses élèves, on en attendait {nf(-att.progression_2018.attendu)} :
            {' '}{pts(att.progression_2018.ecart)} par rapport à l'attendu, {att.progression_2018.rang_ecart}ᵉ
            sur {att.progression_2018.n} pays.{' '}
            {e18.ecart.sig
              ? "L'écart va dans le même sens que la comparaison, significative, avec les pays de l'OCDE présents depuis le début, mais il reste dans la dispersion habituelle entre pays"
              : "L'écart reste dans la dispersion habituelle entre pays, et la différence avec les pays de l'OCDE présents depuis le début n'est pas significative non plus"}{' '}
            : le modèle n'explique que {nf(att.progression_2018.r2 * 100)} % des évolutions.
          </Encadre>
          <p className="text-xs text-gray-400 max-w-3xl mt-3">
            Régression entre pays (moindres carrés) du score moyen 2025 sur le logarithme du PIB par
            habitant en parité de pouvoir d'achat ({data.pib_annee}, Banque mondiale) et l'indice
            socio-économique moyen des élèves (ESCS 2025, OCDE) ; R² = {nf(att.r2, 2)}. Entités
            infranationales exclues. Un score attendu n'est ni un objectif ni une explication.
          </p>
        </Section>

        {/* 4. Ce que la critique dit de vrai */}
        <Section
          id="critique"
          kicker="4. Ce que la critique dit de vrai"
          title="L'origine sociale, les élèves en difficulté, les très bons élèves"
        >
          <DomaineToggle value={dom} onChange={setDom} />
          <h3 className="font-semibold text-gray-900 mb-2">Le poids de l'origine sociale, en 2025 ({COURT[dom].toLowerCase()})</h3>
          <div className="grid sm:grid-cols-3 gap-4 mb-3">
            {[
              ['Écart entre le quart le plus favorisé et le quart le plus défavorisé', soc.ecart, ' pts', 0],
              ["Part des écarts de score liée à l'origine sociale (R²)", soc.r2, ' %', 1],
              ["Points de score associés à une unité de l'indice social (pente)", soc.pente, ' pts', 0],
            ].map(([l, v, u, d]) => (
              <div key={l} className="bg-gray-50 border border-gray-200 rounded-xl px-5 py-4">
                <div className="text-2xl font-black text-indigo-600">{nf(v.fr, d)}{u}</div>
                <div className="text-xs text-gray-500 mb-1">moyenne OCDE : {nf(v.ocde, d)}{u} · <Sig ok={v.sig} /></div>
                <div className="text-sm text-gray-600">{l}</div>
                <div className="text-xs text-gray-400 mt-1">{v.rang_ocde}ᵉ valeur la plus forte sur {v.n_ocde} pays de l'OCDE</div>
              </div>
            ))}
          </div>
          <p className="text-sm text-gray-600 max-w-3xl mb-4">
            L'écart entre élèves favorisés et défavorisés est significativement plus grand en France
            que dans la moyenne de l'OCDE, dans les trois domaines : la France est dans le premier
            tiers des pays de l'OCDE sur ce point, sans en être l'extrême. Les deux autres mesures
            vont dans le même sens, mais l'écart avec la moyenne n'est pas toujours significatif.
          </p>
          <Encadre tone="warn" titre="Pas d'évolution mesurable de l'écart social entre 2022 et 2025">
            L'indice socio-économique de PISA (ESCS) a été calculé autrement en 2025 : une partie
            des questions sur les biens du foyer, dont celles sur les livres, a été remplacée.{' '}
            <a href={src.escs_methode.url} target="_blank" rel="noopener noreferrer" className="underline">
              Le rapport national anglais
            </a>{' '}
            renonce pour cette raison à comparer 2025 aux vagues précédentes, et{' '}
            <a href={src.escs_esade.url} target="_blank" rel="noopener noreferrer" className="underline">
              un document de travail d'EsadeEcPol
            </a>{' '}
            estime que le resserrement de l'écart social publié pour 2025 tient à ce changement de
            méthode. Ce dossier ne compare donc pas l'origine sociale dans le temps.
          </Encadre>

          <h3 className="font-semibold text-gray-900 mt-8 mb-2">Élèves en difficulté et très bons élèves</h3>
          <div className="bg-white border border-gray-200 rounded-xl p-5 mb-3">
            <Legende
              items={[
                ['France, sous le niveau 2', '#DC2626'],
                ['OCDE-23, sous le niveau 2', '#FCA5A5', true],
                ['France, niveau 5 ou plus', FR],
                ['OCDE-23, niveau 5 ou plus', '#93C5FD', true],
              ]}
            />
            <FaiblesForts data={ff.serie} />
          </div>
          <p className="text-sm text-gray-600 max-w-3xl mb-2">
            Depuis {ff.depuis}, la part d'élèves en difficulté {DANS[dom]} (sous le niveau 2, le seuil
            des compétences de base) varie de {sg(ff.evolution.faibles.fr.d, 1)} point{' '}
            <Sig ok={ff.evolution.faibles.fr.sig} /> en France, contre {sg(ff.evolution.faibles.ocde23.d, 1)}{' '}
            dans l'OCDE-23 ; celle des très bons élèves (niveau 5 ou plus) de {sg(ff.evolution.forts.fr.d, 1)}{' '}
            <Sig ok={ff.evolution.forts.fr.sig} />, contre {sg(ff.evolution.forts.ocde23.d, 1)}.
          </p>
          <p className="text-sm text-gray-600 max-w-3xl">
            En 2025 : {nf(ff.vs_ocde_2025.faibles.fr, 1)} % d'élèves en difficulté (moyenne OCDE{' '}
            {nf(ff.vs_ocde_2025.faibles.ocde, 1)} %, <Sig ok={ff.vs_ocde_2025.faibles.sig} />) et{' '}
            {nf(ff.vs_ocde_2025.forts.fr, 1)} % de très bons élèves (moyenne OCDE {nf(ff.vs_ocde_2025.forts.ocde, 1)} %,{' '}
            <Sig ok={ff.vs_ocde_2025.forts.sig} />).
          </p>
        </Section>

        {/* 5. Couverture */}
        <Section id="couverture" kicker="5. Encadré de méthode" title="Tous les pays n'évaluent pas la même part de leurs jeunes">
          <Encadre titre="La couverture de l'échantillon">
            PISA évalue les jeunes de 15 ans scolarisés à partir de la 7ᵉ année d'études (la 5ᵉ en
            France). Ceux qui ont quitté l'école, ceux qui sont scolarisés plus bas et les élèves
            exclus du test ne sont pas représentés. L'OCDE publie la part des 15 ans que représente
            l'échantillon (indice de couverture 3) : {nf(couv.y2025.france, 2)} en France en 2025, au niveau de la
            médiane des {couv.y2025.n} participants ; elle va de {nf(couv.y2025.min, 2)} à{' '}
            {nf(couv.y2025.max, 2)}, et {couv.y2025.n_sous_075} participants sont sous 0,75. Les jeunes
            non couverts étant en moyenne plus faibles, une couverture basse flatte le score moyen.
            <br />
            <br />
            Pour la France, l'effet est mince. Sous une hypothèse simple (les non-couverts auraient
            le score du 10ᵉ ou du 25ᵉ centile de leur pays), son rang {DANS[dom]} passerait de la{' '}
            {hyp.brut}ᵉ place à {hyp.p10 === hyp.p25 ? `la ${hyp.p10}ᵉ` : `la ${Math.min(hyp.p10, hyp.p25)}ᵉ ou la ${Math.max(hyp.p10, hyp.p25)}ᵉ`} : c'est une hypothèse, pas une mesure.
            La leçon vaut surtout pour la lecture des classements : entre pays de couvertures très
            différentes, quelques points d'écart ne disent pas grand-chose. La couverture française
            varie peu d'une vague à l'autre (de {nf(Math.min(...couv.france.map((c) => c.ci3)), 2)} à{' '}
            {nf(Math.max(...couv.france.map((c) => c.ci3)), 2)} depuis {couv.france[0].annee}).
          </Encadre>
        </Section>

        {/* 6. Méthode et limites */}
        <Section id="methode" kicker="6. Méthode et limites" title="Ce que PISA mesure, et ce qu'il ne dit pas">
          <ul className="space-y-2 text-sm text-gray-600 max-w-3xl list-disc pl-5">
            <li>
              PISA mesure des compétences à 15 ans (mobiliser ce que l'on sait dans des situations
              proches de la vie courante), pas l'école dans son ensemble : ni les programmes, ni le
              primaire, ni le supérieur, ni l'insertion.
            </li>
            <li>
              Les chiffres décrivent, ils n'expliquent pas. Rien ici n'attribue la baisse à une
              réforme, à la crise sanitaire ou aux écrans : PISA observe des élèves à un moment donné,
              pas des causes.
            </li>
            <li>
              Les scores sont estimés sur un échantillon (quelques milliers d'élèves par pays) avec
              des « valeurs plausibles » : chaque moyenne a une erreur type, de l'ordre de 3 points
              pour la France. Les évolutions ajoutent une « erreur de lien », due au changement des
              questions d'une vague à l'autre.
            </li>
            <li>
              « Significatif » veut dire que l'écart dépasse 1,96 fois son erreur type : il a moins de
              5 % de chances d'être un simple effet d'échantillon. Un écart non significatif n'est pas
              une égalité prouvée, mais on ne peut pas le distinguer du hasard.
            </li>
            <li>
              La moyenne de l'OCDE (38 pays) change de composition dans le temps ; c'est pourquoi les
              évolutions sont comparées à la moyenne des 23 pays de l'OCDE présents et comparables
              depuis 2000 ({data.ocde23.join(', ')}).
            </li>
            <li>
              Le score attendu est une régression entre pays sur deux variables seulement : il situe
              la France, il ne fixe pas ce qu'elle « devrait » obtenir.
            </li>
          </ul>
        </Section>

        <div className="grid sm:grid-cols-2 gap-5 mb-10">
          <Link to="/international" className="group bg-white border border-gray-200 rounded-xl p-5 hover:shadow-md hover:border-gray-300 transition-all">
            <div className="font-semibold text-gray-900 mb-1">Où se situe la France en Europe ?</div>
            <p className="text-sm text-gray-600">Dépenses publiques, santé, école, travail : 30 pays européens comparés.</p>
            <span className="inline-flex items-center gap-1 text-sm font-medium text-indigo-600 mt-2">Ouvrir le dossier <ArrowRight size={14} /></span>
          </Link>
          <Link to="/terrains/ecole" className="group bg-white border border-gray-200 rounded-xl p-5 hover:shadow-md hover:border-gray-300 transition-all">
            <div className="font-semibold text-gray-900 mb-1">L'école trie-t-elle ?</div>
            <p className="text-sm text-gray-600">À l'intérieur de la France : position sociale et valeur ajoutée des établissements.</p>
            <span className="inline-flex items-center gap-1 text-sm font-medium text-indigo-600 mt-2">Ouvrir le dossier <ArrowRight size={14} /></span>
          </Link>
        </div>

        <p className="text-xs text-gray-400 max-w-3xl">
          Sources :{' '}
          {['vol1_perf', 'vol1_escs', 'vol1_couv', 'vol1_2022', 'pib'].map((k, i) => (
            <span key={k}>
              {i > 0 && ' · '}
              <a href={src[k].url} target="_blank" rel="noopener noreferrer" className="underline hover:text-gray-600">{src[k].label}</a>
            </span>
          ))}
          . Tous les chiffres PISA sont ceux des tableaux publiés par l'OCDE ; aucune donnée
          individuelle n'est utilisée.
        </p>
      </div>
    </div>
  )
}
