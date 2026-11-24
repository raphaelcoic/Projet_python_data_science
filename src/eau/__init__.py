"""Partie eau : de l'API Hub'Eau à la table eau_zones_hydro.parquet.

Fonctions : interroger l'API (interroger_hubeau, avec relances ; indices biologiques I2M2, IBD, IPR,
avec les coordonnées des stations), nettoyer les indices (nettoyer_indices), rattacher les stations
à leur zone hydrographique (rattacher_stations_zones_hydro), puis agréger les indices
à la zone (agreger_eau_zones_hydro). main.ipynb enchaîne ces étapes, une par cellule ;
l'API est appelée à chaque exécution (environ 1 min 15).

Règle : un fichier = une fonction, nommé comme la fonction.
"""
