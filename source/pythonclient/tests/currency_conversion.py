import requests
import pandas as pd
import os
file = "C:\\TWS API\\source\\pythonclient\\tests\\exchange_rates.csv"
def get_rates_frankfurter(base="EUR", symbols=None):
    if symbols is None:
        symbols = ['USD', 'EUR', 'CAD', 'GBP', 'CHF', 'JPY', 'SEK', 'NOK','DKK','PLN','ISK','RON','HUF']
    symbols_str = ",".join(symbols)
    url = f"https://api.frankfurter.app/latest?from={base}&to={symbols_str}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data["rates"]
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion : {e}")
        return {}

def save_rates_to_csv(rates, filename=file):
    df = pd.DataFrame([
        {"From": "EUR", "To": k, "Rate": v}
        for k, v in rates.items()
    ])
    df.to_csv(filename, index=False)
    print(f"✅ Fichier de taux enregistré dans : {filename}")

def convert_from_euro(amount, to_currency, filename=file):
    if not os.path.exists(filename):
        print("❌ Fichier des taux manquant. Lancer d'abord la mise à jour.")
        return None
    df = pd.read_csv(filename)
    row = df[df["To"] == to_currency]
    if row.empty:
        print(f"❌ Devise {to_currency} non trouvée.")
        return None
    rate = row.iloc[0]["Rate"]
    return amount * rate

def convert_to_euro(amount, from_currency, filename=file):
    if not os.path.exists(filename):
        print("❌ Fichier des taux manquant. Lancer d'abord la mise à jour.")
        return None
    df = pd.read_csv(filename)
    row = df[df["To"] == from_currency]
    if row.empty:
        print(f"❌ Devise {from_currency} non trouvée.")
        return None
    rate = row.iloc[0]["Rate"]
    return amount / rate

if __name__ == "__main__":
    # Étape 1 : Récupération des taux depuis EUR vers d'autres devises
    rates = get_rates_frankfurter()
    if rates:
        save_rates_to_csv(rates)

        # Exemple 1 : convertir 400 EUR en SEK
        result1 = convert_from_euro(400, "SEK")
        if result1 is not None:
            print(f"💶 400 EUR = {result1:.2f} SEK")

        # Exemple 2 : convertir 500 USD en EUR
        result2 = convert_to_euro(500, "USD")
        if result2 is not None:
            print(f"💵 500 USD = {result2:.2f} EUR")
