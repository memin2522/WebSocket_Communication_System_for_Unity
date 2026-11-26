using System;
using System.Collections.Concurrent;
using System.Threading.Tasks;
using UnityEngine;

namespace WebSocketCommunication
{
    /// <summary>
    /// Controlador del cliente de visualización: recibe preguntas y respuestas
    /// del servidor y las publica como mensajes (por ejemplo, para texto a voz).
    /// </summary>
    public class DisplayController : MonoBehaviour
    {
        [SerializeField] private WebSocketService _websocketService;

        [Header("Messages")]
        [SerializeField] private string greetingMessage = "Hola, puedes hacerme preguntas";
        [SerializeField] private string readyMessage = "Ya estoy listo para responder tus preguntas";
        [Tooltip("{0} se reemplaza por la pregunta")]
        [SerializeField] private string questionEchoFormat = "Me preguntaste {0}";

        private ConcurrentQueue<string> AnswerQueue = new ConcurrentQueue<string>();
        private ConcurrentQueue<string> QuestionQueue = new ConcurrentQueue<string>();

        public event Action<string> OnLogRequested;
        public event Action<string> OnMessageReceived;

        void Start()
        {
            _websocketService.OnAnswerReceived += OnAnswerReceived;
            _websocketService.OnPreparedToCommunicate += OnPreparedToSpeak;
            _websocketService.OnQuestionReceived += OnQuestionReceived;
            OnMessageReceived?.Invoke(greetingMessage);
        }

        private void Update()
        {
            if (AnswerQueue.TryDequeue(out string answer))
            {
                OnLogRequested?.Invoke($"Received answer from server: {answer}");
                OnMessageReceived?.Invoke(answer);
            }

            if (QuestionQueue.TryDequeue(out string question))
            {
                OnLogRequested?.Invoke($"Received question from server: {question}");
                OnMessageReceived?.Invoke(string.Format(questionEchoFormat, question));
            }
        }

        private void OnPreparedToSpeak()
        {
            OnMessageReceived?.Invoke(readyMessage);
        }

        private void OnAnswerReceived(string answer)
        {
            AnswerQueue.Enqueue(answer);
        }

        private void OnQuestionReceived(string question)
        {
            QuestionQueue.Enqueue(question);
        }

        public void SendQuestion(string question)
        {
            _ = SendQuestionToServer(question);
        }

        private async Task SendQuestionToServer(string question)
        {
            OnLogRequested?.Invoke($"Sended from client: {question}");
            OnMessageReceived?.Invoke(string.Format(questionEchoFormat, question));
            await _websocketService.SendQuestion(question);
        }
    }
}
