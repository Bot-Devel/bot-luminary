import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import os
import asyncio

from utils.moderation import check_banned_words, get_mod_message, \
    get_infractions, get_infraction_msg, get_user_inf_muted_timeout, \
    get_modlog_mute_msg

from utils.database import manage_infractions, manage_muted_users

load_dotenv()
GUILD = int(os.getenv("GUILD"))
BOT_LUMINARY = int(os.getenv("BOT_LUMINARY"))
MOD_LOGS = int(os.getenv("MOD_LOGS"))


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_user_inf_mute_status.start()

    def cog_unload(self):
        self.check_user_inf_mute_status.cancel()

    @commands.Cog.listener()
    async def on_message(self, message):

        # if mods or admin, the roles will be returned i.e. not None
        if (discord.utils.get(message.author.roles, name="Mods") is None) and (discord.utils.get(message.author.roles, name="Admin") is None):
            banned_word_found = check_banned_words(message)
            if banned_word_found:
                current_channel = message.channel
                mod_log_channel = self.bot.get_channel(MOD_LOGS)

                curr_channel_message, mod_log_warn_message = get_mod_message(
                    self.bot, message, banned_word_found)

                timeout_mute = 1
                moderator = self.bot.get_user(BOT_LUMINARY)
                mod_log_mute_message = get_modlog_mute_msg(
                    self.bot, message.author.id, moderator, timeout_mute)
                user_id, user_infractions = get_infractions(message.author.id)

                # adding the message.delete inside the if statements cuz the db
                # operation has a few secs of delay and the msg needs to be deleted immediately
                if user_infractions < 3:

                    await message.delete()  # deletes the message containing the bad word
                    infraction_message = f"{message.author.mention} has been warned. You used a word which is not allowed in this server. You have {user_infractions+1} infractions"
                    # add infractions to database
                    manage_infractions(message, 1)
                    await mod_log_channel.send(embed=mod_log_warn_message)

                else:

                    await message.delete()  # deletes the message containing the bad word
                    role = discord.utils.get(message.guild.roles, name="Muted")
                    member = message.author
                    infraction_message = f"{message.author.mention} has been muted. You used a word which is not allowed in this server."

                    await member.add_roles(role)
                    # insert into muted_users table
                    manage_muted_users(message, 1)
                    await mod_log_channel.send(embed=mod_log_mute_message)

                await current_channel.send(embed=curr_channel_message)
                await message.author.send(infraction_message)

    # Creates a background task which checks for user infractions & mute timeout
    @tasks.loop(seconds=5.0)
    async def check_user_inf_mute_status(self):
        """
        check for muted_users and infractions and clear them after 30 mins timeout
        """

        while not self.bot.is_closed():
            guild = self.bot.get_guild(GUILD)

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

            await asyncio.sleep(10)

    @check_user_inf_mute_status.before_loop
    async def before_check_user_inf_mute_status(self):
        await self.bot.wait_until_ready()

    @commands.command(aliases=['inf'])
    @commands.has_any_role("Mods", "Admin")
    async def infractions(self, ctx, *, arg):
        """
        Checks the infractions table for user infractions
        """

        user_id, user_infractions = get_infractions(arg)

        if user_id is not None:
            user_name = self.bot.get_user(user_id)
            user_infraction_message = get_infraction_msg(
                user_name, user_infractions)
        else:
            user_infraction_message = discord.Embed(
                description="No infractions found!"
            )

        await ctx.channel.send(embed=user_infraction_message)

    @commands.command(aliases=['clr_all_inf', 'clr-all-inf', 'clear-all-infractions'])
    @commands.has_any_role("Mods", "Admin")
    async def clear_all_infractions(self, ctx, *, arg):
        """
        Deletes all infractions for the user from the infractions table
        """

        status = manage_infractions(arg, 2)
        if status:
            clear_infraction_message = discord.Embed(
                description="All infractions cleared for the user!"
            )

        await ctx.channel.send(embed=clear_infraction_message)

    @commands.command()
    @commands.has_any_role("Mods", "Admin")
    async def mute(self, ctx, *, arg):
        """
        Inserts the user from the muted_users table
        """
        user = ctx.guild.get_member(int(arg))

        # if mods or admin, the roles will be returned i.e. not None
        if (discord.utils.get(user.roles, name="Mods") is None) and \
                (discord.utils.get(user.roles, name="Admin") is None):
            mod_log_channel = self.bot.get_channel(MOD_LOGS)

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
                    self.bot, int(arg), moderator, timeout_mute)

            await mod_log_channel.send(embed=mod_log_mute_message)
            await ctx.channel.send(embed=bot_message)

    @commands.command()
    @commands.has_any_role("Mods", "Admin")
    async def unmute(self, ctx, *, arg):
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


def setup(bot):
    bot.add_cog(Moderation(bot))
