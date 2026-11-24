import pyogrio


def extraire_contours_departement(chemin_rpg, parcelles, departements, code_dep):
    """Contours des parcelles d'un département, lus dans l'archive du RPG 2023 de l'IGN.

    chemin_rpg : GeoPackage des parcelles renvoyé par recuperer_rpg_ign.
    parcelles : DataFrame de parcelles_rpg_2023.parquet (id_parcelle, code_dep).
    departements : GeoDataFrame renvoyé par recuperer_departements.
    code_dep : code du département en texte ("91").
    Sert à la démonstration de main.ipynb (partie 3.1) : associer_parcelles_zones_hydro
    tourne sur ce seul département en quelques secondes, sans l'archive.
    Renvoie un GeoDataFrame avec ID_PARCEL et geometry (Lambert 93, EPSG:2154).
    """
    contour = departements[departements["code_dep"] == code_dep].to_crs("EPSG:2154")
    contours = pyogrio.read_dataframe(chemin_rpg, columns=["ID_PARCEL"], bbox=tuple(contour.total_bounds), use_arrow=True)
    ids = parcelles.loc[parcelles["code_dep"] == code_dep, "id_parcelle"]
    return contours[contours["ID_PARCEL"].isin(ids)].reset_index(drop=True)
