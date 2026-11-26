# Manual de instalación y uso

**Software:** WebSocket Communication System for Unity · **Versión:** 1.0.0

## 1. Requisitos

| Para | Requisito |
|---|---|
| Ejecutar todo con contenedores | Docker 24+ con Docker Compose v2.24+ |
| Ejecutar el servidor sin Docker | Python 3.11 o superior |
| Ejecutar el cliente web sin Docker | Node.js 20 o superior |
| Cliente Unity | Unity 6000.2.12f1 y SDK de .NET (para descargar las DLL) |

## 2. Instalación con Docker (recomendada)

```sh
cd WebSocket_Communication_System_for_Unity
cp .env.example .env          # opcional: ajustar puertos y roles
docker compose up --build -d
docker compose ps             # el servicio "server" debe aparecer como healthy
```

| Servicio | URL |
|---|---|
| Middleware | http://localhost:5000 |
| Salud | http://localhost:5000/health → `OK` |
| Documentación de la API | http://localhost:5000/swagger-ui |
| Cliente web de pruebas | http://localhost:3000 |

Para detenerlo: `docker compose down`.

## 3. Instalación sin Docker

### 3.1 Servidor

```sh
cd server
python -m venv .venv
. .venv/bin/activate                 # Windows: .venv\Scripts\activate
pip install -r requirements.txt
gunicorn -k eventlet -w 1 -b 0.0.0.0:5000 wsgi:app
```

Las variables de entorno (`ROLE_DISPLAY`, `ROLE_AI`, etc.) se pueden exportar
antes de ejecutar o poner en un archivo `.env` dentro de `server/`.

> Usa siempre **un solo worker** (`-w 1`): la sesión se guarda en la memoria del proceso.

### 3.2 Cliente web de pruebas

```sh
cd clients/web-tester
npm ci
SERVER_URL=http://localhost:5000 npm start
```

### 3.3 Cliente Unity

Ver `clients/unity/README.md`.

## 4. Configuración

Copia `.env.example` como `.env`. Todas las variables son opcionales:

| Variable | Por defecto | Descripción |
|---|---|---|
| `SERVER_PORT` | 5000 | Puerto del servidor |
| `ROLE_DISPLAY` | display | Rol que envía el cliente de visualización en `join_session` |
| `ROLE_AI` | ai | Rol que envía el cliente de IA en `join_session` |
| `CORS_ALLOWED_ORIGINS` | * | `*` o lista separada por comas |
| `API_TITLE` | WebSocket Communication System | Título mostrado en `/` y en OpenAPI |
| `WEB_TESTER_PORT` | 3000 | Puerto del cliente web |
| `SERVER_PUBLIC_URL` | http://localhost:5000 | URL del servidor que usa el navegador |

**Compatibilidad con clientes existentes:** si tus clientes envían otros
nombres de rol (por ejemplo `unity` e `ia`), configura `ROLE_DISPLAY=unity` y
`ROLE_AI=ia`. Los nombres de los dos roles deben ser distintos.

## 5. Uso

### 5.1 Probar con el cliente web

1. Abre http://localhost:3000 en **dos pestañas** y la consola del navegador (F12) en cada una.
2. En la pestaña 1 elige *Display client* y pulsa **Join as role**. En la pestaña 2 elige *AI client* y pulsa **Join as role**. Cada pestaña muestra `Session Joined` en la consola.
3. En la pestaña 1 escribe una pregunta y pulsa **Send Question**. La pestaña 2 muestra `Question Received`.
4. En la pestaña 2 escribe una respuesta y pulsa **Send Answer**. La pestaña 1 muestra `Answer Received`.
5. En la pestaña 2, **Simulate a listened question** envía `question_listened` a la pestaña 1.

### 5.2 Integrar un cliente propio

Cualquier cliente Socket.IO (protocolo v5: socket.io-client 4.x, python-socketio 5.x, SocketIOClient 3.x para .NET) puede conectarse:

```js
const socket = io("http://localhost:5000", { transports: ["websocket"] });
socket.emit("join_session", "ai");
socket.on("question", ({ question }) => {
  socket.emit("send_answer", `Respuesta a: ${question}`);
});
```

El catálogo completo de eventos está en `docs/descripcion-tecnica.md`, sección 3.

### 5.3 Ejecutar las pruebas

```sh
cd server
pip install -r requirements-dev.txt
pytest
```

Resultado esperado: `37 passed`.

## 6. Solución de problemas

| Síntoma | Causa probable | Solución |
|---|---|---|
| El cliente recibe `info: ... not connected yet` | El otro rol no se ha unido | Une el otro cliente con `join_session` |
| El cliente recibe `error: Only ... can ...` | El evento no corresponde a su rol, o no se unió a la sesión | Revisa el rol enviado en `join_session` y `ROLE_DISPLAY`/`ROLE_AI` |
| `join_session` no responde | El rol enviado no coincide con ninguno de los configurados | Ajusta el rol del cliente o las variables del servidor |
| Error de CORS en el navegador | Origen no permitido | Agrega el origen a `CORS_ALLOWED_ORIGINS` |
| `server` no aparece como *healthy* | El servidor no arrancó | `docker compose logs server` |
| Los mensajes se pierden con varios workers | La sesión está en memoria | Usa `-w 1` |
