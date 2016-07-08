#!/usr/bin/env python3.5
import socketserver
import socket
import re
import lujvo
import vlasisapi as vl
import traceback

lujvo.debug = True
favi, star = None, None
with open("favi.png", "rb") as df:
    favi = df.read()
with open("start.png", "rb") as df:
    star = df.read()
picheader = b"""HTTP/1.1 200 OK
Content-Type: image/png

"""

def pd(p, d):
    if d is None:
        return ""
    return "<dh>{}</dh><dd>{}</dd>".format(p,d)

def hd(t):
    return "<h3 id=\"def\">{0}</h3>".format(t)

class Vlasis(socketserver.BaseRequestHandler):

    def append(self, af="<p> ... enter your request</p>"):
        return bytes("""HTTP/1.1 418 OK
        Content-Type: text/html; utf8
        Connection: close

        <html>
        <head>
        <title>mibvlasisku</title>
        <meta http-equiv="Content-type" content="text/html; charset=utf-8">
        <meta name="viewport" content="user-scalable=no, width=device-width, initial-scale=1">
        <link rel="shortcut icon" type="image/png" href="/favi.png"/>
        <link rel="apple-touch-icon" href="/favi.png">
        <link rel="apple-touch-startup-image" href="/start.png"/>
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="black">
        <style>
        body {
            padding: 0;
            margin: 0;
            max-width: 700px;
            margin: auto auto;
        }
        form {
            padding: 1px 5px;
            margin: 0;
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
            padding: 7px 10px;
            margin: 0;
        }
        input[type="text"] {
            font-size: 200%;
        }
        h3 {
            padding: 0;
            margin: 0;
        }
        a {
            color: #d72121;
            text-decoration: none;
        }
        </style>
        </head>
        <body>
        <form method="GET" action="/">
        <input type="text" name="r" placeholder="input"></input><br>
        <input type="submit" style="display:none;"></input>
        </form>
        <div id="response">
        """+af+"""
        </div>
        <script>
            var a=document.getElementsByTagName("a");
            for(var i=0;i<a.length;i++)
            {
                a[i].onclick=function()
                {
                    window.location=this.getAttribute("href");
                    return false
                }
            }
        </script>
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
        answ = "<dl>"
        note = ""
        callFunc = self.callFunc
        try:
            vlasis = vl.get(req)
            last = None
            if type(vlasis.finding) == list:
                last = "({})".format(len(vlasis.finding))
                vlasis = vl.get(vlasis.finding[0])
                if vlasis.finding != None:
                    vlasis.finding = vlasis.finding.replace("\\", "")

            if req != vlasis.finding:
                if vlasis.finding is None:
                    answ = hd("Could not find: \"{}\"".format(req)) + answ
                    raise ValueError("Could not find "+req)
                else:
                    answ = hd("{} -> {} {}".format(req, vlasis.finding, "" if last is None else last)) + answ
            else:
                answ = hd(req) + answ
            vlasis.definition = vlasis.definition.replace("\\n", "<br>").replace("\\","")
            vlasis.type = vlasis.type.replace("\\", "")
            answ += pd("Definition ({})".format(vlasis.finding), vlasis.definition)
            r = vlasis.getrafsi()
            if r != "":
                answ += pd("Rafsi", r.replace("\\", ""))
            answ += pd("Type ({})".format(vlasis.finding), vlasis.type)
            note = pd("Notes ({})".format(vlasis.finding), vlasis.notes)
        except Exception as e:
            print(e)
        if " " not in req:
            try:
                split = ["<a href=\"/?r={0}\">{0}</a>".format(r) for r in lujvo.splitLujvo(req)]
                if not (len(split) == 1 and split[0] == req):
                    answ += pd("Split into Rafsi", " - ".join(split))
            except:
                pass
            answ += callFunc("Word Score ({})".format(req), lujvo.score, req)
            answ += callFunc("C-V Form ({})".format(req), lujvo.rafsiForm, req)
            if req != vlasis.finding:
                answ += callFunc("Word Score ({})".format(vlasis.finding), lujvo.score, vlasis.finding)
                answ += callFunc("C-V Form ({})".format(vlasis.finding), lujvo.rafsiForm, vlasis.finding)
        else:
            lujv = lujvo.bestLujvo(req.split(" "))
            if lujv and lujv != "":
                answ += pd("Concatenated Lujvo", "<a href=\"/?r={0}\">{0}</a>: {1}".format(*(lujv[0])))
                answ += pd("Other valid Lujvo", "<br>".join(["{}: {}".format(a,b) for (a,b) in lujv]))
                answ = re.sub("-> .*?<\/h", "-> {}</h".format(lujv[0][0]), answ)
        see_also = ""
        try:
            sare = "See also (.*?)\."
            see_also = re.search(sare, note)
            if see_also is not None and see_also.groups():
                note = re.sub(sare, "", note)
                note += "See also:"
                for wrd in see_also.group(1).split(", "):
                    note += " <a href=\"/?r={0}\">{0}</a>".format(wrd)
        except:
            pass
        answ += "<p>" + note.replace("\\n","</p><p>").replace("\\","") + "</p>"
        answ += "</dl>"
        return answ

    def handle(self):
        global c
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        try:
            req = re.search("GET \/\?r=(.*) HTTP\/1\.1", str(self.data,"utf8"), re.DOTALL)
            answ = "made by /u/mtib"
            if req is not None and len(req.groups()) == 1:
                req = req.group(1)
                req = req.replace("%27", "'").replace("+", " ")
                print(req)
                answ = self.lookup(req)
            res = re.search("GET \/(.*)\.png HTTP", str(self.data,"utf8"))
            if res is not None and len(res.groups()) == 1:
                res = res.group(1)
                if res == "start":
                    self.request.sendall(picheader + star)
                    return
                elif res == "favi":
                    self.request.sendall(picheader + favi)
                    return
                else:
                    answ = "that resource does not exist"

        except Exception:
            answ = "An error occurred:<br>{}".format(traceback.format_exc())


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
