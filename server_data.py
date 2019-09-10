import sqlite3
from typing import (
    List
)


class ChannelExistsInListError(Exception):
    pass


class ChannelNotInListError(Exception):
    pass


class Server(object):
    def __init__(self, c: sqlite3.Connection, id: int, ac: str, flags: int) -> None:
        self.conn: sqlite3.Connection = c
        self.id: int = id
        self.flags: int = flags

        # transform the allowed channels into a list of channels
        channels = []
        if ac:
            for channel in ac.split(','):
                try:
                    channels.append(int(channel))
                except ValueError:
                    print('Malformed channel! Skipping.')

        self.allowed_channels: List[int] = channels

    def __enter__(self) -> 'Server':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        # TODO: Make context management
        self.conn.commit()
        self.conn.close()

    # HELPERS

    def _update_allowed_channels(self) -> None:
        # serialize the list
        list_repr = ','.join(str(chnl_id) for chnl_id in self.allowed_channels)

        # update the record
        self.conn.execute('UPDATE servers SET allowed_channels=? WHERE server_id=?', (list_repr, self.id))

    # SETTERS

    def add_allowed_channel(self, channel_id: int) -> None:
        # check if channel already exists
        if any(c == channel_id for c in self.allowed_channels):
            raise ChannelExistsInListError()

        # update the allowed channels
        self.allowed_channels.append(channel_id)

        # update sql
        self._update_allowed_channels()

    def remove_allowed_channel(self, channel_id: int) -> None:
        # update the allowed channels
        try:
            self.allowed_channels.remove(channel_id)
        except ValueError:
            raise ChannelNotInListError()

        # update sql
        self._update_allowed_channels()

    # FLAGS ARE STORED BINARY FLAGS
    # so, the binary number 0010 would be stored as 2, and would have flags for certain values
    def set_flags(self, flags: int):
        # update the flags value
        self.flags = flags

        # update sql
        self.conn.execute('UPDATE servers SET flags=? WHERE server_id=?', (self.flags, self.id))

    # GETTERS
    def is_channel_in_allowed_channels(self, id: int) -> bool:
        return any(c == id for c in self.allowed_channels)

    def get_allowed_channels(self) -> List[int]:
        return self.allowed_channels

    def get_flags(self) -> int:
        return self.flags
