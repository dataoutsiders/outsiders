import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Loader2, AlertCircle, ArrowRight, Filter, Info, Globe, Map } from 'lucide-react'
import { useRouteMeta } from '../../lib/meta'

const COLORS = { vert: '#10B981', rouge: '#EF4444', bleu: '#3B82F6', gris: '#9CA3AF', orange: '#F59E0B' }

// Codes outre-mer : 97x/98x, ou tout code à 3 caractères commençant par 9.
const isOutremer = (code) => {
  const c = String(code || '')
  return /^9[78]/.test(c) || (c.length > 2 && c[0] === '9')
}

// Barre horizontale simple (label + valeur), largeur proportionnelle.
function RankBar({ label, sub, value, max, color, suffix = '%' }) {
  const w = max ? Math.max(2, (value / max) * 100) : 0
  return (
    <div className="flex items-center gap-3 py-1">
      <div className="w-44 shrink-0 text-sm text-gray-700 truncate" title={label}>
        {label}
        {sub && <span className="text-gray-400"> · {sub}</span>}
      </div>
      <div className="flex-1 bg-gray-100 rounded-full h-5 overflow-hidden">
        <div
          className="h-full rounded-full flex items-center justify-end pr-2"
          style={{ width: `${w}%`, backgroundColor: color }}
        >
          <span className="text-[11px] font-medium text-white">
            {value}
            {suffix}
          </span>
        </div>
      </div>
    </div>
  )
}

const pct1 = (x) => (x == null ? 'n/d' : `${x.toFixed(1).replace('.', ',')} %`)

// Une étape du filtre : le taux observé, comparé au taux attendu d'après les candidats
// de la même commune (ou de la même liste). L'écart entre les deux barres est le filtre
// propre à l'étape, une fois la géographie neutralisée.
function FiltreLigne({ etape, observe, attendu, attenduLabel, max }) {
  const w = (v) => (max && v != null ? Math.max(1.5, (v / max) * 100) : 0)
  return (
    <div className="py-3 border-b border-gray-100 last:border-0">
      <div className="text-sm font-semibold text-gray-900 mb-1.5">{etape}</div>
      <div className="flex items-center gap-3 mb-1">
        <span className="w-40 shrink-0 text-xs text-gray-600">Observé</span>
        <div className="flex-1 h-4 bg-gray-100 rounded-full overflow-hidden">
          <div className="h-full rounded-full bg-blue-600" style={{ width: `${w(observe)}%` }} />
        </div>
        <span className="w-14 shrink-0 text-right text-sm font-semibold text-gray-800">{pct1(observe)}</span>
      </div>
      <div className="flex items-center gap-3">
        <span className="w-40 shrink-0 text-xs text-gray-500">{attenduLabel}</span>
        <div className="flex-1 h-4 bg-gray-100 rounded-full overflow-hidden">
          <div className="h-full rounded-full bg-gray-400" style={{ width: `${w(attendu)}%` }} />
        </div>
        <span className="w-14 shrink-0 text-right text-sm text-gray-600">{pct1(attendu)}</span>
      </div>
    </div>
  )
}

function Section({ title, description, children }) {
  return (
    <section className="mb-12">
      <h2 className="text-2xl font-bold text-gray-900 mb-1">{title}</h2>
      {description && <p className="text-gray-600 mb-5">{description}</p>}
      {children}
    </section>
  )
}

