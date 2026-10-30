/**
 * Newsletter (Brevo, formule gratuite) : formulaire « Newsletter Outsiders », liste
 * « Newsletter Outsiders », SANS mail de confirmation (choix de l'usager, 30/10/2026) : l'adresse
 * est inscrite dès l'envoi, aucun mail ne part. Si l'on ajoute un jour un mail de confirmation
 * (simple ou double), adapter les textes de NewsletterForm, de /newsletter et des mentions légales.
 * La page /newsletter?confirme=1 reste prête pour ce cas.
 *
 * Le site n'intègre PAS le formulaire de Brevo (scripts, polices, captcha éventuel) pour
 * rester sans cookie : NewsletterForm envoie l'adresse directement à l'adresse d'envoi du
 * formulaire. Ces adresses sont publiques par nature (elles figurent dans tout formulaire
 * intégré) ; si le formulaire est recréé dans Brevo, les remplacer ici.
 */
const FORMULAIRE =
  'https://f0b96a2f.sibforms.com/serve/MUIFANaScOu7SmxrMqPVywMh4Hi8xSJG4PsKzRNBoiqgdppHxGT-X0ptyt00yaGRo_T07qctwUWmSqJpgrEakG08YBE1U9vmvQHQ2EsgpLnvmRCr5uuqukqLgyGvztDnUralfEcukOeiamOKzEh6lob7ICa1r2nJc6kq8PFq7_MYVplJsrQbWOVD9Ht9OpUuRTaTJrA2xvjnmRm9Rw=='

// Adresse d'envoi du formulaire (attribut action du code d'intégration de Brevo).
export const NEWSLETTER_ACTION = FORMULAIRE

// Page d'inscription hébergée par Brevo : solution de repli si l'envoi direct échoue.
export const NEWSLETTER_PAGE_BREVO = FORMULAIRE
