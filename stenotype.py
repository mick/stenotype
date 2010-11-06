ACCOUNT_SID = 'XXX'
AUTH_TOKEN = 'XXX'
CALLER_ID = '555-555-5555'



from twisted.web.resource import Resource
from twisted.web.server import NOT_DONE_YET

import txilio
from twisted.python import log
from twisted.web import resource
from twisted.words.xish import domish, xpath
from wokkel.subprotocols import XMPPHandler
from wokkel.xmppim import AvailablePresence, Presence
from xml.dom.minidom import parse, parseString

import simplejson as json


NS_MUC = 'http://jabber.org/protocol/muc'
NS_XHTML_IM = 'http://jabber.org/protocols/xhtml-im'
NS_XHTML_W3C = 'http://www.w3.org/1999/xhtml'

class StenoBot(XMPPHandler):
    messageTypes = ["chat", "groupchat"]
    number = ""
    def __init__(self, room, nick):
        XMPPHandler.__init__(self)

        self.room = room
        self.nick = nick

    def connectionMade(self):
        self.send(AvailablePresence())

        # add handlers

        # join room
        pres = Presence()
        pres['to'] = self.room + '/' + self.nick
        pres.addElement((NS_MUC, 'x'))
        self.send(pres)


    def connectionInitialized(self):
            self.xmlstream.addObserver("/message[@type='groupchat']", self._onMessage)
#            self.xmlstream.addObserver("/message/x[@xmlns!='jabber:x:delay']", self._onMessage)

    def _onMessage(self, message):
        if message.handled:
            return

        messageType = message.getAttribute("type")

        if messageType == 'error':
            return

        if messageType not in self.messageTypes:
            message["type"] = 'normal'

        self.onMessage(message)

    def onMessage(self, msg):
        """
        Called when a message stanza was received.
        """

        if xpath.matches("/message/x[@xmlns='jabber:x:delay']", msg) == 1:
            print "skip"
            return
        print "process"
#        if msg.x and msg.x.uri == "jabber:x:delay":
#            print "DELAYED "+str(msg.x) + msg.x.ur
#        if msg.x and msg.x.hasAttribute("xmlns") and msg.x['xmlns'] == "jabber:x:delay":
#            return

        if msg["type"] == 'groupchat' and hasattr(msg, "body"):
            print (msg.body)
            content = str(msg.body)
            if(content[:5].lower() == "call "):
                number = content[5:]
                print "GOT A NUMBER!! "+ number
#                if number  != self.number:
#                    self.number = number
                data = {
                    'Caller' : CALLER_ID,
                    'Called' : number,
                    'Url' : 'http://dmt.im/twilio/twilio.xml',
                    #            'SendDigits' : '965376#1'
                    }

                account = txilio.Account(ACCOUNT_SID, AUTH_TOKEN)
                d = account.request('Calls', 'POST', data)
                self.notify("CALLING "+number)
                def _done(res):
                    print str(res)
                    request.write(str(res))
                    request.finish()

                d.addBoth(_done)
                return NOT_DONE_YET

    def notify(self, data):
        # build the messages
        text = []
        html = []
        link = r"<a href='%s' name='%s'>%s</a>"

        text.append(data)

        msg = domish.Element((None, 'message'))
        msg['to'] = self.room
        msg['type'] = 'groupchat'
        msg.addElement('body', content=''.join(text))
        wrap = msg.addElement((NS_XHTML_IM, 'html'))
        body = wrap.addElement((NS_XHTML_W3C, 'body'))
        body.addRawXml(''.join(html))

        self.send(msg)


class StenotypeResource(Resource):
    isLeaf = True

    def __init__(self, bot):
        resource.Resource.__init__(self)
        self.bot = bot

    def render_GET(self, request):
        print 'got a get'
        #start up the listener?
        #
        data = {
            'Caller' : CALLER_ID,
            'Called' : '505-920-6781',
            'Url' : 'http://dmt.im/twilio/twilio.xml',
#            'SendDigits' : '965376#1'
        }

        account = txilio.Account(ACCOUNT_SID, AUTH_TOKEN)
        d = account.request('Calls', 'POST', data)

        def _done(res):
            print str(res)
            request.write(str(res))
            request.finish()

        d.addBoth(_done)
        return NOT_DONE_YET


    def getText(nodelist):
        rc = []
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc.append(node.data)
        return ''.join(rc)

    def render_POST(self, req):
        #data = req.content.readlines()
        self.bot.notify(req.args['TranscriptionText'][0])

        return '<?xml version="1.0" encoding="UTF-8"?><Response><Record transcribe="true" transcribeCallback="http://dmt.im:1234/" playBeep="false" maxLength="20" timeout="30" /> </Response>'

