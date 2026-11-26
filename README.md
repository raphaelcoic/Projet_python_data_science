# Eau et agriculture : les pesticides laissent-ils une trace dans les rivières ?

Projet Python pour la data science (ENSAE, 2026). Auteurs : _à compléter_.

**Problématique :** là où l'on achète le plus de pesticides, les rivières sont-elles en moins bonne santé biologique ? France métropolitaine continentale (94 départements), 2013-2023.

La directive-cadre sur l'eau juge le « bon état écologique » des cours d'eau en partie avec des indices biologiques, qui mesurent ce qui vit dans la rivière. On les croise avec les achats de 10 pesticides, répartis sur les parcelles agricoles qui les utilisent, puis sommés par zone hydrographique (le petit bassin versant d'une rivière). La réponse se fait en trois questions, avec des statistiques descriptives et sans modèle : dans le temps, dans l'espace, et après l'interdiction de trois molécules.

## Résultats principaux

1. **Dans le temps**, la médiane nationale des indices bouge trop peu pour être reliée aux achats.
2. **Dans l'espace**, les zones qui reçoivent le plus de pesticides ont des rivières en moins bon état. Des zones peu aux très exposées, l'I2M2 médian passe de 0,67 à 0,41 et la part des zones en bon état de 83 % à 45 %, y compris à part agricole comparable. Le lien est plus fragile pour les diatomées (IBD) et faible pour les poissons (IPR).
3. **Après les interdictions** de l'isoproturon, du chlorpyriphos-éthyl et de l'imidaclopride, les zones les plus exposées ne s'améliorent pas plus que les autres.

## Données

| Données | Source | Récupération |
|---|---|---|
| Indices biologiques des cours d'eau (I2M2, IBD, IPR), avec les coordonnées des stations | [Hub'Eau – Hydrobiologie](https://hubeau.eaufrance.fr/page/api-hydrobiologie) | API, 94 départements, environ 1 min 15 |
| Zones hydrographiques | [BD TOPAGE](https://www.sandre.eaufrance.fr/atlas/srv/fre/catalog.search#/home) (Sandre) | WFS, environ 20 s |
| Achats de produits phytosanitaires par département | [BNV-D sur data.gouv.fr](https://www.data.gouv.fr/api/1/datasets/r/6f664bd4-f27d-4e33-8ca7-c197c6adf217) (quantités en kg) | CSV |
| Parcelles agricoles et leur culture | [RPG 2023](https://www.data.gouv.fr/datasets/rpg) (IGN / ASP), archive nationale de l'IGN | archive de 2,75 Go, lue dans la release (voir plus bas) |
| Contours des départements | [france-geojson](https://github.com/gregoiredavid/france-geojson) | GeoJSON |

## Lancer le projet

Python 3.10 ou plus récent. Depuis la racine du dépôt :

```bash
pip install -r requirements.txt
```

Puis ouvrir `main.ipynb`, le rapport, et exécuter toutes les cellules dans l'ordre. Il télécharge lui-même les données dans `data/` (non versionné).

**Ce qui est lu dans la release.** Tout est recalculé à partir des sources, sauf les deux tables tirées de l'archive du RPG 2023 (environ 15 minutes de téléchargement, puis 25 minutes de calcul) : `parcelles_rpg_2023.parquet` et `parcelles_zones_hydro.parquet`. Elles sont déposées dans la release [`donnees-v1`](https://github.com/raphaelcoic/Projet_python_data_science/releases/tag/donnees-v1) et lues avec `recuperer_release(nom)`, qui les télécharge dans `data/processed/` au premier appel. Le code qui les produit est dans `src/` (`construire_parcelles_rpg`, `associer_parcelles_zones_hydro`), et la partie 3.1 de `main.ipynb` le rejoue sur l'Essonne (`parcelles_rpg_2023_91.gpkg`, aussi dans la release) pour vérifier que le résultat est identique.

## Organisation du dépôt

```
├── main.ipynb              # le rapport : raconte l'analyse et appelle les fonctions de src/
├── src/                    # le code, une fonction par fichier
│   ├── geo/                    #   départements du périmètre, contours, zones hydrographiques
│   ├── eau/                    #   indices biologiques : API Hub'Eau, nettoyage, agrégation par zone
│   ├── agriculture/            #   parcelles du RPG 2023 (archive IGN)
│   ├── pesticides/             #   achats des 10 molécules par département
│   ├── zones_hydrographiques/  #   croisement par zone : parcelles, doses de pesticides, base finale
│   ├── visualisation/          #   graphiques et cartes
│   └── recuperer_release.py    #   lit un fichier de la release
├── notebooks/exploration/  # brouillons de chaque partie, avec les statistiques retirées du rapport
├── docs/
│   └── bibliographie_pesticides.md
└── requirements.txt
```

| Notebook d'exploration | Partie | Contenu |
|---|---|---|
| [`rc_eau_indices`](notebooks/exploration/rc_eau_indices.ipynb) | Eau (Raph) | évolution 2013-2023 de chaque indice par zone |
| [`notebook_pesticides_final`](notebooks/exploration/notebook_pesticides_final.ipynb) | Pesticides (Sacha) | qualité des données, cartes, concentration, distributions, tendances |
| [`tf_selection_molecules_eau`](notebooks/exploration/tf_selection_molecules_eau.ipynb) | Champs (Tomia) | choix des 10 molécules dans la littérature |
| [`tf_correspondance_groupes_molecules`](notebooks/exploration/tf_correspondance_groupes_molecules.ipynb) | Champs (Tomia) | quels groupes de cultures utilisent quelle molécule |
| [`tf_rpg_exploration_2023`](notebooks/exploration/tf_rpg_exploration_2023.ipynb) | Champs (Tomia) | RPG 2023 : catégories, groupes, régions, cartes, filières, zoom sur 8 départements |

Les notebooks d'exploration lisent ce que `main.ipynb` a calculé : on les lance après lui.

## Règles de travail en groupe

- **Un fichier = une fonction**, dans le bon dossier de `src/`, avec une docstring ; le notebook ne fait qu'enchaîner les étapes.
- **Chemins relatifs** à la racine du dépôt (`data/...`) ; les notebooks d'exploration commencent par s'y placer.
- **`main.ipynb`** : une seule personne l'édite à la fois. Chacun ne modifie que ses notebooks d'exploration.
- **Branches** : une branche par tâche, puis une pull request vers `main`.
- **Données** : jamais commitées ; la release ne garde que les fichiers qui prennent plus de 5 minutes à calculer.
