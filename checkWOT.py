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
    def __init__(self, url, extraInfo = None, chainID = 1):
        self.url = url
        self.chainID = chainID
        self.extraInfo = extraInfo

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
        cat_names = {'Good site' : 'good_site', 
                     'Useful, informative' : 'useful_informative', 
                     'Entertaining' : 'entertaining', 
                     'Good customer experience' : 'good_cus_exper', 
                     'Child friendly' : 'child_friendly', 
                     'Spam' : 'spam', 
                     'Annoying ads or popups' : 'annoying_ads', 
                     'Bad cusotmer experience' : 'bad_exper', 
                     'Phishing or other scams' : 'phishing', 
                     'Malicious content, viruses' : 'malicious_viruses', 
                     'Browser exploit' : 'bro_exploit', 
                     'Spyware or adware' : 'spyware', 
                     'Adult content' : 'adult_content', 
                     'Hateful or questionable content' : 'hateful', 
                     'Ethical issues' : 'eth_issues', 
                     'Useless' : 'useless' , 
                     'Other' : 'other'}
        commentCats = {}
        table = self.body.find('table', id='category-table')
        for cat in cat_names:
            commentCats[cat] = '0'
        for category in table.findAll('tr'):
            commentCats[category.find('div', { 'class' : 'cat-title'}).text] = category.find('span').text
        self.commentStats = commentCats

    def savePageToFile(self):
        f = open(os.getcwd() + FOLDER + '/' + self.url.replace('http://', '').replace('/', '_') + '.txt', 'w')
        f.write(str(self.body))
        f.close()

    def saveToDatabase(self):
        db = MySQLdb.connect(host="localhost", user="dan", passwd="", db="mywot")
        cursor = db.cursor()

        # Miscelanious Things not implemented yet
        spam_nonspam = False
        occurances = False
        time_1 = 1
        time_2 = 2

        # urls 
        url = self.url
        Trustworthiness = self.ratings['Trustworthiness'][1]
        Trust_confidence = self.ratings['Trustworthiness'][0]
        Vendor_Reliability = self.ratings['Vendor reliability'][1]
        Vendor_confidence = self.ratings['Vendor reliability'][0]
        Privacy = self.ratings['Privacy'][1]
        Privacy_confidence = self.ratings['Privacy'][0] 
        Child_safety = self.ratings['Child safety'][1]
        Child_confidence = self.ratings['Child safety'][0] 
        stats = self.commentStats

        urlID = None
        sql = """INSERT INTO urls(url, Trustworthiness, Trust_confidence, Vendor_Reliability, 
                 Vendor_confidence, Privacy, Privacy_confidence,
	     		 Child_safety, Child_confidence, spam_nonspam, occurances, time_1, time_2, 
                 good_site, useful_informative, entertaining, good_cus_exper,
                 child_friendly, spam, annoying_ads, bad_exper, phishing, 
                 malicious_viruses, bro_exploit, spyware, adult_content, 
                 hateful, eth_issues, useless, other, chain_id)
	     		 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                         %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                         %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

        try:
            #print 'Entering URL info into database'
            cursor.execute(sql.replace('\n', ''), (url, Trustworthiness, Trust_confidence, 
                                 Vendor_Reliability, Vendor_confidence, Privacy, Privacy_confidence, 
                                 Child_safety, Child_confidence, spam_nonspam, occurances, time_1, time_2, 
                                 stats['Good site'], stats['Useful, informative'], stats['Entertaining'],
                                 stats['Good customer experience'], stats['Child friendly'], stats['Spam'], 
                                 stats['Annoying ads or popups'], stats['Bad cusotmer experience'], 
                                 stats['Phishing or other scams'], stats['Malicious content, viruses'], 
                                 stats['Browser exploit'], stats['Spyware or adware'], 
                                 stats['Adult content'], stats['Hateful or questionable content'], 
                                 stats['Ethical issues'], stats['Useless'], stats['Other'], self.chainID))
            db.commit()
            urlID = cursor.lastrowid
            print urlID
        except MySQLdb.Error, e:
            print "%s" %e
            db.rollback()
            #print "\nInserting URL info Failed\n"

        if not urlID is None:
            # comments
            print 'Entering comments into database'
            sql = """INSERT INTO comments(comment_date, author, 
                     text, description, karma, votesEnabled, upvotes, 
                     downvotes, url_id)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""

            for comment in self.comments:
                try:
                    cursor.execute(sql, (comment['date'], comment['author'], 
                                         comment['text'], comment['description'], 
                                         comment['karma'], comment['votesEnabled'], 
                                         comment['upVotes'], comment['downVotes'], urlID))
                    db.commit()
                except MySQLdb.Error, e:
                    print "%s" %e
                    db.rollback()
                    print "\nInserting Comment Failed\n"

            db.close()
            print 'saveToDatabase not finished or tested'


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
                date = c.find('em', { 'class' : 'date' }).text.split('/')
                comment['date'] = datetime.date(int(date[2]), int(date[0]), int(date[1]))
                comment['author'] = c.find('strong', { 'class' : 'author' }).text
                comment['text'] = c.find('p', {'class' : 'sc-full-text'}).text.strip(' \n\r\t')
                comment['description'] = c.find('p', {'class' : 'note'}).text
                comment['karma'] = c.find('p', {'class' : 'note'})['class'][1]
                if hasattr(c.find('li', {'class' : 'icon-like'}), 'contents'):
                    comment['votesEnabled'] = True
                    comment['upVotes'] = c.find('li', {'class' : 'icon-like'}).contents[0].text
                    comment['downVotes'] = c.find('li', {'class' : 'icon-unlike'}).contents[0].text
                else:
                    comment['votesEnabled'] = False
                    comment['upVotes'] = '0'
                    comment['downVotes'] = '0'
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
            print 'Not in WOT Database (' + self.url + ')'
            self.saveToDatabase()
        return self

def runBatch(file_name, startingPoint, howMany, follow):
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
        runBatch(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), follow)
    else:
        url = sys.argv[1]
        if not re.match('(?=http)\w+', url):
            print "Please provide a valid URL"
        else:
            entry = MywotEntry(url.strip('\n\r')).getAllInfo()
            entry.printOfficialRatings()
else:
    print 'Usage: checkWOT.py http://www.some_url.com    OR     ./checkWOT.py -batch listOfURLs.txt 0 10'
