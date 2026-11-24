import numpy as np


def calculer_gini(valeurs):
    """Indice de Gini de quantités positives ou nulles, par exemple les achats d'une molécule par département.

    0 : quantités réparties également ; proche de 1 : concentrées en quelques endroits.
    """
    valeurs = np.sort(np.asarray(valeurs, dtype=float))
    n = len(valeurs)
    return 2 * np.sum(np.arange(1, n + 1) * valeurs) / (n * valeurs.sum()) - (n + 1) / n
