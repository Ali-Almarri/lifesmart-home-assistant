import hashlib
import json
import time
import urllib.request
userid ="xxxx"
usertoken="xxxx"
appkey="xxxx"
apptoken="xxxx"
url = "https://api.ilifesmart.com/app/api.EpGetAll"
tick = int(time.time())
sdata = "method:EpGetAll,time:"+str(tick)+",userid:"+userid+",usertoken:"+usertoken+",appkey:"+appkey+",apptoken:"+apptoken
sign = hashlib.md5(sdata.encode(encoding='UTF-8')).hexdigest()
send_values ={
  "id": 1,
  "method": "EpGetAll",
  "system": {
  "ver": "1.0",
  "lang": "en",
  "userid": userid,
  "appkey": appkey,
  "time": tick,
  "sign": sign
  }
}
header = {'Content-Type': 'application/json'}
send_data = json.dumps(send_values)
req = urllib.request.Request(url=url, data=send_data.encode('utf-8'), headers=header, method='POST')
response = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
if response['code'] == 0:
    print(  response['message'])
print(response)
print(sign)
print(sdata)