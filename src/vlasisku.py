#!/usr/bin/env python3.5
import os
import discord
import vlasisapi
import lujvo

lb = discord.Client()
lbc = []
itc = dict()

async def stwexe(msg, prefix, func):
    s = "!{} ".format(prefix)
    if msg.content.startswith(s):
        msg.content = msg.content[len(s):]
        try:
            await func(msg)
        except discord.HTTPException:
            await reply(msg, "Dicsord HTTP Error")
        except Exception as e:
            await reply(msg, "Internal Error\n"+str(e))
        return True
    return False

async def reply(msg, text):
    await lb.send_message(msg.channel, texts)

async def lujvo_combine(msg):
    await reply(msg, "**{}** {}".format(*(lujvo.bestLujvo(msg.content.split(" "))[0])))

async def lujvo_split(msg):
    raf = lujvo.splitLujvo(msg.content)
    print(raf)
    t = "-".join(raf)
    await reply(msg, "**"+t+"**")

async def vlasisku_search(msg):
    v = None
    try:
        v = vlasisapi.get(msg.content)
    except:
        await lb.delete_message(msg)
        await reply(msg, "Could not find **{}**".format(msg.content))
    if v is None:
        return
    t = ""
    if v.type == "search":
        t = "Results for search term: **{}**\n".format(v.search)
        for x in range(v.num):
            t += "**{}**:\n    {}\n".format(v.finding[x], v.definition[x])
            if x == 10:
                t += "\n*and more:* {}\n".format(vlasisapi.furl(v.search))
                break
    else:
        t = "**{}**: {} \t{}\n{}".format(v.finding, v.getrafsi(), v.type, v.definition)
    try:
        await reply(msg, t[:2000])
        await lb.delete_message(msg)
    except discord.errors.Forbidden:
        print("forbidden to delete command")
    except discord.errors.HTTPException:
        print("response too long")
        print(e)
    except Exception as e:
        print("unknown exception:",e)

@lb.event
async def on_ready():
    #print("lb: ready")
    pass

@lb.event
async def on_message(msg):
    vl = await stwexe(msg, "vl", vlasisku_search)
    vl = vl or await stwexe(msg, "lc", lujvo_combine)
    vl = vl or await stwexe(msg, "ls", lujvo_split)
    if vl and not msg.channel in lbc:
        lbc.append(msg.channel)
    if vl:
        c = "{}#{}".format(msg.author.name, msg.author.discriminator)
        itc[c] = itc.get(c, 0) + 1

def tell_all():
    t = "**Stats**\n"
    for u, n in itc.items():
        t += "{} : {}\n".format(str(u), n)
    for c in lbc:
        lb.loop.create_task(lb.send_message(c, t))

async def send_as(text, name, back):
    for c in lbc:
        try:
            await lb.change_nickname(c.server.me, name)
        except :
            pass #no permission to change own nick
        await lb.send_message(c, text)
        try:
            await lb.change_nickname(c.server.me, back)
        except:
            pass #no permission to change own nick

def broadcast(text, name="mibvlasisku", back="mibvlasisku"):
    lb.loop.create_task(send_as(text[:2000],name,back))

def cliloop():
    import re
    while True:
        line = str(input("> "))
        if line == "stats":
            tell_all()
        if line.startswith("say "):
            broadcast(line[4:])
        if line.startswith("sayas "):
            name, text = re.search("sayas (\S*) (.*)", line).groups()
            broadcast(text, name)
        if line == "quit":
            lb.loop.create_task(lb.logout())
            return

if __name__ == "__main__":
    import threading
    import sys
    t = threading.Thread(target=cliloop, daemon=True)
    t.start()
    lb.run(os.environ["MIBVLASISKU"])
    sys.exit(0)
