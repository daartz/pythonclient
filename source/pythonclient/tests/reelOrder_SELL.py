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
    tps.sleep(10)
    app.all_orderId()
    tps.sleep(5)

    file = f"C:\\TWS API\\source\\pythonclient\\tests\\Data\\portfolio_{port}.csv"

    data = pd.read_csv(file, index_col=0)

    index = index_list

    orders = ['sell']

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
                    valq = 750
                    trailPercent = 5
                elif "US" in country and country != "US9":
                    currency = "USD"
                    valq = 750
                    trailPercent = 5
                else:
                    currency = "EUR"
                    valq = 1500
                    trailPercent = 3

                order_type = row['ORDER']

                quantity = valq // row['BUY']

                if quantity == 0:
                    quantity = 1

                price = row['BUY']

                # No penny stocks
                if price < 1:
                    continue

                contract = app.create_contract(stock, secType, exchange, currency)

                if order_type == "SELL":
                    try:
                        if app.find_position(stock):

                            orderId_list = app.orderId_present(stock, "SELL", currency=currency)

                            if len(orderId_list) != 0:
                                for num in orderId_list:
                                    app.cancelOrder(num, manualCancelOrderTime=formatted_cancel_time)
                                    tps.sleep(0.30)

                            else:
                                print("OrderId is empty")

                            quantity = app.getPosition(stock)
                            trailPercent =trailPercent
                            trailAmt = round(price * trailPercent / 100, 2)
                            trailStopPrice = price - trailAmt
                            order = app.stop_order(quantity, trailStopPrice=round(trailStopPrice,2))
                            tps.sleep(1)

                            app.add_order(contract, order)
                            tps.sleep(1)

                    except Exception as e:
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

if __name__ == "__main__":

    indice = ['US9', 'ITALY','SPAIN','BELGIUM','GERMANY','NDL','EUROFRANCE','US IPO']
    process_orders(port_pro_prod(), indice, True)
    sys.exit()
