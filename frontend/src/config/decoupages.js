/**
 * Découpages = l'unité d'analyse de l'explorateur (« ce qu'est une ligne »).
 *
 * Colonne vertébrale du projet : Découpage × Indicateur × Mode de lecture.
 * Deux découpages actifs : « territoire » (cas spécial, carte + fiche, pages /atlas et
 * /territoires) et « milieu social » (premier découpage non géographique, moteur générique
 * UnitView sur /explorer/:id). Genre et Génération suivront : voir docs/AJOUTER_UN_DECOUPAGE.md.
 *
 * À distinguer des THÈMES (config/themes.js, l'angle mesuré) et des TERRAINS
 * (config/terrains.js, une population étudiée sous tous les angles).
 */
import { MapPin, Users, Layers3, Cake, Globe, Map as MapIcon, FileText, LayoutDashboard } from 'lucide-react'

// Métadonnées des modes (libellé + icône), partagées. La ROUTE d'un mode dépend du
// découpage (chaque découpage porte ses `modeRoutes`).
export const MODE_META = {
  carte: { label: 'Carte', icon: MapIcon, aide: 'Un indicateur, toutes les unités.' },
  fiche: { label: 'Fiche', icon: FileText, aide: 'Une unité, tous les indicateurs.' },
  tableau: { label: 'Tableau de bord', icon: LayoutDashboard, aide: "La vue d'ensemble." },
}

// Format d'affichage des indicateurs des découpages non géographiques.
const eurAn = (v) => Math.round(v).toLocaleString('fr-FR') + ' €'
const pct = (v) => v.toLocaleString('fr-FR', { maximumFractionDigits: 1 }) + ' %'
const ans = (v) => v.toLocaleString('fr-FR', { maximumFractionDigits: 1 }) + ' ans'
const pmil = (v) => v.toLocaleString('fr-FR', { maximumFractionDigits: 1 }) + ' ‰'
const heures = (v) => v.toLocaleString('fr-FR', { maximumFractionDigits: 1 }) + ' h'
const indice = (v) => v.toLocaleString('fr-FR', { maximumFractionDigits: 1 })

