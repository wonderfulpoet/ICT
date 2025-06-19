/**
 * 文件预览功能
 */

// 文件类型图标映射
const fileIcons = {
    'pdf': 'fa-file-pdf',
    'doc': 'fa-file-word',
    'docx': 'fa-file-word',
    'xls': 'fa-file-excel',
    'xlsx': 'fa-file-excel',
    'ppt': 'fa-file-powerpoint',
    'pptx': 'fa-file-powerpoint',
    'txt': 'fa-file-alt',
    'csv': 'fa-file-csv',
    'json': 'fa-file-code',
    'js': 'fa-file-code',
    'html': 'fa-file-code',
    'css': 'fa-file-code',
    'py': 'fa-file-code',
    'java': 'fa-file-code',
    'c': 'fa-file-code',
    'cpp': 'fa-file-code',
    'jpg': 'fa-file-image',
    'jpeg': 'fa-file-image',
    'png': 'fa-file-image',
    'gif': 'fa-file-image',
    'svg': 'fa-file-image',
    'mp3': 'fa-file-audio',
    'wav': 'fa-file-audio',
    'mp4': 'fa-file-video',
    'avi': 'fa-file-video',
    'zip': 'fa-file-archive',
    'rar': 'fa-file-archive',
    'tar': 'fa-file-archive',
    'gz': 'fa-file-archive',
    'md': 'fa-file-alt'
};

/**
 * 获取文件类型图标
 * @param {string} filename - 文件名
 * @returns {string} - 图标类名
 */
function getFileIcon(filename) {
    const extension = filename.split('.').pop().toLowerCase();
    return fileIcons[extension] || 'fa-file';
}

/**
 * 创建文件预览元素
 * @param {File} file - 文件对象
 * @returns {Promise<HTMLElement>} - 预览元素
 */
function createFilePreview(file) {
    return new Promise((resolve, reject) => {
        const extension = file.name.split('.').pop().toLowerCase();
        const previewContainer = document.createElement('div');
        previewContainer.className = 'preview-container';
        
        const previewContent = document.createElement('div');
        previewContent.className = 'preview-content';
        
        const previewHeader = document.createElement('div');
        previewHeader.className = 'preview-header';
        previewHeader.innerHTML = `
            <span><i class="fas ${getFileIcon(file.name)}"></i> ${file.name}</span>
            <button class="close-preview">&times;</button>
        `;
        
        const previewBody = document.createElement('div');
        previewBody.className = 'preview-body';
        
        // 根据文件类型创建不同的预览
        if (['jpg', 'jpeg', 'png', 'gif', 'svg'].includes(extension)) {
            // 图片预览
            const reader = new FileReader();
            reader.onload = function(e) {
                const img = document.createElement('img');
                img.src = e.target.result;
                img.className = 'preview-image';
                previewBody.appendChild(img);
                resolve(previewContainer);
            };
            reader.onerror = reject;
            reader.readAsDataURL(file);
        } else if (['txt', 'csv', 'json', 'js', 'html', 'css', 'py', 'java', 'c', 'cpp', 'md'].includes(extension)) {
            // 文本文件预览
            const reader = new FileReader();
            reader.onload = function(e) {
                const pre = document.createElement('pre');
                pre.className = 'preview-text';
                pre.textContent = e.target.result;
                previewBody.appendChild(pre);
                resolve(previewContainer);
            };
            reader.onerror = reject;
            reader.readAsText(file);
        } else {
            // 其他文件类型
            previewBody.innerHTML = `
                <div style="text-align: center; padding: 20px;">
                    <i class="fas ${getFileIcon(file.name)}" style="font-size: 4rem; color: var(--primary-color); margin-bottom: 15px;"></i>
                    <p>无法预览此文件类型</p>
                    <p>文件大小: ${formatFileSize(file.size)}</p>
                </div>
            `;
            resolve(previewContainer);
        }
        
        previewContent.appendChild(previewHeader);
        previewContent.appendChild(previewBody);
        previewContainer.appendChild(previewContent);
        
        // 添加关闭事件
        previewContainer.querySelector('.close-preview').addEventListener('click', function() {
            previewContainer.remove();
        });
    });
}

/**
 * 格式化文件大小
 * @param {number} bytes - 文件大小（字节）
 * @returns {string} - 格式化后的大小
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * 预览文件
 * @param {File} file - 文件对象
 */
function previewFile(file) {
    if (!file) return;
    
    createFilePreview(file).then(previewElement => {
        document.body.appendChild(previewElement);
    }).catch(error => {
        console.error('预览文件失败:', error);
        alert('预览文件失败: ' + error.message);
    });
}

// 导出函数
window.previewFile = previewFile;
