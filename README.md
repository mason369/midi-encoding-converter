# MIDI Encoding Converter

A Python tool to convert text event encodings in MIDI files. Supports conversion between various character encodings such as Shift_JIS, GBK, UTF-8, and more.

## Features

- Convert text encodings in MIDI files (lyrics, track names, markers, etc.)
- Support for all standard text meta events (Text, Copyright, Track Name, Instrument Name, Lyric, Marker, Cue Point)
- Automatic encoding detection (requires `chardet`)
- Pure Python implementation - no external dependencies required for basic usage
- Preserves all MIDI data integrity during conversion

## Installation

### From Source

```bash
git clone https://github.com/yourusername/midi-encoding-converter.git
cd midi-encoding-converter
```

### Optional Dependencies

For encoding detection feature:

```bash
pip install chardet
```

## Usage

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

The converter supports all encodings available in Python's `codecs` module, including:

| Encoding | Common Use |
|----------|------------|
| `utf-8` | Universal |
| `shift_jis` / `cp932` | Japanese |
| `gbk` / `gb2312` / `gb18030` | Chinese (Simplified) |
| `big5` | Chinese (Traditional) |
| `euc-kr` / `cp949` | Korean |
| `iso-8859-1` / `latin-1` | Western European |
| `cp1252` | Windows Western |

## Examples

### Convert Japanese MIDI (Shift_JIS to UTF-8)

```bash
python midi_encoding_converter.py japanese_song.mid -f shift_jis -t utf-8
```

### Convert Chinese MIDI (GBK to UTF-8)

```bash
python midi_encoding_converter.py chinese_song.mid -f gbk -t utf-8
```

### Batch Conversion (PowerShell)

```powershell
Get-ChildItem *.mid | ForEach-Object {
    python midi_encoding_converter.py $_.Name -o "converted_$($_.Name)"
}
```

### Batch Conversion (Bash)

```bash
for f in *.mid; do
    python midi_encoding_converter.py "$f" -o "converted_$f"
done
```

## Version History

### v1.0.0 (2025-01-22)

- Initial release
- Support for all text meta events
- Encoding detection feature
- Command line interface

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Credits

Inspired by [midiiconv](https://github.com/tonychee7000/midiiconv) (Go implementation).

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
3. Decode text from source encoding
4. Re-encode to target encoding
5. Recalculate track lengths
6. Write converted MIDI file
