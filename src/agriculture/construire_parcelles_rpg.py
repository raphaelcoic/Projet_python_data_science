import pandas as pd

from src.agriculture.ajouter_libelles_rpg import ajouter_libelles_rpg
from src.agriculture.lire_parcelles_rpg import lire_parcelles_rpg
from src.agriculture.nettoyer_parcelles_rpg import nettoyer_parcelles_rpg
from src.geo.rattacher_departements import rattacher_departements

COLONNES = [
    "id_parcelle", "code_dep", "nom_dep", "surface_ha", "code_culture",
    "code_groupe", "libelle_groupe", "categorie_culture",
]


def construire_parcelles_rpg(chemin_rpg, departements):
    """Construit parcelles_rpg_2023.parquet : une ligne par parcelle du RPG 2023, sans les contours.

    chemin_rpg : GeoPackage des parcelles renvoyé par recuperer_rpg_ign.
    departements : GeoDataFrame renvoyé par recuperer_departements (94 départements, sans la Corse).
    Lit les parcelles par paquets, donne à chacune son département (celles de Corse sont
    écartées), puis nettoie la table et ajoute les libellés.
    Renvoie un DataFrame avec les colonnes de COLONNES.
    """
    paquets = [
        rattacher_departements(parcelles, departements)
        for parcelles in lire_parcelles_rpg(chemin_rpg, ["ID_PARCEL", "CODE_CULTU", "CODE_GROUP", "SURF_PARC"])
    ]
    parcelles = pd.concat(paquets, ignore_index=True).rename(columns={
        "ID_PARCEL": "id_parcelle", "SURF_PARC": "surface_ha",
        "CODE_CULTU": "code_culture", "CODE_GROUP": "code_groupe",
    })
    return ajouter_libelles_rpg(nettoyer_parcelles_rpg(parcelles))[COLONNES]
