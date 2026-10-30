import { useEffect, useMemo, useState } from 'react'
import { useSearchParams, Link } from 'react-router-dom'
import { Loader2, Users, Shuffle, SplitSquareHorizontal, ChevronDown, GraduationCap, ArrowRight } from 'lucide-react'
import TerritoireSearch from '../../components/TerritoireSearch'
import CarreauxMap from '../../components/charts/CarreauxMap'
import MixiteScatter from '../../components/charts/MixiteScatter'
import { useRouteMeta, usePageMeta } from '../../lib/meta'
import { depFromInsee } from '../../lib/territoire'
import { regionOfDep } from '../../lib/regions'
import Toggle from '../../components/Toggle'

const norm = (s) => String(s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase()

// Couleurs par axe. Mélange interne : fort = vert (quartiers divers), faible = gris.
function mixColor(s) {
  if (s == null) return '#9ca3af'
  if (s >= 66) return '#10B981'
  if (s >= 33) return '#34d399'
  return '#cbd5e1'
}
// Séparation entre quartiers : forte = rouge, faible = vert (ensemble).
function sepColor(s) {
  if (s == null) return '#9ca3af'
  if (s >= 66) return '#EF4444'
  if (s >= 33) return '#F59E0B'
  return '#10B981'
}
const TYPO_COLOR = {
  'Mélangée': '#10B981', 'Peu séparée': '#14B8A6', 'Homogène': '#64748b',
  'Contrastée': '#F59E0B', 'Fracturée': '#EF4444',
}
const typoColor = (t) => TYPO_COLOR[t] || '#9ca3af'

// Couleur du niveau de vie (le cadre : riche / moyen / modeste).
function niveauColor(n) {
  if (n === 'Très aisée' || n === 'Aisée') return '#6366F1'
  if (n === 'Modeste' || n === 'Très modeste') return '#EA580C'
  return '#64748b'
}

// Nombre à une décimale, format français (3.8 -> « 3,8 »).
const fr1 = (x) => (x == null ? '?' : x.toLocaleString('fr-FR', { minimumFractionDigits: 1, maximumFractionDigits: 1 }))

function Gauge({ titre, icon: Icon, score, label, value, help, phrase, tone }) {
  const c = tone === 'mix' ? mixColor(score) : sepColor(score)
  const [gauche, droite] = tone === 'mix' ? ['Homogènes', 'Très mélangés'] : ['Semblables', 'Très séparés']
  return (
    <div className="bg-white border border-gray-200 rounded-2xl p-6">
      <div className="flex items-center gap-2 text-sm font-semibold text-gray-500 mb-2">
        <Icon size={18} /> {titre}
      </div>
      {value ? (
        <div className="flex items-baseline gap-2 mb-3">
          <span className="text-3xl font-bold" style={{ color: c }}>{value}</span>
          <span className="text-base font-semibold text-gray-600">{label}</span>
        </div>
      ) : (
        <div className="text-2xl font-bold mb-3" style={{ color: c }}>{label ?? 'n/d'}</div>
      )}
      <div className="h-2.5 rounded-full bg-gray-100 overflow-hidden mb-1">
        <div className="h-full rounded-full" style={{ width: `${score ?? 0}%`, backgroundColor: c }} />
      </div>
      <div className="flex justify-between text-xs text-gray-400 mb-3">
        <span>{gauche}</span><span>{droite}</span>
      </div>
      {help && <p className="text-xs text-gray-400 leading-relaxed">{help}</p>}
      {phrase && <p className="text-sm text-gray-700 mt-2 leading-relaxed">{phrase}</p>}
    </div>
  )
}

// Composition des quartiers : part des habitants par type de carreau.
function CompositionQuartiers({ q }) {
  if (!q || q.pct_mixtes == null) return null
  const segs = [
    { pct: q.pct_mixtes, color: '#10B981', label: 'quartiers mixtes' },
    { pct: q.pct_aises, color: '#6366F1', label: 'homogènes aisés' },
    { pct: q.pct_pauvres, color: '#64748b', label: 'homogènes pauvres' },
  ]
  return (
    <div className="bg-white border border-gray-200 rounded-2xl p-6 mb-6">
      <h3 className="font-bold text-gray-900 mb-1">De quoi sont faits ses quartiers ?</h3>
      <p className="text-sm text-gray-500 mb-4">
        Part des habitants vivant dans un quartier (carré de 200 m) qui mélange les revenus,
        qui n'a presque pas de pauvres, ou au contraire à forte pauvreté.
      </p>
      <div className="flex h-6 rounded-full overflow-hidden mb-3 bg-gray-100">
        {segs.map((s, i) => s.pct > 0 && <div key={i} style={{ width: `${s.pct}%`, backgroundColor: s.color }} />)}
      </div>
      <div className="flex flex-wrap gap-x-6 gap-y-1 text-sm text-gray-700">
        {segs.map((s, i) => (
          <span key={i} className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-sm shrink-0" style={{ backgroundColor: s.color }} />
            <strong>{s.pct} %</strong> {s.label}
          </span>
        ))}
      </div>
    </div>
  )
}

// Et l'école ? Les collèges sont-ils plus triés que les quartiers (évitement) ?
function EcoleBloc({ ecole, sep }) {
  if (!ecole) return null
  const ec = ecole.ecart_ecole_logement
  const tone = ec == null ? '#64748b' : ec > 15 ? '#EF4444' : ec < -15 ? '#10B981' : '#F59E0B'
  const verdict = ec == null ? 'Données scolaires partielles pour cette ville.'
    : ec > 15 ? "Les collèges y sont bien plus triés socialement que les quartiers : le signe d'un évitement scolaire, souvent une fuite vers le privé."
    : ec < -15 ? "Les collèges y sont plus mélangés que ne le sont les quartiers."
    : "Les collèges y reflètent à peu près la composition des quartiers."
  return (
    <div className="bg-white border border-gray-200 rounded-2xl p-6 mb-6" style={{ borderLeft: `4px solid ${tone}` }}>
      <h3 className="font-bold text-gray-900 mb-1">Et l'école ?</h3>
      <p className="text-sm text-gray-700 mb-3 leading-relaxed">{verdict}</p>
      {ecole.ips_public != null && ecole.ips_prive != null && (
        <p className="text-sm text-gray-600">
          IPS moyen des collèges : <strong>public {ecole.ips_public}</strong> · <strong>privé {ecole.ips_prive}</strong>
          {ecole.gap_pub_pr != null ? ` (écart de ${ecole.gap_pub_pr} points en faveur du privé)` : ''}.
        </p>
      )}
      <p className="text-xs text-gray-400 mt-2">
        {ecole.n_colleges} collèges. Ségrégation scolaire au {ecole.ips_std_pct}ᵉ percentile national, logement au {sep}ᵉ.
      </p>
      <Link to="/terrains/ecole" className="inline-flex items-center gap-1.5 mt-3 text-sm font-medium text-violet-600 hover:text-violet-700">
        <GraduationCap size={16} /> Le dossier École : où l'école trie plus que le quartier <ArrowRight size={14} />
      </Link>
    </div>
  )
}

function Fiche({ code }) {
  const [data, setData] = useState(null)
  const [erreur, setErreur] = useState(false)
  useEffect(() => {
    setData(null); setErreur(false)
    fetch(`/data/segregation/${code}.json`)
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then(setData)
      .catch(() => setErreur(true))
  }, [code])

  usePageMeta(data ? `Ségrégation à ${data.nom} : quartiers, revenus, âges` : null)

  if (erreur)
    return <p className="text-gray-500 py-10 text-center">Cette ville n'est pas dans l'analyse (communes de plus de 10 000 habitants uniquement).</p>
  if (!data)
    return <div className="py-16 text-center text-gray-400"><Loader2 className="animate-spin inline" /> Chargement…</div>

  const { nom, pop, revenu, age, carreaux, quartiers, pop_couverte, pct_impute } = data
  const nc = niveauColor(revenu.niveau)
  return (
    <section className="mb-14">
      <div className="mb-5">
        <h2 className="text-3xl font-bold text-gray-900">{nom}</h2>
        <p className="text-gray-500">{pop.toLocaleString('fr-FR')} habitants · analyse sur {carreaux.length} carreaux de 200 m</p>
      </div>

      {/* Le cadre : niveau de vie global, pour ne pas confondre mélange interne et diversité sociale. */}
      <div className="rounded-2xl p-6 mb-4" style={{ backgroundColor: `${nc}12`, border: `1px solid ${nc}33` }}>
        <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1 mb-2">
          <span className="text-xl font-bold" style={{ color: nc }}>{revenu.niveau ?? 'Niveau inconnu'}</span>
          <span className="text-gray-600">niveau de vie médian {revenu.p50.toLocaleString('fr-FR')} €/an</span>
          {revenu.niveau_score != null && (
            <span className="text-sm text-gray-400">plus aisée que {revenu.niveau_score} % des villes</span>
          )}
        </div>
        {revenu.phrase && <p className="text-gray-800 leading-relaxed">{revenu.phrase}</p>}
      </div>

      {/* Les deux axes du revenu. */}
      <div className="grid md:grid-cols-2 gap-4 mb-8">
        <Gauge tone="mix" titre="Mélange dans les quartiers" icon={Shuffle}
          score={revenu.melange_interne} label={revenu.melange_label} value={revenu.interne_rd != null ? `×${fr1(revenu.interne_rd)}` : null}
          help="Dans le quartier type, les 10 % les plus aisés gagnent autant de fois les 10 % les plus modestes (rapport interdécile des IRIS, source INSEE). Plus c'est élevé, plus le quartier mélange." />
        <Gauge tone="sep" titre="Écart entre quartiers" icon={SplitSquareHorizontal}
          score={revenu.separation} label={revenu.separation_label} value={revenu.p90_p10 != null ? `×${fr1(revenu.p90_p10)}` : null}
          help="Le quartier le plus aisé de la ville a un niveau de vie de tant de fois celui du plus modeste. Plus c'est élevé, plus les quartiers sont à part." />
      </div>

      <CompositionQuartiers q={quartiers} />

      <div className="bg-white border border-gray-200 rounded-2xl p-6 mb-6">
        <h3 className="font-bold text-gray-900 mb-1">La carte des quartiers</h3>
        <p className="text-sm text-gray-500 mb-4">
          Chaque point est un carré de 200 m, coloré par le niveau de vie moyen de ses habitants.
          Des couleurs mélangées = une ville qui fait cohabiter ; de grandes plages séparées = une ville en damier.
        </p>
        <CarreauxMap carreaux={carreaux} />
      </div>

      <EcoleBloc ecole={data.ecole} sep={revenu.separation} />

      <div className="mb-6">
        <Gauge tone="sep" titre="Âges" icon={Users} score={age.tri} label={age.typologie}
          help="Les jeunes et les seniors habitent-ils les mêmes quartiers, ou des quartiers différents ?"
          phrase={age.phrase} />
      </div>

      <details className="text-sm text-gray-500">
        <summary className="cursor-pointer font-medium text-gray-600">Détail des indicateurs</summary>
        <div className="mt-2 grid sm:grid-cols-2 gap-x-8 gap-y-1">
          <div>Rapport interdécile médian des quartiers : <strong>{revenu.interne_rd ?? 'n/d'}</strong></div>
          <div>Taux de pauvreté de la ville : <strong>{revenu.taux_pauvrete} %</strong></div>
          <div>Écart quartier aisé / modeste (carreaux, P90/P10) : <strong>{revenu.p90_p10}×</strong></div>
          <div>Quartiers IRIS analysés : <strong>{revenu.n_iris ?? 0}</strong></div>
          <div>Population couverte : <strong>{pop_couverte.toLocaleString('fr-FR')}</strong></div>
          <div>Carreaux à revenu imputé (exclus) : <strong>{pct_impute} %</strong></div>
        </div>
      </details>
    </section>
  )
}

function Tag({ typo }) {
  return <span className="text-xs font-medium shrink-0" style={{ color: typoColor(typo) }}>{typo}</span>
}

function Colonne({ titre, sous, villes, onSelect }) {
  return (
    <div>
      <h3 className="font-bold text-gray-900">{titre}</h3>
      <p className="text-sm text-gray-500 mb-3">{sous}</p>
      <ol className="space-y-1">
        {villes.map((v, i) => (
          <li key={v.code}>
            <button onClick={() => onSelect(v.code)} className="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-50 text-left">
              <span className="w-5 text-sm text-gray-400 tabular-nums">{i + 1}</span>
              <span className="flex-1 text-gray-900 truncate">{v.nom}</span>
              <span className="text-xs text-gray-400 hidden sm:inline">{v.revenu.niveau}</span>
              <Tag typo={v.revenu.typologie} />
            </button>
          </li>
        ))}
      </ol>
    </div>
  )
}

export default function Segregation() {
  useRouteMeta('/segregation')
  const [params, setParams] = useSearchParams()
  const ville = params.get('ville')
  const [villes, setVilles] = useState(null)
  const [deps, setDeps] = useState([])
  const [terrMode, setTerrMode] = useState('regions')

  useEffect(() => {
    fetch('/data/segregation/villes.json').then((r) => r.json()).then((d) => setVilles(d.villes)).catch(() => setVilles([]))
    fetch('/data/segregation/departements.json').then((r) => r.json()).then((d) => setDeps(d.departements || [])).catch(() => {})
  }, [])

  const searchable = useMemo(
    () => (villes || []).map((v) => ({ code: v.code, nom: v.nom, niveau: 'commune', dep: depFromInsee(v.code), key: norm(v.nom) })),
    [villes],
  )
  const select = (code) => {
    setParams({ ville: code })
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  // Chiffres nationaux (compréhension rapide).
  const apercu = useMemo(() => {
    if (!villes || !villes.length) return null
    const n = villes.length
    const frac = villes.filter((v) => v.revenu.typologie === 'Fracturée').length
    const med = (arr) => {
      const a = arr.filter((x) => x != null).sort((x, y) => x - y)
      return a.length ? a[Math.floor(a.length / 2)] : null
    }
    const p90 = villes.map((v) => v.revenu.p90_p10).filter(Boolean)
    return {
      n, fracPct: Math.round((100 * frac) / n),
      medContrast: med(p90),
      rdGrandes: med(villes.filter((v) => v.pop >= 200000).map((v) => v.revenu.interne_rd)),
      rdPetites: med(villes.filter((v) => v.pop < 30000).map((v) => v.revenu.interne_rd)),
    }
  }, [villes])

  // Lecture territoriale (IRIS agrégés par département, couverture complète) :
  // par région (départements pondérés par leur nombre d'IRIS) et par département.
  const territoire = useMemo(() => {
    if (!deps.length) return { regions: [], departements: [] }
    const byReg = {}
    for (const d of deps) {
      if (d.separation == null) continue
      const r = regionOfDep(d.dep)
      if (!r) continue
      const o = byReg[r] || (byReg[r] = { w: 0, sw: 0 })
      o.w += d.n_iris
      o.sw += d.separation * d.n_iris
    }
    const regions = Object.entries(byReg)
      .map(([label, o]) => ({ label, sep: Math.round(o.sw / o.w) }))
      .sort((a, b) => b.sep - a.sep)
    const departements = deps
      .filter((d) => d.separation != null)
      .map((d) => ({ label: `${d.nom} (${d.dep})`, sep: d.separation }))
      .sort((a, b) => b.sep - a.sep)
    return { regions, departements }
  }, [deps])

  // villes.json trié des plus séparées (entre quartiers) aux moins.
  const plusSeparees = useMemo(() => (villes || []).slice(0, 15), [villes])
  const moinsSeparees = useMemo(() => (villes ? [...villes].reverse().slice(0, 15) : []), [villes])

  return (
    <div className="max-w-4xl mx-auto px-4 py-10">
      <header className="mb-6">
        <p className="text-sm font-semibold text-blue-600 uppercase tracking-wide mb-2">Données ouvertes · INSEE FiLoSoFi</p>
        <h1 className="text-4xl font-bold text-gray-900 mb-3">Riches et pauvres vivent-ils séparés ?</h1>
        <p className="text-lg text-gray-600 leading-relaxed">
          Dans une même ville, se côtoient-ils dans les mêmes quartiers, ou s'évitent-ils ? On mesure, pour
          chaque ville, son niveau de vie, le mélange des revenus <em>à l'intérieur</em> des quartiers, et
          l'écart <em>entre</em> les quartiers. La séparation varie énormément, et contre l'intuition, les
          grandes villes mélangent souvent plus, à l'échelle de la rue, que bien des petites villes proprement
          zonées.
        </p>
      </header>

      {ville && <Fiche code={ville} />}

      {apercu && (
        <section className="mb-10 grid sm:grid-cols-3 gap-4">
          <div className="bg-white border border-gray-200 rounded-2xl p-5">
            <div className="text-3xl font-bold text-red-600">{apercu.fracPct} %</div>
            <div className="text-sm text-gray-600 mt-1">des villes sont classées <strong>fracturées</strong> : le tiers où quartiers riches et pauvres sont le plus à part. Un classement relatif, pas un seuil absolu.</div>
          </div>
          <div className="bg-white border border-gray-200 rounded-2xl p-5">
            <div className="text-3xl font-bold text-amber-600">×{fr1(apercu.medContrast)}</div>
            <div className="text-sm text-gray-600 mt-1"><strong>Entre</strong> quartiers : dans la ville type, les îlots les plus aisés (les 10 % du haut, carreaux de 200 m) ont un niveau de vie {fr1(apercu.medContrast)} fois celui des plus modestes (les 10 % du bas).</div>
          </div>
          <div className="bg-white border border-gray-200 rounded-2xl p-5">
            <div className="text-3xl font-bold text-blue-600">×{fr1(apercu.rdGrandes)} <span className="text-lg font-medium text-gray-400">vs ×{fr1(apercu.rdPetites)}</span></div>
            <div className="text-sm text-gray-600 mt-1"><strong>Dans</strong> un quartier : les 10 % les plus aisés y gagnent {fr1(apercu.rdGrandes)} fois les 10 % les plus modestes en grande ville, contre {fr1(apercu.rdPetites)} en petite. Les grandes villes mélangent plus.</div>
          </div>
        </section>
      )}

      {territoire.regions.length > 0 && (
        <section className="mb-10">
          <div className="flex flex-wrap items-center justify-between gap-3 mb-1">
            <h2 className="text-2xl font-bold text-gray-900">Où, en France, riches et pauvres se séparent le plus ?</h2>
            <Toggle options={[['regions', 'Régions'], ['departements', 'Départements']]} value={terrMode} onChange={setTerrMode} />
          </div>
          <p className="text-gray-500 mb-4">
            Écart de niveau de vie entre les quartiers de chaque territoire (rang national, tous les IRIS de l'INSEE).
            Plus la barre est longue, plus les quartiers riches et pauvres y sont à part.
          </p>
          <div className={`bg-white border border-gray-200 rounded-2xl p-6 space-y-1.5${terrMode === 'departements' ? ' max-h-[28rem] overflow-y-auto' : ''}`}>
            {(terrMode === 'regions' ? territoire.regions : territoire.departements).map((r) => (
              <div key={r.label} className="flex items-center gap-3">
                <span className="w-52 shrink-0 text-sm text-gray-800 truncate">{r.label}</span>
                <div className="flex-1 h-3 bg-gray-100 rounded-full overflow-hidden">
                  <div className="h-full rounded-full" style={{ width: `${r.sep}%`, backgroundColor: r.sep >= 66 ? '#EF4444' : r.sep >= 33 ? '#F59E0B' : '#10B981' }} />
                </div>
                <span className="w-8 text-sm font-semibold text-gray-700 text-right tabular-nums">{r.sep}</span>
              </div>
            ))}
          </div>
          <p className="text-xs text-gray-400 mt-2">
            Source : IRIS FiLoSoFi (communes de 5 000 habitants et plus). Les zones frontalières (Pays de Gex,
            Bâle) ressortent surestimées : hauts revenus, mais pas forcément forte diversité sociale.
          </p>
        </section>
      )}

      {villes && villes.length > 0 && (
        <section className="mb-4">
          <h2 className="text-2xl font-bold text-gray-900 mb-1">Explorer les villes</h2>
          <p className="text-gray-500 mb-4">
            Chaque point est une ville. Par défaut : plus une ville est peuplée, plus ses quartiers mêlent
            les revenus (contre-intuitif). Changez les axes, zoomez sur une région ou un département, ou
            cherchez une ville. Les outsiders sont les villes qui s'écartent de la tendance.
          </p>
          <div className="bg-white border border-gray-200 rounded-2xl p-6">
            <MixiteScatter villes={villes} deps={deps} onSelect={select} />
          </div>
        </section>
      )}

      {villes && villes.length > 0 && (
        <section className="border-t border-gray-100 pt-10 mt-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-1">Le classement des villes</h2>
          <p className="text-gray-500 mb-6">
            Selon l'écart de niveau de vie <strong>entre</strong> les quartiers. À gauche, les villes les plus
            fracturées (quartiers riches et pauvres nettement à part) ; à droite, celles dont les quartiers se
            ressemblent le plus (villes de plus de 10 000 habitants).
          </p>
          <div className="grid md:grid-cols-2 gap-8">
            <Colonne titre="Les plus fracturées" sous="Quartiers riches et pauvres très séparés" villes={plusSeparees} onSelect={select} />
            <Colonne titre="Les plus homogènes" sous="Des quartiers qui se ressemblent" villes={moinsSeparees} onSelect={select} />
          </div>
        </section>
      )}


      <section className="border-t border-gray-100 pt-10 mt-10 max-w-md">
        <h2 className="text-lg font-bold text-gray-900 mb-1">Et votre ville ?</h2>
        <p className="text-sm text-gray-500 mb-3">Cherchez-la pour voir son niveau de vie, le mélange de ses quartiers et sa situation scolaire.</p>
        {villes == null ? (
          <div className="text-gray-400 flex items-center gap-2"><Loader2 className="animate-spin" size={16} /> Chargement…</div>
        ) : (
          <TerritoireSearch searchable={searchable} onSelect={select} placeholder="ex. Marseille, Rennes…" />
        )}
      </section>

      <details className="mt-12 text-sm text-gray-500">
        <summary className="cursor-pointer font-medium text-gray-600 flex items-center gap-1"><ChevronDown size={15} /> Méthode et sources</summary>
        <div className="mt-3 space-y-2 leading-relaxed">
          <p>
            Sources : <a className="text-blue-600 hover:underline" href="https://www.insee.fr/fr/statistiques/8735243" target="_blank" rel="noopener noreferrer">INSEE, FiLoSoFi 2021, carreaux 200 m</a> (la carte et la composition des quartiers)
            et <a className="text-blue-600 hover:underline" href="https://www.insee.fr/fr/statistiques/8229323" target="_blank" rel="noopener noreferrer">INSEE, FiLoSoFi 2021 à l'IRIS</a> (le mélange interne et l'écart entre quartiers).
          </p>
          <p>
            On lit chaque ville sur trois axes. Le <strong>niveau de vie</strong> (médiane) situe la ville : riche, moyenne ou modeste,
            pour ne pas confondre un fort mélange interne avec de la diversité sociale (une ville aisée peut avoir des quartiers
            internement très inégaux sans compter de pauvres). Le <strong>mélange dans les quartiers</strong> vient du rapport interdécile
            D9/D1 des IRIS : dans un même quartier, l'écart entre les 10 % du haut et les 10 % du bas. L'<strong>écart entre quartiers</strong>
            mesure à quel point les quartiers diffèrent par leur niveau de vie. La typologie combine ces deux derniers axes ; chaque score
            est un rang national (percentile).
          </p>
          <p>
            <strong>Et l'école ?</strong> On compare la ségrégation sociale des collèges d'une ville (dispersion de leur
            <a className="text-blue-600 hover:underline" href="https://www.education.gouv.fr/depp/l-indice-de-position-sociale-ips-357755" target="_blank" rel="noopener noreferrer"> indice de position sociale</a>, Éducation nationale)
            à la ségrégation de ses quartiers. Quand l'école trie nettement plus que le logement, c'est un indice d'évitement scolaire.
            On repère l'anomalie, sans pouvoir prouver le mécanisme (fuite vers le privé, dérogations, carte scolaire) ; l'écart d'IPS
            public/privé aide à l'attribuer.
          </p>
          <p className="text-gray-400">
            Limites : l'IRIS fait environ 2 000 habitants (communes de 5 000 habitants et plus) ; les carreaux à moins de 11 ménages,
            estimés par l'INSEE, sont exclus du calcul des revenus ; l'IPS mesure la composition sociale, pas le revenu ; le secteur réel
            d'un collège n'est pas connu (rapprochement approximatif avec les quartiers).
          </p>
        </div>
      </details>
    </div>
  )
}
