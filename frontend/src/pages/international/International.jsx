import { useEffect, useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Globe, ArrowRight, Table2, Flag, GraduationCap } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import OutsidersScatter from '../../components/charts/OutsidersScatter'
import { DECOUPAGE_BY_ID } from '../../config/decoupages'
import { useRouteMeta } from '../../lib/meta'

const d = DECOUPAGE_BY_ID['pays']
const IND_BY_ID = Object.fromEntries(d.indicateurs.map((i) => [i.id, i]))

// Rang favorable de la France (1 = la mieux placée) ; pour les indicateurs
// descriptifs (sens neutre), rang de la valeur la plus haute.
function rangFrance(categories, ind) {
  const vals = categories.map((c) => ({ id: c.id, v: c.valeurs[ind.id] })).filter((x) => x.v != null)
  if (!vals.length) return null
  const haut = ind.sens === 'bas' ? false : true
  vals.sort((a, b) => (haut ? b.v - a.v : a.v - b.v))
  const i = vals.findIndex((x) => x.id === 'fr')
  return i < 0 ? null : { rang: i + 1, n: vals.length }
}

function valeur(categories, id, indId) {
  return categories.find((c) => c.id === id)?.valeurs?.[indId] ?? null
}

// ─────────────── Carte d'identité : un dot-plot par indicateur ───────────────
function DotPlot({ ind, categories, references }) {
  const vals = categories.map((c) => ({ ...c, v: c.valeurs[ind.id] })).filter((x) => x.v != null)
  if (vals.length < 2) return null
  const min = vals.reduce((a, b) => (a.v <= b.v ? a : b))
  const max = vals.reduce((a, b) => (a.v >= b.v ? a : b))
  const fr = vals.find((x) => x.id === 'fr')
  const ue = references[ind.id]
  const pos = (v) => ((v - min.v) / (max.v - min.v)) * 100
  const r = rangFrance(categories, ind)
  const tiers = r ? (r.rang - 1) / (r.n - 1) : null
  const rangCouleur =
    ind.sens === 'neutre' || tiers == null ? '#64748B' : tiers <= 0.34 ? '#059669' : tiers >= 0.66 ? '#DC2626' : '#D97706'
  const rangTexte = r
    ? ind.sens === 'neutre'
      ? `${r.rang}ᵉ valeur la plus haute sur ${r.n}`
      : `${r.rang}ᵉ sur ${r.n}`
    : 'n/d'

  return (
    <div className="py-3 border-b border-gray-100 last:border-0">
      <div className="flex items-baseline justify-between gap-3 mb-1.5">
        <div className="text-sm font-medium text-gray-800" title={ind.aide}>
          {ind.label}
        </div>
        <div className="text-sm font-semibold shrink-0" style={{ color: rangCouleur }}>
          {fr ? ind.fmt(fr.v) : 'n/d'} · {rangTexte}
        </div>
      </div>
      <div className="relative h-6">
        {/* piste min → max */}
        <div className="absolute top-1/2 -translate-y-1/2 left-0 right-0 h-1.5 rounded-full bg-gray-100" />
        {/* repère UE27 */}
        {ue != null && (
          <div
            className="absolute top-1/2 -translate-y-1/2 w-0.5 h-4 bg-gray-400"
            style={{ left: `${pos(ue)}%` }}
            title={`Moyenne UE27 : ${ind.fmt(ue)}`}
          />
        )}
        {/* point France */}
        {fr && (
          <div
            className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 w-3.5 h-3.5 rounded-full bg-blue-600 border-2 border-white shadow"
            style={{ left: `${pos(fr.v)}%` }}
            title={`France : ${ind.fmt(fr.v)}`}
          />
        )}
      </div>
      <div className="flex justify-between text-[11px] text-gray-400">
        <span>{min.nom} {ind.fmt(min.v)}</span>
        {ue != null && <span>| moyenne UE27 {ind.fmt(ue)}</span>}
        <span>{max.nom} {ind.fmt(max.v)}</span>
      </div>
    </div>
  )
}

