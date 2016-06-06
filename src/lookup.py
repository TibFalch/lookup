#!/usr/bin/env python3.5
import discord    # library v0.10 to interface with discord
import nltk       # natural language tool kit
import os         # used for environment variables
import wikipedia  # used for looking up wiki entries
import genius_lyrics.g_lyrics_funcs as genius

client = discord.Client()

# Search Depth to get rid of disambiguations
WIKI_SEARCH_DEPTH = 2
LANGUAGE = "en"

def searchWords(message):
    tokens = nltk.word_tokenize(message)
    tagged = nltk.pos_tag(tokens)
    sw = [] # array to contain all found phrases
    # TODO traverse the tree and find combined phrases
    # there's a function in the nltk library to do that..
    tree = nltk.chunk.ne_chunk(tagged)
    print(tree)
    for v in tagged:
        if v[1] == "NP" or v[1] == "NNS" or v[1] == "NNP" or v[1] == "NN":
            sw.append(v[0])
    # TODO check whether a wikipedia article exists
    return sw # return the phrases

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
    if message.content.startswith("!what "):
        try:
            await client.send_message(message.channel, wikipedia.summary(message.content[6:], sentences=2))
        except:
            pass
        return

    if message.content.startswith("!lyrics "):
        try:
            await client.send_message(message.channel, genius.genius_search(message.content[8:])[0].form_output())
        except:
            pass
        return

    if message.content.startswith("!wikilang "):
        wikipedia.set_lang(message.content[10:])

    if message.content.startswith("!explain "):
        wrds = searchWords(message.content[9:])
        await wikiAnswer(client, message, wrds)
        return


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
                    page = wikipedia.page(wikipedia.search(w)[x])
                except:
                    continue
                answ += w + ": " + page.url + "\n"
                ispage = True
                break
        print(answ)
        await client.send_message(message.channel, answ)

if __name__ == "__main__":
    # LookUpAPID contains the token
    token = os.environ["LOOKUPAPID"]
    client.run(token)
