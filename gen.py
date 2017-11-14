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
from HTMLParser import HTMLParser
import datetime

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
def remedyUrl(url, newUrl):
	#print("bef:"+newUrl)
	if newUrl.startswith('//'):
		hbeg = url.find('//')
		if  hbeg == -1:
			logging.getLogger(self._logEntity).error('getLinksRe cannot find // in page[%s] with new ULR [%s]' % (url, newUrl))
			return ''
		newUrl = url[0:hbeg]+newUrl
	elif newUrl.startswith('/'):
		hbeg = url.find('//')
		if  hbeg == -1:
			logging.getLogger(self._logEntity).error('getLinksRe cannot find // in page[%s] with new ULR [%s]' % (url, newUrl))
			return ''
		pbeg = url.find('/', hbeg+2)
		if  pbeg == -1:
			newUrl = url + newUrl
		else :
			newUrl = url[0:pbeg]+newUrl
	elif newUrl.startswith('?'):
		newUrl = url + newUrl
	#print("aft:"+newUrl)
	return newUrl
	
def testRemedyUrl():
	assert(remedyUrl("http://abc.com", "//cdf.com/a?b") == "http://cdf.com/a?b")
	assert(remedyUrl("https://abc.com", "//cdf.com/a?b") == "https://cdf.com/a?b")
	assert(remedyUrl("https://abc.com", "/cdf.com/a?b") == "https://abc.com/cdf.com/a?b")
	assert(remedyUrl("https://abc.com/", "/cdf.com/a?b") == "https://abc.com/cdf.com/a?b")
	assert(remedyUrl("https://abc.com/a.html", "?cdf/a?b") == "https://abc.com/a.html?cdf/a?b")
	assert(remedyUrl("https://abc.com", "http://cdf.com/a?b") == "http://cdf.com/a?b")
class surf_web():
	def __init__(self):
		self._dataMeter = 0
		self._goodRequests = 0
		self._badRequests = 0
		self._minWait = 3
		self._maxWait = 15
		self._userAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) ' \
			'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
		self._urlTimeout = 15
		self._logEntity = "http"
		self._blacklist = []
		self._width = 5
		self._depth = 5
		pass

	def doRequest(self, url):
		sleepTime = random.randrange(config.minWait,config.maxWait)
		headers = {'user-agent': config.userAgent}
		try:
			r = requests.get(url, headers=headers, timeout=self._urlTimeout)
		except requests.exceptions.RequestException as e:
			logging.getLogger(self._logEntity).error('HTTPError[%s] to [%s]'%(str(e), url))
			return False
		except :
			import traceback
			logging.getLogger(self._logEntity).error('Http 2[%s] exception: %s'%(url, traceback.format_exc()))
			return False
			
		status = r.status_code
		pageSize = len(r.content)
		logging.getLogger(self._logEntity).debug("doRequest[%s]status[%s]len[%d]" % (url, status, pageSize))
		self._dataMeter = self._dataMeter + pageSize
		if ( status != 200 ):
			self._badRequests+=1
			logging.getLogger(self._logEntity).info("Response status[%s]for[%s]" % (r.status_code, url))
		else:
			self._goodRequests+=1
			
		time.sleep(sleepTime)
		return r

	def getLinksRe(self, url, page_content):
		links1=set()
		links2=set()

		#pattern=r"(?:href\=\")(https?:\/\/[^\"]+)(?:\")"
		pattern=r"(?:href\=\")(https?:\/\/[^\"]+|(?:\/?\/)[^\"]+|(?:\?)[^\"]+)(?:\")"
		#print(page_content)
		matches = re.findall(pattern,str(page_content))
		
		for match in matches: # check all matches against config.blacklist
			if any(bl in match for bl in self._blacklist):
				pass
			else:
				try:
					h = HTMLParser()
					match = h.unescape(match)
				except:
					import traceback
					logging.getLogger(self._logEntity).error('HTMLParser.unescape 2[%s] exception: %s'%(url, traceback.format_exc()))
					continue

				#print("URL1:%s"%str(match))
				match = remedyUrl(url, match)
				if match == '':
					continue
				links1.add(match)
		return links1
	
	def getLinks(self, url, page_content):
		return self.getLinksRe(url, page_content)
	# browse the url and click width+random urls and depth in the every url.    
	def _browseUrl(self, url, width, depth):
		logging.getLogger(self._logEntity).debug("_browseUrl:%s width %d depth %d"%(url, width, depth))
		page = self.doRequest(url)  # hit current root URL
		if depth <= 0 : return
		if width <= 0 : return
		if page:
			links = self.getLinks(url, page.content) # extract links from page
			linkCount = len(links)
		else:
			logging.getLogger(self._logEntity).error("Error requesting %s" % url)
			return
			
		linkCount = len(links)
		if linkCount < width:
			realWidth = linkCount
		else:
			realWidth = width
		for i in range(1, realWidth):
			clickLink = random.choice(tuple(links))
			logging.getLogger(self._logEntity).debug("Random[%d/%d]get[%s]in[%s]:%d" % (i, realWidth, clickLink, url, linkCount))
			self._browseUrl(clickLink, width, depth-1)
	def browseUrl(self, url):
		self._browseUrl(url, self._width, self._depth)
