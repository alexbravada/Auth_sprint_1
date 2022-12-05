from flask import Blueprint
from flask import request

from oauth import oauth_service

callback_bp = Blueprint('callback', __name__, url_prefix='/callback')


@callback_bp.route('/vk', methods=['GET'])
def callback_vk():
    vk_code = request.args.get('code')
    vk_instance = oauth_service.VKOAuth()
    return vk_instance.callback(vk_code)
