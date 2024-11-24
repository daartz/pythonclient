import os
import subprocess
import sys
import time
from datetime import datetime, timedelta
import csv
from send_mail import *
import math


def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])


try:
    import pandas as pd
    from ibapi.client import EClient
except ImportError:
    print("Pandas n'est pas installé. Installation en cours...")
    install_package("pandas")
    install_package("ibapi")

    import pandas as pd

from ibapi.client import EClient
from ibapi.contract import Contract
from ibapi.order import Order
from ibapi.order_condition import PriceCondition
from ibapi.wrapper import EWrapper

# Exemple d'heure d'annulation : 24 heures à partir de maintenant, en UTC
cancel_time = datetime.utcnow() + timedelta(days=1)
formatted_cancel_time = cancel_time.strftime("%Y%m%d-%H:%M:%S")


# Fonction pour créer un contrat
def create_contract(symbol, secType, exchange, currency):
    contract = Contract()
    contract.symbol = symbol
    contract.secType = secType
    contract.exchange = exchange
    contract.currency = currency

    print("Contract created :" + symbol + " - " + secType + " - " + exchange + " - " + currency)
    return contract


# Fonction pour créer un ordre
def buy_order(quantity):
    order = Order()
    order.orderType = "MKT"
    order.totalQuantity = quantity
    order.action = "BUY"
    order.eTradeOnly = False
    order.firmQuoteOnly = False
    order.transmit = True
    # order.outsideRth = True

    print("Buy Order created : " + order.orderType + " - Qty : " + str(order.totalQuantity) + " - " + order.action)
    return order


def stop_order(quantity, StopPrice, action="SELL"):
    order = Order()
    order.action = action
    order.orderType = "STP"
    order.auxPrice = StopPrice
    order.totalQuantity = quantity
    order.eTradeOnly = False
    order.firmQuoteOnly = False
    order.transmit = True

    print("Stop Order created : " + order.orderType + " - Qty : " + str(order.totalQuantity) + " - " + order.action)
    return order


def sell_order(quantity):
    order = Order()
    order.orderType = "MKT"
    order.totalQuantity = quantity
    order.action = "SELL"
    order.eTradeOnly = False
    order.firmQuoteOnly = False
    order.transmit = True
    # order.outsideRth = True

    print("Sell Order created : " + order.orderType + " - Qty : " + str(order.totalQuantity) + " - " + order.action)
    return order


def sell_short_order(quantity):
    order = Order()
    order.orderType = "MKT"  # Ordre au marché
    order.totalQuantity = quantity
    order.action = "SELL"  # Spécifie qu'il s'agit d'une vente à découvert
    order.eTradeOnly = False
    order.firmQuoteOnly = False
    order.transmit = True
    # order.outsideRth = True  # Permettre l'exécution en dehors des heures de marché (si nécessaire)

    print(
        "Sell Short Order created : " + order.orderType + " - Qty : " + str(order.totalQuantity) + " - " + order.action)
    return order


# Fonction pour créer un ordre stop limit suiveur
def trailing_stop_order(quantity, action='SELL', trailStopPrice=None, trailAmt=None, trailPercent=None):
    """
    Crée un ordre stop suiveur.

    :param trailStopPrice:
    :param action: 'BUY' ou 'SELL'
    :param quantity: Quantité d'actions à acheter ou vendre
    :param trailAmt: Montant du suivi (trailing amount) en points absolus
    :param trailPercent: Pourcentage du suivi
    :return: Un objet Order configuré comme un ordre stop suiveur
    """
    order = Order()
    order.action = action
    order.totalQuantity = quantity
    order.orderType = "TRAIL"

    order.eTradeOnly = False
    order.firmQuoteOnly = False
    order.timeInForce = 'GTC'
    order.transmit = True

    if trailStopPrice is not None:
        order.trailStopPrice = trailStopPrice

    if trailAmt is not None:
        order.auxPrice = trailAmt  # Montant du suivi en points absolus
    elif trailPercent is not None:
        order.trailPercent = trailPercent  # Pourcentage du suivi

    print("Trailing stop order created - quantity : " + str(quantity) + " - trailPercent : " + str(
        trailPercent) + " - trailAmt : " + str(
        trailAmt) + " - trailStopPrice : " + str(
        trailStopPrice))

    return order


# Classe TradingApp
def create_market_on_close_order(action, quantity, price, isMore, conId):
    order = Order()
    order.action = action
    order.totalQuantity = quantity
    order.orderType = "MOC"
    order.lmtPrice = price
    order.eTradeOnly = False
    order.firmQuoteOnly = False

    price_condition = PriceCondition()
    price_condition.triggerMethod = PriceCondition.TriggerMethodEnum.Last
    price_condition.conId = conId
    price_condition.exchange = "SMART"
    price_condition.price = price
    price_condition.isMore = isMore

    order.conditions.append(price_condition)
    return order


# Function to read a CSV file with various encoding and delimiter attempts
def read_csv_with_encoding_and_delimiter_attempts(file_path):
    encodings = ['utf-8', 'latin1', None]  # Include 'None' for default encoding
    delimiters = [';', ',']

    for encoding in encodings:
        for delimiter in delimiters:
            try:
                df = pd.read_csv(file_path, encoding=encoding, delimiter=delimiter)
                date = df['DATE']
                return df
            except:
                continue


