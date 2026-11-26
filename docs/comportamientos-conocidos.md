# Comportamientos conocidos


Comportamientos heredados de la versión original que se conservaron sin cambios
para mantener la compatibilidad. Son candidatos a corrección en una versión futura.

1. **`POST /question` tiene la condición invertida:** solo guarda la pregunta si ya había una, así que siempre responde 400 y `GET /question` nunca devuelve una pregunta. Esta API REST era el mecanismo anterior a los WebSockets.
2. **Mensaje `info` con el rol equivocado:** en `init_activity`, `init_listen` y `end_listen`, cuando el cliente de IA no está conectado, el mensaje nombra al rol de visualización.
3. **`disconnect` emitido como evento:** el cliente web y el de Unity emiten `"disconnect"`, que es un nombre reservado de Socket.IO. En el cliente web (socket.io-client 4.x) eso lanza un error y el botón **Disconnect** no llega a ejecutar `socket.close()`.
4. **El cliente web no tiene botones** para `init_activity`, `init_listen`, `end_listen`, `approach_camera`, `retreat_camera` ni `ready_listen`, que se agregaron al servidor después.
5. **Sin autenticación:** cualquier cliente puede unirse con cualquier rol, y una nueva conexión con un rol ya registrado reemplaza a la anterior.
6. **Una sola sesión por proceso:** el servidor debe ejecutarse con un solo worker.
7. **eventlet está obsoleto** según sus mantenedores. Funciona, pero conviene migrar en una versión futura.
8. **Unity interpreta el JSON recibido quitando los corchetes** del arreglo de argumentos (`TrimStart('[')`/`TrimEnd(']')`).
