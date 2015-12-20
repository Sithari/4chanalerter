from BeautifulSoup import BeautifulSoup
import urllib2 #for wget
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import os
import getpass
from fake_useragent import UserAgent
from time import sleep
from sys import exit

def getThreadIds(ua):

    global debug
    ids = list()
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', ua)]
    response = opener.open('https://boards.4chan.org/b/')

    #print("Response:" + response.read())

    soup = BeautifulSoup(response)
    prettyHTML=soup.prettify()  #prettify the html
    soup2 = BeautifulSoup(prettyHTML)

    try:
       #print soup2.findAll('div', attrs={'class': 'thread'})['id']
        for div in soup2.findAll("div", attrs={'class': 'thread'}):
            ids.append(div['id'])
    except IOError:
        print 'IO error'
    return ids

def getThreadContent(threadid, input_strings, ua):

    global htmlbody
    global count
    titleIsSet = 0

    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', ua)]
    response = opener.open('https://boards.4chan.org/b/thread/' + threadid)

    soup = BeautifulSoup(response)
    prettyHTML=soup.prettify()  #prettify the html

    for item in prettyHTML.split("\n"):
        for string in input_strings:
            if string in item.decode('utf-8'):
                current_date = datetime.now().strftime("%m-%d-%Y")
                if not os.path.exists(current_date):
                    os.makedirs(current_date)
                archiver = open(current_date + "/" + threadid + " - " + datetime.now().strftime("%H-%M-%S") + ".html", 'w+') #save the page to file since it found a match http://www.cyberciti.biz/faq/howto-get-current-date-time-in-python/
                archiver.write(prettyHTML)
                archiver.close()

                count+=1
                print("match on: " + item.decode('utf-8'))

                if titleIsSet is 0:
                    htmlbody += "<h2>Matches found on thread <a href=\"https://boards.4chan.org/b/thread/" + threadid + "\">" + threadid + "</a>:</h2>"
                    titleIsSet=1
                htmlbody += "\n<p>For string <b>" + string + "</b>:<br>"
                try:
                    htmlbody += "The line is: " + item.encode('utf-8') + "<br>"
                except UnicodeDecodeError:
                    htmlbody += "The line is: " + item.decode('utf-8') + "<br>"


def sendMail(from_address, from_address_pswd, to_address, now):

    global htmlbody

    FROM = from_address
    PWD = from_address_pswd
    TO = to_address

    SUBJECT = "4Chan string match alert (" + now + ")"

    msg = MIMEMultipart('alternative')
    msg['Subject'] = SUBJECT
    msg['From'] = FROM
    msg['To'] = TO

    # Prepare actual message

    part2 = MIMEText(htmlbody, 'html')
    # Attach parts into message container.
    msg.attach(part2)
    # Send the mail
    smtpserver = smtplib.SMTP("smtp.gmail.com",587)
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.ehlo
    try:
        smtpserver.login(FROM, PWD)
    except smtplib.SMTPAuthenticationError:
        print ("Pswd was wrong for the FROM gmail account. Exiting..")
        exit(0)
    #print (htmlbody)
    smtpserver.sendmail(FROM, TO, msg.as_string())
    smtpserver.quit()




#main

debug = False

#ask user for which strings to monitor
input = raw_input('Enter strings you would like to monitor: ')
input_strings = input.split(",")

to_email = raw_input('Enter the destination email address: ')

from_email = raw_input('Enter from address(use a dummy account): ')

from_emailpw = getpass.getpass('Enter the from address pw: ')

ua = UserAgent()


while True:
    count = 0
    random_ua = ua.random  # new UA every 10 minutes
    if(debug):
        print("Current UA: " + random_ua)

    now = datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')
    print ("Running at time %s" % now)

    htmlbody = """\
                <html>
                <head></head>
                <body>
                """

    threadids = getThreadIds(random_ua)  # Get the thread IDs on 4chan/b

    for threadid in threadids:
        if (debug):
            print ("Current id is: " + threadid[1:])
        getThreadContent(threadid[1:], input_strings, random_ua)  # add content to htmlbody

    htmlbody += """\
                </p>
                </body>
                </html>
                """

    if (debug):
        print ("html body " + htmlbody)
    if count is 0:
        print("No matches found. No email being sent")
    else:
        print("Found " + str(count) + " matches")
        sendMail(from_email, from_emailpw, to_email, now) #send the report via email

    print("Sleeping for 10 minutes")
    sleep(600) # delays for 10 minutes
