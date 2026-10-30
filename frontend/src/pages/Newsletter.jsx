import { useEffect } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { Mail, CheckCircle2 } from 'lucide-react'
import { useRouteMeta } from '../lib/meta'
import { trackEvent } from '../lib/analytics'
import NewsletterForm from '../components/NewsletterForm'

// /newsletter : inscription, et page de retour de Brevo après la double confirmation
// (?confirme=1, réglé dans le formulaire Brevo).
function Newsletter() {
  useRouteMeta('/newsletter')
  const [params] = useSearchParams()
  const confirme = params.get('confirme') === '1'

  useEffect(() => {
    if (confirme) trackEvent('newsletter-confirmee', 'Newsletter : inscription confirmée')
  }, [confirme])

  return (
    <div className="py-12 px-4">
      <div className="max-w-2xl mx-auto">
        {confirme ? (
          <div className="bg-emerald-50 border border-emerald-200 rounded-2xl p-6 mb-10 flex gap-3">
            <CheckCircle2 className="text-emerald-600 shrink-0" size={26} />
            <div>
              <h1 className="text-2xl font-bold text-gray-900 mb-1">Inscription confirmée, merci</h1>
              <p className="text-gray-700">
                Vous recevrez un mail quand un dossier sort ou qu'une donnée est mise à jour. En attendant, les{' '}
                <Link to="/terrains" className="text-blue-600 hover:underline">dossiers</Link> et la{' '}
                <Link to="/atlas" className="text-blue-600 hover:underline">carte des outsiders</Link> sont là.
              </p>
            </div>
          </div>
        ) : (
          <header className="mb-8">
            <div className="flex items-center gap-2 text-blue-600 mb-2">
              <Mail size={18} />
              <span className="text-sm font-semibold uppercase tracking-wide">Newsletter</span>
            </div>
            <h1 className="text-4xl font-bold text-gray-900 mb-4">Recevoir les nouveaux dossiers</h1>
            <p className="text-lg text-gray-600">
              Un mail quand un dossier sort ou qu'une donnée publique est mise à jour, avec ce qu'elle change. Pas plus
              d'un par mois, sans publicité.
            </p>
          </header>
        )}

        {!confirme && (
          <div className="bg-white border border-gray-200 rounded-2xl p-6">
            <NewsletterForm variante="large" />
          </div>
        )}

        <section className="mt-10 text-sm text-gray-600 space-y-2">
          <h2 className="font-semibold text-gray-900">Ce que devient votre adresse</h2>
          <ul className="list-disc pl-6 space-y-1.5">
            <li>Elle sert uniquement à vous envoyer cette newsletter ; elle n'est ni cédée, ni vendue.</li>
            <li>
              Elle est conservée chez notre prestataire d'envoi, Brevo, dont les données sont hébergées dans l'Union
              européenne, jusqu'à votre désinscription.
            </li>
            <li>Chaque mail contient un lien de désinscription ; un clic suffit.</li>
            <li>
              Inscrit par erreur, ou par quelqu'un d'autre ? Le lien de désinscription du premier mail reçu vous retire de
              la liste, ou écrivez-nous.
            </li>
          </ul>
          <p>
            Détails dans les{' '}
            <Link to="/mentions-legales" className="text-blue-600 hover:underline">mentions légales</Link>.
          </p>
        </section>
      </div>
    </div>
  )
}

export default Newsletter
