/**
 * DeepSeek大模型交互平台前端脚本
 * 提供额外的前端交互功能
 */

// 自动调整文本框高度
function autoResizeTextarea(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = (textarea.scrollHeight) + 'px';
}

// 主题切换功能
function toggleTheme() {
    const body = document.body;
    const themeIcon = document.getElementById('themeIcon');
    
    if (body.classList.contains('dark-theme')) {
        body.classList.remove('dark-theme');
        themeIcon.classList.remove('fa-sun');
        themeIcon.classList.add('fa-moon');
        localStorage.setItem('theme', 'light');
    } else {
        body.classList.add('dark-theme');
        themeIcon.classList.remove('fa-moon');
        themeIcon.classList.add('fa-sun');
        localStorage.setItem('theme', 'dark');
    }
}

// 初始化主题
function initializeTheme() {
    const storedTheme = localStorage.getItem('theme');
    const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');
    const themeIcon = document.getElementById('themeIcon');
    
    if (storedTheme === 'dark' || (!storedTheme && prefersDarkScheme.matches)) {
        document.body.classList.add('dark-theme');
        if (themeIcon) {
            themeIcon.classList.remove('fa-moon');
            themeIcon.classList.add('fa-sun');
        }
    }
}

// 初始化页面功能
document.addEventListener('DOMContentLoaded', function() {
    const textarea = document.getElementById('promptInput');
    const themeToggle = document.getElementById('themeToggle');
    
    // 初始化主题
    initializeTheme();
    
    // 监听主题切换按钮
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
    
    // 监听输入事件调整文本框高度
    if (textarea) {
        textarea.addEventListener('input', function() {
            autoResizeTextarea(this);
        });
    }
    
    // 自动聚焦到输入框
    if (textarea) {
        textarea.focus();
    }
});

// 处理代码复制
function copyToClipboard(text) {
    // 创建临时textarea元素
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.setAttribute('readonly', '');
    textarea.style.position = 'absolute';
    textarea.style.left = '-9999px';
    document.body.appendChild(textarea);
    
    // 选择文本并复制
    textarea.select();
    document.execCommand('copy');
    
    // 移除临时元素
    document.body.removeChild(textarea);
}

// 处理用户上传的文件预览
function previewFile(file) {
    if (!file) return;
    
    // 只处理图片预览
    if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const preview = document.createElement('div');
            preview.className = 'file-preview';
            preview.innerHTML = `
                <div class="preview-header">图片预览 <span class="close-preview">&times;</span></div>
                <img src="${e.target.result}" alt="文件预览">
            `;
            document.body.appendChild(preview);
            
            // 添加关闭按钮事件
            preview.querySelector('.close-preview').addEventListener('click', function() {
                document.body.removeChild(preview);
            });
        };
        reader.readAsDataURL(file);
    }
}
