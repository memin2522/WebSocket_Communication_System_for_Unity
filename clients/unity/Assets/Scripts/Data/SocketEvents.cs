namespace WebSocketCommunication
{
    /// <summary>
    /// Nombres de los eventos Socket.IO que usa el cliente de visualización.
    /// Deben coincidir con el catálogo del servidor (server/app/events.py).
    /// </summary>
    public static class SocketEvents
    {
        // Cliente -> servidor
        public const string JoinSession = "join_session";
        public const string AskQuestion = "ask_question";
        public const string Disconnect = "disconnect";

        // Servidor -> cliente
        public const string Answer = "answer";
        public const string QuestionListened = "question_listened";
    }
}
