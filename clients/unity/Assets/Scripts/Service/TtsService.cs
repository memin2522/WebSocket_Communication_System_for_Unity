using Meta.WitAi.TTS.Utilities;
using UnityEngine;

namespace WebSocketCommunication
{
    /// <summary>
    /// Reproduce con texto a voz (Meta Voice SDK) cada mensaje del controlador.
    /// </summary>
    public class TtsService : MonoBehaviour
    {
        [SerializeField] private TTSSpeaker voice;
        [SerializeField] private DisplayController controller;

        private void Awake()
        {
            controller.OnMessageReceived += Speak;
        }

        public void Speak(string message)
        {
            voice.SpeakQueued(message);
        }
    }
}
