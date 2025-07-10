// DOM Elements
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
const resultAnalysis = document.getElementById('result-analysis');
const uploadBtn = document.getElementById('upload-btn');
const clearBtn = document.getElementById('clear-btn');
const downloadBtn = document.getElementById('download-btn');
const imageDescription = document.getElementById('image-description');
const charCount = document.getElementById('char-count');
const resultTextOutput = document.getElementById('result-text-output');
const copyTextBtn = document.getElementById('copy-text-btn');

// Event Listeners
if (uploadBox) {
    uploadBox.addEventListener('click', () => imageInput.click());
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

if (imageInput) imageInput.addEventListener('change', previewImage);
if (detectBtn) detectBtn.addEventListener('click', startDetection);
if (uploadBtn) uploadBtn.addEventListener('click', () => imageInput.click());
if (clearBtn) clearBtn.addEventListener('click', resetInputArea);
if (downloadBtn) downloadBtn.addEventListener('click', downloadResult);
if (imageDescription && charCount) {
    imageDescription.addEventListener('input', updateCharCount);
}
if (copyTextBtn) {
    copyTextBtn.addEventListener('click', copyResultText);
}

// Functions
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

function updateCharCount() {
    const currentLength = imageDescription.value.length;
    charCount.textContent = currentLength;
    
    if (currentLength > 180) {
        charCount.style.color = '#ff6b6b';
    } else {
        charCount.style.color = 'inherit';
    }
}

async function startDetection() {
    if (!imageInput.files || !imageInput.files.length) {
        alert("请先上传一张图片！");
        return;
    }

    detectBtn.disabled = true;
    detectBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 检测中...';
    resultPlaceholder.textContent = '正在分析图像，请稍候...';
    resultPlaceholder.style.display = 'block';
    resultImagePreview.style.display = 'none';
    resultInfoDetails.style.display = 'none';
    resultTextOutput.innerHTML = '<p><i class="fas fa-spinner fa-spin"></i> 正在生成分析结果...</p>';
    
    try {
        const file = imageInput.files[0];
        const description = imageDescription.value || '';
        const fileName = file.name;

        const imageBase64 = await new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result);
            reader.onerror = reject;
            reader.readAsDataURL(file);
        });
        
        const response = await fetch('/call_api', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                image_data: imageBase64.split(',')[1],
                description: description,
                file_name: fileName
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || `检测失败: ${response.status}`);
        }
        
        const result = await response.json();
        displayDetectionResult(result);
        
    } catch (error) {
        console.error('检测错误:', error);
        resultPlaceholder.textContent = '检测失败: ' + error.message;
        resultPlaceholder.style.display = 'block';
        resultTextOutput.innerHTML = `<p class="error-text">检测失败: ${error.message}</p>`;
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
    
    if (data.processed_image) {
        resultImagePreview.src = data.processed_image;
        resultImagePreview.style.display = 'block';
        resultPlaceholder.style.display = 'none';
    }

    if (data.description){
        resultTextOutput.innerHTML = data.description;
    }

    resultIsFake.textContent = data.is_fake ? '是' : '否';
    // 更新伪造类型显示
    if (data.fake_type) {
        resultFakeType.textContent = data.fake_type;
    } else {
        resultFakeType.textContent = '未知';
    }
    
    // 如果有置信度评分，可以这样显示
    if (data.confidence_scores) {
        const scores = data.confidence_scores;
        resultConfidenceScore.innerHTML = scores;
    }
    
    // 如果有分析说明
    if (data.analysis) {
        resultAnalysis.textContent = data.analysis;
    }
    
    // 显示结果详情区域
    resultInfoDetails.style.display = 'block';
    downloadBtn.disabled = false;
    copyTextBtn.disabled = false;
}

function resetInputArea() {
    imageInput.value = '';
    inputPreview.src = '';
    inputPreview.style.display = 'none';
    uploadPlaceholder.style.display = 'block';
    imageDescription.value = '';
    charCount.textContent = '0';
    charCount.style.color = 'inherit';
    resetResultArea();
}

function resetResultArea() {
    resultImagePreview.src = '';
    resultImagePreview.style.display = 'none';
    resultPlaceholder.textContent = '检测结果将在此显示';
    resultPlaceholder.style.display = ';none';
    resultInfoDetails.style.display = 'none';
    resultIsFake.textContent = '';
    resultFakeType.textContent = '';
    resultConfidenceScore.textContent = '';
    resultAnalysis.textContent = '';
    resultTextOutput.innerHTML = '<p>检测结果文本将在此显示...</p>';
    downloadBtn.disabled = true;
    copyTextBtn.disabled = true;
}

function downloadResult() {
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
}

function copyResultText() {
    const textToCopy = resultTextOutput.innerText;
    navigator.clipboard.writeText(textToCopy).then(() => {
        const originalText = copyTextBtn.innerHTML;
        copyTextBtn.innerHTML = '<i class="fas fa-check"></i> 已复制';
        copyTextBtn.style.backgroundColor = '#28a745';
        setTimeout(() => {
            copyTextBtn.innerHTML = originalText;
            copyTextBtn.style.backgroundColor = '#555';
        }, 2000);
    }).catch(err => {
        console.error('复制失败:', err);
        alert('复制文本失败，请手动选择文本复制');
    });
}