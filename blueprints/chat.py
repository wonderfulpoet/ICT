# --- START OF REPLACEMENT for chat.py ---
from flask import Blueprint, request, jsonify, render_template, session, current_app
import cv2
import numpy as np
import base64
import os
import random
import requests
from werkzeug.utils import secure_filename
import csv
from config import *
import json
import re
from io import BytesIO  # 用于在内存中处理文件

# --- 用于处理不同文件类型的库 ---
# PyMuPDF性能更高，如果已安装，可以使用它代替PyPDF2
try:
    import fitz  # PyMuPDF

    pdf_lib = 'fitz'
except ImportError:
    import PyPDF2

    pdf_lib = 'PyPDF2'

# import docx  # 用于处理.docx

bp = Blueprint('chat', __name__, url_prefix="/")

# API配置
API_KEY = os.environ.get("API_KEY", "sk-0d8f31e1cf5d4774bcf82f2f7624c02d")
API_URL = os.environ.get("API_URL", "https://api.deepseek.com/v1")

# --- 模型定义保持不变 ---
MODELS = {
    "Moonshot-8K": "moonshot-v1-8k",
    "Moonshot-32K": "moonshot-v1-32k"
}
FREE_MODELS = ["GLM-4-FlashX-P002"]
PREMIUM_MODELS = ["DeepSeek-R1", "DeepSeek-V3-250324-P001", "QwQ-N011-32B", "GLM-4-Plus-P002",
                  "GLM-4V-Plus-0111-P002", "Qwen2.5-VL-72B-Instruct-P003"]


# --- 路由 /chat_page, /chat, /search 和辅助函数保持不变 ---

@bp.route('/chat_page', methods=['GET', 'POST'])
def chat_page():
    available_models = MODELS.copy()
    is_logged_in = 'logged_in' in session

    if not is_logged_in:
        for model_key in list(available_models.keys()):
            if available_models[model_key] in PREMIUM_MODELS:
                available_models.pop(model_key)

    return render_template('chat.html', models=available_models)


@bp.route('/chat', methods=['POST'])
def chat():
    # ... (这部分代码保持不变，服务于 chat.html 页面) ...
    data = request.form
    prompt = data.get('prompt', '')
    model_name = data.get('model', list(MODELS.values())[0])
    auto_search = data.get('auto_search', 'false').lower() == 'true'

    if model_name in PREMIUM_MODELS and not session.get('logged_in', False):
        return jsonify({"error": "您需要登录才能使用高级模型，请先登录或注册账号"})

    file_content = ""
    file = request.files.get('file')
    image_base64 = None

    if file and file.filename != '' and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

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
                'id': str(uuid.uuid4()), 'filename': filename, 'filepath': file_path,
                'upload_time': datetime.now().isoformat(), 'size_bytes': os.path.getsize(file_path),
                'file_type': file_type, 'status': 'pending', 'username': session.get('username', 'guest')
            }

            with open(METADATA_FILE, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=METADATA_HEADER)
                if f.tell() == 0: writer.writeheader()
                writer.writerow(metadata)
        except Exception as e:
            current_app.logger.error(f"无法记录文件元数据: {e}")

        if filename.lower().endswith('.pdf'):
            file_content = extract_text_from_pdf(file_path)
            prompt = f"以下是PDF文档内容，请分析并回答: \n\n{file_content}\n\n{prompt}"
        elif filename.lower().endswith(('.png', '.jpg', 'jpeg', '.gif')):
            image_base64 = encode_image_to_base64(file_path)
        else:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                file_content = f.read()
            prompt = f"以下是文件内容，请分析并回答: \n\n{file_content}\n\n{prompt}"

    search_details = []

    if auto_search:
        thinking_prompt = f"用户请求: {prompt}\n\n请分析用户问题，确定是否需要联网搜索额外信息。如果需要，生成1-3个搜索关键词，每个关键词应该能够帮助回答用户的问题。格式: 关键词1, 关键词2, 关键词3。如果不需要联网搜索，直接回复 '无需搜索'。请简洁回复，不需要额外解释。"
        thinking_response = call_llm_api(thinking_prompt, model_name)
        if "error" not in thinking_response:
            search_decision = thinking_response["choices"][0]["message"]["content"].strip()
            if search_decision.lower() != "无需搜索" and not search_decision.startswith("无需"):
                search_keywords = [kw.strip() for kw in search_decision.split(',') if kw.strip()][:3]
                search_results_combined = {}
                for keyword in search_keywords:
                    search_results = search_online(keyword)
                    if "error" not in search_results:
                        search_results_combined[keyword] = search_results
                        if 'organic' in search_results:
                            for result in search_results['organic'][:5]:
                                if 'link' in result and 'title' in result:
                                    search_details.append({'source': result['title'], 'url': result['link']})
                if search_results_combined:
                    prompt = f"以下是相关的搜索结果:\n\n{json.dumps(search_results_combined, ensure_ascii=False, indent=2)}\n\n请基于这些信息回答用户问题: {prompt}"

    response = call_llm_api(prompt, model_name, image_base64)

    if "error" in response:
        return jsonify({"error": response["error"]})

    try:
        answer = response["choices"][0]["message"]["content"]
        answer = re.sub(r'<think>.*?</think>', '', answer, flags=re.DOTALL).strip()
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": f"解析API响应出错: {str(e)}", "raw_response": response})


