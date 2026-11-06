from pathlib import Path

import geopandas as gpd
import pandas as pd

from src.nettoyage.agreger_champs_zones import CLE, agreger_champs_zones

DOSSIER = Path("data/processed/rpg/rpg2023")
COLONNES = ["code_groupe", "libelle_groupe", "surface_ha", "geometry"]


def agreger_tous_champs_zones(zones):
    """Agrège tous les fichiers départementaux du RPG 2023 à la zone hydrographique × groupe de cultures.

    Une zone peut s'étendre sur plusieurs départements : les surfaces sont sommées à la fin.
    Renvoie un DataFrame avec les colonnes de champs_zones.parquet.
    """
    resultats = []
    for fichier in sorted(DOSSIER.glob("rpg_2023_*.parquet")):
        resultats.append(agreger_champs_zones(gpd.read_parquet(fichier, columns=COLONNES), zones))
    return pd.concat(resultats, ignore_index=True).groupby(CLE, as_index=False)["surface_ha"].sum()
