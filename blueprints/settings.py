from flask import Blueprint, render_template, jsonify

bp = Blueprint('settings', __name__, url_prefix='/settings')

@bp.route('/')
def index():
    """渲染设置页面框架"""
    return render_template('settings.html')
 