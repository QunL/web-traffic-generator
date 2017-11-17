#!/usr/bin/python
#
# written by liqun@ncl
# https://github.com/QunL/web-traffic-generator
#
# based on https://github.com/ecapuano/web-traffic-generator
#20170714 shyft ADDED python 2.7 and 3.x compatibility and generic config
'''
The module surf_web is a class simulate surfing web from root url
click random links and following the link random clicks until certain depth.
'''
from __future__ import print_function
import re
import time
import random
import datetime
import logging
import HTMLParser
import urllib2

LOG_ENTITY = 'surfweb'
def remedy_url(url, new_url):
    ''' The fund remedy new_url retrieved from url page. The new_url might be
    //cef.com/, /a.thml, ?a=c, etc. '''
    #print("bef:"+new_url)
    if new_url.startswith('//'):
        hbeg = url.find('//')
        if  hbeg == -1:
            logging.getLogger(LOG_ENTITY).error('get_links_re cannot '\
                'find // in page[%s] with new ULR [%s]', url, new_url)
            return ''
        new_url = url[0:hbeg]+new_url
    elif new_url.startswith('/'):
        hbeg = url.find('//')
        if  hbeg == -1:
            logging.getLogger(LOG_ENTITY).error('get_links_re cannot '\
                'find // in page[%s] with new ULR [%s]', url, new_url)
            return ''
        pbeg = url.find('/', hbeg+2)
        if pbeg == -1:
            new_url = url + new_url
        else:
            new_url = url[0:pbeg]+new_url
    elif new_url.startswith('?'):
        new_url = url + new_url
    #print("aft:"+new_url)
    return new_url

def test_remedy_url():
    ''' The func test remedy_url. '''
    assert(remedy_url("http://abc.com", "//cdf.com/a?b")
           == "http://cdf.com/a?b")
    assert(remedy_url("https://abc.com", "//cdf.com/a?b")
           == "https://cdf.com/a?b")
    assert(remedy_url("https://abc.com", "/cdf.com/a?b")
           == "https://abc.com/cdf.com/a?b")
    assert(remedy_url("https://abc.com/", "/cdf.com/a?b")
           == "https://abc.com/cdf.com/a?b")
    assert(remedy_url("https://abc.com/a.html", "?cdf/a?b")
           == "https://abc.com/a.html?cdf/a?b")
    assert(remedy_url("https://abc.com", "http://cdf.com/a?b")
           == "http://cdf.com/a?b")
class SurfWeb(object):
    '''The class simulates surfing web from root url click random links and
    following the link random clicks until certain depth.'''
    def __init__(self):
        self.data_meter = 0
        self.good_requests = 0
        self.bad_requests = 0
        self.min_wait = 1
        self.max_wait = 5
        self.user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) '\
            'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 '\
            'Safari/537.36'
        self.url_timeout = 1
        self.log_entity = LOG_ENTITY
        self.black_list = []
        self.width = 2
        self.depth = 2
        self.url_opener = urllib2.build_opener()
        self.url_opener.addheaders = [('User-agent', self.user_agent)]

    def do_request(self, url):
        ''' The func request the url, return the request.response.'''
        sleep_time = random.randrange(self.min_wait, self.max_wait)
        try:
            req = self.url_opener.open(url, timeout=self.url_timeout)
            page_content = req.read()
            status = req.getcode()
            page_size = len(page_content)
        except urllib2.HTTPError, exp:
            logging.getLogger(self.log_entity).error('HTTPError[%s] to [%s]',
                str(exp.code) + str(exp.reason), url)
            return ''
        except urllib2.URLError, exp:
            logging.getLogger(self.log_entity).error(
                'HTTPURLError [%s] to [%s]', str(exp.reason), url)
            return ''
        except Exception:
            import traceback
            logging.getLogger(self.log_entity).error('Exception: ' + traceback.format_exc())
            return ''
        logging.getLogger(self.log_entity).debug(
            "do_request[%s]status[%s]len[%d]", url, status, page_size)
        self.data_meter = self.data_meter + page_size
        if status != 200:
            self.bad_requests += 1
            logging.getLogger(self.log_entity).info(
                "Response status[%s]for[%s]", status, url)
        else:
            self.good_requests += 1

        time.sleep(sleep_time)
        return page_content

    def get_links_re(self, url, page_content):
        ''' The func return the link list in page_content from url by re.'''
        links1 = set()

        #pattern=r"(?:href\=\")(https?:\/\/[^\"]+)(?:\")"
        pattern = r"(?:href\=\")(https?:\/\/[^\"]+|(?:\/?\/)[^\"]+|(?:\?)[^\"]+)(?:\")"
        #print(page_content)
        matches = re.findall(pattern, str(page_content))

        for match in matches: # check all matches against self.black_list
            if any(bl in match for bl in self.black_list):
                pass
            else:
                try:
                    hparser = HTMLParser.HTMLParser()
                    match = hparser.unescape(match)
                except HTMLParser.HTMLParseError:
                    import traceback
                    logging.getLogger(self.log_entity).error(
                        'HTMLParser.unescape 2[%s] exception: %s',
                        url, traceback.format_exc())
                    continue

                #print("URL1:%s"%str(match))
                match = remedy_url(url, match)
                if match == '':
                    continue
                links1.add(match)
        return links1

    def get_links(self, url, page_content):
        ''' The func return the link list in page_content from url.'''
        return self.get_links_re(url, page_content)
    # browse the url and click width+random urls and depth in the every url.
    def browse_url_wd(self, url, width, depth):
        ''' The func surf the link with width random click in the page and
        following the link for depth.'''
        logging.getLogger(self.log_entity).debug(
            "browse_url_wd:%s width %d depth %d", url, width, depth)
        page_content = self.do_request(url)  # hit current root URL
        if depth <= 0:
            return
        if width <= 0:
            return
        if page_content:
            links = self.get_links(url, page_content)
            link_count = len(links)
        else:
            logging.getLogger(self.log_entity).error(
                "Error requesting %s", url)
            return

        link_count = len(links)
        if link_count < width:
            real_width = link_count
        else:
            real_width = width
        for i in range(1, real_width):
            click_link = random.choice(tuple(links))
            logging.getLogger(self.log_entity).debug(
                "Random[%d/%d]get[%s]in[%s]:%d", i, real_width, click_link,
                url, link_count)
            self.browse_url_wd(click_link, width, depth-1)
    def browse_url(self, url):
        ''' The func surf the link with width random click in the page and
        following the link for depth.'''
        self.browse_url_wd(url, self.width, self.depth)

