"""Données agricoles : parcelles du RPG, lues dans les archives publiées par l'IGN.

Fonctions : téléchargement des archives (telecharger_archive_ign ; recuperer_rpg_ign pour 2023,
recuperer_rpg_2013_ign pour les 13 archives régionales de 2013), lecture des parcelles 2023 par paquets
(lire_parcelles_rpg), tables à la parcelle avec leur département, sans les contours
(tabuler_parcelles_rpg pour 2023, tabuler_ilots_rpg_2013 pour 2013).
Les référentiels (groupes, catégories, nomenclature des cultures) sont dans constantes_rpg.py.

Règle : un fichier = une fonction, nommé comme la fonction.
"""
