import pandas as pd

from src.agriculture.constantes_rpg import CATEGORIES_CULTURE, CULTURE_VERS_CATEGORIE, LIBELLES_GROUPES_RPG
from src.agriculture.lire_parcelles_rpg import lire_parcelles_rpg
from src.geo.rattacher_departements import rattacher_departements

COLONNES = [
    "id_parcelle", "code_dep", "nom_dep", "surface_ha", "code_culture",
    "code_groupe", "libelle_groupe", "categorie_culture",
]


def tabuler_parcelles_rpg(chemin_rpg, departements):
    """Une ligne par parcelle du RPG 2023, avec son département, sans les contours.

    chemin_rpg : GeoPackage des parcelles renvoyé par recuperer_rpg_ign.
    departements : GeoDataFrame renvoyé par recuperer_departements (avec_corse=True pour garder la Corse).
    categorie_culture vaut TA, PP, CP ou SB d'après le code culture, et reste vide pour les
    surfaces non agricoles ou non classées.
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
    parcelles["libelle_groupe"] = parcelles["code_groupe"].map(LIBELLES_GROUPES_RPG)
    categorie = parcelles["code_culture"].map(CULTURE_VERS_CATEGORIE)
    parcelles["categorie_culture"] = categorie.where(categorie.isin(list(CATEGORIES_CULTURE)))
    return parcelles[COLONNES]
