import time as tps
import traceback

import pandas as pd

from marketHours import *
from placeOrder import *
from portfolio import *
from currency_conversion import *


def process_orders(port, index_list, sendMail=True):
    # Current date in YYYY-MM-DD format
    global levier, buyingPower
    today = datetime.now().date()
    hour = datetime.now().hour
    minute = datetime.now().minute
    multiple_levier = 5
    now = datetime.now()
    current_time = now.strftime("%H:%M")

    devises_valides = ['USD', 'EUR', 'CAD', 'GBP', 'CHF', 'JPY', 'SEK', 'NOK']

    # Connection details to IBKR
    HOST = '127.0.0.1'
    PORT = port

    CLIENT_ID = 1  # Unique for each connection

    # Initialize the trading application
    app = TradingApp(PORT)
    app.connect(HOST, PORT, CLIENT_ID)

    tps.sleep(2)
    app.reqOpenOrders()
    tps.sleep(8)
    app.all_orderId()
    tps.sleep(5)

    account_value_file = f"C:\\TWS API\\source\\pythonclient\\tests\\Data\\account_value_{port}.csv"
    df = pd.read_csv(account_value_file)

    result = df[(df["Key"] == "StockMarketValue") & (df["Currency"] == "BASE")]

    stockMarketValue = float(result["Val"].iloc[0]) if not result.empty else None

    print(f"({port}) StockMarketValue : " + str(stockMarketValue))

    result = df[(df["Key"] == "NetLiquidation")]

    netLiquidation = float(result["Val"].iloc[0]) if not result.empty else None

    print(f"({port}) NetLiquidation : " + str(netLiquidation))

    try:

        if port != 4002:
            levier = round(stockMarketValue / netLiquidation, 2)

            print(f"({port}) Levier : " + str(levier))
            buyingPower = round((netLiquidation * multiple_levier) - stockMarketValue, 2)

            print(f"({port}) BuyingPower : " + str(buyingPower))
    except Exception as e:
        levier = 1
        error_message = f"An unexpected error occurred: {e}\n\nTraceback:\n{traceback.format_exc()}"
        print(error_message)

    file = f"C:\\TWS API\\source\\pythonclient\\tests\\Data\\portfolio_{port}.csv"

    data = pd.read_csv(file, index_col=0)

    index = index_list

    df = data[data['UnrealizedPNL'] != 0.0]
    nb_stock = df['Stock'].count()
    print(f"({port}) Nb stocks: " + str(nb_stock))

    max_stock = 500

    ID_ACCOUNT = ""

    if port == 4001:
        max_stock = 150
        ID_ACCOUNT = 'U11227042'
    elif port == 5001:
        max_stock = 260
        ID_ACCOUNT = 'U16043850'
    orders = []

    if port in [5001]:
        if levier <= multiple_levier:
            orders = ['sell', 'buy', 'vad sell', 'vad buy']
            # orders = ['sell',  'vad buy']
        else:
            print("*** LEVIER DEPASSE ***")
            orders = ['sell', 'vad buy']
    elif port in [4001]:
        if levier <= multiple_levier:
            orders = ['sell','buy']
            # orders = ['sell']
        else:
            print("*** LEVIER DEPASSE ***")
            orders = ['sell']
    # elif port in [4002]:
    #     # pass
    #     orders = ['vad sell', 'vad buy','sell']

    for country in index:
        print(country)

        for order in orders:

            csv_file_path = f'C:\\Users\\daart\\OneDrive\\PROREALTIME\\Signals\\{country} {order} signals {today}.csv'

            if not os.path.exists(csv_file_path):
                print(f"File not found: {csv_file_path}")
                continue

            # Read the CSV file
            df = read_csv_with_encoding_and_delimiter_attempts(csv_file_path)

            if df is None:
                continue

            # Convert the 'DATE' column to datetime and filter for today's date
            df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce')

            # Filter the DataFrame for today's date
            df_today = df[df['DATE'].dt.date == today]

            # Process orders
            for index, row in df_today.iterrows():

                date = row['DATE'].strftime("%Y-%m-%d")

                if date != str(today):
                    continue

                print('-------------------------------------------------------------------')
                print("(" + str(port) + ') ****   ' + row['STOCK'] + ' - ' + row['NAME'] + ' - ' + row[
                    'ORDER'] + ' - ' + str(
                    row['BUY']) + ' - ' + str(
                    row['DATE']) + '   ****')

                stock = row['STOCK']

                if "." in stock:
                    stock = '.'.join(row['STOCK'].split('.')[:-1])

                secType = "STK"
                exchange = "SMART"
                stop_loss_price = centieme(float(row['SL']))
                trailPercent = centieme(float(row['SL %']))
                currency = row['DEVISE']
                print(currency)

                if currency not in devises_valides:
                    print("*********DEVISE INVALIDE*************")
                    continue

                valq = 0

                if "US" in country or country in ['DJI', 'SP500', 'NASDAQ']:
                    if port in [4001]:
                        valq += 500
                    else:
                        valq += 600

                elif "CANADA" in country:
                    if port in [4001]:
                        valq += 450
                    else:
                        valq += 600

                elif "ETF" in country:
                    if port in [4001]:
                        valq += 1500
                    else:
                        valq += 2000

                else:
                    valq += 600

                valq = convert_from_euro(valq, currency)
                print("Value in currency : "+ str(valq) + " " + currency)

                order_type = row['ORDER']

                quantity = valq // row['BUY']

                # if quantity == 0:
                #     quantity = 1

                price = row['BUY']

                # No penny stocks
                if "US" in country:
                    if price < 2:
                        continue
                else:
                    if price < 1:
                        continue

                if "US" in country and hour < 16:
                    continue
                if "EURO" in country and hour < 10:
                    continue
                if country in ['DJI', 'SP500', 'CANADA', 'NASDAQ'] and hour < 16:
                    continue

                contract = app.create_contract(stock, secType, exchange, currency)

                if order_type == "BUY":

                    if port != 4002 and buyingPower < 0:
                        print("BuyingPower < 0")
                        continue

                    if nb_stock > max_stock:
                        print("Maximum number of stocks reached")
                        continue

                    if row["SCORE"] < 4:
                        print("Score inférieur à 5")
                        continue

                    if quantity == 0:
                        print("0 stock")
                        continue

                    try:
                        if app.find_position(stock):
                            continue

                        tps.sleep(1)

                        orderId_list = app.orderId_present(stock, "BUY", currency=currency)

                        if len(orderId_list) != 0:
                            continue

                        order = buy_order(quantity)
                        # order.outsideRth = True
                        # order.account = ID_ACCOUNT
                        app.add_order(contract, order)

                        stop_loss_price = centieme(price * 0.90)  # 90% du prix d'achat
                        stop_order_pnl = stop_order(quantity, StopPrice=stop_loss_price, action="SELL")
                        stop_order_pnl.account = ID_ACCOUNT
                        app.add_order(contract, stop_order_pnl)

                        # trailAmt = price - stop_loss_price
                        #
                        # trailStopPrice = stop_loss_price
                        # order = app.trailing_stop_order(quantity, action="SELL", trailStopPrice=trailStopPrice,
                        #                                     trailAmt=trailAmt, trailPercent=trailPercent)
                        # # order.outsideRth = True
                        # app.add_order(contract, order)

                        tps.sleep(0.5)

                        nb_stock += 1
                        buyingPower -= valq

                    except:
                        pass

                elif order_type == "SELL":

                    try:

                        if app.find_position(stock):

                            orderId_list = app.orderId_present(stock, "SELL", currency=currency)

                            if orderId_list:
                                try:
                                    for num in orderId_list:
                                        app.cancelOrder(num)
                                        tps.sleep(1)

                                except Exception as e:
                                    print(e)

                            else:

                                print("OrderId is empty")

                            quantity = app.getPosition(stock)
                            print(quantity)

                            # order = app.trailing_stop_order(quantity, trailStopPrice=trailStopPrice, trailAmt=trailAmt,

                            #                                 trailPercent=trailPercent)

                            tps.sleep(0.5)

                            order = app.sell_order(quantity)
                            order.account = ID_ACCOUNT
                            order.outsideRth = False
                            app.add_order(contract, order)
                            tps.sleep(0.5)

                    except Exception as e:
                        print(e)
                        pass

                # Vente à découvert
                elif order_type == "VAD SELL":


                    if quantity == 0:
                        print("0 stock")
                        continue

                    if port in ['5001', '4001'] and row['MARKET'] not in ['DJI', 'SP500', 'CANADA', 'NASDAQ']:
                        continue

                    try:
                        # Vérifier si une position courte existe déjà pour l'action
                        # if app.find_position_vad(stock, position_type="SELL"):
                        if app.find_position(stock):
                            print("Position present ? " + str(app.find_position(stock)))
                            continue

                        tps.sleep(1)

                        orderId_list = app.orderId_present(stock, "SELL", currency=currency)

                        if len(orderId_list) != 0:
                            continue

                        # Placer l'ordre de vente à découvert
                        order = sell_short_order(quantity)  # Utiliser une fonction spécifique pour la vente à découvert
                        order.account = ID_ACCOUNT
                        order.outsideRth = False
                        app.add_order(contract, order)

                        # Calculer le trailing stop pour protéger la position
                        trailAmt = round(price * 0.08, 2)

                        trailStopPrice = round(price * 1.08, 2)

                        order = trailing_stop_order(quantity, action="BUY", trailStopPrice=trailStopPrice,
                                                    trailAmt=trailAmt,
                                                    trailPercent=8)

                        order.outsideRth = False
                        app.add_order(contract, order)
                        tps.sleep(0.5)

                    except:
                        pass

                elif order_type == "VAD BUY":  # Couvrir une position short

                    if port in ['5001', '4001'] and row['MARKET'] not in ['DJI', 'SP500', 'CANADA', 'NASDAQ']:
                        continue

                    try:
                        # Vérifier si une position short existe
                        if app.find_position_vad(stock, position_type="SELL"):
                            print("SELL position present ? " + str(app.find_position_vad(stock, position_type="SELL")))

                            # Vérifier si un ordre BUY exite
                            orderId_list = app.orderId_present(stock, "BUY", currency=currency)

                            # Si oui >> annuler l'ordre BUY
                            if len(orderId_list) != 0:
                                try:
                                    for num in orderId_list:
                                        app.cancelOrder(num)
                                        tps.sleep(0.5)

                                except Exception as e:
                                    print(e)

                            else:
                                print("OrderId is empty")

                            quantity = abs(app.getPosition(stock))  # Quantité pour couvrir la position short
                            tps.sleep(1)

                            print(quantity)
                            # Placer l'ordre de rachat pour couvrir la vente à découvert
                            order = buy_order(quantity)
                            order.outsideRth = False
                            order.account = ID_ACCOUNT
                            app.add_order(contract, order)
                            tps.sleep(0.5)
                    except:
                        pass

                # elif order_type == "VAD HOLD":
                #     #
                #     # if port in ['5001', '4001'] :
                #     #     continue
                #     # elif order_type == "VAD HOLD":
                #     try:
                #
                #         if app.find_position(stock):
                #
                #             orderId_list = app.orderId_present(stock, "BUY", currency=currency)
                #
                #             if orderId_list:
                #                 try:
                #                     for num in orderId_list:
                #                         app.cancelOrder(num)
                #                         tps.sleep(1)
                #
                #                 except Exception as e:
                #                     print(e)
                #
                #             else:
                #
                #                 print("OrderId is empty")
                #
                #             quantity = abs(app.getPosition(stock))
                #             print(quantity)
                #
                #
                #             # Calculer le trailing stop pour protéger la position
                #             trailAmt = round(price * 0.08, 2)
                #
                #             trailStopPrice = round(price * 1.08, 2)
                #
                #             order = trailing_stop_order(quantity, action="BUY", trailStopPrice=trailStopPrice,
                #                                         trailAmt=trailAmt,
                #                                         trailPercent=8)
                #
                #             order.outsideRth = False
                #             order.account = ID_ACCOUNT
                #             app.add_order(contract, order)
                #             tps.sleep(0.5)
                #
                #     except:
                #         pass

    # Disconnect after processing all files
    try:
        app.run()
        tps.sleep(2)
        app.disconnect()

    except Exception as e:
        print("Error:", e)

    finally:
        app.disconnect()
        # app.connect('127.0.0.1', '8000', '22')
        return False

# if __name__ == "__main__":
#
#     process_orders(port_pro_prod(), index_pro(), True)
#     sys.exit()
