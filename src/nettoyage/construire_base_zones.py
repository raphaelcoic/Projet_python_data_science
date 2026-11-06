def construire_base_zones(indices, stations_zones, champs_zones, zones):
    """Croise les indices biologiques et les cultures : une ligne par zone hydrographique suivie.

    indices : DataFrame renvoyé par nettoyer_indices.
    stations_zones : DataFrame renvoyé par rattacher_stations_zones.
    champs_zones : DataFrame renvoyé par agreger_champs_zones.
    zones : GeoDataFrame renvoyé par recuperer_zones_hydro.
    Pour chaque indice, on prend la médiane de chaque station puis la médiane des stations
    de la zone, pour qu'une station très suivie ne pèse pas plus que les autres.
    Renvoie un DataFrame avec les colonnes de base_zones.parquet.
    """
    par_station = indices.groupby(["code_station", "indice"], as_index=False)["valeur"].median()
    par_station = par_station.merge(stations_zones, on="code_station")
    eau = par_station.pivot_table(index="code_zone", columns="indice", values="valeur", aggfunc="median")
    eau["nb_stations"] = par_station.groupby("code_zone")["code_station"].nunique()

    surfaces = champs_zones.pivot_table(
        index="code_zone", columns="code_groupe_culture", values="surface_ha", aggfunc="sum", fill_value=0,
    ).add_prefix("surface_groupe_")
    surfaces.insert(0, "surface_agricole", surfaces.sum(axis=1))

    base = eau.reset_index().merge(zones[["code_zone", "nom_zone", "surface_zone_ha"]], on="code_zone")
    base = base.merge(surfaces.reset_index(), on="code_zone", how="left")
    # une zone suivie sans parcelle n'a vraiment aucune culture (le RPG couvre tout le territoire)
    colonnes = list(surfaces.columns)
    base[colonnes] = base[colonnes].fillna(0)
    parts = base[colonnes].div(base["surface_zone_ha"], axis=0) * 100
    parts.columns = [c.replace("surface_", "part_") for c in colonnes]
    return base.drop(columns=colonnes).join(parts)
