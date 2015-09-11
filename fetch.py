import json
import random
import requests

base_url_parts = ["http://app.njtransit.com/NJTAppWS/services/getDV?_dc=","1000000000000","&station=","NY","&callback="]
stops = ["AM","AB","AZ","AH","AS","AN","AP","AO","AC","AV","BI","BH","MC","BS","BY","BV","BM","BN","BK","BB","BU","BW","BF","CB","CM","CY","IF","CN","XC","DL","DV","DO","DN","EO","ED","EH","EL","EZ","EN","EX","FW","FH","GD","GW","GI","GL","GG","GK","RS","HQ","HL","HN","RM","HW","HZ","HG","HI","HD","UF","HB","JA","KG","HP","ON","LP","LI","LW","FA","LS","LB","LN","LY","MA","MZ","SQ","MW","MP","MU","MI","MD","MB","GO","MK","HS","UV","ZM","MX","MR","HV","OL","TB","MS","ML","MT","MV","MH","NN","NT","NE","NH","NB","NV","NY","NA","ND","NP","OR","NZ","OD","OG","OS","PV","PS","RN","PC","PQ","PN","PE","PH","PF","PL","PP","PO","PR","PJ","FZ","RH","RY","17","RA","RB","RW","RG","RL","RF","CW","TS","SE","RT","XG","SM","CH","SO","LA","SV","SG","SF","ST","TE","TO","TR","TC","US","UM","WK","WA","WG","WT","23","WF","WW","WH","WR","WB","WL"]
# stops = ["NB"]

def _decode_list(data):
    rv = []
    for item in data:
        if isinstance(item, unicode):
            item = item.encode('utf-8')
        elif isinstance(item, list):
            item = _decode_list(item)
        elif isinstance(item, dict):
            item = _decode_dict(item)
        rv.append(item)
    return rv

def _decode_dict(data):
    rv = {}
    for key, value in data.iteritems():
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        elif isinstance(value, list):
            value = _decode_list(value)
        elif isinstance(value, dict):
            value = _decode_dict(value)
        rv[key] = value
    return rv


for s in stops:
	base_url_parts[1] = str(random.randint(10**12, 10**13-1))
	base_url_parts[3] = s
	req_url = "".join(base_url_parts)
	r = requests.get(req_url)
	response = json.loads(r.text[1:-1], object_hook=_decode_dict)['STATION']
	print response

