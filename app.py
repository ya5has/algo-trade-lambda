from flask import Flask, jsonify, request
from kiteconnect import KiteConnect
from datetime import datetime
from boto3.dynamodb.conditions import Key, Attr
import boto3
import base64
import json
import pytz
import requests
import logging

#logging.basicConfig(level=logging.DEBUG)

# Zerodha Constants
KITE_API_KEY = "8k89pux7hxe58snm"
KITE_API_SECRET = "24uqvpxbalc9yc8nmnrb0ei4y9crhvke"

# Telegram Constants
TESTING_GROUP_ID = "-342024797"
SIGNAL_BOT_TOKEN = "k720087545:AAFe4C2JyjB7r3hp2YO53mHfqEzQwKknjoE"
SIGNAL_BOT_URL = "https://api.telegram.org/bot{}".format(SIGNAL_BOT_TOKEN)
SIGNAL_BOT_SEND_URL = SIGNAL_BOT_URL+"/sendMessage?chat_id="+TESTING_GROUP_ID+"&text="
ALGOTRADE_BOT_TOKEN = "878159613:AAFEF_7UtZgkFbaLhsyP0ddlmT1L2m-MjaA"
ALGOTRADE_BOT_URL = "https://api.telegram.org/bot{}".format(ALGOTRADE_BOT_TOKEN)
ALGOTRADE_BOT_SEND_URL = ALGOTRADE_BOT_URL+"/sendMessage?chat_id="+TESTING_GROUP_ID+"&text="

# App Constants
TIMEZONE = pytz.timezone("Asia/Kolkata")

# Flask Server
app = Flask(__name__)
# Add Dynamodb resource
dynamodb = boto3.resource('dynamodb')
# Kite connect auth token table
token_table = dynamodb.Table("kite_connect_token")
# Initialize kite object
kite = KiteConnect(api_key=KITE_API_KEY)

def get_datetime():
    '''
    Returns a list which contains date and time
    '''
    return datetime.now(TIMEZONE).replace(microsecond=0).isoformat().split('T')

def update_token_table(_access_token):
    '''
    Update Token Table with new access token
    '''
    # Get current datetime in isoformat
    dtime = get_datetime()

    try:
        response = token_table.put_item(
            Item = {
                'date_stamp': dtime[0],
                'time_stamp': dtime[1],
                'access_token': _access_token
            }
        )

    except:
        return "Error: Token table update failed"
    
    return response['ResponseMetadata']['HTTPStatusCode']
    
    
def get_access_token():
    '''
    Retrieve Access Token from Token Table
    '''
    # Get current datetime in isoformat
    dtime = get_datetime()

    try:
        response = token_table.query(
            KeyConditionExpression=Key('date_stamp').eq(dtime[0]),
            ProjectionExpression="access_token",
            ScanIndexForward = False,
            Limit = 1
        )

    except:
        return 0

    return response['Items'][0]['access_token']


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

    except:
        return "Error: Maybe related to network. Try again"

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

    except:
        return "Error: Maybe related to network. Try again"

    else: 
        if trades:
            return str(trades)
        else:
            return "No trades today"


def handle_invalid_telegram_command():
    '''
    handles invalid commands given to telegram bot
    '''
    return "Inavalid Command! Please try again"


def send_telegram(url, message):
    '''
    Sends telegram given url and message
    '''
    requests.get(url+str(message))
    return

def execute_auto_trade(trade_signal):
    '''
    Places order in zerodha
    '''
    send_telegram(ALGOTRADE_BOT_SEND_URL, "Autotrade request received")
    return

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
        # Get the command out of the text (in telegram groups the command includes bot name after '@')
        command = text.split('@')[0][1:]
        
        # Check if it is a valid command
        if command in ALGOTRADE_COMMANDS:
            # Execute the command
            response = ALGOTRADE_COMMANDS[command]()
        else:
            # Handle invalid command
            response = handle_invalid_telegram_command()

        # Build a response url for the particular chat_id
        response_url = ALGOTRADE_BOT_URL+"/sendMessage?chat_id="+str(chat_id)+"&text="
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
        telegram_msg = str(trade_signal).replace("'", "").replace(", ", "%0A").replace("{", "").replace("}", "")
        # Send telegram
        send_telegram(SIGNAL_BOT_SEND_URL, telegram_msg)
        # Check if Auto Trade parameter is enabled
        auto_trade = telegram_msg['autoTrade']
        if auto_trade:
            execute_auto_trade(trade_signal)

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