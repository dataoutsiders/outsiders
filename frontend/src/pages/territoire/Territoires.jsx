import { useEffect, useMemo, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import {
  Building2, MapPin, ArrowRight, ArrowLeft, Loader2, Map as MapIcon,
  Info, GraduationCap, Banknote, Users, ArrowUp, ArrowDown, Sparkles,
  GitCompare, Layers, BookOpen, ChevronRight, HeartPulse,
} from 'lucide-react'
import { INDICATEURS, GROUPES, INDICATEUR_BY_ID } from '../../config/indicateurs'
import {
  depFromInsee, niveauFromCode, positionPct, bandeLabel, titleCase,
  popBracket, statsFromValues, EPCI_BRACKETS, ficheHref,
} from '../../lib/territoire'
import { REGIONS_INSEE, REGION_INSEE_BY_CODE, regionInseeOfDep } from '../../lib/regions'
import { loadVectors, findTwins, vecteursDepuis } from '../../lib/jumeau'
import { dansNosDossiers, contexteRegion } from '../../config/dossiersTerritoires'
import ExplorerBar from '../../components/ExplorerBar'
import TerritoireSearch, { buildSearchable } from '../../components/TerritoireSearch'
import ToneCallout from '../../components/ToneCallout'
import { usePageMeta, useRouteMeta } from '../../lib/meta'
import { trackEvent } from '../../lib/analytics'

// Planchers de plausibilité (cohérents avec build_territoires_index.py) pour les
// références calculées à la volée (département, intercommunalités, régions).
const FLOORS = { prix_m2: 100, revenu: 1000 }

const GROUPE_ICON = { École: GraduationCap, Richesse: Banknote, 'Représentation politique': Users, Santé: HeartPulse }
const NIVEAU_ICON = { commune: Building2, epci: Layers, dept: MapPin, region: MapIcon }

// Fichiers chargés à la demande, une seule fois par session.
const jsonCache = new Map()
function loadJson(url) {
  if (!jsonCache.has(url)) {
    jsonCache.set(
      url,
      fetch(url)
        .then((r) => (r.ok ? r.json() : Promise.reject(r.status)))
        .catch((e) => {
          jsonCache.delete(url)
          throw e
        }),
    )
  }
  return jsonCache.get(url)
}

// Clé d'un indicateur selon l'échelle : les intercommunalités suivent le nommage communal
// (atlas/epci.json), les régions le nommage départemental (atlas/regions.json).
const keyOfNiveau = (niveau, ind) => (niveau === 'commune' || niveau === 'epci' ? ind.communeKey : ind.deptKey)

// Territoires de même échelle (jauges) et formule du sous-titre.
const ECHELLE_PAIRS = {
  commune: 'les communes de France',
  dept: 'les départements',
  epci: 'les intercommunalités',
  region: 'les régions',
}
const SITUE = {
  commune: 'situé par rapport à la France',
  dept: 'situé par rapport à la France',
  epci: 'situé parmi les intercommunalités',
  region: 'situé parmi les régions',
}

// Groupe de comparaison « national » selon l'échelle (atypies, description de la page).
const PAIRS_LABEL = {
  commune: 'la France',
  dept: 'la France',
  epci: 'les intercommunalités',
  region: 'les autres régions',
}

// Sources des indicateurs (dédupliquées par lien), citées sous les vues.
const SOURCES = INDICATEURS.filter((ind, i, a) => a.findIndex((x) => x.sourceUrl === ind.sourceUrl) === i)
function SourcesLinks() {
  return SOURCES.map((s, i) => (
    <span key={s.sourceUrl}>
      {i > 0 ? ' · ' : ''}
      <a href={s.sourceUrl} target="_blank" rel="noopener noreferrer" className="underline hover:text-gray-600">
        {s.source}
      </a>
    </span>
  ))
}

// Lecture spécifique de la valeur ajoutée (au lieu d'un simple rang).
function vaRead(v) {
  if (v == null) return 'non disponible'
  if (v > 0.5) return 'fait progresser au-delà des attentes'
  if (v < -0.5) return 'sous-performe au regard du profil social'
  return 'conforme aux attentes'
}

// ───────────────────────── Jauge de position (fiche) ─────────────────────────
function Gauge({ pct, color }) {
  if (pct == null) return null
  return (
    <div className="relative h-2.5 rounded-full bg-gradient-to-r from-gray-100 via-gray-200 to-gray-100 my-2">
      <div className="absolute top-1/2 -translate-y-1/2 w-px h-3 bg-gray-400" style={{ left: '50%' }} />
      <div
        className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 w-3.5 h-3.5 rounded-full border-2 border-white shadow"
        style={{ left: `${pct}%`, backgroundColor: color }}
      />
    </div>
  )
}

function IndicatorCard({ ind, value, st }) {
  const pct = positionPct(value, st)
  const sous = value == null ? 'non disponible' : ind.id === 'va_lycee' ? vaRead(value) : bandeLabel(pct)
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="font-medium text-gray-900">{ind.label}</div>
          <div className="text-xs text-gray-500">{sous}{ind.precision ? ` · ${ind.precision}` : ''}</div>
        </div>
        <div className="text-2xl font-bold shrink-0" style={{ color: value == null ? '#9CA3AF' : ind.couleur }}>
          {value == null ? 'n/d' : ind.fmt(value)}
        </div>
      </div>
      {value != null && pct != null && st && (
        <>
          <Gauge pct={pct} color={ind.couleur} />
          <div className="flex justify-between text-[11px] text-gray-400">
            <span>{ind.fmt(st.min)}</span>
            <span>médiane {ind.fmt(st.median)}</span>
            <span>{ind.fmt(st.max)}</span>
          </div>
        </>
      )}
    </div>
  )
}

