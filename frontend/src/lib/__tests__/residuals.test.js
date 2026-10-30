import { describe, it, expect } from 'vitest'
import { ols, withResiduals, residCategory } from '../residuals'

describe('ols', () => {
  it('retrouve une droite parfaite', () => {
    const pts = [1, 2, 3, 4, 5].map((x) => ({ x, y: 2 * x + 1 }))
    const m = ols(pts)
    expect(m.a).toBeCloseTo(1, 8)
    expect(m.b).toBeCloseTo(2, 8)
    expect(m.r2).toBeCloseTo(1, 8)
    expect(m.s).toBeCloseTo(0, 8)
  })

  it('renvoie null sous 3 points', () => {
    expect(ols([{ x: 1, y: 1 }, { x: 2, y: 2 }])).toBeNull()
  })

  it('renvoie null quand x est constant (pas de pente définissable)', () => {
    expect(ols([{ x: 1, y: 1 }, { x: 1, y: 2 }, { x: 1, y: 3 }])).toBeNull()
  })

  it('estime une pente négative', () => {
    const pts = [1, 2, 3, 4].map((x) => ({ x, y: 10 - 3 * x }))
    expect(ols(pts).b).toBeCloseTo(-3, 8)
  })
})

describe('withResiduals', () => {
  it('signale le point qui dévie de la tendance', () => {
    // Droite y = x, sauf un point tiré vers le haut.
    const pts = [
      { x: 1, y: 1 }, { x: 2, y: 2 }, { x: 3, y: 3 }, { x: 4, y: 4 },
      { x: 5, y: 5 }, { x: 6, y: 6 }, { x: 7, y: 7 }, { x: 8, y: 14 },
    ]
    const { model, points } = withResiduals(pts)
    expect(model).not.toBeNull()
    const outlier = points.find((p) => p.x === 8)
    const conforme = points.find((p) => p.x === 4)
    expect(outlier.t).toBeGreaterThan(1)
    expect(Math.abs(outlier.t)).toBeGreaterThan(Math.abs(conforme.t))
    expect(outlier.resid).toBeGreaterThan(0)
  })

  it('rend une liste vide quand le modèle est inestimable', () => {
    const { model, points } = withResiduals([{ x: 1, y: 1 }])
    expect(model).toBeNull()
    expect(points).toEqual([])
  })

  it('yhat = a + b·x pour chaque point', () => {
    const pts = [1, 2, 3, 4, 5].map((x) => ({ x, y: x * 3 + 2 }))
    const { model, points } = withResiduals(pts)
    for (const p of points) expect(p.yhat).toBeCloseTo(model.a + model.b * p.x, 8)
  })
})

describe('residCategory', () => {
  it('classe selon les seuils 1 et 2 sigma', () => {
    expect(residCategory(2.5)).toBe('pos-fort')
    expect(residCategory(2)).toBe('pos-fort')
    expect(residCategory(1.2)).toBe('pos')
    expect(residCategory(0)).toBe('neutre')
    expect(residCategory(-1.2)).toBe('neg')
    expect(residCategory(-2)).toBe('neg-fort')
  })
})
