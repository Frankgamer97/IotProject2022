from twisted.python import log
import txthings.resource as resource
import txthings.coap as coap
from twisted.internet import reactor, defer, protocol
import sys

class Hello(resource.CoAPResource):

    def __init__(self):
        super().__init__()
        self.visibile = True
    async def render_get(self, request):

        response = coap.Message(code=coap.CONTENT, payload="HELLO THERE!")
        return defer.succeed(response)

def main():
    log.startLogging(sys.stdout)
    root = resource.CoAPResource()
    root.putChild(b"hello", Hello())
    endpoint = resource.Endpoint(root)
    reactor.listenUDP(coap.COAP_PORT, coap.Coap(endpoint))
    reactor.run()

if __name__ == '__main__':
    main()