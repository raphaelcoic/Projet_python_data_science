# Contrat de données

Ce document fixe **ce que chaque partie doit livrer** à la fin de la collecte,
pour que les trois bases puissent être jointes sans retouche.
Toute modification du contrat se décide **à trois** et se note en bas de page.

## 1. Règles communes

| Règle | Valeur |
|---|---|
| Maille | **département × année** |
| Territoire | France métropolitaine continentale : **94 départements, hors Corse** (`2A`, `2B`) et hors DROM |
| Période | **2013 – 2023** (achats de pesticides disponibles sur 2013-2023, millésimes RPG 2013 et 2023) |
| Format | Parquet, dans `data/processed/` |
| Partage | les fichiers sont lus avec `telecharger_donnee(chemin, creer)` (local, sinon release `donnees-v1`, sinon créé puis déposé ; `recalculer=True` pour le régénérer). Pour l'eau, seul `eau_zones.parquet` est dans la release ; les stations et indices Hub'Eau sont demandés à l'API |
| Noms de colonnes | `snake_case`, sans accents, unité en suffixe (`_kg`, `_ha`, `_ugl`) |
| `code_dep` | **texte** sur 2 caractères : `"01"`, `"75"` (jamais `1`) |
| `annee` | entier (`int`) |
| Valeurs manquantes | `NaN` = pas de donnée ; `0` = mesuré / compté et nul. Ne jamais remplacer un `NaN` par `0`. |
| Unicité | une seule ligne par clé (voir chaque table) ; à vérifier avec `df.duplicated(subset=cle).sum() == 0` |

## 2. Indicateurs de qualité de l'eau

La partie Eau suit trois **indices biologiques** des cours d'eau (Hub'Eau Hydrobiologie)
plutôt que les concentrations de molécules : ils résument l'état écologique et sont
disponibles partout sur 2013-2023.

Attention : le réseau de suivi I2M2 double en 2015 (environ 2 300 indices par an avant,
4 000 après). Pour une évolution dans le temps, comparer à stations constantes.

| Indice | Code SANDRE | Organismes | Sens |
|---|---|---|---|
| I2M2 | 7613 | invertébrés | élevé = bonne qualité |
| IBD | 5856 | diatomées | élevé = bonne qualité |
| IPR | 7036 | poissons | **bas** = bonne qualité |

L'ancienne liste `data/reference/molecules.csv` est supprimée : la jointure avec les
pesticides se fait sur `code_dep` × `annee` (quantités totales), plus par molécule.

Nettoyage : ne garder que les indices qualifiés « corrects » (`code_qualification == "1"`)
et retirer la valeur codée `999` de l'IPR (`src/hubeau/nettoyer_indices.py`).
L'eau n'a pas de livrable au département : elle est agrégée à la zone hydrographique (`eau_zones.parquet`, partie 5).

## 3. Livrables

### A — Champs : `data/processed/champs.parquet`

Clé : `code_dep`, `code_groupe_culture` — **millésime RPG 2023 uniquement** : l'assolement d'un
département change peu d'une année à l'autre, la même photo sert pour toutes les années.

| Colonne | Type | Description |
|---|---|---|
| `code_dep` | str | département de la parcelle |
| `code_groupe_culture` | str | code du groupe de cultures RPG (`"1"` à `"28"`) |
| `libelle_groupe_culture` | str | libellé (blé tendre, maïs grain et ensilage, …) |
| `surface_ha` | float | surface totale du groupe dans le département, en hectares |

Produit par `src/nettoyage/agreger_champs.py` à partir de `data/processed/parcelles_rpg_2023.parquet`,
une ligne par parcelle de l'archive nationale du RPG 2023 de l'IGN (`RPG_2-2__GPKG_LAMB93_FXX_2023-01-01`),
construite par `src/agriculture/tabuler_parcelles_rpg.py` : chaque parcelle va au département qui contient
un point de sa surface. On somme ensuite la surface déclarée par département et groupe de cultures.

#### Table intermédiaire : `data/processed/parcelles_rpg_2023.parquet`

Clé : `id_parcelle`. Une ligne par parcelle, Corse comprise, sans les contours. Sert aussi à
lier les parcelles aux ventes de molécules.

| Colonne | Type | Description |
|---|---|---|
| `id_parcelle` | str | identifiant de la parcelle dans le RPG (`ID_PARCEL`) |
| `code_dep`, `nom_dep` | str | département de la parcelle |
| `surface_ha` | float | surface déclarée, en hectares |
| `code_culture` | str | code culture RPG (3 lettres) |
| `code_groupe`, `libelle_groupe` | str | groupe de cultures RPG (`"1"` à `"28"`) et son libellé |
| `categorie_culture` | str | `TA`, `PP`, `CP` ou `SB`, vide pour les surfaces non agricoles |

### B — Pesticides : `data/processed/pesticides.parquet`

Clé : `code_dep`, `annee`, `cas`

| Colonne | Type | Description |
|---|---|---|
| `code_dep` | str | département de l'acheteur |
| `annee` | int | année d'achat |
| `cas` | str | numéro CAS de la substance |
| `substance` | str | nom de la substance |
| `quantite_kg` | float | quantité de substance active achetée, en kg |

