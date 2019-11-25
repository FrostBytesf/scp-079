from interface.options import config_option, OptionsLoader
from discord.ext.commands import Bot
from typing import Optional

class BotClient:
    def __init__(self, options: str):
        self.__options_file: str = options

        self.token: str = ''
        self.prefix: str = ''

        self.read_config(self.__options_file)

        self.__bot: Optional[Bot] = None

        self.init_bot()

    @config_option
    def bot_token(self, token: str = '<token>'):
        self.token = token

    @config_option
    def bot_prefix(self, prefix: str = '<prefix>'):
        self.prefix = prefix

    def init_bot(self):
        if self.__bot is None:
            self.__bot = Bot(command_prefix=self.prefix)

    def read_config(self, filename: str):
        loader = OptionsLoader(filename)

        loader.read_to_object(self)

    def start(self):
        self.__bot.run(self.token)
