from flask import Flask, jsonify, request
from kiteconnect import KiteConnect
from datetime import datetime
import boto3
from boto3.dynamodb.conditions import Key, Attr
import base64
import json
import requests

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

# Flask Server
app = Flask(__name__)
# Add Dynamodb resource
dynamodb = boto3.resource('dynamodb')
# Kite connect auth token table
token_table = dynamodb.Table("kite_connect_token")
# Initialize kite object
kite = KiteConnect(api_key=KITE_API_KEY)

def update_token_table(_access_token):
    '''
    Update Token Table with new access token
    '''
    # Get current datetime in isoformat
    dtime = datetime.now().replace(microsecond=0).isoformat().split('T')

    try:
        response = token_table.put_item(
            Item = {
                'date_stamp': dtime[0],
                'time_stamp': dtime[1],
                'access_token': _access_token
            }
        )

    except Exception as err:
        return err
    
    return response
    
    
def boto_testing2():
    # Get current datetime in isoformat
    dtime = datetime.now().replace(microsecond=0).isoformat().split('T')

    try:
        response = token_table.query(
            KeyConditionExpression=Key('date_stamp').eq(dtime[0]),
            #FilterExpression=Key('time_stamp').max(),
            #ProjectionExpression="access_token",
            
            ScanIndexForward = False,
            Limit = 1
        )
        if response['Items']:
            print(json.dumps(response['Items']['access_token']))
        else:
            print("no access token found for today")

    except Exception as e:
        print (e)

    return


# Custom functions
def get_kite_orders():
    '''
    Returns the list of all orders (open and executed) for the day
    '''
    return "getting_kite_orders (function not implemented yet)"

def get_kite_trades():
    '''
    Returns the list of all executed trades for the day
    '''
    return "getting_kite_trades (function not implemented yet)"

def handle_invalid_telegram_command():
    '''
    handles invalid commands given to telegram bot
    '''
    response = "Inavalid Command! Please try again"
    return response

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
    return

# Telegram Commands
ALGOTRADE_COMMANDS = {
    'orders': get_kite_orders,
    'trades': get_kite_trades
}

# API Routes
@app.route('/')
def hello():
    response = {
        "server": "Aws lambda",
        "status": "Working"
    }
    return jsonify(response)

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
        # Get the command out of the text (in groups the command includes bot name after '@')
        command = text.split('@')[0][1:]
        # Check if it is a valid command
        if command in ALGOTRADE_COMMANDS:
            # Execute the command
            response = ALGOTRADE_COMMANDS[command]()
        else:
            # Handle invalid command
            response = handle_invalid_telegram_command()
        # Get the chat_id from which the text was received
        chat_id = message["chat"]["id"]
        # Build a response url for the particular chat_id
        response_url = ALGOTRADE_BOT_URL+"/sendMessage?chat_id="+str(chat_id)+"&text="
        # send telegram
        send_telegram(response_url, response)
    
    except Exception as e:
        return jsonify({
            'ERROR!': e
        })

    return jsonify({
        "success": "Bot responded!"
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
    Updates Kite Connect access tokens using obtained request token
    '''
    try:
        # Get url parameter request_token
        request_token = request.args.get('request_token')
        # Get url parameter status
        login_status = request.args.get('status')
        # Generate access token
        data = kite.generate_session(request_token, api_secret=KITE_API_SECRET)
        # Get access token
        access_token = data["access_token"]
        # Set access token in the kite object
        kite.set_access_token(access_token)
        # Add Access token to dynamodb table
        db_response = update_token_table(access_token)

    
    except Exception as err:
        return jsonify({
            'ERROR': err
        })
    
    return jsonify({
        "request_token": request_token,
        "login_status": login_status,
        "db_response": db_response
    })


if __name__ == '__main__':
    app.run(debug=True)