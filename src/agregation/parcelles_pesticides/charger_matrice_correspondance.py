"""Chargement de la matrice binaire groupes RPG × molécules."""

from pathlib import Path

import pandas as pd

from src.agregation.parcelles_pesticides.constantes_agregation import (
    CHEMIN_CORRESPONDANCE_DEFAUT,
    MOLECULES,
)
from src.agregation.parcelles_pesticides.creer_correspondance_groupes_molecules import (
    creer_correspondance_groupes_molecules,
)


def charger_matrice_correspondance(chemin=CHEMIN_CORRESPONDANCE_DEFAUT, actualiser=True):
    """Construit la matrice binaire (libelle_groupe × molécules) depuis le CSV de correspondance.

    Appelle ``creer_correspondance_groupes_molecules`` pour générer (ou régénérer si
    ``actualiser=True``) le fichier CSV à partir de la table codée en dur.

    Paramètres
    ----------
    chemin : str ou Path
        Chemin vers ``correspondance_groupes_molecules.csv``.
    actualiser : bool
        Si ``True`` (défaut) ou si le fichier n'existe pas encore, appelle
        ``creer_correspondance_groupes_molecules(chemin)`` avant la lecture.

    Renvoie
    -------
    pd.DataFrame
        DataFrame indexé par ``libelle_groupe`` (23 groupes) avec 10 colonnes
        (une par molécule dans l'ordre de ``MOLECULES``) et des valeurs entières
        ``0`` ou ``1``.
    """
    chemin = Path(chemin)
    if actualiser or not chemin.exists():
        creer_correspondance_groupes_molecules(chemin)

    df = pd.read_csv(chemin)

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
