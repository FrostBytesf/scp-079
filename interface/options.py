import os.path

from yaml import load, dump
from typing import (
    List,
    Any,
    Optional,
    Type
)

try:
    from yaml import CSafeLoader as Loader, CSafeDumper as Dumper
except ImportError:
    from yaml import SafeLoader as Loader, SafeDumper as Dumper


class Option:
    def __init__(self, name: str, default: Any, ttype: Type):
        self.__name: str = name
        self.__type: Type = ttype

        self.__default: Any = default
        self.__value: Optional[Any] = None

    @property
    def name(self) -> str:
        return self.__name

    @property
    def value_type(self) -> Type:
        return self.__type

    @property
    def default(self) -> Any:
        return self.__default

    def __get__(self, instance, owner) -> Any:
        # return the value when retrieved from an owner class
        return self.value

    def __set__(self, instance, value) -> None:
        raise AttributeError(self.name)

    @property
    def value(self) -> Any:
        if self.__value is None:
            return self.__value
        else:
            return self.__default

    def set_value(self, value: Any) -> None:
        self.__value = value


class OptionsError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message


class OptionsLoader:
    def __init__(self, filename: str) -> None:
        self.__filename: str = filename
        self.token: str = ""
        self.prefix: str = ""

        if not os.path.exists(self.__filename):
            open(self.__filename, "w").close()

    def read_to_object(self, obj: object):
        fields = obj.__dict__
        options = []

        for value in fields.values():
            if isinstance(value, Option):
                options.append(value)

        self.read_config(options)

    def read_config(self, fields: List[Option]) -> None:
        pure = True

        # get a scanner to read the yaml
        with open(self.__filename, "r+t") as file:
            options = load(file, Loader=Loader)

            if options is None:
                if len(fields) > 0:
                    pure = False
            else:
                for field in fields:
                    if field.name in options:
                        # get the type
                        if isinstance(options[field.name], field.value_type):
                            field.set_value(options[field.name])
                        else:
                            pure = False
                    else:
                        pure = False

        # check if there were any missing members
        if not pure:
            # write back to yaml
            with open(self.__filename, "wt") as file:
                dumper = Dumper(stream=file)

                try:
                    dumper.open()
                    for field in fields:
                        dumper.represent_scalar(field.name, field.value)
                    dumper.close()
                finally:
                    dumper.dispose()

            raise OptionsError('Config is missing some members! Fill them out and try again.')
