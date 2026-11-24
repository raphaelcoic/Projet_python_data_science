from pathlib import Path

import pandas as pd

from src.pesticides.recuperer_pesticides import recuperer_pesticides


# Liste des 10 molécules retenues
SUBSTANCES_SELECTIONNEES = [
    "glyphosate",
    "s-metolachlore",
    "isoproturon",
    "chlorotoluron",
    "cuivre",
    "boscalid",
    "tebuconazole",
    "imidaclopride",
    "cypermethrine",
    "chlorpyriphos-ethyl",
]


def preparer_pesticides():
    """Télécharge les données brutes, les nettoie et enregistre le résultat."""

    # 1. Télécharger une nouvelle copie des données brutes
    chemin_csv = recuperer_pesticides(actualiser=True)

    df = pd.read_csv(
        chemin_csv,
        dtype={"geocode_departement": str}
    )

    # 2. Préparation des données
    df["date_mesure"] = pd.to_datetime(df["date_mesure"])
    df["annee"] = df["date_mesure"].dt.year
    df["geocode_departement"] = df["geocode_departement"].str.strip()

    # 3. Exclusion de la Corse et des DOM-TOM
    departements_exclus = ["2A", "2B", "971", "972", "973", "974", "976"]

    df = df[
        ~df["geocode_departement"].isin(departements_exclus)
    ]

    # 4. Conservation des 10 molécules sélectionnées
    df = df[
        df["substance"].isin(SUBSTANCES_SELECTIONNEES)
    ]

    # 5. Agrégation des quantités (biocontrôle + hors biocontrôle)
    df_pesticides = (
        df.groupby(
            ["geocode_departement", "libelle_departement", "annee", "substance"],
            as_index=False
        )
        .agg(quantite_totale=("valeur", "sum"))
    )

    # 6. Enregistrement du fichier nettoyé
    chemin_sortie = Path("data/processed/pesticides.parquet")
    chemin_sortie.parent.mkdir(parents=True, exist_ok=True)
    df_pesticides.to_parquet(chemin_sortie, index=False)

    print(f"Fichier nettoyé enregistré : {chemin_sortie}")
    print(f"Dimensions : {df_pesticides.shape}")
    print(f"Molécules sélectionnées : {SUBSTANCES_SELECTIONNEES}")

    return df_pesticides