import datetime
from typing import Optional

from sqlalchemy import Column, MetaData, create_engine, or_, UniqueConstraint, PrimaryKeyConstraint, event
from sqlalchemy import Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import declarative_base, backref, relationship
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
    __table_args__ = (
        UniqueConstraint('id', 'device_type'),
        {
            'postgresql_partition_by': 'LIST (device_type)',
        }
    )
    login_time = Column(DateTime(), nullable=False)
    useragent = Column(String(256), nullable=True)
    device_type = Column(String(64), nullable=True, primary_key=True)

    user_id = Column(Integer, ForeignKey('user_info.id', ondelete='CASCADE'), nullable=False)

    def __repr__(self):
        return f'LoginRecord(id={self.id!r}, login_time={self.login_time!r}, ' \
               f'useragent={self.useragent!r}, device_type={self.device_type!r})'


class User(DefaultMixin, Base):
    __tablename__ = 'user_info'
    __table_args__ = (UniqueConstraint('email', 'username', name='user_email_username_unique_constr'),)
    email = Column(String(256), unique=True, nullable=False)
    username = Column(String(256), nullable=True)
    first_name = Column(String(256), nullable=True)
    last_name = Column(String(256), nullable=True)
    password = Column(String(512), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    is_adult = Column(Boolean, default=False)

    role_id = Column(Integer, ForeignKey('role.id'), nullable=False)

    login_records = relationship('LoginRecord', cascade='all, delete-orphan', passive_deletes=True)

    social_accounts = relationship('SocialAccount', backref='user',
                                   cascade='all, delete-orphan',
                                   passive_deletes=True)

    def __repr__(self):
        return f'User(id={self.id!r}, email={self.email!r})'

    @classmethod
    def get_user_by_universal_login(cls, username: Optional[str] = None, email: Optional[str] = None):
        """
        возвращает первое совпадение фильтра username OR email
        """
        return cls.query.filter(or_(cls.username == username, cls.email == email)).first()


class SocialAccount(DefaultMixin, Base):
    __tablename__ = 'social_account'
    __table_args__ = (UniqueConstraint('social_id', 'social_name', name='social_pk'),
                      UniqueConstraint('id', 'social_name'),
                      {
                          'postgresql_partition_by': 'LIST (social_name)',
                      }
                      )

    user_id = Column(Integer(), ForeignKey('user_info.id', ondelete='CASCADE'), nullable=False)

    social_id = Column(Text, nullable=False)
    social_name = Column(Text, nullable=False, primary_key=True)

    def __repr__(self):
        return f'<SocialAccount {self.social_name}:{self.user_id}>'


class Role(DefaultMixin, Base):
    __tablename__ = 'role'
    name = Column(String(128), nullable=False)
    description = Column(String(256), nullable=True)

    users = relationship('User', backref='role')

    def __repr__(self):
        return f'Role(id={self.id!r}, name={self.name!r})'


class ResourceRole(DefaultMixin, Base):
    __tablename__ = 'resource__role'
    role_id = Column(Integer(), ForeignKey('role.id'))
    resource_id = Column(Integer(), ForeignKey('resource.id', ondelete='CASCADE'))
    can_create = Column(Boolean, nullable=False)
    can_read = Column(Boolean, nullable=False)
    can_update = Column(Boolean, nullable=False)
    can_delete = Column(Boolean, nullable=False)

    def __repr__(self):
        return f'ResourceRole(id={self.id!r}, role_id={self.role_id!r}, resource_id={self.resource_id!r}, ' \
               f'can_create={self.can_create!r}, can_read={self.can_read!r}, can_update={self.can_update!r}, ' \
               f'can_delete={self.can_delete!r})'


class Resource(DefaultMixin, Base):
    __tablename__ = 'resource'
    __table_args__ = (UniqueConstraint('resource_uuid', 'resource_type', name='uuid__type_pk'),)
    resource_uuid = Column(String(256), nullable=False)
    resource_type = Column(String(256), nullable=False)
    name = Column(String(250), nullable=True)

    roles = relationship('ResourceRole', backref='resource', cascade='all, delete-orphan', passive_deletes=True)
