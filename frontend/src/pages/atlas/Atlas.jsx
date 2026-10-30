import { useEffect, useMemo, useState } from 'react'
import { useSearchParams, Link, useNavigate } from 'react-router-dom'
import { Loader2, Map as MapIcon, ChevronLeft, Link2, Check, ArrowRight, Code2 } from 'lucide-react'
import ChoroplethMap from '../../components/charts/ChoroplethMap'
import PointMap from '../../components/charts/PointMap'
import AnalyseBloc from './AnalyseBloc'
import CroisementsSuggeres from './CroisementsSuggeres'
import ExplorerBar from '../../components/ExplorerBar'
import { GROUPES, INDICATEUR_BY_ID, DEFAULT_INDICATEUR } from '../../config/indicateurs'
import { useRouteMeta } from '../../lib/meta'
import { titleCase } from '../../lib/territoire'
import { trackEvent } from '../../lib/analytics'

// Parse etablissements.tsv (réutilisé du dossier École) pour la couche de points.
function parseEtabs(text) {
  const lines = text.split('\n')
  const out = []
  for (let i = 1; i < lines.length; i++) {
    const p = lines[i].split('\t')
    if (p.length < 12) continue
    out.push({
      nom: p[1], commune: p[2], secteur: p[4], niveau: p[5],
      ips: +p[6], va: p[8] === '' ? null : +p[8],
      lat: p[10] ? +p[10] : null, lon: p[11] ? +p[11] : null,
    })
  }
  return out
}

// Dossier (terrain) lié à un groupe d'indicateurs, pour « aller plus loin ».
const DOSSIERS = {
  École: { to: '/terrains/ecole', label: "le dossier École, cumul des 3 étapes, valeur ajoutée, recherche d'établissement" },
  'Représentation politique': { to: '/terrains/elus', label: 'le dossier Élus, du candidat au maire, par parti' },
}

