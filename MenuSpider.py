import requests
import scrapy
import re

class MenuSpider(scrapy.Spider):
    name = 'njtransit-menu'
    start_urls = ['http://m.njtransit.com/mo/mo_servlet.srv?hdnPageAction=DvTo']

    def parse(self, response):
	print response.css("[id='dvStationList'] option").extract()

