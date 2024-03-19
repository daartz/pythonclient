import time

from reelOrder_V2 import *
from portfolio import *

import threading

port_list = [port_perso_test(), port_perso_prod(), port_pro_prod()]

index_pro = [ 'US9']
index_perso = ['US IPO']
index_test = ['GERMANY', 'FRANCE', 'US9', 'ITALY', 'SPAIN', 'BELGIUM', 'US IPO', "NDL", "SWITZERLAND"]

def process_reel_order(port_code, index, sendMail = True):
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
    if port == 4001:
        open_order_thread = threading.Thread(target=process_reel_order, args=(port,index_perso, True,))
        open_order_thread.start()
        threads.append(open_order_thread)
        pass
    elif port == 5001:
        open_order_thread = threading.Thread(target=process_reel_order, args=(port,index_pro, True,))
        open_order_thread.start()
        threads.append(open_order_thread)
    else:
        open_order_thread = threading.Thread(target=process_reel_order, args=(port, index_test, True,))
        open_order_thread.start()
        threads.append(open_order_thread)

# Attendez que tous les threads se terminent
for thread in threads:
    thread.join()

print("Tous les threads ont terminé leur traitement.")
