import pyogrio

TAILLE_PAQUET = 500_000


def lire_parcelles_rpg(chemin_rpg):
    """Lit les parcelles du RPG par paquets de 500 000, pour limiter la mémoire.

    chemin_rpg : GeoPackage des parcelles renvoyé par recuperer_rpg_ign.
    Renvoie, paquet par paquet, des GeoDataFrame avec CODE_GROUP (groupe de cultures),
    SURF_PARC (surface déclarée en hectares) et geometry (Lambert 93, EPSG:2154).
    """
    nb_parcelles = pyogrio.read_info(chemin_rpg)["features"]
    for debut in range(0, nb_parcelles, TAILLE_PAQUET):
        parcelles = pyogrio.read_dataframe(
            chemin_rpg,
            columns=["CODE_GROUP", "SURF_PARC"],
            skip_features=debut,
            max_features=TAILLE_PAQUET,
            use_arrow=True,
        )
        parcelles["SURF_PARC"] = parcelles["SURF_PARC"].astype("float64")
        yield parcelles
