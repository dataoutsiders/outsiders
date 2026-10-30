/**
 * Post-build : écrit dist/robots.txt et dist/sitemap.xml à partir des routes
 * déclarées dans config/seo.js (même source que les aperçus de partage).
 *
 * Sans ces deux fichiers, le repli SPA de Cloudflare Pages renvoie la page
 * d'accueil à leur place, et les moteurs de recherche ne trouvent ni consignes
 * ni plan du site.
 */
import { writeFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { ROUTES_META, SITE_URL } from '../src/config/seo.js'

const dist = join(dirname(fileURLToPath(import.meta.url)), '..', 'dist')
const siteUrl = (process.env.SITE_URL || SITE_URL).replace(/\/$/, '')

// Pages accessibles mais retirées de la navigation : on ne les propose pas aux moteurs.
const HORS_PLAN = new Set(['/themes'])

const jour = new Date().toISOString().slice(0, 10)
const urls = Object.keys(ROUTES_META)
  .filter((path) => !HORS_PLAN.has(path))
  .map((path) => {
    const priorite = path === '/' ? '1.0' : path === '/mentions-legales' ? '0.2' : '0.7'
    return `  <url>\n    <loc>${siteUrl}${path}</loc>\n    <lastmod>${jour}</lastmod>\n    <priority>${priorite}</priority>\n  </url>`
  })

writeFileSync(
  join(dist, 'sitemap.xml'),
  `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls.join('\n')}\n</urlset>\n`,
)

// Les vues /embed sont des copies nues destinées aux iframes : inutile de les indexer.
writeFileSync(
  join(dist, 'robots.txt'),
  `User-agent: *\nAllow: /\nDisallow: /embed/\n\nSitemap: ${siteUrl}/sitemap.xml\n`,
)

console.log(`generate-sitemap : ${urls.length} adresses dans dist/sitemap.xml, robots.txt écrit`)
