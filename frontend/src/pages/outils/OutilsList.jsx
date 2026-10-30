import { Link } from 'react-router-dom'
import {
  Globe, ShieldCheck, ArrowRight, Wrench, Map as MapIcon, Building2, Layers3,
} from 'lucide-react'
import { useRouteMeta } from '../../lib/meta'

/**
 * Tous les outils, rangés par ce qu'ils permettent de faire. Deux familles :
 * ceux qui tournent sur les données publiques qu'on fournit, et ceux qui
 * tournent sur vos propres fichiers (100 % navigateur).
 */
const FAMILLES = [
  {
    id: 'publiques',
    titre: 'Sur les données publiques',
    sous: "La donnée est fournie et sourcée ; vous menez l'enquête.",
    outils: [
      {
        to: '/atlas',
        icon: MapIcon,
        color: '#3B82F6',
        titre: 'La carte des outsiders',
        description:
          "Croisez deux indicateurs sur la carte de France : une droite de pronostic apparaît, et avec elle les territoires qui la démentent. Du département à la commune, vue intégrable en iframe.",
        tags: ['Carte', 'Croisements', 'Embed'],
      },
      {
        to: '/territoires',
        icon: Building2,
        color: '#0EA5E9',
        titre: 'La fiche territoire',
        description:
          "Une commune ou un département : ses atypies, son jumeau statistique et tous ses indicateurs situés par rapport à la France, au département ou aux communes de même taille.",
        tags: ['Commune', 'Jumeau statistique'],
      },
      {
        to: '/explorer/milieu-social',
        icon: Layers3,
        color: '#F59E0B',
        titre: 'Les comparateurs : groupes et pays',
        description:
          "Milieu social, sexe, âge ou pays européens : les mêmes indicateurs, les mêmes sources officielles, pour mesurer les écarts. Tableau, heatmap et fiches par catégorie, dont la fiche France parmi 30 pays.",
        tags: ['Milieu social', 'Sexe', 'Âge', 'Pays'],
      },
    ],
  },
  {
    id: 'fichiers',
    titre: 'Sur vos fichiers',
    sous: 'Vos données restent dans votre navigateur, rien ne transite par un serveur.',
    outils: [
      {
        to: '/outils/representativite',
        icon: Globe,
        color: '#10B981',
        titre: "Représentativité d'un fichier de noms",
        description:
          'Mesurez la diversité patronymique, le taux de féminisation et la structure d\'âge d\'une liste de noms, comparés à la population française.',
        tags: ['Diversité', 'Sexe', 'Âge', 'Discriminations'],
      },
    ],
  },
]

function OutilCard({ o }) {
  const Icon = o.icon
  return (
    <Link
      to={o.to}
      className="group bg-white rounded-xl border border-gray-200 p-6 shadow-sm hover:shadow-md hover:border-gray-300 transition-all"
    >
      <div className="flex items-center gap-3 mb-3">
        <div className="p-2.5 rounded-lg" style={{ backgroundColor: o.color + '20' }}>
          <Icon size={22} style={{ color: o.color }} />
        </div>
        <h2 className="font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
          {o.titre}
        </h2>
      </div>
      <p className="text-sm text-gray-600 mb-4">{o.description}</p>
      <div className="flex flex-wrap gap-1.5 mb-4">
        {o.tags.map((t) => (
          <span key={t} className="px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-600">
            {t}
          </span>
        ))}
      </div>
      <span className="inline-flex items-center gap-1.5 text-sm font-medium text-blue-600">
        Ouvrir l'outil
        <ArrowRight size={16} className="group-hover:translate-x-0.5 transition-transform" />
      </span>
    </Link>
  )
}

export default function OutilsList() {
  useRouteMeta('/outils')
  return (
    <div className="py-12 px-4">
      <div className="max-w-5xl mx-auto">
        <header className="mb-10">
          <div className="flex items-center gap-2 text-blue-600 mb-2">
            <Wrench size={20} />
            <span className="text-sm font-semibold uppercase tracking-wide">Outils</span>
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-3">
            Des outils d'analyse, pas seulement des analyses
          </h1>
          <p className="text-xl text-gray-600">
            Des instruments statistiques à faire tourner sur les données publiques qu'on fournit,
            ou sur vos propres fichiers, directement dans votre navigateur.
          </p>
        </header>

        <div className="flex items-start gap-3 bg-emerald-50 border border-emerald-200 rounded-xl p-4 mb-10">
          <ShieldCheck className="text-emerald-600 shrink-0 mt-0.5" size={22} />
          <div className="text-sm text-emerald-900">
            Tous les calculs s'effectuent localement. Vos fichiers ne quittent jamais votre
            appareil, et chaque chiffre affiché cite sa source d'origine.
          </div>
        </div>

        <div className="space-y-12">
          {FAMILLES.map((f) => (
            <section key={f.id}>
              <div className="mb-4">
                <h2 className="text-sm font-semibold uppercase tracking-wide text-gray-400">{f.titre}</h2>
                <p className="text-gray-500 text-sm">{f.sous}</p>
              </div>
              <div className="grid sm:grid-cols-2 gap-6">
                {f.outils.map((o) => (
                  <OutilCard key={o.to} o={o} />
                ))}
              </div>
            </section>
          ))}
        </div>

        {/* Lien vers les terrains */}
        <div className="mt-12 text-center">
          <p className="text-gray-600 mb-2">
            Vous cherchez plutôt des études déjà faites sur données publiques ?
          </p>
          <Link
            to="/terrains"
            className="inline-flex items-center gap-1.5 text-sm font-medium text-emerald-600 hover:text-emerald-700"
          >
            Voir les dossiers <ArrowRight size={16} />
          </Link>
        </div>
      </div>
    </div>
  )
}
