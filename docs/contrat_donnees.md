# Contrat de données

Ce document fixe **ce que chaque partie doit livrer** à la fin de la collecte,
pour que les trois bases puissent être jointes sans retouche.
Toute modification du contrat se décide **à trois** et se note en bas de page.

## 1. Règles communes

| Règle | Valeur |
|---|---|
| Maille | **zone hydrographique × année** pour le croisement final (`base_finale`) ; les achats de pesticides sont au **département × année** |
| Territoire | France métropolitaine continentale : **94 départements, hors Corse** (`2A`, `2B`) et hors DROM |
| Période | **2013 – 2023** (achats de pesticides disponibles sur 2013-2023 ; le RPG 2023 sert pour toutes les années) |
| Format | Parquet, dans `data/processed/` |
| Partage | tout est recalculé par le code dans `main.ipynb`. Seuls les fichiers qui prennent plus de 5 minutes à calculer sont dans la release `donnees-v1`, lus avec `recuperer_release(nom)` : `parcelles_rpg_2023.parquet` et `parcelles_zones_hydro.parquet` (tirés de l'archive RPG de l'IGN). Les indices Hub'Eau, avec les coordonnées des stations, sont demandés à l'API (environ 1 min 15) |
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

L'ancienne liste `data/reference/molecules.csv` est supprimée : les pesticides suivis sont
les 10 molécules de la partie 3.B, attribuées aux zones hydrographiques (partie 5).

Nettoyage : ne garder que les indices qualifiés « corrects » (`code_qualification == "1"`)
et retirer la valeur codée `999` de l'IPR (`src/eau/nettoyer_indices.py`).
L'eau n'a pas de livrable au département : elle est agrégée à la zone hydrographique (`eau_zones_hydro.parquet`, partie 5).

## 3. Livrables

### A — Champs : `data/processed/parcelles_rpg_2023.parquet`

Clé : `id_parcelle` — **millésime RPG 2023 uniquement** : l'assolement change peu d'une année à
l'autre, la même photo sert pour toutes les années. Une ligne par parcelle des 94 départements,
sans les contours. Sert à lier les parcelles aux ventes de molécules.

| Colonne | Type | Description |
|---|---|---|
| `id_parcelle` | str | identifiant de la parcelle dans le RPG (`ID_PARCEL`) |
| `code_dep`, `nom_dep` | str | département de la parcelle |
| `surface_ha` | float | surface déclarée, en hectares |
| `code_culture` | str | code culture RPG (3 lettres) |
| `code_groupe`, `libelle_groupe` | str | groupe de cultures RPG (`"1"` à `"28"`) et son libellé |
| `categorie_culture` | str | `TA`, `PP`, `CP` ou `SB`, vide pour les surfaces non agricoles |

Construit par `src/agriculture/construire_parcelles_rpg.py` à partir de l'archive nationale du RPG 2023
de l'IGN (`RPG_2-2__GPKG_LAMB93_FXX_2023-01-01`) : chaque parcelle va au département qui contient
un point de sa surface ; les parcelles de Corse sont écartées. Le nettoyage
(`nettoyer_parcelles_rpg.py`) retire les doublons d'identifiant (aucun en 2023) et les parcelles
de surface nulle (environ 8 500 miettes de moins de 0,005 ha).
Dans la release (le calcul demande l'archive de 2,75 Go), lu avec `recuperer_release`.

### B — Pesticides : `data/processed/pesticides.parquet`

Clé : `code_dep`, `annee`, `substance`. Une ligne par département, année et molécule, pour les
**10 molécules suivies** (`MOLECULES`, dans `src/pesticides/constantes_pesticides.py`).

| Colonne | Type | Description |
|---|---|---|
| `code_dep`, `nom_dep` | str | département de l'acheteur |
| `annee` | int | année d'achat |
| `substance` | str | nom de la molécule (`cuivre` regroupe les 8 sels de cuivre de la BNV-D) |
| `quantite_kg` | float | quantité de substance active achetée, en kg (produits de biocontrôle et autres additionnés) |

Source : achats de produits phytosanitaires de la BNV-D **par département de l'acheteur**
(data.gouv.fr). Les valeurs du fichier sont en kg, même si sa description parle de tonnes.
Construit par `src/pesticides/preparer_pesticides.py`, qui retire la Corse (`2A`, `2B`) et les DROM.

## 4. Pesticides attribués aux cultures (en mémoire, pas de fichier)

Les achats d'une molécule dans un département sont répartis entre les groupes de cultures qui
l'utilisent (`MOLECULES_PAR_GROUPE`), au prorata de leur surface dans le département (RPG 2023
pour toutes les années). Détail du calcul : [`docs/repartition_pesticides.md`](repartition_pesticides.md).

Table des doses (`calculer_doses_pesticides_groupes`) — clé : `code_dep`, `annee`, `libelle_groupe`, `molecule`.

