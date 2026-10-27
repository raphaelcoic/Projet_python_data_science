def liste_departements():
    """Codes des 96 départements de métropole, en texte : "01" ... "19", "2A", "2B", "21" ... "95"."""
    codes = []
    for i in range(1, 96):
        if i == 20:
            codes += ["2A", "2B"]
        else:
            codes.append(f"{i:02d}")
    return codes
