@echo off
chcp 65001 >nul
echo ==========================================
echo   MIDI 编码转换器 - 编译脚本
echo ==========================================
echo.

echo [1/3] 检查依赖...
pip show pyinstaller >nul 2>&1 || (
    echo 正在安装 PyInstaller...
    pip install pyinstaller
)

pip show chardet >nul 2>&1 || (
    echo 正在安装 chardet...
    pip install chardet
)

echo [2/3] 开始编译...
echo.
pyinstaller --clean --noconfirm midi_converter.spec

echo.
echo [3/3] 编译完成!
echo.
echo 可执行文件位置: dist\MIDI编码转换器.exe
echo.
pause
