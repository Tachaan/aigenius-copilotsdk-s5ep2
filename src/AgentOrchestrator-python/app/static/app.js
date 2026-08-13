// Chat UI for the Python stack. Mirrors the Blazor client in
// src/AgentOrchestrator/AgentHQDemo.Web: same API calls, same localStorage keys,
// same rendering behaviour — just without a WebAssembly runtime in front of it.

const FALLBACK_MODELS = {
    'claude-haiku-4.5': 'Claude Haiku 4.5 ⚡',
    'gpt-4.1': 'GPT-4.1',
    'gpt-5': 'GPT-5',
    'claude-sonnet-4.5': 'Claude Sonnet 4.5',
    'claude-opus-4.5': 'Claude Opus 4.5',
    'gemini-2.5-pro': 'Gemini 2.5 Pro',
};

const SUGGESTIONS = [
    'Who are our highest spending customers?',
    'Which customer segments are at risk?',
    'What are the top product categories by revenue?',
    'Predict which segment customer C002 belongs to',
    'How can we improve retention for at-risk customers?',
];

const STORAGE_KEYS = {
    messages: 'chat_messages',
    model: 'selected_model',
    theme: 'theme',
};

const el = {
    app: document.getElementById('chat-app'),
    messages: document.getElementById('messages-container'),
    welcome: document.getElementById('welcome'),
    suggestions: document.getElementById('suggestions'),
    input: document.getElementById('chat-input'),
    send: document.getElementById('send-btn'),
    modelSelect: document.getElementById('model-select'),
    clear: document.getElementById('btn-clear'),
    theme: document.getElementById('btn-theme'),
};

let messages = [];
let selectedModel = 'claude-haiku-4.5';
let isDark = true;
let isStreaming = false;

// ---------------------------------------------------------------- storage

function loadState() {
    try {
        messages = JSON.parse(localStorage.getItem(STORAGE_KEYS.messages) || '[]');
    } catch {
        messages = [];
    }
    selectedModel = localStorage.getItem(STORAGE_KEYS.model) || 'claude-haiku-4.5';
    isDark = (localStorage.getItem(STORAGE_KEYS.theme) || 'dark') === 'dark';
}

function saveMessages() {
    localStorage.setItem(STORAGE_KEYS.messages, JSON.stringify(messages));
}

// ---------------------------------------------------------------- rendering

function renderMarkdown(text) {
    return marked.parse(text, { breaks: true, gfm: true });
}

function highlightCode() {
    document.querySelectorAll('pre code:not(.hljs)').forEach((block) => hljs.highlightElement(block));
}

function scrollToBottom() {
    el.messages.scrollTop = el.messages.scrollHeight;
}

function renderMessages() {
    if (messages.length === 0) {
        el.messages.innerHTML = '';
        el.messages.appendChild(el.welcome);
        el.welcome.style.display = '';
        return;
    }

    el.welcome.style.display = 'none';
    el.messages.innerHTML = messages
        .map((msg) => {
            const role = msg.isUser ? 'user' : 'assistant';
            const avatar = msg.isUser ? '👤' : '🤖';
            const body = msg.content
                ? renderMarkdown(msg.content)
                : '<div class="typing-indicator"><span></span><span></span><span></span></div>';
            return `<div class="message ${role}">
                        <div class="avatar">${avatar}</div>
                        <div class="message-content">${body}</div>
                    </div>`;
        })
        .join('');

    highlightCode();
    scrollToBottom();
}

function setTheme(dark) {
    isDark = dark;
    el.app.className = `chat-app ${dark ? 'dark' : 'light'}`;
    el.theme.textContent = dark ? '🌙' : '☀️';
    document.getElementById('hljs-dark').disabled = !dark;
    document.getElementById('hljs-light').disabled = dark;
    localStorage.setItem(STORAGE_KEYS.theme, dark ? 'dark' : 'light');
}

// ---------------------------------------------------------------- models

