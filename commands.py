import discord
import datetime
from discord.ext import commands

from base import (
    BaseCog,
    has_permissions
)

from typing import (
    Optional
)

from data.server import *


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
        except EntryExistsInListError:
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
        except EntryNotInListError:
            await channel.send('This channel is not accepting bot commands!')
            return

        # send confirmation message
        await channel.send('This channel is no longer accepting bot commands!!')

    @commands.group(name='roles')
    async def roles_command(self, ctx: commands.Context):
        pass

    @roles_command.command(name='add')
    async def roles_add_command(self, ctx: commands.Context, role: discord.Role):
        # do check
        if not await self.allowed_channel_check(ctx):
            return

        # try to add the command
        try:
            with self.data_manager.get_server(ctx.guild.id) as server:
                server.add_self_roles(role.id)
        except EntryExistsInListError:
            await ctx.send('The role %s is already a self role!' % role.name)

        # send confirmation message
        await ctx.send('The role %s is now a self role!' % role.name)

    @roles_command.command(name='remove')
    async def roles_remove_command(self, ctx: commands.Context, role: discord.Role):
        # do check
        if not await self.allowed_channel_check(ctx):
            return

        # try to remove the command
        try:
            with self.data_manager.get_server(ctx.guild.id) as server:
                server.remove_self_roles(role.id)
        except EntryNotInListError:
            await ctx.send('The role %s is not already a self role!' % role.name)

        # send confirmation message
        await ctx.send('The role %s is no longer a self role!' % role.name)

    @roles_command.command(name='join')
    async def roles_join_command(self, ctx: commands.Context, role: discord.Role):
        # do check
        if not await self.allowed_channel_check(ctx):
            return

        with self.data_manager.get_server(ctx.guild.id) as server:
            for role_id in server.get_self_roles():
                other_role = ctx.guild.get_role(role_id)

                if other_role is None:
                    # remove non-existent role
                    server.remove_self_roles(role_id)
                else:
                    # check if they are the same
                    if other_role == role:
                        # if so, then grant the role
                        try:
                            await ctx.author.add_roles(other_role.id, 'Self role.')
                        except discord.Forbidden:
                            await ctx.send('I do not have sufficient permission.')


class LevellingCog(BaseCog):
    BAR_LENGTH = 20
    BAR_CHAR = '='
    EMPTY_BAR_CHAR = '-'

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # prepare to update levelling
        with self.data_manager.get_server_user(message.guild.id, message.author.id) as user:
            if user.check_cooldown():
                # award exp
                if user.award_exp():
                    # if we have levelled up
                    print(f'{str(message.author)} has levelled up to {user.get_level()} yes')

    @commands.command(name='level')
    async def level_command(self, ctx: commands.Context, user: Optional[discord.User]) -> None:
        # fill in user if none
        if user is None:
            user = ctx.author

        # get user info
        with self.data_manager.get_server_user(ctx.guild.id, ctx.author.id) as data_user:
            # build an embed and send it
            embed = discord.Embed(title='level info for %s' % str(user), timestamp=datetime.datetime.now(),
                                  colour=discord.Colour.blue())

            # get a factor for bar length
            this_level_exp = data_user.calculate_exp(data_user.get_level())
            next_level_exp = data_user.calculate_exp(data_user.get_level() + 1)
            factor = float(data_user.get_total_exp() - this_level_exp) / float(next_level_exp - this_level_exp)

            length_factor = int(factor * self.BAR_LENGTH)

            embed.description = '```lvl %s [%s] lvl %s```' % (data_user.get_level(),
                                                              (self.BAR_CHAR * length_factor) +
                                                              (self.EMPTY_BAR_CHAR * (self.BAR_LENGTH - length_factor)),
                                                              data_user.get_level() + 1)

            embed.add_field(name='leveldata', value='%s total exp\n%s exp required' %
                                                    (data_user.get_total_exp(), next_level_exp))

            embed.set_footer(text='requested by %s' % str(ctx.author), icon_url=ctx.author.avatar_url_as())

            await ctx.send(embed=embed)


class AdministrationCog(BaseCog):
    @commands.command(name='grant')
    async def grant_command(self, ctx: commands.Context, user: discord.User):
        if not await self.programmer_access_check(ctx):
            await ctx.send('The `grant` command is reserved for administrators only!')
            return

        # parse the grant
