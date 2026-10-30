/**
 * Terrains = populations étudiées (une par étude), analysées sous tous les angles.
 * À distinguer des THÈMES (dimensions) dans config/themes.js, qui comparent
 * UN angle à travers TOUS les terrains.
 *
 * `metrics` = chiffre-phare du terrain pour chaque dimension (sert à la
 * comparaison inter-terrains sur les pages thèmes).
 */
import { Landmark, Trophy, Building2, GraduationCap, DoorOpen, Car, TrendingUp, HeartPulse } from 'lucide-react'

export const TERRAINS = [
  {
    id: 'ecole',
    titre: "L'école",
    sousTitre: 'École · Collège · Lycée',
    description:
      "La ségrégation scolaire mesurée par l'IPS : qui cumule les trois étapes du côté défavorisé ou favorisé ?",
    icon: GraduationCap,
    color: '#8B5CF6',
    statut: 'disponible',
    to: '/terrains/ecole',
    angles: ['ecole', 'college', 'lycee'],
    metrics: {},
  },
  {
    id: 'elus',
    titre: 'Les élus',
    sousTitre: 'Municipales 2026',
    description:
      "888 000 candidats analysés : du candidat au maire, le filtre invisible du pouvoir local.",
    icon: Landmark,
    color: '#10B981',
    statut: 'disponible',
    to: '/terrains/elus',
    angles: ['diversite', 'genre', 'age'],
    metrics: { diversite: 4.4, genre: 48.7, age: 51 },
  },
  {
    id: 'selectivite',
    titre: 'La sélectivité',
    sousTitre: 'Parcoursup 2025',
    description:
      "14 000 formations au crible du taux d'accès : quelles disciplines ferment, où l'accès est le plus dur, et qui sont les admis boursiers.",
    icon: DoorOpen,
    color: '#0891B2',
    statut: 'disponible',
    to: '/terrains/selectivite',
    angles: [],
    metrics: {},
  },
  {
    id: 'assemblee',
    titre: "L'Assemblée",
    sousTitre: '17ᵉ législature',
    description:
      "577 députés et 2 060 collaborateurs au miroir de la France : profession, sexe, âge, diversité, groupe par groupe.",
    icon: Landmark,
    color: '#4F46E5',
    statut: 'disponible',
    to: '/terrains/assemblee',
    angles: ['diversite', 'genre', 'age'],
    metrics: { diversite: 4.2, genre: 37.8, age: 52 },
  },
  {
    id: 'auto-ecoles',
    titre: 'Les auto-écoles',
    sousTitre: 'Permis B · à contexte égal',
    description:
      "7 922 auto-écoles comparées à ce que leur contexte laisse attendre : le département de l'examen et la ville pèsent un tiers des écarts de réussite.",
    icon: Car,
    color: '#EA580C',
    statut: 'disponible',
    to: '/terrains/auto-ecoles',
    angles: [],
    metrics: {},
  },
  {
    id: 'revenus',
    titre: "Qui s'enrichit, qui décroche ?",
    sousTitre: 'Revenus des communes · 2014-2021',
    description:
      "La position de chaque ville dans la hiérarchie des niveaux de vie : la proche banlieue se gentrifie, la grande couronne recule.",
    icon: TrendingUp,
    color: '#0D9488',
    statut: 'disponible',
    to: '/terrains/revenus',
    angles: [],
    metrics: {},
  },
  {
    id: 'sport',
    titre: 'Le sport',
    sousTitre: 'Licences, clubs et équipements · 2023',
    description:
      "Le foot, sport des quartiers ? Les filles arrêtent plus tôt ? Qui manque de clubs, qui manque de licenciés ? Les idées reçues à l'épreuve des licences.",
    icon: Trophy,
    color: '#F59E0B',
    statut: 'disponible',
    to: '/terrains/sport',
    angles: [],
    metrics: {},
  },
  {
    id: 'pratiques',
    titre: 'Les modes de vie',
    sousTitre: 'Pratiques, corps, tabac · INCA 3 et Baromètre 2024',
    description:
      "La carte de nos pratiques, de la table au sport : ce qu'elles doivent à l'âge, au diplôme et à l'argent, et ce qu'elles disent de l'obésité, du tabac et du regard sur son corps.",
    icon: HeartPulse,
    color: '#DB2777',
    statut: 'disponible',
    to: '/terrains/pratiques',
    angles: [],
    metrics: {},
  },
  {
    id: 'entreprises',
    titre: 'Les entreprises',
    sousTitre: 'Dirigeants',
    description: "Diversité et parité au sommet des entreprises françaises.",
    icon: Building2,
    color: '#3B82F6',
    statut: 'a-venir',
    angles: ['diversite', 'genre'],
    metrics: {},
  },
]

export const TERRAIN_BY_ID = Object.fromEntries(TERRAINS.map((t) => [t.id, t]))