export const DECOUPAGES = [
  {
    id: 'territoire',
    titre: 'Territoire',
    sousTitre: 'commune, département',
    icon: MapPin,
    statut: 'disponible',
    aCarte: true, // seul découpage géographique : le mode carte existe
    modes: ['carte', 'fiche', 'tableau'],
    modeRoutes: { carte: '/atlas', fiche: '/territoires', tableau: '/territoires' },
    route: '/atlas',
  },
  {
    id: 'milieu-social',
    titre: 'Milieu social',
    sousTitre: 'catégories sociales',
    icon: Layers3,
    statut: 'disponible',
    aCarte: false,
    modes: ['tableau', 'fiche'],
    modeRoutes: { tableau: '/explorer/milieu-social', fiche: '/explorer/milieu-social' },
    route: '/explorer/milieu-social',
    dataUrl: '/data/decoupages/milieu-social.json',
    rowLabel: 'catégorie',
    rowLabelPluriel: 'catégories',
    intro:
      "Cinq grandes catégories socioprofessionnelles, comparées sur le revenu, l'emploi, la santé, la participation et l'accès à l'information.",
    indicateurs: [
      { id: 'niveau_vie', label: 'Niveau de vie', theme: 'Revenu', unite: '€', fmt: eurAn, sens: 'haut', aide: 'Niveau de vie annuel moyen (revenu disponible du ménage par personne).' },
      { id: 'pauvrete', label: 'Taux de pauvreté', theme: 'Revenu', unite: '%', fmt: pct, sens: 'bas', aide: 'Part vivant sous le seuil de pauvreté (60 % du niveau de vie médian).' },
      { id: 'chomage', label: 'Chômage', theme: 'Emploi', unite: '%', fmt: pct, sens: 'bas', aide: 'Taux de chômage au sens du BIT. Non calculé pour les indépendants.' },
      { id: 'esperance_vie_h', label: 'Espérance de vie à 35 ans (hommes)', theme: 'Santé', unite: 'ans', fmt: ans, sens: 'haut', aide: "Années restant à vivre en moyenne à 35 ans, chez les hommes. Chez les femmes, l'écart cadres/ouvrières est plus faible (53,0 vs 49,6 ans)." },
      { id: 'abstention', label: 'Abstention systématique', theme: 'Participation', unite: '%', fmt: pct, sens: 'bas', aide: "Part des inscrits n'ayant voté à aucun tour aux élections de 2022." },
      { id: 'numerique', label: "S'informe d'abord en numérique", theme: 'Information', unite: '%', fmt: pct, sens: 'neutre', aide: "Parmi ceux qui s'informent, part dont le principal moyen d'information passe par un écran connecté : réseaux, sites, moteurs de recherche, mais aussi télévision, radio ou presse suivies sur smartphone ou ordinateur." },
    ],
  },
  {
    id: 'sexe',
    titre: 'Sexe',
    sousTitre: 'femmes, hommes',
    icon: Users,
    statut: 'disponible',
    aCarte: false,
    modes: ['tableau', 'fiche'],
    modeRoutes: { tableau: '/explorer/sexe', fiche: '/explorer/sexe' },
    route: '/explorer/sexe',
    dataUrl: '/data/decoupages/sexe.json',
    rowLabel: 'sexe',
    rowLabelPluriel: 'sexes',
    intro:
      "Femmes et hommes comparés sur le salaire, l'emploi, la retraite et l'espérance de vie : le panorama des inégalités de sexe.",
    indicateurs: [
      { id: 'salaire_eqtp', label: 'Salaire net (équivalent temps plein)', theme: 'Revenu', unite: '€', fmt: eurAn, sens: 'haut', aide: 'Salaire net mensuel moyen en équivalent temps plein, secteur privé (2024).' },
      { id: 'taux_emploi', label: "Taux d'emploi (15-64 ans)", theme: 'Emploi', unite: '%', fmt: pct, sens: 'haut', aide: 'Part des 15 à 64 ans en emploi.' },
      { id: 'temps_partiel', label: 'Temps partiel', theme: 'Emploi', unite: '%', fmt: pct, sens: 'bas', aide: "Part des salariés (hors apprentis) à temps partiel dans leur emploi principal. Les femmes y sont environ 3 fois plus souvent, en partie de façon subie." },
      { id: 'esperance_vie', label: 'Espérance de vie à la naissance', theme: 'Santé', unite: 'ans', fmt: ans, sens: 'haut', aide: "Années de vie attendues à la naissance (2025, données provisoires). Le seul indicateur où les femmes sont devant." },
      { id: 'pension', label: 'Pension de retraite (droit direct)', theme: 'Retraite', unite: '€', fmt: eurAn, sens: 'haut', aide: "Pension moyenne de droit direct, hors réversion (la pension de réversion réduit l'écart)." },
    ],
  },
  {
    id: 'age',
    titre: 'Âge',
    sousTitre: "classes d'âge",
    icon: Cake,
    statut: 'disponible',
    aCarte: false,
    modes: ['tableau', 'fiche'],
    modeRoutes: { tableau: '/explorer/age', fiche: '/explorer/age' },
    route: '/explorer/age',
    dataUrl: '/data/decoupages/age.json',
    rowLabel: "tranche d'âge",
    rowLabelPluriel: "tranches d'âge",
    intro:
      "Comment les Français s'informent selon l'âge : le clivage générationnel le plus marqué des données ouvertes (source Arcom 2024).",
    indicateurs: [
      { id: 's_informe', label: "S'informe régulièrement", theme: "S'informer", unite: '%', fmt: pct, sens: 'neutre', aide: "Utilise au moins un moyen d'information (télévision, radio, presse, sites, moteurs de recherche, réseaux sociaux, vidéo en ligne) au moins une fois par mois. Recalcul Outsiders sur la base Arcom." },
      { id: 's_informe_jour', label: "S'informe chaque jour", theme: "S'informer", unite: '%', fmt: pct, sens: 'neutre', aide: "Utilise au moins un moyen d'information au moins une fois par jour. Recalcul Outsiders sur la base Arcom." },
      { id: 'numerique', label: "S'informe d'abord en numérique", theme: "Mode d'information", unite: '%', fmt: pct, sens: 'neutre', aide: "Parmi ceux qui s'informent, part dont le principal moyen d'information passe par un écran connecté : réseaux, sites, moteurs de recherche, applis, mais aussi télévision, radio ou presse suivies sur smartphone ou ordinateur." },
      { id: 'via_tv', label: "S'informe chaque jour via la télévision", theme: 'Canaux', unite: '%', fmt: pct, sens: 'neutre', aide: "Regarde la télévision (en direct ou en replay) pour s'informer au moins une fois par jour." },
      { id: 'via_reseaux', label: "S'informe chaque jour via les réseaux sociaux", theme: 'Canaux', unite: '%', fmt: pct, sens: 'neutre', aide: "Consulte les réseaux sociaux pour s'informer au moins une fois par jour." },
      { id: 'tiktok', label: 'TikTok', theme: 'Plateformes', unite: '%', fmt: pct, sens: 'neutre', aide: "Parmi les utilisateurs de réseaux sociaux, part qui s'informe sur TikTok." },
      { id: 'instagram', label: 'Instagram', theme: 'Plateformes', unite: '%', fmt: pct, sens: 'neutre', aide: "Parmi les utilisateurs de réseaux sociaux, part qui s'informe sur Instagram." },
      { id: 'facebook', label: 'Facebook', theme: 'Plateformes', unite: '%', fmt: pct, sens: 'neutre', aide: "Parmi les utilisateurs de réseaux sociaux, part qui s'informe sur Facebook." },
    ],
  },
  {
    id: 'pays',
    titre: 'Pays',
    sousTitre: '30 pays européens',
    icon: Globe,
    statut: 'disponible',
    aCarte: false,
    modes: ['tableau', 'fiche'],
    modeRoutes: { tableau: '/explorer/pays', fiche: '/explorer/pays' },
    route: '/explorer/pays',
    dataUrl: '/data/decoupages/pays.json',
    rowLabel: 'pays',
    rowLabelPluriel: 'pays',
    intro:
      "Où se situe la France ? Trente pays européens comparés sur huit indicateurs : l'État, l'enfance, la santé, l'école, les inégalités, le travail. Sources Eurostat, millésimes 2024-2025.",
    // Mode classement : beaucoup de catégories -> pays en lignes, indicateurs en colonnes,
    // présélections calculées sur la position de la catégorie repère (la France).
    tableauClassement: true,
    categorieRepere: 'fr',
    referenceLabel: 'Moyenne UE27',
    indicateursDefaut: ['dep_publiques', 'pauvrete_enfants', 'esperance_vie', 'emploi_seniors'],
    indicateurs: [
      { id: 'dep_publiques', label: 'Dépenses publiques', court: 'Dépenses publiques', theme: "L'État et les enfants", unite: '% du PIB', fmt: pct, sens: 'neutre', aide: "Total des dépenses des administrations publiques (État, collectivités, sécurité sociale), en part du PIB. La France est au 2e rang européen, derrière la Finlande. 2025." },
      { id: 'pauvrete_enfants', label: "Enfants menacés de pauvreté ou d'exclusion", court: 'Pauvreté des enfants', theme: "L'État et les enfants", unite: '%', fmt: pct, sens: 'bas', aide: "Part des moins de 18 ans menacés de pauvreté ou d'exclusion sociale (AROPE : pauvreté monétaire, privation matérielle sévère ou très faible intensité d'emploi du ménage). 2025 (Islande et Suisse non disponibles)." },
      { id: 'esperance_vie', label: 'Espérance de vie à la naissance', court: 'Espérance de vie', theme: 'Santé', unite: 'ans', fmt: ans, sens: 'haut', aide: "Années de vie attendues à la naissance, deux sexes confondus. 2024." },
      { id: 'mortalite_infantile', label: 'Mortalité infantile', court: 'Mortalité infantile', theme: 'Santé', unite: '‰', fmt: pmil, sens: 'bas', aide: "Décès avant un an, pour 1000 naissances vivantes. La France, longtemps meilleure que la moyenne européenne, est passée au-dessus en 2015. Les comparaisons dépendent en partie de l'enregistrement des naissances très prématurées. 2024." },
      { id: 'decrochage', label: 'Décrochage scolaire (18-24 ans)', court: 'Décrochage scolaire', theme: 'École et inégalités', unite: '%', fmt: pct, sens: 'bas', aide: "Part des 18-24 ans sortis du système scolaire sans diplôme du second cycle et hors de toute formation. 2025 (Luxembourg non disponible)." },
      { id: 'gini', label: 'Inégalités de revenu (Gini)', court: 'Gini', theme: 'École et inégalités', unite: '', fmt: indice, sens: 'bas', aide: "Coefficient de Gini du revenu disponible : 0 = égalité parfaite, 100 = un seul ménage concentre tout. 2025 (Islande et Suisse non disponibles)." },
      { id: 'emploi_seniors', label: 'Emploi des 55-64 ans', court: 'Emploi 55-64 ans', theme: 'Travail', unite: '%', fmt: pct, sens: 'haut', aide: "Part des 55-64 ans en emploi. Un des points faibles français, sous la moyenne européenne. 2025." },
      { id: 'heures_tp', label: 'Heures hebdo des temps pleins', court: 'Heures temps plein', theme: 'Travail', unite: 'h', fmt: heures, sens: 'neutre', aide: "Heures effectivement travaillées par semaine dans l'emploi principal, par les temps pleins (salariés et indépendants). Ne compte ni le temps partiel ni les congés annuels : comparer des semaines, pas des années. 2025." },
    ],
  },
]

export const DECOUPAGE_BY_ID = Object.fromEntries(DECOUPAGES.map((d) => [d.id, d]))
