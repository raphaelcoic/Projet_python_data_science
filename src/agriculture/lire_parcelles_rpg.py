import sqlite3

import pyogrio

TAILLE_PAQUET = 500_000


def lire_parcelles_rpg(chemin_rpg, colonnes=("CODE_GROUP", "SURF_PARC")):
    """Lit les parcelles du RPG 2023 par paquets de 500 000, pour limiter la mémoire.

    chemin_rpg : GeoPackage des parcelles renvoyé par recuperer_rpg_ign.
    colonnes : colonnes à lire parmi CODE_CULTU (code culture), CODE_GROUP (groupe de cultures)
    et SURF_PARC (surface déclarée en hectares).
    Les paquets sont lus par plage d'identifiants (rowid), bien plus vite qu'en sautant des lignes.
    Renvoie, paquet par paquet, des GeoDataFrame avec ces colonnes et geometry (Lambert 93, EPSG:2154).
    """
    with sqlite3.connect(f"file:{chemin_rpg}?mode=ro", uri=True) as connexion:
        dernier = connexion.execute("SELECT max(rowid) FROM PARCELLES_GRAPHIQUES").fetchone()[0]
    for debut in range(0, dernier, TAILLE_PAQUET):
        parcelles = pyogrio.read_dataframe(
            chemin_rpg,
            columns=list(colonnes),
            where=f"rowid > {debut} AND rowid <= {debut + TAILLE_PAQUET}",
            use_arrow=True,
        )
        if "SURF_PARC" in parcelles:
            parcelles["SURF_PARC"] = parcelles["SURF_PARC"].astype("float64")
        yield parcelles
