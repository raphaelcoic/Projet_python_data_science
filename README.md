# Eau et agriculture : qualité des eaux et usage des pesticides

Projet Python pour la data science (ENSAE).

**Problématique :** _à formuler_

## Sources de données

| Données | Source |
|---|---|
| Qualité des cours d'eau | [Hub'Eau – Qualité des cours d'eau](https://hubeau.eaufrance.fr/page/api-qualite-cours-deau) |
| Qualité des nappes | [Hub'Eau – Qualité des nappes](https://hubeau.eaufrance.fr/page/api-qualite-nappes) |
| Ventes de pesticides | BNV-D (data.gouv.fr) |
| Parcelles agricoles | RPG (IGN) |
| Fonds de carte | ADMIN-EXPRESS (IGN) / cartiflette |

## Organisation du dépôt

```
├── main.ipynb              # Notebook FINAL : raconte l'analyse, appelle les fonctions de src/
├── src/                    # Code réutilisable : un fichier = une fonction
│   ├── hubeau/             #   API Hub'Eau (cours d'eau, nappes)
│   ├── pesticides/         #   ventes de pesticides (BNV-D)
│   ├── agriculture/        #   parcelles / surfaces agricoles (RPG)
│   ├── geo/                #   geopandas : CRS, jointures spatiales
│   ├── nettoyage/          #   nettoyage, agrégation, fusion
│   └── visualisation/      #   graphiques et cartes
├── notebooks/exploration/  # Brouillons perso (un par personne / sujet)
├── data/                   # Non versionné (voir .gitignore)
│   ├── raw/                #   données brutes téléchargées
│   ├── processed/          #   données nettoyées
│   └── geo/                #   shapefiles / fonds de carte
├── output/figures/         # Figures exportées
└── requirements.txt
```

**Le flux :** API / fichiers → `data/raw/` → nettoyage → `data/processed/` → analyse et cartes dans `main.ipynb`.

## Installation

```bash
pip install -r requirements.txt
```

## Règles de travail en groupe

- **Notebooks d'exploration** : nommés `initiales_sujet.ipynb` (ex. `rc_hubeau_stations.ipynb`). Chacun ne modifie que les siens, ce qui évite les conflits git sur les notebooks.
- **Un fichier = une fonction** : quand un bout de code marche, il devient une fonction dans son propre fichier, nommé comme elle, dans le bon dossier de `src/`. Exemple : la fonction `recuperer_stations` va dans `src/hubeau/recuperer_stations.py` et s'importe avec `from src.hubeau.recuperer_stations import recuperer_stations`.
- Lancer Jupyter depuis la racine du dépôt pour que les imports `src...` fonctionnent.
- **`main.ipynb`** : une seule personne l'édite à la fois (prévenez le groupe).
- **Branches** : une branche par tâche (ex. `hubeau-pagination`), puis une pull request vers `main`.
- **Données** : jamais commitées. Tout doit pouvoir être re-téléchargé par le code.
- Avant de commit un notebook, vider les sorties lourdes (*Kernel → Restart & Clear Output*) si possible.

## Répartition

| Membre | Partie |
|---|---|
| _…_ | Hub'Eau (cours d'eau + nappes) |
| _…_ | Pesticides + agriculture |
| _…_ | Géographie + visualisations |
