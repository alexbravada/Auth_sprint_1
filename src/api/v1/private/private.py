from http import HTTPStatus

from flask import Blueprint, make_response, request, jsonify, abort
from sqlalchemy.exc import OperationalError

from services.resource_service import ResourceService
from services.user_service import UserService

private_bp = Blueprint('callback', __name__, url_prefix='/')


@private_bp.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), HTTPStatus.NOT_FOUND)


@private_bp.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Request data is invalid'}), HTTPStatus.BAD_REQUEST)


def validation_at_least_one(rrequest, method, param: tuple):
    '''
    хотя бы один из указанных в param ключей
    '''
    if method == 'get' or method == 'delete':
        if len(set(param).intersection(set(rrequest.args.keys()))) == 0:
            return False
        else:
            return True
    else:
        if len(set(param).intersection(set(rrequest.json.keys()))) == 0:
            return False
        else:
            return True


def validation_allowed(rrequest, method, param: tuple):
    '''
    только указанные в param ключи
    '''
    if method == 'get' or method == 'delete':
        if not set(rrequest.args.keys()).issubset(set(param)):
            return False
        else:
            return True
    else:
        if not set(rrequest.json.keys()).issubset(set(param)):
            return False
        else:
            return True


@private_bp.route('/check_permissions', methods=["GET"])
def check_permission():
    if not validation_allowed(request, 'get', ('role_id', 'resource_uuid', 'resource_type',)):
        abort(400)
    if validation_at_least_one(request, 'get', ('resource_uuid',)) and \
            validation_at_least_one(request, 'get', ('resource_type',)):
        role_id = request.args.get('role_id')
        try:
            return jsonify(ResourceService().check_permissions_role_resource(
                role_id=role_id if role_id else 1,
                resource_uuid=request.args.get('resource_uuid'),
                resource_type=request.args.get('resource_type')
            )), HTTPStatus.OK
        except OperationalError:
            return jsonify({
                'resource': {
                    'resource_uuid': request.args.get('resource_uuid'),
                    'resource_type': request.args.get('resource_type')
                },
                'permissions': {
                    'role_id': 1,
                    'can_create': False,
                    'can_read': False,
                    'can_update': False,
                    'can_delete': False
                }

            }), HTTPStatus.SERVICE_UNAVAILABLE
    else:
        abort(400)


@private_bp.route('/resources', methods=["POST"])
def create_resource():
    if not validation_allowed(request, 'post', (
            'resource_uuid', 'resource_type', 'resource_name', 'role_id', 'can_create', 'can_read', 'can_update',
            'can_delete',)):
        abort(400)
    if validation_at_least_one(request, 'post', ('resource_uuid',)) and \
            validation_at_least_one(request, 'post', ('resource_type',)):
        return jsonify(ResourceService().create_resource(**request.json)), HTTPStatus.CREATED
    else:
        abort(400)


@private_bp.route('/resources/<string:resource_type>/<string:resource_uuid>', methods=["GET"])
def read_resource_type_uuid(resource_type, resource_uuid):
    return jsonify(
        ResourceService().show_resource(resource_type=resource_type, resource_uuid=resource_uuid)
    ), HTTPStatus.OK


@private_bp.route('/resources', methods=["GET"])
def read_resource_any_params():
    if not validation_allowed(request, 'get', ('resource_id', 'resource_uuid', 'resource_type', 'resource_name',)):
        abort(400)
    return jsonify(ResourceService().show_resource(**request.args)), HTTPStatus.OK


@private_bp.route('/resources/<string:resource_type>/<string:resource_uuid>', methods=["PUT"])
def update_resource_type_uuid(resource_type, resource_uuid):
    if not validation_allowed(request, 'put', ('new_uuid', 'new_type', 'new_name',)):
        abort(400)
    if validation_at_least_one(request, 'put', ('new_uuid', 'new_type', 'new_name',)):
        return jsonify(ResourceService().update_resource(resource_type=resource_type, resource_uuid=resource_uuid,
                                                         **request.json)), HTTPStatus.OK
    else:
        abort(400)


@private_bp.route('/resources', methods=["PUT"])
def update_resource_id():
    if not validation_allowed(request, 'put',
                              ('new_uuid', 'new_type', 'new_name', 'resource_id', 'resource_uuid', 'resource_type',)):
        abort(400)

    if validation_at_least_one(request, 'put', ('resource_id',)) and \
            validation_at_least_one(request, 'put', ('new_uuid', 'new_type', 'new_name',)):
        return jsonify(ResourceService().update_resource(**request.json)), HTTPStatus.OK

    elif validation_at_least_one(request, 'put', ('resource_uuid', 'resource_type',)) and \
            validation_at_least_one(request, 'put', ('new_uuid', 'new_type', 'new_name',)):
        return jsonify(ResourceService().update_resource(**request.json)), HTTPStatus.OK

    else:
        abort(400)


@private_bp.route('/resources/<string:resource_type>/<string:resource_uuid>', methods=["DELETE"])
def delete_resource_type_uuid(resource_type, resource_uuid):
    return jsonify(ResourceService().delete_resource(
        resource_uuid=resource_uuid, resource_type=resource_type)), HTTPStatus.OK


@private_bp.route('/resources', methods=["DELETE"])
def delete_resource_id():
    if not validation_allowed(request, 'delete', ('resource_id', 'resource_uuid', 'resource_type',)):
        abort(400)
    if validation_at_least_one(request, 'delete', ('resource_id',)) or \
            validation_at_least_one(request, 'delete', ('resource_uuid', 'resource_type',)):
        return jsonify(ResourceService().delete_resource(**request.args)), HTTPStatus.OK
    else:
        abort(400)


@private_bp.route('/userinfo/<int:start_offset>/<int:end_offset>', methods=["GET"])
def get_user_info_batch(start_offset, end_offset):
    return jsonify(UserService().get_users_info(start_offset, end_offset), HTTPStatus.OK)
