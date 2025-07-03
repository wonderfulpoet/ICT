import requests
import json
import base64
from PIL import Image
import io
import os

# API配置
API_KEY = "sk-Pb986eUQIj2VFlHy7mMd5g"
API_URL = "https://llmapi.paratera.com/v1/chat/completions"
MODEL = "DeepSeek-R1"

def test_text_completion():
    """测试基本的文本完成功能"""
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": "请简要介绍一下中国的人工智能发展现状。"}
        ],
        "temperature": 0.7,
        "max_tokens": 1000,
        "stream": False
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        
        # 打印状态码和原始响应
        print(f"状态码: {response.status_code}")
        print(f"原始响应: {response.text}\n")
        
        if response.status_code == 200:
            result = response.json()
            print("成功获取响应:")
            print(f"模型: {result.get('model')}")
            print(f"总Token: {result.get('usage', {}).get('total_tokens')}")
            print(f"回答: {result.get('choices', [{}])[0].get('message', {}).get('content')}")
        else:
            print(f"请求失败，错误信息: {response.text}")
    
    except Exception as e:
        print(f"发生错误: {str(e)}")

def test_thinking_process():
    """测试带思考过程的回答"""
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": "请分析以下问题。在回答前，请用<think></think>标签包裹你的思考过程。问题：中国历史上最伟大的发明是什么？"}
        ],
        "temperature": 0.7,
        "max_tokens": 1500,
        "stream": False
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            
            # 提取思考过程
            import re
            think_pattern = re.compile(r'<think>(.*?)</think>', re.DOTALL)
            think_matches = think_pattern.findall(content)
            
            thinking = "\n".join(think_matches) if think_matches else "未找到思考过程"
            
            # 移除思考标记，获取最终答案
            answer = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
            
            print("思考过程:")
            print(thinking)
            print("\n最终答案:")
            print(answer)
        else:
            print(f"请求失败，错误信息: {response.text}")
    
    except Exception as e:
        print(f"发生错误: {str(e)}")

def encode_image(image_path):
    """将图片编码为base64字符串"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def test_image_analysis(image_path):
    """测试图像分析功能"""
    
    # 检查文件是否存在
    if not os.path.exists(image_path):
        print(f"错误: 图片文件不存在: {image_path}")
        return
    
    # 编码图像
    try:
        base64_image = encode_image(image_path)
    except Exception as e:
        print(f"图片编码错误: {str(e)}")
        return
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "请详细描述这张图片中的内容。"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "temperature": 0.7,
        "max_tokens": 1000,
        "stream": False
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print("图像分析结果:")
            print(result.get('choices', [{}])[0].get('message', {}).get('content'))
        else:
            print(f"请求失败，错误信息: {response.text}")
    
    except Exception as e:
        print(f"发生错误: {str(e)}")

def main():
    print("=== DeepSeek-R1 API 测试 ===\n")
    
    print("测试1: 基本文本完成")
    print("-" * 50)
    test_text_completion()
    
    print("\n\n测试2: 带思考过程的回答")
    print("-" * 50)
    test_thinking_process()
    
    # 图像测试需要图片路径
    image_path = input("\n\n请输入要分析的图片路径 (留空跳过图像测试): ")
    if image_path:
        print("\n测试3: 图像分析")
        print("-" * 50)
        test_image_analysis(image_path)

if __name__ == "__main__":
    main()