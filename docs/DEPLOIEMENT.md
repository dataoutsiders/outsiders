# Outsiders, Fiche de référence (déploiement & infos)

> Tout ce qu'il faut pour retrouver, mettre à jour et faire évoluer le site.
> Dernière maj : 2026-07-04. (Aucun mot de passe / token ici, voir « Sécurité » en bas.)

---

## 1. Adresses

| | URL |
|---|---|
| **Production** (à partager) | **https://dataoutsiders.fr/** (et `www.dataoutsiders.fr`) |
| Adresse technique Cloudflare | https://outsiders-pu2.pages.dev/ (toujours active) |
| Développement local | `http://localhost:5173/` (lancer `npm run dev` dans `frontend/`) |

Exemple de lien profond partageable (l'état est dans l'URL) :
`https://dataoutsiders.fr/atlas?i=revenu&dep=93`

---

## 2. Comptes & identifiants

| Élément | Valeur |
|---|---|
| **Hébergement** | Cloudflare Pages, compte **`dataoutsiders@gmail.com`**, projet **`outsiders`** |
| Email contact / projet | `contact@dataoutsiders.fr` affiché sur le site, renvoyé vers `dataoutsiders@gmail.com` par Cloudflare Email Routing (réception seule ; les réponses partent du Gmail) |
| Registrar du domaine | **Scaleway** (BookMyName), `dataoutsiders.fr` acheté le 2026-10-29 ; serveurs de noms délégués à Cloudflare (`tia.ns.cloudflare.com`, `zeus.ns.cloudflare.com`), DNSSEC à laisser désactivé chez Scaleway (réactivable depuis Cloudflare) ; zone Cloudflare en offre Free, domaine relié au projet Pages (Custom domains) |
| VPS (existant, autre projet) | OVH VPS-1, partagé avec muzik-arsiv. **Non utilisé** pour Outsiders (alternative possible) |
| Auth déploiement | Cloudflare OAuth via `wrangler login` (jeton stocké en local, pas de mot de passe à retenir) |
| **Sauvegarde du code** | **GitHub**, compte `dataoutsiders` (dataoutsiders@gmail.com), dépôt **privé** `https://github.com/dataoutsiders/outsiders`, mis en place le 2026-10-30. Identité Git **locale au dépôt** : `Outsiders <248203330+dataoutsiders@users.noreply.github.com>` (l'identité Git globale de la machine est nominative et professionnelle : ne jamais la laisser signer un enregistrement d'Outsiders). Ne jamais envoyer ce dépôt vers la forge professionnelle (forge.apps.education.fr). Exclus du dépôt (`.gitignore`) : `python/data/` (données brutes de plusieurs Go et listes nominatives), caches, `_archive/`, sauvegardes `.bak`, `.claude/`, documents personnels. Données brutes : copie ponctuelle sur disque externe |
| **Newsletter** | **Brevo**, formule gratuite, compte créé par l'usager le 2026-10-30 (organisation « Data Outsiders »). Domaine `dataoutsiders.fr` authentifié, expéditeur « Outsiders » `contact@dataoutsiders.fr`. Voir §5 bis |

---

## 3. Architecture (pourquoi pas de backend)

- Site **statique** : React/Vite compilé → fichiers servis par le **CDN mondial Cloudflare**. Rapide, gratuit, scale tout seul.
- **Le « backend » = les scripts Python** (`python/tools/`), qui tournent **hors-ligne** et précalculent des JSON. Rien ne tourne par requête.
- L'outil onomastique tourne **100 % dans le navigateur** → aucune donnée perso ne transite. À garder ainsi.
- Liens profonds : `frontend/public/_redirects` (`/* /index.html 200`) renvoie toute URL vers l'app (fallback SPA).

---

## 4. Mettre à jour le site

### A. Changement de code / design → **une commande**
Dans `frontend/` :
```
npm run deploy
```
(= `npm run build` + déploiement Cloudflare). Renvoie l'URL de déploiement à la fin.

