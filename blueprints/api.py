import os
import requests
from flask import Blueprint, request, jsonify
import cv2
import numpy as np
import base64
import random

bp = Blueprint('api', __name__, url_prefix="/")

@bp.route('/call_api', methods=['POST'])
def call_api():
    if request.method == 'POST':
        data = request.get_json()   
        
        # 解码Base64图像
        image_data = base64.b64decode(data['image_data'])  # 移除data:image前缀
        np_img = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
        
        if img is None:
            return jsonify({'error': 'Failed to decode image'}), 400
            
        # 临时保存图像文件
        temp_path = f'./temp_image/temp_image_{random.randint(1000, 9999)}.jpg'
        cv2.imwrite(temp_path, img)
        
        # 调用模型API
        with open(temp_path, 'rb') as f:
            response = requests.post(
                'http://localhost:3000/model_api',
                files={'img': f}
            )
        
        # 删除临时文件
        os.remove(temp_path)
        print(response.json())
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'error': 'Model API failed'}), 500


@bp.route('/model_api', methods=['POST'])
def model_api():
    try:
        if 'img' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
            
        file = request.files['img']
        img_bytes = file.read()
        np_img = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
        
        if img is None:
            return jsonify({'error': 'Invalid image format'}), 400
        
        # 模拟模型处理
        is_fake = random.choice([True, False])
        fake_types = ["Photoshop编辑", "Deepfake换脸", "AI生成", "复制粘贴篡改"]
        fake_type = random.choice(fake_types)
        
        confidence = {
            "photoshop": round(random.uniform(0, 100), 1),
            "deepfake": round(random.uniform(0, 100), 1),
            "aigc": round(random.uniform(0, 100), 1)
        }
        
        # 添加红色边框作为处理效果
        processed_img = cv2.copyMakeBorder(
            img, 10, 10, 10, 10, 
            cv2.BORDER_CONSTANT, 
            value=[0, 0, 255]  # 红色边框
        )
        
        # 编码为Base64 (完整的数据URL)
        _, buffer = cv2.imencode('.jpg', processed_img)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        processed_image_url = f"data:image/jpeg;base64,{img_base64}"
        
        return jsonify({
            "status": "success",
            "result": {
                "is_fake": is_fake,
                "fake_type": fake_type,
                "confidence_scores": confidence,  # 保持前端使用的字段名一致
                "processed_image": processed_image_url,  # 完整的data URL
                "text_report": f"""
                    检测报告：
                    - 伪造可能性: {'高' if is_fake else '低'}
                    - 主要伪造类型: {fake_type}
                    - 置信度:
                      * Photoshop: {confidence['photoshop']}%
                      * Deepfake: {confidence['deepfake']}%
                      * AI生成: {confidence['aigc']}%
                """
            }
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "message": "模型处理失败"
        }), 500