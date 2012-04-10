#!/usr/bin/env python
import sys, urllib2, re
from xml.dom.minidom import parseString

if (len(sys.argv) > 1):
    url = sys.argv[1]
    if not re.match('(?=http)\w+', url):
        print "Please provide a valid URL"
    else:
        dom = parseString(urllib2.urlopen('http://api.mywot.com/0.4/public_query2?url=' + url).read())
        applications = dom.getElementsByTagName('application')
        if applications:
            print "WOT ratings for " + url + ' is:\n'
            print 'Category\t\t| Confidence \t| Rating'
            print 'Trustworthiness \t| ' + applications[0].getAttribute('c') + '\t\t| ' + applications[0].getAttribute('r')
            print 'Vendor reliability \t| ' + applications[1].getAttribute('c') + '\t\t| ' + applications[1].getAttribute('r')
            print 'Privacy \t\t| ' + applications[2].getAttribute('c') + '\t\t| ' + applications[2].getAttribute('r')
            print 'Child safety \t\t| ' + applications[3].getAttribute('c') + '\t\t| ' + applications[3].getAttribute('r')
        else:
            print "URL was not found on WOT"
