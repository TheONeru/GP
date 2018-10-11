import json
import datetime

def Get_Value(name):
    with open(name + '.json', 'rt') as f:
        data=json.load(f)
    res = json.loads(data)
    close_ask = []
    high_ask=[]
    low_ask=[]
    for re in res['candles']:
        close_ask.append(float(re['closeAsk']))
        high_ask.append(float(re['highAsk']))
        low_ask.append(float(re['lowAsk']))
        
    return close_ask, high_ask, low_ask


def Get_Time(name):
    with open(name + '.json', 'rt') as f:
        data=json.load(f)
    res = json.loads(data)
    time = []
    for re in res['candles']:
        dtime = datetime.datetime.strptime(re['time'], '%Y-%m-%dT%H:%M:%S.%fZ')
        time.append(dtime)
    return time
