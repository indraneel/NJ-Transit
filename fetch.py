import sys
import json
import random
import requests
import psycopg2
import config

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

insert_into_default = ["train_line", "station_name", "station_abbr", "destination"]

insert_into = ["sched_dep_day", "sched_dep_time", "track", "line", "train_line", "train_number", "status", "sec_late", "gps_lat", "gps_lon", "gps_time", "station_name", "station_abbr", "destination"]

for s in stops:
    default_train = {
	    "ITEM_INDEX": "",
	    "SCHED_DEP_DAY": "1/1/1970",
	    "SCHED_DEP_TIME": "00:00:01 AM",
	    "DESTINATION": "",
	    "TRACK": "",
	    "LINE": "",
	    "TRAIN_ID": "",
	    "STATUS": "",
	    "SEC_LATE": "",
	    "TRAIN_LINE": "",
	    "STATION_ABBR": "",
	    "STATION_NAME": "",
	    "GPSLONGITUDE": "0.0",
	    "GPSLATITUDE": "0.0",
	    "GPSTIME": "1/1/1970 00:00:01 AM"
    }

    base_url_parts[1] = str(random.randint(10**12, 10**13-1))
    base_url_parts[3] = s
    req_url = "".join(base_url_parts)
    print "GET/\t",req_url
    r = requests.get(req_url)
    """
    text = r.text
    if not text:
	continue
    """
    response = json.loads(r.text[1:-1], object_hook=_decode_dict)['STATION']
    print response
    if not response:
	continue
    # response = (r.text[1:-1])
    # print response
    con = psycopg2.connect("dbname='"+config.dbname+"' user='"+config.dbuser+"'") 
    cur = con.cursor()
    print "about to write to db\n"
    # sys.exit(1)
    if response['ITEMS'] is None:
	default_train['STATION_NAME'] = response['STATION_2CHAR']
	default_train['STATION_ABBR'] = response['STATIONNAME'] 
	try:
	    cur.execute("INSERT INTO trains("+",".join(insert_into_default)+"""
	    ) VALUES(%(TRAIN_LINE)s, %(STATION_NAME)s, %(STATION_ABBR)s, %(DESTINATION)s)
	    """, default_train)

	    con.commit()
	    print "commited\t",default_train

	except Exception, e:
	    if con:
		con.rollback()
		print "1 - rollback on\t",response
		print e,"\n"
		sys.exit(1)
	
    if isinstance(response['ITEMS']['ITEM'], dict):
	try:
	    temp_item = response['ITEMS']['ITEM']
	    # temp_item['SCHED_DEP_DATE'] = " ".join(["-".join(list(reversed(response['ITEMS']['ITEM'].split(" ")[1].split("/")))), response['ITEMS']['ITEM'].split(" ")[0]])
	    # print temp_item['SCHED_DEP_DATE'] 
	    temp_item['SCHED_DEP_DAY'] = response['ITEMS']['ITEM']['SCHED_DEP_DATE'].split(" ")[1]
	    temp_item['SCHED_DEP_TIME'] = response['ITEMS']['ITEM']['SCHED_DEP_DATE'].split(" ")[0]
	    temp_item['STATION_ABBR'] = response['STATION_2CHAR']
	    temp_item['STATION_NAME'] = response['STATIONNAME'] 
	    if "GPSLATITUDE" not in item:
		temp_item['GPSLATITUDE'] = "0.0"
	    else:
		if item['GPSLATITUDE'] is "":
		    temp_item['GPSLATITUDE'] = "0.0"

	    if "GPSLONGITUDE" not in item:
		temp_item['GPSLONGITUDE'] = "0.0"
	    else:
		if item['GPSLONGITUDE'] is "":
		    temp_item['GPSLONGITUDE'] = "0.0"
	    if "GPSTIME" not in item:
		temp_item['GPSTIME'] = "1/1/1970 00:00:01 AM"
	    else:
		if item['GPSTIME'] is "":
		    temp_item['GPSTIME'] = "1/1/1970 00:00:01 AM"

	    cur.execute("INSERT INTO trains("+",".join(insert_into)+"""
	    ) VALUES(%(SCHED_DEP_DAY)s, %(SCHED_DEP_TIME)s, %(TRACK)s, %(LINE)s, %(TRAIN_LINE)s, %(TRAIN_ID)s, %(STATUS)s, %(SEC_LATE)s, %(GPSLATITUDE)s, %(GPSLONGITUDE)s, %(GPSTIME)s, %(STATION_NAME)s, %(STATION_ABBR)s, %(DESTINATION)s)
	    """, temp_item)

	    con.commit()
	    print "commited\t",temp_item
# i have to write a thing where i iterate over the item from the API and if theres a non empty string then i can overwrite the original data object but otherwise just use the default original data object 
	except Exception, e:
	    if con:
		con.rollback()
		print "2 - rollback on\t",temp_item
		print e
		sys.exit(1)
    if isinstance(response['ITEMS']['ITEM'], list):
	for item in response['ITEMS']['ITEM']:
	    temp_item = item
	    # temp_item['SCHED_DEP_DATE'] = " ".join(["-".join(list(reversed(item.split(" ")[1].split("/")))), item.split(" ")[0]])
	    # print temp_item['SCHED_DEP_DATE'] 
	    temp_item['SCHED_DEP_DAY'] = item['SCHED_DEP_DATE'].split(" ")[1]
	    temp_item['SCHED_DEP_TIME'] = item['SCHED_DEP_DATE'].split(" ")[0]
	    temp_item['STATION_ABBR'] = response['STATION_2CHAR']
	    temp_item['STATION_NAME'] = response['STATIONNAME'] 
	    if "GPSLATITUDE" not in item:
		temp_item['GPSLATITUDE'] = "0.0"
	    else:
		if item['GPSLATITUDE'] is "":
		    temp_item['GPSLATITUDE'] = "0.0"

	    if "GPSLONGITUDE" not in item:
		temp_item['GPSLONGITUDE'] = "0.0"
	    else:
		if item['GPSLONGITUDE'] is "":
		    temp_item['GPSLONGITUDE'] = "0.0"
	    if "GPSTIME" not in item:
		temp_item['GPSTIME'] = "1/1/1970 00:00:01 AM"
	    else:
		if item['GPSTIME'] is "":
		    temp_item['GPSTIME'] = "1/1/1970 00:00:01 AM"

	    try:
		cur.execute("INSERT INTO trains("+",".join(insert_into)+"""
		) VALUES(%(SCHED_DEP_DAY)s, %(SCHED_DEP_TIME)s, %(TRACK)s, %(LINE)s, %(TRAIN_LINE)s, %(TRAIN_ID)s, %(STATUS)s, %(SEC_LATE)s, %(GPSLATITUDE)s, %(GPSLONGITUDE)s, %(GPSTIME)s, %(STATION_NAME)s, %(STATION_ABBR)s, %(DESTINATION)s)
		""", temp_item)

		con.commit()
		print "commited\t",temp_item

	    except Exception, e:
		if con:
		    con.rollback()
		    print "3 - rollback on\t",temp_item
		    print e,"\n"
		    sys.exit(1)

		# sys.exit(1)

