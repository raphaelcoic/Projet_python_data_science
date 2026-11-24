"""Génération du CSV de correspondance groupes de cultures RPG × 10 molécules clés.

Table codée en dur à partir des homologations E-Phy (ANSES) et des guides techniques
de filière (Arvalis, Terres Inovia, IFV, CTIFL) sur la période 2013–2023, en miroir
du notebook d'exploration ``notebooks/exploration/tf_correspondance_groupes_molecules.ipynb``.
"""

from pathlib import Path

import pandas as pd

from src.agregation.parcelles_pesticides.constantes_agregation import (
    CHEMIN_CORRESPONDANCE_DEFAUT,
    MOLECULES,
)

FAMILLE_MOLECULE = {
    "glyphosate": "Herbicide",
    "s-metolachlore": "Herbicide",
    "isoproturon": "Herbicide",
    "chlorotoluron": "Herbicide",
    "cuivre": "Fongicide",
    "boscalid": "Fongicide",
    "tebuconazole": "Fongicide",
    "imidaclopride": "Insecticide",
    "cypermethrine": "Insecticide",
    "chlorpyriphos-ethyl": "Insecticide",
}

# Table de correspondance directe : pour chaque libelle_groupe RPG -> molécules utilisées (2013–2023)
MOLECULES_PAR_GROUPE = {
    "Blé tendre": [
        "glyphosate", "isoproturon", "chlorotoluron",
        "boscalid", "tebuconazole",
        "imidaclopride", "cypermethrine", "chlorpyriphos-ethyl",
    ],
    "Orge": [
        "glyphosate", "isoproturon", "chlorotoluron",
        "boscalid", "tebuconazole",
        "imidaclopride", "cypermethrine", "chlorpyriphos-ethyl",
    ],
    "Maïs grain et ensilage": [
        "glyphosate", "s-metolachlore",
        "imidaclopride", "cypermethrine", "chlorpyriphos-ethyl",
    ],
    "Légumes ou fleurs": [
        # Inclut la pomme de terre, le maraîchage et l'horticulture ornementale
        "glyphosate", "s-metolachlore",
        "cuivre", "boscalid", "tebuconazole",
        "imidaclopride", "cypermethrine", "chlorpyriphos-ethyl",
    ],
    "Autres céréales": [
        # Blé dur, triticale, seigle, avoine + sorgho (s-metolachlore)
        "glyphosate", "s-metolachlore", "isoproturon", "chlorotoluron",
        "boscalid", "tebuconazole",
        "imidaclopride", "cypermethrine", "chlorpyriphos-ethyl",
    ],
    "Divers": [],
    "Prairies permanentes": [],
    "Tournesol": [
        "glyphosate", "s-metolachlore",
        "boscalid",
        "cypermethrine",
    ],
    "Gel (surfaces gelées sans production)": [],
    "Autres cultures industrielles": [
        # Betterave sucrière, chicorée, houblon, tabac, PPAM
        "glyphosate", "s-metolachlore",
        "cuivre", "boscalid", "tebuconazole",
        "imidaclopride", "cypermethrine", "chlorpyriphos-ethyl",
    ],
    "Colza": [
        "glyphosate",
        "boscalid", "tebuconazole",
        "cypermethrine", "chlorpyriphos-ethyl",
    ],
    "Fourrage": [
        # Luzerne, trèfle, mélanges fourragers (destruction interculture + ravageurs luzerne)
        "glyphosate",
        "chlorpyriphos-ethyl",
    ],
    "Autres oléagineux": [
        # Soja (s-metolachlore), lin oléagineux, moutarde, navette
        "glyphosate", "s-metolachlore",
        "boscalid", "tebuconazole",
        "cypermethrine",
    ],
    "Prairies temporaires": [
        # Destruction / rénovation avant implantation
        "glyphosate",
    ],
    "Protéagineux": [
        # Pois protéagineux, féverole, lupin
        "glyphosate",
        "boscalid", "tebuconazole",
        "cypermethrine",
    ],
    "Estives et landes": [],
    "Vergers": [
        "glyphosate",
        "cuivre", "boscalid", "tebuconazole",
        "imidaclopride", "cypermethrine", "chlorpyriphos-ethyl",
    ],
    "Plantes à fibres": [
        # Lin fibres, chanvre
        "glyphosate",
        "tebuconazole",
        "cypermethrine",
    ],
    "Légumineuses à grains": [
        # Lentille, pois chiche, haricots/pois secs
        "glyphosate",
        "boscalid", "tebuconazole",
        "cypermethrine",
    ],
    "Vignes": [
        "glyphosate",
        "cuivre", "boscalid", "tebuconazole",
        "imidaclopride", "cypermethrine", "chlorpyriphos-ethyl",
    ],
    "Fruits à coque": [
        # Noyer, noisetier, châtaignier, amandier
        "glyphosate",
        "cuivre",
        "cypermethrine", "chlorpyriphos-ethyl",
    ],
    "Oliviers": [
        "glyphosate",
        "cuivre",
        "cypermethrine",
    ],
    "Riz": [
        # Désherbage interculture avant semis
        "glyphosate",
    ],
}


def _filtrer_famille(molecules, famille):
    return ", ".join(m for m in molecules if FAMILLE_MOLECULE[m] == famille)


def creer_correspondance_groupes_molecules(chemin_sortie=CHEMIN_CORRESPONDANCE_DEFAUT):
    """Crée le fichier CSV de correspondance entre les 23 groupes RPG et les 10 molécules clés.

    Paramètres
    ----------
    chemin_sortie : str ou Path
        Emplacement du fichier CSV à créer (par défaut :
        ``data/processed/correspondance_groupes_molecules.csv``).

    Renvoie
    -------
    Path
        Chemin du fichier CSV créé.
    """
    molecules_valides = set(MOLECULES)
    for groupe, mols in MOLECULES_PAR_GROUPE.items():
        inconnues = set(mols) - molecules_valides
        if inconnues:
            raise ValueError(f"Molécules inconnues dans le groupe '{groupe}' : {sorted(inconnues)}")

    table = (
        pd.DataFrame([
            {
                "libelle_groupe": groupe,
                "nb_molecules": len(mols),
                "herbicides": _filtrer_famille(mols, "Herbicide"),
                "fongicides": _filtrer_famille(mols, "Fongicide"),
                "insecticides": _filtrer_famille(mols, "Insecticide"),
                "molecules_utilisees": ", ".join(mols) if mols else "(aucune)",
            }
            for groupe, mols in MOLECULES_PAR_GROUPE.items()
        ])
        .sort_values(["nb_molecules", "libelle_groupe"], ascending=[False, True])
        .reset_index(drop=True)
    )

    chemin_sortie = Path(chemin_sortie)
    chemin_sortie.parent.mkdir(parents=True, exist_ok=True)
    temporaire = chemin_sortie.with_suffix(".csv.tmp")
    try:
        table.to_csv(temporaire, index=False, encoding="utf-8")
        temporaire.replace(chemin_sortie)
    finally:
        if temporaire.exists():
            temporaire.unlink()

    return chemin_sortie


if __name__ == "__main__":
    chemin = creer_correspondance_groupes_molecules()
    print(f"Table de correspondance enregistrée : {chemin}")
