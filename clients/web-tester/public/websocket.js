const config = window.APP_CONFIG;
const socket = io(config.serverUrl, { transports: ["websocket"] });

// Opciones del selector de rol a partir de la configuración
const roleSelect = document.getElementById("roleSelect");
[
    { value: config.roleDisplay, label: `Display client (${config.roleDisplay})` },
    { value: config.roleAi, label: `AI client (${config.roleAi})` },
].forEach(({ value, label }) => roleSelect.add(new Option(label, value)));

//Subscriptions to server events
/*
Server Events:
- "session_joined": Emitted when a user successfully joins a session.
- "question": Emitted when the display client submits a question.
- "answer": Emitted when the AI client submits an answer.
- "error": Emitted when an error occurs.
- "info": Emitted for informational messages.
- "question_listened": Emitted from the AI client when a question is listened from the STT.
*/

function subscribeToServerEvents() {

    socket.on("session_joined", (data) => {
        console.log("Session Joined:", data);
    });

    socket.on("question", (data) => {
        console.log("Question Received:", data);
    });

    socket.on("answer", (data) => {
        console.log("Answer Received:", data);
    });

    socket.on("error", (error) => {
        console.error("Error:", error);
    });

    socket.on("info", (info) => {
        console.log("Info:", info);
    });

    socket.on("question_listened", (data) => {
        console.log("Question Listened:", data);
    });
}

//Calls to server
/*
Client Events:
- "join_session": To join a session sending the role
- "ask_question": To ask a question to the AI client
- "send_answer": To send an answer from the AI client
- "disconnect": To disconnect from the server
*/

function joinSession(role) {
    socket.emit("join_session", role);
}

function askQuestion(question) {
    socket.emit("ask_question", question);
}

function sendAnswer(answer) {
    socket.emit("send_answer", answer);
}

function disconnect() {
    socket.emit("disconnect");
    socket.close();
}

function simulateQuestionListened(question) {
    socket.emit("question_listened", question);
}

//Button Event Listeners

document.getElementById("joinSessionBtn").addEventListener("click", () => {
    joinSession(roleSelect.value);
});

document.getElementById("askQuestionBtn").addEventListener("click", () => {
    const question = document.getElementById("questionInput").value;
    askQuestion(question);
});

document.getElementById("sendAnswerBtn").addEventListener("click", () => {
    const answer = document.getElementById("answerInput").value;
    sendAnswer(answer);
});

document.getElementById("disconnectBtn").addEventListener("click", () => {
    disconnect();
});

document.getElementById("listenQuestionBtn").addEventListener("click", () => {
    const question = document.getElementById("listenInput").value;
    simulateQuestionListened(question);
});


subscribeToServerEvents();
