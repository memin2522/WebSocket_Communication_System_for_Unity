# WebSocket Communication System for Unity

Middleware en tiempo real que retransmite eventos Socket.IO entre un **cliente
de visualización** (por ejemplo, una aplicación Unity) y un **cliente de IA**
(por ejemplo, un servicio de reconocimiento de voz y generación de respuestas).

Versión 1.0.0 · 2026

## Componentes

| Carpeta | Componente | Tecnología |
|---|---|---|
| `server/` | Middleware de eventos con API REST, `/health` y documentación OpenAPI | Python 3.12, Flask, Flask-SocketIO |
| `clients/web-tester/` | Cliente web para probar los eventos a mano | Node.js, Express, Socket.IO JS |
| `clients/unity/` | Scripts del cliente de visualización para Unity | C#, Unity 6, SocketIOClient |

## Inicio rápido

```sh
cp .env.example .env        # opcional
docker compose up --build
```

- Servidor: <http://localhost:5000> (salud en `/health`, documentación en `/swagger-ui`)
- Cliente web de pruebas: <http://localhost:3000>

Pruebas del servidor:

```sh
cd server
python -m venv .venv && . .venv/bin/activate
pip install -r requirements-dev.txt
pytest
```

## Documentación

- [Descripción técnica](docs/descripcion-tecnica.md)
- [Manual de instalación y uso](docs/manual-instalacion-uso.md)
- [Comportamientos conocidos](docs/comportamientos-conocidos.md)
- [Cliente Unity](clients/unity/README.md)

## Configuración

Toda la configuración se hace con variables de entorno. Ver `.env.example`.
Los nombres de los roles (`ROLE_DISPLAY`, `ROLE_AI`) son configurables.