// Une ligne du bloc « ce qui sort de l'ordinaire » : indicateur très haut ou très bas
// par rapport au groupe de référence, avec sa position en clair.
function AtypieRow({ ind, val, pct }) {
  const haut = pct >= 50
  const Arrow = haut ? ArrowUp : ArrowDown
  return (
    <div className="flex items-center justify-between gap-3 px-4 py-3">
      <div className="min-w-0">
        <div className="font-medium text-gray-900 truncate">{ind.label}</div>
        <div className="text-xs text-gray-500">{bandeLabel(pct)}</div>
      </div>
      <div className="flex items-center gap-2 shrink-0">
        <Arrow size={16} className={haut ? 'text-emerald-600' : 'text-rose-500'} />
        <span className="text-lg font-bold" style={{ color: ind.couleur }}>{ind.fmt(val)}</span>
      </div>
    </div>
  )
}

// Carte d'un voisin statistique (jumeau ou anti-jumeau), commune ou intercommunalité.
function TwinCard({ kind, t, name, nameByCode, niveau }) {
  const isJ = kind === 'jumeau'
  const nName = t.nom || titleCase(nameByCode[t.code]) || t.code
  const div = INDICATEUR_BY_ID[t.divCol]
  const pairs = niveau === 'epci' ? 'les intercommunalités' : 'les communes'
  return (
    <div className={`border rounded-xl p-4 ${isJ ? 'bg-blue-50 border-blue-100' : 'bg-gray-50 border-gray-200'}`}>
      <div className={`text-xs uppercase tracking-wide font-semibold mb-1 ${isJ ? 'text-blue-700' : 'text-gray-500'}`}>
        {isJ ? 'La plus ressemblante' : 'À taille comparable, la plus différente'}
      </div>
      <div className="flex items-baseline gap-2 flex-wrap">
        <Link to={ficheHref(niveau, t.code)} className="text-lg font-bold text-gray-900 hover:underline">
          {nName}
        </Link>
        {t.km != null && <span className="text-sm text-gray-500">à {t.km} km</span>}
      </div>
      <p className="text-sm text-gray-600 mt-2">
        {isJ
          ? `Ressemble le plus à ${name}, sur ${t.shared} indicateurs.`
          : `La plus éloignée de ${name} parmi ${pairs} de taille voisine.`}{' '}
        {div && (
          <>
            Elles divergent surtout sur <strong>{div.label}</strong> ({div.fmt(t.targetVal)} contre{' '}
            {div.fmt(t.neighborVal)}).
          </>
        )}
      </p>
    </div>
  )
}

// Lecture combinée « aide à la décision » à partir des valeurs + positions.
function buildInsights(vals, pcts, level, deptRec) {
  const out = []
  const ipsId = vals.ips_college_public != null ? 'ips_college_public'
    : vals.ips_ecole_public != null ? 'ips_ecole_public' : null
  const ipsPct = ipsId ? pcts[ipsId] : null
  const va = vals.va_lycee

  if (level === 'dept' && deptRec?.cumul === 'triple-bas')
    out.push({ tone: 'warn', text: "Ségrégation scolaire cumulative : IPS bas à l'école, au collège et au lycée. Le désavantage social se concentre à chaque étage du parcours." })
  if (level === 'dept' && deptRec?.cumul === 'triple-haut')
    out.push({ tone: 'info', text: 'Public favorisé aux trois niveaux (école, collège, lycée), un entre-soi scolaire marqué.' })

  if (ipsPct != null && va != null) {
    if (ipsPct <= 30 && va > 0.5)
      out.push({ tone: 'good', text: "École qui compense : malgré un public plutôt défavorisé, les lycées font progresser les élèves au-delà des attentes. Ce n'est pas un territoire « qui échoue », c'est un territoire désavantagé où l'école joue son rôle." })
    else if (ipsPct <= 30 && va < -0.5)
      out.push({ tone: 'warn', text: "Cumul de fragilités : public défavorisé et valeur ajoutée négative. Le territoire additionne désavantage social et sous-performance scolaire, c'est là qu'un levier éducatif aurait le plus d'effet." })
    else if (ipsPct >= 70 && va < -0.5)
      out.push({ tone: 'info', text: "Résultats portés par le milieu social : public favorisé mais valeur ajoutée négative, les bons résultats doivent davantage aux familles qu'à l'établissement." })
  }

  const rPct = pcts.revenu
  const pPct = pcts.prix_m2
  if (rPct != null && pPct != null && pPct - rPct >= 25)
    out.push({ tone: 'warn', text: 'Tension immobilière : les prix se situent nettement plus haut que les revenus locaux, accès au logement difficile au regard du niveau de vie.' })

  if (pcts.idp != null && pcts.idp >= 85)
    out.push({ tone: 'info', text: "Diversité d'origine élevée parmi les candidats aux municipales, au regard du reste du pays." })

  if (vals.apl_mg != null && vals.apl_mg <= 2.5)
    out.push({ tone: 'warn', text: "Sous-dotation en généralistes : 2,5 consultations accessibles par an et par habitant ou moins, le seuil sous lequel l'Insee parle de commune sous-dotée." })
  if (pcts.apl_mg_60 != null && pcts.apl_mg_60 >= 85)
    out.push({ tone: 'warn', text: "Accès fragile : une part élevée des consultations de généraliste accessibles repose sur des médecins de plus de 60 ans, au regard du reste du pays." })

  return out
}

