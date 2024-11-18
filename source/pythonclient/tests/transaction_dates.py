import requests
import pandas as pd
from datetime import datetime

# Informations nécessaires
FLEX_TOKEN = 741289782337547768006278  # Remplacez par votre token Flex
FLEX_QUERY_ID = 1097628  # Remplacez par l'ID de votre Flex Query
BASE_URL = "https://gdcdyn.interactivebrokers.com/Universal/servlet/FlexStatementService.SendRequest"


# Étape 1 : Envoyer une requête pour récupérer le rapport
def request_flex_report():
    params = {
        "t": FLEX_TOKEN,  # Token d'authentification
        "q": FLEX_QUERY_ID  # ID de la Flex Query
    }

    response = requests.get(BASE_URL, params=params)

    if response.status_code == 200:
        # Extraire l'ID du rapport
        xml_data = response.text
        start = xml_data.find("<referenceCode>") + len("<referenceCode>")
        end = xml_data.find("</referenceCode>")
        reference_code = xml_data[start:end]
        print(f"Référence du rapport reçu : {reference_code}")
        return reference_code
    else:
        print("Erreur lors de la requête Flex Query :", response.text)
        return None


# Étape 2 : Télécharger le rapport
def download_flex_report(reference_code):
    download_url = "https://gdcdyn.interactivebrokers.com/Universal/servlet/FlexStatementService.GetStatement"
    params = {
        "t": FLEX_TOKEN,  # Token d'authentification
        "q": reference_code  # Code de référence du rapport
    }

    response = requests.get(download_url, params=params)

    if response.status_code == 200:
        print("Rapport téléchargé avec succès !")

        return response.text
    else:
        print("Erreur lors du téléchargement du rapport :", response.text)
        return None


# Étape 3 : Convertir le XML en DataFrame et filtrer par année
def process_flex_report(xml_data):
    # Charger le XML dans pandas (ou lxml en cas de structure complexe)
    try:
        df = pd.read_xml(xml_data)

        # Filtrer les données pour l'année en cours
        current_year = datetime.now().year
        df['TradeDate'] = pd.to_datetime(df['TradeDate'], errors='coerce')
        df_filtered = df[df['TradeDate'].dt.year == current_year]

        # Enregistrer le fichier en CSV
        output_file = "flex_query_report_current_year.csv"
        df_filtered.to_csv(output_file, index=False)
        print(f"Rapport filtré enregistré sous : {output_file}")
        return output_file
    except Exception as e:
        print("Erreur lors du traitement du rapport XML :", e)
        return None


# Main
if __name__ == "__main__":
    reference_code = request_flex_report()
    if reference_code:
        xml_data = download_flex_report(reference_code)
        if xml_data:
            process_flex_report(xml_data)