from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import threading
import time

class TradingApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)

    # Ajoutez ici d'autres méthodes nécessaires pour gérer les réponses de l'API

def run_loop():
    app.run()

app = TradingApp()
app.connect("127.0.0.1", 7497, clientId=100)  # Assurez-vous que le port est correct

# Démarrer la boucle de traitement des messages dans un thread séparé
api_thread = threading.Thread(target=run_loop, daemon=True)
api_thread.start()

# Attendre quelques secondes pour que la connexion soit établie
time.sleep(3)

# Ajoutez ici votre logique de trading ou de gestion de données

# Pour garder le script en cours d'exécution, utilisez une boucle ou un mécanisme similaire
# Par exemple, un simple input pour arrêter le script
input("Press Enter to exit\n")
