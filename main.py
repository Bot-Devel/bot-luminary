import discord
from discord.ext import commands
from discord.flags import Intents
from dotenv import load_dotenv
import os

from utils.moderation import check_bad_words, get_mod_message, \
    get_show_infractions, get_infraction_msg
from utils.database import manage_infractions
# from utils.bot_status import keep_alive
from utils.welcome import welcome_message
from utils.reaction_roles import rx_dict_master, role_update

intents = discord.Intents.default()
intents.members = True
intents.reactions = True

bot = commands.Bot(command_prefix=';', intents=intents)

load_dotenv()
TOKEN = os.getenv("TOKEN")

WELCOME = int(os.getenv("WELCOME"))
BLDISC = int(os.getenv("BLDISC"))
SPLFREE = int(os.getenv("SPLFREE"))
RXROLES = int(os.getenv("RXROLES"))
JOIN_LEAVE = int(os.getenv("JOINLEAVE"))
MEMBERS_LOG = int(os.getenv("MEMBERSLOG"))


@bot.event
async def on_ready():
    rx_roles = bot.get_channel(RXROLES)
    await bot.change_presence(
        activity=discord.Game(name="Black Luminary")
    )


@bot.event
async def on_member_join(member):
    members_log = bot.get_channel(MEMBERS_LOG)
    channel = bot.get_channel(WELCOME)
    bldisc = bot.get_channel(BLDISC)
    splfree = bot.get_channel(SPLFREE)
    join_leave = bot.get_channel(JOIN_LEAVE)

    welcome = f"Welcome to Black Luminary, {member.mention}! Head over to {bldisc.mention} if you're caught up with the fic or to {splfree.mention} if you're looking to discuss it while reading!"

    mod_welcome_message = welcome_message(member, 1)

    await channel.send(welcome)

    role = discord.utils.get(
        member.guild.roles, name="Person"
    )
    await member.add_roles(role)
    role_update_message = role_update(member, role, 1)

    await join_leave.send(embed=mod_welcome_message)
    await members_log.send(embed=role_update_message)


@bot.event
async def on_member_remove(member):

    join_leave = bot.get_channel(JOIN_LEAVE)
    mod_leave_message = welcome_message(member, 0)
    await join_leave.send(embed=mod_leave_message)


@ bot.event
async def on_raw_reaction_add(payload):
    members_log = bot.get_channel(MEMBERS_LOG)
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
                role_update_message = role_update(member, role, 1)
                await members_log.send(embed=role_update_message)


@bot.event
async def on_raw_reaction_remove(payload):
    members_log = bot.get_channel(MEMBERS_LOG)
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
                role_update_message = role_update(member, role, 0)
                await members_log.send(embed=role_update_message)


@bot.event
async def on_message(message):
    # To run bot.commands & bot.event simultaneously
    await bot.process_commands(message)

    bad_words_found = check_bad_words(message)
    if bad_words_found:
        current_channel = message.channel
        mod_log_channel = bot.get_channel(810574629647286294)

        curr_channel_message, mod_log_message = get_mod_message(
            bot, message, bad_words_found)

        manage_infractions(message, 1)  # add infractions to database

        await message.delete()  # deletes the message containing the bad word
        await current_channel.send(embed=curr_channel_message)
        await mod_log_channel.send(embed=mod_log_message)


@bot.command(aliases=['inf'])
async def infractions(ctx, *, arg):
    """
    Checks the moderation table for user infractions
    """

    if discord.utils.get(ctx.author.roles, name="Mods") is not None:

        user_id, user_infractions = get_show_infractions(arg)

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
async def clear_all_infractions(ctx, *, arg):
    """
    Deletes all infractions for the user from the moderation table
    """
    if discord.utils.get(ctx.author.roles, name="Mods") is not None:

        status = manage_infractions(arg, 2)
        if status:
            clear_infraction_message = discord.Embed(
                description="All infractions cleared for the user!"
            )

        await ctx.channel.send(embed=clear_infraction_message)

# keep_alive()
bot.run(TOKEN)
