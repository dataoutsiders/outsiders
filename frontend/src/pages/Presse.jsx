import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Newspaper, Quote, Code, Image as ImageIcon, Mail, Copy, Check, ArrowRight, ExternalLink } from 'lucide-react'
import { useRouteMeta } from '../lib/meta'
import { ROUTES_META, ogSlug } from '../config/seo'
import { QUESTIONS, VERDICTS } from './Home'
import { trackEvent } from '../lib/analytics'
import NewsletterForm from '../components/NewsletterForm'

// Résultats proposés à la reprise : les cartes de l'accueil (même source, donc toujours
// les mêmes chiffres), hors sujets politiques ou sensibles (Élus, Assemblée, Sélectivité).
const RESULTATS = ['revenus', 'sport', 'etat-enfants', 'ecole', 'auto-ecoles', 'esperance', 'sante-paradoxe', 'age', 'hlm', 'sexe', 'segregation']

// Pages dont l'image de partage est proposée au téléchargement.
const IMAGES = ['/atlas', '/terrains/revenus', '/terrains/sport', '/terrains/ecole', '/terrains/auto-ecoles', '/international', '/segregation']

const EXEMPLE_IFRAME =
  '<iframe src="https://dataoutsiders.fr/embed/carte?i=revenu" width="100%" height="560" style="border:0;border-radius:12px" loading="lazy" title="Outsiders, revenu médian"></iframe>'

function BoutonCopier({ texte, label = 'Copier', evenement }) {
  const [copie, setCopie] = useState(false)
  const copier = () => {
    if (evenement) trackEvent(evenement, 'Presse : copie')
    navigator.clipboard?.writeText(texte).then(() => {
      setCopie(true)
      setTimeout(() => setCopie(false), 1500)
    })
  }
  return (
    <button
      onClick={copier}
      className="inline-flex items-center gap-1.5 text-xs font-medium text-blue-600 hover:text-blue-800"
    >
      {copie ? <Check size={14} /> : <Copy size={14} />}
      {copie ? 'Copié' : label}
    </button>
  )
}

function Resultat({ q }) {
  const v = VERDICTS[q.verdict]
  const citation = `${q.chiffre} ${q.chiffreLabel} (Outsiders, d'après ${q.source.label}).`
  return (
    <div className="bg-white border border-gray-200 rounded-xl p-5 flex flex-col">
      <div className="flex items-center justify-between gap-3 mb-2">
        <span className="text-xs font-semibold uppercase tracking-wide text-gray-400">{q.kicker}</span>
        {v && (
          <span className="text-xs font-bold px-2 py-0.5 rounded" style={{ color: v.couleur, border: `1px solid ${v.couleur}` }}>
            {v.label}
          </span>
        )}
      </div>
      <h3 className="font-semibold text-gray-900 mb-2">{q.question}</h3>
      <p className="text-sm text-gray-700 mb-3">
        <strong className="text-gray-900">{q.chiffre}</strong> {q.chiffreLabel}
      </p>
      <div className="mt-auto flex flex-wrap items-center gap-x-4 gap-y-2 text-xs">
        <BoutonCopier texte={citation} label="Copier la phrase et sa source" evenement={`presse-phrase/${q.id}`} />
        <Link to={q.cta.to} className="inline-flex items-center gap-1 text-gray-600 hover:text-blue-600">
          Le dossier <ArrowRight size={13} />
        </Link>
        <a href={q.source.url} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1 text-gray-600 hover:text-blue-600">
          Source <ExternalLink size={12} />
        </a>
      </div>
    </div>
  )
}

