from datetime import timedelta
from typing import Literal, Optional

from pydantic import BaseSettings, BaseModel, AnyUrl
import os
from dotenv import load_dotenv


load_dotenv()

class PGDSN(BaseModel):
    host: str = os.environ.get('PG_HOST', 'localhost')
    port: int = os.environ.get('PG_PORT', 5432)
    dbname: str = os.environ.get('PG_DB_NAME', 'db_users')
    user: str = os.environ.get('PG_USER', 'user')
    password: str = os.environ.get('PG_PASSWORD', '123qwe')


class RedisDSN(BaseModel):
    host: str = os.environ.get('REDIS_HOST', 'localhost')
    port: int = os.environ.get('REDIS_PORT', 6379)
    db: int = os.environ.get('REDIS_DB_INT', 0)
    password: str = os.environ.get('REDIS_PASSWORD', '')


class Settings(BaseSettings):
    PG: PGDSN = PGDSN()
    Redis: RedisDSN = RedisDSN()
    PG_CONNECT_STRING: AnyUrl = f'postgresql+psycopg2://{PG.user}:{PG.password}@0.0.0.0:{PG.port}/{PG.dbname}'
    ACCESS_TOKEN_TTL = timedelta(minutes=10)
    REFRESH_TOKEN_TTL = timedelta(days=30)

    # LOG_LEVEL: Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'] = 'INFO'
    class Config:
        env_file = 'dev.env'
        env_file_encoding = 'utf-8'
        env_nested_delimiter = '_'



'''docker run -d \
  --name flask-postgres \
  -p 5432:5432 \
  -v $HOME/postgresql/flask_data:/var/lib/postgresql/flask_volume_data \
  -e POSTGRES_PASSWORD=123qwe \
  -e POSTGRES_USER=user \
  -e POSTGRES_DB=db_users  \
  postgres:13 '''

'''
psql -h 127.0.0.1 -U user -d db_users
'''