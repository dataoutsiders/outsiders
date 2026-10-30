import { useEffect, useMemo, useRef } from 'react'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { RAMP, quantileBreaks, colorForFactory, legendControl, fondDeCarte } from './choroplethScale'

/**
 * Carte des carreaux de 200 m d'une ville, colorés par niveau de vie moyen.
 * La couleur est calculée en quantiles PROPRES à la ville : on voit si les
 * quartiers riches et pauvres se mélangent (damier bariolé) ou se regroupent
 * (grandes plages de couleur). C'est la preuve visuelle de la ségrégation.
 *
 * @param {Array<[number,number,number,number]>} carreaux [lat, lon, niveauDeVie, nbHab]
 * @param {'revenu'|'age'} mode  colore par revenu (défaut) ; 'age' réservé pour extension
 */
export default function CarreauxMap({ carreaux, height = 460 }) {
  const containerRef = useRef(null)
  const mapRef = useRef(null)
  const layerRef = useRef(null)
  const legendRef = useRef(null)

  const values = useMemo(() => carreaux.map((c) => c[2]), [carreaux])
  const breaks = useMemo(() => quantileBreaks(values, RAMP.length), [values])
  const colorFor = colorForFactory(breaks, '#cbd5e1')

  useEffect(() => {
    if (mapRef.current || !containerRef.current) return
    const map = L.map(containerRef.current, { zoomControl: true, scrollWheelZoom: false, preferCanvas: true })
    fondDeCarte().addTo(map)
    mapRef.current = map
    setTimeout(() => { try { map.invalidateSize() } catch { /* noop */ } }, 150)
    return () => { map.remove(); mapRef.current = null }
  }, [])

  useEffect(() => {
    const map = mapRef.current
    if (!map || !carreaux.length) return
    if (layerRef.current) map.removeLayer(layerRef.current)
    const renderer = L.canvas({ padding: 0.5 })
    const layer = L.layerGroup()
    for (const [lat, lon, rev, ind] of carreaux) {
      if (lat == null || lon == null || rev == null) continue
      L.circleMarker([lat, lon], { renderer, radius: 4, stroke: false, fillColor: colorFor(rev), fillOpacity: 0.82 })
        .bindTooltip(`Niveau de vie moyen : <strong>${rev.toLocaleString('fr-FR')} €</strong>/an<br/>${Math.round(ind)} habitants`, { sticky: true })
        .addTo(layer)
    }
    layer.addTo(map)
    layerRef.current = layer

    const bounds = L.latLngBounds(carreaux.map((c) => [c[0], c[1]]))
    if (bounds.isValid()) map.fitBounds(bounds, { padding: [20, 20] })

    if (legendRef.current) legendRef.current.remove()
    const legend = legendControl({ label: 'Niveau de vie', unit: ' €', breaks, values, swatch: 'circle' })
    legend.addTo(map)
    legendRef.current = legend
  }, [carreaux, breaks])

  return <div ref={containerRef} style={{ width: '100%', height }} className="rounded-lg overflow-hidden border border-gray-200" />
}
