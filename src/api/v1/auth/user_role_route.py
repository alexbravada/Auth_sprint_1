from http import HTTPStatus

from flask import Blueprint
from flask import request
from flask import jsonify
from flask import make_response
from flask import abort
from flask_jwt_extended import jwt_required

from db.role_service import RoleService
from .auth_service import admin_required, token_validation

user_role_bp = Blueprint('user_role', __name__, url_prefix='/user_role')


@user_role_bp.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), HTTPStatus.NOT_FOUND)


@user_role_bp.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Request data is invalid'}), HTTPStatus.BAD_REQUEST)


@user_role_bp.errorhandler(403)
def forbidden(error):
    return make_response(jsonify({'error': 'Request data is invalid'}), HTTPStatus.FORBIDDEN)


def body_validate(rrequest):
    if not rrequest.json or 'user_id' not in rrequest.json or 'role_id' not in rrequest.json:
        abort(400)


@user_role_bp.route('', methods=['GET'])
@jwt_required()
@admin_required()
@token_validation(request)
def show_user_role():
    db = RoleService()
    return jsonify({'user__roles': [x.as_dict for x in db.user_role_show_all()]}), HTTPStatus.OK


@user_role_bp.route('/user_role_add', methods=['POST'])
@jwt_required()
@admin_required()
@token_validation(request)
def user_add_role():
    body_validate(request)
    db = RoleService()
    return jsonify({'user__role created':
                        [db.user_add_role(user_id=request.json.get('user_id'),
                                          role_id=request.json.get('role_id')).as_dict]
                    }), HTTPStatus.CREATED


@user_role_bp.route('/user_role_show/<int:user_id>', methods=['GET'])
@jwt_required()
@admin_required()
@token_validation(request)
def user_check_role(user_id):
    db = RoleService()
    return jsonify({'user__role': [x.as_dict for x in db.user_check_role(user_id)]}), HTTPStatus.OK


@user_role_bp.route('/role_user_show/<int:role_id>', methods=['GET'])
@jwt_required()
@admin_required()
@token_validation(request)
def role_check_user(role_id):
    db = RoleService()
    return jsonify({'role__user': [x.as_dict for x in db.role_check_user(role_id)]}), HTTPStatus.OK


@user_role_bp.route('/user_role_delete', methods=['DELETE'])
@jwt_required()
@admin_required()
@token_validation(request)
def user_role_remove():
    body_validate(request)
    db = RoleService()
    return jsonify({'user__role deleted':
                        [db.user_remove_role(user_id=request.json.get('user_id'),
                                             role_id=request.json.get('role_id')).as_dict]
                    }), HTTPStatus.OK
