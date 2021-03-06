import requests
import scrapy
import re
import sys

# stops = ["NB"]
stops = ["AM","AB","AZ","AH","AS","AN","AP","AO","AC","AV","BI","BH","MC","BS","BY","BV","BM","BN","BK","BB","BU","BW","BF","CB","CM","CY","IF","CN","XC","DL","DV","DO","DN","EO","ED","EH","EL","EZ","EN","EX","FW","FH","GD","GW","GI","GL","GG","GK","RS","HQ","HL","HN","RM","HW","HZ","HG","HI","HD","UF","HB","JA","KG","HP","ON","LP","LI","LW","FA","LS","LB","LN","LY","MA","MZ","SQ","MW","MP","MU","MI","MD","MB","GO","MK","HS","UV","ZM","MX","MR","HV","OL","TB","MS","ML","MT","MV","MH","NN","NT","NE","NH","NB","NV","NY","NA","ND","NP","OR","NZ","OD","OG","OS","PV","PS","RN","PC","PQ","PN","PE","PH","PF","PL","PP","PO","PR","PJ","FZ","RH","RY","17","RA","RB","RW","RG","RL","RF","CW","TS","SE","RT","XG","SM","CH","SO","LA","SV","SG","SF","ST","TE","TO","TR","TC","US","UM","WK","WA","WG","WT","23","WF","WW","WH","WR","WB","WL"]

class TrainSpider(scrapy.Spider):
	name = 'njtransit'
	# start_urls = ['http://dv.njtransit.com/mobile/tid-mobile.aspx?sid=NB']
	
	def start_requests(self):
		base_url = 'http://dv.njtransit.com/mobile/tid-mobile.aspx?sid='
		for stop in stops:
			new_url = base_url + str(stop)
			stop_request = scrapy.http.Request(new_url, callback=self.parse)
			stop_request.meta['stop'] = stop
			yield stop_request


	def parse(self, response):
		output = []
		combine = False
		last = ""
		for tr in response.css('#GridView1 tr'):
			row = tr.css('::text').extract()
			# print row
			temp_row = []
			for c in row:
				col = c.encode('utf-8')
				col = re.sub('\\r', '', col)
				col = re.sub('\\n', '', col)
				col = re.sub('\xe2\x9c\x88', '', col)
				col = re.sub('\xc2\xa0', '', col)
				col = col.strip()
				if col is "" or col is None:
					continue
				if combine:
					temp_row.append(str(last)+str(col))
					combine = False
					continue
				else:
					if col[len(col)-1] == "-":
						combine = True
						last = col
						continue
					else:
						temp_row.append(str(col))
						combine = False
						continue
			# print "row\t", row, "\ntemp row \t", temp_row
			if len(output) == 0:
				output.append(temp_row)
			else:
				if output[len(output)-1] != temp_row:
					output.append(temp_row)
					single_train_url = "http://dv.njtransit.com/mobile/train_stops.aspx?sid=" + response.meta['stop'] + "&train=" + str(temp_row[4])
					single_train_response = scrapy.http.Request(single_train_url, callback=self.single_train)
					single_train_response.meta['train'] = str(temp_row[4])
					yield single_train_response

		print output

	def single_train(self, response):
		output = {}
		for tr in response.css("#table_stops"):
			stop = tr.css('::text').extract()
			stop  = [re.sub('\xc2\xa0\xc2\xa0', " ", r.encode('utf-8').strip()) for r in stop]
			new_stops = []
			combine = False
			last_stop = ""
			for s in stop:
				if ' at ' in s:
					try:
						curr_stop, est = s.split(" at ")
					except:
						print "ERROR"
						print stop
						print s
					new_stops.append({curr_stop.strip(): est.strip()})
				else:
					if combine:
						combine = False
						new_stops.append({last_stop: s})
						continue
					else:
						combine = True
						last_stop = s
						continue

			output[response.meta['train']] = new_stops
		
		print output
