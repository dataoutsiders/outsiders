# -*- coding: utf-8 -*-
"""
Showcase « La diversité des élus », calcule l'IDP des candidats municipaux 2026
par département, par commune (top/bottom) et par parti, en réutilisant EXACTEMENT
le référentiel de l'outil (surnames.tsv) pour garantir la cohérence des chiffres.

Sortie : frontend/public/data/showcases/elus-diversite.json
"""
import json
import re
import unicodedata
from datetime import date
from pathlib import Path

import pandas as pd

SCRIPT_DIR = Path(__file__).parent.resolve()
REPO_ROOT = SCRIPT_DIR.parent.parent
ONO_DIR = REPO_ROOT / 'frontend' / 'public' / 'data' / 'onomastics'
CANDIDATS_FILE = REPO_ROOT / 'python' / 'data' / 'municipales' / 'municipales-2026.csv'
# Répertoire national des élus (data.gouv.fr), élus en fonction après les municipales 2026.
# Fichiers : elus-maire-mai.csv et elus-conseiller-municipal-cm.csv, mise à jour du 11/08/2026.
RNE_DIR = REPO_ROOT / 'python' / 'data' / 'municipales' / 'rne'
RNE_MAIRES = RNE_DIR / 'elus-maires-2026-08.csv'
RNE_CONSEILLERS = RNE_DIR / 'elus-conseillers-municipaux-2026-08.csv'
RNE_MAJ = '11/08/2026'
OUTPUT_DIR = REPO_ROOT / 'frontend' / 'public' / 'data' / 'showcases'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SEUIL_COMMUNE = 50   # nb minimal de noms reconnus pour classer une commune

# --- Normalisation : identique au moteur ---
def normaliser(nom) -> str:
    if nom is None:
        return ''
    s = str(nom).upper().strip()
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    s = s.replace("'", ' ').replace('’', ' ')
    s = re.sub(r'\s+', ' ', s)
    return s.strip()

# --- Référentiel IDP depuis l'artefact de l'outil ---
print('Chargement du référentiel surnames.tsv...')
divers_set, known_set = set(), set()
with open(ONO_DIR / 'surnames.tsv', encoding='utf-8') as f:
    for line in f:
        nom, flag = line.rstrip('\n').split('\t')
        known_set.add(nom)
        if flag == '1':
            divers_set.add(nom)
print(f'  {len(known_set)} noms connus, {len(divers_set)} diversité')

def idp_flag(nom_norm):
    if nom_norm in divers_set:
        return True
    if nom_norm in known_set:
        return False
    return None

# --- Données candidats ---
print('Chargement des candidats...')
df = pd.read_csv(CANDIDATS_FILE, sep=';', encoding='utf-8', dtype=str)
df.columns = [c.strip('"').strip() for c in df.columns]
for c in df.columns:
    df[c] = df[c].str.strip('"')

COL_DEP_CODE = 'Code département'
COL_DEP = 'Département'
COL_COM_CODE = 'Code circonscription'
COL_COM = 'Circonscription'
COL_NUANCE = 'Nuance de liste'
COL_TETE = 'Tête de liste'
COL_SEXE = 'Sexe'
COL_NOM = 'Nom sur le bulletin de vote'

df['nom_norm'] = df[COL_NOM].apply(normaliser)
df['idp'] = df['nom_norm'].apply(idp_flag)          # True / False / None
df['femme'] = df[COL_SEXE].str.upper().str[0] == 'F'

def idp_pct(sub):
    """% IDP sur les noms reconnus + effectif reconnu."""
    rec = sub['idp'].dropna()
    n = len(rec)
    return (round(rec.mean() * 100, 1) if n else None), n

def fem_pct(sub):
    n = len(sub)
    return (round(sub['femme'].mean() * 100, 1) if n else None), n

# --- National + funnel ---
print('Calcul national + funnel...')
idp_nat, n_rec_nat = idp_pct(df)
fem_nat, _ = fem_pct(df)
tetes = df[df[COL_TETE] == 'OUI']
idp_tetes, n_tetes = idp_pct(tetes)

national = {
    'idp': idp_nat,
    'feminisation': fem_nat,
    'n': int(len(df)),
    'n_reconnus': int(n_rec_nat),
}
# Élus en fonction : Répertoire national des élus, même référentiel et même normalisation
# que pour les candidats (les noms hors référentiel sont exclus du taux, comme dans l'outil).
def charger_rne(chemin):
    rne = pd.read_csv(chemin, sep=';', encoding='utf-8', dtype=str)
    rne['idp'] = rne["Nom de l'élu"].apply(normaliser).apply(idp_flag)
    rne['femme'] = rne['Code sexe'].str.upper().str[0] == 'F'
    return rne

