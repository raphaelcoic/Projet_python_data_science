"""Chargement de la matrice binaire groupes RPG × molécules."""

from pathlib import Path

import pandas as pd

from src.agregation.constantes_agregation import (
    CHEMIN_CORRESPONDANCE_DEFAUT,
    MOLECULES,
)


def charger_matrice_correspondance(chemin=CHEMIN_CORRESPONDANCE_DEFAUT):
    """Construit la matrice binaire (libelle_groupe × molécules) depuis le CSV de correspondance.

    Paramètres
    ----------
    chemin : str ou Path
        Chemin vers ``correspondance_groupes_molecules.csv``.

    Renvoie
    -------
    pd.DataFrame
        DataFrame indexé par ``libelle_groupe`` (23 groupes) avec 10 colonnes
        (une par molécule dans l'ordre de ``MOLECULES``) et des valeurs entières
        ``0`` ou ``1``.
    """
    df = pd.read_csv(Path(chemin))

    if "libelle_groupe" not in df.columns or "molecules_utilisees" not in df.columns:
        raise ValueError(
            "Le fichier de correspondance doit contenir les colonnes "
            "'libelle_groupe' et 'molecules_utilisees'."
        )

    lignes = {}
    for _, ligne in df.iterrows():
        groupe = str(ligne["libelle_groupe"]).strip()
        brut = "" if pd.isna(ligne["molecules_utilisees"]) else str(ligne["molecules_utilisees"]).strip()

        if not brut or brut == "(aucune)":
            actives = set()
        else:
            actives = {item.strip() for item in brut.split(",") if item.strip()}

        inconnues = actives - set(MOLECULES)
        if inconnues:
            raise ValueError(
                f"Molécules inconnues dans le groupe '{groupe}' : {sorted(inconnues)}"
            )

        lignes[groupe] = [1 if m in actives else 0 for m in MOLECULES]

    matrice = pd.DataFrame.from_dict(lignes, orient="index", columns=MOLECULES)
    matrice.index.name = "libelle_groupe"
    return matrice.astype("int8")
