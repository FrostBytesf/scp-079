import discord
import datetime
import game
from discord.ext import commands
from io import StringIO

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


class FunCog(BaseCog):
    IGNORE_SYMBOLS = [',', '\'', '.', '?', '.', '-']

    @commands.command(name='wordmap')
    async def wordmap_command(self, ctx: commands.Context, channel: discord.TextChannel):
        try:
            wordmap_list = game.Wordmap()

            async for message in channel.history(limit=1000):
                words = message.clean_content.split(' ')

                for word in words:
                    english = True
                    clean_word = ''

                    for letter in word:
                        if letter.isalpha():
                            clean_word += letter.lower()
                        elif any(letter == x for x in self.IGNORE_SYMBOLS):
                            continue
                        else:
                            english = False
                            break

                    if english and not clean_word.strip() == '':
                        wordmap_list.inc_word(clean_word)

            top_words = wordmap_list.get_words(100)
            await ctx.send('```\n' + ' '.join(str(word) for word in top_words) + '\n```')
        except discord.Forbidden:
            await ctx.send('I have no access to the channel!')


class ManagementCog(BaseCog):
    LIST_SEPARATOR = ',\n'

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        with self.data_manager.get_server(member.guild.id) as server:
            role_id = server.get_auto_role()

            if role_id > 0:
                # get the role
                role = member.guild.get_role(role_id)

                if role is None:
                    server.set_auto_role(0)
                else:
                    await member.add_roles(role)

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

    @commands.group(name='roles', invoke_without_command=True)
    async def roles_command(self, ctx: commands.Context):
        # do check
        if not await self.allowed_channel_check(ctx):
            return

        with self.data_manager.get_server(ctx.guild.id) as server:
            embed = discord.Embed(title='role info for %s' % ctx.guild.name, timestamp=datetime.datetime.now(),
                                  colour=discord.Colour.blue())

            embed.description = 'use the .roles add, .roles remove to add roles to the selfrole join system.\n' \
                                'the levelroles feature also exist, use .roles levelroles'

            auto_role = ctx.guild.get_role(server.get_auto_role())
            if auto_role is not None:
                embed.add_field(name='AUTOROLE', value=auto_role.name)

            sr_description = ''
            for self_role_id in server.get_self_roles():
                self_role = ctx.guild.get_role(self_role_id)
                if self_role is not None:
                    sr_description += self_role.name + self.LIST_SEPARATOR

            sr_description.strip(self.LIST_SEPARATOR)
            if len(sr_description) > 0:
                embed.add_field(name='SELFROLES', value=sr_description)

            embed.set_footer(text='management command', icon_url=ctx.guild.icon_url_as())

            await ctx.send(embed=embed)

    @roles_command.command(name='autorole')
    @has_permissions(discord.Permissions(0b100000))
    async def roles_autorole_command(self, ctx: commands.Context, role: Optional[discord.Role]):
        # do check
        if not await self.allowed_channel_check(ctx):
            return

        with self.data_manager.get_server(ctx.guild.id) as server:
            if role is None:
                # clear the role
                server.set_auto_role(0)
                await ctx.send('Auto role has been cleared!')
            else:
                # set the role
                server.set_auto_role(role.id)
                await ctx.send('Auto role has been set to %s!' % role.name)

    @roles_command.command(name='add')
    @has_permissions(discord.Permissions(0b100000))
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
    @has_permissions(discord.Permissions(0b100000))
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
                            await ctx.author.add_roles(other_role, reason='Self role.')
                            await ctx.send('Given role %s to user %s!' % (other_role.name, str(ctx.author)))
                        except discord.Forbidden:
                            await ctx.send('I do not have sufficient permission.')

    @roles_command.group(name='levelroles')
    async def roles_levelroles_command(self, ctx: commands.Context):
        pass

    @roles_levelroles_command.command(name='add')
    @has_permissions(discord.Permissions(0b100000))
    async def roles_levelroles_add_command(self, ctx: commands.Context, role: discord.Role, levels: commands.Greedy[int]):
        # do check
        if not await self.allowed_channel_check(ctx):
            return

        with self.data_manager.get_server(ctx.guild.id) as server:
            try:
                server.add_level_roles(role.id, levels)

                await ctx.send('The role %s has been given a level rule!' % role.name)
            except EntryExistsInListError:
                await ctx.send('The role %s has level rules set! Delete them to re-set them!' % role.name)

    @roles_levelroles_command.command(name='remove')
    @has_permissions(discord.Permissions(0b100000))
    async def roles_levelroles_remove_command(self, ctx: commands.Context, role: discord.Role):
        # do check
        if not await self.allowed_channel_check(ctx):
            return

        with self.data_manager.get_server(ctx.guild.id) as server:
            try:
                server.remove_level_roles(role.id)

                await ctx.send('Level rule removed!')
            except EntryNotInListError:
                await ctx.send('That role does not have any level rules set!')


class LevellingCog(BaseCog):
    BAR_LENGTH = 20
    BAR_CHAR = '='
    EMPTY_BAR_CHAR = '-'

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # prepare to update levelling
        level_up = False
        with self.data_manager.get_server_user(message.guild.id, message.author.id) as user:
            if user.check_cooldown():
                # award exp
                if user.award_exp():
                    # if we have levelled up
                    level_up = True
                    print(f'{str(message.author)} has levelled up to {user.get_level()} yes')

        # award any levelling roles if we have levelled up
        if level_up:
            with self.data_manager.get_server(message.guild.id) as server:
                roles = server.get_level_roles_at(user.get_level())
                given_roles = []

                for role in roles:
                    given_role = message.guild.get_role(role)

                    if given_role is not None:
                        given_roles.append(given_role)
                    else:
                        server.remove_level_roles(role)

                # award roles
                if len(given_roles) > 0:
                    await message.author.add_roles(*given_roles, reason='Level roles')

    @commands.command(name='level')
    async def level_command(self, ctx: commands.Context, user: Optional[discord.User]) -> None:
        # do check
        if not await self.allowed_channel_check(ctx):
            return

        # fill in user if none
        if user is None:
            user = ctx.author

        # get user info
        with self.data_manager.get_server_user(ctx.guild.id, user.id) as data_user:
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
