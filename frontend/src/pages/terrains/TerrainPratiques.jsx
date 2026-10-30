import { useEffect, useMemo, useState } from 'react'
import { Loader2, AlertCircle } from 'lucide-react'
import { useRouteMeta } from '../../lib/meta'
import { titleCase } from '../../lib/territoire'
import ToneCallout from '../../components/ToneCallout'
import ChoroplethMap from '../../components/charts/ChoroplethMap'
import PratiquesCarte from '../../components/charts/PratiquesCarte'
import NuageSimple from '../../components/charts/NuageSimple'

const ACCENT = '#DB2777'
// Identité des blocs (palette validée : daltonisme et contraste), toujours la même d'un graphique à l'autre.
const BLOCS = { Âge: '#2563EB', Diplôme: '#0D9488', Revenu: '#D97706', PCS: '#9333EA', Sexe: '#DB2777', 'Taille de ville': '#9CA3AF' }
const COULEURS_PROJ = {
  Âge: BLOCS.Âge, Diplôme: BLOCS.Diplôme, 'Revenu par personne': BLOCS.Revenu, 'Milieu social': BLOCS.PCS, Sexe: BLOCS.Sexe,
  'Santé et précarité': '#374151',
}
const AXES = {
  gauche: 'Répertoire étroit, le prix',
  droite: 'Répertoire large, la qualité',
  haut: 'Plus âgé, à la maison',
  bas: 'Plus jeune, dehors',
}

const INSEE_PRIX = 'https://www.insee.fr/fr/plan-du-site/famille-bdm/103157792'

const f1 = (v) => (v == null ? 'n/d' : v.toLocaleString('fr-FR', { maximumFractionDigits: 1 }))
const f0 = (v) => (v == null ? 'n/d' : Math.round(v).toLocaleString('fr-FR'))
const sg = (v) => {
  if (v == null) return 'n/d'
  const r = Math.round(Math.abs(v) * 10) / 10
  return r === 0 ? '0' : `${v > 0 ? '+' : '−'}${f1(r)}`
}
const net = (m) => Math.abs(m.b) > m.ic

function Section({ titre, intro, children }) {
  return (
    <section className="mb-14">
      <h2 className="text-2xl font-bold text-gray-900 mb-1">{titre}</h2>
      {intro && <p className="text-gray-600 mb-5 max-w-3xl">{intro}</p>}
      {children}
    </section>
  )
}

function Chiffre({ valeur, texte }) {
  return (
    <div className="bg-gray-50 border border-gray-200 rounded-xl px-4 py-3">
      <div className="text-2xl font-bold text-gray-900">{valeur}</div>
      <div className="text-xs text-gray-500 mt-0.5">{texte}</div>
    </div>
  )
}

// Point et intervalle à 95 % sur une échelle centrée sur zéro.
function LigneIntervalle({ label, sous, b, ic, max, unite, couleur = '#374151', discret = false }) {
  const pos = (v) => 50 + (Math.max(-max, Math.min(max, v)) / max) * 50
  return (
    <div className="flex items-center gap-3 py-1" title={`${label} : ${sg(b)} ${unite} (± ${f1(ic)})`}>
      <div className={`w-32 sm:w-56 shrink-0 text-sm ${discret ? 'text-gray-500' : 'text-gray-800'}`}>
        {label}
        {sous && <span className="text-xs text-gray-400"> · {sous}</span>}
      </div>
      <div className="flex-1 relative h-5 min-w-[60px]">
        <div className="absolute left-1/2 top-0 h-full w-px bg-gray-300" />
        <div
          className="absolute top-1/2 -translate-y-1/2 h-0.5 rounded"
          style={{ left: `${pos(b - ic)}%`, width: `${pos(b + ic) - pos(b - ic)}%`, backgroundColor: discret ? '#D1D5DB' : couleur }}
        />
        <div
          className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 w-2.5 h-2.5 rounded-full ring-2 ring-white"
          style={{ left: `${pos(b)}%`, backgroundColor: discret ? '#9CA3AF' : couleur }}
        />
      </div>
      <div className={`w-[92px] sm:w-28 shrink-0 text-right text-sm ${discret ? 'text-gray-400' : 'font-semibold text-gray-900'}`}>
        {sg(b)} <span className="font-normal text-xs text-gray-400">± {f1(ic)}</span>
      </div>
    </div>
  )
}

function CarteEcart({ e }) {
  const max = Math.max(...e.modeles.map((m) => Math.abs(m.b) + m.ic)) * 1.05
  const unite = e.unite === 'pts' ? 'points' : e.unite
  const fin = e.modeles[e.modeles.length - 1]
  return (
    <div className="bg-white border border-gray-200 rounded-xl p-5">
      <div className="flex items-baseline justify-between gap-3 mb-1">
        <h3 className="font-semibold text-gray-900">{e.label}</h3>
        <span className="text-xs text-gray-400">{unite}, bac +4 comparé à primaire-collège</span>
      </div>
      <p className="text-xs text-gray-500 mb-2">
        {e.niveaux.map((n) => `${n.label} : ${f1(n.v)}${e.unite === 'pts' ? ' %' : ` ${e.unite}`}`).join(' · ')}
      </p>
      {e.modeles.map((m) => (
        <LigneIntervalle key={m.nom} label={m.nom} b={m.b} ic={m.ic} max={max} unite={unite} couleur={BLOCS.Diplôme} discret={!net(m)} />
      ))}
      <p className="text-xs text-gray-500 mt-2">
        {net(fin) ? "L'écart de diplôme reste net une fois tout pris en compte." : "Une fois tout pris en compte, l'écart de diplôme n'est plus distinguable de zéro."}{' '}
        À diplôme égal, le revenu le plus haut comparé au plus bas : {sg(e.revenu_net.b)} {unite} (± {f1(e.revenu_net.ic)})
        {net(e.revenu_net) ? '.' : ', non significatif.'}
      </p>
    </div>
  )
}

function Parts({ lignes }) {
  const max = Math.max(...lignes.map((l) => l.total))
  const noms = Object.keys(BLOCS)
  return (
    <div className="bg-white border border-gray-200 rounded-xl p-5">
      <div className="flex flex-wrap gap-x-4 gap-y-1 mb-4">
        {noms.map((n) => (
          <span key={n} className="inline-flex items-center gap-1.5 text-xs text-gray-600">
            <span className="w-3 h-3 rounded-sm" style={{ backgroundColor: BLOCS[n] }} /> {n}
          </span>
        ))}
      </div>
      <div className="space-y-2.5">
        {lignes.map((l) => (
          <div key={l.id} className="flex items-center gap-3">
            <div className="w-32 sm:w-52 shrink-0 text-sm text-gray-800">{l.label}</div>
            <div className="flex-1 flex gap-0.5 h-4">
              {noms.map((n) => (
                <div
                  key={n}
                  className="h-full first:rounded-l last:rounded-r"
                  title={`${n} : ${f1(l.parts[n])} points`}
                  style={{ width: `${(l.parts[n] / max) * 100}%`, backgroundColor: BLOCS[n] }}
                />
              ))}
            </div>
            <div className="w-14 shrink-0 text-right text-sm font-semibold text-gray-900">{f1(l.total)} %</div>
          </div>
        ))}
      </div>
    </div>
  )
}

