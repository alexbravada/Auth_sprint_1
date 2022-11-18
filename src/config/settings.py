from datetime import timedelta

from pydantic import BaseSettings, BaseModel, AnyUrl
import os
from dotenv import load_dotenv

load_dotenv()


class PGDSN(BaseModel):
    host: str = os.environ.get('PG_HOST')
    port: int = int(os.environ.get('PG_PORT'))
    dbname: str = os.environ.get('POSTGRES_DB')
    user: str = os.environ.get('POSTGRES_USER')
    password: str = os.environ.get('POSTGRES_PASSWORD')


class RedisDSN(BaseModel):
    host: str = os.environ.get('REDIS_HOST')
    port: int = int(os.environ.get('REDIS_PORT'))
    db: int = int(os.environ.get('REDIS_DB_INT'))
    password: str = os.environ.get('REDIS_PASSWORD')


class Settings(BaseSettings):
    PG: PGDSN = PGDSN()
    Redis: RedisDSN = RedisDSN()
    PG_CONNECT_STRING: AnyUrl = f'postgresql+psycopg2://{PG.user}:{PG.password}@{PG.host}:{PG.port}/{PG.dbname}'
    ACCESS_TOKEN_TTL = timedelta(minutes=10)
    REFRESH_TOKEN_TTL = timedelta(days=30)