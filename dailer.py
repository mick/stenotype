#!/usr/bin/env python

import twilio
import sys
from xml.dom.minidom import parse, parseString


# Twilio REST API version
API_VERSION = '2008-08-01'

# Twilio AccountSid and AuthToken
ACCOUNT_SID = 'XXXX'
ACCOUNT_TOKEN = 'XXX'

# Outgoing Caller ID previously validated with Twilio
CALLER_ID = '555555555';

CALL_XML = 'http://dmt.im/twilio/twilio.xml'
HANGUP_XML = 'http://dmt.im/twilio/hangup.xml'

# Create a Twilio REST account object using your Twilio account ID and token
account = twilio.Account(ACCOUNT_SID, ACCOUNT_TOKEN)




# ===========================================================================
# 1. Initiate a new outbound call to 415-555-1212
#    uses a HTTP POST
#
#

def connect(phone="5059206781"):

    d = {
        'Caller' : CALLER_ID,
        'Called' : phone,
        'Url' : CALL_XML,
#        'SendDigits' : '965376#1'
        }
    try:
        print account.request('/%s/Accounts/%s/Calls' % \
                                  (API_VERSION, ACCOUNT_SID), 'POST', d)
    except Exception, e:
        print e
        print e.read()


def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)

def hangup():
    calls = ""
    d = {}
    try:
        calls = account.request('/%s/Accounts/%s/Calls?Status=1' % \
                                  (API_VERSION, ACCOUNT_SID), 'GET', d)
    except Exception, e:
        print e

    print calls
    domcalls = parseString(calls)
    for a in domcalls.getElementsByTagName("Sid"):
        print getText(a.childNodes)
        endcall(getText(a.childNodes))

def endcall(sid):
    calls = ""
    d = {'CurrentUrl' : HANGUP_XML}
    try:
        calls = account.request('/%s/Accounts/%s/Calls/%s' % \
                                  (API_VERSION, ACCOUNT_SID, sid), 'POST', d)
    except Exception, e:
        print e


if(len(sys.argv) > 1):
    action = sys.argv[1]
    if(action == "connect"):
        if(len(sys.argv) > 2):
            connect(sys.argv[2])
        else:
            connect()
    elif(action == "hangup"):
        hangup()