// Barre « candidats » + repère ▲ pour les têtes de liste (même échelle).
// En dessous de 10 têtes au nom reconnu, on n'affiche pas de valeur (non fiable)
// mais on indique combien de têtes de liste le parti comptait réellement.
function PartiBar({ label, listes, tetes, nTetes, nTetesTotal, max }) {
  const f = (x) => x.toFixed(1).replace('.', ',')
  const barW = max ? Math.max(1.5, (listes / max) * 100) : 0
  const reliable = tetes != null && nTetes >= 10
  const markX = reliable && max ? (tetes / max) * 100 : null
  return (
    <div className="flex items-center gap-3 pt-5 pb-1">
      <div className="w-44 shrink-0 text-sm text-gray-700 truncate" title={label}>
        {label}
      </div>
      <div className="flex-1 relative h-6 bg-gray-100 rounded-full">
        <div
          className="absolute left-0 top-0 h-full rounded-full bg-blue-500"
          style={{ width: `${barW}%` }}
        />
        {markX != null && (
          <div
            className="absolute top-0 h-full flex flex-col items-center"
            style={{ left: `${markX}%`, transform: 'translateX(-50%)' }}
          >
            <span className="absolute -top-4 text-[10px] font-medium text-gray-700 whitespace-nowrap">
              ▲ {f(tetes)}
            </span>
            <div className="w-px h-full bg-gray-900" />
          </div>
        )}
        {!reliable && (
          <span
            className="absolute -top-4 right-1 text-[10px] italic text-gray-400 whitespace-nowrap"
            title="Trop peu de têtes de liste reconnues pour une statistique fiable"
          >
            ▲ n/d · {nTetesTotal} têtes seulement
          </span>
        )}
      </div>
      <div className="w-10 shrink-0 text-right text-sm font-semibold text-gray-800">{f(listes)}</div>
    </div>
  )
}

