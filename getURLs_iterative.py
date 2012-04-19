#!/usr/bin/env python

import sys
from PyQt4.QtGui import *  
from PyQt4.QtCore import *  
from PyQt4.QtWebKit import *  
  
class Render(QWebPage):  
  def __init__(self, url):
    self.app = QApplication(sys.argv)
    QWebPage.__init__(self)  
    self.loadFinished.connect(self._loadFinished)  
    self.mainFrame().load(QUrl(url))  
    self.app.exec_()  
  
  def _loadFinished(self, result):  
    self.frame = self.mainFrame()
    self.app.quit()  

# Both of these cause segfaults...
#urls = ['http://www.mywot.com/en/scorecard/www.blogspot.com#page-1', 'http://www.mywot.com/en/scorecard/www.blogspot.com#page-2', 'http://www.mywot.com/en/scorecard/www.blogspot.com#page-3']
urls = ['http://www.mywot.com/en/scorecard/www.blogspot.com#page-1', 'http://www.mywot.com/en/scorecard/www.blogspot.com#page-2']

for url in urls:
    r = Render(url)
    html = r.frame.toHtml()
    unicoded = str(html.toUtf8()).decode("utf-8")
    finalHTML = eval(repr(unicoded)[1:])
    print url
#    print finalHTML

