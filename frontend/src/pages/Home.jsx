import { useRef, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import {
  ArrowRight, ArrowUpRight, Map as MapIcon, Building2, Layers3, Globe,
  ShieldCheck, Wrench,
} from 'lucide-react'
import { TERRAINS } from '../config/terrains'
import TerritoireSearch from '../components/TerritoireSearch'
import { ficheHref } from '../lib/territoire'
import { useRouteMeta } from '../lib/meta'
import NewsletterForm from '../components/NewsletterForm'
import { trackEvent } from '../lib/analytics'

/**
 * Les cartes « vrai ou faux » : une idée reçue, un verdict, un chiffre, sa source.
 * RÈGLES : chaque chiffre reflète exactement ce qu'affiche la vue d'atterrissage
 * (le CTA doit permettre de refaire le raisonnement), et cite sa source d'origine.
 */
export const VERDICTS = {
  faux: { label: 'Faux', couleur: '#DC2626' },
  pasPartout: { label: 'Pas partout', couleur: '#D97706' },
  vraiMais: { label: 'Vrai, mais', couleur: '#0891B2' },
}

export const QUESTIONS = [
  {
    id: 'segregation',
    kicker: 'Niveau de vie',
    unite: 'Villes',
    question: 'Riches et pauvres vivent-ils séparés ?',
    verdict: 'pasPartout',
    chiffre: '× 1,6',
    chiffreLabel: 'dans la ville type, le niveau de vie de ses îlots les plus aisés rapporté à celui des plus modestes',
    couleur: '#14B8A6',
    texte:
      "L'écart varie beaucoup d'une ville à l'autre : la page classe les 997 villes de plus de 10 000 habitants de la plus séparée à la plus mélangée, un classement relatif et non un seuil absolu. Paris figure à la fois parmi les villes dont les quartiers diffèrent le plus et parmi celles où chaque quartier (IRIS, environ 2 000 habitants) mêle le plus des revenus très différents.",
    source: {
      label: 'Insee, FiLoSoFi 2021 (carreaux de 200 m et IRIS)',
      url: 'https://www.insee.fr/fr/statistiques/8735243',
    },
    cta: { label: "Voir l'analyse nationale", to: '/segregation' },
  },
  {
    id: 'revenus',
    kicker: 'Niveau de vie',
    unite: 'Communes',
    question: 'La banlieue décroche ?',
    verdict: 'pasPartout',
    chiffre: '85 %',
    chiffreLabel: 'des habitants de la grande couronne vivent dans une commune qui a reculé',
    couleur: '#0D9488',
    texte:
      "De 2014 à 2021, les communes limitrophes de Paris montent dans la hiérarchie des revenus (Clichy, Saint-Ouen, Romainville, Montreuil) pendant que la grande couronne pavillonnaire recule, souvent de peu. Le contrôle sur 2023 confirme le mouvement. Une position relative : presque partout, les revenus augmentent en euros.",
    source: {
      label: 'Insee, Filosofi 2014 et 2021 (contrôle sur 2023)',
      url: 'https://www.insee.fr/fr/statistiques/7756729',
    },
    cta: { label: 'Qui monte, qui recule ?', to: '/terrains/revenus' },
  },
  {
    id: 'sport',
    kicker: 'Sport',
    unite: 'Quartiers',
    question: 'Le foot, sport des quartiers ?',
    verdict: 'vraiMais',
    chiffre: '35 %',
    chiffreLabel: 'des licences des quartiers prioritaires sont du foot, contre 15 % dans le reste de la commune',
    couleur: '#F59E0B',
    texte:
      "Par habitant, le foot n'y est que 1,4 fois plus fréquent : sa place tient surtout à la moindre pratique en club des autres sports. Et les terrains y sont rares : on compte près de trois fois plus de licenciés résidents par terrain de quartier qu'ailleurs.",
    source: {
      label: 'INJEP, licences et clubs 2023 ; Data ES',
      url: 'https://www.data.gouv.fr/datasets/donnees-geocodees-issues-du-recensement-des-licences-et-clubs-aupres-des-federations-sportives-agreees-par-le-ministere-charge-des-sports',
    },
    cta: { label: 'Les idées reçues sur le sport', to: '/terrains/sport' },
  },
  {
    id: 'elus',
    kicker: 'Représentation politique',
    unite: 'Élus',
    question: 'La politique locale se diversifie ?',
    verdict: 'vraiMais',
    chiffre: '2,6 → 3,2 %',
    chiffreLabel: 'de noms classés « diversité » (indice IDP) parmi les conseillers élus au premier tour, de 2020 à 2026, dans les mêmes communes',
    couleur: '#EC4899',
    texte:
      "La hausse se retrouve chez les candidats (5,4 % puis 6,2 %) et les têtes de liste (2,5 % puis 3,3 %), mais elle est lente et reste loin des 7 % de la population. La diversité se perd surtout au choix de qui conduit la liste : 2 % des têtes de liste portent un tel nom, contre 3 % de leurs colistiers. Indicateur de groupe calculé sur les noms, pas une origine.",
    source: {
      label: 'Municipales 2020 et 2026, candidats et élus du premier tour (data.gouv.fr)',
      url: 'https://www.data.gouv.fr/datasets/elections-municipales-2026-resultats-du-premier-tour',
    },
    cta: { label: 'Voir 2020 et 2026 côte à côte', to: '/terrains/elus' },
  },
  {
    id: 'assemblee',
    kicker: 'Représentation politique',
    unite: 'Députés',
    question: 'Les députés ressemblent aux Français ?',
    verdict: 'faux',
    chiffre: '6 / 577',
    chiffreLabel: 'députés ouvriers, quand les ouvriers sont 18,6 % des personnes en emploi',
    couleur: '#4F46E5',
    texte:
      "66 % des députés se déclarent cadres ou professions intellectuelles supérieures (22 % des personnes en emploi). Côté noms, 4,2 % des députés portent un nom classé « diversité » (indice IDP), contre 6,4 % de leurs collaborateurs et 7 % de la population : un écart à confirmer, sur une vingtaine de députés.",
    source: {
      label: 'Open data Assemblée nationale · INSEE',
      url: 'https://data.assemblee-nationale.fr/acteurs/deputes-en-exercice',
    },
    cta: { label: "Ouvrir le dossier Assemblée", to: '/terrains/assemblee' },
  },
  {
    id: 'etat-enfants',
    kicker: 'État-providence',
    unite: 'Pays',
    question: 'Beaucoup de dépense publique, des enfants mieux protégés ?',
    verdict: 'faux',
    chiffre: '27,5 %',
    chiffreLabel: "des moins de 18 ans menacés de pauvreté ou d'exclusion, dans l'un des deux pays qui dépensent le plus d'Europe",
    couleur: '#3B82F6',
    texte:
      "57,3 % du PIB de dépenses publiques en 2025, au 2e rang des 30 pays comparés, derrière la Finlande (57,5 %). Et pourtant plus d'un enfant sur quatre est menacé de pauvreté ou d'exclusion, plus que la moyenne européenne (24,3 %) : seuls 4 des 28 pays disponibles font pire. Ce contraste ne dit pas à lui seul ce que vaut la dépense, qui finance d'abord les retraites et la santé.",
    source: {
      label: 'Eurostat, dépenses publiques et AROPE moins de 18 ans (2025)',
      url: 'https://ec.europa.eu/eurostat/databrowser/view/ilc_peps01n/default/table?lang=fr',
    },
    cta: { label: 'Ouvrir le dossier France en Europe', to: '/international' },
  },
  {
    id: 'pisa',
    kicker: 'École',
    unite: 'Pays',
    question: 'La France décroche dans PISA ?',
    verdict: 'vraiMais',
    chiffre: '−53 / −33',
    chiffreLabel: "points en maths de 2003 à 2025 : la France, puis la moyenne des 23 pays de l'OCDE présents depuis le début",
    couleur: '#6366F1',
    texte:
      "La France baisse significativement plus que ces pays, en maths comme en lecture, et l'écart s'est creusé depuis 2018. Mais en 2025 son score ne se distingue pas significativement de la moyenne de l'OCDE, il correspond à ce que laissent attendre sa richesse et le profil social de ses élèves, et une partie de la chute au classement tient à l'arrivée de nouveaux participants.",
    source: {
      label: 'OCDE, PISA 2025 Results (Volume I), tableaux de tendance',
      url: 'https://stat.link/mrq53f',
    },
    cta: { label: 'Ouvrir le dossier PISA', to: '/international/pisa' },
  },
  {
    id: 'age',
    kicker: 'Information',
    unite: 'Âge',
    question: "Les jeunes ne s'informent plus ?",
    verdict: 'faux',
    chiffre: '96 %',
    chiffreLabel: "des 18-24 ans s'informent au moins une fois par mois, 90 % chaque jour",
    couleur: '#F97316',
    texte:
      "Ils ont quitté le journal télévisé, pas l'information : 41 % s'informent chaque jour par la télévision, contre 89 % des 70 ans et plus, et pour 77 % d'entre eux le numérique (réseaux, sites, applis, mais aussi télévision et radio suivies sur écran) est devenu le premier moyen de s'informer.",
    source: {
      label: 'Arcom, Les Français et l\'information (2024)',
      url: 'https://www.arcom.fr/se-documenter/etudes-et-donnees/etudes-bilans-et-rapports-de-larcom/les-francais-et-linformation',
    },
    cta: { label: 'Comparer les générations', to: '/explorer/age' },
  },
  {
    id: 'selectivite',
    kicker: 'Enseignement supérieur',
    unite: 'Formations',
    question: "La prépa, la formation la plus difficile d'accès ?",
    verdict: 'faux',
    chiffre: '4 %',
    chiffreLabel: "de taux d'accès médian dans les formations au BPJEPS (sport), le plus bas de Parcoursup",
    couleur: '#0891B2',
    texte:
      "Le sport, les instituts d'études politiques (10 %) et les arts appliqués (23 %) donnent moins de propositions à leurs candidats que la prépa scientifique (41 %). Le taux d'accès dit combien de candidats reçoivent une proposition, pas le niveau demandé. Et la licence n'accueille plus tous ses candidats partout : seules 33 % en acceptent la totalité, 20 % en Île-de-France, faute de places plus que par sélection.",
    source: {
      label: 'MESR, Parcoursup 2025',
      url: 'https://data.enseignementsup-recherche.gouv.fr/explore/dataset/fr-esr-parcoursup/',
    },
    cta: { label: 'Ouvrir le dossier Sélectivité', to: '/terrains/selectivite' },
  },
  {
    id: 'auto-ecoles',
    kicker: 'Permis de conduire',
    unite: 'Auto-écoles',
    question: 'Le meilleur taux de réussite fait la meilleure auto-école ?',
    verdict: 'faux',
    chiffre: '44 %',
    chiffreLabel: 'des auto-écoles changent de quart de classement une fois leur contexte pris en compte',
    couleur: '#EA580C',
    texte:
      "Le taux publié dépend pour un quart du département de l'examen (de 36 % en Guadeloupe à 73 % en Haute-Loire) et aussi de la ville : à département égal, une commune dix fois plus peuplée va avec 2,7 points de moins. Comparée à ce que son contexte laisse attendre, près d'une école sur deux change de quart de classement.",
    source: {
      label: 'Sécurité routière, taux de réussite des auto-écoles (fichier du 19 février 2026, data.gouv.fr)',
      url: 'https://www.data.gouv.fr/fr/datasets/liste-des-auto-ecoles-et-taux-de-reussite-au-permis-de-conduire/',
    },
    cta: { label: 'Comparer à contexte égal', to: '/terrains/auto-ecoles' },
  },
  {
    id: 'ecole',
    kicker: 'École',
    unite: 'Établissements',
    question: 'Public, privé : les mêmes élèves ?',
    verdict: 'faux',
    chiffre: '88 → 122',
    chiffreLabel: 'indice de position sociale moyen des collèges publics et privés de Seine-Saint-Denis (rentrée 2025)',
    couleur: '#8B5CF6',
    texte:
      "Dans le département le plus défavorisé de métropole, les collèges privés accueillent un public plus favorisé que la moyenne des collèges publics de Paris (115). C'est l'écart entre public et privé le plus grand de métropole : 34 points.",
    source: {
      label: 'Éducation nationale, IPS des collèges (rentrée 2025)',
      url: 'https://www.education.gouv.fr/depp/l-indice-de-position-sociale-ips-357755',
    },
    cta: { label: 'Ouvrir le dossier École', to: '/terrains/ecole' },
  },
  {
    id: 'esperance',
    kicker: 'Santé',
    unite: 'Milieu social',
    question: 'Face à la santé, tous égaux ?',
    verdict: 'faux',
    chiffre: '+5,3 ans',
    chiffreLabel: "d'espérance de vie pour un homme cadre de 35 ans, comparé à un ouvrier",
    couleur: '#EF4444',
    texte:
      "À 35 ans, un homme cadre peut espérer vivre encore 48,9 ans, un ouvrier 43,6. Chez les femmes, l'écart est de 3,4 ans. Le milieu social se lit jusque dans les tables de mortalité.",
    source: {
      label: 'Insee, mortalité par catégorie sociale 2020-2022',
      url: 'https://www.insee.fr/fr/statistiques/2383438',
    },
    cta: { label: 'Comparer les milieux sociaux', to: '/explorer/milieu-social' },
  },
  {
    id: 'sante-paradoxe',
    kicker: 'Santé',
    unite: 'Pays',
    question: 'La France, bon élève de la santé en Europe ?',
    verdict: 'vraiMais',
    chiffre: '24e / 30',
    chiffreLabel: 'pour la mortalité infantile : 4,1 ‰, au-dessus de la moyenne européenne (3,5)',
    couleur: '#0EA5E9',
    texte:
      "L'espérance de vie française reste dans le haut du classement (83,0 ans, 9e sur 30). Mais la mortalité infantile, meilleure que la moyenne européenne jusqu'en 2014, est passée au-dessus : seuls 6 pays européens font pire. Les comparaisons dépendent en partie de la façon dont chaque pays enregistre les naissances très prématurées.",
    source: {
      label: 'Eurostat, mortalité infantile et espérance de vie (2024)',
      url: 'https://ec.europa.eu/eurostat/databrowser/view/demo_minfind/default/table?lang=fr',
    },
    cta: { label: 'Voir la trajectoire du décrochage', to: '/international' },
  },
  {
    id: 'sexe',
    kicker: 'Travail',
    unite: 'Genre',
    question: "L'égalité femmes-hommes, c'est réglé ?",
    verdict: 'faux',
    chiffre: '−39 %',
    chiffreLabel: 'de pension de droit direct pour les femmes de 65 ans ou plus (981 € nets contre 1 600 €, en 2019)',
    couleur: '#EC4899',
    texte:
      "L'écart de salaire (13 % en équivalent temps plein) paraît se réduire ; le temps partiel et les carrières interrompues contribuent à le creuser au moment de la retraite. Les pensions de réversion ramènent l'écart sur la pension totale à 24 %.",
    source: {
      label: "Insee, Femmes et hommes, l'égalité en question (édition 2022, données 2019)",
      url: 'https://www.insee.fr/fr/statistiques/6047747',
    },
    cta: { label: 'Voir tous les écarts', to: '/explorer/sexe' },
  },
  {
    id: 'hlm',
    kicker: 'Logement',
    unite: 'Départements',
    question: 'Les HLM sont là où la France est pauvre ?',
    verdict: 'pasPartout',
    chiffre: '24 % vs 8 %',
    chiffreLabel: 'de logements HLM dans les Hauts-de-Seine, département parmi les plus riches, contre la Creuse',
    couleur: '#0D9488',
    texte:
      "Le logement social suit d'abord la ville : les départements urbains en comptent le plus, qu'ils soient aisés comme les Hauts-de-Seine ou modestes comme la Seine-Saint-Denis (31 %). C'est à l'intérieur de chaque département que les HLM se concentrent dans les communes modestes. La relation change selon l'échelle, un piège classique des moyennes territoriales.",
    source: {
      label: 'INSEE, recensement 2023 (logement)',
      url: 'https://www.insee.fr/fr/statistiques/8997194',
    },
    cta: { label: 'Voir le croisement sur la carte', to: '/atlas?i=hlm&vs=revenu' },
  },
  {
    id: 'outsiders',
    kicker: 'Reproduction sociale',
    unite: 'Départements',
    question: 'Les lycées des territoires modestes font moins bien que prévu ?',
    verdict: 'faux',
    chiffre: '8 sur 22',
    chiffreLabel: 'départements défavorisés aux trois étapes où les lycées font mieux que prévu au bac, autant que chez les favorisés (8 sur 25)',
    couleur: '#10B981',
    texte:
      "La valeur ajoutée compare la réussite au bac à ce que laisse attendre le profil des élèves. Elle ne suit ni le revenu du territoire, ni les prix de l'immobilier : le lycée qui fait progresser n'est pas forcément là où on l'attend. Les écarts restent souvent faibles, de l'ordre d'un point.",
    source: {
      label: 'Éducation nationale, IVAL et IPS (data.gouv.fr)',
      url: 'https://www.data.gouv.fr/datasets/indicateurs-de-valeur-ajoutee-des-lycees-denseignement-general-et-technologique-2',
    },
    cta: { label: 'Comparer les départements', to: '/terrains/ecole' },
  },
]

// Les outils, présentés par ce qu'ils permettent de faire (pas par leur origine).
const OUTILS = [
  {
    to: '/atlas',
    icon: MapIcon,
    color: '#3B82F6',
    verbe: 'Repérer',
    titre: 'La carte des outsiders',
    texte:
      "Croisez deux indicateurs sur la carte de France : une droite de pronostic apparaît, et avec elle les territoires qui la démentent, au-dessus comme en dessous. Du département à la commune.",
    tag: 'données publiques',
  },
  {
    to: '/territoires',
    icon: Building2,
    color: '#0EA5E9',
    verbe: 'Situer',
    titre: 'La fiche territoire',
    texte:
      "Une commune ou un département : ce qui le rend inhabituel, son jumeau statistique (le territoire qui lui ressemble le plus) et tous ses indicateurs situés par rapport à la France.",
    tag: 'données publiques',
  },
  {
    to: '/explorer/milieu-social',
    icon: Layers3,
    color: '#F59E0B',
    verbe: 'Comparer',
    titre: 'Les comparateurs : groupes et pays',
    texte:
      "Milieu social, sexe, âge, et désormais 30 pays européens (où se situe la France ?) : les mêmes indicateurs, les mêmes sources officielles, pour mesurer les écarts au lieu de les supposer.",
    tag: 'données publiques',
  },
  {
    to: '/outils/representativite',
    icon: Globe,
    color: '#10B981',
    verbe: 'Auditer',
    titre: 'Le test de représentativité',
    texte:
      "Déposez une liste de noms (élus, salariés, adhérents…) : diversité, parité et âge estimés en agrégé, entièrement dans votre navigateur. Rien n'est envoyé.",
    tag: 'vos fichiers',
  },
]

function Stamp({ verdict }) {
  const v = VERDICTS[verdict]
  return (
    <span
      className="shrink-0 -rotate-3 select-none border-2 rounded-md px-2 py-0.5 text-xs font-black uppercase tracking-widest"
      style={{ borderColor: v.couleur, color: v.couleur }}
    >
      {v.label}
    </span>
  )
}

function QuestionCard({ q }) {
  return (
    <article className="relative flex flex-col h-full bg-white border border-gray-200 rounded-2xl p-4 sm:p-6 shadow-sm hover:shadow-md hover:border-gray-300 transition-all">
      <div className="absolute top-4 right-4 sm:top-6 sm:right-6">
        <Stamp verdict={q.verdict} />
      </div>
      <div className="flex items-center gap-2 flex-wrap pr-24 mb-3 min-h-[1.5rem]">
        <span className="text-xs font-semibold uppercase tracking-wide text-gray-400">{q.kicker}</span>
        {q.unite && (
          <span
            className="text-[10px] font-semibold uppercase tracking-wide px-1.5 py-0.5 rounded-full"
            style={{ backgroundColor: `${q.couleur}18`, color: q.couleur }}
            title="Unité d'analyse"
          >
            {q.unite}
          </span>
        )}
      </div>
      <h3 className="text-lg sm:text-xl font-bold text-gray-900 leading-snug mb-2 sm:mb-4">{q.question}</h3>
      <div className="mb-1.5 sm:mb-3">
        <span className="text-[1.75rem] sm:text-4xl font-black tracking-tight" style={{ color: q.couleur }}>
          {q.chiffre}
        </span>
        <span className="block text-xs sm:text-sm text-gray-500 mt-1">{q.chiffreLabel}</span>
      </div>
      <p className="text-sm text-gray-600 leading-relaxed flex-1 line-clamp-2 sm:line-clamp-none">{q.texte}</p>
      <div className="flex items-center justify-between gap-3 mt-3 sm:mt-4 pt-1 sm:pt-3 border-t border-gray-100">
        <a
          href={q.source.url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-xs text-gray-400 hover:text-gray-600 underline decoration-gray-300 truncate"
          title={q.source.label}
        >
          {q.source.label}
        </a>
        <Link
          to={q.cta.to}
          onClick={() => trackEvent(`accueil-carte/${q.id}`, 'Accueil : carte cliquée')}
          className="inline-flex items-center gap-1 shrink-0 min-h-[44px] text-sm font-medium hover:underline"
          style={{ color: q.couleur }}
        >
          {q.cta.label} <ArrowRight size={15} />
        </Link>
      </div>
    </article>
  )
}

// Exemples de la recherche : une grande ville, un département, une région.
const EXEMPLES = [
  { label: 'Marseille', niveau: 'commune', code: '13055' },
  { label: 'Seine-Saint-Denis', niveau: 'dept', code: '93' },
  { label: 'Bretagne', niveau: 'region', code: '53' },
]

function CartesQuestions() {
  const piste = useRef(null)
  const [actif, setActif] = useState(0)
  // Carte visible dans le carrousel (téléphone) : position de défilement / largeur d'une carte.
  const surDefilement = () => {
    const el = piste.current
    if (!el || !el.firstElementChild) return
    const pas = el.firstElementChild.getBoundingClientRect().width + 12
    setActif(Math.min(QUESTIONS.length - 1, Math.round(el.scrollLeft / pas)))
  }
  return (
    <section className="pt-1 pb-10 sm:py-12 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="hidden sm:block mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">Vrai ou faux ?</h2>
          <p className="text-gray-600 max-w-2xl">
            Des idées qu'on entend partout, passées au banc d'essai des données ouvertes. Les verdicts sortent des
            chiffres cités, pas d'une opinion : cliquez pour refaire le raisonnement vous-même.
          </p>
        </div>
        {/* Téléphone : une carte entière et le bord de la suivante, on glisse. */}
        <div
          ref={piste}
          onScroll={surDefilement}
          className="sm:hidden -mx-4 px-4 flex gap-3 overflow-x-auto snap-x snap-mandatory sans-barre"
          aria-label="Idées reçues, faites glisser pour voir la suivante"
        >
          {QUESTIONS.map((q) => (
            <div key={q.id} className="w-[86%] shrink-0 snap-center">
              <QuestionCard q={q} />
            </div>
          ))}
        </div>
        <div className="sm:hidden flex items-center justify-between gap-3 mt-3 text-xs text-gray-500">
          <span>
            {actif + 1} / {QUESTIONS.length} · glissez →
          </span>
          <Link to="/fil" className="inline-flex items-center gap-1 min-h-[36px] font-medium text-blue-600">
            Tout voir en plein écran <ArrowRight size={14} />
          </Link>
        </div>
        {/* Tablette et ordinateur : la grille. */}
        <div className="hidden sm:grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {QUESTIONS.map((q) => (
            <QuestionCard key={q.id} q={q} />
          ))}
        </div>
        <div className="hidden sm:block text-center mt-6">
          <Link to="/fil" className="inline-flex items-center gap-1.5 text-sm font-medium text-blue-600 hover:underline">
            Les voir une par une, en plein écran <ArrowRight size={15} />
          </Link>
        </div>
      </div>
    </section>
  )
}

