from flask import Blueprint

from oauth import oauth_service

authorize_bp = Blueprint('authorize', __name__, url_prefix='/authorize')


@authorize_bp.route('/vk', methods=['GET'])
def authorize_vk():
    vk_instance = oauth_service.VKOAuth()
    return vk_instance.authorize()


@authorize_bp.route('/yandex', methods=['GET'])
def authorize_yandex():
    yandex_instance = oauth_service.YandexOAuth()
    return yandex_instance.authorize()


@authorize_bp.route('/google', methods=['GET'])
def authorize_google():
    google_instance = oauth_service.GoogleOAuth()
    return google_instance.authorize()
