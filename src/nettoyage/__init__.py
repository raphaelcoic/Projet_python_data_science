"""Croisement eau × cultures × pesticides par zone hydrographique.

Fonctions : agrégation des parcelles du RPG 2023 aux zones hydrographiques, avec leurs contours
(agreger_champs_zones) ; part de chaque parcelle dans chaque zone qu'elle touche
(associer_parcelles_zones), qui sert à sommer par zone les pesticides attribués aux parcelles
(agreger_pesticides_zones) ; table croisée par zone et par année (construire_base_zones).

Règle : un fichier = une fonction, nommé comme la fonction.
"""
