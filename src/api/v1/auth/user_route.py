from http import HTTPStatus

from flask import Blueprint
from flask import request
from flask import jsonify
from flask import make_response
from flask import abort
from flask_jwt_extended import jwt_required, get_jwt

from db.user_service import UserService
from db.redis_base import AbstractCacheStorage
from db.token_store_service import get_token_store_service
from .auth_service import create_login_tokens, logout_service, \
    logout_all_service, token_validation, blacklisting_tokens


user_bp = Blueprint('user', __name__, url_prefix='/user')


@user_bp.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), HTTPStatus.NOT_FOUND)


@user_bp.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Request data is invalid'}), HTTPStatus.BAD_REQUEST)


@user_bp.errorhandler(401)
def unauthorized(error):
    return make_response(jsonify({'error': 'Request data is invalid'}), HTTPStatus.UNAUTHORIZED)


def body_validation(rrequest):
    if 'email' not in rrequest.json or 'password' not in rrequest.json:
        abort(400)


@user_bp.route("/signin", methods=['POST'])
def sign_in():
    body_validation(request)
    db = UserService()
    email = request.json.get('email')
    useragent = request.headers.get('User-Agent')
    payload = db.login(email=email, password=request.json.get('password'), useragent=useragent)
    access_token, refresh_token = create_login_tokens(email, payload)
    response = {'access_token': access_token,
                'refresh_token': refresh_token}
    return jsonify(response), HTTPStatus.OK


@user_bp.route('/signup', methods=['POST'])
def sign_up():
    db = UserService()
    return jsonify({'created': [
        db.register(email=request.json.get('email'), password=request.json.get('password'),
                    first_name=request.json.get('first_name'),
                    last_name=request.json.get('last_name')).as_dict
    ]}), HTTPStatus.CREATED


@user_bp.route('/logout', methods=['GET'])
@jwt_required(locations=['headers'])
def logout_all():
    token = get_jwt()
    return jsonify({"logout": logout_all_service(token)}), HTTPStatus.OK


@user_bp.route('/change_password', methods=['PUT'])
@jwt_required(locations=['headers'])
@token_validation(request)
def change_password():
    jwt = get_jwt()
    db = UserService()
    return jsonify(
        {'password changed': [
            db.change_pwd(email=jwt.get('email'), old_password=request.json.get('old_password'),
                          new_password=request.json.get('new_password')).as_dict
        ]}), HTTPStatus.OK


@user_bp.route('/change_email', methods=['PUT'])
@jwt_required(locations=['headers'])
def change_pwd(token_store_service: AbstractCacheStorage = get_token_store_service()):
    old_access_token = request.headers['Authorization'].split()[1]
    jwt = get_jwt()
    db = UserService()
    response_inner = db.change_email(email=jwt.get('email'), password=request.json.get('password'),
                                     new_email=request.json.get('new_email'))
    token_store_service.add_to_blacklist(old_access_token)
    return jsonify({'email changed': [response_inner]}), HTTPStatus.OK


@user_bp.route('/access', methods=['GET'])
@jwt_required(locations=['headers'])
@token_validation(request)
def access():
    return jsonify({'access': True}), HTTPStatus.OK


@user_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True, locations=['headers'])
def get_refresh():
    email = blacklisting_tokens(request)
    db = UserService()
    payload = db.get_user_payload(email)
    access_token, refresh_token = create_login_tokens(email, payload)
    response = {'access_token': access_token,
                'refresh_token': refresh_token}
    return jsonify({'new_tokens': response}), HTTPStatus.OK


@user_bp.route('/login_history', methods=['GET'])
@jwt_required(locations=['headers'])
@token_validation(request)
def get_login_history():
    db = UserService()
    token = get_jwt()
    user_id = token.get('id')
    return jsonify({'login history': [db.get_auth_history(user_id)]})
