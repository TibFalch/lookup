import os
import lookbot as lb
import discord_dice as db
lb.client.login(os.environ["LOOKUPAPID"])
lb.client.connect()
db.run("DICEBOTID", "DICEBOT")
