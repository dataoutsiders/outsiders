/**
 * Registre « Dans nos dossiers » de la fiche territoire.
 *
 * Chaque dossier qui publie des résultats par territoire déclare ici, échelle par échelle
 * (commune, epci, dept, region), le fichier à lire, la fonction qui en extrait la ligne du
 * territoire et la phrase à afficher. La fiche territoire ne lit que ce registre : un nouveau
 * dossier géographique s'inscrit ici (ou dans EXCLUSIONS, avec sa raison), sans quoi le test
 * src/lib/__tests__/dossiersTerritoires.test.js échoue.
 *
 * Garde-fous (impératifs) :
 *  - une échelle n'est déclarée que si la page du dossier montre déjà des résultats à cette
 *    échelle, avec les mêmes précautions (reprises dans `precaution`) ;
 *  - rien de l'encadré « L'élite » du dossier Sport (diversité des noms des sportifs), jamais ;
 *  - Élus : seulement les départements (la seule échelle que le dossier affiche en entier), avec
 *    la phrase de garde-fou du dossier, sans rang ni classement ;
 *  - aucun rang qui ne figure pas déjà dans le dossier ; décrire, ne pas juger.
 *
 * Contrat d'une échelle :
 *   fichier   : chemin sous /data/ (chargé à la demande, mis en cache ; < 1 Mo, sinon un extrait léger
 *               produit par python/tools/build_territoires_echelles.py)
 *   extraire  : (donnees, code, ctx) => ligne | null   (null = le dossier ne couvre pas ce territoire)
 *   phrase    : (ligne, ctx, donnees) => { texte, precaution? }
 *   lien      : (code) => adresse du dossier (territoire présélectionné quand le dossier le permet)
 * ctx = { nom, deps } : nom du territoire affiché, et départements membres (région).
 */
const fr = (v, d = 1) =>
  v == null ? 'n/d' : Number(v).toLocaleString('fr-FR', { minimumFractionDigits: 0, maximumFractionDigits: d })
const fr1 = (v) =>
  v == null ? 'n/d' : Number(v).toLocaleString('fr-FR', { minimumFractionDigits: 1, maximumFractionDigits: 1 })
const signe = (v) => `${v > 0 ? '+' : v < 0 ? '−' : ''}${fr(Math.abs(v))}`
// « 0,4 point », « 3,4 points » (accord en français : pluriel à partir de 2).
const pts = (v) => `${signe(v)} ${Math.abs(v) < 2 ? 'point' : 'points'}`
const ent = (v) => Math.round(v).toLocaleString('fr-FR')
// Rang centile en toutes lettres : 1er, 2e, ... (une position 0,3 se lit « 1er centile »).
const centile = (v) => {
  const n = Math.max(1, Math.round(v))
  return n === 1 ? '1er' : `${n}e`
}
// Nom de sport : en minuscules comme dans le dossier, sauf noms propres (fédérations multisports).
const sport = (s) => (/\s[A-ZÀ-Ý]/.test(s) ? s : s.toLowerCase())
const sansAccents = (s) =>
  String(s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/[^a-z]/g, '')

// Phrase de garde-fou du dossier Élus, reprise mot pour mot.
export const GARDE_FOU_IDP =
  "L'indice IDP est un indicateur de groupe calculé sur les noms : il ne dit rien d'une personne, et un nom n'est pas une origine."

