#!/usr/bin/env python

import sys, urllib2, re, os, MySQLdb, time
import datetime
from xml.dom.minidom import parseString
from bs4 import BeautifulSoup
#from webkit_browser.webkit_browser import Browser
from webkit_browser.webkit_browser_mod import Browser
from pyvirtualdisplay import Display
from mywot.checkWOT import MywotEntry

#http://blog.cartercole.com/2010/08/new-seo-api-http-redirect-chain-test.html


FOLDER = '/Site Samples/' + str(datetime.datetime.now()).replace(' ', '_')

b = None
display = None
urlCount = 0
chainCount = 0

def followChain(url):
    b = Browser()
    b.open(url)
    dirtyhtml = b.main_frame['content'].read()
    history = b.history
    unicoded = str(dirtyhtml.encode("ascii", 'ignore')).decode("utf-8")
    html = eval(repr(unicoded)[1:])
    b.close()

    if url in history:
        print 'Did not follow or is not a chain'
        print url
        print '\n'
        return False
    else:
        print url + ':'
        print history
        print ' '
        return history

if (len(sys.argv) > 1):
    if '-batch' in sys.argv[1]:
        f = open(sys.argv[2], 'r')
        display = Display(visible=None).start()
        try:
            for url in f:
                history = followChain(url.split(' ')[0])
                urlCount += 1
                if history:
                    chainCount += 1
                    # Call checkWOT
                    for redirect in history:
                        print 'need to call checkWot here'                
        finally:
            del b
            display.stop()
            print '\n' + str(urlCount) + ' URLs, ' + str(chainCount) + ' Chains'            

    elif not re.match('(?=http)\w+',  sys.argv[1]):
        print "Please provide a valid URL"
    else:
        followChain(sys.argv[1].strip('\n\r'))
else:
    print 'Usage: followChain.py http://www.some_url.com'
