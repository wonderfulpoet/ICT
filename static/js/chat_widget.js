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
    const filePreviewContainer = document.getElementById('dsFilePreviewContainer');
    const imagePreview = document.getElementById('dsImagePreview');
    const fileInfoPreview = document.getElementById('dsFilePreviewInfo');
    const fileNameSpan = document.getElementById('dsFileName');
    const removeFileBtn = document.getElementById('dsRemoveFileBtn');

    let chatHistory = [{ role: 'ai', content: '你好！有什么可以帮你的吗？' }];
    let selectedFileBase64 = null;
    let selectedFile = null;

    function renderMessages() {
        if (!messagesBox) return;
        messagesBox.innerHTML = '';
        chatHistory.forEach(msg => {
            const div = document.createElement('div');
            div.className = 'ds-bubble ' + (msg.role === 'user' ? 'user' : 'ai');

            const content = msg.content;

            // 如果 content 是一个包含文件或图片的对象
            if (typeof content === 'object' && content !== null) {
                // 渲染图片
                if (content.image) {
                    const img = document.createElement('img');
                    img.src = content.image;
                    img.className = 'ds-bubble-image';
                    img.alt = 'User uploaded image';
                    div.appendChild(img);
                }
                // 渲染文件信息
                if (content.file) {
                    const fileDiv = document.createElement('div');
                    fileDiv.className = 'ds-bubble-file';
                    fileDiv.innerHTML = `<i class="fas fa-file-alt"></i> <span>${content.file.name}</span>`;
                    div.appendChild(fileDiv);
                }
                // 渲染文本
                if (content.text) {
                    const p = document.createElement('p');
                    p.textContent = content.text;
                    div.appendChild(p);
                }
            } else { // 如果 content 只是一个字符串（例如AI的回复）
                div.textContent = content;
            }

            messagesBox.appendChild(div);
        });
        messagesBox.scrollTop = messagesBox.scrollHeight;
    }

    function sendMsg() {
        const text = promptInput.value.trim();
        if (!text && !selectedFile) return;

        // 构建用户消息内容
        const userMessageContent = { text: text };
        if (selectedFile) {
            if (selectedFile.type.startsWith('image/')) {
                userMessageContent.image = selectedFileBase64;
            } else {
                userMessageContent.file = { name: selectedFile.name };
            }
        }

        chatHistory.push({ role: 'user', content: userMessageContent });
        renderMessages();

        // 准备发送到后端的数据
        const promptToSend = text;
        const fileBase64ToSend = selectedFileBase64;

        // 重置输入框和文件选择
        promptInput.value = '';
        promptInput.style.height = 'auto';
        resetFileInput();

        // 显示“思考中”的提示
        chatHistory.push({ role: 'ai', content: '思考中...' });
        renderMessages();

        fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                prompt: promptToSend,
                image_base64: fileBase64ToSend // 后端可解析此base64字符串获取MIME类型和数据
            })
        })
        .then(r => {
            if (!r.ok) throw new Error(`服务器错误: ${r.statusText}`);
            return r.json();
        })
        .then(data => {
            chatHistory.pop(); // 移除 "思考中..."
            chatHistory.push({ role: 'ai', content: data.answer || `错误: ${data.error || '未收到有效回复'}` });
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
        selectedFile = null;
        filePreviewContainer.style.display = 'none';
        imagePreview.style.display = 'none';
        fileInfoPreview.style.display = 'none';
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
            if (file) {
                selectedFile = file;
                const reader = new FileReader();
                reader.onload = function(event) {
                    selectedFileBase64 = event.target.result; // 包含 data:mime/type;base64,...

                    if (file.type.startsWith('image/')) {
                        imagePreview.src = selectedFileBase64;
                        imagePreview.style.display = 'block';
                        fileInfoPreview.style.display = 'none';
                    } else {
                        fileNameSpan.textContent = file.name;
                        imagePreview.style.display = 'none';
                        fileInfoPreview.style.display = 'flex';
                    }
                    filePreviewContainer.style.display = 'block';
                };
                reader.readAsDataURL(file);
            }
        });
    }

    if (removeFileBtn) {
        removeFileBtn.addEventListener('click', resetFileInput);
    }

    // 初始渲染
    renderMessages();
});
// --- END OF REPLACEMENT for chat_widget.js ---