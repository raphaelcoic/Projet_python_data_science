# Notebooks d'exploration

Brouillons de chacun, rangés dans `exploration/` et nommés `initiales_sujet.ipynb`.
Ils restent versionnés pour garder la trace du travail, même quand le code
est passé dans `src/` et l'analyse dans `main.ipynb`.

Quand vous ajoutez un notebook, ajoutez une ligne ici.

| Notebook | Auteur | Sujet |
|---|---|---|
| [`notebook_pesticides_final.ipynb`](exploration/notebook_pesticides_final.ipynb) | Sacha | Achats de produits phytosanitaires par département, 2013-2023 : qualité des données, 10 molécules du projet, cartes (niveaux, molécule dominante, évolutions), concentration, tendances |
| [`tf_selection_molecules_eau.ipynb`](exploration/tf_selection_molecules_eau.ipynb) | Tomia | Sélection bibliographique indépendante (réduction de variables : 511 → 10 molécules clés) des pesticides les plus impactants pour la qualité de l'eau |
| [`tf_correspondance_groupes_molecules.ipynb`](exploration/tf_correspondance_groupes_molecules.ipynb) | Tomia | Table de correspondance simple entre les 23 `libelle_groupe` du RPG et les 10 molécules clés sélectionnées pour la qualité de l'eau |
| [`tf_rpg_exploration_2023.ipynb`](exploration/tf_rpg_exploration_2023.ipynb) | Tomia | RPG 2023 : surfaces par catégorie, groupe et culture, profils régionaux, cartes par département |

Les notebooks RPG lisent l'archive nationale du RPG 2023 publiée par l'IGN, via `src/agriculture/`.
