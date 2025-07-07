from threading import Timer

from ibapi.client import EClient
from ibapi.contract import Contract
from ibapi.wrapper import EWrapper
from send_mail import *


def index_suffix(symbol, exchange):
    exchange_suffix_mapping = {
        "AEB": ".AS",  # Amsterdam
        "SBF": ".PA",  # Paris
        "IBIS": ".DE",  # Germany
        "SWX": ".VX",  # Switzerland
        "BVME": ".MI",  # Italy
        "BM": ".MC",  # Spain
        "ISE": ".IR",  # Ireland
        "HEL": ".HE",  # Finland
        "CSE": ".CO",  # Denmark
        "OSE": ".OL",  # Norway
        "VSE": ".VI",  # Austria
        "ENEXT.BE": ".BR",  # Belgium
        "LISB": ".LS",  # Portugal
        "AT": ".AT",  # Greece
        # "NYSE": ".NY",
        # "NASDAQ": ".OQ",
        "LSE": ".L",  # UK
        "SIX": ".SW",
        "HKSE": ".HK",  # HONG KONG
        # "TSX": ".TO",
        "ASX": ".AX",  # AUSTRALIA
        "TSE": ".TO",  # CANADA
        "BSE": ".BO",
        # "NSE": ".NS",
        # Ajoutez d'autres échanges et leurs suffixes ici
    }

    suffix = exchange_suffix_mapping.get(exchange, "")
    return f"{symbol}{suffix}"


