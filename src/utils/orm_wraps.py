from functools import wraps
from sqlalchemy.orm import Session


def engine_session():
    def wrapper(fn):
        @wraps(fn)
        def decorator(self, *args, **kwargs):
            with Session(self.engine) as session:
                return fn(self, *args, **kwargs, session=session)

        return decorator

    return wrapper
