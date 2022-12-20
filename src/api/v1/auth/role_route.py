from http import HTTPStatus

from flask import Blueprint
from flask import request
from flask import jsonify
from flask import make_response
from flask import abort

from flask_jwt_extended import jwt_required

from db.role_service import RoleService
from .auth_service import admin_required, token_validation


role_bp = Blueprint('role', __name__, url_prefix='/role')


@role_bp.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), HTTPStatus.NOT_FOUND)


@role_bp.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Request data is invalid'}), HTTPStatus.BAD_REQUEST)


@role_bp.errorhandler(403)
def forbidden(error):
    return make_response(jsonify({'error': 'Request data is invalid'}), HTTPStatus.FORBIDDEN)


def body_validation(rrequest, param: str):
    if not rrequest.json.get(param):
        abort(400)


@role_bp.route("/add", methods=['POST'])
@jwt_required()
@admin_required()
@token_validation(request)
def add_role():
    body_validation(request, 'name')
    db = RoleService()
    return jsonify({'role': [db.add_role(name=request.json.get('name'),
                                         description=request.json.get('description')).as_dict]}
                   ), HTTPStatus.CREATED


@role_bp.route('/delete', methods=['DELETE'])
@jwt_required()
@admin_required()
@token_validation(request)
def delete_role():
    body_validation(request, 'id')
    db = RoleService()
    return jsonify({'deleted role': [db.del_role(request.json.get('id')).as_dict]}), HTTPStatus.OK


@role_bp.route('', methods=['GET'])
@jwt_required()
@admin_required()
@token_validation(request)
def show_roles_all():
    db = RoleService()
    return jsonify({'roles': [x.as_dict for x in db.show_all_roles()]}), HTTPStatus.OK


@role_bp.route('/<int:role_id>', methods=['GET'])
@jwt_required()
@admin_required()
@token_validation(request)
def show_role(role_id):
    db = RoleService()
    return jsonify({'role': [db.show_role(role_id).as_dict]}), HTTPStatus.OK


@role_bp.route('/update', methods=['PUT'])
@jwt_required()
@admin_required()
@token_validation(request)
def update_role():
    body_validation(request, 'id')
    db = RoleService()
    return jsonify({'role updated': [db.update_role(role_id=request.json.get('id'),
                                                    name=request.json.get('name'),
                                                    description=request.json.get('description')).as_dict]
                    }), HTTPStatus.CREATED
