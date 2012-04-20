#!/usr/bin/env python
import sys, urllib2, re, os, MySQLdb, datetime, time
from xml.dom.minidom import parseString
from bs4 import BeautifulSoup
from webkit_browser.webkit_browser import Browser
from pyvirtualdisplay import Display

FOLDER = '/Site Samples/' + str(datetime.datetime.now()).replace(' ', '_')
HEADERS = { 'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.142 Safari/535.19', \
            'Connection' : 'keep-alive\r\n', \
            'Cache-Control' : 'max-age=0\r\n', \
            'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n'}

def runBatch(file_name):
    f = open(file_name, 'r')
    for url in f:
        getAllInfo(url.strip('\n').strip('\r'))


def savePage(url, body):
    f = open(os.getcwd() + FOLDER + '/' + url.replace('http://', '').replace('/', '_') + '.txt', 'w')
    f.write(str(body))
    f.close()

def getOfficialRatings(url):
    dom = parseString(urllib2.urlopen('http://api.mywot.com/0.4/public_query2?target=' + url.replace('http://', '')).read())
    categoryNames = { '0' : 'Trustworthiness', '1' : 'Vendor reliability', '2' : 'Privacy', '4' : 'Child safety'}
    ratings = {}
    for application in dom.getElementsByTagName('application'):
        ratings[categoryNames[application.getAttribute('name')]] = [application.getAttribute('r'), application.getAttribute('c')]
    return ratings

def printOfficialRatings(ratings, url):
    print 'WOT ratings for ' + url + ':'
    print 'Category\t\t| Confidence \t| Rating'
    print 'Trustworthiness \t| ' + ratings['Trustworthiness'][1] + '\t\t| ' + ratings['Trustworthiness'][0]
    print 'Vendor reliability \t| ' + ratings['Vendor reliability'][1] + '\t\t| ' + ratings['Vendor reliability'][0]
    print 'Privacy \t\t| ' + ratings['Privacy'][1] + '\t\t| ' + ratings['Privacy'][0]
    print 'Child safety \t\t| ' + ratings['Child safety'][1] + '\t\t| ' + ratings['Child safety'][0]
    print '\n'

def getComments(url, body):
    display = Display(visible=None).start()
    lastPage =  int(body.findAll('div', { 'class' : 'paging'})[0].findAll('li', { 'class' : 'btn' })[-1]['page'])
    comments = []

    # Get a list of URLs to fetch
    for pageNum in range(1, lastPage + 1):
        commentURL = 'http://www.mywot.com/en/scorecard/' + url.replace('http://', '') + '#page-' + str(pageNum)

        # Render pages
        b = Browser()
        b.open(commentURL)
        dirtyhtml = b.main_frame['content'].read()
        unicoded = str(dirtyhtml.encode("ascii", 'ignore')).decode("utf-8")
        html = eval(repr(unicoded)[1:])
        b.close()

        # Parse rendered pages
        commentsSection = BeautifulSoup(html).find('div', { 'class' : 'sc-comment-row' })
        for c in commentsSection.findAll('div', { 'class' : 'sc-comment' }):
            comment = {}
            comment['date'] = c.find('em', { 'class' : 'date' }).text
            comment['author'] = c.find('strong', { 'class' : 'author' }).text
            #Not sure why, but the order of these strip statements seems to matter, also, there still seems to be trailing tabs...
            comment['text'] = c.find('p', {'class' : 'sc-full-text'}).text.strip(' \n\r\t')
            comment['description'] = c.find('p', {'class' : 'note'}).text
            comment['karma'] = c.find('p', {'class' : 'note'})['class'][1]
            comment['upVotes'] = c.find('li', {'class' : 'icon-like'}).contents[0].text
            comment['downVotes'] = c.find('li', {'class' : 'icon-unlike'}).contents[0].text
            comments.append(comment)
    del b
    display.stop()
    return comments

def getThirdPartyInfo(url):
    print "getThirdPartyInfo Not Done"

def getCommentStatistics(url, body):
    commentCount = {}
    table = body.find('table', id='category-table')
    for category in table.findAll('tr'):
        commentCount[category.find('div', { 'class' : 'cat-title'}).text] = category.find('span').text
    return commentCount

def getAllInfo(url):
        ratings = getOfficialRatings(url)
        if ratings:
            # Request the html page
            req = urllib2.Request('http://www.mywot.com/en/scorecard/' + url, None, HEADERS)
            ratingsPageBody = BeautifulSoup(urllib2.urlopen(req).read()).body

            # Extract information
            savePage(url, ratingsPageBody)
            getCommentStatistics(url, ratingsPageBody)
            getComments(url, ratingsPageBody)
        #    getThirdPartyInfo(url)
#            saveToDatabase()
        else:
            print 'Not in WOT Database'
#            saveToDatabase(url)

if (len(sys.argv) > 1):
    os.mkdir(os.getcwd() + FOLDER)
    if '-batch' in sys.argv[1]:
        print 'Running batch on ' + sys.argv[2]
        runBatch(sys.argv[2])
    else:
        url = sys.argv[1]
        if not re.match('(?=http)\w+', url):
            print "Please provide a valid URL"
        else:
            getAllInfo(url)
else:
    print 'Usage: checkWOT.py http://www.some_url.com    OR     ./checkWOT.py -batch listOfURLs.txt'
