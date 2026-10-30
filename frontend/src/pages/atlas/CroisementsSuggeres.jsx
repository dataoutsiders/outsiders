import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { ArrowUpRight, ArrowDownRight, ArrowRight, ChevronDown, ChevronUp } from 'lucide-react'
import { INDICATEUR_BY_ID } from '../../config/indicateurs'

function MiniListe({ titre, icon, items, fmtY }) {
  if (!items?.length) return null
  return (
    <div className="flex-1 min-w-[10rem]">
      <div className="flex items-center gap-1 text-xs font-semibold text-gray-500 mb-1.5">
        {icon}
        {titre}
      </div>
      <ul className="space-y-0.5">
        {items.slice(0, 3).map((o) => (
          <li key={o.code} className="text-sm truncate">
            <Link to={`/territoires?code=${o.code}`} className="text-gray-800 hover:underline">
              {o.nom}
            </Link>
            <span className="text-gray-400"> · {fmtY(o.y)}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}

/**
 * Les croisements retenus automatiquement (data/atlas/croisements.json, généré par
 * python/tools/build_croisements.py) : une carte par paire de dimensions, avec les
 * communes les plus loin du pronostic des deux côtés. Un clic ouvre le nuage préconfiguré.
 */
export default function CroisementsSuggeres({ onOpen }) {
  const [data, setData] = useState(null)
  const [all, setAll] = useState(false)
  useEffect(() => {
    fetch('/data/atlas/croisements.json')
      .then((r) => (r.ok ? r.json() : null))
      .then(setData)
      .catch(() => {})
  }, [])

  const croisements = (data?.croisements || []).filter(
    (c) => INDICATEUR_BY_ID[c.y] && INDICATEUR_BY_ID[c.x],
  )
  if (!croisements.length) return null
  const cards = all ? croisements : croisements.slice(0, 6)

  return (
    <section className="max-w-5xl mx-auto px-4 mt-12">
      <h2 className="text-2xl font-bold text-gray-900 mb-1">Par où commencer ? Les croisements qui comptent</h2>
      <p className="text-gray-600 mb-6 max-w-3xl">
        Plutôt que de croiser au hasard, voici les relations les plus nettes entre indicateurs
        de mondes différents. Pour chacune, la droite donne le pronostic ; les communes citées
        s'en écartent le plus, dans un sens ou dans l'autre. C'est là que ça se discute.
      </p>

      <div className="grid md:grid-cols-2 gap-5">
        {cards.map((c) => {
          const y = INDICATEUR_BY_ID[c.y]
          const x = INDICATEUR_BY_ID[c.x]
          return (
            <div key={c.id} className="bg-white border border-gray-200 rounded-xl p-5 flex flex-col">
              <div className="flex flex-wrap items-center gap-1.5 mb-2 text-xs font-medium">
                <span className="px-2 py-0.5 rounded-full text-white" style={{ backgroundColor: y.couleur }}>
                  {y.label}
                </span>
                <span className="text-gray-400">selon</span>
                <span className="px-2 py-0.5 rounded-full text-white" style={{ backgroundColor: x.couleur }}>
                  {x.label}
                </span>
              </div>
              <h3 className="font-semibold text-gray-900 mb-1">{c.question}</h3>
              <p className="text-sm text-gray-500 mb-4">{c.lecture}</p>

              <div className="flex flex-wrap gap-4 mb-4">
                <MiniListe
                  titre="Bien au-dessus du pronostic"
                  icon={<ArrowUpRight size={13} className="text-emerald-600" />}
                  items={c.dessus}
                  fmtY={y.fmt}
                />
                <MiniListe
                  titre="Bien en dessous"
                  icon={<ArrowDownRight size={13} className="text-rose-500" />}
                  items={c.dessous}
                  fmtY={y.fmt}
                />
              </div>

              {c.note && (
                <p className="text-xs text-amber-800 bg-amber-50 border border-amber-100 rounded-lg px-3 py-2 mb-4">
                  {c.note}
                </p>
              )}

              <div className="mt-auto flex items-center justify-between gap-2">
                <button
                  onClick={() => onOpen(c.y, c.x)}
                  className="inline-flex items-center gap-1.5 text-sm font-medium text-blue-600 hover:text-blue-700"
                >
                  Voir le nuage complet
                  <ArrowRight size={15} />
                </button>
                <span className="text-[11px] text-gray-400 text-right">
                  Sources :{' '}
                  <a href={y.sourceUrl} target="_blank" rel="noopener noreferrer" className="underline hover:text-gray-600">
                    {y.source}
                  </a>
                  {' · '}
                  <a href={x.sourceUrl} target="_blank" rel="noopener noreferrer" className="underline hover:text-gray-600">
                    {x.source}
                  </a>
                </span>
              </div>
            </div>
          )
        })}
      </div>

      {croisements.length > 6 && (
        <button
          onClick={() => setAll(!all)}
          className="mt-4 inline-flex items-center gap-1.5 text-sm font-medium text-gray-600 hover:text-gray-900"
        >
          {all ? <ChevronUp size={15} /> : <ChevronDown size={15} />}
          {all ? 'Réduire' : `Voir les ${croisements.length - 6} autres croisements`}
        </button>
      )}

      <p className="text-xs text-gray-400 mt-4 max-w-3xl">
        Ces relations comparent des territoires, pas des personnes : une corrélation entre
        communes ne dit rien des individus, et un pronostic n'est pas une cause. Un écart au
        pronostic est une piste à creuser, pas un verdict.
      </p>
    </section>
  )
}
