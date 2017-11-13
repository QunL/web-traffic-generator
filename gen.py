#!/usr/bin/python

#
# written by @eric_capuano
# https://github.com/ecapuano/web-traffic-generator
#
# published under MIT license :) do what you want.
#
#20170714 shyft ADDED python 2.7 and 3.x compatibility and generic config
from __future__ import print_function 
import requests, re, time, random 
import logging
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

def doRequest(url):
	global dataMeter
	global goodRequests
	global badRequests
	sleepTime = random.randrange(config.minWait,config.maxWait)
	
	if config.debug:
		print("requesting: %s" % url)
	
	headers = {'user-agent': config.userAgent}
	
	try:
	except:
		r = requests.get(url, headers=headers, timeout=15)
	except requests.exceptions.RequestException as e:
		logging.getLogger("http").error('HTTPError[%s] to [%s]'%(str(e), url))
		return False
	except :
		import traceback
		logging.getLogger("http").error('Http 2[%s] generic exception: %s'%(url, traceback.format_exc()))
#		time.sleep(30) # else we'll enter 100% CPU loop in a net down situation
		return False
		
	status = r.status_code
	
	pageSize = len(r.content)
	dataMeter = dataMeter + pageSize

	
	if config.debug:
		print("Page size: %s" % pageSize)
		if ( dataMeter > 1000000 ):
			print("Data meter: %s MB" % (dataMeter / 1000000))
		else:
			print("Data meter: %s bytes" % dataMeter)
	
	if ( status != 200 ):
		badRequests+=1
		if config.debug:
			print("Response status: %s" % r.status_code)
		if ( status == 429 ):
			if config.debug:
				print("We're making requests too frequently... sleeping longer...")
			sleepTime+=30
	else:
		goodRequests+=1
	
	# need to sleep for random number of seconds!
	if config.debug:
		print("Good requests: %s" % goodRequests)
		print("Bad reqeusts: %s" % badRequests)
		print("Sleeping for %s seconds..." % sleepTime)
		
	time.sleep(sleepTime)
	return r
from BeautifulSoup import BeautifulSoup, SoupStrainer

test_str = """<li><a href="https://forums.craigslist.org/?areaID=15&amp;forumID=3232"><span class="txt">apple<sup class="c"></sup></span></a></li>
<li><a href="https://forums.craigslist.org/?areaID=15&amp;forumID=49"><span class="txt">arts<sup class="c"></sup></span></a></li>
<li><a href="https://forums.craigslist.org/?areaID=15&amp;forumID=575"><span class="txt">haiku<sup class="c"></sup></span></a></li>"""
test_str1 = '<a class="channel__subnav__nav-item" href="/channel/longreads">'
test_str2 = '		   <a href="http://accounts.craigslist.org/login/home">account</a>'
test_str3 = '<a href=" https://www.ebay.com/rpp/gift-cards" _sp="m570.l6463" class="gh-p"> Gift Cards</a>'


def test_geturl_re():
	getLinks(test_str)
	getLinks(test_str2)
	getLinks(test_str3)
from HTMLParser import HTMLParser
def getLinksRe(page_content):
	links1=set()
	links2=set()

	#pattern=r"(?:href\=\")(https?:\/\/[^\"]+)(?:\")"
	pattern=r"(?:href\=\")(https?:\/\/[^\"]+|(?:\/?\/)[^\"]+|(?:\?)[^\"]+)(?:\")"
	#print(page_content)
	matches = re.findall(pattern,str(page_content))
	
	for match in matches: # check all matches against config.blacklist
		if any(bl in match for bl in config.blacklist):
			pass
		else:
			h = HTMLParser()
			match = h.unescape(match)

			#print("URL1:%s"%str(match))
			links1.add(match)
	return links1
	
def getLinksBS(page_content):
	links2=set()

	for link in BeautifulSoup(page_content).findAll('a', href=True): #, parseOnlyThese=SoupStrainer('a')):
		#print("link:"+str(link))
		if link.get('href') == '#': continue
		if link.get('href').startswith('javascript'): continue
		#print("URL2:"+link.get('href'))
		links2.add(link.get('href'))
	return links2
