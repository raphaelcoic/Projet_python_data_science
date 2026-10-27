"""Récupération des données agricoles : parcelles du RPG via le WFS de la Géoplateforme IGN.

Fonctions : téléchargement des parcelles par département (recuperer_parcelles_rpg),
sauvegarde par millésime dans data/processed/rpg/ (sauvegarder_parcelles_rpg),
puis fusion en un fichier national sans géométrie (fusionner_tous_millesimes_rpg).
Les référentiels partagés (colonnes, groupes de cultures) sont dans constantes_rpg.py.

Règle : un fichier = une fonction, nommé comme la fonction.
"""
