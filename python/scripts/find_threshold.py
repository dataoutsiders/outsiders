"""
Trouver le seuil optimal pour filtrer les pratiques peu repandues
Calcul sur population TOTALE pour toutes les variables
"""
import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data" / "francais-information"

# Charger les donnees
df = pd.read_excel(DATA_DIR / "base-info-arcom.xlsx")
df['POIDS03'] = df['POIDS03'].astype(str).str.replace(',', '.').astype(float)

# ============================================================================
# LABELS POUR TOUTES LES VARIABLES
# ============================================================================

# NEWS1_R1: Sources d'info principales (multi-choix avec codes)
news1_sources = {
    1: 'Television',
    2: 'Moteur recherche',
    3: 'Reseaux sociaux',
    4: 'Radio/podcasts',
    5: 'Portail actualite',
    6: 'Journal/magazine',
    7: 'Site media internet',
    8: 'Plateforme video',
}

# RSINFO_2_LR_R: Plateformes RS pour s'informer (colonnes binaires)
plateformes_rs = {
    1: 'Facebook',
    2: 'Instagram',
    3: 'Twitter/X',
    4: 'TikTok',
    5: 'Snapchat',
    6: 'LinkedIn',
    7: 'WhatsApp',
    8: 'Telegram',
    9: 'Youtube',
    10: 'Reddit',
    11: 'Discord',
    12: 'Twitch',
    13: 'Autre RS',
}

# SOURCES1BR_B2_R: Journaux/presse ecrite
journaux = {
    1: 'Le Monde',
    2: 'Le Parisien',
    3: 'Le Figaro',
    4: 'Les Echos',
    5: 'L Equipe',
    6: 'La Croix',
    7: 'Liberation',
    8: 'L Humanite',
    9: 'Mediapart',
    10: 'Huffington Post',
    11: 'Journal regional',
    12: 'Journal dimanche',
    13: 'Journal satirique',
    14: 'Quotidien gratuit',
    15: 'Autre journal',
}

# SOURCES1CR_B3_R: Magazines/revues
magazines = {
    1: 'Telerama',
    2: 'M Le Monde',
    3: 'Le Point',
    4: 'L Obs',
    5: 'L Express',
    6: 'Le Figaro Magazine',
    7: 'Courrier International',
    8: 'Marianne',
    9: 'Paris Match',
    10: 'Valeurs Actuelles',
    11: 'Presse feminine',
    12: 'Presse people',
    13: 'Presse economique',
    14: 'Presse internationale',
    15: 'Autre magazine',
}

# TV2AR_R: JT/journaux televises
jt_tv = {
    1: 'JT 20h TF1',
    2: 'JT 20h France 2',
    3: '19/20 France 3',
    4: '19-45 M6',
    5: 'Arte Journal',
    6: 'JT 13h TF1',
    7: 'JT 13h France 2',
    8: 'JT 12h France 3',
    9: '12-45 M6',
    10: 'Autre JT',
}

# TV2CR_R: Magazines TV
magazines_tv = {
    1: 'Zone Interdite',
    2: 'Cash Investigation',
    3: 'Capital',
    4: 'Enquete exclusive',
    5: 'Envoye Special',
    6: 'Sept a Huit',
    7: 'Complement enquete',
    8: '66 Minutes',
    9: 'Grands reportages',
    10: 'Autre magazine TV',
}

# Labels des chaines TV generalistes (SOURCES1DR_B4_R)
chaines_generalistes = {
    1: 'TF1',
    2: 'France 2',
    3: 'France 3',
    4: 'France 5',
    5: 'Arte',
    6: 'M6',
    7: 'C8',
    8: 'Canal+',
    9: 'TMC',
    10: 'RMC Story',
    11: 'Autre generaliste',
    12: 'TV locale',
}

# Labels des medias RS natifs (SOURCES1FR_R)
medias_rs = {
    1: 'Blast',
    2: 'Atlantico',
    3: 'Rue89',
    4: 'Slate',
    5: 'Linternaute',
    6: 'Konbini',
    7: 'Loopsider',
    8: 'Brut',
    9: 'AJ+',
    10: 'Hugo Decrypte',
    11: 'Samuel Etienne',
    12: 'Autre createur',
    13: 'Autre personnalite',
}

