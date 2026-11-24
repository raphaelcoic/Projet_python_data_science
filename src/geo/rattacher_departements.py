import pandas as pd

DISTANCE_MAX = 1000  # mètres : rattrape les parcelles du littoral, hors des contours simplifiés


def rattacher_departements(parcelles, departements):
    """Donne à chaque parcelle le département où elle se trouve.

    parcelles : GeoDataFrame de polygones (parcelles ou îlots du RPG).
    departements : GeoDataFrame renvoyé par recuperer_departements.
    Chaque parcelle va au département qui contient un point de sa surface, ou au plus proche
    à moins de 1 km (les contours sont simplifiés). Les parcelles hors des départements
    fournis sont écartées.
    Renvoie un DataFrame sans géométrie, avec en plus code_dep et nom_dep.
    """
    departements = departements[["code_dep", "nom_dep", "geometry"]].to_crs(parcelles.crs)
    points = parcelles.set_geometry(parcelles.representative_point())
    dedans = points.sjoin(departements, predicate="within")
    # la recherche du plus proche est lente : seulement pour les rares points hors des contours
    proches = points.drop(dedans.index).sjoin_nearest(departements, max_distance=DISTANCE_MAX)
    points = pd.concat([dedans, proches]).sort_index()
    points = points[~points.index.duplicated()]  # point sur une frontière : un seul département
    return pd.DataFrame(points.drop(columns=["geometry", "index_right"]))
