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

// // --- 模拟数据 ---
// const dummyResult = {
//     isFake: "是",
//     fakeType: "Photoshop编辑篡改",
//     confidence: { photoshop: 0.89, deepfake: 0.12, aigc: 0.08 },
//     resultImageUrl: "https://source.unsplash.com/random/800x600?abstract,art" 
// };

// --- 事件监听区域 ---

// 重点：为可见的div（uploadBox）注册点击事件
if (uploadBox) {
    uploadBox.addEventListener('click', () => {
        imageInput.click();
    });
    uploadBox.addEventListener('dragover', e => { e.preventDefault(); uploadBox.style.borderColor = '#6a5acd'; });
    uploadBox.addEventListener('dragleave', e => { e.preventDefault(); uploadBox.style.borderColor = '#d0dbe5'; });
    uploadBox.addEventListener('drop', e => {
        e.preventDefault();
        uploadBox.style.borderColor = '#d0dbe5';
        if (e.dataTransfer.files.length) {
            imageInput.files = e.dataTransfer.files;
            previewImage();
        }
    });
}

// 为隐藏的input注册change事件，以便在选择文件后进行预览
if (imageInput) {
    imageInput.addEventListener('change', previewImage);
}

// 检测按钮点击事件
if (detectBtn) {
    detectBtn.addEventListener('click', () => {
        if (!imageInput.files.length) {
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
    detectBtn.textContent = '检测中...';
    resultPlaceholder.textContent = '正在分析图像，请稍候...';
    resultPlaceholder.style.display = 'block';
    resultImagePreview.style.display = 'none';
    resultInfoDetails.style.display = 'none';
    
    try {
        const formData = new FormData();
        formData.append('image', imageInput.files[0]);
        
        const response = await fetch('/detect_action', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`检测失败: ${response.status}`);
        }
        
        const result = await response.json();
        
        // 显示结果
        resultImagePreview.src = 'data:image/jpeg;base64,' + result.processed_image;
        resultImagePreview.style.display = 'block';
        resultPlaceholder.style.display = 'none';
        
        resultIsFake.textContent = result.is_fake ? '是' : '否';
        resultFakeType.textContent = result.fake_type;
        
        // 格式化置信度评分
        if (result.confidence_scores) {
            const scores = result.confidence_scores;
            resultConfidenceScore.textContent = 
                `Photoshop: ${scores.photoshop}%\n` +
                `Deepfake: ${scores.deepfake}%\n` +
                `AIGC: ${scores.aigc}%`;
        }
        
        resultInfoDetails.style.display = 'block';
        
    } catch (error) {
        console.error('检测错误:', error);
        alert('检测失败: ' + error.message);
    } finally {
        detectBtn.disabled = false;
        detectBtn.textContent = '开始检测';
    }
}


function showDetectionResult(result) {
    resultImagePreview.src = result.resultImageUrl;
    resultImagePreview.style.display = 'block';
    resultPlaceholder.style.display = 'none';
    resultIsFake.textContent = result.isFake;
    resultFakeType.textContent = result.fakeType;
    resultConfidenceScore.textContent = `\n  - Photoshop: ${(result.confidence.photoshop * 100).toFixed(1)}%\n  - Deepfake: ${(result.confidence.deepfake * 100).toFixed(1)}%\n  - AIGC: ${(result.confidence.aigc * 100).toFixed(1)}%`;
    resultInfoDetails.style.display = 'block';
}

function resetResultArea() {
    resultImagePreview.src = '';
    resultImagePreview.style.display = 'none';
    resultPlaceholder.textContent = '检测结果将在此显示';
    resultPlaceholder.style.display = 'block';
    resultInfoDetails.style.display = 'none';
} 

