#!/usr/bin/env python

import sys, urllib2, re, os, MySQLdb, time, requests, signal, datetime
from xml.dom.minidom import parseString
from bs4 import BeautifulSoup
from pyvirtualdisplay import Display
from mywot.mywot import MywotEntry
from webkit_browser.webkit_browser_mod import Browser
from guppy import hpy

DATABASE = 'mywot'
HEADERS = { 'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.142 Safari/535.19', \
            'Connection' : 'keep-alive\r\n', \
            'Cache-Control' : 'max-age=0\r\n', \
            'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n'}

FOLDER = '/Site Samples/' + str(datetime.datetime.now()).replace(' ', '_')
TIMEOUT = 20

def tooLong(signum, frame):
    h = hpy()
    print h.heap()
    raise Exception("TIMED OUT\n")

signal.signal(signal.SIGALRM, tooLong)

def followChain(url):
    signal.alarm(TIMEOUT)
    try:
        requestChain = followChainRequests(url)
        webkitChain = followChainWebkit(url)
        signal.alarm(0)
        return combineChains(webkitChain, requestChain)
    except Exception, exc:
        sys.stderr.write(url + ' ' + str(exc))
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

def createNewChain(url):
    db = MySQLdb.connect(host="localhost", user="dan", passwd="", db=DATABASE)
    cursor = db.cursor()
    newID = False
    
    try:
        cursor.execute("SELECT chain_id FROM chains ORDER BY chain_id DESC LIMIT 0,1")
        newID = int(cursor.fetchall()[0][0]) + 1
    except MySQLdb.Error, e:
        print "%s" %e
        print "\nInserting Chain Failed\n"

    sql = """INSERT INTO chains(chain_id, original_url)
             VALUES (%s, %s)"""

    if newID:
        try:
            cursor.execute(sql, (newID, url))
            db.commit()
        except MySQLdb.Error, e:
            print "%s" %e
            db.rollback()
            print "\nInserting Chain Failed\n"

    db.close()
    return newID

def runBatch(file_name, startingPoint, howMany, getComments):
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
            signal.alarm(TIMEOUT)
            iteration += 1
            try:
                if iteration >= startingPoint and iteration < endPoint:
                    iterStartTime = datetime.datetime.now()
                    print str(iteration) + ': ' + url.split(' ')[0].strip('\n\r')
                    history = followChain(url.split(' ')[0])
                    urlCount += 1
                    if history and len(history) > 1:
                        chainCount += 1
                        linkLengths.append(len(history))
                        extraInfo = {'spam_nonspam' : 0 if 'nonspam' in url.split(' ')[1] else 1,
                                     'occurances' : url.split(' ')[2],
                                     'time_1' : url.split(' ')[3],
                                     'time_2' : url.split(' ')[4]}
                        chainID = createNewChain(url.split(' ')[0])
                        if chainID:
                            for url in history:
                                print '\t' + url.split(' ')[0].strip('\n\r')
                                entry = MywotEntry(url.split(' ')[0].strip('\n\r').replace('http://bitly.com/a/warning?url=', ''), FOLDER, extraInfo=extraInfo, chainID=chainID, getComments=getComments).getAllInfo()
            except Exception, exc:
                sys.stderr.write(url + ' ' + str(exc))
            
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
        os._exit(1)

if (len(sys.argv) > 1):
    os.mkdir(os.getcwd() + FOLDER)
    getComments = True
    if '-skipcomments' in sys.argv:
        getComments = False
    if '-batch' in sys.argv:
        runBatch(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), getComments)
    else:
        url = sys.argv[1]
        if not re.match('(?=http)\w+', url):
            print "Please provide a valid URL"
        else:
            followChain(sys.argv[1].strip('\n\r'))
else:
    print 'Usage: chains.py http://www.some_url.com    OR     ./chains.py -batch listOfURLs.txt 0 10 [-skipComments]'
