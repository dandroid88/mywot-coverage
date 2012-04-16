#!/usr/bin/env python
import sys, urllib2, re, os, sqlite3
from xml.dom.minidom import parseString
from bs4 import BeautifulSoup
import downloadRenderedPage as download

# This header avoids mywot.com's script detection system
headers = { 'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.142 Safari/535.19', \
            'Connection' : 'keep-alive\r\n', \
            'Cache-Control' : 'max-age=0\r\n', \
            'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n'}


def savePage(url, body):
    f = open(os.getcwd() + '/Site Samples/' + url.replace('http://', '').replace('/', '_') + '.txt', 'w')
    f.write(str(body))
    f.close()

def getOfficialRatings(url):
    dom = parseString(urllib2.urlopen('http://api.mywot.com/0.4/public_query2?url=' + url).read())
    categoryNames = { '0' : 'Trustworthiness', '1' : 'Vendor reliability', '2' : 'Privacy', '4' : 'Child safety'}
    ratings = {}
    for application in dom.getElementsByTagName('application'):
        ratings[categoryNames[application.getAttribute('name')]] = [application.getAttribute('r'), application.getAttribute('c')]
    print '\nOfficial Ratings:'
    print ratings
    return ratings

def printOfficialRatings(ratings):
    print "WOT ratings for " + url + ':\n'
    print 'Category\t\t| Confidence \t| Rating'
    print 'Trustworthiness \t| ' + applications[0].getAttribute('c') + '\t\t| ' + applications[0].getAttribute('r')
    print 'Vendor reliability \t| ' + applications[1].getAttribute('c') + '\t\t| ' + applications[1].getAttribute('r')
    print 'Privacy \t\t| ' + applications[2].getAttribute('c') + '\t\t| ' + applications[2].getAttribute('r')
    print 'Child safety \t\t| ' + applications[3].getAttribute('c') + '\t\t| ' + applications[3].getAttribute('r')


def getComments(url, body):
    lastPage =  int(body.findAll('div', { 'class' : 'paging'})[0].findAll('li', { 'class' : 'btn' })[-1]['page'])
    comments = []

    # Download all of the pages after they have been rendered - there is still a bug here...depending uponhow long it takes to get these pages the javascript may not have completed running...
    #for pageNum in range(1, lastPage + 1):
       # commentPageURL = 'http://www.mywot.com/en/scorecard/' + url.replace('http://', '') + '#page-' + str(pageNum)
       # download.main(url=commentPageURL)

    # Parse rendered pages
    for pageNum in range(1, lastPage + 1):
        #fileName = os.getcwd() + '/temp/temp-' + str(pageNum) + '.html'
        #f = open(fileName, 'r')
        #html = f.read()
        #f.close()
        #os.remove(fileName)

        commentPageURL = 'http://www.mywot.com/en/scorecard/' + url.replace('http://', '') + '#page-' + str(pageNum)
        html = download.main(url=commentPageURL)

        commentsSection = BeautifulSoup(html).find('div', { 'class' : 'sc-comment-row' })
        print 'Results for comments page ' + str(pageNum) + '\n'
        for c in commentsSection.findAll('div', { 'class' : 'sc-comment' }):
            comment = {}
            comment['date'] = c.find('em', { 'class' : 'date' }).text
            comment['author'] = c.find('strong', { 'class' : 'author' }).text
            print comment['author']
    print "getComments Not Done"

def getThirdPartyInfo(url):
    print "getThirdPartyInfo Not Done"

def getCommentStatistics(url, body):
    commentCount = {}
    table = body.find('table', id='category-table')
    for category in table.findAll('tr'):
        commentCount[category.find('div', { 'class' : 'cat-title'}).text] = category.find('span').text
    print '\nComment Statistics:'
    print commentCount
    return commentCount


if (len(sys.argv) > 1):
    url = sys.argv[1]
    if not re.match('(?=http)\w+', url):
        print "Please provide a valid URL"
    else:
        req = urllib2.Request('http://www.mywot.com/en/scorecard/' + url, None, headers)
        ratingsPageBody = BeautifulSoup(urllib2.urlopen(req).read()).body
        savePage(url, ratingsPageBody)
#        getOfficialRatings(url)
        getComments(url, ratingsPageBody)
#        getCommentStatistics(url, ratingsPageBody)
#        getThirdPartyInfo(url)
else:
    print 'Usage: checkWOT http://www.some_url.com'