# Labels des chaines info TV (SOURCES1ER_B4_R)
chaines_info = {
    1: 'Franceinfo TV',
    2: 'LCI',
    3: 'BFM TV',
    4: 'CNews',
    5: 'France24',
    6: 'Chaines internationales',
    7: 'Autre internationale',
}

# Labels des emissions quotidiennes (TV2BR_R)
emissions_quotid = {
    1: 'Quotidien',
    2: 'TPMP',
    3: 'Les grandes gueules',
    4: 'C a vous',
    5: 'Heure des pros',
    6: '28 minutes',
    7: 'C dans lair',
    8: '24h Pujadas',
    9: 'Les informes',
    10: 'Telematin',
    11: 'Premiere Edition',
    12: 'C ce soir',
    13: 'Autre emission',
}

# Fonction pour créer variable binaire pour un code spécifique
def utilise_code(df, pattern, code):
    cols = [c for c in df.columns if c.startswith(pattern)]
    result = pd.Series(0, index=df.index)
    for col in cols:
        result = result | (df[col] == code)
    return result.astype(int)

# Fonction pour calculer le % max pondéré par modalité socio-démo
def get_max_pct_by_sociodemo(df, var_pratique, poids='POIDS03'):
    """Calcule le % max de pratique parmi toutes les modalités socio-démo"""
    vi_vars = [
        ('RS2C_RECODE_AG_R', 'Age'),
        ('RS1_R', 'Genre'),
        ('CAPITAL_CULTUREL', 'Diplome'),
        ('CAPITAL_ECO', 'Revenus'),
        ('CC_R', 'Agglo'),
    ]

    max_pct = 0
    max_info = None

    for vi_var, vi_label in vi_vars:
        if vi_var not in df.columns:
            continue

        for cat in df[vi_var].dropna().unique():
            subset = df[df[vi_var] == cat]
            if len(subset) < 30:
                continue

            total_poids = subset[poids].sum()
            pratique_poids = subset[subset[var_pratique] == 1][poids].sum()
            pct = (pratique_poids / total_poids * 100) if total_poids > 0 else 0

            if pct > max_pct:
                max_pct = pct
                max_info = (vi_label, cat, pct, len(subset))

    return max_pct, max_info

print("=" * 70)
print("ANALYSE DES USAGES INDIVIDUELS")
print("=" * 70)

# Créer les capitaux si pas déjà fait
def recode_capital_culturel(rs5):
    if pd.isna(rs5): return None
    if rs5 in [1, 2, 3, 4]: return 'Faible'
    elif rs5 in [5, 6]: return 'Moyen'
    elif rs5 in [7, 8, 9]: return 'Eleve'
    return None

REVENUS_MIDPOINT = {1: 750, 2: 2250, 3: 3750, 4: 6000, 5: 8500, 6: None}
def recode_capital_eco(row):
    rs14, rs7 = row.get('RS14_R'), row.get('RS7_R')
    if pd.isna(rs14) or pd.isna(rs7) or rs14 == 6: return None
    revenu = REVENUS_MIDPOINT.get(rs14)
    if revenu is None: return None
    rev_pers = revenu / (rs7 if rs7 <= 6 else 6)
    if rev_pers < 800: return 'Faible'
    elif rev_pers <= 1500: return 'Moyen'
    else: return 'Eleve'

df['CAPITAL_CULTUREL'] = df['RS5_R'].apply(recode_capital_culturel)
df['CAPITAL_ECO'] = df.apply(recode_capital_eco, axis=1)

# Collecter tous les usages avec leur % max
all_usages = []

# Créer UTILISE_RS et UTILISE_TV sur population totale
news1_cols = [f'NEWS1_R1_{i}' for i in range(1, 10) if f'NEWS1_R1_{i}' in df.columns]
def utilise_source(row, code):
    for col in news1_cols:
        if pd.notna(row[col]) and row[col] == code:
            return 1
    return 0
