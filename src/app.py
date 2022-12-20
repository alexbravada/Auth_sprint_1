from flask import Flask, render_template, request
from flask_jwt_extended import JWTManager
from flask.cli import with_appcontext
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
import click

from config.settings import Settings
from db.user_service import UserService
from api import api_blueprint


SETTINGS = Settings()

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


@app.before_request
def before_request():
    request_id = request.headers.get('X-Request-Id')
    if not request_id:
        raise RuntimeError('request id is required')


def configure_tracer() -> None:
    jaegersettings = SETTINGS.Jaeger.dict()
    trace.set_tracer_provider(TracerProvider())
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(
            JaegerExporter(
                agent_host_name=jaegersettings.get('host'),
                agent_port=jaegersettings.get('port'),
            )
        )
    )
    trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))


configure_tracer()
FlaskInstrumentor().instrument_app(app)

app.cli.add_command(create_admin)

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8005,
        debug=True
    )
