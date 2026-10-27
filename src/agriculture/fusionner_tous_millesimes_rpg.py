"""
Exécution directe (depuis la racine du dépôt) :
    python -m src.agriculture.fusionner_tous_millesimes_rpg
"""

from __future__ import annotations

from pathlib import Path

from src.agriculture.constantes_rpg import DEPARTEMENTS_EXCLUS_DEFAUT, DOSSIER_RPG
from src.agriculture.fusionner_millesime_rpg import fusionner_millesime_rpg


def fusionner_tous_millesimes_rpg(
    annees: list[int] | tuple[int, ...] = (2013, 2023),
    dossier_racine: str | Path = DOSSIER_RPG,
    departements_exclus: tuple[str, ...] | list[str] = DEPARTEMENTS_EXCLUS_DEFAUT,
    colonnes: list[str] | None = None,
    ecraser: bool = True,
    verbose: bool = True,
) -> dict[int, Path]:
    """
    Génère les fichiers Parquet nationaux (sans `geometry`, hors Corse et DROM)
    pour l'ensemble des millésimes spécifiés dans `annees`.
    """
    return {
        annee: fusionner_millesime_rpg(
            annee=annee,
            dossier_racine=dossier_racine,
            departements_exclus=departements_exclus,
            colonnes=colonnes,
            ecraser=ecraser,
            verbose=verbose,
        )
        for annee in annees
    }


if __name__ == "__main__":
    fusionner_tous_millesimes_rpg()
