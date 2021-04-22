from datetime import datetime

import discord
from discord.ext.commands import Cog
from discord.ext.commands import command
from dotenv import load_dotenv
import os

load_dotenv()
SERVER_LOG = int(os.getenv("SERVER_LOG"))
MESSAGE_LOG = int(os.getenv("MESSAGE_LOG"))
MEMBER_LOG = int(os.getenv("MEMBER_LOG"))
VOICE_LOG = int(os.getenv("VOICE_LOG"))
JOIN_LEAVE_LOG = int(os.getenv("JOIN_LEAVE_LOG"))


class Logs(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        self.server_log_channel = self.bot.get_channel(SERVER_LOG)
        self.message_log_channel = self.bot.get_channel(MESSAGE_LOG)
        self.member_log_channel = self.bot.get_channel(MEMBER_LOG)
        self.voice_log_channel = self.bot.get_channel(VOICE_LOG)
        self.join_leave_log_channel = self.bot.get_channel(JOIN_LEAVE_LOG)

    @Cog.listener()
    async def on_user_update(self, before, after):
        if before.name != after.name:

            embed = discord.Embed(
                title="Username Update",
                description=f"**Before:** {before.name}\n**After:** {after.name}",
                colour=discord.Colour(0xF23E3),
                timestamp=datetime.utcnow()
            )

            embed.set_author(
                name=after.author,
                icon_url=after.author.avatar_url
            )
            embed.set_footer(text=f"ID: {after.author.id}")

            await self.member_log_channel.send(embed=embed)

        if before.avatar_url != after.avatar_url:
            embed = discord.Embed(title="Avatar Update",
                                  colour=discord.Colour(0xF23E3),
                                  timestamp=datetime.utcnow())

            embed.set_author(
                name=after,
                icon_url=after.avatar_url
            )
            embed.set_thumbnail(url=after.avatar_url)

            await self.member_log_channel.send(embed=embed)

    @Cog.listener()
    async def on_member_update(self, before, after):
        if before.display_name != after.display_name:

            embed = discord.Embed(
                title="Nickname Update",
                description=f"**Before:** {before.display_name}\n**After:** {after.display_name}",
                colour=discord.Colour(0xF23E3),
                timestamp=datetime.utcnow()
            )

            embed.set_author(
                name=after,
                icon_url=after.avatar_url
            )
            embed.set_footer(text=f"ID: {after.id}")

            await self.member_log_channel.send(embed=embed)

    @Cog.listener()
    async def on_message_edit(self, before, after):
        if not after.author.bot:  # if author is not bot

            if before.content != after.content:
                embed = discord.Embed(
                    title=f"Message edited in #{before.channel}",
                    description=f"**Before:** {before.content}\n**After:** {after.content}",
                    colour=discord.Colour(0x118ceb),
                    timestamp=datetime.utcnow()
                )

                embed.set_author(
                    name=after,
                    icon_url=after.avatar_url
                )
                embed.set_footer(text=f"ID: {after.id}")

                await self.message_log_channel.send(embed=embed)

    @Cog.listener()
    async def on_message_delete(self, message):
        if not message.author.bot:

            embed = discord.Embed(
                title=f"Message deleted in #{message.channel}",
                description=f"**Message:** {message.content}",
                colour=discord.Colour(0x118ceb),
                timestamp=datetime.utcnow()
            )

            embed.set_author(
                name=message.author,
                icon_url=message.author.avatar_url
            )
            embed.set_footer(text=f"ID: {message.author.id}")

            await self.message_log_channel.send(embed=embed)

    @Cog.listener()
    async def on_voice_state_update(self, member, before, after):

        if not before.channel and after.channel:  # user joined voice channel

            embed = discord.Embed(
                title="Member joined voice channel",
                description=f"**{member}** joined #{after.channel}",
                colour=discord.Colour(0xfe64e),
                timestamp=datetime.utcnow()

            )
            embed.set_author(
                name=member,
                icon_url=member.avatar_url
            )
            embed.set_footer(text=f"ID: {member.id}")

        elif before.channel and not after.channel:  # user left voice channel

            embed = discord.Embed(
                title="Member left voice channel",
                description=f"**{member}** left #{before.channel}",
                colour=discord.Colour(0xf60000),
                timestamp=datetime.utcnow()
            )
            embed.set_author(
                name=member,
                icon_url=member.avatar_url
            )
            embed.set_footer(text=f"ID: {member.id}")

        await self.voice_log_channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Logs(bot))
