
import os
import socket
import re
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse


sockAddr = "/root/app/proxy.sock"  # Default path

# ----------------- #

routing = {}
routing["GET"] = {}
routing["POST"] = {}
routing["PUT"] = {}
routing["DELETE"] = {}

#-------------------#


def routerGET(path, func):
    global routing
    routing["GET"][path] = func

#---------#


def routerPOST(path, func):
    global routing
    routing["POST"][path] = func

#---------#


def routerPUT(path, func):
    global routing
    routing["PUT"][path] = func

#---------#


def routerDELETE(path, func):
    global routing
    routing["DELETE"][path] = func


#---------#

#-------------------#

class HTTPHandler(BaseHTTPRequestHandler):
    # protocol_version = "HTTP/1.1"
    #---------------#
    def callAPI(self, method="GET", body=""):
        inPath = urlparse(self.path).path
        routPath = ""
        # print( body)
        for key in routing.get(method):
            if re.match(r"^" + key + "$", inPath):
                routPath = key
                break
        try:
            resCode, resBody, resHeaders = routing.get(method).get(routPath)(self.path,
                                                                             body)
        except Exception as e:
            print("Error: ", e)
            resCode = 404
            resBody = b"Not found"
            resHeaders = []

        self.send(resCode, resBody, resHeaders)

    #---------------#

    def do_GET(self):
        self.callAPI()

    #---------------#

    def do_POST(self):
        size = int(self.headers.get('Content-length', 0))
        body = self.rfile.read(size)
        # fields = urlparse.parse_qs(body)

        self.callAPI("POST", body)

    #---------------#

    def do_PUT(self):
        size = int(self.headers.get('Content-length', 0))
        body = self.rfile.read(size)
        # fields = urlparse.parse_qs(body)

        self.callAPI("PUT", body)

    #---------------#

    def do_DELETE(self):
        size = int(self.headers.get('Content-length', 0))
        body = self.rfile.read(size)

        self.callAPI("DELETE", body)

    #---------------#

    def send(self, code, reply, resHeaders):
        self.client_address = (
            '', )  # avoid exception in BaseHTTPServer.py log_message()
        self.send_response(code)

        # We may need more fixes here, this kind of header is just for content-type
        if len(resHeaders) > 0:
            for h in resHeaders:
                self.send_header('Content-type', h)

        # self.send_header('Content-type','text/html')
        self.end_headers()
        self.wfile.write(reply)


#----------------------#


def start():
    # Make sure the socket does not already exist
    try:
        os.unlink(sockAddr)
    except OSError:
        if os.path.exists(sockAddr):
            raise

    unixSock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

    print('Binding on %s' % sockAddr)
    unixSock.bind(sockAddr)

    # Listen for incoming connections
    unixSock.listen(5)

    server = HTTPServer(sockAddr, HTTPHandler, False)
    # ThreadingHTTPServer
    server.socket = unixSock
    server.serve_forever()

    unixSock.shutdown(socket.SHUT_RDWR)
    unixSock.close()
    os.remove(sockAddr)
