from abc import ABC
from abc import abstractmethod
from config.settings import Settings
import redis


SETTINGS = Settings()


class AbstractCacheStorage(ABC):
    @abstractmethod
    def get(self, key: str, **kwargs):
        pass

    @abstractmethod
    def set(self, key: str, value: str, expire: int, **kwargs):
        pass


class RedisStorage(AbstractCacheStorage):
    def __init__(self, conn: redis.Redis):
        self.redis = conn
    def get(self, key: str):
        return self.redis.get(key)

    def set(self, key, value, ex):
        self.redis.set(key, value, ex=ex)

def get_redis():
    return redis.Redis(**SETTINGS.Redis.dict(), decode_responses=True)