export const DOSSIERS_TERRITOIRES = [
  // ───────────────────────── Revenus des communes, 2014-2021 ─────────────────────────
  {
    id: 'revenus',
    titre: 'Qui s’enrichit, qui décroche ?',
    route: '/terrains/revenus',
    source: 'Insee, Filosofi 2014, 2021 et 2023',
    sourceUrl: 'https://www.insee.fr/fr/statistiques/7756729',
    // Le fichier a aussi une clé `departements` : le dossier ne l'affiche pas, la fiche non plus.
    fichiers: ['showcases/evolution-revenus.json'],
    echelles: {
      commune: {
        fichier: 'showcases/evolution-revenus.json',
        // Paris, Lyon et Marseille figurent dans le dossier par arrondissements ; Paris entier y a
        // en plus son propre résultat (« Paris intra-muros », premier anneau du dossier).
        extraire: (d, code) => {
          if (code === '75056') {
            const a = d.anneaux.find((x) => x.nom === 'Paris')
            return a ? { anneau: a } : null
          }
          const row = d.villes.find((r) => r[0] === code)
          return row ? Object.fromEntries(d.colonnes_villes.map((c, i) => [c, row[i]])) : null
        },
        phrase: (v, { nom }) => {
          if (v.anneau)
            return {
              texte: `Paris intra-muros : de 2014 à 2021, la position de ses arrondissements dans la hiérarchie des niveaux de vie des communes a évolué en moyenne de ${pts(v.anneau.evolution)} (contrôle 2023 : ${pts(v.anneau.evolution_2023)}).`,
              precaution:
                "Moyenne pondérée par la population. Par construction, les gains des uns sont les pertes des autres : la mesure est une position relative, pas une évolution en euros.",
            }
          const dp = v.position_2021 - v.position_2014
          const d23 = v.position_2023 - v.position_2014
          const texte =
            Math.abs(dp) < 2
              ? `Dans la hiérarchie des niveaux de vie des communes, ${nom} a peu bougé de 2014 à 2021 : du ${centile(v.position_2014)} au ${centile(v.position_2021)} centile (contrôle 2023 : ${centile(v.position_2023)}).`
              : `Dans la hiérarchie des niveaux de vie des communes, ${nom} est passée du ${centile(v.position_2014)} au ${centile(v.position_2021)} centile de 2014 à 2021, soit ${pts(dp)} (contrôle 2023 : ${centile(v.position_2023)}).`
          const prudence =
            Math.sign(dp) === Math.sign(d23) || Math.abs(dp) < 1
              ? ''
              : " Le contrôle sur 2023 va dans l'autre sens : prudence, la méthode de l'Insee a changé entre 2021 et 2023."
          return {
            texte,
            precaution:
              "Position relative : part de la population des communes comparées qui vit dans une commune plus modeste. Une commune qui monte n'est pas forcément une commune dont les habitants s'enrichissent." +
              prudence,
          }
        },
        // Paris entier n'est pas une ligne du dossier (arrondissements) : lien simple.
        lien: (code) => (code === '75056' ? '/terrains/revenus' : `/terrains/revenus?ville=${code}`),
      },
      epci: {
        fichier: 'showcases/evolution-revenus.json',
        // La carte du dossier ne colore que les intercommunalités d'au moins 2 communes comparées.
        extraire: (d, code) => d.epci.find((e) => e.code === code && e.n >= 2) || null,
        phrase: (e) => ({
          texte: `De 2014 à 2021, la position de ses ${e.n} communes comparées dans la hiérarchie des niveaux de vie a évolué en moyenne de ${pts(e.evolution)} (moyenne pondérée par la population).`,
          precaution:
            "Par construction, les gains des uns sont les pertes des autres : la mesure est une position relative, pas une évolution en euros.",
        }),
        lien: () => '/terrains/revenus',
      },
    },
  },

  // ───────────────────────── Villes : ségrégation résidentielle ─────────────────────────
  {
    id: 'segregation',
    titre: 'Riches et pauvres vivent-ils séparés ?',
    route: '/segregation',
    source: 'Insee, FiLoSoFi 2021 (IRIS et carreaux de 200 m) ; Éducation nationale (IPS)',
    sourceUrl: 'https://www.insee.fr/fr/statistiques/8229323',
    fichiers: ['segregation/villes.json', 'segregation/departements.json'],
    echelles: {
      commune: {
        fichier: 'segregation/villes.json',
        extraire: (d, code) => d.villes.find((v) => v.code === code) || null,
        phrase: (v, ctx, d) => {
          const r = v.revenu
          let texte = `Ville au niveau de vie « ${r.niveau.toLowerCase()} », plus aisée que ${r.niveau_score} % des ${ent(d.villes.length)} villes étudiées. Entre ses quartiers, les plus aisés ont un niveau de vie ${fr1(r.p90_p10)} fois celui des plus modestes`
          texte += r.interne_rd != null ? ` ; dans le quartier type, l'écart entre les 10 % du haut et les 10 % du bas est de ${fr1(r.interne_rd)}.` : '.'
          if (r.typologie) texte += ` Typologie : ${r.typologie.toLowerCase()}.`
          const e = v.ecole
          if (e && e.ips_public != null && e.ips_prive != null)
            texte += ` IPS moyen des collèges : ${e.ips_public} dans le public, ${e.ips_prive} dans le privé.`
          return {
            texte,
            precaution:
              'Scores et typologie sont des rangs entre villes de plus de 10 000 habitants, pas des seuils absolus.',
          }
        },
        lien: (code) => `/segregation?ville=${code}`,
      },
      dept: {
        fichier: 'segregation/departements.json',
        extraire: (d, code) => d.departements.find((x) => x.dep === code && x.separation != null) || null,
        phrase: (x) => ({
          texte: `Écart de niveau de vie entre ses quartiers : ${x.separation} sur 100 (rang national parmi les départements, sur ${ent(x.n_iris)} quartiers IRIS).`,
          precaution:
            ['01', '74', '68'].includes(x.dep)
              ? 'Les zones frontalières (Pays de Gex, Bâle) ressortent surestimées : hauts revenus, mais pas forcément forte diversité sociale.'
              : 'Quartiers IRIS des communes de 5 000 habitants et plus.',
        }),
        lien: () => '/segregation',
      },
      region: {
        fichier: 'segregation/departements.json',
        // Même calcul que la vue « Régions » du dossier : rangs des départements pondérés par leur
        // nombre de quartiers. Le dossier regroupe l'outre-mer en une seule ligne : pas de valeur
        // pour une région d'outre-mer prise seule.
        extraire: (d, code, { deps, outreMer }) => {
          if (outreMer) return null
          const membres = d.departements.filter((x) => deps.includes(x.dep) && x.separation != null)
          const w = membres.reduce((a, x) => a + x.n_iris, 0)
          if (!w) return null
          return { sep: Math.round(membres.reduce((a, x) => a + x.separation * x.n_iris, 0) / w), n_iris: w }
        },
        phrase: (x) => ({
          texte: `Écart de niveau de vie entre les quartiers : ${x.sep} sur 100 (rangs nationaux de ses départements, pondérés par leurs ${ent(x.n_iris)} quartiers IRIS, comme dans le dossier).`,
          precaution: 'Quartiers IRIS des communes de 5 000 habitants et plus.',
        }),
        lien: () => '/segregation',
      },
    },
  },

  // ───────────────────────── École ─────────────────────────
  {
    id: 'ecole',
    titre: "L'école trie-t-elle ?",
    route: '/terrains/ecole',
    source: 'Éducation nationale, IPS et IVAL',
    sourceUrl: 'https://www.education.gouv.fr/depp/l-indice-de-position-sociale-ips-357755',
    // La clé `epci` du fichier alimente le socle de la fiche (atlas/epci.json) ; le dossier ne
    // montre que les départements.
    fichiers: ['showcases/ecole-ips.json'],
    echelles: {
      dept: {
        fichier: 'showcases/ecole-ips.json',
        extraire: (d, code) => d.departements.find((x) => x.code === code) || null,
        phrase: (x, ctx, d) => {
          const a = d.annees
          let texte =
            x.cumul === 'triple-bas'
              ? "Public modeste aux trois étapes : l'IPS moyen des écoles, des collèges et des lycées publics est dans le tiers le plus bas des départements."
              : x.cumul === 'triple-haut'
                ? "Entre-soi cumulé : l'IPS moyen des écoles, des collèges et des lycées publics est dans le tiers le plus haut des départements."
                : "Ni dans le tiers le plus modeste, ni dans le tiers le plus favorisé aux trois étapes à la fois (IPS des écoles, collèges et lycées publics)."
          if (x.va_lycee != null) texte += ` Valeur ajoutée moyenne des lycées : ${signe(x.va_lycee)}.`
          return {
            texte,
            precaution: `IPS : milieu social moyen des élèves (écoles ${a.ecole}, collèges et lycées ${a.college}). Valeur ajoutée : réussite au bac au-delà, ou en deçà, de ce que le profil des élèves laissait attendre.`,
          }
        },
        lien: () => '/terrains/ecole',
      },
    },
  },

  // ───────────────────────── Élus : diversité des candidats ─────────────────────────
  {
    id: 'elus',
    titre: 'La diversité des élus, du candidat au maire',
    route: '/terrains/elus',
    source: 'Candidatures municipales 2026 (data.gouv.fr), indice IDP',
    sourceUrl: 'https://www.data.gouv.fr/datasets/elections-municipales-2026-listes-candidates-au-premier-tour',
    // Communes : le dossier ne montre que les extrêmes (un classement), pas chaque commune.
    // Intercommunalités : présentes dans le fichier (`epci`), affichées nulle part dans le dossier.
    fichiers: ['showcases/elus-diversite.json'],
    echelles: {
      dept: {
        fichier: 'showcases/elus-diversite.json',
        extraire: (d, code) => d.departements.find((x) => x.code === code) || null,
        phrase: (x, ctx, d) => ({
          texte: `Parmi les candidats aux élections municipales de 2026, ${fr(x.idp)} % portent un nom classé « diversité » (France : ${fr(d.national.idp)} %).`,
          precaution:
            GARDE_FOU_IDP +
            (x.code.length === 3
              ? " Outre-mer : l'IDP capte les migrations postérieures à 1950, pas toute la diversité (noms inscrits à l'état civil avant 1950)."
              : ''),
        }),
        lien: () => '/terrains/elus',
      },
    },
  },

  // ───────────────────────── Sport ─────────────────────────
  {
    id: 'sport',
    titre: 'Le sport, miroir des inégalités ?',
    route: '/terrains/sport',
    source: 'INJEP-MEDES, recensement des licences sportives',
    sourceUrl:
      'https://www.data.gouv.fr/datasets/donnees-geocodees-issues-du-recensement-des-licences-et-clubs-aupres-des-federations-sportives-agreees-par-le-ministere-charge-des-sports',
    // Rien de l'encadré « L'élite » (elite_noms, elite_zones) : jamais par territoire.
    fichiers: ['showcases/sport.json'],
    echelles: {
      dept: {
        fichier: 'showcases/sport.json',
        extraire: (d, code) => d.departements.find((x) => x.code === code) || null,
        phrase: (x, ctx, d) => {
          let texte = `${fr(x.licences_pour_1000)} licences sportives pour 1 000 habitants en ${d.millesime}.`
          const memeSport = x.signature && x.signature === x.premier
          if (memeSport && x.signature_indice != null)
            texte += ` Sport n° 1 et sport « signature » : ${sport(x.premier)} (${fr(x.premier_pour_1000)} licences pour 1 000 hab., ${fr(x.signature_indice)} fois plus pratiqué qu'en moyenne nationale).`
          else {
            texte += ` Sport n° 1 : ${sport(x.premier)} (${fr(x.premier_pour_1000)} pour 1 000 hab.).`
            if (x.signature && x.signature_indice != null)
              texte += ` Sport « signature » : ${sport(x.signature)}, ${fr(x.signature_indice)} fois plus pratiqué qu'en moyenne nationale.`
          }
          return {
            texte,
            precaution:
              "Licences en club comptées au domicile des licenciés, fédérations scolaires et universitaires exclues ; sports comparés parmi les fédérations d'un seul sport (les fédérations multisports ne disent pas quel sport est pratiqué).",
          }
        },
        lien: () => '/terrains/sport',
      },
    },
  },

  // ───────────────────────── Auto-écoles ─────────────────────────
  {
    id: 'auto-ecoles',
    titre: 'La meilleure auto-école est-elle celle qui a le meilleur taux ?',
    route: '/terrains/auto-ecoles',
    source: 'Sécurité routière, taux de réussite au permis B',
    sourceUrl: 'https://www.data.gouv.fr/datasets/liste-des-auto-ecoles-et-taux-de-reussite-au-permis-de-conduire',
    // auto-ecoles.json pèse plus de 1 Mo : la fiche lit l'extrait départemental produit par
    // build_territoires_echelles.py. Communes : le dossier montre des écoles, pas de résultat communal.
    fichiers: ['showcases/auto-ecoles.json', 'territoires/auto-ecoles-departements.json'],
    echelles: {
      dept: {
        fichier: 'territoires/auto-ecoles-departements.json',
        extraire: (d, code) => d.departements[code] || null,
        phrase: (x, ctx, d) => ({
          texte: `${ent(x.ecoles)} auto-écoles et ${ent(x.candidats)} candidats au permis B ; taux de réussite moyen de ${fr(x.taux)} % (France : ${fr(d.taux_national)} %).`,
          precaution:
            "Le taux brut mesure d'abord le contexte : le dossier compare chaque école à ce que son département et sa commune laissent attendre.",
        }),
        lien: (code) => `/terrains/auto-ecoles?dep=${code}`,
      },
    },
  },

  // ───────────────────────── Modes de vie ─────────────────────────
  {
    id: 'pratiques',
    titre: 'Manger, bouger, fumer : le poids du milieu social',
    route: '/terrains/pratiques',
    source: 'Assurance maladie 2024 ; Santé publique France, Baromètre 2024',
    sourceUrl: 'https://www.data.gouv.fr/datasets/62b31f7b128643f46ea1f848',
    fichiers: ['showcases/pratiques.json'],
    echelles: {
      dept: {
        fichier: 'showcases/pratiques.json',
        extraire: (d, code) => {
          const ligne = (id) => {
            const p = d.departements.find((x) => x.id === id)
            const l = p.lignes.find((x) => x.code === code)
            return l ? { std: l.std, france: p.france } : null
          }
          const addictions = ligne('addictions')
          const diabete = ligne('diabete')
          return addictions && diabete ? { addictions, diabete } : null
        },
        phrase: (x) => ({
          texte: `À âge et sexe égaux, ${fr(x.addictions.std)} % des habitants sont pris en charge pour des troubles addictifs (France : ${fr(x.addictions.france)} %) et ${fr(x.diabete.std)} % pour un diabète (France : ${fr(x.diabete.france)} %).`,
          precaution:
            "Ces chiffres comptent des personnes prises en charge par le système de soins, pas des personnes malades : un taux bas peut aussi signaler un recours aux soins plus faible.",
        }),
        lien: () => '/terrains/pratiques',
      },
      region: {
        fichier: 'showcases/pratiques.json',
        extraire: (d, code) => {
          const ligne = (id) => {
            const r = d.regions.find((x) => x.id === id)
            const l = r.lignes.find((x) => x.code === code)
            return l ? { v: l.v, france: r.national.v } : null
          }
          const tabac = ligne('tabac')
          const alcool = ligne('alcool')
          return tabac && alcool ? { tabac, alcool } : null
        },
        phrase: (x) => ({
          texte: `${fr(x.tabac.v)} % des personnes interrogées fument chaque jour (France : ${fr(x.tabac.france)} %) et ${fr(x.alcool.v)} % dépassent les repères de consommation d'alcool (France : ${fr(x.alcool.france)} %).`,
          precaution: "Enquête déclarative : un écart d'un ou deux points avec la France n'est pas toujours significatif.",
        }),
        lien: () => '/terrains/pratiques',
      },
    },
  },

  // ───────────────────────── Sélectivité du supérieur ─────────────────────────
  {
    id: 'selectivite',
    titre: 'Qui peut entrer ? La sélectivité du supérieur',
    route: '/terrains/selectivite',
    source: 'MESR, Parcoursup 2025',
    sourceUrl: 'https://data.enseignementsup-recherche.gouv.fr/explore/dataset/fr-esr-parcoursup/',
    // La matrice du dossier est par académie, une échelle que la fiche n'a pas : non reprise.
    fichiers: ['showcases/selectivite.json'],
    echelles: {
      region: {
        fichier: 'showcases/selectivite.json',
        extraire: (d, code, { nom }) => {
          const alias = { centre: 'centrevaldeloire', reunion: 'lareunion' }
          const cle = (s) => alias[sansAccents(s)] || sansAccents(s)
          return d.licence.regions.find((r) => cle(r.region) === cle(nom)) || null
        },
        phrase: (r, ctx, d) => ({
          texte: `Parcoursup ${d.session} : ${r.pct_100} % des ${ent(r.n)} formations de licence de la région acceptent tous leurs candidats (France : ${d.licence.pct_100} %) ; taux d'accès médian : ${r.taux_median} %.`,
          precaution:
            "Le taux d'accès est la part des candidats en position de recevoir une proposition : c'est la longueur de la file d'attente, pas le niveau exigé.",
        }),
        lien: () => '/terrains/selectivite',
      },
    },
  },
]

