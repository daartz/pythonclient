import time

from datetime import datetime

today = datetime.now().date()
hour = datetime.now().hour

from reelOrder_V2 import *
from portfolio import *

import threading

from connection_port import port_pro_prod, port_perso_prod, port_perso_test

port_list = [port_perso_prod(), port_pro_prod(), port_perso_test()]

# index_pro = ['USX','EUROX','US IPO','US9A', 'US9B', 'US9C','CANADA', 'ITALY','SPAIN','BELGIUM','GERMANY','NDL',
# 'FRANCE','EUROFRANCE'] index_pro = ['US','EUROPE',"CANADA","US IPO"]
index_pro = ["ETF", "US", "CANADA", "DJI", "NASDAQ", "SP500"]
index_pro_2 = ["ETF", "CANADA", "US","DJI", "NASDAQ", "SP500"]
index_perso = ["ETF", "US IPO", "US", "CANADA","DJI", "NASDAQ", "SP500"]
index_test = ["ETF", "CANADA", "US IPO", "US9A", "US9B", "US9C", "US", "EUROPE"]


def process_reel_order(port_code, index, sendMail=True):
    try:
        process_orders(port_code, index, sendMail=sendMail)
    except Exception as e:
        print(f"Error processing open orders: {e}")


def process_portfolio(port_code):
    try:
        main_portfolio(port_code)
    except Exception as e:
        print(f"Error processing portfolio: {e}")


threads = []

for port in port_list:
    portfolio_thread = threading.Thread(target=process_portfolio, args=(port,))
    portfolio_thread.start()
    threads.append(portfolio_thread)

for port in port_list:
    if port == 4001 and hour > 10 :
        open_order_thread = threading.Thread(target=process_reel_order, args=(port, index_perso, True,))
        open_order_thread.start()
        threads.append(open_order_thread)

    elif port == 5001 and hour > 10 :
        open_order_thread = threading.Thread(target=process_reel_order, args=(port, index_pro, True,))
        open_order_thread.start()
        threads.append(open_order_thread)

    # elif port == 4002:
    #     # if hour < 20:
    #     print("TEST " + str(hour))
    #     open_order_thread = threading.Thread(target=process_reel_order, args=(port, index_test, True,))
    #     open_order_thread.start()
    #     threads.append(open_order_thread)

# Attendez que tous les threads se terminent
for thread in threads:
    thread.join()

print("Tous les threads ont terminé leur traitement.")
