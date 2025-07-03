@echo off
echo 正在启动DeepSeek大模型平台...

REM 检查是否安装了Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo 未找到Python，请先安装Python并确保添加到PATH环境变量中。
    pause
    exit /b
)

REM 检查是否安装了必要的依赖
echo 正在检查和安装依赖...
python -m pip install -r requirements.txt

REM 启动Flask应用
echo 正在启动服务，请在浏览器中访问 http://localhost:3000
python app.py

pause
