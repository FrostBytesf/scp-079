import sqlite3
from data import (
    server,
    user
)

from typing import (
    Optional
)


class DataManager(object):
    SERVER_FLAGS = 0

    def __init__(self, db: str):
        self.filename = db

    # HELPERS

    def __assure_exp_table(self, server_id: int, conn: sqlite3.Connection) -> None:
        # execute a quick statement
        result = conn.execute('SELECT name FROM sqlite_master WHERE type=? AND name=?',
                              ('table', 'server_' + str(server_id)))

        if result.fetchone() is None:
            # exp table doesn't exist, create it
            conn.execute("""
            CREATE TABLE server_%s (
                user_id INTEGER PRIMARY KEY,
                level INTEGER NOT NULL,
                total_exp INTEGER NOT NULL,
                cooldown INTEGER NOT NULL
            )
            """ % server_id)

    # ACCESSORS

    def get_server(self, id: int) -> server.Server:
        # get a connection
        conn = sqlite3.Connection(self.filename)

        # try to get the server
        serv = conn.execute('SELECT * FROM servers WHERE server_id=?', (id,)).fetchone()

        if serv is None:
            # create new server instance
            return self.create_server(id, conn)
        else:
            # found the server!
            return server.Server(conn, serv[0], serv[1], serv[2], serv[3], serv[4])

    def create_server(self, id: int, conn: Optional[sqlite3.Connection]) -> server.Server:
        # get a connection if none has been passed
        if conn is None:
            conn = sqlite3.Connection(self.filename)

        # try to create a server object
        # use defaults
        allowed_channels = ''
        self_roles = ''
        auto_role = 0
        flags = self.SERVER_FLAGS

        # add the entry
        conn.execute('INSERT INTO servers VALUES (?,?,?,?,?)', (id, allowed_channels, self_roles, auto_role, flags))

        # return a representation
        return server.Server(conn, id, allowed_channels, self_roles, auto_role, flags)

    def get_server_user(self, server_id: int, user_id: int) -> user.ServerUser:
        # try to find the user
        # get a new connection
        conn = sqlite3.Connection('data.db')  # MAGIC VALUE

        # make sure the table exists
        self.__assure_exp_table(server_id, conn)

        # find the user
        u = conn.execute(f'SELECT * FROM server_{server_id} WHERE user_id=?', (user_id,)).fetchone()
        if u is None:
            # user does not exist! create a new user
            return self.create_server_user(server_id, user_id, conn)
        else:
            # create a new user object!
            # warning! this is a hotfix, and should be changed immediately.
            return user.ServerUser(conn, u[0], 'not implemented', 0, server_id, u[1], u[2], u[3])

    def create_server_user(self, server_id: int, user_id: int, conn: Optional[sqlite3.Connection]) -> user.ServerUser:
        if conn is None:
            conn = sqlite3.Connection('data.db')  # MAGIC VALUE

            # make sure the table exists
            self.__assure_exp_table(server_id, conn)

        # set some variables
        level = 0
        total_exp = 0
        cooldown = 0

        # create the user
        conn.execute(f'INSERT INTO server_{server_id} VALUES (?,?,?,?)', (user_id, level, total_exp, cooldown))

        # return a representation
        # warning! this is a hotfix, and should be changed immediately.
        return user.ServerUser(conn, user_id, 'not implemented', 0, server_id, level, total_exp, cooldown)