@bp.route('/search', methods=['POST'])
def search():
    data = request.form
    query = data.get('query', '')
    if not query: return jsonify({"error": "搜索查询不能为空"})
    results = search_online(query)
    return jsonify(results)


ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'docx', 'xlsx', 'pptx', 'md', 'csv', 'json'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# --- call_llm_api 保持不变 ---
def call_llm_api(prompt, model_name, image_base64=None):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    content_parts = []
    if prompt:
        content_parts.append({"type": "text", "text": prompt})
    if image_base64:
        # 确保只传递Base64编码部分
        if "base64," in image_base64:
            image_base64 = image_base64.split(',', 1)[1]
        content_parts.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
        })
    if not content_parts:
        return {"error": "没有提供任何输入（文本或图片）"}

    is_vision_model = 'vl' in model_name or 'v2' in model_name

    # 修正 content 格式
    content_to_send = content_parts if is_vision_model and image_base64 else prompt

    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": content_to_send}],
        "temperature": 0.7,
        "max_tokens": 4096
    }
    if image_base64 and not is_vision_model:
        return {"error": f"模型 '{model_name}' 不支持图片输入。请选择视觉模型。"}
    try:
        response = requests.post(f"{API_URL}/chat/completions", headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        error_details = http_err.response.text
        try:
            error_json = http_err.response.json()
            error_message = error_json.get('error', {}).get('message', '未知API错误')
            details = f"API返回错误: {error_message} (状态码: {http_err.response.status_code})"
        except json.JSONDecodeError:
            details = f"API返回了非JSON格式的错误: {error_details} (状态码: {http_err.response.status_code})"
        return {"error": "API请求失败", "details": details}
    except Exception as e:
        return {"error": f"调用API过程中发生未知错误: {str(e)}"}


# --- 辅助函数：extract_text_from_pdf, encode_image_to_base64, search_online 保持不变 ---
def extract_text_from_pdf(file_path_or_stream):
    text = ""
    try:
        if pdf_lib == 'fitz':
            # PyMuPDF 可以直接从内存流读取
            with fitz.open(stream=file_path_or_stream, filetype="pdf") as doc:
                for page in doc:
                    text += page.get_text()
        else:  # PyPDF2
            # PyPDF2 需要一个文件对象
            reader = PyPDF2.PdfReader(file_path_or_stream)
            for page in reader.pages:
                text += page.extract_text() or "" + "\n"  # 确保返回字符串
    except Exception as e:
        text = f"PDF解析错误: {str(e)}"
    return text


# def extract_text_from_docx(stream):
#     text = ""
#     try:
#         doc = docx.Document(stream)
#         text = "\n".join([para.text for para in doc.paragraphs])
#     except Exception as e:
#         text = f"Word文档解析错误: {str(e)}"
#     return text


def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        return f"图片编码错误: {str(e)}"


def search_online(query):
    try:
        url = f"example.com/search?query={query}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"搜索请求失败，状态码: {response.status_code}"}
    except Exception as e:
        return {"error": f"搜索过程中出错: {str(e)}"}


# === 关键修改：重构 /api/chat 端点以处理多种文件类型 ===
@bp.route('/api/chat', methods=['POST'])
def api_chat():
    """处理来自聊天小部件的AJAX请求，支持图片、PDF和Word文档"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "无效的请求，需要JSON格式数据"}), 400

        user_prompt = data.get('prompt', '')
        data_uri = data.get('image_base64')  # 这个字段现在可能包含任何文件类型

        final_prompt = user_prompt
        image_base64_for_api = None

        # 如果有文件数据，进行处理
        if data_uri:
            # 1. 解析 Data URI
            try:
                match = re.match(r'data:(?P<mime_type>.*?);base64,(?P<data>.*)', data_uri)
                if not match:
                    raise ValueError("无效的Data URI格式")

                mime_type = match.group('mime_type')
                encoded_data = match.group('data')
                decoded_bytes = base64.b64decode(encoded_data)
                file_stream = BytesIO(decoded_bytes)
            except (ValueError, IndexError, base64.binascii.Error) as e:
                current_app.logger.error(f"Base64解码或Data URI解析失败: {e}")
                return jsonify({"error": "无效的文件数据格式"}), 400

            # 2. 根据 MIME 类型分流处理
            file_content_text = ""
            if 'image' in mime_type:
                # 如果是图片，保留Base64编码给视觉模型
                image_base64_for_api = encoded_data
                file_content_text = "[用户上传了一张图片]"

            elif 'pdf' in mime_type:
                # 如果是PDF，提取文本
                file_content_text = extract_text_from_pdf(file_stream)
                if "PDF解析错误" in file_content_text:
                    return jsonify({"error": file_content_text}), 500

            # elif 'vnd.openxmlformats-officedocument.wordprocessingml.document' in mime_type:
            #     # 如果是 .docx，提取文本
            #     file_content_text = extract_text_from_docx(file_stream)
            #     if "Word文档解析错误" in file_content_text:
            #         return jsonify({"error": file_content_text}), 500

            else:
                # 对于其他文本类型如.txt，可以直接解码
                try:
                    file_content_text = decoded_bytes.decode('utf-8')
                except UnicodeDecodeError:
                    file_content_text = "[用户上传了一个无法预览的二进制文件]"

            # 3. 组合最终的 prompt
            final_prompt = f"请基于以下文件内容回答问题。\n\n--- 文件内容开始 ---\n{file_content_text}\n--- 文件内容结束 ---\n\n用户问题：{user_prompt}"

        # 4. 选择合适的模型并调用API
        # 如果有图片，必须用视觉模型；否则用普通聊天模型
        model_name = "deepseek-vl-chat" if image_base64_for_api else "deepseek-chat"

        response = call_llm_api(final_prompt, model_name, image_base64_for_api)

        if "error" in response:
            error_msg = response.get("details", response["error"])
            current_app.logger.error(f"LLM API call failed: {error_msg}")
            return jsonify({"error": f"调用AI服务失败: {error_msg}"}), 500

        answer = response.get("choices", [{}])[0].get("message", {}).get("content", "抱歉，我无法生成回复。")
        answer = re.sub(r'<think>.*?</think>', '', answer, flags=re.DOTALL).strip()

        return jsonify({"answer": answer})

    except Exception as e:
        current_app.logger.error(f"Error in /api/chat: {e}", exc_info=True)
        return jsonify({"error": "服务器内部发生未知错误。"}), 500
# --- END OF REPLACEMENT for chat.py ---