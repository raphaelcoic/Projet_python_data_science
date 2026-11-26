from pathlib import Path

import pandas as pd

from src.pesticides.agreger_pesticides import agreger_pesticides
from src.pesticides.constantes_pesticides import MOLECULES, VARIANTES_CUIVRE  # noqa: F401 (VARIANTES_CUIVRE : importée par le notebook pesticides)
from src.pesticides.nettoyer_pesticides import nettoyer_pesticides
from src.pesticides.recuperer_pesticides import recuperer_pesticides


def preparer_pesticides(actualiser=False):
    """Enchaîne les étapes de la base pesticides et l'enregistre dans data/processed/pesticides.parquet.

    actualiser : True pour retélécharger le CSV même s'il est déjà dans data/raw/.
    Étapes : téléchargement (recuperer_pesticides), lecture, nettoyage (nettoyer_pesticides),
    puis sélection des 10 molécules et somme de leurs achats (agreger_pesticides).
    main.ipynb montre ces étapes une par une ; cette fonction sert aux notebooks d'exploration.
    Renvoie un DataFrame : code_dep, nom_dep, annee, substance, quantite_kg.
    """
    pesticides_bruts = pd.read_csv(recuperer_pesticides(actualiser=actualiser), dtype={"geocode_departement": str})
    pesticides = agreger_pesticides(nettoyer_pesticides(pesticides_bruts), MOLECULES)
    chemin = Path("data/processed/pesticides.parquet")
    chemin.parent.mkdir(parents=True, exist_ok=True)
    pesticides.to_parquet(chemin, index=False)
    return pesticides
