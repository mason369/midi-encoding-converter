#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIDI 编码转换器 - 完整单文件版本
支持中英文界面切换，自动检测源编码
"""

import sys
import os
import struct
from pathlib import Path
from typing import Tuple, List, Optional

# ============== 多语言支持 ==============

TRANSLATIONS = {
    'zh': {
        'app_title': 'MIDI 编码转换器',
        'app_subtitle': '轻松转换 MIDI 文件中的文本编码',
        'select_file': '📁  选择 MIDI 文件',
        'drop_hint': '拖放 MIDI 文件到此处',
        'drop_hint2': '或点击"浏览"按钮选择文件',
        'browse': '浏览文件',
        'no_file': '未选择文件',
        'file_selected': '[已选择]',
        'encoding_settings': '⚙️  编码设置',
        'source_encoding': '源编码:',
        'target_encoding': '目标编码:',
        'auto_detect': '🔍 自动检测',
        'start_convert': '🚀 开始转换',
        'output_log': '📋  输出日志',
        'clear': '清空',
        'log_placeholder': '转换日志将在此显示...',
        'footer': 'MIDI 编码转换器 v1.1.0  |  MIT 许可证',
        'select_midi_file': '选择 MIDI 文件',
        'save_midi_file': '保存转换后的 MIDI 文件',
        'midi_files': 'MIDI 文件',
        'all_files': '所有文件',
        'convert_complete': '转换完成',
        'convert_success': '转换成功!',
        'output_file': '输出文件',
        'text_events': '文本事件',
        'track_count': '音轨数量',
        'error': '错误',
        'convert_failed': '转换失败',
        'starting': '开始转换...',
        'input_file': '输入文件',
        'encoding_convert': '编码转换',
        'complete': '[完成] 转换成功!',
        'file_size': '文件大小',
        'bytes': '字节',
        'detecting': '正在检测编码...',
        'detected_encodings': '检测到的编码:',
        'no_encoding_detected': '未检测到编码 (文件可能仅包含ASCII文本)',
        'set_source_encoding': '-> 已设置源编码为:',
        'language': '🌐 语言',
        'auto': '自动检测',
        'selected_file': '已选择文件',
    },
    'en': {
        'app_title': 'MIDI Encoding Converter',
        'app_subtitle': 'Easily convert text encodings in MIDI files',
        'select_file': '📁  Select MIDI File',
        'drop_hint': 'Drag & Drop MIDI file here',
        'drop_hint2': 'or click "Browse" to select',
        'browse': 'Browse',
        'no_file': 'No file selected',
        'file_selected': '[Selected]',
        'encoding_settings': '⚙️  Encoding Settings',
        'source_encoding': 'Source:',
        'target_encoding': 'Target:',
        'auto_detect': '🔍 Auto Detect',
        'start_convert': '🚀 Convert',
        'output_log': '📋  Output Log',
        'clear': 'Clear',
        'log_placeholder': 'Conversion logs will appear here...',
        'footer': 'MIDI Encoding Converter v1.1.0  |  MIT License',
        'select_midi_file': 'Select MIDI File',
        'save_midi_file': 'Save Converted MIDI File',
        'midi_files': 'MIDI Files',
        'all_files': 'All Files',
        'convert_complete': 'Conversion Complete',
        'convert_success': 'Conversion successful!',
        'output_file': 'Output',
        'text_events': 'Text events',
        'track_count': 'Tracks',
        'error': 'Error',
        'convert_failed': 'Conversion failed',
        'starting': 'Starting conversion...',
        'input_file': 'Input',
        'encoding_convert': 'Encoding',
        'complete': '[Done] Conversion successful!',
        'file_size': 'Size',
        'bytes': 'bytes',
        'detecting': 'Detecting encoding...',
        'detected_encodings': 'Detected encodings:',
        'no_encoding_detected': 'No encoding detected (file may contain only ASCII)',
        'set_source_encoding': '-> Source encoding set to:',
        'language': '🌐 Language',
        'auto': 'Auto Detect',
        'selected_file': 'Selected file',
    }
}

current_language = 'zh'

def tr(key):
    """获取翻译文本"""
    return TRANSLATIONS.get(current_language, TRANSLATIONS['zh']).get(key, key)


# ============== 核心转换模块 ==============

__version__ = "1.1.0"


class MidiEncodingConverter:
    """转换 MIDI 文件中的文本编码"""

    TEXT_META_TYPES = {
        0x01: "Text Event",
        0x02: "Copyright Notice",
        0x03: "Track Name",
        0x04: "Instrument Name",
        0x05: "Lyric",
        0x06: "Marker",
        0x07: "Cue Point",
    }

    def __init__(self, from_encoding: str = "shift_jis", to_encoding: str = "utf-8"):
        self.from_encoding = from_encoding
        self.to_encoding = to_encoding
        self.converted_count = 0
        self.error_count = 0
        self.verbose = False

    @staticmethod
    def read_variable_length(data: bytes, pos: int) -> Tuple[int, int]:
        value = 0
        while True:
            byte = data[pos]
            value = (value << 7) | (byte & 0x7F)
            pos += 1
            if not (byte & 0x80):
                break
        return value, pos

    @staticmethod
    def write_variable_length(value: int) -> bytes:
        result = [value & 0x7F]
        value >>= 7
        while value:
            result.append((value & 0x7F) | 0x80)
            value >>= 7
        return bytes(reversed(result))

    def convert_text(self, data: bytes) -> bytes:
        try:
            text = data.decode(self.from_encoding, errors='replace')
            return text.encode(self.to_encoding)
        except Exception as e:
            self.error_count += 1
            if self.verbose:
                print(f"Warning: Conversion error - {e}", file=sys.stderr)
            return data

    def convert(self, input_file: str, output_file: Optional[str] = None) -> dict:
        input_path = Path(input_file)

        if output_file is None:
            output_file = input_path.stem + "_converted" + input_path.suffix

        with open(input_file, 'rb') as f:
            data = bytearray(f.read())

        if data[:4] != b'MThd':
            raise ValueError("Not a valid MIDI file (missing MThd header)")

        self.converted_count = 0
        self.error_count = 0

        pos = 0
        output = bytearray()

        header_length = struct.unpack('>I', data[4:8])[0]
        output.extend(data[:8 + header_length])
        pos = 8 + header_length

        track_count = 0
        while pos < len(data):
            if data[pos:pos+4] != b'MTrk':
                break

            track_count += 1
            track_start = len(output)
            output.extend(data[pos:pos+4])
            pos += 4

            track_length = struct.unpack('>I', data[pos:pos+4])[0]
            pos += 4
            output.extend(b'\x00\x00\x00\x00')

            track_data_start = len(output)
            track_end = pos + track_length

            running_status = 0

            while pos < track_end:
                delta, new_pos = self.read_variable_length(data, pos)
                output.extend(self.write_variable_length(delta))
                pos = new_pos

                status = data[pos]

                if status == 0xFF:
                    output.append(data[pos])
                    pos += 1
                    meta_type = data[pos]
                    output.append(data[pos])
                    pos += 1
                    length, new_pos = self.read_variable_length(data, pos)
                    pos = new_pos

                    meta_data = data[pos:pos + length]
                    pos += length

                    if meta_type in self.TEXT_META_TYPES:
                        new_data = self.convert_text(bytes(meta_data))
                        self.converted_count += 1
                    else:
                        new_data = meta_data

                    output.extend(self.write_variable_length(len(new_data)))
                    output.extend(new_data)

                elif status == 0xF0 or status == 0xF7:
                    output.append(data[pos])
                    pos += 1
                    length, new_pos = self.read_variable_length(data, pos)
                    output.extend(self.write_variable_length(length))
                    pos = new_pos
                    output.extend(data[pos:pos + length])
                    pos += length
                    running_status = 0

                elif status & 0x80:
                    running_status = status
                    output.append(data[pos])
                    pos += 1

                    if status & 0xF0 in (0x80, 0x90, 0xA0, 0xB0, 0xE0):
                        output.extend(data[pos:pos+2])
                        pos += 2
                    elif status & 0xF0 in (0xC0, 0xD0):
                        output.append(data[pos])
                        pos += 1

                else:
                    if running_status:
                        output.append(data[pos])
                        pos += 1
                        if running_status & 0xF0 in (0x80, 0x90, 0xA0, 0xB0, 0xE0):
                            output.append(data[pos])
                            pos += 1
                    else:
                        output.append(data[pos])
                        pos += 1

            track_data_length = len(output) - track_data_start
            struct.pack_into('>I', output, track_start + 4, track_data_length)

        with open(output_file, 'wb') as f:
            f.write(output)

        return {
            'input_file': str(input_file),
            'output_file': str(output_file),
            'tracks': track_count,
            'converted': self.converted_count,
            'errors': self.error_count,
            'input_size': len(data),
            'output_size': len(output),
        }


def detect_encoding(input_file: str) -> List[Tuple[str, float]]:
    """检测MIDI文件中文本的编码"""
    try:
        import chardet
    except ImportError:
        return []

    with open(input_file, 'rb') as f:
        data = f.read()

    if data[:4] != b'MThd':
        raise ValueError("Not a valid MIDI file")

    all_text_bytes = bytearray()
    pos = 8 + struct.unpack('>I', data[4:8])[0]

    while pos < len(data):
        if data[pos:pos+4] != b'MTrk':
            break
        pos += 4
        track_length = struct.unpack('>I', data[pos:pos+4])[0]
        pos += 4
        track_end = pos + track_length

        while pos < track_end:
            while pos < len(data) and data[pos] & 0x80:
                pos += 1
            if pos >= len(data):
                break
            pos += 1

            if pos >= len(data):
                break
            status = data[pos]

            if status == 0xFF:
                pos += 1
                if pos >= len(data):
                    break
                meta_type = data[pos]
                pos += 1
                length = 0
                while pos < len(data) and data[pos] & 0x80:
                    length = (length << 7) | (data[pos] & 0x7F)
                    pos += 1
                if pos >= len(data):
                    break
                length = (length << 7) | data[pos]
                pos += 1

                if meta_type in (0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07):
                    all_text_bytes.extend(data[pos:pos + length])
                pos += length
            elif status == 0xF0 or status == 0xF7:
                pos += 1
                length = 0
                while pos < len(data) and data[pos] & 0x80:
                    length = (length << 7) | (data[pos] & 0x7F)
                    pos += 1
                if pos >= len(data):
                    break
                length = (length << 7) | data[pos]
                pos += 1
                pos += length
            elif status & 0x80:
                pos += 1
                if status & 0xF0 in (0x80, 0x90, 0xA0, 0xB0, 0xE0):
                    pos += 2
                elif status & 0xF0 in (0xC0, 0xD0):
                    pos += 1
            else:
                pos += 1

    if all_text_bytes:
        results = chardet.detect_all(bytes(all_text_bytes))
        return [(r['encoding'], r['confidence']) for r in results if r['encoding']]

    return []


# ============== GUI 模块 ==============

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QFileDialog, QTextEdit,
    QProgressBar, QFrame, QGridLayout, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent


COLORS = {
    'primary': '#6366f1',
    'primary_hover': '#4f46e5',
    'primary_pressed': '#4338ca',
    'secondary': '#8b5cf6',
    'success': '#10b981',
    'warning': '#f59e0b',
    'error': '#ef4444',
    'background': '#0f172a',
    'surface': '#1e293b',
    'surface_light': '#334155',
    'border': '#475569',
    'text': '#f8fafc',
    'text_secondary': '#94a3b8',
    'text_muted': '#64748b',
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

QPushButton#langBtn {{
    background-color: transparent;
    color: {COLORS['text_secondary']};
    border: 1px solid {COLORS['border']};
    padding: 6px 12px;
    font-size: 12px;
}}

QPushButton#langBtn:hover {{
    background-color: {COLORS['surface_light']};
    color: {COLORS['text']};
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

QScrollBar:vertical {{
    background-color: {COLORS['surface']};
    width: 10px;
    border-radius: 5px;
}}

QScrollBar::handle:vertical {{
    background-color: {COLORS['border']};
    border-radius: 5px;
    min-height: 30px;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
"""


class ConversionWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    log = pyqtSignal(str)

    def __init__(self, input_file, output_file, from_encoding, to_encoding):
        super().__init__()
        self.input_file = input_file
        self.output_file = output_file
        self.from_encoding = from_encoding
        self.to_encoding = to_encoding

    def run(self):
        try:
            self.log.emit(f"{tr('starting')}")
            self.log.emit(f"{tr('input_file')}: {self.input_file}")
            self.log.emit(f"{tr('encoding_convert')}: {self.from_encoding} -> {self.to_encoding}")
            self.progress.emit(20)

            converter = MidiEncodingConverter(self.from_encoding, self.to_encoding)
            self.progress.emit(40)
            result = converter.convert(self.input_file, self.output_file)
            self.progress.emit(80)

            self.log.emit(f"\n{tr('complete')}")
            self.log.emit(f"  {tr('output_file')}: {result['output_file']}")
            self.log.emit(f"  {tr('track_count')}: {result['tracks']}")
            self.log.emit(f"  {tr('text_events')}: {result['converted']}")
            self.log.emit(f"  {tr('file_size')}: {result['input_size']} -> {result['output_size']} {tr('bytes')}")

            self.progress.emit(100)
            self.finished.emit(result)

        except Exception as e:
            self.error.emit(str(e))


