# Pipeline d'agrégation : Parcelles RPG 2023 × Achats de pesticides (2013–2023)

Ce sous-module (`src/agregation/parcelles_pesticides/`) croise les parcelles agricoles du **RPG 2023**, les **achats départementaux de produits phytosanitaires (BNV-D, 2013–2023)** et la **table de correspondance groupes de cultures × molécules** afin d'estimer, pour chaque parcelle et chaque année, la quantité (en **kg de substance active**) des **10 molécules clés** attribuée à cette parcelle.

Pour éviter de manipuler un monolithe de plus de 107 millions de lignes en mémoire, le pipeline produit **une table Parquet par année** (`parcelles_pesticides_2013.parquet` à `parcelles_pesticides_2023.parquet`), générée en lecture/écriture par lots (*streaming*).

---

## 1. Ordre d'exécution du pipeline complet

Toutes les commandes ci-dessous s'exécutent **depuis la racine du dépôt**.

### Vue d'ensemble de la chaîne

```text
1. Parcelles RPG 2023        ──► data/processed/parcelles_rpg_2023.parquet
2. Achats de pesticides      ──► data/raw/...csv ──► data/processed/pesticides.parquet
3. Correspondance cultures   ──► data/processed/correspondance_groupes_molecules.csv
        │
        ▼
4. Pipeline d'agrégation (src/agregation/parcelles_pesticides/) :
   a. charger_matrice_correspondance.py       (matrice binaire 23 × 10)
   b. calculer_doses_pesticides_groupes.py    ──► data/processed/doses_pesticides_groupes.parquet
   c. construire_parcelles_pesticides_annee.py (appelé pour chaque année par l'orchestrateur)
   d. construire_parcelles_pesticides.py      ──► data/processed/parcelles_pesticides/parcelles_pesticides_<annee>.parquet
```

### Exécution pas à pas (de zéro)

