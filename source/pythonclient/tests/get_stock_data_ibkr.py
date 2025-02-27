from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import pandas as pd
import time

class IBApi(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.data = []

    def historicalData(self, reqId, bar):
        self.data.append([bar.date, bar.open, bar.high, bar.low, bar.close, bar.volume])

    def historicalDataEnd(self, reqId, start, end):
        print("✅ Données récupérées.")
        self.disconnect()

def get_stock_data_ibkr(ticker, start_date, end_date, bar_size="1 day"):
    print(f"🔄 Récupération des données pour {ticker} ({start_date} → {end_date}, {bar_size})")

    app = IBApi()
    app.connect("127.0.0.1", 4002, clientId=1)  # 🔹 Vérifie bien le port (7497 = paper, 7496 = live)

    contract = Contract()
    contract.symbol = ticker
    contract.secType = "STK"
    contract.exchange = "SMART"
    contract.currency = "USD"

    app.reqHistoricalData(
        reqId=1,
        contract=contract,
        endDateTime=end_date,
        durationStr="1 Y",
        barSizeSetting=bar_size,
        whatToShow="TRADES",
        useRTH=1,
        formatDate=1,
        keepUpToDate=False,
        chartOptions=[]  # 🔹 Correction de l'erreur TypeError
    )

    app.run()

    df = pd.DataFrame(app.data, columns=["Date", "Open", "High", "Low", "Close", "Volume"])
    df["Date"] = pd.to_datetime(df["Date"])
    df.set_index("Date", inplace=True)

    return df

# ✅ Exemple d'utilisation
ticker = "AAPL"
start_date = "20240101 00:00:00"
end_date = "20240215 00:00:00"

df = get_stock_data_ibkr(ticker, start_date, end_date, "1 day")
print(df.head())
