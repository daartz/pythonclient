import time
from threading import Thread

import pandas as pd

from ibapi.client import EClient
from ibapi.contract import Contract
from ibapi.wrapper import EWrapper
from connection_port import port

class Trading_App(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.positions = {}  # Dictionnaire pour stocker les positions ouvertes
        self.data = pd.DataFrame(self.positions)

    def position(self, account, contract: Contract, pos, avgCost):
        # Callback qui reçoit les informations de position
        if pos > 0:
            position_type = "BUY"  # Position longue
        elif pos < 0:
            position_type = "SELL"  # Position courte
        else:
            position_type = "NEUTRAL"

        self.positions[contract.symbol] = {
            "Type": position_type,
            "Quantity": abs(pos),
            "Average Cost": round(avgCost,2),
            "Currency": contract.currency,
            "Instrument": contract.secType
        }

        self.data = pd.DataFrame(self.positions)
        self.data = self.data.loc[:, self.data.loc["Quantity"] != 0]
        self.data.to_csv("C:\\TWS API\\source\\pythonclient\\tests\\Data\\positions.csv",index = True)

    def positionEnd(self):
        # Callback indiquant la fin de la transmission des positions
        self.disconnect()  # Déconnexion après avoir reçu toutes les positions

    def retPositions(self):
        return self.positions

    def present(self,action, type, currency="USD"):
        present = False
        data = self.data
        reponse = "SYMBOL : " + data[action].name + " - POSITION : " + data[action]['Type'] + " - QUANTITY : " + str(
                        data[action]['Quantity'])

        try:
            if data[action].name and data[action]['Type'] == type and data[action]['Currency'] == currency:
                print("Position présente")
                print(reponse)
                present = True
            else:
                print("Symbol présent mais position absente")
                print("SYMBOL : " + action + " - POSITION : " + type)
                print("----------------------------------------------")
                print("Position actuelle pour " + action)

        except:
            print("Position absente")
            print("SYMBOL : " + action + " - POSITION : " + type)

        return present


def main():
    app = Trading_App()
    # PORT = 7497
    PORT = port()
    app.connect("127.0.0.1", PORT, clientId=5)

    con_thread = Thread(target=lambda: app.run())
    con_thread.start()

    time.sleep(1)  # Laisser le temps pour la connexion

    app.reqPositions()  # Demander les positions ouvertes
    pos = app.retPositions()
    time.sleep(1)  # Attendre la réception des données de position

    con_thread.join()  # Attendre que le thread se termine proprement
    #
    # app.present('AMZN', 'BUY',"USD")
    print(pos)

    time.sleep(1)
    # app.connect("127.0.0.1", 7801, clientId=1)


if __name__ == "__main__":
    main()
