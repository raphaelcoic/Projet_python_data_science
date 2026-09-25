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
├── src/                    # Code réutilisable (fonctions uniquement)
│   ├── hubeau.py           #   API Hub'Eau (cours d'eau, nappes)
│   ├── pesticides.py       #   ventes de pesticides (BNV-D)
│   ├── agriculture.py      #   parcelles / surfaces agricoles (RPG)
│   ├── geo.py              #   geopandas : CRS, jointures spatiales
│   ├── nettoyage.py        #   nettoyage, agrégation, fusion
│   └── visualisation.py    #   graphiques et cartes
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
- **Quand un bout de code marche**, il passe dans une fonction de `src/`, puis il est appelé depuis `main.ipynb`.
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
