import geopandas as gpd


def rattacher_stations_zones_hydro(stations, zones_hydro):
    """Associe chaque station à sa zone hydrographique.

    stations : DataFrame avec code_station, longitude et latitude.
    zones_hydro : GeoDataFrame renvoyé par recuperer_zones_hydro.
    Une station juste hors des limites (côte, frontière) va dans la zone la plus proche.
    Renvoie un DataFrame avec code_station et code_zone, une ligne par station.
    """
    points = gpd.GeoDataFrame(
        stations[["code_station"]],
        geometry=gpd.points_from_xy(stations["longitude"], stations["latitude"]),
        crs="EPSG:4326",
    ).to_crs(zones_hydro.crs)
    rattachees = points.sjoin_nearest(zones_hydro[["code_zone", "geometry"]])
    return rattachees[["code_station", "code_zone"]].drop_duplicates("code_station")