#### Étape 1 — Récupérer `data/processed/parcelles_rpg_2023.parquet`
Télécharge le fichier pré-calculé depuis la release GitHub `donnees-v1` (ou le recalcule depuis l'archive IGN via `src/agriculture/construire_parcelles_rpg.py` s'il n'y est pas) :

```bash
python -c "from src.telecharger_donnee import telecharger_donnee; from src.agriculture.construire_parcelles_rpg import construire_parcelles_rpg; from src.agriculture.recuperer_rpg_ign import recuperer_rpg_ign; from src.geo.recuperer_departements import recuperer_departements; telecharger_donnee('data/processed/parcelles_rpg_2023.parquet', lambda: construire_parcelles_rpg(recuperer_rpg_ign(), recuperer_departements()))"
```

#### Étape 2 — Télécharger et préparer `data/processed/pesticides.parquet`
Appelle `src/pesticides/recuperer_pesticides.py` (CSV brut dans `data/raw/`) puis `src/pesticides/preparer_pesticides.py` (exclusion Corse/DROM, regroupement des 8 sels de cuivre sous `"cuivre"`, filtre sur les 10 molécules clés) :

```bash
python -c "from src.pesticides.preparer_pesticides import preparer_pesticides; preparer_pesticides()"
```

#### Étape 3 — Vérifier la présence de la table de correspondance
Le fichier `data/processed/correspondance_groupes_molecules.csv` est produit par le notebook `notebooks/exploration/tf_correspondance_groupes_molecules.ipynb`. S'il est absent, exécuter ce notebook au préalable.

#### Étape 4 — Lancer l'agrégation parcelles × pesticides (génère les 11 tables Parquet annuelles)
L'orchestrateur `construire_parcelles_pesticides.py` exécute automatiquement dans l'ordre :
1. `charger_matrice_correspondance.py`
2. `calculer_doses_pesticides_groupes.py` → produit `data/processed/doses_pesticides_groupes.parquet`
3. `construire_parcelles_pesticides_annee.py` pour chaque année → produit `data/processed/parcelles_pesticides/parcelles_pesticides_<annee>.parquet`

```bash
# Générer toutes les années (2013 à 2023)
python -m src.agregation.parcelles_pesticides.construire_parcelles_pesticides

# Ou générer uniquement certaines années (ex. 2022 et 2023)
python -m src.agregation.parcelles_pesticides.construire_parcelles_pesticides --annees 2022 2023
```

### Lecture d'une table annuelle en Python

```python
import pandas as pd

df_2023 = pd.read_parquet("data/processed/parcelles_pesticides/parcelles_pesticides_2023.parquet")
```

---

## 2. Données en entrée

| Fichier | Maille | Rôle dans le pipeline |
|---|---|---|
| `data/processed/parcelles_rpg_2023.parquet` | 1 ligne par parcelle (`9 742 907` lignes, 94 départements continentaux) | Fournit `id_parcelle`, `code_dep`, `nom_dep`, `surface_ha`, `code_groupe`, `libelle_groupe` (les colonnes `code_culture` et `categorie_culture` sont retirées en sortie). |
| `data/processed/pesticides.parquet` | `geocode_departement` × `annee` × `substance` (2013–2023) | Fournit la quantité achetée $Q_{d,t,m}$ (en **kg** de substance active) pour les 10 molécules retenues (dont le `cuivre`, obtenu par agrégation de ses 8 sels). |
| `data/processed/correspondance_groupes_molecules.csv` | 23 groupes RPG × 10 molécules | Définit quels groupes de cultures utilisent chaque molécule ($I_{g,m} \in \{0, 1\}$). |

> **Remarque importante sur l'unité des achats BNV-D** : la description textuelle du jeu de données sur data.gouv.fr mentionne « en tonnes », mais les valeurs numériques du fichier CSV départemental sont bien en **kilogrammes (kg)** (ex. total national 2023 ≈ `63,8 millions`, soit ~63 800 tonnes toutes substances ; glyphosate 2023 ≈ `6,67 millions`, soit ~6 674 tonnes). Aucune conversion n'est appliquée et les colonnes de sortie sont suffixées en `_kg`.

### Les 10 molécules suivies

- **Herbicides** : `glyphosate`, `s-metolachlore`, `isoproturon`, `chlorotoluron`
- **Fongicides** : `cuivre` (somme des 8 sels de cuivre de la BNV-D), `boscalid`, `tebuconazole`
- **Insecticides** : `imidaclopride`, `cypermethrine`, `chlorpyriphos-ethyl`

---

## 3. Modèle mathématique d'allocation

### Notations

- $d \in \{1, \dots, 94\}$ : département de France métropolitaine continentale (hors Corse `2A`/`2B` et DROM).
- $t \in \{2013, \dots, 2023\}$ : année d'achat des pesticides.
- $g \in \{1, \dots, 23\}$ : groupe de cultures RPG (`libelle_groupe`).
- $m \in \{1, \dots, 10\}$ : molécule active.
- $i$ : parcelle agricole appartenant au département $d_i$ et au groupe $g_i$, de surface déclarée $s_i$ (en ha).
- $I_{g, m} \in \{0, 1\}$ : indicatrice issue de `correspondance_groupes_molecules.csv` ($1$ si le groupe $g$ utilise la molécule $m$, $0$ sinon).
- $Q_{d, t, m} \ge 0$ : quantité totale (en kg) de molécule $m$ achetée dans le département $d$ durant l'année $t$.

### Étape A — Surfaces agricoles par département et groupe

La surface totale du groupe $g$ dans le département $d$ vaut :

$$S_{d, g} = \sum_{i \in (d, g)} s_i$$

La **surface éligible** à la molécule $m$ dans le département $d$ est la somme des surfaces des groupes qui utilisent effectivement $m$ :

$$S_{d, m}^{\text{elig}} = \sum_{g=1}^{23} I_{g, m} \, S_{d, g}$$

### Étape B — Quantité de molécule attribuée au groupe $g$ dans le département $d$

Les achats BNV-D n'étant pas ventilés par culture, la quantité départementale $Q_{d, t, m}$ est répartie entre les groupes éligibles au prorata de leurs surfaces dans le département :

$$Q_{d, t, m, g} = \begin{cases} I_{g, m} \, Q_{d, t, m} \, \dfrac{S_{d, g}}{S_{d, m}^{\text{elig}}} & \text{si } S_{d, m}^{\text{elig}} > 0 \\ 0 & \text{si } S_{d, m}^{\text{elig}} = 0 \end{cases}$$

### Étape C — Quantité attribuée à chaque parcelle $i$

Au sein de son département $d_i$ et de son groupe $g_i$, chaque parcelle $i$ reçoit une part du tonnage du groupe proportionnelle au quotient de sa surface sur la surface totale du groupe dans le département :

$$q_{i, t, m} = \frac{s_i}{S_{d_i, g_i}} \, Q_{d_i, t, m, g_i}$$

En remplaçant $Q_{d_i, t, m, g_i}$ par son expression de l'étape B, $S_{d_i, g_i}$ se simplifie :

$$q_{i, t, m} = I_{g_i, m} \, \underbrace{\frac{Q_{d_i, t, m}}{S_{d_i, m}^{\text{elig}}}}_{D_{d_i, t, m}} \, s_i = D_{d_i, t, m, g_i} \, s_i$$

où $D_{d, t, m, g} = I_{g, m} \dfrac{Q_{d, t, m}}{S_{d, m}^{\text{elig}}}$ représente la **dose moyenne départementale par hectare éligible** (en $\text{kg/ha}$).

### Propriétés clés du modèle

1. **Conservation exacte de la masse** : pour tout département $d$, toute année $t$ et toute molécule $m$ tels que $S_{d,m}^{\text{elig}} > 0$ :
   $$\sum_{i \in d} q_{i, t, m} = \sum_{g=1}^{23} \sum_{i \in (d, g)} \frac{s_i}{S_{d, g}} Q_{d, t, m, g} = \sum_{g=1}^{23} Q_{d, t, m, g} = Q_{d, t, m}$$
2. **Zéro sur les groupes non concernés** : les 4 groupes sans molécule (`Prairies permanentes`, `Estives et landes`, `Gel (surfaces gelées sans production)`, `Divers`) ainsi que tout couple $(g, m)$ tel que $I_{g,m} = 0$ reçoivent strictement $0{,}0\text{ kg}$.
3. **Hypothèse de stabilité du parcellaire** : conformément au contrat de données (`docs/contrat_donnees.md`), le millésime RPG 2023 sert de photographie fixe des surfaces agricoles pour toutes les années 2013–2023.

---

## 4. Gestion de la mémoire et organisation des scripts

Le produit cartésien complet représente $9\,742\,907 \times 11 = 107\,171\,977$ lignes. Pour éviter toute saturation de la RAM (~10–15 Go en `pandas` naïf) :

1. **Factorisation préalable** : la table intermédiaire `data/processed/doses_pesticides_groupes.parquet` ne compte que $94 \times 11 \times 23 = 23\,782$ lignes (< 1 Mo) et pré-calcule toutes les doses $D_{d, t, m, g}$.
2. **Une table Parquet par année** : chaque année est stockée dans son propre fichier `data/processed/parcelles_pesticides/parcelles_pesticides_<annee>.parquet` (~133 à 165 Mo/fichier).
3. **Traitement par lots (*streaming*)** : `parcelles_rpg_2023.parquet` est lu par paquets de `500 000` parcelles via `pyarrow.parquet.ParquetFile.iter_batches`, multiplié de façon vectorisée en `float64` sur une grille dense `(94 × 23 × 10)`, converti en `float32` et écrit directement sur disque via `pyarrow.parquet.ParquetWriter` (compression `zstd` + encodage dictionnaire). L'empreinte mémoire reste inférieure à **~250 Mo** pendant toute l'exécution.
4. **Écriture atomique** : chaque fichier est d'abord écrit sous `.parquet.tmp` puis renommé, garantissant l'absence de fichier corrompu en cas d'interruption.

### Fichiers dans `src/agregation/parcelles_pesticides/`

| Ordre | Fichier | Rôle |
|---|---|---|
| 0 | `constantes_agregation.py` | Chemins par défaut, colonnes conservées et mapping des 10 colonnes `*_kg`. |
| 1 | `charger_matrice_correspondance.py` | Parse `correspondance_groupes_molecules.csv` en matrice binaire `23 × 10`. |
| 2 | `calculer_doses_pesticides_groupes.py` | Agrège les surfaces $S_{d,g}$ par lots, calcule les doses $D_{d,t,m,g}$ et journalise les quantités non allouables. |
| 3 | `construire_parcelles_pesticides_annee.py` | Génère un fichier annuel `parcelles_pesticides_<annee>.parquet` en streaming et calcule les métriques de contrôle qualité. |
| 4 | `construire_parcelles_pesticides.py` | Orchestrateur complet (CLI + fonction Python) qui enchaîne les étapes 1 → 3 pour toutes les années demandées et vérifie la conservation de masse. |

---

## 5. Schéma des tables produites

### Table intermédiaire : `data/processed/doses_pesticides_groupes.parquet`
- **Clé** : `(code_dep, annee, libelle_groupe)` — `23 782` lignes.
- **Colonnes** : `code_dep`, `annee`, `libelle_groupe`, `surface_groupe_ha`, et les 10 colonnes `dose_<molecule>_kg_ha`.

### Tables annuelles : `data/processed/parcelles_pesticides/parcelles_pesticides_<annee>.parquet`
- **Clé** : `(id_parcelle, annee)` — `9 742 907` lignes par fichier.
- **Colonnes** (17 au total ; `code_culture` et `categorie_culture` retirées) :
  - Identifiants & contexte : `id_parcelle` (`str`), `annee` (`int16`), `code_dep` (`str`), `nom_dep` (`str`), `surface_ha` (`float64`), `code_groupe` (`str`), `libelle_groupe` (`str`).
  - Quantités estimées (`float32`, en **kg**) : `glyphosate_kg`, `s_metolachlore_kg`, `isoproturon_kg`, `chlorotoluron_kg`, `cuivre_kg`, `boscalid_kg`, `tebuconazole_kg`, `imidaclopride_kg`, `cypermethrine_kg`, `chlorpyriphos_ethyl_kg`.

---

## 6. Cas limites traités

- **Sels de cuivre** : dans `src/pesticides/preparer_pesticides.py`, les 8 formes de cuivre présentes dans la BNV-D sont regroupées sous `"cuivre"` avant agrégation.
- **Départements sans surface éligible ($S_{d, m}^{\text{elig}} = 0$)** :
  - `75` (Paris) : aucune parcelle éligible pour les 10 molécules.
  - `92` (Hauts-de-Seine) : aucune parcelle éligible pour `s-metolachlore` et `cuivre`.
  - Les doses correspondantes sont fixées à `0.0` (aucune division par zéro / `NaN` / `inf`), et le tonnage non allouable est comptabilisé séparément dans le bilan de contrôle.
- **Molécules retirées ou sans achat sur une année** (ex. `isoproturon` après 2017, `imidaclopride` après 2018, `chlorpyriphos-ethyl` après 2020) : l'absence de ligne d'achat dans la BNV-D est interprétée comme `0.0 kg`.
