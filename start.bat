@echo off
chcp 65001 >nul
echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║                                                           ║
echo ║       🎮 CobbleSeer MCP Server v1.0.0 🎮                 ║
echo ║                                                           ║
echo ║   AI驱动的 Cobblemon 资源包生成器                         ║
echo ║                                                           ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

:: 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装，请先安装Python 3.11+
    echo.
    echo 下载地址：https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python已安装
echo.

:: 检查依赖
echo 🔍 检查依赖...
python -c "import fastmcp" >nul 2>&1
if errorlevel 1 (
    echo.
    echo ⚠️  依赖未安装，正在安装...
    echo.
    pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo ❌ 依赖安装失败
        pause
        exit /b 1
    )
)

echo ✅ 依赖已就绪
echo.

:: 启动选择
echo 请选择启动模式：
echo.
echo 1. stdio模式（Cursor调用）
echo 2. HTTP模式（Web UI调用）
echo 3. 调试模式（显示详细日志）
echo.
set /p mode="请输入数字 (1/2/3): "

if "%mode%"=="1" (
    echo.
    echo 📡 启动 stdio 模式...
    echo.
    python server.py
) else if "%mode%"=="2" (
    echo.
    echo 🌐 启动 HTTP 模式...
    echo 服务地址：http://127.0.0.1:8765
    echo.
    python server.py --http
) else if "%mode%"=="3" (
    echo.
    echo 🐛 启动调试模式...
    echo.
    set DEBUG=true
    python server.py --http --reload
) else (
    echo.
    echo ❌ 无效选择
    pause
    exit /b 1
)

pause

