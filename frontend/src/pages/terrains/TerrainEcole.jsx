import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { Loader2, AlertCircle, Info, GraduationCap, Map, Scale, Search } from 'lucide-react'
import PointMap from '../../components/charts/PointMap'
import CroisementScatter from '../../components/charts/CroisementScatter'
import Toggle from '../../components/Toggle'
import { useRouteMeta } from '../../lib/meta'
import { withResiduals } from '../../lib/residuals'
import { titleCase } from '../../lib/territoire'

const COLORS = { bas: '#EF4444', haut: '#10B981' }
const NIV_LABEL = { e: 'École', c: 'Collège', l: 'Lycée' }

// Niveaux pour le classement « cumul » (toujours sur le public).
const NIVEAUX = [
  ['ecole', 'École', 'ips_ecole_public'],
  ['college', 'Collège', 'ips_college_public'],
  ['lycee', 'Lycée', 'ips_lycee_public'],
]
// Vues de la carte : 3 IPS + valeur ajoutée.
const VUES = [
  ['ecole', 'École', 'IPS'],
  ['college', 'Collège', 'IPS'],
  ['lycee', 'Lycée', 'IPS'],
  ['va', 'Valeur ajoutée', 'Valeur ajoutée'],
]
const NIVK = { ecole: 'e', college: 'c', lycee: 'l' }
const SECTEURS = [
  ['public', 'Public'],
  ['prive', 'Privé'],
  ['tous', 'Tous'],
]

const stripAccents = (s) => s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '')

function parseEtabs(text) {
  const lines = text.split('\n')
  const out = []
  for (let i = 1; i < lines.length; i++) {
    const p = lines[i].split('\t')
    if (p.length < 8) continue
    out.push({
      uai: p[0], nom: p[1], commune: p[2], dep: p[3], secteur: p[4], niveau: p[5],
      ips: +p[6], pct: p[7] === '' ? null : +p[7],
      va: p[8] === '' ? null : +p[8], taux: p[9] === '' ? null : +p[9],
      lat: p[10] ? +p[10] : null, lon: p[11] ? +p[11] : null,
    })
  }
  return out
}

// Ligne du classement « cumul » : 3 IPS (public) + valeur ajoutée du lycée.
function CumulRow({ d, color }) {
  const scale = (v) => Math.max(4, ((v - 60) / (125 - 60)) * 100)
  return (
    <div className="py-2.5 border-b border-gray-100 last:border-0">
      <div className="text-sm font-medium text-gray-800 mb-1.5">
        {titleCase(d.dep)} <span className="text-gray-400 font-normal">({d.code})</span>
      </div>
      <div className="space-y-1">
        {NIVEAUX.map(([id, label, key]) => (
          <div key={id} className="flex items-center gap-2">
            <span className="text-[11px] text-gray-400 w-12 shrink-0">{label}</span>
            <div className="flex-1 h-3 bg-gray-100 rounded-full overflow-hidden">
              <div className="h-full rounded-full" style={{ width: `${scale(d[key])}%`, backgroundColor: color }} />
            </div>
            <span className="text-xs font-semibold text-gray-700 w-10 text-right">{d[key]}</span>
          </div>
        ))}
      </div>
      {d.va_lycee != null && (
        <div className="mt-1.5 text-xs">
          <span className={`font-medium ${d.va_lycee > 0 ? 'text-emerald-600' : 'text-red-600'}`}>
            Lycée · valeur ajoutée {d.va_lycee > 0 ? '+' : ''}
            {d.va_lycee}
          </span>
          <span className="text-gray-400">, {d.va_lycee > 0 ? "l'école compense" : 'sous-performe'}</span>
        </div>
      )}
    </div>
  )
}

function StatExplain({ n, label, text }) {
  return (
    <div className="flex items-start gap-4 bg-white border border-gray-200 rounded-xl p-5">
      <div className="shrink-0 text-2xl font-bold text-violet-700 w-32">{n}</div>
      <div>
        <div className="font-medium text-gray-900">{label}</div>
        <div className="text-sm text-gray-600 mt-0.5">{text}</div>
      </div>
    </div>
  )
}

