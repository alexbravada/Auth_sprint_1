from flask import Blueprint
from .user_route import user_bp
from .user_role_route import user_role_bp
from .role_route import role_bp


auth_dir_bp = Blueprint('auth', __name__, url_prefix='/auth')

auth_dir_bp.register_blueprint(user_bp)
auth_dir_bp.register_blueprint(role_bp)
auth_dir_bp.register_blueprint(user_role_bp)
