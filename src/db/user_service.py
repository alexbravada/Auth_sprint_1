from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from sqlalchemy.exc import MultipleResultsFound
from werkzeug.security import generate_password_hash, check_password_hash
from flask import abort

from db.pg_base import PostgresService
from models.user import User, LoginRecord
from models.pydantic_classes import UserOutput


class UserService(PostgresService):
    def __init__(self):
        super().__init__()

    def admin_register(self, email, password, first_name=None, last_name=None):
        with Session(self.engine) as session:
            try:
                admin = session.query(User).filter(User.email == email).one()
                if admin:
                    return {'msg': 'User with that email has been exist'}
            except MultipleResultsFound:
                return {'msg': 'User with that email has been exist'}
            except NoResultFound:
                admin = User(email=email, password=generate_password_hash(password), first_name=first_name,
                             last_name=last_name, is_admin=True)
                session.add(admin)
                session.commit()
                return {'msg': 'superuser created'}

    def register(self, email, password, first_name=None, last_name=None):
        with Session(self.engine) as session:
            try:
                user = session.query(User).filter(User.email == email).one()
                if user:
                    abort(400)
            except MultipleResultsFound:
                abort(400)
            except NoResultFound:
                user = User(email=email, password=generate_password_hash(password), first_name=first_name,
                            last_name=last_name)
                session.add(user)
                session.commit()
                return user

    def login(self, email, password, useragent):
        with Session(self.engine) as session:
            try:
                user = session.query(User).filter(User.email == email).one()
                d = user.as_dict
                if user and check_password_hash(user.password, password):
                    output = UserOutput(**d)
                    output = dict(output)
                    loginrec = LoginRecord(login_time=datetime.utcnow(),
                                           useragent=useragent,
                                           user_id=user.id)
                    session.add(loginrec)
                    session.commit()
                    return output
                else:
                    abort(401)
            except NoResultFound:
                abort(404)

    def get_user_payload(self, email):
        with Session(self.engine) as session:
            try:
                user = session.query(User).filter(User.email == email).one()
                if user:
                    d = self._row_to_dict(user)
                    output = UserOutput(**d)
                    output = dict(output)
                    session.close()
                    return output
            except NoResultFound:
                abort(400)

    def change_pwd(self, email: str, old_password: str, new_password: str) -> bool:
        with Session(self.engine) as session:
            try:
                user = session.query(User).filter(User.email == email).one()
                if user and check_password_hash(user.password, old_password):
                    user.password = generate_password_hash(new_password)
                    session.commit()
                    return user
            except NoResultFound:
                abort(404)

    def change_email(self, email: str, password: str, new_email: str) -> dict:
        with Session(self.engine) as session:
            try:
                user = session.query(User).filter(User.email == email).one()
                if user and check_password_hash(user.password, password):
                    user.email = new_email
                    d = user.as_dict
                    output = UserOutput(**d)
                    output = dict(output)
                    session.commit()
                    return output
            except NoResultFound:
                abort(404)

    def update_user_from_dict(self, email: str, data: dict):
        with Session(self.engine) as session:
            try:
                user = session.query(User).filter(User.email == email).one().values(**data)
                if user:
                    d = self._row_to_dict(user)
                    output = UserOutput(**d)
                    output = dict(output)
                    return True, output
            except NoResultFound:
                return False, {}

    def get_auth_history(self, user_id: str) -> dict:
        with Session(self.engine) as session:
            try:
                output = dict()
                user_history = session.query(LoginRecord).filter(LoginRecord.user_id == user_id).all()
                for eachrow in user_history:
                    output[str(eachrow.login_time)] = eachrow.useragent
                return output
            except NoResultFound:
                abort(404)

    @staticmethod
    def _row_to_dict(row) -> dict:
        d = {}
        for column in row.__table__.columns:
            d[column.name] = getattr(row, column.name)
        return d
