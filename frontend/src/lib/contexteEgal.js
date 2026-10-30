/**
 * Comparer des sites « à contexte égal » (dossier Auto-écoles) : fonctions pures,
 * sans React, testées dans __tests__/contexteEgal.test.js.
 *
 * Chaque école porte trois lectures de son « attendu », précalculées en Python
 * (python/tools/build_auto_ecoles.py) :
 *  - brut : aucune, on classe au taux observé ;
 *  - departement : la moyenne des écoles du département (mêmes inspecteurs, mêmes centres) ;
 *  - complet : département + profil de la commune (régression pondérée).
 * L'écart retenu est « rétréci » vers 0 selon le nombre de candidats, avec un intervalle
 * à 95 % [lo ; hi] : une école n'est dite au-dessus ou en dessous que si l'intervalle
 * exclut 0.
 */

export const VARIANTES = {
  brut: { id: 'brut', label: 'De rien', court: 'taux brut', att: null, e: null, lo: null, hi: null },
  departement: {
    id: 'departement', label: 'Du département', court: 'à département égal',
    att: 'a1', e: 'e1', lo: 'lo1', hi: 'hi1',
  },
  complet: {
    id: 'complet', label: 'Du département et de la commune', court: 'à contexte égal',
    att: 'a2', e: 'e2', lo: 'lo2', hi: 'hi2',
  },
}

export const VERDICT_LABELS = {
  dessus: "Au-dessus de l'attendu",
  dessous: "Sous l'attendu",
  norme: "Dans l'attendu",
}

/** Table colonnaire {cols, rows} -> objets, avec une clé de recherche sans accents. */
export function fromColumnar({ cols, rows }) {
  return rows.map((r) => {
    const o = Object.fromEntries(cols.map((c, i) => [c, r[i]]))
    o.cle = normNom(`${o.nom} ${o.commune}`)
    return o
  })
}

export const normNom = (s) =>
  String(s || '')
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .toUpperCase()

const escapeRe = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')

/** Fabrique le test « nom contenant q (mot entier), et pas exclude ». */
export function groupeMatcher({ q, exclude } = {}) {
  if (!q) return () => false
  const mot = (x) => new RegExp(`\\b${escapeRe(normNom(x))}\\b`)
  const oui = mot(q)
  const non = exclude ? mot(exclude) : null
  return (nom) => {
    const n = normNom(nom)
    return oui.test(n) && !(non && non.test(n))
  }
}

/** Verdict d'après l'intervalle à 95 % de l'écart retenu. */
export function verdict(lo, hi) {
  if (lo == null || hi == null) return 'norme'
  if (lo > 0) return 'dessus'
  if (hi < 0) return 'dessous'
  return 'norme'
}

/**
 * Classe un groupe d'écoles : rang brut (taux observé) et rang selon la variante
 * (écart retenu). Égalités départagées par le nombre de candidats. Renvoie une copie
 * triée par rang de la variante.
 */
export function classer(ecoles, varianteId = 'complet') {
  const v = VARIANTES[varianteId]
  const parTaux = [...ecoles].sort((a, b) => b.t - a.t || b.n - a.n)
  const rangBrut = new Map(parTaux.map((x, i) => [x.id, i + 1]))
  const parVariante = v.e ? [...ecoles].sort((a, b) => b[v.e] - a[v.e] || b.n - a.n) : parTaux
  return parVariante.map((x, i) => ({
    ...x,
    rangBrut: rangBrut.get(x.id),
    rang: i + 1,
    attendu: v.att ? x[v.att] : null,
    ecart: v.e ? x[v.e] : null,
    lo: v.lo ? x[v.lo] : null,
    hi: v.hi ? x[v.hi] : null,
    verdict: v.e ? verdict(x[v.lo], x[v.hi]) : null,
  }))
}

const quart = (rang, n) => Math.min(3, Math.floor(((rang - 1) * 4) / n))

/**
 * Synthèse d'un groupe classé : taux et écart moyens pondérés par les candidats
 * (l'écart du groupe est calculé sur les écarts bruts, que le volume cumulé rend
 * fiables), verdicts, part des écoles qui changent de quart de classement.
 */
export function resumeGroupe(classees) {
  const candidats = classees.reduce((s, x) => s + x.n, 0)
  const taux = candidats ? classees.reduce((s, x) => s + x.t * x.n, 0) / candidats : null
  const avecAtt = classees.filter((x) => x.attendu != null)
  const nAtt = avecAtt.reduce((s, x) => s + x.n, 0)
  const ecart = nAtt ? avecAtt.reduce((s, x) => s + (x.t - x.attendu) * x.n, 0) / nAtt : null
  const N = classees.length
  const changent = N >= 4 ? classees.filter((x) => quart(x.rang, N) !== quart(x.rangBrut, N)).length : 0
  return {
    ecoles: N,
    candidats,
    taux,
    ecart,
    dessus: classees.filter((x) => x.verdict === 'dessus').length,
    dessous: classees.filter((x) => x.verdict === 'dessous').length,
    changentDeQuart: changent,
  }
}

/** Écoles comparables : même département, contexte le plus proche (attendu complet). */
export function comparables(ecole, toutes, k = 5) {
  return toutes
    .filter((x) => x.id !== ecole.id && x.dep === ecole.dep && x.m === 2)
    .map((x) => ({ x, d: Math.abs(x.a2 - ecole.a2) }))
    .sort((a, b) => a.d - b.d || b.x.n - a.x.n)
    .slice(0, k)
    .map(({ x }) => x)
}

/** Recherche sans accents sur le nom et la commune ; les débuts de mot d'abord. */
export function rechercher(ecoles, q, limit = 10) {
  const nq = normNom(q).trim()
  if (nq.length < 2) return []
  const debut = []
  const dedans = []
  for (const x of ecoles) {
    const cle = x.cle ?? normNom(`${x.nom} ${x.commune}`)
    const i = cle.indexOf(nq)
    if (i === 0 || (i > 0 && cle[i - 1] === ' ')) debut.push(x)
    else if (i > 0) dedans.push(x)
    if (debut.length >= limit) break
  }
  return [...debut, ...dedans].slice(0, limit)
}

const cellule = (x) => {
  if (x == null) return ''
  const s = typeof x === 'number' ? String(x).replace('.', ',') : String(x)
  return /[";\r\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s
}

/** Export tableur (séparateur « ; », virgule décimale, BOM pour Excel). */
export function toCsv(classees, varianteId = 'complet') {
  const v = VARIANTES[varianteId]
  const tete = ['Rang', 'Rang brut', 'Auto-école', 'Commune', 'Département', 'Candidats (1re présentation)', 'Taux de réussite (%)']
  if (v.e) tete.push('Taux attendu (%)', 'Écart retenu (pts)', 'Intervalle bas (pts)', 'Intervalle haut (pts)', 'Verdict')
  const lignes = classees.map((x) => {
    const l = [x.rang, x.rangBrut, x.nom, x.commune, x.dep, x.n, x.t]
    if (v.e) l.push(x.attendu, x.ecart, x.lo, x.hi, VERDICT_LABELS[x.verdict])
    return l
  })
  return '﻿' + [tete, ...lignes].map((l) => l.map(cellule).join(';')).join('\r\n')
}

/** Rang en toutes lettres courtes : 1er, 2e, 3e... */
export const ordinal = (n) => (n === 1 ? '1er' : `${n}e`)
