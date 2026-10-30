/**
 * Génère une image de partage (Open Graph) 1200×630 par route statique, au build.
 *
 * Pourquoi au build : le site est une SPA sans serveur de rendu ; générer des
 * cartes de marque cohérentes une fois pour toutes évite tout backend et garde
 * les fichiers versionnables. Les images dynamiques (fiche d'une commune, nuage
 * d'un croisement précis) relèveront d'une Cloudflare Pages Function (phase 2).
 *
 * Rendu : satori (arbre d'éléments -> SVG) puis @resvg/resvg-js (SVG -> PNG).
 * Police : Inter (.woff, même police que le site) fournie par @fontsource/inter.
 */
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import satori from 'satori'
import { Resvg } from '@resvg/resvg-js'
import { ROUTES_META, SITE_NAME, ogSlug } from '../src/config/seo.js'

const root = join(dirname(fileURLToPath(import.meta.url)), '..')
const outDir = join(root, 'dist', 'og')
const fontDir = join(root, 'node_modules', '@fontsource', 'inter', 'files')
const font = (w) => readFileSync(join(fontDir, `inter-latin-${w}-normal.woff`))

// Identité tricolore officielle (mêmes tokens que src/index.css).
const BLUE = '#0063CB'
const RED = '#E1000F'
const INK = '#161616'
const GRAY = '#5b5b5b'
const PAPER = '#FFFFFF'

// Élément « React-like » accepté tel quel par satori (pas de JSX nécessaire).
const el = (type, style, children) => ({ type, props: { style, children } })
const txt = (style, s) => el('div', { display: 'flex', ...style }, s)

/** Bandeau contextuel selon la section de route. */
function eyebrow(path) {
  if (path === '/') return 'Données publiques · France entière'
  if (path.startsWith('/atlas')) return 'La carte'
  if (path.startsWith('/territoires')) return 'Situer un territoire'
  if (path.startsWith('/explorer')) return 'Comparer des groupes'
  if (path.startsWith('/outils')) return 'Les outils'
  if (path.startsWith('/terrains')) return 'Dossier'
  if (path.startsWith('/themes')) return 'Thème'
  if (path.startsWith('/methodologie') || path.startsWith('/about')) return 'À propos'
  return SITE_NAME
}

/** Titre affiché sur l'image (accroche plus percutante que le <title> pour la home). */
function ogTitle(path, meta) {
  if (path === '/') return 'Vous croyez connaître la France ?'
  return meta.title
}

function card(path, meta) {
  const title = ogTitle(path, meta)
  const big = title.length <= 46
  return el(
    'div',
    {
      width: 1200,
      height: 630,
      display: 'flex',
      flexDirection: 'column',
      backgroundColor: PAPER,
      fontFamily: 'Inter',
      position: 'relative',
      padding: '76px 84px 64px 96px',
    },
    [
      // Épine tricolore à gauche (nod au drapeau : bleu / blanc = fond / rouge).
      el('div', { position: 'absolute', left: 0, top: 0, bottom: 0, width: 16, display: 'flex', flexDirection: 'column' }, [
        el('div', { flex: 1, backgroundColor: BLUE }, ''),
        el('div', { flex: 1, backgroundColor: PAPER }, ''),
        el('div', { flex: 1, backgroundColor: RED }, ''),
      ]),

      // En-tête : marque + point rouge.
      el('div', { display: 'flex', alignItems: 'center', marginBottom: 'auto' }, [
        txt({ fontSize: 30, fontWeight: 700, letterSpacing: 4, color: INK }, 'OUTSIDERS'),
        el('div', { width: 12, height: 12, borderRadius: 12, backgroundColor: RED, marginLeft: 12, display: 'flex' }, ''),
      ]),

      // Bandeau contextuel.
      txt(
        { fontSize: 24, fontWeight: 600, letterSpacing: 3, color: BLUE, textTransform: 'uppercase', marginBottom: 22 },
        eyebrow(path),
      ),

      // Titre.
      txt(
        { fontSize: big ? 72 : 58, fontWeight: 700, color: INK, lineHeight: 1.05, letterSpacing: -1, maxWidth: 940 },
        title,
      ),

      // Description.
      txt(
        { fontSize: 29, fontWeight: 400, color: GRAY, lineHeight: 1.35, marginTop: 26, maxWidth: 900 },
        meta.description,
      ),

      // Pied : filet + signature.
      el('div', { display: 'flex', alignItems: 'center', marginTop: 'auto', paddingTop: 34, borderTop: '2px solid #ECECEC' }, [
        el('div', { display: 'flex', marginRight: 14 }, [
          el('div', { width: 26, height: 10, backgroundColor: BLUE, display: 'flex' }, ''),
          el('div', { width: 26, height: 10, backgroundColor: RED, display: 'flex' }, ''),
        ]),
        txt({ fontSize: 24, fontWeight: 600, color: INK }, 'Comprendre la France par ses angles morts'),
      ]),
    ],
  )
}

const fonts = [
  { name: 'Inter', data: font('400'), weight: 400, style: 'normal' },
  { name: 'Inter', data: font('600'), weight: 600, style: 'normal' },
  { name: 'Inter', data: font('700'), weight: 700, style: 'normal' },
]

mkdirSync(outDir, { recursive: true })
let n = 0
for (const [path, meta] of Object.entries(ROUTES_META)) {
  const svg = await satori(card(path, meta), { width: 1200, height: 630, fonts })
  const png = new Resvg(svg, { fitTo: { mode: 'width', value: 1200 } }).render().asPng()
  writeFileSync(join(outDir, `${ogSlug(path)}.png`), png)
  n++
}
console.log(`generate-og : ${n} images de partage écrites dans dist/og/`)
