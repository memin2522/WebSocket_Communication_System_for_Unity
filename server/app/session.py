from dataclasses import dataclass
from typing import Optional


@dataclass
class SessionData:
    """Sesión única del servidor: un cliente de visualización y un cliente de IA."""

    display_sid: Optional[str] = None
    ai_sid: Optional[str] = None
    question: Optional[str] = None
    answer: Optional[str] = None
