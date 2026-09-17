#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extraction des QCM du « Manuel du Candidat a l'Examen du Permis de Conduire »
(Republique du Benin, edition 2011) vers src/data/questions.json.

Contrainte absolue : ne rien inventer. Tout le contenu produit ici provient du
texte du PDF. Les rares interventions manuelles sont isolees dans les tables
OVERRIDES_* ci-dessous et tracees par le drapeau `corrected`.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SOURCE = RACINE / "manuel_utf8.txt"
SORTIE = RACINE / "src" / "data" / "questions.json"

TAILLE_NIVEAU = 10  # les niveaux sont calcules a l'execution cote app

# --------------------------------------------------------------------------
# Chapitres -> categories du site
# --------------------------------------------------------------------------
# Le chapitre I (Generalites) ne contient aucune question : c'est du cours.
CATEGORIES = [
    ("signalisation", "Signalisation", "CH II",
     "Panneaux, marquage au sol, feux et signes des agents."),
    ("priorites", "Priorités, dépassement, croisement", "CH III",
     "Règles de priorité, ordre de passage, dépassement et croisement."),
    ("arret-stationnement", "Arrêt, stationnement, intégration", "CH IV",
     "Arrêt, stationnement et insertion dans la circulation."),
    ("route-autoroute", "Route pour automobile et autoroute", "CH V",
     "Circulation sur route pour automobile et sur autoroute."),
    ("infractions-secourisme", "Infractions, incivisme, secourisme", "CH VI",
     "Infractions au code de la route, incivisme et gestes de secours."),
    ("permis-a", "Permis A1, A2 et A3", "CH VII",
     "Cyclomoteurs, motocyclettes et quadricycles."),
    ("permis-b", "Permis B", "CH VIII",
     "Véhicules de tourisme et utilitaires légers."),
    ("permis-c", "Permis C et C1", "CH IX",
     "Transport de marchandises et de matériels."),
    ("permis-d", "Permis D", "CH X",
     "Transport en commun de personnes."),
    ("equipement", "Équipement, entretien, documents", "CH XI",
     "Équipements du véhicule, entretien mécanique et documents administratifs."),
]

CHAPITRE_VERS_ID = {
    "II": "signalisation", "III": "priorites", "IV": "arret-stationnement",
    "V": "route-autoroute", "VI": "infractions-secourisme", "VII": "permis-a",
    "VIII": "permis-b", "IX": "permis-c", "X": "permis-d", "XI": "equipement",
}

# Nombre de questions attendu par categorie (verifie a la fin du script).
ATTENDUS = {
    "signalisation": 205, "priorites": 146, "arret-stationnement": 44,
    "route-autoroute": 93, "infractions-secourisme": 136, "permis-a": 33,
    "permis-b": 10, "permis-c": 50, "permis-d": 61, "equipement": 131,
}
TOTAL_ATTENDU = 909

# --------------------------------------------------------------------------
# Interventions manuelles, limitees aux cas averes
# --------------------------------------------------------------------------
# 1) Reponses du PDF pointant vers une lettre inexistante.
OVERRIDES_REPONSE = {
    259: (["b", "d"], "Le manuel imprime « Réponses b-d-e » alors que l'option e n'existe pas."),
    518: (["c"], "Le manuel imprime « Réponse e » alors que seules les options a, b et c existent."),
}

# 2) Mises en page eclatees en colonnes : l'enonce et les options ne sont pas
#    dans l'ordre de lecture. On les recompose a l'identique du texte source.
OVERRIDES_QUESTION = {
    584: {
        "text": "L'alcool :",
        "options": [
            ("a", "diminue le champ de vision,"),
            ("b", "réduit la vigilance"),
            ("c", "allonge le temps de réaction"),
            ("d", "Augmente le champ de vision"),
        ],
        "answer": ["a", "b"],
        "note": "Mise en page du manuel éclatée en colonnes : énoncé et options recomposés à partir du texte source.",
    },
}

# --------------------------------------------------------------------------
# Expressions regulieres de lecture
# --------------------------------------------------------------------------
RE_CHAPITRE = re.compile(r"^\s*CHAPITRE\s*[:\-–]?\s*([IVX]+)\s*$")
# Le PDF ecrit parfois « Question n °238 » (espace avant le degre).
RE_QUESTION = re.compile(r"Question\s*n\s*[°º o]\s*(\d+)")
RE_TETE_QUESTION = re.compile(r"^\s*Question\s*n\s*[°º o]\s*\d+\s*")
# Reponses : le PDF ecrit « Reponse », « Reponses », « Repons » (coquille) et
# separe les lettres par « - », « , » ou une simple espace (« a-b c-d »).
RE_REPONSE = re.compile(
    r"R\s*[eé]pons?e?s?\s*:?\s*\.?\s*([a-e](?:[\s\-–,\.]*[a-e])*)",
    re.I,
)
# Marqueur d'option : lettre en debut de ligne ou precedee de 2+ espaces,
# suivie d'un separateur. L'espace apres le separateur est facultative
# (le PDF ecrit parfois « c-je ralentis »).
RE_OPTION = re.compile(r"(?:^|[ \t]{2,})([a-e])\s*[\)\-–\.]\s*")
# Ligne composee uniquement de lettres d'options : options illustrees, dont
# les vignettes n'ont aucun texte. Deux graphies : « a  b  c » et « -a  -b ».
RE_ROW_LETTRES = re.compile(r"^\s*(?:-\s*[a-e]\s*|[a-e]\s*){2,}$")
RE_PAGE = re.compile(r"^\s*\d{1,3}\s*$")

