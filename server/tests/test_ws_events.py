import pytest

from app import create_app
from app.events import RELAYS, DISPLAY
from conftest import received


def test_join_session_confirma_rol(app, socketio):
    client = socketio.test_client(app)
    client.emit("join_session", "display")
    assert received(client) == [
        ("session_joined", [{"message": "display joined the session."}])
    ]


def test_join_session_rol_desconocido_se_ignora(app, socketio):
    client = socketio.test_client(app)
    client.emit("join_session", "otro")
    assert received(client) == []
    assert app.extensions["ws_session"].display_sid is None
    assert app.extensions["ws_session"].ai_sid is None


@pytest.mark.parametrize("relay", RELAYS, ids=lambda r: r.incoming)
def test_retransmision_al_otro_rol(joined, relay):
    display, ai = joined
    sender, target = (display, ai) if relay.sender == DISPLAY else (ai, display)
    if relay.payload_key:
        sender.emit(relay.incoming, "hola")
        expected = [{relay.payload_key: "hola"}]
    else:
        sender.emit(relay.incoming)
        expected = []
    assert received(target) == [(relay.outgoing, expected)]
    assert received(sender) == []


@pytest.mark.parametrize("relay", RELAYS, ids=lambda r: r.incoming)
def test_rol_no_autorizado_recibe_error(joined, relay):
    display, ai = joined
    wrong, other = (ai, display) if relay.sender == DISPLAY else (display, ai)
    if relay.payload_key:
        wrong.emit(relay.incoming, "x")
    else:
        wrong.emit(relay.incoming)
    events = received(wrong)
    assert len(events) == 1 and events[0][0] == "error"
    assert received(other) == []


@pytest.mark.parametrize("relay", RELAYS, ids=lambda r: r.incoming)
def test_destino_desconectado_recibe_info(app, socketio, relay):
    sender = socketio.test_client(app)
    role = "display" if relay.sender == DISPLAY else "ai"
    sender.emit("join_session", role)
    sender.get_received()
    if relay.payload_key:
        sender.emit(relay.incoming, "x")
    else:
        sender.emit(relay.incoming)
    expected_label = "display" if relay.missing_label == DISPLAY else "ai"
    assert received(sender) == [
        ("info", [{"message": f"{expected_label} not connected yet"}])
    ]


def test_desconexion_libera_el_rol(app, joined):
    display, _ = joined
    display.disconnect()
    assert app.extensions["ws_session"].display_sid is None
    assert app.extensions["ws_session"].ai_sid is not None


def test_roles_configurables_compatibles_con_clientes_originales():
    app = create_app({"ROLE_DISPLAY": "unity", "ROLE_AI": "ia"})
    sio = app.extensions["socketio"]
    unity, ia = sio.test_client(app), sio.test_client(app)
    unity.emit("join_session", "unity")
    ia.emit("join_session", "ia")
    unity.get_received()
    ia.get_received()
    unity.emit("ask_question", "¿hola?")
    assert received(ia) == [("question", [{"question": "¿hola?"}])]
    ia.emit("send_answer", "respuesta")
    assert received(unity) == [("answer", [{"answer": "respuesta"}])]


def test_roles_iguales_no_se_permiten():
    with pytest.raises(ValueError):
        create_app({"ROLE_DISPLAY": "x", "ROLE_AI": "x"})
