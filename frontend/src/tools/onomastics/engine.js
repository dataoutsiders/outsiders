/**
 * Moteur d'inférence onomastique, Outsiders.
 *
 * À partir d'une liste de noms/prénoms, estime en agrégé :
 *   - la diversité patronymique (IDP, Kheddache & L'Horty 2023),
 *   - le taux de féminisation (proxy sexe via prénom),
 *   - la structure d'âge (proxy via l'année de naissance associée au prénom).
 *
 * Conçu pour tourner 100% côté navigateur : les données nominatives ne
 * quittent jamais le poste, seuls des agrégats sont produits.
 *
 * IMPORTANT : normalize() doit rester STRICTEMENT identique à la fonction
 * `normaliser` du script python/tools/build_onomastics_reference.py, sinon
 * les noms ne matchent plus le référentiel.
 */

/** Normalisation : MAJUSCULES, sans accents, apostrophes -> espace, espaces compactés. */
export function normalize(name) {
  if (name == null) return ''
  let s = String(name).toUpperCase().trim()
  s = s.normalize('NFD').replace(/[̀-ͯ]/g, '') // retire les accents
  s = s.replace(/['’]/g, ' ')                        // apostrophes droite + courbe
  s = s.replace(/\s+/g, ' ')
  return s.trim()
}

// ============================================================
// Statistiques
// ============================================================

/** Borne d'un intervalle de Wilson (95%) pour une proportion. */
export function wilsonInterval(successes, n, z = 1.96) {
  if (n === 0) return { low: 0, high: 0 }
  const p = successes / n
  const z2 = z * z
  const denom = 1 + z2 / n
  const centre = (p + z2 / (2 * n)) / denom
  const demi = (z / denom) * Math.sqrt((p * (1 - p)) / n + z2 / (4 * n * n))
  return { low: Math.max(0, centre - demi), high: Math.min(1, centre + demi) }
}

/**
 * Test z d'une proportion observée contre une baseline p0.
 * Renvoie { z, pValue, significant } (significant = écart à 95%).
 */
export function proportionZTest(successes, n, p0) {
  if (n === 0 || p0 <= 0 || p0 >= 1) return { z: 0, pValue: 1, significant: false }
  const p = successes / n
  const se = Math.sqrt((p0 * (1 - p0)) / n)
  const z = (p - p0) / se
  const pValue = 2 * (1 - normalCdf(Math.abs(z)))
  return { z, pValue, significant: Math.abs(z) > 1.96 }
}

/** Fonction de répartition de la loi normale centrée réduite (approx. Abramowitz-Stegun). */
function normalCdf(x) {
  const t = 1 / (1 + 0.2316419 * Math.abs(x))
  const d = 0.3989423 * Math.exp((-x * x) / 2)
  let prob =
    d * t * (0.3193815 + t * (-0.3565638 + t * (1.781478 + t * (-1.821256 + t * 1.330274))))
  prob = 1 - prob
  return x >= 0 ? prob : 1 - prob
}

// Milieux des décennies, pour estimer une année de naissance médiane.
const DECADE_MIDPOINTS = [
  1905, 1915, 1925, 1935, 1945, 1955, 1965, 1975, 1985, 1995, 2005, 2015, 2022,
]

// ============================================================
// Moteur
// ============================================================

export class OnomasticEngine {
  /**
   * @param {Object} refs
   * @param {Map<string, boolean>} refs.surnames   nom normalisé -> diversité (true/false)
   * @param {Object} refs.firstnames               prénom normalisé -> { h, f, age:number[13] }
   * @param {Object} refs.meta                      baselines + libellés
   */
  constructor({ surnames, firstnames, meta }) {
    this.surnames = surnames
    this.firstnames = firstnames
    this.meta = meta
  }

  /** @returns {true|false|null} true=diversité, false=non, null=inconnu (hors dénominateur). */
  inferDiversity(nom) {
    const key = normalize(nom)
    if (!key) return null
    const v = this.surnames.get(key)
    return v === undefined ? null : v
  }

  /** @returns {{sex:'F'|'M'|null, pFemale:number, n:number}|null} */
  inferGender(prenom) {
    const d = this.firstnames[normalize(prenom)]
    if (!d) return null
    const tot = d.h + d.f
    if (tot === 0) return null
    const pFemale = d.f / tot
    return { sex: pFemale >= 0.5 ? 'F' : 'M', pFemale, n: tot }
  }

  /** Distribution d'âge (par décennie, normalisée) d'un prénom. @returns {number[13]|null} */
  inferAgeDistribution(prenom) {
    const d = this.firstnames[normalize(prenom)]
    if (!d) return null
    const tot = d.age.reduce((a, b) => a + b, 0)
    if (tot === 0) return null
    return d.age.map((c) => c / tot)
  }

  /**
   * Analyse agrégée d'un jeu de lignes.
   * @param {Array<Object>} rows
   * @param {Object} keys  { surname:(row)=>string, firstname:(row)=>string }
   * @param {number} currentYear  pour convertir l'année de naissance en âge
   */
  analyze(rows, keys, currentYear = 2026) {
    const total = rows.length

    // --- Diversité (IDP) ---
    let dvKnown = 0
    let dvDivers = 0
    if (keys.surname) {
      for (const row of rows) {
        const r = this.inferDiversity(keys.surname(row))
        if (r === null) continue
        dvKnown++
        if (r) dvDivers++
      }
    }
    const diversity = this._buildProportion(dvDivers, dvKnown, total, this.meta?.idp?.population_baseline_pct)

    // --- Sexe ---
    let gKnown = 0
    let gFemale = 0
    if (keys.firstname) {
      for (const row of rows) {
        const g = this.inferGender(keys.firstname(row))
        if (!g) continue
        gKnown++
        if (g.sex === 'F') gFemale++
      }
    }
    const gender = this._buildProportion(gFemale, gKnown, total, 50)

    // --- Âge (somme des distributions individuelles) ---
    let aKnown = 0
    const ageAgg = new Array(13).fill(0)
    if (keys.firstname) {
      for (const row of rows) {
        const dist = this.inferAgeDistribution(keys.firstname(row))
        if (!dist) continue
        aKnown++
        for (let i = 0; i < 13; i++) ageAgg[i] += dist[i]
      }
    }
    const age = this._buildAge(ageAgg, aKnown, total, currentYear)

    return { total, diversity, gender, age }
  }

  _buildProportion(successes, known, total, baselinePct) {
    if (known === 0) {
      return { pct: null, n: 0, coverage: 0, successes: 0 }
    }
    const ci = wilsonInterval(successes, known)
    const baseline = baselinePct == null ? null : baselinePct / 100
    const test = baseline == null ? null : proportionZTest(successes, known, baseline)
    return {
      pct: (successes / known) * 100,
      successes,
      n: known,
      coverage: total ? known / total : 0,
      ciLow: ci.low * 100,
      ciHigh: ci.high * 100,
      baselinePct: baselinePct ?? null,
      gapPct: baselinePct == null ? null : (successes / known) * 100 - baselinePct,
      significant: test ? test.significant : null,
      pValue: test ? test.pValue : null,
    }
  }

  _buildAge(ageAgg, known, total, currentYear) {
    if (known === 0) return { n: 0, coverage: 0, distributionPct: null }
    const distributionPct = ageAgg.map((c) => (c / known) * 100)
    // Année de naissance médiane via la distribution cumulée des décennies.
    let cum = 0
    let medianYear = null
    for (let i = 0; i < 13; i++) {
      cum += ageAgg[i] / known
      if (medianYear === null && cum >= 0.5) medianYear = DECADE_MIDPOINTS[i]
    }
    const meanYear =
      ageAgg.reduce((s, c, i) => s + (c / known) * DECADE_MIDPOINTS[i], 0)
    return {
      n: known,
      coverage: total ? known / total : 0,
      distributionPct,
      medianBirthYear: medianYear,
      meanBirthYear: Math.round(meanYear),
      medianAge: medianYear == null ? null : currentYear - medianYear,
      meanAge: Math.round(currentYear - meanYear),
    }
  }
}

// ============================================================
// Chargement des artefacts (navigateur)
// ============================================================

/** Parse le contenu de surnames.tsv en Map<string, boolean>. */
export function parseSurnames(text) {
  const map = new Map()
  const lines = text.split('\n')
  for (const line of lines) {
    if (!line) continue
    const tab = line.indexOf('\t')
    if (tab === -1) continue
    map.set(line.slice(0, tab), line.charCodeAt(tab + 1) === 49 /* '1' */)
  }
  return map
}

/** Charge le moteur depuis un répertoire public (fetch). */
export async function loadEngine(basePath = '/data/onomastics') {
  const [surnamesText, firstnames, meta] = await Promise.all([
    fetch(`${basePath}/surnames.tsv`).then((r) => r.text()),
    fetch(`${basePath}/firstnames.json`).then((r) => r.json()),
    fetch(`${basePath}/meta.json`).then((r) => r.json()),
  ])
  return new OnomasticEngine({ surnames: parseSurnames(surnamesText), firstnames, meta })
}
