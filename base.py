import discord
from discord.ext import commands

from data.general import DataManager
from interface.options import OptionsLoader


class BaseCog(commands.Cog):
    def __init__(self, bot: commands.Bot, options: OptionsLoader, data: DataManager):
        self.options: OptionsLoader = options
        self.data_manager: DataManager = data
        self.bot: commands.Bot = bot

    async def allowed_channel_check(self, ctx: commands.Context) -> bool:
        # get the server
        server_id = ctx.guild.id
        with self.data_manager.get_server(server_id) as server:
            # check if the channel_id is in the list
            return server.is_channel_in_allowed_channels(ctx.channel.id)

    async def programmer_access_check(self, ctx: commands.Context) -> bool:
        # check if the user owns the bot app
        if (await self.bot.application_info()).owner == ctx.author:
            return True

        # get the user
        user_id = ctx.author.id
        with self.data_manager.get_user(user_id) as user:
            # check if the user has the programmer badge
            return user.get_badges().programmer


def has_permissions(perms: discord.permissions.Permissions):
    async def predicate(ctx: commands.Context):
        return ctx.author.guild_permissions >= perms
    return commands.check(predicate)
