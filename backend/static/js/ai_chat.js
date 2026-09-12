// ==========================================
// TalentIQ AI Chat v3.0
// ==========================================

const form = document.getElementById("chatForm");
const input = document.getElementById("message");
const chatBox = document.getElementById("chatBox");
const sendBtn = document.getElementById("sendBtn");

let isSending = false;

// ==========================================
// HELPERS
// ==========================================

function escapeHtml(text) {

    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;

}

function formatReply(text) {

    return escapeHtml(text).replace(/\n/g, "<br>");

}

function hideWelcomeSection() {

    const welcomeCard = document.querySelector(".welcome-card");
    const quickPrompts = document.querySelector(".quick-prompts");

    if (welcomeCard) {
        welcomeCard.style.display = "none";
    }

    if (quickPrompts) {
        quickPrompts.style.display = "none";
    }

}

function scrollToBottom() {

    chatBox.scrollTop = chatBox.scrollHeight;

}

function appendUserMessage(message) {

    chatBox.insertAdjacentHTML("beforeend", `

    <div class="user-message">

        <div class="avatar">👤</div>

        <div class="message">
            ${escapeHtml(message)}
        </div>

    </div>

    `);

}

function appendTypingIndicator() {

    chatBox.insertAdjacentHTML("beforeend", `

    <div class="bot-message" id="typing">

        <div class="avatar">🤖</div>

        <div class="message">

            <strong>TalentIQ AI</strong>

            <br><br>

            <span class="typing-text">
                Thinking<span class="dots"></span>
            </span>

        </div>

    </div>

    `);

}

function removeTypingIndicator() {

    const typing = document.getElementById("typing");

    if (typing) {
        typing.remove();
    }

}

function appendBotMessage(reply) {

    chatBox.insertAdjacentHTML("beforeend", `

    <div class="bot-message">

        <div class="avatar">🤖</div>

        <div class="message">
            ${formatReply(reply)}
        </div>

    </div>

    `);

}

function appendErrorMessage(message) {

    chatBox.insertAdjacentHTML("beforeend", `

    <div class="bot-message error-message">

        <div class="avatar">⚠️</div>

        <div class="message">
            ${escapeHtml(message)}
        </div>

    </div>

    `);

}

function setInputState(disabled) {

    isSending = disabled;
    input.disabled = disabled;
    sendBtn.disabled = disabled;

    if (disabled) {
        sendBtn.classList.add("loading");
    } else {
        sendBtn.classList.remove("loading");
        input.focus();
    }

}

// ==========================================
// SEND MESSAGE
// ==========================================

async function sendMessage(message) {

    const trimmed = message.trim();

    if (trimmed === "" || isSending) {
        return;
    }

    hideWelcomeSection();
    appendUserMessage(trimmed);
    scrollToBottom();

    input.value = "";
    setInputState(true);
    appendTypingIndicator();
    scrollToBottom();

    try {

        const response = await fetch("/ask-ai", {

            method: "POST",

            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },

            body: "message=" + encodeURIComponent(trimmed)

        });

        const data = await response.json();

        removeTypingIndicator();

        if (!response.ok || data.error) {
            appendErrorMessage(
                data.reply || "Something went wrong. Please try again."
            );
        } else {
            appendBotMessage(data.reply);
        }

    } catch (error) {

        removeTypingIndicator();

        appendErrorMessage(
            "Unable to reach TalentIQ AI. Please check your connection."
        );

    }

    setInputState(false);
    scrollToBottom();

}

// ==========================================
// FORM SUBMIT
// ==========================================

form.addEventListener("submit", function (e) {

    e.preventDefault();
    sendMessage(input.value);

});

// ==========================================
// QUICK PROMPTS
// ==========================================

function bindPrompt(element) {

    element.addEventListener("click", () => {

        const prompt = element.dataset.prompt;

        if (prompt) {
            sendMessage(prompt);
        }

    });

}

document.querySelectorAll(".prompt-card").forEach(bindPrompt);
document.querySelectorAll(".feature-chip").forEach(bindPrompt);

// ==========================================
// KEYBOARD SHORTCUT
// ==========================================

input.addEventListener("keydown", function (e) {

    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        form.dispatchEvent(new Event("submit"));
    }

});

input.focus();
