import discord
from discord.ext import commands
from discord.flags import Intents
from dotenv import load_dotenv
from discord.ext import commands
import os

load_dotenv()
TOKEN = os.getenv("TOKEN")

WELCOME = int(os.getenv("WELCOME"))
BLDISC = int(os.getenv("BLDISC"))
SPLFREE = int(os.getenv("SPLFREE"))
RXROLES = int(os.getenv("RXROLES"))

RX_HOUSES = int(os.getenv("RXHOUSES"))
RX_ANNOUNCEMENTS = int(os.getenv("RXANNOUNCEMENTS"))

intents = discord.Intents.default()
intents.members = True
intents.reactions = True

bot = commands.Bot(command_prefix=';', intents=intents)


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="Black Luminary"))


@bot.event
async def on_message(message):
    await bot.process_commands(message)


@bot.event
async def on_member_join(member):
    channel = bot.get_channel(WELCOME)
    bldisc = bot.get_channel(BLDISC)
    splfree = bot.get_channel(SPLFREE)
    welcome = f"Welcome to Black Luminary, {member.mention}! Head over to {bldisc.mention} if you're caught up with the fic, or to {splfree.mention} if you're looking to discuss it while reading!"
    await channel.send(welcome)

rx_dict_houses = {"gryffindor": "Gryffindor", "ravenclaw": "Ravenclaw",
                  "slytherin": "Slytherin", "hufflepuff": "Hufflepuff"}

rx_dict_announcements = {"🗒️": "Story News", "📣": "Announcements"}

rx_dict_master = {"RX_HOUSES": [RX_HOUSES, rx_dict_houses], "RX_ANNOUNCEMENTS": [
    RX_ANNOUNCEMENTS, rx_dict_announcements]}


@bot.event
async def on_raw_reaction_add(payload):
    for i in rx_dict_master.keys():
        if payload.message_id == rx_dict_master[i][0]:
            dict_to_use = rx_dict_master[i][1]
            emote = payload.emoji.name
            guild_id = payload.guild_id
            guild = discord.utils.find(lambda g: g.id == guild_id, bot.guilds)
            if emote in dict_to_use.keys():
                role = discord.utils.get(guild.roles, name=dict_to_use[emote])
                member = discord.utils.find(
                    lambda m: m.id == payload.user_id, guild.members)
                await member.add_roles(role)


@bot.event
async def on_raw_reaction_remove(payload):
    for i in rx_dict_master.keys():
        if payload.message_id == rx_dict_master[i][0]:
            dict_to_use = rx_dict_master[i][1]
            emote = payload.emoji.name
            guild_id = payload.guild_id
            guild = discord.utils.find(lambda g: g.id == guild_id, bot.guilds)
            if emote in dict_to_use.keys():
                role = discord.utils.get(guild.roles, name=dict_to_use[emote])
                member = discord.utils.find(
                    lambda m: m.id == payload.user_id, guild.members)
                await member.remove_roles(role)

bot.run(TOKEN)
