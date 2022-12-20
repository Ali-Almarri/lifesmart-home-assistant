
import json
import requests
url = "https://api.ilifesmart.com/app/auth.do_auth"

payload = json.dumps({
  # user-id from lifesmart-app or from response token tool
  "userid": "change-with-user-id",
  # from response lifesmart-tool-get-token.py
  "token": "change-with-user-token",
  # from website
  "appkey": "change-with-appkey",
  #  from response lifesmart-tool-get-token.py
  "rgn": "change-with-rgn"
})
headers = {
  'Content-Type': 'application/json'
}
response = requests.request("POST", url, headers=headers, data=payload)
print(response.text)