import { useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Compass, Map, Search } from 'lucide-react'
import { usePageMeta } from '../lib/meta'

function NotFound() {
  usePageMeta('Page introuvable', "Cette page n'existe pas ou a changé d'adresse.")

  // Le site est servi en SPA : l'hébergeur répond 200 même pour une adresse inconnue.
  // On demande donc aux moteurs de ne pas indexer cette page.
  useEffect(() => {
    const tag = document.createElement('meta')
    tag.name = 'robots'
    tag.content = 'noindex'
    document.head.appendChild(tag)
    return () => tag.remove()
  }, [])
  return (
    <div className="py-20 px-4">
      <div className="max-w-2xl mx-auto text-center">
        <p className="text-sm font-semibold tracking-wide text-blue-600 mb-3">PAGE INTROUVABLE</p>
        <h1 className="text-4xl font-bold text-gray-900 mb-4">Cette page est restée dans un angle mort.</h1>
        <p className="text-lg text-gray-600 mb-10">
          L'adresse a peut-être changé, ou le lien est incomplet. Voici de quoi repartir.
        </p>
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <Link
            to="/"
            className="inline-flex items-center justify-center gap-2 px-5 py-3 rounded-lg bg-blue-600 text-white hover:bg-blue-700 transition-colors"
          >
            <Compass size={18} />
            Accueil
          </Link>
          <Link
            to="/atlas"
            className="inline-flex items-center justify-center gap-2 px-5 py-3 rounded-lg border border-gray-300 text-gray-700 hover:border-blue-600 hover:text-blue-600 transition-colors"
          >
            <Map size={18} />
            Carte des outsiders
          </Link>
          <Link
            to="/territoires"
            className="inline-flex items-center justify-center gap-2 px-5 py-3 rounded-lg border border-gray-300 text-gray-700 hover:border-blue-600 hover:text-blue-600 transition-colors"
          >
            <Search size={18} />
            Chercher une commune
          </Link>
        </div>
      </div>
    </div>
  )
}

export default NotFound
