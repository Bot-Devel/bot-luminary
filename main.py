import discord
from discord.ext import commands  # , tasks
from discord.flags import Intents
from dotenv import load_dotenv
import os
import asyncio

from utils.moderation import check_banned_words, get_mod_message, \
    get_infractions, get_infraction_msg, get_user_inf_muted_timeout, \
    get_modlog_mute_msg

from utils.database import manage_infractions, manage_muted_users
from utils.bot_status import keep_alive

load_dotenv()
TOKEN = os.getenv("TOKEN")

GUILD = int(os.getenv("GUILD"))
BOT_LUMINARY = int(os.getenv("BOT_LUMINARY"))
WELCOME = int(os.getenv("WELCOME"))
BLDISC = int(os.getenv("BLDISC"))
SPLFREE = int(os.getenv("SPLFREE"))
MOD_LOGS = int(os.getenv("MOD_LOGS"))
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
    # if mods or admin, the roles will be returned i.e. not None
    if (discord.utils.get(message.author.roles, name="Mods") is None) and (discord.utils.get(message.author.roles, name="Admin") is None):
        banned_word_found = check_banned_words(message)
        if banned_word_found:
            current_channel = message.channel
            mod_log_channel = bot.get_channel(MOD_LOGS)

            curr_channel_message, mod_log_warn_message = get_mod_message(
                bot, message, banned_word_found)

            timeout_mute = 1
            moderator = bot.get_user(BOT_LUMINARY)
            mod_log_mute_message = get_modlog_mute_msg(
                bot, message.author.id, moderator, timeout_mute)
            user_id, user_infractions = get_infractions(message.author.id)

            # adding the message.delete inside the if statements cuz the db
            # operation has a few secs of delay and the msg needs to be deleted immediately
            if user_infractions < 3:

                await message.delete()  # deletes the message containing the bad word
                infraction_message = f"{message.author.mention} has been warned. You used a word which is not allowed in this server. You have {user_infractions+1} infractions"
                manage_infractions(message, 1)  # add infractions to database
                await mod_log_channel.send(embed=mod_log_warn_message)

            else:

                await message.delete()  # deletes the message containing the bad word
                role = discord.utils.get(message.guild.roles, name="Muted")
                member = message.author
                infraction_message = f"{message.author.mention} has been muted. You used a word which is not allowed in this server."

                await member.add_roles(role)
                manage_muted_users(message, 1)  # insert into muted_users table
                await mod_log_channel.send(embed=mod_log_mute_message)

            await current_channel.send(embed=curr_channel_message)
            await message.author.send(infraction_message)


# background task
async def check_user_inf_mute_status():
    """
    check for muted_users and infractions and clear them after 30 mins timeout
    """
    await bot.wait_until_ready()
    while not bot.is_closed():
        guild = bot.get_guild(GUILD)

        timeout_inf = 60
        timeout_mute = 30
        users_inf_timeout, users_muted_timeout = get_user_inf_muted_timeout(
            timeout_inf, timeout_mute)

        for user in users_muted_timeout:
            manage_muted_users(user, 2)

            role = discord.utils.get(guild.roles, name="Muted")
            member = guild.get_member(int(user))

            # So that it wont stop if it cant remove a user which doesn exist
            try:
                await member.remove_roles(role)
            except Exception:
                pass

        await asyncio.sleep(5)


@bot.command(aliases=['inf'])
@commands.has_any_role("Mods", "Admin")
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
@commands.has_any_role("Mods", "Admin")
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
@commands.has_any_role("Mods", "Admin")
async def mute(ctx, *, arg):
    """
    Inserts the user from the muted_users table
    """
    user = ctx.guild.get_member(int(arg))

    # if mods or admin, the roles will be returned i.e. not None
    if (discord.utils.get(user.roles, name="Mods") is None) and \
            (discord.utils.get(user.roles, name="Admin") is None):
        mod_log_channel = bot.get_channel(MOD_LOGS)

        role = discord.utils.get(ctx.guild.roles, name="Muted")
        member = ctx.guild.get_member(int(arg))

        await member.add_roles(role)

        # inserting into muted_user table
        status = manage_muted_users(int(arg), 1)
        if status:

            bot_message = discord.Embed(
                description="User has been muted!"
            )

            timeout_mute = 30
            moderator = ctx.author
            mod_log_mute_message = get_modlog_mute_msg(
                bot, int(arg), moderator, timeout_mute)

        await mod_log_channel.send(embed=mod_log_mute_message)
        await ctx.channel.send(embed=bot_message)


@ bot.command()
@ commands.has_any_role("Mods", "Admin")
async def unmute(ctx, *, arg):
    """
    Removes the user from the muted_users table
    """
    role = discord.utils.get(ctx.guild.roles, name="Muted")
    member = ctx.guild.get_member(int(arg))

    await member.remove_roles(role)

    status = manage_muted_users(arg, 2)
    if status:
        bot_message = discord.Embed(
            description="User has been unmuted!"
        )

    await ctx.channel.send(embed=bot_message)

keep_alive()  # To start the flask server

# Creates a background task which checks for user infractions & mute timeout
bot.loop.create_task(check_user_inf_mute_status())
bot.run(TOKEN)