df['UTILISE_RS'] = df.apply(lambda r: utilise_source(r, 3), axis=1)
df['UTILISE_TV'] = df.apply(lambda r: utilise_source(r, 1), axis=1)

# 1. Chaînes TV GÉNÉRALISTES (sur population TOTALE)
print("\n1. CHAINES TV GENERALISTES (population totale)")
print("-" * 50)

for code, label in chaines_generalistes.items():
    var_name = f'CHAINE_GEN_{code}'
    df[var_name] = utilise_code(df, 'SOURCES1DR_B4_R_', code)

    max_pct, max_info = get_max_pct_by_sociodemo(df, var_name)

    all_usages.append({
        'categorie': 'Chaine generaliste',
        'label': label,
        'code': code,
        'max_pct': max_pct,
        'max_info': max_info,
        'base': 'tous'
    })

    if max_info:
        print(f"  {label}: max {max_pct:.1f}% ({max_info[0]}={max_info[1]}, n={max_info[3]})")
    else:
        print(f"  {label}: max {max_pct:.1f}%")

# 2. Chaînes info TV (sur population TOTALE)
print("\n2. CHAINES INFO TV (population totale)")
print("-" * 50)

for code, label in chaines_info.items():
    var_name = f'CHAINE_INFO_{code}'
    df[var_name] = utilise_code(df, 'SOURCES1ER_B4_R_', code)

    max_pct, max_info = get_max_pct_by_sociodemo(df, var_name)

    all_usages.append({
        'categorie': 'Chaine info TV',
        'label': label,
        'code': code,
        'max_pct': max_pct,
        'max_info': max_info,
        'base': 'tous'
    })

    if max_info:
        print(f"  {label}: max {max_pct:.1f}% ({max_info[0]}={max_info[1]}, n={max_info[3]})")
    else:
        print(f"  {label}: max {max_pct:.1f}%")

# 3. Émissions quotidiennes (sur population TOTALE)
print("\n3. EMISSIONS QUOTIDIENNES (population totale)")
print("-" * 50)

for code, label in emissions_quotid.items():
    var_name = f'EMISSION_{code}'
    df[var_name] = utilise_code(df, 'TV2BR_R_', code)

    max_pct, max_info = get_max_pct_by_sociodemo(df, var_name)

    all_usages.append({
        'categorie': 'Emission TV',
        'label': label,
        'code': code,
        'max_pct': max_pct,
        'max_info': max_info,
        'base': 'tous'
    })

    if max_info:
        print(f"  {label}: max {max_pct:.1f}% ({max_info[0]}={max_info[1]}, n={max_info[3]})")
    else:
        print(f"  {label}: max {max_pct:.1f}%")

# 4. Medias RS natifs (sur population TOTALE)
print("\n4. MEDIAS RS NATIFS (population totale)")
print("-" * 50)

for code, label in medias_rs.items():
    var_name = f'MEDIA_RS_{code}'
    df[var_name] = utilise_code(df, 'SOURCES1FR_R_', code)

    max_pct, max_info = get_max_pct_by_sociodemo(df, var_name)

    all_usages.append({
        'categorie': 'Media RS',
        'label': label,
        'code': code,
        'max_pct': max_pct,
        'max_info': max_info,
        'base': 'tous'
    })

    if max_info:
        print(f"  {label}: max {max_pct:.1f}% ({max_info[0]}={max_info[1]}, n={max_info[3]})")
    else:
        print(f"  {label}: max {max_pct:.1f}%")

# 5. NEWS1: Sources d'information principales
print("\n5. NEWS1 SOURCES INFO (population totale)")
print("-" * 50)

for code, label in news1_sources.items():
    var_name = f'NEWS1_SOURCE_{code}'
    df[var_name] = utilise_code(df, 'NEWS1_R1_', code)

    max_pct, max_info = get_max_pct_by_sociodemo(df, var_name)

    all_usages.append({
        'categorie': 'Source info',
        'label': label,
        'code': code,
        'max_pct': max_pct,
        'max_info': max_info,
        'base': 'tous'
    })

    if max_info:
        print(f"  {label}: max {max_pct:.1f}% ({max_info[0]}={max_info[1]}, n={max_info[3]})")
    else:
        print(f"  {label}: max {max_pct:.1f}%")

