def fusionner_eau_cultures_pesticides(eau_zones, champs_zones, pesticides_zones, zones):
    """Croise les indices biologiques, les cultures et les pesticides : une ligne par zone hydrographique suivie et par année.

    eau_zones : DataFrame renvoyé par agreger_eau_zones.
    champs_zones : DataFrame renvoyé par agreger_champs_zones.
    pesticides_zones : DataFrame renvoyé par agreger_pesticides_zones.
    zones : GeoDataFrame renvoyé par recuperer_zones_hydro.
    Renvoie un DataFrame avec les colonnes de base_zones.parquet.
    """
    surfaces = champs_zones.pivot_table(
        index="code_zone", columns="code_groupe_culture", values="surface_ha", aggfunc="sum", fill_value=0,
    ).add_prefix("surface_groupe_")
    surfaces.insert(0, "surface_agricole", surfaces.sum(axis=1))

    base = eau_zones.merge(zones[["code_zone", "nom_zone", "surface_zone_ha"]], on="code_zone")
    base = base.merge(surfaces.reset_index(), on="code_zone", how="left")
    # une zone suivie sans parcelle n'a vraiment aucune culture (le RPG couvre tout le territoire)
    colonnes = list(surfaces.columns)
    base[colonnes] = base[colonnes].fillna(0)
    parts = base[colonnes].div(base["surface_zone_ha"], axis=0) * 100
    parts.columns = [c.replace("surface_", "part_") for c in colonnes]
    base = base.drop(columns=colonnes).join(parts)

    # pesticides de la zone l'année de l'indice, en kg par hectare de zone ; une zone suivie sans parcelle n'en reçoit pas
    kg = [c for c in pesticides_zones.columns if c.endswith("_kg")]
    base = base.merge(pesticides_zones, on=["code_zone", "annee"], how="left")
    base[kg] = base[kg].fillna(0).div(base["surface_zone_ha"], axis=0)
    return base.rename(columns={c: f"{c}_ha" for c in kg})