class TestApp(EWrapper, EClient):
    def __init__(self, send_email=False, account_code=""):
        EClient.__init__(self, self)
        self.account_code = account_code
        self.portfolio = {}
        self.accountName = []
        self.symbol = []
        self.stock = []
        self.sectype = []
        self.exchange = []
        self.position = []
        self.marketprice = []
        self.marketvalue = []
        self.averagecost = []
        self.rate = []
        self.unrealizedPNL = []
        self.realizedPNL = []
        self.account = ""
        self.accountvalue = {}
        self.key = []
        self.val = []
        self.currency = []
        self.conid = []
        self.accountname2 = []
        self.port_code = None  # New attribute to store the port code
        self.send_email = send_email

    # def error(self, reqId, errorCode, errorString):
    #     print("Error: ", reqId, " ", errorCode, " ", errorString)

    def nextValidId(self, orderId):
        self.start()

    def updatePortfolio(self, contract: Contract, position: float, marketPrice: float, marketValue: float,
                        averageCost: float, unrealizedPNL: float, realizedPNL: float, accountName: str):
        # print("UpdatePortfolio.", "Symbol:", contract.symbol, "SecType:", contract.secType, "Exchange:", contract.exchange,
        #       "Position:", position, "MarketPrice:", marketPrice, "MarketValue:", marketValue, "AverageCost:", averageCost,
        #       "UnrealizedPNL:", unrealizedPNL, "RealizedPNL:", realizedPNL, "AccountName:", accountName)

        try:
            rate = ((marketPrice / averageCost) - 1) * 100
        except:
            rate = 0

        self.accountName.append(accountName)
        self.symbol.append(contract.symbol)
        self.stock.append(index_suffix(contract.symbol, contract.primaryExchange))
        self.sectype.append(contract.secType)
        self.exchange.append(contract.primaryExchange)
        # self.currency.append(contract.currency)
        self.conid.append(contract.conId)
        self.position.append(position)
        self.marketprice.append(round(marketPrice, 2))
        self.marketvalue.append(round(marketValue, 2))
        self.averagecost.append(round(averageCost, 2))
        self.rate.append(round(rate, 2))
        self.unrealizedPNL.append(round(unrealizedPNL, 2))
        self.realizedPNL.append(round(realizedPNL, 2))

    def updateAccountValue(self, key: str, val: str, currency: str, accountName: str):
        # print("UpdateAccountValue. Key:", key, "Value:", val, "Currency:", currency, "AccountName:", accountName)

        if any(keyword in key for keyword in
               ['Account', 'Bond', 'FundV', 'Future', 'Fx', 'Issue', 'Option', 'Warrant', 'RealCu', 'Currency',
                'Exchange']):
            pass
        elif val == '0.00':
            pass
        else:
            self.key.append(key)
            self.val.append(val)
            self.currency.append(currency)
            self.accountname2.append(accountName)

    def updateAccountTime(self, timeStamp: str):
        # print("UpdateAccountTime. Time:", timeStamp)
        pass

    def accountDownloadEnd(self, accountName: str):
        # print("AccountDownloadEnd. Account:", accountName)

        portfolio_file = f"C:\\TWS API\\source\\pythonclient\\tests\\Data\\portfolio_{self.port}.csv"
        account_value_file = f"C:\\TWS API\\source\\pythonclient\\tests\\Data\\account_value_{self.port}.csv"

        self.porfolio = {}
        # self.porfolio["AccountName"] = self.accountName
        self.porfolio["Symbol"] = self.symbol
        self.porfolio["Stock"] = self.stock
        # self.porfolio["SecType"] = self.sectype
        self.porfolio["Exchange"] = self.exchange
        self.porfolio["Position"] = self.position
        # self.porfolio["Currency"] = self.currency
        # self.porfolio["ConID"] = self.conid
        self.porfolio["MarketPrice"] = self.marketprice
        self.porfolio["MarketValue"] = self.marketvalue
        self.porfolio["AverageCost"] = self.averagecost
        self.porfolio["Rate"] = self.rate
        self.porfolio["UnrealizedPNL"] = self.unrealizedPNL
        self.porfolio["RealizedPNL"] = self.realizedPNL

        try:
            data = pd.DataFrame(self.porfolio)

            # Ajout des colonnes SENS et résultats W/L
            data["SENS"] = data["Position"].apply(lambda x: "Long" if x > 0 else ("Short" if x < 0 else "Neutre"))
            data["Ur W/L"] = data["UnrealizedPNL"].apply(lambda x: "W" if x > 0 else ("L" if x < 0 else "N"))
            data["R W/L"] = data["RealizedPNL"].apply(lambda x: "W" if x > 0 else ("L" if x < 0 else "N"))

            # Stats sur PNL non réalisé
            df_unr = data[data['UnrealizedPNL'] != 0.0]
            nb_unr = len(df_unr)
            ur_nb_win = len(df_unr[df_unr["Ur W/L"] == "W"])
            ur_nb_lose = len(df_unr[df_unr["Ur W/L"] == "L"])
            percentage_ur_win = round(ur_nb_win / nb_unr * 100, 2) if nb_unr else 0
            percentage_ur_lose = round(ur_nb_lose / nb_unr * 100, 2) if nb_unr else 0

            # Stats sur PNL réalisé
            df_r = data[data['RealizedPNL'] != 0.0]
            nb_r = len(df_r)
            r_nb_win = len(df_r[df_r["R W/L"] == "W"])
            r_nb_lose = len(df_r[df_r["R W/L"] == "L"])
            percentage_r_win = round(r_nb_win / nb_r * 100, 2) if nb_r else 0
            percentage_r_lose = round(r_nb_lose / nb_r * 100, 2) if nb_r else 0

            # Valeur globale
            mktValue = round(data["MarketValue"].sum(), 2)
            unrpnl = round(data["UnrealizedPNL"].sum(), 2)
            rpnl = round(data["RealizedPNL"].sum(), 2)
            txUnrpnl = round((unrpnl / mktValue) * 100, 2) if mktValue else 0

            data.to_csv(portfolio_file, index=False)

            if self.send_email:
                html_resume = f"""
                   <h3>IBKR Portfolio Summary ({self.accountName[0]})</h3>
                   <ul>
                       <li><b>Nb of Stocks (Unrealized PNL)</b>: {nb_unr}</li>
                       <li><b>Unrealized PNL</b>: {unrpnl} ({txUnrpnl}%)</li>
                       <li><b>Win %</b>: {percentage_ur_win}% | <b>Lose %</b>: {percentage_ur_lose}%</li>
                       <li><b>Nb of Stocks (Realized PNL)</b>: {nb_r}</li>
                       <li><b>Realized PNL</b>: {rpnl}</li>
                       <li><b>Win %</b>: {percentage_r_win}% | <b>Lose %</b>: {percentage_r_lose}%</li>
                       <li><b>Total Market Value</b>: {mktValue}</li>
                   </ul>
                   """

                html_table = data.to_html(index=False, border=1)

                html_data = html_resume + "<h3>Détail du Portefeuille</h3>" + html_table
                send_mail_html("IBKR TWS Portfolio " + self.accountName[0], html_data)
        except:

            if self.send_email:
                send_mail("IBKR TWS Portfolio " + str(self.port_code), "No Account data to send")
            else:
                pass

        try:

            self.accountvalue = {}
            self.accountvalue["Key"] = self.key
            self.accountvalue['Val'] = self.val
            self.accountvalue["Currency"] = self.currency
            # self.accountvalue['AccountName']= self.accountname2

            data = pd.DataFrame(self.accountvalue)
            data = data.sort_values(by="Key")
            data.to_csv(account_value_file, index=False)

            if self.send_email:
                html_data = '<p>(TWS) Account Value : ' + self.accountname2[0] + '</p>' + data.to_html(index=False)
                send_mail_html("IBKR TWS Account Value " + self.accountname2[0], html_data)

        except:
            if self.send_email:
                send_mail("IBKR TWS Account Value " + str(self.port_code), "No Account data to send")
            else:
                pass

    def start(self):
        # Account number can be omitted when using reqAccountUpdates with single account structure
        if self.port == 4001:
            self.account_code = "U11227042"
        self.reqAccountUpdates(True, self.account_code)
        self.portfolio = {}
        # self.port_code = f"{self.host}_{self.port}"
        self.port_code = f"{self.port}"

    def stop(self):
        self.reqAccountUpdates(False, "")
        self.done = True
        self.disconnect()


def main_portfolio(port, send_email=False, account_code=""):
    app = TestApp(send_email, account_code)
    app.connect("127.0.0.1", port, 0)

    Timer(5, app.stop).start()

    app.run()

# if __name__ == "__main__":
#     main_portfolio()