# 6. RSINFO_2_LR_R: Plateformes RS pour s'informer (colonnes binaires)
print("\n6. PLATEFORMES RS POUR INFO (population totale)")
print("-" * 50)

for code, label in plateformes_rs.items():
    col_name = f'RSINFO_2_LR_R_{code}'
    if col_name in df.columns:
        var_name = f'PLATEFORME_RS_{code}'
        df[var_name] = (df[col_name] == 1).astype(int)

        max_pct, max_info = get_max_pct_by_sociodemo(df, var_name)

        all_usages.append({
            'categorie': 'Plateforme RS',
            'label': label,
            'code': code,
            'max_pct': max_pct,
            'max_info': max_info,
            'base': 'tous'
        })

        if max_info:
            print(f"  {label}: max {max_pct:.1f}% ({max_info[0]}={max_info[1]}, n={max_info[3]})")
        else:
            print(f"  {label}: max {max_pct:.1f}%")
    else:
        print(f"  {label}: colonne non trouvee")

# 7. SOURCES1BR_B2_R: Journaux/presse ecrite
print("\n7. JOURNAUX/PRESSE ECRITE (population totale)")
print("-" * 50)

for code, label in journaux.items():
    var_name = f'JOURNAL_{code}'
    df[var_name] = utilise_code(df, 'SOURCES1BR_B2_R_', code)

    max_pct, max_info = get_max_pct_by_sociodemo(df, var_name)

    all_usages.append({
        'categorie': 'Journal',
        'label': label,
        'code': code,
        'max_pct': max_pct,
        'max_info': max_info,
        'base': 'tous'
    })

    if max_info:
        print(f"  {label}: max {max_pct:.1f}% ({max_info[0]}={max_info[1]}, n={max_info[3]})")
    else:
        print(f"  {label}: max {max_pct:.1f}%")

# 8. SOURCES1CR_B3_R: Magazines/revues
print("\n8. MAGAZINES/REVUES (population totale)")
print("-" * 50)

for code, label in magazines.items():
    var_name = f'MAGAZINE_{code}'
    df[var_name] = utilise_code(df, 'SOURCES1CR_B3_R_', code)

    max_pct, max_info = get_max_pct_by_sociodemo(df, var_name)

    all_usages.append({
        'categorie': 'Magazine',
        'label': label,
        'code': code,
        'max_pct': max_pct,
        'max_info': max_info,
        'base': 'tous'
    })

    if max_info:
        print(f"  {label}: max {max_pct:.1f}% ({max_info[0]}={max_info[1]}, n={max_info[3]})")
    else:
        print(f"  {label}: max {max_pct:.1f}%")

# 9. TV2AR_R: JT/journaux televises
print("\n9. JT/JOURNAUX TELEVISES (population totale)")
print("-" * 50)

for code, label in jt_tv.items():
    var_name = f'JT_{code}'
    df[var_name] = utilise_code(df, 'TV2AR_R_', code)

    max_pct, max_info = get_max_pct_by_sociodemo(df, var_name)

    all_usages.append({
        'categorie': 'JT',
        'label': label,
        'code': code,
        'max_pct': max_pct,
        'max_info': max_info,
        'base': 'tous'
    })

    if max_info:
        print(f"  {label}: max {max_pct:.1f}% ({max_info[0]}={max_info[1]}, n={max_info[3]})")
    else:
        print(f"  {label}: max {max_pct:.1f}%")

# 10. TV2CR_R: Magazines TV
print("\n10. MAGAZINES TV (population totale)")
print("-" * 50)

for code, label in magazines_tv.items():
    var_name = f'MAG_TV_{code}'
    df[var_name] = utilise_code(df, 'TV2CR_R_', code)

    max_pct, max_info = get_max_pct_by_sociodemo(df, var_name)

    all_usages.append({
        'categorie': 'Magazine TV',
        'label': label,
        'code': code,
        'max_pct': max_pct,
        'max_info': max_info,
        'base': 'tous'
    })

    if max_info:
        print(f"  {label}: max {max_pct:.1f}% ({max_info[0]}={max_info[1]}, n={max_info[3]})")
    else:
        print(f"  {label}: max {max_pct:.1f}%")

