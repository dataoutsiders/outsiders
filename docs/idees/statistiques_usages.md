# Idée à court terme : connaître les usages

> Noté le 30/10/2026. À faire juste après les fiches territoire (mêmes pages), avant PISA.

## Existant
GoatCounter sans cookie (index.html + src/lib/analytics.js) : pages vues, provenance, pays, tailles d'écran. Tableau de bord : https://outsiders.goatcounter.com (connexion par l'usager). Les vues /embed ne sont pas comptées.

## À ajouter : des événements (aucune donnée sur la personne)
- territoires consultés dans les fiches (choix des portraits et des collectivités à contacter) ;
- reprises : clics « Intégrer » (carte, nuage), phrases copiées sur /presse, images téléchargées ;
- vues des cartes intégrées ailleurs, comptées à part avec le site d'accueil (qui republie nos cartes) ;
- croisements choisis dans l'Atlas ; usages de l'outil Représentativité (le fait, jamais le contenu) ;
- clics de la rubrique « Dans nos dossiers ».

## Page de statistiques
- Pour l'usager : le tableau de bord GoatCounter (pas de page privée sur le site sans serveur : la clé d'API serait exposée).
- Plus tard : page publique « Audience » (option de GoatCounter), quand les chiffres seront parlants.
- Si le site devient commercial, l'offre gratuite de GoatCounter ne s'applique plus.

# Idée à court terme : newsletter (demande de l'usager, 30/10/2026)

À faire avec les statistiques, juste après les fiches territoire.
- Service spécialisé (le site n'a pas de serveur, aucune adresse stockée chez nous) : Brevo (français, données en Europe, gratuit jusqu'à 300 mails/jour) ou Buttondown ; éviter Substack (met l'auteur en avant). Compte créé par l'usager.
- Anonymat : VÉRIFIER si le service impose une adresse postale en pied de mail ; sinon boîte postale ou domiciliation.
- Formulaire sur l'accueil, en bas des dossiers et sur /presse ; double confirmation.
- Envoi depuis contact@dataoutsiders.fr : enregistrements DNS (SPF, DKIM, DMARC) à préparer, saisis par l'usager dans Cloudflare.
- Mentions légales : données collectées, finalité, durée, désinscription.
- Événement GoatCounter sur l'inscription (quelles pages font s'abonner).
- Plus tard : brouillon de newsletter préparé à chaque nouveau dossier ou mise à jour, relu par l'usager avant envoi.

## FAIT le 30/10/2026 (déployé) : événements GoatCounter
Fonction `trackEvent` (src/lib/analytics.js). Événements :
- `fiche/<niveau>/<code>` : fiche territoire consultée (commune, epci, dept, region) ;
- `fiche-vers-dossier/<dossier>` : clic de la rubrique « Dans nos dossiers » ;
- `atlas-croisement/<indicateur>/<croisement>` : croisement choisi dans l'Atlas ;
- `integrer-carte/<indicateur>`, `integrer-graphique/<ind>/<vs>` : code d'intégration copié ;
- `presse-phrase/<carte>`, `presse-formule`, `presse-iframe`, `presse-image/<page>` : reprises depuis /presse ;
- `outil-representativite` : analyse lancée (aucun contenu du fichier).
Les cartes intégrées ailleurs sont comptées comme pages vues `/embed/...`, avec en provenance le site qui les accueille.
Reste : événement d'inscription à la newsletter (quand le service sera choisi) ; page publique « Audience » plus tard.

## FAIT le 30/10/2026 : newsletter en place

Compte Brevo créé par l'usager, domaine authentifié (DNS saisis dans Cloudflare et vérifiés), expéditeur
« Outsiders » contact@dataoutsiders.fr, formulaire et liste « Newsletter Outsiders », inscription SANS mail
de confirmation (choix de l'usager). Sur le site : formulaire maison sans script tiers, page /newsletter,
accueil, /presse, pied de page, mentions légales, événement `newsletter-inscription/<page>`. Test réussi
(adresse reçue dans la liste). Tout est décrit dans docs/DEPLOIEMENT.md, §5 bis.
Reste : première newsletter ; vérifier le pied de mail (adresse postale) sur un envoi de test ; suivi des
ouvertures et des clics à désactiver dans chaque campagne.