| Colonne | Type | Description |
|---|---|---|
| `code_dep` | str | département |
| `annee` | int | année d'achat |
| `libelle_groupe` | str | groupe de cultures qui utilise la molécule |
| `molecule` | str | une des 10 molécules |
| `dose_kg_ha` | float | kg de la molécule attribués à chaque hectare du groupe dans le département (0 si le département n'a aucune surface qui l'utilise) |

## 5. Croisement eau × cultures par zone hydrographique

Le département mélange des bassins très différents. Pour croiser l'eau et les cultures,
on passe donc par les 6 190 zones hydrographiques de la BD TOPAGE (`recuperer_zones_hydro`).
Les pesticides, achetés au département, passent par les doses de la partie 4 et par la part de chaque parcelle dans chaque zone.

### `stations_zones_hydro` (en mémoire, pas de fichier)

Clé : `code_station`. Colonnes : `code_station` (str), `code_zone` (str).
Chaque station va dans la zone qui la contient, ou dans la plus proche si elle est juste hors limites.

### `data/processed/eau_zones_hydro.parquet`

Clé : `code_zone`, `annee`. Une ligne par zone et par année où au moins une station de la zone a un indice.
Recalculé dans `main.ipynb` à partir de l'API Hub'Eau (pas dans la release).

| Colonne | Type | Description |
|---|---|---|
| `code_zone` | str | code de la zone hydrographique |
| `annee` | int | année des prélèvements (2013 à 2023) |
| `I2M2`, `IBD`, `IPR` | float | médiane, sur les stations de la zone, de la moyenne des mesures de chaque station dans l'année |
| `nb_stations` | int | nombre de stations de la zone ayant un indice cette année-là |

Produit par `src/eau/agreger_eau_zones_hydro.py` à partir des indices nettoyés et de `stations_zones_hydro`.

### `champs_zones_hydro` (en mémoire, pas de fichier)

Clé : `code_zone`, `code_groupe_culture`

| Colonne | Type | Description |
|---|---|---|
| `code_zone` | str | code de la zone hydrographique |
| `code_groupe_culture` | str | code du groupe de cultures RPG |
| `libelle_groupe_culture` | str | libellé du groupe |
| `surface_ha` | float | surface du groupe dans la zone, en hectares |

Produit par `src/zones_hydrographiques/agreger_champs_zones_hydro.py` à partir de `parcelles_zones_hydro` et de
`parcelles_rpg_2023` : chaque parcelle compte dans chaque zone qu'elle touche pour sa part de
surface déclarée.

### `data/processed/parcelles_zones_hydro.parquet`

Clé : `id_parcelle`, `code_zone`. Une ligne par parcelle du RPG 2023 et par zone qu'elle touche.

| Colonne | Type | Description |
|---|---|---|
| `id_parcelle` | str | identifiant de la parcelle (même clé que `parcelles_rpg_2023.parquet`) |
| `code_zone` | str | code de la zone hydrographique |
| `part` | float | part de la parcelle dans la zone : 1 si elle n'en touche qu'une, sinon aire du morceau / aire de la parcelle ; les parts d'une parcelle font 1 |

