from flask import Flask, jsonify, request
import base64
import json
import requests
import boto3
import kiteconnect
from datetime import datetime
from time import time
from boto3.dynamodb.conditions import Key, Attr


app = Flask(__name__)
dynamodb = boto3.resource('dynamodb')
token_table = dynamodb.Table("kite_connect_token")

# AWS Constants
#KITE_TOKEN_TABLE = "kite_connect_token"

def boto_testing1():
    dtime = datetime.now().replace(microsecond=0).isoformat().split('T')
    try:
        response = token_table.put_item(
            Item={
                'date_stamp': dtime[0],
                'time_stamp': dtime[1],
                'access_token': 'jackfrui'
            }
        )
        print(response)

    except Exception as e:
        print (e)
    
def boto_testing2():
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
    
boto_testing2()

# Telegram Constants
TESTING_GROUP_ID = "-342024797"
SIGNAL_BOT_TOKEN = "720087545:AAFe4C2JyjB7r3hp2YO53mHfqEzQwKknjoE"
SIGNAL_BOT_URL = "https://api.telegram.org/bot{}".format(SIGNAL_BOT_TOKEN)
SIGNAL_BOT_SEND_URL = SIGNAL_BOT_URL+"/sendMessage?chat_id="+TESTING_GROUP_ID+"&text="
ALGOTRADE_BOT_TOKEN = "878159613:AAFEF_7UtZgkFbaLhsyP0ddlmT1L2m-MjaA"
ALGOTRADE_BOT_URL = "https://api.telegram.org/bot{}".format(ALGOTRADE_BOT_TOKEN)
ALGOTRADE_BOT_SEND_URL = ALGOTRADE_BOT_URL+"/sendMessage?chat_id="+TESTING_GROUP_ID+"&text="

# Zerodha Constants
KITE_API_KEY = "8k89pux7hxe58snm"
KITE_API_SECRET = "24uqvpxbalc9yc8nmnrb0ei4y9crhvke"

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

def auto_trade(trade_signal):
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
        if(telegram_msg['autoTrade'] == 1):
            auto_trade(trade_signal)

    except Exception as err:
        return jsonify({
            'ERROR': err,
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
        login_status = request.args.get('status')
        response = {
            "request_token": request_token,
            "login_status": login_status
        }
    
    except:
        return jsonify({
            'error': True,
            'function': "handle_request_token()",
            'description': "Updates Kite Connect access tokens using obtained request token"
        })
    
    return jsonify(response)

    






if __name__ == '__main__':
    app.run(debug=True)