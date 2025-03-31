import time

from connection_port import *
from portfolio import *
from openOrder import *
from reelOrder_V2 import *

import threading

# port_list = [port_perso_prod(), port_pro_prod(), port_perso_test()]
port_list = [port_perso_prod(), port_pro_prod()]

def process_portfolio(port_code):
    try:
        account_code = ""
        if port_code ==4001:
            account_code = "U11227042"
        main_portfolio(port_code, send_email=True)

    except Exception as e:
        print(f"Error processing portfolio: {e}")

def process_open_order(port_code):
    try:
        main_openOrder(port_code)
    except Exception as e:
        print(f"Error processing open orders: {e}")


threads = []

for port in port_list:
    print("PORT TEST "+ str(port))
    portfolio_thread = threading.Thread(target=process_portfolio, args=(port,))
    portfolio_thread.start()
    threads.append(portfolio_thread)

for port in port_list:
    open_order_thread = threading.Thread(target=process_open_order, args=(port,))
    open_order_thread.start()
    threads.append(open_order_thread)

# Attendez que tous les threads se terminent
for thread in threads:
    thread.join()


print("Tous les threads ont terminé leur traitement.")
