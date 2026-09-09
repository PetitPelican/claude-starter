#!/usr/bin/env python3
"""L'INSTRUMENT QUI MANQUAIT À LA MÉMOIRE : noter ce qui a SERVI.

54 notes, aucune trace de celles qui ont déjà servi. Impossible donc de
distinguer une note vivante d'une note morte : l'index grossit, tout se vaut, et
rien ne remonte au bon moment. C'est le même trou que le harnais avait sur ses
propres blocages jusqu'au 09/09/2026 — **un mécanisme sans trace ne peut pas
être jugé**, et une mémoire dont on ignore l'usage ne peut pas être entretenue.

Repris à Hermes (`agent/curator.py`), qui fait vieillir ses compétences sur leur
dernier usage. Sa mécanique est bonne ; il lui fallait, chez nous, la mesure.

CE HOOK NE DÉCIDE RIEN. Il écrit une ligne quand une note de mémoire est lue.
Le vieillissement, l'archivage et le rangement sont le travail de
`claude-memoire`, qui tourne à part et rend un rapport.

POURQUOI SUR `Read` ET PAS SUR UNE DÉCLARATION DE L'AGENT. Une étiquette que
l'agent pose lui-même ne se pose jamais : `échoué` existe depuis le début du
carnet d'équipe et ZÉRO des vingt entrées la porte. Le déclencheur juste est
celui que l'agent produit sans y penser — ici, ouvrir le fichier.

BUDGET. Ce hook tourne après CHAQUE lecture de fichier. Il doit donc sortir en
quelques millisecondes quand le chemin ne le concerne pas — c'est-à-dire
presque toujours. D'où la forme : un test de sous-chaîne, puis `sys.exit(0)`.
Aucun import lourd, aucune I/O avant le test.
"""
import sys, os, json, pathlib, datetime

# Le dossier de mémoire auto, quel que soit le projet. La clé est le CHEMIN
# slugifié du projet : `~/.claude/projects/<slug>/memory/`.
MARQUE = "/.claude/projects/"
SOUS = "/memory/"


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return                                   # fail-open, toujours

    chemin = ""
    for source in (data.get("tool_input") or {}, data.get("tool_response") or {}):
        if isinstance(source, dict):
            chemin = str(source.get("file_path") or source.get("filePath") or "") or chemin

    if not chemin or MARQUE not in chemin or SOUS not in chemin:
        return                                   # le cas de très loin le plus fréquent
    if not chemin.endswith(".md"):
        return

    p = pathlib.Path(chemin)
    nom = p.stem
    # MEMORY.md est l'index, pas une note : le lire ne prouve rien sur les notes.
    if nom.upper() == "MEMORY":
        return

    etat = p.parent / ".usage.json"
    try:
        d = json.loads(etat.read_text()) if etat.exists() else {}
    except Exception:
        d = {}
    e = d.get(nom) or {}
    e["vu"] = datetime.date.today().isoformat()
    e["n"] = int(e.get("n", 0)) + 1
    d[nom] = e
    try:
        # Écriture atomique : ce fichier est lu par `claude-memoire` pendant que
        # des agents écrivent dedans. Un fichier tronqué se lirait comme une
        # mémoire jamais servie, et ferait archiver ce qui vient de servir.
        tmp = etat.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(d, ensure_ascii=False, indent=1, sort_keys=True))
        os.replace(tmp, etat)
    except Exception:
        pass


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
