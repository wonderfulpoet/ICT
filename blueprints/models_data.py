"""
静态模型数据，用于模型中心展示。
在实际应用中，这些数据可能来自数据库或配置文件。
"""

MODELS_DATA = [
    {
        "id": "deepseek-v3",
        "name": "DeepSeek-V3",
        "logo": "fas fa-brain", # Font Awesome icon class
        "version": "3.0.1",
        "formats": ["Text", "Code"],
        "updated_time": "2024-05-20",
        "status": "online",
        "performance": {
            "accuracy": 95,
            "speed": 88
        },
        "details": {
            "developer": "DeepSeek AI",
            "data_size": "2T Tokens",
            "languages": ["中文", "英文"],
            "description": "DeepSeek V3 是一个功能强大的代码生成和理解模型，经过海量代码数据训练，能够生成高质量、多语言的代码。",
            "api_example": """import requests

headers = {"Authorization": "Bearer YOUR_API_KEY"}
data = {
    "model": "deepseek-v3",
    "prompt": "Write a python function to sort a list."
}
response = requests.post("https://api.deepseek.com/v1/completions", headers=headers, json=data)
print(response.json())""",
            "usage_stats": [120, 150, 180, 160, 200, 210, 250] # 最近7天调用次数
        }
    },
    {
        "id": "glm-4-flash",
        "name": "GLM-4-Flash",
        "logo": "fas fa-bolt",
        "version": "4.1.0",
        "formats": ["Text", "Vision"],
        "updated_time": "2024-04-28",
        "status": "online",
        "performance": {
            "accuracy": 92,
            "speed": 98
        },
        "details": {
            "developer": "Zhipu AI",
            "data_size": "10T Tokens",
            "languages": ["中文", "英文"],
            "description": "GLM-4-Flash 是智谱AI最新推出的轻量级、高速的视觉语言模型，适用于需要快速响应的实时多媒体交互场景。",
            "api_example": """import requests

# ... (API调用代码) ...
""",
            "usage_stats": [300, 320, 280, 350, 400, 410, 390]
        }
    },
    {
        "id": "qwen-2.5-vl",
        "name": "Qwen2.5-VL",
        "logo": "fas fa-cubes",
        "version": "2.5.2",
        "formats": ["Text", "Vision", "Audio"],
        "updated_time": "2024-03-15",
        "status": "offline",
        "performance": {
            "accuracy": 96,
            "speed": 75
        },
        "details": {
            "developer": "Alibaba Cloud",
            "data_size": "N/A",
            "languages": ["多语言"],
            "description": "通义千问2.5-VL是一个强大的多模态模型，具备卓越的图像、文本、音频理解能力，但目前正在维护中。",
             "api_example": """import requests

# ... (API调用代码) ...
""",
            "usage_stats": [80, 90, 85, 100, 110, 95, 105]
        }
    },
     {
        "id": "moonshot-v1",
        "name": "Moonshot-V1",
        "logo": "fas fa-moon",
        "version": "1.0-32k",
        "formats": ["Text"],
        "updated_time": "2024-02-10",
        "status": "online",
        "performance": {
            "accuracy": 89,
            "speed": 92
        },
        "details": {
            "developer": "Moonshot AI",
            "data_size": "N/A",
            "languages": ["中文", "英文"],
            "description": "Moonshot V1是月之暗面科技开发的大语言模型，以其超长的上下文窗口（32K）而闻名，特别适合处理长文本任务。",
            "api_example": """import requests

# ... (API调用代码) ...
""",
            "usage_stats": [450, 480, 500, 520, 550, 530, 580]
        }
    },
    {
        "id": "another-model",
        "name": "Example Model A",
        "logo": "fas fa-star",
        "version": "1.2.0",
        "formats": ["Text"],
        "updated_time": "2023-11-22",
        "status": "online",
        "performance": {
            "accuracy": 85,
            "speed": 80
        },
        "details": {
            "developer": "Community",
            "data_size": "500B Tokens",
            "languages": ["英文"],
            "description": "一个用于演示目的的开源模型，性能稳定可靠。",
            "api_example": """import requests

# ... (API调用代码) ...
""",
            "usage_stats": [50, 60, 55, 65, 70, 75, 80]
        }
    },
    {
        "id": "example-model-b",
        "name": "Example Model B",
        "logo": "fas fa-atom",
        "version": "0.9.5",
        "formats": ["Code"],
        "updated_time": "2024-01-05",
        "status": "offline",
        "performance": {
            "accuracy": 88,
            "speed": 70
        },
        "details": {
            "developer": "Research Lab",
            "data_size": "1T Tokens",
            "languages": ["Python", "JavaScript"],
            "description": "专注于代码生成的实验性模型，目前处于离线调试阶段。",
            "api_example": """import requests

# ... (API调用代码) ...
""",
            "usage_stats": [10, 15, 12, 18, 20, 22, 25]
        }
    }
] 