Produit par `src/zones_hydrographiques/associer_parcelles_zones_hydro.py` à partir des contours de l'archive IGN.
Dans la release (environ 25 minutes de calcul en plus de l'archive), lu avec `recuperer_release`. La release contient aussi les contours des parcelles de l'Essonne (`parcelles_rpg_2023_91.gpkg`, couche `PARCELLES_GRAPHIQUES`, colonne `ID_PARCEL`), pour rejouer ce calcul sur un département dans `main.ipynb`.

### `pesticides_zones_hydro` (en mémoire, pas de fichier)

Clé : `code_zone`, `annee`. Quantités des 10 molécules attribuées à la zone (kg de substance active), 2013 à 2023.

| Colonne | Type | Description |
|---|---|---|
| `code_zone` | str | code de la zone hydrographique |
| `annee` | int | année d'achat |
| `glyphosate_kg`, … | float | somme, sur les parcelles de la zone, de la quantité attribuée à la parcelle × sa part dans la zone |

Produit par `src/zones_hydrographiques/agreger_pesticides_zones_hydro.py` : les doses de la partie 4 multipliées par la
surface de chaque groupe de cultures de chaque département dans la zone (`parcelles_zones_hydro` × `parcelles_rpg_2023`),
ce qui revient à sommer la quantité de chaque parcelle × sa part dans la zone.

### `data/processed/base_finale.parquet`

Clé : `code_zone`, `annee`. Une ligne par ligne de `eau_zones_hydro.parquet` ; les parts de cultures (RPG 2023) sont les mêmes pour toutes les années d'une zone.
Produit par `src/zones_hydrographiques/fusionner_eau_cultures_pesticides.py`, qui fusionne `eau_zones_hydro`, `champs_zones_hydro` et `pesticides_zones_hydro`.

| Colonne | Type | Description |
|---|---|---|
| `code_zone`, `nom_zone` | str | zone hydrographique |
| `annee`, `I2M2`, `IBD`, `IPR`, `nb_stations` | | repris de `eau_zones_hydro.parquet` |
| `surface_zone_ha` | float | surface de la zone, en hectares |
| `part_agricole` | float | part de la zone en parcelles du RPG, en % (peut dépasser 100 % de quelques dixièmes sur le littoral, où des parcelles débordent du contour de la zone) |
| `part_groupe_1`, … | float | part de la zone occupée par chaque groupe de cultures, en % |
| `glyphosate_kg_ha`, … | float | pesticides attribués à la zone l'année de l'indice, en kg par hectare de zone (0 si la zone n'a pas de parcelle) |

Limite : la zone ne couvre que le bassin local. Pour une station sur un grand cours d'eau,
une partie de l'amont reste hors de la zone.

## 6. Points ouverts (à décider à trois)

Aucun.

## Historique des modifications

| Date | Modification | Validé par |
|---|---|---|
| | Version initiale | |
| 2026-10-27 | Eau : indices biologiques (I2M2, IBD, IPR) à la place des molécules ; suppression de `molecules.csv` | à valider |
| 2026-10-27 | Période élargie de 2015-2022 à 2013-2023 (période commune aux trois sources) | à valider |
| 2026-10-27 | Corse retirée du périmètre (RPG trop incomplet en Corse) | à valider |
| 2026-10-27 | Champs : RPG 2023 seul, clé `code_dep` × `code_groupe_culture`, jointure sur `code_dep` | à valider |
| 2026-11-06 | Ajout du croisement eau × cultures par zone hydrographique (`stations_zones`, `champs_zones`, `base_zones`) | à valider |
| 2026-11-10 | `champs_zones` : grandes parcelles partagées entre les zones qu'elles touchent, doublons du fichier national comptés une fois | à valider |
| 2026-11-10 | Tous les fichiers téléchargés et intermédiaires sur la release `donnees-v1`, via `telecharger_donnee` | à valider |
| 2026-11-10 | `champs_zones` : toutes les parcelles coupées selon les zones, à partir de l'archive RPG de l'IGN (remplace le point de référence) | à valider |
| 2026-11-23 | Champs : abandon du WFS ; `champs.parquet` aussi calculé à partir de l'archive RPG 2023 de l'IGN | à valider |
| 2026-11-23 | Eau : ajout de `eau_zones.parquet` (indices par zone hydrographique), seule base eau sur la release ; stations et indices Hub'Eau demandés à l'API, `stations_zones` calculé en mémoire | à valider |
| 2026-11-23 | Eau : suppression de `eau.parquet` (département × année) ; l'eau n'est plus agrégée qu'à la zone hydrographique, `base_finale` croise pesticides et champs | à valider |
| 2026-11-23 | Eau : `eau_zones` et `base_zones` passent à une ligne par zone et par année (clé `code_zone`, `annee`) ; plusieurs mesures d'une station la même année sont moyennées | à valider |
| 2026-11-24 | RPG 2023 seul (2013 abandonné) ; `champs.parquet` supprimé, remplacé par `parcelles_rpg_2023.parquet` (sans la Corse) | à valider |
| 2026-11-24 | Pesticides par zone : `parcelles_zones` et `pesticides_zones` ; `base_zones` gagne les 10 molécules en kg/ha de zone | à valider |
| 2026-11-24 | Pesticides : `pesticides.parquet` décrit tel qu'il est produit (achats par département, 10 molécules, colonnes `code_dep`, `nom_dep`, `quantite_kg`) ; `base_finale` retiré (jamais produit), remplacé par la table des doses ; maille commune = zone hydrographique × année | à valider |
| 2026-11-24 | `champs_zones` calculé à partir de `parcelles_zones` ; `pesticides_zones` à partir des doses par département × groupe (plus de fichiers par parcelle) | à valider |
| 2026-11-24 | Noms : suffixe `_zones` remplacé par `_zones_hydro` (`eau_zones_hydro`, `parcelles_zones_hydro`, `champs_zones_hydro`, `pesticides_zones_hydro`, `stations_zones_hydro`) ; `base_zones` renommé `base_finale` ; `champs_zones_hydro` et `pesticides_zones_hydro` calculés en mémoire, plus déposés sur la release | à valider |
| 2026-11-24 | Release réduite aux fichiers de plus de 5 minutes de calcul (`parcelles_rpg_2023`, `parcelles_zones_hydro`), lus avec `recuperer_release` ; `telecharger_donnee` supprimée. Hub'Eau : coordonnées des stations tirées de l'API des indices (plus d'appel aux stations), 8 départements à la fois | à valider |
