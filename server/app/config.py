"""Configuración del servidor a partir de variables de entorno.

Todas las variables tienen un valor por defecto, de modo que el servidor
arranca sin archivo .env. Ver .env.example en la raíz del repositorio.
"""
import os

DEFAULTS = {
    # Nombre con el que se identifica el cliente de visualización en join_session
    "ROLE_DISPLAY": "display",
    # Nombre con el que se identifica el cliente de IA en join_session
    "ROLE_AI": "ai",
    # Orígenes permitidos para CORS de Socket.IO ("*" o lista separada por comas)
    "CORS_ALLOWED_ORIGINS": "*",
    # Título mostrado en la página principal y en la documentación OpenAPI
    "API_TITLE": "WebSocket Communication System",
    "API_VERSION": "V1",
}


def load_config(overrides=None):
    """Devuelve la configuración efectiva: valores por defecto < entorno < overrides."""
    config = {key: os.getenv(key, default) for key, default in DEFAULTS.items()}
    if overrides:
        config.update(overrides)

    if config["ROLE_DISPLAY"] == config["ROLE_AI"]:
        raise ValueError("ROLE_DISPLAY y ROLE_AI deben ser distintos")

    origins = config["CORS_ALLOWED_ORIGINS"]
    if isinstance(origins, str) and origins != "*":
        config["CORS_ALLOWED_ORIGINS"] = [o.strip() for o in origins.split(",") if o.strip()]

    return config