print('Chargement du Répertoire national des élus...')
conseillers = charger_rne(RNE_CONSEILLERS)
maires = charger_rne(RNE_MAIRES)
idp_cm, _ = idp_pct(conseillers)
idp_maires, _ = idp_pct(maires)
print(f'  conseillers municipaux : {len(conseillers)}, IDP {idp_cm} % ; maires : {len(maires)}, IDP {idp_maires} %')

funnel = [
    {'etape': 'Tous les candidats', 'idp': idp_nat, 'n': int(len(df))},
    {'etape': 'Têtes de liste', 'idp': idp_tetes, 'n': int(len(tetes))},
    {'etape': 'Conseillers municipaux élus', 'idp': idp_cm, 'n': int(len(conseillers)),
     'source': f'Répertoire national des élus, {RNE_MAJ}'},
    {'etape': 'Maires', 'idp': idp_maires, 'n': int(len(maires)),
     'source': f'Répertoire national des élus, {RNE_MAJ}'},
]
national['feminisation_maires'] = round(maires['femme'].mean() * 100, 1)
national['feminisation_conseillers'] = round(conseillers['femme'].mean() * 100, 1)

# --- Où se joue le filtre ? Comparaison commune par commune (2026) ---
# L'écart brut candidats -> maires mélange deux effets : la géographie (les candidats
# aux noms classés « diversité » sont concentrés dans les grandes villes, où les listes et
# les candidats sont nombreux, alors que chaque commune n'a qu'un maire) et la sélection
# à l'intérieur d'une même commune ou d'une même liste. On compare donc chaque élu aux
# candidats de sa propre commune (ou chaque tête de liste à ses colistiers).
print('Filtre commune par commune...')

def cle_commune(dep, com):
    """Clé département|code commune sur 3 caractères, commune à 2020 et 2026."""
    dep = str(dep).strip().strip('"')
    com = str(com).strip().strip('"')
    if dep.isdigit() and len(dep) < 2:
        dep = dep.zfill(2)
    return f"{dep}|{com.zfill(3)[-3:]}"

def moyenne_pct(serie):
    s = serie.dropna()
    return round(float(s.mean()) * 100, 1) if len(s) else None

df['cle'] = [cle_commune(d, c) for d, c in zip(df[COL_DEP_CODE], df[COL_COM_CODE])]
df['cle_liste'] = df['cle'] + '#' + df['Numéro de panneau'].fillna('')
taux_commune = df.groupby('cle')['idp'].apply(lambda s: s.dropna().mean())
taux_liste = df.groupby('cle_liste')['idp'].apply(lambda s: s.dropna().mean())
taux_tetes_commune = tetes.assign(cle=df.loc[tetes.index, 'cle']).groupby('cle')['idp'].apply(
    lambda s: s.dropna().mean())
tetes_rec = df.loc[tetes.index].dropna(subset=['idp'])
for rne in (conseillers, maires):
    rne['cle'] = [cle_commune(d, c) for d, c in zip(rne['Code du département'], rne['Code de la commune'])]
cons_rec = conseillers.dropna(subset=['idp'])
maires_rec = maires.dropna(subset=['idp'])
maires_attendu = moyenne_pct(maires_rec['cle'].map(taux_commune))
filtre = {
    'candidats': idp_nat,
    'candidats_moyenne_communes': moyenne_pct(taux_commune),
    'tetes': idp_tetes,
    'tetes_attendu_liste': moyenne_pct(tetes_rec['cle_liste'].map(taux_liste)),
    'conseillers': idp_cm,
    'conseillers_attendu_commune': moyenne_pct(cons_rec['cle'].map(taux_commune)),
    'maires': idp_maires,
    'maires_attendu_candidats_commune': maires_attendu,
    'maires_attendu_tetes_commune': moyenne_pct(maires_rec['cle'].map(taux_tetes_commune)),
}
# Rapports calculés sur les taux non arrondis (sinon 2,2 / 1,2 donnerait 1,8 au lieu de 1,9).
taux_maires_brut = float(maires['idp'].dropna().mean())
filtre['rapport_brut'] = round(float(df['idp'].dropna().mean()) / taux_maires_brut, 1)
filtre['rapport_commune'] = round(float(maires_rec['cle'].map(taux_commune).dropna().mean()) / taux_maires_brut, 1)
print(f"  {filtre}")

