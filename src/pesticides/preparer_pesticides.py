from pathlib import Path

import pandas as pd

from src.pesticides.constantes_pesticides import MOLECULES
from src.pesticides.recuperer_pesticides import recuperer_pesticides


# Les 8 sels de cuivre présents dans la base BNV-D regroupés sous le libellé "cuivre"
VARIANTES_CUIVRE = [
    "cuivre de l'hydroxyde de cuivre",
    "cuivre de l'oxychlorure de cuivre",
    "cuivre de l'oxychlorure de cuivre (trihydroxychlorure de dicuivre)",
    "cuivre de l'oxyde cuivreux",
    "cuivre du sulfate de cuivre",
    "cuivre du sulfate tetracuivrique et tricalcique",
    "cuivre du sulfate tribasique",
    "cuivre du tallate de cuivre",
]


def preparer_pesticides(actualiser=False):
    """Télécharge les données brutes, les nettoie et enregistre le résultat.

    actualiser : True pour retélécharger le CSV même s'il est déjà dans data/raw/.
    Renvoie un DataFrame (code_dep, nom_dep, annee, substance, quantite_kg), une ligne par
    département, année et molécule, aussi enregistré dans data/processed/pesticides.parquet.
    """

    # 1. Récupérer les données brutes (télécharge si absent ou si actualiser=True)
    chemin_csv = recuperer_pesticides(actualiser=actualiser)

    df = pd.read_csv(
        chemin_csv,
        dtype={"geocode_departement": str}
    )

    # 2. Préparation des données
    df["date_mesure"] = pd.to_datetime(df["date_mesure"])
    df["annee"] = df["date_mesure"].dt.year
    df["geocode_departement"] = df["geocode_departement"].str.strip()
    df["substance"] = df["substance"].str.strip().replace(
        {variante: "cuivre" for variante in VARIANTES_CUIVRE}
    )

    # 3. Exclusion de la Corse et des DOM-TOM
    departements_exclus = ["2A", "2B", "971", "972", "973", "974", "976"]

    df = df[
        ~df["geocode_departement"].isin(departements_exclus)
    ]

    # 4. Conservation des 10 molécules sélectionnées
    df = df[
        df["substance"].isin(MOLECULES)
    ]

    # 5. Agrégation des quantités (biocontrôle + hors biocontrôle)
    df_pesticides = (
        df.groupby(
            ["geocode_departement", "libelle_departement", "annee", "substance"],
            as_index=False
        )
        .agg(quantite_kg=("valeur", "sum"))
        .rename(columns={"geocode_departement": "code_dep", "libelle_departement": "nom_dep"})
    )

    # 6. Enregistrement du fichier nettoyé
    chemin_sortie = Path("data/processed/pesticides.parquet")
    chemin_sortie.parent.mkdir(parents=True, exist_ok=True)
    df_pesticides.to_parquet(chemin_sortie, index=False)

    print(f"Fichier nettoyé enregistré : {chemin_sortie}")
    print(f"Dimensions : {df_pesticides.shape}")
    print(f"Molécules sélectionnées : {MOLECULES}")

    return df_pesticides