export default function Home() {
  const navigate = useNavigate()
  useRouteMeta('/')

  return (
    <div>
      {/* Haut de page : la promesse en deux lignes, puis tout de suite les cartes. Sur téléphone,
          une carte entière doit être visible sans faire défiler. */}
      <section
        className="relative pt-3 pb-2 sm:pt-16 sm:pb-8 px-4"
        style={{
          backgroundImage: 'radial-gradient(circle, #E5E7EB 1px, transparent 1px)',
          backgroundSize: '26px 26px',
        }}
      >
        <div className="relative max-w-3xl mx-auto text-center">
          <p className="hidden sm:block text-sm font-semibold uppercase tracking-widest text-blue-600 mb-4">
            Données ouvertes · France entière · du pays à la commune
          </p>
          <h1 className="text-[1.75rem] sm:text-4xl md:text-5xl font-bold text-gray-900 mb-2 sm:mb-5 leading-tight">
            Vous{' '}
            <span className="underline decoration-amber-400 decoration-4 underline-offset-4">croyez</span>{' '}
            connaître la{' '}
            <span className="whitespace-nowrap">France{' '}?</span>
          </h1>
          <p className="text-base sm:text-xl text-gray-600 leading-relaxed">
            <span className="sm:hidden">Les idées reçues face aux données publiques.</span>
            <span className="hidden sm:inline">
              Des idées reçues confrontées aux données publiques : chaque chiffre cite sa source, chaque verdict se
              rejoue en deux clics.
            </span>
          </p>
        </div>
      </section>

      {/* Vrai ou faux : carrousel sur téléphone, grille ailleurs */}
      <CartesQuestions />

      {/* Et chez vous ? */}
      <section className="py-10 sm:py-14 px-4 bg-gray-50 border-y border-gray-100">
        <div className="max-w-xl mx-auto">
          <h2 className="text-2xl font-bold text-gray-900 mb-1">Et chez vous ?</h2>
          <p className="text-sm text-gray-600 mb-4">
            Une commune, une intercommunalité, un département ou une région : ce qui le distingue, son jumeau
            statistique, et ce qu'en disent nos dossiers.
          </p>
          <TerritoireSearch
            placeholder="Votre commune, votre département…"
            onSelect={(code, niveau) => {
              trackEvent('accueil-recherche', 'Accueil : recherche de territoire')
              navigate(ficheHref(niveau, code))
            }}
          />
          <div className="flex flex-wrap items-center gap-2 mt-3 text-sm">
            <span className="text-gray-400">Par exemple :</span>
            {EXEMPLES.map((e) => (
              <Link
                key={e.label}
                to={ficheHref(e.niveau, e.code)}
                onClick={() => trackEvent('accueil-exemple', 'Accueil : exemple de territoire')}
                className="inline-flex items-center min-h-[36px] px-3 rounded-full bg-white border border-gray-200 text-gray-700 hover:border-blue-300 hover:text-blue-700"
              >
                {e.label}
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Les outils */}
      <section className="py-16 px-4 bg-gray-50">
        <div className="max-w-6xl mx-auto">
          <div className="mb-8">
            <div className="flex items-center gap-2 text-blue-600 mb-2">
              <Wrench size={18} />
              <span className="text-sm font-semibold uppercase tracking-wide">Les outils</span>
            </div>
            <h2 className="text-3xl font-bold text-gray-900 mb-2">
              Des outils, pas des articles
            </h2>
            <p className="text-gray-600 max-w-2xl">
              Quatre instruments pour enquêter vous-même, sur les données publiques qu'on fournit
              ou sur vos propres fichiers. Cartes et graphiques s'intègrent chez vous en un clic
              (code iframe fourni), avec leur source.
            </p>
          </div>
          <div className="grid sm:grid-cols-2 gap-6">
            {OUTILS.map((o) => {
              const Icon = o.icon
              return (
                <Link
                  key={o.to}
                  to={o.to}
                  className="group bg-white border border-gray-200 rounded-2xl p-7 shadow-sm hover:shadow-md hover:border-gray-300 transition-all"
                >
                  <div className="flex items-center justify-between mb-4">
                    <div className="p-3 rounded-lg inline-flex" style={{ backgroundColor: o.color + '20' }}>
                      <Icon size={24} style={{ color: o.color }} />
                    </div>
                    <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-500">
                      {o.tag}
                    </span>
                  </div>
                  <div className="text-xs font-semibold uppercase tracking-wide mb-1" style={{ color: o.color }}>
                    {o.verbe}
                  </div>
                  <h3 className="text-xl font-bold text-gray-900 mb-2">{o.titre}</h3>
                  <p className="text-gray-600 mb-4 text-sm leading-relaxed">{o.texte}</p>
                  <span className="inline-flex items-center gap-1.5 font-medium text-sm" style={{ color: o.color }}>
                    Ouvrir l'outil
                    <ArrowRight size={16} className="group-hover:translate-x-0.5 transition-transform" />
                  </span>
                </Link>
              )
            })}
          </div>
        </div>
      </section>

      {/* Les dossiers */}
      <section className="py-16 px-4">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-bold text-gray-900 mb-2 text-center">Les dossiers</h2>
          <p className="text-gray-600 text-center mb-10 max-w-2xl mx-auto">
            Quand une question mérite plus qu'une carte : une population passée au crible de tous
            les angles à la fois, sur données publiques.
          </p>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {TERRAINS.map((t) => {
              const Icon = t.icon
              const dispo = t.statut === 'disponible'
              const card = (
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg" style={{ backgroundColor: t.color + '20' }}>
                    <Icon size={20} style={{ color: t.color }} />
                  </div>
                  <div>
                    <div className="font-semibold text-gray-900">{t.titre}</div>
                    <div className="text-xs text-gray-500">{dispo ? t.sousTitre : 'Bientôt'}</div>
                  </div>
                </div>
              )
              return dispo ? (
                <Link key={t.id} to={t.to} className="bg-white p-4 rounded-lg border border-gray-200 hover:shadow-sm transition-all">
                  {card}
                </Link>
              ) : (
                <div key={t.id} className="bg-white/60 p-4 rounded-lg border border-dashed border-gray-200">
                  {card}
                </div>
              )
            })}
          </div>
        </div>
      </section>

      {/* Newsletter */}
      <section className="py-14 px-4">
        <div className="max-w-2xl mx-auto text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Ne ratez pas les prochains dossiers</h2>
          <p className="text-gray-600 mb-5">
            Un mail quand un dossier sort ou qu'une donnée publique est mise à jour, avec ce qu'elle change.
          </p>
          <div className="text-left">
            <NewsletterForm variante="large" />
          </div>
        </div>
      </section>

      {/* Méthode & confidentialité */}
      <section className="py-16 px-4 bg-gray-50">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-start gap-3 bg-emerald-50 border border-emerald-200 rounded-xl p-5 mb-8">
            <ShieldCheck className="text-emerald-600 shrink-0 mt-0.5" size={22} />
            <div className="text-sm text-emerald-900">
              <strong>Respect des données.</strong> Les outils traitent vos fichiers entièrement
              dans le navigateur, rien n'est envoyé. La méthode (indice de diversité patronymique,
              proxys onomastiques) est compatible avec le droit français : pas de statistiques
              ethniques. Chaque chiffre affiché cite sa source d'origine.
            </div>
          </div>
          <div className="text-center">
            <Link
              to="/methodologie"
              className="inline-flex items-center gap-2 text-blue-600 font-medium hover:text-blue-700 transition-colors"
            >
              Découvrir la méthodologie <ArrowUpRight size={16} />
            </Link>
          </div>
        </div>
      </section>
    </div>
  )
}
