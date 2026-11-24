"""Agrégation et ventilation des achats de pesticides à la maille parcellaire (RPG 2023).

Construit une table Parquet par année (2013–2023) combinant :
- data/processed/parcelles_rpg_2023.parquet
- data/processed/pesticides.parquet
- data/processed/correspondance_groupes_molecules.csv

Règle du dépôt : un fichier = une fonction, nommé comme la fonction.
Exécution complète : ``python -m src.agregation.construire_parcelles_pesticides``
"""
