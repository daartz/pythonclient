from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.ticktype import TickTypeEnum
import threading
import time

class IBKRWrapper(EWrapper):
    def __init__(self):
        EWrapper.__init__(self)
        self.dividend_data = {}

    def fundamentalData(self, reqId, data):
        print(f"FundamentalData. ReqId: {reqId}, Data: {data}")
        self.dividend_data[reqId] = data

class IBKRClient(EClient):
    def __init__(self, wrapper):
        EClient.__init__(self, wrapper)

class IBKRApp(IBKRWrapper, IBKRClient):
    def __init__(self):
        IBKRWrapper.__init__(self)
        IBKRClient.__init__(self, wrapper=self)

    def error(self, reqId, errorCode, errorString):
        print(f"Error. ReqId: {reqId}, Code: {errorCode}, Msg: {errorString}")

def run_loop():
    app.run()

if __name__ == "__main__":
    app = IBKRApp()

    # Connect to TWS or IB Gateway running on localhost with port 7497
    app.connect("127.0.0.1", 4001, clientId=0)

    # Start the socket in a thread
    api_thread = threading.Thread(target=run_loop, daemon=True)
    api_thread.start()

    # Define the stock contracts you are interested in
    stocks = ["AAPL", "MSFT", "GOOGL"]
    contracts = []

    for stock in stocks:
        contract = Contract()
        contract.symbol = stock
        contract.secType = "STK"
        contract.exchange = "SMART"
        contract.currency = "USD"
        contracts.append(contract)

    # Request fundamental data for each stock
    for i, contract in enumerate(contracts):
        app.reqFundamentalData(i, contract, "ReportsFinSummary", [])

    # Sleep to ensure data is received
    time.sleep(10)

    # Disconnect from TWS
    app.disconnect()

    # Print dividend data
    for reqId, data in app.dividend_data.items():
        print(f"Stock: {stocks[reqId]}")
        print(f"Dividend Data: {data}\n")
