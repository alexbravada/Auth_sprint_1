import datetime

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import Boolean
from sqlalchemy import MetaData
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr

from config.settings import Settings

settings = Settings()

db_connection_string = settings.PG_CONNECT_STRING
engine = create_engine(
    db_connection_string,
    isolation_level="REPEATABLE READ",
    echo=True,
)

Base = declarative_base()
metadata_obj = MetaData()


class DefaultMixin:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True, autoincrement=True)
    created = Column(DateTime(), nullable=False, default=datetime.datetime.utcnow())
    modified = Column(DateTime(), nullable=True)

    @property
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class LoginRecord(DefaultMixin, Base):
    __tablename__ = 'login_history'
    login_time = Column(DateTime(), nullable=False)
    useragent = Column(String(256), nullable=True)

    user_id = Column(Integer, ForeignKey('user_info.id'), nullable=False)

    def __repr__(self):
        return f'LoginRecord(id={self.id!r}, login_time={self.login_time!r}, useragent={self.useragent!r})'


class User(DefaultMixin, Base):
    __tablename__ = 'user_info'
    email = Column(String(256), unique=True, nullable=False)
    first_name = Column(String(256), nullable=True)
    last_name = Column(String(256), nullable=True)
    password = Column(String(512), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)

    login_records = relationship('LoginRecord')
    roles = relationship('UserRole', backref='user')

    def __repr__(self):
        return f'User(id={self.id!r}, email={self.email!r})'


class UserRole(DefaultMixin, Base):
    __tablename__ = 'user__role'
    user_id = Column(Integer(), ForeignKey('user_info.id'))
    role_id = Column(Integer(), ForeignKey('role.id'))

    def __repr__(self):
        return f'User_Role(id={self.id!r}, user_id={self.user_id!r}, role_id={self.role_id!r})'


class Role(DefaultMixin, Base):
    __tablename__ = 'role'
    name = Column(String(128), nullable=False)
    description = Column(String(256), nullable=True)
    users = relationship('UserRole', backref='role')

    def __repr__(self):
        return f'Role(id={self.id!r}, name={self.name!r})'


class ResourceRole(DefaultMixin, Base):
    __tablename__ = 'resource__role'
    role_id = Column(Integer(), ForeignKey('role.id'))
    # resource_id = Column(Integer(), ForeignKey('resource.id'))
    can_create = Column(Boolean, nullable=False)
    can_read = Column(Boolean, nullable=False)
    can_update = Column(Boolean, nullable=False)
    can_delete = Column(Boolean, nullable=False)

    def __repr__(self):
        return f'ResourceRole(id={self.id!r}, role_id={self.role_id!r}, resource_id={self.resource_id!r}, ' \
               f'can_create={self.can_create!r}, can_read={self.can_read!r}, can_update={self.can_update!r}, ' \
               f'can_delete={self.can_delete!r})'


Base.metadata.create_all(bind=engine)