# --- La politique locale se diversifie-t-elle ? 2020 -> 2026, mêmes communes ---
# Champ : communes de métropole qui élisaient déjà leur conseil au scrutin de liste en
# 2020 (1 000 habitants et plus) et présentes en 2026. Pour les élus : premier tour
# seulement, communes pourvues au premier tour les deux années (le second tour de 2020
# s'est tenu en juin, sous Covid). Même référentiel IDP et même normalisation.
print('Comparaison 2020 -> 2026...')
MUNI = REPO_ROOT / 'python' / 'data' / 'municipales'
c20 = pd.read_csv(MUNI / 'candidatures-2020-t1.txt', sep='\t', encoding='latin1', skiprows=2, dtype=str)
c20.columns = [c.strip() for c in c20.columns]
c20['idp'] = c20['Nom candidat'].apply(normaliser).apply(idp_flag)
c20['cle'] = [cle_commune(d, c) for d, c in zip(c20['Code du département'], c20['Code commune'])]
c20['tete'] = c20['N° candidat'].str.strip() == '1'
e20 = pd.read_csv(MUNI / 'candidats-elus-2020-t1.txt', sep='\t', encoding='latin1', dtype=str)
e20.columns = [c.strip() for c in e20.columns]
e20['idp'] = e20['Nom'].apply(normaliser).apply(idp_flag)
e20['cle'] = [cle_commune(d, c) for d, c in zip(e20['Code dpt'], e20['Code commune'])]
e26 = pd.read_csv(MUNI / 'candidats-elus-t1.csv', sep=';', encoding='utf-8', dtype=str)
e26['idp'] = e26['NOMPSN'].apply(normaliser).apply(idp_flag)
e26['cle'] = [cle_commune(d, c) for d, c in zip(e26['CODDPT'], e26['CODCOM'])]

def metro(cle):
    return not cle.startswith(('97', '98', 'Z'))

communes_listes = {k for k in set(c20['cle']) & set(df['cle']) if metro(k)}
communes_elus = communes_listes & set(e20['cle']) & set(e26['cle'])
c20m, c26m = c20[c20['cle'].isin(communes_listes)], df[df['cle'].isin(communes_listes)]
e20m, e26m = e20[e20['cle'].isin(communes_elus)], e26[e26['cle'].isin(communes_elus)]
evolution = {
    'champ': ("Communes de métropole élisant leur conseil au scrutin de liste dès 2020 "
              "(1 000 habitants et plus). Élus : premier tour, communes pourvues au premier tour "
              "en 2020 et en 2026."),
    'n_communes': len(communes_listes),
    'n_communes_elus': len(communes_elus),
    'lignes': [
        {'etape': 'Candidats', 'idp_2020': idp_pct(c20m)[0], 'idp_2026': idp_pct(c26m)[0],
         'n_2020': int(len(c20m)), 'n_2026': int(len(c26m))},
        {'etape': 'Têtes de liste', 'idp_2020': idp_pct(c20m[c20m['tete']])[0],
         'idp_2026': idp_pct(c26m[c26m[COL_TETE] == 'OUI'])[0],
         'n_2020': int(c20m['tete'].sum()), 'n_2026': int((c26m[COL_TETE] == 'OUI').sum())},
        {'etape': 'Conseillers élus au premier tour', 'idp_2020': idp_pct(e20m)[0],
         'idp_2026': idp_pct(e26m)[0], 'n_2020': int(len(e20m)), 'n_2026': int(len(e26m))},
    ],
    'sources': [
        {'label': 'Municipales 2020, candidatures au premier tour (data.gouv.fr)',
         'url': 'https://www.data.gouv.fr/datasets/elections-municipales-2020-candidatures-au-1er-tour'},
        {'label': 'Municipales 2020, candidats élus au premier tour (data.gouv.fr)',
         'url': 'https://www.data.gouv.fr/datasets/elections-municipales-2020-liste-des-candidats-elus-au-t1-et-liste-des-communes-entierement-pourvues'},
        {'label': 'Municipales 2026, candidats élus au premier tour (data.gouv.fr)',
         'url': 'https://www.data.gouv.fr/datasets/elections-municipales-2026-resultats-du-premier-tour'},
    ],
}
for l in evolution['lignes']:
    print(f"  {l['etape']:35} 2020 {l['idp_2020']} % -> 2026 {l['idp_2026']} %")

# --- Par département ---
print('Calcul par département...')
departements = []
for code, sub in df.groupby(COL_DEP_CODE):
    idp, n = idp_pct(sub)
    fem, _ = fem_pct(sub)
    if idp is None:
        continue
    departements.append({
        'code': code,
        'nom': sub[COL_DEP].iloc[0],
        'idp': idp,
        'feminisation': fem,
        'n': int(n),
    })
departements.sort(key=lambda d: d['idp'], reverse=True)

