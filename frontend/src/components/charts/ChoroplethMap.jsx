import { useEffect, useMemo, useRef } from 'react'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { RAMP, RAMP_DIVERGENT, quantileBreaks, colorForFactory, legendControl, fondDeCarte } from './choroplethScale'

const fmt = (v, unit) => (v == null ? 'non renseigné' : `${(+v).toFixed(1)} ${unit}`)

/**
 * Choroplèthe Leaflet, générique (départements OU EPCI). Leaflet dessine en
 * planaire : insensible à l'ordre d'enroulement des polygones (contrairement à
 * d3-geo), ce qui règle l'affichage du GeoJSON EPCI.
 *
 * @param {Object} geo          FeatureCollection (propriétés {code, nom})
 * @param {Object} valueByCode  code -> valeur numérique
 * @param {number[]} divergingBreaks  seuils symétriques (6 valeurs) : active la rampe
 *                   rouge / vert, pour une évolution qui peut monter ou baisser
 */
export default function ChoroplethMap({
  geo,
  valueByCode,
  unit = '%',
  height = 560,
  label = 'IDP',
  format = null,
  onSelectFeature = null,
  highlightCode = null,
  fitBounds = false,
  divergingBreaks = null,
}) {
  const containerRef = useRef(null)
  const mapRef = useRef(null)
  const layerRef = useRef(null)
  const legendRef = useRef(null)
  const featuresRef = useRef({})

  const ramp = divergingBreaks ? RAMP_DIVERGENT : RAMP
  const breaks = useMemo(
    () => divergingBreaks ?? quantileBreaks(Object.values(valueByCode), RAMP.length),
    [valueByCode, divergingBreaks],
  )

  const colorFor = colorForFactory(breaks, undefined, ramp)

  // Init de la carte (une fois), vue métropole fixe.
  useEffect(() => {
    if (mapRef.current || !containerRef.current) return
    const map = L.map(containerRef.current, {
      center: [46.6, 2.4],
      zoom: 6,
      scrollWheelZoom: true,
      attributionControl: true,
    })
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

  // (Re)dessin de la couche quand le GeoJSON ou les valeurs changent.
  useEffect(() => {
    const map = mapRef.current
    if (!map || !geo) return
    if (layerRef.current) {
      map.removeLayer(layerRef.current)
      layerRef.current = null
    }
    featuresRef.current = {}

    const layer = L.geoJSON(geo, {
      style: (feat) => {
        const val = valueByCode[feat.properties.code]
        return {
          fillColor: colorFor(val),
          fillOpacity: val == null ? 0.4 : 0.85,
          color: '#ffffff',
          weight: 0.4,
        }
      },
      onEachFeature: (feat, lyr) => {
        featuresRef.current[feat.properties.code] = lyr
        const val = valueByCode[feat.properties.code]
        const txt = val == null ? 'non renseigné' : format ? format(val) : fmt(val, unit)
        lyr.bindTooltip(`<strong>${feat.properties.nom}</strong><br/>${txt}`, { sticky: true })
        const handlers = {
          mouseover: (e) => e.target.setStyle({ weight: 1.5, color: '#333' }),
          mouseout: (e) => layer.resetStyle(e.target),
        }
        if (onSelectFeature) handlers.click = () => onSelectFeature(feat.properties.code)
        lyr.on(handlers)
      },
    }).addTo(map)
    layerRef.current = layer

    if (fitBounds) {
      try {
        map.fitBounds(layer.getBounds(), { padding: [12, 12] })
      } catch {
        /* noop */
      }
    } else {
      map.setView([46.6, 2.4], 6)
    }

    // Légende (quantiles)
    if (legendRef.current) legendRef.current.remove()
    const legend = legendControl({
      label,
      unit,
      breaks,
      values: Object.values(valueByCode),
      swatch: 'square',
      noDataRow: true,
      ramp,
      diverging: !!divergingBreaks,
    })
    legend.addTo(map)
    legendRef.current = legend
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [geo, valueByCode, breaks, unit, label, format, onSelectFeature, fitBounds])

  // Surbrillance d'un territoire (survol d'un outsider dans le bloc d'analyse).
  useEffect(() => {
    const layer = layerRef.current
    if (!layer) return
    Object.values(featuresRef.current).forEach((lyr) => layer.resetStyle(lyr))
    const hl = highlightCode && featuresRef.current[highlightCode]
    if (hl) {
      hl.setStyle({ weight: 3, color: '#111827' })
      try {
        hl.bringToFront()
      } catch {
        /* noop */
      }
    }
  }, [highlightCode, geo, valueByCode])

  return <div ref={containerRef} style={{ width: '100%', height }} className="rounded-lg overflow-hidden" />
}
