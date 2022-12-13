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


class Jaeger(BaseModel):
    host: str = os.environ.get('JAEGER_HOSTNAME')
    port: int = int(os.environ.get('JAEGER_PORT'))


class OAuthCredVK(BaseModel):
    id: str = os.environ.get('VK_OAUTH_ID')
    secret: str = os.environ.get('VK_OAUTH_SECRET')
    service_key: str = os.environ.get('VK_OAUTH_SERVICE_KEY')

class OAuthCredYandex(BaseModel):
    id: str = os.environ.get('Yandex_OAUTH_ClientID')
    secret: str = os.environ.get('Yandex_OAUTH_ClientSecret')


class Settings(BaseSettings):
    PG: PGDSN = PGDSN()
    Redis: RedisDSN = RedisDSN()
    Jaeger: Jaeger = Jaeger()
    VK: OAuthCredVK = OAuthCredVK()
    Yandex: OAuthCredYandex = OAuthCredYandex()
    PG_CONNECT_STRING: AnyUrl = f'postgresql+psycopg2://{PG.user}:{PG.password}@{PG.host}:{PG.port}/{PG.dbname}'
    ACCESS_TOKEN_TTL = timedelta(minutes=10)
    REFRESH_TOKEN_TTL = timedelta(days=30)
    BASE_URL: AnyUrl = os.environ.get('APP_URL')
