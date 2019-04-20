from flask import Flask, jsonify
import base64
import json
import requests

app = Flask(__name__)

# Telegram Constants
TESTING_GROUP_ID = "-342024797"
SIGNAL_BOT_TOKEN = "720087545:AAFe4C2JyjB7r3hp2YO53mHfqEzQwKknjoE"
SIGNAL_BOT_URL = "https://api.telegram.org/bot{}".format(SIGNAL_BOT_TOKEN)
SIGNAL_BOT_SEND_URL = SIGNAL_BOT_URL+"/sendMessage?chat_id="+TESTING_GROUP_ID+"&text="
ALGOTRADE_BOT_TOKEN = "878159613:AAFEF_7UtZgkFbaLhsyP0ddlmT1L2m-MjaA"
ALGOTRADE_BOT_URL = "https://api.telegram.org/bot{}".format(ALGOTRADE_BOT_TOKEN)
ALGOTRADE_BOT_SEND_URL = ALGOTRADE_BOT_URL+"/sendMessage?chat_id="+TESTING_GROUP_ID+"&text="

@app.route('/')
def hello():
    data = {'message': 'hi there'}
    return jsonify(data)

@app.route("/signal/<string:encoded_data>", methods=["GET"])
def get_signal_encoded(encoded_data):
    '''
    handles encoded signals from amibroker 
    and sends telegram notification
    '''
    try:
        # Decode the enoded string
        decoded_data = base64.b64decode(encoded_data).decode('utf-8')
        # Convert to python dictionary
        trade_signal = json.loads(decoded_data)
        # Construct telegram message from trade signal
        telegram_msg = str(trade_signal).replace("'", "").replace(", ", "%0A").replace("{", "").replace("}", "")
        # Send telegram message
        requests.get(SIGNAL_BOT_SEND_URL+telegram_msg)

    except:
        return jsonify({
            'error': True
        })

    return jsonify({
        'status': True,
        'trade_signal': trade_signal
    })


if __name__ == '__main__':
    app.run()