
import random
from pathlib import Path

import pandas as pd

from src.pesticides.recuperer_pesticides import recuperer_pesticides


# Liste provisoire : à remplacer par les 10 molécules définitives
def selectionner_substances(df, nombre=10, graine=0):
    substances = df["substance"].dropna().unique().tolist()

    if len(substances) < nombre:
        raise ValueError(f"Seulement {len(substances)} substances disponibles.")

    return random.Random(graine).sample(substances, nombre)


def preparer_pesticides():
    """Télécharge les données brutes, les nettoie et enregistre le résultat."""

    # 1. Télécharger une nouvelle copie des données brutes
    chemin_csv = recuperer_pesticides(actualiser=True)

    df = pd.read_csv(
        chemin_csv,
        dtype={"geocode_departement": str}
    )

    # 2. Sélection provisoire des 10 molécules
    substances_selectionnees = selectionner_substances(df)

    # 3. Préparation des données
    df["date_mesure"] = pd.to_datetime(df["date_mesure"])
    df["annee"] = df["date_mesure"].dt.year
    df["geocode_departement"] = df["geocode_departement"].str.strip()

    # 4. Exclusion de la Corse et des DOM-TOM
    departements_exclus = ["2A", "2B", "971", "972", "973", "974", "976"]

    df = df[
        ~df["geocode_departement"].isin(departements_exclus)
    ]

    # 5. Conservation des molécules sélectionnées
    df = df[
        df["substance"].isin(substances_selectionnees)
    ]

    # 6. Agrégation des quantités (biocontrôle + hors biocontrôle)
    df_pesticides = (
        df.groupby(
            ["geocode_departement", "libelle_departement", "annee", "substance"],
            as_index=False
        )
        .agg(quantite_totale=("valeur", "sum"))
    )

    # 7. Enregistrement du fichier nettoyé
    chemin_sortie = Path("data/processed/pesticides.parquet")
    chemin_sortie.parent.mkdir(parents=True, exist_ok=True)
    df_pesticides.to_parquet(chemin_sortie, index=False)

    print(f"Fichier nettoyé enregistré : {chemin_sortie}")
    print(f"Dimensions : {df_pesticides.shape}")
    print(f"Molécules sélectionnées : {substances_selectionnees}")

    return df_pesticides
