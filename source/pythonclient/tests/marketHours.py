from datetime import datetime, timezone, time

def closing_hours(x):
    # Obtenez l'heure GMT actuelle
    heure_gmt = datetime.now(timezone.utc)
    closing = False
    # Définissez les heures de début et de fin (17h00 et 17h30)
    if "US" in x:
        # Passage à l'heure d'été aux États-Unis (heure avancée)
        heure_debut = time(19, 30, 0)  # 20h00
        heure_fin = time(21, 0, 0)  # 22h00
    else:
        heure_debut = time(15, 30, 0)
        heure_fin = time(16, 30, 0)

    if heure_gmt.weekday() in [5, 6]:
        print(x)
        print("Jour de fermeture des marchés")
    # Vérifiez si l'heure actuelle est dans la plage
    elif heure_debut <= heure_gmt.time() <= heure_fin:
        closing = True
        print(x)
        print(heure_gmt)
        print("Jour d'ouverture des marchés")
        print("Pré-cloture :" + str(closing))
    else:
        closing = False
        print(x)
        print(heure_gmt)
        print("Jour d'ouverture des marchés")
        print("Pré-cloture :" + str(closing))

    return closing

def opening_hours(x):
    # Obtenez l'heure GMT actuelle
    heure_gmt = datetime.now(timezone.utc)
    opening = False

    if "US" in x:
        # Passage à l'heure d'été aux États-Unis (heure avancée)
        heure_debut = time(13, 30, 0)
        heure_fin = time(21, 0, 0)
    else:
        heure_debut = time(8, 0, 0)
        heure_fin = time(16, 30, 0)

    if heure_gmt.weekday() in [5, 6]:
        print("Jour de fermeture des marchés")
    # Vérifiez si l'heure actuelle est dans la plage
    elif heure_debut <= heure_gmt.time() <= heure_fin:
        opening = True
        print(x)
        print(heure_gmt)
        print("Jour d'ouverture des marchés")
        print("Marché ouvert :" + str(opening))
    else:
        print(x)
        print(heure_gmt)
        print("Jour d'ouverture des marchés")
        print("Marché ouvert :" + str(opening))

    return opening

# Test du code
# opening_hours("US9")
# opening_hours("FRANCE")
# closing_hours("FRANCE")
