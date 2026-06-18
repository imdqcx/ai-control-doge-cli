@echo off
echo ========================================
echo AI Doge Remote - 打包脚本
echo ========================================
echo.

:: 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.10+
    pause
    exit /b 1
)

:: 检查PyInstaller是否安装
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo 正在安装PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo 错误: PyInstaller安装失败
        pause
        exit /b 1
    )
)

:: 安装项目依赖
echo 正在安装项目依赖...
pip install -r requirements.txt
if errorlevel 1 (
    echo 错误: 依赖安装失败
    pause
    exit /b 1
)

:: 清理旧的构建文件
echo 正在清理旧的构建文件...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "*.spec" del /q "*.spec"

:: 打包
echo 正在打包...
pyinstaller ^
    --onefile ^
    --windowed ^
    --name "AIDogeRemote" ^
    --icon "assets/doge.ico" ^
    --add-data "assets;assets" ^
    --hidden-import "pystray._win32" ^
    --hidden-import "PIL._tkinter_finder" ^
    src/main.py

if errorlevel 1 (
    echo 错误: 打包失败
    pause
    exit /b 1
)

:: 复制配置文件
echo 正在复制配置文件...
if not exist "dist\config" mkdir "dist\config"
copy "config\*.*" "dist\config\" >nul

:: 完成
echo.
echo ========================================
echo 打包完成！
echo.
echo 可执行文件位置: dist\AIDogeRemote.exe
echo.
echo 使用方法:
echo   1. 将 dist 目录复制到目标机器
echo   2. 双击 AIDogeRemote.exe 运行
echo   3. 程序将在系统托盘显示图标
echo   4. 默认API地址: http://localhost:8765
echo ========================================
echo.

:: 打开输出目录
explorer dist

pause