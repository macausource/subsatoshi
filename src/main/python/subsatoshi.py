#!/usr/bin/python

import re
import cgi
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from subprocess import call
from time import localtime, strftime

import os

import urllib
import urllib2
import json
import base64
import properties

from urlparse import urlparse, parse_qs

import vdp

def outPay(recipientAddr, amount):

    toAddr=recipientAddr;
    paras="password="+properties.main_password+"&to="+toAddr+"&amount="+amount;
    url="https://blockchain.info/merchant/"+properties.guid+"/payment?"+paras;
    print url
    response=urllib2.urlopen(url);
    data=json.load(response);
    return data;

def outPayMulti(recipients):
    quotedrecipients = str(recipients).replace('\'','"')
    quotedrecipients = urllib.quote_plus(quotedrecipients)
    note = urllib.quote_plus("subsatoshi.org")

    paras="password="+properties.main_password+"&recipients="+quotedrecipients+"&note="+note;
    url="https://blockchain.info/merchant/"+properties.guid+"/sendmany?"+paras;
    print url
    response=urllib2.urlopen(url);
    data=json.load(response);
    return data;

def processPayment(amount):
    # must deduct mining fee
    amount = amount - 10000
    recipients = vdp.getRecipients(amount, properties.vdp_url)

    print recipients

    return outPayMulti(recipients)


class MyHandler(BaseHTTPRequestHandler):

    def getTimestamp(self):
        return strftime("%Y%m%d%H%M%S", localtime())


    def do_GET(self):

        if self.path == '/' :
            self.send_response(200)
            self.send_header('Content-type','text/plain')
            self.end_headers()
            self.wfile.write(('subsatoshi blockchain service - status: OK'))
            return

        if self.path.startswith('/test'):
            self.send_response(200)
            self.send_header('Content-type','text/plain')
            self.end_headers()

            self.wfile.write(('incoming test. thank you!'))
            return


        if self.path.startswith('/notification'):
            self.send_response(200)
            self.send_header('Content-type','text/plain')
            self.end_headers()

            print 'incoming ...'
            query_components=parse_qs(urlparse(self.path).query)

            transaction_hash=query_components['transaction_hash'];
            value_in_btc=int(query_components['value'][0]);

            if value_in_btc < 0:
                print "outgoing payment of" + str(value_in_btc)
                self.wfile.write(('*ok*'))
                return

            print "get income: "+str(value_in_btc);
            address=query_components['address'][0];
            confirmations=int(query_components['confirmations'][0]);

            print "confirmations [" + str(confirmations) + "]";

            if confirmations >= 1:
                self.wfile.write(('*ok*'))
                processPayment(value_in_btc)
            else:
			    self.wfile.write(('confirm'))

            return

        if self.path.startswith('/outgoing'):
            self.send_response(200)
            self.send_header('Content-type','text/plain')
            self.end_headers()

            query_components=parse_qs(urlparse(self.path).query)
            recipient=query_components['recipient'][0];
            payment=query_components['payment'][0];
            response=outPay(recipient, payment);

            print response

            self.wfile.write(('outgoing payment done. thank you!'))
            return

def main():

    try:
        print 'started subsatoshi blockchain service'
        print 'using VDP: ' + properties.vdp_url
        server = HTTPServer(('', 8081), MyHandler)
        print 'started httpserver...'
        server.serve_forever()
    except KeyboardInterrupt:
        print '^C received, shutting down server'
        server.socket.close()

if __name__ == '__main__':
    main()
