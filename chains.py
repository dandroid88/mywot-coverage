#!/usr/bin/env python

import sys, urllib2, re, os, MySQLdb, time, requests, signal, datetime
from xml.dom.minidom import parseString
from bs4 import BeautifulSoup
from pyvirtualdisplay import Display
from mywot.checkWOT import MywotEntry

#from webkit_browser.webkit_browser import Browser
from webkit_browser.webkit_browser_mod import Browser


#http://blog.cartercole.com/2010/08/new-seo-api-http-redirect-chain-test.html

HEADERS = { 'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.142 Safari/535.19', \
            'Connection' : 'keep-alive\r\n', \
            'Cache-Control' : 'max-age=0\r\n', \
            'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n'}

FOLDER = '/Site Samples/' + str(datetime.datetime.now()).replace(' ', '_')
TIMEOUT = 15


def tooLong(signum, frame):
    raise Exception("TIMED OUT")

signal.signal(signal.SIGALRM, tooLong)

def followChain(url):
    signal.alarm(TIMEOUT)
    try:
        requestChain = followChainRequests(url)
        webkitChain = followChainWebkit(url)
        return combineChains(webkitChain, requestChain)
    except Exception, exc:
        print url + ' ' + str(exc)
        return False

def combineChains(webkitChain, requestChain):
    history = requestChain
    if webkitChain and requestChain:
        for url in webkitChain:
            if not url in requestChain:
                history.append(url)
    return history               

def followChainRequests(url):
    history = []
    r = requests.get(url, headers=HEADERS)
    for redirect in r.history:
        history.append(redirect.url)
    return history

def followChainWebkit(url):
    b = Browser()
    b.open(url)
    dirtyhtml = b.main_frame['content'].read()
    history = b.history
    unicoded = str(dirtyhtml.encode("ascii", 'ignore')).decode("utf-8")
    html = eval(repr(unicoded)[1:])
    b.close()
    del b

    if url in history:
        return False
    else:
        return history

def runBatch(file_name, startingPoint, howMany):
    totalNumComments = 0
    urlCount = 0
    startTime = datetime.datetime.now()
    endPoint = startingPoint + howMany
    iteration = 0
    linkLengths = []
    chainCount = 0

    f = open(file_name, 'r')
    display = Display(visible=None).start()
    try:
        for url in f:
            if iteration >= startingPoint and iteration < endPoint:
                iterStartTime = datetime.datetime.now()
                history = followChain(url.split(' ')[0])
                urlCount += 1
                if history and len(history) > 1:
                    chainCount += 1
                    linkLengths.append(len(history))
                    # Call checkWOT
                    for url in history:
                        #print 'need to call checkWot here'
                        print url
                    print '\n'
            iteration += 1              
    finally:
        display.stop()
        runtime = datetime.datetime.now() - startTime
        
        print '\n-----------------------------------'
        print 'Total number of URLs:\t\t', urlCount
        print 'Total Number of Chains:\t\t', chainCount
        print 'Average Number of Links:\t', float(sum(linkLengths)) / len(linkLengths)
        print 'Average Runtime per URL:\t', runtime / urlCount
        print 'Total Runtime:\t\t\t', runtime
        print '\n\n'

if (len(sys.argv) > 1):
    os.mkdir(os.getcwd() + FOLDER)
    if '-batch' in sys.argv:
        runBatch(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
    else:
        url = sys.argv[1]
        if not re.match('(?=http)\w+', url):
            print "Please provide a valid URL"
        else:
            followChain(sys.argv[1].strip('\n\r'))
else:
    print 'Usage: chains.py http://www.some_url.com    OR     ./chains.py -batch listOfURLs.txt 0 10'
