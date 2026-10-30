import { Link } from 'react-router-dom'
import { useRouteMeta } from '../lib/meta'

function MentionsLegales() {
  useRouteMeta('/mentions-legales')
  return (
    <div className="py-12 px-4">
      <div className="max-w-4xl mx-auto">
        <header className="mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Mentions légales</h1>
        </header>

        <div className="prose-outsiders">
          <section className="mb-10">
            <h2>Éditeur</h2>
            <p>
              Outsiders est un projet indépendant, édité à titre non professionnel. Conformément à
              l'article 6, III, 2 de la loi n° 2004-575 du 21 juin 2004 pour la confiance dans
              l'économie numérique, l'éditeur a communiqué ses éléments d'identification à
              l'hébergeur.
            </p>
            <p>
              Contact :{' '}
              <a href="mailto:contact@dataoutsiders.fr" className="text-blue-600 hover:underline">
                contact@dataoutsiders.fr
              </a>
            </p>
          </section>

          <section className="mb-10">
            <h2>Hébergeur</h2>
            <p>
              Cloudflare, Inc. (service Cloudflare Pages), 101 Townsend Street, San Francisco,
              CA 94107, États-Unis. Téléphone : +1 888 993 5273.
            </p>
          </section>

          <section className="mb-10">
            <h2>Contenus et licence</h2>
            <p>
              Les textes, cartes et graphiques du site sont publiés sous licence{' '}
              <strong>Creative Commons Attribution 4.0 (CC BY 4.0)</strong> : vous pouvez les reprendre,
              y compris à des fins commerciales, en citant Outsiders et le lien de la page.
            </p>
            <p>
              Les données affichées proviennent de sources publiques (INSEE, ministère de l'Éducation
              nationale, Etalab, Eurostat, Assemblée nationale, Arcom, entre autres), citées sous chaque
              chiffre avec un lien vers l'origine. Elles restent soumises à la licence de leur
              producteur, le plus souvent la Licence Ouverte d'Etalab.
            </p>
          </section>

          <section className="mb-10">
            <h2>Données personnelles</h2>
            <ul className="list-disc pl-6 mt-4 space-y-2">
              <li>
                <strong>Aucun cookie</strong> : la fréquentation est mesurée par GoatCounter, sans
                cookie ni identification des visiteurs. Certaines actions sont comptées de la même façon
                (consulter une fiche territoire, copier un code d'intégration ou une phrase de la page
                presse, lancer un outil), sans rien enregistrer sur la personne ni sur ce qu'elle saisit.
              </li>
              <li>
                <strong>Outils</strong> : les fichiers et listes que vous analysez avec les outils du
                site sont traités dans votre navigateur. Ils ne sont ni envoyés, ni conservés.
              </li>
              <li>
                <strong>Newsletter</strong> : si vous vous inscrivez, seule votre adresse électronique est
                collectée, pour vous envoyer la newsletter d'Outsiders et rien d'autre. Elle est conservée
                par notre prestataire d'envoi, Brevo (Sendinblue SAS, France ; données hébergées dans
                l'Union européenne), jusqu'à votre désinscription. Chaque mail contient un lien de
                désinscription. Vous
                pouvez aussi demander l'accès à vos données ou leur suppression à l'adresse de contact.
                Base légale : votre consentement.
              </li>
              <li>
                <strong>Messages</strong> : les courriels que vous nous adressez servent uniquement à
                vous répondre ; ils ne sont ni cédés, ni utilisés à d'autres fins. Vous pouvez demander
                leur suppression à la même adresse.
              </li>
            </ul>
          </section>

          <section className="mb-10">
            <h2>Responsabilité</h2>
            <p>
              Les analyses sont produites avec soin à partir des données publiques disponibles, dont
              les limites sont décrites dans la page{' '}
              <Link to="/methodologie" className="text-blue-600 hover:underline">Méthodologie</Link>.
              Elles peuvent néanmoins contenir des erreurs : signalez-les nous, nous les corrigerons.
              Les analyses n'engagent que le projet Outsiders.
            </p>
          </section>
        </div>
      </div>
    </div>
  )
}

export default MentionsLegales
