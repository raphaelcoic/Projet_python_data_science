# Eau et agriculture : qualité des eaux et usage des pesticides

Projet Python pour la data science (ENSAE).

**Problématique :** _à formuler_

## Sources de données

| Données | Source |
|---|---|
| Indices biologiques des cours d'eau (I2M2, IBD, IPR), avec les coordonnées des stations | [Hub'Eau – Hydrobiologie](https://hubeau.eaufrance.fr/page/api-hydrobiologie) |
| Zones hydrographiques | [BD TOPAGE](https://www.sandre.eaufrance.fr/atlas/srv/fre/catalog.search#/home) (Sandre), via son WFS |
| Achats de produits phytosanitaires par département | [CSV data.gouv.fr](https://www.data.gouv.fr/api/1/datasets/r/6f664bd4-f27d-4e33-8ca7-c197c6adf217) (BNV-D, quantités en kg) |
| Parcelles agricoles | [RPG](https://www.data.gouv.fr/datasets/rpg) (IGN / ASP), archive nationale 2023 de l'IGN |
| Fonds de carte | [france-geojson](https://github.com/gregoiredavid/france-geojson) |

## Organisation du dépôt

```
├── main.ipynb              # Notebook FINAL : raconte l'analyse, appelle les fonctions de src/
├── src/                    # Code réutilisable : un fichier = une fonction
│   ├── geo/                    #   périmètre (94 départements, hors Corse), contours des départements et des zones hydrographiques
│   ├── eau/                    #   indices biologiques : API Hub'Eau → eau_zones_hydro.parquet
│   ├── agriculture/            #   parcelles du RPG 2023 (archive IGN) → parcelles_rpg_2023.parquet ; constantes_rpg.py = libellés des cultures
│   ├── pesticides/             #   achats des 10 molécules par département → pesticides.parquet
│   ├── zones_hydrographiques/  #   croisement : parcelles, cultures et pesticides par zone hydrographique, puis fusion avec l'eau → base_finale.parquet
│   ├── visualisation/          #   statistiques descriptives, graphiques et cartes
│   └── recuperer_release.py    #   lit dans la release un fichier qui prend plus de 5 minutes à calculer
├── notebooks/
│   ├── README.md           #   index des notebooks (qui, quoi)
│   └── exploration/        #   brouillons perso (un par personne / sujet)
├── data/
│   ├── raw/                #   données brutes téléchargées (non versionné)
│   ├── processed/          #   livrables du contrat de données (non versionné)
│   └── geo/                #   shapefiles / fonds de carte (non versionné)
├── docs/
│   ├── contrat_donnees.md        # format des livrables de chaque partie
│   └── repartition_pesticides.md # méthode de répartition des achats de pesticides entre les cultures
└── requirements.txt
```

**La chaîne :**

1. **Chaque source à part** : `src/eau/` → `eau_zones_hydro.parquet`, `src/agriculture/` → `parcelles_rpg_2023.parquet`, `src/pesticides/` → `pesticides.parquet`.
2. **Croisement dans `src/zones_hydrographiques/`** :
   - parcelles → zones hydrographiques (`associer_parcelles_zones_hydro` → `parcelles_zones_hydro.parquet`) → surface de chaque culture par zone (`agreger_champs_zones_hydro`, en mémoire) ;
   - achats répartis entre les cultures qui utilisent chaque molécule (`calculer_doses_pesticides_groupes`) → pesticides par zone (`agreger_pesticides_zones_hydro`, en mémoire) ;
   - fusion avec les indices de l'eau (`fusionner_eau_cultures_pesticides` → `base_finale.parquet`).
3. **Analyse et cartes** dans `main.ipynb`.

## Installation

Python 3.9 ou plus récent.

```bash
pip install -r requirements.txt
```

## Données : calculées ou lues dans la release

`main.ipynb` recalcule tout à partir des sources. Seule exception : un fichier qui prend **plus de 5 minutes** à calculer est déposé à la main dans la release [`donnees-v1`](https://github.com/raphaelcoic/Projet_python_data_science/releases/tag/donnees-v1), puis lu avec `recuperer_release(nom)`, qui le télécharge dans `data/processed/` s'il n'y est pas déjà.

Ce sont aujourd'hui les deux tables tirées de l'archive du RPG 2023 de l'IGN (2,75 Go, environ 15 minutes de téléchargement) :

| Fichier | Calcul |
|---|---|
| `parcelles_rpg_2023.parquet` (104 Mo) | `construire_parcelles_rpg(recuperer_rpg_ign(), recuperer_departements())` |
| `parcelles_zones_hydro.parquet` (76 Mo) | `associer_parcelles_zones_hydro(recuperer_rpg_ign(), zones_hydro)`, environ 25 minutes en plus de l'archive |

La release contient aussi `parcelles_rpg_2023_91.gpkg` (10 Mo) : les contours des parcelles de l'Essonne, tirés de l'archive par `extraire_contours_departement(recuperer_rpg_ign(), parcelles, departements, "91")`. La partie 3.1 de `main.ipynb` y rejoue `associer_parcelles_zones_hydro` en une seconde et vérifie que le résultat est identique à `parcelles_zones_hydro.parquet`.

Tout le reste prend moins de 2 minutes (mesures du 2026-11-24) : les indices Hub'Eau environ 1 min 15 (8 départements à la fois), les zones hydrographiques 20 s, le CSV des pesticides 3 s, chaque agrégation par zone une dizaine de secondes.

L'archive elle-même n'est pas dans la release : elle dépasse la limite de 2 Go par fichier de GitHub, et l'IGN l'héberge déjà. `recuperer_rpg_ign()` la télécharge dans `data/raw/rpg_ign/`.

Si le code qui produit un fichier de la release change, on le recalcule puis on remplace sa copie dans la release (droits d'écriture sur le dépôt) :

```python
associer_parcelles_zones_hydro(recuperer_rpg_ign(), zones_hydro).to_parquet("data/processed/parcelles_zones_hydro.parquet", index=False)
```

```bash
gh release upload donnees-v1 data/processed/parcelles_zones_hydro.parquet --clobber
```

## Régénérer les données

| Partie | Commande | Produit |
|---|---|---|
| Eau | `recuperer_tous_indices()` (API Hub'Eau, environ 1 min 15 ; donne aussi les coordonnées des stations) | en mémoire (`indices_bruts`, `stations`) |
| | `nettoyer_indices(indices_bruts)` | en mémoire (`indices`) |
| Champs | `construire_parcelles_rpg(recuperer_rpg_ign(), recuperer_departements())` (archive RPG 2023 de l'IGN, 2,75 Go ; une ligne par parcelle, pour lier aux ventes de molécules) | `data/processed/parcelles_rpg_2023.parquet` (release) |
| Pesticides | `preparer_pesticides()` (télécharge le CSV dans `data/raw/`, garde les 10 molécules) | `data/processed/pesticides.parquet` |
| Zones | `recuperer_zones_hydro()` | en mémoire (`zones_hydro`) |
| | `rattacher_stations_zones_hydro(stations_suivies, zones_hydro)` | en mémoire (`stations_zones_hydro`) |
| | `agreger_eau_zones_hydro(indices, stations_zones_hydro)` | `data/processed/eau_zones_hydro.parquet` |
| | `associer_parcelles_zones_hydro(recuperer_rpg_ign(), zones_hydro)` (archive RPG 2023 de l'IGN, environ 25 min) | `data/processed/parcelles_zones_hydro.parquet` (release) |
| | `agreger_champs_zones_hydro(parcelles, parcelles_zones_hydro)` (quelques secondes) | en mémoire (`champs_zones_hydro`) |
| | `calculer_doses_pesticides_groupes(parcelles, pesticides)` | en mémoire (`doses`) |
| | `agreger_pesticides_zones_hydro(doses, parcelles, parcelles_zones_hydro)` (quelques secondes) | en mémoire (`pesticides_zones_hydro`) |
| | `fusionner_eau_cultures_pesticides(eau_zones_hydro, champs_zones_hydro, pesticides_zones_hydro, zones_hydro)` | `data/processed/base_finale.parquet` |

## Règles de travail en groupe

- **Notebooks d'exploration** : tous dans `notebooks/exploration/`, nommés `initiales_sujet.ipynb` (ex. `rc_hubeau_stations.ipynb`), et listés dans `notebooks/README.md`. Chacun ne modifie que les siens, ce qui évite les conflits git sur les notebooks.
- **Un fichier = une fonction** : quand un bout de code marche, il devient une fonction dans son propre fichier, nommé comme elle, dans le bon dossier de `src/`. Exemple : la fonction `recuperer_indices` va dans `src/eau/recuperer_indices.py` et s'importe avec `from src.eau.recuperer_indices import recuperer_indices`.
- **Chemins** : le code utilise des chemins relatifs à la racine du dépôt (`data/...`). Les notebooks de `notebooks/exploration/` commencent donc par une cellule qui se place à la racine (`os.chdir`) ; les scripts se lancent depuis la racine avec `python -m src.dossier.fichier`.
- **`main.ipynb`** : une seule personne l'édite à la fois (prévenez le groupe).
- **Branches** : une branche par tâche (ex. `hubeau-pagination`), puis une pull request vers `main`.
- **Données** : jamais commitées. Tout doit pouvoir être recalculé par le code ; la release ne garde que les fichiers qui prennent plus de 5 minutes à calculer.
- Avant de commit un notebook, vider les sorties lourdes (*Kernel → Restart & Clear Output*) si possible.

## Répartition

| Étape | Membre A — Eau | Membre B — Champs | Membre C — Pesticides |
|---|---|---|---|
| Nom | _…_ | _…_ | _…_ |
| 1. Collecte (en parallèle) | `src/eau/` → `eau_zones_hydro.parquet` | `src/agriculture/` → `parcelles_rpg_2023.parquet` | `src/pesticides/` → `pesticides.parquet` |
| 2. Jointure (une personne) | `src/zones_hydrographiques/` → `base_finale.parquet` | | |
| 3. Stats descriptives (en parallèle) | qualité de l'eau | surfaces et cultures | achats de pesticides |

Le croisement eau × champs × pesticides se fait à trois, puis une seule personne assemble `main.ipynb`.

**Avant de coder, lire [`docs/contrat_donnees.md`](docs/contrat_donnees.md)** : maille, colonnes et types de chaque livrable.
