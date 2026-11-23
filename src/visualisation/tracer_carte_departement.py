import geopandas as gpd


def tracer_carte_departement(departement, stations, colonne, titre, ax, cmap="Blues"):
    """Carte d'un département avec ses stations colorées selon une colonne (par défaut foncé = élevé).

    departement : GeoDataFrame réduit au département voulu.
    stations : DataFrame avec longitude, latitude (EPSG:4326) et la colonne à représenter.
    Les stations sans valeur pour cette colonne ne sont pas affichées.
    """
    stations = stations.dropna(subset=[colonne])
    points = gpd.GeoDataFrame(
        stations,
        geometry=gpd.points_from_xy(stations["longitude"], stations["latitude"]),
        crs="EPSG:4326",
    ).to_crs(departement.crs)
    departement.plot(ax=ax, color="#f5f5f5", edgecolor="#999999")
    points.plot(
        column=colonne, cmap=cmap, legend=True, ax=ax,
        markersize=25, edgecolor="#555555", linewidth=0.3,
        legend_kwds={"shrink": 0.6},
    )
    ax.set_title(titre)
    ax.set_axis_off()
