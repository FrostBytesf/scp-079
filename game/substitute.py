from typing import List, Optional
from praw import Reddit
from praw.models import Subreddit


class Substitute:
    def __init__(self,
                 client_id: str, client_secret: str,
                 username: str, password: str):
        self.__username: str = username
        self.__password: str = password

        self.__client_id: str = client_id
        self.__cliemt_secret: str = client_secret

        self.__reddit: Reddit = Reddit(user_agent='Substitute/v1.0.0',
                                       client_id=self.__client_id,
                                       client_secret=self.__cliemt_secret,
                                       username=self.__username,
                                       password=self.__password)

        self.__registered_subreddits: List[Subreddit] = []

    def get_subreddit(self, subreddit: str) -> Optional[Subreddit]:
        for sub in self.__registered_subreddits:
            if sub.display_name == subreddit:
                return sub

        return None

    def load_subreddit(self, subreddit: str) -> None:
        if self.get_subreddit(subreddit) is not None:
            return

        self.__registered_subreddits.append(self.__reddit.subreddit(subreddit))

    def load_all_subreddits(self, list: List[str]):
        for name in list:
            self.load_subreddit(name)
