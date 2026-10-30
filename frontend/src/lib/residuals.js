/**
 * Régression linéaire (OLS) et résidus studentisés, en JS pur (côté navigateur).
 *
 * Sert au moteur « Outsiders » : on ne s'intéresse pas au niveau brut d'un
 * territoire mais à son écart au pronostic (résidu), une fois la relation X→Y
 * estimée. Les résidus sont studentisés (standardisés) pour être comparables
 * d'un point à l'autre.
 *
 * v2 prévue : remplacer ols() par une régression robuste (Huber) sans toucher au
 * reste, car les valeurs extrêmes tirent la droite des moindres carrés.
 */

// Ajustement des moindres carrés y = a + b·x. Renvoie aussi R² et l'erreur-type.
export function ols(points) {
  const n = points.length
  if (n < 3) return null
  let sx = 0, sy = 0
  for (const p of points) {
    sx += p.x
    sy += p.y
  }
  const mx = sx / n
  const my = sy / n
  let sxx = 0, sxy = 0, syy = 0
  for (const p of points) {
    const dx = p.x - mx
    const dy = p.y - my
    sxx += dx * dx
    sxy += dx * dy
    syy += dy * dy
  }
  if (sxx === 0) return null
  const b = sxy / sxx
  const a = my - b * mx
  let sse = 0
  for (const p of points) {
    const e = p.y - (a + b * p.x)
    sse += e * e
  }
  const r2 = syy === 0 ? 0 : 1 - sse / syy
  const s = n > 2 ? Math.sqrt(sse / (n - 2)) : 0 // erreur-type résiduelle
  return { a, b, r2, n, mx, sxx, s }
}

/**
 * Enrichit chaque point de sa valeur prédite (yhat), de son résidu (resid) et de
 * son résidu studentisé (t). t = e / (s·√(1 - h)), avec h le levier
 * h = 1/n + (x - x̄)² / Σ(x - x̄)².
 */
export function withResiduals(points) {
  const model = ols(points)
  if (!model) return { model: null, points: [] }
  const { a, b, s, n, mx, sxx } = model
  const out = points.map((p) => {
    const yhat = a + b * p.x
    const resid = p.y - yhat
    const h = 1 / n + (p.x - mx) ** 2 / sxx
    const denom = s * Math.sqrt(Math.max(1e-9, 1 - h))
    const t = denom > 1e-12 ? resid / denom : 0
    return { ...p, yhat, resid, t }
  })
  return { model, points: out }
}

// Catégorie d'écart selon le résidu studentisé (seuils usuels 1 et 2 σ).
export function residCategory(t) {
  if (t >= 2) return 'pos-fort'
  if (t >= 1) return 'pos'
  if (t <= -2) return 'neg-fort'
  if (t <= -1) return 'neg'
  return 'neutre'
}
