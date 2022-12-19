from typing import Optional
import datetime

import orjson
from pydantic import BaseModel


def orjson_dumps(v, *, default):
    # orjson.dumps возвращает bytes, а pydantic требует unicode, поэтому декодируем
    return orjson.dumps(v, default=default).decode()


class BaseOrjsonModel(BaseModel):
    class Config:
        # Заменяем стандартную работу с json на более быструю
        # json_encoders = {id: uuid4}
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class UserOutput(BaseOrjsonModel):
    id: int
    email: str
    first_name: Optional[str] = 'Your Name'
    last_name: Optional[str] = 'Your Lastname'
    created: datetime.datetime
    modified: Optional[str]
    is_active: bool
    is_verified: bool
    is_admin: bool
    role_id: int
    password: str