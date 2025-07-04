// --- DOM 元素获取 ---
const uploadBox = document.getElementById('upload-box');
const imageInput = document.getElementById('image-input');
const inputPreview = document.getElementById('input-preview');
const uploadPlaceholder = document.getElementById('upload-placeholder');
const resultImagePreview = document.getElementById('result-image-preview');
const resultPlaceholder = document.getElementById('result-placeholder');
const detectBtn = document.getElementById('detect-btn');
const resultInfoDetails = document.getElementById('result-info-details');
const resultIsFake = document.getElementById('result-is-fake');
const resultFakeType = document.getElementById('result-fake-type');
const resultConfidenceScore = document.getElementById('result-confidence-score');
const uploadBtn = document.getElementById('upload-btn');
const clearBtn = document.getElementById('clear-btn');
const downloadBtn = document.getElementById('download-btn');

// --- 事件监听区域 ---

// 为可见的div（uploadBox）注册点击事件
if (uploadBox) {
    uploadBox.addEventListener('click', () => {
        imageInput.click();
    });
    uploadBox.addEventListener('dragover', e => { 
        e.preventDefault(); 
        uploadBox.style.borderColor = '#6a5acd'; 
    });
    uploadBox.addEventListener('dragleave', e => { 
        e.preventDefault(); 
        uploadBox.style.borderColor = '#d0dbe5'; 
    });
    uploadBox.addEventListener('drop', e => {
        e.preventDefault();
        uploadBox.style.borderColor = '#d0dbe5';
        if (e.dataTransfer.files.length) {
            imageInput.files = e.dataTransfer.files;
            previewImage();
        }
    });
}

// 为隐藏的input注册change事件
if (imageInput) {
    imageInput.addEventListener('change', previewImage);
}

// 检测按钮点击事件
if (detectBtn) {
    detectBtn.addEventListener('click', () => {
        if (!imageInput.files || !imageInput.files.length) {
            alert("请先上传一张图片！");
            return;
        }
        startDetection();
    });
}

// 上传按钮：触发文件选择
if (uploadBtn) {
    uploadBtn.addEventListener('click', () => {
        if (imageInput) imageInput.click();
    });
}

// 清除按钮：清空图片
if (clearBtn) {
    clearBtn.addEventListener('click', () => {
        if (imageInput) imageInput.value = '';
        if (inputPreview) {
            inputPreview.src = '';
            inputPreview.style.display = 'none';
        }
        if (uploadPlaceholder) uploadPlaceholder.style.display = 'block';
        resetResultArea();
    });
}

// 下载按钮：下载检测结果图片
if (downloadBtn) {
    downloadBtn.addEventListener('click', () => {
        if (resultImagePreview && resultImagePreview.src && resultImagePreview.style.display !== 'none') {
            const link = document.createElement('a');
            link.href = resultImagePreview.src;
            link.download = '检测结果.png';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        } else {
            alert('暂无可下载的检测结果图片！');
        }
    });
}

// --- 功能函数 ---
function previewImage() {
    const file = imageInput.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = e => {
            inputPreview.src = e.target.result;
            inputPreview.style.display = 'block';
            uploadPlaceholder.style.display = 'none';
            resetResultArea(); 
        };
        reader.readAsDataURL(file);
    }
}
async function startDetection() {
    detectBtn.disabled = true;
    detectBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 检测中...';
    resultPlaceholder.textContent = '正在分析图像，请稍候...';
    resultPlaceholder.style.display = 'block';
    resultImagePreview.style.display = 'none';
    resultInfoDetails.style.display = 'none';
    
    try {
        const file = imageInput.files[0];
        if (!file) {
            throw new Error('没有选择文件');
        }

        // 读取文件为Base64 (完整的数据URL)
        const imageBase64 = await new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result);
            reader.onerror = reject;
            reader.readAsDataURL(file);
        });
        
        // 发送请求
        const response = await fetch('/call_api', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ image_data: imageBase64.split(',')[1] })  // 只发送base64部分
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || `检测失败: ${response.status}`);
        }
        
        const result = await response.json();
        
        // 显示结果
        displayDetectionResult(result);
        
    } catch (error) {
        console.error('检测错误:', error);
        resultPlaceholder.textContent = '检测失败: ' + error.message;
        resultPlaceholder.style.display = 'block';
    } finally {
        detectBtn.disabled = false;
        detectBtn.innerHTML = '<i class="fas fa-search"></i> 开始检测';
    }
}

function displayDetectionResult(result) {
    if (result.status !== "success") {
        throw new Error(result.error || "未知错误");
    }

    const data = result.result;
    
    // 1. 显示处理后的图片
    if (data.processed_image) {
        resultImagePreview.src = data.processed_image;  // 直接使用完整的data URL
        resultImagePreview.style.display = 'block';
        resultPlaceholder.style.display = 'none';
    }

    // 2. 显示检测结果信息
    resultIsFake.textContent = data.is_fake ? '是' : '否';
    resultFakeType.textContent = data.fake_type || '未知';
    
    if (data.confidence_scores) {
        const scores = data.confidence_scores;
        resultConfidenceScore.innerHTML = `
            <span>Photoshop: ${scores.photoshop}%</span><br>
            <span>Deepfake: ${scores.deepfake}%</span><br>
            <span>AI生成: ${scores.aigc}%</span>
        `;
    }
    
    resultInfoDetails.style.display = 'block';
    
    // 3. 启用下载按钮
    downloadBtn.disabled = false;
}

function readFileAsBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => {
            // 移除data:image/...;base64,前缀
            const base64String = reader.result.split(',')[1];
            resolve(base64String);
        };
        reader.onerror = reject;
        reader.readAsDataURL(file);
    });
}

function resetResultArea() {
    resultImagePreview.src = '';
    resultImagePreview.style.display = 'none';
    resultPlaceholder.textContent = '检测结果将在此显示';
    resultPlaceholder.style.display = 'block';
    resultInfoDetails.style.display = 'none';
    resultIsFake.textContent = '';
    resultFakeType.textContent = '';
    resultConfidenceScore.textContent = '';
}