import { Link } from 'react-router-dom'
import { Mail } from 'lucide-react'
import NewsletterForm from './NewsletterForm'
import InstallerApplication from './InstallerApplication'

function Footer() {
  return (
    <footer className="bg-gray-100 border-t border-gray-200 mt-20">
      <div className="max-w-7xl mx-auto px-4 py-12">
        <div className="grid md:grid-cols-3 gap-8">
          <div>
            <h3 className="font-bold text-gray-900 mb-4">Outsiders</h3>
            <p className="text-gray-600 text-sm">
              Comprendre la France par ses angles morts : des données publiques sous-utilisées,
              de l'école à la richesse, du pays à la commune, et des outils à faire tourner sur
              vos propres données.
            </p>
          </div>

          <div>
            <h4 className="font-semibold text-gray-900 mb-4">Navigation</h4>
            <div className="grid grid-cols-2 gap-x-4 gap-y-4 text-sm">
              <div>
                <div className="text-xs font-semibold uppercase tracking-wide text-gray-400 mb-1.5">Outils</div>
                <ul className="space-y-1.5">
                  <li><Link to="/atlas" className="text-gray-600 hover:text-blue-600 transition-colors">Carte des outsiders</Link></li>
                  <li><Link to="/territoires" className="text-gray-600 hover:text-blue-600 transition-colors">Fiche territoire</Link></li>
                  <li><Link to="/outils" className="text-gray-600 hover:text-blue-600 transition-colors">Tous les outils</Link></li>
                </ul>
              </div>
              <div>
                <div className="text-xs font-semibold uppercase tracking-wide text-gray-400 mb-1.5">Dossiers</div>
                <ul className="space-y-1.5">
                  <li><Link to="/terrains/ecole" className="text-gray-600 hover:text-blue-600 transition-colors">École</Link></li>
                  <li><Link to="/terrains/elus" className="text-gray-600 hover:text-blue-600 transition-colors">Élus</Link></li>
                  <li><Link to="/terrains" className="text-gray-600 hover:text-blue-600 transition-colors">Tous les terrains</Link></li>
                </ul>
              </div>
              <ul className="col-span-2 space-y-1.5 border-t border-gray-200 pt-3">
                <li><Link to="/methodologie" className="text-gray-600 hover:text-blue-600 transition-colors">Méthodologie</Link></li>
                <li><Link to="/about" className="text-gray-600 hover:text-blue-600 transition-colors">À propos</Link></li>
                <li><Link to="/about#collaborer" className="text-gray-600 hover:text-blue-600 transition-colors">Travailler avec nous</Link></li>
                <li><Link to="/presse" className="text-gray-600 hover:text-blue-600 transition-colors">Presse et réutilisation</Link></li>
                <li><Link to="/newsletter" className="text-gray-600 hover:text-blue-600 transition-colors">Newsletter</Link></li>
                <li><Link to="/fil" className="text-gray-600 hover:text-blue-600 transition-colors">Vrai ou faux, le fil</Link></li>
              </ul>
            </div>
          </div>

          <div>
            <h4 className="font-semibold text-gray-900 mb-4">Contact</h4>
            <a
              href="mailto:contact@dataoutsiders.fr"
              className="text-sm text-gray-600 hover:text-blue-600 transition-colors flex items-center gap-2 mb-4"
            >
              <Mail size={16} />
              contact@dataoutsiders.fr
            </a>
            <p className="text-xs text-gray-500">
              Une remarque, une donnée à signaler, un territoire à creuser ? Écrivez-nous.
            </p>
            <p className="text-xs text-gray-500 mt-3">
              Journaliste, chercheur, collectivité, association ?{' '}
              <Link to="/about#collaborer" className="text-blue-600 hover:underline">Travaillons ensemble</Link>.
            </p>
          </div>
        </div>

        <div className="border-t border-gray-200 mt-8 pt-8 max-w-xl">
          <h4 className="font-semibold text-gray-900 mb-1">Newsletter</h4>
          <p className="text-sm text-gray-600 mb-3">Recevoir les nouveaux dossiers et les mises à jour.</p>
          <NewsletterForm />
          <div className="mt-4">
            <InstallerApplication />
          </div>
        </div>

        <div className="border-t border-gray-200 mt-8 pt-8 text-sm text-gray-500 text-center">
          <p>
            © 2026 Outsiders. Contenu sous licence CC BY 4.0 ·{' '}
            <Link to="/mentions-legales" className="hover:text-blue-600 transition-colors">Mentions légales</Link>
          </p>
        </div>
      </div>
    </footer>
  )
}

export default Footer
