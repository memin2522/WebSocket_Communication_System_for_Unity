using SocketIOClient;
using System;
using System.Threading.Tasks;
using UnityEngine;

namespace WebSocketCommunication
{
    public class WebSocketService : MonoBehaviour
    {
        [Header("Server Configuration")]
        [Tooltip("URL of the middleware server")]
        [SerializeField] string serverUrl = "http://localhost:5000/";

        [Tooltip("Role name sent in join_session. Must match ROLE_DISPLAY on the server")]
        [SerializeField] string role = "display";

        SocketIOClient.SocketIO client;
        public Action<string> OnAnswerReceived;
        public Action<string> OnQuestionReceived;
        public Action OnPreparedToCommunicate;

        async void Start()
        {
            client = new SocketIOClient.SocketIO(serverUrl, new SocketIOOptions
            {
                Transport = SocketIOClient.Transport.TransportProtocol.WebSocket
            });

            client.OnConnected += async (s, e) =>
            {
                Debug.Log("[SocketIO] Display client successfully connected to the server");
                OnPreparedToCommunicate();
                await client.EmitAsync(SocketEvents.JoinSession, role);
            };

            client.OnDisconnected += async (s, e) =>
            {
                Debug.LogWarning("[SocketIO] Disconnected from the server");
                await client.EmitAsync(SocketEvents.Disconnect);
            };

            client.On(SocketEvents.Answer, response =>
            {
                string json = response.ToString();

                json = json.TrimStart('[').TrimEnd(']');

                AnswerResponse data = JsonUtility.FromJson<AnswerResponse>(json);
                Debug.Log($"Answer recevied: {data.answer}");
                OnAnswerReceived(data.answer);
            });

            client.On(SocketEvents.QuestionListened, response =>
            {
                string json = response.ToString();

                json = json.TrimStart('[').TrimEnd(']');

                QuestionResponse data = JsonUtility.FromJson<QuestionResponse>(json);
                Debug.Log($"Question recevied: {data.question}");
                OnQuestionReceived(data.question);
            });

            try
            {
                await client.ConnectAsync();
            }
            catch (Exception ex)
            {
                Debug.LogError("[SocketIO] Error conectando: " + ex);
            }
        }

        public async Task SendQuestion(string question)
        {
            await client.EmitAsync(SocketEvents.AskQuestion, question);
        }
    }
}
