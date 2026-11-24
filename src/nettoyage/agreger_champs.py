from src.agriculture.constantes_rpg import LIBELLES_GROUPES_RPG
from src.geo.liste_departements import liste_departements

CLE = ["code_dep", "code_groupe_culture", "libelle_groupe_culture"]


def agreger_champs(parcelles):
    """Agrège les parcelles du RPG 2023 au département × groupe de cultures (surfaces en hectares).

    parcelles : DataFrame renvoyé par tabuler_parcelles_rpg.
    Seuls les 94 départements du périmètre sont gardés (la Corse est écartée).
    Renvoie un DataFrame avec les colonnes de champs.parquet.
    """
    parcelles = parcelles[parcelles["code_dep"].isin(liste_departements())]
    champs = parcelles.groupby(["code_dep", "code_groupe"], as_index=False)["surface_ha"].sum()
    champs.columns = ["code_dep", "code_groupe_culture", "surface_ha"]
    champs["libelle_groupe_culture"] = champs["code_groupe_culture"].map(LIBELLES_GROUPES_RPG)
    return champs[[*CLE, "surface_ha"]]
