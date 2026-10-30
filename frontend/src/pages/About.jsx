import { useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Mail, BookOpen, Users, ShieldCheck, Compass, Handshake, UsersRound, Map as MapIcon, ListChecks } from 'lucide-react'
import { useRouteMeta } from '../lib/meta'

function About() {
  useRouteMeta('/about')
  const { hash } = useLocation()

  // Les liens /about#qui et /about#collaborer arrivent sur la bonne section
  // (React Router ne fait pas défiler jusqu'à l'ancre tout seul).
  // On décale de la hauteur de l'en-tête fixe pour que le titre reste visible.
  useEffect(() => {
    if (!hash) return
    const timer = setTimeout(() => {
      const cible = document.getElementById(hash.slice(1))
      if (!cible) return
      const entete = document.querySelector('header')?.offsetHeight ?? 0
      const y = cible.getBoundingClientRect().top + window.scrollY - entete - 16
      window.scrollTo({ top: y, behavior: 'smooth' })
    }, 50)
    return () => clearTimeout(timer)
  }, [hash])

  return (
    <div className="py-12 px-4">
      <div className="max-w-4xl mx-auto">
        <header className="mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">À propos</h1>
          <p className="text-xl text-gray-600">Comprendre la France par ses angles morts.</p>
        </header>

        <div className="prose-outsiders">
          <section className="mb-12">
            <h2 className="flex items-center gap-3">
              <Compass className="text-blue-600" size={26} />
              Le projet
            </h2>
            <p>
              Une carte et deux indicateurs croisés, tout le monde sait faire. Ce qu'on regarde moins,
              c'est <strong>l'écart au pronostic</strong> : le territoire intéressant n'est pas celui
              qui réussit, c'est celui qui réussit, ou échoue, <strong>contre ce que son profil
              laissait attendre</strong>. Une école qui fait progresser ses élèves malgré un milieu
              défavorisé. Une commune cossue dont la plus proche voisine statistique se trouve à
              l'autre bout du pays.
            </p>
            <p>
              Outsiders met cette lecture au centre, à partir de <strong>données publiques ouvertes</strong>,
              officielles et gratuites mais peu croisées, <strong>du pays à la commune</strong>.
            </p>
            <p>Deux familles d'usages :</p>
            <ul className="list-disc pl-6 mt-4 space-y-2">
              <li>
                <strong>Explorer</strong> : une carte qui croise deux indicateurs et fait remonter les
                outsiders, au-dessus et en dessous de la droite de pronostic ; une fiche par territoire
                menée par ce qui le rend inhabituel, avec son jumeau statistique ; des dossiers
                approfondis sur une question.
              </li>
              <li>
                <strong>Mesurer</strong> : des outils que vous faites tourner sur vos propres fichiers
                (diversité, parité, âge), directement dans votre navigateur.
              </li>
            </ul>
          </section>

          <section className="mb-12">
            <h2 className="flex items-center gap-3">
              <MapIcon className="text-blue-600" size={26} />
              Ce que vous trouverez ici
            </h2>
            <ul className="list-disc pl-6 mt-4 space-y-2">
              <li>
                <strong>Des idées reçues à l'épreuve des chiffres</strong> : sur la page d'accueil, chaque
                question reçoit un verdict, un chiffre sourcé et un lien vers la preuve.
              </li>
              <li>
                <strong>La{' '}
                <Link to="/atlas" className="text-blue-600 hover:underline">carte des outsiders</Link></strong> :
                une vingtaine d'indicateurs publics (revenu, école, logement, diplômes, âge, natalité…) par
                département, intercommunalité et commune.
              </li>
              <li>
                <strong>Une{' '}
                <Link to="/territoires" className="text-blue-600 hover:underline">fiche pour chaque territoire</Link></strong>,
                de la commune à la région : ce qui le distingue, son jumeau statistique, et ce que nos
                dossiers disent de lui.
              </li>
              <li>
                <strong>Des dossiers</strong> : la France en Europe, PISA 2025, la séparation des riches et des
                pauvres dans les villes, l'évolution des revenus des communes, le sport, l'école, les élus,
                l'Assemblée, l'accès au supérieur, les auto-écoles.
              </li>
              <li>
                <strong>Des comparaisons de groupes</strong> : milieu social, sexe, âge, et 30 pays européens.
              </li>
              <li>
                <strong>Sur téléphone</strong>, les idées reçues une par écran dans{' '}
                <Link to="/fil" className="text-blue-600 hover:underline">le fil</Link>, et le site s'installe comme
                une application sur l'écran d'accueil.
              </li>
            </ul>
          </section>

          <section className="mb-12">
            <h2 className="flex items-center gap-3">
              <ListChecks className="text-blue-600" size={26} />
              Comment nous travaillons
            </h2>
            <ul className="list-disc pl-6 mt-4 space-y-2">
              <li>
                <strong>Des chiffres vérifiés</strong> : chaque chiffre de la page d'accueil est retrouvé dans les
                données publiées, avec sa source, et chaque verdict doit découler des chiffres. Un rang se donne
                avec sa marge d'incertitude ; une différence n'est affirmée que si elle est statistiquement
                significative.
              </li>
              <li>
                <strong>Des données tenues à jour</strong> : chaque source est reprise à son dernier millésime
                publié, et la source de chaque chiffre en indique l'année.
              </li>
              <li>
                <strong>Les limites affichées</strong> : ce qu'une donnée ne dit pas est écrit à côté d'elle (par
                exemple, une licence sportive est comptée par fédération, pas par sport pratiqué).
              </li>
              <li>
                <strong>Des sujets sensibles traités avec précaution</strong> : sur la diversité des noms, rien
                n'est publié par personne, aucun groupe de moins de 30 noms n'est affiché, et aucun classement
                n'est présenté comme un palmarès.
              </li>
            </ul>
            <p>
              Vous voulez reprendre un chiffre, une carte ou une image ? Tout ce qu'il faut est sur la page{' '}
              <Link to="/presse" className="text-blue-600 hover:underline">Presse et réutilisation</Link>.
            </p>
          </section>

          <section id="qui" className="mb-12 scroll-mt-24">
            <h2 className="flex items-center gap-3">
              <UsersRound className="text-blue-600" size={26} />
              Qui fait Outsiders ?
            </h2>
            <p>
              Outsiders est un <strong>projet indépendant</strong>, né de la rencontre entre la
              statistique publique et les sciences sociales. Il n'a ni financement, ni lien avec une
              institution, un parti ou une entreprise : <strong>ses analyses n'engagent que lui</strong>.
            </p>
            <p>
              Le projet préfère que l'on juge le travail plutôt que ses auteurs : chaque chiffre renvoie
              à sa source, chaque méthode est décrite dans la page{' '}
              <Link to="/methodologie" className="text-blue-600 hover:underline">Méthodologie</Link>, et
              chacun peut refaire les calculs.
            </p>
          </section>

          <section className="mb-12">
            <h2 className="flex items-center gap-3">
              <Users className="text-blue-600" size={26} />
              Pour qui ?
            </h2>
            <p>
              Pour les <strong>curieux</strong> qui veulent situer leur commune, les
              <strong> journalistes</strong> et <strong>chercheurs</strong> qui cherchent des chiffres
              sourcés, et les <strong>élus et acteurs publics</strong> qui ont besoin d'une vue d'ensemble
              pour décider, notamment à l'échelle territoriale.
            </p>
            <p>
              Tout le contenu est publié sous licence <strong>Creative Commons (CC BY)</strong> : reprenez-le
              librement, avec citation.
            </p>
          </section>

          <section id="collaborer" className="mb-12 scroll-mt-24">
            <h2 className="flex items-center gap-3">
              <Handshake className="text-blue-600" size={26} />
              Travailler avec nous
            </h2>
            <p>
              Outsiders est <strong>ouvert aux collaborations</strong>. Vous êtes journaliste et voulez
              creuser un territoire ou reprendre une carte ? Chercheur ou observatoire, et vous voulez
              croiser vos données avec les nôtres ? Collectivité, association ou fondation, avec une
              question que les données publiques pourraient éclairer ?
            </p>
            <p>Quelques exemples de ce que nous pouvons faire ensemble :</p>
            <ul className="list-disc pl-6 mt-4 mb-5 space-y-2">
              <li>une carte ou un nuage des outsiders à intégrer dans un article, source citée ;</li>
              <li>
                la lecture d'un territoire ou d'une population <strong>à contexte égal</strong> :
                ce qui s'écarte vraiment de l'attendu, et ce qui n'est que l'effet du profil ;
              </li>
              <li>une étude commune, quantitative ou qualitative, sur une question précise ;</li>
              <li>un nouveau jeu de données publiques à rendre lisible.</li>
            </ul>
            <p>
              Écrivez-nous en quelques lignes : qui vous êtes, votre question, vos délais. Nous lisons
              tous les messages.
            </p>
            <a
              href="mailto:contact@dataoutsiders.fr?subject=Travailler%20avec%20Outsiders"
              className="inline-flex items-center gap-3 text-blue-600 hover:text-blue-700 transition-colors mt-2"
            >
              <Mail size={20} />
              contact@dataoutsiders.fr
            </a>
          </section>

          <section className="mb-12">
            <h2 className="flex items-center gap-3">
              <ShieldCheck className="text-blue-600" size={26} />
              Nos principes
            </h2>
            <ul className="list-disc pl-6 mt-4 space-y-2">
              <li><strong>Données ouvertes et sources citées</strong> : tout est vérifiable.</li>
              <li>
                <strong>Respect de la vie privée</strong> : les outils traitent vos fichiers dans le
                navigateur, rien n'est envoyé. Aucune donnée sur l'origine des personnes : l'indice de
                diversité des noms est un indicateur statistique, qui ne se lit qu'à l'échelle d'un
                groupe, jamais d'un individu.
              </li>
              <li><strong>Décrire, pas juger</strong> : les indicateurs éclairent, ils ne notent pas les territoires.</li>
            </ul>
          </section>

          <section className="mb-12">
            <h2 className="flex items-center gap-3">
              <Mail className="text-blue-600" size={26} />
              Contact
            </h2>
            <p>Une remarque, une donnée à signaler, un territoire à creuser ?</p>
            <a
              href="mailto:contact@dataoutsiders.fr"
              className="inline-flex items-center gap-3 text-blue-600 hover:text-blue-700 transition-colors mt-2"
            >
              <Mail size={20} />
              contact@dataoutsiders.fr
            </a>
          </section>

          <section className="mb-12">
            <h2 className="flex items-center gap-3">
              <BookOpen className="text-blue-600" size={24} />
              D'où vient le nom
            </h2>
            <p>
              « Outsiders » fait un clin d'œil au livre d'Howard Becker, <em>Outsiders</em> (1963) :
              ce qui se joue <strong>en marge</strong>, hors du regard dominant. C'est l'esprit du site,
              s'intéresser aux <strong>angles morts</strong> des données publiques, ce qu'elles disent
              mais qu'on ne regarde pas.
            </p>
          </section>
        </div>
      </div>
    </div>
  )
}

export default About