# For test and compare.
def test_geturl_re():
    '''Test func getLinsRe'''
    test_str = """<li><a href="https://forums.craigslist.org/?areaID=15&amp;forumID=3232">
    <span class="txt">apple<sup class="c"></sup></span></a></li>
    <li><a href="https://forums.craigslist.org/?areaID=15&amp;forumID=49">
    <span class="txt">arts<sup class="c"></sup></span></a></li>
    <li><a href="https://forums.craigslist.org/?areaID=15&amp;forumID=575">
    <span class="txt">haiku<sup class="c"></sup></span></a></li>"""
    test_str1 = '<a class="channel__subnav__nav-item" href="/channel/longreads">'
    test_str2 = '  <a href="http://accounts.craigslist.org/login/home">account</a>'
    test_str3 = '<a href=" https://www.ebay.com/rpp/gift-cards" '\
        '_sp="m570.l6463" class="gh-p"> Gift Cards</a>'
    surf_web = SurfWeb()
    surf_web.get_links('abc.com', test_str)
    surf_web.get_links('abc.com', test_str1)
    surf_web.get_links('abc.com', test_str2)
    surf_web.get_links('abc.com', test_str3)
def get_links_bs(url, page_content):
    ''' The func return the link list in page_content from url by bs.'''
    from BeautifulSoup import BeautifulSoup
    #, SoupStrainer
    links2 = set()

    for link in BeautifulSoup(page_content).findAll('a', href=True):
        #, parseOnlyThese=SoupStrainer('a')):
        #print("link:"+str(link))
        if link.get('href') == '#':
            continue
        if link.get('href').startswith('javascript'):
            continue
        #print("URL2:"+link.get('href'))
        links2.add(remedy_url(url, link.get('href')))
    return links2

def test_get_links_diff(url):
    '''Test func different get_links re with bs'''
    surf_web = SurfWeb()
    page_content = surf_web.do_request(url)  # hit current root URL
    begtime = datetime.datetime.now()
    surf_web = SurfWeb()
    links1 = surf_web.get_links_re(url, page_content)
    endtime = datetime.datetime.now()
    print("Re use time: %s"%str(endtime - begtime))
    print("############################################")
    begtime = datetime.datetime.now()
    links2 = get_links_bs(url, page_content)
    endtime = datetime.datetime.now()
    print("BQ use time: %s"%str(endtime - begtime))
    only2 = 0
    for link in links2:
        if link not in links1:
            print("only2:"+link)
            only2 += 1
    print("#############")
    only1 = 0
    for link in links1:
        if link not in links2:
            print("only1:" + link)
            only1 += 1
    print("Got URL NUM %d:%d Only:%d:%d"%(len(links1), len(links2), only1, only2))
    return links2

# For test.
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)-8s %(levelname)-6s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        filename="log.txt")
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s %(name)-8s %(levelname)-6s %(message)s')
    ch.setFormatter(formatter)
    # add the handlers to logger
    logging.getLogger(LOG_ENTITY).addHandler(ch)

    test_remedy_url()
    test_geturl_re()
    test_get_links_diff("https://digg.com")
    test_get_links_diff("https://cnn.com")
