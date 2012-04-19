#!/usr/bin/env python
import sys, thread # kudos to Nicholas Herriot (see comments)
import gtk
import webkit
import warnings
from time import sleep
from optparse import OptionParser

warnings.filterwarnings('ignore')

class WebView(webkit.WebView):
    def get_html(self):
        self.execute_script('oldtitle=document.title;document.title=document.documentElement.innerHTML;')
        html = self.get_main_frame().get_title()
        self.execute_script('document.title=oldtitle;')
        return html
 
class Crawler(gtk.Window):
    def __init__(self, url):
        gtk.gdk.threads_init() # suggested by Nicholas Herriot for Ubuntu Koala
        gtk.Window.__init__(self)
        self._url = url
        self._file = 'temp/temp-' + url.split('-')[-1] + '.html'
        self._html = ''
 
    def crawl(self):
        view = WebView()
        view.open(self._url)
        view.connect('load-finished', self._finished_loading)
        self.add(view)
        gtk.main()
    
    def _finished_loading(self, view, frame):
        self.html = view.get_html()
#        with open(self._file, 'w') as f:
#            f.write(view.get_html())
        gtk.main_quit()
#        return self.html

def main(url):
    crawler = Crawler(url)
    crawler.crawl()
    return self.html
 
if __name__ == '__main__':
    main(url)