// ─────────────────────────── Trajectoires ───────────────────────────
function Trajectoire({ series, indId }) {
  const ind = IND_BY_ID[indId]
  const data = (series?.[indId] || []).filter((p) => p.fr != null || p.ue != null)
  if (!data.length) return <p className="text-sm text-gray-400">Pas de série disponible.</p>
  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data} margin={{ top: 10, right: 15, bottom: 5, left: 0 }}>
        <XAxis dataKey="a" tick={{ fontSize: 11 }} minTickGap={25} />
        <YAxis tick={{ fontSize: 11 }} domain={['auto', 'auto']} width={45} />
        <Tooltip
          content={({ payload, label }) => {
            if (!payload?.length) return null
            const row = payload[0].payload
            return (
              <div className="bg-gray-900 text-white text-xs rounded-lg px-2.5 py-1.5">
                <div className="font-semibold">{label}</div>
                <div>France : {row.fr == null ? 'n/d' : ind.fmt(row.fr)}</div>
                <div>Moyenne UE27 : {row.ue == null ? 'n/d' : ind.fmt(row.ue)}</div>
              </div>
            )
          }}
        />
        <Line type="monotone" dataKey="ue" name="Moyenne UE27" stroke="#9CA3AF" strokeWidth={2} strokeDasharray="6 4" dot={false} connectNulls />
        <Line type="monotone" dataKey="fr" name="France" stroke="#3B82F6" strokeWidth={2.5} dot={false} connectNulls />
      </LineChart>
    </ResponsiveContainer>
  )
}

