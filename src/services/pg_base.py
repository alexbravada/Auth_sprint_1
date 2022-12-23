from sqlalchemy import create_engine
from config.settings import Settings


class PostgresService:
    def __init__(self):
        self.settings = Settings()
        self.engine = create_engine(
            self.settings.PG_CONNECT_STRING,
            isolation_level="REPEATABLE READ",
            echo=True
        )
