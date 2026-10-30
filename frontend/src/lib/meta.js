/**
 * Titre et métadonnées de la page courante (SPA : mis à jour à la navigation).
 * Le rendu initial des balises pour les robots est assuré par
 * scripts/prerender-meta.mjs à partir de la même config (config/seo.js).
 */
import { useEffect } from 'react'
import { SITE_NAME, ROUTES_META } from '../config/seo'

function setTag(attr, key, content) {
  if (!content) return
  let el = document.head.querySelector(`meta[${attr}="${key}"]`)
  if (!el) {
    el = document.createElement('meta')
    el.setAttribute(attr, key)
    document.head.appendChild(el)
  }
  el.setAttribute('content', content)
}

/** Applique titre + description. Le titre reçoit le suffixe du site s'il ne le contient pas déjà. */
export function usePageMeta(title, description) {
  useEffect(() => {
    if (title) {
      const full = title.includes(SITE_NAME) ? title : `${title} · ${SITE_NAME}`
      document.title = full
      setTag('property', 'og:title', full)
    }
    if (description) {
      setTag('name', 'description', description)
      setTag('property', 'og:description', description)
    }
    setTag('property', 'og:url', window.location.origin + window.location.pathname)
  }, [title, description])
}

/**
 * Variante : métadonnées d'une route statique (config/seo.js), avec surcharge
 * possible pour les vues dynamiques (ex. le nom de la commune sur sa fiche).
 */
export function useRouteMeta(path, override = {}) {
  const base = ROUTES_META[path] || {}
  usePageMeta(override.title ?? base.title, override.description ?? base.description)
}
