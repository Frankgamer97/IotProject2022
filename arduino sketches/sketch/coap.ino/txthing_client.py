import sys
from twisted.internet.defer import Deferred
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from twisted.python import log

import txthings.coap as coap
import txthings.resource as resource

from ipaddress import ip_address

class Agent():

    def __init__(self, protocol):
        self.protocol = protocol
        reactor.callLater(1, self.requestResource)
    
    def requestResource(self):
        request = coap.Message(code=coap.GET)
        request.opt.uri_path = (b"hello", )
        request.opt.obeserve = 0
        request.remote = (ip_address("192.168.1.30"), coap.COAP_PORT)
        d = self.protocol.request(request, observeCallback=self.printLaterResponse)
        # d = protocol.request(request)
        d.addCallback(self.printResponse)
        d.addErrback(self.noResponse)

    def printResponse(self, response):
        print("Result:")
        print(response.payload)

    def printLaterResponse(self, response):
        print("Observable results: ")
        print(response.payload)
    def noResponse(self, failure):
        print("failed to fetch resource")
        print(failure)

log.startLogging(sys.stdout)
endpoint = resource.Endpoint(None)
protocol = coap.Coap(endpoint)

client = Agent(protocol)
reactor.listenUDP(6166, protocol)
reactor.run()