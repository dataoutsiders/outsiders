import { describe, it, expect } from 'vitest'
import {
  groupeMatcher, verdict, classer, resumeGroupe, comparables, rechercher, toCsv, fromColumnar, ordinal,
} from '../contexteEgal'

// Trois écoles d'un même groupe : A a le meilleur taux mais un contexte facile,
// B le plus mauvais taux mais un contexte difficile.
const A = { id: 'A', nom: 'ECF MELUN', commune: 'Melun', dep: '77', m: 2, n: 200, t: 70, a1: 62, a2: 75, e1: 6, lo1: 1, hi1: 11, e2: -4, lo2: -8, hi2: -0.5 }
const B = { id: 'B', nom: 'ECF BOBIGNY', commune: 'Bobigny', dep: '93', m: 2, n: 150, t: 50, a1: 45, a2: 41, e1: 4, lo1: -1, hi1: 9, e2: 8, lo2: 3, hi2: 13 }
const C = { id: 'C', nom: 'ECF CERCA NIORT', commune: 'Niort', dep: '79', m: 2, n: 100, t: 60, a1: 66, a2: 60, e1: -5, lo1: -10, hi1: -0.2, e2: 0, lo2: -5, hi2: 5 }

describe('groupeMatcher', () => {
  it('reconnaît un mot entier, sans tenir compte des accents ni de la casse', () => {
    const ecf = groupeMatcher({ q: 'ECF' })
    expect(ecf('ECF MELUN')).toBe(true)
    expect(ecf('Auto-école ecf Vigier')).toBe(true)
    expect(ecf('ECOLE SECFORM')).toBe(false)
  })

  it("applique l'exclusion (CER hors ECF) et ne confond pas CER avec CERCA", () => {
    const cer = groupeMatcher({ q: 'CER', exclude: 'ECF' })
    expect(cer('AUTO ECOLE CER MARECHAL')).toBe(true)
    expect(cer('ECF CER CENTRE ATLANTIQUE')).toBe(false)
    expect(cer('AUTO ECOLE CERCA')).toBe(false)
  })

  it('ne retient rien sans motif', () => {
    expect(groupeMatcher({})('ECF')).toBe(false)
  })
})

describe('verdict', () => {
  it("ne tranche que si l'intervalle exclut 0", () => {
    expect(verdict(1, 5)).toBe('dessus')
    expect(verdict(-5, -1)).toBe('dessous')
    expect(verdict(-1, 2)).toBe('norme')
    expect(verdict(null, null)).toBe('norme')
  })
})

describe('classer', () => {
  it('le classement à contexte égal peut inverser le classement brut', () => {
    const r = classer([A, B, C], 'complet')
    expect(r.map((x) => x.id)).toEqual(['B', 'C', 'A'])
    const byId = Object.fromEntries(r.map((x) => [x.id, x]))
    expect(byId.A.rangBrut).toBe(1)
    expect(byId.A.rang).toBe(3)
    expect(byId.B.rangBrut).toBe(3)
    expect(byId.B.rang).toBe(1)
    expect(byId.B.verdict).toBe('dessus')
    expect(byId.A.verdict).toBe('dessous')
    expect(byId.C.verdict).toBe('norme')
    expect(byId.A.attendu).toBe(75)
  })

  it('la lecture brute classe au taux observé, sans écart ni verdict', () => {
    const r = classer([B, C, A], 'brut')
    expect(r.map((x) => x.id)).toEqual(['A', 'C', 'B'])
    for (const x of r) {
      expect(x.rang).toBe(x.rangBrut)
      expect(x.ecart).toBeNull()
      expect(x.verdict).toBeNull()
    }
  })

  it('départage les égalités par le nombre de candidats', () => {
    const X = { ...C, id: 'X', n: 300 }
    const r = classer([C, X], 'brut')
    expect(r[0].id).toBe('X')
  })
})

describe('resumeGroupe', () => {
  it('pondère par les candidats et compte les verdicts', () => {
    const s = resumeGroupe(classer([A, B, C], 'complet'))
    expect(s.ecoles).toBe(3)
    expect(s.candidats).toBe(450)
    expect(s.taux).toBeCloseTo((70 * 200 + 50 * 150 + 60 * 100) / 450, 8)
    // écart brut pondéré : (70-75)*200 + (50-41)*150 + (60-60)*100
    expect(s.ecart).toBeCloseTo((-5 * 200 + 9 * 150) / 450, 8)
    expect(s.dessus).toBe(1)
    expect(s.dessous).toBe(1)
  })

  it('compte les écoles qui changent de quart de classement', () => {
    const ecoles = [1, 2, 3, 4].map((i) => ({ ...C, id: `E${i}`, t: 50 + i, e2: -i, lo2: -1, hi2: 1 }))
    const s = resumeGroupe(classer(ecoles, 'complet'))
    // classement exactement inversé : les 4 écoles changent de quart
    expect(s.changentDeQuart).toBe(4)
  })
})

describe('comparables', () => {
  it('cherche dans le même département le contexte le plus proche', () => {
    const pool = [
      { id: 'P1', dep: '93', m: 2, n: 50, a2: 42 },
      { id: 'P2', dep: '93', m: 2, n: 50, a2: 55 },
      { id: 'P3', dep: '75', m: 2, n: 50, a2: 41 },
      { id: 'P4', dep: '93', m: 1, n: 50, a2: 41 },
      B,
    ]
    const r = comparables(B, pool, 5)
    expect(r.map((x) => x.id)).toEqual(['P1', 'P2'])
  })
})

describe('rechercher', () => {
  const ecoles = fromColumnar({
    cols: ['id', 'nom', 'commune'],
    rows: [['1', 'AUTO ECOLE DU CENTRE', 'Évry-Courcouronnes'], ['2', 'CENTRE CONDUITE', 'Lyon'], ['3', 'ECF VIGIER', 'Évreux']],
  })

  it('ignore les accents et place les débuts de mot en premier', () => {
    expect(rechercher(ecoles, 'evr').map((x) => x.id)).toEqual(['1', '3'])
    expect(rechercher(ecoles, 'centre').map((x) => x.id)).toEqual(['1', '2'])
  })

  it('attend au moins deux caractères', () => {
    expect(rechercher(ecoles, 'e')).toEqual([])
  })
})

describe('toCsv', () => {
  it('produit un CSV pour tableur français (BOM, point-virgule, virgule décimale, guillemets)', () => {
    const csv = toCsv(classer([{ ...A, nom: 'ECF "LE" ; MELUN', t: 70.5 }, B], 'complet'), 'complet')
    expect(csv.startsWith('﻿')).toBe(true)
    const lignes = csv.slice(1).split('\r\n')
    expect(lignes[0].split(';')[0]).toBe('Rang')
    expect(lignes).toHaveLength(3)
    expect(csv).toContain('"ECF ""LE"" ; MELUN"')
    expect(csv).toContain('70,5')
    expect(csv).toContain("Au-dessus de l'attendu")
  })

  it("n'exporte pas de colonnes d'attendu en lecture brute", () => {
    const tete = toCsv(classer([A], 'brut'), 'brut').slice(1).split('\r\n')[0]
    expect(tete).not.toContain('attendu')
  })
})

describe('ordinal', () => {
  it('écrit 1er puis 2e, 3e', () => {
    expect(ordinal(1)).toBe('1er')
    expect(ordinal(2)).toBe('2e')
    expect(ordinal(48)).toBe('48e')
  })
})
