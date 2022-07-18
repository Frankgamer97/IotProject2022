from coapthon.server.coap import CoAP
from coapthon.resources.resource import Resource

class HelloResource(Resource):

    def __init__(self, name="HelloResource", coap_server=None):
        super(HelloResource, self).__init__(name, coap_server, visible=True,
                                            observable=True, allow_children=True)
        self.payload = "Hello"
        self.content_type = "text/plain"

    def render_GET(self, request):
        return self

    def render_PUT(self, request):
        print()
        print(request.payload)
        print()
        self.payload = request.payload
        return self

class CoAPServer(CoAP):
    def __init__(self, host, port, multicast=False):
        CoAP.__init__(self, (host, port), multicast)
        self.add_resource('hello/', HelloResource())

        print("CoAP Server start on " + host + ":" + str(port))
        print(self.root.dump())

def main():
    ip = "0.0.0.0"
    port = 5683
    multicast = True

    server = CoAPServer(ip, port, multicast)
    try:
        server.listen(10)
    except KeyboardInterrupt:
        print("Server Shutdown")
        server.close()
        print("Exiting...")


if __name__ == '__main__':
    main()