#!/usr/bin/python
# getCalls.py
#     Opens the T-Mobile Recent Usage webpage and obtains
#     the calls placed in the current billing cycle.

from HTMLParser import HTMLParser
import urllib2

class parseHTML(HTMLParser):
    def __init__(self, html):
        HTMLParser.__init__(self)
        self.td = 0
        self.calls = ""
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        if tag == "td" and attrs:
            if attrs[0][1] == "mula_startOnDate" or \
               attrs[0][1] == "mula_callDestination" or \
               attrs[0][1] == "mula_startOnHour" or \
               attrs[0][1] == "mula_billPresentation1" or \
               attrs[0][1] == "mula_messages":
                self.td = 1
        else:
            self.td = 0
    
    def handle_endtag(self, tag):
        if tag == "td":
            self.td = 0
    
    def handle_data(self, data):
        if self.td == 1:
            try:
                int(data)
                self.calls = "%s%s\n" % (self.calls, data)
            except ValueError:
                self.calls = "%s%s\t" % (self.calls, data.rstrip())
    
    def read(self):
        return str(self.calls)

def getUnparsed():
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())

    # Login to My T-Mobile
    loginURL, loginQueryString = loginParams()
    login = opener.open(loginURL, loginQueryString)
    
    # This program needs this page to properly open the call records
    billing = opener.open("https://my.t-mobile.com/Billing/")
    currentUsage = opener.open("https://ebill.t-mobile.com/myTMobile/onMinutesUsedLinkClick.do")
    
    # Get the first page of call records
    pg1 = opener.open("https://ebill.t-mobile.com/myTMobile/onMinutesUsedLinkClick.do")
    htmlOriginal = pg1.read()
    start = htmlOriginal.index("<!-- Call Detail Rows Start -->")
    end = htmlOriginal.index("<!-- Bill Details Legends: Start -->")
    html = htmlOriginal[start:end]
    
    # Get the rest of the pages
    for n in range(2, html.count("currentPageIndex") + 2):
        pgURL = "https://ebill.t-mobile.com/myTMobile/onPagination.do?" \
                "currentPageIndex="
        pg = opener.open("%s%s" % (pgURL, n))
        htmlOriginal = pg.read()
        start = htmlOriginal.index("<!-- Call Detail Rows Start -->")
        end = htmlOriginal.index("<!-- Bill Details Legends: Start -->")
        html = "%s%s" % (html, htmlOriginal[start:end])
        pg.close()
    
    # Close all connections
    login.close()
    pg1.close()
    return html

def loginParams():
    url = "https://my.t-mobile.com/Login/LoginController.aspx"
    phone = ""
    password = ""
    queryString = "__EVENTTARGET=&__EVENTARGUMENT=&txtMSISDN=%s" \
                  "&txtPassword=%s&txtPasswordText=+password" % \
                  (phone, password)
    return url, queryString

def overwriteFile(data):
    statement = open("statement.txt", "w")
    statement.write(data)
    statement.close()

def main():
    html = getUnparsed()
    calls = parseHTML(html)
    
    # Write call records to statement file
    overwriteFile(calls.read())
    

if __name__ == "__main__":
    main()