import geopandas as gpd


def tracer_stations(stations, departements, ax):
    """Carte des stations (un point par station) sur les contours des départements.

    stations : DataFrame avec longitude et latitude (EPSG:4326).
    departements : GeoDataFrame des départements, dans le système de projection voulu.
    """
    points = gpd.GeoDataFrame(
        stations,
        geometry=gpd.points_from_xy(stations["longitude"], stations["latitude"]),
        crs="EPSG:4326",
    ).to_crs(departements.crs)
    departements.boundary.plot(ax=ax, color="#999999", linewidth=0.3)
    points.plot(ax=ax, markersize=0.3, color="#2a78d6")
    ax.set_axis_off()
