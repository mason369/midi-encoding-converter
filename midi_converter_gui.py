#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIDI 编码转换器 - Qt 图形界面

一个美观的图形用户界面，用于转换 MIDI 文件中的文本编码。

作者: AI Assistant
许可: MIT
版本: 1.0.0
"""

import sys
import os
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QFileDialog, QTextEdit,
    QProgressBar, QFrame, QGroupBox, QGridLayout, QMessageBox,
    QSizePolicy, QSpacerItem, QCheckBox, QScrollArea
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve, QSize
from PyQt6.QtGui import QFont, QIcon, QPalette, QColor, QDragEnterEvent, QDropEvent, QPixmap, QPainter, QLinearGradient

from midi_encoding_converter import MidiEncodingConverter, detect_encoding


# 现代配色方案
COLORS = {
    'primary': '#6366f1',        # 靛蓝色
    'primary_hover': '#4f46e5',
    'primary_pressed': '#4338ca',
    'secondary': '#8b5cf6',      # 紫罗兰色
    'success': '#10b981',        # 翡翠绿
    'warning': '#f59e0b',        # 琥珀色
    'error': '#ef4444',          # 红色
    'background': '#0f172a',     # 深蓝灰
    'surface': '#1e293b',        # 中蓝灰
    'surface_light': '#334155',  # 浅蓝灰
    'border': '#475569',         # 边框色
    'text': '#f8fafc',           # 文本色
    'text_secondary': '#94a3b8', # 次要文本色
    'text_muted': '#64748b',     # 暗淡文本色
}

STYLESHEET = f"""
QMainWindow {{
    background-color: {COLORS['background']};
}}

QWidget {{
    font-family: 'Microsoft YaHei UI', 'Segoe UI', sans-serif;
    color: {COLORS['text']};
}}

QLabel {{
    color: {COLORS['text']};
    font-size: 14px;
}}

QLabel#title {{
    font-size: 28px;
    font-weight: bold;
    color: {COLORS['text']};
    padding: 10px 0;
}}

QLabel#subtitle {{
    font-size: 14px;
    color: {COLORS['text_secondary']};
    padding-bottom: 20px;
}}

QLabel#sectionTitle {{
    font-size: 16px;
    font-weight: 600;
    color: {COLORS['text']};
    padding: 8px 0;
}}

QPushButton {{
    background-color: {COLORS['primary']};
    color: white;
    border: none;
    border-radius: 8px;
    padding: 12px 24px;
    font-size: 14px;
    font-weight: 600;
    min-height: 20px;
}}

QPushButton:hover {{
    background-color: {COLORS['primary_hover']};
}}

QPushButton:pressed {{
    background-color: {COLORS['primary_pressed']};
}}

QPushButton:disabled {{
    background-color: {COLORS['surface_light']};
    color: {COLORS['text_muted']};
}}

QPushButton#secondaryBtn {{
    background-color: {COLORS['surface_light']};
    color: {COLORS['text']};
    border: 1px solid {COLORS['border']};
}}

QPushButton#secondaryBtn:hover {{
    background-color: {COLORS['border']};
}}

QPushButton#successBtn {{
    background-color: {COLORS['success']};
}}

QPushButton#successBtn:hover {{
    background-color: #059669;
}}

QComboBox {{
    background-color: {COLORS['surface']};
    color: {COLORS['text']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    padding: 10px 16px;
    font-size: 14px;
    min-height: 20px;
}}

QComboBox:hover {{
    border-color: {COLORS['primary']};
}}

QComboBox:focus {{
    border-color: {COLORS['primary']};
    outline: none;
}}

QComboBox::drop-down {{
    border: none;
    padding-right: 16px;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid {COLORS['text_secondary']};
    margin-right: 10px;
}}

QComboBox QAbstractItemView {{
    background-color: {COLORS['surface']};
    color: {COLORS['text']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    selection-background-color: {COLORS['primary']};
    selection-color: white;
    padding: 4px;
}}

QTextEdit {{
    background-color: {COLORS['surface']};
    color: {COLORS['text']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    padding: 12px;
    font-family: 'Consolas', 'Microsoft YaHei UI', monospace;
    font-size: 13px;
    line-height: 1.5;
}}

QTextEdit:focus {{
    border-color: {COLORS['primary']};
}}

QProgressBar {{
    background-color: {COLORS['surface']};
    border: none;
    border-radius: 6px;
    height: 12px;
    text-align: center;
}}

QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {COLORS['primary']}, stop:1 {COLORS['secondary']});
    border-radius: 6px;
}}

QGroupBox {{
    background-color: {COLORS['surface']};
    border: 1px solid {COLORS['border']};
    border-radius: 12px;
    margin-top: 16px;
    padding: 20px;
    font-size: 14px;
    font-weight: 600;
}}

