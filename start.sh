#!/bin/bash

echo "========================================"
echo "    Ascend RAG Assistant 一键启动"
echo "========================================"
echo ""

# 设置环境变量解决OMP冲突
export KMP_DUPLICATE_LIB_OK=TRUE

# 启动API服务器
echo "启动技能树API服务器..."
python server.py &
API_PID=$!

echo "等待API服务器启动..."
sleep 3

echo ""
echo "启动Streamlit前端..."
echo "前端启动后请在浏览器访问: http://localhost:8501"
echo ""

streamlit run app.py

# 退出时杀死API进程
kill $API_PID
