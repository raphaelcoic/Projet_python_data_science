from src.agriculture.telecharger_archive_ign import telecharger_archive_ign

# Le RPG 2013 n'est publié que par région (13 régions de métropole, Corse comprise)
REGIONS = ["R11", "R24", "R27", "R28", "R32", "R44", "R52", "R53", "R75", "R76", "R84", "R93", "R94"]


def recuperer_rpg_2013_ign(dossier="data/raw/rpg_ign"):
    """Télécharge et décompresse les 13 archives régionales du RPG 2013 publiées par l'IGN.

    dossier : dossier où ranger les archives et leur contenu décompressé.
    En 2013, le RPG décrit des îlots (groupes de parcelles d'une exploitation),
    chacun avec son groupe de cultures majoritaire.
    Renvoie la liste des fichiers d'îlots (un shapefile par région).
    """
    return [
        next(telecharger_archive_ign(f"RPG_1-0__SHP_LAMB93_{region}_2013-01-01", dossier).rglob("ILOTS_ANONYMES.shp"))
        for region in REGIONS
    ]
