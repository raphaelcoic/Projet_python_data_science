"""
Module d'acquisition, d'harmonisation et de sélection des variables du RPG
(Registre Parcellaire Graphique) via l'API WFS de la Géoplateforme IGN.
"""

from .fusionner_parcelles_rpg import (
    COLONNES_TABULAIRES_RPG,
    DEPARTEMENTS_EXCLUS_DEFAUT,
    fusionner_millesime_rpg,
    fusionner_tous_millesimes_rpg,
)
from .get_parcelles_rpg import COLONNES_PROJET_RPG, get_parcelles_rpg

__all__ = [
    "COLONNES_PROJET_RPG",
    "COLONNES_TABULAIRES_RPG",
    "DEPARTEMENTS_EXCLUS_DEFAUT",
    "fusionner_millesime_rpg",
    "fusionner_tous_millesimes_rpg",
    "get_parcelles_rpg",
]