def test_geturl_re():
	test_str = """<li><a href="https://forums.craigslist.org/?areaID=15&amp;forumID=3232"><span class="txt">apple<sup class="c"></sup></span></a></li>
	<li><a href="https://forums.craigslist.org/?areaID=15&amp;forumID=49"><span class="txt">arts<sup class="c"></sup></span></a></li>
	<li><a href="https://forums.craigslist.org/?areaID=15&amp;forumID=575"><span class="txt">haiku<sup class="c"></sup></span></a></li>"""
	test_str1 = '<a class="channel__subnav__nav-item" href="/channel/longreads">'
	test_str2 = '		   <a href="http://accounts.craigslist.org/login/home">account</a>'
	test_str3 = '<a href=" https://www.ebay.com/rpp/gift-cards" _sp="m570.l6463" class="gh-p"> Gift Cards</a>'
	sw = surf_web()
	sw.getLinks('abc.com', test_str)
	sw.getLinks('abc.com', test_str2)
	sw.getLinks('abc.com', test_str3)
def getLinksBS(url, page_content):
	from BeautifulSoup import BeautifulSoup, SoupStrainer
	links2=set()

	for link in BeautifulSoup(page_content).findAll('a', href=True): #, parseOnlyThese=SoupStrainer('a')):
		#print("link:"+str(link))
		if link.get('href') == '#': continue
		if link.get('href').startswith('javascript'): continue
		#print("URL2:"+link.get('href'))
		links2.add(remedyUrl(url, link.get('href')))
	return links2

def getLinksTestDiff(url):
	sw = surf_web()
	page = sw.doRequest(url)  # hit current root URL
	begtime = datetime.datetime.now()
	sw = surf_web()
	links1 = sw.getLinksRe(url, page.content)
	endtime = datetime.datetime.now()
	print("Re use time: %s"%str(endtime - begtime))
	print("############################################")
	begtime = datetime.datetime.now()
	links2 = getLinksBS(url, page.content);
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
	sw = surf_web()
	sw._maxWait = config.maxWait
	sw._minWait = config.minWait
	sw._blacklist = config.blacklist
	sw._depth = config.clickDepth
	sw._width = config.clickWidth
	for url in urls:
		urlCount = len(urls)

		logging.getLogger('main').debug("Request root URL:%s"%url)
		sw.browseUrl(url)  # hit current root URL
		if config.debug:
			if ( sw._dataMeter > 1000000 ):
				print("Data meter: %s MB" % (sw._dataMeter / 1000000))
			else:
				print("Data meter: %s bytes" % sw._dataMeter)
			print("Good requests: %s" % sw._goodRequests)
			print("Bad reqeusts: %s" % sw._badRequests)
			
	logging.getLogger('main').debug("Done.")

#while True:
if True:
	'''testRemedyUrl()
	test_geturl_re()
	getLinksTestDiff("https://digg.com")
	getLinksTestDiff("https://cnn.com")
	exit() '''
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
	logging.getLogger('http').addHandler(ch)
	browse(config.rootURLs)
