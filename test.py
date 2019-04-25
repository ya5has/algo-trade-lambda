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
  "quantity": "100"
}
target = round((float(x['target']) - float(x['price'])), 1)
stoploss = round((float(x['price']) - float(x['stoploss'])), 1)

print(target, stoploss)

response = {
	'ResponseMetadata': {
		'RequestId': 'TCSSUCU7MKU03JVDR07IT0D8VBVV4KQNSO5AEMVJF66Q9ASUAAJG',
		'HTTPStatusCode': 200,
		'HTTPHeaders': {
			'server': 'Server',
			'date': 'Wed, 01 May 2019 11:14:42 GMT',
			'content-type':
			'application/x-amz-json-1.0',
			'content-length': '2',
			'connection': 'keep-alive',
			'x-amzn-requestid': 'TCSSUCU7MKU03JVDR07IT0D8VBVV4KQNSO5AEMVJF66Q9ASUAAJG',
			'x-amz-crc32': '2745614147'
		},
		'RetryAttempts': 0
	}
}

if 'Item' not in response:
  print('empty')



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