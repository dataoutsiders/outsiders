# -*- coding: utf-8 -*-
"""
Génération des artefacts de référence pour le moteur d'inférence onomastique.

Transforme les fichiers bruts INSEE en artefacts compacts, embarquables côté
navigateur (traitement 100% client-side ensuite) :

  - surnames.tsv   : noms de famille connus + flag IDP (diversité oui/non)
  - firstnames.json: prénoms -> sexe (h/f) + distribution d'âge par décennie
  - meta.json      : baselines, provenance, libellés

Méthode IDP : Kheddache M. & L'Horty Y. (2023), Indice de Diversité Patronymique,
Rapport TEPP n°2024-1. Un nom est « issu de la diversité » s'il était absent des
registres avant 1950, ou s'il a été multiplié par > 15 après 1950.
"""
import json
import re
import unicodedata
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

# ============================================
# CHEMINS
# ============================================
SCRIPT_DIR = Path(__file__).parent.resolve()
REPO_ROOT = SCRIPT_DIR.parent.parent          # .../outsiders
DATA_DIR = REPO_ROOT / 'python' / 'data' / 'municipales'
NOMS_FILE = DATA_DIR / 'noms_famille' / 'noms2008nat_txt.txt'
PRENOMS_FILE = DATA_DIR / 'prenoms' / 'prenoms-2025-nat.csv'   # Insee, diffusion de juillet 2026 (effectifs arrondis à 5)
CANDIDATS_FILE = DATA_DIR / 'municipales-2026.csv'   # pour la validation

OUTPUT_DIR = REPO_ROOT / 'frontend' / 'public' / 'data' / 'onomastics'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================
# NORMALISATION (doit rester STRICTEMENT identique au moteur JS)
# ============================================
_MN = 'Mn'  # marques combinantes (accents)

def normaliser(nom) -> str:
    if nom is None:
        return ''
    s = str(nom).upper().strip()
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if unicodedata.category(c) != _MN)
    s = s.replace("'", ' ').replace('’', ' ')
    s = re.sub(r'\s+', ' ', s)
    return s.strip()

# ============================================
# 1. NOMS DE FAMILLE -> IDP
# ============================================
print('1. Construction de la référence IDP (noms de famille)...')
noms = pd.read_csv(NOMS_FILE, sep='\t', encoding='utf-8', dtype=str)

cols_avant = ['_1891_1900', '_1901_1910', '_1911_1920', '_1921_1930', '_1931_1940', '_1941_1950']
cols_apres = ['_1951_1960', '_1961_1970', '_1971_1980', '_1981_1990', '_1991_2000']
for c in cols_avant + cols_apres:
    noms[c] = pd.to_numeric(noms[c], errors='coerce').fillna(0).astype(np.int64)

noms['nom_norm'] = noms['NOM'].apply(normaliser)
noms = noms[noms['nom_norm'] != '']

# Agréger les variantes qui se normalisent vers le même nom (dédup propre),
# PUIS recalculer le critère sur les sommes agrégées.
agg = noms.groupby('nom_norm', as_index=False)[cols_avant + cols_apres].sum()
agg['sum_avant'] = agg[cols_avant].sum(axis=1)
agg['sum_apres'] = agg[cols_apres].sum(axis=1)

critere_absent = agg['sum_avant'] == 0
ratio = np.where(agg['sum_avant'] > 0, agg['sum_apres'] / agg['sum_avant'].replace(0, np.nan), 0)
critere_expansion = (agg['sum_avant'] > 0) & (pd.Series(ratio, index=agg.index) > 15)
agg['issu_diversite'] = (critere_absent | critere_expansion)

n_known = len(agg)
n_divers = int(agg['issu_diversite'].sum())
print(f'   {n_known} noms connus, {n_divers} issus de la diversite '
      f'({n_divers / n_known * 100:.1f}% du referentiel)')

# Écriture surnames.tsv : NOM<TAB>FLAG (1 = diversite, 0 = non)
surnames_path = OUTPUT_DIR / 'surnames.tsv'
with open(surnames_path, 'w', encoding='utf-8') as f:
    for nom, flag in zip(agg['nom_norm'], agg['issu_diversite']):
        f.write(f'{nom}\t{1 if flag else 0}\n')
print(f'   -> {surnames_path.name}')

# Sets en mémoire pour la validation plus bas
divers_set = set(agg.loc[agg['issu_diversite'], 'nom_norm'])
known_set = set(agg['nom_norm'])

# ============================================
# 2. PRÉNOMS -> SEXE + ÂGE
# ============================================
print('2. Construction de la table prenoms (sexe + age)...')
pren = pd.read_csv(PRENOMS_FILE, sep=';', encoding='utf-8', dtype=str)
pren.columns = [c.strip() for c in pren.columns]

pren['sexe'] = pd.to_numeric(pren['sexe'], errors='coerce')
pren['annee'] = pd.to_numeric(pren['periode'], errors='coerce')
pren['valeur'] = pd.to_numeric(pren['valeur'], errors='coerce').fillna(0).astype(np.int64)
pren['prenom_norm'] = pren['prenom'].apply(normaliser)

# Exclure les prenoms « rares » (agregat INSEE) et lignes invalides
pren = pren[(pren['prenom_norm'] != '') &
            (~pren['prenom_norm'].str.contains('RARES')) &
            pren['sexe'].isin([1, 2]) &
            pren['annee'].notna()]

