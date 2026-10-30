# Idées : une version payante ?

> Notes du 30/10/2026, question posée « au cas où ». Rien n'est engagé.

## Préalables
- Vendre fait perdre l'anonymat : un éditeur professionnel doit s'identifier (nom, SIRET, conditions de vente). Choisir entre anonymat et vente, ou vendre par une autre structure.
- Cumul d'activités : autorisation de l'employeur tant que l'usager est agent public (même sujet que le catalogue freelance).
- Données publiques et contenus CC BY restent gratuits : on vend du temps, de l'outillage ou du sur-mesure, pas la donnée.

## Pistes, du plus réaliste au plus incertain
1. Études et portraits sur commande (collectivités, agences d'urbanisme, associations) ; achat sans appel d'offres sous 40 000 € HT ; offre O5 du catalogue.
2. « Rapport de territoire » complet : tous les indicateurs, comparaisons choisies, zonage à façon, export Excel, mise à jour annuelle. Prolonge le générateur de portraits.
3. « Mettez vos données, on calcule l'écart à l'attendu » : implantations, adhérents, résultats d'enquête ; calcul dans le navigateur (aucune donnée stockée, argument RGPD).
4. IA : rédaction à partir des seuls chiffres du site, avec contrôle du chiffre exact (leçon de Sup'Doc) ; coût par question, donc payant ; risque de crédibilité, en dernier.
5. Don ou adhésion : simple, rapporte peu.
À éviter : publicité, site entièrement payant.

## Technique
Aujourd'hui site statique sans comptes. Il faudrait : identification, paiement (Stripe), petit serveur (Cloudflare Workers), conditions de vente, TVA (franchise en base), support.

## Prochaine étape conseillée
Tester la demande dans les invitations aux collectivités et agences d'urbanisme (« un rapport complet sur votre territoire vous intéresserait-il ? ») avant de construire quoi que ce soit.
