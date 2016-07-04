#!/usr/bin/env python3.5
import discord    # library v0.10 to interface with discord
#import nltk       # natural language tool kit
import os         # used for environment variables
import wikipedia  # used for looking up wiki entries
import genius_lyrics.g_lyrics_funcs as genius

client = discord.Client()

# Search Depth to get rid of disambiguations
WIKI_SEARCH_DEPTH = 2
LANGUAGE = {}
USED_CHANNEL = []

# This is just debugging
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

# Called when the server, the bot is invited into receives a message
@client.event
async def on_message(message):
    if not message.channel in USED_CHANNEL:
        USED_CHANNEL.append(message.channel)
        LANGUAGE[message.channel] = "en"

    if message.content.startswith("!latex "):
        cmd = message.content[len("!latex "):]
        stand = """\\documentclass[preview]{standalone}
\\usepackage{amsmath}
\\begin{document}
$ %s $
\\end{document}"""
        out = open("/tmp/lookup.tex", "w")
        out.write(stand % cmd)
        out.close()
        os.system("cd /tmp; xelatex -interaction=nonstopmode lookup.tex && convert -density 600 lookup.pdf lookup.jpg")
        await client.send_file(message.channel, "/tmp/lookup.jpg", filename="latex.jpg", content="Here's your picture:")




    if message.content.startswith("!what "):
        try:
            wikipedia.set_lang(LANGUAGE[message.channel])
            await client.send_message(message.channel, wikipedia.summary(message.content[6:], sentences=2))
        except:
            pass
        return

    if message.content.startswith("!ed "):
        try:
            await client.send_message(message.channel, "{:.2f} DKK".format(float(message.content[4:]) * 7.43601))
        except:
            pass

    if message.content.startswith("!de "):
        try:
            await client.send_message(message.channel, "{:.2f} €".format(float(message.content[4:]) * 0.134481))
        except:
            pass

    if message.content.startswith("!lyrics "):
        try:
            await client.send_message(message.channel, genius.genius_search(message.content[8:])[0].form_output())
        except:
            await client.send_message(message.channel, "Couldn't find song!")
        yt = "https://www.youtube.com/results?search_query="
        for s in message.content[8:].split():
            yt += s+ "+"
        await client.send_message(message.channel, yt[:-1])
        return

    if message.content.startswith("!wikilang "):
        LANGUAGE[message.channel] = message.content[10:]


async def wikiAnswer(client, message, wrds):
    # assumes that all found wrds have existing articles on wikipedia
    # don't answer to your own message!
    if len(wrds) and (message.author != client.user):
        print(wrds)
        answ = "**Look it up:**\n"
        for w in wrds:
            ispage = True  # maybe necessary later
            page = { "url": "#error" } # still error if fetch fails
            for x in range(WIKI_SEARCH_DEPTH):
                try:
                    wikipedia.set_lang(LANGUAGE[message.channel])
                    page = wikipedia.page(wikipedia.search(w)[x])
                except:
                    continue
                answ += w + ": " + page.url + "\n"
                ispage = True
                break
        print(answ)
        await client.send_message(message.channel, answ)

# not used
async def broadcast():
    while 1:
        text = input()
        for c in USED_CHANNEL:
            try:
                client.send_message(c, text)
            except:
                pass

if __name__ == "__main__":
    # LookUpAPID contains the token
    token = os.environ["LOOKUPAPID"]
    client.run(token)
