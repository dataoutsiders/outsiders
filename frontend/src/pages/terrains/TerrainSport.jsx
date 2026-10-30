import { useEffect, useMemo, useState } from 'react'
import { Loader2, AlertCircle, Trophy } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { useRouteMeta } from '../../lib/meta'
import ToneCallout from '../../components/ToneCallout'
import ChoroplethMap from '../../components/charts/ChoroplethMap'

const ACCENT = '#F59E0B'
const QPV_COL = '#7C3AED'
const HORS_COL = '#9CA3AF'
const COULEURS_SERIES = ['#16A34A', '#2563EB', '#EA580C', '#DC2626', '#7C3AED', '#0891B2', '#CA8A04', '#DB2777']

const f1 = (v) => (v == null ? 'n/d' : v.toLocaleString('fr-FR', { maximumFractionDigits: 1 }))
const f2 = (v) => (v == null ? 'n/d' : v.toLocaleString('fr-FR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }))
const pct = (v) => (v == null ? 'n/d' : `${Math.round(v * 100)} %`)

function Section({ title, description, children }) {
  return (
    <section className="mb-12">
      <h2 className="text-2xl font-bold text-gray-900 mb-1">{title}</h2>
      {description && <p className="text-gray-600 mb-5">{description}</p>}
      {children}
    </section>
  )
}

// Encart « idée reçue » : la question, le verdict, l'explication.
const VERDICTS = {
  vrai: ['Vrai', 'bg-emerald-100 text-emerald-800'],
  faux: ['Faux', 'bg-red-100 text-red-800'],
  nuance: ['Vrai, mais', 'bg-amber-100 text-amber-800'],
  inconnu: ['On ne sait pas', 'bg-gray-100 text-gray-700'],
}
function IdeeRecue({ question, verdict, children }) {
  const [label, cls] = VERDICTS[verdict]
  return (
    <div className="bg-white border border-gray-200 rounded-xl p-5 mb-4">
      <div className="flex items-start justify-between gap-3 mb-2">
        <h3 className="font-semibold text-gray-900">« {question} »</h3>
        <span className={`shrink-0 px-2.5 py-0.5 rounded-full text-xs font-semibold ${cls}`}>{label}</span>
      </div>
      <p className="text-sm text-gray-700 leading-relaxed">{children}</p>
    </div>
  )
}

// Deux barres côte à côte : quartier prioritaire et reste de la commune.
function PaireBarres({ label, qpv, hors, max, unite = '' }) {
  const w = (v) => `${Math.max(2, (v / max) * 100)}%`
  return (
    <div className="py-2">
      <div className="text-sm text-gray-700 mb-1">{label}</div>
      {[
        ['Quartiers prioritaires', qpv, QPV_COL],
        ['Reste de la commune', hors, HORS_COL],
      ].map(([lib, v, c]) => (
        <div key={lib} className="flex items-center gap-2 mb-1">
          <div className="w-40 shrink-0 text-xs text-gray-500">{lib}</div>
          <div className="flex-1 bg-gray-100 rounded-full h-4">
            <div className="h-4 rounded-full" style={{ width: w(v), backgroundColor: c }} />
          </div>
          <div className="w-16 text-right text-sm font-semibold text-gray-800">
            {f1(v)}
            {unite}
          </div>
        </div>
      ))}
    </div>
  )
}

// Rapport centré sur 1 (échelle logarithmique) : à droite plus fréquent, à gauche moins.
function BarreRapport({ label, value, sub }) {
  const x = Math.log2(value)
  const w = Math.min(50, (Math.abs(x) / 3.5) * 50)
  const plus = x >= 0
  return (
    <div className="flex items-center gap-3 py-1">
      <div className="w-36 shrink-0 text-sm text-gray-700 truncate" title={label}>
        {label}
      </div>
      <div className="flex-1 relative h-4">
        <div className="absolute left-1/2 top-0 h-full w-px bg-gray-300" />
        <div
          className="absolute top-0 h-full rounded"
          style={{ width: `${w}%`, left: plus ? '50%' : `${50 - w}%`, backgroundColor: plus ? QPV_COL : HORS_COL }}
        />
      </div>
      <div className="w-24 shrink-0 text-right text-sm">
        <span className="font-semibold text-gray-800">× {f2(value)}</span>
        {sub && <div className="text-[11px] text-gray-400">{sub}</div>}
      </div>
    </div>
  )
}

export default function TerrainSport() {
  useRouteMeta('/terrains/sport')
  const [data, setData] = useState(null)
  const [geo, setGeo] = useState(null)
  const [state, setState] = useState('loading')

  useEffect(() => {
    fetch('/data/showcases/sport.json')
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then((d) => {
        setData(d)
        setState('ok')
      })
      .catch(() => setState('error'))
    fetch('/data/geo/departements.geojson')
      .then((r) => (r.ok ? r.json() : null))
      .then(setGeo)
      .catch(() => setGeo(null))
  }, [])

  const nomDep = useMemo(
    () => Object.fromEntries((geo?.features || []).map((f) => [f.properties.code, f.properties.nom])),
    [geo],
  )

  const serieIndice = useMemo(() => {
    if (!data) return []
    const annees = Object.keys(data.evolution[0]?.licences || {})
    return annees.map((a) => {
      const ligne = { annee: a }
      for (const s of data.evolution) {
        const base = s.licences['2013']
        if (base && s.licences[a]) ligne[s.sport] = Math.round((s.licences[a] / base) * 100)
      }
      return ligne
    })
  }, [data])

  const serieFemmes = useMemo(() => {
    if (!data) return []
    const annees = Object.keys(data.femmes[0]?.part || {})
    return annees.map((a) => Object.fromEntries([['annee', a], ...data.femmes.map((s) => [s.sport, s.part[a]])]))
  }, [data])

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

  const q = data.qpv
  const foot = data.sports_qpv.find((s) => s.sport === 'Football')
  const footOffre = data.offre.find((s) => s.sport === 'Football')
  const exceptions = data.departements.filter((d) => d.premier !== 'Football')
  const signatures = [...data.departements]
    .filter((d) => d.signature_indice != null)
    .sort((a, b) => b.signature_indice - a.signature_indice)
    .slice(0, 12)
  const tauxParDep = Object.fromEntries(data.departements.map((d) => [d.code, d.licences_pour_1000]))
  const r = data.retention
  const ab = (sexe, decile) => data.abandon_revenu_2018.find((x) => x.sexe === sexe && x.decile === decile)
  const maxDecile = Math.max(...data.revenu_deciles.map((d) => d.licences_pour_1000))
  const plusRiches = [...data.sports_revenu].reverse().slice(0, 8)
  const plusPopulaires = data.sports_revenu.slice(0, 6)

  return (
    <div className="py-12 px-4">
      <div className="max-w-4xl mx-auto">
        <header className="mb-10">
          <div className="flex items-center gap-2 mb-2" style={{ color: ACCENT }}>
            <Trophy size={20} />
            <span className="text-sm font-semibold uppercase tracking-wide">Dossier · Licences sportives, {data.millesime}</span>
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-3">{data.titre}</h1>
          <p className="text-xl text-gray-600">
            « Le foot, sport des quartiers », « les filles arrêtent », « les enfants de cadres lâchent le sport
            pour l'école » : 13 millions de licences en club (hors sport scolaire), comptées au domicile des licenciés, permettent de
            vérifier. Et de se demander si les quartiers manquent de clubs, ou de licenciés.
          </p>
        </header>

        <div className="grid sm:grid-cols-3 gap-4 mb-12">
          <div className="bg-violet-50 border border-violet-200 rounded-xl p-5">
            <div className="text-3xl font-bold text-violet-700">
              {f1(q.taux_qpv)} <span className="text-lg">contre</span> {f1(q.taux_hors)}
            </div>
            <div className="text-sm text-violet-900">
              licences pour 1 000 habitants dans les quartiers prioritaires, contre le reste de la même commune
            </div>
          </div>
          {foot && (
            <div className="bg-amber-50 border border-amber-200 rounded-xl p-5">
              <div className="text-3xl font-bold text-amber-700">{f1(foot.part_qpv)} %</div>
              <div className="text-sm text-amber-900">
                des licences des quartiers sont du football, contre {f1(foot.part_hors)} % dans le reste de la commune
              </div>
            </div>
          )}
          {footOffre && (
            <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-5">
              <div className="text-3xl font-bold text-emerald-700">
                × {f1(footOffre.lic_par_equip_qpv / footOffre.lic_par_equip_hors)}
              </div>
              <div className="text-sm text-emerald-900">
                licenciés par terrain de foot dans les quartiers : des terrains saturés
              </div>
            </div>
          )}
        </div>

        <Section
          title="Le foot partout, ou presque"
          description="Licences pour 1 000 habitants par département (fédérations scolaires et universitaires exclues). Le football est le premier sport dans 95 départements sur 100."
        >
          {geo && (
            <ChoroplethMap
              geo={geo}
              valueByCode={tauxParDep}
              label="Licences pour 1 000 hab."
              unit=""
              format={(v) => `${f1(v)} licences pour 1 000 habitants`}
              height={480}
            />
          )}
          <div className="grid md:grid-cols-2 gap-6 mt-6">
            <div className="bg-white border border-gray-200 rounded-xl p-5">
              <h3 className="font-semibold text-gray-900 mb-3">Là où le foot n'est pas premier</h3>
              <ul className="space-y-1.5 text-sm text-gray-700">
                {exceptions.map((d) => (
                  <li key={d.code}>
                    <strong>{nomDep[d.code] || d.code}</strong> : {d.premier.toLowerCase()} ({f1(d.premier_pour_1000)} pour 1 000 hab.)
                  </li>
                ))}
              </ul>
            </div>
            <div className="bg-white border border-gray-200 rounded-xl p-5">
              <h3 className="font-semibold text-gray-900 mb-1">Le sport qui distingue un département</h3>
              <p className="text-xs text-gray-500 mb-3">
                Combien de fois plus pratiqué qu'en moyenne nationale, parmi les fédérations d'un seul sport.
              </p>
              <ul className="space-y-1.5 text-sm text-gray-700">
                {signatures.map((d) => (
                  <li key={d.code} className="flex justify-between gap-2">
                    <span>
                      <strong>{nomDep[d.code] || d.code}</strong> : {d.signature.toLowerCase()}
                    </span>
                    <span className="text-gray-500">× {f1(d.signature_indice)}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </Section>

        <Section
          title="Dans les quartiers : moins de sport, et moins de sports"
          description={`Quartiers prioritaires (QPV) comparés au reste de leur propre commune, ce qui neutralise l'offre locale : ${q.communes} communes, ${(q.pop_qpv / 1e6).toLocaleString('fr-FR', { maximumFractionDigits: 1 })} million d'habitants des quartiers. Licences pour 1 000 habitants.`}
        >
          <div className="bg-white border border-gray-200 rounded-xl p-6 mb-6">
            <PaireBarres label="Ensemble" qpv={q.taux_qpv} hors={q.taux_hors} max={q.taux_hors} />
            <PaireBarres label="Filles et femmes" qpv={q.taux_f_qpv} hors={q.taux_f_hors} max={q.taux_hors} />
            <PaireBarres label="Garçons et hommes" qpv={q.taux_h_qpv} hors={q.taux_h_hors} max={q.taux_hors} />
            <p className="text-xs text-gray-500 mt-2">
              Le quartier fait mieux que le reste de sa commune dans {f1(q.part_communes_qpv_mieux)} % des communes seulement.
            </p>
          </div>
          <div className="bg-white border border-gray-200 rounded-xl p-6">
            <h3 className="font-semibold text-gray-900 mb-1">Sport par sport : combien de fois plus (ou moins) en quartier</h3>
            <p className="text-xs text-gray-500 mb-3">
              Licences par habitant du quartier, rapportées à celles du reste de la commune. En violet, plus fréquent dans les quartiers.
            </p>
            {data.sports_qpv.map((s) => (
              <BarreRapport key={s.sport} label={s.sport} value={s.rapport} sub={`${f1(s.part_qpv)} % des licences du quartier`} />
            ))}
          </div>
        </Section>

        <Section title="Trois idées reçues à l'épreuve">
          <IdeeRecue question="Le foot, c'est le sport des quartiers" verdict="nuance">
            Le football pèse {f1(foot?.part_qpv)} % des licences des quartiers, contre {f1(foot?.part_hors)} % dans le reste
            de la commune. Mais par habitant, il n'y est que {f1(foot?.rapport)} fois plus fréquent, et l'âge plus jeune des
            quartiers en explique une bonne part. Sa place tient surtout à l'absence des autres sports : le tennis y est
            presque quatre fois moins fréquent, le golf dix fois.
          </IdeeRecue>
          <IdeeRecue question="Les filles des quartiers arrêtent plus tôt" verdict="vrai">
            Entre 10-14 ans et 15-19 ans, les filles des quartiers gardent {pct(r.F_Q)} de leurs licences, contre {pct(r.F_H)}{' '}
            dans le reste de la commune. Chez les garçons, aucune différence : {pct(r.H_Q)} dans les deux cas.
          </IdeeRecue>
          <IdeeRecue question="Les enfants des milieux aisés arrêtent le sport vers 15 ans pour l'école" verdict="faux">
            Dans les communes les plus aisées, les adolescentes gardent davantage leurs licences entre 10-14 et 15-19 ans (
            {pct(ab('F', 10)?.r_15_19)}) que dans les plus modestes ({pct(ab('F', 1)?.r_15_19)}) ; chez les garçons, c'est
            pareil ({pct(ab('H', 10)?.r_15_19)} contre {pct(ab('H', 1)?.r_15_19)}). L'arrêt y vient plus tard, après 20 ans.
            Une réserve : on compare des communes, pas des familles (licences et population par âge de 2018).
          </IdeeRecue>
        </Section>

        <Section
          title="Riches et pauvres ne font pas les mêmes sports"
          description="Communes rangées en dix tranches de revenu (niveau de vie médian). Plus la commune est aisée, plus on y prend de licences."
        >
          <div className="bg-white border border-gray-200 rounded-xl p-6 mb-6">
            {data.revenu_deciles.map((d) => (
              <div key={d.decile} className="flex items-center gap-3 py-1">
                <div className="w-40 shrink-0 text-sm text-gray-700">
                  {d.decile === 1 ? '10 % les plus modestes' : d.decile === 10 ? '10 % les plus aisées' : `${d.decile}e tranche`}
                </div>
                <div className="flex-1 bg-gray-100 rounded-full h-4">
                  <div className="h-4 rounded-full" style={{ width: `${(d.licences_pour_1000 / maxDecile) * 100}%`, backgroundColor: ACCENT }} />
                </div>
                <div className="w-14 text-right text-sm font-semibold text-gray-800">{Math.round(d.licences_pour_1000)}</div>
              </div>
            ))}
            <p className="text-xs text-gray-500 mt-2">Licences pour 1 000 habitants.</p>
          </div>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-white border border-gray-200 rounded-xl p-5">
              <h3 className="font-semibold text-gray-900 mb-1">Sports des communes aisées</h3>
              <p className="text-xs text-gray-500 mb-3">Combien de fois plus pratiqués dans les 10 % de communes les plus aisées que dans les 10 % les plus modestes.</p>
              {plusRiches.map((s) => (
                <div key={s.sport} className="flex justify-between text-sm py-0.5">
                  <span className="text-gray-700">{s.sport}</span>
                  <span className="font-semibold text-gray-800">× {f1(s.rapport)}</span>
                </div>
              ))}
            </div>
            <div className="bg-white border border-gray-200 rounded-xl p-5">
              <h3 className="font-semibold text-gray-900 mb-1">Sports des communes modestes</h3>
              <p className="text-xs text-gray-500 mb-3">Rapport inférieur à 1 : plus pratiqués dans les communes les plus modestes.</p>
              {plusPopulaires.map((s) => (
                <div key={s.sport} className="flex justify-between text-sm py-0.5">
                  <span className="text-gray-700">{s.sport}</span>
                  <span className="font-semibold text-gray-800">× {f2(s.rapport)}</span>
                </div>
              ))}
            </div>
          </div>
        </Section>

        <Section
          title="Pas de clubs, ou pas de demande ?"
          description="Pour chaque sport, le quartier comparé au reste de sa commune, pour 10 000 habitants : équipements (recensement Data ES), clubs actifs (INJEP) et licences. Un rapport de 1 = autant que le reste de la commune."
        >
          <div className="bg-white border border-gray-200 rounded-xl overflow-x-auto mb-4">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 text-gray-600">
                <tr>
                  <th className="text-left px-4 py-2 font-medium">Sport</th>
                  <th className="text-right px-3 py-2 font-medium">Équipements</th>
                  <th className="text-right px-3 py-2 font-medium">Clubs actifs</th>
                  <th className="text-right px-3 py-2 font-medium">Licences</th>
                  <th className="text-right px-4 py-2 font-medium">Licenciés par équipement (quartier / reste)</th>
                </tr>
              </thead>
              <tbody>
                {data.offre.map((s) => (
                  <tr key={s.sport} className="border-t border-gray-100">
                    <td className="px-4 py-2 text-gray-800">{s.sport}</td>
                    <td className="px-3 py-2 text-right">{f2(s.equipements)}</td>
                    <td className="px-3 py-2 text-right">{f2(s.clubs)}</td>
                    <td className="px-3 py-2 text-right font-semibold">{f2(s.licences)}</td>
                    <td className="px-4 py-2 text-right text-gray-600">
                      {s.lic_par_equip_qpv} / {s.lic_par_equip_hors}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="space-y-3">
            <ToneCallout tone="info">
              Tennis, natation, judo : les quartiers ont moins d'équipements, mais ceux qui existent sont aussi utilisés
              qu'ailleurs. L'écart de licences suit l'écart d'offre.
            </ToneCallout>
            <ToneCallout tone="good">
              Football : c'est l'inverse de « pas de demande ». Les quartiers ont deux fois moins de terrains par habitant,
              mais plus de licenciés : chaque terrain y porte près de trois fois plus de joueurs qu'ailleurs.
            </ToneCallout>
            <ToneCallout tone="warn">
              Sports de gymnase (handball, gymnastique, athlétisme) : le bâtiment est souvent là, les licences non. Ce qui
              manque n'est pas le lieu, sans doute les créneaux, l'encadrement ou le coût, que ces données ne mesurent pas.
            </ToneCallout>
          </div>
          <div className="grid md:grid-cols-2 gap-6 mt-6">
            <div className="bg-white border border-gray-200 rounded-xl p-5">
              <h3 className="font-semibold text-gray-900 mb-1">Avec ou sans club dans le quartier (2023)</h3>
              <p className="text-xs text-gray-500 mb-3">Licences du quartier rapportées au taux du reste de sa commune.</p>
              {data.test3.map((s) => (
                <div key={s.sport} className="flex justify-between text-sm py-0.5">
                  <span className="text-gray-700">{s.sport}</span>
                  <span className="text-gray-800">
                    {f2(s.sans_club)} → <strong>{f2(s.avec_club)}</strong>
                  </span>
                </div>
              ))}
              <p className="text-xs text-gray-500 mt-3">
                Avoir un club sur place va avec plus de licences, mais ne comble pas l'écart. Et un club naît là où il y a déjà
                des pratiquants : association, pas causalité.
              </p>
            </div>
            <div className="bg-white border border-gray-200 rounded-xl p-5">
              <h3 className="font-semibold text-gray-900 mb-1">Quand un club arrive (2020 à 2022)</h3>
              <p className="text-xs text-gray-500 mb-3">Évolution des licences comparée à des quartiers sans changement (1 = aucun effet).</p>
              {data.test4.map((s) => (
                <div key={s.sport} className="flex justify-between text-sm py-0.5">
                  <span className="text-gray-700">
                    {s.sport} <span className="text-gray-400">({s.arrivees} cas)</span>
                  </span>
                  <span className="text-gray-800">
                    × {f2(s.effet_arrivee)} <span className="text-xs text-gray-400">[{f2(s.ic_bas)} ; {f2(s.ic_haut)}]</span>
                  </span>
                </div>
              ))}
              <p className="text-xs text-gray-500 mt-3">
                Là où les cas sont nombreux (football, judo, basket), l'arrivée d'un club ne change pas les licences de façon
                mesurable. Résultats fragiles : une seule année avant, Covid juste après.
              </p>
            </div>
          </div>
        </Section>

        <Section title="Dans le temps" description="Licences par sport, base 100 en 2013, et part des femmes parmi les licenciés.">
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-white border border-gray-200 rounded-xl p-4">
              <h3 className="font-semibold text-gray-900 mb-2 text-sm">Licences (base 100 en 2013)</h3>
              <ResponsiveContainer width="100%" height={260}>
                <LineChart data={serieIndice} margin={{ left: -10, right: 10 }}>
                  <XAxis dataKey="annee" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} domain={['auto', 'auto']} />
                  <Tooltip />
                  <Legend wrapperStyle={{ fontSize: 11 }} />
                  {data.evolution.slice(0, 5).map((s, i) => (
                    <Line key={s.sport} type="monotone" dataKey={s.sport} stroke={COULEURS_SERIES[i]} dot={false} strokeWidth={2} />
                  ))}
                </LineChart>
              </ResponsiveContainer>
            </div>
            <div className="bg-white border border-gray-200 rounded-xl p-4">
              <h3 className="font-semibold text-gray-900 mb-2 text-sm">Part des femmes parmi les licenciés (%)</h3>
              <ResponsiveContainer width="100%" height={260}>
                <LineChart data={serieFemmes} margin={{ left: -10, right: 10 }}>
                  <XAxis dataKey="annee" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} />
                  <Tooltip />
                  <Legend wrapperStyle={{ fontSize: 11 }} />
                  {data.femmes.map((s, i) => (
                    <Line key={s.sport} type="monotone" dataKey={s.sport} stroke={COULEURS_SERIES[i]} dot={false} strokeWidth={2} />
                  ))}
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
          <p className="text-xs text-gray-500 mt-3">
            Ruptures de série : en 2019, les licences non localisées sont intégrées (les années d'avant sont un peu plus basses) ;
            2020 et 2021 sont marquées par le Covid.
          </p>
        </Section>

        {data.elite_noms && (
          <Section
            title="L'élite : qui accède au haut niveau ?"
            description="Un sport ne recrute pas son élite au hasard : il la trouve là où il est pratiqué, dans les clubs et les centres de formation qui repèrent les jeunes. Regarder qui porte le maillot de l'équipe de France, c'est regarder les filières par lesquelles une société mène certains de ses enfants vers le haut niveau, et le sport comme voie d'ascension sociale."
          >
            <div className="bg-white border border-gray-200 rounded-xl p-6 mb-6 text-sm text-gray-700 space-y-2">
              <h3 className="font-semibold text-gray-900">Ce que l'on mesure, et comment</h3>
              <p>
                <strong>Les équipes</strong> : les internationaux de football, de rugby à XV, de basket et de handball, et la
                délégation française des Jeux de Paris 2024 comme repère tous sports (Wikidata et Wikipédia).
              </p>
              <p>
                <strong>L'indicateur</strong> : l'indice de diversité des noms (Kheddache et L'Horty, 2023). Un nom compte
                « diversité » s'il était absent des naissances en France avant 1950, ou s'il y est devenu au moins 15 fois plus
                fréquent depuis. C'est un indicateur de groupe : il ne dit rien d'une personne.
              </p>
              <p>
                <strong>La comparaison</strong> : chaque équipe est comparée à sa génération, pas à la France d'aujourd'hui, et le
                résultat est donné en fourchette. En bas, la génération à l'adolescence, en comptant tous les enfants immigrés
                présents vers 17 ans comme « diversité » (référence prudente) ; en haut, les seules naissances en France de la même
                période. Champ : les internationaux nés en France ; inclure ceux nés à l'étranger ne change presque rien.
              </p>
            </div>

            <div className="bg-white border border-gray-200 rounded-xl overflow-x-auto mb-2">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 text-gray-600">
                  <tr>
                    <th className="text-left px-4 py-2 font-medium">Équipe</th>
                    <th className="text-right px-4 py-2 font-medium">Nés de 1971 à 1990</th>
                    <th className="text-right px-4 py-2 font-medium">Nés depuis 1991</th>
                  </tr>
                </thead>
                <tbody>
                  {data.elite_noms.map((e) => (
                    <tr key={e.equipe} className="border-t border-gray-100">
                      <td className="px-4 py-2 text-gray-800">{e.equipe}</td>
                      {['p1971', 'p1991'].map((k) => (
                        <td key={k} className="px-4 py-2 text-right">
                          {e[k] ? (
                            <span className={e[k].bas > 1 ? 'font-semibold text-gray-900' : 'text-gray-700'}>
                              × {f1(e[k].bas)} à × {f1(e[k].haut)}
                            </span>
                          ) : (
                            <span className="text-gray-300">·</span>
                          )}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="text-xs text-gray-500 mb-6">
              Lecture : parmi les internationaux de football nés depuis 1991, la part de noms « diversité » est{' '}
              {f1(data.elite_noms[0]?.p1991?.bas)} à {f1(data.elite_noms[0]?.p1991?.haut)} fois celle de leur génération. Football
              féminin : toutes les joueuses nées depuis 1991 sont présentes, 76 % de celles nées de 1971 à 1990 ; on suppose que
              les absentes ressemblent aux présentes. Cases de moins de 30 noms non affichées.
            </p>

            <div className="space-y-3 mb-8">
              <ToneCallout tone="info">
                Prise dans son ensemble, l'élite sportive ressemble à sa génération : la délégation olympique de 2024 est à son
                niveau, voire en dessous pour les hommes. L'écart est propre au football et au basket, précisément les sports les
                plus pratiqués dans les quartiers populaires, comme le montrent les licences plus haut. Le rugby, pratiqué
                ailleurs, est en dessous.
              </ToneCallout>
              <ToneCallout tone="info">
                Le football masculin récent est le résultat le plus solide : il reste au-dessus de sa génération même avec une
                hypothèse volontairement excessive (compter tous les immigrés de la génération, y compris ceux arrivés adultes).
              </ToneCallout>
            </div>

            <h3 className="font-semibold text-gray-900 mb-2">D'où viennent les internationaux ?</h3>
            <p className="text-sm text-gray-600 mb-3">
              Internationaux nés dans un territoire, rapportés au nombre attendu d'après ses licenciés de 10 à 19 ans (nés en 1970
              et après ; licences 2013).
            </p>
            <div className="bg-white border border-gray-200 rounded-xl overflow-x-auto mb-3">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 text-gray-600">
                  <tr>
                    <th className="text-left px-4 py-2 font-medium">Territoire</th>
                    {['Football', 'Rugby', 'Basket', 'Handball'].map((s) => (
                      <th key={s} className="text-right px-3 py-2 font-medium">{s}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {data.elite_zones.map((z) => (
                    <tr key={z.zone} className="border-t border-gray-100">
                      <td className="px-4 py-2 text-gray-800">{z.zone}</td>
                      {['football', 'rugby à XV', 'basket-ball', 'handball'].map((s) => (
                        <td key={s} className="px-3 py-2 text-right">
                          {!z[s] ? (
                            '·'
                          ) : z[s].significatif ? (
                            <strong>× {f1(z[s].rapport)}</strong>
                          ) : (
                            <span className="text-gray-400">{z[s].observes <= 1 ? 'quasi nul' : 'non significatif'}</span>
                          )}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="space-y-3 mb-8">
              <ToneCallout tone="info">
                Le cœur de l'agglomération parisienne produit bien plus d'internationaux que ses licenciés ne le laissent attendre,
                dans tous les sports. Une partie de cet écart tient sans doute au lieu de naissance, qui n'est pas toujours celui
                où l'on grandit (les maternités sont concentrées en ville) : Kylian Mbappé est né à Paris et a grandi à Bondy.
                Au-delà de Paris et de Lyon, les départements urbains denses, et ceux où une part importante des habitants vit en
                quartier prioritaire, produisent un peu plus d'internationaux par licencié ; le nombre de clubs n'y est pour rien.
                L'outre-mer est un vivier du basket et du handball, pas du football.
              </ToneCallout>
            </div>

            <h3 className="font-semibold text-gray-900 mb-2">Ce que ces chiffres ne disent pas</h3>
            <ul className="list-disc pl-6 space-y-1.5 text-sm text-gray-700">
              <li>
                Ils ne disent pas qui est français, ni d'où viennent les familles : presque tous les joueurs comptés sont nés en
                France. Un nom n'est pas une origine, encore moins une identité.
              </li>
              <li>
                L'indice ne voit pas les migrations anciennes : les grandes vagues italienne, polonaise, espagnole et portugaise
                d'avant 1950 n'y apparaissent pas, et beaucoup de grands joueurs français issus de l'immigration n'y sont pas
                comptés. Une hausse dans le temps vient donc en partie de l'outil lui-même, d'où la comparaison à chaque génération.
              </li>
              <li>
                Ils ne mesurent pas une cause : ils décrivent des filières (où chaque sport est pratiqué, qui il repère, à qui il
                ouvre le haut niveau).
              </li>
              <li>Ce que nous ne publions pas : aucun résultat par joueur, aucun classement de départements, aucune case de moins de 30 noms.</li>
            </ul>
            <p className="text-xs text-gray-400 mt-4">
              Sources : Wikidata et Wikipédia (listes des internationaux) ; Insee, fichier des noms de famille et recensement 2023
              (immigrés par âge) ; INJEP, licences 2013 et 2023.
            </p>
          </Section>
        )}

        <Section title="Méthode et limites">
          <div className="space-y-3">
            <ToneCallout tone="info">
              Une licence est une adhésion à un club fédéré, comptée au domicile du licencié : le sport hors club (course seul,
              salle privée, foot de rue) n'y figure pas, et une personne peut avoir plusieurs licences. Les fédérations scolaires
              et universitaires, comptées à l'adresse de l'établissement, sont exclues. Les chiffres par commune sont des
              estimations de l'INJEP.
            </ToneCallout>
            <ToneCallout tone="info">
              Les licences sont comptées par fédération, pas par activité. Les fédérations multisports (UFOLEP, FSGT, Léo
              Lagrange, gymnastique volontaire, handisport, sport adapté…) regroupent{' '}
              {data.multisport ? `${f1(data.multisport.part)} % des licences` : 'une part importante des licences'} sans dire quel
              sport est pratiqué (une licence multisport ouvre droit à toutes leurs disciplines et ne les mentionne en général
              pas) : elles comptent dans les totaux, mais jamais dans les comparaisons par sport. Comme dans les statistiques
              officielles, « football » désigne donc la seule Fédération française de football : le foot joué à la FSGT ou à
              l'UFOLEP n'y est pas compté.
            </ToneCallout>
            <ToneCallout tone="warn">
              Un quartier prioritaire n'est pas une origine : il désigne un territoire à bas revenus. Les comparaisons par revenu
              portent sur des communes, pas sur des familles. Rien ici n'établit de cause : les équipements et les clubs ne sont
              pas placés au hasard.
            </ToneCallout>
            <ToneCallout tone="warn">
              Quartiers : géographie 2024, quartiers situés dans une seule commune ; population des quartiers 2020 et des
              communes 2021. Équipements : état 2025-2026, partagés entre sports et avec les scolaires ; l'adresse d'un club est
              souvent celle de son siège.
            </ToneCallout>
          </div>
          <p className="text-xs text-gray-400 mt-6">
            Sources :{' '}
            {data.sources.map((s, i) => (
              <span key={s.url}>
                {i > 0 && ' · '}
                <a href={s.url} target="_blank" rel="noopener noreferrer" className="underline hover:text-gray-600">
                  {s.label}
                </a>
              </span>
            ))}
          </p>
        </Section>
      </div>
    </div>
  )
}
