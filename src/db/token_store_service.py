import datetime
import time
from functools import lru_cache

import redis
from db.redis_base import AbstractCacheStorage
from db.redis_base import get_redis


class TokenStoreService:
    def __init__(self, storage: AbstractCacheStorage):
        self.storage = storage

    def add_to_blacklist(self, token: str, value: str = "True", expired: int = 600):
        self.storage.set(token, value=value, ex=datetime.timedelta(seconds=expired))

    def check_blacklist(self, token) -> str:
        return self.storage.get(token)

    def logout_all(self, email: str, iat=round(time.time()), expired: int = 2600000):
        self.storage.set(email, value=str(iat), ex=datetime.timedelta(seconds=int(expired)))

    def check_logout_email_date(self, email: str, iat) -> bool:
        '''returns False if token is blocked
            else -> True'''
        date = self.check_blacklist(email)
        if date and iat <= int(date):
            return True
        else:
            return False


@lru_cache()
def get_token_store_service(
        storage: redis.Redis = get_redis()
) -> TokenStoreService:
    return TokenStoreService(storage)
