"""Récupération des données Hub'Eau sur les cours d'eau.

Fonctions : interroger l'API (stations hydrobiologiques, indices biologiques
I2M2, IBD, IPR), renvoyer des DataFrames bruts sauvegardés dans data/raw/,
puis agréger les indices nettoyés à la zone hydrographique (agreger_eau_zones).

Règle : un fichier = une fonction, nommé comme la fonction.
"""
