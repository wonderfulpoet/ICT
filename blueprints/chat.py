from flask import Blueprint, request, jsonify, render_template, session
import cv2
import numpy as np
import base64
import os
import random
import requests
from werkzeug.utils import secure_filename
import base64
import csv
import PyPDF2
from config import *

bp = Blueprint('chat', __name__, url_prefix="/")

# API配置
API_KEY = os.environ.get("API_KEY", "sk-0d8f31e1cf5d4774bcf82f2f7624c02d")
API_URL = os.environ.get("API_URL", "https://api.deepseek.com/v1")


MODELS = {
    "Moonshot-8K": "moonshot-v1-8k",
    "Moonshot-32K": "moonshot-v1-32k"
}

# 免费模型和高级模型
FREE_MODELS = ["GLM-4-FlashX-P002"]
PREMIUM_MODELS = ["DeepSeek-R1", "DeepSeek-V3-250324-P001", "QwQ-N011-32B", "GLM-4-Plus-P002", 
                "GLM-4V-Plus-0111-P002", "Qwen2.5-VL-72B-Instruct-P003"]

@bp.route('/chat_page', methods=['GET', 'POST'])
def chat_page():
    available_models = MODELS.copy()
    is_logged_in = 'logged_in' in session

    # 如果未登录，只展示免费模型
    if not is_logged_in:
        # 移除高级模型
        for model_key in list(available_models.keys()):
            if available_models[model_key] in PREMIUM_MODELS:
                available_models.pop(model_key)
    
    return render_template('chat.html', models=available_models)

@bp.route('/chat', methods=['POST'])
def chat():
    data = request.form
    prompt = data.get('prompt', '')
    model_name = data.get('model', list(MODELS.values())[0])
    auto_search = data.get('auto_search', 'false').lower() == 'true'
    
    # 检查用户是否有权限使用选定的模型
    if model_name in PREMIUM_MODELS and not session.get('logged_in', False):
        return jsonify({"error": "您需要登录才能使用高级模型，请先登录或注册账号"})
    
    # 检查是否有文件上传
    file_content = ""
    file = request.files.get('file')
    image_base64 = None
    
    if file and file.filename != '' and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        # ---- 添加文件元数据记录 ----
        try:
            from blueprints.data_management import ensure_metadata_file, METADATA_FILE, METADATA_HEADER
            from datetime import datetime
            import uuid

            ensure_metadata_file()
            
            file_ext = filename.rsplit('.', 1)[1].lower()
            file_type = 'other'
            if file_ext in ['txt', 'md', 'json', 'csv', 'docx', 'pptx']:
                file_type = 'text'
            elif file_ext in ['png', 'jpg', 'jpeg', 'gif']:
                file_type = 'image'
            elif file_ext in ['pdf']:
                file_type = 'pdf'
            elif file_ext in ['xlsx', 'csv']:
                file_type = 'spreadsheet'

            metadata = {
                'id': str(uuid.uuid4()),
                'filename': filename,
                'filepath': file_path,
                'upload_time': datetime.now().isoformat(),
                'size_bytes': os.path.getsize(file_path),
                'file_type': file_type,
                'status': 'pending', # 初始状态为待处理
                'username': session.get('username', 'guest') 
            }
            
            with open(METADATA_FILE, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=METADATA_HEADER)
                # 如果文件是空的，先写header
                if f.tell() == 0:
                    writer.writeheader()
                writer.writerow(metadata)

        except Exception as e:
            current_app.logger.error(f"无法记录文件元数据: {e}")
        # ---- 元数据记录结束 ----
        
        # 处理不同类型的文件
        if filename.lower().endswith('.pdf'):
            file_content = extract_text_from_pdf(file_path)
            prompt = f"以下是PDF文档内容，请分析并回答: \n\n{file_content}\n\n{prompt}"
        elif filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            image_base64 = encode_image_to_base64(file_path)
            # 图片处理直接在API调用中进行
        else:
            # 其他文本文件
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                file_content = f.read()
            prompt = f"以下是文件内容，请分析并回答: \n\n{file_content}\n\n{prompt}"
    
    # 自动联网搜索功能
    search_details = []
    
    if auto_search:
        # 首先调用模型生成可能需要的搜索查询
        thinking_prompt = f"用户请求: {prompt}\n\n请分析用户问题，确定是否需要联网搜索额外信息。如果需要，生成1-3个搜索关键词，每个关键词应该能够帮助回答用户的问题。格式: 关键词1, 关键词2, 关键词3。如果不需要联网搜索，直接回复 '无需搜索'。请简洁回复，不需要额外解释。"
        
        thinking_response = call_llm_api(thinking_prompt, model_name)
        
        if "error" not in thinking_response:
            search_decision = thinking_response["choices"][0]["message"]["content"].strip()
            
            if search_decision.lower() != "无需搜索" and not search_decision.startswith("无需"):
                # 从模型回复中提取关键词
                search_keywords = [kw.strip() for kw in search_decision.split(',') if kw.strip()]
                
                # 限制关键词数量
                search_keywords = search_keywords[:3]
                
                search_results_combined = {}
                for keyword in search_keywords:
                    search_results = search_online(keyword)
                    if "error" not in search_results:
                        search_results_combined[keyword] = search_results
                        
                        # 从搜索结果中提取网站信息并添加到search_details
                        if 'organic' in search_results:
                            for result in search_results['organic'][:5]:  # 只取前5个结果
                                if 'link' in result and 'title' in result:
                                    search_details.append({
                                        'source': result['title'],
                                        'url': result['link']
                                    })
                
                if search_results_combined:
                    prompt = f"以下是相关的搜索结果:\n\n{json.dumps(search_results_combined, ensure_ascii=False, indent=2)}\n\n请基于这些信息回答用户问题: {prompt}"
        # 调用大模型API
    response = call_llm_api(prompt, model_name, image_base64)
    
    if "error" in response:
        return jsonify({"error": response["error"]})
    
    try:
        answer = response["choices"][0]["message"]["content"]
        
        # 从回答中移除所有<think></think>标签及其内容
        answer = re.sub(r'<think>.*?</think>', '', answer, flags=re.DOTALL)
        answer = answer.strip()
        
        # 返回结果，不包含搜索详情
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": f"解析API响应出错: {str(e)}", "raw_response": response})
    
@bp.route('/search', methods=['POST'])
def search():
    data = request.form    
    query = data.get('query', '')
    if not query:
        return jsonify({"error": "搜索查询不能为空"})
    results = search_online(query)
    return jsonify(results)



# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'docx', 'xlsx', 'pptx', 'md', 'csv', 'json'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def call_llm_api(prompt, model_name, image_base64=None):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    if image_base64:
        content = [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
        ]
    else:
        content = prompt

    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": content}],
        "temperature": 0.7,
        "max_tokens": 10000
    }
    try:
        response = requests.post(f"{API_URL}/v1/chat/completions", headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API请求失败，状态码: {response.status_code}", "details": response.text}
    except Exception as e:
        return {"error": f"调用API过程中出错: {str(e)}"}
    

def extract_text_from_pdf(file_path):
    """从PDF文件中提取文本"""
    text = ""
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        text = f"PDF解析错误: {str(e)}"
    return text


def encode_image_to_base64(image_path):
    """将图片编码为base64字符串"""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        return f"图片编码错误: {str(e)}"


def search_online(query):
    """使用提供的API进行在线搜索"""
    try:
        url = f"example.com/search?query={query}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"搜索请求失败，状态码: {response.status_code}"}
    except Exception as e:
        return {"error": f"搜索过程中出错: {str(e)}"}
