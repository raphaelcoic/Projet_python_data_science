"""Croisement eau × cultures × pesticides par zone hydrographique.

Dans l'ordre :
- part de chaque parcelle du RPG 2023 dans chaque zone qu'elle touche, à partir des contours
  (associer_parcelles_zones), puis surface de chaque groupe de cultures par zone (agreger_champs_zones) ;
- achats de chaque département répartis entre les groupes de cultures qui utilisent chaque molécule
  (constantes_cultures_molecules.py, calculer_doses_pesticides_groupes), puis pesticides attribués
  à chaque zone par année (agreger_pesticides_zones) ;
- fusion avec les indices de l'eau : table croisée par zone et par année (fusionner_eau_cultures_pesticides).
Méthode de répartition des pesticides : docs/repartition_pesticides.md.

Règle : un fichier = une fonction, nommé comme la fonction.
"""
