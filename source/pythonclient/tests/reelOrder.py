import time as tps
from threading import Thread

from connection_port import *
from marketHours import *
from placeOrder import *
from send_mail import *


# Current date in YYYY-MM-DD format
today = datetime.now().date()

# Connection details to IBKR
HOST = '127.0.0.1'
PORT = port()
CLIENT_ID = 1  # Unique for each connection

index = ['GERMANY', 'FRANCE', 'US9', 'ITALY', 'SPAIN', 'BELGIUM', 'US IPO','AUSTRALIA']
index = ['US9']
# Initialize the trading application
app = TradingApp(PORT)
app.connect(HOST, PORT, CLIENT_ID)

tps.sleep(2)
app.reqOpenOrders()
tps.sleep(3)
app.all_orderId()
tps.sleep(3)

data = pd.read_csv("C:\\TWS API\\source\\pythonclient\\tests\\Data\\positions.csv", index_col=0)

orders = ['buy','sell']

for country in index:
    print(country)

    # if opening_hours(country) == False:
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
            print('****   ' + row['STOCK'] + ' - ' + row['NAME'] + ' - ' + row['ORDER'] + ' - ' + str(
                row['BUY']) + ' - ' + str(
                row['DATE']) + '   ****')

            stock = row['STOCK'].split('.')[0]
            secType = "STK"
            exchange = "SMART"

            trailPercent = 4
            valq = 0
            if "US9" in country:
                currency = "USD"
                valq = 1000
            elif "US" in country and country != "US9":
                currency = "USD"
                valq = 1000
            elif "AUSTRALIA" in country:
                currency = "AUD"
                valq = 1000
            else:
                currency = "EUR"
                valq = 2000
                trailPercent = 3

            order_type = row['ORDER']
            quantity = valq // row['BUY']
            price = row['BUY']

            contract = app.create_contract(stock, secType, exchange, currency)

            if order_type == "BUY" :
            # if order_type == "BUY" and closing_hours(country):
                if app.find_position(stock):
                    continue

                tps.sleep(1)

                orderId_list = app.orderId_present(stock, "BUY", currency=currency)

                if len(orderId_list) != 0:
                    continue

                trailAmt = round(price * trailPercent / 100, 2)
                trailStopPrice = price - trailAmt
                order = buy_order(quantity)
                app.add_order(contract, order)

                order = app.trailing_stop_order(quantity, trailStopPrice=trailStopPrice, trailAmt=trailAmt,
                                                trailPercent=trailPercent)
                app.add_order(contract, order)
                tps.sleep(2)

            elif order_type == "SELL":
                try:
                    if app.find_position(stock):

                        app.reqOpenOrders()
                        tps.sleep(1)

                        orderId_list = app.orderId_present(stock, "SELL", currency=currency)

                        if len(orderId_list) != 0:
                            for num in orderId_list:
                                app.cancelOrder(num, manualCancelOrderTime=formatted_cancel_time)
                                tps.sleep(0.30)

                            quantity = data[stock]['Quantity']
                            trailPercent = 1
                            trailAmt = round(price * trailPercent / 100, 2)
                            order = app.trailing_stop_order(quantity, trailStopPrice=row['SELL'], trailAmt=trailAmt,
                                                            trailPercent=trailPercent)

                            app.add_order(contract, order)
                            tps.sleep(2)
                        else:
                            print("OrderId is empty")

                except Exception as e:
                    print("Error:", e)

app.sendOpenOrders()

# Run the app and disconnect after processing all files
try:
    con_thread = Thread(target=lambda: app.run())
    con_thread.start()

    con_thread.join()

    tps.sleep(3)


except Exception as e:
    print("Error:", e)
finally:
    app.disconnect()
