/**
 * Habillage partagé par les cartes Leaflet (ChoroplethMap, PointMap, CarreauxMap) :
 * fond de carte, rampe séquentielle, seuils par quantiles, contrôle de légende. Une
 * seule implémentation pour que surfaces, points et carreaux restent visuellement
 * cohérents.
 */
import L from 'leaflet'
import { greyToEmerald } from '../../lib/colorScale'

/**
 * Fond de carte : tuiles OpenStreetMap France (gratuites, sans clé), passées en gris
 * clair par la classe CSS `fond-carte` (index.css) pour ne pas concurrencer les
 * couleurs des données. Les tuiles CARTO « light_all » exigent désormais une clé
 * (filigrane « API KEY REQUIRED »).
 */
export function fondDeCarte() {
  return L.tileLayer('https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png', {
    attribution:
      '&copy; <a href="https://www.openstreetmap.org/copyright">contributeurs OpenStreetMap</a> · fond <a href="https://www.openstreetmap.fr/">OpenStreetMap France</a>',
    subdomains: 'abc',
    maxZoom: 19,
    className: 'fond-carte',
  })
}

// Rampe séquentielle gris clair -> émeraude (cohérente avec l'entonnoir).
export const RAMP = Array.from({ length: 6 }, (_, i) => greyToEmerald(i / 5))
export const NO_DATA = '#ececec'

// Rampe divergente rouge -> gris neutre -> vert, pour une évolution qui peut monter ou
// baisser (classe centrale = autour de zéro). Sept classes, seuils symétriques fixés
// par l'appelant (ex. [-6, -3, -1, 1, 3, 6]).
export const RAMP_DIVERGENT = ['#B91C1C', '#EF4444', '#FCA5A5', '#F3F4F6', '#86EFAC', '#22C55E', '#15803D']

export function quantileBreaks(values, n) {
  const v = values.filter((x) => x != null && !isNaN(x)).sort((a, b) => a - b)
  if (!v.length) return []
  const breaks = []
  for (let i = 1; i < n; i++) breaks.push(v[Math.floor((i / n) * (v.length - 1))])
  return breaks
}

/** Fabrique la fonction valeur -> couleur pour des seuils donnés. */
export function colorForFactory(breaks, noData = NO_DATA, ramp = RAMP) {
  return (v) => {
    if (v == null || isNaN(v)) return noData
    let i = 0
    while (i < breaks.length && v > breaks[i]) i++
    return ramp[Math.min(i, ramp.length - 1)]
  }
}

const signe = (x) => `${x > 0 ? '+' : x < 0 ? '−' : ''}${Math.abs(+x).toLocaleString('fr-FR')}`

/**
 * Contrôle de légende Leaflet (quantiles). swatch : 'square' (surfaces) ou
 * 'circle' (points) ; noDataRow ajoute la ligne « n/d ».
 */
export function legendControl({ label, unit, breaks, values, swatch = 'square', noDataRow = false, ramp = RAMP, diverging = false, position = 'bottomright' }) {
  const legend = L.control({ position })
  legend.onAdd = () => {
    const div = L.DomUtil.create('div')
    div.style.cssText =
      'background:#fff;padding:8px 10px;border-radius:8px;box-shadow:0 1px 4px rgba(0,0,0,.2);font-size:11px;line-height:1.7;'
    const vals = values.filter((v) => v != null && !isNaN(v))
    const lo = [vals.length ? Math.min(...vals) : 0, ...breaks]
    const radius = swatch === 'circle' ? '50%' : '2px'
    const sw = (color) =>
      `<span style="display:inline-block;width:12px;height:12px;background:${color};margin-right:6px;border-radius:${radius};"></span>`
    let html = `<div style="font-weight:700;margin-bottom:4px;">${label}</div>`
    for (let i = 0; i < ramp.length; i++) {
      let lab
      if (diverging) {
        // Seuils fixes et signés : « moins de −6 », « −6 à −3 », …, « plus de +6 ».
        if (i === 0) lab = `moins de ${signe(breaks[0])} ${unit}`
        else if (i === breaks.length) lab = `plus de ${signe(breaks[i - 1])} ${unit}`
        else lab = `${signe(breaks[i - 1])} à ${signe(breaks[i])} ${unit}`
      } else {
        const a = lo[i]
        const b = breaks[i]
        // Une décimale quand l'étendue est faible (sinon « 3–3 ») ; espace devant une unité en toutes lettres.
        const d = Math.max(...breaks) - Math.min(...breaks) < 10 ? 1 : 0
        const n = (x) => (+x).toLocaleString('fr-FR', { minimumFractionDigits: d, maximumFractionDigits: d, useGrouping: false })
        const u = /^[a-zà-ÿ]/i.test(unit) ? ` ${unit}` : unit
        lab = b != null ? `${n(a)}–${n(b)}${u}` : `≥ ${n(a)}${u}`
      }
      html += `<div>${sw(ramp[i])}${lab}</div>`
    }
    if (noDataRow) html += `<div>${sw(NO_DATA)}n/d</div>`
    div.innerHTML = html
    return div
  }
  return legend
}

/** Légende à catégories fixes (items : [{color, label}]), même habillage que legendControl. */
export function itemsLegendControl({ label, items, swatch = 'circle' }) {
  const legend = L.control({ position: 'bottomright' })
  legend.onAdd = () => {
    const div = L.DomUtil.create('div')
    div.style.cssText =
      'background:#fff;padding:8px 10px;border-radius:8px;box-shadow:0 1px 4px rgba(0,0,0,.2);font-size:11px;line-height:1.7;'
    const radius = swatch === 'circle' ? '50%' : '2px'
    let html = `<div style="font-weight:700;margin-bottom:4px;">${label}</div>`
    for (const it of items) {
      html += `<div><span style="display:inline-block;width:12px;height:12px;background:${it.color};margin-right:6px;border-radius:${radius};"></span>${it.label}</div>`
    }
    div.innerHTML = html
    return div
  }
  return legend
}