const COULEURS_TYPES = ['#2563EB', '#0D9488', '#D97706', '#9333EA']
const net2 = (m) => Math.abs(m.b) > m.ic
const DEFS_CLASSES = ['pcs', 'diplome', 'revenu']

function Verdict({ question, resultat, reponse }) {
  return (
    <div className="flex flex-col sm:flex-row sm:items-baseline gap-x-4 gap-y-0.5 py-2.5">
      <div className="sm:w-72 shrink-0 text-sm font-medium text-gray-900">{question}</div>
      <div className="flex-1 text-sm text-gray-600">{resultat}</div>
      <div className="sm:w-28 shrink-0 sm:text-right text-sm font-semibold text-gray-900">{reponse}</div>
    </div>
  )
}

function TypesParDiplome({ classes }) {
  const diplomes = classes[0].diplomes.map((d) => d.label)
  return (
    <div className="bg-white border border-gray-200 rounded-xl p-5">
      <div className="flex flex-wrap gap-x-4 gap-y-1 mb-4">
        {classes.map((c, i) => (
          <span key={c.nom} className="inline-flex items-center gap-1.5 text-xs text-gray-600">
            <span className="w-3 h-3 rounded-sm" style={{ backgroundColor: COULEURS_TYPES[i] }} /> {c.nom}
          </span>
        ))}
      </div>
      <div className="space-y-2">
        {diplomes.map((d, j) => (
          <div key={d} className="flex items-center gap-3">
            <div className="w-32 sm:w-40 shrink-0 text-sm text-gray-800">{d}</div>
            <div className="flex-1 flex gap-0.5 h-6">
              {classes.map((c, i) => (
                <div
                  key={c.nom}
                  className="h-full first:rounded-l last:rounded-r flex items-center justify-center text-xs font-semibold text-white"
                  title={`${c.nom} : ${f1(c.diplomes[j].v)} %`}
                  style={{ width: `${c.diplomes[j].v}%`, backgroundColor: COULEURS_TYPES[i] }}
                >
                  {c.diplomes[j].v >= 9 ? f0(c.diplomes[j].v) : ''}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
      <div className="grid sm:grid-cols-2 gap-4 mt-5">
        {classes.map((c) => (
          <div key={c.nom} className="text-sm text-gray-600">
            <div className="font-semibold text-gray-900">{c.nom} : {f0(c.part)} % des adultes</div>
            <div>
              En moyenne {f0(c.ampleur)} aliments chaque mois. Plus fréquents qu'en moyenne : {c.plus.join(', ').toLowerCase()}.
              {' '}Plus rares : {c.moins.join(', ').toLowerCase()}.
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function SectionOmnivore({ o, inseeUrl }) {
  const [def, setDef] = useState('pcs')
  const c = o.criteres[def]
  const compo = o.composition[def]
  const parCritere = useMemo(() => [...o.aliments].sort((a, b) => b.part - a.part), [o])
  const g = o.t1.grad.complet
  const r = o.t2.grad.complet
  const sansFl = o.t1.sans_fl.complet
  const { n_maj: nMaj, n_mino: nMino, n_pas_chers: nPasChers, n_chers: nChers } = o.t7
  const large = o.t5.classes[0]
  const vieux = o.t5.classes[1]
  const jeune = o.t5.classes[2]
  const lignesRep = [
    ['Tous les aliments', g], ['Fruits et légumes', o.t1.fl.complet], ['Autres aliments', sansFl],
    ['Aliments majoritaires', nMaj], ['Aliments minoritaires', nMino], ['Aliments pas chers', nPasChers], ['Aliments chers', nChers],
  ]
  const maxRep = Math.max(...lignesRep.map(([, m]) => Math.abs(m.b) + m.ic)) * 1.05
  const parts = (x) => `${x.moins} en dessous, ${x.plus} au-dessus, ${x.nul} sans écart net`
  const pointsPart = o.aliments.map((a) => ({ id: a.id, x: a.part, y: a.ecarts[def].b, label: a.label }))
  const pointsPrix = o.aliments.filter((a) => a.prix != null).map((a) => ({ id: a.id, x: a.prix, y: a.ecarts[def].b, label: a.label }))
  return (
    <Section
      titre="L'omnivore à l'épreuve"
      intro="Pour Pierre Bourdieu, le goût distingue : on se situe aussi par ce qu'on refuse. Pour Richard Peterson, les milieux favorisés seraient devenus omnivores : ils cumulent au lieu d'exclure. Ces thèses ont été bâties sur la musique et la culture. Voici le test sur ce que les Français mangent."
    >
      <div className="bg-white border border-gray-200 rounded-xl px-5 py-2 divide-y divide-gray-100 mb-5">
        <Verdict question="Le répertoire s'élargit-il avec le diplôme ?"
          resultat={`${sg(g.b)} aliments consommés chaque mois sur ${o.t1.total} (± ${f1(g.ic)}), bac +4 comparé à primaire-collège, à âge, sexe, revenu, PCS et ville égaux`}
          reponse={net2(g) ? 'Oui' : 'Non'} />
        <Verdict question="Est-ce un effet du questionnaire ?"
          resultat={`${sg(r.b)} aliments différents (± ${f1(r.ic)}) dans les relevés de 2 ou 3 jours, une mesure indépendante du questionnaire`}
          reponse={net2(r) ? 'Non' : 'Possible'} />
        <Verdict question="Les plus diplômés abandonnent-ils les aliments majoritaires ou pas chers ?"
          resultat={`Ils en consomment plus : ${sg(nMaj.b)} aliments majoritaires (± ${f1(nMaj.ic)}), ${sg(nPasChers.b)} pas chers (± ${f1(nPasChers.ic)})`}
          reponse={o.verdict.conserve_majoritaires && o.verdict.conserve_pas_chers ? 'Non' : 'Oui'} />
        <Verdict question="Se distinguent-ils par des aliments minoritaires ?"
          resultat={`${sg(nMino.b)} aliment (± ${f1(nMino.ic)})`}
          reponse={net2(nMino) ? 'Oui' : 'Non'} />
        <Verdict question="Refusent-ils certains aliments ?"
          resultat={`${o.t4.baisse} baisse nette sur ${o.t1.total} aliments (les boissons énergisantes), contre ${o.t4.hausse} hausses`}
          reponse="Presque pas" />
        <Verdict question="L'écart tient-il sans les fruits et légumes ?"
          resultat={`${sg(sansFl.b)} aliment (± ${f1(sansFl.ic)}). Sur les ${f1(g.b)} aliments d'écart, ${f1(o.t1.fl.complet.b)} sont des fruits et légumes`}
          reponse={net2(sansFl) ? 'Oui' : 'Non'} />
        <Verdict question="L'écart est-il plus fort chez les jeunes ?"
          resultat="Différence entre générations non significative"
          reponse="Non démontré" />
      </div>
      <div className="space-y-3 text-gray-700 max-w-3xl mb-6">
        <p>
          <strong>La thèse tient dans sa version faible.</strong> Les plus diplômés ne rejettent presque rien et cumulent.
          Mais ce n'est pas une conquête d'aliments rares ou coûteux, et à caractéristiques égales l'élargissement passe
          surtout par les fruits et légumes. Cela peut relever autant de la prescription nutritionnelle que de l'éclectisme :
          ces données ne permettent pas de trancher.
        </p>
      </div>
      <div className="bg-white border border-gray-200 rounded-xl p-5 mb-5">
        <div className="text-xs text-gray-400 mb-2">Écart de répertoire, bac +4 comparé à primaire-collège, en nombre d'aliments, à caractéristiques égales, intervalle à 95 %</div>
        {lignesRep.map(([label, m]) => (
          <LigneIntervalle key={label} label={label} b={m.b} ic={m.ic} max={maxRep} unite="aliments" couleur={BLOCS.Diplôme} discret={!net2(m)} />
        ))}
      </div>

      <h3 className="text-lg font-bold text-gray-900 mt-8 mb-1">Que mangent les classes populaires ?</h3>
      <p className="text-gray-600 mb-4 max-w-3xl">
        « Populaire » peut vouloir dire deux choses, qu'on mesure ici séparément et sans classer les aliments à la main.
        <strong> Majoritaire</strong> : consommé au moins une fois par mois par plus de la moitié des adultes
        ({o.n_majoritaires} aliments sur {o.t1.total}). <strong>Pas cher</strong> : sous le prix médian au kilo des {o.n_prix} aliments
        suivis par l'Insee ({f1(o.prix_median)} €). Le résultat ne dépend pas de la définition des classes populaires :
      </p>
      <div className="flex flex-wrap gap-2 mb-4">
        {DEFS_CLASSES.map((k) => (
          <button key={k} type="button" aria-pressed={k === def} onClick={() => setDef(k)}
            className={`px-3 py-1 rounded-full text-sm font-medium border transition-colors ${k === def ? 'text-white' : 'border-gray-200 text-gray-600 hover:bg-gray-50'}`}
            style={k === def ? { backgroundColor: ACCENT, borderColor: ACCENT } : undefined}>
            {o.criteres[k].nom}
          </button>
        ))}
      </div>
      <p className="text-sm text-gray-500 mb-3">
        Comparaison : « {c.lo} » face à « {c.hi} », à âge et sexe égaux. Un écart négatif signifie que les classes
        populaires consomment moins souvent l'aliment.
      </p>
      <div className="space-y-4 mb-4">
        <div className="bg-white border border-gray-200 rounded-xl p-4">
          <h4 className="font-semibold text-gray-900 mb-1">Critère 1 : majoritaire</h4>
          <p className="text-xs text-gray-500 mb-2">Sur {c.majoritaire.n_oui} aliments majoritaires : {parts(c.majoritaire.repartition)}.</p>
          <NuageSimple points={pointsPart} xLabel="Part des adultes consommateurs chaque mois (%)" yLabel="Écart des classes populaires (points)" couleur={ACCENT} height={340} />
        </div>
        <div className="bg-white border border-gray-200 rounded-xl p-4">
          <h4 className="font-semibold text-gray-900 mb-1">Critère 2 : pas cher</h4>
          <p className="text-xs text-gray-500 mb-2">Sur {c.pas_cher.n_oui} aliments pas chers : {parts(c.pas_cher.repartition)}. Lien avec le prix : {c.pas_cher.spearman.p < 0.05 ? 'significatif' : 'non significatif'}.</p>
          <NuageSimple points={pointsPrix} xLabel="Prix Insee 2014-2015 (€/kg ou €/l, échelle logarithmique)" yLabel="Écart des classes populaires (points)" logX couleur={ACCENT} height={340} />
        </div>
      </div>
      <div className="bg-white border border-gray-200 rounded-xl p-5 mb-5 overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-xs text-gray-400">
              <th className="font-medium pb-2 pr-3">Composition du répertoire</th>
              <th className="font-medium pb-2 px-3 text-right">{c.lo}</th>
              <th className="font-medium pb-2 pl-3 text-right">{c.hi}</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {compo.map((l) => (
              <tr key={l.id}>
                <td className="py-1.5 pr-3 text-gray-800">{l.label}</td>
                <td className="py-1.5 px-3 text-right font-semibold text-gray-900">{l.lo.toLocaleString('fr-FR', { maximumFractionDigits: 2 })}</td>
                <td className="py-1.5 pl-3 text-right font-semibold text-gray-900">{l.hi.toLocaleString('fr-FR', { maximumFractionDigits: 2 })}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="space-y-3 text-gray-700 max-w-3xl mb-5">
        <p>
          <strong>Les classes populaires ne correspondent à aucun des deux critères.</strong> Les aliments majoritaires ou
          pas chers ne leur sont pas propres : les classes supérieures en consomment plutôt davantage. Leur répertoire
          a la même composition, avec la même part d'aliments majoritaires et pas chers et le même prix moyen au kilo. Il est
          simplement plus court.
        </p>
        <p>
          Seule une poignée d'aliments sont nettement plus consommés par les classes populaires : les frites, quelle que soit la
          définition, et selon les cas les boissons énergisantes, le riz complet ou le lait.
        </p>
      </div>
      <ToneCallout tone="warn">
        Le prix a des limites fortes. L'Insee ne couvre que {o.n_prix} aliments sur {o.t1.total}, surtout frais : ni frites, ni sodas, ni
        biscuits, ni chips, alors que les frites et les boissons énergisantes sont justement du côté des classes populaires. Un même aliment
        peut aussi coûter très différemment selon la gamme et le magasin, ce que ces prix moyens ne voient pas. Enfin, le prix au kilo
        n'est pas le prix à la calorie, et les deux classent différemment les aliments : le second n'a pas pu être calculé ici.
      </ToneCallout>

      <h3 className="text-lg font-bold text-gray-900 mt-8 mb-1">Quatre façons de manger</h3>
      <p className="text-gray-600 mb-4 max-w-3xl">
        Une classification automatique, sans a priori, regroupe les adultes selon les aliments qu'ils consomment.
        Le répertoire large concerne {f0(large.diplomes[0].v)} % des personnes de niveau primaire-collège et {f0(large.diplomes[3].v)} % des
        bac +4. Aucun groupe ne ressemble à un « snob » qui ne consommerait que des aliments rares ou chers.
      </p>
      <TypesParDiplome classes={o.t5.classes} />
      <p className="text-gray-700 max-w-3xl mt-4">
        Les deux types intermédiaires séparent surtout des générations : « {vieux.nom.toLowerCase()} » regroupe{' '}
        {f0(vieux.ages[2].v)} % des 65 ans et plus, « {jeune.nom.toLowerCase()} » {f0(jeune.ages[0].v)} % des 18-44 ans. Le nombre de
        quatre types est un choix de lisibilité : le découpage reste stable d'une moitié de l'échantillon à l'autre, mais d'autres
        découpages, plus fins, seraient possibles.
      </p>

      <details className="bg-gray-50 border border-gray-200 rounded-xl p-5 text-sm text-gray-600 mt-5">
        <summary className="cursor-pointer font-semibold text-gray-900">Les {o.t1.total} aliments, leur part de consommateurs, leur prix</summary>
        <div className="overflow-x-auto mt-3">
          <table className="w-full text-xs">
            <thead>
              <tr className="text-left text-gray-400">
                <th className="font-medium pb-1 pr-3">Aliment</th>
                <th className="font-medium pb-1 px-2 text-right">Consommateurs</th>
                <th className="font-medium pb-1 px-2 text-right">Prix</th>
                <th className="font-medium pb-1 pl-2 text-right">Écart, {c.nom.toLowerCase()}</th>
              </tr>
            </thead>
            <tbody>
              {parCritere.map((a) => (
                <tr key={a.id} className="border-t border-gray-200">
                  <td className="py-1 pr-3 text-gray-800">{a.label}</td>
                  <td className="py-1 px-2 text-right">{f0(a.part)} %</td>
                  <td className="py-1 px-2 text-right">{a.prix != null ? `${a.prix.toLocaleString('fr-FR', { maximumFractionDigits: 2 })} €` : 'non couvert'}</td>
                  <td className={`py-1 pl-2 text-right ${a.ecarts[def].net ? 'font-semibold text-gray-900' : 'text-gray-400'}`}>{sg(a.ecarts[def].b)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="mt-2">
          Écart en points : classes populaires moins classes supérieures. En gras, les écarts qui résistent à la correction pour
          comparaisons multiples. Prix :{' '}
          <a href={inseeUrl} target="_blank" rel="noopener noreferrer" className="underline hover:text-gray-800">Insee, prix moyens de vente au détail</a>, moyenne 2014-2015.
        </p>
      </details>
      <p className="text-xs text-gray-400 mt-3">
        Références :{' '}
        <a href="https://doi.org/10.2307/2096460" target="_blank" rel="noopener noreferrer" className="underline hover:text-gray-600">Peterson et Kern, 1996</a>
        {' · '}
        <a href="https://doi.org/10.2307/2096459" target="_blank" rel="noopener noreferrer" className="underline hover:text-gray-600">Bryson, 1996</a>
        {' · '}
        <a href="https://research.manchester.ac.uk/en/publications/comsumption-and-the-problem-of-variety-cultural-omnivorousness-so/" target="_blank" rel="noopener noreferrer" className="underline hover:text-gray-600">Warde, Martens et Olsen, 1999</a>.
      </p>
    </Section>
  )
}

function CourbeJugement({ courbe }) {
  const [survol, setSurvol] = useState(null)
  const W = 640
  const H = 300
  const m = { l: 40, r: 74, t: 12, b: 42 }
  const X = (i) => m.l + (i / (courbe.length - 1)) * (W - m.l - m.r)
  const Y = (v) => m.t + (1 - v / 100) * (H - m.t - m.b)
  const serie = (k) => courbe.map((c, i) => (c[k].v == null ? null : [i, c[k].v])).filter(Boolean)
  const SERIES = [
    { k: 'f', nom: 'Femmes', c: BLOCS.Sexe },
    { k: 'h', nom: 'Hommes', c: BLOCS.Âge },
  ]
  const c = survol != null ? courbe[survol] : null
  return (
    <div className="relative">
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full h-auto" role="img" aria-label="Part des personnes qui se jugent trop grosses selon leur indice de masse corporelle, femmes et hommes.">
        {[0, 25, 50, 75, 100].map((v) => (
          <g key={v}>
            <line x1={m.l} x2={W - m.r} y1={Y(v)} y2={Y(v)} stroke="#F3F4F6" />
            <text x={m.l - 6} y={Y(v) + 4} fontSize="11" fill="#6B7280" textAnchor="end">{v} %</text>
          </g>
        ))}
        {courbe.map((b, i) => (
          <text key={b.label} x={X(i)} y={H - m.b + 16} fontSize="11" fill="#6B7280" textAnchor="middle">{b.label}</text>
        ))}
        <text x={(m.l + W - m.r) / 2} y={H - 6} fontSize="11" fill="#6B7280" textAnchor="middle">Indice de masse corporelle (kg/m²)</text>
        {survol != null && <line x1={X(survol)} x2={X(survol)} y1={m.t} y2={H - m.b} stroke="#D1D5DB" />}
        {SERIES.map((s) => {
          const pts = serie(s.k)
          const fin = pts[pts.length - 1]
          return (
            <g key={s.k}>
              <polyline points={pts.map(([i, v]) => `${X(i)},${Y(v)}`).join(' ')} fill="none" stroke={s.c} strokeWidth="2" strokeLinejoin="round" strokeLinecap="round" />
              {pts.map(([i, v]) => <circle key={i} cx={X(i)} cy={Y(v)} r="4" fill={s.c} stroke="#fff" strokeWidth="2" />)}
              <text x={X(fin[0]) + 9} y={Y(fin[1]) + (s.k === 'f' ? -3 : 9)} fontSize="12" fontWeight="600" fill="#374151">{s.nom}</text>
            </g>
          )
        })}
        {courbe.map((b, i) => (
          <rect key={b.label} x={X(i) - (W - m.l - m.r) / (courbe.length - 1) / 2} y={m.t} width={(W - m.l - m.r) / (courbe.length - 1)} height={H - m.t - m.b} fill="transparent"
            onMouseEnter={() => setSurvol(i)} onMouseLeave={() => setSurvol(null)} />
        ))}
      </svg>
      {c && (
        <div className="absolute z-10 pointer-events-none bg-white border border-gray-200 rounded-lg shadow px-3 py-1.5 text-xs text-gray-700"
          style={{ left: `${Math.min(62, (X(survol) / W) * 100)}%`, top: 8 }}>
          <div className="font-semibold text-gray-900">IMC {c.label}</div>
          {SERIES.map((s) => (
            <div key={s.k}>
              {s.nom} : {c[s.k].v == null ? `moins de 30 répondants` : `${f1(c[s.k].v)} % (${c[s.k].n} répondants)`}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function Regions({ data, geo }) {
  const [id, setId] = useState(data[0].id)
  const ind = data.find((d) => d.id === id)
  const nat = ind.national
  const valeurs = useMemo(() => Object.fromEntries(ind.lignes.map((l) => [l.code, l.v])), [ind])
  const lire = (l) => (l.inf > nat.sup ? 'au-dessus' : l.sup < nat.inf ? 'en dessous' : 'pas d\'écart net')
  return (
    <div>
      <div className="flex flex-wrap gap-2 mb-4">
        {data.map((d) => (
          <button key={d.id} type="button" aria-pressed={d.id === id} onClick={() => setId(d.id)}
            className={`px-3 py-1 rounded-full text-sm font-medium border transition-colors ${d.id === id ? 'text-white' : 'border-gray-200 text-gray-600 hover:bg-gray-50'}`}
            style={d.id === id ? { backgroundColor: ACCENT, borderColor: ACCENT } : undefined}>
            {d.label}
          </button>
        ))}
      </div>
      <div className="grid lg:grid-cols-2 gap-5">
        <div className="bg-white border border-gray-200 rounded-xl p-3">
          {geo ? (
            <ChoroplethMap geo={geo} valueByCode={valeurs} label={ind.label} unit="%" format={(v) => `${f1(v)} %`} height={460} fitBounds legendPosition="bottomleft" />
          ) : (
            <div className="h-[460px] flex items-center justify-center text-gray-400"><Loader2 className="animate-spin" size={22} /></div>
          )}
        </div>
        <div className="bg-white border border-gray-200 rounded-xl p-4">
          <div className="text-sm text-gray-600 mb-2">
            {ind.sous}. France : <strong className="text-gray-900">{f1(nat.v)} %</strong> (de {f1(nat.inf)} à {f1(nat.sup)} %)
          </div>
          <div className="divide-y divide-gray-100">
            {ind.lignes.map((l) => {
              const sens = lire(l)
              return (
                <div key={l.code} className="flex items-center justify-between gap-3 py-1 text-sm">
                  <span className="text-gray-800 truncate">{l.nom}</span>
                  <span className="shrink-0 text-right">
                    <strong className="text-gray-900">{f1(l.v)} %</strong>{' '}
                    <span className="text-xs text-gray-400">{f1(l.inf)} à {f1(l.sup)}</span>{' '}
                    <span className="text-xs text-gray-500 inline-block w-[84px] text-right whitespace-nowrap">{sens}</span>
                  </span>
                </div>
              )
            })}
          </div>
        </div>
      </div>
    </div>
  )
}

function Departements({ data, geo }) {
  const [id, setId] = useState(data[0].id)
  const ind = data.find((d) => d.id === id)
  const valeurs = useMemo(() => Object.fromEntries(ind.lignes.map((l) => [l.code, l.std])), [ind])
  const metropole = ind.lignes.filter((l) => l.code.length === 2)
  const colonne = (titre, lignes) => (
    <div>
      <div className="text-xs font-semibold uppercase tracking-wide text-gray-400 mb-1">{titre}</div>
      {lignes.map((l) => (
        <div key={l.code} className="flex justify-between gap-3 py-0.5 text-sm">
          <span className="text-gray-800 truncate">{titleCase(l.nom)}</span>
          <strong className="text-gray-900 shrink-0">{f1(l.std)} %</strong>
        </div>
      ))}
    </div>
  )
  return (
    <div>
      <div className="flex flex-wrap gap-2 mb-4">
        {data.map((d) => (
          <button key={d.id} type="button" aria-pressed={d.id === id} onClick={() => setId(d.id)}
            className={`px-3 py-1 rounded-full text-sm font-medium border transition-colors ${d.id === id ? 'text-white' : 'border-gray-200 text-gray-600 hover:bg-gray-50'}`}
            style={d.id === id ? { backgroundColor: ACCENT, borderColor: ACCENT } : undefined}>
            {d.label}
          </button>
        ))}
      </div>
      <div className="grid lg:grid-cols-2 gap-5">
        <div className="bg-white border border-gray-200 rounded-xl p-3">
          {geo ? (
            <ChoroplethMap geo={geo} valueByCode={valeurs} label={ind.label} unit="%" format={(v) => `${f1(v)} %`} height={460} fitBounds legendPosition="bottomleft" />
          ) : (
            <div className="h-[460px] flex items-center justify-center text-gray-400"><Loader2 className="animate-spin" size={22} /></div>
          )}
        </div>
        <div className="bg-white border border-gray-200 rounded-xl p-4">
          <div className="text-sm text-gray-600 mb-3">
            Part des habitants pris en charge, à âge et sexe égaux. France : <strong className="text-gray-900">{f1(ind.france)} %</strong>
          </div>
          <div className="grid sm:grid-cols-2 gap-5">
            {colonne('Métropole, les plus hauts', metropole.slice(0, 7))}
            {colonne('Métropole, les plus bas', metropole.slice(-7).reverse())}
          </div>
        </div>
      </div>
    </div>
  )
}

export default function TerrainPratiques() {
  useRouteMeta('/terrains/pratiques')
  const [d, setD] = useState(null)
  const [omnivore, setOmnivore] = useState(null)
  const [etat, setEtat] = useState('loading')
  const [geoReg, setGeoReg] = useState(null)
  const [geoDep, setGeoDep] = useState(null)
  const [cible, setCible] = useState('ob')

  useEffect(() => {
    fetch('/data/showcases/pratiques.json')
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then((j) => { setD(j); setEtat('ok') })
      .catch(() => setEtat('error'))
    fetch('/data/showcases/omnivore.json').then((r) => r.json()).then(setOmnivore).catch(() => {})
    fetch('/data/geo/regions.geojson').then((r) => r.json()).then(setGeoReg).catch(() => {})
    fetch('/data/geo/departements.geojson').then((r) => r.json()).then(setGeoDep).catch(() => {})
  }, [])

  const poles = useMemo(() => {
    if (!d) return null
    const m = d.acm.modalites
    const top = (cle, garde) => [...m].filter(garde).sort((a, b) => b[cle] - a[cle]).slice(0, 7).map((x) => x.label).join(', ')
    return {
      gauche: top('ctr1', (x) => x.x < 0), droite: top('ctr1', (x) => x.x > 0),
      bas: top('ctr2', (x) => x.y < 0), haut: top('ctr2', (x) => x.y > 0),
    }
  }, [d])

  if (etat === 'loading')
    return <div className="py-24 text-center text-gray-400"><Loader2 className="animate-spin inline" size={22} /></div>
  if (etat === 'error')
    return (
      <div className="py-24 text-center text-gray-500">
        <AlertCircle className="inline mr-2" size={20} /> Les données de ce dossier n'ont pas pu être chargées.
      </div>
    )

  const { meta, acm, variances, ecarts, activites, jugement, regions, departements } = d
  const ob = ecarts.find((e) => e.id === 'ob')
  const tabac = ecarts.find((e) => e.id === 'fume_j')
  const alcool = ecarts.find((e) => e.id === 'alcool')
  const obFin = ob.modeles[ob.modeles.length - 1]
  const tabacFin = tabac.modeles[tabac.modeles.length - 1]
  const rep = acm.repertoire
  const repDip = rep.diplome
  const pn = jugement.classes.find((c) => c.label === 'Poids normal')
  const sp = jugement.classes.find((c) => c.label === 'Surpoids')
  const lignesAct = activites.lignes.filter((l) => l.y === cible).sort((a, b) => a.b - b.b)
  const cibleInfo = activites.cibles[cible]
  const uniteAct = cibleInfo.unite === 'pts' ? 'points' : cibleInfo.unite
  const maxAct = Math.max(...lignesAct.map((l) => Math.abs(l.b) + l.ic)) * 1.05
  const effectifsReg = regions.flatMap((r) => r.lignes.map((l) => l.n))
  const minReg = Math.round(Math.min(...effectifsReg) / 100) * 100
  const maxReg = Math.round(Math.max(...effectifsReg) / 100) * 100

  return (
    <div className="max-w-5xl mx-auto px-4 py-10">
      <header className="mb-8">
        <div className="text-sm font-semibold uppercase tracking-wide mb-2" style={{ color: ACCENT }}>Modes de vie</div>
        <h1 className="text-4xl font-bold text-gray-900 mb-3">Manger, bouger, fumer : le poids du milieu social</h1>
        <p className="text-lg text-gray-600 max-w-3xl">
          Bio ou promotions, jogging ou bricolage, marché ou grande surface : nos pratiques dessinent une carte.
          Que doit-elle à l'âge, au diplôme, à l'argent ? Et que dit-elle de l'obésité, du tabac, de l'alcool, du
          regard porté sur son corps ?
        </p>
      </header>

      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3 mb-10">
        <Chiffre valeur={`${sg(tabacFin.b)} pts`} texte="de tabac quotidien pour les bac +4 comparés au niveau primaire-collège, à âge, sexe, revenu, PCS et ville égaux" />
        <Chiffre valeur={`${sg(obFin.b)} pts`} texte="d'obésité dans la même comparaison" />
        <Chiffre valeur={`${f1(repDip[0].v)} contre ${f1(repDip[3].v)}`} texte={`aliments jamais consommés sur ${rep.total} suivis : primaire-collège et bac +4`} />
        <Chiffre valeur={`${f0(pn.gros.Femmes.v)} % contre ${f0(pn.gros.Hommes.v)} %`} texte="des femmes et des hommes de corpulence normale (IMC de 18,5 à 25) se jugent trop gros" />
      </div>

      <div className="mb-12">
        <ToneCallout tone="info">
          Deux enquêtes, deux époques. Les pratiques et le corps viennent de l'étude INCA 3 de l'Anses
          ({f0(meta.n_adultes)} adultes, {meta.annees}), les cartes du Baromètre 2024 et de l'Assurance maladie.
          Ces sources ne se croisent pas : on ne peut pas relier une région de la carte à un point de l'analyse. Toutes
          ces données décrivent des liens, jamais des causes.
        </ToneCallout>
      </div>

      <Section
        titre="La carte des pratiques"
        intro={`Chaque point gris est une pratique : deux points proches sont souvent le fait des mêmes personnes. Cette carte est calculée sur ${meta.n_variables} variables et ${f0(meta.n_acm)} adultes, à partir des seules pratiques et représentations. L'âge, le diplôme ou le revenu n'y entrent pas : on les projette ensuite, pour voir où ils tombent.`}
      >
        <div className="bg-white border border-gray-200 rounded-xl p-4 sm:p-5">
          <PratiquesCarte modalites={acm.modalites} projections={acm.projections} couleurs={COULEURS_PROJ} axes={AXES} />
        </div>
        <div className="grid md:grid-cols-2 gap-4 mt-4">
          <div className="text-sm text-gray-600">
            <h3 className="font-semibold text-gray-900 mb-1">Axe horizontal, {f0(acm.axes[0])} % de l'information corrigée</h3>
            <p><strong className="text-gray-800">À gauche :</strong> {poles.gauche}.</p>
            <p className="mt-1"><strong className="text-gray-800">À droite :</strong> {poles.droite}.</p>
          </div>
          <div className="text-sm text-gray-600">
            <h3 className="font-semibold text-gray-900 mb-1">Axe vertical, {f0(acm.axes[1])} %</h3>
            <p><strong className="text-gray-800">En bas :</strong> {poles.bas}.</p>
            <p className="mt-1"><strong className="text-gray-800">En haut :</strong> {poles.haut}.</p>
          </div>
        </div>
        <div className="mt-5 space-y-3 text-gray-700 max-w-3xl">
          <p>
            L'axe horizontal mêle deux choses. Du côté droit, on choisit selon l'origine, les labels, le mode de
            production. Du côté gauche, on choisit selon le prix et surtout, on a écarté plus d'aliments : le nombre
            d'aliments jamais consommés suit de près cet axe (corrélation de −{Math.abs(rep.corr_axe1).toLocaleString('fr-FR')}). C'est
            un résultat proche de « l'omnivore » du sociologue Richard Peterson, à côté de la distinction de Bourdieu :
            en haut de l'échelle des diplômes, on se distingue aussi par l'étendue de ce qu'on mange.
          </p>
          <p>
            Ce répertoire suit le diplôme. À âge, sexe, PCS et ville égaux, un bac +4 écarte{' '}
            {f1(Math.abs(rep.bac4_net.b))} aliment de moins (± {f1(rep.bac4_net.ic)}) qu'une personne de niveau
            primaire-collège, à revenu égal. Sur ces {rep.total} aliments, l'écart entre revenus extrêmes n'est pas
            significatif ({sg(rep.revenu_net.b)}, ± {f1(rep.revenu_net.ic)}), mais l'argent compte aussi : sur une mesure
            plus large{omnivore ? ` (${f0(omnivore.t1.total)} aliments), le revenu ajoute ${sg(omnivore.t1.grad.revenu.b)} aliments (± ${f1(omnivore.t1.grad.revenu.ic)}), et le diplôme ${sg(omnivore.t1.grad.complet.b)} (± ${f1(omnivore.t1.grad.complet.ic)})` : ', le revenu joue aussi'}.
          </p>
          <p>
            L'axe vertical, lui, est surtout une affaire d'âge. Les deux premiers axes n'opposent pas nettement
            capital culturel et capital économique, comme le faisait Bourdieu pour la France des années 1970 :
            diplôme et revenu tirent ici dans le même sens.
          </p>
        </div>
      </Section>

      {omnivore && <SectionOmnivore o={omnivore} inseeUrl={INSEE_PRIX} />}

      <Section
        titre="Ce que le social explique, et ce qu'il n'explique pas"
        intro="Pour chaque pratique ou état de santé, la part des différences entre individus attribuable à chaque caractéristique. Le total ne monte jamais bien haut."
      >
        <Parts lignes={variances} />
        <div className="mt-5 space-y-3 text-gray-700 max-w-3xl">
          <p>
            Le social crée de grands écarts entre groupes, mais il dit peu de choses d'une personne en particulier :
            les caractéristiques mesurées rendent compte de {f1(variances.find((v) => v.id === 'ob').total)} % des
            différences d'obésité. Le reste tient à ce que l'enquête ne voit pas, ou à ce qu'elle mesure mal.
          </p>
          <p>
            Sur l'axe vertical, le poids de la PCS vient en bonne partie des retraités, classés à part dans
            l'enquête : il faut le lire avec l'âge. Pour l'alcool, c'est le sexe qui domine.
          </p>
        </div>
      </Section>

      <Section
        titre="Obésité, tabac, alcool, sucre : l'écart brut, puis l'écart contrôlé"
        intro="Comparaison des bac +4 et du niveau primaire-collège. On retire progressivement ce qui tient à l'âge, au sexe, au revenu, à la PCS et à la ville. Un point gris signale un écart non distinguable de zéro."
      >
        <div className="grid lg:grid-cols-2 gap-4">
          {ecarts.map((e) => <CarteEcart key={e.id} e={e} />)}
        </div>
        <div className="mt-5 space-y-3 text-gray-700 max-w-3xl">
          <p>
            <strong>Le tabac est le cas le plus frappant.</strong> L'écart passe de {sg(tabac.modeles[0].b)} à{' '}
            {sg(tabac.modeles[1].b)} points une fois l'âge pris en compte : les plus âgés, moins souvent diplômés,
            fument aussi beaucoup moins, ce qui masquait une partie de l'écart. Et il tient au diplôme bien plus qu'au
            revenu.
          </p>
          <p>
            <strong>L'obésité recule d'un tiers</strong> ({sg(ob.modeles[0].b)} puis {sg(obFin.b)} points) mais ne
            disparaît pas. <strong>L'alcool ne suit pas le diplôme</strong> : l'écart n'est pas significatif, alors
            que les hommes déclarent {f1(alcool.sexes.find((s) => s.label === 'Hommes').v)} g par jour contre{' '}
            {f1(alcool.sexes.find((s) => s.label === 'Femmes').v)} g pour les femmes.
          </p>
          <p>
            <strong>Le sucre ne raconte pas une histoire simple.</strong> Les plus diplômés mangent plutôt plus de
            produits sucrés (gâteaux, chocolat, glaces) et boivent moins de boissons rafraîchissantes, une catégorie
            qui comprend aussi les boissons sans sucre. Ces quantités sont estimées sur 2 ou 3 jours et les plus petits
            mangeurs sous-déclarent ; le résultat résiste à leur retrait, mais il reste fragile.
          </p>
        </div>
      </Section>

      <Section
        titre="Les activités, à caractéristiques égales"
        intro={`À âge, sexe, diplôme, revenu, PCS et ville égaux, quelle différence entre ceux qui pratiquent et les autres ? ${activites.tests} comparaisons ont été faites, ${activites.retenus} résistent à la correction pour comparaisons multiples : elles seules sont en couleur.`}
      >
        <div className="flex flex-wrap gap-2 mb-3">
          {Object.entries(activites.cibles).map(([k, v]) => (
            <button key={k} type="button" aria-pressed={k === cible} onClick={() => setCible(k)}
              className={`px-3 py-1 rounded-full text-sm font-medium border transition-colors ${k === cible ? 'text-white' : 'border-gray-200 text-gray-600 hover:bg-gray-50'}`}
              style={k === cible ? { backgroundColor: ACCENT, borderColor: ACCENT } : undefined}>
              {v.label}
            </button>
          ))}
        </div>
        <div className="bg-white border border-gray-200 rounded-xl p-5">
          <div className="text-xs text-gray-400 mb-2">Écart avec les non-pratiquants, en {uniteAct}, intervalle à 95 %. Après le nom : nombre de pratiquants dans l'enquête.</div>
          {lignesAct.map((l) => (
            <LigneIntervalle key={l.id} label={l.label} sous={`${f0(l.n1)}`} b={l.b} ic={l.ic} max={maxAct} unite={uniteAct} couleur={ACCENT} discret={!l.retenu} />
          ))}
        </div>
        <div className="mt-4">
          <ToneCallout tone="warn">
            Ces chiffres ne sont pas des effets. Avoir du mal à courir à cause de son poids produit le même écart que
            maigrir en courant, et l'enquête ne permet pas de les séparer. Le contrôle reste aussi imparfait :
            l'âge n'est connu qu'en trois classes (18-44, 45-64, 65 ans et plus), et un joggeur de 25 ans est
            comparé à une personne de 44 ans. Les écarts avec des pratiques peu fréquentes, comme la danse de salon,
            sont à lire avec une prudence particulière.
          </ToneCallout>
        </div>
      </Section>

      <Section
        titre="Le regard sur son propre corps"
        intro="L'enquête demande à chacun s'il se trouve d'un poids normal, trop gros ou trop maigre. Elle ne dit rien du regard porté sur les autres."
      >
        <div className="bg-white border border-gray-200 rounded-xl p-5">
          <CourbeJugement courbe={jugement.courbe} />
        </div>
        <div className="mt-5 space-y-3 text-gray-700 max-w-3xl">
          <p>
            On compare ici à corpulence égale, pas à poids égal : 70 kg ne pèsent pas la même chose sur 1,60 m et sur
            1,80 m, et les femmes sont en moyenne plus petites. L'indice de masse corporelle (IMC) rapporte le poids à la
            taille. Or à IMC égal, le verdict change selon le sexe. Parmi les personnes de corpulence normale,{' '}
            {f1(pn.gros.Femmes.v)} % des femmes se trouvent trop grosses, contre {f1(pn.gros.Hommes.v)} % des hommes. En
            surpoids, c'est {f1(sp.gros.Femmes.v)} % contre {f1(sp.gros.Hommes.v)} %. Les courbes ne se rejoignent qu'à
            partir de l'obésité.
          </p>
          <p>
            À IMC, âge, diplôme et revenu égaux, les hommes se jugent trop gros {f1(Math.abs(jugement.net.homme.b))} points
            moins souvent (± {f1(jugement.net.homme.ic)}). L'écart entre bac +4 et primaire-collège, lui, n'est pas
            significatif ({sg(jugement.net.bac4.b)}, ± {f1(jugement.net.bac4.ic)}) : sur ce terrain, le sexe pèse
            plus que le diplôme. L'écart entre femmes et hommes tient aussi à poids et taille égaux ({sg(jugement.net.homme_poids_taille.b)}{' '}
            points, ± {f1(jugement.net.homme_poids_taille.ic)}).
          </p>
          <p>
            Une limite compte ici : l'IMC ne distingue pas le muscle de la graisse. À IMC égal, les femmes ont en moyenne
            une part de masse grasse plus élevée que les hommes, et l'enquête ne la mesure pas. Une partie de l'écart peut
            donc tenir à une différence réelle de composition du corps, et pas seulement à un regard plus sévère. L'IMC
            n'est pas non plus, à lui seul, un diagnostic de santé.
          </p>
        </div>
      </Section>

      <Section
        titre="Addictions et pratiques, région par région"
        intro={`Baromètre de Santé publique France 2024 : de ${f0(minReg)} à ${f0(maxReg)} répondants par région. Une région n'est dite au-dessus ou en dessous de la France que si son intervalle de confiance ne recouvre pas celui du pays. Mayotte n'est pas couverte, et l'outre-mer figure dans la liste mais pas sur la carte.`}
      >
        <Regions data={regions} geo={geoReg} />
      </Section>

      <Section
        titre="Les prises en charge, département par département"
        intro="Assurance maladie 2024. Les taux sont standardisés : ils comparent les départements comme s'ils avaient la même pyramide des âges."
      >
        <Departements data={departements} geo={geoDep} />
        <div className="mt-4">
          <ToneCallout tone="warn">
            Ces chiffres comptent des personnes prises en charge par le système de soins, pas des personnes malades.
            Un taux bas de troubles addictifs peut signaler peu de cas comme peu de recours aux soins : c'est sans doute
            une partie de ce qu'on observe en outre-mer, tout en bas de ce classement.
          </ToneCallout>
        </div>
      </Section>

      <details className="bg-gray-50 border border-gray-200 rounded-xl p-5 text-sm text-gray-600 mb-8">
        <summary className="cursor-pointer font-semibold text-gray-900">Méthode et limites</summary>
        <div className="mt-3 space-y-2">
          <p>
            <strong>Population.</strong> Adultes de 18 à 79 ans ayant rempli les questionnaires d'INCA 3. Consommations
            journalières sur {f0(meta.n_conso)} d'entre eux, à partir de 2 ou 3 jours de rappels. Données déclaratives, sauf
            le poids et la taille, mesurés pour la plupart.
          </p>
          <p>
            <strong>Carte.</strong> Analyse des correspondances multiples pondérée, taux d'inertie corrigés de Benzécri ;
            sur 200 rééchantillonnages, la corrélation des coordonnées avec celles de la carte publiée reste au moins de{' '}
            {f1(acm.stabilite[0])} pour les deux axes dans 95 % des cas. Les réponses manquantes (2 % en moyenne) sont
            remplacées par la modalité la plus fréquente, et les personnes à plus de 10 % de réponses manquantes écartées.
          </p>
          <p>
            <strong>Part de variance.</strong> Valeurs de Shapley du R² pondéré, qui répartissent équitablement ce que les
            caractéristiques expliquent en commun.
          </p>
          <p>
            <strong>Écarts.</strong> Moindres carrés pondérés, intervalles à 95 % tenant compte des strates et des unités
            primaires du plan de sondage. Correction de Benjamini-Hochberg pour les {activites.tests} comparaisons
            d'activités (seuil de 10 %). Aucune donnée d'enquête ne permet ici de conclure à une cause.
          </p>
          {omnivore && (
            <p>
              <strong>Test de l'omnivore.</strong> {omnivore.t1.total} aliments du questionnaire, sans totaux ni variantes de
              saison, comptés dès lors qu'ils sont consommés au moins une fois par mois. Les critères « majoritaire » et « pas
              cher » sont fixés sans regarder le lien avec le milieu social. Classes populaires et supérieures sont comparées selon
              trois définitions : PCS (les retraités, classés à part par l'enquête, en sont exclus), diplôme, revenu. Le lien
              entre l'écart d'un aliment et ses critères est testé par permutation, et comparé aussi à l'intérieur de chaque
              famille d'aliments. Résultats inchangés à un seuil annuel, sans porc ni alcool et hors régimes. Classes
              latentes : mélange de lois de Bernoulli pondéré ; le critère BIC favorise plus de quatre classes, ce chiffre est un
              choix de lisibilité. Une seule enquête ne permet pas de tester le récit historique de Peterson.
            </p>
          )}
          <p>
            <strong>Assurance maladie.</strong> Standardisation indirecte par âge et sexe, les petits effectifs étant masqués
            dans la source. Licence ODbL.
          </p>
        </div>
      </details>

      <p className="text-xs text-gray-400">
        Sources :{' '}
        <a href={meta.inca_url} target="_blank" rel="noopener noreferrer" className="underline hover:text-gray-600">Anses, étude INCA 3 (2014-2015), data.gouv.fr</a>
        {' · '}
        <a href={meta.barometre_url} target="_blank" rel="noopener noreferrer" className="underline hover:text-gray-600">Santé publique France, Baromètre 2024, Odissé</a>
        {' · '}
        <a href={meta.ameli_url} target="_blank" rel="noopener noreferrer" className="underline hover:text-gray-600">Assurance maladie, effectifs de patients par pathologie, 2024</a>
        {' · '}
        <a href={INSEE_PRIX} target="_blank" rel="noopener noreferrer" className="underline hover:text-gray-600">Insee, prix moyens de vente au détail, 2014-2015</a>.
      </p>
    </div>
  )
}
