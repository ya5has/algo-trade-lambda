import logging
from kiteconnect import KiteTicker

logging.basicConfig(level=logging.DEBUG)

KITE_API_KEY = "8k89pux7hxe58snm"
KITE_ACCESS_TOKEN = "GEE4u6SKUWbX3nEEv6TIACgxV7MRG8eB"
# Initialise
kws = KiteTicker(KITE_API_KEY, KITE_ACCESS_TOKEN)


def on_ticks(ws, ticks):
    # Callback to receive ticks.
    logging.debug("Ticks: {}".format(ticks))


def on_connect(ws, response):
    # Callback on successful connect.
    # Subscribe to a list of instrument_tokens (RELIANCE and ACC here).
    ws.subscribe([5633])


def on_close(ws, code, reason):
    # On connection close stop the main loop
    # Reconnection will not happen after executing `ws.stop()`
    ws.stop()


def on_order_update(ws, data):
    print("successsssssssssssssssssssssssss----------------")
    print(data)


# Assign the callbacks.
kws.on_ticks = on_ticks
kws.on_connect = on_connect
kws.on_close = on_close
kws.order_update = on_order_update

kws.connect()
