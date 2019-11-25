import os.path
from inspect import signature, Parameter

from yaml import load
from typing import (
    List,
    Any,
    Callable,
    Optional,
    get_type_hints
)

try:
    from yaml import CSafeLoader as Loader, CSafeDumper as Dumper
except ImportError:
    from yaml import SafeLoader as Loader, SafeDumper as Dumper


class Option:
    def __init__(self, func: Callable):
        self.__func: Callable = func
        self.__name: str = func.__name__

    @property
    def name(self) -> str:
        return self.__name

    @property
    def func(self):
        return self.__func


def config_option(func) -> Option:
    return Option(func)


class OptionInstance:
    def __init__(self, option: Option, inst: Any):
        self.__option: Option = option
        self.__inst: Any = inst

        self.__value: Any = None

    @property
    def name(self):
        return self.__option.name

    @property
    def value(self):
        return self.__value

    def return_default(self):
        self.return_value(None)

    def return_value(self, value: Any):
        func = self.__option.func
        sig = signature(func)

        kwargs = {}

        for i, param in enumerate(sig.parameters.values()):
            if i == 0:
                if param.name == 'self':
                    kwargs[param.name] = self.__inst
                    continue

            default = None
            if param.default != Parameter.empty:
                default = param.default

            if value is None:
                value = default

            # stash value for later reference
            self.__value = value

            if param.annotation == Parameter.empty or param.annotation == type(value):
                kwargs[param.name] = value
                break

        func(**kwargs)


class OptionsError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message

    def __str__(self) -> str:
        return self.message


class OptionsLoader:
    def __init__(self, filename: str) -> None:
        self.__filename: str = filename

        if not os.path.exists(self.__filename):
            open(self.__filename, "w").close()

    def read_to_object(self, obj: object):
        fields = type(obj).__dict__
        options = []

        for value in fields.values():
            if isinstance(value, Option):
                options.append(OptionInstance(value, obj))

        self.read_config(options)

    def read_config(self, fields: List[OptionInstance]) -> None:
        pure = True

        # get a scanner to read the yaml
        with open(self.__filename, "r+t") as file:
            options = load(file, Loader=Loader)

            if len(fields) > 0:
                for field in fields:
                    if options is not None and field.name in options:
                        # get the type
                        field.return_value(options[field.name])
                    else:
                        field.return_default()
                        pure = False

        # check if there were any missing members
        if not pure:
            # write back to yaml
            with open(self.__filename, "w+t") as file:
                dumper = Dumper(stream=file)

                try:
                    dumper.open()

                    mapping = {field.name: field.value for field in fields}
                    dumper.serialize(dumper.represent_mapping(None, mapping))

                    dumper.close()
                finally:
                    dumper.dispose()

            raise OptionsError('Config is missing some members! Fill them out and try again.')
