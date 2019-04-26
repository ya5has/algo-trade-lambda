from flask import Flask, jsonify, request
from kiteconnect import KiteConnect
from datetime import datetime
import boto3
import base64
import json
import pytz
import requests
import logging

logging.basicConfig(level=logging.DEBUG)

# Zerodha Constants
KITE_API_KEY = "8k89pux7hxe58snm"
KITE_API_SECRET = "24uqvpxbalc9yc8nmnrb0ei4y9crhvke"

# Telegram Constants
TESTING_GROUP_ID = "-342024797"
SIGNAL_BOT_TOKEN = "720087545:AAFe4C2JyjB7r3hp2YO53mHfqEzQwKknjoE"
SIGNAL_BOT_URL = "https://api.telegram.org/bot{}".format(SIGNAL_BOT_TOKEN)
SIGNAL_BOT_SEND_URL = SIGNAL_BOT_URL + \
    "/sendMessage?chat_id="+TESTING_GROUP_ID+"&text="
ALGOTRADE_BOT_TOKEN = "878159613:AAFEF_7UtZgkFbaLhsyP0ddlmT1L2m-MjaA"
ALGOTRADE_BOT_URL = "https://api.telegram.org/bot{}".format(
    ALGOTRADE_BOT_TOKEN)
ALGOTRADE_BOT_SEND_URL = ALGOTRADE_BOT_URL + \
    "/sendMessage?chat_id="+TESTING_GROUP_ID+"&parse_mode=markdown&text="

# App Constants
IST = pytz.timezone("Asia/Kolkata")

# Flask Server
app = Flask(__name__)
# Add Dynamodb resource
dynamodb = boto3.resource('dynamodb')
# Kite connect auth token table
token_table = dynamodb.Table("kite-access-token-table")
# Initialize kite object
kite = KiteConnect(api_key=KITE_API_KEY)


def get_date():
    '''
    Returns today's date in isoformat
    '''
    return datetime.now(IST).strftime('%Y-%m-%d')


def update_token_table(_access_token):
    '''
    Update Token Table with new access tokens
    '''
    # Get current date
    date = get_date()

    try:
        token_table.put_item(
            Item={
                'date_stamp': date,
                'access_token': _access_token
            }
        )

    except Exception:
        return "Error: Token table update failed"

    return "Token table update success"


def get_access_token():
    '''
    Retrieve Access Token from Token Table
    '''
    # Get current date in isoformat
    date = get_date()

    try:
        response = token_table.get_item(
            Key={
                "date_stamp": date
            }
        )

        # Chech if access token is retrieved
        if 'Item' not in response:
            return 0

    except Exception:
        return 0

    return response['Item']['access_token']


# Custom functions
def get_kite_orders():
    '''
    Returns the list of all orders (open and executed) for the day
    '''
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
        if orders:
            return str(orders)
        else:
            return "No orders today"


def get_kite_trades():
    '''
    Returns the list of all executed trades for the day
    '''
    try:
        # Get Access token from the DB
        access_token = get_access_token()
        # Check if the query is successful
        if not access_token:
            return "Error: Getting access token failed"

        # Set access token in the kite object
        kite.set_access_token(access_token)
        # Get all orders
        trades = kite.trades()

    except Exception:
        return "Error: Invalid access token or network error. Try again"

    else:
        if trades:
            return str(trades)
        else:
            return "*No trades today*"


def handle_invalid_telegram_command():
    '''
    handles invalid commands given to telegram bot
    '''
    return "Inavalid Command! Please try again"


def send_telegram(_url, _message):
    '''
    Sends telegram given url and message
    '''
    requests.get(_url+str(_message))
    return


def get_bo_trade_details(_trade_signal):
    price = float(_trade_signal['price'])
    # target = round((_trade_signal['target'] * 100 / price), 1)
    # stoploss = round((_trade_signal['stoploss'] * 100 / price), 1)
    squareoff = round((float(_trade_signal['target']) - price), 1)
    stoploss = round((price - float(_trade_signal['stoploss'])), 1)
    return price, squareoff, stoploss


