import { useEffect, useMemo, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { Loader2, AlertCircle, TrendingUp, Search, ArrowRight } from 'lucide-react'
import { useRouteMeta } from '../../lib/meta'
import ToneCallout from '../../components/ToneCallout'
import RangsSlope from '../../components/charts/RangsSlope'
import ChoroplethMap from '../../components/charts/ChoroplethMap'

const ACCENT = '#0D9488'
const HAUSSE = '#059669'
const BAISSE = '#DC2626'

const f1 = (v) => (v == null ? 'n/d' : v.toLocaleString('fr-FR', { maximumFractionDigits: 1 }))
const signe = (v) => (v == null ? 'n/d' : `${v > 0 ? '+' : ''}${f1(v)}`)
const eur = (v) => `${Math.round(v).toLocaleString('fr-FR')} €`
const normaliser = (s) =>
  s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/[-'’]/g, ' ').trim()

function Section({ title, description, children }) {
  return (
    <section className="mb-12">
      <h2 className="text-2xl font-bold text-gray-900 mb-1">{title}</h2>
      {description && <p className="text-gray-600 mb-5">{description}</p>}
      {children}
    </section>
  )
}

// Barre divergente centrée sur zéro (évolution de la position, en points).
function BarreEcart({ label, sub, value, max }) {
  const w = max ? Math.min(50, (Math.abs(value) / max) * 50) : 0
  const pos = value >= 0
  return (
    <div className="flex items-center gap-3 py-1.5">
      <div className="w-64 shrink-0 text-sm text-gray-700">
        {label}
        {sub && <div className="text-xs text-gray-400">{sub}</div>}
      </div>
      <div className="flex-1 relative h-5">
        <div className="absolute left-1/2 top-0 h-full w-px bg-gray-300" />
        <div
          className="absolute top-0 h-full rounded"
          style={{
            width: `${w}%`,
            left: pos ? '50%' : `${50 - w}%`,
            backgroundColor: pos ? HAUSSE : BAISSE,
          }}
        />
      </div>
      <div className={`w-20 shrink-0 text-right text-sm font-semibold ${pos ? 'text-emerald-700' : 'text-red-700'}`}>
        {signe(value)} pts
      </div>
    </div>
  )
}

// Ligne d'un classement : position 2014 -> 2021, et le contrôle 2023.
function LigneVille({ v, onClick }) {
  const d = v.position_2021 - v.position_2014
  return (
    <button
      type="button"
      onClick={onClick}
      className="w-full text-left flex items-center gap-3 py-2 px-2 rounded-lg hover:bg-gray-50 transition-colors"
    >
      <div className="flex-1 min-w-0">
        <div className="text-sm font-medium text-gray-900 truncate">{v.nom}</div>
        <div className="text-xs text-gray-400">
          {v.pop.toLocaleString('fr-FR')} hab. · dép. {v.dep}
        </div>
      </div>
      <div className="text-xs text-gray-500 w-28 text-right">
        {f1(v.position_2014)} → <strong className="text-gray-800">{f1(v.position_2021)}</strong>
        <div className="text-gray-400">2023 : {f1(v.position_2023)}</div>
      </div>
      <div className={`w-16 text-right text-sm font-semibold ${d >= 0 ? 'text-emerald-700' : 'text-red-700'}`}>
        {signe(d)}
      </div>
    </button>
  )
}

function FicheVille({ v }) {
  const d = v.position_2021 - v.position_2014
  const d23 = v.position_2023 - v.position_2014
  const coherent = Math.sign(d) === Math.sign(d23) || Math.abs(d) < 1
  const lecture =
    Math.abs(d) < 2
      ? 'Sa place dans la hiérarchie des revenus a peu bougé.'
      : d > 0
        ? `Elle a gagné ${f1(d)} points : en 2021, ${f1(v.position_2021)} % de la population des communes comparées vit dans une commune plus modeste, contre ${f1(v.position_2014)} % en 2014.`
        : `Elle a perdu ${f1(-d)} points : en 2021, ${f1(v.position_2021)} % de la population des communes comparées vit dans une commune plus modeste, contre ${f1(v.position_2014)} % en 2014.`
  return (
    <div className="bg-white border border-gray-200 rounded-xl p-6">
      <div className="flex items-baseline justify-between gap-3 mb-4">
        <h3 className="text-xl font-bold text-gray-900">{v.nom}</h3>
        <Link to={`/territoires?code=${v.code}`} className="text-sm text-blue-600 hover:underline inline-flex items-center gap-1">
          Fiche territoire <ArrowRight size={14} />
        </Link>
      </div>
      <div className="grid grid-cols-3 gap-3 mb-4">
        {[
          ['2014', v.position_2014, v.revenu_2014],
          ['2021', v.position_2021, v.revenu_2021],
          ['2023 (contrôle)', v.position_2023, v.revenu_2023],
        ].map(([an, p, r]) => (
          <div key={an} className="bg-gray-50 rounded-lg p-3 text-center">
            <div className="text-xs text-gray-500">{an}</div>
            <div className="text-2xl font-bold text-gray-900">{f1(p)}</div>
            <div className="text-xs text-gray-500">niveau de vie médian : {eur(r)}</div>
          </div>
        ))}
      </div>
      <p className="text-sm text-gray-700">{lecture}</p>
      {!coherent && (
        <p className="text-xs text-amber-700 mt-2">
          Le contrôle sur 2023 va dans l'autre sens : prudence, la méthode de l'Insee a changé entre
          2021 et 2023.
        </p>
      )}
    </div>
  )
}

export default function TerrainRevenus() {
  useRouteMeta('/terrains/revenus')
  const [data, setData] = useState(null)
  const [geoEpci, setGeoEpci] = useState(null)
  const [state, setState] = useState('loading')
  const [seuil, setSeuil] = useState(20000)
  const [requete, setRequete] = useState('')
  // ?ville=<code Insee> ouvre directement la commune (liens depuis les fiches territoire).
  const [params] = useSearchParams()
  const [choix, setChoix] = useState(params.get('ville'))

  useEffect(() => {
    fetch('/data/showcases/evolution-revenus.json')
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then((d) => {
        setData(d)
        setState('ok')
      })
      .catch(() => setState('error'))
    fetch('/data/geo/epci.geojson')
      .then((r) => (r.ok ? r.json() : null))
      .then(setGeoEpci)
      .catch(() => setGeoEpci(null))
  }, [])

  const villes = useMemo(() => {
    if (!data) return []
    const cols = data.colonnes_villes
    return data.villes.map((row) => Object.fromEntries(cols.map((c, i) => [c, row[i]])))
  }, [data])

  const classees = useMemo(
    () => villes.filter((v) => v.pop >= seuil).map((v) => ({ ...v, d: v.position_2021 - v.position_2014 })),
    [villes, seuil],
  )
  const montent = useMemo(() => [...classees].sort((a, b) => b.d - a.d).slice(0, 12), [classees])
  const reculent = useMemo(() => [...classees].sort((a, b) => a.d - b.d).slice(0, 12), [classees])

  // Classement des villes de 100 000 habitants et plus, 2014 contre 2021 (1 = la plus aisée).
  const pente = useMemo(() => {
    const g = villes.filter((v) => v.pop >= 100000)
    const rang = (key) => {
      const tri = [...g].sort((a, b) => b[key] - a[key])
      return new Map(tri.map((v, i) => [v.code, i + 1]))
    }
    const r14 = rang('revenu_2014')
    const r21 = rang('revenu_2021')
    return g.map((v) => ({ id: v.code, nom: v.nom, rangBrut: r14.get(v.code), rang: r21.get(v.code) }))
  }, [villes])

  const suggestions = useMemo(() => {
    const q = normaliser(requete)
    if (q.length < 2) return []
    return villes.filter((v) => normaliser(v.nom).startsWith(q)).slice(0, 8)
  }, [villes, requete])

  // Arrivée par ?ville= : faire défiler jusqu'à « Et votre ville ? » une fois les données chargées.
  useEffect(() => {
    if (state !== 'ok' || !params.get('ville')) return
    const timer = setTimeout(() => {
      const cible = document.getElementById('votre-ville')
      if (!cible) return
      const entete = document.querySelector('header')?.offsetHeight ?? 0
      window.scrollTo({ top: cible.getBoundingClientRect().top + window.scrollY - entete - 16, behavior: 'smooth' })
    }, 50)
    return () => clearTimeout(timer)
  }, [state, params])

  const epciValues = useMemo(
    () => (data ? Object.fromEntries(data.epci.filter((e) => e.n >= 2).map((e) => [e.code, e.evolution])) : {}),
    [data],
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

  const anneau = (nom) => data.anneaux.find((a) => a.nom === nom)
  const paris = anneau('Paris')
  const gc = anneau('Grande couronne')
  const premier = montent[0]
  const maxAnneau = Math.max(...data.anneaux.map((a) => Math.abs(a.evolution)))
  const ficheVille = choix ? villes.find((v) => v.code === choix) : null

  return (
    <div className="py-12 px-4">
      <div className="max-w-4xl mx-auto">
        <header className="mb-10">
          <div className="flex items-center gap-2 mb-2" style={{ color: ACCENT }}>
            <TrendingUp size={20} />
            <span className="text-sm font-semibold uppercase tracking-wide">Dossier · Revenus des communes, 2014-2021</span>
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-3">{data.titre}</h1>
          <p className="text-xl text-gray-600">
            Presque partout, les revenus augmentent en euros. La vraie question est ailleurs : quelles
            villes montent dans la hiérarchie des revenus, et lesquelles décrochent ? Entre 2014 et 2021,
            les communes limitrophes de Paris montent pendant que la grande couronne pavillonnaire recule.
          </p>
        </header>

        <div className="grid sm:grid-cols-3 gap-4 mb-12">
          {premier && (
            <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-5">
              <div className="text-3xl font-bold text-emerald-700">{signe(premier.d)} pts</div>
              <div className="text-sm text-emerald-900">
                {premier.nom}, plus forte progression des villes de 20 000 habitants et plus
              </div>
            </div>
          )}
          {gc && (
            <div className="bg-red-50 border border-red-200 rounded-xl p-5">
              <div className="text-3xl font-bold text-red-700">{f1(100 - gc.part_pop_en_hausse)} %</div>
              <div className="text-sm text-red-900">
                des habitants de la grande couronne vivent dans une commune qui a reculé
              </div>
            </div>
          )}
          {paris && (
            <div className="bg-blue-50 border border-blue-200 rounded-xl p-5">
              <div className="text-3xl font-bold text-blue-700">{signe(paris.evolution)} pts</div>
              <div className="text-sm text-blue-900">pour Paris intra-muros, qui s'éloigne encore du reste du pays</div>
            </div>
          )}
        </div>

        <Section
          title="Le double mouvement"
          description="Évolution moyenne de la position, pondérée par la population, selon la place dans le territoire. Un point = un point de centile."
        >
          <div className="bg-white border border-gray-200 rounded-xl p-6">
            {data.anneaux.map((a) => (
              <BarreEcart
                key={a.nom}
                label={a.nom}
                sub={`${a.n.toLocaleString('fr-FR')} communes · contrôle 2023 : ${signe(a.evolution_2023)} pts`}
                value={a.evolution}
                max={maxAnneau}
              />
            ))}
          </div>
          <div className="mt-4">
            <ToneCallout tone="info">
              Par construction, les gains des uns sont les pertes des autres : la mesure est une
              position relative. Le recul de la grande couronne ne veut pas dire que ses habitants
              s'appauvrissent en euros, mais que leur commune glisse dans la hiérarchie des revenus.
            </ToneCallout>
          </div>
        </Section>

        <Section
          title="Les villes qui montent, les villes qui reculent"
          description="Position dans la distribution des niveaux de vie, en 2014 puis en 2021, et le contrôle sur 2023. Cliquez sur une ville pour sa fiche."
        >
          <div className="flex gap-2 mb-4">
            {[20000, 50000, 100000].map((s) => (
              <button
                key={s}
                type="button"
                onClick={() => setSeuil(s)}
                className={`px-3 py-1.5 rounded-full text-sm border transition-colors ${
                  seuil === s ? 'bg-gray-900 text-white border-gray-900' : 'border-gray-300 text-gray-700 hover:border-gray-500'
                }`}
              >
                {s.toLocaleString('fr-FR')} hab. et plus
              </button>
            ))}
          </div>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-white border border-gray-200 rounded-xl p-4">
              <h3 className="font-semibold text-emerald-700 mb-2">Elles montent</h3>
              {montent.map((v) => (
                <LigneVille key={v.code} v={v} onClick={() => setChoix(v.code)} />
              ))}
            </div>
            <div className="bg-white border border-gray-200 rounded-xl p-4">
              <h3 className="font-semibold text-red-700 mb-2">Elles reculent</h3>
              {reculent.map((v) => (
                <LigneVille key={v.code} v={v} onClick={() => setChoix(v.code)} />
              ))}
            </div>
          </div>
        </Section>

        <Section
          title="Les grandes villes, 2014 contre 2021"
          description="Classement des villes de 100 000 habitants et plus par niveau de vie médian (1 = la plus aisée). En vert, celles qui remontent ; en rouge, celles qui reculent."
        >
          <div className="bg-white border border-gray-200 rounded-xl p-4 overflow-x-auto">
            <RangsSlope
              items={pente}
              labelA="Classement 2014"
              labelB="Classement 2021"
              selectedId={choix}
              onSelect={(id) => setChoix(id)}
            />
          </div>
        </Section>

        {geoEpci && (
          <Section
            title="La carte des intercommunalités"
            description="Évolution moyenne de la position des communes de chaque intercommunalité, pondérée par la population (en points). En vert, les territoires qui montent ; en rouge, ceux qui reculent."
          >
            <ChoroplethMap
              geo={geoEpci}
              valueByCode={epciValues}
              label="Évolution de la position"
              unit="pts"
              format={(v) => `${signe(v)} pts`}
              divergingBreaks={[-6, -3, -1, 1, 3, 6]}
            />
          </Section>
        )}

        <div id="votre-ville" />
        <Section title="Et votre ville ?" description="Communes de 2 000 habitants et plus dont le territoire n'a pas changé depuis 2014.">
          <div className="relative mb-4">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
            <input
              type="text"
              value={requete}
              onChange={(e) => setRequete(e.target.value)}
              placeholder="Tapez le nom d'une commune…"
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-teal-500"
            />
            {suggestions.length > 0 && (
              <ul className="absolute z-10 left-0 right-0 mt-1 bg-white border border-gray-200 rounded-xl shadow-lg overflow-hidden">
                {suggestions.map((v) => (
                  <li key={v.code}>
                    <button
                      type="button"
                      onClick={() => {
                        setChoix(v.code)
                        setRequete('')
                      }}
                      className="w-full text-left px-4 py-2 text-sm hover:bg-gray-50"
                    >
                      {v.nom} <span className="text-gray-400">({v.dep}, {v.pop.toLocaleString('fr-FR')} hab.)</span>
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
          {ficheVille ? (
            <FicheVille v={ficheVille} />
          ) : (
            <p className="text-sm text-gray-500">Choisissez une commune, ou cliquez sur une ville des classements.</p>
          )}
        </Section>

        <Section title="Méthode et limites">
          <div className="space-y-3">
            <ToneCallout tone="info">
              La position d'une commune est la part de la population des communes comparées qui vit dans
              une commune au niveau de vie médian plus faible (de 0 à 100). Comparer des positions, plutôt
              que des euros, neutralise l'inflation et la hausse générale des revenus. Champ :{' '}
              {data.champ.communes.toLocaleString('fr-FR')} communes de France métropolitaine, présentes en
              2014, 2021 et 2023 ; {data.champ.communes_ecartees_perimetre.toLocaleString('fr-FR')} communes
              dont le territoire a changé depuis 2014 (fusions, communes nouvelles) sont écartées, car leur
              évolution mélangerait revenu et périmètre.
            </ToneCallout>
            <ToneCallout tone="warn">
              2014 et 2021 viennent du même dispositif de l'Insee (Filosofi). Le millésime 2023 vient d'un
              nouveau dispositif, Filosofi 2, que l'Insee juge non directement comparable : il sert ici de
              contrôle. Sur les villes de 20 000 habitants et plus, les évolutions 2014-2021 et 2014-2023
              concordent fortement (corrélation de {f1(data.coherence_2023)}).
            </ToneCallout>
            <ToneCallout tone="warn">
              Une commune qui monte n'est pas forcément une commune dont les habitants s'enrichissent :
              l'arrivée de ménages plus aisés et le départ de ménages modestes suffisent à la faire monter.
              Le niveau de vie médian décrit une commune, pas les trajectoires de ses habitants.
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
