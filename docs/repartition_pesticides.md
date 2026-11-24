# Achats de pesticides attribués aux cultures (RPG 2023 × BNV-D 2013–2023)

On estime la quantité (en **kg de substance active**) des **10 molécules clés** attribuée à chaque hectare de chaque groupe de cultures du RPG 2023, par département et par année.

| Fichier | Rôle |
|---|---|
| `src/pesticides/constantes_pesticides.py` | Les 10 molécules (`MOLECULES`) et les noms de colonnes `<molecule>_kg` |
| `src/zones_hydrographiques/constantes_cultures_molecules.py` | Les molécules utilisées par chacun des 23 groupes de cultures (`MOLECULES_PAR_GROUPE`) |
| `src/zones_hydrographiques/calculer_doses_pesticides_groupes.py` | Dose de chaque molécule par hectare des groupes qui l'utilisent, par département et par année |

`src/zones_hydrographiques/agreger_pesticides_zones.py` multiplie ensuite ces doses par la surface de chaque groupe dans chaque zone hydrographique (partie 5.2 de `main.ipynb`) :

```python
doses = calculer_doses_pesticides_groupes(parcelles, pesticides)   # parcelles_rpg_2023, pesticides.parquet
pesticides_zones = agreger_pesticides_zones(doses, parcelles, parcelles_zones)
```

## Données en entrée

| Données | Rôle |
|---|---|
| `parcelles_rpg_2023.parquet` (une ligne par parcelle, 94 départements) | surfaces par département et groupe de cultures |
| `pesticides.parquet` (`preparer_pesticides`) | quantité achetée $Q_{d,t,m}$, en **kg**, pour les 10 molécules (le `cuivre` regroupe les 8 sels de cuivre de la BNV-D) |
| `MOLECULES_PAR_GROUPE` | quels groupes de cultures utilisent chaque molécule ($I_{g,m} \in \{0, 1\}$), d'après les homologations E-Phy (Anses) et les guides des instituts techniques ; sources détaillées dans `notebooks/exploration/tf_correspondance_groupes_molecules.ipynb` |

> **Unité des achats BNV-D** : la description du jeu de données sur data.gouv.fr dit « en tonnes », mais les valeurs du CSV départemental sont en **kilogrammes** (total national 2023 ≈ 63,8 millions, soit ~63 800 tonnes toutes substances ; glyphosate 2023 ≈ 6,67 millions, soit ~6 674 tonnes). Aucune conversion n'est appliquée.

Les 10 molécules : herbicides `glyphosate`, `s-metolachlore`, `isoproturon`, `chlorotoluron` ; fongicides `cuivre`, `boscalid`, `tebuconazole` ; insecticides `imidaclopride`, `cypermethrine`, `chlorpyriphos-ethyl`.

## Modèle d'allocation

Notations : $d$ département, $t$ année, $g$ groupe de cultures, $m$ molécule, $i$ parcelle de surface $s_i$ (ha), $I_{g,m} = 1$ si le groupe $g$ utilise la molécule $m$.

La surface du groupe $g$ dans le département $d$ est $S_{d,g} = \sum_{i \in (d,g)} s_i$, et la **surface éligible** à la molécule $m$ est celle des groupes qui l'utilisent :

$$S_{d,m}^{\text{elig}} = \sum_{g} I_{g,m} \, S_{d,g}$$

Les achats n'étant pas ventilés par culture, $Q_{d,t,m}$ est réparti entre les groupes éligibles au prorata de leur surface, puis entre les parcelles d'un groupe au prorata de la leur. La quantité attribuée à une parcelle se simplifie en une dose par hectare multipliée par sa surface :

$$q_{i,t,m} = D_{d_i,t,m,g_i} \, s_i \quad \text{avec} \quad D_{d,t,m,g} = I_{g,m} \, \frac{Q_{d,t,m}}{S_{d,m}^{\text{elig}}}$$

C'est la colonne `dose_kg_ha` de `calculer_doses_pesticides_groupes`. Comme la dose ne dépend que du département, du groupe et de l'année, la quantité d'une zone hydrographique s'obtient sans passer par les parcelles une à une : $\sum_i \text{part}_{i,z} \, q_{i,t,m} = \sum_{d,g} D_{d,t,m,g} \sum_{i \in (d,g)} \text{part}_{i,z} \, s_i$.

Propriétés :

1. **Conservation** : pour tout $(d, t, m)$ tel que $S_{d,m}^{\text{elig}} > 0$, la somme des $q_{i,t,m}$ du département vaut $Q_{d,t,m}$.
2. **Zéro sur les groupes non concernés** : les 4 groupes sans molécule (`Prairies permanentes`, `Estives et landes`, `Gel (surfaces gelées sans production)`, `Divers`) et tout couple $(g, m)$ tel que $I_{g,m} = 0$ ne reçoivent rien.
3. **Parcellaire fixe** : conformément au contrat de données, le RPG 2023 sert pour toutes les années 2013–2023.

## Cas limites

- **Départements sans surface éligible** ($S_{d,m}^{\text{elig}} = 0$) : Paris (`75`) pour les 10 molécules, Hauts-de-Seine (`92`) pour `s-metolachlore` et `cuivre`. La dose vaut 0 : ces achats (environ 136 t sur 2013–2023) ne sont attribués à aucune parcelle.
- **Molécules retirées ou sans achat une année** (`isoproturon` après 2017, `imidaclopride` après 2018, `chlorpyriphos-ethyl` après 2020) : sans ligne d'achat, rien n'est attribué (0 kg).
