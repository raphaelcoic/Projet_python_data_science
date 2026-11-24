import pandas as pd

from src.agriculture.lire_parcelles_rpg import lire_parcelles_rpg


def _associer_paquet(parcelles, zones):
    """Zones touchées par chaque parcelle d'un paquet, avec la part de la parcelle dans chacune."""
    paires = parcelles.sjoin(zones[["code_zone", "geometry"]], predicate="intersects")
    paires["part"] = 1.0
    coupees = paires.index.duplicated(keep=False)
    contours = paires.geometry[coupees].make_valid()
    morceaux = contours.intersection(zones.geometry.loc[paires.loc[coupees, "index_right"]], align=False)
    paires.loc[coupees, "part"] = morceaux.area
    paires = paires[paires["part"] > 0]
    # parts ramenées à 1 par parcelle : rien n'est perdu quand une parcelle déborde des zones
    paires["part"] /= paires.groupby(level=0)["part"].transform("sum")
    return pd.DataFrame({"id_parcelle": paires["ID_PARCEL"], "code_zone": paires["code_zone"], "part": paires["part"]})


def associer_parcelles_zones(chemin_rpg, zones):
    """Associe chaque parcelle du RPG 2023 à la ou aux zones hydrographiques qu'elle touche.

    chemin_rpg : GeoPackage des parcelles renvoyé par recuperer_rpg_ign.
    zones : GeoDataFrame renvoyé par recuperer_zones_hydro (sans la Corse).
    Une parcelle qui touche une seule zone y va entière (part = 1). Une parcelle qui en touche
    plusieurs est coupée par leurs limites : part = aire du morceau dans la zone / aire de la
    parcelle, les parts d'une parcelle font 1. Les parcelles hors des zones sont écartées.
    Renvoie un DataFrame : id_parcelle, code_zone, part (une ligne par parcelle et par zone).
    """
    paquets = [_associer_paquet(parcelles.to_crs(zones.crs), zones) for parcelles in lire_parcelles_rpg(chemin_rpg, ["ID_PARCEL"])]
    return pd.concat(paquets, ignore_index=True)
