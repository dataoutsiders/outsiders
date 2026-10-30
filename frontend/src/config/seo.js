/**
 * Métadonnées de partage des routes statiques. Source unique pour :
 *  - le hook usePageMeta / useRouteMeta (titre + description au fil de la navigation),
 *  - scripts/prerender-meta.mjs (balises statiques écrites dans dist/ pour que chaque
 *    lien partagé ait son propre aperçu, le site étant une SPA sans rendu serveur).
 *
 * Règle : titre court (< 60 caractères), description concrète (< 160), pas de jargon maison.
 */
export const SITE_NAME = 'Outsiders'

/**
 * URL de production, utilisée pour construire les og:url / og:image absolus
 * (les robots sociaux exigent des URL absolues). Les scripts de build peuvent
 * la surcharger via la variable d'environnement SITE_URL.
 * NB : pas de process.env ici, ce fichier est aussi importé côté navigateur.
 */
export const SITE_URL = 'https://dataoutsiders.fr'

/** Nom de fichier de l'image de partage d'une route ('/atlas' -> 'atlas', '/' -> 'home'). */
export function ogSlug(path) {
  return path === '/' ? 'home' : path.replace(/^\//, '').replace(/\//g, '-')
}

export const ROUTES_META = {
  '/': {
    title: 'Outsiders : comprendre la France par ses angles morts',
    description:
      "Des idées reçues vérifiées aux données publiques, une carte des territoires qui défient leur pronostic, la fiche de votre commune et des outils d'analyse gratuits, dans le navigateur.",
  },
  '/atlas': {
    title: 'La carte des outsiders',
    description:
      'Croisez deux indicateurs sur la carte de France : la droite de pronostic apparaît, avec les territoires qui la démentent, du département à la commune.',
  },
  '/territoires': {
    title: 'Situer un territoire : atypies, jumeau statistique, indicateurs',
    description:
      "Cherchez une commune, une intercommunalité, un département ou une région : ce qui le rend inhabituel, son jumeau statistique, ce qu'en disent nos dossiers et tous ses indicateurs, sources citées.",
  },
  '/explorer/milieu-social': {
    title: 'Milieu social : revenus, santé, emploi comparés',
    description:
      "Cadres, professions intermédiaires, employés, ouvriers, indépendants : niveau de vie, pauvreté, chômage, espérance de vie, abstention. Sources Insee et Arcom.",
  },
  '/explorer/sexe': {
    title: 'Femmes et hommes : les écarts en chiffres',
    description:
      "Salaire, emploi, temps partiel, retraite, espérance de vie : les inégalités entre femmes et hommes mesurées par l'Insee, mises côte à côte.",
  },
  '/explorer/age': {
    title: "S'informer selon l'âge : le clivage générationnel",
    description:
      "96 % des 18-24 ans s'informent : numérique, télévision, réseaux sociaux, comment chaque génération s'informe, d'après l'enquête Arcom 2024.",
  },
  '/explorer/pays': {
    title: 'Le classement : 30 pays européens comparés',
    description:
      "Pays en lignes, indicateurs au choix, moyenne UE27 en repère : le tableau comparatif de la France et de ses 29 voisins. Chiffres Eurostat 2024-2025.",
  },
  '/terrains/selectivite': {
    title: 'Qui peut entrer ? La sélectivité de Parcoursup',
    description:
      "Le plus difficile d'accès n'est pas la prépa : BPJEPS 4 % d'accès médian, instituts d'études politiques 10 %. Seules 33 % des licences acceptent tous leurs candidats, et à filière égale l'accès dépend de l'académie. Données MESR 2025.",
  },
  '/terrains/assemblee': {
    title: "Qui représente qui ? L'Assemblée au miroir de la France",
    description:
      "66 % de cadres, 6 ouvriers sur 577 députés, et des collaborateurs plus divers que les élus : l'Assemblée nationale comparée à la France, groupe par groupe. Et qui vote avec qui, sujet par sujet. Open data AN et INSEE.",
  },
  '/terrains/sport': {
    title: 'Le sport, miroir des inégalités ?',
    description:
      "Le foot, sport des quartiers ? Les filles arrêtent plus tôt ? Les enfants aisés lâchent le sport pour l'école ? 13 millions de licences et l'offre de clubs et d'équipements pour vérifier.",
  },
  '/terrains/pratiques': {
    title: 'Manger, bouger, fumer : le poids du milieu social',
    description:
      "La carte de nos pratiques, de la table au sport, et la thèse de l'omnivore à l'épreuve. À âge, sexe et revenu égaux, le tabac et l'obésité suivent le diplôme ; à IMC égal, les femmes se jugent plus souvent trop grosses. Anses, Santé publique France, Assurance maladie.",
  },
  '/terrains/revenus': {
    title: "Qui s'enrichit, qui décroche ?",
    description:
      "De 2014 à 2021, les communes limitrophes de Paris montent dans la hiérarchie des revenus, la grande couronne pavillonnaire recule. Toutes les communes de 2 000 habitants et plus, avec le contrôle 2023.",
  },
  '/terrains/auto-ecoles': {
    title: 'Auto-écoles : le meilleur taux fait-il la meilleure école ?',
    description:
      "Le taux de réussite au permis dépend du département et de la ville : à contexte égal, 44 % des auto-écoles changent de quart de classement. Sécurité routière.",
  },
  '/international': {
    title: 'Où se situe la France ? Le dossier',
    description:
      "2e pour les dépenses publiques, plus d'un enfant sur quatre menacé de pauvreté, mortalité infantile déclassée : la France face à 29 voisins européens. Chiffres Eurostat.",
  },
  '/international/pisa': {
    title: 'PISA 2025 : la France décroche-t-elle ?',
    description:
      "Un score en baisse mais dans la moyenne de l'OCDE, un rang qui chute plus que le niveau, moins de très bons élèves en maths : la France dans PISA 2025.",
  },
  '/outils': {
    title: 'Les outils',
    description:
      "Des instruments d'analyse à faire tourner sur les données publiques ou sur vos propres fichiers, sans rien envoyer : carte, fiche territoire, comparateurs, représentativité.",
  },
  '/outils/representativite': {
    title: "Représentativité d'un fichier de noms",
    description:
      "Déposez une liste de noms : diversité patronymique (IDP), taux de féminisation et structure d'âge, calculés dans votre navigateur. Rien n'est envoyé.",
  },
  '/terrains': {
    title: 'Les terrains',
    description:
      "Une population passée au crible des données publiques : l'école, les élus, et bientôt le sport et les entreprises.",
  },
  '/terrains/elus': {
    title: 'La diversité des élus, du candidat au maire',
    description:
      "Municipales 2020-2026 : la diversité des noms progresse chez les élus, lentement (2,6 % à 3,2 %), et se perd surtout au choix des têtes de liste.",
  },
  '/terrains/ecole': {
    title: "L'école trie-t-elle ?",
    description:
      "Écoles, collèges, lycées : l'indice de position sociale révèle une ségrégation cumulative, et les lycées qui compensent. Données Éducation nationale.",
  },
  '/segregation': {
    title: 'Riches et pauvres vivent-ils séparés ?',
    description:
      "Dans votre ville, riches et pauvres se côtoient-ils ou s'évitent-ils ? Score de mixité des revenus et des âges, quartier par quartier. Données INSEE FiLoSoFi.",
  },
  '/themes': {
    title: 'Les thèmes',
    description: 'Un angle (diversité, genre, âge) comparé à travers tous les terrains.',
  },
  '/methodologie': {
    title: 'Méthodologie',
    description:
      "Sources ouvertes, écart au pronostic, résidus studentisés, jumeau statistique, indice de diversité patronymique : la méthode complète et ses limites.",
  },
  '/about': {
    title: 'À propos',
    description:
      "Pourquoi Outsiders : l'écart à l'attendu comme angle de lecture de la France, sur données publiques. Qui fait le projet, travailler avec nous, contact et licence.",
  },
  '/presse': {
    title: 'Presse et réutilisation',
    description:
      "Reprendre les chiffres, cartes et graphiques d'Outsiders : résultats vérifiés avec leur source, formule de citation, code d'intégration, images et contact.",
  },
  '/fil': {
    title: 'Vrai ou faux ? Les idées reçues face aux chiffres',
    description:
      'Les idées reçues sur la France, une par écran : un verdict, un chiffre sourcé, la preuve en un clic. À faire défiler et à partager.',
  },
  '/newsletter': {
    title: 'Newsletter',
    description:
      "Recevoir un mail quand un dossier d'Outsiders sort ou qu'une donnée publique est mise à jour. Pas plus d'un par mois, désinscription en un clic.",
  },
  '/mentions-legales': {
    title: 'Mentions légales',
    description: 'Éditeur, hébergeur, licence des contenus et données personnelles du site Outsiders.',
  },
}
