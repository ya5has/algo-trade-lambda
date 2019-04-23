from datetime import datetime
import pytz

timezone = pytz.timezone("Asia/Tokyo")
timezone2 = pytz.timezone("America/Lima")


dtime = datetime.now(timezone).replace(microsecond=0).isoformat().split('T')
print(dtime)


daware = timezone.localize(datetime.now().replace(microsecond=0)).isoformat().split('T')

#print(datetime.tzinfo)

print(daware)


#print(ptime)

response = {'Items':[{'date_stamp': '2019-04-30', 'time_stamp': '20:51:49+05:30', 'access_token': 'o2AQvTDDJ2nhWp8T0I978TQ4I1OqYlIp'}], 'Count': 1, 'ScannedCount': 1, 'ResponseMetadata': {'RequestId': 'RELSQ7K121SO857LKNJ7TLLSU7VV4KQNSO5AEMVJF66Q9ASUAAJG', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'Server', 'date': 'Tue, 30 Apr 2019 15:25:17 GMT', 'content-type': 'application/x-amz-json-1.0', 'content-length': '164', 'connection': 'keep-alive', 'x-amzn-requestid': 'RELSQ7K121SO857LKNJ7TLLSU7VV4KQNSO5AEMVJF66Q9ASUAAJG', 'x-amz-crc32': '3419861183'}, 'RetryAttempts': 0}}

print(response['Items'][0]['access_token'])