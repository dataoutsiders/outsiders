import { useEffect, useMemo, useRef, useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { X, Share2, ArrowRight, ChevronDown, Check, Map as MapIcon, BookOpen } from 'lucide-react'
import { QUESTIONS, VERDICTS } from './Home'
import { useRouteMeta } from '../lib/meta'
import { trackEvent } from '../lib/analytics'
import NewsletterForm from '../components/NewsletterForm'
import InstallerApplication from '../components/InstallerApplication'

/**
 * Le fil (/fil) : les idées reçues de l'accueil en plein écran, une par écran, qu'on fait
 * défiler verticalement comme des stories. Même source que l'accueil (QUESTIONS), donc
 * toujours les mêmes chiffres vérifiés. ?q=<id> ouvre directement une carte : c'est le lien
 * partagé par le bouton « Partager ».
 *
 * Affiché par-dessus le site (position fixe) plutôt que hors de la mise en page, pour que
 * les pages vues restent comptées par usePageviews.
 */
function Ecran({ q, index, total, onPartager, partage }) {
  const v = VERDICTS[q.verdict]
  return (
    <section
      data-id={q.id}
      className="relative h-[100dvh] snap-start flex flex-col justify-center px-6 pt-14 pb-12"
      style={{ background: `linear-gradient(180deg, ${q.couleur}14 0%, #ffffff 55%)` }}
    >
      <div className="max-w-md w-full mx-auto">
        <div className="flex items-center justify-between mb-4">
          <span className="text-xs font-semibold uppercase tracking-widest text-gray-500">{q.kicker}</span>
          {v && (
            <span
              className="-rotate-3 border-2 rounded-md px-2.5 py-1 text-sm font-black uppercase tracking-widest"
              style={{ borderColor: v.couleur, color: v.couleur }}
            >
              {v.label}
            </span>
          )}
        </div>
        <h2 className="text-2xl sm:text-3xl font-bold text-gray-900 leading-tight mb-4">{q.question}</h2>
        <div className="text-5xl sm:text-6xl font-black tracking-tight mb-1" style={{ color: q.couleur }}>
          {q.chiffre}
        </div>
        <p className="text-sm sm:text-base text-gray-600 mb-3">{q.chiffreLabel}</p>
        <p className="text-sm sm:text-base text-gray-700 leading-relaxed mb-5 line-clamp-4 sm:line-clamp-none">{q.texte}</p>
        <div className="flex items-center gap-3">
          <Link
            to={q.cta.to}
            onClick={() => trackEvent(`fil-preuve/${q.id}`, 'Fil : voir la preuve')}
            className="inline-flex items-center gap-1.5 min-h-[44px] px-4 rounded-full text-white font-medium"
            style={{ backgroundColor: q.couleur }}
          >
            Voir la preuve <ArrowRight size={16} />
          </Link>
          <button
            onClick={() => onPartager(q)}
            className="inline-flex items-center gap-1.5 min-h-[44px] px-4 rounded-full border border-gray-300 bg-white text-gray-700 font-medium"
          >
            {partage === q.id ? <Check size={16} /> : <Share2 size={16} />}
            {partage === q.id ? 'Lien copié' : 'Partager'}
          </button>
        </div>
        <a
          href={q.source.url}
          target="_blank"
          rel="noopener noreferrer"
          className="block mt-3 text-xs text-gray-400 underline decoration-gray-300 truncate"
        >
          Source : {q.source.label}
        </a>
      </div>
      <div className="absolute bottom-3 left-0 right-0 flex flex-col items-center text-xs text-gray-400">
        <span>
          {index + 1} / {total}
        </span>
        {index === 0 && (
          <span className="flex items-center gap-1 mt-1 animate-bounce">
            Faites défiler <ChevronDown size={14} />
          </span>
        )}
      </div>
    </section>
  )
}

export default function Fil() {
  useRouteMeta('/fil')
  const navigate = useNavigate()
  const [params] = useSearchParams()
  const conteneur = useRef(null)
  const [partage, setPartage] = useState(null)
  const depart = params.get('q')

  // La carte demandée par le lien partagé passe en tête ; les autres suivent dans l'ordre.
  const cartes = useMemo(() => {
    const i = QUESTIONS.findIndex((q) => q.id === depart)
    return i > 0 ? [QUESTIONS[i], ...QUESTIONS.slice(0, i), ...QUESTIONS.slice(i + 1)] : QUESTIONS
  }, [depart])

  // Pas de défilement de la page derrière le fil.
  useEffect(() => {
    const avant = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    return () => {
      document.body.style.overflow = avant
    }
  }, [])

  // Chaque carte vue (à moitié visible) est comptée une fois.
  useEffect(() => {
    const vues = new Set()
    const obs = new IntersectionObserver(
      (entrees) => {
        entrees.forEach((e) => {
          const id = e.target.dataset.id
          if (e.isIntersecting && id && !vues.has(id)) {
            vues.add(id)
            trackEvent(`fil-vue/${id}`, 'Fil : carte vue')
          }
        })
      },
      { root: conteneur.current, threshold: 0.5 },
    )
    conteneur.current?.querySelectorAll('section[data-id]').forEach((s) => obs.observe(s))
    return () => obs.disconnect()
  }, [cartes])

  const partager = async (q) => {
    const url = `${window.location.origin}/fil?q=${q.id}`
    const texte = `${q.question} ${VERDICTS[q.verdict]?.label ?? ''} : ${q.chiffre} ${q.chiffreLabel}`
    trackEvent(`fil-partage/${q.id}`, 'Fil : partage')
    try {
      if (navigator.share) {
        await navigator.share({ title: q.question, text: texte, url })
        return
      }
    } catch {
      return // partage annulé par la personne
    }
    navigator.clipboard?.writeText(`${texte} ${url}`).then(() => {
      setPartage(q.id)
      setTimeout(() => setPartage(null), 1800)
    })
  }

  const fermer = () => (window.history.length > 1 ? navigate(-1) : navigate('/'))

  return (
    <div className="fixed inset-0 z-[60] bg-white">
      <div className="absolute top-0 left-0 right-0 z-10 flex items-center justify-between px-4 py-3 bg-white/80 backdrop-blur">
        <Link to="/" className="font-bold text-gray-900 tracking-tight">
          OUTSIDERS <span className="font-normal text-gray-500">· vrai ou faux ?</span>
        </Link>
        <button onClick={fermer} aria-label="Fermer le fil" className="p-2 -mr-2 text-gray-700">
          <X size={22} />
        </button>
      </div>

      <div ref={conteneur} className="h-full overflow-y-auto snap-y snap-mandatory sans-barre">
        {cartes.map((q, i) => (
          <Ecran key={q.id} q={q} index={i} total={cartes.length} onPartager={partager} partage={partage} />
        ))}

        <section className="h-[100dvh] snap-start flex flex-col justify-center px-6 py-16 bg-gray-50">
          <div className="max-w-md w-full mx-auto">
            <h2 className="text-3xl font-bold text-gray-900 mb-3">Vous avez tout vu</h2>
            <p className="text-gray-600 mb-6">
              La suite se joue dans les dossiers et sur la carte : chaque chiffre s'y vérifie, territoire par
              territoire.
            </p>
            <div className="flex flex-wrap gap-3 mb-8">
              <Link to="/atlas" className="inline-flex items-center gap-1.5 min-h-[44px] px-4 rounded-full bg-blue-600 text-white font-medium">
                <MapIcon size={16} /> La carte
              </Link>
              <Link to="/terrains" className="inline-flex items-center gap-1.5 min-h-[44px] px-4 rounded-full border border-gray-300 bg-white text-gray-700 font-medium">
                <BookOpen size={16} /> Les dossiers
              </Link>
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">Être prévenu des prochaines</h3>
            <NewsletterForm />
            <div className="mt-5">
              <InstallerApplication />
            </div>
          </div>
        </section>
      </div>
    </div>
  )
}
