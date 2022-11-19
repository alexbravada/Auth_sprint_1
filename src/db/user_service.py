from db.pg_base import PostgresService
from models.user import User, LoginRecord
from models.pydantic_classes import UserOutput
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from sqlalchemy.exc import MultipleResultsFound
from werkzeug.security import generate_password_hash, check_password_hash
from typing import Tuple


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
                    return {"status": "403", "msg": "account with that email has been used"}
            except MultipleResultsFound as e:
                return {"status": "403", "msg": "account with that email has been used"}
            except NoResultFound as e:
                user = User(email=email, password=generate_password_hash(password), first_name=first_name,
                            last_name=last_name)
                session.add(user)
                session.commit()
            return {"status": "201"}

    def login(self, email, password) -> Tuple[bool, dict]:
        with Session(self.engine) as session:
            user = ''
            try:
                user = session.query(User).filter(User.email == email).one()
                d = self._row_to_dict(user)
                if user and check_password_hash(user.password, password):
                    output = UserOutput(**d)
                    output = dict(output)
                    return True, output  # output для payload
                return False, {}
            except NoResultFound as ee:
                return False, {}

    def get_user_payload(self, email):
        with Session(self.engine) as session:
            user = ''
        try:
            user = session.query(User).filter(User.email == email).one()
            if user:
                d = self._row_to_dict(user)
                output = UserOutput(**d)
                output = dict(output)
                session.close()
                return output
        except NoResultFound:
            return False

    def change_pwd(self, email: str, old_password: str, new_password: str) -> bool:
        with Session(self.engine) as session:
            user = ''
        try:
            user = session.query(User).filter(User.email == email).one()
            if user and check_password_hash(user.password, old_password):
                user.password = generate_password_hash(new_password)
                session.commit()
                print('VSE OK OK OK Password changed')
                return True
        except NoResultFound:
            return False

    def change_email(self, email: str, password: str, new_email: str) -> bool:
        with Session(self.engine) as session:
            user = ''
        try:
            user = session.query(User).filter(User.email == email).one()
            if user and check_password_hash(user.password, password):
                user.email = new_email
                d = self._row_to_dict(user)
                output = UserOutput(**d)
                output = dict(output)
                print(output)
                session.commit()
                print('OK OK OK')
                return True, output
        except NoResultFound:
            print('bad', user)
            return False, {}

    def update_user_from_dict(self, email: str, data: dict):
        with Session(self.engine) as session:
            user = ''
        try:
            user = session.query(User).filter(User.email == email).one().values(**data)
            if user:
                d = self._row_to_dict(user)
                output = UserOutput(**d)
                output = dict(output)
                print(output)
                return True, output
        except NoResultFound:
            return False, {}

    def get_auth_history(self, user_id: int):
        with Session(self.engine) as session:
            user_history = ''
        try:
            output = dict()
            user_history = session.query(LoginRecord).filter(LoginRecord.user_id == user_id).one()
            for agent in user_history:
                output[agent.useragent] = agent.login_time
            return True, output
        except NoResultFound:
            return False, {}


    def _row_to_dict(self, row) -> dict:
        d = {}
        for column in row.__table__.columns:
            d[column.name] = getattr(row, column.name)
        return d
