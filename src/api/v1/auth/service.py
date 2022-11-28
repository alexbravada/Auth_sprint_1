from functools import wraps
from http import HTTPStatus
from datetime import timedelta
import time

from flask import jsonify
from flask_jwt_extended import get_jwt
from flask_jwt_extended import verify_jwt_in_request
from flask_jwt_extended import create_access_token, create_refresh_token

from db.token_store_service import AbstractCacheStorage, get_token_store_service


def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims["is_admin"]:
                return fn(*args, **kwargs)
            else:
                return jsonify(msg="Admins only!"), HTTPStatus.FORBIDDEN

        return decorator

    return wrapper


def token_validation(request,
                     token_store_service: AbstractCacheStorage = get_token_store_service()):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            access_token = request.headers['Authorization'].split()[1]
            payload = get_jwt()
            email = payload.get('email')
            iat = payload.get('iat')
            blacklist = token_store_service.check_blacklist(access_token)
            expired = token_store_service.check_logout_email_date(email, iat)
            if blacklist or expired:
                return jsonify(msg="Invalid access token!"), HTTPStatus.FORBIDDEN
            else:
                return fn(*args, **kwargs)

        return decorator

    return wrapper


def create_login_tokens(email: str, payload: dict) -> tuple[str, str]:
    exp_delta = timedelta(minutes=10)
    exp_refresh_delta = timedelta(days=30)
    access_token = create_access_token(
        email, additional_claims=payload, expires_delta=exp_delta)
    refresh_token = create_refresh_token(
        email, additional_claims=payload, expires_delta=exp_refresh_delta)
    return access_token, refresh_token


def logout_service(request,
                   token_store_service: AbstractCacheStorage = get_token_store_service()) -> str:
    access_token = request.json.get('access_token')
    jwt = get_jwt()
    now = round(time.time())
    refresh_exp = jwt.get('exp')
    refresh_token = request.headers['Authorization'].split()[1]
    refresh_ttl = refresh_exp - now
    if refresh_ttl > 0:
        token_store_service.add_to_blacklist(refresh_token, expired=refresh_ttl)
    token_store_service.add_to_blacklist(access_token, expired=600)
    return token_store_service.check_blacklist(refresh_token)


def logout_all_service(token,
                       token_store_service: AbstractCacheStorage = get_token_store_service()) -> str:
    email = token.get('email')
    iat = token.get('iat')
    exp = token.get('exp')
    exp = exp - iat
    token_store_service.logout_all(email, iat, exp)
    return email


def blacklisting_tokens(request,
                        token_store_service: AbstractCacheStorage = get_token_store_service()) -> str:
    old_refresh_token = request.headers['Authorization'].split()[1]
    old_access_token = request.json.get('access_token')
    jwt = get_jwt()
    refresh_exp = jwt.get('exp') - jwt.get('iat')
    email = jwt.get('email')
    token_store_service.add_to_blacklist(old_access_token)
    token_store_service.add_to_blacklist(old_refresh_token, expired=refresh_exp)
    return email
