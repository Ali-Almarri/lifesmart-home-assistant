
import requests
import json



url = "https://api.ilifesmart.com/app/auth.login"

payload = json.dumps({
  # accuont user email  
  "uid": "change-with-account-email",
  # account password
  "pwd": "change-with-account-password",
  # app-key from www.ilifesmar.com/open
  "appkey": "change-with-app-key"
})
headers = {
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)
print(response.text)
# example response {"token":"F2xcVFLozOACBbvB1ow","code":"success","userid":"814356","rgn":"qa","rgnid":"AME"}