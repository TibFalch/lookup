#!/usr/bin/usr python3.5
import socketserver

import time

c = 0
s = time.time()

class Vlasis(socketserver.BaseRequestHandler):

    def handle(self):
        global c
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        dat = b"""HTTP/1.1 418 OK
Content-Type: text/html; utf8
Connection: close
Refresh: 1

<html><h1>Hello</h1><p>"""+bytes(time.ctime() + " Bytes: " + str(c) + "<br>B/S: " + str(round(float(c)/(time.time()-s),2)),"utf8")+b"""</p></html>"""
        c += len(self.data) + len(dat)
        # just send back the same data, but upper-cased
        self.request.sendall(dat)

if __name__ == "__main__":
    start = 8000
    server = None
    while True:
        try:
            server = socketserver.TCPServer(("127.0.0.1", start), Vlasis)
            break
        except OSError:
            start += 1
    print("serving on", start)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
        print("\nbye")
