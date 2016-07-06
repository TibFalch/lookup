#!/usr/bin/env python3.5

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

def isVowel(c):
    return c in vowels or c == "y"

def isConsonant(c):
    return not isVowel(c)

def rafsiForm(rafsi):
    r = ""
    for c in rafsi:
        if c == "'":
            continue
        r += "V" if isVowel(c) else "C"
    return r

def rafsiScore(rafsi, final=False):
    form = rafsiForm(rafsi)
    if len(form) == 5 and form[4] not in "yrn":
        final = True
    elif len(form) == 5:
        form = form[4]
        print("reduced form to", form)
    form = form if not final else form + "f"
    sc = rafsco.get(form, None)
    if sc == 8 and "'" in rafsi:
        sc = 6
    return sc

def splitLujvo(lujvo):
    form = rafsiForm(lujvo)
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
            elif i+5 == len(lujvo):
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
                        print("Proposed skip useful")
                        i += 1
                        break
            i += 3
        else:
            print("redo")
            li += 1
            for x in range(li):
                r = rafs.pop()
                if "'" in r:
                    o -= 1

        print(rafs)
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
    print(L, A, H, R, V)
    return 1000*L - 500*A + 100*H - 10*R - V


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
