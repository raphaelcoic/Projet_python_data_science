import pandas as pd

from src.pesticides.constantes_pesticides import DEPARTEMENTS_EXCLUS, VARIANTES_CUIVRE


def nettoyer_pesticides(pesticides_bruts):
    """Nettoie les achats bruts de produits phytosanitaires (CSV de la BNV-D lu par pd.read_csv).

    pesticides_bruts : DataFrame avec date_mesure, geocode_departement (en texte), libelle_departement,
    biocontrole, danger_substance, substance et valeur (quantité achetée, en kg).
    Renomme les colonnes avec les noms du projet, tire l'année de la date, retire les espaces autour
    des codes et des noms, regroupe les 8 sels de cuivre sous « cuivre », et retire la Corse et les DROM.
    Garde toutes les substances : la sélection des 10 molécules vient ensuite (agreger_pesticides).
    Renvoie un DataFrame : code_dep, nom_dep, annee, substance, biocontrole, danger_substance, quantite_kg.
    """
    pesticides = pesticides_bruts.rename(columns={
        "geocode_departement": "code_dep",
        "libelle_departement": "nom_dep",
        "valeur": "quantite_kg",
    })
    pesticides["annee"] = pd.to_datetime(pesticides["date_mesure"]).dt.year
    pesticides["code_dep"] = pesticides["code_dep"].str.strip()
    pesticides["substance"] = pesticides["substance"].str.strip().replace({variante: "cuivre" for variante in VARIANTES_CUIVRE})
    pesticides = pesticides[~pesticides["code_dep"].isin(DEPARTEMENTS_EXCLUS)]
    return pesticides[["code_dep", "nom_dep", "annee", "substance", "biocontrole", "danger_substance", "quantite_kg"]]