> `npm run build` enchaîne trois étapes : `vite build`, puis **`scripts/generate-og.mjs`**
> (une image de partage 1200×630 par route dans `dist/og/`, satori + resvg, source `config/seo.js`),
> puis **`scripts/prerender-meta.mjs`** (écrit `dist/<route>/index.html` avec title/description/OG par
> route, pour les aperçus sur les réseaux, le site étant une SPA sans rendu serveur). Pour des og:url /
> og:image absolus sur un autre domaine : `SITE_URL=https://mondomaine npm run build` (défaut = la
> constante `SITE_URL` de `config/seo.js`).

> **Première fois sur une nouvelle machine** : `npx wrangler login` dans un **terminal normal** (PowerShell/VS Code), pas via `!` (sinon ça part en arrière-plan et le login échoue). Autoriser dans le navigateur → « Successfully logged in ». Ensuite `npm run deploy` marche tout seul.

### B. Rafraîchir les **données** (quand les sources open data sont mises à jour, ~1×/an)
Avec le venv Python (`.venv\Scripts\python.exe` à la racine), lancer **dans cet ordre** :
```
python python/tools/build_onomastics_reference.py   # → surnames.tsv, firstnames.json (référentiel IDP/sexe/âge)
# Revenu : python/tools/revenu_filosofi.py (Insee Filosofi 2023, cache _cache_filosofi/) est importé par build_ecole, build_atlas_communes et build_atlas_epci.
python python/tools/build_ecole.py                  # → ecole-ips.json, ecole-communes.json, etablissements.tsv
python python/tools/build_atlas_communes.py         # → atlas/departements.json + atlas/communes/<dep>.json (dépend de build_ecole)
python python/tools/build_atlas_epci.py             # → geo/epci.geojson (contours simplifiés) + atlas/epci.json (maille EPCI ; dépend de build_atlas_communes + build_ecole)
# Indicateurs INSEE recensement/état civil fusionnés dans communes/dept/epci (dépendent de build_atlas_communes + build_atlas_epci) :
python python/tools/build_atlas_insee.py            # → diplôme du supérieur (RP 2023, DS_RP_DIPLOMES_PRINC, https://www.insee.fr/fr/statistiques/9006527)
python python/tools/build_atlas_logement.py         # → hlm, res_secondaires, vacants, proprietaires, maisons (RP 2023, DS_RP_LOGEMENT_PRINC, https://www.insee.fr/fr/statistiques/8997194 ; CSV de 1,2 Go lu par morceaux)
python python/tools/build_atlas_demo.py             # → jeunes 0-14, ages65 (RP 2023, DS_RP_POPULATION_PRINC, https://www.insee.fr/fr/statistiques/9005956)
python python/tools/build_atlas_pcs.py              # → cadres, intermediaires, employes, ouvriers (RP 2023, exploitation complémentaire DS_RP_EMPLOI_LR_COMP, https://www.insee.fr/fr/statistiques/9002680)
python python/tools/build_atlas_natalite.py         # → natalité ‰ (naissances 2021-2025, base_naissances_2008-2025_geo2026_xlsx.zip, https://www.insee.fr/fr/statistiques/1893255 + population RP 2023 9005956)
python python/tools/build_atlas_sante.py            # → apl_mg, apl_mg_60, apl_dentistes, apl_kines, apl_infirmieres, apl_sages_femmes (Drees, APL 2024, jeu 530_l-accessibilite-potentielle-localisee-apl) + depassement_spe, secteur2_spe (Assurance maladie 2025, département seulement) ; fichiers en cache dans _cache_sante/, numerateurs-departements.json repris par build_territoires_echelles
python python/tools/build_atlas_population.py        # → champ technique `pop` (population RP 2023, 9005956) par commune/dept/EPCI ; sert au moteur de résidus, PAS un indicateur affiché
python python/tools/build_pratiques.py              # → showcases/pratiques.json + geo/regions.geojson (dossier Modes de vie ; autonome, lit atlas/departements.json pour les noms ; INCA 3 en cache dans _cache_inca3/, Baromètre et Assurance maladie dans _cache_pratiques/, à vider pour rafraîchir)
python python/tools/build_votes.py                  # → showcases/votes-assemblee.json (votes de la 17e législature ; fichiers officiels dans _cache_votes/, 50 Mo ; vider ce dossier pour rafraîchir)
python python/tools/build_omnivore.py               # → showcases/omnivore.json (section « L'omnivore à l'épreuve » ; prix Insee dans _cache_pratiques/ipc-pm.xml, rappels de 24 h dans _cache_inca3/conso-compo-alim.csv, 200 Mo)
python python/tools/build_territoires_echelles.py   # → atlas/epci-communes.json (communes de chaque intercommunalité), atlas/regions.json (valeurs régionales officielles ou recalculées comme au département, contrôle d'écart affiché), territoires/auto-ecoles-departements.json (extrait du dossier Auto-écoles) ; APRÈS tous les build_atlas_* et build_ecole, et à relancer après build_auto_ecoles.py (plus bas) pour que l'extrait Auto-écoles suive ; statistiques DVF en cache dans _cache_territoires/
python python/tools/build_territoires_index.py      # → atlas/territoires-index.json + stats-nationales.json (+ tranches de population ; hors-ligne ; relancer APRÈS tout ajout d'indicateur atlas ET après build_atlas_population)
python python/tools/build_atlas_vecteurs.py          # → communes-vecteurs.json (jumeau statistique, communes >= 1000 hab. + centroïdes geo.api ; après build_atlas_population)
python python/tools/build_showcase_elus.py          # → elus-diversite.json (terrain Élus)
python python/tools/build_assemblee.py              # → assemblee.json (terrain Assemblée : sexe/âge/PCS/IDP par groupe + collaborateurs ; open data AN 17e législature, cache _cache_assemblee/ à vider après remaniement de groupes ; APRÈS build_onomastics_reference (surnames.tsv))
python python/tools/build_parcoursup.py             # → selectivite.json (terrain Sélectivité : filières par taux d'accès, licences ouvertes par région, matrice académie × filière, boursiers ; jeu fr-esr-parcoursup MESR, cache _cache_parcoursup/ à vider à chaque session)
python python/tools/explore_sport_injep.py ; python python/tools/explore_sport_offre.py ; python python/tools/build_showcase_sport.py   # → showcases/sport.json (dossier Sport ; ~2,5 Go de téléchargements dans python/data/sport/)
python python/tools/build_evolution_revenus.py      # → showcases/evolution-revenus.json (dossier « Qui s'enrichit, qui décroche ? » ; après build_atlas_population)
python python/tools/build_segregation.py            # → segregation/villes.json + <code>.json + colleges-evitement.json + departements.json (ségrégation revenu 3 axes + âge par ville, carreaux FiLoSoFi 200 m via API Koumoul + interdécile IRIS + agrégat territorial par département ; APRÈS build_ecole (etablissements.tsv, évitement scolaire) et build_territoires_index (noms de départements) ; cache dans python/tools/_cache_segregation/, vider pour re-télécharger ; modes : `ecole` = évitement établissement seul, `terr` = agrégat départemental seul)
python python/tools/build_croisements.py            # → atlas/croisements.json (cartes-croisements de l'Atlas : sélection auto + outliers nommés ; textes surchargés par docs/croisements/overrides.json ; APRÈS tous les build_atlas_*)
python python/tools/build_international.py          # → decoupages/pays.json (unité Pays + dossier /international : 8 indicateurs Eurostat, 30 pays UE27+AELE, moyenne UE27 en repère, séries France vs UE27 depuis 1995 ; autonome, API Eurostat en direct ; mettre à jour `time` dans les params à chaque millésime)
python python/tools/build_auto_ecoles.py            # → showcases/auto-ecoles.json (terrain Auto-écoles : taux de réussite permis B par école, attendu « à contexte égal » département + commune (taille, âge, logement, diplômes, IPS des collèges publics avec repli intercommunalité puis département), écarts rétrécis + intervalles 95 %, décomposition, leviers, écoles en ligne, corrélations départementales dont brevet et IVAL ; APRÈS build_atlas_* et build_territoires_index (lit atlas/communes, epci.json, departements.json + python/data/municipales/communes-epci.json) ; télécharge Sécurité routière + La Poste + centres geo.api + brevet par établissement dans _cache_auto_ecoles/, vider ce dossier pour rafraîchir ; `--explore` compare les spécifications du modèle sans rien écrire)
```
Puis re-déployer : `cd frontend ; npm run deploy`.

