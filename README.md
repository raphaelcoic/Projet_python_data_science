# Eau et agriculture : qualité des eaux et usage des pesticides

Projet Python pour la data science (ENSAE).

**Problématique :** _à formuler_

## Sources de données

| Données | Source |
|---|---|
| Indices biologiques des cours d'eau (I2M2, IBD, IPR) | [Hub'Eau – Hydrobiologie](https://hubeau.eaufrance.fr/page/api-hydrobiologie) |
| Stations de mesure des cours d'eau | [Hub'Eau – Qualité des cours d'eau](https://hubeau.eaufrance.fr/page/api-qualite-cours-deau) |
| Achats de produits phytosanitaires par département | CSV data.gouv.fr (lien exact à ajouter) |
| Parcelles agricoles | [RPG](https://www.data.gouv.fr/datasets/rpg) (IGN / ASP), via le WFS de la Géoplateforme |
| Fonds de carte | [france-geojson](https://github.com/gregoiredavid/france-geojson), ADMIN-EXPRESS (IGN) |

## Organisation du dépôt

```
├── main.ipynb              # Notebook FINAL : raconte l'analyse, appelle les fonctions de src/
├── src/                    # Code réutilisable : un fichier = une fonction
│   ├── hubeau/             #   API Hub'Eau (stations, indices biologiques)
│   ├── pesticides/         #   achats de pesticides
│   ├── agriculture/        #   parcelles agricoles du RPG (WFS IGN) ; constantes_rpg.py = référentiels
│   ├── geo/                #   périmètre (94 départements, hors Corse) et fonds de carte
│   ├── nettoyage/          #   nettoyage, agrégation, fusion
│   └── visualisation/      #   graphiques et cartes
├── notebooks/
│   ├── README.md           #   index des notebooks (qui, quoi)
│   └── exploration/        #   brouillons perso (un par personne / sujet)
├── data/
│   ├── raw/                #   données brutes téléchargées (non versionné)
│   ├── processed/          #   livrables du contrat de données, et rpg/ (non versionné)
│   └── geo/                #   shapefiles / fonds de carte (non versionné)
├── docs/contrat_donnees.md # Format des livrables de chaque partie
├── output/figures/         # Figures exportées
└── requirements.txt
```

**Le flux :** API / fichiers → `data/raw/` → nettoyage → `data/processed/` → analyse et cartes dans `main.ipynb`.

## Installation

Python 3.9 ou plus récent.

```bash
pip install -r requirements.txt
```

## Régénérer les données

| Partie | Commande | Produit |
|---|---|---|
| Eau | exécuter les parties 1 et 2 de `main.ipynb` | `data/raw/*.parquet`, `data/processed/eau.parquet` |
| Champs | `python -m src.agriculture.sauvegarder_parcelles_rpg` (millésimes 2013 et 2023, plusieurs heures, reprend où il s'est arrêté) | `data/processed/rpg/rpg2013/`, `rpg2023/` |
| | `python -m src.agriculture.fusionner_tous_millesimes_rpg` | `data/processed/rpg/rpg_{annee}_national.parquet` |
| | `agreger_champs(pd.read_parquet("data/processed/rpg/rpg_2023_national.parquet"))` | `data/processed/champs.parquet` |
| Pesticides | télécharger le CSV dans `data/raw/` | |

## Règles de travail en groupe

- **Notebooks d'exploration** : tous dans `notebooks/exploration/`, nommés `initiales_sujet.ipynb` (ex. `rc_hubeau_stations.ipynb`), et listés dans `notebooks/README.md`. Chacun ne modifie que les siens, ce qui évite les conflits git sur les notebooks.
- **Un fichier = une fonction** : quand un bout de code marche, il devient une fonction dans son propre fichier, nommé comme elle, dans le bon dossier de `src/`. Exemple : la fonction `recuperer_stations` va dans `src/hubeau/recuperer_stations.py` et s'importe avec `from src.hubeau.recuperer_stations import recuperer_stations`.
- **Chemins** : le code utilise des chemins relatifs à la racine du dépôt (`data/...`). Les notebooks de `notebooks/exploration/` commencent donc par une cellule qui se place à la racine (`os.chdir`) ; les scripts se lancent depuis la racine avec `python -m src.dossier.fichier`.
- **`main.ipynb`** : une seule personne l'édite à la fois (prévenez le groupe).
- **Branches** : une branche par tâche (ex. `hubeau-pagination`), puis une pull request vers `main`.
- **Données** : jamais commitées. Tout doit pouvoir être re-téléchargé par le code.
- Avant de commit un notebook, vider les sorties lourdes (*Kernel → Restart & Clear Output*) si possible.

## Répartition

| Étape | Membre A — Eau | Membre B — Champs | Membre C — Pesticides |
|---|---|---|---|
| Nom | _…_ | _…_ | _…_ |
| 1. Collecte (en parallèle) | `src/hubeau/` → `eau.parquet` | `src/agriculture/` → `champs.parquet` | `src/pesticides/` → `pesticides.parquet` |
| 2. Jointure (une personne) | `src/nettoyage/` → `base_finale.parquet` | | |
| 3. Stats descriptives (en parallèle) | qualité de l'eau | surfaces et cultures | achats de pesticides |

Le croisement eau × champs × pesticides se fait à trois, puis une seule personne assemble `main.ipynb`.

**Avant de coder, lire [`docs/contrat_donnees.md`](docs/contrat_donnees.md)** : maille, colonnes et types de chaque livrable.
