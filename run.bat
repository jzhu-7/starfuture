@echo off
REM 房地产销售数据监控系统启动脚本 (Windows)

echo 🚀 启动房地产销售数据监控系统...

REM 获取脚本所在目录
set SCRIPT_DIR=%~dp0

REM 激活虚拟环境
call "%SCRIPT_DIR%.venv\Scripts\activate.bat"

REM 设置Python路径
set PYTHONPATH=%SCRIPT_DIR%;%PYTHONPATH%

REM 启动Streamlit应用
echo 📊 正在启动Streamlit应用...
echo 🌐 应用将在浏览器中打开，通常访问 http://localhost:8501
echo ⚠️  如果无法自动打开浏览器，请手动访问上述地址
echo.

streamlit run "%SCRIPT_DIR%app.py" --server.headless true --server.address 0.0.0.0

pause