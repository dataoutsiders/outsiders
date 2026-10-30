import { useEffect, useMemo, useRef } from 'react'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { RAMP, quantileBreaks, colorForFactory, legendControl, itemsLegendControl, fondDeCarte } from './choroplethScale'

// Cadre de la France métropolitaine (Corse comprise), pour fit="metropole".
const enMetropole = (p) => p.lat > 41 && p.lat < 51.6 && p.lon > -5.6 && p.lon < 10

/**
 * Carte à points (Leaflet canvas), un point par établissement, coloré par valeur.
 * Par défaut : rampe séquentielle par quantiles. Options (à passer stables, via
 * useMemo/useCallback ou au niveau module, sinon la couche est redessinée à chaque rendu) :
 * colorFn (valeur -> couleur) + legendItems ([{color, label}]) pour une échelle à
 * catégories, tooltipFn (point -> HTML déjà échappé), fit (cadrer sur les points).
 * @param {Array<{lat:number, lon:number, value:number, label:string}>} points
 */
export default function PointMap({
  points, unit = '', label = 'IPS', height = 560,
  colorFn = null, legendItems = null, tooltipFn = null, fit = false, radius = 3,
}) {
  const containerRef = useRef(null)
  const mapRef = useRef(null)
  const layerRef = useRef(null)
  const legendRef = useRef(null)

  const breaks = useMemo(
    () => (colorFn ? [] : quantileBreaks(points.map((p) => p.value), RAMP.length)),
    [points, colorFn],
  )
  const colorFor = useMemo(() => colorFn || colorForFactory(breaks, '#cbd5e1'), [colorFn, breaks])

  useEffect(() => {
    if (mapRef.current || !containerRef.current) return
    const map = L.map(containerRef.current, { center: [46.6, 2.4], zoom: 6, scrollWheelZoom: true, preferCanvas: true })
    fondDeCarte().addTo(map)
    mapRef.current = map
    setTimeout(() => {
      try {
        map.invalidateSize()
      } catch {
        /* noop */
      }
    }, 150)
    return () => {
      map.remove()
      mapRef.current = null
    }
  }, [])

  useEffect(() => {
    const map = mapRef.current
    if (!map) return
    if (layerRef.current) map.removeLayer(layerRef.current)
    const renderer = L.canvas({ padding: 0.5 })
    const layer = L.layerGroup()
    const coords = []
    for (const p of points) {
      if (p.lat == null || p.lon == null || p.value == null) continue
      coords.push([p.lat, p.lon])
      L.circleMarker([p.lat, p.lon], { renderer, radius, stroke: false, fillColor: colorFor(p.value), fillOpacity: 0.75 })
        .bindTooltip(tooltipFn ? tooltipFn(p) : `<strong>${p.label}</strong><br/>${label} ${(+p.value).toFixed(1)}${unit}`, { sticky: true })
        .addTo(layer)
    }
    layer.addTo(map)
    layerRef.current = layer
    if (fit && coords.length) {
      // fit = 'metropole' ou fonction : on cadre sur les points retenus, sinon sur tous.
      const filtre = typeof fit === 'function' ? fit : fit === 'metropole' ? enMetropole : null
      const cadre = filtre
        ? points.filter((p) => p.lat != null && p.lon != null && filtre(p)).map((p) => [p.lat, p.lon])
        : coords
      map.fitBounds(cadre.length ? cadre : coords, { padding: [28, 28], maxZoom: 11 })
    }

    if (legendRef.current) legendRef.current.remove()
    const legend = legendItems
      ? itemsLegendControl({ label, items: legendItems })
      : legendControl({
          label,
          unit,
          breaks,
          values: points.map((p) => p.value),
          swatch: 'circle',
        })
    legend.addTo(map)
    legendRef.current = legend
  }, [points, breaks, colorFor, label, unit, legendItems, tooltipFn, fit, radius])

  return <div ref={containerRef} style={{ width: '100%', height }} className="rounded-lg overflow-hidden" />
}
