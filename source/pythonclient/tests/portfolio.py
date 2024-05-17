import pandas as pd

import sys
from send_mail import *

from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from threading import Timer

from connection_port import *


class TestApp(EWrapper, EClient):
    def __init__(self, send_email = False):
        EClient.__init__(self, self)
        self.portfolio ={}
        self.accountName = []
        self.symbol =[]
        self.sectype = []
        self.exchange =[]
        self.position =[]
        self.marketprice = []
        self.marketvalue =[]
        self.averagecost = []
        self.unrealizedPNL = []
        self.realizedPNL = []
        self.account = ""
        self.accountvalue = {}
        self.key = []
        self.val =[]
        self.currency =[]
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

        self.accountName.append(accountName)
        self.symbol.append(contract.symbol)
        self.sectype.append(contract.secType)
        self.exchange.append(contract.exchange)
        self.position.append(position)
        self.marketprice.append(round(marketPrice,2))
        self.marketvalue.append(round(marketValue,2))
        self.averagecost.append(round(averageCost,2))
        self.unrealizedPNL.append(round(unrealizedPNL,2))
        self.realizedPNL.append(round(realizedPNL,2))


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
        self.porfolio["Symbol"]=  self.symbol
        self.porfolio["SecType"] = self.sectype
        self.porfolio["Exchange"]= self.exchange
        self.porfolio["Position"] = self.position
        self.porfolio["MarketPrice"] = self.marketprice
        self.porfolio["MarketValue"] = self.marketvalue
        self.porfolio["AverageCost"]= self.averagecost
        self.porfolio ["UnrealizedPNL"] = self.unrealizedPNL
        self.porfolio ["RealizedPNL"] = self.realizedPNL
        


        try:
            data = pd.DataFrame(self.porfolio)
            nb = data["Symbol"].count()
            unrpnl = round(data["UnrealizedPNL"].sum(),2)
            rpnl = round(data["RealizedPNL"].sum(),2)

            data.to_csv(portfolio_file, index = False)

            if self.send_email:

                html_data = '<p>(TWS) Portfolio : '+ self.accountName[0]+' </p><p>Nb of Stocks : '+ str(nb)+ '</p><p>Unrealized PNL : '+\
                            str(unrpnl)+'</p><p>Realized PNL : '+ str(rpnl)+'</p>'+ data.to_html()
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
            data.to_csv(account_value_file, index = False)

            if self.send_email:

                html_data = '<p>(TWS) Account Value : ' + self.accountname2[0] +'</p>' + data.to_html()
                send_mail_html("IBKR TWS Account Value " + self.accountname2[0] , html_data)

        except:
            if self.send_email:
                send_mail("IBKR TWS Account Value " + str(self.port_code), "No Account data to send")
            else:
                pass


    def start(self):
        # Account number can be omitted when using reqAccountUpdates with single account structure
        self.reqAccountUpdates(True, "")
        self.portfolio = {}
        # self.port_code = f"{self.host}_{self.port}"
        self.port_code = f"{self.port}"


    def stop(self):
        self.reqAccountUpdates(False, "")
        self.done = True
        self.disconnect()

def main_portfolio(port, send_email = False):
    app = TestApp(send_email)
    app.connect("127.0.0.1", port, 0)

    Timer(5, app.stop).start()

    app.run()

# if __name__ == "__main__":
#     main_portfolio(port())