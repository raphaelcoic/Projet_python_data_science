import pandas as pd

from src.agriculture.constantes_rpg import LIBELLES_GROUPES_RPG
from src.agriculture.lire_parcelles_rpg import lire_parcelles_rpg

CLE = ["code_dep", "code_groupe_culture", "libelle_groupe_culture"]
DISTANCE_MAX = 1000  # mètres : rattrape les parcelles du littoral, hors des contours simplifiés


def agreger_champs(chemin_rpg, departements):
    """Agrège les parcelles du RPG au département × groupe de cultures (surfaces en hectares).

    chemin_rpg : GeoPackage des parcelles renvoyé par recuperer_rpg_ign.
    departements : GeoDataFrame renvoyé par recuperer_departements.
    Chaque parcelle va au département qui contient un point de sa surface, ou au plus proche
    à moins de 1 km (les contours sont simplifiés). Les parcelles de Corse, hors périmètre,
    ne sont rattachées à aucun département et sont écartées.
    Renvoie un DataFrame avec les colonnes de champs.parquet.
    """
    departements = departements[["code_dep", "geometry"]].to_crs("EPSG:2154")
    paquets = []
    for parcelles in lire_parcelles_rpg(chemin_rpg):
        points = parcelles.set_geometry(parcelles.representative_point())
        points = points.sjoin_nearest(departements, max_distance=DISTANCE_MAX)
        points = points[~points.index.duplicated()]  # point sur une frontière : un seul département
        paquets.append(points.groupby(["code_dep", "CODE_GROUP"])["SURF_PARC"].sum())

    surfaces = pd.concat(paquets).groupby(level=[0, 1]).sum().reset_index()
    surfaces.columns = ["code_dep", "code_groupe_culture", "surface_ha"]
    surfaces["libelle_groupe_culture"] = surfaces["code_groupe_culture"].map(LIBELLES_GROUPES_RPG)
    return surfaces[[*CLE, "surface_ha"]]