class DetectionWorker(QThread):
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    log = pyqtSignal(str)

    def __init__(self, input_file):
        super().__init__()
        self.input_file = input_file

    def run(self):
        try:
            self.log.emit(f"{tr('detecting')}")
            results = detect_encoding(self.input_file)

            if results:
                self.log.emit(f"\n{tr('detected_encodings')}")
                for encoding, confidence in results:
                    self.log.emit(f"  - {encoding}: {confidence:.1%}")
            else:
                self.log.emit(tr('no_encoding_detected'))

            self.finished.emit(results)

        except Exception as e:
            self.error.emit(str(e))


class DropZone(QFrame):
    fileDropped = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("dropZone")
        self.setAcceptDrops(True)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.icon_label = QLabel("🎵")
        self.icon_label.setStyleSheet("font-size: 48px;")
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.icon_label)

        self.text_label = QLabel(tr('drop_hint'))
        self.text_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 16px;")
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.text_label)

        self.hint_label = QLabel(tr('drop_hint2'))
        self.hint_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 13px;")
        self.hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.hint_label)

    def update_language(self):
        self.text_label.setText(tr('drop_hint'))
        self.hint_label.setText(tr('drop_hint2'))

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
    def __init__(self):
        super().__init__()
        self.input_file = None
        self.output_file = None
        self.worker = None
        self.detected_encoding = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(tr('app_title'))
        self.setMinimumSize(800, 700)
        self.resize(900, 750)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(32, 24, 32, 32)
        main_layout.setSpacing(16)

        # 标题栏（带语言切换）
        header_layout = QHBoxLayout()

        title_layout = QVBoxLayout()
        title_layout.setSpacing(4)

        self.title_label = QLabel(tr('app_title'))
        self.title_label.setObjectName("title")
        title_layout.addWidget(self.title_label)

        self.subtitle_label = QLabel(tr('app_subtitle'))
        self.subtitle_label.setObjectName("subtitle")
        title_layout.addWidget(self.subtitle_label)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()

        # 语言切换按钮
        self.lang_btn = QPushButton("🌐 中文 / English")
        self.lang_btn.setObjectName("langBtn")
        self.lang_btn.clicked.connect(self.toggle_language)
        header_layout.addWidget(self.lang_btn)

        main_layout.addLayout(header_layout)

        # 内容
        content_layout = QHBoxLayout()
        content_layout.setSpacing(24)

        # 左侧面板
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(16)

        # 文件选择
        file_section = QWidget()
        file_section.setObjectName("card")
        file_section_layout = QVBoxLayout(file_section)
        file_section_layout.setContentsMargins(20, 20, 20, 20)
        file_section_layout.setSpacing(12)

        self.file_title = QLabel(tr('select_file'))
        self.file_title.setObjectName("sectionTitle")
        file_section_layout.addWidget(self.file_title)

        self.drop_zone = DropZone()
        self.drop_zone.fileDropped.connect(self.on_file_selected)
        file_section_layout.addWidget(self.drop_zone)

        browse_layout = QHBoxLayout()
        browse_layout.addStretch()
        self.browse_btn = QPushButton(tr('browse'))
        self.browse_btn.setObjectName("secondaryBtn")
        self.browse_btn.clicked.connect(self.browse_file)
        browse_layout.addWidget(self.browse_btn)
        browse_layout.addStretch()
        file_section_layout.addLayout(browse_layout)

        self.file_label = QLabel(tr('no_file'))
        self.file_label.setStyleSheet(f"color: {COLORS['text_muted']}; padding: 8px 0;")
        self.file_label.setWordWrap(True)
        file_section_layout.addWidget(self.file_label)

        left_layout.addWidget(file_section)

        # 编码设置
        encoding_section = QWidget()
        encoding_section.setObjectName("card")
        encoding_section_layout = QVBoxLayout(encoding_section)
        encoding_section_layout.setContentsMargins(20, 20, 20, 20)
        encoding_section_layout.setSpacing(16)

        self.encoding_title = QLabel(tr('encoding_settings'))
        self.encoding_title.setObjectName("sectionTitle")
        encoding_section_layout.addWidget(self.encoding_title)

        encoding_grid = QGridLayout()
        encoding_grid.setSpacing(12)

        self.from_label = QLabel(tr('source_encoding'))
        self.from_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        encoding_grid.addWidget(self.from_label, 0, 0)

        self.from_encoding = QComboBox()
        self.from_encoding.addItems([
            tr('auto'),
            "shift_jis", "cp932", "gbk", "gb2312", "gb18030",
            "big5", "euc-kr", "cp949", "utf-8", "utf-16",
            "iso-8859-1", "cp1252", "ascii"
        ])
        encoding_grid.addWidget(self.from_encoding, 0, 1)

        arrow_label = QLabel("→")
        arrow_label.setStyleSheet(f"font-size: 20px; color: {COLORS['primary']};")
        arrow_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        encoding_grid.addWidget(arrow_label, 0, 2)

        self.to_label = QLabel(tr('target_encoding'))
        self.to_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        encoding_grid.addWidget(self.to_label, 0, 3)

        self.to_encoding = QComboBox()
        self.to_encoding.addItems([
            "utf-8", "utf-16", "shift_jis", "cp932", "gbk",
            "gb2312", "gb18030", "big5", "euc-kr", "cp949",
            "iso-8859-1", "cp1252", "ascii"
        ])
        encoding_grid.addWidget(self.to_encoding, 0, 4)

        encoding_section_layout.addLayout(encoding_grid)

        left_layout.addWidget(encoding_section)

        # 转换按钮
        action_layout = QHBoxLayout()
        action_layout.setSpacing(12)

        self.convert_btn = QPushButton(tr('start_convert'))
        self.convert_btn.setObjectName("successBtn")
        self.convert_btn.clicked.connect(self.start_conversion)
        self.convert_btn.setEnabled(False)
        self.convert_btn.setMinimumHeight(50)
        action_layout.addWidget(self.convert_btn)

        left_layout.addLayout(action_layout)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(False)
        left_layout.addWidget(self.progress_bar)

        left_layout.addStretch()

        content_layout.addWidget(left_panel, stretch=1)

        # 右侧面板 - 日志
        right_panel = QWidget()
        right_panel.setObjectName("card")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(20, 20, 20, 20)
        right_layout.setSpacing(12)

        log_header = QHBoxLayout()
        self.log_title = QLabel(tr('output_log'))
        self.log_title.setObjectName("sectionTitle")
        log_header.addWidget(self.log_title)
        log_header.addStretch()

        self.clear_log_btn = QPushButton(tr('clear'))
        self.clear_log_btn.setObjectName("secondaryBtn")
        self.clear_log_btn.setFixedWidth(80)
        self.clear_log_btn.clicked.connect(self.clear_log)
        log_header.addWidget(self.clear_log_btn)

        right_layout.addLayout(log_header)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setPlaceholderText(tr('log_placeholder'))
        right_layout.addWidget(self.log_output)

        content_layout.addWidget(right_panel, stretch=1)

        main_layout.addLayout(content_layout)

        # 页脚
        self.footer_label = QLabel(tr('footer'))
        self.footer_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 12px; padding-top: 8px;")
        self.footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.footer_label)

    def toggle_language(self):
        global current_language
        current_language = 'en' if current_language == 'zh' else 'zh'
        self.update_ui_language()

    def update_ui_language(self):
        self.setWindowTitle(tr('app_title'))
        self.title_label.setText(tr('app_title'))
        self.subtitle_label.setText(tr('app_subtitle'))
        self.file_title.setText(tr('select_file'))
        self.browse_btn.setText(tr('browse'))
        if not self.input_file:
            self.file_label.setText(tr('no_file'))
        self.encoding_title.setText(tr('encoding_settings'))
        self.from_label.setText(tr('source_encoding'))
        self.to_label.setText(tr('target_encoding'))
        self.convert_btn.setText(tr('start_convert'))
        self.log_title.setText(tr('output_log'))
        self.clear_log_btn.setText(tr('clear'))
        self.log_output.setPlaceholderText(tr('log_placeholder'))
        self.footer_label.setText(tr('footer'))
        self.drop_zone.update_language()

        # 更新源编码下拉框第一项
        self.from_encoding.setItemText(0, tr('auto'))

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            tr('select_midi_file'),
            "",
            f"{tr('midi_files')} (*.mid *.midi);;{tr('all_files')} (*.*)"
        )
        if file_path:
            self.on_file_selected(file_path)

    def on_file_selected(self, file_path):
        self.input_file = file_path
        file_name = Path(file_path).name
        self.file_label.setText(f"{tr('file_selected')} {file_name}")
        self.file_label.setStyleSheet(f"color: {COLORS['success']}; padding: 8px 0;")
        self.convert_btn.setEnabled(True)
        self.log_message(f"{tr('selected_file')}: {file_path}")

        # 自动检测编码
        self.auto_detect_encoding()

    def auto_detect_encoding(self):
        if not self.input_file:
            return

        self.worker = DetectionWorker(self.input_file)
        self.worker.log.connect(self.log_message)
        self.worker.finished.connect(self.on_detection_finished)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def on_detection_finished(self, results):
        if results:
            best_encoding = results[0][0].lower().replace('-', '_')
            self.detected_encoding = best_encoding
            self.log_message(f"\n{tr('set_source_encoding')} {best_encoding}")

    def start_conversion(self):
        if not self.input_file:
            return

        input_path = Path(self.input_file)
        self.output_file = str(input_path.parent / f"{input_path.stem}_converted{input_path.suffix}")

        output_path, _ = QFileDialog.getSaveFileName(
            self,
            tr('save_midi_file'),
            self.output_file,
            f"{tr('midi_files')} (*.mid *.midi);;{tr('all_files')} (*.*)"
        )

        if not output_path:
            return

        self.output_file = output_path

        # 确定源编码
        from_enc = self.from_encoding.currentText()
        if from_enc == tr('auto') or from_enc == '自动检测' or from_enc == 'Auto Detect':
            if self.detected_encoding:
                from_enc = self.detected_encoding
            else:
                from_enc = 'utf-8'

        self.convert_btn.setEnabled(False)
        self.browse_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        self.worker = ConversionWorker(
            self.input_file,
            self.output_file,
            from_enc,
            self.to_encoding.currentText()
        )
        self.worker.progress.connect(self.update_progress)
        self.worker.log.connect(self.log_message)
        self.worker.finished.connect(self.on_conversion_finished)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def on_conversion_finished(self, result):
        self.convert_btn.setEnabled(True)
        self.browse_btn.setEnabled(True)
        self.progress_bar.setVisible(False)

        QMessageBox.information(
            self,
            tr('convert_complete'),
            f"{tr('convert_success')}\n\n"
            f"{tr('output_file')}: {result['output_file']}\n"
            f"{tr('text_events')}: {result['converted']}\n"
            f"{tr('track_count')}: {result['tracks']}"
        )

    def on_error(self, error_msg):
        self.convert_btn.setEnabled(True)
        self.browse_btn.setEnabled(True)
        self.progress_bar.setVisible(False)

        self.log_message(f"\n[{tr('error')}] {error_msg}")

        QMessageBox.critical(
            self,
            tr('error'),
            f"{tr('convert_failed')}:\n\n{error_msg}"
        )

    def log_message(self, message):
        self.log_output.append(message)
        scrollbar = self.log_output.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def clear_log(self):
        self.log_output.clear()


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setStyleSheet(STYLESHEET)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
