@echo off
chcp 65001 >nul
echo ========================================
echo    Ascend RAG Assistant - Starting All Services
echo ========================================
echo.
echo Setting environment to avoid OMP conflict...
set KMP_DUPLICATE_LIB_OK=TRUE
echo.

echo Starting Go RSS service...
if exist "%~dp0services\rss-crawler\server.exe" (
    start "Go RSS Server" cmd /k "cd /d %~dp0services\rss-crawler && server.exe"
) else (
    start "Go RSS Server" cmd /k "cd /d %~dp0services\rss-crawler && go run cmd/server/main.go"
)
echo.

echo Starting FastAPI server...
start "FastAPI Server" cmd /k "cd /d %~dp0 && python rag_server.py"
echo.

echo Waiting for API server to start...
timeout /t 3 /nobreak >nul
echo.

echo Starting frontend dev server...
start "Frontend Dev Server" cmd /k "cd /d %~dp0frontend && npm run dev"
echo.

echo ========================================
echo    All services started
echo    - Go RSS service: http://localhost:8081
echo    - FastAPI service: http://localhost:8000
echo    - Frontend dev server: http://localhost:3000
echo ========================================
pause
