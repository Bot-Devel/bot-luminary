import discord
from discord.ext import commands
from discord.flags import Intents
from dotenv import load_dotenv
import os

from utils.moderation import check_banned_words, get_mod_message, \
    get_infractions, get_infraction_msg
from utils.database import manage_infractions, manage_muted_users
from utils.bot_status import keep_alive

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
    await bot.change_presence(
        activity=discord.Game(name="Black Luminary")
    )


@bot.event
async def on_member_join(member):

    channel = bot.get_channel(WELCOME)
    bldisc = bot.get_channel(BLDISC)
    splfree = bot.get_channel(SPLFREE)

    welcome = f"Welcome to Black Luminary, {member.mention}! Head over to {bldisc.mention} if you're caught up with the fic, or to {splfree.mention} if you're looking to discuss it while reading!"

    await channel.send(welcome)

rx_dict_houses = {
    "gryffindor": "Gryffindor",
    "ravenclaw": "Ravenclaw",
    "slytherin": "Slytherin",
    "hufflepuff": "Hufflepuff"
}

rx_dict_announcements = {
    "🗒️": "Story News",
    "📣": "Announcements"
}

rx_dict_master = {
    "RX_HOUSES": [RX_HOUSES, rx_dict_houses],
    "RX_ANNOUNCEMENTS": [RX_ANNOUNCEMENTS, rx_dict_announcements]
}


@bot.event
async def on_raw_reaction_add(payload):
    for i in rx_dict_master.keys():
        if payload.message_id == rx_dict_master[i][0]:

            dict_to_use = rx_dict_master[i][1]
            emote = payload.emoji.name
            guild_id = payload.guild_id

            guild = discord.utils.find(
                lambda g: g.id == guild_id, bot.guilds
            )

            if emote in dict_to_use.keys():
                role = discord.utils.get(
                    guild.roles, name=dict_to_use[emote]
                )

                member = discord.utils.find(
                    lambda m: m.id == payload.user_id, guild.members
                )
                await member.add_roles(role)


@bot.event
async def on_raw_reaction_remove(payload):
    for i in rx_dict_master.keys():
        if payload.message_id == rx_dict_master[i][0]:

            dict_to_use = rx_dict_master[i][1]
            emote = payload.emoji.name
            guild_id = payload.guild_id

            guild = discord.utils.find(
                lambda g: g.id == guild_id, bot.guilds
            )

            if emote in dict_to_use.keys():
                role = discord.utils.get(
                    guild.roles, name=dict_to_use[emote]
                )

                member = discord.utils.find(
                    lambda m: m.id == payload.user_id, guild.members
                )
                await member.remove_roles(role)


@bot.event
async def on_message(message):
    # To run bot.commands & bot.event simultaneously
    await bot.process_commands(message)

    # moderation
    banned_word_found = check_banned_words(message)
    if banned_word_found:
        current_channel = message.channel
        mod_log_channel = bot.get_channel(810574629647286294)

        curr_channel_message, mod_log_message = get_mod_message(
            bot, message, banned_word_found)

        user_id, user_infractions = get_infractions(message.author.id)
        if user_infractions <= 3:
            manage_infractions(message, 1)  # add infractions to database
            infraction_message = f"{message.author.mention} has been warned. You used a word which is not allowed in this server. You have {user_infractions+1} infractions"

        else:
            role = discord.utils.get(message.guild.roles, name="Muted")
            member = message.author
            infraction_message = f"{message.author.mention} has been muted. You used a word which is not allowed in this server. You have {user_infractions+1} infractions"

            manage_muted_users(message, 1)  # insert into muted_users table

            await member.add_roles(role)

        await message.delete()  # deletes the message containing the bad word
        await current_channel.send(embed=curr_channel_message)
        await message.author.send(infraction_message)
        await mod_log_channel.send(embed=mod_log_message)


@bot.command(aliases=['inf'])
@commands.has_role("Mods")
async def infractions(ctx, *, arg):
    """
    Checks the infractions table for user infractions
    """

    user_id, user_infractions = get_infractions(arg)

    if user_id is not None:
        user_name = bot.get_user(user_id)
        user_infraction_message = get_infraction_msg(
            user_name, user_infractions)
    else:
        user_infraction_message = discord.Embed(
            description="No infractions found!"
        )

    await ctx.channel.send(embed=user_infraction_message)


@bot.command(aliases=['clr_all_inf', 'clr-all-inf', 'clear-all-infractions'])
@commands.has_role("Mods")
async def clear_all_infractions(ctx, *, arg):
    """
    Deletes all infractions for the user from the infractions table
    """

    status = manage_infractions(arg, 2)
    if status:
        clear_infraction_message = discord.Embed(
            description="All infractions cleared for the user!"
        )

    await ctx.channel.send(embed=clear_infraction_message)


@bot.command()
@commands.has_role("Mods")
async def mute(ctx, *, arg):
    """
    Removes the user from the muted_users table
    """

    status = manage_muted_users(int(arg), 1)
    if status:

        bot_message = discord.Embed(
            description="User has been muted!"
        )
    role = discord.utils.get(ctx.guild.roles, name="Muted")
    member = ctx.guild.get_member(int(arg))

    await member.add_roles(role)
    await ctx.channel.send(embed=bot_message)


@bot.command()
@commands.has_role("Mods")
async def unmute(ctx, *, arg):
    """
    Removes the user from the muted_users table
    """

    status = manage_muted_users(arg, 2)
    if status:
        bot_message = discord.Embed(
            description="User has been unmuted!"
        )
    role = discord.utils.get(ctx.guild.roles, name="Muted")
    member = ctx.guild.get_member(int(arg))

    await member.remove_roles(role)
    await ctx.channel.send(embed=bot_message)

keep_alive()
bot.run(TOKEN)
