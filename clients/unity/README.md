# Cliente de visualización para Unity

Scripts C# que conectan una escena de Unity al middleware como **cliente de
visualización**. El cliente envía preguntas al servidor y recibe respuestas
(`answer`) y preguntas escuchadas por el cliente de IA (`question_listened`).
Cada mensaje se puede mostrar en un registro en pantalla y reproducir con texto
a voz.

## Contenido

```
clients/unity/
├── Assets/Scripts/
│   ├── DisplayController.cs        # recibe/envía mensajes y los publica como eventos
│   ├── Service/WebSocketService.cs # conexión Socket.IO (URL y rol configurables)
│   ├── Service/TtsService.cs       # texto a voz con Meta Voice SDK (opcional)
│   ├── UI/LogUIController.cs       # registro en pantalla y campo para preguntar
│   └── Data/                       # nombres de eventos y clases de payload
├── Packages/manifest.json          # paquetes de Unity requeridos
├── ProjectSettings/ProjectVersion.txt
└── tools/fetch-socketio-dlls.sh    # descarga las DLL de Socket.IO desde NuGet
```

No incluye escenas, modelos 3D, texturas ni DLL de terceros.

## Requisitos

- Unity **6000.2.12f1** (o compatible con Unity 6).
- SDK de .NET (solo para descargar las DLL con el script).
- Paquetes de `Packages/manifest.json`. Unity los instala al abrir el proyecto.
  Incluye `com.meta.xr.sdk.voice` 77.0.0 (Meta Voice SDK), que solo necesita
  `TtsService.cs`.
- TextMesh Pro: al abrir el proyecto, *Window → TextMeshPro → Import TMP
  Essential Resources*.

## Instalación

1. Abre `clients/unity/` desde Unity Hub (*Add project from disk*).
2. Descarga las DLL del cliente Socket.IO:
   ```sh
   ./tools/fetch-socketio-dlls.sh
   ```
   El script copia en `Assets/Plugins/SocketIO/` la librería SocketIOClient 3.1.2
   con sus dependencias (Newtonsoft.Json, System.Text.Json, etc.).
3. Si vas a usar texto a voz, configura en el Meta Voice SDK **tu propio** token
   de Wit.ai (*Meta → Voice SDK → Settings*). El repositorio no incluye
   ningún token.

## Configuración de la escena

1. Crea un GameObject y agrégale `WebSocketService`:
   - **Server Url:** URL del middleware, por ejemplo `http://localhost:5000/`.
   - **Role:** debe coincidir con `ROLE_DISPLAY` del servidor (por defecto
     `display`).
2. Agrega `DisplayController` y asigna el `WebSocketService`. Los mensajes de
   saludo, de "listo" y el formato de eco de la pregunta se editan desde el
   Inspector.
3. (Opcional) Agrega `TtsService` con un `TTSSpeaker` del Meta Voice SDK y el
   `DisplayController`.
4. (Opcional) Crea un Canvas con un `TMP_InputField`, un `TextMeshProUGUI`
   y un botón, y conéctalos a `LogUIController`. El botón llama a
   `OnSendButtonClicked()`, y `ToggleLogUI()` muestra u oculta el registro.

## Flujo

1. Al conectarse, el cliente emite `join_session` con su rol y
   `DisplayController` publica el mensaje de "listo".
2. `SendQuestion(texto)` emite `ask_question`.
3. Al recibir `answer` o `question_listened`, el mensaje entra en una cola
   concurrente y se procesa en el hilo principal (`Update`).
