import os
import json
import requests
import csv
from flask import Flask, render_template, request, jsonify, url_for, redirect, send_from_directory, session, flash, g
from datetime import timedelta
from io import BytesIO
from PIL import Image

import re
import traceback
from functools import wraps
from dotenv import load_dotenv
import secrets
from blueprints.detection import bp as dect_bp
from blueprints.chat import bp as chat_bp
from blueprints.data_management import bp as data_bp
from blueprints.model_center import bp as model_center_bp
from blueprints.settings import bp as settings_bp
from blueprints.menu import bp as menu_bp
from blueprints.api import bp as api_bp
from config import *
# 加载环境变量
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(16))
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH  # 限制上传文件大小为16MB
app.config['PORT'] = PORT
app.config['PASSWORD_FILE'] = PASSWORD_FILE
# 在创建 app 后添加这些配置
app.config.update(
    SECRET_KEY=os.environ.get("SECRET_KEY") or 'your-fallback-secret-key-here',
    PERMANENT_SESSION_LIFETIME=timedelta(days=7),
    SESSION_COOKIE_SECURE=False,  # 开发时设为 False，生产环境设为 True
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax'
)

app.register_blueprint(dect_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(data_bp)
app.register_blueprint(model_center_bp)
app.register_blueprint(settings_bp)
app.register_blueprint(menu_bp)
app.register_blueprint(api_bp)

# 确保上传文件夹存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


# 模型列表
# 这里的模型名称和ID需要根据实际API进行调整
MODELS = {
    "Moonshot-8K": "moonshot-v1-8k",
    "Moonshot-32K": "moonshot-v1-32k",
    "deepseek-chat": "deepseek-r1",
    "DeepSeek-V3-250324-P001": "deepseek-v3-250"
}



# 免费模型和高级模型
FREE_MODELS = ["GLM-4-FlashX-P002"]
PREMIUM_MODELS = ["DeepSeek-R1", "DeepSeek-V3-250324-P001", "QwQ-N011-32B", "GLM-4-Plus-P002", 
                "GLM-4V-Plus-0111-P002", "Qwen2.5-VL-72B-Instruct-P003"]



# 上下文传递
@app.before_request
def my_before_request():
    session.permanent = True  # 确保会话是永久的
    username=session.get('username', None)
    logged_in = session.get('logged_in', False)
    if username:
        setattr(g,'username',username)
        setattr(g,'logged_in',logged_in)
    else:
        setattr(g,'username',None)
        setattr(g,'logged_in',False)

@app.context_processor
def my_context_porcessor():
    return {'username':g.username,'logged_in':g.logged_in}


@app.route('/')
def welcome():
    return render_template('welcome.html')


# 全局错误处理
@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({"error": "文件大小超过限制（最大16MB）"}), 413

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "请求的资源不存在"}), 404

@app.errorhandler(500)
def internal_server_error(error):
    app.logger.error(f"服务器错误: {error}\n{traceback.format_exc()}")
    return jsonify({"error": "服务器内部错误，请稍后再试"}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error(f"未处理的异常: {str(e)}\n{traceback.format_exc()}")
    return jsonify({"error": f"发生错误: {str(e)}"}), 500

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """提供上传文件的访问"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# @app.route('/chat', methods=['GET'])
# def chat_page():
#     available_models = MODELS.copy()
#     is_logged_in = 'logged_in' in session
#     if not is_logged_in:
#         for model_key in list(available_models.keys()):
#             if available_models[model_key] in PREMIUM_MODELS:
#                 available_models.pop(model_key)
#     return render_template('chat.html', models=available_models, logged_in=is_logged_in)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=app.config['PORT'])