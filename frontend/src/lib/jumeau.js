/**
 * Jumeau statistique : pour une commune, sa plus proche voisine dans l'espace
 * multi-indicateurs standardisé (z-scores), et son « anti-jumeau » à taille
 * comparable. Tout en navigateur, sur le fichier compact communes-vecteurs.json.
 *
 * Distance = moyenne des carrés d'écarts de z-scores sur les colonnes communes
 * (gère les indicateurs manquants ; exige un minimum de colonnes partagées).
 */
const MIN_COLS = 6 // colonnes partagées minimales pour comparer deux communes

let _cache = null
export function loadVectors() {
  if (!_cache) _cache = fetch('/data/atlas/communes-vecteurs.json').then((r) => r.json())
  return _cache
}

function km(aLon, aLat, bLon, bLat) {
  if ([aLon, aLat, bLon, bLat].some((v) => v == null)) return null
  const R = 6371
  const toR = Math.PI / 180
  const dLat = (bLat - aLat) * toR
  const dLon = (bLon - aLon) * toR
  const s = Math.sin(dLat / 2) ** 2 + Math.cos(aLat * toR) * Math.cos(bLat * toR) * Math.sin(dLon / 2) ** 2
  return Math.round(2 * R * Math.asin(Math.min(1, Math.sqrt(s))))
}

/**
 * @returns {null | { jumeau, antiJumeau }} chaque voisin :
 *   { code, pop, km, shared, divCol, targetVal, neighborVal }
 */
export function findTwins(data, targetCode) {
  const { cols, mean, std, rows } = data
  const idx = rows.findIndex((r) => r[0] === targetCode)
  if (idx < 0) return null
  const target = rows[idx]
  const tvals = target.slice(5)
  const tpop = target[2]
  const z = (v, i) => (v == null || !std[i] ? null : (v - mean[i]) / std[i])
  const tz = tvals.map(z)

  const compare = (r) => {
    const rv = r.slice(5)
    let s = 0, k = 0, maxd = -1, maxi = -1
    for (let i = 0; i < cols.length; i++) {
      const a = tz[i]
      const b = z(rv[i], i)
      if (a == null || b == null) continue
      const d = (a - b) ** 2
      s += d
      k++
      if (d > maxd) { maxd = d; maxi = i }
    }
    if (k < MIN_COLS) return null
    return { d: Math.sqrt(s / k), k, maxi }
  }

  let jum = null, anti = null
  for (let j = 0; j < rows.length; j++) {
    if (j === idx) continue
    const r = rows[j]
    const res = compare(r)
    if (!res) continue
    if (!jum || res.d < jum.d) jum = { r, ...res }
    const p = r[2]
    if (p >= tpop / 2 && p <= tpop * 2 && (!anti || res.d > anti.d)) anti = { r, ...res }
  }

  const pack = (e) =>
    e && {
      code: e.r[0],
      nom: e.r[1],
      pop: e.r[2],
      km: km(target[3], target[4], e.r[3], e.r[4]),
      shared: e.k,
      divCol: cols[e.maxi],
      targetVal: tvals[e.maxi],
      neighborVal: e.r[5 + e.maxi],
    }

  return { jumeau: pack(jum), antiJumeau: pack(anti) }
}

/**
 * Construit, à partir d'enregistrements { code, nom, pop, <indicateurs> } (par exemple les
 * intercommunalités de atlas/epci.json), la même structure compacte que communes-vecteurs.json
 * ({ cols, mean, std, rows }), pour réutiliser findTwins à une autre échelle. Pas de coordonnées :
 * la distance en kilomètres reste vide.
 */
export function vecteursDepuis(records, cols) {
  const mean = [], std = []
  for (const c of cols) {
    const v = records.map((r) => r[c]).filter((x) => x != null && !isNaN(x))
    const m = v.length ? v.reduce((a, b) => a + b, 0) / v.length : 0
    const s = v.length ? Math.sqrt(v.reduce((a, b) => a + (b - m) ** 2, 0) / v.length) : 0
    mean.push(m)
    std.push(s)
  }
  const rows = records.map((r) => [r.code, r.nom, r.pop ?? null, null, null, ...cols.map((c) => r[c] ?? null)])
  return { cols, mean, std, rows }
}
