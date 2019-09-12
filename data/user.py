import sqlite3
from data import flags


class GlobalUser:
    def __init__(self, conn: sqlite3.Connection, id: int, desc: str, badges: int) -> None:
        self.conn: sqlite3.Connection = conn
        self.id: int = id
        self.desc: str = desc
        self.badges: int = badges

    def __enter__(self) -> 'GlobalUser':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # TODO: Make context management
        self.conn.commit()
        self.conn.close()

    # SETTERS

    def set_description(self, new_desc: str) -> None:
        self.desc = new_desc

        # update record
        self.conn.execute('UPDATE users SET description=? WHERE user_id=?', (self.desc, self.id))

    def set_badges(self, new_badges: flags.Badges) -> None:
        self.badges = new_badges.as_int()

        # update record
        self.conn.execute('UPDATE users SET badges=? WHERE user_id=?', (self.badges, self.id))

    # GETTERS

    def get_description(self) -> str:
        return self.desc

    def get_badges(self) -> flags.Badges:
        return flags.Badges(self.badges)

    def get_id(self) -> int:
        return self.id


class ServerUser(GlobalUser):
    def __init__(self, conn: sqlite3.Connection, id: int, desc: str, badges: int,
                 level: int, cur_exp: int, total_exp: int) -> None:
        super(ServerUser, self).__init__(conn, id, desc, badges)

        self.level: int = level
        self.cur_exp: int = cur_exp
        self.total_exp: int = total_exp