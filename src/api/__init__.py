from flask import Blueprint
from .v1 import v1_blueprint


api_blueprint = Blueprint('api', __name__, url_prefix='/api')

api_blueprint.register_blueprint(v1_blueprint)
