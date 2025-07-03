from flask import Blueprint, render_template, jsonify
from .models_data import MODELS_DATA

bp = Blueprint('model_center', __name__, url_prefix='/models')

@bp.route('/')
def index():
    """渲染模型中心页面框架"""
    # 这个路由只返回html片段，由前端JS加载
    return render_template('model_center.html')

@bp.route('/api/list')
def get_models():
    """提供模型列表数据"""
    # 在实际应用中，这里可以添加认证和权限控制
    return jsonify(MODELS_DATA) 