import datetime
def getLinks(page_content):
	return getLinksRe(page_content)
def getLinksTestDiff(page_content):
	begtime = datetime.datetime.now()
	links1 = getLinksRe(page_content)
	endtime = datetime.datetime.now()
	print("Re use time: %s"%str(endtime - begtime))
	print("############################################")
	begtime = datetime.datetime.now()
	links2 = getLinksBS(page_content);
	endtime = datetime.datetime.now()
	print("BQ use time: %s"%str(endtime - begtime))
	Only2 = 0
	for link in links2:
		if (link not in links1):
			print("Only2:"+link)
			Only2 += 1
	print("#############")
	Only1 = 0
	for link in links1:
		if link not in links2:
			print("Only1:"+ link)
			Only1 += 1
	print("Got URL NUM %d:%d Only:%d:%d"%(len(links1),len(links2), Only1, Only2))
	return links2
	
def browse(urls):
	currURL = 1
	for url in urls:
		urlCount = len(urls)

		print("Request root URL:%s"%url)
		page = doRequest(url)  # hit current root URL
		if page:
			links = getLinks(page.content) # extract links from page
			linkCount = len(links)
		else:
			if config.debug:
				print("Error requesting %s" % url)
			continue
			
			
		depth=0
		while ( depth < config.clickDepth ):
			if config.debug:
				print("------------------------------------------------------")
				print("config.blacklist: %s" % config.blacklist )
			# set the link count, which will change throughout the loop
			linkCount = len(links)
			if ( linkCount > 1): # make sure we have more than 1 link to use
			
				if config.debug:
					print("URL: %s / %s -- Depth: %s / %s" \
						% (currURL,urlCount,depth,config.clickDepth))
					print("Choosing random link from total: %s" % linkCount)
					
				randomLink = random.randrange(0,linkCount - 1)
				
				if config.debug:
					print("Link chosen: %s of %s" % (randomLink,linkCount))
					
				clickLink = links[randomLink]
				
				try:
					# browse to random link on rootURL
					sub_page = doRequest(clickLink)
					if sub_page:
						checkLinkCount = len(getLinks(sub_page.content))
					else:
						if config.debug:
							print("Error requesting %s" % url)
						break
					
					
					checkLinkCount = len(getLinks(sub_page.content))

					# make sure we have more than 1 link to pick from 
					if ( checkLinkCount > 1 ):
						# extract links from the new page
						links = getLinks(sub_page.content)
					else:
						# else retry with current link list
						if config.debug:
							print("Not enough links found! Found: %s  -- " \
								"Going back up a level" % checkLinkCount)
						config.blacklist.insert(0,clickLink)
						# remove the dead-end link from our list
						del links[randomLink]
				except:
					if config.debug:
						print("Exception on URL: %s	 -- " \
							"removing from list and trying again!" % clickLink)
					# I need to expand more on exception type for config.debugging
					config.blacklist.insert(0,clickLink)
					# remove the dead-end link from our list
					del links[randomLink] 
					pass
				# increment counter whether request was successful or not 
				# so that we don't end up in an infinite failed request loop
				depth+=1
			else:
				# we land here if we went down a path that dead-ends
				# could implement logic to simply restart at same root
				if config.debug:
					print("Hit a dead end...Moving to next Root URL")
				config.blacklist.insert(0,url)
				depth = config.clickDepth 
			
		
		currURL+=1 # increase rootURL iteration
	if config.debug:
		print("Done.")

# initialize our global variables
dataMeter = 0
goodRequests = 0
badRequests = 0

while True:
#if True:
	#test_geturl_re()
	#exit()
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
						format = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
						datefmt = '%Y-%m-%d %H:%M:%S',
						filename = "log.txt")
	ch = logging.StreamHandler()
	ch.setLevel(logging.DEBUG)
	# create formatter and add it to the handlers
	formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
	ch.setFormatter(formatter)
	# add the handlers to logger
	logging.getLogger('main').addHandler(ch)
	logging.getLogger('http').addHandler(ch)
	browse(config.rootURLs)
