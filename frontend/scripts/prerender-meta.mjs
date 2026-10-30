/**
 * Post-build : écrit dist/<route>/index.html pour chaque route statique, avec
 * titre + description + Open Graph propres à la route (config/seo.js).
 *
 * Pourquoi : le site est une SPA sans rendu serveur ; les robots des réseaux
 * sociaux ne lisent que le HTML initial. Cloudflare Pages sert le fichier
 * physique s'il existe (dist/atlas/index.html pour /atlas), sinon retombe sur
 * l'index racine : chaque lien partagé a donc son propre aperçu, sans SSR.
 *
 * Optionnel : SITE_URL=https://outsiders.example node scripts/prerender-meta.mjs
 * ajoute les og:url absolus.
 */
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { ROUTES_META, SITE_NAME, SITE_URL, ogSlug } from '../src/config/seo.js'

const root = join(dirname(fileURLToPath(import.meta.url)), '..')
const dist = join(root, 'dist')
const base = readFileSync(join(dist, 'index.html'), 'utf-8')
const siteUrl = (process.env.SITE_URL || SITE_URL).replace(/\/$/, '')

const esc = (s) => s.replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;')

function withMeta(html, path, { title, description }) {
  const full = title.includes(SITE_NAME) ? title : `${title} · ${SITE_NAME}`
  const image = `${siteUrl}/og/${ogSlug(path)}.png`
  let out = html
    .replace(/<title>[^<]*<\/title>/, `<title>${esc(full)}</title>`)
    .replace(
      /(<meta\s+name="description"\s+content=")[^"]*(")/,
      `$1${esc(description)}$2`,
    )
    .replace(
      /(<meta\s+property="og:title"\s+content=")[^"]*(")/,
      `$1${esc(full)}$2`,
    )
    .replace(
      /(<meta\s+property="og:description"\s+content=")[^"]*(")/,
      `$1${esc(description)}$2`,
    )
    .replace(
      /(<meta\s+property="og:image"\s+content=")[^"]*(")/,
      `$1${esc(image)}$2`,
    )
    .replace(
      /(<meta\s+name="twitter:image"\s+content=")[^"]*(")/,
      `$1${esc(image)}$2`,
    )
    .replace(
      '</head>',
      `  <meta property="og:url" content="${siteUrl}${path}" />\n  </head>`,
    )
  return out
}

let n = 0
for (const [path, meta] of Object.entries(ROUTES_META)) {
  if (path === '/') {
    writeFileSync(join(dist, 'index.html'), withMeta(base, path, meta))
    n++
    continue
  }
  const dir = join(dist, ...path.split('/').filter(Boolean))
  mkdirSync(dir, { recursive: true })
  writeFileSync(join(dir, 'index.html'), withMeta(base, path, meta))
  n++
}
console.log(`prerender-meta : ${n} routes écrites dans dist/ (base ${siteUrl})`)
