"""Récupération des achats de produits phytosanitaires par département.

Fonctions : téléchargement du CSV dans data/raw/ (recuperer_pesticides), puis nettoyage
et agrégation des 10 molécules retenues (constantes_pesticides.py) vers pesticides.parquet
(preparer_pesticides). Le croisement avec les parcelles est dans src/zones_hydrographiques/.

Règle : un fichier = une fonction, nommé comme la fonction.
"""
