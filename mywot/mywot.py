#!/usr/bin/env python

import sys, urllib2, re, os, MySQLdb, time
import datetime
from xml.dom.minidom import parseString
from bs4 import BeautifulSoup
from webkit_browser.webkit_browser import Browser
from pyvirtualdisplay import Display

DATABASE = 'mywot'
COMMENT_PAGE_LIMIT = 1000
HEADERS = { 'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.142 Safari/535.19', \
            'Connection' : 'keep-alive\r\n', \
            'Cache-Control' : 'max-age=0\r\n', \
            'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n'}


class MywotEntry():
    def __init__(self, url, folder, extraInfo = {'spam_nonspam' : False, 'occurances' : False, 'time_1' : 0, 'time_2' : 0}, chainID = 1, getComments = True, popularity = 0):
        self.url = url
        self.folder = folder
        self.chainID = chainID
        self.extraInfo = extraInfo
        self.shouldGetComments = getComments
        self.comments = []
        self.popularity = popularity

    def getOfficialRatings(self):
        apiURL = 'http://api.mywot.com/0.4/public_query2?target=' + self.url.replace('http://', '').split('/')[0]
        dom = parseString(urllib2.urlopen(apiURL).read())
        categoryNames = { '0' : 'Trustworthiness', '1' : 'Vendor reliability', '2' : 'Privacy', '4' : 'Child safety'}
        ratings = {}
        for application in dom.getElementsByTagName('application'):
            ratings[categoryNames[application.getAttribute('name')]] = [application.getAttribute('r'), application.getAttribute('c')]
        # if there are any ratings, fill in the empty ratings with None
        if ratings:
            for cat in categoryNames:
                if not categoryNames[cat] in ratings:
                    ratings[categoryNames[cat]] = [None, None]
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
        f = open(os.getcwd() + self.folder + '/' + self.url.replace('http://', '').replace('/', '_') + '.txt', 'w')
        f.write(str(self.body))
        f.close()

    def saveEmptyToDatabase(self):
        try:
            db = MySQLdb.connect(host="localhost", user="dan", passwd="", db=DATABASE)
            cursor = db.cursor()
            
            extra = self.extraInfo

            sql = """INSERT INTO urls(url, spam_nonspam, occurances, time_1, time_2, popularity, chain_id) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s)"""

            #print 'Entering URL info into database'
            cursor.execute(sql.replace('\n', ''), (self.url, extra['spam_nonspam'], 
                                 extra['occurances'], extra['time_1'], extra['time_2'], 
                                 self.popularity, self.chainID))
            db.commit()
        except MySQLdb.Error, e:
            print "%s" %e
            db.rollback()
            print 'Save empty to database FAILED'
        db.close()


    def saveToDatabase(self):
        try:
            db = MySQLdb.connect(host="localhost", user="dan", passwd="", db=DATABASE)
            cursor = db.cursor()

            extra = self.extraInfo
            url = self.url
            Trustworthiness = self.ratings['Trustworthiness'][0]
            Trust_confidence = self.ratings['Trustworthiness'][1]
            Vendor_Reliability = self.ratings['Vendor reliability'][0]
            Vendor_confidence = self.ratings['Vendor reliability'][1]
            Privacy = self.ratings['Privacy'][0]
            Privacy_confidence = self.ratings['Privacy'][1] 
            Child_safety = self.ratings['Child safety'][0]
            Child_confidence = self.ratings['Child safety'][1] 
            stats = self.commentStats

            urlID = None
            sql = """INSERT INTO urls(url, Trustworthiness, Trust_confidence, Vendor_Reliability, 
                     Vendor_confidence, Privacy, Privacy_confidence,
	         		 Child_safety, Child_confidence, spam_nonspam, occurances, time_1, time_2, 
                     popularity, good_site, useful_informative, entertaining, good_cus_exper,
                     child_friendly, spam, annoying_ads, bad_exper, phishing, 
                     malicious_viruses, bro_exploit, spyware, adult_content, 
                     hateful, eth_issues, useless, other, chain_id)
	         		 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                             %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                             %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

            #print 'Entering URL info into database'
            cursor.execute(sql.replace('\n', ''), (url, Trustworthiness, Trust_confidence, 
                                 Vendor_Reliability, Vendor_confidence, Privacy, Privacy_confidence, 
                                 Child_safety, Child_confidence, extra['spam_nonspam'], 
                                 extra['occurances'], extra['time_1'], extra['time_2'], self.popularity,
                                 stats['Good site'], stats['Useful, informative'], stats['Entertaining'],
                                 stats['Good customer experience'], stats['Child friendly'], stats['Spam'], 
                                 stats['Annoying ads or popups'], stats['Bad cusotmer experience'], 
                                 stats['Phishing or other scams'], stats['Malicious content, viruses'], 
                                 stats['Browser exploit'], stats['Spyware or adware'], 
                                 stats['Adult content'], stats['Hateful or questionable content'], 
                                 stats['Ethical issues'], stats['Useless'], stats['Other'], self.chainID))
            db.commit()
            urlID = cursor.lastrowid
        except MySQLdb.Error, e:
            print "%s" %e
            db.rollback()
            print "\nInserting URL info Failed\n"

        if not urlID is None and self.shouldGetComments:
            # comments
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

    def getThirdPartyInfo(self):
        notDone = True        
        #print "getThirdPartyInfo Not Done"

    def getComments(self):
        display = Display(visible=None).start()
        lastPage = 1
        paging = self.body.findAll('div', { 'class' : 'paging'})
        if paging:
            lastPage = int(paging[0].findAll('li', { 'class' : 'btn' })[-1]['page'])
            lastPage = min(COMMENT_PAGE_LIMIT, lastPage)
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
            allComments = commentsSection.findAll('div', { 'class' : 'sc-comment' })
            if allComments:
                for c in allComments:
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
#            print self.url
            # Request the html page
            try:
                req = urllib2.Request('http://www.mywot.com/en/scorecard/' + self.url, None, HEADERS)
                self.body = BeautifulSoup(urllib2.urlopen(req).read()).body

                # Extract information
                self.savePageToFile()
                self.getCommentStatistics()
                if self.shouldGetComments:
                    self.getComments()
                self.getThirdPartyInfo()
                self.saveToDatabase()
            except Exception, e:
                print e
        else:
            print 'Not in WOT Database (' + self.url + ')'
            self.saveEmptyToDatabase()
        return self
