SEUIL_SURFACE_HA = 100
SEUIL_PART_ZONE = 0.01


def choisir_parcelles_a_decouper(parcelles, zones):
    """Liste les parcelles trop grandes pour être rangées entières dans une seule zone.

    parcelles : GeoDataFrame du fichier national du RPG (id_parcelle, surface_ha, point_reference).
    zones : GeoDataFrame renvoyé par recuperer_zones_hydro.
    Une parcelle est retenue si elle fait au moins 100 ha, ou au moins 1 % de la zone
    qui contient son point.
    Renvoie la liste de leurs id_parcelle.
    """
    rattachees = parcelles.to_crs(zones.crs).sjoin(
        zones[["surface_zone_ha", "geometry"]], how="left", predicate="within"
    )
    grandes = (rattachees["surface_ha"] >= SEUIL_SURFACE_HA) | (
        rattachees["surface_ha"] >= SEUIL_PART_ZONE * rattachees["surface_zone_ha"]
    )
    return rattachees.loc[grandes, "id_parcelle"].unique().tolist()
