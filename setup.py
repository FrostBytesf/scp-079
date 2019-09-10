import discord.ext.commands
import options
import data
import commands

from typing import (
    Optional
)

# read config
options = options.YamlOptions("config.yml")
options.read_config()

# read the database
data = data.DataManager("data.db")

# construct the bot
client = discord.ext.commands.Bot(command_prefix=options.prefix)

# cogs
client.add_cog(commands.InfoCog(client, options, data))
client.add_cog(commands.ManagementCog(client, options, data))


@client.event
async def on_ready():
    print("logged into discord! user %s#%s" % (client.user.display_name, client.user.discriminator))

client.run(options.token)
