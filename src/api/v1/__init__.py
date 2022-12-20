from flask import Blueprint

from .auth import auth_dir_bp
from .oauth import oauth_dir_bp
from .private import private_dir_bp


v1_blueprint = Blueprint('v1', __name__, url_prefix='/v1')

v1_blueprint.register_blueprint(auth_dir_bp)
v1_blueprint.register_blueprint(oauth_dir_bp)
v1_blueprint.register_blueprint(private_dir_bp)

