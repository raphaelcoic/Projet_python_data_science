def liste_departements():
    """Codes des 94 départements de métropole continentale (hors Corse), en texte : "01" ... "95"."""
    return [f"{i:02d}" for i in range(1, 96) if i != 20]
