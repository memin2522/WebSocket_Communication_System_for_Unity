"""Catálogo único de eventos Socket.IO.

Cada evento de retransmisión (Relay) llega de un rol emisor y se reenvía al
rol destino con otro nombre. Los roles se nombran de forma abstracta
("display" / "ai"); el nombre real que usan los clientes en join_session se
configura con ROLE_DISPLAY y ROLE_AI.
"""
from dataclasses import dataclass
from typing import Optional

DISPLAY = "display"
AI = "ai"

# Eventos de control
JOIN_SESSION = "join_session"      # cliente -> servidor, payload: nombre del rol
SESSION_JOINED = "session_joined"  # servidor -> cliente, {"message": str}
ERROR = "error"                    # servidor -> emisor, {"message": str}
INFO = "info"                      # servidor -> emisor, {"message": str}


@dataclass(frozen=True)
class Relay:
    incoming: str               # evento que recibe el servidor
    sender: str                 # rol autorizado a enviarlo (DISPLAY o AI)
    outgoing: str               # evento que se emite al otro rol
    payload_key: Optional[str]  # clave del payload reenviado; None si no lleva datos
    error_message: str          # plantilla; {display} y {ai} se reemplazan por los roles
    # Rol que se nombra en el mensaje "info" cuando el destino no está conectado.
    # Normalmente es el destino; en tres eventos el original nombra al emisor y
    # se conserva así (ver docs/comportamientos-conocidos.md).
    missing_label: str


RELAYS = (
    # Visualización -> IA
    Relay("ask_question", DISPLAY, "question", "question",
          "Only {display} can send questions", AI),
    Relay("init_activity", DISPLAY, "on_activity_init", None,
          "Only {display} can init the activity", DISPLAY),
    Relay("init_listen", DISPLAY, "on_init_listen", None,
          "Only {display} can send this event", DISPLAY),
    Relay("end_listen", DISPLAY, "on_end_listen", None,
          "Only {display} can send this event", DISPLAY),
    # IA -> Visualización
    Relay("send_answer", AI, "answer", "answer",
          "Only {ai} can send answers", DISPLAY),
    Relay("approach_camera", AI, "on_approach_camera", None,
          "Only the {ai} can send this event", DISPLAY),
    Relay("retreat_camera", AI, "on_retreat_camera", None,
          "Only the {ai} can send this event", DISPLAY),
    Relay("question_listened", AI, "question_listened", "question",
          "Only the {ai} can confirm listened questions", DISPLAY),
    Relay("ready_listen", AI, "on_ready_listen", None,
          "Only the {ai} can send this event", DISPLAY),
)
