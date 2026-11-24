"""Constantes partagées du pipeline d'agrégation parcelles × pesticides."""

from pathlib import Path

# Chemins par défaut (relatifs à la racine du dépôt)
CHEMIN_PARCELLES_DEFAUT = Path("data/processed/parcelles_rpg_2023.parquet")
CHEMIN_PESTICIDES_DEFAUT = Path("data/processed/pesticides.parquet")
CHEMIN_CORRESPONDANCE_DEFAUT = Path("data/processed/correspondance_groupes_molecules.csv")
CHEMIN_DOSES_DEFAUT = Path("data/processed/doses_pesticides_groupes.parquet")
DOSSIER_SORTIE_DEFAUT = Path("data/processed/parcelles_pesticides")

# Colonnes conservées depuis parcelles_rpg_2023.parquet
# (code_culture et categorie_culture sont volontairement écartées)
COLONNES_PARCELLES_CONSERVEES = [
    "id_parcelle",
    "code_dep",
    "nom_dep",
    "surface_ha",
    "code_groupe",
    "libelle_groupe",
]

# Ordre canonique des 10 molécules retenues
MOLECULES = [
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

# Correspondance nom de molécule -> nom de colonne en snake_case avec unité (kg)
COLONNES_MOLECULES = {
    molecule: f"{molecule.replace('-', '_')}_kg"
    for molecule in MOLECULES
}

LISTE_COLONNES_MOLECULES = [COLONNES_MOLECULES[m] for m in MOLECULES]
