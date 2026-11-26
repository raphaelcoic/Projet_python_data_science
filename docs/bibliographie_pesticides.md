# Bibliographie : partie pesticides

Références utilisées pour la partie pesticides du projet (`notebooks/exploration/notebook_pesticides_final.ipynb`,
`src/pesticides/`). Elles sont classées selon leur rôle dans le rapport : situer le sujet, justifier les données
et la méthode, puis ouvrir la discussion.

## 1. État de l'art : ce que d'autres ont fait

### Effets des pesticides sur les cours d'eau

- **Beketov, M. A., Kefford, B. J., Schäfer, R. B. & Liess, M. (2013).** Pesticides reduce regional biodiversity
  of stream invertebrates. *PNAS*, 110(27), 11039-11043. https://doi.org/10.1073/pnas.1305618110
  Cours d'eau d'Allemagne, de France et d'Australie : jusqu'à 42 % de taxons d'invertébrés en moins dans les sites
  les plus contaminés, y compris sous les seuils réglementaires. Lien direct avec l'indice I2M2.

- **Malaj, E., von der Ohe, P. C., Grote, M., Kühne, R., Mondy, C. P., Usseglio-Polatera, P., Brack, W. & Schäfer, R. B. (2014).**
  Organic chemicals jeopardize the health of freshwater ecosystems on the continental scale. *PNAS*, 111(26),
  9549-9554. https://doi.org/10.1073/pnas.1321082111
  Environ 4 000 sites de surveillance européens : risque chronique sur 42 % des sites, risque aigu sur 14 %.
  Les pesticides sont de loin les premiers responsables.

- **Stehle, S. & Schulz, R. (2015).** Agricultural insecticides threaten surface waters at the global scale.
  *PNAS*, 112(18), 5750-5755. https://doi.org/10.1073/pnas.1500232112
  Méta-analyse de 838 études (plus de 2 500 sites, 73 pays) : plus de la moitié des concentrations d'insecticides
  détectées dépassent les seuils réglementaires.

### Synthèses sur la présence des pesticides dans l'eau

- **de Souza, R. M., Seibert, D., Quesada, H. B., Bassetti, F. J., Fagundes-Klen, M. R. & Bergamasco, R. (2020).**
  Occurrence, impacts and general aspects of pesticides in surface water: a review. *Process Safety and
  Environmental Protection*, 135, 22-37. https://doi.org/10.1016/j.psep.2019.12.035
  Revue des pesticides retrouvés dans les eaux de surface dans le monde (2012-2019), classe par classe
  (herbicides, insecticides, fongicides), avec la question des mélanges.

- **Farah, I. F., dos Santos, C. R., Pinto, M. C. F., Araújo, C. R. & Amaral, M. C. S. (2024).** Pesticides in
  aquatic environment: occurrence, ecological implications and legal framework. *Journal of Environmental Chemical
  Engineering*, 12, 114072. https://doi.org/10.1016/j.jece.2024.114072
  Revue plus récente qui combine présence dans l'eau, évaluation du risque écologique (quotient de risque) et
  comparaison des réglementations : utile pour relier nos molécules aux seuils réglementaires.

### Relier les usages de pesticides à la qualité de l'eau

- **Auterives, C. & Baran, N. (2015).** *Pressions et impacts des produits phytosanitaires sur les eaux souterraines :
  état de l'art sur les approches méthodologiques.* Rapport final BRGM/RP-64623-FR, 68 p.
  https://infoterre.brgm.fr/rapports/RP-64623-FR.pdf
  Recense les méthodes qui relient les usages de pesticides à la qualité des nappes (indices, approches
  statistiques, modèles numériques) et conclut qu'aucune ne suffit seule à l'échelle nationale. Utile pour situer
  notre approche statistique, même si nous travaillons sur les eaux de surface.

- **Lungarska, A., Poméon, T., Ramalanjaona, L., Lision, O., Cantelaube, P. & Lardot, B. (2023).** La BNVDs :
  spatialisation à l'échelle de la parcelle agricole des données d'achats des produits phytopharmaceutiques en
  France. *Environnement, Risques & Santé*, 22(S1), 19-26. https://doi.org/10.1684/ers.2023.1761
  Méthode INRAE qui répartit les achats de la BNV-D sur les parcelles agricoles. C'est la démarche la plus proche
  de la nôtre (répartition des achats départementaux sur les parcelles du RPG puis agrégation par zone
  hydrographique), en plus fin.