# Décennies : 0 = 1900-1909 ... 12 = 2020-2025
pren['decennie'] = ((pren['annee'] - 1900) // 10).clip(0, 12).astype(int)

firstnames = {}
for prenom_norm, grp in pren.groupby('prenom_norm'):
    h = int(grp.loc[grp['sexe'] == 1, 'valeur'].sum())
    f = int(grp.loc[grp['sexe'] == 2, 'valeur'].sum())
    age = [0] * 13
    for dec, v in grp.groupby('decennie')['valeur'].sum().items():
        age[int(dec)] = int(v)
    firstnames[prenom_norm] = {'h': h, 'f': f, 'age': age}

print(f'   {len(firstnames)} prenoms distincts')

firstnames_path = OUTPUT_DIR / 'firstnames.json'
with open(firstnames_path, 'w', encoding='utf-8') as f:
    json.dump(firstnames, f, ensure_ascii=False, separators=(',', ':'))
print(f'   -> {firstnames_path.name}')

# ============================================
# 3. META / BASELINES
# ============================================
print('3. Meta / baselines...')
total_h = sum(d['h'] for d in firstnames.values())
total_f = sum(d['f'] for d in firstnames.values())
female_birth_pct = round(total_f / (total_h + total_f) * 100, 1)

meta = {
    'generated': date.today().isoformat(),
    'normalization': "upper, NFD sans accents, apostrophes -> espace, espaces compactes",
    'idp': {
        'population_baseline_pct': 7.0,
        'n_surnames_known': n_known,
        'n_surnames_divers': n_divers,
        'divers_pct_of_reference': round(n_divers / n_known * 100, 1),
        'rule': "absent avant 1950 OU multiplie par >15 apres 1950",
        'source': "Kheddache M., L'Horty Y. (2023), Indice de Diversite Patronymique, Rapport TEPP n°2024-1",
        'reference_file': "INSEE - noms de famille 1891-2000 (218 983 patronymes)",
    },
    'gender': {
        'n_firstnames': len(firstnames),
        'national_female_birth_pct': female_birth_pct,
        'source': "INSEE - fichier des prenoms (naissances 1900-2025)",
        'note': "proxy : sexe associe au prenom, fiable en agrege, bruite a l'individu",
    },
    'age': {
        'decade_labels': ['1900-1909', '1910-1919', '1920-1929', '1930-1939',
                          '1940-1949', '1950-1959', '1960-1969', '1970-1979',
                          '1980-1989', '1990-1999', '2000-2009', '2010-2019', '2020-2025'],
        'source': "INSEE - fichier des prenoms (naissances 1900-2025)",
        'note': "proxy d'age via l'annee de naissance associee au prenom",
    },
}
meta_path = OUTPUT_DIR / 'meta.json'
with open(meta_path, 'w', encoding='utf-8') as f:
    json.dump(meta, f, ensure_ascii=False, indent=2)
print(f'   -> {meta_path.name}')

# ============================================
# 4. VALIDATION : reproduire les nombres connus sur les candidats municipaux
# ============================================
print('4. Validation sur les candidats municipaux 2026...')

def idp_flag(nom_norm):
    if nom_norm in divers_set:
        return True
    if nom_norm in known_set:
        return False
    return None  # inconnu -> exclu du denominateur

cand = pd.read_csv(CANDIDATS_FILE, sep=';', encoding='utf-8', dtype=str)
cand.columns = [c.strip('"').strip() for c in cand.columns]
for c in cand.columns:
    cand[c] = cand[c].str.strip('"')

col_nom = 'Nom sur le bulletin de vote'
col_pre = 'Prénom sur le bulletin de vote'
col_sexe = 'Sexe'

# IDP
cand['nom_norm'] = cand[col_nom].apply(normaliser)
flags = cand['nom_norm'].apply(idp_flag)
classes = flags.dropna()
idp_cand = classes.mean() * 100
print(f'   IDP candidats = {idp_cand:.1f}%  (attendu ~4.4%) '
      f'| {len(classes)}/{len(cand)} noms reconnus')

# Cross-check du proxy SEXE : on connait le vrai sexe (colonne Sexe) -> on mesure
# la precision du proxy onomastique.
def genre_proxy(prenom):
    d = firstnames.get(normaliser(prenom))
    if not d or (d['h'] + d['f']) == 0:
        return None
    return 'F' if d['f'] >= d['h'] else 'M'

cand['genre_proxy'] = cand[col_pre].apply(genre_proxy)
vrai = cand[col_sexe].str.upper().str[0]   # 'M' / 'F'
mask = cand['genre_proxy'].notna() & vrai.isin(['M', 'F'])
acc = (cand.loc[mask, 'genre_proxy'] == vrai[mask]).mean() * 100
couv = mask.mean() * 100
print(f'   Proxy sexe : {acc:.1f}% de precision sur {couv:.1f}% de couverture '
      f'(verite = colonne Sexe)')

# ============================================
# 5. TAILLES DES FICHIERS
# ============================================
print('5. Tailles des artefacts generes :')
for p in [surnames_path, firstnames_path, meta_path]:
    print(f'   {p.name:18s} {p.stat().st_size / 1024:8.1f} Ko')

print('\nTERMINE.')
