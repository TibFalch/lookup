#!/usr/bin/env python3.5
import socketserver
import socket
import re
import lujvo
import vlasisapi as vl

lujvo.debug = True

def pd(p, d):
    return "<dh>{}</dh><dd>{}</dd>".format(p,d)

def hd(t):
    return "<h3 id=\"{0}\">{0}</h3>".format(t)

class Vlasis(socketserver.BaseRequestHandler):

    def append(self, af="<p> ... enter your request</p>"):
        return bytes("""HTTP/1.1 418 OK
        Content-Type: text/html; utf8
        Connection: close

        <html>
        <head>
        <title>mibvlasisku</title>
        <style>
        body {
            padding: 0;
            margin: 0;
            max-width: 700px;
            margin: auto auto;
        }
        form {
            padding: 5px;
        }
        form * {
            width: 100%;
        }
        dh {
            font-weight: bold;
        }
        dd {
            padding-bottom: 1em;
        }
        #response {
            padding: 10px;
        }
        </style>
        </head>
        <body>
        <form method="GET" action="/">
        <input type="text" name="r" placeholder="input"></input><br>
        <input type="submit"></input>
        </form>
        <div id="response">
        """+af+"""
        </div>
        </body>
        </html>""", "utf8")

    def callFunc(self, head, func, para, unpack=None, re=False):
        try:
            if unpack is None:
                if re:
                    return func(para)
                return pd(head, func(para))
            else:
                if re:
                    return func(para)[unpack]
                return pd(head, func(para)[unpack])
        except:
            return ""

    def lookup(self, req):
        answ = hd(req)
        answ += "<dl>"
        note = ""
        callFunc = self.callFunc
        try:
            vlasis = vl.get(req)
            r = vlasis.getrafsi()
            if r != "":
                answ += pd("Rafsi", r.replace("\\", ""))
            answ += pd("Definition ({})".format(vlasis.finding), vlasis.definition)
            answ += pd("Type ({})".format(vlasis.finding), vlasis.type)
            note = pd("Notes ({})".format(vlasis.finding), vlasis.notes)
        except Exception as e:
            print(e)
            raise e # DEBUG
        if " " not in req:
            answ += callFunc("split lujvo", lujvo.splitLujvo,req)
            answ += callFunc("score", lujvo.score,req)
            answ += callFunc("form", lujvo.rafsiForm, req)
        else:
            luj = callFunc("create lujvo", lujvo.bestLujvo,req.split(" "), re=True)
            if luj != "":
                answ += pd("create lujvo", "{}: {}".format(*(luj[0])))
                answ += pd("possible lujvo", "<br>".join(["{}: {}".format(a,b) for (a,b) in luj]))
        answ += note.replace("\\n","<br>")
        answ += "</dl>"
        return answ

    def handle(self):
        global c
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()

        req = re.search("GET \/\?r=(.*) HTTP\/1\.1", str(self.data,"utf8"), re.DOTALL)
        answ = "... enter your request ..."
        if req is not None and len(req.groups()) == 1:
            req = req.group(1)
            req = req.replace("%27", "'").replace("+", " ")
            print(req)
            answ = self.lookup(req)


        self.request.sendall(self.append(answ))

if __name__ == "__main__":
    start = 8000
    server = None
    while True:
        try:
            server = socketserver.TCPServer(("", start), Vlasis)
            break
        except OSError:
            start += 1
    print("serving on", start)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
        print("\nbye")
