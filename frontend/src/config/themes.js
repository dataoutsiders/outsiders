/**
 * Thèmes = dimensions d'inégalité (un angle), comparées À TRAVERS les terrains.
 * À distinguer des TERRAINS (populations) dans config/terrains.js.
 *
 * Chaque dimension est mesurée par les outils onomastiques :
 *   diversité (IDP), genre (féminisation), âge (structure d'âge).
 */
import { Globe, Users, Cake } from 'lucide-react'

export const THEMES = [
  {
    id: 'diversite',
    titre: 'Diversité',
    unite: '% IDP',
    sens: 'haut', // une valeur haute = plus de diversité
    reference: '7 % en population',
    description:
      "La diversité patronymique : part des noms apparus en France après 1950 (indice IDP).",
    icon: Globe,
    color: '#10B981',
  },
  {
    id: 'genre',
    titre: 'Genre',
    unite: '% de femmes',
    sens: 'parite', // référence = 50 %
    reference: 'parité 50 %',
    description: "La place des femmes, mesurée par le taux de féminisation.",
    icon: Users,
    color: '#8B5CF6',
  },
  {
    id: 'age',
    titre: 'Âge',
    unite: 'âge médian',
    sens: 'bas', // une valeur basse = population plus jeune
    reference: '~42 ans en population adulte',
    description: "La structure d'âge : l'accès des plus jeunes aux positions.",
    icon: Cake,
    color: '#F59E0B',
  },
]

export const THEME_BY_ID = Object.fromEntries(THEMES.map((t) => [t.id, t]))
