from flask import Blueprint, render_template, jsonify
from datetime import datetime, timedelta
import random

bp = Blueprint('settings', __name__, url_prefix='/settings')

@bp.route('/')
def index():
    """渲染设置页面框架"""
    return render_template('settings.html')

@bp.route('/api/system-info')
def get_system_info():
    """提供模拟的系统信息"""
    
    # 模拟登录设备
    devices = [
        {
            "id": 1,
            "type": "Desktop",
            "os": "Windows 11",
            "browser": "Chrome",
            "ip": "192.168.1.101",
            "last_active": (datetime.now() - timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S"),
            "is_current": True
        },
        {
            "id": 2,
            "type": "Mobile",
            "os": "Android 14",
            "browser": "Firefox",
            "ip": "10.0.2.15",
            "last_active": (datetime.now() - timedelta(days=1, hours=3)).strftime("%Y-%m-%d %H:%M:%S"),
            "is_current": False
        },
        {
            "id": 3,
            "type": "Tablet",
            "os": "iPadOS 17",
            "browser": "Safari",
            "ip": "172.16.0.5",
            "last_active": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d %H:%M:%S"),
            "is_current": False
        }
    ]

    # 模拟系统资源
    resources = {
        "cpu_usage": random.randint(15, 50),
        "memory": {
            "used_gb": round(random.uniform(3.5, 7.8), 1),
            "total_gb": 16.0
        }
    }
    resources["memory"]["usage_percent"] = int((resources["memory"]["used_gb"] / resources["memory"]["total_gb"]) * 100)

    return jsonify({
        "devices": devices,
        "resources": resources
    }) 