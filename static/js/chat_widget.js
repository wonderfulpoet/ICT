// --- START OF REPLACEMENT for chat_widget.js ---
document.addEventListener('DOMContentLoaded', function() {
    // --- 聊天窗口折叠/展开逻辑 ---
    const chatWidget = document.getElementById('chat-widget');
    const chatToggle = document.getElementById('chat-widget-toggle');

    if (chatToggle) {
        chatToggle.addEventListener('click', () => {
            chatWidget.classList.toggle('is-collapsed');
        });
    }

    // --- 聊天功能 ---
    const messagesBox = document.getElementById('dsMessages');
    const promptInput = document.getElementById('dsPromptInput');
    const sendBtn = document.getElementById('dsSendBtn');
    const fileInput = document.getElementById('dsFileInput');
    const imagePreviewContainer = document.getElementById('dsImagePreviewContainer');
    const imagePreview = document.getElementById('dsImagePreview');
    const removeImageBtn = document.getElementById('dsRemoveImageBtn');

    let chatHistory = [{ role: 'ai', content: '你好！有什么可以帮你的吗？' }];
    let selectedFileBase64 = null;

    function renderMessages() {
        if (!messagesBox) return;
        messagesBox.innerHTML = '';
        chatHistory.forEach(msg => {
            const div = document.createElement('div');
            div.className = 'ds-bubble ' + (msg.role === 'user' ? 'user' : 'ai');

            if (typeof msg.content === 'object' && msg.content.image) {
                const img = document.createElement('img');
                img.src = msg.content.image;
                img.className = 'ds-bubble-image';
                img.alt = 'User uploaded image';
                div.appendChild(img);
                if (msg.content.text) {
                    const p = document.createElement('p');
                    p.textContent = msg.content.text;
                    div.appendChild(p);
                }
            } else {
                div.textContent = typeof msg.content === 'string' ? msg.content : msg.content.text;
            }

            messagesBox.appendChild(div);
        });
        messagesBox.scrollTop = messagesBox.scrollHeight;
    }

    function sendMsg() {
        const text = promptInput.value.trim();
        if (!text && !selectedFileBase64) return;

        const userMessageContent = {
            text: text,
            image: selectedFileBase64
        };
        chatHistory.push({ role: 'user', content: userMessageContent });
        renderMessages();

        // 重置输入框和文件选择
        const promptToSend = text;
        const imageToSend = selectedFileBase64;
        promptInput.value = '';
        promptInput.style.height = 'auto';
        resetFileInput();

        // 显示“思考中”的提示
        chatHistory.push({ role: 'ai', content: '思考中...' });
        renderMessages();

        // *** 修改点：调用我们自己的后端API，而不是DeepSeek ***
        fetch('/api/chat', { // <--- 关键修改：指向自己的后端路由
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                // 不需要 'Authorization' 头，后端会处理
            },
            body: JSON.stringify({
                prompt: promptToSend,
                image_base64: imageToSend // 发送prompt和base64编码的图片
            })
        })
        .then(r => {
            if (!r.ok) { // 检查响应状态码
                throw new Error(`服务器错误: ${r.statusText}`);
            }
            return r.json();
        })
        .then(data => {
            chatHistory.pop(); // 移除 "思考中..."
            if (data.answer) {
                chatHistory.push({ role: 'ai', content: data.answer });
            } else {
                chatHistory.push({ role: 'ai', content: `错误: ${data.error || '未收到有效回复'}` });
            }
            renderMessages();
        })
        .catch(e => {
            chatHistory.pop();
            chatHistory.push({ role: 'ai', content: `请求错误: ${e.message}` });
            renderMessages();
        });
    }

    function resetFileInput() {
        fileInput.value = '';
        selectedFileBase64 = null;
        imagePreviewContainer.style.display = 'none';
    }

    if (sendBtn) sendBtn.addEventListener('click', sendMsg);

    if (promptInput) {
        promptInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMsg();
            }
        });
        promptInput.addEventListener('input', () => {
            promptInput.style.height = 'auto';
            promptInput.style.height = (promptInput.scrollHeight) + 'px';
        });
    }

    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file && file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = function(event) {
                    selectedFileBase64 = event.target.result; // event.target.result 包含 "data:image/jpeg;base64,..."
                    imagePreview.src = selectedFileBase64;
                    imagePreviewContainer.style.display = 'block';
                };
                reader.readAsDataURL(file);
            }
        });
    }

    if (removeImageBtn) {
        removeImageBtn.addEventListener('click', resetFileInput);
    }

    renderMessages();
});
// --- END OF REPLACEMENT for chat_widget.js ---