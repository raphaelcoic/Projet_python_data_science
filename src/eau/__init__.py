"""Partie eau : de l'API Hub'Eau à la table eau_zones_hydro.parquet.

Fonctions : interroger l'API (interroger_hubeau, avec relances ; stations hydrobiologiques, indices biologiques
I2M2, IBD, IPR), nettoyer les indices (nettoyer_indices), rattacher les stations
à leur zone hydrographique (rattacher_stations_zones_hydro), puis agréger les indices
à la zone (agreger_eau_zones_hydro). construire_eau_zones_hydro enchaîne ces étapes ;
l'API n'est appelée que si eau_zones_hydro.parquet manque.

Règle : un fichier = une fonction, nommé comme la fonction.
"""
