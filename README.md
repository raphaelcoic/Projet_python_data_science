# Eau et agriculture : qualité des eaux et usage des pesticides

Projet Python pour la data science (ENSAE).

**Problématique :** _à formuler_

## Sources de données

| Données | Source |
|---|---|
| Indices biologiques des cours d'eau (I2M2, IBD, IPR) | [Hub'Eau – Hydrobiologie](https://hubeau.eaufrance.fr/page/api-hydrobiologie) |
| Stations hydrobiologiques (coordonnées) | [Hub'Eau – Hydrobiologie](https://hubeau.eaufrance.fr/page/api-hydrobiologie) |
| Zones hydrographiques | [BD TOPAGE](https://www.sandre.eaufrance.fr/atlas/srv/fre/catalog.search#/home) (Sandre), via son WFS |
| Achats de produits phytosanitaires par département | [CSV data.gouv.fr](https://www.data.gouv.fr/api/1/datasets/r/6f664bd4-f27d-4e33-8ca7-c197c6adf217) (BNV-D, quantités en kg) |
| Parcelles agricoles | [RPG](https://www.data.gouv.fr/datasets/rpg) (IGN / ASP), archive nationale 2023 de l'IGN |
| Fonds de carte | [france-geojson](https://github.com/gregoiredavid/france-geojson) |

## Organisation du dépôt

```
├── main.ipynb              # Notebook FINAL : raconte l'analyse, appelle les fonctions de src/
├── src/                    # Code réutilisable : un fichier = une fonction
│   ├── hubeau/             #   partie eau, de l'API Hub'Eau à eau_zones.parquet (nettoyage, rattachement aux zones, agrégation)
│   ├── pesticides/         #   achats de pesticides
│   ├── agriculture/        #   parcelles agricoles du RPG (archive IGN) ; constantes_rpg.py = libellés des cultures
│   ├── geo/                #   périmètre (94 départements, hors Corse) et fonds de carte
│   ├── agregation/         #   les 10 molécules, leurs groupes de cultures et les doses par hectare (voir son README)
│   ├── nettoyage/          #   nettoyage, agrégation, fusion
│   ├── visualisation/      #   graphiques et cartes
│   └── telecharger_donnee.py #  récupère un fichier déjà calculé depuis la release
├── notebooks/
│   ├── README.md           #   index des notebooks (qui, quoi)
│   └── exploration/        #   brouillons perso (un par personne / sujet)
├── data/
│   ├── raw/                #   données brutes téléchargées (non versionné)
│   ├── processed/          #   livrables du contrat de données (non versionné)
│   └── geo/                #   shapefiles / fonds de carte (non versionné)
├── docs/contrat_donnees.md # Format des livrables de chaque partie
└── requirements.txt
```

**Le flux :** API / fichiers → `data/raw/` → nettoyage → `data/processed/` → analyse et cartes dans `main.ipynb`.

## Installation

Python 3.9 ou plus récent.

```bash
pip install -r requirements.txt
```

## Récupérer les données déjà calculées

Les fichiers de `main.ipynb` sont sur la release [`donnees-v1`](https://github.com/raphaelcoic/Projet_python_data_science/releases/tag/donnees-v1). Pour la partie eau, seule la table finale `eau_zones.parquet` (indices agrégés par zone hydrographique) y est : les stations et les indices sont demandés directement à l'API Hub'Eau. Chaque fichier de la release passe par `telecharger_donnee(chemin, creer)`, qui suit cet ordre :

1. Si le fichier existe en local, il est utilisé.
2. Sinon, il est téléchargé depuis la release, sans compte GitHub.
3. S'il n'est pas non plus dans la release, il est créé avec `creer()`, puis déposé dans la release avec `gh`. Il faut avoir les droits d'écriture sur le dépôt.

```python
from src.telecharger_donnee import telecharger_donnee

zones = gpd.read_parquet(telecharger_donnee("data/geo/zones_hydro.parquet", recuperer_zones_hydro))
eau_zones = pd.read_parquet(telecharger_donnee("data/processed/eau_zones.parquet", lambda: construire_eau_zones(zones)))
parcelles_zones = pd.read_parquet(telecharger_donnee("data/processed/parcelles_zones.parquet", lambda: associer_parcelles_zones(recuperer_rpg_ign(), zones)))
```

L'archive du RPG de l'IGN (2,75 Go) n'est pas dans la release : elle dépasse la limite de 2 Go par fichier de GitHub, et l'IGN l'héberge déjà. `recuperer_rpg_ign()` la télécharge dans `data/raw/rpg_ign/`. La table à la parcelle qui en est tirée, sans les contours (`parcelles_rpg_2023.parquet`), est dans la release.

Les noms de fichiers doivent être uniques dans la release. Si le code qui produit un fichier change, passez `recalculer=True` : le fichier est recréé, puis remplace sa copie locale et sa copie dans la release.

## Régénérer les données

| Partie | Commande | Produit |
|---|---|---|
| Eau | `recuperer_toutes_stations_hydrobio()`, `recuperer_tous_indices()` (API Hub'Eau, plusieurs minutes) | en mémoire |
| Champs | `construire_parcelles_rpg(recuperer_rpg_ign(), recuperer_departements())` (archive RPG 2023 de l'IGN, 2,75 Go ; une ligne par parcelle, pour lier aux ventes de molécules) | `data/processed/parcelles_rpg_2023.parquet` |
| Pesticides | `preparer_pesticides()` (télécharge le CSV dans `data/raw/`, garde les 10 molécules) | `data/processed/pesticides.parquet` |
| Zones | `recuperer_zones_hydro()` | `data/geo/zones_hydro.parquet` |
| | `rattacher_stations_zones(stations, zones)` | en mémoire (`stations_zones`) |
| | `construire_eau_zones(zones)` : appelle l'API, nettoie, rattache aux zones et agrège (seul fichier eau de la release) | `data/processed/eau_zones.parquet` |
| | `associer_parcelles_zones(recuperer_rpg_ign(), zones)` (archive RPG 2023 de l'IGN, environ 25 min) | `data/processed/parcelles_zones.parquet` |
| | `agreger_champs_zones(parcelles, parcelles_zones)` (quelques secondes) | `data/processed/champs_zones.parquet` |
| | `agreger_pesticides_zones(calculer_doses_pesticides_groupes(parcelles, pesticides), parcelles, parcelles_zones)` (quelques secondes) | `data/processed/pesticides_zones.parquet` |
| | `construire_base_zones(eau_zones, champs_zones, pesticides_zones, zones)` | `data/processed/base_zones.parquet` |

## Règles de travail en groupe

- **Notebooks d'exploration** : tous dans `notebooks/exploration/`, nommés `initiales_sujet.ipynb` (ex. `rc_hubeau_stations.ipynb`), et listés dans `notebooks/README.md`. Chacun ne modifie que les siens, ce qui évite les conflits git sur les notebooks.
- **Un fichier = une fonction** : quand un bout de code marche, il devient une fonction dans son propre fichier, nommé comme elle, dans le bon dossier de `src/`. Exemple : la fonction `recuperer_indices` va dans `src/hubeau/recuperer_indices.py` et s'importe avec `from src.hubeau.recuperer_indices import recuperer_indices`.
- **Chemins** : le code utilise des chemins relatifs à la racine du dépôt (`data/...`). Les notebooks de `notebooks/exploration/` commencent donc par une cellule qui se place à la racine (`os.chdir`) ; les scripts se lancent depuis la racine avec `python -m src.dossier.fichier`.
- **`main.ipynb`** : une seule personne l'édite à la fois (prévenez le groupe).
- **Branches** : une branche par tâche (ex. `hubeau-pagination`), puis une pull request vers `main`.
- **Données** : jamais commitées. Tout doit pouvoir être re-téléchargé par le code ; la release ne sert que de raccourci.
- Avant de commit un notebook, vider les sorties lourdes (*Kernel → Restart & Clear Output*) si possible.

## Répartition

| Étape | Membre A — Eau | Membre B — Champs | Membre C — Pesticides |
|---|---|---|---|
| Nom | _…_ | _…_ | _…_ |
| 1. Collecte (en parallèle) | `src/hubeau/` → `eau_zones.parquet` | `src/agriculture/` → `parcelles_rpg_2023.parquet` | `src/pesticides/` → `pesticides.parquet` |
| 2. Jointure (une personne) | `src/nettoyage/` → `base_zones.parquet` | | |
| 3. Stats descriptives (en parallèle) | qualité de l'eau | surfaces et cultures | achats de pesticides |

Le croisement eau × champs × pesticides se fait à trois, puis une seule personne assemble `main.ipynb`.

**Avant de coder, lire [`docs/contrat_donnees.md`](docs/contrat_donnees.md)** : maille, colonnes et types de chaque livrable.