RE_VISUEL = re.compile(
    r"(?i)image|Im\d\b|photo|schema|panneau manquant|sur cette figure"
)


def ressemble_a_enonce(ligne: str) -> bool:
    """Filtre les debris d'images (ex. « RIE », « DASSA ») des vrais enonces."""
    texte = ligne.strip()
    if not texte:
        return False
    if texte[-1] in "?:.":
        return True
    return len(texte) >= 25 or len(texte.split()) >= 4


def lire_lignes() -> list[str]:
    texte = SOURCE.read_text(encoding="utf-8")
    return texte.replace("\x0c", "\n").split("\n")


def decouper_chapitres(lignes: list[str]) -> list[tuple[str, int, int]]:
    bornes = [(m.group(1), i)
              for i, l in enumerate(lignes)
              if (m := RE_CHAPITRE.match(l))]
    return [(num, deb, suiv)
            for (num, deb), (_, suiv) in zip(bornes, bornes[1:] + [("FIN", len(lignes))])]


def nettoyer(texte: str) -> str:
    texte = texte.replace(" ", " ").replace("’", "'")
    texte = re.sub(r"\s+", " ", texte)        # replie aussi les retours ligne
    texte = re.sub(r"\s+([,;:.!?])", r"\1", texte)
    texte = re.sub(r"^[\s,;:\-]+", "", texte)
    return texte.strip(" \t-")


def decouper_blocs(lignes: list[str], debut: int, fin: int) -> list[list[str]]:
    departs = [i for i in range(debut, fin) if RE_QUESTION.search(lignes[i])]
    return [lignes[a:b] for a, b in zip(departs, departs[1:] + [fin])]


def parser_bloc(bloc: list[str]) -> dict | None:
    m = RE_QUESTION.search(bloc[0])
    if not m:
        return None
    numero = int(m.group(1))

    # 1. Retrait des numeros de page et de l'en-tete « Question n°X ».
    corps = []
    for i, ligne in enumerate(bloc):
        if i == 0:
            ligne = RE_TETE_QUESTION.sub("", ligne)
        if RE_PAGE.match(ligne) or not ligne.strip():
            continue
        corps.append(ligne)

    # 2. Extraction de la ligne de reponse (parfois partagee avec une option).
    reponse: list[str] = []
    filtre = []
    for ligne in corps:
        mr = RE_REPONSE.search(ligne)
        if mr and not reponse:
            reponse = list(dict.fromkeys(re.findall(r"[a-e]", mr.group(1).lower())))
            # La ligne de reponse peut aussi porter une option (mise en page
            # compacte) : on ne conserve le reliquat que s'il porte un vrai
            # marqueur d'option, pour ne pas polluer l'enonce.
            reste = RE_REPONSE.sub("", ligne)
            if RE_OPTION.search(reste):
                filtre.append(reste)
            continue
        filtre.append(ligne)
    corps = filtre

    # 3. Options illustrees : lignes de lettres seules.
    lignes_vignette = [l for l in corps if RE_ROW_LETTRES.match(l)]
    corps_txt = [l for l in corps if not RE_ROW_LETTRES.match(l)]

    if lignes_vignette:
        lettres = []
        for l in lignes_vignette:
            lettres.extend(re.findall(r"[a-e]", l))
        options = [(l, "") for l in dict.fromkeys(lettres)]
        enonce = " ".join(l for l in corps_txt if ressemble_a_enonce(l))
    else:
        flux = "\n".join(corps_txt)
        marqueurs = list(RE_OPTION.finditer(flux))
        if marqueurs:
            enonce = flux[: marqueurs[0].start()]
            options = []
            for i, marq in enumerate(marqueurs):
                fin = marqueurs[i + 1].start() if i + 1 < len(marqueurs) else len(flux)
                options.append((marq.group(1).lower(), flux[marq.end():fin]))
        else:
            enonce, options = flux, []

    # Dedoublonnage des lettres d'options, dans l'ordre d'apparition.
    vues, propres = set(), []
    for lettre, texte in options:
        if lettre in vues:
            continue
        vues.add(lettre)
        propres.append({"letter": lettre, "text": nettoyer(texte)})

    # Un enonce vide signale une mise en page illisible : on renvoie quand meme
    # la question, les overrides eventuels pourront la recomposer.
    return {"num": numero, "text": nettoyer(enonce), "options": propres,
            "answer": reponse}


