import dice
import discord
import os

_client = discord.Client()

def run(id, token):
    id = os.environ[id]
    token = os.environ[token]
    print(id)
    print(token)
    _client.run(token)
