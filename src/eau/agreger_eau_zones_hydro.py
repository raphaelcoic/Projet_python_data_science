def agreger_eau_zones_hydro(indices, stations_zones_hydro):
    """Agrège les indices biologiques nettoyés à la zone hydrographique : une ligne par zone suivie et par année.

    indices : DataFrame renvoyé par nettoyer_indices.
    stations_zones_hydro : DataFrame renvoyé par rattacher_stations_zones_hydro.
    Pour chaque indice, on fait la moyenne des mesures de chaque station dans l'année, puis la médiane
    des stations de la zone (moins sensible que la moyenne aux valeurs extrêmes de l'IPR).
    Renvoie un DataFrame avec code_zone, annee, I2M2, IBD, IPR et nb_stations.
    """
    par_station = indices.groupby(["code_station", "annee", "indice"], as_index=False)["valeur"].mean()
    par_station = par_station.merge(stations_zones_hydro, on="code_station")
    eau = par_station.pivot_table(index=["code_zone", "annee"], columns="indice", values="valeur", aggfunc="median")
    eau["nb_stations"] = par_station.groupby(["code_zone", "annee"])["code_station"].nunique()
    return eau.rename_axis(columns=None).reset_index()
