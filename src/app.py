from flask import Flask, render_template
from flask_jwt_extended import JWTManager
import click
from flask.cli import with_appcontext

from db.user_service import UserService
from api import api_blueprint

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'changeme'
jwt = JWTManager(app)

app.register_blueprint(api_blueprint)


@app.route('/')
def get_docs():
    return render_template('swaggerui.html')


@click.command(name='create-superuser')
@click.argument('email')
@click.argument('password')
@with_appcontext
def create_admin(email, password):
    db = UserService()
    db.admin_register(email=email,
                      password=password)


app.cli.add_command(create_admin)

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8005,
        debug=True
    )
