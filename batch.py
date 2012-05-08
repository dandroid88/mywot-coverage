#!/usr/bin/env python

import sys, urllib2, re, os, MySQLdb, time
import datetime
from xml.dom.minidom import parseString
from bs4 import BeautifulSoup
from webkit_browser.webkit_browser import Browser
from pyvirtualdisplay import Display
from mywot.mywot import MywotEntry

FOLDER = '/Site Samples/' + str(datetime.datetime.now()).replace(' ', '_')

def runBatch(file_name, startingPoint, howMany, getComments):
    totalNumComments = 0
    urlCount = 0
    startTime = datetime.datetime.now()
    endPoint = startingPoint + howMany
    f = open(file_name, 'r')
    iteration = 0
    for url in f:
        if iteration >= startingPoint and iteration < endPoint:
            iterStartTime = datetime.datetime.now()
            entry = MywotEntry(url.split(' ')[0].strip('\n\r'), FOLDER, getComments=getComments).getAllInfo()
            urlCount += 1
            if entry.ratings:
                totalNumComments += len(entry.comments)
                print 'URL ' + str(iteration) + ' took ' + str(datetime.datetime.now() - iterStartTime) + ' and had ' + str(len(entry.comments)) + ' comments (' + entry.url + ')' 
        iteration += 1
    runtime = datetime.datetime.now() - startTime
    print '\n-----------------------------------'
    print 'Total number of URLs:\t\t', urlCount
    print 'Total Number of Comments:\t', totalNumComments
    print 'Average Number of Comments:\t', totalNumComments / urlCount
    print 'Average Runtime per URL:\t', runtime / urlCount
    print 'Total Runtime:\t\t\t', runtime

if (len(sys.argv) > 1):
    os.mkdir(os.getcwd() + FOLDER)
    getComments = True
    if '-skipcomments' in sys.argv:
        getComments = False
    if '-batch' in sys.argv[1]:
        runBatch(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), getComments)
    else:
        url = sys.argv[1]
        if not re.match('(?=http)\w+', url):
            print "Please provide a valid URL"
        else:
            entry = MywotEntry(url.strip('\n\r')).getAllInfo()
            entry.printOfficialRatings()
else:
    print 'Usage: checkWOT.py http://www.some_url.com    OR     ./checkWOT.py -batch listOfURLs.txt 0 10'
