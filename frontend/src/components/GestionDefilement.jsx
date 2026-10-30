import { useEffect } from 'react'
import { useLocation, useNavigationType } from 'react-router-dom'

// Pages dont le contenu change selon l'adresse (?code=...) : changer de territoire, c'est
// changer de page. Ailleurs (Atlas, dossiers à filtres), les paramètres règlent une vue sans
// devoir remonter en haut.
const PARAMS_DE_PAGE = {
  '/territoires': ['code', 'niveau'],
}

function clePage(pathname, search) {
  const params = PARAMS_DE_PAGE[pathname]
  if (!params) return pathname
  const p = new URLSearchParams(search)
  return `${pathname}?${params.map((k) => `${k}=${p.get(k) ?? ''}`).join('&')}`
}

const haut = () => window.scrollTo({ top: 0, left: 0, behavior: 'instant' })

/**
 * Défilement à chaque navigation (le routeur ne le gère pas) :
 * - nouvelle page : en haut ;
 * - lien vers une section (#ancre) : sur la section, sous l'en-tête fixe, une fois la page
 *   affichée (pages chargées à la demande : on réessaie quelques fois) ;
 * - retour ou avance du navigateur : rien, le navigateur garde la main.
 *
 * Le saut est INSTANTANÉ : index.css rend le défilement animé (scroll-behavior: smooth), et une
 * animation lancée pendant que la nouvelle page se charge est interrompue quand sa hauteur
 * change, ce qui laissait la page au milieu ou en bas.
 */
export default function GestionDefilement() {
  const { pathname, search, hash } = useLocation()
  const type = useNavigationType()
  const cle = clePage(pathname, search)

  useEffect(() => {
    if (type === 'POP') return
    if (!hash) {
      haut()
      return
    }
    let essais = 0
    let minuteur
    const viser = () => {
      const cible = document.getElementById(decodeURIComponent(hash.slice(1)))
      if (cible) {
        const entete = document.querySelector('header')?.offsetHeight ?? 0
        window.scrollTo({ top: cible.getBoundingClientRect().top + window.scrollY - entete - 16, behavior: 'instant' })
      } else if (essais++ < 20) {
        minuteur = setTimeout(viser, 100)
      } else {
        haut()
      }
    }
    viser()
    return () => clearTimeout(minuteur)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [cle, hash])

  return null
}
