from flask import Blueprint
from .authorize import authorize_bp
from .callback import callback_bp

oauth_dir_bp = Blueprint('oauth', __name__, url_prefix='/oauth')

oauth_dir_bp.register_blueprint(authorize_bp)
oauth_dir_bp.register_blueprint(callback_bp)
