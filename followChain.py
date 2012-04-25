#!/usr/bin/env python

import sys, urllib2, re, os, MySQLdb, time
import datetime
from xml.dom.minidom import parseString
from bs4 import BeautifulSoup
from webkit_browser.webkit_browser import Browser
from pyvirtualdisplay import Display


def followChain(url):
    b = Browser()
    b.open(url)
    dirtyhtml = b.main_frame['content'].read()
    print b.history
    unicoded = str(dirtyhtml.encode("ascii", 'ignore')).decode("utf-8")
    html = eval(repr(unicoded)[1:])
    b.close()

if (len(sys.argv) > 1):
    url = sys.argv[1]
    if not re.match('(?=http)\w+', url):
        print "Please provide a valid URL"
    else:
        followChain(url.strip('\n\r'))
else:
    print 'Usage: followChain.py http://www.some_url.com'
