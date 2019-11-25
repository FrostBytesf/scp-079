from interface.options import Option, OptionsLoader
from discord.ext.commands import Bot
from typing import Optional

class BotClient:
    def __init__(self, options: str):
        self.__options_file: str = options

        self.token: Option = Option('token', '<token>', str)
        self.prefix: Option = Option('prefix', '<prefix>', str)

        self.read_config(self.__options_file)

        self.__bot: Optional[Bot] = None

        self.init_bot()

    def init_bot(self):
        print(self.prefix.__get__(self, BotClient))

        if self.__bot is None:
            self.__bot = Bot(command_prefix=self.prefix)

    def read_config(self, filename: str):
        loader = OptionsLoader(filename)

        loader.read_to_object(self)

    def start(self):
        token = self.token
        self.__bot.run(token)
