from flask import Blueprint
from flask import request
from flask import jsonify
from flask import make_response
from flask import abort

from flask_jwt_extended import jwt_required, get_jwt

from db.role_service import RoleService
from db.token_store_service import AbstractCacheStorage, get_token_store_service

role_bp = Blueprint('role', __name__, url_prefix='/role')


@role_bp.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@role_bp.errorhandler(400)
def not_found(error):
    return make_response(jsonify({'error': 'Request data is invalid'}), 400)


@role_bp.route("/add", methods=['POST'])
@jwt_required()
def add_role(token_store_service: AbstractCacheStorage = get_token_store_service()):
    '''curl -X POST -H "Content-Type: application/json" -d '{"name":"role_name33", "description":"descrip"}' http://127.0.0.1:5000/api/v1/auth/role/add'''
    access_token = request.headers['Authorization']
    payload = get_jwt()
    if not payload.get('is_admin'):
        abort(403)
    email = payload.get('email')
    iat = payload.get('iat')
    blacklist = token_store_service.check_blacklist(access_token)
    expired = token_store_service.check_logout_email_date(email, iat)
    if blacklist or expired:
        abort(403)
    if not request.json or not 'name' in request.json:
        abort(400)
    result = request.json
    name = result.get('name')
    description = result.get('description')
    db = RoleService()
    response_array = [db.add_role(name, description).as_dict]
    return jsonify({'role': response_array}), 201


@role_bp.route('/delete', methods=['DELETE'])
@jwt_required()
def delete_role(token_store_service: AbstractCacheStorage = get_token_store_service()):
    ''' curl -X DELETE -H "Authorization: Bearer <access_token>" http://127.0.0.1:5000/api/v1/auth/role/delete'''
    access_token = request.headers['Authorization']
    payload = get_jwt()
    if not payload.get('is_admin'):
        abort(403)
    email = payload.get('email')
    iat = payload.get('iat')
    blacklist = token_store_service.check_blacklist(access_token)
    expired = token_store_service.check_logout_email_date(email, iat)
    if blacklist or expired:
        abort(403)
    if not request.json or not 'id' in request.json:
        abort(400)
    result = request.json
    role_id = result.get('id')
    db = RoleService()
    response_array = [db.del_role(role_id).as_dict]
    return jsonify({'deleted role': response_array})


@role_bp.route('', methods=['GET'])
@jwt_required()
def show_roles_all(token_store_service: AbstractCacheStorage = get_token_store_service()):
    ''' curl -X GET -H "Authorization: Bearer <access_token>" http://127.0.0.1:5000/api/v1/auth/role'''
    access_token = request.headers['Authorization']
    payload = get_jwt()
    if not payload.get('is_admin'):
        abort(403)
    email = payload.get('email')
    iat = payload.get('iat')
    blacklist = token_store_service.check_blacklist(access_token)
    expired = token_store_service.check_logout_email_date(email, iat)
    if blacklist or expired:
        abort(403)
    db = RoleService()
    response_inner = [x.as_dict for x in db.show_all_roles()]
    return jsonify({'roles': response_inner})


@role_bp.route('/<int:role_id>', methods=['GET'])
@jwt_required()
def show_role(role_id, token_store_service: AbstractCacheStorage = get_token_store_service()):
    ''' curl -X GET -H "Authorization: Bearer <access_token>" http://127.0.0.1:5000/api/v1/auth/role/1'''
    access_token = request.headers['Authorization']
    payload = get_jwt()
    if not payload.get('is_admin'):
        abort(403)
    email = payload.get('email')
    iat = payload.get('iat')
    blacklist = token_store_service.check_blacklist(access_token)
    expired = token_store_service.check_logout_email_date(email, iat)
    if blacklist or expired:
        abort(403)
    db = RoleService()
    response_inner = [db.show_role(role_id).as_dict]
    return jsonify({'role': response_inner})


@role_bp.route('/update', methods=['PUT'])
@jwt_required()
def update_role(token_store_service: AbstractCacheStorage = get_token_store_service()):
    ''' curl -X PUT -H "Authorization: Bearer <access_token>" http://127.0.0.1:5000/api/v1/auth/role/update'''
    access_token = request.headers['Authorization']
    payload = get_jwt()
    if not payload.get('is_admin'):
        abort(403)
    email = payload.get('email')
    iat = payload.get('iat')
    blacklist = token_store_service.check_blacklist(access_token)
    expired = token_store_service.check_logout_email_date(email, iat)
    if blacklist or expired:
        abort(403)
    if not request.json or not 'id' in request.json:
        abort(400)
    result = request.json
    role_id = result.get('id')
    name = result.get('name')
    description = result.get('description')
    db = RoleService()
    response_inner = [db.update_role(role_id, name, description).as_dict]
    return jsonify({'role updated': response_inner}), 201
