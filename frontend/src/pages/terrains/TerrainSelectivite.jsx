import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Loader2, AlertCircle, ArrowRight, Info, DoorOpen, GraduationCap } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import { useRouteMeta } from '../../lib/meta'

// Trois façons de mesurer la porte d'entrée : la mesure officielle en tête,
// les deux autres en lectures complémentaires (chacune avec ses limites).
const MESURES = {
  acces: {
    label: "Taux d'accès (officiel)",
    suffix: ' %',
    desc: "Part des candidats en position de recevoir une proposition (rang du dernier appelé) : la longueur de la file d'attente. Plus c'est bas, plus la porte est étroite.",
    get: (f) => f.taux_median,
    asc: true,
    evolGet: (p) => p.acces,
    fermeQuand: 'baisse',
    evolNote: "Le taux officiel n'existe que depuis 2022 (il repose sur le rang du dernier appelé, non publié avant) : pour remonter à 2018, choisissez la pression ou le taux d'acceptation.",
  },
  pression: {
    label: 'Pression (vœux par place)',
    suffix: '',
    desc: "Candidatures par place : la demande. Une pression forte peut venir du manque de places comme de l'attractivité.",
    get: (f) => f.voeux_par_place,
    asc: false,
    evolGet: (p) => p.pression,
    fermeQuand: 'hausse',
    evolNote: 'Une pression qui monte = une porte qui se referme (plus de candidatures par place).',
  },
  acceptation: {
    label: "Taux d'acceptation",
    suffix: ' %',
    desc: "Part des candidatures qui finissent en inscription : mélange sélectivité et attractivité (un candidat n'accepte qu'un seul de ses vœux), et ne voit pas l'auto-censure de ceux qui ne candidatent pas.",
    get: (f) => f.taux_acceptation,
    asc: true,
    evolGet: (p) => p.acceptation,
    fermeQuand: 'baisse',
    evolNote: "Un taux d'acceptation qui baisse peut venir de la sélectivité comme de l'attractivité : à lire avec la pression.",
  },
}

const f0 = (v) => (v == null ? 'n/d' : Math.round(v).toLocaleString('fr-FR'))
const f1 = (v) => (v == null ? 'n/d' : v.toLocaleString('fr-FR', { maximumFractionDigits: 1 }))

function Section({ title, description, children }) {
  return (
    <section className="mb-12">
      <h2 className="text-2xl font-bold text-gray-900 mb-1">{title}</h2>
      {description && <p className="text-gray-600 mb-5">{description}</p>}
      {children}
    </section>
  )
}

function Bar({ label, sub, value, max, color, suffix = ' %' }) {
  const w = max && value != null ? Math.max(2, (value / max) * 100) : 0
  return (
    <div className="flex items-center gap-3 py-1">
      <div className="w-52 shrink-0 text-sm text-gray-700 truncate" title={label}>
        {label}
        {sub && <span className="text-gray-400"> · {sub}</span>}
      </div>
      <div className="flex-1 bg-gray-100 rounded-full h-5 overflow-hidden">
        <div
          className="h-full rounded-full flex items-center justify-end pr-2"
          style={{ width: `${w}%`, backgroundColor: color }}
        >
          <span className="text-[11px] font-medium text-white">{f1(value)}{suffix}</span>
        </div>
      </div>
    </div>
  )
}

// Couleur d'une cellule de la matrice : rouge = accès dur, vert = ouvert (échelle par colonne).
function cellColor(v, min, max) {
  if (v == null) return '#f9fafb'
  const n = max > min ? (v - min) / (max - min) : 0.5
  return `hsl(${Math.round(n * 135)}, 70%, 90%)`
}

