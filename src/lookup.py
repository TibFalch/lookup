#!/usr/bin/env python3.5
import discord  # library v0.10 to interface with discord
import nltk     # natural language tool kit
import os       # used for environment variables

client = discord.Client()

def searchWords(message):
    tokens = nltk.word_tokenize(message)
    tagged = nltk.pos_tag(tokens)
    sw = [] # array to contain all found phrases
    # TODO traverse the tree and find combined phrases
    # there's a function in the nltk library to do that..
    for v in tagged:
        print(v)
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
    wrds = searchWords(message.content)
    # assumes that all found wrds have existing articles on wikipedia
    # don't answer to your own message!
    if len(wrds) > 0 and message.author != client.user:
        print(wrds)
        answ = "**Look it up:**\n"
        for w in wrds:
            answ += "https://en.wikipedia.org/wiki/" + w + "\n"
        print(answ)
        await client.send_message(message.channel, answ)

if __name__ == "__main__":
    # LookUpAPID contains the token
    token = os.environ["LOOKUPAPID"]
    client.run(token)
