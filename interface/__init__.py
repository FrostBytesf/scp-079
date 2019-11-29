from interface.options import config_option, OptionsLoader
from discord.ext.commands import Bot, Context
from interface.base import BaseCog
from data.general import DataManager
from typing import Optional

class BotClient:
    def __init__(self, options: str):
        self.__options_file: str = options

        self.token: str = ''
        self.prefix: str = ''

        self.read_config(self.__options_file)

        self.__bot: Optional[Bot] = None

        self.init_bot()

        self.__database: DataManager = DataManager('data.db')

    @config_option
    def bot_token(self, token: str = '<token>'):
        self.token = token

    @config_option
    def bot_prefix(self, prefix: str = '<prefix>'):
        self.prefix = prefix

    def init_bot(self):
        if self.__bot is None:
            self.__bot = Bot(command_prefix=self.prefix)

            @self.__bot.check
            async def source_check(ctx: Context):
                return not (ctx.guild is None or ctx.author.bot)

            @self.__bot.event
            async def on_ready():
                print("logged into discord! user %s#%s" % (self.__bot.user.display_name, self.__bot.user.discriminator))

    def read_config(self, filename: str):
        loader = OptionsLoader(filename)

        loader.read_to_object(self)

    def with_cogs(self, *args: type):
        for t in args:
            if issubclass(t, BaseCog):
                self.__bot.add_cog(t(self.__bot, self.__database))

    def start(self):
        self.__bot.run(self.token)
