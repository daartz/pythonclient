import csv
import os
import threading
import time
from datetime import datetime, timedelta
from send_mail import *
from connection_port import *
import pandas as pd

from ibapi.client import EClient
from ibapi.contract import Contract
from ibapi.order import Order
from ibapi.wrapper import EWrapper

# Exemple d'heure d'annulation : 24 heures à partir de maintenant, en UTC
cancel_time = datetime.utcnow() + timedelta(days=1)
formatted_cancel_time = cancel_time.strftime("%Y%m%d-%H:%M:%S")


class OpenOrdersApp(EWrapper, EClient):
    def __init__(self, port):
        EClient.__init__(self, self)
        self.open_orders = []
        self.port_code = port
        self.open_orders_file = ""

    def start(self):
        # Account number can be omitted when using reqAccountUpdates with single account structure
        self.reqAccountUpdates(True, "")

        # self.port_code = f"{self.host}_{self.port}"
        self.port_code = str(f"{self.port}")


    def openOrder(self, orderId, contract: Contract, order: Order, orderState):
        """ Callback to receive open order information """
        # Simplify and select the data you need
        order_info = {
            "index": len(self.open_orders) + 1,
            "orderId": orderId,
            "symbol": contract.symbol,
            "secType": contract.secType,
            "currency": contract.currency,
            "action": order.action,
            "orderType": order.orderType,
            "totalQty": order.totalQuantity,
            "lmtPrice": order.lmtPrice,
            "auxPrice": order.auxPrice,
            "status": orderState.status,
        }
        self.open_orders.append(order_info)

    def openOrderEnd(self):
        """ Indicates the end of the initial open orders' download """
        super().openOrderEnd()
        print("("+ str(self.port_code) +") Received all open orders. Saving to CSV file.")
        self.save_orders_to_csv()

    def save_orders_to_csv(self):
        """ Sauvegarder les informations sur les ordres collectées dans un fichier CSV """
        fields = ['index', 'orderId', 'symbol', 'secType', 'currency', 'action', 'orderType', 'totalQty', 'lmtPrice',
                  'auxPrice', 'status']
        # existing_order_ids = set()

        csv_file_path = f"C:\\TWS API\\source\\pythonclient\\tests\\Data\\open_orders_{self.port_code}.csv"

        if os.path.exists(csv_file_path):
            os.remove(csv_file_path)

        with open(csv_file_path, 'w', newline='') as file:  # Ouvrir en mode écriture ('w')
            writer = csv.DictWriter(file, fieldnames=fields)
            writer.writeheader()

            # Écrire tous les ordres à chaque fois
            for order in self.open_orders:
                writer.writerow(order)

        print(f"Les ordres en cours ont été sauvegardés dans open_orders_{self.port_code}.csv")

    def sendOpenOrders(self):
        data = pd.read_csv(f"C:\\TWS API\\source\\pythonclient\\tests\\Data\\open_orders_{self.port_code}.csv",
                           index_col=0)

        data = data.reset_index(drop=True)

        data = data.sort_values(by='symbol')

        html_data = '<p>(TWS) Open Orders</p>' + data.to_html()

        send_mail_html("IBKR TWS Open Orders "+ str(self.port_code), html_data)

    def error(self, reqId, errorCode, errorString, *args):
        """ Handle errors with an additional arguments placeholder """
        print(f"Error: {reqId}, {errorCode}, {errorString}")
        # if args:
        #     print(f"Additional info: {args}")

    def orderId_present(self, action, side, currency="USD"):
        try:
            print("OrderId present for " + action + ", side " + side)
            data = pd.read_csv(f"C:\\TWS API\\source\\pythonclient\\tests\\Data\\open_orders_{self.port_code}.csv",
                               index_col=0)
            data = data[data['action'] == side]
            data = data[data['symbol'] == action]
            data = data[data['secType'] == 'STK']
            data = data[data['currency'] == currency]

            if data is not None:
                return list(set(data['orderId'].values))
            else:
                return []
        except:
            pass

    def all_orderId(self):
        csv_file_path = f"C:\\TWS API\\source\\pythonclient\\tests\\Data\\open_orders_{self.port_code}.csv"

        if os.path.exists(csv_file_path) and os.path.getsize(csv_file_path) > 0:
            data = pd.read_csv(csv_file_path, index_col=0)
            print("----ALL ORDERID " + str(self.port_code) + "----")
            return list(set(data['orderId'].values))
        else:
            return []

def main_openOrder(port):
    app = OpenOrdersApp(port)
    app.connect("127.0.0.1", port, clientId=1)  # Make sure to match the port and clientId with your TWS/IB Gateway

    # Start the socket in a thread
    thread = threading.Thread(target=app.run)
    thread.start()

    time.sleep(1)  # Allow some time for the connection to establish

    #  Retrieve all open orders
    app.reqOpenOrders()
    time.sleep(3)
    # Retrieve specific orderId
    print(app.all_orderId())

    time.sleep(2)  # Wait for orders to be returned and processed

    app.sendOpenOrders()
    time.sleep(0.5)

    app.disconnect()  # Disconnect when done

# if __name__ == "__main__":
#     port_code = port()  # Assuming port() function returns your port code
#     main_openOrder(port_code)