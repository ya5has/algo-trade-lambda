from datetime import datetime
import pytz

timezone = pytz.timezone("Asia/Kolkata")
timezone2 = pytz.timezone("America/Lima")


dtime = datetime.now(timezone2).replace(microsecond=0).isoformat().split('T')
print(dtime)


daware = timezone.localize(datetime.now().replace(microsecond=0)).isoformat().split('T')

#print(datetime.tzinfo)

print(daware)


#print(ptime)