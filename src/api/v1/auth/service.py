from functools import wraps
from http import HTTPStatus

from flask import jsonify
from flask_jwt_extended import get_jwt
from flask_jwt_extended import verify_jwt_in_request

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


def token_validation(request, token_store_service: AbstractCacheStorage = get_token_store_service()):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            access_token = request.headers['Authorization']
            payload = get_jwt()
            email = payload.get('email')
            iat = payload.get('iat')
            blacklist = token_store_service.check_blacklist(access_token)
            expired = token_store_service.check_logout_email_date(email, iat)
            if blacklist or expired:
                jsonify(msg="Invalid access token!"), HTTPStatus.FORBIDDEN
            else:
                return fn(*args, **kwargs)

        return decorator

    return wrapper

