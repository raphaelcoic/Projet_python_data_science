def agreger_champs_zones_hydro(parcelles, parcelles_zones_hydro):
    """Surface de chaque groupe de cultures par zone hydrographique, en hectares.

    parcelles : DataFrame de parcelles_rpg_2023.parquet (id_parcelle, code_groupe, libelle_groupe, surface_ha).
    parcelles_zones_hydro : DataFrame renvoyé par associer_parcelles_zones_hydro.
    Une parcelle partagée entre plusieurs zones compte dans chacune pour sa part de surface.
    Renvoie un DataFrame : code_zone, code_groupe_culture, libelle_groupe_culture, surface_ha.
    """
    champs = parcelles_zones_hydro.merge(parcelles[["id_parcelle", "code_groupe", "libelle_groupe", "surface_ha"]], on="id_parcelle")
    champs["surface_ha"] *= champs["part"]
    champs = champs.groupby(["code_zone", "code_groupe", "libelle_groupe"], as_index=False)["surface_ha"].sum()
    return champs.rename(columns={"code_groupe": "code_groupe_culture", "libelle_groupe": "libelle_groupe_culture"})
