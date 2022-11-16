import datetime
import orjson

from pydantic import BaseModel, Field
from typing import Optional


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


'''{'id': 1, 'created': datetime.datetime(2022, 11, 7, 14, 14, 27, 547219),
 'modified': None, 'email': 'test_user', 'first_name': None, 'last_name': None,
  'password': '',
 'is_active': True, 'is_verified': False}'''