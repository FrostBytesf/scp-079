import sqlite3
import server_data
from typing import (
    Optional
)


# CREATE TABLE servers (
#     server_id INT PRIMARY KEY,
#     allowed_channels TEXT NOT NULL,
#     flags INT NOT NULL
# )


class DataCreateError(Exception):
    def __init__(self, message: str) -> None:
        self.message: str = message


class DataManager:
    def __init__(self, file: str) -> None:
        self.filename: str = file

    def get_server(self, id: int) -> server_data.Server:
        # instantiate a connection
        conn = sqlite3.connect(self.filename)

        # try to get information
        server = conn.execute('SELECT * FROM servers WHERE server_id=?', (id,)).fetchone()

        if server is None:
            # we didn't find a server!
            return self.create_server(id, conn)
        else:
            # we did find a server! construct a server object out of it
            return server_data.Server(conn, server[0], server[1], server[2])

    def create_server(self, id: int, conn: Optional[sqlite3.Connection]) -> server_data.Server:
        # instantiate a connection if none is passed
        if conn is None:
            conn = sqlite3.connect(self.filename)

        allowed_channels = ""
        flags = 0

        # create the server
        conn.execute('INSERT INTO servers VALUES (?,?,?)', (id, allowed_channels, flags))
        return server_data.Server(conn, id, allowed_channels, flags)
