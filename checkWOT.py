#!/usr/bin/env python
import sys, urllib2, re
from bs4 import BeautifulSoup
if (len(sys.argv) > 1):
    url = sys.argv[1]
    if not re.match('(?=http)\w+', url):
        print "Please provide a valid URL"
    else:
        apiResponse = urllib2.urlopen('http://api.mywot.com/0.4/public_query2?url=' + url).read()
        print apiResponse
        print "Loading " + url
        page = urllib2.urlopen(url).read()
        #print BeautifulSoup(page).prettify()