class TradingApp(EWrapper, EClient):
    def __init__(self, port):
        EClient.__init__(self, self)
        self.nextOrderId = 0
        self.order_queue = []  # File d'attente pour les ordres
        self.conId = None
        self.positions = {}  # Dictionnaire pour stocker les positions ouvertes
        self.data = pd.DataFrame(self.positions)
        self.open_orders = []
        self.port_code = str(port)

    def create_contract(self, symbol, secType, exchange, currency):
        contract = Contract()
        contract.symbol = symbol
        contract.secType = secType
        contract.exchange = exchange
        contract.currency = currency

        print(
            "(" + self.port_code + ") Contract created :" + symbol + " - " + secType + " - " + exchange + " - " + currency)
        return contract

    def sell_order(self, quantity):
        order = Order()
        order.orderType = "MKT"
        order.totalQuantity = quantity
        order.action = "SELL"
        order.eTradeOnly = False
        order.firmQuoteOnly = False
        order.transmit = True

        print("SELL Order created : " + order.orderType + " - Qty : " + str(
            order.totalQuantity) + " - " + order.action)
        return order

    # Fonction pour créer un ordre stop limit suiveur
    def trailing_stop_order(self, quantity, action="SELL", trailStopPrice=None, trailAmt=None, trailPercent=None):
        """
        Crée un ordre stop suiveur.

        :param trailStopPrice:
        :param action: 'BUY' ou 'SELL'
        :param quantity: Quantité d'actions à acheter ou vendre
        :param trailAmt: Montant du suivi (trailing amount) en points absolus
        :param trailPercent: Pourcentage du suivi
        :return: Un objet Order configuré comme un ordre stop suiveur
        """
        order = Order()
        order.action = action
        order.totalQuantity = quantity
        order.orderType = "TRAIL"

        order.eTradeOnly = False
        order.firmQuoteOnly = False
        order.timeInForce = 'GTC'
        order.transmit = True

        if trailStopPrice is not None:
            order.trailStopPrice = trailStopPrice

        if trailAmt is not None:
            order.auxPrice = trailAmt  # Montant du suivi en points absolus
        elif trailPercent is not None:
            order.trailPercent = trailPercent  # Pourcentage du suivi

        print("(" + self.port_code + ") Trailing stop order created - quantity : " + str(
            quantity) + " - trailPercent : " + str(
            trailPercent) + " - trailAmt : " + str(
            trailAmt) + " - trailStopPrice : " + str(
            trailStopPrice))

        return order

    def start(self):
        self.reqAccountUpdates(True, "")
        self.port_code = f"{self.port}"

    def stop(self):
        self.reqAccountUpdates(False, "")
        self.done = True
        self.disconnect()

    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)
        self.nextOrderId = orderId
        self.process_order_queue()

    def process_order_queue(self):
        for contract, order in self.order_queue:
            self.placeOrder(self.nextOrderId, contract, order)
            self.nextOrderId += 1
        self.order_queue.clear()

    def add_order(self, contract, order):
        self.order_queue.append((contract, order))

    def check_if_order_exists(self, orderId: int) -> bool:
        # Vérifie si l'ordre avec l'ID donné existe dans le dictionnaire d'état
        with self.order_status_lock:
            return orderId in self.order_status and \
                self.order_status[orderId] not in ['Cancelled', 'Filled']

    def contractDetails(self, reqId, contractDetails):
        super().contractDetails(reqId, contractDetails)
        self.conId = contractDetails.contract.conId
        print("self.conId : ")
        print(self.conId)

    def place_order(self, contract, order):
        self.placeOrder(self.nextOrderId, contract, order)

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
            "Average Cost": round(avgCost, 2),
            "Currency": contract.currency,
            "Instrument": contract.secType
        }
        self.data = pd.DataFrame(self.positions)
        self.data = self.data.loc[:, self.data.loc["Quantity"] != 0]

        self.data.to_csv("C:\\TWS API\\source\\pythonclient\\tests\\Data\\positions" + self.port_code + ".csv",
                         index=False)

    def positionEnd(self):
        # Callback indiquant la fin de la transmission des positions
        self.disconnect()  # Déconnexion après avoir reçu toutes les positions

    def retPositions(self):
        return self.positions

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
        print("(" + self.port_code + ") Received all open orders. Saving to CSV file.")
        self.save_orders_to_csv()

    def save_orders_to_csv(self):
        """ Sauvegarder les informations sur les ordres collectées dans un fichier CSV """
        fields = ['index', 'orderId', 'symbol', 'secType', 'currency', 'action', 'orderType', 'totalQty', 'lmtPrice',
                  'auxPrice', 'status']
        # existing_order_ids = set()

        csv_file_path = f"C:\\TWS API\\source\\pythonclient\\tests\\Data\\open_orders_{self.port_code}.csv"

        if os.path.exists(csv_file_path):
            os.remove(csv_file_path)

        time.sleep(5)

        with open(csv_file_path, 'w', newline='') as file:  # Ouvrir en mode écriture ('w')
            writer = csv.DictWriter(file, fieldnames=fields)
            writer.writeheader()

            # Écrire tous les ordres à chaque fois
            for order in self.open_orders:
                writer.writerow(order)

        print(
            "(" + self.port_code + ") " + f"Les ordres en cours ont été sauvegardés dans open_orders_{self.port_code}.csv")
        time.sleep(2)

    def error(self, reqId, errorCode, errorString, *args):
        """ Handle errors with an additional arguments placeholder """
        print("(" + self.port_code + ") " + f"Error: {reqId}, {errorCode}, {errorString}")
        # if args:
        #     print(f"Additional info: {args}")

    def orderId_present(self, stock, side, currency="USD"):
        file = f"C:\\TWS API\\source\\pythonclient\\tests\\Data\\open_orders_{self.port_code}.csv"
        try:
            data = pd.read_csv(file, index_col=0)

            try:
                data = data.drop_duplicates(subset=['orderId'])
            except:
                pass

            data = data[data['action'] == side]
            data = data[data['symbol'] == stock]
            data = data[data['secType'] == 'STK']
            data = data[data['currency'] == currency]

            if stock in data['symbol'].values:  # Check if DataFrame is not empty
                print("(" + self.port_code + ") OrderId present")
                id_values = list(set(data['orderId'].values))
                print(id_values)
                return id_values
            else:
                print("(" + self.port_code + ") No orderId present")
                return []
        except Exception as e:
            print("(" + self.port_code + ") Error:", e)
            print("(" + self.port_code + ")No orderId present")
            return []

    def all_orderId(self):
        csv_file_path = f"C:\\TWS API\\source\\pythonclient\\tests\\Data\\open_orders_{self.port_code}.csv"

        if os.path.exists(csv_file_path) and os.path.getsize(csv_file_path) > 0:
            data = pd.read_csv(csv_file_path, index_col=0)
            try:
                data = data.drop_duplicates(subset=['orderId'])
            except:
                pass
            orderIds = list(set(data['orderId'].values))
            print("(" + self.port_code + ")----ALL ORDERID----")
            print(orderIds)
            return orderIds
        else:
            return []

    def sendOpenOrders(self):
        file = f"C:\\TWS API\\source\\pythonclient\\tests\\Data\\open_orders_{self.port_code}.csv"

        data = pd.read_csv(file, index_col=0)

        data = data.reset_index(drop=True)

        try:
            data = data.drop_duplicates(subset=['orderId'])
        except:
            pass

        html_data = '<p>(TWS) Open Orders (from reelOrders.py)</p>' + data.to_html()

        send_mail_html("IBKR TWS Open Orders " + str(self.port_code), html_data)

    def find_position(self, stock):
        present = False

        file = f"C:\\TWS API\\source\\pythonclient\\tests\\Data\\portfolio_{self.port_code}.csv"
        data = pd.read_csv(file)

        try:
            if (data['Symbol'] == stock).any():
                print("(" + self.port_code + ") " + stock + ": stock present")
                present = True
            else:
                print("(" + self.port_code + ") " + stock + ": stock not present")

        except Exception as e:
            print(stock + ": Error occurred:", e)
            print(stock + ": Stock not present")

        return present

    def find_position_vad(self, stock, position_type="BUY"):
        """
        Vérifie si le stock est présent dans le portefeuille avec la position longue ou courte.
        Args:
            stock (str): Le symbole de l'action à rechercher.
            position_type (str): Type de position à vérifier, "long" ou "short".
        Returns:
            bool: True si la position est présente, sinon False.
        """
        present = False

        file = f"C:\\TWS API\\source\\pythonclient\\tests\\Data\\portfolio_{self.port_code}.csv"
        data = pd.read_csv(file)

        try:
            if (data['Symbol'] == stock).any():
                print("(" + self.port_code + ") " + stock + ": stock present")
                present = True
            else:
                print("(" + self.port_code + ") " + stock + ": stock not present")

        except Exception as e:
            print(stock + ": Error occurred:", e)
            print(stock + ": Stock not present")

        return present

    def getPosition(self, stock):
        position = 0
        file = f"C:\\TWS API\\source\\pythonclient\\tests\\Data\\portfolio_{self.port_code}.csv"
        data = pd.read_csv(file)

        try:
            filtered_data = data[data['Symbol'] == stock]
            if not filtered_data.empty:
                position = int(filtered_data.iloc[0]['Position'])
                if position != 0:
                    print("(" + self.port_code + ") Quantity for " + stock + " : " + str(position))
        except Exception as e:
            print("Error occurred:", e)

        return position

    # def error(self, reqId, errorCode, errorString, advancedOrderRejectJson=None):
    #     print("Error: ", reqId, " ", errorCode, " ", errorString)
    #     if advancedOrderRejectJson:
    #         print("Advanced order rejection info:", advancedOrderRejectJson)

def centieme(val):
    # Valeur initiale
    valeur = val

    # Arrondi au centième supérieur
    return math.ceil(valeur * 20) / 20
