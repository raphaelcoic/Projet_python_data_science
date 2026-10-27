# Contrat de données

Ce document fixe **ce que chaque partie doit livrer** à la fin de la collecte,
pour que les trois bases puissent être jointes sans retouche.
Toute modification du contrat se décide **à trois** et se note en bas de page.

## 1. Règles communes

| Règle | Valeur |
|---|---|
| Maille | **département × année** |
| Territoire | France métropolitaine (96 départements, Corse = `2A` et `2B`) |
| Période | **2015 – 2022** (début du RPG au format actuel, fin des ventes BNV-D disponibles) |
| Format | Parquet, dans `data/processed/` |
| Noms de colonnes | `snake_case`, sans accents, unité en suffixe (`_kg`, `_ha`, `_ugl`) |
| `code_dep` | **texte** sur 2 caractères : `"01"`, `"2A"`, `"75"` (jamais `1`) |
| `annee` | entier (`int`) |
| Valeurs manquantes | `NaN` = pas de donnée ; `0` = mesuré / compté et nul. Ne jamais remplacer un `NaN` par `0`. |
| Unicité | une seule ligne par clé (voir chaque table) ; à vérifier avec `df.duplicated(subset=cle).sum() == 0` |

## 2. Indicateurs de qualité de l'eau

La partie Eau suit trois **indices biologiques** des cours d'eau (Hub'Eau Hydrobiologie)
plutôt que les concentrations de molécules : ils résument l'état écologique et sont
disponibles partout sur 2015-2022.

| Indice | Code SANDRE | Organismes | Sens |
|---|---|---|---|
| I2M2 | 7613 | invertébrés | élevé = bonne qualité |
| IBD | 5856 | diatomées | élevé = bonne qualité |
| IPR | 7036 | poissons | **bas** = bonne qualité |

L'ancienne liste `data/reference/molecules.csv` est supprimée : la jointure avec les
pesticides se fait sur `code_dep` × `annee` (quantités totales), plus par molécule.

## 3. Livrables

### A — Eau : `data/processed/eau.parquet`

Clé : `code_dep`, `annee`, `indice`

| Colonne | Type | Description |
|---|---|---|
| `code_dep` | str | département de la station |
| `annee` | int | année du prélèvement |
| `indice` | str | `"I2M2"`, `"IBD"` ou `"IPR"` |
| `nb_stations` | int | nombre de stations ayant au moins un indice |
| `nb_prelevements` | int | nombre d'indices calculés |
| `valeur_moyenne` | float | moyenne de l'indice sur les prélèvements |
| `valeur_mediane` | float | médiane de l'indice sur les prélèvements |

Points d'attention : ne garder que les indices qualifiés « corrects » (`code_qualification == "1"`)
et retirer la valeur codée `999` de l'IPR (`src/nettoyage/nettoyer_indices.py`).

### B — Champs : `data/processed/champs.parquet`

Clé : `code_dep`, `annee`, `code_groupe_culture`

| Colonne | Type | Description |
|---|---|---|
| `code_dep` | str | département de la parcelle |
| `annee` | int | année du RPG |
| `code_groupe_culture` | str | code du groupe de cultures RPG |
| `libelle_groupe_culture` | str | libellé (blé tendre, maïs grain et ensilage, …) |
| `surface_ha` | float | surface totale du groupe dans le département, en hectares |

Points d'attention : le RPG est très lourd, travailler département par département
et ne garder que les colonnes utiles ; livrer des surfaces, **pas de géométries**.

### C — Pesticides : `data/processed/pesticides.parquet`

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
correspondent à la Corse (`2A` ou `2B`), pas à un département `"20"`.
Garder **toutes** les substances (utile pour les totaux), pas seulement la liste de référence.

## 4. Jointure : `data/processed/base_finale.parquet`

Réalisée dans `src/nettoyage/` une fois les trois livrables prêts.

- `eau` passé en colonnes (une colonne par indice) via `code_dep`, `annee`
- × `pesticides` sommé par département et année (`quantite_kg` totale) via `code_dep`, `annee`
- × `champs` passé en colonnes (une colonne de surface par groupe de cultures + `surface_agricole_ha` totale) via `code_dep`, `annee`

Contrôles obligatoires : nombre de lignes avant / après chaque `merge`,
et départements présents d'un côté mais pas de l'autre (`indicator=True`).

## 5. Points ouverts (à décider à trois)

- **Période** : le contrat dit 2015-2022, mais le RPG est téléchargé pour 2013 et 2023
  (2023 retenue comme année de référence) et les achats de pesticides couvrent 2013-2023.
- **Corse** : le contrat inclut `2A` et `2B`, mais les fichiers RPG nationaux l'excluent
  (catégories de culture trop souvent manquantes, voir `tf_rpg_valeurs_manquantes_corse.ipynb`).
- **Champs** : `champs.parquet` (département × année × groupe de cultures) n'est pas encore
  produit ; les fichiers RPG actuels sont à la parcelle.
- **Pesticides** : la source utilisée (achats par département, colonne `valeur`) n'est pas
  celle prévue (achats BNV-D par code postal, en kg, avec `cas`) ; unité et clé à fixer.

## Historique des modifications

| Date | Modification | Validé par |
|---|---|---|
| | Version initiale | |
| 2026-10-27 | Eau : indices biologiques (I2M2, IBD, IPR) à la place des molécules ; suppression de `molecules.csv` | à valider |
