# -*- coding: utf-8 -*-
"""
Sujet A « Qui represente qui ? » - VALIDATION des donnees Assemblee nationale (n'ecrit rien).

Verifie que l'open data AN (acteurs / organes / mandats, 17e legislature) porte bien ce
qu'il faut pour le terrain : sexe, date de naissance, NOM (pour le moteur IDP),
profession declaree ET categorie socioprofessionnelle INSEE, groupe politique actif.
Affiche les couvertures de champs et les premieres distributions par groupe.

Usage : python python/tools/validate_assemblee.py
Cache : python/tools/_cache_assemblee/
"""
import io
import json
import urllib.request
import zipfile
from collections import Counter
from datetime import date
from pathlib import Path

CACHE = Path(__file__).resolve().parent / "_cache_assemblee"
CACHE.mkdir(exist_ok=True)
H = {"User-Agent": "outsiders/1.0"}

URLS = [
    # deputes actifs + mandats actifs + organes, 17e legislature
    "https://data.assemblee-nationale.fr/static/openData/repository/17/amo/deputes_actifs_mandats_actifs_organes/AMO10_deputes_actifs_mandats_actifs_organes.json.zip",
    "https://data.assemblee-nationale.fr/static/openData/repository/17/amo/deputes_actifs_mandats_actifs_organes_divises/AMO10_deputes_actifs_mandats_actifs_organes.json.zip",
]


def fetch_zip():
    cached = CACHE / "amo10.zip"
    if cached.exists():
        print(f"   cache : {cached}")
        return cached.read_bytes()
    for url in URLS:
        try:
            print(f"   essai : {url}")
            with urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=300) as r:
                blob = r.read()
            cached.write_bytes(blob)
            return blob
        except Exception as e:
            print(f"   echec : {e}")
    raise RuntimeError("aucune URL ne repond, verifier data.assemblee-nationale.fr")


def get(d, *keys):
    for k in keys:
        if not isinstance(d, dict):
            return None
        d = d.get(k)
    return d


def txt(v):
    """Normalise un champ AN : les valeurs vides arrivent en dict {'@xsi:nil': 'true'}."""
    if isinstance(v, dict):
        v = v.get("#text")
    return v if isinstance(v, str) and v.strip() else None


def main():
    print("Telechargement open data AN (17e legislature)...")
    zf = zipfile.ZipFile(io.BytesIO(fetch_zip()))
    names = zf.namelist()
    acteurs_f = [n for n in names if "/acteur/" in n and n.endswith(".json")]
    organes_f = [n for n in names if "/organe/" in n and n.endswith(".json")]
    print(f"   {len(acteurs_f)} acteurs, {len(organes_f)} organes")

    # Organes : uid -> (type, sigle, libelle)
    organes = {}
    for n in organes_f:
        o = json.loads(zf.read(n).decode("utf-8")).get("organe", {})
        organes[get(o, "uid")] = (get(o, "codeType"), get(o, "libelleAbrev"), get(o, "libelle"))

    deputes = []
    for n in acteurs_f:
        a = json.loads(zf.read(n).decode("utf-8")).get("acteur", {})
        civ = txt(get(a, "etatCivil", "ident", "civ"))
        nais = txt(get(a, "etatCivil", "infoNaissance", "dateNais"))
        prof = txt(get(a, "profession", "libelleCourant"))
        cat = txt(get(a, "profession", "socProcINSEE", "catSocPro"))
        fam = txt(get(a, "profession", "socProcINSEE", "famSocPro"))
        nom = txt(get(a, "etatCivil", "ident", "nom"))
        groupe = None
        mandats = get(a, "mandats", "mandat") or []
        if isinstance(mandats, dict):
            mandats = [mandats]
        for m in mandats:
            if get(m, "typeOrgane") == "GP" and get(m, "dateFin") is None:
                ref = get(m, "organes", "organeRef")
                if ref in organes:
                    groupe = organes[ref][1] or organes[ref][2]
        deputes.append({
            "nom": nom, "civ": civ, "nais": nais,
            "prof": prof, "cat": cat, "fam": fam, "groupe": groupe,
        })

    n = len(deputes)
    print(f"\n{n} deputes charges. Couverture des champs :")
    for champ, label in [("nom", "nom (pour IDP)"), ("civ", "sexe (civilite)"),
                         ("nais", "date de naissance"), ("prof", "profession declaree"),
                         ("cat", "categorie INSEE (catSocPro)"), ("fam", "famille INSEE (famSocPro)"),
                         ("groupe", "groupe politique actif")]:
        ok = sum(1 for d in deputes if d[champ])
        print(f"   {label:32} {ok}/{n} ({ok / n:.0%})")

    print("\nGroupes politiques (mandat GP actif) :")
    for g, c in Counter(d["groupe"] or "SANS" for d in deputes).most_common():
        print(f"   {g:12} {c}")

    print("\nFamilles socioprofessionnelles (famSocPro), ensemble :")
    for f, c in Counter(d["fam"] or "Non renseigne" for d in deputes).most_common():
        print(f"   {c:4}  {f}")

    femmes = sum(1 for d in deputes if d["civ"] == "Mme")
    annee = date.today().year
    ages = [annee - int(d["nais"][:4]) for d in deputes if d["nais"]]
    print(f"\nFemmes : {femmes}/{n} ({femmes / n:.0%})  ·  age moyen : {sum(ages) / len(ages):.0f} ans")

    print("\nEchantillon de professions declarees (le champ semi-libre a recoder) :")
    for d in deputes[:8]:
        print(f"   {str(d['prof']):45.45} | cat: {str(d['cat']):40.40}")


if __name__ == "__main__":
    main()
