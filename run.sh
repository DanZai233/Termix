#!/bin/bash
# Termix 启动脚本

echo "🍸 启动 Termix 终端调酒游戏..."

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "检查依赖..."
pip install -r requirements.txt > /dev/null 2>&1

# 运行游戏
echo "启动游戏..."
python main.py