// ─────────────────────────────── Page ───────────────────────────────
export default function International() {
  useRouteMeta('/international')
  const navigate = useNavigate()
  const [data, setData] = useState(null)
  const [pair, setPair] = useState({ x: 'dep_publiques', y: 'pauvrete_enfants' })
  const [traj, setTraj] = useState('mortalite_infantile')

  useEffect(() => {
    fetch(d.dataUrl).then((r) => r.json()).then(setData).catch(() => {})
  }, [])

  const scatterPoints = useMemo(() => {
    if (!data) return []
    return data.categories
      .map((c) => ({ code: c.id, nom: c.nom, x: c.valeurs[pair.x], y: c.valeurs[pair.y], pop: null }))
      .filter((p) => p.x != null && p.y != null)
  }, [data, pair])

  if (!data)
    return <div className="py-20 text-center text-gray-400">Chargement…</div>

  const { categories, references = {}, series = {}, sources = {} } = data
  const v = (id, ind) => valeur(categories, id, ind)
  const frDep = v('fr', 'dep_publiques')
  const frPauv = v('fr', 'pauvrete_enfants')
  const rMort = rangFrance(categories, IND_BY_ID.mortalite_infantile)
  const rEsp = rangFrance(categories, IND_BY_ID.esperance_vie)
  const dep2e = [...categories]
    .filter((c) => c.valeurs.dep_publiques != null && c.id !== 'fr')
    .sort((a, b) => b.valeurs.dep_publiques - a.valeurs.dep_publiques)[0]
  // Rang de la France sur les dépenses (compté du plus haut au plus bas) : la Finlande
  // passe devant en 2024 et 2025, le texte ne doit pas parler de record par défaut.
  const depVals = categories.map((c) => c.valeurs.dep_publiques).filter((x) => x != null)
  const depRang = frDep != null ? depVals.filter((x) => x > frDep).length + 1 : null
  const depPremier = dep2e && frDep != null && dep2e.valeurs.dep_publiques > frDep ? dep2e : null
  const depPhrase = depRang === 1
    ? `record des ${depVals.length} pays${dep2e ? ` (${dep2e.nom} suit à ${dep2e.valeurs.dep_publiques.toLocaleString('fr-FR')} %)` : ''}`
    : `${depRang}ᵉ rang des ${depVals.length} pays${depPremier ? `, derrière ${depPremier.nom === 'Finlande' ? 'la Finlande' : depPremier.nom} (${depPremier.valeurs.dep_publiques.toLocaleString('fr-FR')} %)` : ''}`
  const pauvVals = categories.map((c) => c.valeurs.pauvrete_enfants).filter((x) => x != null)
  const pauvPires = frPauv != null ? pauvVals.filter((x) => x > frPauv).length : null

  const scrollTo = (id) => document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' })
  const paires = [
    {
      titre: "L'État et les enfants",
      texte: `${frDep?.toLocaleString('fr-FR')} % du PIB de dépenses publiques, ${depPhrase}. Et pourtant ${frPauv?.toLocaleString('fr-FR')} % des moins de 18 ans sont menacés de pauvreté ou d'exclusion, plus que la moyenne UE (${references.pauvrete_enfants?.toLocaleString('fr-FR')} %) : seuls ${pauvPires} des ${pauvVals.length} pays disponibles font pire. Ce contraste ne dit pas à lui seul ce que vaut la dépense, qui finance d'abord les retraites et la santé.`,
      action: () => { setPair({ x: 'dep_publiques', y: 'pauvrete_enfants' }); scrollTo('nuage') },
      cta: 'Voir le nuage dépenses × pauvreté',
    },
    {
      titre: 'Le paradoxe sanitaire',
      texte: `Espérance de vie au ${rEsp ? `${rEsp.rang}ᵉ rang sur ${rEsp.n}` : 'sommet'} (${v('fr', 'esperance_vie')} ans), mais mortalité infantile ${rMort ? `${rMort.rang}ᵉ sur ${rMort.n}` : 'déclassée'} : meilleure que la moyenne européenne jusqu'en 2014, la France est passée au-dessus en 2015 et l'écart s'est creusé depuis. Les comparaisons dépendent en partie de la façon dont chaque pays enregistre les naissances très prématurées.`,
      action: () => { setTraj('mortalite_infantile'); scrollTo('trajectoires') },
      cta: 'Voir la trajectoire du décrochage',
    },
    {
      titre: 'École et égalité',
      texte: `Le naufrage scolaire annoncé n'a pas lieu : ${v('fr', 'decrochage')} % de décrochage, mieux que la moyenne UE (${references.decrochage} %) et que l'Allemagne (${v('de', 'decrochage')} %). Et le pays qui se croit égalitaire est moyen : Gini de ${v('fr', 'gini')}, contre ${references.gini} en moyenne UE.`,
      action: () => { setPair({ x: 'dep_publiques', y: 'decrochage' }); scrollTo('nuage') },
      cta: 'Voir le nuage dépenses × décrochage',
    },
    {
      titre: 'Le travail',
      texte: `« Les Français ne travaillent pas » : la semaine des temps pleins (${v('fr', 'heures_tp')} h) est quasi identique à la moyenne UE (${references.heures_tp} h). L'écart est ailleurs : ${v('fr', 'emploi_seniors')} % des 55-64 ans en emploi, contre ${references.emploi_seniors} % en moyenne UE.`,
      action: () => { setTraj('emploi_seniors'); scrollTo('trajectoires') },
      cta: "Voir la trajectoire de l'emploi des seniors",
    },
  ]

  const enBref = [
    { chiffre: `${frDep?.toLocaleString('fr-FR')} %`, label: `du PIB de dépenses publiques : ${depRang === 1 ? `record des ${depVals.length} pays comparés` : `${depRang}ᵉ des ${depVals.length} pays comparés`}` },
    { chiffre: '1 sur 4', label: `enfants menacés de pauvreté ou d'exclusion (${frPauv?.toLocaleString('fr-FR')} %), plus que la moyenne UE` },
    { chiffre: `${rMort ? `${rMort.rang}ᵉ/${rMort.n}` : 'n/d'}`, label: 'pour la mortalité infantile, longtemps meilleure que la moyenne européenne' },
  ]

  return (
    <div className="py-10">
      {/* En-tête */}
      <div className="max-w-4xl mx-auto px-4">
        <div className="flex items-center gap-2 text-blue-600 mb-2">
          <Globe size={20} />
          <span className="text-sm font-semibold uppercase tracking-wide">Dossier · 30 pays européens</span>
        </div>
        <h1 className="text-4xl font-bold text-gray-900 mb-3">Où se situe la France ?</h1>
        <p className="text-lg text-gray-600 max-w-3xl mb-8">
          On dit la France championne des impôts, égalitaire, dotée du meilleur système de santé du
          monde, et fâchée avec le travail. Les données européennes harmonisées permettent de
          vérifier : parfois le cliché tient, souvent il se retourne. Huit indicateurs, 30 pays
          (Union européenne, Islande, Norvège, Suisse), sources Eurostat.
        </p>

        {/* En bref */}
        <div className="grid sm:grid-cols-3 gap-4 mb-12">
          {enBref.map((s, i) => (
            <div key={i} className="bg-gray-50 border border-gray-200 rounded-xl px-5 py-4">
              <div className="text-3xl font-black text-blue-600 mb-1">{s.chiffre}</div>
              <div className="text-sm text-gray-600">{s.label}</div>
            </div>
          ))}
        </div>

        {/* Carte d'identité */}
        <h2 className="text-2xl font-bold text-gray-900 mb-1">La carte d'identité européenne de la France</h2>
        <p className="text-gray-600 mb-4 max-w-3xl">
          Chaque ligne va du pays le plus bas au plus haut ; le point bleu est la France, le trait
          gris la moyenne UE27. Le rang est compté du meilleur au moins bon quand l'indicateur a un
          sens favorable, en gris quand il est simplement descriptif.
        </p>
        <div className="bg-white border border-gray-200 rounded-xl px-5 py-2 mb-4">
          {d.indicateurs.map((ind) => (
            <DotPlot key={ind.id} ind={ind} categories={categories} references={references} />
          ))}
        </div>
        <p className="text-xs text-gray-400 mb-12">
          Sources :{' '}
          {Object.values(sources).map((s, i) => (
            <span key={s.url}>
              {i > 0 && ' · '}
              <a href={s.url} target="_blank" rel="noopener noreferrer" className="underline hover:text-gray-600">{s.label}</a>
            </span>
          ))}
          . Définitions harmonisées par Eurostat ; millésimes 2024-2025 selon l'indicateur.
        </p>

        {/* Les 4 histoires */}
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Quatre histoires que racontent ces chiffres</h2>
        <div className="grid sm:grid-cols-2 gap-5 mb-12">
          {paires.map((p) => (
            <div key={p.titre} className="bg-white border border-gray-200 rounded-xl p-5 flex flex-col">
              <h3 className="font-semibold text-gray-900 mb-2">{p.titre}</h3>
              <p className="text-sm text-gray-600 leading-relaxed flex-1">{p.texte}</p>
              <button
                onClick={p.action}
                className="mt-3 inline-flex items-center gap-1.5 text-sm font-medium text-blue-600 hover:text-blue-700 self-start"
              >
                {p.cta} <ArrowRight size={15} />
              </button>
            </div>
          ))}
        </div>

        {/* Nuage de pronostic */}
        <section id="nuage" className="scroll-mt-20 mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-1">Que rapporte la dépense publique ?</h2>
          <p className="text-gray-600 mb-4 max-w-3xl">
            La signature Outsiders, appliquée aux pays : la droite donne le pronostic (à dépense
            donnée, le résultat « attendu ») et les pays qui s'en écartent deviennent les vraies
            questions. Choisissez ce que la dépense est censée acheter.
          </p>
          <div className="flex flex-wrap items-center gap-2 mb-4">
            <span className="text-sm text-gray-500">Résultat :</span>
            {d.indicateurs.filter((i) => i.sens !== 'neutre').map((i) => (
              <button
                key={i.id}
                onClick={() => setPair({ x: 'dep_publiques', y: i.id })}
                className={`px-3 py-1 rounded-full text-sm border transition-colors ${
                  pair.y === i.id ? 'bg-blue-600 border-blue-600 text-white' : 'border-gray-200 text-gray-600 hover:border-blue-300'
                }`}
              >
                {i.court || i.label}
              </button>
            ))}
          </div>
          <div className="bg-white border border-gray-200 rounded-xl p-5">
            <OutsidersScatter
              points={scatterPoints}
              xLabel={IND_BY_ID[pair.x].label}
              xUnit={IND_BY_ID[pair.x].unite}
              xFmt={IND_BY_ID[pair.x].fmt}
              yLabel={IND_BY_ID[pair.y].label}
              yUnit={IND_BY_ID[pair.y].unite}
              yFmt={IND_BY_ID[pair.y].fmt}
              mots={{ sing: 'pays', plur: 'pays' }}
              onSelect={(code) => navigate(`/explorer/pays?cat=${code}`)}
            />
          </div>
        </section>

        {/* Trajectoires */}
        <section id="trajectoires" className="scroll-mt-20 mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-1">La France décroche-t-elle ?</h2>
          <p className="text-gray-600 mb-4 max-w-3xl">
            Un rang ne dit pas d'où l'on vient. Les trajectoires depuis 1995 montrent si la France
            converge vers la moyenne européenne, ou s'en éloigne.
          </p>
          <div className="flex flex-wrap items-center gap-2 mb-4">
            {d.indicateurs.filter((i) => (series[i.id] || []).length > 4).map((i) => (
              <button
                key={i.id}
                onClick={() => setTraj(i.id)}
                className={`px-3 py-1 rounded-full text-sm border transition-colors ${
                  traj === i.id ? 'bg-blue-600 border-blue-600 text-white' : 'border-gray-200 text-gray-600 hover:border-blue-300'
                }`}
              >
                {i.court || i.label}
              </button>
            ))}
          </div>
          <div className="bg-white border border-gray-200 rounded-xl p-5">
            <div className="flex items-center gap-4 text-xs text-gray-500 mb-2">
              <span className="inline-flex items-center gap-1.5"><span className="w-4 h-0.5 bg-blue-600 inline-block" /> France</span>
              <span className="inline-flex items-center gap-1.5"><span className="w-4 h-0.5 bg-gray-400 inline-block" style={{ borderTop: '2px dashed #9CA3AF', height: 0 }} /> Moyenne UE27</span>
            </div>
            <Trajectoire series={series} indId={traj} />
            {traj === 'mortalite_infantile' && (
              <p className="text-sm text-gray-600 mt-2">
                La preuve du décrochage : nettement meilleure que la moyenne européenne dans les
                années 2000, la mortalité infantile française croise la moyenne UE vers 2015, puis
                remonte (3,5 ‰ en 2012, 4,1 ‰ en 2024) pendant que l'Europe continue de baisser.
              </p>
            )}
          </div>
        </section>

        {/* Explorer */}
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Explorer par vous-même</h2>
        <div className="grid sm:grid-cols-2 gap-5 mb-10">
          <Link to="/explorer/pays" className="group bg-white border border-gray-200 rounded-xl p-5 hover:shadow-md hover:border-gray-300 transition-all">
            <div className="flex items-center gap-2 mb-2 text-blue-600"><Table2 size={18} /><span className="font-semibold text-gray-900">Le classement des 30 pays</span></div>
            <p className="text-sm text-gray-600">
              Pays en lignes, indicateurs au choix, tri par colonne, moyenne UE27 en repère.
              Présélections : là où la France est forte, moyenne, faible.
            </p>
            <span className="inline-flex items-center gap-1 text-sm font-medium text-blue-600 mt-2">Ouvrir le tableau <ArrowRight size={14} className="group-hover:translate-x-0.5 transition-transform" /></span>
          </Link>
          <Link to="/international/pisa" className="group sm:col-span-2 bg-white border border-gray-200 rounded-xl p-5 hover:shadow-md hover:border-gray-300 transition-all sm:order-last">
            <div className="flex items-center gap-2 mb-2 text-blue-600"><GraduationCap size={18} /><span className="font-semibold text-gray-900">PISA 2025 : la France décroche-t-elle ?</span></div>
            <p className="text-sm text-gray-600">
              Au-delà de l'Europe : les compétences des élèves de 15 ans dans 91 pays et économies.
              Le score, le rang, ce qu'on peut attendre de la France, et ce que la critique dit de
              vrai, à partir des tableaux de l'OCDE.
            </p>
            <span className="inline-flex items-center gap-1 text-sm font-medium text-blue-600 mt-2">Ouvrir le dossier <ArrowRight size={14} className="group-hover:translate-x-0.5 transition-transform" /></span>
          </Link>
          <Link to="/explorer/pays?cat=fr" className="group bg-white border border-gray-200 rounded-xl p-5 hover:shadow-md hover:border-gray-300 transition-all">
            <div className="flex items-center gap-2 mb-2 text-blue-600"><Flag size={18} /><span className="font-semibold text-gray-900">La fiche France</span></div>
            <p className="text-sm text-gray-600">
              Les huit indicateurs situés parmi les 30 pays, avec les extrêmes détectés
              automatiquement. Chaque pays a la sienne.
            </p>
            <span className="inline-flex items-center gap-1 text-sm font-medium text-blue-600 mt-2">Ouvrir la fiche <ArrowRight size={14} className="group-hover:translate-x-0.5 transition-transform" /></span>
          </Link>
        </div>

        <p className="text-xs text-gray-400 max-w-3xl">
          {data.note} Un rang n'est pas un palmarès de précision : à quelques dixièmes près, des
          pays sont interchangeables. Corrélation entre pays n'est pas causalité, et un pronostic
          n'est pas un objectif.
        </p>
      </div>
    </div>
  )
}