QGroupBox::title {{
    color: {COLORS['text']};
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 12px;
    background-color: {COLORS['surface']};
    border-radius: 4px;
}}

QFrame#dropZone {{
    background-color: {COLORS['surface']};
    border: 2px dashed {COLORS['border']};
    border-radius: 12px;
    min-height: 120px;
}}

QFrame#dropZone:hover {{
    border-color: {COLORS['primary']};
    background-color: rgba(99, 102, 241, 0.1);
}}

QFrame#card {{
    background-color: {COLORS['surface']};
    border: 1px solid {COLORS['border']};
    border-radius: 12px;
    padding: 16px;
}}

QCheckBox {{
    color: {COLORS['text']};
    font-size: 14px;
    spacing: 8px;
}}

QCheckBox::indicator {{
    width: 20px;
    height: 20px;
    border-radius: 4px;
    border: 2px solid {COLORS['border']};
    background-color: {COLORS['surface']};
}}

QCheckBox::indicator:hover {{
    border-color: {COLORS['primary']};
}}

QCheckBox::indicator:checked {{
    background-color: {COLORS['primary']};
    border-color: {COLORS['primary']};
}}

QScrollArea {{
    background-color: transparent;
    border: none;
}}

QScrollBar:vertical {{
    background-color: {COLORS['surface']};
    width: 10px;
    border-radius: 5px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background-color: {COLORS['border']};
    border-radius: 5px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {COLORS['text_muted']};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
"""


class ConversionWorker(QThread):
    """MIDI 转换工作线程"""

    progress = pyqtSignal(int)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    log = pyqtSignal(str)

    def __init__(self, input_file: str, output_file: str,
                 from_encoding: str, to_encoding: str):
        super().__init__()
        self.input_file = input_file
        self.output_file = output_file
        self.from_encoding = from_encoding
        self.to_encoding = to_encoding

    def run(self):
        try:
            self.log.emit(f"开始转换...")
            self.log.emit(f"输入文件: {self.input_file}")
            self.log.emit(f"编码转换: {self.from_encoding} -> {self.to_encoding}")
            self.progress.emit(20)

            converter = MidiEncodingConverter(self.from_encoding, self.to_encoding)
            converter.verbose = True

            self.progress.emit(40)
            result = converter.convert(self.input_file, self.output_file)
            self.progress.emit(80)

            self.log.emit(f"\n[完成] 转换成功!")
            self.log.emit(f"  输出文件: {result['output_file']}")
            self.log.emit(f"  音轨数量: {result['tracks']}")
            self.log.emit(f"  文本事件: {result['converted']} 个")
            self.log.emit(f"  文件大小: {result['input_size']} -> {result['output_size']} 字节")

            if result['errors'] > 0:
                self.log.emit(f"  [警告] 错误数: {result['errors']}")

            self.progress.emit(100)
            self.finished.emit(result)

        except Exception as e:
            self.error.emit(str(e))


class DetectionWorker(QThread):
    """编码检测工作线程"""

    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    log = pyqtSignal(str)

    def __init__(self, input_file: str):
        super().__init__()
        self.input_file = input_file

    def run(self):
        try:
            self.log.emit(f"正在检测编码: {self.input_file}")
            results = detect_encoding(self.input_file)

            if results:
                self.log.emit("\n检测到的编码:")
                for encoding, confidence in results:
                    self.log.emit(f"  - {encoding}: {confidence:.1%}")
            else:
                self.log.emit("未检测到编码 (文件可能仅包含ASCII文本)")

            self.finished.emit(results)

        except Exception as e:
            self.error.emit(str(e))


class DropZone(QFrame):
    """文件拖放区域"""

    fileDropped = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("dropZone")
        self.setAcceptDrops(True)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 图标标签
        icon_label = QLabel("🎵")
        icon_label.setStyleSheet("font-size: 48px;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)

        # 文本标签
        text_label = QLabel("拖放 MIDI 文件到此处")
        text_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 16px;")
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(text_label)

        # 提示标签
        hint_label = QLabel('或点击"浏览"按钮选择文件')
        hint_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 13px;")
        hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(hint_label)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            url = event.mimeData().urls()[0]
            if url.toLocalFile().lower().endswith(('.mid', '.midi')):
                event.acceptProposedAction()
                self.setStyleSheet(f"""
                    QFrame#dropZone {{
                        border-color: {COLORS['primary']};
                        background-color: rgba(99, 102, 241, 0.15);
                    }}
                """)

    def dragLeaveEvent(self, event):
        self.setStyleSheet("")

    def dropEvent(self, event: QDropEvent):
        self.setStyleSheet("")
        url = event.mimeData().urls()[0]
        file_path = url.toLocalFile()
        if file_path.lower().endswith(('.mid', '.midi')):
            self.fileDropped.emit(file_path)


class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self):
        super().__init__()
        self.input_file: Optional[str] = None
        self.output_file: Optional[str] = None
        self.worker: Optional[QThread] = None

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("MIDI 编码转换器")
        self.setMinimumSize(800, 700)
        self.resize(900, 750)

        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(32, 24, 32, 32)
        main_layout.setSpacing(16)

        # 标题区域
        header_layout = QVBoxLayout()
        header_layout.setSpacing(4)

        title = QLabel("MIDI 编码转换器")
        title.setObjectName("title")
        header_layout.addWidget(title)

        subtitle = QLabel("轻松转换 MIDI 文件中的文本编码")
        subtitle.setObjectName("subtitle")
        header_layout.addWidget(subtitle)

        main_layout.addLayout(header_layout)

        # 内容区域
        content_layout = QHBoxLayout()
        content_layout.setSpacing(24)

        # 左侧面板 - 设置
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(16)

        # 文件选择区域
        file_section = QWidget()
        file_section.setObjectName("card")
        file_section_layout = QVBoxLayout(file_section)
        file_section_layout.setContentsMargins(20, 20, 20, 20)
        file_section_layout.setSpacing(12)

        file_title = QLabel("📁  选择 MIDI 文件")
        file_title.setObjectName("sectionTitle")
        file_section_layout.addWidget(file_title)

        # 拖放区域
        self.drop_zone = DropZone()
        self.drop_zone.fileDropped.connect(self.on_file_selected)
        file_section_layout.addWidget(self.drop_zone)

        # 浏览按钮
        browse_layout = QHBoxLayout()
        browse_layout.addStretch()
        self.browse_btn = QPushButton("浏览文件")
        self.browse_btn.setObjectName("secondaryBtn")
        self.browse_btn.clicked.connect(self.browse_file)
        browse_layout.addWidget(self.browse_btn)
        browse_layout.addStretch()
        file_section_layout.addLayout(browse_layout)

        # 已选择文件显示
        self.file_label = QLabel("未选择文件")
        self.file_label.setStyleSheet(f"color: {COLORS['text_muted']}; padding: 8px 0;")
        self.file_label.setWordWrap(True)
        file_section_layout.addWidget(self.file_label)

        left_layout.addWidget(file_section)

        # 编码设置区域
        encoding_section = QWidget()
        encoding_section.setObjectName("card")
        encoding_section_layout = QVBoxLayout(encoding_section)
        encoding_section_layout.setContentsMargins(20, 20, 20, 20)
        encoding_section_layout.setSpacing(16)

        encoding_title = QLabel("⚙️  编码设置")
        encoding_title.setObjectName("sectionTitle")
        encoding_section_layout.addWidget(encoding_title)

        # 编码选择网格
        encoding_grid = QGridLayout()
        encoding_grid.setSpacing(12)

        # 源编码
        from_label = QLabel("源编码:")
        from_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        encoding_grid.addWidget(from_label, 0, 0)

        self.from_encoding = QComboBox()
        self.from_encoding.addItems([
            "shift_jis", "cp932", "gbk", "gb2312", "gb18030",
            "big5", "euc-kr", "cp949", "utf-8", "utf-16",
            "iso-8859-1", "cp1252", "ascii"
        ])
        encoding_grid.addWidget(self.from_encoding, 0, 1)

        # 箭头
        arrow_label = QLabel("→")
        arrow_label.setStyleSheet(f"font-size: 20px; color: {COLORS['primary']};")
        arrow_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        encoding_grid.addWidget(arrow_label, 0, 2)

        # 目标编码
        to_label = QLabel("目标编码:")
        to_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        encoding_grid.addWidget(to_label, 0, 3)

        self.to_encoding = QComboBox()
        self.to_encoding.addItems([
            "utf-8", "utf-16", "shift_jis", "cp932", "gbk",
            "gb2312", "gb18030", "big5", "euc-kr", "cp949",
            "iso-8859-1", "cp1252", "ascii"
        ])
        encoding_grid.addWidget(self.to_encoding, 0, 4)

        encoding_section_layout.addLayout(encoding_grid)

        # 检测编码按钮
        self.detect_btn = QPushButton("🔍 自动检测编码")
        self.detect_btn.setObjectName("secondaryBtn")
        self.detect_btn.clicked.connect(self.detect_encoding)
        self.detect_btn.setEnabled(False)
        encoding_section_layout.addWidget(self.detect_btn)

        left_layout.addWidget(encoding_section)

        # 操作按钮
        action_layout = QHBoxLayout()
        action_layout.setSpacing(12)

        self.convert_btn = QPushButton("🚀 开始转换")
        self.convert_btn.setObjectName("successBtn")
        self.convert_btn.clicked.connect(self.start_conversion)
        self.convert_btn.setEnabled(False)
        self.convert_btn.setMinimumHeight(50)
        action_layout.addWidget(self.convert_btn)

        left_layout.addLayout(action_layout)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(False)
        left_layout.addWidget(self.progress_bar)

        left_layout.addStretch()

        content_layout.addWidget(left_panel, stretch=1)

        # 右侧面板 - 日志输出
        right_panel = QWidget()
        right_panel.setObjectName("card")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(20, 20, 20, 20)
        right_layout.setSpacing(12)

        log_header = QHBoxLayout()
        log_title = QLabel("📋  输出日志")
        log_title.setObjectName("sectionTitle")
        log_header.addWidget(log_title)
        log_header.addStretch()

        self.clear_log_btn = QPushButton("清空")
        self.clear_log_btn.setObjectName("secondaryBtn")
        self.clear_log_btn.setFixedWidth(80)
        self.clear_log_btn.clicked.connect(self.clear_log)
        log_header.addWidget(self.clear_log_btn)

        right_layout.addLayout(log_header)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setPlaceholderText("转换日志将在此显示...")
        right_layout.addWidget(self.log_output)

        content_layout.addWidget(right_panel, stretch=1)

        main_layout.addLayout(content_layout)

        # 页脚
        footer = QLabel("MIDI 编码转换器 v1.0.0  |  MIT 许可证")
        footer.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 12px; padding-top: 8px;")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(footer)

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择 MIDI 文件",
            "",
            "MIDI 文件 (*.mid *.midi);;所有文件 (*.*)"
        )
        if file_path:
            self.on_file_selected(file_path)

    def on_file_selected(self, file_path: str):
        self.input_file = file_path
        file_name = Path(file_path).name
        self.file_label.setText(f"[已选择] {file_name}")
        self.file_label.setStyleSheet(f"color: {COLORS['success']}; padding: 8px 0;")
        self.convert_btn.setEnabled(True)
        self.detect_btn.setEnabled(True)
        self.log_message(f"已选择文件: {file_path}")

    def detect_encoding(self):
        if not self.input_file:
            return

        self.detect_btn.setEnabled(False)
        self.worker = DetectionWorker(self.input_file)
        self.worker.log.connect(self.log_message)
        self.worker.finished.connect(self.on_detection_finished)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def on_detection_finished(self, results: list):
        self.detect_btn.setEnabled(True)
        if results:
            # 设置检测到的编码
            best_encoding = results[0][0].lower().replace('-', '_')
            index = self.from_encoding.findText(best_encoding, Qt.MatchFlag.MatchFixedString)
            if index >= 0:
                self.from_encoding.setCurrentIndex(index)
                self.log_message(f"\n-> 已设置源编码为: {best_encoding}")

    def start_conversion(self):
        if not self.input_file:
            return

        # 生成输出文件路径
        input_path = Path(self.input_file)
        self.output_file = str(input_path.parent / f"{input_path.stem}_converted{input_path.suffix}")

        # 询问用户保存位置
        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存转换后的 MIDI 文件",
            self.output_file,
            "MIDI 文件 (*.mid *.midi);;所有文件 (*.*)"
        )

        if not output_path:
            return

        self.output_file = output_path

        # 禁用界面
        self.convert_btn.setEnabled(False)
        self.browse_btn.setEnabled(False)
        self.detect_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        # 开始转换
        self.worker = ConversionWorker(
            self.input_file,
            self.output_file,
            self.from_encoding.currentText(),
            self.to_encoding.currentText()
        )
        self.worker.progress.connect(self.update_progress)
        self.worker.log.connect(self.log_message)
        self.worker.finished.connect(self.on_conversion_finished)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def update_progress(self, value: int):
        self.progress_bar.setValue(value)

    def on_conversion_finished(self, result: dict):
        self.convert_btn.setEnabled(True)
        self.browse_btn.setEnabled(True)
        self.detect_btn.setEnabled(True)
        self.progress_bar.setVisible(False)

        QMessageBox.information(
            self,
            "转换完成",
            f"转换成功!\n\n"
            f"输出文件: {result['output_file']}\n"
            f"文本事件: {result['converted']} 个\n"
            f"音轨数量: {result['tracks']}"
        )

    def on_error(self, error_msg: str):
        self.convert_btn.setEnabled(True)
        self.browse_btn.setEnabled(True)
        self.detect_btn.setEnabled(True)
        self.progress_bar.setVisible(False)

        self.log_message(f"\n[错误] {error_msg}")

        QMessageBox.critical(
            self,
            "错误",
            f"转换失败:\n\n{error_msg}"
        )

    def log_message(self, message: str):
        self.log_output.append(message)
        # 滚动到底部
        scrollbar = self.log_output.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def clear_log(self):
        self.log_output.clear()


def main():
    """GUI应用主入口"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # 应用样式表
    app.setStyleSheet(STYLESHEET)

    # 创建并显示主窗口
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
