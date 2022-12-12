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

@callback_bp.route('/yandex', methods=['GET'])
def callback_yandex():
    yandex_code = request.args.get('code')
    yandex_instance = oauth_service.YandexOAuth()
    return jsonify(yandex_instance.callback(yandex_code, useragent=request.headers.get('User-Agent'))), HTTPStatus.OK
