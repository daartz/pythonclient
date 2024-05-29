import os
import threading
import time

import pandas as pd
from datetime import datetime
import time as tps
from placeOrder import *
from portfolio import *
import sys
from connection_port import *
from marketHours import *

def process_orders(port, index_list, sendMail = True):
    # Current date in YYYY-MM-DD format
    today = datetime.now().date()

    # Connection details to IBKR
    HOST = '127.0.0.1'
    PORT = port

    CLIENT_ID = 1  # Unique for each connection

    # Initialize the trading application
    app = TradingApp(PORT)
    app.connect(HOST, PORT, CLIENT_ID)

    tps.sleep(2)
    app.reqOpenOrders()
    tps.sleep(5)
    app.all_orderId()
    tps.sleep(5)

    file = f"C:\\TWS API\\source\\pythonclient\\tests\\Data\\portfolio_{port}.csv"

    data = pd.read_csv(file, index_col=0)

    index = index_list

    orders = ['buy','sell']

    for country in index:
        print(country)

        # if opening_hours(country) == False:
        #     continue
        #
        # if closing_hours(country) == False:
        #     continue

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

            df_today = df_today[df_today['ORDER'] != 'HOLD']

            # Process orders
            for index, row in df_today.iterrows():
                date = row['DATE'].strftime("%Y-%m-%d")

                if date != str(today):
                    continue

                print('-------------------------------------------------------------------')
                print("("+ str(port) +') ****   ' + row['STOCK'] + ' - ' + row['NAME'] + ' - ' + row['ORDER'] + ' - ' + str(
                    row['BUY']) + ' - ' + str(
                    row['DATE']) + '   ****')

                stock = row['STOCK'].split('.')[0]
                secType = "STK"
                exchange = "SMART"

                trailPercent = 5
                valq = 0
                if "US9" in country:
                    currency = "USD"
                    valq = 1000
                    trailPercent = 5
                elif "US" in country and country != "US9":
                    currency = "USD"
                    valq = 1000
                    trailPercent = 5
                else:
                    currency = "EUR"
                    valq = 1500
                    trailPercent = 5

                order_type = row['ORDER']

                quantity = valq // row['BUY']

                if quantity == 0:
                    quantity = 1

                price = row['BUY']

                # No penny stocks
                if price < 1:
                    continue

                contract = app.create_contract(stock, secType, exchange, currency)

                # if order_type == "BUY" and closing_hours(country):
                if order_type == "BUY" :
                    try:
                        if app.find_position(stock):
                            continue

                        tps.sleep(1)

                        orderId_list = app.orderId_present(stock, "BUY", currency=currency)

                        if len(orderId_list) != 0:
                            continue

                        trailAmt = round(price * trailPercent / 100, 2)
                        trailStopPrice =round(price - trailAmt,2)
                        buyOrder = buy_order(quantity)
                        app.add_order(contract, buyOrder)

                        tps.sleep(0.5)

                        trail0rder = app.trailing_stop_order(quantity, trailStopPrice=trailStopPrice, trailAmt=trailAmt,
                                                    trailPercent=trailPercent)
                        app.add_order(contract, trail0rder)
                        tps.sleep(1)

                    except:
                        pass

                elif order_type == "SELL":
                    try:
                        if app.find_position(stock):

                            app.reqOpenOrders()
                            tps.sleep(1)

                            orderId_list = app.orderId_present(stock, "SELL", currency=currency)
                            tps.sleep(0.3)

                            for num in orderId_list:
                                app.cancelOrder(num, manualCancelOrderTime=formatted_cancel_time)
                                tps.sleep(0.3)

                            quantity = app.getPosition(stock)
                            print("QUANTITY :" + str(quantity))

                            tps.sleep(0.3)

                            order = sell_order(quantity)
                            app.add_order(contract, order)
                            tps.sleep(1)


                    except Exception as e:
                        pass

    # current_minutes = datetime.now().minute
    # if 50 <= current_minutes <= 59:
    #     if sendMail:
    #         app.sendOpenOrders()



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
#     process_orders(port(), index_test(), True)
#     sys.exit()