# Trouver le seuil optimal
print("\n" + "=" * 70)
print("RECHERCHE DU SEUIL OPTIMAL")
print("=" * 70)

# Trier par % max décroissant
all_usages_sorted = sorted(all_usages, key=lambda x: -x['max_pct'])

print("\nNombre de pratiques conservées selon le seuil:")
for threshold in [5, 10, 15, 20, 25, 30, 35, 40]:
    count = sum(1 for u in all_usages if u['max_pct'] >= threshold)
    print(f"  Seuil {threshold}%: {count} pratiques")

# Pour ~50 pratiques, quel seuil ?
# On a déjà 51 croisements significatifs de base, donc on cherche ~15-20 nouvelles pratiques
print("\n" + "-" * 50)
print("Pour avoir environ 15-20 pratiques supplementaires:")
for threshold in range(5, 50):
    count = sum(1 for u in all_usages if u['max_pct'] >= threshold)
    if 15 <= count <= 25:
        print(f"  Seuil {threshold}%: {count} pratiques")

# Calculer la diffusion ponderee dans la population totale pour chaque pratique
print("\n" + "=" * 70)
print("DIFFUSION PONDEREE POPULATION TOTALE")
print("=" * 70)

total_poids = df['POIDS03'].sum()
for u in all_usages:
    # Trouver la variable correspondante
    cat = u['categorie']
    code = u['code']

    if cat == 'Chaine generaliste':
        var_name = f'CHAINE_GEN_{code}'
    elif cat == 'Chaine info TV':
        var_name = f'CHAINE_INFO_{code}'
    elif cat == 'Emission TV':
        var_name = f'EMISSION_{code}'
    elif cat == 'Media RS':
        var_name = f'MEDIA_RS_{code}'
    elif cat == 'Source info':
        var_name = f'NEWS1_SOURCE_{code}'
    elif cat == 'Plateforme RS':
        var_name = f'PLATEFORME_RS_{code}'
    elif cat == 'Journal':
        var_name = f'JOURNAL_{code}'
    elif cat == 'Magazine':
        var_name = f'MAGAZINE_{code}'
    elif cat == 'JT':
        var_name = f'JT_{code}'
    elif cat == 'Magazine TV':
        var_name = f'MAG_TV_{code}'
    else:
        var_name = None

    if var_name and var_name in df.columns:
        pratique_poids = df[df[var_name] == 1]['POIDS03'].sum()
        pct_total = (pratique_poids / total_poids * 100)
        u['pct_total'] = pct_total
    else:
        u['pct_total'] = 0

print("\n" + "=" * 70)
print("PRATIQUES CONSERVEES (seuil 15%)")
print("=" * 70)

# Re-trier
all_usages_sorted = sorted(all_usages, key=lambda x: -x['max_pct'])

for u in all_usages_sorted:
    if u['max_pct'] >= 15:
        print(f"  {u['label']} ({u['categorie']}): max {u['max_pct']:.1f}%, pop totale {u.get('pct_total', 0):.1f}%")

# Export pour utilisation dans generate_chapitre1_json.py
print("\n" + "=" * 70)
print("EXPORT PYTHON (seuil 15%)")
print("=" * 70)

print("\n# Pratiques a inclure (seuil 15%)")
for cat in ['Source info', 'Plateforme RS', 'Chaine generaliste', 'Chaine info TV',
            'Media RS', 'Emission TV', 'JT', 'Magazine TV', 'Journal', 'Magazine']:
    pratiques = [u for u in all_usages if u['categorie'] == cat and u['max_pct'] >= 15]
    if pratiques:
        print(f"\n# {cat}")
        for u in sorted(pratiques, key=lambda x: -x['max_pct']):
            print(f"#   {u['code']}: '{u['label']}' -> max {u['max_pct']:.1f}%, total {u.get('pct_total', 0):.1f}%")
