import pandas as pd
import pyogrio

from src.agriculture.constantes_rpg import LIBELLES_GROUPES_RPG

CLE = ["code_zone", "code_groupe_culture", "libelle_groupe_culture"]
TAILLE_PAQUET = 500_000


def _agreger_paquet(parcelles, zones):
    """Surface de chaque groupe de cultures par zone, pour un paquet de parcelles."""
    paires = parcelles.sjoin(zones[["code_zone", "geometry"]], predicate="intersects")
    coupees = paires.index.duplicated(keep=False)
    contours = paires.geometry[coupees].make_valid()
    morceaux = contours.intersection(zones.geometry.loc[paires.loc[coupees, "index_right"]], align=False)
    paires.loc[coupees, "SURF_PARC"] *= morceaux.area / contours.area
    return paires.groupby(["code_zone", "CODE_GROUP"])["SURF_PARC"].sum()


def agreger_champs_zones(chemin_rpg, zones):
    """Agrège les parcelles du RPG à la zone hydrographique × groupe de cultures (surfaces en hectares).

    chemin_rpg : GeoPackage des parcelles renvoyé par recuperer_rpg_ign.
    zones : GeoDataFrame renvoyé par recuperer_zones_hydro.
    Une parcelle qui touche une seule zone y va entière. Une parcelle qui en touche
    plusieurs est coupée selon leurs limites, et sa surface est répartie au prorata.
    Les parcelles sont lues par paquets de 500 000 pour limiter la mémoire.
    Renvoie un DataFrame avec les colonnes de champs_zones.parquet.
    """
    nb_parcelles = pyogrio.read_info(chemin_rpg)["features"]
    paquets = []
    for debut in range(0, nb_parcelles, TAILLE_PAQUET):
        parcelles = pyogrio.read_dataframe(
            chemin_rpg,
            columns=["CODE_GROUP", "SURF_PARC"],
            skip_features=debut,
            max_features=TAILLE_PAQUET,
            use_arrow=True,
        ).to_crs(zones.crs)
        parcelles["SURF_PARC"] = parcelles["SURF_PARC"].astype("float64")
        paquets.append(_agreger_paquet(parcelles, zones))

    surfaces = pd.concat(paquets).groupby(level=[0, 1]).sum().reset_index()
    surfaces.columns = ["code_zone", "code_groupe_culture", "surface_ha"]
    surfaces["libelle_groupe_culture"] = surfaces["code_groupe_culture"].map(LIBELLES_GROUPES_RPG)
    return surfaces[[*CLE, "surface_ha"]]
