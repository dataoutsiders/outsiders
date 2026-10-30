import { useEffect, useMemo, useState } from 'react'
import {
  Upload,
  ShieldCheck,
  Loader2,
  AlertCircle,
  Users,
  Globe,
  Cake,
  Info,
  RotateCcw,
  Sparkles,
} from 'lucide-react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts'
import { loadEngine, proportionZTest } from '../../tools/onomastics/engine.js'
import { useRouteMeta } from '../../lib/meta'
import { trackEvent } from '../../lib/analytics'

// ============================================================
// Parsing CSV/TSV côté client (aucune dépendance)
// ============================================================
function detectDelimiter(line) {
  const counts = { ';': 0, ',': 0, '\t': 0 }
  let q = false
  for (const c of line) {
    if (c === '"') q = !q
    else if (!q && c in counts) counts[c]++
  }
  return Object.entries(counts).sort((a, b) => b[1] - a[1])[0][0]
}

function parseLine(line, delim) {
  const out = []
  let cur = ''
  let q = false
  for (let i = 0; i < line.length; i++) {
    const c = line[i]
    if (c === '"') {
      if (q && line[i + 1] === '"') {
        cur += '"'
        i++
      } else q = !q
    } else if (c === delim && !q) {
      out.push(cur)
      cur = ''
    } else cur += c
  }
  out.push(cur)
  return out.map((s) => s.trim())
}

function parseDelimited(text) {
  const lines = text.replace(/\r/g, '').split('\n').filter((l) => l.length)
  if (lines.length < 2) throw new Error('Fichier vide ou sans données.')
  const delim = detectDelimiter(lines[0])
  const headers = parseLine(lines[0], delim)
  const rows = []
  for (let i = 1; i < lines.length; i++) {
    const cells = parseLine(lines[i], delim)
    const row = {}
    headers.forEach((h, j) => (row[h] = cells[j] ?? ''))
    rows.push(row)
  }
  return { headers, rows, delim }
}

// Détection auto des colonnes nom / prénom à partir des en-têtes.
function guessColumn(headers, kind) {
  const norm = (s) => s.toLowerCase()
  if (kind === 'firstname') {
    return headers.find((h) => /pr[ée]nom|firstname|first name|given/.test(norm(h))) || ''
  }
  return (
    headers.find(
      (h) => /\bnom\b|surname|lastname|last name|family|patronyme/.test(norm(h)) && !/pr[ée]nom/.test(norm(h)),
    ) || ''
  )
}

// Sépare une colonne « nom complet » selon l'ordre choisi.
function splitFullname(value, order) {
  const tokens = String(value || '').trim().split(/\s+/).filter(Boolean)
  if (tokens.length === 0) return { surname: '', firstname: '' }
  if (tokens.length === 1) return { surname: tokens[0], firstname: tokens[0] }
  if (order === 'nom-prenom') {
    return { firstname: tokens[tokens.length - 1], surname: tokens.slice(0, -1).join(' ') }
  }
  return { firstname: tokens[0], surname: tokens.slice(1).join(' ') }
}

// ============================================================
// Contexte de comparaison IDP (Kheddache & L'Horty, 2023)
// ============================================================
// En dessous de ce nombre de noms reconnus, un pourcentage décrirait presque des individus :
// l'outil ne mesure que des groupes, il refuse donc le calcul.
const MIN_NOMS = 30

const IDP_REFERENCES = [
  { label: 'EDF masculine (foot)', value: 73.9 },
  { label: 'Avocats', value: 29.1 },
  { label: 'Députés (2022)', value: 11.9 },
  { label: 'Population française', value: 7.0, ref: true },
  { label: 'Sénateurs', value: 4.5 },
  { label: 'Élus municipaux 2026', value: 2.3 },
]

const COLORS = {
  rouge: '#EF4444',
  orange: '#F59E0B',
  vert: '#10B981',
  bleu: '#3B82F6',
  indigo: '#6366F1',
  violet: '#8B5CF6',
  gris: '#9CA3AF',
}

const DECADE_LABELS = [
  '1900', '1910', '1920', '1930', '1940', '1950', '1960',
  '1970', '1980', '1990', '2000', '2010', '2020',
]

// ============================================================
// Petits composants de restitution
// ============================================================
function SignifBadge({ significant, gapPct }) {
  if (significant == null) return null
  if (!significant) {
    return (
      <span className="inline-block px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-600">
        écart non significatif
      </span>
    )
  }
  const sur = gapPct > 0
  return (
    <span
      className={`inline-block px-2 py-0.5 rounded-full text-xs font-medium ${
        sur ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-700'
      }`}
    >
      {sur ? 'sur' : 'sous'}-représentation significative
    </span>
  )
}

