import csv
import threading
import time
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
client.connect("127.0.0.1", port(), 1)

# Starting the client on a separate thread

tps.sleep(1)  # Give it a moment to establish the connection

indices = ["FRANCE", "BELGIUM", "ITALY", "US9","US8", "GERMANY", "SPAIN", "UK","US IPO1","US IPO2","US5","US6","US7"]

file = "C:\\Users\\daart\\OneDrive\\PROREALTIME\\Stocks list V2.csv"
file = "C:\\Users\\daart\\OneDrive\\PROREALTIME\\STOCK IPO US.csv"

dict = {}
market = []
stock = []
devise = []

with open(file, "r", encoding='latin-1') as f:
    reader = csv.reader(f, delimiter=",")
    for i in reader:
        # if i[3] in indices:
            # if "US" in i[3]:
            #     devise.append("USD")
            # else:
            #     devise.append("EUR")
        devise.append("USD")
        market.append("US")
        stock.append(i[1])

dict['MARKET'] = market
dict['STOCK'] = stock
dict['DEVISE'] = devise

thread = threading.Thread(target=client.run)
thread.start()

for i in range(len(stock)):
    get_conid(client, stock[i], currency=devise[i])
    time.sleep(0.1)

time.sleep(5)  # Wait for all responses to come in

client.disconnect()
thread.join()
print(client.contract_details.items())


# Écriture dans un fichier CSV
with open('contract_details IPO.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Symbol', 'Currency', 'conId'])
    for req_id, details in client.contract_details.items():
        writer.writerow([stock[req_id -1], details['currency'], details['conId']])

print("CSV file written successfully.")
