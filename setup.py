import discord.ext.commands
import options
import data.general
import commands

# read config
options = options.YamlOptions("config.yml")
options.read_config()

# read the database
data = data.general.DataManager("data.db")

# construct the bot
client = discord.ext.commands.Bot(command_prefix=options.prefix)

# cogs
client.add_cog(commands.InfoCog(client, options, data))
client.add_cog(commands.ManagementCog(client, options, data))

# add a check
@client.check
async def source_check(ctx: discord.ext.commands.Context):
    return not (ctx.guild is None or ctx.author.bot)


@client.event
async def on_ready():
    print("logged into discord! user %s#%s" % (client.user.display_name, client.user.discriminator))

client.run(options.token)
