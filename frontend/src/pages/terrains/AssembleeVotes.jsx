import { useEffect, useMemo, useState } from 'react'
import ToneCallout from '../../components/ToneCallout'

// Couleurs des groupes : les mêmes que dans le reste du dossier Assemblée.
const COULEURS = {
  GDR: '#991B1B', 'LFI-NFP': '#DC2626', ECOS: '#16A34A', SOC: '#EC4899', LIOT: '#0D9488', DEM: '#F97316',
  EPR: '#EAB308', HOR: '#38BDF8', DR: '#2563EB', UDDPLR: '#4338CA', RN: '#1E3A8A',
}
const f1 = (v) => (v == null ? 'n/d' : v.toLocaleString('fr-FR', { maximumFractionDigits: 1 }))
const f0 = (v) => (v == null ? 'n/d' : Math.round(v).toLocaleString('fr-FR'))
const sg = (v) => {
  const r = Math.round(Math.abs(v) * 10) / 10
  return r === 0 ? '0' : `${v > 0 ? '+' : '−'}${f1(r)}`
}
const net = (m) => Math.abs(m.b) > m.ic
const lien = 'underline hover:text-gray-600'

// Une seule teinte, du clair au foncé, pour l'accord en pourcentage.
function cellule(v) {
  if (v == null) return { backgroundColor: '#F9FAFB', color: '#9CA3AF' }
  const t = Math.max(0, Math.min(1, v / 100))
  const m = (a, b) => Math.round(a + (b - a) * t)
  return { backgroundColor: `rgb(${m(239, 30)},${m(246, 64)},${m(255, 175)})`, color: v >= 55 ? '#fff' : '#1F2937' }
}

