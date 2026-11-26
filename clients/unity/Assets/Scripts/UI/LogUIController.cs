using UnityEngine;
using TMPro;

namespace WebSocketCommunication
{
    public class LogUIController : MonoBehaviour
    {
        [SerializeField] private DisplayController displayController;

        [SerializeField] private GameObject logUIElements;
        [SerializeField] private TMP_InputField inputQuestion;
        [SerializeField] private TextMeshProUGUI textLabel;

        private bool isLogOn = true;

        private void Awake()
        {
            displayController.OnLogRequested += AddLog;
        }

        public void AddLog(string text)
        {
            textLabel.text += text + "\n";
        }

        public void OnSendButtonClicked()
        {
            string question = inputQuestion.text.Trim();
            inputQuestion.text = "";

            if (string.IsNullOrEmpty(question))
                return;

            displayController.SendQuestion(question);
        }

        public void ToggleLogUI()
        {
            isLogOn = !isLogOn;
            logUIElements.SetActive(isLogOn);
        }
    }
}
