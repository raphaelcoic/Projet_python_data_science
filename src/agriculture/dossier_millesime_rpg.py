from __future__ import annotations

from pathlib import Path

from src.agriculture.constantes_rpg import DOSSIER_RPG


def dossier_millesime_rpg(dossier_racine: str | Path = DOSSIER_RPG, annee: int = 2025) -> Path:
    """
    Retourne le chemin du sous-dossier `rpg20XX` correspondant au millésime `annee`.
    Si `dossier_racine` pointe déjà vers `.../rpg20XX`, il est retourné tel quel.
    """
    p = Path(dossier_racine)
    nom_attendu = f"rpg{annee}"
    if p.name.lower() == nom_attendu.lower():
        return p
    return p / nom_attendu
