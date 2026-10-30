/**
 * Utilitaires pour situer un territoire (commune / département) vs national.
 * Aucune dépendance : pure logique, réutilisable côté fiche et tableau de bord.
 */

// Code département à partir d'un code INSEE (gère Corse 2A/2B et DOM 97x/98x).
// Cohérent avec dep_of() de python/tools/build_atlas_communes.py.
export function depFromInsee(code) {
  code = String(code)
  return code.slice(0, 2) === '97' || code.slice(0, 2) === '98' ? code.slice(0, 3) : code.slice(0, 2)
}

// Échelles de la fiche territoire.
export const NIVEAUX = ['commune', 'epci', 'dept', 'region']

/**
 * Niveau d'un territoire. Le paramètre explicite `niveau` (?niveau=epci|region dans l'URL)
 * l'emporte ; sans lui, on garde l'adressage historique par la longueur du code :
 * commune (5 caractères) ou département (2-3). Un SIREN d'intercommunalité (9 chiffres) est
 * reconnu même sans paramètre ; un code de région (2 chiffres) ne l'est jamais, puisqu'il se
 * confond avec un département : la région exige ?niveau=region.
 */
export function niveauFromCode(code, niveau = null) {
  if (NIVEAUX.includes(niveau)) return niveau
  const c = String(code)
  if (/^\d{9}$/.test(c)) return 'epci'
  return c.length >= 5 ? 'commune' : 'dept'
}

// Adresse de la fiche d'un territoire (les URL historiques des communes et départements restent valides).
export function ficheHref(niveau, code) {
  if (niveau === 'epci' || niveau === 'region') return `/territoires?niveau=${niveau}&code=${code}`
  return `/territoires?code=${code}`
}

// Repères de distribution, du plus bas au plus haut, pour interpoler un percentile.
const ANCHORS = [
  ['min', 0],
  ['p10', 10],
  ['p25', 25],
  ['median', 50],
  ['p75', 75],
  ['p90', 90],
  ['max', 100],
]

/**
 * Position (0–100) d'une valeur dans la distribution nationale, par interpolation
 * linéaire entre les repères (min, p10, p25, médiane, p75, p90, max) de stats-nationales.
 * Renvoie null si la valeur ou les repères manquent.
 */
export function positionPct(valeur, st) {
  if (valeur == null || !st) return null
  const pts = ANCHORS.map(([k, p]) => [st[k], p]).filter(([v]) => v != null)
  if (pts.length < 2) return null
  if (valeur <= pts[0][0]) return 0
  if (valeur >= pts[pts.length - 1][0]) return 100
  for (let i = 1; i < pts.length; i++) {
    const [v0, p0] = pts[i - 1]
    const [v1, p1] = pts[i]
    if (valeur <= v1) return v1 === v0 ? p1 : Math.round(p0 + ((valeur - v0) / (v1 - v0)) * (p1 - p0))
  }
  return 100
}

// Tranches de taille de commune (bornes partagées avec build_territoires_index.py).
export const POP_BRACKETS = [
  { id: '0', label: 'communes de moins de 1 000 hab.', max: 1000 },
  { id: '1', label: 'communes de 1 000 à 5 000 hab.', max: 5000 },
  { id: '2', label: 'communes de 5 000 à 20 000 hab.', max: 20000 },
  { id: '3', label: 'communes de 20 000 à 100 000 hab.', max: 100000 },
  { id: '4', label: 'communes de 100 000 hab. et plus', max: Infinity },
]

export function popBracket(pop, brackets = POP_BRACKETS) {
  if (pop == null) return null
  return brackets.find((b) => pop < b.max) || brackets[brackets.length - 1]
}

// Tranches de taille des intercommunalités (bornes proches des quintiles de population des
// 1 255 intercommunalités : 13 000, 23 000, 45 000, 100 000 habitants environ).
export const EPCI_BRACKETS = [
  { id: '0', label: 'intercommunalités de moins de 15 000 hab.', max: 15000 },
  { id: '1', label: 'intercommunalités de 15 000 à 30 000 hab.', max: 30000 },
  { id: '2', label: 'intercommunalités de 30 000 à 60 000 hab.', max: 60000 },
  { id: '3', label: 'intercommunalités de 60 000 à 150 000 hab.', max: 150000 },
  { id: '4', label: 'intercommunalités de 150 000 hab. et plus', max: Infinity },
]

/**
 * Repères de distribution (min, p10, p25, médiane, p75, p90, max) calculés à la
 * volée sur une liste de valeurs, pour situer un territoire dans un groupe de
 * référence local (ex. les communes de son département). Même forme que stats-nationales.
 */
export function statsFromValues(values, floor = null) {
  let v = values.filter((x) => x != null && !isNaN(x))
  if (floor != null) v = v.filter((x) => x >= floor)
  if (v.length < 3) return null
  v.sort((a, b) => a - b)
  const q = (p) => v[Math.floor((p / 100) * (v.length - 1))]
  return { min: v[0], p10: q(10), p25: q(25), median: q(50), p75: q(75), p90: q(90), max: v[v.length - 1], n: v.length }
}

// Libellé en clair d'un rang percentile (neutre : haut/bas, sans jugement de valeur).
export function bandeLabel(pct) {
  if (pct == null) return null
  if (pct <= 10) return 'parmi les 10 % les plus bas'
  if (pct <= 25) return 'dans le quart inférieur'
  if (pct < 45) return 'sous la médiane'
  if (pct <= 55) return 'autour de la médiane'
  if (pct < 75) return 'au-dessus de la médiane'
  if (pct < 90) return 'dans le quart supérieur'
  return 'parmi les 10 % les plus élevés'
}

// Met un nom (commune ou département, souvent en capitales) en casse de titre française.
export function titleCase(s) {
  return String(s || '')
    .toLowerCase()
    .replace(/(^|[\s'’-])([a-zà-ÿ])/g, (m, sep, c) => sep + c.toUpperCase())
}
