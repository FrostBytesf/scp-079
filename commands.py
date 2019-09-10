import discord
from discord.ext import commands

import server_data
from base import (
    BaseCog,
    has_permissions
)

from typing import (
    Optional
)


class InfoCog(BaseCog):
    @commands.command(name='echo')
    async def echo_command(self, ctx: commands.Context, *, text: Optional[str]):
        # do check
        if not await self.allowed_channel_check(ctx):
            return

        if text is None:
            text = 'Pong! `%sms`' % round(self.bot.latency * 1000)

        await ctx.send(text)


class ManagementCog(BaseCog):
    @commands.command(name='allow')
    @has_permissions(discord.Permissions(0b100000))
    async def allow_command(self, ctx: commands.Context, channel: Optional[discord.TextChannel]):
        if channel is None:
            channel = ctx.channel

        # add allowed channel
        try:
            with self.data_manager.get_server(ctx.guild.id) as server:
                server.add_allowed_channel(channel.id)
        except server_data.ChannelExistsInListError:
            await channel.send('This channel is already accepting bot commands!')
            return

        # send confirmation message
        await channel.send('This channel may now accept bot commands!')

    @commands.command(name='disallow')
    @has_permissions(discord.Permissions(0b100000))
    async def disallow_commmand(self, ctx: commands.Context, channel: Optional[discord.TextChannel]):
        if channel is None:
            channel = ctx.channel

        # remove allowed channel
        try:
            with self.data_manager.get_server(ctx.guild.id) as server:
                server.remove_allowed_channel(channel.id)
        except server_data.ChannelNotInListError:
            await channel.send('This channel is not accepting bot commands!')
            return

        # send confirmation message
        await channel.send('This channel is no longer accepting bot commands!!')

