document.addEventListener('DOMContentLoaded', function() {
    // --- 聊天窗口折叠/展开逻辑 ---
    const chatWidget = document.getElementById('chat-widget');
    const chatToggle = document.getElementById('chat-widget-toggle');

    if (chatToggle) {
        chatToggle.addEventListener('click', () => {
            chatWidget.classList.toggle('is-collapsed');
        });
    }

    // --- 聊天功能 (从原内联脚本改编) ---
    const messagesBox = document.getElementById('dsMessages');
    const promptInput = document.getElementById('dsPromptInput');
    const sendBtn = document.getElementById('dsSendBtn');

    // 为聊天窗口提供简单的会话内历史记录
    let chatHistory = [{ role: 'ai', content: '你好！有什么可以帮你的吗？' }];

    function renderMessages() {
        if (!messagesBox) return;
        messagesBox.innerHTML = '';
        chatHistory.forEach(msg => {
            const div = document.createElement('div');
            div.className = 'ds-bubble ' + (msg.role === 'user' ? 'user' : 'ai');
            // 为了安全，使用 textContent 避免渲染不安全的 HTML
            div.textContent = msg.content;
            messagesBox.appendChild(div);
        });
        messagesBox.scrollTop = messagesBox.scrollHeight;
    }

    function sendMsg() {
        const text = promptInput.value.trim();
        if (!text) return;

        chatHistory.push({ role: 'user', content: text });
        renderMessages();
        promptInput.value = '';
        promptInput.style.height = 'auto';

        // 显示“思考中”的提示
        chatHistory.push({ role: 'ai', content: '思考中...' });
        renderMessages();

        // --- API 调用 ---
        // 重要提示：在真实应用中，绝不要在客户端暴露您的 API 密钥。
        // 这应该由您的后端处理。此处仅为演示目的。
        const apiKey = 'sk-0d8f31e1cf5d4774bcf82f2f7624c02d'; // 替换为你的 API KEY
        const apiUrl = 'https://api.deepseek.com/v1/chat/completions';

        fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + apiKey
            },
            body: JSON.stringify({
                model: 'deepseek-chat',
                messages: [{ role: 'user', content: text }]
            })
        })
        .then(r => r.json())
        .then(data => {
            chatHistory.pop(); // 移除 "思考中..."
            if (data.choices && data.choices[0] && data.choices[0].message) {
                chatHistory.push({ role: 'ai', content: data.choices[0].message.content });
            } else {
                chatHistory.push({ role: 'ai', content: `错误: ${data.error?.message || '未知错误'}` });
            }
            renderMessages();
        })
        .catch(e => {
            chatHistory.pop();
            chatHistory.push({ role: 'ai', content: `请求错误: ${e.message}` });
            renderMessages();
        });
    }

    if (sendBtn) sendBtn.addEventListener('click', sendMsg);
    if (promptInput) {
        promptInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMsg();
            }
        });
        // 自动调整文本框高度
        promptInput.addEventListener('input', () => {
            promptInput.style.height = 'auto';
            promptInput.style.height = (promptInput.scrollHeight) + 'px';
        });
    }

    // 初始渲染
    renderMessages();
});