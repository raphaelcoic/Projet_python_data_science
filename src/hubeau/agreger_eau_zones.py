def agreger_eau_zones(indices, stations_zones):
    """Agrège les indices biologiques nettoyés à la zone hydrographique : une ligne par zone suivie.

    indices : DataFrame renvoyé par nettoyer_indices.
    stations_zones : DataFrame renvoyé par rattacher_stations_zones.
    Pour chaque indice, on prend la médiane de chaque station sur 2013-2023 puis la médiane
    des stations de la zone, pour qu'une station très suivie ne pèse pas plus que les autres.
    Renvoie un DataFrame avec code_zone, I2M2, IBD, IPR et nb_stations.
    """
    par_station = indices.groupby(["code_station", "indice"], as_index=False)["valeur"].median()
    par_station = par_station.merge(stations_zones, on="code_station")
    eau = par_station.pivot_table(index="code_zone", columns="indice", values="valeur", aggfunc="median")
    eau["nb_stations"] = par_station.groupby("code_zone")["code_station"].nunique()
    return eau.rename_axis(columns=None).reset_index()