/**
 * Fichiers de dossiers qui contiennent des données par territoire mais ne sont pas repris
 * dans la rubrique, chacun avec sa raison. Une entrée a soit un `fichier` exact, soit un `motif`
 * (expression régulière sur le chemin sous /data/).
 */
export const EXCLUSIONS_TERRITOIRES = [
  {
    // Fichier intermédiaire de la chaîne Atlas (build_ecole.py -> build_atlas_communes.py), lu par
    // aucune page ; ses IPS communaux sont déjà dans le socle de la fiche.
    fichier: 'showcases/ecole-communes.json',
    raison: "Fichier intermédiaire de l'Atlas, lu par aucune page ; ses IPS par commune sont déjà dans le socle de la fiche.",
  },
  {
    // Classement de collèges nommés (décrochés / attractifs) : un résultat par établissement, pas
    // par territoire ; le reprendre par commune ferait un palmarès d'établissements.
    fichier: 'segregation/colleges-evitement.json',
    raison: "Classement d'établissements nommés, pas un résultat par territoire.",
  },
  {
    // Détail cartographique de chaque ville (carreaux de 200 m) : la rubrique reprend la synthèse
    // de villes.json et renvoie à la fiche ville du dossier, qui affiche ce détail.
    motif: /^segregation\/(\d{5}|2[AB]\d{3})\.json$/,
    raison: 'Détail cartographique de la fiche ville du dossier, accessible par le lien de la rubrique.',
  },
]

