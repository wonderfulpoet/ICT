from flask import Blueprint, request, jsonify, render_template
import cv2
import numpy as np
import base64
import os
import random
import requests

bp =Blueprint('api',__name__,url_prefix="/")

#假设这是后端这边的路由
@bp.route('/api1')
def api1():
    response =requests.get('http://localhost:3000/api2') # 指定接口的!
    if response.status_code == 200:
        return "API1:"+response.text
    else:
        return "API1: Failed to call API2!"

#假设这是模型那边的路由
@bp.route('/api2')
def api2():
    return "API2:Hello from API2"