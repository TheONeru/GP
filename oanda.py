import requests
import json
import matplotlib.pyplot as plt
import datetime
import csv
#requests.Requestでheaderパラメータなどを付与

access_token = 'e777fc0c0a7aedb89e00f91e15a7b415-ac361a890d2fa25b195ba4dbe825f38b'
account_id = '2828919'
   
domainDict = { 'live' : 'stream-fxtrade.oanda.com',
               'demo' : 'api-fxpractice.oanda.com',
               'sanbox':'api-sandbox.oanda.com'}

#candlesではinstrument priceはinstruments
params = {'instrument':'GBP_JPY', 'start':'2017-07-08T15',
          'count':'5000', 'granularity':'M1'}
headers = { 'Content-Type': 'application/json',
            'Authorization' : 'Bearer ' + access_token,#そうゆうやつ（アクセストークン送る）
           }

try:
    s = requests.Session()
    url = "https://" + domainDict['demo'] + "/v1/candles"
    req = requests.Request('GET', url, headers = headers, params = params)
    pre = req.prepare()
    resp = s.send(pre, stream = True, verify = True)
except Exception as e:
    s.close()
    print("Caught exception when connecting to stream\n" + str(e)) 

res=json.loads(resp.text)
with open('test.json', 'wt') as f:
    json.dump(resp.text, f)
