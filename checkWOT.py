#!/usr/bin/env python
import sys, urllib2, re, os, MySQLdb, time
import datetime
from xml.dom.minidom import parseString
from bs4 import BeautifulSoup
from webkit_browser.webkit_browser import Browser
from pyvirtualdisplay import Display

FOLDER = '/Site Samples/' + str(datetime.datetime.now()).replace(' ', '_')
HEADERS = { 'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.142 Safari/535.19', \
            'Connection' : 'keep-alive\r\n', \
            'Cache-Control' : 'max-age=0\r\n', \
            'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n'}


class MywotEntry():
    def __init__(self, url):
        self.url = url

    def getOfficialRatings(self):
        apiURL = 'http://api.mywot.com/0.4/public_query2?target=' + self.url.replace('http://', '').split('/')[0]
        dom = parseString(urllib2.urlopen(apiURL).read())
        categoryNames = { '0' : 'Trustworthiness', '1' : 'Vendor reliability', '2' : 'Privacy', '4' : 'Child safety'}
        ratings = {}
        for application in dom.getElementsByTagName('application'):
            ratings[categoryNames[application.getAttribute('name')]] = [application.getAttribute('r'), application.getAttribute('c')]
        self.ratings = ratings

    def printOfficialRatings(self):
        print 'WOT ratings for ' + self.url + ':'
        print 'Category\t\t| Confidence \t| Rating'
        print 'Trustworthiness \t| ' + self.ratings['Trustworthiness'][1] + '\t\t| ' + self.ratings['Trustworthiness'][0]
        print 'Vendor reliability \t| ' + self.ratings['Vendor reliability'][1] + '\t\t| ' + self.ratings['Vendor reliability'][0]
        print 'Privacy \t\t| ' + self.ratings['Privacy'][1] + '\t\t| ' + self.ratings['Privacy'][0]
        print 'Child safety \t\t| ' + self.ratings['Child safety'][1] + '\t\t| ' + self.ratings['Child safety'][0]
        print '\n'

    def getCommentStatistics(self):
        commentCount = {}
        table = self.body.find('table', id='category-table')
        for category in table.findAll('tr'):
            commentCount[category.find('div', { 'class' : 'cat-title'}).text] = category.find('span').text
        self.commentStats =  commentCount

    def savePageToFile(self):
        f = open(os.getcwd() + FOLDER + '/' + self.url.replace('http://', '').replace('/', '_') + '.txt', 'w')
        f.write(str(self.body))
        f.close()

    def saveToDatabase(self):
        notDone = True
        #print 'saveToDatabase not implemented'


    def getThirdPartyInfo(self):
        notDone = True        
        #print "getThirdPartyInfo Not Done"

    def getComments(self):
        display = Display(visible=None).start()
        lastPage = 1
        paging = self.body.findAll('div', { 'class' : 'paging'})
        if paging:
            lastPage =  int(paging[0].findAll('li', { 'class' : 'btn' })[-1]['page'])
        comments = []

        # Get a list of URLs to fetch
        for pageNum in range(1, lastPage + 1):
            commentURL = 'http://www.mywot.com/en/scorecard/' + self.url.replace('http://', '') + '#page-' + str(pageNum)

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
        self.comments = comments


    def getAllInfo(self):
        self.getOfficialRatings()
        if self.ratings:
            # Request the html page
            req = urllib2.Request('http://www.mywot.com/en/scorecard/' + self.url, None, HEADERS)
            self.body = BeautifulSoup(urllib2.urlopen(req).read()).body

            # Extract information
            self.savePageToFile()
            self.getCommentStatistics()
            self.getComments()
            self.getThirdPartyInfo()
            self.saveToDatabase()
            
        else:
            print 'Not in WOT Database'
            self.saveToDatabase()
        return self

def runBatch(file_name, startingPoint, howMany):
    totalNumComments = 0
    urlCount = 0
    startTime = datetime.datetime.now()
    endPoint = startingPoint + howMany
    f = open(file_name, 'r')
    iteration = 0
    for url in f:
        if iteration >= startingPoint and iteration < endPoint:
            iterStartTime = datetime.datetime.now()
            entry = MywotEntry(url.split(' ')[0].strip('\n\r')).getAllInfo()
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
    if '-batch' in sys.argv[1]:
        runBatch(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
    else:
        url = sys.argv[1]
        if not re.match('(?=http)\w+', url):
            print "Please provide a valid URL"
        else:
            entry = MywotEntry(url.strip('\n\r')).getAllInfo()
            entry.printOfficialRatings()
else:
    print 'Usage: checkWOT.py http://www.some_url.com    OR     ./checkWOT.py -batch listOfURLs.txt 0 10'
