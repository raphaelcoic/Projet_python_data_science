# Notebooks d'exploration

Brouillons de chacun, rangés dans `exploration/` et nommés `initiales_sujet.ipynb`.
Ils restent versionnés pour garder la trace du travail, même quand le code
est passé dans `src/` et l'analyse dans `main.ipynb`.

Quand vous ajoutez un notebook, ajoutez une ligne ici.

| Notebook | Auteur | Sujet |
|---|---|---|
| [`rc_eau_indices.ipynb`](exploration/rc_eau_indices.ipynb) | Raph | Indices biologiques des cours d'eau (I2M2, IBD, IPR), 2013-2023 : couverture, distribution, évolution, cartes, zoom sur l'Ille-et-Vilaine |
| [`sc_pesticides.ipynb`](exploration/sc_pesticides.ipynb) | Sacha | Achats de produits phytosanitaires par département et substance, 2013-2023 : qualité des données, cartes, évolution |
| [`tf_selection_molecules_eau.ipynb`](exploration/tf_selection_molecules_eau.ipynb) | Tomia | Sélection bibliographique indépendante (réduction de variables : 511 → 10 molécules clés) des pesticides les plus impactants pour la qualité de l'eau |
| [`tf_correspondance_groupes_molecules.ipynb`](exploration/tf_correspondance_groupes_molecules.ipynb) | Tomia | Table de correspondance simple entre les 23 `libelle_groupe` du RPG et les 10 molécules clés sélectionnées pour la qualité de l'eau |

Les notebooks RPG de Tomia (`tf_rpg_*`) lisaient les données du WFS de l'IGN, abandonné le 2026-11-23 :
ils restent consultables dans l'historique git.
