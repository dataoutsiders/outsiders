import { Database, Users, ShieldCheck, BarChart3, AlertTriangle, GitBranch, TrendingUp, GitCompare, Scale } from 'lucide-react'
import { useRouteMeta } from '../lib/meta'

function Methodologie() {
  useRouteMeta('/methodologie')
  return (
    <div className="py-12 px-4">
      <div className="max-w-4xl mx-auto">
        <header className="mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Méthodologie</h1>
          <p className="text-xl text-gray-600">
            Des données publiques ouvertes, calculées de façon transparente et reproductible.
          </p>
        </header>

        <div className="prose-outsiders">
          <section className="mb-12">
            <h2 className="flex items-center gap-3">
              <Database className="text-blue-600" size={28} />
              Des données ouvertes, sous-exploitées
            </h2>
            <p>
              Nous partons de jeux de données publics, officiels et gratuits, mais que peu de gens
              croisent. Les principales sources :
            </p>
            <ul className="list-disc pl-6 mt-4 space-y-2">
              <li>
                <strong>École</strong> : l'<strong>IPS</strong> (indice de position sociale, milieu social
                moyen des élèves), l'<strong>IVAL</strong> (valeur ajoutée des lycées au bac) et les
                <strong> résultats du brevet</strong> par collège, publiés par l'Éducation nationale.
              </li>
              <li>
                <strong>Richesse</strong> : le <strong>revenu médian</strong> par commune, département et intercommunalité (niveau de vie médian, Insee, Filosofi 2023) et
                le <strong>prix immobilier au m²</strong> (DVF, demandes de valeurs foncières, Etalab).
              </li>
              <li>
                <strong>Représentation</strong> : les <strong>candidatures aux municipales 2026</strong>,
                analysées via l'indice de diversité patronymique.
              </li>
              <li>
                <strong>Population et société</strong> : le <strong>recensement INSEE 2023</strong>, dont on
                tire par commune les diplômés du supérieur, les catégories socioprofessionnelles (cadres,
                professions intermédiaires, employés, ouvriers), le logement (HLM, propriétaires, vacance,
                résidences secondaires, maisons) et la structure par âge.
              </li>
              <li>
                <strong>État civil</strong> : les <strong>naissances domiciliées</strong> (INSEE), pour un
                taux de natalité rapporté à la population.
              </li>
              <li>
                <strong>Permis de conduire</strong> : le <strong>taux de réussite de chaque auto-école</strong>{' '}
                au permis B en première présentation, publié par la Sécurité routière.
              </li>
            </ul>
          </section>

          <section className="mb-12">
            <h2 className="flex items-center gap-3">
              <TrendingUp className="text-blue-600" size={28} />
              L'écart au pronostic : repérer les outsiders
            </h2>
            <p>
              C'est le coeur du site. Plutôt que le niveau brut d'un territoire, on regarde son
              <strong> écart à ce que son profil laisse attendre</strong>. En croisant deux indicateurs
              (par exemple la réussite scolaire et le revenu), on ajuste une <strong>droite de
              régression</strong>, le « pronostic » : un territoire au-dessus fait mieux que prévu, en
              dessous moins bien. Ce sont les <strong>outsiders</strong>.
            </p>
            <ul className="list-disc pl-6 mt-4 space-y-2">
              <li>
                Les écarts sont mesurés en <strong>résidus studentisés</strong> (standardisés), donc
                comparables d'un territoire à l'autre.
              </li>
              <li>
                Un <strong>filtre de population</strong> écarte les très petites communes, dont les
                indicateurs varient trop pour être fiables (sans quoi les « outsiders » ne seraient que du bruit).
              </li>
              <li>
                Le <strong>R²</strong> indique la solidité de la relation : s'il est faible, les écarts sont à
                lire avec prudence.
              </li>
              <li>
                Les écarts sont des <strong>signaux descriptifs</strong> (« ça mérite qu'on regarde »), jamais
                des explications. Une corrélation entre territoires ne dit rien des individus (erreur
                écologique), et les outsiders changent selon la maille (commune, intercommunalité, département).
              </li>
            </ul>
          </section>

          <section className="mb-12">
            <h2 className="flex items-center gap-3">
              <GitCompare className="text-blue-600" size={28} />
              Situer et comparer un territoire
            </h2>
            <ul className="list-disc pl-6 mt-4 space-y-2">
              <li>
                <strong>Ce qui sort de l'ordinaire</strong> : la fiche d'un territoire met en avant les
                indicateurs où il s'écarte le plus de sa référence. La <strong>référence est au choix</strong>{' '}
                (la France, son département, ou les communes de sa taille), car le caractère atypique dépend
                de ce à quoi on compare.
              </li>
              <li>
                <strong>Quatre échelles</strong> : la fiche existe pour la commune, l'intercommunalité, le
                département et la région, et chaque territoire est situé parmi ceux de même échelle. Les
                valeurs d'une intercommunalité ou d'une région sont celles que la source publie à cette
                échelle (Insee : revenu médian, recensement) ou, à défaut, recalculées depuis les effectifs
                avec la même définition qu'au département ; jamais une moyenne de médianes. Sans valeur
                publiée ni effectifs (prix immobilier régional), l'indicateur n'est pas affiché.
              </li>
              <li>
                <strong>Le jumeau statistique</strong> : la commune qui ressemble le plus à la vôtre dans
                l'espace des indicateurs <strong>standardisés</strong> (z-scores), sa distance en kilomètres,
                et son anti-jumeau à taille comparable. Même calcul pour une intercommunalité, parmi les
                intercommunalités. Calculé dans le navigateur.
              </li>
              <li>
                <strong>Dans nos dossiers</strong> : la fiche reprend ce que chaque dossier publie déjà sur ce
                territoire, à cette échelle, avec ses précautions, et rien d'autre (ni rang que le dossier ne
                donne pas, ni résultat qu'il ne montre pas à cette échelle).
              </li>
            </ul>
          </section>

          <section className="mb-12">
            <h2 className="flex items-center gap-3">
              <Scale className="text-blue-600" size={28} />
              Comparer des établissements à contexte égal
            </h2>
            <p>
              Le dossier Auto-écoles applique l'écart au pronostic à des établissements : chaque école est
              comparée à ce qu'une école moyenne obtiendrait <strong>dans le même contexte</strong>, et non
              à la moyenne nationale.
            </p>
            <ul className="list-disc pl-6 mt-4 space-y-2">
              <li>
                <strong>Le taux attendu</strong> vient d'une régression pondérée par le nombre de candidats,
                avec un effet propre à chaque département (mêmes inspecteurs, mêmes centres d'examen) et le
                profil de la commune (taille, âge, logement, diplômes) et de ses collégiens (indice de
                position sociale des collèges publics, à défaut celui de l'intercommunalité ou du département).
              </li>
              <li>
                <strong>Le hasard est pris en compte</strong> : un taux calculé sur 20 candidats est fragile.
                L'écart est rapproché de zéro d'autant plus que l'effectif est petit (estimateur bayésien
                empirique) et accompagné d'un intervalle à 95 % ; une école n'est dite au-dessus ou en dessous
                de l'attendu que si cet intervalle exclut zéro.
              </li>
              <li>
                <strong>Les écarts sont décomposés</strong> entre département, commune, écart durable propre
                à l'école (ou à ce que les données ne voient pas) et bruit d'échantillonnage.
              </li>
              <li>
                <strong>Les caractéristiques des écoles</strong> (label, conduite accompagnée, statut
                associatif, volume) sont comparées toutes choses égales par ailleurs, avec des erreurs-types
                robustes : on distingue ce qui est net, probable, ou non distinguable du hasard. Ce sont des
                associations, pas des causes.
              </li>
            </ul>
          </section>

          <section className="mb-12">
            <h2 className="flex items-center gap-3">
              <Users className="text-blue-600" size={28} />
              L'indice de diversité patronymique (IDP)
            </h2>
            <p>
              Faute de statistiques d'origine (interdites en France), on utilise un <strong>proxy
              onomastique</strong> : la part des noms de famille <strong>apparus en France après 1950</strong>,
              trace des migrations récentes. C'est une mesure indirecte, à manier avec précaution :
            </p>
            <ul className="list-disc pl-6 mt-4 space-y-2">
              <li>elle capte l'<strong>immigration récente</strong>, pas toute la diversité ;</li>
              <li>
                elle sous-estime les territoires dont les noms sont inscrits à l'état civil <em>avant</em> 1950
                (ainsi certains outre-mer ressortent paradoxalement bas).
              </li>
            </ul>
          </section>

          <section className="mb-12">
            <h2 className="flex items-center gap-3">
              <ShieldCheck className="text-blue-600" size={28} />
              Vie privée & droit français
            </h2>
            <p>
              Les <strong>outils tournent à 100 % dans votre navigateur</strong> : votre fichier n'est
              jamais envoyé sur un serveur. Nous ne produisons <strong>aucune statistique ethnique</strong>,
              seulement des proxys agrégés, à l'échelle de territoires ou de groupes, jamais d'origine
              individuelle déclarée. La démarche est compatible avec le droit français.
            </p>
          </section>

          <section className="mb-12">
            <h2 className="flex items-center gap-3">
              <BarChart3 className="text-blue-600" size={28} />
              Comment on calcule
            </h2>
            <ul className="list-disc pl-6 mt-4 space-y-2">
              <li>Les indicateurs sont <strong>agrégés par commune et par département</strong> (médianes, parts).</li>
              <li>
                Chaque territoire est <strong>situé dans la distribution nationale</strong> (percentiles) :
                « parmi les 10 % les plus bas », « au-dessus de la médiane »…
              </li>
              <li>Des <strong>seuils minimaux</strong> (par ex. un nombre suffisant de candidats) écartent les effectifs trop faibles pour être fiables.</li>
              <li>On <strong>décrit</strong> des écarts : aucun indicateur n'est une « note » du territoire.</li>
            </ul>
          </section>

          <section className="mb-12">
            <h2 className="flex items-center gap-3">
              <AlertTriangle className="text-blue-600" size={28} />
              Limites
            </h2>
            <ul className="list-disc pl-6 mt-4 space-y-2">
              <li>L'<strong>IDP</strong> ne capte que les migrations postérieures à 1950 (outre-mer mal mesuré).</li>
              <li>L'<strong>IPS</strong> décrit le milieu social, pas le niveau scolaire ; la <strong>valeur ajoutée</strong> distingue les deux.</li>
              <li>Les <strong>prix DVF</strong> dépendent des ventes enregistrées : peu de transactions = estimation fragile.</li>
              <li>
                Le <strong>taux de réussite d'une auto-école</strong> dépend aussi de ses candidats (âge, heures
                de conduite), que les données publiques ne décrivent pas : un écart à l'attendu signale, il ne note pas.
              </li>
              <li>Ce sont des <strong>photographies</strong>, des corrélations, pas des liens de cause à effet.</li>
            </ul>
          </section>

          <section className="mb-12">
            <h2 className="flex items-center gap-3">
              <GitBranch className="text-blue-600" size={28} />
              Reproductibilité & technique
            </h2>
            <p>
              Des <strong>pipelines Python</strong> précalculent, hors-ligne, des fichiers JSON statiques,
              servis ensuite par un CDN. Rien ne tourne « par requête » : le site est rapide et vérifiable,
              et les calculs peuvent être rejoués à l'identique. Certains traitements (écart au pronostic,
              jumeau statistique, outils onomastiques) se font <strong>directement dans votre navigateur</strong>,
              sur des fichiers déjà publiés, sans aucun serveur.
            </p>
            <div className="bg-gray-100 p-4 rounded-lg mt-4">
              <p className="text-sm text-gray-600">
                Stack : Python (pandas, numpy) pour les données ; React, Vite, Tailwind CSS, Leaflet (cartes)
                et Recharts (graphiques) pour l'interface.
              </p>
            </div>
          </section>
        </div>
      </div>
    </div>
  )
}

export default Methodologie
