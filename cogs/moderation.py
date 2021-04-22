import discord
from discord.ext import tasks
from discord.ext.commands import has_any_role, command, Cog
from dotenv import load_dotenv
import os
import asyncio

from utils.moderation import check_banned_words, get_banned_wrd_message, \
    get_infractions, get_infraction_msg, get_user_inf_muted_timeout, \
    get_modlog_mute_msg, get_modlog_kick_ban_msg, get_mod_log_warn_message

from utils.database import manage_infractions, manage_muted_users

load_dotenv()
GUILD = int(os.getenv("GUILD"))
BOT_LUMINARY = int(os.getenv("BOT_LUMINARY"))
MOD_LOGS = int(os.getenv("MOD_LOGS"))


class Moderation(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_user_inf_mute_status.start()

    def cog_unload(self):
        self.check_user_inf_mute_status.cancel()

    @Cog.listener()
    async def on_message(self, message):
        # if mods or admin, the roles will be returned i.e. not None
        if (discord.utils.get(message.author.roles, name="Mods") is None) and (discord.utils.get(message.author.roles, name="Admin") is None):
            banned_word_found = check_banned_words(message)
            if banned_word_found:
                current_channel = message.channel
                mod_log_channel = self.bot.get_channel(MOD_LOGS)

                curr_channel_message, mod_log_warn_message = get_banned_wrd_message(
                    self.bot, message, banned_word_found)

                reason = "Bad word usage"
                timeout_mute = 30
                moderator = self.bot.get_user(BOT_LUMINARY)
                mod_log_mute_message = get_modlog_mute_msg(
                    self.bot, message.author, moderator, timeout_mute, reason)
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
                    manage_muted_users(message, timeout_mute, 1)
                    await mod_log_channel.send(embed=mod_log_mute_message)

                await current_channel.send(embed=curr_channel_message)
                await message.author.send(infraction_message)

    # Creates a background task which checks for user infractions & mute timeout
    @tasks.loop(seconds=5.0)
    async def check_user_inf_mute_status(self):
        """
        Check for muted_users and infractions and clear them after timeout
        """

        while not self.bot.is_closed():
            guild = self.bot.get_guild(GUILD)

            users_inf_timeout, users_muted_timeout = get_user_inf_muted_timeout()

            for user in users_inf_timeout:
                manage_infractions(user, 2)

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

    @command(aliases=['inf'])
    @has_any_role("Mods", "Admin")
    async def infractions(self, ctx, member: discord.Member = None):
        """
        Checks the infractions table for user infractions
        """

        user_id, user_infractions = get_infractions(member.id)

        if user_id is not None:
            user_name = self.bot.get_user(user_id)
            user_infraction_message = get_infraction_msg(
                user_name, user_infractions)
        else:
            user_infraction_message = discord.Embed(
                description="No infractions found!"
            )

        await ctx.channel.send(embed=user_infraction_message)

    @command(aliases=['clr_all_inf', 'clr-all-inf', 'clear-all-infractions'])
    @has_any_role("Mods", "Admin")
    async def clear_all_infractions(self, ctx, member: discord.Member = None):
        """
        Deletes all infractions for the user from the infractions table
        """

        status = manage_infractions(member.id, 2)
        if status:
            clear_infraction_message = discord.Embed(
                description="All infractions cleared for the user!"
            )

        await ctx.channel.send(embed=clear_infraction_message)

    @command()
    @has_any_role("Mods", "Admin")
    async def mute(self, ctx, member: discord.Member = None, time_out=15.0, *, reason=None):
        """
        Inserts the user to the muted_users table and sends a mute event message
        """

        # if mods or admin, the roles will be returned i.e. not None
        if (discord.utils.get(member.roles, name="Mods") is None) and \
                (discord.utils.get(member.roles, name="Admin") is None):
            mod_log_channel = self.bot.get_channel(MOD_LOGS)

            role = discord.utils.get(ctx.guild.roles, name="Muted")

            await member.add_roles(role)

            # inserting into muted_user table
            manage_muted_users(member, 1, time_out)

            bot_message = discord.Embed(
                description="User has been muted!"
            )

            timeout_mute = 30
            moderator = ctx.author
            mod_log_mute_message = get_modlog_mute_msg(
                self.bot, member, moderator, timeout_mute, reason)

            await mod_log_channel.send(embed=mod_log_mute_message)
            await ctx.channel.send(embed=bot_message)

    @command()
    @has_any_role("Mods", "Admin")
    async def unmute(self, ctx, member: discord.Member = None, *, reason=None):
        """
        Removes the user from the muted_users table
        """
        role = discord.utils.get(ctx.guild.roles, name="Muted")

        await member.remove_roles(role)

    @command()
    @has_any_role("Mods", "Admin")
    async def ban(self, ctx, member: discord.User = None, *, reason=None):

        mod_log_channel = self.bot.get_channel(MOD_LOGS)
        if (member is None) or (member == ctx.message.author):
            return

        if reason is None:
            reason = "Reasons!"

        msg_type = 1  # ban
        moderator = ctx.author
        mod_log_ban_message = get_modlog_kick_ban_msg(
            self.bot, member, moderator, reason, msg_type)

        message = f"You have been banned from {ctx.guild.name} for {reason}"

        await member.send(message)
        await ctx.guild.ban(member, reason=reason)
        await mod_log_channel.send(embed=mod_log_ban_message)
        await ctx.channel.send(f"{member} is banned!")

    @command()
    @has_any_role("Mods", "Admin")
    async def unban(self, ctx, member: discord.User = None, *, reason=None):

        mod_log_channel = self.bot.get_channel(MOD_LOGS)
        if (member is None) or (member == ctx.message.author):
            return

        if reason is None:
            reason = "Reasons!"

        msg_type = 2  # unban
        moderator = ctx.author
        mod_log_ban_message = get_modlog_kick_ban_msg(
            self.bot, member, moderator, reason, msg_type)

        message = f"You have been unbanned from {ctx.guild.name} for {reason}. \
         Behave from next time."

        await member.send(message)
        await ctx.guild.unban(member, reason=reason)
        await mod_log_channel.send(embed=mod_log_ban_message)

    @command()
    @has_any_role("Mods", "Admin")
    async def kick(self, ctx, member: discord.User = None, *, reason=None):

        mod_log_channel = self.bot.get_channel(MOD_LOGS)
        if (member is None) or (member == ctx.message.author):
            return

        if reason is None:
            reason = "Reasons!"

        msg_type = 3  # kick
        moderator = ctx.author
        mod_log_message = get_modlog_kick_ban_msg(
            self.bot, member, moderator, reason, msg_type)

        message = f"You have been kicked from {ctx.guild.name} for {reason}"

        await member.send(message)
        await ctx.guild.kick(member, reason=reason)
        await mod_log_channel.send(embed=mod_log_message)
        await ctx.channel.send(f"{member} has been kicked out!")

    @command()
    @has_any_role("Mods", "Admin")
    async def warn(self, ctx, member: discord.Member = None, current_channel_id=None,  *, reason=None):
        """
        Inserts the user to the infractions table and sends a warning message
        """
        mod_log_channel = self.bot.get_channel(MOD_LOGS)

        user_id, user_infractions = get_infractions(member.id)

        if reason:
            warn_message = discord.Embed(
                description=f"{member.mention} has been warned.\n**Reason:** " +
                str(reason)
            )
        else:
            warn_message = discord.Embed(
                description=f"{member.mention} has been warned."
            )

        if current_channel_id:
            replace_char = ['<', '>', '#']
            for i in replace_char:
                current_channel_id = current_channel_id.replace(i, '')

            current_channel_id = int(current_channel_id)
            current_channel = self.bot.get_channel(current_channel_id)

            if current_channel:
                await current_channel.send(embed=warn_message)

        moderator = ctx.author
        mod_log_warn_message = get_mod_log_warn_message(
            moderator, member, reason)

        # add infractions to database
        if user_infractions < 3:
            # add infractions to database
            manage_infractions(member.id, 1)
            await mod_log_channel.send(embed=mod_log_warn_message)
        else:

            timeout_mute = 30
            mod_log_mute_message = get_modlog_mute_msg(
                self.bot, member, moderator, timeout_mute, reason)
            role = discord.utils.get(member.guild.roles, name="Muted")
            infraction_message = f"{member.mention} has been muted."

            await member.add_roles(role)
            # insert into muted_users table
            manage_muted_users(member, timeout_mute, 1)
            await member.send(infraction_message)
            await mod_log_channel.send(embed=mod_log_mute_message)

    @command(aliases=['clean', 'clear'])
    @has_any_role("Mods", "Admin")
    async def purge(self, ctx, number):
        """
        Deletes messages from the channel
        """

        deleted = await ctx.channel.purge(limit=int(number))

        await ctx.channel.send('Deleted {} message(s)'.format(len(deleted)))
        await ctx.channel.purge(limit=1)


def setup(bot):
    bot.add_cog(Moderation(bot))
