from flask import Blueprint, request, jsonify, render_template, session
import cv2
import numpy as np
import base64
import os
import random

bp = Blueprint('qa', __name__, url_prefix="/")

MODELS = {
    "Moonshot-8K": "moonshot-v1-8k",
    "Moonshot-32K": "moonshot-v1-32k"
}

# 免费模型和高级模型
FREE_MODELS = ["GLM-4-FlashX-P002"]
PREMIUM_MODELS = ["DeepSeek-R1", "DeepSeek-V3-250324-P001", "QwQ-N011-32B", "GLM-4-Plus-P002", 
                "GLM-4V-Plus-0111-P002", "Qwen2.5-VL-72B-Instruct-P003"]

@bp.route('/qa', methods=['GET', 'POST'])
def qa():
    available_models = MODELS.copy()
    is_logged_in = 'logged_in' in session
    
    # 如果未登录，只展示免费模型
    if not is_logged_in:
        # 移除高级模型
        for model_key in list(available_models.keys()):
            if available_models[model_key] in PREMIUM_MODELS:
                available_models.pop(model_key)
    
    return render_template('chat.html', models=available_models)