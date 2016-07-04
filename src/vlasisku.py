#!/usr/bin/env python3.5
import os
import discord
import vlasisapi

lb = discord.Client()

async def stwexe(msg, prefix, func):
    s = "!{} ".format(prefix)
    if msg.content.startswith(s):
        msg.content = msg.content[len(s):]
        await func(msg)

async def vlasisku_search(msg):
    v = None
    try:
        v = vlasisapi.get(msg.content)
    except Exception as e:
        await lb.delete_message(msg)
        await lb.send_message(msg.channel, "Could not find **{}**".format(msg.content))
    if v is None:
        return
    t = ""
    if v.type == "search":
        t = "Results for search term: **{}**\n".format(v.search)
        for x in range(v.num):
            t += "**{}**:\n    {}\n".format(v.finding[x], v.definition[x] if len(v.definition[x]) < 200 else v.definition[x][:200] + " ...")
            if x == 10:
                t += "\n*and more:* {}\n".format(vlasisapi.furl(v.search))
                break
    else:
        if len(v.rafsi):
            r = "\t*-"
            for raf in v.rafsi:
                r += raf + "-"
            r += "*"
        else:
            r = ""

        t = "**{}**:{} \t{}\n{}".format(v.search, r, v.type, v.definition)
    print(t)
    try:
        await lb.send_message(msg.channel, t[:2000])
        await lb.delete_message(msg)
    except discord.errors.Forbidden:
        print("forbidden to delete command")
    except discord.errors.HTTPException:
        print("response too long")

@lb.event
async def on_ready():
    print("lb: ready")

@lb.event
async def on_message(msg):
    await stwexe(msg, "vl", vlasisku_search)

if __name__ == "__main__":
    lb.run(os.environ["MIBVLASISKU"])
