from flask import request
from flask_socketio import emit

from . import events
from .events import Relay


def register_ws_events(app):
    socketio = app.extensions["socketio"]
    session = app.extensions["ws_session"]
    role_names = {
        events.DISPLAY: app.config["ROLE_DISPLAY"],
        events.AI: app.config["ROLE_AI"],
    }

    def sid_of(role):
        return session.display_sid if role == events.DISPLAY else session.ai_sid

    def other(role):
        return events.AI if role == events.DISPLAY else events.DISPLAY

    @socketio.on(events.JOIN_SESSION)
    def join_session_event(role: str):
        if role == role_names[events.DISPLAY]:
            session.display_sid = request.sid
        elif role == role_names[events.AI]:
            session.ai_sid = request.sid
        else:
            return
        emit(events.SESSION_JOINED, {"message": f"{role} joined the session."}, room=request.sid)

    def make_relay_handler(relay: Relay):
        target = other(relay.sender)
        error_message = relay.error_message.format(
            display=role_names[events.DISPLAY], ai=role_names[events.AI]
        )
        missing_message = f"{role_names[relay.missing_label]} not connected yet"

        def relay_event(*payload):
            if request.sid != sid_of(relay.sender):
                emit(events.ERROR, {"message": error_message}, room=request.sid)
                return
            data = None
            if relay.payload_key is not None:
                data = {relay.payload_key: payload[0]}
                # La sesión guarda la última pregunta/respuesta, como el original
                if relay.incoming == "ask_question":
                    session.question = payload[0]
                elif relay.incoming == "send_answer":
                    session.answer = payload[0]
            target_sid = sid_of(target)
            if target_sid:
                if data is None:
                    emit(relay.outgoing, room=target_sid)
                else:
                    emit(relay.outgoing, data, room=target_sid)
            else:
                emit(events.INFO, {"message": missing_message}, room=request.sid)

        # Misma firma que los handlers originales: un argumento si el evento
        # lleva datos, ninguno si no los lleva.
        if relay.payload_key is not None:
            def handler(data):
                relay_event(data)
        else:
            def handler():
                relay_event()
        handler.__name__ = f"{relay.incoming}_event"
        return handler

    for relay in events.RELAYS:
        socketio.on_event(relay.incoming, make_relay_handler(relay))

    @socketio.on("disconnect")
    def on_disconnect(*_):
        if request.sid == session.display_sid:
            session.display_sid = None
        if request.sid == session.ai_sid:
            session.ai_sid = None
