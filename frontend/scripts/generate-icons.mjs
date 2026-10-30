/**
 * Icônes du site et de l'application installable (une fois, puis à relancer si le dessin change) :
 *   node scripts/generate-icons.mjs
 * Écrit dans public/ : favicon.svg, icons/icon-192.png, icons/icon-512.png,
 * icons/icon-maskable-512.png (contenu réduit dans la zone sûre des icônes rognées par
 * Android) et icons/apple-touch-icon.png (180 px, iPhone).
 *
 * Dessin : sur le bleu du site, des points blancs alignés sur une droite (le pronostic) et
 * un point rouge à l'écart (l'outsider), soit le nuage de l'Atlas en miniature. Couleurs de
 * l'identité tricolore (generate-og.mjs).
 */
import { mkdirSync, writeFileSync } from 'node:fs'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'
import { Resvg } from '@resvg/resvg-js'

const BLUE = '#0063CB'
const RED = '#E1000F'
const root = join(dirname(fileURLToPath(import.meta.url)), '..')
const pub = join(root, 'public')

// Contenu dessiné sur une grille de 512 ; `echelle` < 1 le resserre autour du centre.
const dessin = (echelle = 1) => `
  <g transform="translate(256 256) scale(${echelle}) translate(-256 -256)">
    <line x1="104" y1="408" x2="408" y2="104" stroke="#FFFFFF" stroke-opacity="0.35" stroke-width="14" stroke-linecap="round"/>
    <circle cx="140" cy="372" r="36" fill="#FFFFFF"/>
    <circle cx="220" cy="292" r="36" fill="#FFFFFF"/>
    <circle cx="300" cy="212" r="36" fill="#FFFFFF"/>
    <circle cx="380" cy="132" r="36" fill="#FFFFFF"/>
    <circle cx="358" cy="362" r="54" fill="${RED}" stroke="#FFFFFF" stroke-width="12"/>
  </g>`

const svg = ({ arrondi = 0, echelle = 1 } = {}) =>
  `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">` +
  `<rect width="512" height="512" rx="${arrondi}" fill="${BLUE}"/>${dessin(echelle)}</svg>`

const png = (source, taille) =>
  new Resvg(source, { fitTo: { mode: 'width', value: taille } }).render().asPng()

mkdirSync(join(pub, 'icons'), { recursive: true })
writeFileSync(join(pub, 'favicon.svg'), svg({ arrondi: 96 }))
writeFileSync(join(pub, 'icons', 'icon-192.png'), png(svg({ arrondi: 96 }), 192))
writeFileSync(join(pub, 'icons', 'icon-512.png'), png(svg({ arrondi: 96 }), 512))
// Icône « maskable » : fond plein (le système découpe), dessin dans le cercle sûr de 80 %.
writeFileSync(join(pub, 'icons', 'icon-maskable-512.png'), png(svg({ echelle: 0.78 }), 512))
// iPhone : fond plein, le système arrondit lui-même.
writeFileSync(join(pub, 'icons', 'apple-touch-icon.png'), png(svg({ echelle: 0.9 }), 180))
console.log('generate-icons : favicon.svg + 4 icônes écrites dans public/')
