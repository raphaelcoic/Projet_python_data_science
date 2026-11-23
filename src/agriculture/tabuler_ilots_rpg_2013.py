import numpy as np
import pandas as pd
import pyogrio
import shapely

from src.agriculture.constantes_rpg import CATEGORIES_CULTURE, GROUPE_VERS_CATEGORIE
from src.geo.rattacher_departements import rattacher_departements

COLONNES = ["code_dep", "nom_dep", "surface_ha", "code_groupe", "categorie_culture"]


def tabuler_ilots_rpg_2013(chemins, departements):
    """Une ligne par îlot du RPG 2013, avec son département, sans les contours.

    chemins : fichiers d'îlots renvoyés par recuperer_rpg_2013_ign.
    departements : GeoDataFrame renvoyé par recuperer_departements (avec_corse=True pour garder la Corse).
    Le département est celui où se trouve l'îlot : la colonne DEP_RATTAC de l'IGN donne
    celui de l'exploitation, qui peut être ailleurs.
    Les archives de l'IGN répètent certains îlots (même contour sous un autre numéro, ou dans deux
    régions ; la Corrèze est en double dans celle de Nouvelle-Aquitaine) : on n'en garde qu'un.
    code_groupe est le groupe de cultures majoritaire de l'îlot (vide s'il n'est pas renseigné) ;
    categorie_culture vaut TA, PP ou CP d'après ce groupe, et reste vide pour le groupe 28 (divers).
    Renvoie un DataFrame avec code_dep, nom_dep, surface_ha, code_groupe et categorie_culture.
    """
    paquets = []
    deja_vus = np.array([], dtype="uint64")
    for chemin in chemins:
        ilots = pyogrio.read_dataframe(chemin, columns=["SURF_GRAPH", "CODE_CULTU"], use_arrow=True)
        contour = pd.util.hash_array(shapely.to_wkb(ilots.geometry.values))
        doublon = pd.Series(contour).duplicated().to_numpy() | np.isin(contour, deja_vus)
        deja_vus = np.concatenate([deja_vus, contour[~doublon]])
        ilots = ilots[~doublon].set_crs("EPSG:2154", allow_override=True)
        paquets.append(rattacher_departements(ilots, departements))
    ilots = pd.concat(paquets, ignore_index=True)

    ilots["surface_ha"] = pd.to_numeric(ilots["SURF_GRAPH"], errors="coerce")  # 6 îlots ont "NR" : vides
    groupe = ilots["CODE_CULTU"].str.lstrip("0")  # "01" -> "1", comme en 2023
    ilots["code_groupe"] = groupe.where(groupe != "NR")
    categorie = ilots["code_groupe"].map(GROUPE_VERS_CATEGORIE)
    ilots["categorie_culture"] = categorie.where(categorie.isin(list(CATEGORIES_CULTURE)))
    return ilots[COLONNES]
