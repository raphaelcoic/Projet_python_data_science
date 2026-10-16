def liste_departements():
    L = []
    for i in range(1, 96):
        if i <= 9:
            L.append(f"0{i}")
        elif i == 20:
            L.append("2A", "2B")
        else:
            L.append(f"{i}")
    return L