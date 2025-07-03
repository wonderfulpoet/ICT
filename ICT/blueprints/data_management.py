from flask import Blueprint, render_template, request, jsonify, current_app, g, redirect
from functools import wraps
import csv
import os
from datetime import datetime, timedelta

bp = Blueprint('data_management', __name__, url_prefix='/data')

METADATA_FILE = 'data/file_metadata.csv'
METADATA_HEADER = ['id', 'filename', 'filepath', 'upload_time', 'size_bytes', 'file_type', 'status', 'username']

def ensure_metadata_file():
    """确保元数据文件和目录存在"""
    os.makedirs(os.path.dirname(METADATA_FILE), exist_ok=True)
    if not os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(METADATA_HEADER)

def login_required(f):
    """自定义的登录验证装饰器，适配蓝图"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.logged_in:
            # 对于AJAX请求，返回JSON错误
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify(error='请先登录以访问此页面'), 401
            # 对于普通请求，可以重定向到登录页，但在此SPA结构中返回错误更合适
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/')
@login_required
def index():
    """渲染数据管理页面框架"""
    # 这个路由只返回html片段，由前端JS加载
    return render_template('data_management.html')

@bp.route('/files')
@login_required
def get_files():
    """获取并筛选文件列表"""
    ensure_metadata_file()
    
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    per_page = 10 # 每页显示10条
    search_query = request.args.get('search', '')
    date_range = request.args.get('date', 'all') # all, today, week, month
    file_types = request.args.getlist('type') # ['text', 'image', ...]
    status = request.args.get('status', 'all') # all, processed, pending

    records = []
    with open(METADATA_FILE, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        # 只读取属于当前登录用户的文件
        records = [row for row in reader if row['username'] == g.username]
    
    # 筛选逻辑
    # 1. 按文件名搜索
    if search_query:
        records = [r for r in records if search_query.lower() in r['filename'].lower()]

    # 2. 按状态筛选
    if status != 'all':
        records = [r for r in records if r['status'] == status]

    # 3. 按文件类型筛选
    if file_types:
        records = [r for r in records if r['file_type'] in file_types]
    
    # 4. 按日期范围筛选
    if date_range != 'all':
        now = datetime.now()
        if date_range == 'today':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif date_range == 'week':
            start_date = now - timedelta(days=now.weekday())
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif date_range == 'month':
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            start_date = None
            
        if start_date:
            records = [r for r in records if datetime.fromisoformat(r['upload_time']) >= start_date]

    # 按上传时间降序排序
    records.sort(key=lambda r: r['upload_time'], reverse=True)
    
    total_records = len(records)
    
    # 分页
    start = (page - 1) * per_page
    end = start + per_page
    paginated_records = records[start:end]

    return jsonify({
        'records': paginated_records,
        'total': total_records,
        'page': page,
        'per_page': per_page,
        'pages': (total_records + per_page - 1) // per_page
    })

@bp.route('/delete', methods=['POST'])
@login_required
def delete_files():
    """删除文件"""
    ensure_metadata_file()
    file_ids_to_delete = request.json.get('ids', [])
    if not file_ids_to_delete:
        return jsonify(error="没有提供文件ID"), 400

    remaining_records = []
    deleted_files_info = []
    with open(METADATA_FILE, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # 检查文件是否属于当前用户并且ID匹配
            if row['id'] in file_ids_to_delete and row['username'] == g.username:
                deleted_files_info.append(row)
            else:
                remaining_records.append(row)

    # 从文件系统中删除文件
    for info in deleted_files_info:
        try:
            os.remove(info['filepath'])
        except OSError as e:
            # 即便文件删除失败，也继续从元数据中移除
            current_app.logger.error(f"无法删除文件 {info['filepath']}: {e}")

    # 重写元数据文件
    with open(METADATA_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=METADATA_HEADER)
        writer.writeheader()
        writer.writerows(remaining_records)

    return jsonify(success=True, message=f"成功删除了 {len(deleted_files_info)} 个文件。") 