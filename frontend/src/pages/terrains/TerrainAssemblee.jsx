import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Loader2, AlertCircle, ArrowRight, Filter, Info, Landmark } from 'lucide-react'
import { useRouteMeta } from '../../lib/meta'
import AssembleeVotes from './AssembleeVotes'

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

// Barre horizontale : valeur pleine + repère ▲ population (même échelle).
function Bar({ label, sub, value, max, color, suffix = ' %', refValue = null, faible = false }) {
  const w = max && value != null ? Math.max(1.5, (value / max) * 100) : 0
  const refX = refValue != null && max ? Math.min(100, (refValue / max) * 100) : null
  return (
    <div className="flex items-center gap-3 pt-4 pb-0.5">
      <div className="w-44 shrink-0 text-sm text-gray-700 truncate" title={label}>
        {label}
        {sub && <span className="text-gray-400"> · {sub}</span>}
      </div>
      <div className="flex-1 relative h-5 bg-gray-100 rounded-full">
        <div className="absolute left-0 top-0 h-full rounded-full" style={{ width: `${w}%`, backgroundColor: color }} />
        {refX != null && (
          <div className="absolute top-0 h-full" style={{ left: `${refX}%`, transform: 'translateX(-50%)' }}>
            <span className="absolute -top-3.5 left-1/2 -translate-x-1/2 text-[10px] text-gray-500 whitespace-nowrap">▲</span>
            <div className="w-px h-full bg-gray-900/70" />
          </div>
        )}
      </div>
      <div className={`w-16 shrink-0 text-right text-sm font-semibold ${faible ? 'text-gray-400 italic' : 'text-gray-800'}`}>
        {value == null ? 'n/d' : `${f1(value)}${suffix}`}
      </div>
    </div>
  )
}

