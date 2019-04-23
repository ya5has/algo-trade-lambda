import logging
from kiteconnect import KiteConnect

#logging.basicConfig(level=logging.DEBUG)

# Zerodha Constants
KITE_API_KEY = "8k89pux7hxe58snm"
KITE_API_SECRET = "24uqvpxbalc9yc8nmnrb0ei4y9crhvke"
ACCESS_TOKEN = "Mr0JAmbqT3F1Uex8NFAqMwks4lOSvQDH"

kite = KiteConnect(api_key=KITE_API_KEY)

#data = kite.generate_session(REQUEST_TOKEN, api_secret=KITE_API_SECRET)
#print(data["access_token"])

kite.set_access_token(ACCESS_TOKEN)


# Fetch all orders
orders = kite.orders()
if orders:
    print(orders)
else:
    print("No orders today")

# Fetch all Trades
orders = kite.trades()
if orders:
    print(orders)
else:
    print("No trades today")



#https://api.kite.trade/orders"
