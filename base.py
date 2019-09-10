import discord
from discord.ext import commands

from data import DataManager
from options import YamlOptions


class BaseCog(commands.Cog):
    def __init__(self, bot: commands.Bot, options: YamlOptions, data: DataManager):
        self.options: YamlOptions = options
        self.data_manager: DataManager = data
        self.bot: commands.Bot = bot

    async def allowed_channel_check(self, ctx: commands.Context) -> bool:
        # check if we are in dms or the user is a bot
        general_check = ctx.guild is None or ctx.author.bot
        if general_check:
            return False

        # get the server
        server_id = ctx.guild.id
        with self.data_manager.get_server(server_id) as server:
            # check if the channel_id is in the list
            return server.is_channel_in_allowed_channels(ctx.channel.id)


def has_permissions(perms: discord.permissions.Permissions):
    print(perms.__class__.__name__)

    async def predicate(ctx: commands.Context):
        return ctx.author.guild_permissions >= perms
    return commands.check(predicate)
