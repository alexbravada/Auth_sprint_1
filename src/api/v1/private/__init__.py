from flask import Blueprint
from .private import private_bp


private_dir_bp = Blueprint('private', __name__, url_prefix='/private')

private_dir_bp.register_blueprint(private_bp)
