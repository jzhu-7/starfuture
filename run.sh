#!/bin/bash

# 房地产销售数据监控系统启动脚本

echo "启动销售数据监控系统..."

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 激活虚拟环境
source "$SCRIPT_DIR/.venv/bin/activate"

# 设置Python路径
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

# 启动Streamlit应用
echo "📊 正在启动Streamlit应用..."
echo "🌐 应用将在浏览器中打开，通常访问 http://localhost:8501"
echo "⚠️  如果无法自动打开浏览器，请手动访问上述地址"
echo ""

streamlit run "$SCRIPT_DIR/app.py" --server.headless true --server.address 0.0.0.0