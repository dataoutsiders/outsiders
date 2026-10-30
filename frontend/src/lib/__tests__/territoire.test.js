import { describe, it, expect } from 'vitest'
import {
  depFromInsee, niveauFromCode, positionPct, statsFromValues, popBracket,
  bandeLabel, titleCase, ficheHref, EPCI_BRACKETS,
} from '../territoire'
import { vecteursDepuis, findTwins } from '../jumeau'
import { REGIONS_INSEE, regionInseeOfDep } from '../regions'

describe('depFromInsee', () => {
  it('métropole : 2 premiers caractères', () => {
    expect(depFromInsee('75056')).toBe('75')
    expect(depFromInsee('01053')).toBe('01')
  })
  it('Corse : codes 2A/2B', () => {
    expect(depFromInsee('2A004')).toBe('2A')
    expect(depFromInsee('2B033')).toBe('2B')
  })
  it('outre-mer : 3 caractères', () => {
    expect(depFromInsee('97411')).toBe('974')
    expect(depFromInsee('98818')).toBe('988')
  })
})

describe('niveauFromCode', () => {
  it('distingue commune et département', () => {
    expect(niveauFromCode('75056')).toBe('commune')
    expect(niveauFromCode('75')).toBe('dept')
    expect(niveauFromCode('974')).toBe('dept')
  })
})

describe('positionPct', () => {
  const st = { min: 0, p10: 10, p25: 25, median: 50, p75: 75, p90: 90, max: 100 }
  it('repères exacts', () => {
    expect(positionPct(50, st)).toBe(50)
    expect(positionPct(0, st)).toBe(0)
    expect(positionPct(100, st)).toBe(100)
  })
  it('interpole entre repères', () => {
    expect(positionPct(62.5, st)).toBe(63) // arrondi de 62,5 entre p50 et p75
  })
  it('borne hors distribution', () => {
    expect(positionPct(-5, st)).toBe(0)
    expect(positionPct(200, st)).toBe(100)
  })
  it('null si valeur ou repères manquants', () => {
    expect(positionPct(null, st)).toBeNull()
    expect(positionPct(50, null)).toBeNull()
  })
})

describe('statsFromValues', () => {
  it('calcule les repères sur les valeurs valides', () => {
    const st = statsFromValues([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, null, NaN])
    expect(st.min).toBe(1)
    expect(st.max).toBe(10)
    expect(st.median).toBe(5)
    expect(st.n).toBe(10)
  })
  it('applique le plancher de plausibilité', () => {
    const st = statsFromValues([5, 1000, 2000, 3000], 1000)
    expect(st.min).toBe(1000)
    expect(st.n).toBe(3)
  })
  it('null sous 3 valeurs', () => {
    expect(statsFromValues([1, 2])).toBeNull()
  })
})

describe('popBracket', () => {
  it('classe par taille de commune', () => {
    expect(popBracket(500).id).toBe('0')
    expect(popBracket(1000).id).toBe('1')
    expect(popBracket(250000).id).toBe('4')
    expect(popBracket(null)).toBeNull()
  })
})

describe('bandeLabel', () => {
  it('libellés neutres par bande', () => {
    expect(bandeLabel(5)).toBe('parmi les 10 % les plus bas')
    expect(bandeLabel(50)).toBe('autour de la médiane')
    expect(bandeLabel(95)).toBe('parmi les 10 % les plus élevés')
    expect(bandeLabel(null)).toBeNull()
  })
})

describe('titleCase', () => {
  it('capitales -> casse de titre, tirets et apostrophes gérés', () => {
    expect(titleCase('SAINT-DENIS')).toBe('Saint-Denis')
    expect(titleCase("L'HAY LES ROSES")).toBe("L'Hay Les Roses")
    expect(titleCase('AIX-EN-PROVENCE')).toBe('Aix-En-Provence')
  })
  it('tolère null et vide', () => {
    expect(titleCase(null)).toBe('')
    expect(titleCase('')).toBe('')
  })
})

describe('échelles intercommunalité et région', () => {
  const niv = niveauFromCode
  const pb = popBracket

  it('niveau explicite prioritaire, URL historiques inchangées', () => {
    expect(niv('75056')).toBe('commune')
    expect(niv('32')).toBe('dept')
    expect(niv('200054781')).toBe('epci') // SIREN reconnu même sans paramètre
    expect(niv('11', 'region')).toBe('region') // une région exige le paramètre
    expect(niv('11')).toBe('dept')
    expect(niv('200054781', 'inconnu')).toBe('epci')
  })
  it('adresses des fiches', () => {
    expect(ficheHref('commune', '93010')).toBe('/territoires?code=93010')
    expect(ficheHref('dept', '32')).toBe('/territoires?code=32')
    expect(ficheHref('epci', '200054781')).toBe('/territoires?niveau=epci&code=200054781')
    expect(ficheHref('region', '11')).toBe('/territoires?niveau=region&code=11')
  })
  it('tranches de taille des intercommunalités', () => {
    expect(pb(9000, EPCI_BRACKETS).id).toBe('0')
    expect(pb(7000000, EPCI_BRACKETS).id).toBe('4')
  })
  it('18 régions, chaque département rattaché une fois', () => {
    expect(REGIONS_INSEE).toHaveLength(18)
    const deps = REGIONS_INSEE.flatMap((r) => r.deps)
    expect(new Set(deps).size).toBe(deps.length)
    expect(deps).toHaveLength(101)
    expect(regionInseeOfDep('32').nom).toBe('Occitanie')
    expect(regionInseeOfDep('974').code).toBe('04')
  })
  it('jumeau sur des enregistrements génériques', () => {
    const recs = [
      { code: 'a', nom: 'A', pop: 100, x: 1, y: 1, z: 1, u: 1, v: 1, w: 1 },
      { code: 'b', nom: 'B', pop: 120, x: 1.1, y: 1, z: 1, u: 1, v: 1, w: 1.1 },
      { code: 'c', nom: 'C', pop: 150, x: 9, y: 8, z: 7, u: 9, v: 8, w: 9 },
    ]
    const t = findTwins(vecteursDepuis(recs, ['x', 'y', 'z', 'u', 'v', 'w']), 'a')
    expect(t.jumeau.code).toBe('b')
    expect(t.antiJumeau.code).toBe('c')
    expect(t.jumeau.km).toBeNull()
  })
})
