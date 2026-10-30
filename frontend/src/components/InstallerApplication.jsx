import { useEffect, useState } from 'react'
import { Download, Share } from 'lucide-react'
import { trackEvent } from '../lib/analytics'

const dejaInstallee = () =>
  window.matchMedia?.('(display-mode: standalone)').matches || window.navigator.standalone === true

const surIphone = () => /iphone|ipad|ipod/i.test(window.navigator.userAgent)

/**
 * Proposer d'installer le site sur l'écran d'accueil (application web, manifest.webmanifest).
 * Android et ordinateur (Chrome, Edge) : bouton qui ouvre la fenêtre d'installation du
 * navigateur, quand celui-ci la propose. iPhone : pas de bouton possible, on explique le geste.
 * Rien n'est affiché si le site est déjà ouvert comme application.
 */
export default function InstallerApplication({ sombre = false }) {
  const [invite, setInvite] = useState(null)
  const [installee, setInstallee] = useState(false)

  useEffect(() => {
    setInstallee(dejaInstallee())
    const garder = (e) => {
      e.preventDefault()
      setInvite(e)
    }
    const fini = () => {
      setInstallee(true)
      trackEvent('application-installee', 'Application installée')
    }
    window.addEventListener('beforeinstallprompt', garder)
    window.addEventListener('appinstalled', fini)
    return () => {
      window.removeEventListener('beforeinstallprompt', garder)
      window.removeEventListener('appinstalled', fini)
    }
  }, [])

  if (installee) return null
  const petit = sombre ? 'text-gray-400' : 'text-gray-500'

  if (invite)
    return (
      <button
        onClick={async () => {
          trackEvent('application-proposee', "Application : fenêtre d'installation ouverte")
          invite.prompt()
          await invite.userChoice.catch(() => null)
          setInvite(null)
        }}
        className="inline-flex items-center gap-1.5 min-h-[40px] px-3 rounded-lg border border-gray-300 bg-white text-sm font-medium text-gray-700 hover:border-blue-300 hover:text-blue-700"
      >
        <Download size={16} /> Installer l'application
      </button>
    )

  if (surIphone())
    return (
      <p className={`text-xs ${petit} flex items-center gap-1 flex-wrap`}>
        Sur iPhone, pour l'avoir comme une application : touchez <Share size={13} className="inline" /> Partager,
        puis « Sur l'écran d'accueil ».
      </p>
    )

  return null
}
