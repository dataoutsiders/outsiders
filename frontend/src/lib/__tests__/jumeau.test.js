import { describe, it, expect } from 'vitest'
import { findTwins } from '../jumeau'

/**
 * Jeu synthétique : 6 colonnes (le minimum partagé exigé), 4 communes.
 * Ligne = [code, nom, pop, lon, lat, ...valeurs].
 */
const cols = ['a', 'b', 'c', 'd', 'e', 'f']
const data = {
  cols,
  mean: [10, 10, 10, 10, 10, 10],
  std: [2, 2, 2, 2, 2, 2],
  rows: [
    ['00001', 'CIBLE', 2000, 2.0, 46.0, 10, 10, 10, 10, 10, 10],
    ['00002', 'QUASI JUMELLE', 2100, 2.1, 46.1, 10, 10, 10, 10, 10, 11],
    ['00003', 'OPPOSEE', 2500, 5.0, 43.0, 18, 2, 18, 2, 18, 2],
    ['00004', 'OPPOSEE MAIS GEANTE', 90000, 5.0, 43.0, 18, 2, 18, 2, 18, 2],
  ],
}

describe('findTwins', () => {
  const twins = findTwins(data, '00001')

  it('le jumeau est la commune la plus proche en z-scores', () => {
    expect(twins.jumeau.code).toBe('00002')
    expect(twins.jumeau.shared).toBe(6)
  })

  it("l'anti-jumeau est la plus éloignée PARMI les tailles comparables (pop/2 à pop×2)", () => {
    // 00004 est plus éloignée mais 45x plus peuplée : exclue du panel.
    expect(twins.antiJumeau.code).toBe('00003')
  })

  it('identifie la colonne de divergence maximale et ses valeurs', () => {
    expect(twins.jumeau.divCol).toBe('f')
    expect(twins.jumeau.targetVal).toBe(10)
    expect(twins.jumeau.neighborVal).toBe(11)
  })

  it('distance géographique plausible (haversine, en km)', () => {
    expect(twins.jumeau.km).toBeGreaterThan(5)
    expect(twins.jumeau.km).toBeLessThan(30)
  })

  it('code inconnu -> null', () => {
    expect(findTwins(data, '99999')).toBeNull()
  })
})
