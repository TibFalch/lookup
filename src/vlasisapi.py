import urllib.request
import re

p_cma = "<h1>(.*?)<span"
p_aff = "-</span>(.*?)<"
p_typ = "<span class=\"type\">(.*?)</span>"
p_des = "<p class=\"definition\">(.*?)</p>"
p_noe = "<p class=\"notes\">(.*?)</p>"
p_ans = "<div id=\"definition\">(.*?)</div>"
p_an1 = "<dt>\s*<a href=\".*?\">(.*?)</a>\s*</dt>"
p_an2 = "<dd>(.*?)</dd>"
mld = re.DOTALL & re.MULTILINE

def furl(search):
    return "http://vlasisku.lojban.org/vlasisku/{}".format(search)

class Vlasisku:
    def uplink(self):
        body = self.download()
        try:
            self.definition = re.sub("<.*?>", "", re.search(p_des, body).group(1))
            self.definition.replace("\\n", "\t")
            self.vlasis(body)
        except:
            self.search_results(body)

    def vlasis(self, body):
        self.finding = cleanCmavo(re.search(p_cma, body, mld).group(1))
        self.type = re.search(p_typ, body).group(1)
        try:
            self.rafsi = re.findall(p_aff, body)[:-1]
        except:
            self.rafsi = []
        try:
            self.notes = re.sub("<.*?>", "", re.search(p_noe, body).group(1))
        except:
            self.notes = "<None>"

    def search_results(self, body):
        intr = re.search(p_ans, body, mld)
        s = intr.group(1)
        self.type = "search"
        self.definition = [re.sub("(<.*?>)", "",x) for x in re.findall(p_an2, s, mld)]
        self.finding = re.findall(p_an1, s)
        self.num = len(self.finding)

    def download(self):
        res = urllib.request.urlopen(furl(self.search))
        if res.code != 200:
            raise ValueError('Could not connect to Vlasisku')
        body = str(res.read())
        res.close()
        return body

    def debug(self):
        if self.type == "search":
            for x in range(self.num):
                print("\n{}:\n{}".format(self.finding[x], self.definition[x]))
        else:
            print(self.finding, end=" | ")
            for x in self.rafsi:
                print(x, end=" ")
            print("|",self.type)
            print(self.definition)

    def getrafsi(self, sep="-", beg="-", end="-"):
        if self.rafsi:
            return sep + sep.join(self.rafsi) + end
        return ""

    def __init__(self, search):
        self.search = search

def get(search):
    v = Vlasisku(search)
    v.uplink()
    return v

def cleanCmavo(text):
    c = re.sub("(<.*? title=\".*?\">|\s|\n|\\n|<.*?>)", "", text)[2:-2]
    return c.replace("\\n", " ").replace(" \\xe2\\x80\\xa6","...")

def cleanDefinition(text):
    return re.sub("<.*?>","",text.replace("\\n", "\t"))

if __name__ == '__main__':
    import sys
    v = Vlasisku(sys.argv[1])
    v.uplink()
    v.debug()
