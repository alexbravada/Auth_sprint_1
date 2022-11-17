import datetime
import time

from flask import Blueprint
from flask import request
from flask import jsonify

from flask_jwt_extended import create_access_token, create_refresh_token
from flask_jwt_extended import jwt_required, get_jwt

from db.user_service import UserService
from db.redis_base import AbstractCacheStorage
from db.token_store_service import get_token_store_service


user_bp = Blueprint('user', __name__, url_prefix='/user')


@user_bp.route("/signin", methods=['POST'])
def sign_in():
    '''
        curl -X POST -H "Content-Type: application/json" -d '{"email":"test_user", "password":"123"}' http://127.0.0.1:5000/api/v1/auth/user/signin
        url = "http://localhost:8080"
        data = {'email': 'Alice', 'password': 'ChangeMe'}
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    '''
    result = request.json
    email = result.get('email')
    password = result.get('password')
    if not email or not password:
        return jsonify({'error': 'email & password require'}), 401
    db = UserService()
    res, payload = db.login(email, password)
    if not res:
        return jsonify({"error": "Invalid email or password"}), 401
    if res and payload:
        response = dict()
        exp_delta = datetime.timedelta(minutes=10)
        exp_refresh_delta = datetime.timedelta(days=30)
        access_token = create_access_token(email, additional_claims=payload, expires_delta=exp_delta)
        refresh_token = create_refresh_token(email, additional_claims=payload, expires_delta=exp_refresh_delta)
        response['access_token'] = access_token
        response['refresh_token'] = refresh_token
        return jsonify(response), 200


@user_bp.route('/signup', methods=['POST'])
def sign_up():
    '''curl -X POST -H "Content-Type: application/json" -d '{"email":"test_user", "password":"123"}' http://127.0.0.1:5000/api/v1/auth/user/signup'''
    result = request.json # or result = request.get_json(force=True)
    email = result.get('email')
    password = result.get('password')
    first_name = result.get('first_name')
    last_name = result.get('last_name')
    print(email)
    db = UserService()
    response = db.register(email, password, first_name, last_name)
    print('resp sttttttaaaa: ', response.get('status'))
    if response.get('status') == '201':
        return jsonify(response), 201
    return jsonify(response), 403


@user_bp.route('/logout', methods=['POST'])
@jwt_required(refresh=True, locations=['headers'])
def logout(token_store_service: AbstractCacheStorage = get_token_store_service()):
    '''curl -X POST -H "Authorization: Bearer <refresh_token>" -H "Content-Type: application/json" -d '{"access_token": "322"}' http://127.0.0.1:5000/api/v1/auth/user/logout'''
    access_token = request.json.get('access_token')
    jwt = get_jwt()
    now = round(time.time())
    refresh_exp = jwt.get('exp')
    refresh_token = request.headers['Authorization'].split()[1]
    print('refresh from logout', refresh_token)
    refresh_ttl = refresh_exp - now
    if refresh_ttl > 0:
        token_store_service.add_to_blacklist(refresh_token, expired=refresh_ttl)
    token_store_service.add_to_blacklist(access_token, expired=600)
    print('zapisal')
    token_in = token_store_service.check_blacklist(refresh_token)
    print('check refresh', token_store_service.check_blacklist(refresh_token))
    print('check access', token_store_service.check_blacklist(access_token))
    print('chech random', token_store_service.check_blacklist("random key"))
    return jsonify(token_in), 200


@user_bp.route('/logout_all', methods=['POST'])
@jwt_required(locations=['headers'])
def logout_all(token_store_service: AbstractCacheStorage = get_token_store_service()):
    '''curl -X POST -H "Authorization: Bearer <access_token>" http://127.0.0.1:5000/api/v1/auth/user/logout_all'''
    token = get_jwt()
    email = token.get('email')
    iat = token.get('iat')
    exp = token.get('exp')
    exp = exp - iat
    token_store_service.logout_all(email, iat, exp)
    return jsonify({"logout": True}), 200


@user_bp.route('/change_password', methods=['POST'])
@jwt_required(locations=['headers'])
def change_password():
    status = {'status': False} # default state
    # найти пользователя в PostgreSQL
    jwt = get_jwt()
    email = jwt.get('email')
    old_pwd = request.json.get('old_password')
    new_pwd = request.json.get('new_password')
    db = UserService()
    # если да, то установить новый пароль пользователю.
    res = db.change_pwd(email=email, old_password=old_pwd, new_password=new_pwd)
    if res:
        status['status'] = res
        return jsonify(status), 200
    return jsonify(status), 401


@user_bp.route('/change_email', methods=['POST'])
@jwt_required(locations=['headers'])
def change_pwd(token_store_service: AbstractCacheStorage = get_token_store_service()):
    '''curl -X POST -H "Content-Type: application/json"\n
    -d '{"email":"test_user", "password":"123", "new_email":"test_user_new"}' http://127.0.0.1:5000/api/v1/auth/user/change_email'''
    response = {'status': False} # default state
    # найти пользователя в PostgreSQL
    old_access_token = request.headers['Authorization']
    jwt = get_jwt()
    email = jwt.get('email')
    password = request.json.get('password')
    new_email = request.json.get('new_email')
    db = UserService()
    res, _ = db.change_email(email=email, password=password, new_email=new_email)
    if res:
        response['status'] = res
        token_store_service.add_to_blacklist(old_access_token)
        return jsonify(response), 200
    return jsonify(response), 401


@user_bp.route('/access', methods=['POST'])
@jwt_required(locations=['headers'])
def access(token_store_service: AbstractCacheStorage = get_token_store_service()):
    ''' curl -X POST -H "Authorization: Bearer <access_token>" http://127.0.0.1:5000/api/v1/auth/user/access'''
    payload = get_jwt()
    email = payload.get('email')
    iat = payload.get('iat')
    token = request.headers['Authorization'].split()[1]
    print('eto timestamp', payload.get('exp'))
    print('eto payload email', payload.get('email'))
    blacklist = token_store_service.check_blacklist(token)
    expired = token_store_service.check_logout_email_date(email=email, iat=iat)
    if not blacklist and not expired:
        return jsonify({'access': True}), 200
    return jsonify({'access': False, 'msg': 'Access Token expired'}), 403


@user_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True, locations=['headers'])
def get_refresh(token_store_service: AbstractCacheStorage = get_token_store_service()):
    ''' curl -X POST -H "Authorization: Bearer <refresh_token>" -H "Content-Type: application/json" -d '{"access_token": "token"}' http://127.0.0.1:5000/api/v1/auth/user/refresh
    '''
    print(get_jwt())
    #print('eto Refresh TOK', request.headers['Authorization'])
    old_refresh_token = request.headers['Authorization'].split()[1]
    old_access_token = request.json.get('access_token')
    jwt = get_jwt()
    refresh_exp = jwt.get('exp') - jwt.get('iat')
    email = jwt.get('email')
    # get actual user info
    db = UserService()
    payload = db.get_user_payload(email)
    # добавить в blacklist access from body json & refresh from headers
    token_store_service.add_to_blacklist(old_access_token)
    token_store_service.add_to_blacklist(old_refresh_token, expired=refresh_exp)
    # generate new tokens
    response = dict()
    exp_delta = datetime.timedelta(minutes=10)
    exp_refresh_delta = datetime.timedelta(days=30)
    access_token = create_access_token(email, additional_claims=payload, expires_delta=exp_delta)
    refresh_token = create_refresh_token(email, additional_claims=payload, expires_delta=exp_refresh_delta)
    response['access_token'] = access_token
    response['refresh_token'] = refresh_token
    return jsonify(response), 200
