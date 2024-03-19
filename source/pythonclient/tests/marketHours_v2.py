from datetime import datetime, timezone, time, timedelta


def get_market_timezone(country):
    # Détermine le fuseau horaire du marché boursier pour le pays spécifié
    if country == "US":
        return timezone(
            timedelta(hours=-4 if is_daylight_saving_time() else -5))  # Heure d'été (EDT) ou heure standard (EST)
    elif country == "AUSTRALIA":
        return timezone(timedelta(hours=10))  # Fuseau horaire de l'Australie (AEST)
    else:
        return timezone.utc  # Fuseau horaire universel


def is_daylight_saving_time():
    # Vérifie si l'heure actuelle est en heure d'été (EDT)
    now = datetime.now()
    return now.timetuple().tm_isdst > 0


def closing_hours(country):
    # Obtenez l'heure actuelle dans le fuseau horaire du marché boursier
    heure_locale = datetime.now(get_market_timezone(country))
    closing = False

    # Définir l'heure de clôture pour le marché boursier spécifié
    if country == "US":
        heure_cloture = time(16, 0)  # 16h00 EST
    elif country == "AUSTRALIA":
        heure_cloture = time(16, 0)  # 16h00 AEST
    else:
        heure_cloture = time(16, 30)  # 16h30 UTC

    # Plage de clôture (une heure avant la fermeture)
    plage_cloture = (heure_cloture.hour - 1, heure_cloture.minute), (heure_cloture.hour, heure_cloture.minute)

    # Vérifier si l'heure actuelle est dans la plage de clôture
    heure_actuelle = heure_locale.time()
    if plage_cloture[0] <= (heure_actuelle.hour, heure_actuelle.minute) < plage_cloture[1]:
        closing = True

    return closing


def opening_hours(country):
    # Obtenez l'heure actuelle dans le fuseau horaire du marché boursier
    heure_locale = datetime.now(get_market_timezone(country))
    print(heure_locale)
    opening = False

    # Définir l'heure d'ouverture pour le marché boursier spécifié
    if country == "US":
        heure_ouverture = time(9, 30)  # 9h30 EST
    elif country == "AUSTRALIA":
        heure_ouverture = time(10, 0)  # 10h00 AEST
    else:
        heure_ouverture = time(9, 0)  # 9h00 UTC

    # Plage d'ouverture
    plage_ouverture = (heure_ouverture.hour, heure_ouverture.minute), (16, 0)  # 16h00 pour tous les marchés

    # Vérifier si l'heure actuelle est dans la plage d'ouverture
    heure_actuelle = heure_locale.time()
    if plage_ouverture[0] <= (heure_actuelle.hour, heure_actuelle.minute) < plage_ouverture[1]:
        opening = True

    return opening


# Test du code
print(opening_hours("US"))  # Devrait imprimer True ou False selon l'heure actuelle
print(opening_hours("AUSTRALIA"))  # Devrait imprimer True ou False selon l'heure actuelle
print(opening_hours("FRANCE"))  # Devrait imprimer True ou False selon l'heure actuelle

print(closing_hours("US"))  # Devrait imprimer True ou False selon l'heure actuelle
print(closing_hours("AUSTRALIA"))  # Devrait imprimer True ou False selon l'heure actuelle
print(closing_hours("FRANCE"))  # Devrait imprimer True ou False selon l'heure actuelle
