from flask import Flask
from flask_smorest import Api
from flask_socketio import SocketIO

from .config import load_config
from .rest import blp as rest_blueprint, RestState
from .session import SessionData
from .ws_handlers import register_ws_events


def create_app(config_overrides=None):
    app = Flask(__name__)

    app.config.from_prefixed_env()
    app.config.update(load_config(config_overrides))
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

    socketio = SocketIO(app, cors_allowed_origins=app.config["CORS_ALLOWED_ORIGINS"])
    app.extensions["socketio"] = socketio
    app.extensions["ws_session"] = SessionData()
    app.extensions["rest_state"] = RestState()

    api = Api(app)
    api.register_blueprint(rest_blueprint)

    register_ws_events(app)

    return app
