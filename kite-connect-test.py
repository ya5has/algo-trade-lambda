import logging
from kiteconnect import KiteConnect

logging.basicConfig(level=logging.DEBUG)

# Zerodha Constants
KITE_API_KEY = "8k89pux7hxe58snm"
KITE_API_SECRET = "24uqvpxbalc9yc8nmnrb0ei4y9crhvke"
ACCESS_TOKEN = "smFUvQWN7XS6FxZzMCJK5SAjeus17iyf"

kite = KiteConnect(api_key=KITE_API_KEY)

# data = kite.generate_session(REQUEST_TOKEN, api_secret=KITE_API_SECRET)
# print(data["access_token"])

kite.set_access_token(ACCESS_TOKEN)


def get_bo_trade_details(_trade_signal):
    price = float(_trade_signal["price"])
    # target = round((_trade_signal['target'] * 100 / price), 1)
    # stoploss = round((_trade_signal['stoploss'] * 100 / price), 1)
    target = round((float(_trade_signal["target"]) - price), 1)
    stoploss = round((price - float(_trade_signal["stoploss"])), 1)
    return price, target, stoploss


_trade_signal = {
    "time": "2019-04-30 10:45:00",
    "strategy": "gt_InD_15min_reliance",
    "interval": "15min",
    "stock": "TATAELXSI",
    "call": "buy",
    "quantity": "10",
    "price": "932.05",
    "target": "941.3705",
    "stoploss": "922.7295",
    "autotrade": 1,
}

price, target, stoploss = get_bo_trade_details(_trade_signal)

print(target, stoploss)
try:
    order_id = kite.place_order(
        variety=kite.VARIETY_BO,
        product=kite.PRODUCT_MIS,
        order_type=kite.ORDER_TYPE_LIMIT,
        exchange=kite.EXCHANGE_NSE,
        transaction_type=_trade_signal["call"].upper(),
        tradingsymbol=_trade_signal["stock"],
        quantity=int(_trade_signal["quantity"]),
        price=price,
        squareoff=target,
        stoploss=stoploss,
    )

except Exception as e:
    logging.info("Order placement failed: {}".format(e))

print("ORDERRRRRRRRRRRRRR--iDDDD", order_id)


"""
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
"""
# https://api.kite.trade/orders"
