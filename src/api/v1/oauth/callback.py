from http import HTTPStatus

from flask import Blueprint
from flask import request
from flask import jsonify

from oauth import oauth_service

callback_bp = Blueprint('callback', __name__, url_prefix='/callback')


@callback_bp.route('/vk', methods=['GET'])
def callback_vk():
    vk_code = request.args.get('code')
    vk_instance = oauth_service.VKOAuth()
    return jsonify(vk_instance.callback(vk_code, useragent=request.headers.get('User-Agent'))), HTTPStatus.OK