def execute_auto_trade(_trade_signal):
    '''
    Places order in zerodha
    '''
    print("Autotrade request received")
    send_telegram(ALGOTRADE_BOT_SEND_URL, "Autotrade request received")
    try:
        # Get Access token from the DB
        access_token = get_access_token()
        # Check if the query is successful
        if not access_token:
            return "Autotrade error: Getting access token failed"

        # Set access token in the kite object
        kite.set_access_token(access_token)

        # Change SHORT to SELL
        if _trade_signal['call'] == 'short':
            _trade_signal['call'] = 'sell'

        price, squareoff, stoploss = get_bo_trade_details(_trade_signal)

    except Exception:
        return "Error: Invalid access token or network error. Try again"

    try:
        order_id = kite.place_order(
            variety=kite.VARIETY_BO,
            product=kite.PRODUCT_MIS,
            order_type=kite.ORDER_TYPE_LIMIT,
            exchange=kite.EXCHANGE_NSE,
            transaction_type=_trade_signal['call'].upper(),
            tradingsymbol=_trade_signal['stock'],
            quantity=int(_trade_signal['quantity']),
            price=price,
            squareoff=squareoff,
            stoploss=stoploss
        )

        if not order_id:
            return "*Error: Empty order id*%0ACheck trade signal"

    except Exception as e:
        return "*Error: Order placement failed*%0A"+str(e)

    else:
        return "*Autotrade placed*%0AOrder ID: "+str(order_id)


# Telegram Bot Commands
ALGOTRADE_COMMANDS = {
    'orders': get_kite_orders,
    'trades': get_kite_trades
}

# API Routes
@app.route('/')
def hello():
    '''
    home route to check lambda is online
    '''
    return jsonify({
        "server": "Aws lambda",
        "status": "Working"
    })


@app.route("/telegram/algo_trade", methods=["POST"])
def algo_trader_bot():
    '''
    Main bot server for algo trader
    '''
    try:
        # Capture message from post api call from telegram
        message = request.json.get("message")
        # Get the main content of the message
        text = message["text"]
        # Get the chat_id from which the text was received
        chat_id = message["chat"]["id"]
        # Get the command out of the text
        # In telegram groups the command includes bot name after '@'
        command = text.split('@')[0][1:]

        # Check if it is a valid command
        if command in ALGOTRADE_COMMANDS:
            # Execute the command
            response = ALGOTRADE_COMMANDS[command]()
        else:
            # Handle invalid command
            response = handle_invalid_telegram_command()

        # Build a response url for the particular chat_id
        response_url = ALGOTRADE_BOT_URL + \
            "/sendMessage?chat_id="+str(chat_id)+"&text="
        # send telegram
        send_telegram(response_url, response)

    except Exception as err:
        return jsonify({
            'ERROR!': err
        })

    return jsonify({
        "success": "Bot responded!",
        "response": response
    })


@app.route("/signal/<string:encoded_data>", methods=["GET"])
def get_signal_encoded(encoded_data):
    '''
    handles encoded signals from amibroker
    and sends telegram notification
    '''
    try:
        # Decode the encoded string
        decoded_data = base64.b64decode(encoded_data).decode('utf-8')
        # Convert to python dictionary
        trade_signal = json.loads(decoded_data)
        # Construct telegram message from trade signal
        telegram_msg = str(trade_signal).replace("'", "").replace(
            ", ", "%0A").replace("{", "").replace("}", "")
        # Send telegram
        send_telegram(SIGNAL_BOT_SEND_URL, telegram_msg)
        # Check if Auto Trade parameter is enabled
        auto_trade = trade_signal['autotrade']
        if auto_trade:
            respose = execute_auto_trade(trade_signal)
            send_telegram(ALGOTRADE_BOT_SEND_URL, respose)

    except Exception as err:
        return jsonify({
            'ERROR': err
        })

    return jsonify({
        'status': True,
        'trade_signal': trade_signal
    })


@app.route("/kite/login", methods=["GET"])
def handle_request_token():
    '''
    Updates Kite Connect access token using obtained request token
    '''
    try:
        # Get url parameter request_token
        request_token = request.args.get('request_token')

        # Generate access session
        data = kite.generate_session(request_token, api_secret=KITE_API_SECRET)
        # Get access token
        access_token = data["access_token"]
        # Add Access token to dynamodb table
        db_status = update_token_table(access_token)
        # Set access token in the kite object
        kite.set_access_token(access_token)

    except Exception as err:
        return jsonify({
            'ERROR': err
        })

    return jsonify({
        "request_token": request_token,
        "access_token": access_token,
        "db_status": db_status
    })


if __name__ == '__main__':
    app.run(debug=True)


"""
def read_table_item(table_name, pk_name, pk_value):
    '''
    Return item read by primary key.
    '''
    table = dynamodb_resource.Table(table_name)
    response = table.get_item(Key={pk_name: pk_value})

    return response
"""
