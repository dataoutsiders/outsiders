/**
 * Validation Node du moteur onomastique : recharge les artefacts depuis le
 * disque, rejoue l'analyse sur les candidats municipaux 2026, et vérifie que
 * les chiffres correspondent au calcul Python (IDP ~4.4%, proxy sexe ~99%).
 *
 * Lancer : node frontend/scripts/validate_onomastics.mjs
 */
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, resolve } from 'node:path'
import { OnomasticEngine, parseSurnames } from '../src/tools/onomastics/engine.js'

const __dirname = dirname(fileURLToPath(import.meta.url))
const REPO = resolve(__dirname, '..', '..')
const ONO = resolve(REPO, 'frontend', 'public', 'data', 'onomastics')
const CANDIDATS = resolve(REPO, 'python', 'data', 'municipales', 'municipales-2026.csv')

// --- Chargement des artefacts ---
const surnames = parseSurnames(readFileSync(resolve(ONO, 'surnames.tsv'), 'utf8'))
const firstnames = JSON.parse(readFileSync(resolve(ONO, 'firstnames.json'), 'utf8'))
const meta = JSON.parse(readFileSync(resolve(ONO, 'meta.json'), 'utf8'))
const engine = new OnomasticEngine({ surnames, firstnames, meta })
console.log(`Artefacts : ${surnames.size} noms, ${Object.keys(firstnames).length} prénoms`)

// --- Parsing CSV (quote-aware, séparateur ';') ---
function parseLine(line) {
  const out = []
  let cur = ''
  let q = false
  for (let i = 0; i < line.length; i++) {
    const c = line[i]
    if (c === '"') q = !q
    else if (c === ';' && !q) {
      out.push(cur)
      cur = ''
    } else cur += c
  }
  out.push(cur)
  return out
}

const raw = readFileSync(CANDIDATS, 'utf8').split('\n')
const header = parseLine(raw[0])
const iSexe = header.indexOf('Sexe')
const iNom = header.indexOf('Nom sur le bulletin de vote')
const iPre = header.indexOf('Prénom sur le bulletin de vote')

const rows = []
for (let i = 1; i < raw.length; i++) {
  if (!raw[i]) continue
  const f = parseLine(raw[i])
  rows.push({ nom: f[iNom], prenom: f[iPre], sexe: (f[iSexe] || '').toUpperCase()[0] })
}
console.log(`Candidats parsés : ${rows.length}`)

// --- Analyse agrégée ---
const res = engine.analyze(rows, { surname: (r) => r.nom, firstname: (r) => r.prenom }, 2026)

console.log('\n=== Résultats moteur JS ===')
console.log(
  `IDP        : ${res.diversity.pct.toFixed(1)}%  ` +
    `[${res.diversity.ciLow.toFixed(1)}–${res.diversity.ciHigh.toFixed(1)}]  ` +
    `(n=${res.diversity.n}, couverture ${(res.diversity.coverage * 100).toFixed(1)}%)  ` +
    `écart baseline ${res.diversity.gapPct.toFixed(1)} pts, signif=${res.diversity.significant}`,
)
console.log(
  `Féminisation: ${res.gender.pct.toFixed(1)}%  ` +
    `(n=${res.gender.n}, couverture ${(res.gender.coverage * 100).toFixed(1)}%)`,
)
console.log(
  `Âge médian estimé (naissance) : ${res.age.medianBirthYear}  ` +
    `→ ~${res.age.medianAge} ans  (moyenne ~${res.age.meanAge} ans)`,
)

// --- Cross-check précision du proxy sexe vs vérité (colonne Sexe) ---
let ok = 0
let cov = 0
for (const r of rows) {
  const g = engine.inferGender(r.prenom)
  if (!g || (r.sexe !== 'M' && r.sexe !== 'F')) continue
  cov++
  if (g.sex === r.sexe) ok++
}
console.log(
  `\nProxy sexe vs vérité : ${((ok / cov) * 100).toFixed(1)}% précision ` +
    `sur ${((cov / rows.length) * 100).toFixed(1)}% de couverture`,
)

// --- Assertions ---
const idpOk = Math.abs(res.diversity.pct - 4.4) < 0.3
const sexeOk = ok / cov > 0.98
console.log(`\nIDP ≈ 4.4% ? ${idpOk ? 'OK' : 'ÉCHEC'}`)
console.log(`Proxy sexe > 98% ? ${sexeOk ? 'OK' : 'ÉCHEC'}`)
process.exit(idpOk && sexeOk ? 0 : 1)
