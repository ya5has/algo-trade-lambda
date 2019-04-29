from flask import Flask, jsonify, request
from kiteconnect import KiteConnect
from datetime import datetime
import telegram
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
import boto3
import base64
import json
import pytz

# import logging
# logging.basicConfig(level=logging.DEBUG)

# Zerodha Constants
KITE_API_KEY = "8k89pux7hxe58snm"
KITE_API_SECRET = "24uqvpxbalc9yc8nmnrb0ei4y9crhvke"

# Telegram Constants
TESTING_GROUP_ID = "-342024797"
SIGNAL_BOT_TOKEN = "720087545:AAFe4C2JyjB7r3hp2YO53mHfqEzQwKknjoE"
ALGOTRADE_BOT_TOKEN = "878159613:AAFEF_7UtZgkFbaLhsyP0ddlmT1L2m-MjaA"
BASE_URL = {
    "SIGNAL": "https://api.telegram.org/bot{}".format(SIGNAL_BOT_TOKEN),
    "ALGOTRADE": "https://api.telegram.org/bot{}".format(ALGOTRADE_BOT_TOKEN),
}

# App Constants
IST = pytz.timezone("Asia/Kolkata")
REQUIRED_KEYS = [
    "order_id",
    "status",
    "status_message",
    "order_timestamp",
    "tradingsymbol",
    "transaction_type",
    "quantity",
    "price",
    "trigger_price",
]

# Flask Server
app = Flask(__name__)
# Add Dynamodb resource
dynamodb = boto3.resource("dynamodb")
# Kite connect auth token table
token_table = dynamodb.Table("kite-access-token-table")
# Initialize kite object
kite = KiteConnect(api_key=KITE_API_KEY)
# Telegram bots
algobot = Bot(ALGOTRADE_BOT_TOKEN)
signalbot = Bot(SIGNAL_BOT_TOKEN)


def get_date():
    """
    Returns today's date in isoformat
    """
    return datetime.now(IST).strftime("%Y-%m-%d")


def get_access_token():
    """
    Retrieve Access Token from Token Table
    """
    # Get current date in isoformat
    date = get_date()

    try:
        response = token_table.get_item(Key={"date_stamp": date})

        # Chech if access token is retrieved
        if "Item" not in response:
            return 0

    except Exception:
        return 0

    else:
        return response["Item"]["access_token"]


def update_token_table(_access_token):
    """
    Update Token Table with new access tokens
    """
    # Get current date
    date = get_date()

    try:
        token_table.put_item(
            Item={"date_stamp": date, "access_token": _access_token}
        )

    except Exception:
        return "Error: Token table update failed"

    else:
        return "Token table update success"


def get_bo_trade_details(_trade_signal):
    """
    Returns price, sqaureoff and target for the bracket order
    """
    price = float(_trade_signal["price"])
    # target = round((_trade_signal['target'] * 100 / price), 1)
    # stoploss = round((_trade_signal['stoploss'] * 100 / price), 1)
    squareoff = round((float(_trade_signal["target"]) - price), 1)
    stoploss = round((price - float(_trade_signal["stoploss"])), 1)

    # Check if it's a BUY call
    if _trade_signal["call"] == "buy":
        # Buy call: return as it is
        return price, squareoff, stoploss
    else:
        # Sell call: convert to positive values
        return price, squareoff * -1, stoploss * -1


def execute_auto_trade(_trade_signal):
    """
    Places order on zerodha
    Args:
        _trade_signal: type Dictionary
    Returns:
        autotrade status: type String
    """
    algobot.send_message(
        chat_id=TESTING_GROUP_ID, text="Autotrade request received"
    )
    try:
        # Get Access token from the DB
        access_token = get_access_token()
        # Check if the query is successful
        if not access_token:
            return "*Autotrade error:*%0AGetting access token failed"

        # Set access token in the kite object
        kite.set_access_token(access_token)

        # Change SHORT to SELL
        if _trade_signal["call"] == "short":
            _trade_signal["call"] = "sell"

        price, squareoff, stoploss = get_bo_trade_details(_trade_signal)

    except Exception:
        return "*Autotrade Error:*%0AInvalid access token or network error"

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
            squareoff=squareoff,
            stoploss=stoploss,
        )

        if not order_id:
            return "*Error: Empty order id*%0ACheck trade signal"

    except Exception as e:
        return "*Error: Order placement failed*%0A" + str(e)

    else:
        return "*Autotrade placed*%0AOrder ID: " + str(order_id)


def telegram_format(_message):
    """
    formats json to readable telegram message
    """
    return (
        _message.replace(", '", "\n'")
        .replace("{", "")
        .replace("}", "")
        .replace("'", "")
    )


def telegram_kite_orders(_chat_id):
    """
    Returns the list of all orders (open and executed) for the day
    """
    try:
        # Get Access token from the DB
        access_token = get_access_token()
        # Check if the query is successful
        if not access_token:
            return "Error: Getting access token failed"

        # Set access token in the kite object
        kite.set_access_token(access_token)
        # Get all orders
        orders = kite.orders()

    except Exception:
        return "Error: Invalid access token or network error. Try again"

    else:
        # Check if orders list is non empty
        if orders:
            # Send last 3 orders
            for order in orders[-3:]:
                algobot.send_message(
                    chat_id=_chat_id,
                    text=telegram_format(
                        str({key: order[key] for key in REQUIRED_KEYS})
                    ),
                )
            return 0
        else:
            return "No orders today"


