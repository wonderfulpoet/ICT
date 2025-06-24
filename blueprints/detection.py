from flask import Blueprint, request, jsonify, render_template
import cv2
import numpy as np
import base64
import os
import random

bp = Blueprint('detection', __name__, url_prefix="/")

@bp.route('/detection', methods=['GET', 'POST'])
def detection():
    return render_template('detection.html')

@bp.route('/detect_action', methods=['POST'])
def detect_action():

    if 'image' not in request.files:
        return jsonify({'error': '未提供图片'}), 400
    
    img = request.files['image']

    output_path = './uploads/1_out.png'
    if not os.path.exists(output_path):
        return jsonify({'error': 'Processed image not found'}), 404
    
    # Read the image using OpenCV
    processed_img = cv2.imread(output_path)
    # Convert to base64
    _, img_encoded = cv2.imencode('.jpg', processed_img)
    img_base64 = base64.b64encode(img_encoded).decode('utf-8')
    
    # Generate detection results (example values)
    return jsonify({
        'processed_image': img_base64,
        'is_fake': False,  # or False based on your detection
        'fake_type': 'Photoshop编辑篡改',
        'confidence_scores': {
            'photoshop': round(random.uniform(80, 95)),
            'deepfake': round(random.uniform(5, 20)),
            'aigc': round(random.uniform(5, 15))
        }
    })
        