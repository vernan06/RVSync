/**
 * RVSync AI Support Widget
 * Premium Glassmorphism Chat Interface
 */

(function() {
    // 1. Create Styles
    const styles = `
        .ai-widget-container {
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            z-index: 9999;
            font-family: 'Inter', sans-serif;
        }

        .ai-fab {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: linear-gradient(135deg, #7c3aed 0%, #4f46e5 100%);
            box-shadow: 0 10px 25px -5px rgba(124, 58, 237, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            border: 2px solid rgba(255, 255, 255, 0.1);
        }

        .ai-fab:hover {
            transform: scale(1.1) rotate(5deg);
        }

        .ai-fab-icon {
            font-size: 1.5rem;
            color: white;
        }

        .ai-chat-window {
            position: absolute;
            bottom: 0;
            right: 80px;
            width: 350px;
            height: 500px;
            background: rgba(15, 15, 20, 0.95);
            backdrop-filter: blur(25px);
            -webkit-backdrop-filter: blur(25px);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 1.5rem;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7);
            display: none;
            flex-direction: column;
            overflow: hidden;
            transform-origin: bottom right;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .ai-chat-window.active {
            display: flex;
            animation: slideIn 0.3s ease forwards;
        }

        @keyframes slideIn {
            from { opacity: 0; transform: translateX(20px) scale(0.95); }
            to { opacity: 1; transform: translateX(0) scale(1); }
        }

        .ai-chat-header {
            padding: 1.25rem;
            background: rgba(255, 255, 255, 0.05);
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .ai-close-btn {
            background: rgba(255, 255, 255, 0.05);
            border: none;
            color: #9ca3af;
            cursor: pointer;
            font-size: 1rem;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s ease;
        }

        .ai-close-btn:hover {
            background: rgba(239, 68, 68, 0.2);
            color: #ef4444;
            transform: rotate(90deg);
        }

        .ai-chat-title {
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }

        .ai-status-dot {
            width: 8px;
            height: 8px;
            background: #10b981;
            border-radius: 50%;
            box-shadow: 0 0 10px #10b981;
        }

        .ai-chat-messages {
            flex: 1;
            padding: 1rem;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }

        .ai-msg {
            max-width: 85%;
            padding: 0.75rem 1rem;
            border-radius: 1rem;
            font-size: 0.85rem;
            line-height: 1.4;
        }

        .ai-msg-bot {
            align-self: flex-start;
            background: rgba(255, 255, 255, 0.05);
            color: #d1d5db;
            border-bottom-left-radius: 0.25rem;
        }

        .ai-msg-user {
            align-self: flex-end;
            background: #7c3aed;
            color: white;
            border-bottom-right-radius: 0.25rem;
        }

        .ai-chat-input-area {
            padding: 1rem;
            background: rgba(255, 255, 255, 0.03);
            border-top: 1px solid rgba(255, 255, 255, 0.05);
            display: flex;
            gap: 0.5rem;
        }

        .ai-chat-input {
            flex: 1;
            background: rgba(0, 0, 0, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 0.75rem;
            padding: 0.6rem 1rem;
            color: white;
            font-size: 0.85rem;
            outline: none;
        }

        .ai-chat-input:focus {
            border-color: #7c3aed;
        }

        .ai-send-btn {
            background: #7c3aed;
            border: none;
            border-radius: 0.75rem;
            padding: 0.6rem;
            color: white;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .typing-indicator {
            display: flex;
            gap: 4px;
            padding: 4px;
        }

        .dot {
            width: 4px;
            height: 4px;
            background: #9ca3af;
            border-radius: 50%;
            animation: bounce 1.4s infinite ease-in-out;
        }

        .dot:nth-child(1) { animation-delay: -0.32s; }
        .dot:nth-child(2) { animation-delay: -0.16s; }

        @keyframes bounce {
            0%, 80%, 100% { transform: scale(0); }
            40% { transform: scale(1); }
        }
    `;

    // 2. Inject CSS
    const styleEl = document.createElement('style');
    styleEl.textContent = styles;
    document.head.appendChild(styleEl);

    // 3. Inject HTML
    const container = document.createElement('div');
    container.className = 'ai-widget-container';
    container.innerHTML = `
        <div class="ai-chat-window" id="aiChatWindow">
            <div class="ai-chat-header">
                <div class="ai-chat-title">
                    <div class="ai-status-dot"></div>
                    <span style="font-weight: 700; font-size: 0.9rem;">RV-Assistant</span>
                </div>
                <button id="closeAiChat" class="ai-close-btn" title="Close Chat">✕</button>
            </div>
            <div class="ai-chat-messages" id="aiMessages">
                <div class="ai-msg ai-msg-bot">
                    Hi! I'm your RVSync AI assistant. Ask me anything about your courses, timetable, or the platform!
                </div>
            </div>
            <div class="ai-chat-input-area">
                <input type="text" class="ai-chat-input" id="aiInput" placeholder="How do I view my syllabus?">
                <button class="ai-send-btn" id="aiSend">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
                </button>
            </div>
        </div>
        <div class="ai-fab" id="aiFab">
            <div class="ai-fab-icon">🤖</div>
        </div>
    `;
    document.body.appendChild(container);

    // 4. Logic
    const fab = document.getElementById('aiFab');
    const window = document.getElementById('aiChatWindow');
    const closeBtn = document.getElementById('closeAiChat');
    const sendBtn = document.getElementById('aiSend');
    const input = document.getElementById('aiInput');
    const messagesCont = document.getElementById('aiMessages');

    fab.addEventListener('click', () => {
        window.classList.toggle('active');
    });

    closeBtn.addEventListener('click', () => {
        window.classList.remove('active');
    });

    async function handleSend() {
        const text = input.value.trim();
        if (!text) return;

        // Add user message
        addMessage(text, 'user');
        input.value = '';

        // Add typing indicator
        const typingId = addTypingIndicator();
        messagesCont.scrollTop = messagesCont.scrollHeight;

        try {
            const result = await api.postAiChat(text);
            removeTypingIndicator(typingId);
            addMessage(result.response, 'bot');
        } catch (e) {
            removeTypingIndicator(typingId);
            addMessage("I'm having technical difficulties. Please ensure the Gemini API key is configured.", 'bot');
        }
    }

    sendBtn.addEventListener('click', handleSend);
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSend();
    });

    function addMessage(text, type) {
        const msg = document.createElement('div');
        msg.className = `ai-msg ai-msg-${type}`;
        msg.textContent = text;
        messagesCont.appendChild(msg);
        messagesCont.scrollTop = messagesCont.scrollHeight;
    }

    function addTypingIndicator() {
        const id = 'typing-' + Date.now();
        const msg = document.createElement('div');
        msg.className = 'ai-msg ai-msg-bot';
        msg.id = id;
        msg.innerHTML = `
            <div class="typing-indicator">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
            </div>
        `;
        messagesCont.appendChild(msg);
        return id;
    }

    function removeTypingIndicator(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }
})();