// Tous les fichiers couverts par le registre (pour le test de couverture).
export const FICHIERS_REGISTRE = [
  ...new Set(
    DOSSIERS_TERRITOIRES.flatMap((d) => [...(d.fichiers || []), ...Object.values(d.echelles).map((e) => e.fichier)]),
  ),
]

// ───────────────────────── Chargement et extraction ─────────────────────────
const cache = new Map()
export function chargerDonnees(fichier, fetcher = (u) => fetch(u).then((r) => (r.ok ? r.json() : Promise.reject(r.status)))) {
  if (!cache.has(fichier)) {
    const p = fetcher(`/data/${fichier}`).catch((e) => {
      cache.delete(fichier)
      throw e
    })
    cache.set(fichier, p)
  }
  return cache.get(fichier)
}

/**
 * Ce que chaque dossier dit d'un territoire, à une échelle donnée.
 * @returns {Promise<Array<{ dossier, texte, precaution, lien }>>} (dossiers qui ne couvrent pas le territoire omis)
 */
export async function dansNosDossiers(niveau, code, ctx, fetcher) {
  const entrees = DOSSIERS_TERRITOIRES.filter((d) => d.echelles[niveau])
  const res = await Promise.all(
    entrees.map(async (d) => {
      const e = d.echelles[niveau]
      try {
        const donnees = await chargerDonnees(e.fichier, fetcher)
        const ligne = e.extraire(donnees, code, ctx)
        if (!ligne) return null
        const { texte, precaution } = e.phrase(ligne, ctx, donnees)
        return { dossier: d, texte, precaution, lien: e.lien(code) }
      } catch {
        return null
      }
    }),
  )
  return res.filter(Boolean)
}

// Contexte d'une région (départements membres, outre-mer) pour les extractions régionales.
export function contexteRegion(region) {
  return { nom: region.nom, deps: region.deps, outreMer: !!region.outreMer }
}
