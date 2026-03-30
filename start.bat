@echo off
chcp 65001 >nul
echo ========================================
echo    Ascend RAG Assistant 一键启动
echo ========================================
echo.
echo 设置环境变量解决OMP冲突...
set KMP_DUPLICATE_LIB_OK=TRUE
echo.
echo 启动技能树API服务器...
start "FastAPI Server" python server.py
echo.
echo 等待API服务器启动...
timeout /t 3 /nobreak >nul
echo.
echo 启动Streamlit前端...
echo 前端启动后请在浏览器访问: http://localhost:8501
echo.
streamlit run app.py
pause
