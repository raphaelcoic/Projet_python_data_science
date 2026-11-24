from src.eau.agreger_eau_zones import agreger_eau_zones
from src.eau.nettoyer_indices import nettoyer_indices
from src.eau.rattacher_stations_zones import rattacher_stations_zones
from src.eau.recuperer_tous_indices import recuperer_tous_indices
from src.eau.recuperer_toutes_stations_hydrobio import recuperer_toutes_stations_hydrobio


def construire_eau_zones(zones):
    """Construit eau_zones.parquet depuis l'API Hub'Eau (plusieurs minutes).

    zones : GeoDataFrame renvoyé par recuperer_zones_hydro.
    Télécharge les stations et les indices, nettoie les indices, rattache chaque station
    suivie à sa zone, puis agrège les indices à la zone et à l'année.
    Renvoie le DataFrame de agreger_eau_zones.
    """
    stations = recuperer_toutes_stations_hydrobio()
    indices = nettoyer_indices(recuperer_tous_indices())
    stations_suivies = stations[stations["code_station"].isin(indices["code_station"])]
    return agreger_eau_zones(indices, rattacher_stations_zones(stations_suivies, zones))
