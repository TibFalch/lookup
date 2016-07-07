#!/usr/bin/env python3.5
import vlasisapi as vl

debug = True
vowels = "aeiou" # not including y
rafsco = {
    "CVCCVf" : 1,
    "CVCC" : 2,
    "CCVCVf" : 3,
    "CCVC" : 4,
    "CVC" : 5,
    "CVV" : 8,
    "CCV" : 7,
}

def pd(*s):
    if debug:
        print(*s)

def isVowel(c):
    return c in vowels or c == "y"

def isConsonant(c):
    return not isVowel(c)

def rafsiForm(rafsi):
    r = ""
    for c in rafsi:
        if c == "'":
            continue
        r += "V" if c in vowels else "C"
    return r

def rafsiScore(rafsi, final=False):
    form = rafsiForm(rafsi)
    if len(form) == 5 and form[4] not in "yrn":
        final = True
    elif len(form) == 5:
        form = form[4]
        pd("reduced form to", form)
    form = form if not final else form + "f"
    sc = rafsco.get(form, None)
    if sc == 8 and "'" in rafsi:
        sc = 6
    return sc

def splitLujvo(lujvo):
    form = rafsiForm(lujvo)
    pd(lujvo, form)
    rafs = []
    i = 0
    o = 0 #offset because '
    li = 0
    while True:
        if i >= len(form):
            break
        if form[i:i+4] in ["CVCC", "CCVC"]:
            if lujvo[i+o+4] in "yn":
                rafs.append(lujvo[i+o:i+o+4])
                if "'" in lujvo[i+o:i+o+4]:
                    o += 1
                i += 5
                continue
            elif i+5+o == len(lujvo):
                rafs.append(lujvo[i+o:i+o+5])
                break
        if form[i:i+3] in rafsco.keys():
            l = 4 if "'" in lujvo[i+o:i+o+4] else 3
            rafs.append(lujvo[i+o:i+o+l])
            if l == 4:
                o += 1
            if i+3 != len(form) and lujvo[i+o+3] in "yrn":
                pi = i+4
                for x in range(2):
                    if form[pi:pi+3+x] in rafsco.keys():
                        pd("Proposed skip useful")
                        i += 1
                        break
            i += 3
        else:
            pd("redo")
            li += 1
            for x in range(li):
                r = rafs.pop()
                if "'" in r:
                    o -= 1

        pd(rafs)
    return rafs

def htoapo(st):
    return st.replace("h", "'")

# Tansky-Lechevalier scoring algorithm
def score(lujvo):
    L = len(lujvo)
    A = lujvo.count("'")
    rafsis = splitLujvo(lujvo)
    lr = 0
    R = 0
    for raf in rafsis:
        lr += len(raf)
        R += rafsiScore(raf)
    H = L - lr
    V = 0
    for c in lujvo:
        if c in vowels:
            V += 1
    pd(lujvo, L, A, H, R, V)
    return 1000*L - 500*A + 100*H - 10*R - V

def possibleLujvo(*gismo):
    gismo=gismo[0]
    pd(gismo)
    rafsi = [x for x in [a.rafsi for a in [vl.get(g) for g in gismo]]]
    for g in range(len(rafsi)):
        for r in range(len(rafsi[g])):
            rafsi[g][r] = rafsi[g][r].replace("\\","")
        if g == len(rafsi) - 1:
            rafsi[g] = [gismo[g]] + rafsi[g]
            rafsi[g] = [r for r in rafsi[g] if r[-1] in "aeiou"]
            continue
        rafsi[g] = [r+e for r in rafsi[g] for e in "yrn"] + rafsi[g]
        rafsi[g].append(gismo[g][:-1]+"y")
    pd(rafsi)
    combine = lambda words, rest: combine([w+n for w in words for n in rest[0] if (w[-1] in "aeiouy" or n[0] in "aeiou") or len(w) < 5], rest[1:]) if len(rest) else words
    rafsi = combine(rafsi[0], rafsi[1:] if len(rafsi)>1 else [])
    pd(rafsi)
    return rafsi

def bestLujvo(*gismo):
    pos = possibleLujvo(gismo[0])
    pos = [(p,score(p)) for p in pos]
    pd(pos)
    pos.sort(key=lambda a: a[1])
    return pos

if __name__ == '__main__':
    import sys
    r = htoapo(sys.argv[2] if len(sys.argv) > 2 else "")
    if sys.argv[1] == "-r":
        print(rafsiForm(r), rafsiScore(r))
    elif sys.argv[1] == "-l":
        print(score(r))
    elif sys.argv[1] == "-s":
        rafs = splitLujvo(r)
        print(rafs)
        for r in rafs:
            print(r, rafsiScore(r))
    elif sys.argv[1] == "-p":
        pos = bestLujvo(sys.argv[2:])
        pos.reverse()
        for l in pos:
            print(l[0], l[1])
