from src.agriculture.telecharger_archive_ign import telecharger_archive_ign

NOM = "RPG_2-2__GPKG_LAMB93_FXX_2023-01-01"


def recuperer_rpg_ign(dossier="data/raw/rpg_ign"):
    """Télécharge et décompresse l'archive nationale du RPG 2023 publiée par l'IGN.

    dossier : dossier où ranger l'archive (2,75 Go) et son contenu décompressé.
    L'archive contient un GeoPackage des parcelles (Lambert 93, France métropolitaine avec la Corse).
    Renvoie le chemin du GeoPackage des parcelles.
    """
    return next(telecharger_archive_ign(NOM, dossier).rglob("PARCELLES_GRAPHIQUES.gpkg"))