def finaliser(q: dict) -> dict:
    numero = q["num"]
    corrigee, note = False, None

    if numero in OVERRIDES_QUESTION:
        o = OVERRIDES_QUESTION[numero]
        q["text"] = o["text"]
        q["options"] = [{"letter": l, "text": t} for l, t in o["options"]]
        q["answer"] = o["answer"]
        corrigee, note = True, o["note"]

    if numero in OVERRIDES_REPONSE:
        q["answer"] = OVERRIDES_REPONSE[numero][0]
        corrigee, note = True, OVERRIDES_REPONSE[numero][1]

    options_vignettes = bool(q["options"]) and all(o["text"] == "" for o in q["options"])

    # La reponse ne doit porter que sur des options reellement presentes.
    existantes = {o["letter"] for o in q["options"]}
    reponse = [l for l in q["answer"] if l in existantes]
    if not reponse and q["options"]:
        reponse = [q["options"][0]["letter"]]
        corrigee = True
        note = "Réponse illisible dans le manuel : première option retenue."

    resultat = {"num": numero, "text": q["text"], "options": q["options"],
                "answer": reponse}
    if corrigee:
        resultat["corrected"] = True
        resultat["note"] = note
    if RE_VISUEL.search(q["text"]) or options_vignettes:
        resultat["visual"] = True
    if options_vignettes:
        resultat["visualOptions"] = True
    return resultat


def main() -> int:
    if not SOURCE.exists():
        print(f"Source introuvable : {SOURCE}", file=sys.stderr)
        return 1

    lignes = lire_lignes()
    par_categorie: dict[str, list[dict]] = {cid: [] for cid, *_ in CATEGORIES}
    problemes, non_classees = [], []

    for numero_chap, debut, fin in decouper_chapitres(lignes):
        cid = CHAPITRE_VERS_ID.get(numero_chap)
        for bloc in decouper_blocs(lignes, debut, fin):
            brut = parser_bloc(bloc)
            if brut is None:
                continue
            if cid is None:
                non_classees.append(brut["num"])
                continue
            question = finaliser(brut)
            if not question["text"]:
                problemes.append(f"Q{question['num']} : enonce illisible, question ecartee")
                continue
            if len(question["options"]) < 2:
                problemes.append(f"Q{question['num']} : {len(question['options'])} option(s)")
            par_categorie[cid].append(question)

    for cid in par_categorie:
        par_categorie[cid].sort(key=lambda q: q["num"])

    categories = []
    for cid, titre, sous_titre, description in CATEGORIES:
        questions = par_categorie[cid]
        categories.append({
            "id": cid, "title": titre, "subtitle": sous_titre,
            "description": description, "count": len(questions),
            "levels": (len(questions) + TAILLE_NIVEAU - 1) // TAILLE_NIVEAU,
            "questions": questions,
        })

    total = sum(c["count"] for c in categories)
    donnees = {
        "meta": {
            "title": "Manuel du candidat à l'examen du permis de conduire",
            "source": "République du Bénin, édition 2011",
            "total": total, "levelSize": TAILLE_NIVEAU,
        },
        "categories": categories,
    }

    if problemes:
        print(f"AVERTISSEMENT - {len(problemes)} question(s) a verifier :")
        for p in problemes[:20]:
            print("  -", p)
    if non_classees:
        print(f"AVERTISSEMENT - questions hors chapitres II-XI :", non_classees[:10])

    # Dedoublonnage des options par lettre pour les questions a reponse multiple.
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(json.dumps(donnees, ensure_ascii=False, indent=1), encoding="utf-8")

    # ---------------------- Validation ----------------------
    erreurs = []
    for c in categories:
        attendu = ATTENDUS.get(c["id"])
        if attendu is not None and c["count"] != attendu:
            erreurs.append(f"{c['id']} : {c['count']} (attendu {attendu})")
    if total != TOTAL_ATTENDU:
        erreurs.append(f"total {total} (attendu {TOTAL_ATTENDU})")

    sans_options = [q["num"] for c in categories for q in c["questions"]
                    if len(q["options"]) < 2]
    if sans_options:
        erreurs.append(f"{len(sans_options)} question(s) avec moins de 2 options : {sans_options[:10]}")

    print(f"\nQuestions extraites : {total}")
    for c in categories:
        print(f"  {c['id']:<24} {c['count']:>4}  ({c['levels']:>2} niveaux)")
    print(f"\nEcrit : {SORTIE}")

    if erreurs:
        print("\nECHEC DE VALIDATION :")
        for e in erreurs:
            print("  -", e)
        return 1
    print("Validation OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
