# Descripción técnica

**Software:** WebSocket Communication System for Unity · **Versión:** 1.0.0 · **Año:** 2026

## 1. Propósito

El sistema comunica en tiempo real dos aplicaciones independientes que no se
conocen entre sí:

- un **cliente de visualización**, que muestra contenido al público (por
  ejemplo, un personaje 3D en Unity en una pantalla de señalización digital), y
- un **cliente de IA**, que escucha, interpreta y genera respuestas (por
  ejemplo, un servicio de voz a texto y de generación de respuestas).

Un servidor intermedio (*middleware*) recibe los eventos de cada cliente,
valida que el emisor tenga el rol autorizado y los reenvía al otro cliente.
Así, cada aplicación puede desarrollarse y desplegarse por separado.

## 2. Arquitectura

```
┌──────────────────────┐   Socket.IO (WebSocket)  ┌───────────────────────┐   Socket.IO (WebSocket)  ┌──────────────────────┐
│ Cliente de           │ ───────────────────────▶ │  Middleware (server/) │ ───────────────────────▶ │ Cliente de IA        │
│ visualización        │ ◀─────────────────────── │  Flask + Flask-SocketIO│ ◀─────────────────────── │ (externo)            │
│ (clients/unity/)     │                          │  Sesión única en      │                          │                      │
└──────────────────────┘                          │  memoria              │                          └──────────────────────┘
                                                  │  REST: /, /health,    │
┌──────────────────────┐   Socket.IO              │  /question, /answer   │
│ Cliente web de       │ ───────────────────────▶ │  OpenAPI: /swagger-ui │
│ pruebas (web-tester) │   (simula cualquier rol) └───────────────────────┘
└──────────────────────┘
```

### 2.1 Middleware (`server/`)

| Módulo | Responsabilidad |
|---|---|
| `app/__init__.py` | *Factory* `create_app()`: configuración, Socket.IO, API REST, registro de eventos |
| `app/config.py` | Lectura de variables de entorno y validación (roles distintos) |
| `app/events.py` | Catálogo único de eventos: nombre de entrada, rol emisor, evento de salida, payload y mensajes |
| `app/ws_handlers.py` | Registro de los manejadores Socket.IO a partir del catálogo |
| `app/session.py` | `SessionData`: identificador de conexión (`sid`) de cada rol y la última pregunta y respuesta |
| `app/rest.py` | Endpoints REST y estado del mecanismo de consulta periódica |
| `app/schemas.py` | Esquemas marshmallow de pregunta y respuesta |
| `wsgi.py` | Punto de entrada para gunicorn |

El servidor mantiene **una sola sesión en memoria**, con un cliente de
visualización y un cliente de IA. Por eso debe ejecutarse con **un solo
proceso** de gunicorn (`-w 1`) y el worker asíncrono `eventlet`.

### 2.2 Cliente web de pruebas (`clients/web-tester/`)

Es un servidor Express que entrega una página HTML. La página se conecta al
middleware y permite unirse con cualquiera de los dos roles, enviar preguntas,
respuestas y preguntas escuchadas, y ver en la consola del navegador los
eventos que llegan. La URL del servidor y los nombres de los roles se
entregan al navegador en `/config.js`, a partir de las variables de entorno.

### 2.3 Cliente de visualización Unity (`clients/unity/`)

| Script | Responsabilidad |
|---|---|
| `WebSocketService` | Conexión Socket.IO, `join_session` con el rol configurado, recepción de `answer` y `question_listened` |
| `DisplayController` | Colas concurrentes de mensajes, procesadas en el hilo principal; publica eventos de registro y de mensaje |
| `TtsService` | Reproduce cada mensaje con texto a voz (Meta Voice SDK) |
| `LogUIController` | Registro en pantalla y campo de texto para enviar preguntas |
| `SocketEvents`, `SocketPayloads` | Nombres de eventos y clases de los datos JSON |

## 3. Catálogo de eventos Socket.IO

Los roles se nombran *display* (visualización) y *ai* (IA). El nombre real que
envía cada cliente en `join_session` se configura con `ROLE_DISPLAY` y `ROLE_AI`.

### 3.1 Eventos de control

| Evento | Dirección | Payload | Descripción |
|---|---|---|---|
| `join_session` | cliente → servidor | `"<rol>"` (texto) | Registra la conexión con ese rol. Un rol desconocido se ignora. Si el rol ya estaba registrado, la nueva conexión lo reemplaza. |
| `session_joined` | servidor → cliente | `{"message": "<rol> joined the session."}` | Confirma el registro. |
| `error` | servidor → emisor | `{"message": str}` | El emisor no tiene el rol autorizado para el evento. |
| `info` | servidor → emisor | `{"message": "<rol> not connected yet"}` | El destinatario no está conectado. |
| `disconnect` | — | — | Al desconectarse, se libera el rol de esa conexión. |

### 3.2 Eventos retransmitidos

