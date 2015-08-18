import requests
import scrapy
import re

stops = ["","AM","AB","AZ","AH","AS","AN","AP","AO","AC","AV","BI","BH","MC","BS","BY","BV","BM","BN","BK","BB","BU","BW","BF","CB","CM","CY","IF","CN","XC","DL","DV","DO","DN","EO","ED","EH","EL","EZ","EN","EX","FW","FH","GD","GW","GI","GL","GG","GK","RS","HQ","HL","HN","RM","HW","HZ","HG","HI","HD","UF","HB","JA","KG","HP","ON","LP","LI","LW","FA","LS","LB","LN","LY","MA","MZ","SQ","MW","MP","MU","MI","MD","MB","GO","MK","HS","UV","ZM","MX","MR","HV","OL","TB","MS","ML","MT","MV","MH","NN","NT","NE","NH","NB","NV","NY","NA","ND","NP","OR","NZ","OD","OG","OS","PV","PS","RN","PC","PQ","PN","PE","PH","PF","PL","PP","PO","PR","PJ","FZ","RH","RY","17","RA","RB","RW","RG","RL","RF","CW","TS","SE","RT","XG","SM","CH","SO","LA","SV","SG","SF","ST","TE","TO","TR","TC","US","UM","WK","WA","WG","WT","23","WF","WW","WH","WR","WB","WL"]

class TrainSpider(scrapy.Spider):
    name = 'njtransit'
    # start_urls = ['http://dv.njtransit.com/mobile/tid-mobile.aspx?sid=NB']
    
    def start_requests(self):
	base_url = 'http://dv.njtransit.com/mobile/tid-mobile.aspx?sid='
	for stop in stops:
	    new_url = base_url + str(stop)
	    yield scrapy.http.Request(new_url, callback=self.parse)


    def parse(self, response):
	output = []
	for tr in response.css('#GridView1 tr'):
	    """
	    print tr.css('::text').extract()
	    """
	    row = tr.css('::text').extract()
	    temp_row = []
	    for c in row:
		# col = re.sub('\\[a-zA-Z]', '', col)
		# col = re.sub('\\[a-zA-z]*[0-9]*[a-zA-Z]*', ' ', c.encode('utf-8'))
		col = c.encode('utf-8')
		# print "before",col
		# col = re.sub('\\[a-zA-z]*[0-9]*[a-zA-Z]*[-]*', ' ', col)
		col = re.sub('\\r', '', col)
		col = re.sub('\\n', '', col)
		col = col.strip()
		col = re.sub('\\[[a-zA-Z]{2}[0-9]]*', '', col)
		# print "after",col
		if col is "" or col is None:
		    continue
		# temp = [x.encode('utf-8'.strip()) for x in col]
		temp_row.append(str(col))
		# print temp_row
	    output.append(temp_row)
	print output