async function loadModels() {
    let models = FALLBACK_MODELS;
    try {
        const res = await fetch('/api/chat/models');
        if (res.ok) {
            // The API returns a list of {id, name, description}; collapse it to
            // id -> label, exactly as the Blazor ChatService does.
            const list = await res.json();
            if (Array.isArray(list) && list.length > 0) {
                models = Object.fromEntries(
                    list.filter((m) => m.id).map((m) => [m.id, m.name || m.id])
                );
            }
        }
    } catch {
        // Offline or the CLI is not signed in — the static catalogue still lets
        // the page render, matching how the API itself degrades.
    }

    el.modelSelect.innerHTML = Object.entries(models)
        .map(([id, name]) => `<option value="${id}">${name}</option>`)
        .join('');

    // The stored model may no longer be offered by the account — fall back.
    if (!(selectedModel in models)) {
        selectedModel = 'claude-haiku-4.5' in models ? 'claude-haiku-4.5' : Object.keys(models)[0];
        localStorage.setItem(STORAGE_KEYS.model, selectedModel);
    }
    el.modelSelect.value = selectedModel;
}

// ---------------------------------------------------------------- streaming

async function sendMessage(prompt) {
    if (!prompt.trim() || isStreaming) return;

    messages.push({ content: prompt, isUser: true, timestamp: new Date().toISOString() });
    messages.push({ content: '', isUser: false, timestamp: new Date().toISOString() });
    saveMessages();
    renderMessages();

    isStreaming = true;
    updateSendButton();

    let content = '';
    let needsRender = false;

    // Repaint at ~20fps rather than per token, matching the Blazor client's
    // render timer. Without this a fast model repaints hundreds of times.
    const timer = setInterval(() => {
        if (!needsRender) return;
        needsRender = false;
        messages[messages.length - 1].content = content;
        renderMessages();
    }, 50);

    try {
        const res = await fetch('/api/chat/stream', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: prompt, model: selectedModel }),
        });

        if (!res.ok) throw new Error(`HTTP ${res.status}`);

        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop() ?? '';

            for (const line of lines) {
                if (!line.startsWith('data: ')) continue;
                const payload = line.slice(6);
                if (payload === '[DONE]') continue;
                try {
                    const chunk = JSON.parse(payload);
                    if (chunk.content) {
                        content += chunk.content;
                        needsRender = true;
                    }
                } catch {
                    // A partial frame — the next read completes it.
                }
            }
        }
    } catch (err) {
        content = `❌ Error: ${err.message}`;
    } finally {
        clearInterval(timer);
        isStreaming = false;
        messages[messages.length - 1].content = content;
        saveMessages();
        renderMessages();
        updateSendButton();
        el.input.focus();
    }
}

// ---------------------------------------------------------------- input

function updateSendButton() {
    el.send.disabled = isStreaming || el.input.value.trim() === '';
    el.send.innerHTML = isStreaming ? '<span class="spinner"></span>' : '<span>➤</span>';
    el.input.disabled = isStreaming;
}

function wireEvents() {
    el.input.addEventListener('input', updateSendButton);

    el.input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            const text = el.input.value.trim();
            el.input.value = '';
            updateSendButton();
            sendMessage(text);
        }
    });

    el.send.addEventListener('click', () => {
        const text = el.input.value.trim();
        el.input.value = '';
        updateSendButton();
        sendMessage(text);
    });

    el.modelSelect.addEventListener('change', () => {
        selectedModel = el.modelSelect.value;
        localStorage.setItem(STORAGE_KEYS.model, selectedModel);
    });

    el.clear.addEventListener('click', () => {
        messages = [];
        localStorage.removeItem(STORAGE_KEYS.messages);
        renderMessages();
    });

    el.theme.addEventListener('click', () => setTheme(!isDark));

    el.suggestions.innerHTML = SUGGESTIONS.map(
        (s) => `<button class="suggestion-chip">💡 ${s}</button>`
    ).join('');

    el.suggestions.querySelectorAll('.suggestion-chip').forEach((btn, i) => {
        btn.addEventListener('click', () => sendMessage(SUGGESTIONS[i]));
    });
}

// ---------------------------------------------------------------- bootstrap

(async function init() {
    loadState();
    setTheme(isDark);
    wireEvents();
    renderMessages();
    updateSendButton();
    await loadModels();
    el.input.focus();
})();