function Presse() {
  useRouteMeta('/presse')
  const resultats = RESULTATS.map((id) => QUESTIONS.find((q) => q.id === id)).filter(Boolean)
  const formule = "Source : Outsiders (dataoutsiders.fr), d'après [producteur de la donnée, millésime]."

  return (
    <div className="py-12 px-4">
      <div className="max-w-5xl mx-auto">
        <header className="mb-10">
          <div className="flex items-center gap-2 text-blue-600 mb-2">
            <Newspaper size={18} />
            <span className="text-sm font-semibold uppercase tracking-wide">Presse et réutilisation</span>
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Reprenez nos chiffres, nos cartes, nos graphiques</h1>
          <p className="text-lg text-gray-600 max-w-3xl">
            Tout ce qui est publié ici peut être repris, gratuitement et sans demande préalable, à une seule condition :
            citer la source. Cette page rassemble ce qu'il faut pour le faire vite et bien.
          </p>
        </header>

        <section className="mb-14">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Les résultats à reprendre</h2>
          <p className="text-gray-600 mb-6 max-w-3xl">
            Chaque chiffre est vérifié, sourcé et expliqué dans son dossier. Le bouton copie une phrase prête à
            l'emploi, avec sa source.
          </p>
          <div className="grid md:grid-cols-2 gap-4">
            {resultats.map((q) => (
              <Resultat key={q.id} q={q} />
            ))}
          </div>
        </section>

        <section className="mb-14">
          <h2 className="flex items-center gap-2 text-2xl font-bold text-gray-900 mb-3">
            <Quote size={22} className="text-blue-600" /> Comment citer
          </h2>
          <div className="bg-gray-50 border border-gray-200 rounded-xl p-5 mb-4">
            <p className="font-mono text-sm text-gray-800 mb-2">{formule}</p>
            <BoutonCopier texte={formule} evenement="presse-formule" />
          </div>
          <ul className="list-disc pl-6 space-y-1.5 text-gray-700">
            <li>
              Les textes, cartes et graphiques sont sous licence{' '}
              <a href="https://creativecommons.org/licenses/by/4.0/deed.fr" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                Creative Commons Attribution 4.0
              </a>
              , y compris pour un usage commercial.
            </li>
            <li>
              Les données restent soumises à la licence de leur producteur (Insee, ministères, Eurostat…), le plus souvent
              la Licence Ouverte d'Etalab : citez aussi le producteur, indiqué sous chaque chiffre.
            </li>
            <li>
              En ligne, un lien vers la page d'origine suffit à citer ; il permet aussi au lecteur de retrouver la
              méthode.
            </li>
          </ul>
        </section>

        <section className="mb-14">
          <h2 className="flex items-center gap-2 text-2xl font-bold text-gray-900 mb-3">
            <Code size={22} className="text-blue-600" /> Intégrer une carte ou un graphique
          </h2>
          <p className="text-gray-700 mb-3">
            Sur la <Link to="/atlas" className="text-blue-600 hover:underline">carte des outsiders</Link>, choisissez un
            indicateur et une échelle (département, intercommunalité, commune), puis cliquez sur{' '}
            <strong>« Intégrer »</strong> : le code d'intégration est copié, à coller dans votre page. Le nuage de
            croisement de deux indicateurs s'intègre de la même façon (« Intégrer ce graphique »). La source s'affiche
            dans le cadre intégré, et la carte se met à jour avec nos données.
          </p>
          <div className="bg-gray-50 border border-gray-200 rounded-xl p-5">
            <div className="text-xs font-semibold uppercase tracking-wide text-gray-400 mb-2">Exemple : le revenu médian par département</div>
            <pre className="font-mono text-xs text-gray-800 whitespace-pre-wrap break-all mb-2">{EXEMPLE_IFRAME}</pre>
            <BoutonCopier texte={EXEMPLE_IFRAME} label="Copier le code" evenement="presse-iframe" />
          </div>
        </section>

        <section className="mb-14">
          <h2 className="flex items-center gap-2 text-2xl font-bold text-gray-900 mb-3">
            <ImageIcon size={22} className="text-blue-600" /> Images prêtes à l'emploi
          </h2>
          <p className="text-gray-700 mb-5">
            Les visuels de nos dossiers, au format des réseaux sociaux (1200 x 630), à reprendre avec la mention de la
            source.
          </p>
          <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-4">
            {IMAGES.filter((p) => ROUTES_META[p]).map((p) => {
              const src = `/og/${ogSlug(p)}.png`
              return (
                <a key={p} href={src} download onClick={() => trackEvent(`presse-image/${ogSlug(p)}`, 'Presse : image téléchargée')} className="group block bg-white border border-gray-200 rounded-xl overflow-hidden hover:border-gray-300">
                  <img src={src} alt={ROUTES_META[p].title} loading="lazy" className="w-full aspect-[1200/630] object-cover bg-gray-100" />
                  <div className="px-3 py-2 text-xs text-gray-600 group-hover:text-blue-600">{ROUTES_META[p].title}</div>
                </a>
              )
            })}
          </div>
        </section>

        <section className="mb-6">
          <h2 className="flex items-center gap-2 text-2xl font-bold text-gray-900 mb-3">
            <Mail size={22} className="text-blue-600" /> Une question, une demande ?
          </h2>
          <p className="text-gray-700 mb-3">Écrivez-nous, nous répondons par écrit :</p>
          <ul className="list-disc pl-6 space-y-1.5 text-gray-700 mb-4">
            <li>une précision de méthode, ou le tableau qui se trouve derrière un chiffre ;</li>
            <li>une carte ou des chiffres sur votre territoire (ville, département, région) ;</li>
            <li>une erreur à signaler : elle sera vérifiée et corrigée.</li>
          </ul>
          <a
            href="mailto:contact@dataoutsiders.fr"
            className="inline-flex items-center gap-2 px-4 py-2.5 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700"
          >
            <Mail size={18} /> contact@dataoutsiders.fr
          </a>
          <div className="mt-8 bg-gray-50 border border-gray-200 rounded-xl p-5 max-w-2xl">
            <h3 className="font-semibold text-gray-900 mb-1">Être prévenu des nouveaux dossiers</h3>
            <p className="text-sm text-gray-600 mb-3">Un mail à chaque sortie ou mise à jour, pas plus d'un par mois.</p>
            <NewsletterForm />
          </div>
          <p className="text-sm text-gray-500 mt-4">
            Pour une collaboration au long cours (étude, données croisées, atelier), voir{' '}
            <Link to="/about#collaborer" className="text-blue-600 hover:underline">Travailler avec nous</Link>.
          </p>
        </section>
      </div>
    </div>
  )
}

export default Presse
