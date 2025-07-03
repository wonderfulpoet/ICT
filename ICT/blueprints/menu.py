import os
import json
import requests
import csv
from flask import Blueprint, render_template, request, jsonify, url_for, redirect, send_from_directory, session, flash, g
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
from config import *
bp = Blueprint('menu', __name__, url_prefix='/')


@bp.route('/login', methods=['GET', 'POST'])
def login():    
    return render_template('login.html')

@bp.route('/login_action', methods=['GET','POST'])
def login_action():
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
            return redirect('/detection')
        flash('用户名或密码错误!', 'error')
        return redirect('/login')
        

@bp.route('/register', methods=['GET', 'POST'])
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

@bp.route('/register_action', methods=['POST'])
def register_action():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        users = get_users()

        if not username or not password:
            flash('用户名和密码不能为空!', 'error')
        elif password != confirm_password:
            flash('两次密码输入不一致!', 'error')
        elif username in users:
            flash('用户名已存在!', 'error')
        elif add_user(username, password):
            flash('注册成功，请登录!', 'success')
            return redirect('/login')
        else:
            flash('注册失败，请稍后再试!', 'error')

        return redirect('/register')

@bp.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    flash('您已成功退出登录!', 'success')
    return redirect('/login')


def get_users():
    """从CSV文件中获取所有用户信息"""
    users = {}
    
    # 确保密码文件所在目录存在
    os.makedirs(os.path.dirname(PASSWORD_FILE), exist_ok=True)
    
    # 如果文件不存在，创建一个默认文件
    if not os.path.exists(PASSWORD_FILE):
        with open(PASSWORD_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['username', 'password'])
            writer.writerow(['admin', 'admin123'])
    
    # 读取用户信息
    try:
        with open(PASSWORD_FILE, 'r', newline='') as f:
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
        with open(PASSWORD_FILE, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([username, password])
        
        return True
    except Exception as e:
        print(f"添加用户出错: {str(e)}")
        return False

