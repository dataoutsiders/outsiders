import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Mail, Check, Loader2 } from 'lucide-react'
import { NEWSLETTER_ACTION, NEWSLETTER_PAGE_BREVO } from '../config/newsletter'
import { trackEvent } from '../lib/analytics'

const ADRESSE_VALIDE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/

/**
 * Inscription à la newsletter, sans script ni cookie tiers : l'adresse est envoyée
 * directement au formulaire Brevo (champs EMAIL, piège à robots email_address_check vide,
 * locale, html_type, comme le code d'intégration). La réponse de Brevo n'est pas lisible
 * depuis le site (mode no-cors). L'adresse est inscrite dès l'envoi, sans mail de
 * confirmation (voir config/newsletter.js).
 *
 * variante : 'compact' (pied de page, bas de page) ou 'large' (page /newsletter).
 */
export default function NewsletterForm({ variante = 'compact', sombre = false }) {
  const { pathname } = useLocation()
  const [email, setEmail] = useState('')
  const [etat, setEtat] = useState('saisie') // saisie | envoi | envoye | erreur
  const [message, setMessage] = useState('')

  const envoyer = async (e) => {
    e.preventDefault()
    const adresse = email.trim()
    if (!ADRESSE_VALIDE.test(adresse)) {
      setEtat('erreur')
      setMessage('Cette adresse ne semble pas valide.')
      return
    }
    setEtat('envoi')
    try {
      await fetch(NEWSLETTER_ACTION, {
        method: 'POST',
        mode: 'no-cors',
        body: new URLSearchParams({ EMAIL: adresse, email_address_check: '', locale: 'fr', html_type: 'simple' }),
      })
      trackEvent(`newsletter-inscription${pathname}`, 'Newsletter : inscription envoyée')
      setEtat('envoye')
    } catch {
      setEtat('erreur')
      setMessage("L'envoi n'a pas abouti.")
    }
  }

  const texte = sombre ? 'text-gray-300' : 'text-gray-600'
  const petit = sombre ? 'text-gray-400' : 'text-gray-500'

  if (etat === 'envoye')
    return (
      <div className={`flex items-start gap-2 text-sm ${sombre ? 'text-emerald-300' : 'text-emerald-700'}`}>
        <Check size={18} className="shrink-0 mt-0.5" />
        <span>
          C'est noté : <strong>{email.trim()}</strong> recevra les prochains envois. Une erreur ? Chaque mail contient
          un lien de désinscription.
        </span>
      </div>
    )

  return (
    <form onSubmit={envoyer} noValidate>
      <div className={variante === 'large' ? 'flex flex-col sm:flex-row gap-3' : 'flex gap-2'}>
        <label htmlFor={`nl-${variante}`} className="sr-only">
          Adresse e-mail
        </label>
        <input
          id={`nl-${variante}`}
          type="email"
          inputMode="email"
          autoComplete="email"
          value={email}
          onChange={(e) => {
            setEmail(e.target.value)
            if (etat === 'erreur') setEtat('saisie')
          }}
          placeholder="votre@adresse.fr"
          className={`min-w-0 flex-1 px-3 ${variante === 'large' ? 'py-3' : 'py-2'} text-sm border border-gray-300 rounded-lg bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500`}
        />
        <button
          type="submit"
          disabled={etat === 'envoi'}
          className={`inline-flex items-center justify-center gap-1.5 px-4 ${variante === 'large' ? 'py-3' : 'py-2'} text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-60 whitespace-nowrap`}
        >
          {etat === 'envoi' ? <Loader2 size={16} className="animate-spin" /> : <Mail size={16} />}
          S'inscrire
        </button>
      </div>
      {etat === 'erreur' && (
        <p className="text-xs text-red-600 mt-2">
          {message}{' '}
          <a href={NEWSLETTER_PAGE_BREVO} target="_blank" rel="noopener noreferrer" className="underline">
            S'inscrire sur la page de notre prestataire
          </a>
          .
        </p>
      )}
      <p className={`text-xs ${petit} mt-2`}>
        Un mail quand un dossier sort ou qu'une donnée est mise à jour, pas plus d'un par mois. Adresse utilisée pour
        cette seule newsletter, via notre prestataire Brevo ; désinscription en un clic.{' '}
        <Link to="/mentions-legales" className={`underline ${texte}`}>
          Données personnelles
        </Link>
        .
      </p>
    </form>
  )
}