def telegram_kite_trades(_chat_id):
    """
    Returns the list of all executed trades for the day
    """
    try:
        # Get Access token from the DB
        access_token = get_access_token()
        # Check if the query is successful
        if not access_token:
            return "Error: Getting access token failed"

        # Set access token in the kite object
        kite.set_access_token(access_token)
        # Get all trades
        trades = kite.trades()

    except Exception:
        return "Error: Invalid access token or network error. Try again"

    else:
        # Check if trades list is non empty
        if trades:
            # Send last 3 trades
            for trade in trades[-3:]:
                algobot.send_message(
                    chat_id=_chat_id,
                    text=telegram_format(
                        str({key: trade[key] for key in REQUIRED_KEYS})
                    ),
                )
            return 0
        else:
            return "No trades today"


def telegram_test_command(_chat_id):

    keyboard = [
        [
            InlineKeyboardButton("Trade", callback_data="/trades"),
            InlineKeyboardButton("Order", callback_data="/orders"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    algobot.send_message(
        chat_id=_chat_id, text="is it working?", reply_markup=reply_markup
    )
    return


def telegram_invalid_command():
    """
    handles invalid commands given to telegram bot
    """
    return "Inavalid Command! Please try again"


# Telegram Bot Commands
ALGOBOT_COMMANDS = {
    "orders": telegram_kite_orders,
    "trades": telegram_kite_trades,
    "test": telegram_test_command,
}

# API Routes
@app.route("/")
def hello():
    """
    home route to check lambda is online
    """
    return jsonify({"server": "Aws lambda", "status": "Working"})


@app.route("/telegram/algo_trade", methods=["POST"])
def algo_trader_bot():
    """
    Main bot server for algo trader
    """
    try:
        # Capture update from post api call from telegram
        update = request.get_json()

        # Check if its a callback update
        if "callback_query" in update:
            # Get the message property
            message = update["callback_query"]["message"]
            # Get the main content of the message
            data = update["callback_query"]["data"]

        # Check if its a command update
        elif "message" in update:
            # Get the message property
            message = update["message"]
            # Get the main content of the message
            data = message["text"]

        else:
            return jsonify(
                {"ERROR!": "Not a callback_query nor a message update"}
            )

        # Get the chat_id from which the text was received
        chat_id = str(message["chat"]["id"])
        # Get the command out of the data.
        # In telegram groups the command includes bot name after '@'
        command = data.split("@")[0][1:]

        # Check if it is a valid command
        if command in ALGOBOT_COMMANDS:
            # Execute the command
            response = ALGOBOT_COMMANDS[command](chat_id)
        else:
            # Handle invalid command
            response = telegram_invalid_command()

        # Telegram if response is not empty
        if response:
            algobot.send_message(chat_id=chat_id, text=response)

    except Exception as err:
        return jsonify({"ERROR!": str(err)})

    return jsonify({"success": "Bot responded!", "response": response})


@app.route("/signal/<string:encoded_data>", methods=["GET"])
def get_signal_encoded(encoded_data):
    """
    handles encoded signals from amibroker
    and sends telegram notification
    """
    try:
        # Decode the encoded string
        decoded_data = base64.b64decode(encoded_data).decode("utf-8")
        # Convert to python dictionary
        trade_signal = json.loads(decoded_data)

        # Send telegram
        signalbot.send_message(
            chat_id=TESTING_GROUP_ID, text=telegram_format(str(trade_signal))
        )

        # Check if Auto Trade parameter is enabled
        if trade_signal["autotrade"]:
            response = execute_auto_trade(trade_signal)
            algobot.send_message(
                chat_id=TESTING_GROUP_ID,
                text=response,
                parse_mode=telegram.ParseMode.MARKDOWN,
            )

    except Exception as err:
        signalbot.send_message(
            chat_id=TESTING_GROUP_ID, text="Error: " + str(err)
        )
        return jsonify({"ERROR": str(err)})

    return jsonify({"status": True, "trade_signal": trade_signal})


@app.route("/kite/orders", methods=["POST"])
def handle_order_updates():
    """
    Receives postback updates from kite. Send updates to telegram
    """
    try:
        # Capture message from post api call from kite
        message = request.get_json()
        algobot.send_message(
            chat_id=TESTING_GROUP_ID, text=telegram_format(str(message))
        )

    except Exception as err:
        algobot.send_message(
            chat_id=TESTING_GROUP_ID,
            text="handle_order_updates()%0A" + str(err),
        )
        return jsonify({"ERROR!": str(err)})

    return jsonify({"postback": "success"})


@app.route("/kite/login", methods=["GET"])
def handle_request_token():
    """
    Updates Kite Connect access token using obtained request token
    """
    try:
        # Get url parameter request_token
        request_token = request.args.get("request_token")
        # Generate access session
        data = kite.generate_session(request_token, api_secret=KITE_API_SECRET)
        # Get access token
        access_token = data["access_token"]
        # Add Access token to dynamodb table
        db_status = update_token_table(access_token)
        # Set access token in the kite object
        kite.set_access_token(access_token)

    except Exception as err:
        return jsonify({"ERROR": str(err)})

    return jsonify(
        {
            "request_token": request_token,
            "access_token": access_token,
            "db_status": db_status,
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
