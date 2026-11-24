"""Données agricoles : parcelles du RPG 2023, lues dans l'archive nationale publiée par l'IGN.

Chaîne de la table à la parcelle (parcelles_rpg_2023.parquet), dans l'ordre :
téléchargement de l'archive (recuperer_rpg_ign), lecture par paquets (lire_parcelles_rpg),
département de chaque parcelle (src/geo/rattacher_departements.py), retrait des doublons et des
surfaces nulles (nettoyer_parcelles_rpg), libellés (ajouter_libelles_rpg) ; construire_parcelles_rpg
enchaîne ces étapes.
extraire_contours_departement tire de l'archive les contours d'un département, pour la démonstration de main.ipynb.
Le rattachement des parcelles aux zones hydrographiques, avec leurs contours, est dans
src/zones_hydrographiques/associer_parcelles_zones_hydro.py.
Les référentiels (groupes, catégories, nomenclature des cultures) sont dans constantes_rpg.py.

Règle : un fichier = une fonction, nommé comme la fonction.
"""
