#!/usr/bin/python
# callreminder.py
#       This program checks the T-Mobile website to obtain the most current
#       call records. It then reminds you if you havent called the people
#       in your contacts list enough times.

import urllib2
#import cgitb; cgitb.enable()

def main():
    print "Content-type: text/html\n"

    statement = getCallRecords()
    analyzeRecords(statement)

def getCallRecords():
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())

    # Login to My T-mobile
    loginURL, loginQueryString = loginParams()
    login = opener.open(loginURL, loginQueryString)

    # Get call records
    #   Note: billing and currentUsage needed to open the total usage page
    billing = opener.open("https://my.t-mobile.com/Billing/")
    currentUsage = opener.open("https://ebill.t-mobile.com/myTMobile/onMinutesUsedLinkClick.do")
    totalUsageURL = "https://ebill.t-mobile.com/myTMobile/onMinutesUsedPrintBill.do"
    statementObject = opener.open(totalUsageURL)
    statement = statementObject.read()

    # Close up
    login.close()
    billing.close()
    currentUsage.close()
    statementObject.close()

    return statement

def loginParams():
    url = "https://my.t-mobile.com/Login/LoginController.aspx"
    phone = ""
    password = ""
    queryString = "__EVENTTARGET=&__EVENTARGUMENT=&txtMSISDN=%s" \
                  "&txtPassword=%s&txtPasswordText=+password" % \
                  (phone, password)
    return url, queryString

def analyzeRecords(statement):
    # [ Name, phone number, calls to place on a monthly basis ]
    contacts = [
    ["Amalia", "", 31],
    ["Francisco", "", 4],
    ["Joey", "", 4],
    ["Christian", "", 4],
    ["Eric", "", 4],
    ["Parents", "", 4],
    ["Juan", "", 1],
    ["Eddie", "", 1]
    ]

    # Open log file
    allRecords = open("allRecords.txt", "w")

    message = "<br />"
    for p in contacts:
        name = p[0]
        progress = statement.count(p[1])
        weeklyGoal = p[2]/4
        allRecords.writelines("<br />%s (%d/%d)" % (name, progress, weeklyGoal))
        if progress < weeklyGoal:
            message = "%s%s (%d/%d) <br />" % (message, name, progress, weeklyGoal)
    sendMessage(message)
    allRecords.close()

def sendMessage(m):
    print "<message>"
    print "    <content>%s</content>" % (m)
    print "</message>"

if __name__ == "__main__":
    main()