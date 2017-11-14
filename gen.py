#!/usr/bin/python

#
# written by @eric_capuano
# https://github.com/ecapuano/web-traffic-generator
#
# published under MIT license :) do what you want.
#
#20170714 shyft ADDED python 2.7 and 3.x compatibility and generic config
from __future__ import print_function 
import logging
from surf_web import SurfWeb

try:
	import config
except ImportError:
	class ConfigClass: #minimal config incase you don't have the config.py
		clickDepth = 5 # how deep to browse from the rootURL
		minWait = 1 # minimum amount of time allowed between HTTP requests
		maxWait = 3 # maximum amount of time to wait between HTTP requests
		debug = True # set to True to enable useful console output

		# use this single item list to test how a site responds to this crawler
		# be sure to comment out the list below it.
		#rootURLs = ["https://digg.com/"] 
		rootURLs = [
			"https://www.reddit.com"
			]


		# items can be a URL "https://t.co" or simple string to check for "amazon"
		blacklist = [
			'facebook.com',
			'pinterest.com'
			]  

		# must use a valid user agent or sites will hate you
		userAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) ' \
			'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
	config = ConfigClass 
	
def browse(urls):
	currURL = 1
	sw = SurfWeb()
	sw._maxWait = config.maxWait
	sw._minWait = config.minWait
	sw._blacklist = config.blacklist
	sw._depth = config.clickDepth
	sw._width = config.clickWidth
	for url in urls:
		urlCount = len(urls)

		logging.getLogger('main').debug("Request root URL:%s"%url)
		sw.browse_url(url)  # hit current root URL
		if config.debug:
			if ( sw.data_meter > 1000000 ):
				print("Data meter: %s MB" % (sw.data_meter / 1000000))
			else:
				print("Data meter: %s bytes" % sw.data_meter)
			print("Good requests: %s" % sw.good_requests)
			print("Bad reqeusts: %s" % sw.bad_requests)
			
	logging.getLogger('main').debug("Done.")

#while True:
if True:
	print("Traffic generator started...")
	print("----------------------------")
	print("https://github.com/ecapuano/web-traffic-generator")
	print("")
	print("Clcking %s links deep into %s different root URLs, " \
		% (config.clickDepth,len(config.rootURLs)))
	print("waiting between %s and %s seconds between requests. " \
		% (config.minWait,config.maxWait))
	print("")
	print("This script will run indefinitely. Ctrl+C to stop.")
	logging.basicConfig(level = logging.DEBUG,
						format = '%(asctime)s %(name)-8s %(levelname)-6s %(message)s',
						datefmt = '%Y-%m-%d %H:%M:%S',
						filename = "log.txt")
	ch = logging.StreamHandler()
	ch.setLevel(logging.DEBUG)
	# create formatter and add it to the handlers
	formatter = logging.Formatter('%(asctime)s %(name)-8s %(levelname)-6s %(message)s')
	ch.setFormatter(formatter)
	# add the handlers to logger
	logging.getLogger('main').addHandler(ch)
	logging.getLogger('surfweb').addHandler(ch)
	browse(config.rootURLs)
