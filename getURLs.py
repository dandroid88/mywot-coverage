#!/usr/bin/env python
import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
from bs4 import BeautifulSoup
import codecs

class Render(QWebPage):  
  def __init__(self, urls):  
    self.app = QApplication(sys.argv)  
    QWebPage.__init__(self)  
    self.loadFinished.connect(self._loadFinished)  
    self.urls = urls  
    self.data = {} # store downloaded HTML in a dict  
    self.crawl()  
    self.app.exec_()  
      
  def crawl(self):  
    if self.urls:  
      url = self.urls.pop(0)  
      print 'Downloading', url  
      self.mainFrame().load(QUrl(url))
    else:
      self.app.quit()  
        
  def _loadFinished(self, result):
    frame = self.mainFrame()  
    url = str(frame.url().toString())
    print 'Finished' + url + '\n'
    html = frame.toHtml()
    unicoded = str(html.toUtf8()).decode("utf-8")
    self.data[url] = eval(repr(unicoded)[1:])  
    self.crawl()  

def main(urls):
    return Render(urls).data

if __name__ == '__main__':
    main(urls)