| Evento recibido | Emisor autorizado | Evento reenviado | Destino | Payload reenviado |
|---|---|---|---|---|
| `ask_question` | display | `question` | ai | `{"question": str}` |
| `init_activity` | display | `on_activity_init` | ai | — |
| `init_listen` | display | `on_init_listen` | ai | — |
| `end_listen` | display | `on_end_listen` | ai | — |
| `send_answer` | ai | `answer` | display | `{"answer": str}` |
| `question_listened` | ai | `question_listened` | display | `{"question": str}` |
| `approach_camera` | ai | `on_approach_camera` | display | — |
| `retreat_camera` | ai | `on_retreat_camera` | display | — |
| `ready_listen` | ai | `on_ready_listen` | display | — |

## 4. Endpoints HTTP

| Método | Ruta | Respuesta | Descripción |
|---|---|---|---|
| GET | `/` | 200, HTML | Página de verificación con el título configurado (`API_TITLE`) |
| GET | `/health` | 200, `OK` | Verificación de salud (usada por Docker) |
| POST | `/answer` | 201, `{"answer": str}` | Guarda una respuesta (consulta periódica) |
| GET | `/answer` | 200 `{"answer": str}` o 400 | Entrega la respuesta guardada y la borra |
| POST | `/question` | 201 o 400 | Guarda una pregunta (ver docs/comportamientos-conocidos.md) |
| GET | `/question` | 201 `{"question": str}` o 400 | Entrega la pregunta guardada y la borra |
| GET | `/openapi.json` | 200 | Especificación OpenAPI 3.0.3 |
| GET | `/swagger-ui` | 200 | Documentación interactiva |

## 5. Flujos

**Conexión.** Cada cliente se conecta por WebSocket y emite `join_session`
con su rol. El servidor guarda su `sid` y responde `session_joined`.

**Pregunta escrita.**
1. El cliente de visualización emite `ask_question("texto")`.
2. El servidor la reenvía al cliente de IA como `question {"question": "texto"}`.
3. El cliente de IA responde con `send_answer("respuesta")`.
4. El servidor la reenvía al cliente de visualización como `answer {"answer": "respuesta"}`.

**Pregunta por voz.**
1. El cliente de visualización emite `init_listen`, que llega a la IA como `on_init_listen`.
2. Cuando la IA está lista, emite `ready_listen`, que llega como `on_ready_listen`.
3. La IA transcribe la pregunta y emite `question_listened`, que llega a la visualización con el texto.
4. La visualización emite `end_listen` (llega como `on_end_listen`).
5. La IA responde con `send_answer` (llega como `answer`).

**Actividad y cámara.** La visualización emite `init_activity` (llega a la
IA como `on_activity_init`). La IA emite `approach_camera` o `retreat_camera`
para que la visualización acerque o aleje la cámara.

**Errores.** Si un cliente emite un evento que no le corresponde a su rol,
recibe `error` y no se reenvía nada. Si el destinatario no está conectado,
el emisor recibe `info`.

## 6. Configuración

| Variable | Por defecto | Uso |
|---|---|---|
| `ROLE_DISPLAY` | `display` | Nombre del rol de visualización |
| `ROLE_AI` | `ai` | Nombre del rol de IA |
| `CORS_ALLOWED_ORIGINS` | `*` | Orígenes permitidos para Socket.IO |
| `API_TITLE` | `WebSocket Communication System` | Título de la API |
| `SERVER_PORT` / `PORT` | `5000` | Puerto del servidor |
| `WEB_TESTER_PORT` | `3000` | Puerto del cliente web |
| `SERVER_PUBLIC_URL` / `SERVER_URL` | `http://localhost:5000` | URL del servidor que usa el navegador |

## 7. Tecnologías y lenguajes

| Lenguaje | Uso | Líneas (sin vacías) |
|---|---|---|
| Python 3.12 | Middleware y pruebas | 365 |
| C# | Cliente Unity | 216 |
| JavaScript | Cliente web de pruebas | 105 |
| HTML | Cliente web de pruebas | 33 |

Tecnologías: Flask 3.1, Flask-SocketIO 5.7 (protocolo Socket.IO 5), flask-smorest
(OpenAPI 3), marshmallow, eventlet, gunicorn; Node.js 22 y Express 5; Unity 6
(6000.2.12f1), SocketIOClient 3.1.2 para .NET y Meta Voice SDK 77; Docker y
Docker Compose; pytest.

## 8. Pruebas

`server/tests/` contiene 37 pruebas automáticas (pytest):

- unión a la sesión, con roles válidos y desconocidos;
- retransmisión de cada uno de los 9 eventos al rol destino;
- rechazo con `error` cuando emite un rol no autorizado;
- mensaje `info` cuando el destino no está conectado;
- liberación del rol al desconectarse;
- compatibilidad con roles personalizados (`unity`/`ia`) y validación de roles iguales;
- endpoints `/health`, `/`, `/answer`, `/question` y `/openapi.json`.
