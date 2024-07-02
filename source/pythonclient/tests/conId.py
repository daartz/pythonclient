import csv
import threading
import time as tps
from connection_port import *
from ibapi.client import EClient
from ibapi.contract import Contract
from ibapi.wrapper import EWrapper


class TWSClient(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.contract_details = {}
        self.reqId = 1

    def nextReqId(self):
        reqId = self.reqId
        self.reqId += 1
        return reqId

    def contractDetails(self, reqId, contractDetails):
        # Stocker le conId et la devise
        self.contract_details[reqId] = {
            'conId': contractDetails.contract.conId,
            'currency': contractDetails.contract.currency
        }

    def contractDetailsEnd(self, reqId):
        print(f"Contract details received for request {reqId}")


def get_conid(client, symbol, sec_type="STK", currency="USD", exchange="SMART"):
    contract = Contract()
    contract.symbol = symbol
    contract.secType = sec_type
    contract.currency = currency
    contract.exchange = exchange

    req_id = client.nextReqId()
    client.reqContractDetails(req_id, contract)
    return req_id


client = TWSClient()
client.connect("127.0.0.1", 5001, 1)

# Starting the client on a separate thread

tps.sleep(1)  # Give it a moment to establish the connection

indices = ["FRANCE", "BELGIUM", "ITALY", "US9A","US9B", "GERMANY", "SPAIN", "NDL","CANADA","AUSTRALIA"]
indices = ["AUSTRALIA"]

file = "C:\\Users\\daart\\OneDrive\\PROREALTIME\\Stocks list V2.csv"
# file = "C:\\Users\\daart\\OneDrive\\PROREALTIME\\STOCK IPO US.csv"

dict = {}
market = []
stock = []
devise = []

file = "C:\\Users\\daart\\OneDrive\\PROREALTIME\\Stocks list V2.csv"


with open(file, "r", encoding='latin-1') as f:
    reader = csv.reader(f, delimiter=";")
    for i in reader:
        if i[3] in indices:
            if "US" in i[3]:
                devise.append("USD")
                market.append("US")
            elif "CANADA" in i[3]:
                devise.append("CAD")
                market.append("CANADA")
            elif "AUSTRALIA" in i[3]:
                devise.append("AUS")
                market.append("AUTRALIA")
            elif "FRANCE" in i[3]:
                devise.append("EUR")
                market.append("FRANCE")
            elif "NDL" in i[3]:
                devise.append("EUR")
                market.append("NDL")
            elif "GERMANY" in i[3]:
                devise.append("EUR")
                market.append("GERMANY")
            elif "SPAIN" in i[3]:
                devise.append("EUR")
                market.append("SPAIN")
            elif "ITALY" in i[3]:
                devise.append("EUR")
                market.append("ITALY")
            elif "EUROFRANCE" in i[3]:
                devise.append("EUR")
                market.append("EUROFRANCE")
            else:
                devise.append("EUR")
                market.append("EUROPE")
            stock.append(i[6])

dict['MARKET'] = market
dict['STOCK'] = stock
dict['DEVISE'] = devise

thread = threading.Thread(target=client.run)
thread.start()

for i in range(len(stock)):
    get_conid(client, stock[i], currency=devise[i])
    tps.sleep(0.2)

tps.sleep(5)  # Wait for all responses to come in

client.disconnect()
thread.join()
print(client.contract_details.items())


# Écriture dans un fichier CSV
with open('contract_details GLOBAL.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Symbol', 'Currency', 'conId'])
    for req_id, details in client.contract_details.items():
        writer.writerow([stock[req_id -1], details['currency'], details['conId']])

print("CSV file written successfully.")