function Coverage({ n, coverage }) {
  return (
    <p className="text-xs text-gray-500 mt-3">
      Calculé sur {n.toLocaleString('fr-FR')} noms reconnus ({Math.round(coverage * 100)}% du
      fichier). Les noms hors référentiel sont exclus.
    </p>
  )
}

function ResultCard({ icon: Icon, color, title, children }) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
      <div className="flex items-center gap-2 mb-4">
        <div className="p-2 rounded-lg" style={{ backgroundColor: color + '20' }}>
          <Icon size={20} style={{ color }} />
        </div>
        <h3 className="font-semibold text-gray-900">{title}</h3>
      </div>
      {children}
    </div>
  )
}

function BigStat({ value, unit, ci }) {
  return (
    <div className="mb-3">
      <span className="text-4xl font-bold text-gray-900">{value}</span>
      <span className="text-xl text-gray-500 ml-1">{unit}</span>
      {ci && <span className="block text-xs text-gray-400 mt-1">intervalle de confiance 95% : {ci}</span>}
    </div>
  )
}

// ============================================================
// Page
// ============================================================
export default function RepresentativiteTool() {
  useRouteMeta('/outils/representativite')
  const [engine, setEngine] = useState(null)
  const [engineState, setEngineState] = useState('loading')
  const [parsed, setParsed] = useState(null)
  const [filename, setFilename] = useState('')

  const [colMode, setColMode] = useState('split') // 'split' | 'single'
  const [surnameCol, setSurnameCol] = useState('')
  const [firstnameCol, setFirstnameCol] = useState('')
  const [fullnameCol, setFullnameCol] = useState('')
  const [fullnameOrder, setFullnameOrder] = useState('prenom-nom')

  const [baselinePct, setBaselinePct] = useState(7)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [dragOver, setDragOver] = useState(false)

  useEffect(() => {
    loadEngine()
      .then((e) => {
        setEngine(e)
        setEngineState('ready')
      })
      .catch(() => setEngineState('error'))
  }, [])

  function loadText(text, name) {
    setError(null)
    setResult(null)
    try {
      const p = parseDelimited(text)
      setParsed(p)
      setFilename(name)
      const sn = guessColumn(p.headers, 'surname')
      const fn = guessColumn(p.headers, 'firstname')
      setSurnameCol(sn)
      setFirstnameCol(fn)
      setFullnameCol(p.headers[0] || '')
      setColMode(sn || fn ? 'split' : 'single')
    } catch (e) {
      setError(e.message || 'Impossible de lire le fichier.')
      setParsed(null)
    }
  }

  async function handleFile(file) {
    loadText(await file.text(), file.name)
  }

  async function loadExample() {
    try {
      const text = await fetch('/data/onomastics/exemple_noms.csv').then((r) => r.text())
      loadText(text, 'exemple_noms.csv')
    } catch {
      setError("Impossible de charger l'exemple.")
    }
  }

  function runAnalysis() {
    if (!engine || !parsed) return
    const keys = {}
    if (colMode === 'single') {
      if (!fullnameCol) return setError('Choisissez la colonne « nom complet ».')
      keys.surname = (r) => splitFullname(r[fullnameCol], fullnameOrder).surname
      keys.firstname = (r) => splitFullname(r[fullnameCol], fullnameOrder).firstname
    } else {
      if (!surnameCol && !firstnameCol) return setError('Choisissez au moins une colonne (nom et/ou prénom).')
      if (surnameCol) keys.surname = (r) => r[surnameCol]
      if (firstnameCol) keys.firstname = (r) => r[firstnameCol]
    }
    setError(null)
    const res = engine.analyze(parsed.rows, keys)
    const tropPeu = (n) => n > 0 && n < MIN_NOMS
    const masques = []
    if (tropPeu(res.diversity.n)) {
      res.diversity = { ...res.diversity, pct: null }
      masques.push('la diversité patronymique')
    }
    if (tropPeu(res.gender.n)) {
      res.gender = { ...res.gender, pct: null }
      masques.push('le taux de féminisation')
    }
    if (tropPeu(res.age.n)) {
      res.age = { ...res.age, n: 0, distributionPct: null }
      masques.push("l'âge estimé")
    }
    const affiche = res.diversity.pct != null || res.gender.pct != null || res.age.n > 0
    if (!affiche) {
      setResult(null)
      return setError(
        `Il faut au moins ${MIN_NOMS} noms reconnus pour un résultat : en dessous, un pourcentage décrirait presque des personnes, pas un groupe.`
      )
    }
    setResult({ ...res, masques })
    trackEvent('outil-representativite', 'Outil Représentativité : analyse lancée')
  }

  function reset() {
    setParsed(null)
    setResult(null)
    setError(null)
    setFilename('')
  }

  const fmt = (x, d = 1) => (x == null ? '–' : x.toFixed(d).replace('.', ','))

  // Diversité recalculée selon la baseline choisie (sans relancer l'analyse).
  const diversityView = useMemo(() => {
    if (!result || result.diversity.pct == null) return null
    const d = result.diversity
    const test = proportionZTest(d.successes, d.n, baselinePct / 100)
    return { ...d, baselinePct, gapPct: d.pct - baselinePct, significant: test.significant }
  }, [result, baselinePct])

  // Données du graphe de comparaison (calculées une seule fois).
  const compareData = useMemo(() => {
    if (!result || result.diversity.pct == null) return []
    return [
      { label: 'Votre fichier', value: Number(result.diversity.pct.toFixed(1)), vous: true },
      ...IDP_REFERENCES,
    ].sort((a, b) => b.value - a.value)
  }, [result])

  return (
    <div className="py-12 px-4">
      <div className="max-w-5xl mx-auto">
        {/* En-tête */}
        <header className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-3">
            Représentativité d'un fichier de noms
          </h1>
          <p className="text-xl text-gray-600">
            Déposez une liste de noms (élus, salariés, candidats, adhérents…) et mesurez sa
            diversité patronymique, son taux de féminisation et sa structure d'âge, comparés à la
            population française.
          </p>
        </header>

        {/* Bandeau confidentialité */}
        <div className="flex items-start gap-3 bg-emerald-50 border border-emerald-200 rounded-xl p-4 mb-8">
          <ShieldCheck className="text-emerald-600 shrink-0 mt-0.5" size={22} />
          <div className="text-sm text-emerald-900">
            <strong>Aucune donnée n'est envoyée.</strong> Le fichier est lu et analysé entièrement
            dans votre navigateur ; seuls des résultats agrégés s'affichent. Rien ne transite par un
            serveur.
          </div>
        </div>

        {engineState === 'loading' && (
          <div className="flex items-center gap-2 text-gray-500 mb-6">
            <Loader2 className="animate-spin" size={18} />
            Chargement du référentiel onomastique…
          </div>
        )}
        {engineState === 'error' && (
          <div className="flex items-center gap-2 text-red-600 mb-6">
            <AlertCircle size={18} />
            Échec du chargement du référentiel.
          </div>
        )}

        {/* Zone de dépôt */}
        {!parsed && engineState === 'ready' && (
          <>
            <label
              onDragOver={(e) => {
                e.preventDefault()
                setDragOver(true)
              }}
              onDragLeave={() => setDragOver(false)}
              onDrop={(e) => {
                e.preventDefault()
                setDragOver(false)
                if (e.dataTransfer.files[0]) handleFile(e.dataTransfer.files[0])
              }}
              className={`flex flex-col items-center justify-center gap-3 border-2 border-dashed rounded-2xl p-12 cursor-pointer transition-colors ${
                dragOver ? 'border-blue-400 bg-blue-50' : 'border-gray-300 hover:border-gray-400'
              }`}
            >
              <Upload className="text-gray-400" size={40} />
              <div className="text-center">
                <p className="font-medium text-gray-700">
                  Glissez un fichier CSV ici, ou cliquez pour parcourir
                </p>
                <p className="text-sm text-gray-500 mt-1">
                  .csv, .tsv ou .txt, séparateur ; , ou tabulation détecté automatiquement
                </p>
              </div>
              <input
                type="file"
                accept=".csv,.tsv,.txt,text/csv"
                className="hidden"
                onChange={(e) => e.target.files[0] && handleFile(e.target.files[0])}
              />
            </label>
            <div className="text-center mt-4">
              <button
                onClick={loadExample}
                className="inline-flex items-center gap-1.5 text-sm font-medium text-blue-600 hover:text-blue-700"
              >
                <Sparkles size={16} />
                Essayer avec un fichier d'exemple
              </button>
            </div>
          </>
        )}

        {error && (
          <div className="flex items-center gap-2 text-red-600 mt-4">
            <AlertCircle size={18} />
            {error}
          </div>
        )}

        {/* Mapping des colonnes */}
        {parsed && (
          <div className="bg-gray-50 rounded-xl border border-gray-200 p-6 mb-8">
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="font-medium text-gray-900">{filename}</p>
                <p className="text-sm text-gray-500">
                  {parsed.rows.length.toLocaleString('fr-FR')} lignes · {parsed.headers.length} colonnes
                </p>
              </div>
              <button
                onClick={reset}
                className="flex items-center gap-1.5 text-sm text-gray-600 hover:text-gray-900"
              >
                <RotateCcw size={15} /> Changer de fichier
              </button>
            </div>

            {/* Choix du format des colonnes */}
            <div className="flex gap-4 mb-4 text-sm">
              <label className="flex items-center gap-1.5 cursor-pointer">
                <input
                  type="radio"
                  checked={colMode === 'split'}
                  onChange={() => setColMode('split')}
                />
                Nom et prénom séparés
              </label>
              <label className="flex items-center gap-1.5 cursor-pointer">
                <input
                  type="radio"
                  checked={colMode === 'single'}
                  onChange={() => setColMode('single')}
                />
                Une seule colonne (nom complet)
              </label>
            </div>

            {colMode === 'split' ? (
              <div className="grid sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Colonne « nom de famille » <span className="text-gray-400">(→ diversité)</span>
                  </label>
                  <select
                    value={surnameCol}
                    onChange={(e) => setSurnameCol(e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 bg-white"
                  >
                    <option value="">(aucune)</option>
                    {parsed.headers.map((h) => (
                      <option key={h} value={h}>{h}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Colonne « prénom » <span className="text-gray-400">(→ sexe + âge)</span>
                  </label>
                  <select
                    value={firstnameCol}
                    onChange={(e) => setFirstnameCol(e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 bg-white"
                  >
                    <option value="">(aucune)</option>
                    {parsed.headers.map((h) => (
                      <option key={h} value={h}>{h}</option>
                    ))}
                  </select>
                </div>
              </div>
            ) : (
              <div className="grid sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Colonne « nom complet »
                  </label>
                  <select
                    value={fullnameCol}
                    onChange={(e) => setFullnameCol(e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 bg-white"
                  >
                    {parsed.headers.map((h) => (
                      <option key={h} value={h}>{h}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Ordre</label>
                  <select
                    value={fullnameOrder}
                    onChange={(e) => setFullnameOrder(e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 bg-white"
                  >
                    <option value="prenom-nom">Prénom puis Nom (ex : Marie Dupont)</option>
                    <option value="nom-prenom">Nom puis Prénom (ex : Dupont Marie)</option>
                  </select>
                </div>
              </div>
            )}

            <button
              onClick={runAnalysis}
              className="mt-5 px-5 py-2.5 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
            >
              Analyser
            </button>
          </div>
        )}

        {/* Résultats */}
        {result && (
          <div className="space-y-6">
            {result.masques?.length > 0 && (
              <p className="text-sm text-gray-600 bg-amber-50 border border-amber-200 rounded-lg px-4 py-3">
                Non calculé faute de noms reconnus en nombre suffisant (au moins {MIN_NOMS}) :{' '}
                {result.masques.join(', ')}.
              </p>
            )}
            <div className="grid md:grid-cols-3 gap-6">
              {/* Diversité */}
              {diversityView && (
                <ResultCard icon={Globe} color={COLORS.vert} title="Diversité patronymique (IDP)">
                  <BigStat
                    value={fmt(diversityView.pct)}
                    unit="%"
                    ci={`${fmt(diversityView.ciLow)} – ${fmt(diversityView.ciHigh)} %`}
                  />
                  <div className="flex items-center gap-2 mb-2 text-sm text-gray-600">
                    <span>Référence</span>
                    <input
                      type="number"
                      min="0"
                      max="100"
                      step="0.1"
                      value={baselinePct}
                      onChange={(e) => setBaselinePct(Number(e.target.value) || 0)}
                      className="w-16 border border-gray-300 rounded px-2 py-0.5 text-right"
                    />
                    <span>% · écart {diversityView.gapPct > 0 ? '+' : ''}{fmt(diversityView.gapPct)} pts</span>
                  </div>
                  <p className="text-xs text-gray-400 mb-2">
                    7 % = population française. Mettez ici la part locale (commune) pour une
                    comparaison plus juste.
                  </p>
                  <SignifBadge significant={diversityView.significant} gapPct={diversityView.gapPct} />
                  <Coverage n={diversityView.n} coverage={diversityView.coverage} />
                </ResultCard>
              )}

              {/* Féminisation */}
              {result.gender.pct != null && (
                <ResultCard icon={Users} color={COLORS.violet} title="Taux de féminisation">
                  <BigStat
                    value={fmt(result.gender.pct)}
                    unit="%"
                    ci={`${fmt(result.gender.ciLow)} – ${fmt(result.gender.ciHigh)} %`}
                  />
                  <p className="text-sm text-gray-600 mb-2">
                    Parité (50 %) · écart {result.gender.gapPct > 0 ? '+' : ''}
                    {fmt(result.gender.gapPct)} pts
                  </p>
                  <SignifBadge significant={result.gender.significant} gapPct={result.gender.gapPct} />
                  <Coverage n={result.gender.n} coverage={result.gender.coverage} />
                </ResultCard>
              )}

              {/* Âge */}
              {result.age.n > 0 && (
                <ResultCard icon={Cake} color={COLORS.orange} title="Âge estimé">
                  <BigStat value={`${result.age.medianAge}`} unit="ans (médian)" />
                  <p className="text-sm text-gray-600">
                    Naissance médiane ~{result.age.medianBirthYear} · moyenne ~{result.age.meanAge} ans
                  </p>
                  <Coverage n={result.age.n} coverage={result.age.coverage} />
                </ResultCard>
              )}
            </div>

            {/* IDP en contexte */}
            {compareData.length > 0 && (
              <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
                <h3 className="font-semibold text-gray-900 mb-1">
                  Votre fichier dans le paysage de la diversité
                </h3>
                <p className="text-sm text-gray-500 mb-4">
                  IDP comparé à des groupes de référence (Kheddache &amp; L'Horty, 2023).
                </p>
                <ResponsiveContainer width="100%" height={260}>
                  <BarChart layout="vertical" data={compareData} margin={{ left: 40, right: 20 }}>
                    <XAxis type="number" unit="%" />
                    <YAxis type="category" dataKey="label" width={140} tick={{ fontSize: 12 }} />
                    <Tooltip formatter={(v) => `${v} %`} />
                    <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                      {compareData.map((d, i) => (
                        <Cell key={i} fill={d.vous ? COLORS.bleu : d.ref ? COLORS.gris : COLORS.vert} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}

            {/* Distribution d'âge */}
            {result.age.n > 0 && result.age.distributionPct && (
              <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
                <h3 className="font-semibold text-gray-900 mb-4">
                  Distribution d'âge estimée (par décennie de naissance)
                </h3>
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart
                    data={result.age.distributionPct.map((p, i) => ({
                      decennie: DECADE_LABELS[i],
                      pct: Number(p.toFixed(1)),
                    }))}
                  >
                    <XAxis dataKey="decennie" tick={{ fontSize: 11 }} />
                    <YAxis unit="%" />
                    <Tooltip formatter={(v) => `${v} %`} />
                    <Bar dataKey="pct" fill={COLORS.orange} radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>
        )}

        {/* Méthodologie / limites */}
        <details className="mt-10 bg-gray-50 rounded-xl border border-gray-200 p-6">
          <summary className="font-semibold text-gray-900 cursor-pointer flex items-center gap-2">
            <Info size={18} className="text-blue-600" />
            Méthode &amp; limites
          </summary>
          <div className="mt-4 text-sm text-gray-600 space-y-3">
            <p>
              <strong>Diversité (IDP)</strong> : Indice de Diversité Patronymique de Kheddache &amp;
              L'Horty (2023). Un nom est dit « issu de la diversité » s'il était absent des registres
              d'état civil avant 1950, ou multiplié par plus de 15 après. C'est un proxy de la trace
              des vagues migratoires post-1950, compatible avec le droit français (pas de
              classification ethno-raciale).
            </p>
            <p>
              <strong>Sexe &amp; âge</strong> : proxys dérivés du fichier INSEE des prénoms
              (naissances 1900-2025) : sexe et année de naissance associés à chaque prénom.
            </p>
            <p>
              <strong>Limites</strong> : ce sont des estimations attachées <em>au nom</em>, pas à la
              personne : fiables en agrégé (≈99 % de précision sur le sexe), bruitées à l'échelle
              individuelle. Le référentiel ne couvre que les naissances en France ; les noms rares ou
              nés à l'étranger (~10 %) sont exclus du calcul, ce qui peut légèrement sous-estimer la
              diversité. Une référence locale (population de la commune) serait plus juste qu'une
              baseline nationale. Pour la même raison, l'outil ne calcule rien en dessous de{' '}
              {MIN_NOMS} noms reconnus : il mesure des groupes, jamais des personnes.
            </p>
          </div>
        </details>
      </div>
    </div>
  )
}