> **Recensement (RP 2023 et suivants)** : depuis le RP 2023, l'INSEE ne diffuse plus de « base-cc » à colonnes
> P21_... mais des CSV « longs » codés (`DS_RP_<THEME>_PRINC|COMP_2023_CSV_FR.zip` + `_metadata.csv`). Le module
> `python/tools/rp2023.py` les télécharge au besoin dans `python/data/insee_maj/`, les lit par morceaux et décrit
> chaque série avec les libellés INSEE ; les correspondances avec les anciennes variables sont écrites en tête de
> chaque `build_atlas_*.py`. Au millésime suivant : changer `ANNEE` et les noms de jeux dans `SOURCES`.

> **Ségrégation** : `build_segregation.py` est autonome (il lit `communes-vecteurs.json` pour la liste
> des villes > 10 000 hab. et interroge l'API Koumoul des carreaux FiLoSoFi ; ~1000 requêtes, quelques
> minutes). Il met les carreaux en cache disque (`_cache_segregation/`) : relancer est instantané ;
> **vider ce dossier** pour forcer un nouveau téléchargement (ex. nouveau millésime FiLoSoFi ou nouveaux
> champs). Il peut tourner en mode échantillon : `python build_segregation.py 75056 13055` (affiche, n'écrit rien).

### C. Déploiement **100 % automatique** (sur `git push`), optionnel, pour plus tard
1. Le code est déjà sur **GitHub** (§ D ci-dessous).
2. Cloudflare → projet `outsiders` → **Connect to Git**.
   - Build command : `npm run build` · Build output : `frontend/dist` · Root : `frontend`
3. Chaque `git push` redéploie automatiquement. (Pratique si plusieurs contributeurs ou maj fréquentes.)

### D. Sauvegarder (Git et GitHub), après chaque lot de modifications

Le dépôt est sur GitHub (privé) depuis le 2026-10-30, voir §2. Depuis la racine du projet :
```bash
git status                      # ce qui a changé
git add -A
git commit -m "Ce qui a changé, en une phrase"
git push                        # vers github.com/dataoutsiders/outsiders
```
- L'identité est **locale au dépôt** (`git config user.name` doit afficher « Outsiders ») ; ne jamais commiter avec
  l'identité globale de la machine. L'adresse distante contient `dataoutsiders@` pour que Git utilise ce compte et
  pas un autre compte GitHub présent sur le poste.
- Avant un enregistrement important : `git grep -i -l "<nom réel>"` ne doit rien trouver hors des fichiers publics
  de prénoms et de noms de l'Insee.
- `.gitignore` exclut `python/data/`, les caches, `_archive/`, les `.bak` : copier `python/data/` sur un disque
  externe de temps en temps.

---

## 5. Statistiques d'utilisation → **GoatCounter** (en place)

Tableau de bord : **https://outsiders.goatcounter.com** (compte code `outsiders`). Sans cookies,
RGPD-friendly, pas de bandeau de consentement, visites `localhost` ignorées.

- Balise dans `frontend/index.html` (`<script data-goatcounter="https://outsiders.goatcounter.com/count" … src="//gc.zgo.at/count.js">`) : compte la 1re page au chargement.
- Comptage des navigations **SPA** (react-router) : hook `usePageviews()` dans `src/lib/analytics.js`, branché dans `App.jsx` (saute la 1re vue déjà comptée, exclut les vues `/embed`). Sans lui, seule la page d'entrée serait comptée.

> **Pourquoi pas Cloudflare Web Analytics** : il exige un domaine ajouté comme « zone » Cloudflare ;
> `outsiders-pu2.pages.dev` n'en est pas une, d'où l'erreur « pas de site ». À reconsidérer une fois
> `dataoutsiders.fr` branché (§6). Le projet Pages garde par ailleurs des métriques serveur basiques
> (Workers & Pages → outsiders → Metrics), sans visiteurs uniques.

Alternatives évaluées si un jour on veut posséder les données : **Umami** auto-hébergé sur le VPS OVH,
ou **Plausible** (payant).

---

## 5 bis. Newsletter → **Brevo** (en place depuis le 2026-10-30)

**Compte** : Brevo, formule gratuite (300 mails par jour, contacts illimités), créé et administré par l'usager.
Je n'y ai pas accès : toute action dans Brevo (liste, campagne, envoi) est faite par l'usager.

**DNS** (saisis à la main dans Cloudflare le 2026-10-30, vérifiés par requête DNS ; ne pas utiliser la
connexion automatique Brevo-Cloudflare, qui risquerait de doubler le SPF) :

| Type | Nom | Valeur | Proxy |
|---|---|---|---|
| TXT | `@` | `brevo-code:99fa7f5de130ebb6cf37cdab37a01294` | |
| CNAME | `brevo1._domainkey` | `b1.dataoutsiders-fr.dkim.brevo.com` | **DNS uniquement** |
| CNAME | `brevo2._domainkey` | `b2.dataoutsiders-fr.dkim.brevo.com` | **DNS uniquement** |
| TXT | `_dmarc` | `v=DMARC1; p=none; rua=mailto:rua@dmarc.brevo.com` | |

Le SPF existant (`v=spf1 include:_spf.mx.cloudflare.net ~all`, pour la réception par Email Routing) est
**inchangé** : Brevo n'en demande pas, l'alignement DMARC passe par DKIM. Ne jamais créer un second SPF.
Sous-domaine de suivi des liens (« send », « mail »…) : non configuré, facultatif.

**Brevo** : formulaire « Newsletter Outsiders » (type pleine page / intégré, un seul champ : e-mail),
liste « Newsletter Outsiders » (la « Votre première liste » créée par défaut n'est pas utilisée),
**sans mail de confirmation** (choix de l'usager ; la double confirmation avait été conseillée). Test du
2026-10-30 : inscription depuis le site reçue dans la liste.

**Site** : formulaire maison, sans script, police ni captcha de Brevo (le site reste sans cookie).
`src/components/NewsletterForm.jsx` envoie l'adresse en POST `no-cors` à l'adresse d'envoi du formulaire
(`src/config/newsletter.js` : champs `EMAIL`, `email_address_check` vide, `locale`, `html_type`). La réponse
de Brevo n'est pas lisible : seule une inscription test permet de vérifier que la chaîne marche. Formulaire
sur `/newsletter`, en bas de l'accueil, sur `/presse` et dans le pied de page. Événements GoatCounter
`newsletter-inscription/<page>` (et `newsletter-confirmee`, prêt pour une éventuelle double confirmation).
Mentions légales : adresse seule, prestataire Brevo, conservation jusqu'à la désinscription, consentement.

**Si le formulaire est recréé dans Brevo** : remplacer l'adresse dans `src/config/newsletter.js`.
**Si l'on ajoute un mail de confirmation** (simple ou double) : adapter les textes de `NewsletterForm.jsx`,
`pages/Newsletter.jsx` et `pages/MentionsLegales.jsx` (la page `/newsletter?confirme=1` est prête).

**Avant chaque envoi** : relire la liste et supprimer les adresses fantaisistes (aucune vérification à
l'inscription) ; désactiver le suivi des ouvertures et des clics dans la campagne (cohérent avec un site qui
ne trace personne) ; ajouter `?utm_source=newsletter` aux liens vers le site (mesure anonyme dans GoatCounter) ;
vérifier sur un envoi de test ce qu'affiche le pied de mail (adresse postale exigée par Brevo).

---

## 6. Brancher le domaine `dataoutsiders.fr`

1. **Acheter** `dataoutsiders.fr` chez le registrar habituel (celui du site musique, ≠ OVH). ~8-15 €/an. *(Achat = toi, ta carte.)*
2. Cloudflare → **Add a domain** (confier le DNS à Cloudflare ; suivre l'assistant pour pointer les nameservers chez le registrar).
3. Projet Pages `outsiders` → **Custom domains → Set up a domain** → `dataoutsiders.fr`. Cloudflare crée le certificat HTTPS automatiquement.

---

## 7. Stack & structure

- **Frontend** : React 19 + Vite 7 + Tailwind 4 + react-router 7 + **Leaflet** (cartes) + **recharts** (graphes).
- **Données** : JSON statiques précalculés dans `frontend/public/data/` + `geo.api.gouv.fr` (contours communes) à la volée.

- **SEO / partage** : `config/seo.js` (titres + descriptions par route, source unique) ; hook
  `lib/meta.js` (met à jour title/OG au fil de la navigation) ; `scripts/generate-og.mjs` +
  `scripts/prerender-meta.mjs` (images + HTML statiques par route au build). Voir §4A.
- **Audience** : `lib/analytics.js` + balise GoatCounter dans `index.html`. Voir §5.
- **Tests** : `npm test` (vitest) sur les libs statistiques (`lib/residuals`, `lib/territoire`,
  `lib/jumeau`, moteur onomastique).

```
outsiders/
├── frontend/
│   ├── src/                  # app React (pages/, components/, config/, lib/, tools/onomastics/)
│   ├── scripts/              # generate-og.mjs, prerender-meta.mjs (post-build SEO/og:image)
│   ├── public/data/          # données servies (onomastics, showcases, atlas, segregation, decoupages, geo)
│   ├── public/_redirects     # fallback SPA
│   └── dist/                 # build (généré, déployé sur Cloudflare ; inclut dist/og/*.png)
├── python/
│   ├── tools/                # pipelines de données (build_*.py, dont build_segregation.py)
│   └── data/municipales/     # données sources (candidatures, IPS, etc.)
├── docs/                     # vision-et-sujets.md (cap & sujets), veille-open-data.md, ce fichier
└── _archive/                 # ancien site (enquêtes/chapitres) + python/_archive/ (scripts jetables)
```

---

## 8. Coûts

| Poste | Coût |
|---|---|
| Cloudflare Pages (hébergement + CDN + HTTPS + analytics) | **0 €** |
| Domaine `.fr` | ~**8-15 €/an** |
| Newsletter Brevo (formule gratuite) | **0 €** |
| **Total** | ~10 €/an |

---

## 9. Sécurité

- **Aucun secret dans ce dépôt** : pas de mot de passe, pas de token API. L'auth Cloudflare passe par `wrangler login` (OAuth local).
- Le site ne collecte **aucune donnée personnelle** lui-même (outil 100 % navigateur, analytics sans cookies) ; les adresses de la newsletter sont envoyées directement à Brevo et conservées chez lui, jamais par le site.
- Surface d'attaque faible : statique, pas de backend, arbre de dépendances petit et moderne. `npm audit` occasionnel suffit.
