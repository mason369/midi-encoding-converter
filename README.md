# MIDI 编码转换器

[English](README_EN.md)

一个用于转换 MIDI 文件中文本编码的 Python 工具。支持 Shift_JIS、GBK、UTF-8 等多种编码格式之间的转换。

> 在线体验：[https://telknet.cc/](https://telknet.cc/)

![界面预览](https://img.shields.io/badge/界面-Qt6-blue) ![Python](https://img.shields.io/badge/Python-3.8+-green) ![License](https://img.shields.io/badge/License-MIT-yellow)

## 功能特点

- 🎵 转换 MIDI 文件中的文本编码（歌词、音轨名、标记等）
- 🔍 **自动检测**源文件编码（需要 `chardet`）
- 🌐 支持**中英文界面切换**
- 🎨 现代美观的深色主题 GUI
- 📁 支持拖放文件
- 💻 纯 Python 实现，无需外部依赖即可基本使用
- 📦 提供打包好的 Windows 可执行文件

## 下载使用

### 直接下载（推荐）

从 [Releases](../../releases) 页面下载最新版本的 `MIDI_Encoder.exe`，双击即可运行，无需安装 Python。

### 从源码运行

```bash
# 克隆仓库
git clone https://github.com/mason369/midi-encoding-converter.git
cd midi-encoding-converter

# 安装依赖（可选，用于编码自动检测）
pip install chardet

# 安装 GUI 依赖
pip install PyQt6

# 运行图形界面
python midi_converter_standalone.py
```

## 使用方法

### 图形界面

1. 运行程序后，拖放 MIDI 文件到窗口或点击"浏览"按钮选择文件
2. 程序会**自动检测**源文件编码
3. 选择目标编码（默认 UTF-8）
4. 点击"开始转换"
5. 选择保存位置

### 命令行

```bash
# 基本用法：从 Shift_JIS 转换到 UTF-8
python midi_encoding_converter.py input.mid

# 指定输出文件
python midi_encoding_converter.py input.mid -o output.mid

# 从 GBK 转换到 UTF-8
python midi_encoding_converter.py input.mid -f gbk -t utf-8

# 仅检测编码
python midi_encoding_converter.py input.mid --detect

# 详细输出
python midi_encoding_converter.py input.mid -v
```

### 命令行选项

| 选项 | 说明 |
|------|------|
| `input` | 输入 MIDI 文件（必需） |
| `-o, --output` | 输出文件路径（默认：input_converted.mid） |
| `-f, --from-encoding` | 源编码（默认：shift_jis） |
| `-t, --to-encoding` | 目标编码（默认：utf-8） |
| `-d, --detect` | 仅检测编码，不转换 |
| `-v, --verbose` | 显示详细输出 |
| `--version` | 显示版本号 |

### 作为 Python 模块使用

```python
from midi_encoding_converter import MidiEncodingConverter, detect_encoding

# 检测编码
encodings = detect_encoding('input.mid')
for encoding, confidence in encodings:
    print(f"{encoding}: {confidence:.1%}")

# 转换编码
converter = MidiEncodingConverter(from_encoding='shift_jis', to_encoding='utf-8')
result = converter.convert('input.mid', 'output.mid')

print(f"转换了 {result['converted']} 个文本事件")
```

## 支持的编码

| 编码 | 常见用途 |
|------|----------|
| `utf-8` | 通用 |
| `shift_jis` / `cp932` | 日语 |
| `gbk` / `gb2312` / `gb18030` | 简体中文 |
| `big5` | 繁体中文 |
| `euc-kr` / `cp949` | 韩语 |
| `iso-8859-1` / `latin-1` | 西欧语言 |
| `cp1252` | Windows 西欧 |

## 技术说明

### MIDI 文本元事件

转换器处理以下 MIDI 元事件类型：

| 类型 | 十六进制 | 说明 |
|------|----------|------|
| Text Event | 0x01 | 通用文本 |
| Copyright | 0x02 | 版权信息 |
| Track Name | 0x03 | 音轨名称 |
| Instrument | 0x04 | 乐器名称 |
| Lyric | 0x05 | 歌词 |
| Marker | 0x06 | 标记 |
| Cue Point | 0x07 | 提示点 |

### 工作原理

1. 解析 MIDI 文件二进制结构
2. 识别文本元事件
3. 自动检测或使用指定的源编码解码文本
4. 重新编码为目标编码
5. 重新计算音轨长度
6. 写入转换后的 MIDI 文件

## 参考资源

- [MIDI 编码测试仓库](https://github.com/oxygen-dioxide/midi-encoding-test) - MIDI 编码相关测试资源
- [MidiShow 社区讨论](https://tat.midishow.com/t/topic/5772) - 关于 MIDI 编码问题的讨论

## 版本历史

### v1.1.0 (2025-01-23)

- 新增自动检测源编码功能
- 新增中英文界面切换
- 改进 GUI 界面设计
- 添加 GitHub Actions 自动发版

### v1.0.0 (2025-01-22)

- 首次发布
- 支持所有文本元事件
- 编码检测功能
- 命令行界面

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 致谢

灵感来源于 [midiiconv](https://github.com/tonychee7000/midiiconv)（Go 语言实现）
