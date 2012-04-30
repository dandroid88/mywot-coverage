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
    history = b.history
    unicoded = str(dirtyhtml.encode("ascii", 'ignore')).decode("utf-8")
    html = eval(repr(unicoded)[1:])
    b.close()
    del b

    if url in history:
        print 'Did not follow or is not a chain'
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
        for url in f:
            history = followChain(url.split(' ')[0])
            if history:
            # Call checkWOT
            for redirect in history:
                print 'need to call checkWot here'                
            
        display.stop()
    elif not re.match('(?=http)\w+',  sys.argv[1]):
        print "Please provide a valid URL"
    else:
        followChain(sys.argv[1].strip('\n\r'))
else:
    print 'Usage: followChain.py http://www.some_url.com'
