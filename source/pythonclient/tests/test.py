from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.common import OrderId
from threading import Thread
import time

class TestApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.open_orders = {}

    def openOrder(self, orderId: OrderId, order, contract, orderState):
        super().openOrder(orderId, order, contract, orderState)
        self.open_orders[orderId] = {"order": order, "contract": contract, "orderState": orderState}

    def openOrderEnd(self):
        super().openOrderEnd()
        print(self.open_orders)
        print("Received all open order data.")

def run_app():
    app = TestApp()
    app.connect("127.0.0.1", 7497, clientId=1)  # Change these values if needed

    app_thread = Thread(target=app.run)
    app_thread.start()

    time.sleep(1)  # Wait for connection to be established
    return app

app = run_app()
app.reqOpenOrders()
time.sleep(3)  # Allow time for response from server

target_symbol = "MRUS"  # The symbol you are looking for
target_order_id = None

for order_id, order_info in app.open_orders.items():
    if order_info["contract"].symbol == target_symbol:
        target_order_id = order_id
        break

print(f"Order ID for {target_symbol}: {target_order_id}")

app.disconnect()

app.connect("127.0.0.1", 7497, 1)
