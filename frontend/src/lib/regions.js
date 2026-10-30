// Rattachement département -> région (métropole + outre-mer regroupé), pour
// agréger des données communales en une lecture territoriale par région.
import { depFromInsee } from './territoire'

const REGIONS = {
  'Île-de-France': ['75', '77', '78', '91', '92', '93', '94', '95'],
  'Auvergne-Rhône-Alpes': ['01', '03', '07', '15', '26', '38', '42', '43', '63', '69', '73', '74'],
  'Hauts-de-France': ['02', '59', '60', '62', '80'],
  'Grand Est': ['08', '10', '51', '52', '54', '55', '57', '67', '68', '88'],
  "Provence-Alpes-Côte d'Azur": ['04', '05', '06', '13', '83', '84'],
  'Occitanie': ['09', '11', '12', '30', '31', '32', '34', '46', '48', '65', '66', '81', '82'],
  'Nouvelle-Aquitaine': ['16', '17', '19', '23', '24', '33', '40', '47', '64', '79', '86', '87'],
  'Bourgogne-Franche-Comté': ['21', '25', '39', '58', '70', '71', '89', '90'],
  'Bretagne': ['22', '29', '35', '56'],
  'Centre-Val de Loire': ['18', '28', '36', '37', '41', '45'],
  'Normandie': ['14', '27', '50', '61', '76'],
  'Pays de la Loire': ['44', '49', '53', '72', '85'],
  'Corse': ['2A', '2B'],
  'Outre-mer': ['971', '972', '973', '974', '976', '977', '978', '984', '986', '987', '988'],
}

const DEP_TO_REGION = {}
for (const [region, deps] of Object.entries(REGIONS)) {
  for (const d of deps) DEP_TO_REGION[d] = region
}

/** Région d'un code commune (ou département). */
export function regionOf(code) {
  return DEP_TO_REGION[depFromInsee(code)] || null
}

/** Région d'un code département (2-3 caractères). */
export function regionOfDep(dep) {
  return DEP_TO_REGION[dep] || null
}

// Régions administratives au 1er janvier 2026, avec leur code officiel Insee (fiche territoire
// à l'échelle régionale). Liste identique à REGIONS de python/tools/build_territoires_echelles.py.
// Contrairement à REGIONS ci-dessus, chaque région d'outre-mer est une région à part entière.
export const REGIONS_INSEE = [
  { code: '11', nom: 'Île-de-France', deps: ['75', '77', '78', '91', '92', '93', '94', '95'] },
  { code: '24', nom: 'Centre-Val de Loire', deps: ['18', '28', '36', '37', '41', '45'] },
  { code: '27', nom: 'Bourgogne-Franche-Comté', deps: ['21', '25', '39', '58', '70', '71', '89', '90'] },
  { code: '28', nom: 'Normandie', deps: ['14', '27', '50', '61', '76'] },
  { code: '32', nom: 'Hauts-de-France', deps: ['02', '59', '60', '62', '80'] },
  { code: '44', nom: 'Grand Est', deps: ['08', '10', '51', '52', '54', '55', '57', '67', '68', '88'] },
  { code: '52', nom: 'Pays de la Loire', deps: ['44', '49', '53', '72', '85'] },
  { code: '53', nom: 'Bretagne', deps: ['22', '29', '35', '56'] },
  { code: '75', nom: 'Nouvelle-Aquitaine', deps: ['16', '17', '19', '23', '24', '33', '40', '47', '64', '79', '86', '87'] },
  { code: '76', nom: 'Occitanie', deps: ['09', '11', '12', '30', '31', '32', '34', '46', '48', '65', '66', '81', '82'] },
  { code: '84', nom: 'Auvergne-Rhône-Alpes', deps: ['01', '03', '07', '15', '26', '38', '42', '43', '63', '69', '73', '74'] },
  { code: '93', nom: "Provence-Alpes-Côte d'Azur", deps: ['04', '05', '06', '13', '83', '84'] },
  { code: '94', nom: 'Corse', deps: ['2A', '2B'] },
  { code: '01', nom: 'Guadeloupe', deps: ['971'], outreMer: true },
  { code: '02', nom: 'Martinique', deps: ['972'], outreMer: true },
  { code: '03', nom: 'Guyane', deps: ['973'], outreMer: true },
  { code: '04', nom: 'La Réunion', deps: ['974'], outreMer: true },
  { code: '06', nom: 'Mayotte', deps: ['976'], outreMer: true },
]
export const REGION_INSEE_BY_CODE = Object.fromEntries(REGIONS_INSEE.map((r) => [r.code, r]))
const DEP_TO_REGION_INSEE = {}
for (const r of REGIONS_INSEE) for (const d of r.deps) DEP_TO_REGION_INSEE[d] = r

/** Région administrative ({ code, nom, deps }) d'un code département, ou null (collectivités d'outre-mer). */
export function regionInseeOfDep(dep) {
  return DEP_TO_REGION_INSEE[dep] || null
}
