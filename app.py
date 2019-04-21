from flask import Flask, jsonify, request
import base64
import json
import requests
import kiteconnect

app = Flask(__name__)

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

def send_telegram_message(url, message):
    '''
    Sends telegram message given url and message
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

@app.route('/')
def hello():
    response = {
    "server": "Aws lambda",
    "status": "Working"
    }
    return jsonify(response)

@app.route("/kite/trades", methods=["GET"])
def retrieve_trades():
    '''
    Retrieve the list of all executed trades for the day
    '''
    try:
        pass
    except:
        pass
    return

@app.route("/kite/orders", methods=["GET"])
def retrieve_orders():
    '''
    Retrieve the list of all orders (open and executed) for the day
    '''
    try:
        pass
    except:
        pass
    return


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
        command = text.split('@')[0]
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
        # send telegram message
        send_telegram_message(response_url, response)
    

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
        # Send telegram message
        send_telegram_message(SIGNAL_BOT_SEND_URL, telegram_msg)
        # Check if Auto Trade parameter is enabled
        if(telegram_msg['autoTrade'] == 1):
            auto_trade(trade_signal)

    except:
        return jsonify({
            'error': True,
            'function': "get_signal_encoded()",
            'description': "handles encoded signals from amibroker and sends telegram notification"
        })

    return jsonify({
        'status': True,
        'trade_signal': trade_signal
    })




if __name__ == '__main__':
    app.run(debug=True)