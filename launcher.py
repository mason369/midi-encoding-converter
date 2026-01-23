#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIDI 编码转换器 - 启动器
带有错误捕获功能
"""

import sys
import os
import traceback

def main():
    try:
        print("正在启动 MIDI 编码转换器...")
        print(f"Python 版本: {sys.version}")
        print(f"当前目录: {os.getcwd()}")
        print(f"执行文件: {sys.executable}")
        print()

        # 检查 PyQt6
        print("检查 PyQt6...")
        from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
        from PyQt6.QtCore import Qt
        print("PyQt6 加载成功!")

        # 检查核心模块
        print("检查核心模块...")

        # 尝试从当前目录或打包目录导入
        try:
            from midi_encoding_converter import MidiEncodingConverter, detect_encoding
            print("midi_encoding_converter 模块加载成功!")
        except ImportError as e:
            print(f"导入失败: {e}")
            # 尝试添加路径
            if hasattr(sys, '_MEIPASS'):
                sys.path.insert(0, sys._MEIPASS)
                print(f"添加 _MEIPASS 路径: {sys._MEIPASS}")
            from midi_encoding_converter import MidiEncodingConverter, detect_encoding
            print("midi_encoding_converter 模块加载成功 (第二次尝试)!")

        print()
        print("正在启动图形界面...")

        # 导入并启动GUI
        from midi_converter_gui import MainWindow, STYLESHEET

        app = QApplication(sys.argv)
        app.setStyle('Fusion')
        app.setStyleSheet(STYLESHEET)

        window = MainWindow()
        window.show()

        print("界面已显示，进入事件循环...")
        sys.exit(app.exec())

    except Exception as e:
        error_msg = f"启动失败!\n\n错误类型: {type(e).__name__}\n错误信息: {str(e)}\n\n详细信息:\n{traceback.format_exc()}"
        print(error_msg)

        # 尝试显示错误对话框
        try:
            from PyQt6.QtWidgets import QApplication, QMessageBox
            app = QApplication(sys.argv)
            QMessageBox.critical(None, "启动错误", error_msg)
        except:
            pass

        input("\n按回车键退出...")
        sys.exit(1)

if __name__ == '__main__':
    main()