// ───────────────────────── Fil des échelles (commune -> intercommunalité -> département -> région) ─────────────────────────
function FilEchelles({ items }) {
  const liens = items.filter(Boolean)
  if (!liens.length) return null
  return (
    <nav aria-label="Échelles" className="flex flex-wrap items-center gap-1.5 text-sm text-gray-500 mb-6">
      <span className="text-gray-400">Fait partie de :</span>
      {liens.map((it, i) => {
        const Icone = NIVEAU_ICON[it.niveau] || MapPin
        return (
          <span key={`${it.niveau}-${it.code}`} className="inline-flex items-center gap-1.5">
            {i > 0 && <ChevronRight size={14} className="text-gray-300" />}
            <Link
              to={ficheHref(it.niveau, it.code)}
              className="inline-flex items-center gap-1 rounded-full border border-gray-200 bg-white px-2.5 py-0.5 text-gray-700 hover:border-blue-300 hover:text-blue-700"
            >
              <Icone size={13} className="text-gray-400" /> {it.nom}
            </Link>
          </span>
        )
      })}
    </nav>
  )
}

// ───────────────────────── Membres (communes d'une intercommunalité, départements d'une région) ─────────────────────────
function Membres({ titre, items, niveau, limite = 30 }) {
  const [tout, setTout] = useState(false)
  if (!items || !items.length) return null
  const vus = tout ? items : items.slice(0, limite)
  const Icone = NIVEAU_ICON[niveau] || Building2
  return (
    <section className="mb-8">
      <div className="flex items-center gap-2 mb-3">
        <Icone size={18} className="text-gray-400" />
        <h2 className="text-lg font-bold text-gray-900">{titre}</h2>
      </div>
      <div className="flex flex-wrap gap-2">
        {vus.map((m) => (
          <Link
            key={m.code}
            to={ficheHref(niveau, m.code)}
            className="rounded-lg border border-gray-200 bg-white px-3 py-1.5 text-sm text-gray-800 hover:border-blue-300 hover:text-blue-700"
          >
            {m.nom}
          </Link>
        ))}
      </div>
      {items.length > limite && (
        <button
          type="button"
          onClick={() => setTout((v) => !v)}
          className="mt-3 text-sm text-blue-600 hover:underline"
        >
          {tout ? 'Réduire la liste' : `Voir les ${items.length} ${niveau === 'commune' ? 'communes' : 'départements'}`}
        </button>
      )}
    </section>
  )
}

