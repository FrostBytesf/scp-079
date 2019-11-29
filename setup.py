from interface import BotClient
from interface.options import OptionsError
from commands import *

# add a check
# @client.check
# async def source_check(ctx: discord.ext.commands.Context):
#     return not (ctx.guild is None or ctx.author.bot)
#
#
# @client.event
# async def on_ready():
#     print("logged into discord! user %s#%s" % (client.user.display_name, client.user.discriminator))

# create a new bot

try:
    bot = BotClient('config.yml')
    bot.with_cogs(
        ManagementCog,
        LevellingCog,
        FunCog
    )

    bot.start()
except OptionsError as err:
    print(err.message)
    print('Maybe you have not filled in some fields?')
    exit(1)