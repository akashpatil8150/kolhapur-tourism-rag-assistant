const input = document.getElementById("question");
const chatBox = document.getElementById("chat-box");
const sendBtn = document.getElementById("send-btn");

let isWaiting = false;

window.onload = () => input.focus();

input.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
});

function addMessage(kind, title, message, id = "") {
    const bubble = document.createElement("div");
    bubble.className = kind;
    if (id) bubble.id = id;

    const heading = document.createElement("strong");
    heading.textContent = title;
    const content = document.createElement("div");
    content.className = "message-content";
    content.textContent = message;

    bubble.append(heading, document.createElement("br"), content);
    chatBox.appendChild(bubble);
    chatBox.scrollTop = chatBox.scrollHeight;
    return bubble;
}

async function sendMessage() {
    if (isWaiting) return;

    const question = input.value.trim();
    if (!question) return;

    isWaiting = true;
    input.disabled = true;
    sendBtn.disabled = true;
    addMessage("user-message", "🧑 You", question);
    input.value = "";
    const loading = addMessage("bot-message", "🤖 Tourism AI", "Thinking…", "loading");
    loading.querySelector(".message-content").classList.add("typing");

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question }),
        });
        const data = await response.json().catch(() => ({}));
        if (!response.ok || !data.answer) {
            throw new Error(data.detail || "Request failed");
        }
        loading.remove();
        addMessage("bot-message", "🤖 Tourism AI", data.answer);
    } catch (_) {
        loading.remove();
        addMessage("bot-message", "🤖 Tourism AI", "Something went wrong. Please try again.");
    } finally {
        isWaiting = false;
        input.disabled = false;
        sendBtn.disabled = false;
        input.focus();
    }
}
