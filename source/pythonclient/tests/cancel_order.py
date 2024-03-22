from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from tests.placeOrder import formatted_cancel_time


class TestApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)

    def error(self, reqId, errorCode, errorString):
        print("Error:", reqId, errorCode, errorString)

    def nextValidId(self, orderId):
        self.nextOrderId = orderId




def main():
    app = TestApp()
    app.connect("127.0.0.1", 5001, 1)  # Connect to TWS or IB Gateway

    # # Wait for the connection to be established
    # while not app.isConnected():
    #     pass

    # Assume order_id is the ID of the order you want to cancel
    order_id = 57  # Replace this with your order ID
    app.cancelOrder(order_id, manualCancelOrderTime=formatted_cancel_time)

    # Disconnect from TWS or IB Gateway
    app.disconnect()


if __name__ == "__main__":
    main()