# --- Par commune (top / bottom au-dessus du seuil) ---
print('Calcul par commune...')
communes = []
for code, sub in df.groupby(COL_COM_CODE):
    idp, n = idp_pct(sub)
    if idp is None or n < SEUIL_COMMUNE:
        continue
    communes.append({
        'code': code,
        'nom': sub[COL_COM].iloc[0],
        'departement': sub[COL_DEP].iloc[0],
        'idp': idp,
        'n': int(n),
    })
communes.sort(key=lambda c: c['idp'], reverse=True)
communes_block = {
    'seuil': SEUIL_COMMUNE,
    'n_communes': len(communes),
    'top': communes[:15],
    'bottom': list(reversed(communes[-15:])),
}

# --- Par parti (nuance) ---
print('Calcul par parti...')
NUANCE_LABELS = {
    'LFI': 'La France insoumise', 'LECO': 'Écologistes', 'LSOC': 'Parti socialiste',
    'LCOM': 'Parti communiste', 'LUG': 'Union de la gauche', 'LDVG': 'Divers gauche',
    'LENS': 'Bloc central', 'LUC': 'Union du centre', 'LDVC': 'Divers centre',
    'LLR': 'Les Républicains', 'LUD': 'Union de la droite', 'LDVD': 'Divers droite',
    'LRN': 'Rassemblement National', 'LREC': 'Reconquête', 'LDIV': 'Divers',
    'LEXG': 'Extrême gauche', 'LEXD': 'Extrême droite', 'LREG': 'Régionalistes',
}
partis = []
for code, sub in df.groupby(COL_NUANCE):
    idp, n = idp_pct(sub)
    if idp is None or n < 200:
        continue
    sub_tetes = sub[sub[COL_TETE] == 'OUI']
    idp_t, n_t = idp_pct(sub_tetes)
    partis.append({
        'nuance': code,
        'label': NUANCE_LABELS.get(code, code),
        'idp_listes': idp,
        'n_listes': int(n),
        'idp_tetes': idp_t,            # IDP parmi les têtes de liste au nom reconnu
        'n_tetes': int(n_t),           # têtes de liste au nom reconnu (dénominateur)
        'n_tetes_total': int(len(sub_tetes)),  # nombre total de têtes de liste
    })
partis.sort(key=lambda p: p['idp_listes'], reverse=True)

# --- Par EPCI ---
print('Calcul par EPCI...')
with open(REPO_ROOT / 'python' / 'data' / 'municipales' / 'communes-epci.json', encoding='utf-8') as f:
    comm_epci = {c['code']: c.get('codeEpci') for c in json.load(f) if c.get('codeEpci')}
with open(REPO_ROOT / 'frontend' / 'public' / 'data' / 'geo' / 'epci.geojson', encoding='utf-8') as f:
    epci_nom = {ft['properties']['code']: ft['properties']['nom'] for ft in json.load(f)['features']}

df['epci'] = df[COL_COM_CODE].map(comm_epci)
epci_value, epci_rows = {}, []
for code, sub in df.groupby('epci'):
    idp, n = idp_pct(sub)
    if idp is None or n < 20:
        continue
    epci_value[code] = idp
    if n >= 100:
        epci_rows.append({'code': code, 'nom': epci_nom.get(code, code), 'idp': idp, 'n': int(n)})
epci_rows.sort(key=lambda e: e['idp'], reverse=True)
epci_block = {
    'seuil_carte': 20,
    'seuil_classement': 100,
    'n_epci_colores': len(epci_value),
    'valueByCode': epci_value,
    'top': epci_rows[:15],
    'bottom': list(reversed(epci_rows[-15:])),
}

# --- Sauvegarde ---
out = {
    'generated': date.today().isoformat(),
    'titre': 'La diversité des élus, du candidat au maire',
    'source': f"Candidatures municipales 2026 (T1, data.gouv.fr) · élus en fonction : Répertoire national des élus ({RNE_MAJ}) · IDP Kheddache & L'Horty (2023)",
    'national': national,
    'funnel': funnel,
    'filtre': filtre,
    'evolution': evolution,
    'departements': departements,
    'communes': communes_block,
    'epci': epci_block,
    'partis': partis,
}
out_path = OUTPUT_DIR / 'elus-diversite.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

print(f'\n-> {out_path}')
print(f"National IDP {idp_nat}% · féminisation {fem_nat}% · {len(departements)} départements · "
      f"{len(communes)} communes (seuil {SEUIL_COMMUNE}) · {len(partis)} partis")
print(f"Dép le + divers : {departements[0]['nom']} ({departements[0]['idp']}%) | "
      f"le - divers : {departements[-1]['nom']} ({departements[-1]['idp']}%)")