function Titre({ titre, intro }) {
  return (
    <>
      <h3 className="text-xl font-bold text-gray-900 mt-10 mb-1">{titre}</h3>
      {intro && <p className="text-gray-600 mb-4 max-w-3xl">{intro}</p>}
    </>
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

function Matrice({ d, theme }) {
  const m = theme === 'tous' ? d.matrice : d.themes[theme].matrice
  const g = d.groupes_ordre
  return (
    <div className="overflow-x-auto">
      <table className="text-xs border-separate" style={{ borderSpacing: 2 }}>
        <thead>
          <tr>
            <th />
            {g.map((x) => (
              <th key={x} className="font-medium text-gray-500 px-1 pb-1 w-12 align-bottom">{d.noms[x].replace('Droite républicaine', 'Droite rép.').replace('Écologistes', 'Écolos')}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {g.map((x, i) => (
            <tr key={x}>
              <th className="text-left font-medium text-gray-700 pr-2 whitespace-nowrap">{d.noms[x]}</th>
              {g.map((y, j) => (
                <td key={y} className="text-center font-semibold h-8 w-12 rounded" style={i === j ? { backgroundColor: '#F3F4F6' } : cellule(m[i][j])}
                  title={i === j ? d.noms[x] : `${d.noms[x]} et ${d.noms[y]} : ${m[i][j] == null ? 'moins de 15 scrutins communs' : `${m[i][j]} %`}`}>
                  {i === j ? '' : m[i][j] ?? '·'}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function CarteDeputes({ axes, noms }) {
  const W = 760
  const H = 440
  const pad = 16
  const [survol, setSurvol] = useState(null)
  const { X, Y, labels } = useMemo(() => {
    const xs = axes.points.map((p) => p[0])
    const ys = axes.points.map((p) => p[1])
    const [x0, x1] = [Math.min(...xs) - 2, Math.max(...xs) + 2]
    const [y0, y1] = [Math.min(...ys) - 2, Math.max(...ys) + 2]
    const X = (v) => pad + ((v - x0) / (x1 - x0)) * (W - 2 * pad)
    const Y = (v) => pad + (1 - (v - y0) / (y1 - y0)) * (H - 2 * pad)
    const pris = []
    const labels = Object.entries(axes.centres).map(([g, [a, b]]) => {
      const t = noms[g]
      const w = t.length * 7.2
      for (const [dx, dy] of [[0, -14], [0, 20], [-w / 2 - 12, 4], [w / 2 + 12, 4], [0, -30], [0, 36]]) {
        const box = { x: X(a) + dx - w / 2, y: Y(b) + dy - 12, w, h: 15 }
        if (!pris.some((o) => box.x < o.x + o.w && o.x < box.x + box.w && box.y < o.y + o.h && o.y < box.y + box.h)) {
          pris.push(box)
          return { g, t, x: X(a) + dx, y: Y(b) + dy, cx: X(a), cy: Y(b) }
        }
      }
      return { g, t, x: X(a), y: Y(b) - 14, cx: X(a), cy: Y(b) }
    })
    return { X, Y, labels }
  }, [axes, noms])
  return (
    <div className="overflow-x-auto">
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full h-auto min-w-[620px]" role="img" aria-label="Carte des députés selon leurs votes : un point par député, sans nom, position moyenne de chaque groupe.">
        <line x1={X(0)} x2={X(0)} y1={pad} y2={H - pad} stroke="#E5E7EB" />
        <line y1={Y(0)} y2={Y(0)} x1={pad} x2={W - pad} stroke="#E5E7EB" />
        <text x={pad + 2} y={H - 6} fontSize="11" fill="#6B7280" fontWeight="600">Gauche</text>
        <text x={W - pad - 2} y={H - 6} fontSize="11" fill="#6B7280" fontWeight="600" textAnchor="end">Droite</text>
        <text x={W / 2} y={12} fontSize="11" fill="#6B7280" fontWeight="600" textAnchor="middle">Oppositions</text>
        <text x={W / 2} y={H - 6} fontSize="11" fill="#6B7280" fontWeight="600" textAnchor="middle">Bloc central</text>
        {axes.points.map((p, i) => (
          <circle key={i} cx={X(p[0])} cy={Y(p[1])} r="2.6" fill={COULEURS[p[2]] || '#9CA3AF'} opacity={survol && survol !== p[2] ? 0.12 : 0.65} />
        ))}
        {labels.map((l) => (
          <text key={l.g} x={l.x} y={l.y} fontSize="13" fontWeight="700" fill="#111827" textAnchor="middle" stroke="#fff" strokeWidth="3" paintOrder="stroke"
            onMouseEnter={() => setSurvol(l.g)} onMouseLeave={() => setSurvol(null)} style={{ cursor: 'default' }}>
            {l.t}
          </text>
        ))}
      </svg>
    </div>
  )
}

export default function AssembleeVotes() {
  const [d, setD] = useState(null)
  const [theme, setTheme] = useState('tous')
  useEffect(() => {
    fetch('/data/showcases/votes-assemblee.json').then((r) => r.json()).then(setD).catch(() => {})
  }, [])
  if (!d) return null

  const ligne = (a, b, t) => {
    const g = d.groupes_ordre
    const m = t ? d.themes[t].matrice : d.matrice
    return m[g.indexOf(a)][g.indexOf(b)]
  }
  const SOCIAL = 'Affaires sociales, santé'
  const LOIS = 'Lois, justice, sécurité'
  const DEF = 'Défense'
  const FIN = 'Finances, budget'
  const p = d.participation
  const totalDemandes = d.n_scrutins
  const demRN = d.groupes.find((g) => g.id === 'RN').demandes
  const demLFI = d.groupes.find((g) => g.id === 'LFI-NFP').demandes
  const om = p.outre_mer
  const omOui = om.find((x) => x.label === 'True')
  const omNon = om.find((x) => x.label === 'False')
  const prof = d.profil
  const t = d.territoire
  const art1 = t.votes[0]
  const PAIRES = d.paires

  return (
    <section className="mb-12">
      <h2 className="text-2xl font-bold text-gray-900 mb-1">Comment votent-ils ?</h2>
      <p className="text-gray-600 mb-5 max-w-3xl">
        {f0(d.n_scrutins)} scrutins publics et {f0(d.n_votes)} votes nominatifs, d'octobre 2024 à octobre 2026, avec le groupe de chaque député
        au moment du vote. Ce ne sont pas tous les votes : beaucoup se font à main levée. Les scrutins publics sont aussi
        demandés : le RN en a sollicité {f0(demRN)} et LFI {f0(demLFI)}, sur {f0(totalDemandes)}, souvent sur des amendements.
      </p>

      <Titre
        titre="Qui vote avec qui ?"
        intro="Part des scrutins où deux groupes ont adopté la même position, pour ou contre, selon la majorité de leurs votants (au moins 5). Chaque sujet correspond à la commission saisie au fond du texte : le classement est celui de l'Assemblée."
      />
      <div className="flex flex-wrap gap-2 mb-3">
        {['tous', ...d.themes_noms].map((k) => (
          <button key={k} type="button" aria-pressed={k === theme} onClick={() => setTheme(k)}
            className={`px-3 py-1 rounded-full text-sm font-medium border transition-colors ${k === theme ? 'bg-indigo-600 border-indigo-600 text-white' : 'border-gray-200 text-gray-600 hover:bg-gray-50'}`}>
            {k === 'tous' ? 'Tous les sujets' : k}
            {k !== 'tous' && <span className={k === theme ? 'text-indigo-200' : 'text-gray-400'}> {f0(d.themes[k].n)}</span>}
          </button>
        ))}
      </div>
      <div className="bg-white border border-gray-200 rounded-xl p-4 mb-5">
        <Matrice d={d} theme={theme} />
      </div>
      <div className="space-y-3 text-gray-700 max-w-3xl mb-6">
        <p>
          <strong>Trois blocs, et une droite entre deux.</strong> La gauche vote très soudée, le bloc central aussi, le RN et l'UDR presque
          toujours ensemble ({ligne('RN', 'UDDPLR')} %). La Droite républicaine, elle, est à égale distance : {ligne('DR', 'RN')} % d'accord
          avec le RN, {ligne('DR', 'EPR')} % avec Ensemble.
        </p>
      </div>
      <div className="bg-white border border-gray-200 rounded-xl p-4 mb-3">
        <CarteDeputes axes={d.axes} noms={d.noms} />
        <p className="text-xs text-gray-400 mt-2">
          Un point par député, sans nom. Deux points proches ont voté de façon proche. L'axe horizontal résume {f0(d.axes.inertie[0])} % des
          différences de vote, l'axe vertical {f0(d.axes.inertie[1])} %. Survolez le nom d'un groupe pour l'isoler.
        </p>
      </div>
      <p className="text-gray-700 max-w-3xl mb-6">
        L'Assemblée ne se lit pas sur une seule ligne. L'axe horizontal oppose la gauche et la droite. L'axe vertical oppose le bloc central à ses
        oppositions : LFI et le RN, aux deux extrémités de l'hémicycle, se trouvent du même côté de cet axe, alors qu'ils ne votent ensemble
        que dans {ligne('LFI-NFP', 'RN')} % des scrutins.
      </p>

      <Titre titre="Les alliances changent avec le sujet" intro="Accord entre quelques paires de groupes, selon le sujet du texte." />
      <div className="bg-white border border-gray-200 rounded-xl p-4 mb-4 overflow-x-auto">
        <table className="text-xs border-separate w-full" style={{ borderSpacing: 2 }}>
          <thead>
            <tr>
              <th />
              {PAIRES.map(([a, b]) => (
                <th key={a + b} className="font-medium text-gray-500 pb-1 px-1">{d.noms[a]} et {d.noms[b]}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {d.themes_noms.map((n) => (
              <tr key={n}>
                <th className="text-left font-medium text-gray-700 pr-2 whitespace-nowrap">{n}</th>
                {PAIRES.map(([a, b]) => {
                  const v = ligne(a, b, n)
                  return <td key={a + b} className="text-center font-semibold h-8 rounded" style={cellule(v)}>{v ?? '·'}</td>
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="space-y-3 text-gray-700 max-w-3xl mb-6">
        <p>
          <strong>La Droite républicaine change de partenaire selon le texte.</strong> Sur le social et la santé, elle vote avec le RN
          ({ligne('DR', 'RN', SOCIAL)} %) bien plus qu'avec Ensemble ({ligne('EPR', 'DR', SOCIAL)} %). Sur la défense, c'est l'inverse :{' '}
          {ligne('EPR', 'DR', DEF)} % avec Ensemble, {ligne('DR', 'RN', DEF)} % avec le RN.
        </p>
        <p>
          <strong>Ensemble se déplace lui aussi.</strong> Sur les lois, la justice et la sécurité, il est d'accord avec le RN dans{' '}
          {ligne('EPR', 'RN', LOIS)} % des scrutins, et avec le PS dans {ligne('EPR', 'SOC', LOIS)} %. Sur le social, c'est le contraire :{' '}
          {ligne('EPR', 'SOC', SOCIAL)} % avec le PS, {ligne('EPR', 'RN', SOCIAL)} % avec le RN. Sur le budget, il penche vers la Droite
          républicaine ({ligne('EPR', 'DR', FIN)} %).
        </p>
        <p>
          <strong>LFI et le RN ne se rejoignent que sur quelques textes.</strong> Par exemple : {d.convergences.slice(0, 3).map((c) => `« ${c.titre} » (${c.lfi_rn} % sur ${c.n} scrutins)`).join(', ')}.
          Être d'accord sur un scrutin ne veut pas dire défendre le même projet : deux groupes peuvent voter contre un texte pour des raisons opposées.
        </p>
      </div>

      <Titre titre="Qui ne vote pas ?" intro={`Parmi ${f0(p.n)} députés en mandat pendant au moins 500 scrutins, en écartant les cas où ils ne pouvaient pas voter : présidence de séance, présidence de l'Assemblée, gouvernement.`} />
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3 mb-4">
        <Chiffre valeur={`${f0(p.mediane)} %`} texte={`des scrutins votés par le député médian, dont ${f0(p.en_personne)} % sans délégation`} />
        <Chiffre valeur={`${f0(p.types['Scrutins solennels'])} %`} texte="de participation aux scrutins solennels, sur les grands textes" />
        <Chiffre valeur={`${f0(p.commission.sa_commission)} contre ${f0(p.commission.autres)} %`} texte="sur les textes de sa commission et sur les autres" />
        <Chiffre valeur={`${f0(d.part_delegation)} %`} texte="des votes sont exprimés par délégation, par un député absent de l'hémicycle" />
      </div>
      <div className="bg-white border border-gray-200 rounded-xl p-4 mb-4 overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-xs text-gray-400">
              <th className="font-medium pb-2 pr-3">Groupe</th>
              <th className="font-medium pb-2 px-2 text-right">Participation médiane</th>
              <th className="font-medium pb-2 px-2 text-right">Dont en personne</th>
              <th className="font-medium pb-2 px-2 text-right">Votes contre son groupe</th>
              <th className="font-medium pb-2 px-2 text-right">Scrutins demandés</th>
              <th className="font-medium pb-2 pl-2 text-right">Amendements adoptés</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {d.groupes.map((g) => (
              <tr key={g.id}>
                <td className="py-1.5 pr-3 text-gray-800">
                  <span className="inline-block w-2.5 h-2.5 rounded-full mr-2" style={{ backgroundColor: COULEURS[g.id] }} />
                  {g.nom} <span className="text-xs text-gray-400">{g.n}</span>
                </td>
                <td className="py-1.5 px-2 text-right font-semibold text-gray-900">{f1(g.participation)} %</td>
                <td className="py-1.5 px-2 text-right text-gray-700">{f1(g.en_personne)} %</td>
                <td className="py-1.5 px-2 text-right text-gray-700">{f1(g.dissidence)} %</td>
                <td className="py-1.5 px-2 text-right text-gray-700">{f0(g.demandes)}</td>
                <td className="py-1.5 pl-2 text-right text-gray-700">{f0(g.amendements)} %</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="space-y-3 text-gray-700 max-w-3xl mb-4">
        <p>
          Les grands votes mobilisent presque tout le monde : {f0(p.types['Scrutins solennels'])} % de participation aux scrutins solennels, contre{' '}
          {f0(p.types['Scrutins ordinaires'])} % aux scrutins ordinaires, le plus souvent sur des amendements. Et chacun vote d'abord sur ce qu'il
          suit : un député participe bien plus souvent aux scrutins de sa commission.
        </p>
        <p>
          À groupe égal, ni le sexe ({sg(p.net_femme.b)} point, ± {f1(p.net_femme.ic)}) ni l'âge ni le fait d'être nouvel élu ne changent
          nettement la participation. L'éloignement, si : les {omOui.n} députés d'outre-mer votent à {f1(omOui.participation)} % des scrutins contre{' '}
          {f1(omNon.participation)} % pour les autres, un écart de {f1(Math.abs(p.net_outre_mer.b))} points à groupe égal (± {f1(p.net_outre_mer.ic)}).
        </p>
      </div>
      <ToneCallout tone="warn">
        Ne pas voter n'est pas ne pas travailler. Un député peut être en commission, en circonscription ou en mission, et voter sur chaque
        amendement n'est pas son rôle. C'est pourquoi ce dossier ne publie aucun classement individuel, même si les votes sont publics. Les
        motions de censure sont à part : seuls les votes pour y sont comptés. Le nombre d'amendements adoptés porte sur ceux soumis à un
        scrutin public, et suppose un auteur identifié dans l'intitulé.
      </ToneCallout>

      <Titre titre="À groupe égal, le profil compte-t-il ?" intro="Dans un même groupe, femmes et hommes, jeunes et anciens votent-ils différemment ? Pour le savoir, on compte les scrutins où deux sous-groupes prennent des positions opposées, et on compare à des partages tirés au hasard." />
      <div className="bg-white border border-gray-200 rounded-xl p-4 mb-3 overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-xs text-gray-400">
              <th className="font-medium pb-2 pr-3">Comparaison, dans un même groupe</th>
              <th className="font-medium pb-2 px-2 text-right">Scrutins en désaccord</th>
              <th className="font-medium pb-2 pl-2 text-right">Partage au hasard</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {prof.map((r) => (
              <tr key={r.label}>
                <td className="py-1.5 pr-3 text-gray-800">{r.label}</td>
                <td className="py-1.5 px-2 text-right font-semibold text-gray-900">{f1(r.observe)} %</td>
                <td className="py-1.5 pl-2 text-right text-gray-600">{f1(r.hasard)} % <span className="text-xs text-gray-400">({f1(r.bas)} à {f1(r.haut)})</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="text-gray-700 max-w-3xl mb-6">
        <strong>Non : le groupe l'emporte sur le profil.</strong> Un partage par sexe, par âge, par ancienneté ou par profession ne fait pas mieux qu'un tirage
        au sort. Cela ne veut pas dire que le profil des élus n'a aucun effet : il peut peser avant le vote, dans le choix des sujets, les
        amendements déposés ou la ligne du groupe. Mais au moment de voter, c'est l'appartenance au groupe qui compte, par discipline ou par convictions partagées : ces données ne permettent pas de distinguer les deux.
      </p>

      <Titre titre="Le territoire change-t-il le vote ?" intro={`Test sur la proposition de loi contre les déserts médicaux, qui pose directement la question de l'installation des médecins (${t.scrutins} scrutins publics), croisée avec l'accès aux généralistes du département de chaque député.`} />
      <div className="space-y-3 text-gray-700 max-w-3xl mb-3">
        <p>
          <strong>Il ne change pas le vote.</strong> Sur la régulation de l'installation ({art1.n} votants), le groupe décide de tout : 100 % pour à LFI,
          0 % au RN. À groupe égal, l'écart lié à l'accès aux soins du département n'est pas significatif ({sg(art1.b)} points, ± {f1(art1.ic)}).
        </p>
        <p>
          <strong>Mais il fait venir voter.</strong> Plus l'accès aux soins du département est faible, plus le député participe à ces scrutins, à groupe égal :{' '}
          {f1(Math.abs(t.part_dm.b))} points de participation de moins pour une hausse d'un écart-type de l'accès (± {f1(t.part_dm.ic)}). Le territoire
          pèse sur la présence, pas sur la position.
        </p>
      </div>
      <p className="text-xs text-gray-400 max-w-3xl">
        Une seule loi, cinq scrutins et une mesure au département, faute de lien direct entre circonscription et commune : ce résultat appelle d'autres tests.
      </p>

      <details className="bg-gray-50 border border-gray-200 rounded-xl p-5 text-sm text-gray-600 mt-6">
        <summary className="cursor-pointer font-semibold text-gray-900">Méthode et limites</summary>
        <div className="mt-3 space-y-2">
          <p><strong>Accord.</strong> Position d'un groupe : pour ou contre majoritaire, si au moins 5 de ses membres ont voté, selon le groupe au jour du scrutin. Accord calculé dès 15 scrutins communs. L'accord porte sur des scrutins demandés, surtout sur des amendements : il ne décrit pas toute l'activité de l'Assemblée. D'un semestre à l'autre, il varie sans tendance nette.</p>
          <p><strong>Sujets.</strong> Commission saisie au fond du texte. Les scrutins sans dossier ou sans commission retrouvée sont exclus de la lecture par sujet ; les liens manquants du fichier officiel sont complétés par NosParlementaires.</p>
          <p><strong>Carte.</strong> Décomposition en valeurs singulières sur les scrutins d'au moins 100 votants où la minorité dépasse 10 %, députés d'au moins 300 votes.</p>
          <p><strong>Participation.</strong> Votes exprimés rapportés aux scrutins tenus pendant le mandat, hors cas où voter était impossible. La présence dans l'hémicycle n'est pas connue : les absents ne sont pas listés. Les chiffres à groupe égal viennent de régressions linéaires, avec erreurs robustes.</p>
          <p><strong>Profil.</strong> 200 tirages au sort à l'intérieur de chaque groupe, sous-groupes d'au moins 8 députés et 5 votants.</p>
        </div>
      </details>
      <p className="text-xs text-gray-400 mt-3">
        Sources :{' '}
        <a href="https://data.assemblee-nationale.fr/travaux-parlementaires/votes" target="_blank" rel="noopener noreferrer" className={lien}>Assemblée nationale, scrutins</a>
        {' · '}
        <a href="https://data.assemblee-nationale.fr/travaux-parlementaires/dossiers-legislatifs" target="_blank" rel="noopener noreferrer" className={lien}>dossiers législatifs</a>
        {' · '}
        <a href="https://data.assemblee-nationale.fr/acteurs/historique-des-deputes" target="_blank" rel="noopener noreferrer" className={lien}>acteurs et mandats</a>
        {' · '}
        <a href="https://www.data.gouv.fr/datasets/votes-et-activite-des-parlementaires-francais-17e-legislature-nosparlementaires" target="_blank" rel="noopener noreferrer" className={lien}>NosParlementaires</a>
        {' · '}
        <a href="https://data.drees.solidarites-sante.gouv.fr/explore/dataset/530_l-accessibilite-potentielle-localisee-apl/" target="_blank" rel="noopener noreferrer" className={lien}>Drees, APL 2024</a>.
      </p>
    </section>
  )
}