// « La porte du mandat » : population -> collaborateurs -> députés, même échelle.
function Porte({ titre, unite, pop, collabs, deputes, couleur }) {
  const max = Math.max(pop, collabs, deputes)
  const rows = [
    { label: 'Population', v: pop, c: '#9CA3AF' },
    { label: 'Collaborateurs parlementaires', v: collabs, c: couleur },
    { label: 'Députés', v: deputes, c: '#1E3A8A' },
  ]
  return (
    <div className="bg-white border border-gray-200 rounded-xl p-6">
      <h3 className="font-semibold text-gray-900 mb-2">{titre}</h3>
      {rows.map((r) => (
        <div key={r.label} className="flex items-center gap-3 py-1">
          <div className="w-56 shrink-0 text-sm text-gray-700">{r.label}</div>
          <div className="flex-1 bg-gray-100 rounded-full h-5 overflow-hidden">
            <div
              className="h-full rounded-full flex items-center justify-end pr-2"
              style={{ width: `${Math.max(3, (r.v / max) * 100)}%`, backgroundColor: r.c }}
            >
              <span className="text-[11px] font-medium text-white">{f1(r.v)}{unite}</span>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}

const METRIQUES = [
  { id: 'femmes', label: 'Femmes', suffix: ' %', get: (g) => g.femmes_pct, ref: (r) => r.femmes, refLabel: 'population' },
  { id: 'idp', label: 'Diversité (IDP)', suffix: ' %', get: (g) => g.idp_pct, ref: (r) => r.idp, refLabel: 'population' },
  { id: 'cadres', label: 'Cadres', suffix: ' %', get: (g) => g.pcs.cadres, ref: (r) => r.pcs.cadres, refLabel: 'actifs occupés' },
  { id: 'age', label: 'Âge moyen', suffix: ' ans', get: (g) => g.age_moyen, ref: null },
  { id: 'ouvriers', label: 'Ouvriers (effectif)', suffix: '', get: (g) => g.pcs_n.ouvriers, ref: null },
]

export default function TerrainAssemblee() {
  useRouteMeta('/terrains/assemblee')
  const [data, setData] = useState(null)
  const [state, setState] = useState('loading')
  const [met, setMet] = useState('femmes')

  useEffect(() => {
    fetch('/data/showcases/assemblee.json')
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

  const { ensemble: e, references: refs, groupes, sources } = data
  const m = METRIQUES.find((x) => x.id === met)
  const refVal = m.ref ? m.ref(refs) : null
  const rows = [...groupes].sort((a, b) => (m.get(b) ?? -1) - (m.get(a) ?? -1))
  const maxBar = Math.max(...rows.map((g) => m.get(g) ?? 0), refVal ?? 0)

  const pcsRows = Object.entries(data.pcs_labels).map(([id, label]) => ({
    id, label, ass: e.pcs[id], ref: refs.pcs[id] ?? null, n: e.pcs_n[id],
  }))
  const pcsMax = Math.max(...pcsRows.flatMap((r) => [r.ass ?? 0, r.ref ?? 0]))

  return (
    <div className="py-12 px-4">
      <div className="max-w-4xl mx-auto">
        {/* En-tête */}
        <header className="mb-10">
          <div className="flex items-center gap-2 text-indigo-600 mb-2">
            <Landmark size={20} />
            <span className="text-sm font-semibold uppercase tracking-wide">Dossier · Assemblée nationale, 17ᵉ législature</span>
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-3">{data.titre}</h1>
          <p className="text-xl text-gray-600">
            « Les députés ressemblent aux Français », « tel parti est le parti du peuple » : l'open
            data de l'Assemblée permet de vérifier, groupe par groupe. Profession (nomenclature
            INSEE), sexe, âge, diversité des noms, et le portrait des{' '}
            {e.collaborateurs.n.toLocaleString('fr-FR')} collaborateurs parlementaires.
          </p>
        </header>

        {/* Chiffres clés */}
        <div className="grid sm:grid-cols-3 gap-4 mb-12">
          <div className="bg-indigo-50 border border-indigo-200 rounded-xl p-5">
            <div className="text-3xl font-bold text-indigo-700">{f1(e.pcs.cadres)} %</div>
            <div className="text-sm text-indigo-900">de cadres et professions intellectuelles supérieures (vs {f1(refs.pcs.cadres)} % des personnes en emploi)</div>
          </div>
          <div className="bg-red-50 border border-red-200 rounded-xl p-5">
            <div className="text-3xl font-bold text-red-700">{e.pcs_n.ouvriers} / {e.n}</div>
            <div className="text-sm text-red-900">députés ouvriers, quand les ouvriers sont {f1(refs.pcs.ouvriers)} % des personnes en emploi</div>
          </div>
          <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-5">
            <div className="text-3xl font-bold text-emerald-700">{f1(e.idp_pct)} %</div>
            <div className="text-sm text-emerald-900">de diversité des noms (IDP), vs {f1(refs.idp)} % en population</div>
          </div>
        </div>

        {/* La porte du mandat */}
        <Section
          title="Des collaborateurs aux députés"
          description={`Pour la parité, l'écart est net : ${f1(e.collaborateurs.femmes_pct)} % de femmes chez les collaborateurs, ${f1(e.femmes_pct)} % chez les députés. Pour les noms, l'écart (${f1(e.collaborateurs.idp_pct)} % contre ${f1(e.idp_pct)} %) repose sur une vingtaine de députés et n'est pas établi statistiquement ; l'âge des collaborateurs n'est pas publié, alors que l'indice monte avec les générations.`}
        >
          <div className="grid md:grid-cols-2 gap-6">
            <Porte titre="Diversité des noms (IDP)" unite=" %" pop={refs.idp} collabs={e.collaborateurs.idp_pct} deputes={e.idp_pct} couleur="#0D9488" />
            <Porte titre="Part de femmes" unite=" %" pop={refs.femmes} collabs={e.collaborateurs.femmes_pct} deputes={e.femmes_pct} couleur="#EC4899" />
          </div>
          <p className="text-xs text-gray-400 mt-3">
            {e.collaborateurs.n.toLocaleString('fr-FR')} collaborateurs ({f1(e.collaborateurs.par_depute)} par député), listés par
            l'Assemblée avec civilité et nom : la parité et la diversité se mesurent ; les carrières et
            les conditions de travail, non.
          </p>
        </Section>

        {/* Le mur des professions */}
        <Section
          title="Le mur des professions"
          description="Chaque barre bleue est l'Assemblée, le repère ▲ la part dans la population active occupée. Les professions populaires, trois actifs sur cinq, sont presque absentes de l'hémicycle."
        >
          <div className="bg-white border border-gray-200 rounded-xl p-6">
            {pcsRows.map((r) => (
              <Bar
                key={r.id}
                label={r.label}
                sub={`${r.n} député${r.n > 1 ? 's' : ''}`}
                value={r.ass}
                max={pcsMax}
                color={r.id === 'ouvriers' || r.id === 'employes' ? '#DC2626' : '#3B82F6'}
                refValue={r.ref}
              />
            ))}
            <p className="text-xs text-gray-400 mt-4">
              ▲ = part dans la population active occupée (INSEE, enquête Emploi 2023). « Sans
              profession déclarée » n'a pas d'équivalent population.
            </p>
          </div>
        </Section>

        {/* Groupe par groupe */}
        <Section
          title="Groupe par groupe : qui représente qui ?"
          description="Le cœur du sujet : les mêmes mesures, par groupe politique, comparées à la France (repère ▲). Les couleurs suivent l'hémicycle."
        >
          <div className="flex flex-wrap gap-2 mb-4">
            {METRIQUES.map((x) => (
              <button
                key={x.id}
                onClick={() => setMet(x.id)}
                className={`px-3 py-1.5 rounded-full text-sm font-medium border transition-colors ${
                  met === x.id ? 'bg-gray-900 border-gray-900 text-white' : 'border-gray-200 text-gray-600 hover:border-gray-400'
                }`}
              >
                {x.label}
              </button>
            ))}
          </div>
          <div className="bg-white border border-gray-200 rounded-xl p-6">
            {refVal != null && (
              <p className="text-xs text-gray-500 mb-1">▲ = {f1(refVal)}{m.suffix} ({m.refLabel})</p>
            )}
            {rows.map((g) => (
              <Bar
                key={g.sigle}
                label={g.sigle}
                sub={`${g.n} députés`}
                value={m.get(g)}
                max={maxBar}
                color={g.couleur}
                suffix={m.suffix}
                refValue={refVal}
                faible={m.id === 'idp' && g.idp_pct == null}
              />
            ))}
            {m.id === 'idp' && (
              <p className="text-xs text-gray-400 mt-4">
                IDP calculé sur les noms reconnus par le référentiel ; « n/d » : moins de 30 noms reconnus
                dans le groupe, valeur non publiée pour qu'aucune personne ne soit identifiable.
              </p>
            )}
          </div>
        </Section>

        <AssembleeVotes />

        {/* Note méthodo */}
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-5 mb-8 flex items-start gap-3">
          <Info className="text-amber-600 shrink-0 mt-0.5" size={20} />
          <div className="text-sm text-amber-900 space-y-1">
            <p><strong>À lire avec ce recul.</strong></p>
            {data.notes.map((n, i) => (
              <p key={i}>{n}</p>
            ))}
          </div>
        </div>

        {/* CTA vers l'outil */}
        <div className="bg-gray-900 rounded-xl p-8 text-center">
          <Filter className="text-indigo-400 inline mb-3" size={28} />
          <h3 className="text-xl font-bold text-white mb-2">Faites le calcul sur vos propres données</h3>
          <p className="text-gray-300 mb-5">
            La même méthode (diversité, parité, âge), sur votre fichier de noms, directement dans
            votre navigateur.
          </p>
          <Link
            to="/outils/representativite"
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-indigo-500 text-white font-medium rounded-lg hover:bg-indigo-600 transition-colors"
          >
            Ouvrir l'outil <ArrowRight size={18} />
          </Link>
        </div>

        <p className="text-xs text-gray-400 mt-6">
          Sources :{' '}
          {Object.values(sources).map((s, i) => (
            <span key={s.url}>
              {i > 0 && ' · '}
              <a href={s.url} target="_blank" rel="noopener noreferrer" className="underline hover:text-gray-600">
                {s.label}
              </a>
            </span>
          ))}
          .
        </p>
      </div>
    </div>
  )
}
