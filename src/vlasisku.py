#!/usr/bin/env python3.5
import os
import discord
import vlasisapi

lb = discord.Client()
lbc = []
itc = dict()

async def stwexe(msg, prefix, func):
    s = "!{} ".format(prefix)
    if msg.content.startswith(s):
        msg.content = msg.content[len(s):]
        await func(msg)
        return True
    return False

async def vlasisku_search(msg):
    v = None
    try:
        v = vlasisapi.get(msg.content)
    except:
        await lb.delete_message(msg)
        await lb.send_message(msg.channel, "Could not find **{}**".format(msg.content))
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
        t = "**{}**: {} \t{}\n{}".format(v.finding, v.getrafsi("-","*-","-*"), v.type, v.definition)
    try:
        await lb.send_message(msg.channel, t[:2000])
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
    if vl and not msg.channel in lbc:
        lbc.append(msg.channel)
    if vl:
        itc[str(msg.author.display_name)] = itc.get(str(msg.author.display_name), 0) +1

def tell_all():
    t = "**Stats**\n```\n"
    for u, n in itc.items():
        t += "{}: {}\n".format(str(u), n)
    t += "```"
    for c in lbc:
        lb.loop.create_task(lb.send_message(c, t))

def cliloop():
    while True:
        line = str(input("> "))
        if line == "stats":
            tell_all()
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
