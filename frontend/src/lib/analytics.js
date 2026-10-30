/**
 * Comptage des pages vues (GoatCounter), adapté à une SPA.
 *
 * La balise GoatCounter (index.html) compte la PREMIÈRE page au chargement.
 * Comme la navigation React ne recharge pas la page, ce hook signale chaque
 * changement de route côté client (en sautant la 1re vue, déjà comptée par la
 * balise, pour éviter le double comptage et toute course au chargement async).
 *
 * Inerte si GoatCounter n'est pas présent (dev local, ou compte non configuré) :
 * window.goatcounter est alors undefined et rien n'est envoyé.
 */
import { useEffect, useRef } from 'react'
import { useLocation } from 'react-router-dom'

export function usePageviews() {
  const { pathname, search } = useLocation()
  const first = useRef(true)
  useEffect(() => {
    if (first.current) {
      first.current = false // 1re vue déjà comptée par la balise (onload)
      return
    }
    window.goatcounter?.count?.({ path: pathname + search })
  }, [pathname, search])
}

/**
 * Compte une action (événement GoatCounter) : intégrer une carte, copier une phrase, lancer
 * un outil... Le nom décrit l'action, jamais la personne ; rien de ce qu'elle saisit n'est
 * envoyé (pour l'outil Représentativité, seul le fait de lancer l'analyse est compté).
 * Inerte sans GoatCounter, comme usePageviews.
 */
export function trackEvent(name, title) {
  window.goatcounter?.count?.({ path: name, title: title || name, event: true })
}
