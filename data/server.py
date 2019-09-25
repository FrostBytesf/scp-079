import sqlite3
from data import user
from typing import (
    List,
    Optional
)


class ListAccessError(Exception):
    pass


class EntryExistsInListError(ListAccessError):
    pass


class EntryNotInListError(ListAccessError):
    pass


# CREATE TABLE servers (
#   server_id INTEGER PRIMARY KEY,
#   allowed_channels TEXT NOT NULL,
#   self_roles TEXT NOT NULL,
#   auto_role INTEGER NOT NULL,
#   flags INTEGER NOT NULL
# )


class Server(object):
    def __init__(self, c: sqlite3.Connection, id: int, ac: str, sr: str, auto_role: int, flags: int) -> None:
        self.conn: sqlite3.Connection = c
        self.id: int = id
        self.flags: int = flags
        self.auto_role: int = auto_role

        # transform the allowed channels into a list of channels
        channels = []
        if ac:
            for channel in ac.split(','):
                try:
                    channels.append(int(channel))
                except ValueError:
                    print('Malformed channel! Skipping.')

        self.allowed_channels: List[int] = channels

        # transform the self roles into a list of roles
        self_roles = []
        if sr:
            for role in sr.split(','):
                try:
                    self_roles.append(int(role))
                except ValueError:
                    print('Malformed role! Skipping.')

        self.self_roles: List[int] = self_roles

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

    def _update_self_roles(self) -> None:
        # serialize the list
        list_repr = ','.join(str(role) for role in self.self_roles)

        # update the record
        self.conn.execute('UPDATE servers SET self_roles=? WHERE server_id=?', (list_repr, self.id))

    # SETTERS

    def add_allowed_channel(self, channel_id: int) -> None:
        # check if channel already exists
        if any(c == channel_id for c in self.allowed_channels):
            raise EntryExistsInListError()

        # update the allowed channels
        self.allowed_channels.append(channel_id)

        # update sql
        self._update_allowed_channels()

    def remove_allowed_channel(self, channel_id: int) -> None:
        # update the allowed channels
        try:
            self.allowed_channels.remove(channel_id)
        except ValueError:
            raise EntryNotInListError()

        # update sql
        self._update_allowed_channels()

    def add_self_roles(self, role_id: int) -> None:
        # check if role already exists
        if any(r == role_id for r in self.self_roles):
            raise EntryExistsInListError()

        # update the self roles list
        self.self_roles.append(role_id)

        # update sql
        self._update_self_roles()

    def remove_self_roles(self, role_id: int) -> None:
        # update the self roles list
        try:
            self.self_roles.remove(role_id)
        except ValueError:
            raise EntryNotInListError()

        # update sql
        self._update_self_roles()

    def set_auto_role(self, role_id: int) -> None:
        # update the auto role id
        self.auto_role = role_id

        # update sql
        self.conn.execute('UPDATE servers SET auto_role=? WHERE server_id=?', (self.flags, self.id))

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

    def get_self_roles(self) -> List[int]:
        return self.self_roles

    def get_auto_role(self) -> int:
        return self.auto_role

    def get_flags(self) -> int:
        return self.flags
