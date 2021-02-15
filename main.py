import discord
from discord.ext import commands
from discord.flags import Intents
from dotenv import load_dotenv
from discord.ext import commands
import os

from utils.moderation import check_bad_words, get_mod_message

load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix=';', intents=intents)


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="Black Luminary"))


@bot.event
async def on_member_join(member):
    # greetings channel
    gr_channel = bot.get_channel(803742201875005440)
    # black-luminary-discussion channel
    bl_disc_channel = bot.get_channel(803742258880577547)
    # spoilerfree-black-luminary channel
    spl_free_channel = bot.get_channel(806147166434885652)

    welcome = f"Welcome to Black Luminary {member.mention}! Head over to \
    {bl_disc_channel.mention} if you're caught up with the fic, or to \
    {spl_free_channel.mention} if you're looking to discuss it while reading!"

    await gr_channel.send(welcome)


@bot.event
async def on_message(message):

    # moderation
    bad_words_found = check_bad_words(message)
    if bad_words_found:
        current_channel = message.channel
        mod_log_channel = bot.get_channel(810574629647286294)

        channel_message, mod_log_message = get_mod_message(
            bot, message, bad_words_found)

        await message.delete()
        await current_channel.send(embed=channel_message)
        await mod_log_channel.send(embed=mod_log_message)


bot.run(TOKEN)
