import time as tps

from marketHours import *
from placeOrder import *
from portfolio import *


def process_orders(port, index_list, sendMail=True):
    # Current date in YYYY-MM-DD format
    today = datetime.now().date()
    hour = datetime.now().hour
    minute = datetime.now().minute

    now = datetime.now()
    current_time = now.strftime("%H:%M")

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

    file = f"C:\\TWS API\\source\\pythonclient\\tests\\Data\\portfolio_{port}.csv"

    data = pd.read_csv(file, index_col=0)

    index = index_list

    orders = []

    if port in [4001,5001]:
        # orders = ['sell', 'buy','hold']
        orders = ['sell', 'hold']
    elif port in [4002]:
        # pass
        orders = ['vad sell', 'vad buy', 'vad hold']

    for country in index:
        print(country)
        #
        # if port in [4001, 5001, 4002]:
        #     if opening_hours(country) == False:
        #         continue

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

                stock = row['STOCK'].split('.')[0]
                secType = "STK"
                exchange = "SMART"
                stop_lopp_price = centieme(float(row['SL']))
                trailPercent = centieme(float(row['SL %']))

                valq = 0

                if "US" in country:
                    currency = "USD"
                    if port in [4001]:
                        valq += 500
                    else:
                        valq += 550

                elif "CANADA" in country:
                    currency = "CAD"
                    if port in [4001]:
                        valq += 600
                    else:
                        valq += 650
                else:
                    currency = "EUR"
                    valq += 1200

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

                contract = app.create_contract(stock, secType, exchange, currency)

                if order_type == "BUY":

                    if row["SCORE"] < 5:
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
                        app.add_order(contract, order)

                        trailAmt = price - stop_lopp_price

                        trailStopPrice = stop_lopp_price

                        if "US" in country or "CANADA" in country:

                            order = stop_order(quantity, StopPrice=round(trailStopPrice, 2))

                        else:

                            order = app.trailing_stop_order(quantity, action="SELL", trailStopPrice=trailStopPrice,
                                                            trailAmt=trailAmt,
                                                            trailPercent=trailPercent)
                        # order.outsideRth = True
                        app.add_order(contract, order)
                        tps.sleep(0.5)

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
                            order.outsideRth = True
                            app.add_order(contract, order)
                            tps.sleep(0.5)

                    except Exception as e:
                        print(e)
                        pass

                elif order_type == "HOLD" and (10 > hour or hour > 22):

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

                            trailStopPrice = stop_lopp_price

                            order = stop_order(quantity, StopPrice=round(trailStopPrice, 2))

                            app.add_order(contract, order)
                            tps.sleep(0.5)

                    except:
                        pass

                elif order_type == "VAD SELL":  # Vente à découvert

                    if quantity == 0:
                        print("0 stock")
                        continue

                    try:
                        # Vérifier si une position courte existe déjà pour l'action
                        if app.find_position_vad(stock, position_type="SELL"):
                            continue

                        tps.sleep(1)

                        orderId_list = app.orderId_present(stock, "SELL_SHORT", currency=currency)

                        if len(orderId_list) != 0:
                            continue

                        # Placer l'ordre de vente à découvert
                        order = sell_short_order(quantity)  # Utiliser une fonction spécifique pour la vente à découvert
                        order.outsideRth = True
                        app.add_order(contract, order)

                        # Calculer le trailing stop pour protéger la position
                        trailAmt = price - stop_lopp_price

                        trailStopPrice = stop_lopp_price

                        if "US" in country or "CANADA" in country:
                            order = stop_order(quantity, StopPrice=round(trailStopPrice, 2), action="BUY")

                        else:
                            order = app.trailing_stop_order(quantity, action="BUY", trailStopPrice=trailStopPrice,
                                                            trailAmt=trailAmt,
                                                            trailPercent=trailPercent)
                        order.outsideRth = True
                        app.add_order(contract, order)
                        tps.sleep(0.5)

                    except:
                        pass

                elif order_type == "VAD BUY":  # Couvrir une position short

                    try:
                        # Vérifier si une position short existe
                        if app.find_position_vad(stock, position_type="SELL"):

                            orderId_list = app.orderId_present(stock, "BUY", currency=currency)

                            if len(orderId_list) != 0:
                                try:
                                    for num in orderId_list:
                                        app.cancelOrder(num)
                                        tps.sleep(0.5)

                                except Exception as e:
                                    print(e)

                            else:
                                print("OrderId is empty")
                            #
                            quantity = abs(app.getPosition(stock))  # Quantité pour couvrir la position short
                            tps.sleep(1)

                            print(quantity)
                            # Placer l'ordre de rachat pour couvrir la vente à découvert
                            order = buy_order(quantity)
                            order.outsideRth = True
                            app.add_order(contract, order)
                            tps.sleep(0.5)
                    except:
                        pass

                elif order_type == "VAD HOLD" and (10 > hour or hour > 22):

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

                            quantity = abs(app.getPosition(stock))
                            print(quantity)

                            trailStopPrice = stop_lopp_price

                            order = stop_order(quantity, StopPrice=round(trailStopPrice, 2), action="BUY")

                            app.add_order(contract, order)
                            tps.sleep(0.5)

                    except:
                        pass

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
