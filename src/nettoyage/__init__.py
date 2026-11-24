"""Croisement eau × cultures × pesticides par zone hydrographique.

Fonctions : part de chaque parcelle du RPG 2023 dans chaque zone hydrographique qu'elle touche,
à partir des contours (associer_parcelles_zones) ; avec ces parts, surface de chaque groupe de
cultures par zone (agreger_champs_zones) et pesticides attribués à chaque zone par année
(agreger_pesticides_zones) ; table croisée par zone et par année (construire_base_zones).

Règle : un fichier = une fonction, nommé comme la fonction.
"""