## 2. Données et choix des molécules

### Sources de données

- **BNV-D : Banque nationale des ventes des distributeurs de produits phytopharmaceutiques.** Achats de pesticides
  par département et par code postal de l'acheteur, 2013-2023, publiés sur data.gouv.fr.
  https://www.data.gouv.fr/datasets/achats-de-pesticides-par-code-postal-1
- **SDES (2026).** *État des lieux des ventes et des achats des produits phytosanitaires en France : notice
  méthodologique.* Ministère de la Transition écologique. Explique la construction de la BNV-D et ses limites
  (données déclaratives, achats et non usages).

### Choix des 10 molécules (détail dans `tf_selection_molecules_eau.ipynb`)

- **Larras, F., Bouchez, A., Rimet, F. & Montuelle, B. (2012).** Using bioassays and species sensitivity
  distributions to assess herbicide toxicity towards benthic diatoms. *PLOS ONE*, 7(8), e44458.
  https://doi.org/10.1371/journal.pone.0044458
  Sensibilité des diatomées benthiques aux herbicides (dont isoproturon et chlortoluron) : justifie le lien avec
  l'indice IBD.
- **Klátyik, S., Simon, G., Oláh, M., Takács, E., Mesnage, R., Antoniou, M. N., Zaller, J. G. & Székács, A. (2024).**
  Aquatic ecotoxicity of glyphosate, its formulations, and co-formulants: evidence from 2010 to 2023.
  *Environmental Sciences Europe*, 36, 22. https://doi.org/10.1186/s12302-024-00849-1
  Synthèse des effets du glyphosate et de ses formulations commerciales sur les algues, invertébrés, poissons et
  amphibiens. Justifie de garder le glyphosate, première molécule achetée dans nos données.
- **Expertise scientifique collective INRAE-Ifremer (2022).** *Impacts des produits phytopharmaceutiques sur la
  biodiversité et les services écosystémiques.* https://doi.org/10.17180/0gp2-cd65
- **Directive 2013/39/UE** du 12 août 2013 (substances prioritaires de la directive-cadre sur l'eau).
  https://eur-lex.europa.eu/eli/dir/2013/39/oj
- **Arrêté du 27 juillet 2018** (polluants spécifiques de l'état écologique).
  https://www.legifrance.gouv.fr/loda/id/JORFTEXT000037347756/

### Lecture des résultats

- **SDES (2021).** *Plan de réduction des produits phytopharmaceutiques et de sortie du glyphosate : état des lieux
  des ventes et des achats en France en 2019.* Datalab Essentiel n° 247.
  Attribue la forte baisse de 2019 (-36 %) en partie aux achats anticipés fin 2018, avant la hausse de la
  redevance pour pollutions diffuses : c'est l'explication du pic de 2018 et du creux de 2019 dans nos données.

## 3. Ouverture : politiques publiques

- **Cour des comptes (2019).** *Le bilan des plans Écophyto.* Référé du 27 novembre 2019, publié le 4 février 2020.
  Dix ans après, les plans Écophyto n'ont pas atteint leur objectif de réduction de 50 % de l'usage des pesticides,
  ce qui rejoint l'absence de tendance à la baisse dans nos données depuis 2014.
- **Böcker, T. & Finger, R. (2016).** European pesticide tax schemes in comparison: an analysis of experiences and
  developments. *Sustainability*, 8(4), 378. https://doi.org/10.3390/su8040378
  Compare les taxes sur les pesticides en France, au Danemark, en Norvège et en Suède : efficacité limitée en
  général, mais forte quand la taxe est assez élevée sur une substance donnée. La redevance pour pollutions
  diffuses en est un exemple, et nos données en montrent l'effet d'anticipation.
- **Böcker, T. & Finger, R. (2017).** A meta-analysis on the elasticity of demand for pesticides. *Journal of
  Agricultural Economics*, 68(2), 518-533.
- **SDES (2023).** *La pollution chimique des cours d'eau et des plans d'eau en France de 2000 à 2020.* Datalab
  n° 115. Bilan des pesticides quantifiés dans les cours d'eau et des cumuls de pressions toxiques : le pont vers
  la partie « qualité de l'eau » du projet.