Points d'attention : utiliser les **achats par code postal de l'acheteur**
(plus proche du lieu d'usage que les ventes, localisées chez le distributeur),
puis passer du code postal au département. Piège : les codes postaux `20xxx`
correspondent à la Corse, **à exclure** (hors périmètre), pas à un département `"20"`.
Garder **toutes** les substances (utile pour les totaux), pas seulement la liste de référence.

## 4. Jointure : `data/processed/base_finale.parquet`

Réalisée dans `src/nettoyage/` une fois les deux livrables prêts.

- `pesticides` sommé par département et année (`quantite_kg` totale) via `code_dep`, `annee`
- × `champs` passé en colonnes (une colonne de surface par groupe de cultures + `surface_agricole_ha` totale) via `code_dep` seulement (RPG 2023 pour toutes les années)

Contrôles obligatoires : nombre de lignes avant / après chaque `merge`,
et départements présents d'un côté mais pas de l'autre (`indicator=True`).

## 5. Croisement eau × cultures par zone hydrographique

Le département mélange des bassins très différents. Pour croiser l'eau et les cultures,
on passe donc par les 6 190 zones hydrographiques de la BD TOPAGE (`data/geo/zones_hydro.parquet`).
`champs.parquet` reste au département pour le croisement avec les pesticides.

### `stations_zones` (en mémoire, pas de fichier)

Clé : `code_station`. Colonnes : `code_station` (str), `code_zone` (str).
Chaque station va dans la zone qui la contient, ou dans la plus proche si elle est juste hors limites.

### `data/processed/eau_zones.parquet`

Clé : `code_zone`, `annee`. Une ligne par zone et par année où au moins une station de la zone a un indice.
**Seule base de la partie eau déposée sur la release.**

| Colonne | Type | Description |
|---|---|---|
| `code_zone` | str | code de la zone hydrographique |
| `annee` | int | année des prélèvements (2013 à 2023) |
| `I2M2`, `IBD`, `IPR` | float | médiane, sur les stations de la zone, de la moyenne des mesures de chaque station dans l'année |
| `nb_stations` | int | nombre de stations de la zone ayant un indice cette année-là |

Produit par `src/hubeau/agreger_eau_zones.py` à partir des indices nettoyés et de `stations_zones`.

### `data/processed/champs_zones.parquet`

Clé : `code_zone`, `code_groupe_culture`

| Colonne | Type | Description |
|---|---|---|
| `code_zone` | str | code de la zone hydrographique |
| `code_groupe_culture` | str | code du groupe de cultures RPG |
| `libelle_groupe_culture` | str | libellé du groupe |
| `surface_ha` | float | surface du groupe dans la zone, en hectares |

Parcelles : archive nationale du RPG 2023 de l'IGN (`RPG_2-2__GPKG_LAMB93_FXX_2023-01-01`),
avec le contour de chaque parcelle. Une parcelle qui touche une seule
zone y va entière ; une parcelle qui en touche plusieurs est coupée selon leurs limites, et sa
surface déclarée est répartie au prorata de chaque morceau.

### `data/processed/base_zones.parquet`

Clé : `code_zone`, `annee`. Une ligne par ligne de `eau_zones.parquet` ; les parts de cultures (RPG 2023) sont les mêmes pour toutes les années d'une zone.

| Colonne | Type | Description |
|---|---|---|
| `code_zone`, `nom_zone` | str | zone hydrographique |
| `annee`, `I2M2`, `IBD`, `IPR`, `nb_stations` | | repris de `eau_zones.parquet` |
| `surface_zone_ha` | float | surface de la zone, en hectares |
| `part_agricole` | float | part de la zone en parcelles du RPG, en % |
| `part_groupe_1`, … | float | part de la zone occupée par chaque groupe de cultures, en % |

Limite : la zone ne couvre que le bassin local. Pour une station sur un grand cours d'eau,
une partie de l'amont reste hors de la zone.

## 6. Points ouverts (à décider à trois)

- **Pesticides** : la source utilisée (achats par département, colonne `valeur`) n'est pas
  celle prévue (achats BNV-D par code postal, en kg, avec `cas`) ; unité et clé à fixer.

## Historique des modifications

| Date | Modification | Validé par |
|---|---|---|
| | Version initiale | |
| 2026-10-27 | Eau : indices biologiques (I2M2, IBD, IPR) à la place des molécules ; suppression de `molecules.csv` | à valider |
| 2026-10-27 | Période élargie de 2015-2022 à 2013-2023 (période commune aux trois sources) | à valider |
| 2026-10-27 | Corse retirée du périmètre (RPG trop incomplet en Corse, voir `tf_rpg_valeurs_manquantes_corse.ipynb`) | à valider |
| 2026-10-27 | Champs : RPG 2023 seul, clé `code_dep` × `code_groupe_culture`, jointure sur `code_dep` | à valider |
| 2026-11-06 | Ajout du croisement eau × cultures par zone hydrographique (`stations_zones`, `champs_zones`, `base_zones`) | à valider |
| 2026-11-10 | `champs_zones` : grandes parcelles partagées entre les zones qu'elles touchent, doublons du fichier national comptés une fois | à valider |
| 2026-11-10 | Tous les fichiers téléchargés et intermédiaires sur la release `donnees-v1`, via `telecharger_donnee` | à valider |
| 2026-11-10 | `champs_zones` : toutes les parcelles coupées selon les zones, à partir de l'archive RPG de l'IGN (remplace le point de référence) | à valider |
| 2026-11-23 | Champs : abandon du WFS ; `champs.parquet` aussi calculé à partir de l'archive RPG 2023 de l'IGN | à valider |
| 2026-11-23 | Eau : ajout de `eau_zones.parquet` (indices par zone hydrographique), seule base eau sur la release ; stations et indices Hub'Eau demandés à l'API, `stations_zones` calculé en mémoire | à valider |
| 2026-11-23 | Eau : suppression de `eau.parquet` (département × année) ; l'eau n'est plus agrégée qu'à la zone hydrographique, `base_finale` croise pesticides et champs | à valider |
| 2026-11-23 | Eau : `eau_zones` et `base_zones` passent à une ligne par zone et par année (clé `code_zone`, `annee`) ; plusieurs mesures d'une station la même année sont moyennées | à valider |
