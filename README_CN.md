# MIDI 编码转换器

一个用于转换 MIDI 文件中文本事件编码的 Python 工具。支持 Shift_JIS、GBK、UTF-8 等多种字符编码之间的转换。

## 功能特性

- 转换 MIDI 文件中的文本编码（歌词、音轨名称、标记等）
- 支持所有标准文本元事件（文本、版权、音轨名称、乐器名称、歌词、标记、提示点）
- 自动编码检测（需要安装 `chardet`）
- 纯 Python 实现 - 基本使用无需外部依赖
- 转换过程中保持所有 MIDI 数据完整性

## 安装

### 从源码安装

```bash
git clone https://github.com/mason369/midi-encoding-converter.git
cd midi-encoding-converter
```

### 可选依赖

如需使用编码检测功能：

```bash
pip install chardet
```

## 使用方法

### 命令行

```bash
# 基本用法：从 Shift_JIS 转换为 UTF-8
python midi_encoding_converter.py input.mid

# 指定输出文件
python midi_encoding_converter.py input.mid -o output.mid

# 从 GBK 转换为 UTF-8
python midi_encoding_converter.py input.mid -f gbk -t utf-8

# 仅检测编码
python midi_encoding_converter.py input.mid --detect

# 详细输出
python midi_encoding_converter.py input.mid -v
```

### 命令行参数

| 参数 | 说明 |
|------|------|
| `input` | 输入 MIDI 文件（必需） |
| `-o, --output` | 输出 MIDI 文件（默认：input_converted.mid） |
| `-f, --from-encoding` | 源编码（默认：shift_jis） |
| `-t, --to-encoding` | 目标编码（默认：utf-8） |
| `-d, --detect` | 仅检测编码，不进行转换 |
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

print(f"已转换 {result['converted']} 个文本事件")
```

## 支持的编码

转换器支持 Python `codecs` 模块中所有可用的编码，包括：

| 编码 | 常见用途 |
|------|----------|
| `utf-8` | 通用 |
| `shift_jis` / `cp932` | 日语 |
| `gbk` / `gb2312` / `gb18030` | 简体中文 |
| `big5` | 繁体中文 |
| `euc-kr` / `cp949` | 韩语 |
| `iso-8859-1` / `latin-1` | 西欧语言 |
| `cp1252` | Windows 西欧 |

## 使用示例

### 转换日语 MIDI（Shift_JIS 到 UTF-8）

```bash
python midi_encoding_converter.py japanese_song.mid -f shift_jis -t utf-8
```

### 转换中文 MIDI（GBK 到 UTF-8）

```bash
python midi_encoding_converter.py chinese_song.mid -f gbk -t utf-8
```

### 批量转换（PowerShell）

```powershell
Get-ChildItem *.mid | ForEach-Object {
    python midi_encoding_converter.py $_.Name -o "converted_$($_.Name)"
}
```

### 批量转换（Bash）

```bash
for f in *.mid; do
    python midi_encoding_converter.py "$f" -o "converted_$f"
done
```

## 版本历史

### v1.0.0 (2025-01-22)

- 首次发布
- 支持所有文本元事件
- 编码检测功能
- 命令行界面

## 许可证

MIT 许可证

## 贡献

欢迎贡献！请随时提交 Pull Request。

## 致谢

灵感来源于 [midiiconv](https://github.com/tonychee7000/midiiconv)（Go 语言实现）。

## 技术细节

### MIDI 文本元事件

转换器处理以下 MIDI 元事件类型：

| 类型 | 十六进制 | 说明 |
|------|----------|------|
| 文本事件 | 0x01 | 通用文本 |
| 版权声明 | 0x02 | 版权信息 |
| 音轨名称 | 0x03 | 音轨/序列名称 |
| 乐器名称 | 0x04 | 乐器名称 |
| 歌词 | 0x05 | 歌曲歌词 |
| 标记 | 0x06 | 标记文本 |
| 提示点 | 0x07 | 提示点文本 |

### 工作原理

1. 解析 MIDI 文件二进制结构
2. 识别文本元事件
3. 从源编码解码文本
4. 重新编码为目标编码
5. 重新计算音轨长度
6. 写入转换后的 MIDI 文件