export default function Atlas() {
  const [params, setParams] = useSearchParams()
  const indId = params.get('i') || DEFAULT_INDICATEUR
  const ind = INDICATEUR_BY_ID[indId] || INDICATEUR_BY_ID[DEFAULT_INDICATEUR]
  // Un indicateur sans valeur communale reste à la vue nationale.
  const dep = ind.communeKey ? params.get('dep') : null
  const vsId = params.get('vs')
  const vsInd = vsId && vsId !== indId ? INDICATEUR_BY_ID[vsId] : null
  const dossier = DOSSIERS[ind.groupe]
  const navigate = useNavigate()
  useRouteMeta('/atlas', { title: `${ind.label} : la carte des outsiders` })

  // Mailles disponibles pour l'indicateur courant (vue nationale).
  const meshes = [
    { id: 'dept', label: 'Départements' },
    ...(ind.epci ? [{ id: 'epci', label: 'EPCI' }] : []),
    ...(ind.etab ? [{ id: 'etab', label: 'Établissements' }] : []),
  ]
  const meshParam = params.get('m') || 'dept'
  const m = meshes.some((x) => x.id === meshParam) ? meshParam : 'dept'

  const setInd = (id) =>
    setParams((p) => {
      const n = new URLSearchParams(p)
      n.set('i', id)
      return n
    })
  const setDep = (code) =>
    setParams((p) => {
      const n = new URLSearchParams(p)
      if (code) n.set('dep', code)
      else n.delete('dep')
      return n
    })
  const setVs = (id) => {
    if (id) trackEvent(`atlas-croisement/${indId}/${id}`, 'Atlas : croisement choisi')
    return setParams((p) => {
      const n = new URLSearchParams(p)
      if (id) n.set('vs', id)
      else n.delete('vs')
      return n
    })
  }
  // Ouvre un croisement suggéré : indicateur + croisement en un seul changement d'URL,
  // vue nationale, puis défile jusqu'au nuage.
  const openCroisement = (yId, xId) => {
    setParams((p) => {
      const n = new URLSearchParams(p)
      n.set('i', yId)
      n.set('vs', xId)
      n.delete('dep')
      return n
    })
    setTimeout(() => document.getElementById('analyse-bloc')?.scrollIntoView({ behavior: 'smooth' }), 150)
  }
  const setMesh = (id) =>
    setParams((p) => {
      const n = new URLSearchParams(p)
      if (id === 'dept') n.delete('m')
      else n.set('m', id)
      n.delete('dep')
      return n
    })

  // Données nationales (départements)
  const [deptData, setDeptData] = useState(null)
  const [geoDept, setGeoDept] = useState(null)
  useEffect(() => {
    Promise.all([
      fetch('/data/atlas/departements.json').then((r) => r.json()),
      fetch('/data/geo/departements.geojson').then((r) => r.json()),
    ])
      .then(([d, g]) => {
        setDeptData(d)
        setGeoDept(g)
      })
      .catch(() => {})
  }, [])

  // Drill communal (chargé à la demande)
  const [communeGeo, setCommuneGeo] = useState(null)
  const [communeVals, setCommuneVals] = useState(null)
  const [drillLoading, setDrillLoading] = useState(false)
  const [drillError, setDrillError] = useState(false)
  const [retryKey, setRetryKey] = useState(0)
  useEffect(() => {
    if (!dep) {
      setCommuneGeo(null)
      setCommuneVals(null)
      setDrillError(false)
      return
    }
    setDrillLoading(true)
    setDrillError(false)
    setCommuneGeo(null)
    const ctrl = new AbortController()
    const timer = setTimeout(() => ctrl.abort(), 12000)
    Promise.all([
      fetch(`https://geo.api.gouv.fr/departements/${dep}/communes?format=geojson&geometry=contour`, { signal: ctrl.signal }).then((r) => {
        if (!r.ok) throw new Error('geo')
        return r.json()
      }),
      fetch(`/data/atlas/communes/${dep}.json`).then((r) => (r.ok ? r.json() : {})).catch(() => ({})),
    ])
      .then(([g, v]) => {
        setCommuneGeo(g)
        setCommuneVals(v)
      })
      .catch(() => setDrillError(true))
      .finally(() => {
        clearTimeout(timer)
        setDrillLoading(false)
      })
  }, [dep, retryKey])

  // EPCI (maille nationale alternative, chargée à la demande)
  const [epciData, setEpciData] = useState(null)
  const [geoEpci, setGeoEpci] = useState(null)
  useEffect(() => {
    if (m !== 'epci' || geoEpci) return
    Promise.all([
      fetch('/data/atlas/epci.json').then((r) => r.json()),
      fetch('/data/geo/epci.geojson').then((r) => r.json()),
    ])
      .then(([d, g]) => { setEpciData(d); setGeoEpci(g) })
      .catch(() => {})
  }, [m, geoEpci])

  // Établissements (couche de points, chargée à la demande)
  const [etabs, setEtabs] = useState(null)
  useEffect(() => {
    if (m !== 'etab' || etabs) return
    fetch('/data/showcases/etablissements.tsv')
      .then((r) => r.text())
      .then((t) => setEtabs(parseEtabs(t)))
      .catch(() => setEtabs([]))
  }, [m, etabs])

  const nationalVals = useMemo(
    () =>
      deptData
        ? Object.fromEntries(deptData.filter((r) => r[ind.deptKey] != null).map((r) => [r.code, r[ind.deptKey]]))
        : {},
    [deptData, ind],
  )
  const communeValueByCode = useMemo(
    () =>
      communeVals
        ? Object.fromEntries(
            Object.entries(communeVals)
              .filter(([, v]) => v[ind.communeKey] != null)
              .map(([c, v]) => [c, v[ind.communeKey]]),
          )
        : {},
    [communeVals, ind],
  )
  const epciValueByCode = useMemo(
    () => (epciData ? Object.fromEntries(epciData.filter((r) => r[ind.deptKey] != null).map((r) => [r.code, r[ind.deptKey]])) : {}),
    [epciData, ind],
  )
  const etabPoints = useMemo(() => {
    if (!etabs || !ind.etab) return []
    const { niveau, secteur, value } = ind.etab
    return etabs
      .filter((e) => e.lat != null && e.niveau === niveau && (!secteur || e.secteur === secteur) && e[value] != null)
      .map((e) => ({ lat: e.lat, lon: e.lon, value: e[value], label: `${titleCase(e.nom)} · ${titleCase(e.commune)}` }))
  }, [etabs, ind])

  // Enregistrements communaux (pour l'analyse à la maille du département drillé)
  const communeRecords = useMemo(() => {
    if (!dep || !communeGeo || !communeVals) return []
    return communeGeo.features.map((f) => ({
      code: f.properties.code,
      nom: f.properties.nom,
      ...(communeVals[f.properties.code] || {}),
    }))
  }, [dep, communeGeo, communeVals])

  const depNom = dep && deptData ? (deptData.find((d) => d.code === dep) || {}).dep : null
  const depNomTitre = depNom ? titleCase(depNom) : 'ce département'

  // Surbrillance d'un territoire sur la carte au survol d'un outsider (bloc d'analyse).
  const [highlightCode, setHighlightCode] = useState(null)
  // Clic sur un outsider -> sa fiche (commune, département ou intercommunalité : un SIREN de
  // 9 chiffres ouvre la fiche intercommunalité, voir niveauFromCode).
  const selectOutsider = (code) => navigate(`/territoires?code=${code}`)

  const [copied, setCopied] = useState(false)
  const copyLink = () => {
    navigator.clipboard?.writeText(window.location.href).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 1500)
    })
  }

  // Code d'intégration (iframe) de la vue carte courante, pour la republier ailleurs.
  const [embedded, setEmbedded] = useState(false)
  const copyEmbed = () => {
    const q = new URLSearchParams({ i: indId })
    if (!dep && m !== 'dept') q.set('m', m)
    if (dep) q.set('dep', dep)
    const src = `${window.location.origin}/embed/carte?${q.toString()}`
    trackEvent(`integrer-carte/${indId}`, 'Intégrer une carte')
    const code = `<iframe src="${src}" width="100%" height="560" style="border:0;border-radius:12px" loading="lazy" title="Outsiders, ${ind.label}"></iframe>`
    navigator.clipboard?.writeText(code).then(() => {
      setEmbedded(true)
      setTimeout(() => setEmbedded(false), 1800)
    })
  }

  return (
    <>
      <ExplorerBar decoupage="territoire" mode="carte" />
      <div className="py-10">
      <div className="max-w-5xl mx-auto px-4">
        {/* En-tête */}
        <header className="mb-6">
          <div className="flex items-center gap-2 text-blue-600 mb-2">
            <MapIcon size={20} />
            <span className="text-sm font-semibold uppercase tracking-wide">Atlas</span>
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-2">La géographie des angles morts</h1>
          <p className="text-lg text-gray-600">
            Choisissez un indicateur, lisez la France d'un coup d'œil, puis cliquez un département
            pour descendre à la commune. L'adresse de la page suit votre sélection, copiez-la pour
            la partager.
          </p>
        </header>

        {/* Ce que vous pouvez faire */}
        <div className="flex flex-wrap gap-x-6 gap-y-2 mb-5 text-sm text-gray-600">
          {[
            'Choisissez un indicateur',
            'Cliquez un département pour zoomer sur ses communes',
            'Croisez-en deux pour repérer les territoires qui défient leur pronostic',
            'Copiez le lien pour partager exactement cette vue',
          ].map((t, i) => (
            <span key={i} className="inline-flex items-center gap-1.5">
              <span className="w-5 h-5 rounded-full bg-blue-100 text-blue-700 text-xs font-bold flex items-center justify-center shrink-0">
                {i + 1}
              </span>
              {t}
            </span>
          ))}
        </div>

        {/* Sélecteur d'indicateur */}
        <div className="bg-gray-50 border border-gray-200 rounded-2xl p-4 sm:p-5 mb-6">
          <div className="flex flex-wrap items-end gap-x-10 gap-y-4">
            {GROUPES.map((g) => (
              <div key={g.nom}>
                <div className="text-xs font-semibold uppercase tracking-wide text-gray-400 mb-2">{g.nom}</div>
                <div className="flex flex-wrap gap-2">
                  {g.indicateurs.map((i) => {
                    const active = i.id === indId
                    return (
                      <button
                        key={i.id}
                        onClick={() => setInd(i.id)}
                        className="px-3 py-1.5 rounded-full text-sm font-medium border transition-all hover:shadow-sm"
                        style={
                          active
                            ? { backgroundColor: i.couleur, borderColor: i.couleur, color: '#fff' }
                            : { borderColor: '#e5e7eb', color: '#4b5563' }
                        }
                      >
                        {i.label}
                      </button>
                    )
                  })}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Carte */}
      <div className="max-w-5xl mx-auto px-4">
        <div
          className="bg-white border border-gray-200 border-t-4 rounded-2xl p-4 sm:p-6 shadow-sm"
          style={{ borderTopColor: ind.couleur }}
        >
          {/* Indicateur actif + action */}
          <div className="flex items-start justify-between flex-wrap gap-2 mb-3">
            <div>
              <div className="text-lg font-bold leading-tight" style={{ color: ind.couleur }}>
                {ind.label}
              </div>
              <div className="text-xs text-gray-400">
                Source :{' '}
                {ind.sourceUrl ? (
                  <a href={ind.sourceUrl} target="_blank" rel="noopener noreferrer" className="underline hover:text-gray-600">{ind.source}</a>
                ) : (
                  ind.source
                )}
              </div>
            </div>
            <div className="flex items-center gap-4">
              {m !== 'etab' && (
                <button onClick={copyEmbed} className="inline-flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-800" title="Copier le code pour intégrer cette carte sur un autre site">
                  {embedded ? <Check size={15} className="text-emerald-600" /> : <Code2 size={15} />}
                  {embedded ? 'Code copié' : 'Intégrer'}
                </button>
              )}
              <button onClick={copyLink} className="inline-flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-800">
                {copied ? <Check size={15} className="text-emerald-600" /> : <Link2 size={15} />}
                {copied ? 'Lien copié' : 'Copier le lien'}
              </button>
            </div>
          </div>
          {/* Maille (vue nationale) */}
          {!dep && meshes.length > 1 && (
            <div className="inline-flex rounded-lg border border-gray-200 overflow-hidden mb-3 text-sm">
              {meshes.map((mm) => (
                <button
                  key={mm.id}
                  onClick={() => setMesh(mm.id)}
                  className={`px-3 py-1.5 transition-colors ${m === mm.id ? 'bg-blue-600 text-white font-medium' : 'bg-white text-gray-600 hover:bg-gray-50'}`}
                >
                  {mm.label}
                </button>
              ))}
            </div>
          )}
          {/* Fil d'ariane */}
          <div className="text-sm text-gray-600 mb-3">
            {dep ? (
              <button onClick={() => setDep(null)} className="inline-flex items-center gap-1 text-blue-600 hover:text-blue-700">
                <ChevronLeft size={16} /> France
              </button>
            ) : (
              <span className="text-gray-400">
                {m === 'dept'
                  ? ind.communeKey
                    ? 'France · cliquez un département pour voir ses communes'
                    : 'France · donnée publiée au département, cliquez-en un pour sa fiche'
                  : m === 'epci'
                    ? 'Intercommunalités · zoomez pour explorer'
                    : 'Établissements · zoomez et survolez un point'}
              </span>
            )}
            {depNom && <span className="text-gray-900 font-medium"> › {titleCase(depNom)}</span>}
            {dep && <span className="text-gray-400"> · cliquez une commune pour sa fiche</span>}
          </div>

          {!geoDept ? (
            <div className="h-[560px] flex items-center justify-center text-gray-400">
              <Loader2 className="animate-spin" size={22} />
            </div>
          ) : dep ? (
            drillError ? (
              <div className="h-[560px] flex flex-col items-center justify-center gap-4 text-gray-500 px-6 text-center">
                <span>Impossible de charger le détail des communes (service cartographique momentanément indisponible).</span>
                <button
                  onClick={() => setRetryKey((k) => k + 1)}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700"
                >
                  Réessayer
                </button>
              </div>
            ) : drillLoading || !communeGeo ? (
              <div className="h-[560px] flex items-center justify-center text-gray-400">
                <Loader2 className="animate-spin" size={22} /> <span className="ml-2">Chargement des communes…</span>
              </div>
            ) : (
              <ChoroplethMap
                geo={communeGeo}
                valueByCode={communeValueByCode}
                label={ind.label}
                unit={ind.unite}
                format={ind.fmt}
                onSelectFeature={(c) => navigate(`/territoires?code=${c}`)}
                highlightCode={highlightCode}
                fitBounds
              />
            )
          ) : m === 'epci' ? (
            !geoEpci ? (
              <div className="h-[560px] flex items-center justify-center text-gray-400">
                <Loader2 className="animate-spin" size={22} /> <span className="ml-2">Chargement des intercommunalités…</span>
              </div>
            ) : (
              <ChoroplethMap geo={geoEpci} valueByCode={epciValueByCode} label={ind.label} unit={ind.unite} format={ind.fmt} highlightCode={highlightCode} onSelectFeature={(c) => navigate(`/territoires?code=${c}`)} />
            )
          ) : m === 'etab' ? (
            !etabs ? (
              <div className="h-[560px] flex items-center justify-center text-gray-400">
                <Loader2 className="animate-spin" size={22} /> <span className="ml-2">Chargement des établissements…</span>
              </div>
            ) : (
              <PointMap points={etabPoints} unit={ind.unite} label={ind.label} />
            )
          ) : (
            <ChoroplethMap
              geo={geoDept}
              valueByCode={nationalVals}
              label={ind.label}
              unit={ind.unite}
              format={ind.fmt}
              onSelectFeature={(code) => (ind.communeKey ? setDep(code) : selectOutsider(code))}
              highlightCode={highlightCode}
            />
          )}
        </div>
        {dossier && (
          <div className="mt-3 text-sm">
            <Link to={dossier.to} className="inline-flex items-center gap-1.5 text-gray-600 hover:text-gray-900">
              Aller plus loin : {dossier.label}
              <ArrowRight size={15} />
            </Link>
          </div>
        )}
      </div>

      {/* Croisements suggérés : l'entrée éditoriale, avant le croisement libre */}
      <CroisementsSuggeres onOpen={openCroisement} />

      {/* Analyse, à la maille courante (France ou communes du département) */}
      {deptData && (
        <div id="analyse-bloc">
          <AnalyseBloc
            records={dep ? communeRecords : m === 'epci' && epciData ? epciData : deptData}
            level={dep ? 'commune' : m === 'epci' ? 'epci' : 'dept'}
            niveauNom={dep ? depNomTitre : m === 'epci' ? 'Intercommunalités' : 'France'}
            ind={ind}
            vsInd={vsInd}
            onSetVs={setVs}
            onHoverOutsider={setHighlightCode}
            onSelectOutsider={selectOutsider}
          />
        </div>
      )}
      </div>
    </>
  )
}
