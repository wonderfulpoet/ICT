import os
import json
import requests
import csv
from flask import Flask, render_template, request, jsonify, url_for, redirect, send_from_directory, session, flash, g
from werkzeug.utils import secure_filename
import base64
from io import BytesIO
from PIL import Image
import PyPDF2
import re
import traceback
from functools import wraps
from dotenv import load_dotenv
import secrets
from blueprints.detection import bp as dect_bp
from blueprints.qa import bp as qa_bp
from blueprints.data_management import bp as data_bp
from blueprints.model_center import bp as model_center_bp
from blueprints.settings import bp as settings_bp
# 加载环境变量
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(16))
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 限制上传文件大小为16MB
app.config['PORT'] = 3000
app.config['PASSWORD_FILE'] = 'password/pswd.csv'

app.register_blueprint(dect_bp)
app.register_blueprint(qa_bp)
app.register_blueprint(data_bp)
app.register_blueprint(model_center_bp)
app.register_blueprint(settings_bp)

# 确保上传文件夹存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# API配置
API_KEY = os.environ.get("API_KEY", "sk-0d8f31e1cf5d4774bcf82f2f7624c02d")
API_URL = os.environ.get("API_URL", "https://api.deepseek.com")
# 模型列表
# 这里的模型名称和ID需要根据实际API进行调整
MODELS = {
    "Moonshot-8K": "moonshot-v1-8k",
    "Moonshot-32K": "moonshot-v1-32k",
    "deepseek": "deepseek-r1",
    "DeepSeek-V3-250324-P001": "deepseek-v3-250"
}

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'docx', 'xlsx', 'pptx', 'md', 'csv', 'json'}

# 免费模型和高级模型
FREE_MODELS = ["GLM-4-FlashX-P002"]
PREMIUM_MODELS = ["DeepSeek-R1", "DeepSeek-V3-250324-P001", "QwQ-N011-32B", "GLM-4-Plus-P002", 
                "GLM-4V-Plus-0111-P002", "Qwen2.5-VL-72B-Instruct-P003"]

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.before_request
def my_before_request():
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

def get_users():
    """从CSV文件中获取所有用户信息"""
    users = {}
    
    # 确保密码文件所在目录存在
    os.makedirs(os.path.dirname(app.config['PASSWORD_FILE']), exist_ok=True)
    
    # 如果文件不存在，创建一个默认文件
    if not os.path.exists(app.config['PASSWORD_FILE']):
        with open(app.config['PASSWORD_FILE'], 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['username', 'password'])
            writer.writerow(['admin', 'admin123'])
    
    # 读取用户信息
    try:
        with open(app.config['PASSWORD_FILE'], 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                users[row['username']] = row['password']
    except Exception as e:
        print(f"读取用户文件出错: {str(e)}")
    
    return users

def add_user(username, password):
    """将新用户添加到CSV文件中"""
    try:
        users = get_users()
        
        # 用户已存在
        if username in users:
            return False
        
        # 添加新用户
        with open(app.config['PASSWORD_FILE'], 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([username, password])
        
        return True
    except Exception as e:
        print(f"添加用户出错: {str(e)}")
        return False

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

@app.route('/')
def index():
    # 根据用户登录状态准备可用模型
    available_models = MODELS.copy()
    is_logged_in = 'logged_in' in session
    
    # 如果未登录，只展示免费模型
    if not is_logged_in:
        # 移除高级模型
        for model_key in list(available_models.keys()):
            if available_models[model_key] in PREMIUM_MODELS:
                available_models.pop(model_key)
    
    return render_template('index.html', models=available_models)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        users = get_users()
        
        if username in users and users[username] == password:
            session['logged_in'] = True
            session['username'] = username
            
            # 检查是否应该有高级模型访问权限
            session['premium_access'] = True  # 所有登录用户都有高级访问权限
            
            flash('登录成功!', 'success')
            return redirect(url_for('index'))
        else:
            flash('用户名或密码错误!', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if not username or not password:
            flash('用户名和密码不能为空!', 'error')
        elif password != confirm_password:
            flash('两次密码输入不一致!', 'error')
        else:
            if add_user(username, password):
                flash('注册成功，请登录!', 'success')
                return redirect(url_for('login'))
            else:
                flash('用户名已存在!', 'error')
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('您已成功退出登录!', 'success')
    return redirect(url_for('login'))

@app.route('/chat', methods=['POST'])
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
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
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

@app.route('/search', methods=['POST'])
def search():
    data = request.form    
    query = data.get('query', '')
    if not query:
        return jsonify({"error": "搜索查询不能为空"})
    results = search_online(query)
    return jsonify(results)

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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=app.config['PORT'])