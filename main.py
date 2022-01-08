# Base Code Citation: https://www.youtube.com/watch?v=jHZlvRr9KxM
import discord
from discord.ext import commands
import music

cogs = [music]

client = commands.Bot(command_prefix='!',intents=discord.Intents.all())

for i in range(len(cogs)):
  cogs[i].setup(client)

client.run("OTI4MTQ2MzUwNDMwODg4MDM1.YdUhpg.tCAXyzBINqs10jHQFXanj8BkTnM"))