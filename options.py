import os.path

from yaml import *
from typing import (
    List
)


class OptionsError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message


class YamlOptions:
    def __init__(self, filename: str) -> None:
        self.filename: str = filename
        self.token: str = ""
        self.prefix: str = ""

        if not os.path.exists(self.filename):
            open(self.filename, "w").close()

    def read_config(self) -> None:
        pure = True

        # get a scanner to read the yaml
        with open(self.filename, "r+t") as file:
            options = load(file, Loader=CLoader)

            if options is None:
                print("Please fill in the configuration file!")
                exit(1)

            if "token" not in options:
                pure = False
                options["token"] = "<bot token here>"
            else:
                self.token = options["token"]

            if "prefix" not in options:
                pure = False
                options["prefix"] = "<cmd prefix>"
            else:
                self.prefix = options["prefix"]

        # check if there were any missing members
        if not pure:
            # write back to yaml
            with open(self.filename, "w+t") as file:
                dump(options, file, Dumper=CDumper)

            print("Config is missing some members! Fill them out and try again.")
            exit(1)
        else:
            print("Read config!")
