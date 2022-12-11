import random
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from sqlalchemy.exc import MultipleResultsFound
from werkzeug.security import generate_password_hash, check_password_hash
from flask import abort
from user_agents import parse as ua_parse

from db.pg_base import PostgresService
from models.user_model import User, LoginRecord, SocialAccount
from models.pydantic_classes import UserOutput


class UserService(PostgresService):
    def __init__(self):
        super().__init__()

    def admin_register(self, email, password, first_name=None, last_name=None):
        with Session(self.engine) as session:
            try:
                session.query(User).filter(User.email == email).one()
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
                user = session.query(User).filter(User.email == email).one()
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
                                           user_id=user.id,
                                           device_type=self._device_type(useragent))
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
                    user = session.query(User).filter(User.email == email).one()
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

    def oauth_authorize(self, email: str, social_id: str, social_name: str, useragent: str) -> dict:
        from api.v1.auth.auth_service import create_login_tokens
        def _login_wo_pass() -> dict:
            user = session.query(User).filter(User.email == email).one()
            data = user.as_dict
            data = UserOutput(**data)
            access_token, refresh_token = create_login_tokens(email=email, payload=dict(data))
            return {'access_token': access_token, 'refresh_token': refresh_token}

        def _social_reg(user_id: int):
            social_reg = SocialAccount(social_id=social_id, social_name=social_name, user_id=user_id)
            session.add(social_reg)
            session.commit()

        def _login_rec(user_id: int):
            loginrec = LoginRecord(login_time=datetime.utcnow(),
                                   useragent=useragent,
                                   user_id=user_id,
                                   device_type=self._device_type(useragent))
            session.add(loginrec)
            session.commit()

        with Session(self.engine) as session:
            try:
                user = session.query(User).filter(User.email == email).one()
                if user:
                    try:
                        session.query(SocialAccount).filter(SocialAccount.social_id == social_id,
                                                            SocialAccount.social_name == social_name,
                                                            SocialAccount.user_id == user.id).one()
                        _login_rec(user_id=user.id)
                        return _login_wo_pass()
                    except NoResultFound:
                        _social_reg(user_id=user.id)
                        _login_rec(user_id=user.id)
                        return _login_wo_pass()

            except NoResultFound:
                user = self.register(email=email, password=generate_password_hash(str(random.randint(1, 128))))
                session.add(user)
                session.commit()
                user = session.query(User).filter(User.email == email).one()
                _social_reg(user_id=user.id)
                _login_rec(user_id=user.id)
                return _login_wo_pass()

    @staticmethod
    def _device_type(useragent: str) -> str | None:
        try:
            ua_instance = ua_parse(useragent)
            if ua_instance.is_pc:
                return 'pc'
            elif ua_instance.is_mobile:
                return 'mobile'
            elif ua_instance.is_tablet:
                return 'tablet'
            elif ua_instance.is_bot:
                return 'bot'
            else:
                return 'undefined'
        except Exception:
            return None

    @staticmethod
    def _row_to_dict(row) -> dict:
        d = {}
        for column in row.__table__.columns:
            d[column.name] = getattr(row, column.name)
        return d
