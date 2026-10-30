import { describe, it, expect } from 'vitest'
import { readFileSync, readdirSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import path from 'node:path'
import {
  DOSSIERS_TERRITOIRES, EXCLUSIONS_TERRITOIRES, FICHIERS_REGISTRE, GARDE_FOU_IDP,
  dansNosDossiers, contexteRegion,
} from '../../config/dossiersTerritoires'
import { REGION_INSEE_BY_CODE } from '../regions'

const DATA = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../../public/data')
const lireJson = (rel) => JSON.parse(readFileSync(path.join(DATA, rel), 'utf-8'))
// Lecture des fichiers publiés depuis le disque, à la place de fetch('/data/...').
const fetcher = (url) => Promise.resolve(lireJson(url.replace(/^\/data\//, '')))

// ───────────────────────── Détection des données par territoire ─────────────────────────
const CLES_TERRITOIRE = new Set(['communes', 'departements', 'epci', 'regions', 'villes', 'iris'])
const CODE = /^(\d{5}|2[AB]\d{3}|\d{2}|\d{3}|2[AB]|\d{9})$/
const CHAMPS_CODE = ['code', 'insee', 'code_insee', 'dep', 'codeEpci', 'siren']

function estListeDeTerritoires(v) {
  if (!Array.isArray(v) || v.length < 5) return false
  const objets = v.filter((x) => x && typeof x === 'object' && !Array.isArray(x))
  if (objets.length < 5) return false
  return objets.filter((o) => CHAMPS_CODE.some((c) => CODE.test(String(o[c] ?? '')))).length >= objets.length / 2
}
function estDictDeCodes(v) {
  if (!v || typeof v !== 'object' || Array.isArray(v)) return false
  const cles = Object.keys(v)
  return cles.length >= 10 && cles.filter((k) => /^(\d{5}|2[AB]\d{3}|\d{9})$/.test(k)).length >= cles.length / 2
}
/** Vrai si le JSON contient des données par territoire (clé géographique, liste ou dictionnaire de codes Insee). */
function contientDonneesTerritoriales(json, profondeur = 0) {
  if (json == null || typeof json !== 'object') return false
  if (profondeur === 0 && !Array.isArray(json) && /^(\d{5}|2[AB]\d{3})$/.test(String(json.code ?? ''))) return true
  if (estListeDeTerritoires(json) || estDictDeCodes(json)) return true
  if (profondeur >= 3) return false
  if (Array.isArray(json)) return false
  for (const [k, v] of Object.entries(json)) {
    if (CLES_TERRITOIRE.has(k) && v && typeof v === 'object' && (Array.isArray(v) ? v.length > 0 : Object.keys(v).length > 0)) {
      const vals = Array.isArray(v) ? v : Object.values(v)
      if (vals.some((x) => x && typeof x === 'object')) return true
    }
    if (contientDonneesTerritoriales(v, profondeur + 1)) return true
  }
  return false
}

const fichiersDossiers = () => [
  ...readdirSync(path.join(DATA, 'showcases')).filter((f) => f.endsWith('.json')).map((f) => `showcases/${f}`),
  ...readdirSync(path.join(DATA, 'segregation')).filter((f) => f.endsWith('.json')).map((f) => `segregation/${f}`),
]
const exclu = (f) => EXCLUSIONS_TERRITOIRES.find((e) => e.fichier === f || (e.motif && e.motif.test(f)))

describe('registre « Dans nos dossiers » : couverture', () => {
  it('le détecteur reconnaît les formes de données territoriales', () => {
    expect(contientDonneesTerritoriales({ departements: [{ code: '32', x: 1 }] })).toBe(true)
    expect(contientDonneesTerritoriales({ a: { regions: [{ region: 'Corse', n: 3 }] } })).toBe(true)
    expect(contientDonneesTerritoriales(Array.from({ length: 6 }, (_, i) => ({ code: `0100${i}` })))).toBe(true)
    expect(contientDonneesTerritoriales({ rows: Object.fromEntries(Array.from({ length: 12 }, (_, i) => [`930${10 + i}`, [1]])) })).toBe(true)
    expect(contientDonneesTerritoriales({ code: '93010', carreaux: [] })).toBe(true)
    expect(contientDonneesTerritoriales({ groupes: [{ sigle: 'RN', n: 120 }], communes_appariees: 3 })).toBe(false)
  })

  it('le détecteur reconnaît les fichiers géographiques actuels, et eux seulement', () => {
    const detectes = fichiersDossiers().filter((f) => contientDonneesTerritoriales(lireJson(f)))
    for (const f of ['showcases/auto-ecoles.json', 'showcases/ecole-communes.json', 'showcases/ecole-ips.json',
      'showcases/elus-diversite.json', 'showcases/evolution-revenus.json', 'showcases/selectivite.json',
      'showcases/sport.json', 'segregation/villes.json', 'segregation/departements.json',
      'segregation/colleges-evitement.json', 'segregation/93010.json'])
      expect(detectes, f).toContain(f)
    for (const f of ['showcases/assemblee.json', 'showcases/rythmes-scolaires.json']) expect(detectes, f).not.toContain(f)
  })

  it('chaque fichier de dossier avec des données par territoire est dans le registre ou exclu avec une raison', () => {
    const oublis = []
    for (const f of fichiersDossiers()) {
      if (!contientDonneesTerritoriales(lireJson(f))) continue
      if (FICHIERS_REGISTRE.includes(f)) continue
      const e = exclu(f)
      if (e && e.raison && e.raison.length > 20) continue
      oublis.push(f)
    }
    expect(oublis, `À inscrire dans config/dossiersTerritoires.js (registre ou EXCLUSIONS motivée) : ${oublis.join(', ')}`).toEqual([])
  })

  it('chaque fichier lu par le registre existe et pèse moins de 1 Mo', () => {
    for (const d of DOSSIERS_TERRITOIRES)
      for (const e of Object.values(d.echelles)) {
        const brut = readFileSync(path.join(DATA, e.fichier))
        expect(brut.length, e.fichier).toBeLessThan(1024 * 1024)
      }
  })

  it("l'extrait Auto-écoles suit le fichier du dossier (relancer build_territoires_echelles.py sinon)", () => {
    const complet = lireJson('showcases/auto-ecoles.json')
    const extrait = lireJson('territoires/auto-ecoles-departements.json')
    expect(extrait.taux_national).toBe(complet.stats.taux_national)
    for (const d of complet.departements) expect(extrait.departements[d.code]?.taux, d.code).toBe(d.taux)
  })

  it('aucune échelle inconnue, et chaque échelle a fichier, extraction, phrase et lien', () => {
    for (const d of DOSSIERS_TERRITOIRES)
      for (const [niveau, e] of Object.entries(d.echelles)) {
        expect(['commune', 'epci', 'dept', 'region']).toContain(niveau)
        expect(typeof e.fichier).toBe('string')
        expect(typeof e.extraire).toBe('function')
        expect(typeof e.phrase).toBe('function')
        expect(typeof e.lien).toBe('function')
      }
  })
})

// ───────────────────────── Garde-fous ─────────────────────────
describe('registre « Dans nos dossiers » : garde-fous', () => {
  it("Élus : départements seulement, avec la phrase de garde-fou et sans rang", async () => {
    const elus = DOSSIERS_TERRITOIRES.find((d) => d.id === 'elus')
    expect(Object.keys(elus.echelles)).toEqual(['dept'])
    for (const code of ['93', '32', '75', '976']) {
      const r = (await dansNosDossiers('dept', code, { nom: code }, fetcher)).find((x) => x.dossier.id === 'elus')
      expect(r.precaution).toContain(GARDE_FOU_IDP)
      expect(r.texte).not.toMatch(/rang|classement|plus divers|moins divers|\d+e /i)
    }
  })

  it("Sport : rien de l'encadré « L'élite »", async () => {
    const sport = DOSSIERS_TERRITOIRES.find((d) => d.id === 'sport')
    expect(Object.keys(sport.echelles)).toEqual(['dept'])
    for (const code of ['93', '32', '75']) {
      const r = (await dansNosDossiers('dept', code, { nom: code }, fetcher)).find((x) => x.dossier.id === 'sport')
      expect(r.texte).not.toMatch(/élite|IDP|nom/i)
    }
  })

  it('aucune phrase ne présente un palmarès', async () => {
    const cas = [['commune', '93010'], ['commune', '75056'], ['dept', '32'], ['dept', '93'], ['epci', '200054781']]
    for (const [niveau, code] of cas)
      for (const r of await dansNosDossiers(niveau, code, { nom: 'X' }, fetcher))
        expect(r.texte).not.toMatch(/palmarès|meilleur|pire|champion|classé \d|n° \d+ des/i)
  })
})

// ───────────────────────── Contrôles sur des territoires réels ─────────────────────────
const ids = (rs) => rs.map((r) => r.dossier.id).sort()

describe('registre « Dans nos dossiers » : territoires de contrôle', () => {
  it('Bondy (93010) : revenus et ville', async () => {
    const rs = await dansNosDossiers('commune', '93010', { nom: 'Bondy' }, fetcher)
    expect(ids(rs)).toEqual(['revenus', 'segregation'])
    const rev = rs.find((r) => r.dossier.id === 'revenus')
    expect(rev.texte).toMatch(/^Dans la hiérarchie des niveaux de vie des communes, Bondy /)
    expect(rev.texte).toMatch(/centile/)
    const seg = rs.find((r) => r.dossier.id === 'segregation')
    expect(seg.lien).toBe('/segregation?ville=93010')
    expect(seg.texte).toContain('« modeste »')
  })

  it('Paris (75056) : Paris intra-muros (dossier Revenus) et ville', async () => {
    const rs = await dansNosDossiers('commune', '75056', { nom: 'Paris' }, fetcher)
    expect(ids(rs)).toEqual(['revenus', 'segregation'])
    expect(rs.find((r) => r.dossier.id === 'revenus').texte).toMatch(/^Paris intra-muros/)
  })

  it("petite commune rurale (Saint-Clar, 32370, 1 062 hab.) : aucun dossier ne la couvre", async () => {
    expect(await dansNosDossiers('commune', '32370', { nom: 'Saint-Clar' }, fetcher)).toEqual([])
  })

  it('Métropole du Grand Paris (200054781) : revenus', async () => {
    const rs = await dansNosDossiers('epci', '200054781', { nom: 'Métropole du Grand Paris' }, fetcher)
    expect(ids(rs)).toEqual(['revenus'])
  })

  it('Gers (32) : sport « signature » rugby, et les autres dossiers départementaux', async () => {
    const rs = await dansNosDossiers('dept', '32', { nom: 'Gers' }, fetcher)
    expect(ids(rs)).toEqual(['auto-ecoles', 'ecole', 'elus', 'segregation', 'sport'].filter((id) =>
      id !== 'segregation' || lireJson('segregation/departements.json').departements.some((d) => d.dep === '32')))
    const sp = rs.find((r) => r.dossier.id === 'sport')
    expect(sp.texte).toMatch(/sport « signature » : rugby/)
    expect(rs.find((r) => r.dossier.id === 'auto-ecoles').lien).toBe('/terrains/auto-ecoles?dep=32')
  })

  it('Île-de-France (11) : ville et sélectivité', async () => {
    const rs = await dansNosDossiers('region', '11', contexteRegion(REGION_INSEE_BY_CODE['11']), fetcher)
    expect(ids(rs)).toEqual(['segregation', 'selectivite'])
    expect(rs.find((r) => r.dossier.id === 'selectivite').texte).toMatch(/^Parcoursup 2025 : 20 % des 721 formations de licence/)
  })

  it("La Réunion (04) : sélectivité seulement (le dossier Villes regroupe l'outre-mer)", async () => {
    const rs = await dansNosDossiers('region', '04', contexteRegion(REGION_INSEE_BY_CODE['04']), fetcher)
    expect(ids(rs)).toEqual(['selectivite'])
  })

  it('Mayotte (06) : aucun dossier régional', async () => {
    const rs = await dansNosDossiers('region', '06', contexteRegion(REGION_INSEE_BY_CODE['06']), fetcher)
    expect(rs).toEqual([])
  })
})