export default function TerrainEcole() {
  useRouteMeta('/terrains/ecole')
  const [data, setData] = useState(null)
  const [etabs, setEtabs] = useState([])
  const [query, setQuery] = useState('')
  const [state, setState] = useState('loading')
  const [vue, setVue] = useState('college')
  const [secteur, setSecteur] = useState('public')
  const [croiseX, setCroiseX] = useState('revenu')
  const [evit, setEvit] = useState([])

  useEffect(() => {
    Promise.all([
      fetch('/data/showcases/ecole-ips.json').then((r) => r.json()),
      fetch('/data/showcases/etablissements.tsv').then((r) => r.text()),
    ])
      .then(([d, t]) => {
        setData(d)
        setEtabs(parseEtabs(t))
        setState('ready')
      })
      .catch(() => setState('error'))
  }, [])

  const [colEvit, setColEvit] = useState(null)

  // Évitement scolaire : croisement ségrégation des collèges × ségrégation
  // résidentielle, par ville (données de l'étude ségrégation). Optionnel.
  useEffect(() => {
    fetch('/data/segregation/villes.json')
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then((d) =>
        setEvit(
          (d.villes || [])
            .filter((v) => v.ecole && v.ecole.ecart != null)
            .sort((x, y) => y.ecole.ecart - x.ecole.ecart)
            .slice(0, 12),
        ),
      )
      .catch(() => {})
    fetch('/data/segregation/colleges-evitement.json')
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then(setColEvit)
      .catch(() => {})
  }, [])

  const isVA = vue === 'va'
  const legendLabel = (VUES.find((v) => v[0] === vue) || [])[2]

  const points = useMemo(() => {
    const nk = isVA ? 'l' : NIVK[vue]
    return etabs
      .filter(
        (e) =>
          e.lat != null && e.niveau === nk &&
          (secteur === 'tous' || e.secteur === (secteur === 'public' ? 'pu' : 'pr')) &&
          (isVA ? e.va != null : e.ips != null),
      )
      .map((e) => ({ lat: e.lat, lon: e.lon, value: isVA ? e.va : e.ips, label: `${titleCase(e.nom)} · ${titleCase(e.commune)}` }))
  }, [etabs, vue, secteur, isVA])

  const results = useMemo(() => {
    const q = stripAccents(query.trim())
    if (q.length < 2) return []
    return etabs
      .filter((e) => stripAccents(e.nom).includes(q) || stripAccents(e.commune).includes(q))
      .slice(0, 15)
  }, [query, etabs])

  if (state === 'loading')
    return (
      <div className="py-20 text-center text-gray-500">
        <Loader2 className="animate-spin inline" size={22} /> Chargement…
      </div>
    )
  if (state === 'error')
    return (
      <div className="py-20 text-center text-red-600">
        <AlertCircle className="inline" size={22} /> Données indisponibles.
      </div>
    )

  const deps = data.departements
  const bas = deps.filter((d) => d.cumul === 'triple-bas').sort((a, b) => a.ips_moyen - b.ips_moyen)
  const haut = deps.filter((d) => d.cumul === 'triple-haut').sort((a, b) => b.ips_moyen - a.ips_moyen)
  const basVA = bas.filter((d) => d.va_lycee != null)
  const compense = basVA.filter((d) => d.va_lycee > 0).length
  // Point de comparaison : la même part dans les départements favorisés aux 3 étapes.
  const hautVA = haut.filter((d) => d.va_lycee != null)
  const compenseHaut = hautVA.filter((d) => d.va_lycee > 0).length
  const bestComp = basVA.length ? basVA.reduce((x, y) => (y.va_lycee > x.va_lycee ? y : x)) : null
  const worst = basVA.length ? basVA.reduce((x, y) => (y.va_lycee < x.va_lycee ? y : x)) : null

  // Croisement IPS collège ↔ richesse résidentielle (revenu ou prix)
  const croisePoints = deps
    .filter((d) => d.ips_college_public != null && (croiseX === 'prix' ? d.prix_m2 : d.revenu) != null)
    .map((d) => ({ x: croiseX === 'prix' ? d.prix_m2 : d.revenu, y: d.ips_college_public, label: titleCase(d.dep), cumul: d.cumul }))
  const outliers = (() => {
    if (croisePoints.length < 4) return { under: [], over: [] }
    const r = withResiduals(croisePoints).points.sort((p, q) => p.resid - q.resid)
    return { under: r.slice(0, 3).map((p) => p.label), over: r.slice(-3).reverse().map((p) => p.label) }
  })()
  const ssd = deps.find((d) => d.code === '93') || {}
  const xLabel = croiseX === 'prix' ? 'Prix immobilier médian (€/m²)' : 'Revenu médian (€/an)'
  const xUnit = croiseX === 'prix' ? '€/m²' : '€/an'

  const a = data.annees

  return (
    <div className="py-12 px-4">
      <div className="max-w-5xl mx-auto">
        {/* En-tête */}
        <header className="mb-8">
          <div className="flex items-center gap-2 text-violet-600 mb-2">
            <GraduationCap size={20} />
            <span className="text-sm font-semibold uppercase tracking-wide">Terrain · L'école</span>
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-3">L'école trie-t-elle ?</h1>
          <p className="text-xl text-gray-600">
            L'indice de position sociale (IPS) mesure le milieu social des élèves de chaque
            établissement. En suivant les trois étapes, école, collège, lycée, la ségrégation se
            révèle <strong>cumulative</strong>. Mais là où le lycée a une forte{' '}
            <strong>valeur ajoutée</strong>, l'école <em>compense</em>.
          </p>
          <Link
            to="/atlas?i=ips_college_public"
            className="inline-flex items-center gap-1.5 mt-3 text-sm font-medium text-blue-600 hover:text-blue-700"
          >
            <Map size={16} /> Voir l'IPS sur la carte de France
          </Link>
        </header>

        {/* Chiffres clés */}
        <div className="grid sm:grid-cols-3 gap-4 mb-12">
          <div className="bg-red-50 border border-red-200 rounded-xl p-5">
            <div className="text-3xl font-bold text-red-700">{bas.length}</div>
            <div className="text-sm text-red-900">départements défavorisés aux 3 étapes</div>
          </div>
          <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-5">
            <div className="text-3xl font-bold text-emerald-700">{haut.length}</div>
            <div className="text-sm text-emerald-900">départements en entre-soi aux 3 étapes</div>
          </div>
          <div className="bg-violet-50 border border-violet-200 rounded-xl p-5">
            <div className="text-3xl font-bold text-violet-700">93 ↔ 92</div>
            <div className="text-sm text-violet-900">la même région, deux mondes (Seine-St-Denis / Hauts-de-Seine)</div>
          </div>
        </div>

        {/* Recherche d'établissement */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-1">Cherchez votre établissement</h2>
          <p className="text-gray-500 mb-4">
            École, collège ou lycée : tapez un nom ou une commune ({etabs.length.toLocaleString('fr-FR')}{' '}
            établissements).
          </p>
          <div className="relative max-w-xl">
            <Search className="absolute left-3 top-3 text-gray-400" size={18} />
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="ex. Jean Moulin, ou Bobigny…"
              className="w-full border border-gray-300 rounded-lg pl-10 pr-3 py-2.5 focus:outline-none focus:border-violet-400"
            />
          </div>
          {results.length > 0 && (
            <div className="mt-4 space-y-2 max-w-3xl">
              {results.map((e) => (
                <div key={e.uai} className="bg-white border border-gray-200 rounded-lg p-4">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <div className="font-medium text-gray-900">{titleCase(e.nom)}</div>
                      <div className="text-sm text-gray-500">
                        {NIV_LABEL[e.niveau]} {e.secteur === 'pr' ? 'privé' : 'public'} ·{' '}
                        {titleCase(e.commune)} ({e.dep})
                      </div>
                    </div>
                    <div className="text-right shrink-0">
                      <div className="text-lg font-bold text-gray-900">IPS {e.ips}</div>
                      {e.pct != null && (
                        <div className="text-xs text-gray-500">
                          plus favorisé que {e.pct}% des {NIV_LABEL[e.niveau].toLowerCase()}s
                        </div>
                      )}
                    </div>
                  </div>
                  {e.niveau === 'l' && (e.va != null || e.taux != null) && (
                    <div className="mt-2 pt-2 border-t border-gray-100 text-sm flex gap-4">
                      {e.va != null && (
                        <span className={e.va > 0 ? 'text-emerald-600' : 'text-red-600'}>
                          Valeur ajoutée {e.va > 0 ? '+' : ''}
                          {e.va}
                        </span>
                      )}
                      {e.taux != null && <span className="text-gray-600">Réussite bac {e.taux}%</span>}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
          {query.trim().length >= 2 && results.length === 0 && (
            <p className="mt-3 text-sm text-gray-500">Aucun établissement trouvé.</p>
          )}
        </section>

        {/* Carte des établissements (points), la carte de France est dans l'Atlas */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-1">La carte des établissements</h2>
          <p className="text-gray-500 mb-4">
            {isVA
              ? 'Valeur ajoutée au bac : chaque lycée en un point. Vert = sur-performe.'
              : `IPS de chaque établissement (secteur ${SECTEURS.find((s) => s[0] === secteur)[1].toLowerCase()}). Zoomez pour distinguer les écoles.`}{' '}
            Pour la carte de France par indicateur et le détail commune par commune,{' '}
            <Link to="/atlas?i=ips_college_public" className="text-violet-600 font-medium">
              passez à l'Atlas
            </Link>
            .
          </p>
          <div className="bg-white border border-gray-200 rounded-xl p-6">
            <div className="flex flex-wrap items-center gap-3 mb-3">
              <Toggle options={VUES.map((v) => [v[0], v[1]])} value={vue} onChange={setVue} />
              {!isVA && <Toggle options={SECTEURS} value={secteur} onChange={setSecteur} />}
            </div>
            <div className="flex items-center gap-2 text-sm text-gray-500 mb-2">
              <Map size={16} /> {points.length.toLocaleString('fr-FR')} établissements, survolez un point.
            </div>
            <PointMap points={points} unit="" label={legendLabel} />
          </div>
        </section>

        {/* Croisement résidentiel */}
        {croisePoints.length > 4 && (
          <section className="mb-12">
            <h2 className="text-2xl font-bold text-gray-900 mb-1">
              L'école suit-elle la ségrégation résidentielle ?
            </h2>
            <p className="text-gray-500 mb-4">
              Un point = un département. En abscisse la richesse du territoire, en ordonnée l'IPS des
              collèges publics.
            </p>
            <div className="bg-white border border-gray-200 rounded-xl p-6">
              <div className="mb-2">
                <Toggle
                  options={[
                    ['revenu', 'Revenu médian'],
                    ['prix', 'Prix au m²'],
                  ]}
                  value={croiseX}
                  onChange={setCroiseX}
                />
              </div>
              <CroisementScatter points={croisePoints} xLabel={xLabel} xUnit={xUnit} />
            </div>
            <div className="bg-amber-50 border border-amber-200 rounded-xl p-5 mt-4 text-sm text-amber-900">
              <strong>À richesse égale, l'école n'est pas la même partout.</strong> Là où l'IPS est{' '}
              <em>plus bas</em> que le territoire ne le laisse attendre, un filtre scolaire s'ajoute (
              {outliers.under.join(', ')}). Là où il est <em>plus haut</em>, le public reste plus
              mixte ({outliers.over.join(', ')}).
            </div>
          </section>
        )}

        {/* Évitement scolaire, au niveau ville (croisement avec la ségrégation résidentielle) */}
        {evit.length > 0 && (
          <section className="mb-12">
            <h2 className="text-2xl font-bold text-gray-900 mb-1">Où l'école trie plus que le quartier ?</h2>
            <p className="text-gray-500 mb-4">
              Ville par ville, on compare la ségrégation sociale des collèges à celle des quartiers d'habitation.
              Quand les quartiers mélangent les revenus mais que les collèges publics se vident de leurs élèves
              favorisés, partis vers le privé, c'est le signe d'un <strong>évitement scolaire</strong> ou d'une carte
              scolaire concentrante.
            </p>
            <div className="bg-white border border-gray-200 rounded-xl p-6">
              <ol className="space-y-1">
                {evit.map((v, i) => (
                  <li key={v.code}>
                    <Link to={`/segregation?ville=${v.code}`} className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-50">
                      <span className="w-5 text-sm text-gray-400 tabular-nums">{i + 1}</span>
                      <span className="flex-1 text-gray-900 truncate">{v.nom}</span>
                      {v.ecole.ips_public != null && v.ecole.ips_prive != null && (
                        <span className="text-xs text-gray-400 hidden sm:inline">IPS public {v.ecole.ips_public} / privé {v.ecole.ips_prive}</span>
                      )}
                      <span className="text-sm font-semibold tabular-nums text-red-600 w-16 text-right">école +{v.ecole.ecart}</span>
                    </Link>
                  </li>
                ))}
              </ol>
              <p className="text-xs text-gray-400 mt-3">
                « école +N » = la ségrégation des collèges dépasse celle des quartiers de N rangs (percentiles nationaux).
                Cliquez une ville pour la voir dans l'étude de la{' '}
                <Link to="/segregation" className="text-violet-600 font-medium">ségrégation résidentielle</Link>.
                On repère l'anomalie sans prouver le mécanisme (privé, dérogations, sectorisation).
              </p>
            </div>
          </section>
        )}

        {/* Évitement au niveau établissement : collège vs son propre quartier */}
        {colEvit && (
          <section className="mb-12">
            <h2 className="text-2xl font-bold text-gray-900 mb-1">Les collèges décrochés, et attractifs, de leur quartier</h2>
            <p className="text-gray-500 mb-4">
              Pour chaque collège public, on compare son IPS au niveau de vie de son quartier immédiat (les carreaux
              de 200 m à moins de 700 m). Très <em>en dessous</em> : les familles favorisées du coin l'évitent
              (gentrification, privé, sélectif ailleurs). Très <em>au-dessus</em> : un public qui attire au-delà de son
              voisinage, souvent sélectif ou international.
            </p>
            <div className="grid md:grid-cols-2 gap-6">
              <div className="bg-white border border-gray-200 rounded-xl p-6">
                <h3 className="font-semibold text-red-700 mb-1">Décrochés de leur quartier</h3>
                <p className="text-xs text-gray-400 mb-3">IPS bien sous le niveau de vie local</p>
                {colEvit.decroches.slice(0, 12).map((e, i) => (
                  <div key={i} className="flex items-center gap-3 py-1.5 border-b border-gray-100 last:border-0">
                    <div className="flex-1 min-w-0">
                      <div className="text-sm text-gray-800 truncate">{titleCase(e.nom.replace(/^COLLEGE\s+/i, ''))}</div>
                      <div className="text-xs text-gray-400 truncate">{titleCase(e.commune)} · IPS {e.ips}</div>
                    </div>
                    <span className="text-sm font-semibold tabular-nums text-red-600">{e.resid}</span>
                  </div>
                ))}
              </div>
              <div className="bg-white border border-gray-200 rounded-xl p-6">
                <h3 className="font-semibold text-emerald-700 mb-1">Au-dessus de leur quartier</h3>
                <p className="text-xs text-gray-400 mb-3">IPS bien au-dessus du niveau de vie local</p>
                {colEvit.attractifs.slice(0, 12).map((e, i) => (
                  <div key={i} className="flex items-center gap-3 py-1.5 border-b border-gray-100 last:border-0">
                    <div className="flex-1 min-w-0">
                      <div className="text-sm text-gray-800 truncate">{titleCase(e.nom.replace(/^COLLEGE\s+/i, ''))}</div>
                      <div className="text-xs text-gray-400 truncate">{titleCase(e.commune)} · IPS {e.ips}</div>
                    </div>
                    <span className="text-sm font-semibold tabular-nums text-emerald-600">+{e.resid}</span>
                  </div>
                ))}
              </div>
            </div>
            <p className="text-xs text-gray-400 mt-3">
              Résidu = rang national d'IPS du collège − rang national du revenu de son quartier. Exploratoire :
              le revenu n'est pas l'IPS (les zones frontalières ressortent surestimées), et le secteur réel d'un
              collège dépasse 700 m. {colEvit.n.toLocaleString('fr-FR')} collèges publics.
            </p>
          </section>
        )}

        {/* Compensation, l'apport d'IVAL */}
        <div className="bg-violet-50 border border-violet-200 rounded-xl p-5 mb-10 flex items-start gap-3">
          <Scale className="text-violet-600 shrink-0 mt-0.5" size={22} />
          <div className="text-sm text-violet-900">
            <strong>Défavorisé ne veut pas dire « école qui échoue ».</strong> Sur les {basVA.length}{' '}
            départements défavorisés aux 3 étapes où la valeur ajoutée est connue, <strong>{compense}</strong> ont
            des lycées à valeur ajoutée positive, autant que dans les départements favorisés ({compenseHaut} sur{' '}
            {hautVA.length}) ; l'école y fait mieux que prévu
            {bestComp && ` (${titleCase(bestComp.dep)} : +${bestComp.va_lycee})`}. Dans les autres,
            c'est la <strong>double peine</strong> : milieu défavorisé <em>et</em> résultats en
            dessous de l'attendu
            {worst && ` (${titleCase(worst.dep)} : ${worst.va_lycee})`}.
          </div>
        </div>

        {/* Cumul */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-1">Le cumul des trois étapes</h2>
          <p className="text-gray-500 mb-6">
            Départements dans le tiers le plus bas, ou le plus haut, aux trois niveaux d'IPS
            (public), avec la valeur ajoutée du lycée.
          </p>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-white border border-gray-200 rounded-xl p-6">
              <h3 className="font-semibold text-gray-900 mb-3">Public modeste aux trois étapes</h3>
              {bas.map((d) => (
                <CumulRow key={d.code} d={d} color={COLORS.bas} />
              ))}
            </div>
            <div className="bg-white border border-gray-200 rounded-xl p-6">
              <h3 className="font-semibold text-gray-900 mb-3">Entre-soi cumulé</h3>
              {haut.map((d) => (
                <CumulRow key={d.code} d={d} color={COLORS.haut} />
              ))}
            </div>
          </div>
        </section>

        {/* Ce qu'il faut retenir */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-5">Ce qu'il faut retenir</h2>
          <div className="space-y-3">
            <StatExplain
              n={`${bas.length} dépts`}
              label="défavorisés aux trois étapes à la fois"
              text="Un enfant qui y grandit fréquente une école, puis un collège, puis un lycée tous plus pauvres que la moyenne : le désavantage ne se rattrape pas, il s'empile."
            />
            <StatExplain
              n="0,58"
              label="corrélation entre l'école et le revenu du territoire"
              text="Si l'école ne faisait que refléter là où vivent riches et pauvres, ce chiffre serait proche de 1. À 0,58, l'école ajoute sa propre ségrégation à celle du logement."
            />
            {ssd.ips_college_prive != null && (
              <StatExplain
                n={`${ssd.ips_college_public} → ${ssd.ips_college_prive}`}
                label="IPS du collège public vs privé en Seine-Saint-Denis"
                text="Dans le département le plus pauvre de métropole, les collèges privés accueillent un public bien plus favorisé que les collèges publics voisins : l'écart le plus grand de métropole."
              />
            )}
            <StatExplain
              n={`${compense} sur ${basVA.length}`}
              label={`départements défavorisés aux 3 étapes où les lycées font mieux que prévu (${compenseHaut} sur ${hautVA.length} chez les favorisés)`}
              text="Défavorisé n'est pas une fatalité : dans ces départements, les lycées font mieux réussir au bac que ne le laisserait attendre le profil social des élèves (valeur ajoutée positive)."
            />
          </div>
        </section>

        {/* Caveats */}
        <details className="bg-gray-50 rounded-xl border border-gray-200 p-6">
          <summary className="font-semibold text-gray-900 cursor-pointer flex items-center gap-2">
            <Info size={18} className="text-violet-600" /> Méthode & limites
          </summary>
          <div className="mt-4 text-sm text-gray-600 space-y-3">
            <p>
              <strong>IPS vs valeur ajoutée</strong> : l'IPS mesure la <em>composition sociale</em>,
              pas les résultats. La <strong>valeur ajoutée</strong> (IVAL) mesure la réussite au bac
              <em> au-delà</em> de ce qu'on attendrait vu le profil des élèves, elle distingue
              « territoire défavorisé » d'« école qui sous-performe ».
            </p>
            <p>
              <strong>Maille & secteur</strong> : carte par département ou intercommunalité (EPCI),
              vue public / privé / tous. Le cumul est calculé sur le public. La valeur ajoutée couvre
              les lycées GT + professionnels.
            </p>
            <p>
              <strong>Années</strong> : écoles {a.ecole}, collèges {a.college}, lycées {a.lycee}.
              Sources :{' '}
              <a href="https://www.education.gouv.fr/depp/l-indice-de-position-sociale-ips-357755" target="_blank" rel="noopener noreferrer" className="underline hover:text-gray-600">IPS écoles/collèges/lycées</a>{' '}
              et{' '}
              <a href="https://www.data.gouv.fr/datasets/indicateurs-de-valeur-ajoutee-des-lycees-denseignement-general-et-technologique-2" target="_blank" rel="noopener noreferrer" className="underline hover:text-gray-600">IVAL</a>{' '}
              (Éducation nationale, data.gouv.fr).
            </p>
          </div>
        </details>
      </div>
    </div>
  )
}
