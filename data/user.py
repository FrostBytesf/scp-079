import sqlite3
import random
import time
from data import (
    flags,
    general
)


# CREATE TABLE users (
#   user_id INTEGER PRIMARY KEY,
#   description TEXT NOT NULL,
#   badges INTEGER NOT NULL
# )

# CREATE TABLE exp (
#   serial TEXT PRIMARY KEY,
#   level INTEGER NOT NULL,
#   total_exp INTEGER NOT NULL,
#   cooldown INTEGER NOT NULL
# )


class GlobalUser:
    def __init__(self, conn: sqlite3.Connection, id: int, desc: str, badges: int) -> None:
        self.conn: sqlite3.Connection = conn
        self.id: int = id
        self.desc: str = desc
        self.badges: flags.Badges = flags.Badges(badges)

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
        self.badges = new_badges

        # update record
        self.conn.execute('UPDATE users SET badges=? WHERE user_id=?', (self.badges.as_int(), self.id))

    # GETTERS

    def get_description(self) -> str:
        return self.desc

    def get_badges(self) -> flags.Badges:
        return self.badges

    def get_id(self) -> int:
        return self.id


class ServerUser(GlobalUser):
    COOLDOWN_TIME = 30

    def __init__(self, conn: sqlite3.Connection, id: int, desc: str, badges: int,
                 server_id: int, level: int, total_exp: int, cooldown: int) -> None:
        super(ServerUser, self).__init__(conn, id, desc, badges)

        self.server_id: int = server_id

        self.level: int = level
        self.total_exp: int = total_exp
        self.cooldown: int = cooldown

    def __enter__(self) -> 'ServerUser':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # TODO: Make context management
        self.conn.commit()
        self.conn.close()

    # SERIAL HELPERS
    @property
    def serial(self) -> str:
        return general.DataManager.get_serial(self.id, self.server_id)

    # LEVEL HELPERS

    @staticmethod
    def calculate_exp(level: int) -> int:
        if level < 1:
            return 0

        return 64 * level ** 2 + 25

    @staticmethod
    def __get_random_exp() -> int:
        return random.randint(10, 15)

    # SETTERS

    def set_level(self, level: int) -> None:
        self.level = level

        # update record
        self.conn.execute('UPDATE exp SET level=? WHERE serial=?', (self.level, self.serial))

    def set_total_exp(self, total_exp: int) -> None:
        self.total_exp = total_exp

        # update record
        self.conn.execute('UPDATE exp SET total_exp=? WHERE serial=?', (self.total_exp, self.serial))

    def award_exp(self) -> bool:
        self.set_total_exp(self.total_exp + self.__get_random_exp())

        # if the user is past the required exp, then level the user up!
        if self.total_exp > self.calculate_exp(self.level + 1):
            self.set_level(self.level + 1)
            return True
        else:
            return False

    def check_cooldown(self) -> bool:
        if time.time() > self.cooldown:
            # cooldown over.
            self.cooldown = int(time.time()) + self.COOLDOWN_TIME

            # update record
            self.conn.execute('UPDATE exp SET cooldown=? WHERE serial=?', (self.cooldown, self.serial))
            return True
        else:
            return False

    # GETTERS

    def get_level(self) -> int:
        return self.level

    def get_total_exp(self) -> int:
        return self.total_exp