export default function TerrainSelectivite() {
  useRouteMeta('/terrains/selectivite')
  const [data, setData] = useState(null)
  const [state, setState] = useState('loading')
  const [mesure, setMesure] = useState('acces')
  const [evolSel, setEvolSel] = useState(null)

  useEffect(() => {
    fetch('/data/showcases/selectivite.json')
      .then((r) => r.json())
      .then((d) => { setData(d); setState('ready') })
      .catch(() => setState('error'))
  }, [])

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

  const { stats, filieres, detaillees, licence, matrice, croisement, evolution } = data
  const mm = MESURES[mesure]

  // Évolution : lignes calculées pour la mesure choisie (fenêtre propre à chaque filière)
  const evolRows = (evolution?.filieres || [])
    .map((f) => {
      const pts = f.serie.filter((p) => mm.evolGet(p) != null)
      if (pts.length < 2) return null
      const v0 = mm.evolGet(pts[0])
      const v1 = mm.evolGet(pts[pts.length - 1])
      const delta = Math.round((v1 - v0) * 10) / 10
      return {
        id: f.id, label: f.label, pts, v0, v1,
        a0: pts[0].a, a1: pts[pts.length - 1].a, delta,
        ferme: mm.fermeQuand === 'hausse' ? delta > 0 : delta < 0,
      }
    })
    .filter(Boolean)
    .sort((a, b) => (mm.fermeQuand === 'hausse' ? b.delta - a.delta : a.delta - b.delta))
  const evolActif = evolRows.find((r) => r.id === evolSel) || evolRows[0]
  const evolLicence = evolution?.filieres.find((f) => f.id === 'Licence')
  const licAcces = (evolLicence?.serie || []).filter((p) => p.acces != null)
  const l100 = evolution?.licence_pct_100
  const colExtent = Object.fromEntries(
    matrice.filieres.map((fid) => {
      const vals = matrice.rows.map((r) => r[fid]).filter((v) => v != null)
      return [fid, { min: Math.min(...vals), max: Math.max(...vals) }]
    }),
  )

  return (
    <div className="py-12 px-4">
      <div className="max-w-4xl mx-auto">
        {/* En-tête */}
        <header className="mb-10">
          <div className="flex items-center gap-2 text-cyan-700 mb-2">
            <DoorOpen size={20} />
            <span className="text-sm font-semibold uppercase tracking-wide">Dossier · Parcoursup {data.session}</span>
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-3">{data.titre}</h1>
          <p className="text-xl text-gray-600">
            {f0(stats.n_formations)} formations, {(stats.n_voeux / 1e6).toLocaleString('fr-FR', { maximumFractionDigits: 1 })} millions
            de vœux : le taux d'accès de chaque formation dit qui peut entrer, et où. La hiérarchie
            réelle de la sélection ne ressemble pas à sa réputation.
          </p>
        </header>

        {/* Chiffres clés */}
        <div className="grid sm:grid-cols-3 gap-4 mb-12">
          <div className="bg-cyan-50 border border-cyan-200 rounded-xl p-5">
            <div className="text-3xl font-bold text-cyan-700">{stats.plus_dure.taux_median} %</div>
            <div className="text-sm text-cyan-900">d'accès au {stats.plus_dure.label} (sport) : la voie la plus fermée de Parcoursup</div>
          </div>
          <div className="bg-indigo-50 border border-indigo-200 rounded-xl p-5">
            <div className="text-3xl font-bold text-indigo-700">{licence.pct_100} %</div>
            <div className="text-sm text-indigo-900">des licences seulement acceptent tous leurs candidats</div>
          </div>
          <div className="bg-red-50 border border-red-200 rounded-xl p-5">
            <div className="text-3xl font-bold text-red-700">{f1(stats.boursiers_min.pct_boursiers)} % vs {f1(stats.boursiers_max.pct_boursiers)} %</div>
            <div className="text-sm text-red-900">d'admis boursiers : {stats.boursiers_min.label} contre {stats.boursiers_max.label}</div>
          </div>
        </div>

        {/* 1. Filières */}
        <Section
          title="Le plus dur d'entrer, ce n'est pas la prépa"
          description="Trois façons de mesurer la porte d'entrée, chacune avec ses limites : choisissez la lecture."
        >
          <div className="flex flex-wrap gap-2 mb-3">
            {Object.entries(MESURES).map(([id, mm]) => (
              <button
                key={id}
                onClick={() => setMesure(id)}
                className={`px-3 py-1.5 rounded-full text-sm font-medium border transition-colors ${
                  mesure === id ? 'bg-gray-900 border-gray-900 text-white' : 'border-gray-200 text-gray-600 hover:border-gray-400'
                }`}
              >
                {mm.label}
              </button>
            ))}
          </div>
          <div className="bg-white border border-gray-200 rounded-xl p-6 mb-4">
            <p className="text-sm text-gray-500 mb-3">{MESURES[mesure].desc}</p>
            {(() => {
              const mm = MESURES[mesure]
              const tri = [...filieres].sort((a, b) => (mm.asc ? mm.get(a) - mm.get(b) : mm.get(b) - mm.get(a)))
              const maxV = mesure === 'acces' ? 100 : Math.max(...filieres.map((f) => mm.get(f) ?? 0))
              return tri.map((f) => (
                <Bar
                  key={f.id}
                  label={f.label}
                  sub={mesure === 'acces' ? `${f.voeux_par_place ?? '?'} vœux/place` : null}
                  value={mm.get(f)}
                  max={maxV}
                  suffix={mm.suffix}
                  color={
                    mesure === 'acces'
                      ? f.taux_median < 45 ? '#DC2626' : f.taux_median < 65 ? '#F59E0B' : '#10B981'
                      : '#3B82F6'
                  }
                />
              ))
            })()}
          </div>
          <div className="bg-white border border-gray-200 rounded-xl p-6">
            <h3 className="font-semibold text-gray-900 mb-3">Les 15 filières détaillées les plus fermées</h3>
            <div className="grid sm:grid-cols-2 gap-x-8">
              {detaillees.map((f, i) => (
                <div key={f.label} className="flex items-baseline justify-between gap-2 py-1 border-b border-gray-50 text-sm">
                  <span className="text-gray-700 truncate" title={`${f.n} formations`}>{i + 1}. {f.label}</span>
                  <span className="font-semibold text-gray-900 shrink-0">{f.taux_median} %</span>
                </div>
              ))}
            </div>
          </div>
        </Section>

        {/* 1c. Évolution, pilotée par la même mesure que le classement */}
        {evolution && evolRows.length > 0 && (
          <Section
            title={`Qui se ferme, qui s'ouvre ? (${evolRows[0] ? evolution.sessions[0] : ''} → ${evolution.sessions[evolution.sessions.length - 1]})`}
            description="La même mesure que le classement ci-dessus, dans le temps. Une filière qui « s'ouvre » peut gagner des places, perdre en attractivité, ou gagner en auto-censure : les candidatures non exprimées sont invisibles. La fenêtre s'adapte à chaque filière (arrivées dans Parcoursup, mesure officielle depuis 2022)."
          >
            <div className="flex flex-wrap gap-2 mb-3">
              {Object.entries(MESURES).map(([id, x]) => (
                <button
                  key={id}
                  onClick={() => setMesure(id)}
                  className={`px-3 py-1.5 rounded-full text-sm font-medium border transition-colors ${
                    mesure === id ? 'bg-gray-900 border-gray-900 text-white' : 'border-gray-200 text-gray-600 hover:border-gray-400'
                  }`}
                >
                  {x.label}
                </button>
              ))}
            </div>
            <div className="grid md:grid-cols-2 gap-6">
              <div className="bg-white border border-gray-200 rounded-xl p-4">
                {evolRows.map((r) => {
                  const sel = evolActif?.id === r.id
                  return (
                    <button
                      key={r.id}
                      onClick={() => setEvolSel(r.id)}
                      className={`w-full flex items-center justify-between gap-2 rounded-lg px-2.5 py-1.5 text-left text-sm border transition-colors ${
                        sel ? 'bg-cyan-50 border-cyan-200' : 'border-transparent hover:bg-gray-50'
                      }`}
                    >
                      <span className="text-gray-800 truncate">{r.label}</span>
                      <span className="shrink-0 flex items-center gap-2">
                        <span className="text-xs text-gray-400">
                          {f1(r.v0)}{mm.suffix} ({r.a0}) → {f1(r.v1)}{mm.suffix} ({r.a1})
                        </span>
                        <span
                          className="text-xs font-semibold px-1.5 py-0.5 rounded"
                          style={{
                            color: r.ferme ? '#DC2626' : '#059669',
                            backgroundColor: r.ferme ? '#DC262614' : '#05966914',
                          }}
                        >
                          {r.delta > 0 ? '+' : ''}{f1(r.delta)}
                        </span>
                      </span>
                    </button>
                  )
                })}
                <p className="text-xs text-gray-400 mt-2 px-2">
                  Rouge = la porte se referme, vert = elle s'ouvre. Cliquez une filière pour sa courbe.
                </p>
              </div>
              <div className="bg-white border border-gray-200 rounded-xl p-5">
                <h3 className="font-semibold text-gray-900 mb-1">{evolActif?.label}</h3>
                <p className="text-xs text-gray-500 mb-2">{mm.evolNote}</p>
                <ResponsiveContainer width="100%" height={230}>
                  <LineChart
                    data={(evolActif?.pts || []).map((p) => ({ a: p.a, v: mm.evolGet(p) }))}
                    margin={{ top: 10, right: 15, bottom: 5, left: 0 }}
                  >
                    <XAxis dataKey="a" tick={{ fontSize: 11 }} />
                    <YAxis domain={mesure === 'acces' ? [0, 100] : [0, 'auto']} tick={{ fontSize: 11 }} width={35} />
                    <Tooltip
                      content={({ payload, label }) =>
                        payload?.length ? (
                          <div className="bg-gray-900 text-white text-xs rounded-lg px-2.5 py-1.5">
                            <div className="font-semibold">{label}</div>
                            <div>{mm.label} : {f1(payload[0].payload.v)}{mm.suffix}</div>
                          </div>
                        ) : null
                      }
                    />
                    <Line type="monotone" dataKey="v" stroke="#0891B2" strokeWidth={2.5} dot={{ r: 3 }} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          </Section>
        )}

        {/* 2. Licence */}
        <Section
          title="La licence est-elle encore « ouverte à tous » ?"
          description={`Non sélective en droit, la licence ne l'est plus en fait : seules ${licence.pct_100} % acceptent tous leurs candidats, et ${licence.pct_sous_50} % en refusent plus de la moitié.${licAcces.length >= 2 && l100?.length >= 2 ? ` La fermeture vient du milieu : la licence médiane est passée de ${licAcces[0].acces} % d'accès en ${licAcces[0].a} à ${licAcces[licAcces.length - 1].acces} % en ${licAcces[licAcces.length - 1].a}, même si la part de licences totalement ouvertes remonte légèrement (${l100[0].pct} % → ${l100[l100.length - 1].pct} %). Et la pression sur la licence a presque doublé depuis 2018.` : ''} Part des licences réellement ouvertes, par région :`}
        >
          <div className="bg-white border border-gray-200 rounded-xl p-6">
            {licence.regions.map((r) => (
              <Bar
                key={r.region}
                label={r.region}
                sub={`${r.n} licences · accès médian ${r.taux_median} %`}
                value={r.pct_100}
                max={100}
                color={r.pct_100 < 34 ? '#DC2626' : r.pct_100 < 60 ? '#F59E0B' : '#10B981'}
              />
            ))}
            <p className="text-xs text-gray-400 mt-3">
              En Île-de-France, la licence médiane n'est en position d'accepter que{' '}
              {licence.regions[0].taux_median} % de ses candidats : la « fac ouverte » y est devenue l'exception.
            </p>
          </div>
        </Section>

        {/* 3. Matrice académies */}
        <Section
          title="À filière égale, où est-ce plus dur ?"
          description="Taux d'accès médian par académie et par filière : à vœu identique, l'accès dépend de où l'on habite. Rouge = porte étroite, vert = porte ouverte (échelle par colonne)."
        >
          <div className="bg-white border border-gray-200 rounded-xl p-4">
            <div className="overflow-x-auto">
              <table className="w-full text-sm border-separate" style={{ borderSpacing: '3px 3px' }}>
                <thead>
                  <tr>
                    <th className="px-2 py-1 text-left text-xs font-semibold text-gray-500">Académie</th>
                    {matrice.filieres.map((fid) => (
                      <th key={fid} className="px-2 py-1 text-center text-xs font-semibold text-gray-600">{fid}</th>
                    ))}
                    <th className="px-2 py-1 text-center text-xs font-semibold text-gray-500">Moyenne</th>
                  </tr>
                </thead>
                <tbody>
                  {matrice.rows.map((r) => (
                    <tr key={r.academie}>
                      <td className="px-2 py-1 text-gray-800 whitespace-nowrap">{r.academie}</td>
                      {matrice.filieres.map((fid) => (
                        <td
                          key={fid}
                          className="px-2 py-1 text-center font-medium text-gray-800 rounded"
                          style={{ backgroundColor: cellColor(r[fid], colExtent[fid].min, colExtent[fid].max) }}
                        >
                          {r[fid] == null ? '·' : `${r[fid]} %`}
                        </td>
                      ))}
                      <td className="px-2 py-1 text-center text-gray-500">{r.moyenne == null ? '—' : `${r.moyenne} %`}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="text-xs text-gray-400 mt-2">
              {Object.entries(matrice.ecarts).map(([fid, e]) => (
                <span key={fid} className="mr-3">
                  {fid} : {e.ecart} pts d'écart ({e.dur.academie} {e.dur.taux} % vs {e.ouvert.academie} {e.ouvert.taux} %).
                </span>
              ))}
              Cellules à partir de {matrice.seuil_cellule} formations (« · » sinon), moyenne à partir de 2 filières.
            </p>
          </div>
        </Section>

        {/* 4. Boursiers */}
        <Section
          title="L'argent de l'accès : où vont les boursiers ?"
          description="Part d'admis boursiers (néo-bacheliers) par famille de formations : le gradient social du supérieur."
        >
          <div className="bg-white border border-gray-200 rounded-xl p-6 mb-4">
            {[...filieres].filter((f) => f.pct_boursiers != null).sort((a, b) => a.pct_boursiers - b.pct_boursiers).map((f) => (
              <Bar
                key={f.id}
                label={f.label}
                value={f.pct_boursiers}
                max={Math.max(...filieres.map((x) => x.pct_boursiers ?? 0))}
                color={f.pct_boursiers < 12 ? '#DC2626' : '#3B82F6'}
              />
            ))}
          </div>
          <div className="bg-white border border-gray-200 rounded-xl p-6">
            <h3 className="font-semibold text-gray-900 mb-1">Et à l'intérieur d'une même filière ?</h3>
            <p className="text-sm text-gray-500 mb-3">
              Part de boursiers dans le tiers le plus sélectif contre le tiers le plus ouvert de
              chaque filière. En BTS, BUT ou IFSI, le plus sélectif est aussi le plus populaire (les
              formations tendues sont là où vivent les boursiers) ; en CPGE, c'est l'inverse : au
              sommet, la sélection se referme socialement.
            </p>
            <table className="w-full text-sm">
              <thead>
                <tr className="text-xs text-gray-500">
                  <th className="text-left py-1">Filière</th>
                  <th className="text-right py-1">Tiers le + sélectif</th>
                  <th className="text-right py-1">Tiers le + ouvert</th>
                </tr>
              </thead>
              <tbody>
                {croisement.map((c) => {
                  const ferme = c.selectif < c.ouvert
                  return (
                    <tr key={c.id} className="border-t border-gray-100">
                      <td className="py-1.5 text-gray-800">{c.label}</td>
                      <td className={`py-1.5 text-right font-semibold ${ferme ? 'text-red-600' : 'text-gray-800'}`}>{f1(c.selectif)} %</td>
                      <td className="py-1.5 text-right text-gray-600">{f1(c.ouvert)} %</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </Section>

        {/* Notes */}
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-5 mb-8 flex items-start gap-3">
          <Info className="text-amber-600 shrink-0 mt-0.5" size={20} />
          <div className="text-sm text-amber-900 space-y-1">
            <p><strong>À lire avec ce recul.</strong></p>
            {data.notes.map((n, i) => (
              <p key={i}>{n}</p>
            ))}
          </div>
        </div>

        {/* Pont vers le dossier École */}
        <Link
          to="/terrains/ecole"
          className="group flex items-center gap-4 bg-gradient-to-r from-violet-50 to-white border border-violet-200 rounded-xl p-6 hover:shadow-md transition-all mb-8"
        >
          <div className="p-3 rounded-lg bg-violet-100 shrink-0">
            <GraduationCap size={24} className="text-violet-600" />
          </div>
          <div className="flex-1">
            <div className="font-semibold text-gray-900 group-hover:text-violet-700 transition-colors">
              Et avant le bac ? Le dossier École
            </div>
            <div className="text-sm text-gray-600">
              La sélection commence bien avant Parcoursup : ségrégation scolaire, cumul des trois
              étapes, valeur ajoutée des lycées.
            </div>
          </div>
          <ArrowRight size={20} className="text-violet-600 shrink-0 group-hover:translate-x-0.5 transition-transform" />
        </Link>

        <p className="text-xs text-gray-400">
          Source :{' '}
          <a href={data.source.url} target="_blank" rel="noopener noreferrer" className="underline hover:text-gray-600">
            {data.source.label}
          </a>
          .
        </p>
      </div>
    </div>
  )
}
