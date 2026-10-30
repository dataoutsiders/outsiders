"""Fix the frontend JSON file with proper encoding and corrected data"""
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

# Read generated JSON (has correct forest-plot data)
with open(BASE_DIR / "outputs" / "json" / "chapitre-01-basculement.json", 'r', encoding='utf-8') as f:
    data = json.load(f)

# Update accroche with odds ratio
data['accroche'] = {
    'texte': "Un jeune de 18-24 ans a 45 fois plus de chances de citer les réseaux sociaux comme source principale d'information qu'une personne de 70 ans ou plus. Un rapport qui interroge : assiste-t-on à une révolution des pratiques ou à un simple effet d'âge ?",
    'chiffreMarquant': {
        'valeur': '45',
        'unite': '×',
        'label': "plus de chances pour les 18-24 ans de s'informer via les RS que les 70+"
    }
}

# Add prenotions
data['prenotions'] = {
    'titre': "Ce que l'on croit savoir",
    'introduction': "Avant d'explorer les données, confrontons les idées reçues qui circulent dans le débat public avec ce que montrent nos analyses de l'enquête ARCOM 2024.",
    'items': [
        {
            'prejuge': "Les jeunes désertent les médias traditionnels",
            'sourceIdee': {
                'citation': "Nous sommes à un point de bascule. La jeunesse est en train de décrocher de tous les médias traditionnels.",
                'source': "France Télévisions",
                'url': "https://www.cbnews.fr/medias/image-france-televisions-muscle-ses-programmes-jeunes-79448"
            },
            'nosResultats': "19% des 18-24 ans citent encore la TV comme source principale d'information. Certes, c'est bien moins que les 62% des 70 ans et plus, mais la TV reste la 2ème source pour les jeunes derrière les réseaux sociaux (36%).",
            'verdict': 'partiellement_vrai',
            'pourAllerPlusLoin': [
                {'titre': "Les JO font revenir les jeunes vers la TV", 'source': "Médiamétrie / France Info", 'url': "https://www.franceinfo.fr/replay-radio/info-medias/les-jo-et-le-feuilleton-politique-ont-fait-revenir-les-jeunes-vers-la-television-en-2024-selon-mediametrie_7002287.html"}
            ]
        },
        {
            'prejuge': "Les jeunes sont plus vulnérables à la désinformation",
            'sourceIdee': {
                'citation': "75% des jeunes identifient les réseaux sociaux comme le principal vecteur de fake news. [...] Les jeunes seraient les premières victimes de la désinformation en ligne.",
                'source': "L'Info Durable / Sondage 2024",
                'url': "https://www.linfodurable.fr/societe/pour-77-des-jeunes-la-lutte-contre-la-desinformation-passe-dabord-par-lecole-53472"
            },
            'nosResultats': "Score quizz moyen des 18-24 ans : 1.74/4. Score des 70 ans et plus : 1.61/4. Les jeunes ne sont pas moins bien informés que leurs aînés sur les questions d'actualité testées.",
            'verdict': 'faux',
            'pourAllerPlusLoin': [
                {'titre': "Fake news : les ados peuvent se défendre", 'source': "CNRS Le Journal / De Facto", 'url': "https://lejournal.cnrs.fr/articles/fake-news-oui-les-adolescents-peuvent-se-defendre"}
            ]
        },
        {
            'prejuge': "TikTok remplace Google chez les jeunes",
            'sourceIdee': {
                'citation': "32% des 15-34 ans s'informent uniquement par les RS, TikTok est devenu le 4ème moteur de recherche",
                'source': "Digimind 2024",
                'url': "https://blog.digimind.com/fr/tendances/quels-usages-de-linformation-et-des-m%C3%A9dias-en-2024-focus-sur-7-pays"
            },
            'nosResultats': "36% des 18-24 ans citent les réseaux sociaux comme source principale d'information. Mais 64% utilisent encore d'autres sources (TV, radio, presse, sites). Les RS dominent mais ne remplacent pas totalement les autres médias.",
            'verdict': 'partiellement_vrai',
            'pourAllerPlusLoin': [
                {'titre': "Usages de l'information et des médias en 2024", 'source': "Digimind", 'url': "https://blog.digimind.com/fr/tendances/quels-usages-de-linformation-et-des-m%C3%A9dias-en-2024-focus-sur-7-pays"}
            ]
        },
        {
            'prejuge': "La TV est morte pour les moins de 25 ans",
            'sourceIdee': {
                'citation': "La télévision linéaire n'intéresse plus du tout les jeunes générations",
                'source': "Idée reçue médiatique",
                'url': None
            },
            'nosResultats': "19% des 18-24 ans et 29% des 15-17 ans citent la TV comme source principale. Près d'1 jeune sur 5 reste fidèle à la télévision pour s'informer. Elle n'est pas morte, mais a perdu sa position dominante.",
            'verdict': 'faux',
            'pourAllerPlusLoin': [
                {'titre': "Les JO 2024 font revenir les jeunes vers la TV", 'source': "Médiamétrie / France Info", 'url': "https://www.franceinfo.fr/replay-radio/info-medias/les-jo-et-le-feuilleton-politique-ont-fait-revenir-les-jeunes-vers-la-television-en-2024-selon-mediametrie_7002287.html"}
            ]
        }
    ],
    'conclusion': "Sur 4 préjugés examinés : 2 sont faux, 2 partiellement vrais. La réalité est plus complexe que les raccourcis médiatiques. Voyons les données en détail."
}

# Update description
data['analyse']['sections'][0]['description'] = "Quels facteurs sociaux expliquent le mieux les différences de pratiques informationnelles ? Les facteurs analysés sont : âge, milieu social, niveau d'études, revenus, genre et taille d'agglomération."

# Update title and description
data['analyse']['sections'][0]['visualisations'][0]['titre'] = "Force d'association des facteurs sociaux avec les sources d'information"
data['analyse']['sections'][0]['visualisations'][0]['description'] = "V de Cramer (pondéré) : 0 = pas de lien, 0.1 = faible, 0.2 = modéré, 0.3+ = fort"

# Update sousTitre
data['sousTitre'] = "TV vs Réseaux sociaux : un clivage générationnel ?"

# Save to frontend
frontend_path = BASE_DIR.parent / "frontend" / "public" / "data" / "enquetes" / "francais-information" / "chapitres" / "chapitre-01-basculement.json"
with open(frontend_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Frontend JSON fixed with proper encoding")
print(f"Output: {frontend_path}")

# Show first 3 forest plot entries
forest = data['analyse']['sections'][0]['visualisations'][0]['data']
print(f"\nTop 3 croisements (sur {len(forest)}):")
for d in forest[:3]:
    dist = d.get('distribution', [])
    print(f"  {d['var1']} -> {d['var2']}: V={d['v_cramer']}")
    if dist:
        print(f"    {dist[0]['category']}: {dist[0]['pct_oui']}% -> {dist[-1]['category']}: {dist[-1]['pct_oui']}%")