export default function TerrainElus() {
  useRouteMeta('/terrains/elus')
  const [data, setData] = useState(null)
  const [state, setState] = useState('loading')

  useEffect(() => {
    fetch('/data/showcases/elus-diversite.json')
      .then((r) => r.json())
      .then((d) => {
        setData(d)
        setState('ready')
      })
      .catch(() => setState('error'))
  }, [])

  if (state === 'loading')
    return (
      <div className="py-20 text-center text-gray-500">
        <Loader2 className="animate-spin inline" size={22} /> Chargement des données…
      </div>
    )
  if (state === 'error')
    return (
      <div className="py-20 text-center text-red-600">
        <AlertCircle className="inline" size={22} /> Données indisponibles.
      </div>
    )

  const fl = data.filtre
  const evo = data.evolution
  const elus = evo.lignes[evo.lignes.length - 1]
  const filtreMax = Math.max(fl.candidats, fl.tetes_attendu_liste, fl.conseillers_attendu_commune, fl.maires_attendu_candidats_commune)
  const rneDate = (data.funnel[data.funnel.length - 1].source || '').replace('Répertoire national des élus, ', '')
  const depTop = data.departements.slice(0, 12)
  const depBottom = data.departements.slice(-12).reverse()
  const depMax = data.departements[0].idp
  const partiMax = Math.max(
    ...data.partis.flatMap((p) => [p.idp_listes, p.n_tetes >= 10 ? p.idp_tetes : 0]),
  )

  return (
    <div className="py-12 px-4">
      <div className="max-w-4xl mx-auto">
        {/* En-tête */}
        <header className="mb-10">
          <div className="flex items-center gap-2 text-emerald-600 mb-2">
            <Globe size={20} />
            <span className="text-sm font-semibold uppercase tracking-wide">Démonstration</span>
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-3">{data.titre}</h1>
          <p className="text-xl text-gray-600">
            En appliquant l'outil de représentativité aux {data.national.n.toLocaleString('fr-FR')}{' '}
            candidats des municipales 2026, et en les comparant à 2020, deux constats : la diversité
            des noms progresse dans la politique locale, lentement, et elle se perd surtout au moment
            de choisir qui conduit la liste. L'indice IDP est un indicateur de groupe calculé sur les
            noms : il ne dit rien d'une personne, et un nom n'est pas une origine.
          </p>
        </header>

        {/* Chiffres clés */}
        <div className="grid sm:grid-cols-3 gap-4 mb-12">
          <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-5">
            <div className="text-3xl font-bold text-emerald-700">{data.national.idp}%</div>
            <div className="text-sm text-emerald-900">IDP des candidats (vs 7 % en population)</div>
          </div>
          <div className="bg-violet-50 border border-violet-200 rounded-xl p-5">
            <div className="text-3xl font-bold text-violet-700">{data.national.feminisation}%</div>
            <div className="text-sm text-violet-900">de femmes parmi les candidats</div>
          </div>
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-5">
            <div className="text-3xl font-bold text-blue-700">
              {pct1(elus.idp_2020).replace(' %', '')} → {pct1(elus.idp_2026)}
            </div>
            <div className="text-sm text-blue-900">
              de noms classés « diversité » parmi les conseillers élus au premier tour, de 2020 à 2026,
              dans les mêmes communes de 1 000 habitants et plus
            </div>
          </div>
        </div>

        {/* Évolution 2020 -> 2026 */}
        <Section
          title="De 2020 à 2026 : une progression lente"
          description={`Dans les ${evo.n_communes.toLocaleString('fr-FR')} communes de métropole qui élisaient déjà leur conseil au scrutin de liste en 2020 (1 000 habitants et plus), la part des noms classés « diversité » augmente à chaque niveau. Elle reste loin des 7 % de la population.`}
        >
          <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 text-gray-600">
                <tr>
                  <th className="text-left font-medium px-4 py-2">Niveau</th>
                  <th className="text-right font-medium px-4 py-2">2020</th>
                  <th className="text-right font-medium px-4 py-2">2026</th>
                  <th className="text-right font-medium px-4 py-2">Évolution</th>
                </tr>
              </thead>
              <tbody>
                {evo.lignes.map((l) => (
                  <tr key={l.etape} className="border-t border-gray-100">
                    <td className="px-4 py-2 text-gray-800">
                      {l.etape}
                      <span className="block text-xs text-gray-400">
                        {l.n_2020.toLocaleString('fr-FR')} en 2020, {l.n_2026.toLocaleString('fr-FR')} en 2026
                      </span>
                    </td>
                    <td className="px-4 py-2 text-right tabular-nums">{pct1(l.idp_2020)}</td>
                    <td className="px-4 py-2 text-right tabular-nums font-semibold">{pct1(l.idp_2026)}</td>
                    <td className="px-4 py-2 text-right tabular-nums text-gray-600">
                      +{(l.idp_2026 - l.idp_2020).toFixed(1).replace('.', ',')} pt
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="text-xs text-gray-500 mt-3">
            Élus : premier tour seulement, dans les {evo.n_communes_elus.toLocaleString('fr-FR')} communes
            pourvues dès le premier tour en 2020 et en 2026 (le second tour de 2020 s'est tenu en juin,
            sous Covid). Une partie de la hausse peut tenir au renouvellement des générations : le
            référentiel repère des noms devenus fréquents après 1950, plus présents chez les plus jeunes.
            Les maires ne sont pas comparés : la liste publiée en juin 2020 mêle des maires élus en 2014
            et en 2020. Sources :{' '}
            {evo.sources.map((src, i) => (
              <span key={src.url}>
                {i > 0 && ' · '}
                <a href={src.url} target="_blank" rel="noopener noreferrer" className="underline hover:text-gray-700">
                  {src.label}
                </a>
              </span>
            ))}
            .
          </p>
        </Section>

        {/* Où se joue le filtre */}
        <Section
          title="Où se perd la diversité ?"
          description={`Des candidats (${pct1(fl.candidats)}) aux maires (${pct1(fl.maires)}), la part des noms classés « diversité » est divisée par ${fl.rapport_brut.toFixed(1).replace('.', ',')}. Mais cet écart brut mélange deux choses.`}
        >
          <div className="grid md:grid-cols-2 gap-4 mb-5">
            <div className="bg-gray-50 border border-gray-200 rounded-xl p-5 text-sm text-gray-700">
              <strong className="text-gray-900">La géographie.</strong> Ces candidats sont concentrés
              dans les grandes villes, où les listes et les candidats sont nombreux, alors que chaque
              commune, souvent rurale, n'a qu'un maire. Compté commune par commune (chaque commune
              pèse autant), le taux des candidats n'est que de {pct1(fl.candidats_moyenne_communes)}.
            </div>
            <div className="bg-gray-50 border border-gray-200 rounded-xl p-5 text-sm text-gray-700">
              <strong className="text-gray-900">La sélection.</strong> Comparé aux candidats de sa
              propre commune, le maire porte un nom classé « diversité » {fl.rapport_commune.toFixed(1).replace('.', ',')} fois
              moins souvent. Le filtre se joue surtout au choix de la tête de liste ; à l'élection
              elle-même, les conseillers élus ressemblent presque aux candidats de leur commune.
            </div>
          </div>
          <div className="bg-white border border-gray-200 rounded-xl px-6 py-2">
            <FiltreLigne
              etape="Têtes de liste"
              observe={fl.tetes}
              attendu={fl.tetes_attendu_liste}
              attenduLabel="Candidats de leur liste"
              max={filtreMax}
            />
            <FiltreLigne
              etape="Conseillers municipaux élus"
              observe={fl.conseillers}
              attendu={fl.conseillers_attendu_commune}
              attenduLabel="Candidats de leur commune"
              max={filtreMax}
            />
            <FiltreLigne
              etape="Maires"
              observe={fl.maires}
              attendu={fl.maires_attendu_candidats_commune}
              attenduLabel="Candidats de leur commune"
              max={filtreMax}
            />
          </div>
          <p className="text-xs text-gray-500 mt-3">
            Lecture : {pct1(fl.tetes)} des têtes de liste portent un nom classé « diversité », contre{' '}
            {pct1(fl.tetes_attendu_liste)} des candidats de leur propre liste. Parmi les têtes de liste
            de leur commune, le taux est de {pct1(fl.maires_attendu_tetes_commune)}, proche de celui des
            maires ({pct1(fl.maires)}). Candidats : municipales 2026, premier tour ; élus : Répertoire
            national des élus du {rneDate}.
          </p>
        </Section>

        {/* Carte → Atlas (carte unique) */}
        <Section
          title="La carte de la diversité"
          description="La géographie de la diversité des candidats se lit dans l'Atlas, du département au détail commune par commune, et croisable avec le revenu, le prix immobilier ou l'IPS."
        >
          <Link
            to="/atlas?i=idp"
            className="group flex items-center gap-4 bg-gradient-to-r from-emerald-50 to-white border border-emerald-200 rounded-xl p-6 hover:shadow-md transition-all"
          >
            <div className="p-3 rounded-lg bg-emerald-100 shrink-0">
              <Map size={24} className="text-emerald-600" />
            </div>
            <div className="flex-1">
              <div className="font-semibold text-gray-900 group-hover:text-emerald-700 transition-colors">
                Voir la diversité des candidats sur la carte de France
              </div>
              <div className="text-sm text-gray-600">
                Choroplèthe par département, zoom commune par commune, croisement avec d'autres
                indicateurs.
              </div>
            </div>
            <ArrowRight size={20} className="text-emerald-600 shrink-0 group-hover:translate-x-0.5 transition-transform" />
          </Link>
        </Section>

        {/* Départements */}
        <Section
          title="Où la diversité est-elle la plus forte ?"
          description="IDP des candidats par département. Les départements d'outre-mer (signalés) sont un cas particulier, voir la note plus bas."
        >
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-white border border-gray-200 rounded-xl p-6">
              <h3 className="font-semibold text-gray-900 mb-3">Les 12 plus divers</h3>
              {depTop.map((d) => (
                <RankBar
                  key={d.code}
                  label={`${d.nom}${isOutremer(d.code) ? ' *' : ''}`}
                  value={d.idp}
                  max={depMax}
                  color={COLORS.vert}
                />
              ))}
            </div>
            <div className="bg-white border border-gray-200 rounded-xl p-6">
              <h3 className="font-semibold text-gray-900 mb-3">Les 12 moins divers</h3>
              {depBottom.map((d) => (
                <RankBar
                  key={d.code}
                  label={`${d.nom}${isOutremer(d.code) ? ' *' : ''}`}
                  value={d.idp}
                  max={depMax}
                  color={COLORS.gris}
                />
              ))}
            </div>
          </div>
        </Section>

        {/* Communes */}
        <Section
          title="Les communes aux extrêmes"
          description={`Parmi les ${data.communes.n_communes.toLocaleString('fr-FR')} communes d'au moins ${data.communes.seuil} candidats reconnus.`}
        >
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-white border border-gray-200 rounded-xl p-6">
              <h3 className="font-semibold text-gray-900 mb-3">Top 15 : diversité la plus forte</h3>
              {data.communes.top.map((c) => (
                <RankBar
                  key={c.code}
                  label={c.nom}
                  sub={c.departement}
                  value={c.idp}
                  max={data.communes.top[0].idp}
                  color={COLORS.vert}
                />
              ))}
            </div>
            <div className="bg-white border border-gray-200 rounded-xl p-6">
              <h3 className="font-semibold text-gray-900 mb-3">Bottom 15 : diversité la plus faible</h3>
              {data.communes.bottom.map((c) => (
                <RankBar
                  key={c.code}
                  label={c.nom}
                  sub={c.departement}
                  value={c.idp}
                  max={data.communes.top[0].idp}
                  color={COLORS.gris}
                />
              ))}
            </div>
          </div>
        </Section>

        {/* Partis */}
        <Section
          title="La diversité selon le parti"
          description="IDP par nuance politique (listes d'au moins 200 candidats reconnus). Le repère ▲ marque l'IDP parmi les seules têtes de liste. L'écart avec la barre mêle le choix des têtes de liste et la géographie : les listes des grandes villes comptent plus de candidats, et pèsent donc plus dans la barre que dans le repère."
        >
          <div className="bg-white border border-gray-200 rounded-xl p-6">
            <div className="flex items-center gap-4 text-xs text-gray-500 mb-1">
              <span className="inline-flex items-center gap-1.5">
                <span className="inline-block w-3 h-3 rounded-sm bg-blue-500" /> candidats des listes
              </span>
              <span className="inline-flex items-center gap-1.5">
                <span className="inline-block w-px h-3 bg-gray-900" /> ▲ têtes de liste
              </span>
            </div>
            {data.partis.map((p) => (
              <PartiBar
                key={p.nuance}
                label={p.label}
                listes={p.idp_listes}
                tetes={p.idp_tetes}
                nTetes={p.n_tetes}
                nTetesTotal={p.n_tetes_total}
                max={partiMax}
              />
            ))}
            <p className="text-xs text-gray-400 mt-4">
              ▲ n/d : moins de 10 têtes de liste au nom reconnu, effectif trop faible pour une
              statistique fiable (ex. Horizons ne mène que 7 listes).
            </p>
          </div>
        </Section>

        {/* Note outre-mer + méthode */}
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-5 mb-8 flex items-start gap-3">
          <Info className="text-amber-600 shrink-0 mt-0.5" size={20} />
          <div className="text-sm text-amber-900">
            <strong>* Outre-mer et limite de l'IDP.</strong> L'IDP mesure la trace des migrations
            <em> postérieures à 1950</em>. Mayotte ressort très haut (noms francisés récemment),
            tandis que la Martinique ou la Guadeloupe ressortent très bas alors que leur population
            est largement afro-descendante : leurs noms ont été inscrits à l'état civil <em>avant</em>{' '}
            1950. L'IDP capte donc l'immigration récente, pas toute la diversité, à lire avec ce
            recul. C'est un indicateur de groupe : il ne dit rien d'une personne, et un nom n'est pas
            une origine.
          </div>
        </div>

        {/* CTA vers l'outil */}
        <div className="bg-gray-900 rounded-xl p-8 text-center">
          <Filter className="text-emerald-400 inline mb-3" size={28} />
          <h3 className="text-xl font-bold text-white mb-2">Faites le calcul sur vos propres données</h3>
          <p className="text-gray-300 mb-5">
            La même méthode, sur votre fichier, élus, salariés, adhérents, directement dans votre
            navigateur.
          </p>
          <Link
            to="/outils/representativite"
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-emerald-500 text-white font-medium rounded-lg hover:bg-emerald-600 transition-colors"
          >
            Ouvrir l'outil <ArrowRight size={18} />
          </Link>
        </div>

        <p className="text-xs text-gray-400 mt-6">
          <a
            href="https://www.data.gouv.fr/datasets/elections-municipales-2026-listes-candidates-au-premier-tour"
            target="_blank"
            rel="noopener noreferrer"
            className="underline hover:text-gray-600"
          >
            {data.source}
          </a>
          {' · '}
          <a
            href="https://www.data.gouv.fr/datasets/repertoire-national-des-elus-1"
            target="_blank"
            rel="noopener noreferrer"
            className="underline hover:text-gray-600"
          >
            Répertoire national des élus
          </a>
        </p>
      </div>
    </div>
  )
}
