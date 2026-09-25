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
| `code_sandre` | texte (`"1506"`, pas `1506`) |
| Valeurs manquantes | `NaN` = pas de donnée ; `0` = mesuré / compté et nul. Ne jamais remplacer un `NaN` par `0`. |
| Unicité | une seule ligne par clé (voir chaque table) ; à vérifier avec `df.duplicated(subset=cle).sum() == 0` |

## 2. Molécules étudiées

Liste de référence : [`data/reference/molecules.csv`](../data/reference/molecules.csv) (versionné dans git).

| Colonne | Description | Rempli par |
|---|---|---|
| `molecule` | nom usuel | fixé |
| `molecule_mere` | substance vendue dont elle provient (= `molecule` si ce n'est pas un métabolite) | fixé |
| `code_sandre` | code paramètre SANDRE utilisé par Hub'Eau | **A** |
| `cas` | numéro CAS utilisé dans la BNV-D | **C** |

Les métabolites (AMPA, ESA-métolachlore, déséthylatrazine) sont mesurés dans l'eau
mais ne sont pas vendus : on les rattache aux ventes de leur `molecule_mere`.

## 3. Livrables

### A — Eau : `data/processed/eau.parquet`

Clé : `code_dep`, `annee`, `milieu`, `code_sandre`

| Colonne | Type | Description |
|---|---|---|
| `code_dep` | str | département de la station |
| `annee` | int | année du prélèvement |
| `milieu` | str | `"riviere"` ou `"nappe"` |
| `code_sandre` | str | molécule (voir `molecules.csv`) |
| `nb_stations` | int | nombre de stations ayant au moins une analyse |
| `nb_analyses` | int | nombre d'analyses |
| `nb_quantifications` | int | analyses où la molécule est quantifiée (`code_remarque == 1`) |
| `taux_quantification` | float | `nb_quantifications / nb_analyses` |
| `concentration_moyenne_ugl` | float | moyenne en µg/L, **analyses non quantifiées comptées à 0** |
| `concentration_max_ugl` | float | maximum en µg/L |
| `nb_depassements` | int | analyses > 0,1 µg/L (norme eau potable par pesticide) |

Points d'attention : ne garder que les résultats en µg/L (vérifier l'unité),
agréger les stations au département avant de livrer.

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

- `eau` × `molecules.csv` (via `code_sandre`) → ajoute `molecule_mere`
- × `pesticides` (via `cas` de la `molecule_mere`, `code_dep`, `annee`) → ajoute `quantite_kg`
- × `champs` passé en colonnes (une colonne de surface par groupe de cultures + `surface_agricole_ha` totale) via `code_dep`, `annee`

Contrôles obligatoires : nombre de lignes avant / après chaque `merge`,
et départements présents d'un côté mais pas de l'autre (`indicator=True`).

## Historique des modifications

| Date | Modification | Validé par |
|---|---|---|
| | Version initiale | |
