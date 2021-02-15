import discord
from discord import channel
from discord.ext import commands
from discord.flags import Intents
from dotenv import load_dotenv
from discord.ext import commands
import os

load_dotenv()
TOKEN=os.getenv("TOKEN")

intents = discord.Intents.default()
intents.members = True

bot=commands.Bot(command_prefix=';', intents=intents)

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="Black Luminary"))
    print("Online.")

@bot.event
async def on_member_join(member):
    channelId = 803742201875005440 #greetings
    channel = bot.get_channel(channelId)
    bldisc=bot.get_channel(803742258880577547)
    splfree=bot.get_channel(806147166434885652)
    welcome=f"Welcome to Black Luminary {member.mention}! Head over to {bldisc.mention} if you're caught up with the fic, or to {splfree.mention} if you're looking to discuss it while reading!"
    await channel.send(welcome)

bot.run(TOKEN)