# MIDI Encoding Converter

[中文文档](README.md)

A Python tool to convert text event encodings in MIDI files. Supports conversion between various character encodings such as Shift_JIS, GBK, UTF-8, and more.

![GUI](https://img.shields.io/badge/GUI-Qt6-blue) ![Python](https://img.shields.io/badge/Python-3.8+-green) ![License](https://img.shields.io/badge/License-MIT-yellow)

## Features

- 🎵 Convert text encodings in MIDI files (lyrics, track names, markers, etc.)
- 🔍 **Auto-detect** source file encoding (requires `chardet`)
- 🌐 **Bilingual interface** (Chinese/English)
- 🎨 Modern dark theme GUI
- 📁 Drag & drop file support
- 💻 Pure Python implementation - no external dependencies required for basic usage
- 📦 Pre-built Windows executable available

## Download

### Direct Download (Recommended)

Download the latest `MIDI_Encoder.exe` from [Releases](../../releases) page. Just double-click to run - no Python installation required.

### From Source

```bash
# Clone repository
git clone https://github.com/mason369/midi-encoding-converter.git
cd midi-encoding-converter

# Install dependencies (optional, for encoding detection)
pip install chardet

# Install GUI dependencies
pip install PyQt6

# Run GUI
python midi_converter_standalone.py
```

## Usage

### GUI

1. Run the program, drag & drop a MIDI file or click "Browse" to select
2. The program will **auto-detect** source encoding
3. Select target encoding (default: UTF-8)
4. Click "Convert"
5. Choose save location

### Command Line

```bash
# Basic usage: Convert from Shift_JIS to UTF-8
python midi_encoding_converter.py input.mid

# Specify output file
python midi_encoding_converter.py input.mid -o output.mid

# Convert from GBK to UTF-8
python midi_encoding_converter.py input.mid -f gbk -t utf-8

# Detect encoding only
python midi_encoding_converter.py input.mid --detect

# Verbose output
python midi_encoding_converter.py input.mid -v
```

### Command Line Options

| Option | Description |
|--------|-------------|
| `input` | Input MIDI file (required) |
| `-o, --output` | Output MIDI file (default: input_converted.mid) |
| `-f, --from-encoding` | Source encoding (default: shift_jis) |
| `-t, --to-encoding` | Target encoding (default: utf-8) |
| `-d, --detect` | Detect encoding only, do not convert |
| `-v, --verbose` | Show verbose output |
| `--version` | Show version number |

### As a Python Module

```python
from midi_encoding_converter import MidiEncodingConverter, detect_encoding

# Detect encoding
encodings = detect_encoding('input.mid')
for encoding, confidence in encodings:
    print(f"{encoding}: {confidence:.1%}")

# Convert encoding
converter = MidiEncodingConverter(from_encoding='shift_jis', to_encoding='utf-8')
result = converter.convert('input.mid', 'output.mid')

print(f"Converted {result['converted']} text events")
```

## Supported Encodings

| Encoding | Common Use |
|----------|------------|
| `utf-8` | Universal |
| `shift_jis` / `cp932` | Japanese |
| `gbk` / `gb2312` / `gb18030` | Chinese (Simplified) |
| `big5` | Chinese (Traditional) |
| `euc-kr` / `cp949` | Korean |
| `iso-8859-1` / `latin-1` | Western European |
| `cp1252` | Windows Western |

## Technical Details

### MIDI Text Meta Events

The converter handles the following MIDI meta event types:

| Type | Hex | Description |
|------|-----|-------------|
| Text Event | 0x01 | General text |
| Copyright | 0x02 | Copyright notice |
| Track Name | 0x03 | Track/sequence name |
| Instrument | 0x04 | Instrument name |
| Lyric | 0x05 | Song lyrics |
| Marker | 0x06 | Marker text |
| Cue Point | 0x07 | Cue point text |

### How It Works

1. Parse MIDI file binary structure
2. Identify text meta events
3. Auto-detect or use specified source encoding to decode text
4. Re-encode to target encoding
5. Recalculate track lengths
6. Write converted MIDI file

## References

- [MIDI Encoding Test Repository](https://github.com/oxygen-dioxide/midi-encoding-test) - MIDI encoding test resources
- [MidiShow Community Discussion](https://tat.midishow.com/t/topic/5772) - Discussion about MIDI encoding issues

## Version History

### v1.1.0 (2025-01-23)

- Added auto-detect source encoding
- Added bilingual interface (Chinese/English)
- Improved GUI design
- Added GitHub Actions auto-release

### v1.0.0 (2025-01-22)

- Initial release
- Support for all text meta events
- Encoding detection feature
- Command line interface

## License

MIT License

## Contributing

Issues and Pull Requests are welcome!

## Credits

Inspired by [midiiconv](https://github.com/tonychee7000/midiiconv) (Go implementation).
