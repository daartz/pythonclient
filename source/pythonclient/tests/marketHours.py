from datetime import datetime, timezone, time, timedelta


def easter(year):
    """Calcul du dimanche de Pâques basé sur l'algorithme de Butcher."""
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return datetime(year, month, day)

def get_us_holidays(year, country):
    """Génération de la liste des jours fériés pour une année donnée."""

    if "US" in country :
        holidays = {
            "New Year's Day": datetime(year, 1, 1),
            "Martin Luther King Jr. Day": datetime(year, 1, 1) + timedelta(days=(14 - datetime(year, 1, 1).weekday() + 7) % 7),
            "Presidents' Day": datetime(year, 2, 1) + timedelta(days=(14 - datetime(year, 2, 1).weekday() + 7) % 7),
            "Memorial Day": datetime(year, 5, 31) - timedelta(days=datetime(year, 5, 31).weekday()),
            "Independence Day": datetime(year, 7, 4),
            "Labor Day": datetime(year, 9, 1) + timedelta(days=(7 - datetime(year, 9, 1).weekday()) % 7),
            "Thanksgiving": datetime(year, 11, 1) + timedelta(days=(24 + (3 - datetime(year, 11, 1).weekday()) % 7)),
            "Christmas Day": datetime(year, 12, 25)
        }

        # Ajustement pour les jours fériés tombant un weekend
        for holiday, date in holidays.items():
            if date.weekday() == 5:  # Samedi
                holidays[holiday] = date - timedelta(days=1)
            elif date.weekday() == 6:  # Dimanche
                holidays[holiday] = date + timedelta(days=1)

        # Vendredi Saint (le calcul dépend de la date de Pâques)
        good_friday = easter(year) - timedelta(days=2)
        holidays["Good Friday"] = good_friday
        holidays["Easter Monday"] = easter(year) + timedelta(days=1)

    else:
        holidays = {
            "New Year's Day": datetime(year, 1, 1),
            "Labor Day": datetime(year, 5, 1),
            "Christmas Day": datetime(year, 12, 25),
            "Boxing Day": datetime(year, 12, 26),  # Lendemain de Noël
        }

        # Ajout des jours fériés spécifiques à chaque pays
        if country == "FRANCE":
            holidays["Bastille Day"] = datetime(year, 7, 14)
            holidays["Armistice Day"] = datetime(year, 11, 11)
        elif country == "GERMANY":
            holidays["German Unity Day"] = datetime(year, 10, 3)
            # Good Friday et Easter Monday varient par année et par région
        elif country == "SPAIN":
            holidays["Spain National Day"] = datetime(year, 10, 12)
        elif country == "ITALY":
            holidays["Republic Day"] = datetime(year, 6, 2)
        elif country == "BELGIUM":
            holidays["Belgium National Day"] = datetime(year, 7, 21)

        # Pâques et le Lundi de Pâques (varient chaque année)
        easter_sunday = easter(year)
        holidays["Good Friday"] = easter_sunday - timedelta(days=2)
        holidays["Easter Monday"] = easter_sunday + timedelta(days=1)

    return holidays

def is_holiday(date, country):
    """Vérifie si une date est un jour férié."""
    holidays = get_us_holidays(date.year, country)
    return date.strftime('%Y-%m-%d') in {day.strftime('%Y-%m-%d') for day in holidays.values()}

def closing_hours(x):
    # Obtenez l'heure GMT actuelle
    heure_gmt = datetime.now(timezone.utc)
    closing = False
    # Définissez les heures de début et de fin (17h00 et 17h30)
    if "US" in x or "CANADA" in x:
        # Passage à l'heure d'été aux États-Unis (heure avancée)
        heure_debut = time(19, 00, 0)  # 20h00
        heure_fin = time(22, 30, 0)  # 22h00
    else:
        heure_debut = time(13, 30, 0)
        heure_fin = time(18, 30, 0)

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

    if "US" in x or "CANADA" in x:
        # Passage à l'heure d'été aux États-Unis (heure avancée)
        heure_debut = time(13, 30, 0)
        heure_fin = time(22, 30, 0)
    else:
        heure_debut = time(7, 0, 0)
        heure_fin = time(17, 30, 0)

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
