"""Partie pesticides : du CSV de la BNV-D à la table pesticides.parquet (achats par département).

Dans l'ordre : téléchargement du CSV dans data/raw/ (recuperer_pesticides), nettoyage
(nettoyer_pesticides : noms de colonnes, année, sels de cuivre regroupés, Corse et DROM retirés),
puis sélection des 10 molécules et somme de leurs achats (agreger_pesticides).
main.ipynb enchaîne ces étapes, une par cellule ; preparer_pesticides les enchaîne pour les notebooks d'exploration.
Les molécules suivies, les sels de cuivre et les départements exclus sont dans constantes_pesticides.py.
Le croisement avec les parcelles est dans src/zones_hydrographiques/.

Règle : un fichier = une fonction, nommé comme la fonction.
"""
