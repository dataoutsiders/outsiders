import { describe, it, expect } from 'vitest'
import {
  normalize, wilsonInterval, proportionZTest, parseSurnames, OnomasticEngine,
} from '../engine'

describe('normalize', () => {
  it('majuscules, accents retirés, espaces compactés', () => {
    expect(normalize('  Éloïse  Müller ')).toBe('ELOISE MULLER')
    expect(normalize('çédric')).toBe('CEDRIC')
  })
  it('apostrophes droite et courbe -> espace', () => {
    expect(normalize("N'Diaye")).toBe('N DIAYE')
    expect(normalize('N’Diaye')).toBe('N DIAYE')
  })
  it('tolère null', () => {
    expect(normalize(null)).toBe('')
  })
})

describe('wilsonInterval', () => {
  it('n = 0 : intervalle nul', () => {
    expect(wilsonInterval(0, 0)).toEqual({ low: 0, high: 0 })
  })
  it('50/100 : intervalle ~[0,40, 0,60], borné et symétrique', () => {
    const { low, high } = wilsonInterval(50, 100)
    expect(low).toBeGreaterThan(0.39)
    expect(low).toBeLessThan(0.45)
    expect(high).toBeGreaterThan(0.55)
    expect(high).toBeLessThan(0.61)
  })
  it("reste dans [0, 1] aux extrêmes", () => {
    expect(wilsonInterval(0, 20).low).toBe(0)
    expect(wilsonInterval(20, 20).high).toBe(1)
  })
})

describe('proportionZTest', () => {
  it('écart massif : significatif', () => {
    const t = proportionZTest(90, 100, 0.5)
    expect(t.significant).toBe(true)
    expect(t.pValue).toBeLessThan(0.001)
  })
  it('proportion égale à la baseline : non significatif', () => {
    const t = proportionZTest(50, 100, 0.5)
    expect(t.significant).toBe(false)
    expect(t.z).toBeCloseTo(0, 8)
  })
  it('cas dégénérés neutralisés', () => {
    expect(proportionZTest(5, 0, 0.5).significant).toBe(false)
    expect(proportionZTest(5, 10, 0).significant).toBe(false)
    expect(proportionZTest(5, 10, 1).significant).toBe(false)
  })
})

describe('parseSurnames', () => {
  it('parse le TSV nom -> booléen diversité', () => {
    const map = parseSurnames('DUPONT\t0\nTRAORE\t1\n\nMARTIN\t0')
    expect(map.get('DUPONT')).toBe(false)
    expect(map.get('TRAORE')).toBe(true)
    expect(map.get('MARTIN')).toBe(false)
    expect(map.has('ABSENT')).toBe(false)
  })
})

describe('OnomasticEngine.analyze', () => {
  // Distribution d'âge sur 13 décennies (1900 -> 2020) concentrée sur 1980.
  const age1980 = [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0]
  const engine = new OnomasticEngine({
    surnames: parseSurnames('DUPONT\t0\nTRAORE\t1'),
    firstnames: {
      MARIE: { h: 5, f: 995, age: age1980 },
      JEAN: { h: 990, f: 10, age: age1980 },
    },
    meta: { idp: { population_baseline_pct: 7 } },
  })

  const rows = [
    { nom: 'Dupont', prenom: 'Marie' },
    { nom: 'Traoré', prenom: 'Jean' },
    { nom: 'Inconnu', prenom: 'Zzzprenom' }, // hors référentiel : exclu des dénominateurs
  ]
  const keys = { surname: (r) => r.nom, firstname: (r) => r.prenom }
  const res = engine.analyze(rows, keys, 2026)

  it('diversité : 1 nom sur 2 reconnus, couverture 2/3', () => {
    expect(res.diversity.pct).toBeCloseTo(50, 6)
    expect(res.diversity.n).toBe(2)
    expect(res.diversity.coverage).toBeCloseTo(2 / 3, 6)
    expect(res.diversity.baselinePct).toBe(7)
  })

  it('féminisation : Marie comptée F, Jean M', () => {
    expect(res.gender.pct).toBeCloseTo(50, 6)
    expect(res.gender.n).toBe(2)
  })

  it("âge : décennie 1980 -> ~41 ans en 2026", () => {
    expect(res.age.medianBirthYear).toBe(1985)
    expect(res.age.medianAge).toBe(2026 - 1985)
  })

  it('sans colonnes fournies : agrégats vides, pas de crash', () => {
    const empty = engine.analyze(rows, {})
    expect(empty.diversity.pct).toBeNull()
    expect(empty.gender.pct).toBeNull()
    expect(empty.age.n).toBe(0)
  })
})