// ───────────────────────── Dans nos dossiers ─────────────────────────
function DansNosDossiers({ niveau, code, ctx }) {
  const [items, setItems] = useState(null)
  useEffect(() => {
    let alive = true
    setItems(null)
    dansNosDossiers(niveau, code, ctx)
      .then((r) => { if (alive) setItems(r) })
      .catch(() => { if (alive) setItems([]) })
    return () => { alive = false }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [niveau, code, ctx.nom])

  return (
    <section className="mb-8">
      <div className="flex items-center gap-2 mb-1">
        <BookOpen size={18} className="text-violet-500" />
        <h2 className="text-lg font-bold text-gray-900">Dans nos dossiers</h2>
      </div>
      <p className="text-sm text-gray-500 mb-3">
        Ce que nos dossiers disent de ce territoire, avec les précautions de chacun. Un dossier n'apparaît que
        s'il publie un résultat pour ce territoire, à cette échelle.
      </p>
      {items == null ? (
        <div className="text-gray-400 text-sm flex items-center gap-2">
          <Loader2 className="animate-spin" size={15} /> Lecture des dossiers…
        </div>
      ) : items.length === 0 ? (
        <div className="bg-gray-50 border border-gray-200 rounded-xl p-4 text-sm text-gray-600">
          Aucun de nos dossiers ne publie de résultat pour ce territoire à cette échelle.
        </div>
      ) : (
        <div className="space-y-3">
          {items.map((it) => (
            <article key={it.dossier.id} className="bg-white border border-gray-200 rounded-xl p-4">
              <Link
                to={it.lien}
                onClick={() => trackEvent(`fiche-vers-dossier/${it.dossier.id}`, 'Fiche : lien vers un dossier')}
                className="inline-flex items-center gap-1.5 text-sm font-semibold text-violet-700 hover:text-violet-900"
              >
                {it.dossier.titre} <ArrowRight size={14} />
              </Link>
              <p className="text-gray-800 mt-1 leading-relaxed">{it.texte}</p>
              {it.precaution && <p className="text-xs text-gray-500 mt-2 leading-relaxed">{it.precaution}</p>}
              <p className="text-xs text-gray-400 mt-1">
                Source :{' '}
                <a href={it.dossier.sourceUrl} target="_blank" rel="noopener noreferrer" className="underline hover:text-gray-600">
                  {it.dossier.source}
                </a>
              </p>
            </article>
          ))}
        </div>
      )}
      <Link to="/terrains" className="inline-flex items-center gap-1.5 mt-3 text-sm font-medium text-gray-600 hover:text-gray-900">
        Tous les dossiers <ArrowRight size={14} />
      </Link>
    </section>
  )
}

// ───────────────────────── Fiche d'un territoire ─────────────────────────
function FicheTerritoire({ code, level, stats, depts, nameByCode, epciNom }) {
  const deptRec = level === 'dept' ? depts.find((d) => d.code === code) || null : null
  const [rec, setRec] = useState(level === 'dept' ? deptRec : null)
  const [depObj, setDepObj] = useState(null) // communes du département (fiche commune)
  const [pairs, setPairs] = useState(null) // intercommunalités ou régions (fiches epci / region)
  const [regionSources, setRegionSources] = useState(null)
  const [membres, setMembres] = useState(null) // epci-communes.json
  const [state, setState] = useState(level === 'dept' ? (deptRec ? 'ready' : 'error') : 'loading')
  // Groupe de référence pour les atypies ('nation' | 'departement' | 'taille').
  const [ref, setRef] = useState('nation')

  useEffect(() => {
    let alive = true
    const ok = (fn) => (x) => { if (alive) fn(x) }
    const ko = () => { if (alive) setState('error') }
    if (level === 'commune') {
      loadJson(`/data/atlas/communes/${depFromInsee(code)}.json`)
        .then(ok((obj) => { setDepObj(obj); setRec(obj[code] || {}); setState('ready') }))
        .catch(ko)
    } else if (level === 'epci') {
      loadJson('/data/atlas/epci.json')
        .then(ok((list) => {
          const r = list.find((e) => e.code === code)
          setPairs(list)
          setRec(r || null)
          setState(r ? 'ready' : 'error')
        }))
        .catch(ko)
    } else if (level === 'region') {
      loadJson('/data/atlas/regions.json')
        .then(ok((d) => {
          const r = d.regions.find((x) => x.code === code)
          setPairs(d.regions)
          setRegionSources(d.sources || {})
          setRec(r || null)
          setState(r ? 'ready' : 'error')
        }))
        .catch(ko)
    }
    if (level === 'commune' || level === 'epci')
      loadJson('/data/atlas/epci-communes.json').then(ok(setMembres)).catch(() => { if (alive) setMembres({}) })
    return () => { alive = false }
  }, [code, level])

  const keyOf = (ind) => keyOfNiveau(level, ind)
  const get = (ind) => (rec ? rec[keyOf(ind)] ?? null : null)

  // Repères des pairs (intercommunalités ou régions), calculés à la volée.
  const pairStats = useMemo(() => {
    if (!pairs) return {}
    const out = {}
    for (const ind of INDICATEURS)
      out[ind.id] = statsFromValues(pairs.map((p) => p[keyOfNiveau(level, ind)] ?? null), FLOORS[ind.id])
    return out
  }, [pairs, level])

  const stOf = (ind) => {
    if (level === 'commune') return stats[ind.id]?.commune || null
    if (level === 'dept') return stats[ind.id]?.dept || null
    return pairStats[ind.id] || null
  }

  // Repères du département (communes du même département), calculés à la volée.
  const deptStats = useMemo(() => {
    if (level !== 'commune' || !depObj) return {}
    const communes = Object.values(depObj)
    const out = {}
    for (const ind of INDICATEURS) {
      out[ind.id] = statsFromValues(communes.map((c) => c[ind.communeKey] ?? null), FLOORS[ind.id])
    }
    return out
  }, [depObj, level])

  const bracket = rec && (level === 'commune' || level === 'epci')
    ? popBracket(rec.pop, level === 'epci' ? EPCI_BRACKETS : undefined)
    : null

  // Repères des intercommunalités de taille comparable.
  const epciTailleStats = useMemo(() => {
    if (level !== 'epci' || !pairs || !bracket) return {}
    const memes = pairs.filter((p) => popBracket(p.pop, EPCI_BRACKETS)?.id === bracket.id)
    const out = {}
    for (const ind of INDICATEURS) out[ind.id] = statsFromValues(memes.map((p) => p[ind.communeKey] ?? null), FLOORS[ind.id])
    return out
  }, [pairs, level, bracket?.id]) // eslint-disable-line react-hooks/exhaustive-deps

  // Repères selon le groupe de référence choisi (avec repli sur le national).
  const stForRef = (ind) => {
    if (ref === 'departement') return deptStats[ind.id] || stOf(ind)
    if (ref === 'taille' && bracket)
      return (level === 'epci' ? epciTailleStats[ind.id] : stats[ind.id]?.tranches?.[bracket.id]) || stOf(ind)
    return stOf(ind)
  }

  const { valsMap, pcts, nRenseignes } = useMemo(() => {
    const v = {}, p = {}
    let n = 0
    for (const ind of INDICATEURS) {
      const val = get(ind)
      v[ind.id] = val
      p[ind.id] = positionPct(val, stOf(ind))
      if (val != null) n++
    }
    return { valsMap: v, pcts: p, nRenseignes: n }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [rec, level, pairStats])

  // Atypies : indicateurs où le territoire s'écarte le plus de la référence choisie.
  const atypies = useMemo(() => {
    const rows = []
    for (const ind of INDICATEURS) {
      const val = get(ind)
      if (val == null) continue
      const st = stForRef(ind)
      const pct = positionPct(val, st)
      if (pct == null) continue
      rows.push({ ind, val, pct, st, ecart: Math.abs(pct - 50) })
    }
    rows.sort((a, b) => b.ecart - a.ecart)
    return rows
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [rec, level, ref, deptStats, pairStats, epciTailleStats, bracket?.id])

  // Jumeau statistique : communes (>= 1 000 hab., fichier de vecteurs) ou intercommunalités
  // (calcul sur atlas/epci.json, mêmes indicateurs standardisés).
  const [twinsCommune, setTwinsCommune] = useState(null)
  useEffect(() => {
    setTwinsCommune(null)
    if (level !== 'commune' || state !== 'ready' || !rec || (rec.pop ?? 0) < 1000) return
    let alive = true
    loadVectors()
      .then((data) => { if (alive) setTwinsCommune(findTwins(data, code)) })
      .catch(() => {})
    return () => { alive = false }
  }, [code, level, state, rec])
  const twinsEpci = useMemo(() => {
    if (level !== 'epci' || !pairs || !rec) return null
    // Hors santé : mêmes critères de ressemblance qu'avant l'ajout de l'accès aux soins.
    return findTwins(vecteursDepuis(pairs, INDICATEURS.filter((i) => i.groupe !== 'Santé').map((i) => i.communeKey)), code)
  }, [level, pairs, rec, code])
  const twins = level === 'epci' ? twinsEpci : twinsCommune

  // ── Échelles : appartenance (commune -> intercommunalité -> département -> région) ──
  const epciDeCommune = useMemo(() => {
    if (level !== 'commune' || !membres) return null
    for (const [siren, m] of Object.entries(membres)) if (m.communes.includes(code)) return siren
    return null
  }, [level, membres, code])

  const depNom = (d) => titleCase((depts.find((x) => x.code === d) || {}).dep || nameByCode[d] || d)
  const regionInfo = level === 'region' ? REGION_INSEE_BY_CODE[code] || null : null
  const epciMembres = level === 'epci' && membres ? membres[code] || null : null

  const name = level === 'dept'
    ? titleCase((deptRec && deptRec.dep) || nameByCode[code] || code)
    : level === 'epci'
      ? (rec && rec.nom) || epciNom[code] || `Intercommunalité ${code}`
      : level === 'region'
        ? (regionInfo && regionInfo.nom) || `Région ${code}`
        : nameByCode[code] || `Commune ${code}`

  // Contexte transmis au registre des dossiers (stable tant que le territoire ne change pas).
  const ctxDossiers = useMemo(
    () => (level === 'region' && regionInfo ? contexteRegion(regionInfo) : { nom: name }),
    [level, regionInfo, name],
  )

  // Territoire consulté, compté à part (le chemin de page peut perdre le code selon les réglages).
  useEffect(() => {
    trackEvent(`fiche/${level}/${code}`, `Fiche : ${name}`)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [level, code])

  usePageMeta(
    name ? `${name} : atypies, jumeau statistique, indicateurs` : null,
    name
      ? `${name} situé par rapport à ${PAIRS_LABEL[level]} : ce qui sort de l'ordinaire, ce qu'en disent nos dossiers et tous ses indicateurs, sources citées.`
      : null,
  )

  if (state === 'loading')
    return (
      <div className="py-20 text-center text-gray-400">
        <Loader2 className="animate-spin inline" size={22} /> Chargement de la fiche…
      </div>
    )
  if (state === 'error' || (level === 'region' && !regionInfo))
    return (
      <div className="py-20 text-center text-gray-500">
        Territoire introuvable.{' '}
        <Link to="/territoires" className="text-blue-600">Revenir à la recherche</Link>.
      </div>
    )

  const insights = level === 'region' ? [] : buildInsights(valsMap, pcts, level, deptRec)

  // Groupes de référence proposés + sélection des indicateurs les plus atypiques.
  const refOptions = level === 'commune'
    ? [
        { id: 'nation', label: 'la France' },
        { id: 'departement', label: 'son département' },
        { id: 'taille', label: bracket ? 'sa taille' : 'sa taille (n/d)', disabled: !bracket },
      ]
    : level === 'epci'
      ? [
          { id: 'nation', label: 'les intercommunalités' },
          { id: 'taille', label: bracket ? 'celles de sa taille' : 'sa taille (n/d)', disabled: !bracket },
        ]
      : [{ id: 'nation', label: PAIRS_LABEL[level] }]
  const refMot = (refOptions.find((o) => o.id === ref) || refOptions[0]).label
  const forts = atypies.filter((r) => r.ecart >= 12).slice(0, 6)
  const topAtypies = forts.length >= 3 ? forts : atypies.slice(0, Math.min(3, atypies.length))

  // Département de référence (carte, fil des échelles).
  const dep = level === 'commune' ? depFromInsee(code) : level === 'dept' ? code : level === 'epci' ? epciMembres?.dep : null
  const region = level === 'region' ? null : dep ? regionInseeOfDep(dep) : null
  const firstInd = INDICATEURS.find((ind) => get(ind) != null) || INDICATEUR_BY_ID.ips_college_public
  const mapHref = level === 'epci'
    ? `/atlas?i=${firstInd.id}&m=epci`
    : level === 'region'
      ? `/atlas?i=${firstInd.id}`
      : `/atlas?i=${firstInd.id}&dep=${dep}`
  const mapLabel = level === 'epci'
    ? 'Voir les intercommunalités sur la carte'
    : level === 'region'
      ? 'Voir les départements sur la carte'
      : `Voir ${name} sur la carte`

  // Fil des échelles : de la plus large à la plus fine.
  const fil = []
  if (region) fil.push({ niveau: 'region', code: region.code, nom: region.nom })
  if (level !== 'dept' && dep) fil.push({ niveau: 'dept', code: dep, nom: depNom(dep) })
  if (level === 'commune' && epciDeCommune)
    fil.push({ niveau: 'epci', code: epciDeCommune, nom: epciNom[epciDeCommune] || `Intercommunalité ${epciDeCommune}` })

  // Membres : communes d'une intercommunalité, départements d'une région.
  const membresListe = level === 'epci' && epciMembres
    ? epciMembres.communes.map((c) => ({ code: c, nom: nameByCode[c] || c }))
    : level === 'region' && regionInfo
      ? regionInfo.deps.map((d) => ({ code: d, nom: depNom(d) }))
      : null

  // Indicateurs sans valeur à l'échelle régionale (prix DVF, ou données non publiées outre-mer).
  const absentsRegion = level === 'region' ? INDICATEURS.filter((ind) => get(ind) == null) : []

  const Icone = NIVEAU_ICON[level] || MapPin
  const sousTitre = level === 'commune'
    ? `Commune · département ${dep}`
    : level === 'epci'
      ? `Intercommunalité · ${epciMembres ? `${epciMembres.communes.length} communes` : 'communes n/d'}${rec?.pop ? ` · ${rec.pop.toLocaleString('fr-FR')} hab.` : ''}${epciMembres && epciMembres.deps.length > 1 ? ` · sur ${epciMembres.deps.length} départements` : ''}`
      : level === 'region'
        ? `Région · ${regionInfo.deps.length} département${regionInfo.deps.length > 1 ? 's' : ''}${rec?.pop ? ` · ${rec.pop.toLocaleString('fr-FR')} hab.` : ''}`
        : 'Département'

  return (
    <div className="max-w-4xl mx-auto px-4 py-10">
      <Link to="/territoires" className="inline-flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-800 mb-4">
        <ArrowLeft size={15} /> Tous les territoires
      </Link>

      <div className="flex items-center gap-3 mb-1">
        <Icone className="text-blue-500 shrink-0" size={26} />
        <h1 className="text-3xl font-bold text-gray-900">{name}</h1>
      </div>
      <p className="text-gray-500 mb-3">
        {sousTitre} · {nRenseignes} indicateur{nRenseignes > 1 ? 's' : ''} renseigné{nRenseignes > 1 ? 's' : ''} ·{' '}
        {SITUE[level]}
      </p>
      <FilEchelles items={fil} />

      {nRenseignes === 0 ? (
        <div className="bg-gray-50 border border-gray-200 rounded-xl p-6 text-gray-600 mb-8">
          Aucune donnée disponible pour ce territoire dans nos sources actuelles.
        </div>
      ) : (
        <>
          {/* Ce qui sort de l'ordinaire (mener avec les atypies) */}
          {topAtypies.length > 0 && (
            <section className="mb-8">
              <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
                <div className="flex items-center gap-2">
                  <Sparkles size={18} className="text-amber-500" />
                  <h2 className="text-lg font-bold text-gray-900">Ce qui sort de l'ordinaire</h2>
                </div>
                {refOptions.length > 1 && (
                  <div className="inline-flex items-center gap-2 text-sm">
                    <span className="text-gray-500">par rapport à</span>
                    <div className="inline-flex rounded-lg border border-gray-200 overflow-hidden">
                      {refOptions.map((o) => (
                        <button
                          key={o.id}
                          onClick={() => !o.disabled && setRef(o.id)}
                          disabled={o.disabled}
                          className={`px-2.5 py-1 transition-colors ${
                            ref === o.id ? 'bg-gray-800 text-white font-medium' : 'bg-white text-gray-600 hover:bg-gray-50'
                          } ${o.disabled ? 'opacity-40 cursor-not-allowed' : ''}`}
                        >
                          {o.label}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
              <p className="text-sm text-gray-500 mb-3">
                Les indicateurs où {name} s'écarte le plus de {refMot}
                {ref === 'taille' && bracket ? ` (${bracket.label})` : ''}. Un territoire se lit
                d'abord par ce qui le distingue.
                {level === 'region' && ' Avec 18 régions au plus, la comparaison reste grossière.'}
              </p>
              <div className="bg-white border border-gray-200 rounded-xl divide-y divide-gray-100">
                {topAtypies.map((r) => (
                  <AtypieRow key={r.ind.id} ind={r.ind} val={r.val} pct={r.pct} />
                ))}
              </div>
            </section>
          )}

          {/* Aide à la décision */}
          {insights.length > 0 && (
            <section className="mb-8">
              <h2 className="text-lg font-bold text-gray-900 mb-3">Ce que ça veut dire</h2>
              <div className="space-y-3">
                {insights.map((it, i) => (
                  <ToneCallout key={i} tone={it.tone}>{it.text}</ToneCallout>
                ))}
              </div>
            </section>
          )}

          {/* Jumeau statistique */}
          {(level === 'commune' || level === 'epci') && twins?.jumeau && (
            <section className="mb-8">
              <div className="flex items-center gap-2 mb-3">
                <GitCompare size={18} className="text-blue-500" />
                <h2 className="text-lg font-bold text-gray-900">Le jumeau statistique</h2>
              </div>
              <div className="grid sm:grid-cols-2 gap-3">
                <TwinCard kind="jumeau" t={twins.jumeau} name={name} nameByCode={nameByCode} niveau={level} />
                {twins.antiJumeau && (
                  <TwinCard kind="anti" t={twins.antiJumeau} name={name} nameByCode={nameByCode} niveau={level} />
                )}
              </div>
              <p className="text-xs text-gray-400 mt-2">
                Ressemblance mesurée sur {twins.jumeau.shared} indicateurs standardisés (z-scores),
                {level === 'epci'
                  ? ` parmi les ${pairs.length.toLocaleString('fr-FR')} intercommunalités ; la plus différente est cherchée parmi celles de la moitié au double de sa population.`
                  : ' parmi les communes de 1 000 habitants et plus.'}{' '}
                Calcul fait dans votre navigateur.
              </p>
            </section>
          )}

          {/* Indicateurs par thème */}
          {GROUPES.map((g) => {
            const GIcon = GROUPE_ICON[g.nom] || Info
            const inds = g.indicateurs.filter((ind) => (level === 'region' ? get(ind) != null : keyOf(ind) != null))
            const dispo = inds.some((ind) => get(ind) != null)
            if (!dispo) return null
            return (
              <section key={g.nom} className="mb-8">
                <div className="flex items-center gap-2 mb-3">
                  <GIcon size={18} className="text-gray-400" />
                  <h2 className="text-lg font-bold text-gray-900">{g.nom}</h2>
                </div>
                <div className="grid sm:grid-cols-2 gap-3">
                  {inds.map((ind) => (
                    <IndicatorCard key={ind.id} ind={ind} value={get(ind)} st={stOf(ind)} />
                  ))}
                </div>
              </section>
            )
          })}

          {level === 'region' && (
            <div className="bg-gray-50 border border-gray-200 rounded-xl p-4 text-sm text-gray-600 mb-8">
              <p>
                Valeurs régionales : officielles quand la source les publie à cette échelle (Insee, Filosofi
                et recensement) ; sinon recalculées avec la même définition qu'au département (naissances,
                diversité des candidats, IPS et valeur ajoutée, moyennes des établissements). Aucune n'est
                une moyenne de valeurs départementales.
              </p>
              {absentsRegion.length > 0 && (
                <p className="mt-2">
                  Non affichés pour cette région :{' '}
                  {absentsRegion.map((ind) => ind.label.toLowerCase()).join(', ')}.{' '}
                  {absentsRegion.some((ind) => ind.id === 'prix_m2') &&
                    "Le prix immobilier n'a pas de médiane régionale publiée (statistiques DVF), et une médiane ne se déduit pas des médianes départementales. "}
                  {absentsRegion.some((ind) => ind.id !== 'prix_m2') &&
                    'Les autres manquent dans la source à cette échelle (outre-mer).'}
                </p>
              )}
              {regionSources && (
                <details className="mt-2">
                  <summary className="cursor-pointer text-gray-500">Origine de chaque valeur</summary>
                  <ul className="mt-2 space-y-0.5 text-xs text-gray-500">
                    {INDICATEURS.filter((ind) => regionSources[ind.deptKey]).map((ind) => (
                      <li key={ind.id}><strong>{ind.label}</strong> : {regionSources[ind.deptKey]}</li>
                    ))}
                  </ul>
                </details>
              )}
            </div>
          )}
        </>
      )}

      {/* Membres */}
      {membresListe && (
        <Membres
          titre={level === 'epci' ? `Les ${membresListe.length} communes membres` : `Les ${membresListe.length} départements`}
          items={membresListe}
          niveau={level === 'epci' ? 'commune' : 'dept'}
        />
      )}

      {/* Dans nos dossiers (remplace les anciens liens fixes vers deux dossiers) */}
      <DansNosDossiers niveau={level} code={code} ctx={ctxDossiers} />

      {/* Suite */}
      {nRenseignes > 0 && (
        <>
          <div className="flex flex-wrap gap-3 mt-8">
            <Link to={mapHref} className="inline-flex items-center gap-2 px-4 py-2.5 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700">
              <MapIcon size={18} /> {mapLabel}
            </Link>
          </div>
          <p className="text-xs text-gray-400 mt-6">
            La barre situe le territoire parmi {ECHELLE_PAIRS[level]}{' '}
            (jauge gauche = bas, droite = haut ; repère central = médiane). Sources : <SourcesLinks />. Les
            indicateurs ne se valent pas comme jugement : ils décrivent, ils n'évaluent pas.
          </p>
        </>
      )}
    </div>
  )
}

// Barre de distribution nationale (tableau de bord) : étendue + bande P10–P90 + médiane.
function RangeBar({ st, color }) {
  if (!st || st.max === st.min) return null
  const pos = (x) => ((x - st.min) / (st.max - st.min)) * 100
  return (
    <div className="relative h-2.5 rounded-full bg-gray-100 my-2">
      <div
        className="absolute top-0 h-full rounded-full opacity-30"
        style={{ left: `${pos(st.p10)}%`, width: `${pos(st.p90) - pos(st.p10)}%`, backgroundColor: color }}
      />
      <div className="absolute top-1/2 -translate-y-1/2 w-1 h-3.5 rounded-full" style={{ left: `${pos(st.median)}%`, backgroundColor: color }} />
    </div>
  )
}

// ───────────────────────── Tableau de bord national ─────────────────────────
function Dashboard({ stats, depts, searchable, onSelect }) {
  useRouteMeta('/territoires')
  const extremes = (deptKey) => {
    const arr = depts.filter((d) => d[deptKey] != null).map((d) => ({ nom: titleCase(d.dep), v: d[deptKey] }))
    if (!arr.length) return null
    arr.sort((a, b) => b.v - a.v)
    return { hi: arr[0], lo: arr[arr.length - 1] }
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-10">
      <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-2">Situer un territoire</h1>
      <p className="text-lg text-gray-600 mb-2 max-w-2xl">
        Choisissez une commune, une intercommunalité, un département ou une région : vous verrez d'un coup
        d'œil tous les indicateurs réunis et situés par rapport aux territoires de même échelle, et ce que
        nos dossiers en disent. Un outil de lecture pour décider.
      </p>
      <p className="text-sm text-gray-400 mb-6">
        À ne pas confondre avec les <Link to="/terrains" className="underline hover:text-gray-600">dossiers</Link>{' '}
        (une population analysée sous tous les angles). Ici : un lieu, tous les indicateurs.
      </p>

      <div className="mb-4">
        <TerritoireSearch searchable={searchable} onSelect={onSelect} autoFocus />
      </div>
      <div className="mb-12 flex flex-wrap items-center gap-2 text-sm">
        <span className="text-gray-400">Ou une région :</span>
        {REGIONS_INSEE.map((r) => (
          <Link
            key={r.code}
            to={ficheHref('region', r.code)}
            className="rounded-full border border-gray-200 bg-white px-2.5 py-0.5 text-gray-600 hover:border-blue-300 hover:text-blue-700"
          >
            {r.nom}
          </Link>
        ))}
      </div>

      <h2 className="text-2xl font-bold text-gray-900 mb-1">La France en un coup d'œil</h2>
      <p className="text-gray-500 mb-6">
        Pour chaque indicateur : la médiane des départements, l'écart entre eux (bande = 8 départements sur 10),
        et les extrêmes.
      </p>

      <div className="space-y-8">
        {GROUPES.map((g) => {
          const GIcon = GROUPE_ICON[g.nom] || Info
          return (
            <section key={g.nom}>
              <div className="flex items-center gap-2 mb-3">
                <GIcon size={18} className="text-gray-400" />
                <h3 className="text-lg font-bold text-gray-900">{g.nom}</h3>
              </div>
              <div className="bg-white border border-gray-200 rounded-xl divide-y divide-gray-100">
                {g.indicateurs.map((ind) => {
                  const st = stats[ind.id]?.dept
                  const ext = extremes(ind.deptKey)
                  if (!st) return null
                  return (
                    <div key={ind.id} className="p-4">
                      <div className="flex items-baseline justify-between gap-3">
                        <span className="font-medium text-gray-900">{ind.label}</span>
                        <span className="text-lg font-bold shrink-0" style={{ color: ind.couleur }}>
                          {ind.fmt(st.median)}
                        </span>
                      </div>
                      <RangeBar st={st} color={ind.couleur} />
                      {ext && (
                        <div className="flex justify-between text-[11px] text-gray-400">
                          <span>↓ {ext.lo.nom} · {ind.fmt(ext.lo.v)}</span>
                          <span>↑ {ext.hi.nom} · {ind.fmt(ext.hi.v)}</span>
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
            </section>
          )
        })}
      </div>

      <p className="text-xs text-gray-400 mt-8">
        Vue nationale calculée sur les départements (métropole + DOM). Sources : <SourcesLinks />.
      </p>
    </div>
  )
}

// ───────────────────────── Page ─────────────────────────
export default function Territoires() {
  const [params, setParams] = useSearchParams()
  const code = params.get('code')
  // Adressage : ?code=<commune ou département> (inchangé), ?niveau=epci&code=<SIREN>,
  // ?niveau=region&code=<code région Insee>. Voir niveauFromCode.
  const niveau = code ? niveauFromCode(code, params.get('niveau')) : null
  const [stats, setStats] = useState(null)
  const [depts, setDepts] = useState(null)
  const [index, setIndex] = useState(null)

  useEffect(() => {
    Promise.all([
      fetch('/data/atlas/stats-nationales.json').then((r) => r.json()),
      fetch('/data/atlas/departements.json').then((r) => r.json()),
    ])
      .then(([s, d]) => { setStats(s); setDepts(d) })
      .catch(() => { setStats({}); setDepts([]) })
    fetch('/data/atlas/territoires-index.json')
      .then((r) => r.json())
      .then(setIndex)
      .catch(() => setIndex({ deps: [], communes: [], epci: [], regions: [] }))
  }, [])

  const { nameByCode, epciNom } = useMemo(() => {
    const m = {}, e = {}
    if (index) {
      for (const [c, n] of index.deps) m[c] = n
      for (const [c, n] of index.communes) m[c] = n
      for (const [c, n] of index.epci || []) e[c] = n
    }
    return { nameByCode: m, epciNom: e }
  }, [index])

  const searchable = useMemo(() => (index ? buildSearchable(index) : null), [index])

  const select = (c, niv) =>
    setParams(() => {
      const n = new URLSearchParams()
      if (niv === 'epci' || niv === 'region') n.set('niveau', niv)
      n.set('code', c)
      return n
    })

  if (!stats || !depts)
    return (
      <div className="py-20 text-center text-gray-400">
        <Loader2 className="animate-spin inline" size={22} /> Chargement…
      </div>
    )

  return (
    <>
      <ExplorerBar decoupage="territoire" mode={code ? 'fiche' : 'tableau'} />
      {code ? (
        <FicheTerritoire
          key={`${niveau}-${code}`}
          code={code}
          level={niveau}
          stats={stats}
          depts={depts}
          nameByCode={nameByCode}
          epciNom={epciNom}
        />
      ) : (
        <Dashboard stats={stats} depts={depts} searchable={searchable} onSelect={select} />
      )}
    </>
  )
}
