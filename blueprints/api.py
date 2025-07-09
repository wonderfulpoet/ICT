import os
import requests
from flask import Blueprint, request, jsonify
import cv2
import numpy as np
import base64
import random
import json
from pathlib import Path

bp = Blueprint('api', __name__, url_prefix="/")

@bp.route('/call_api', methods=['POST'])
def call_api():
    if request.method == 'POST':
        data = request.get_json()   
        
        # 解码Base64图像
        image_data = base64.b64decode(data['image_data'])
        description = data['description']
        file_name = data['file_name']
        
        np_img = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
        
        if img is None:
            return jsonify({'error': 'Failed to decode image'}), 400
            
        # 临时保存图像文件
        temp_path = f'./temp_image/temp_image_{random.randint(1000, 9999)}.jpg'
        cv2.imwrite(temp_path, img)
        
        # 调用模型API - 正确的方式
        with open(temp_path, 'rb') as f:
            response = requests.post(
                'http://localhost:5000/model_api',
                files={'img': f},  # 只发送文件
                data={  # 其他数据作为表单数据
                    'description': description,
                    'file_name': file_name,
                    'image_data': data['image_data']  # 如果需要的话
                }
            )
        
        # 删除临时文件
        os.remove(temp_path)
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'error': 'Model API failed', 'details': response.text}), 500
        
@bp.route('/model_api', methods=['POST'])
def model_api():
    try:
        # 检查是否有文件上传
        if 'img' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400

        # 获取上传的文件
        file = request.files['img']
        
        # 获取表单数据
        file_name = Path(request.form.get('file_name')).stem
        # description = request.form.get('description')
        # image_data = request.form.get('image_data')  # 可选
        
        if not file_name:
            return jsonify({'error': 'file_name is required'}), 400

        results_path = f'./all_results/{file_name}'
        
        # 读取 mask 图像
        mask = cv2.imread(f'{results_path}/{file_name}-mask.jpg', cv2.IMREAD_COLOR)
        if mask is None:
            return jsonify({'error': 'Failed to load mask image'}), 400

        # 将 mask 编码为 Base64
        _, mask_buffer = cv2.imencode('.jpg', mask)
        mask_base64 = base64.b64encode(mask_buffer).decode('utf-8')
        mask_url = f"data:image/jpeg;base64,{mask_base64}"

        # 读取 JSON 文件
        try:
            with open(f'{results_path}/{file_name}.json', 'r') as f:
                json_data = json.load(f)  # 首先解析外层JSON
                
                # description字段本身是一个JSON字符串，需要再次解析
                description_data = json.loads(json_data['description'])
                
                # 现在可以获取outputs
                description_output = description_data['outputs']
                
        except Exception as e:
            return jsonify({'error': f'Failed to read JSON file: {str(e)}'}), 400

        # print(description_output)
        # 处理上传的图像
        img_bytes = file.read()
        np_img = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
        
        if img is None:
            return jsonify({'error': 'Invalid image format'}), 400

        # 编码原始图像为 Base64
        _, img_buffer = cv2.imencode('.jpg', img)
        img_base64 = base64.b64encode(img_buffer).decode('utf-8')
        img_url = f"data:image/jpeg;base64,{img_base64}"

        return jsonify({
            "status": "success",
            "result": {
                "original_image": img_url,
                "processed_image": mask_url,
                "description": description_output,
            }
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "message": "模型处理失败"
        }), 500