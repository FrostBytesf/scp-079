from interface.options import config_option, OptionsLoader
from discord.ext.commands import Bot
from typing import Optional
from data.general import DataManager

import commands

class BotClient:
    def __init__(self, options: str):
        self.__options_file: str = options

        self.token: str = ''
        self.prefix: str = ''

        self.read_config(self.__options_file)

        self.__database: Optional[DataManager] = None
        self.__bot: Optional[Bot] = None

        self.init_data()
        self.init_bot()

    @config_option
    def bot_token(self, token: str = '<token>'):
        self.token = token

    @config_option
    def bot_prefix(self, prefix: str = '<prefix>'):
        self.prefix = prefix

    def init_data(self):
        if self.__database is None:
            self.__database = DataManager('data.db')

    def init_bot(self):
        if self.__bot is None:
            self.__bot = Bot(command_prefix=self.prefix)

            self.__bot.add_cog(commands.FunCog(self.__bot, self.__database))
            self.__bot.add_cog(commands.ManagementCog(self.__bot, self.__database))
            self.__bot.add_cog(commands.LevellingCog(self.__bot, self.__database))

            # self.__bot.add_cog(commands.InfoCog(self.__bot, self.__database))
            # self.__bot.add_cog(commands.AdministrationCog(self.__bot, self.__database))

            @self.__bot.event
            async def on_ready():
                print("logged into discord! user %s#%s" % (self.__bot.user.display_name, self.__bot.user.discriminator))

    def read_config(self, filename: str):
        loader = OptionsLoader(filename)

        loader.read_to_object(self)

    def start(self):
        self.__bot.run(self.token)
