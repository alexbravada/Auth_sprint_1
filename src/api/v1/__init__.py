from flask import Blueprint

from .auth import auth_dir_bp


v1_blueprint = Blueprint('v1', __name__, url_prefix='/v1')

v1_blueprint.register_blueprint(auth_dir_bp)
