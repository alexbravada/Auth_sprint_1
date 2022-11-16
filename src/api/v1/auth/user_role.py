from flask import Blueprint
from flask import request
from flask import jsonify
from flask import make_response
from flask import abort

from flask_jwt_extended import jwt_required, get_jwt
from db.role_service import RoleService
from db.token_store_service import AbstractCacheStorage, get_token_store_service

user_role_bp = Blueprint('user_role', __name__, url_prefix='/user/role')


# TODO add JWT required to each route

@user_role_bp.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@user_role_bp.errorhandler(400)
def not_found(error):
    return make_response(jsonify({'error': 'Request data is invalid'}), 400)


def _json_check(rrequest):
    if not rrequest.json or not 'user_id' in rrequest.json or not 'role_id' in rrequest.json:
        abort(400)


@user_role_bp.route('', methods=['GET'])
@jwt_required()
def show_user_role(token_store_service: AbstractCacheStorage = get_token_store_service()):
    ''' curl -X GET -H "Authorization: Bearer <access_token>" http://127.0.0.1:5000/api/v1/auth/user/role'''
    access_token = request.headers['Authorization']
    payload = get_jwt()
    if not payload.get('is_admin'):
        abort(403)
    email = payload.get('email')
    iat = payload.get('iat')
    blacklist = token_store_service.check_blacklist(access_token)
    expired = token_store_service.check_logout_email_date(email, iat)
    if not blacklist and not expired:
        pass
    else: 
        abort(403)
    db = RoleService()
    response_inner = [x.as_dict for x in db.user_role_show_all()]
    return jsonify({'user__roles': response_inner})


@user_role_bp.route('/user_role_add', methods=['POST'])
@jwt_required()
def user_add_role(token_store_service: AbstractCacheStorage = get_token_store_service()):
    ''' curl -X POST -H "Authorization: Bearer <access_token>" http://127.0.0.1:5000/api/v1/auth/user/role/user_role_add'''
    access_token = request.headers['Authorization']
    payload = get_jwt()
    if not payload.get('is_admin'):
        abort(403)
    email = payload.get('email')
    iat = payload.get('iat')
    blacklist = token_store_service.check_blacklist(access_token)
    expired = token_store_service.check_logout_email_date(email, iat)
    if not blacklist and not expired:
        pass
    else: 
        abort(403)
    _json_check(request)
    result = request.json
    user_id = result.get('user_id')
    role_id = result.get('role_id')
    db = RoleService()
    response_inner = [db.user_add_role(user_id, role_id).as_dict]
    return jsonify({'user__role created': response_inner})


@user_role_bp.route('/user_role_show/<int:user_id>', methods=['GET'])
@jwt_required()
def user_check_role(user_id, token_store_service: AbstractCacheStorage = get_token_store_service()):
    ''' curl -X GET -H "Authorization: Bearer <access_token>" http://127.0.0.1:5000/api/v1/auth/user/role/user_role_show/1'''
    access_token = request.headers['Authorization']
    payload = get_jwt()
    if not payload.get('is_admin'):
        abort(403)
    email = payload.get('email')
    iat = payload.get('iat')
    blacklist = token_store_service.check_blacklist(access_token)
    expired = token_store_service.check_logout_email_date(email, iat)
    if not blacklist and not expired:
        pass
    else: 
        abort(403)
    db = RoleService()
    response_inner = [x.as_dict for x in db.user_check_role(user_id)]
    return jsonify({'user__role': response_inner})


@user_role_bp.route('/role_user_show/<int:role_id>', methods=['GET'])
@jwt_required()
def role_check_user(role_id, token_store_service: AbstractCacheStorage = get_token_store_service()):
    ''' curl -X GET -H "Authorization: Bearer <access_token>" http://127.0.0.1:5000/api/v1/auth/user/role/role_user_show/1'''
    access_token = request.headers['Authorization']
    payload = get_jwt()
    if not payload.get('is_admin'):
        abort(403)
    email = payload.get('email')
    iat = payload.get('iat')
    blacklist = token_store_service.check_blacklist(access_token)
    expired = token_store_service.check_logout_email_date(email, iat)
    if not blacklist and not expired:
        pass
    else: 
        abort(403)
    db = RoleService()
    response_inner = [x.as_dict for x in db.role_check_user(role_id)]
    return jsonify({'role__user': response_inner})


@user_role_bp.route('/user_role_delete', methods=['DELETE'])
@jwt_required()
def user_role_remove(token_store_service: AbstractCacheStorage = get_token_store_service()):
    ''' curl -X DELETE -H "Authorization: Bearer <access_token>" http://127.0.0.1:5000/api/v1/auth/user/role/user_role_delete'''
    access_token = request.headers['Authorization']
    payload = get_jwt()
    if not payload.get('is_admin'):
        abort(403)
    email = payload.get('email')
    iat = payload.get('iat')
    blacklist = token_store_service.check_blacklist(access_token)
    expired = token_store_service.check_logout_email_date(email, iat)
    if not blacklist and not expired:
        pass
    else: 
        abort(403)
    _json_check(request)
    result = request.json
    user_id = result.get('user_id')
    role_id = result.get('role_id')
    db = RoleService()
    response_inner = [db.user_remove_role(user_id, role_id).as_dict]
    return jsonify({'user__role deleted': response_inner})
