price = float("402.6")
target = float("398.574")
stoploss = float("407.626")
squareoff = round((target - price), 1)
stoploss = round((price - stoploss), 1)

print(squareoff, stoploss)

"""
SIGNAL_BOT_URL = "https://api.telegram.org/bot{}".format(SIGNAL_BOT_TOKEN)
SIGNAL_BOT_SEND_URL = (
    SIGNAL_BOT_URL + "/sendMessage?chat_id=" + TESTING_GROUP_ID + "&text="
)

ALGOTRADE_BOT_URL = "https://api.telegram.org/bot{}".format(
    ALGOTRADE_BOT_TOKEN
)
ALGOTRADE_BOT_SEND_URL = (
    ALGOTRADE_BOT_URL + "/sendMessage?chat_id=" + TESTING_GROUP_ID + "&text="
)
"""
"""
x = {
    "call": "SHORT",
    "interval": "15min",
    "price": "1377",
    "stock": "RELIANCE",
    "stoploss": "1363.725",
    "Strategy": "gt_InD_15min_reliance",
    "target": "1391",
    "time": "2019-04-30 10:30:00",
    "autotrade": "1",
    "quantity": "100",
}
target = round((float(x["target"]) - float(x["price"])), 1)
stoploss = round((float(x["price"]) - float(x["stoploss"])), 1)

print(target, stoploss)
"""

'''
def update_token_table(_access_token):
    """
    Update Token Table with new access token
    """
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
    """
    Retrieve Access Token from Token Table
    """
    # Get current datetime in isoformat
    dtime = get_datetime()

    try:
        response = token_table.query(
            KeyConditionExpression=Key('date_stamp').eq(dtime[0]),
            ProjectionExpression="access_token",
            ScanIndexForward = False,
            Limit = 1
        )

        if not response['I']

    except:
        return 0

    return response['Items'][0]['access_token']

'''
