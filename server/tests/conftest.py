import pytest

from app import create_app


@pytest.fixture
def app():
    return create_app({"ROLE_DISPLAY": "display", "ROLE_AI": "ai"})


@pytest.fixture
def socketio(app):
    return app.extensions["socketio"]


@pytest.fixture
def http(app):
    return app.test_client()


def received(client, name=None):
    """Eventos recibidos por un cliente de prueba como lista de (nombre, args)."""
    out = [(e["name"], e["args"]) for e in client.get_received()]
    if name is not None:
        out = [e for e in out if e[0] == name]
    return out


@pytest.fixture
def joined(app, socketio):
    """Cliente de visualización y cliente de IA ya unidos a la sesión."""
    display = socketio.test_client(app)
    ai = socketio.test_client(app)
    display.emit("join_session", "display")
    ai.emit("join_session", "ai")
    display.get_received()
    ai.get_received()
    return display, ai
