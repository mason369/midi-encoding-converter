#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create test MIDI files with different encodings for testing.
"""

import struct


def write_variable_length(value: int) -> bytes:
    """Write a variable-length quantity."""
    result = [value & 0x7F]
    value >>= 7
    while value:
        result.append((value & 0x7F) | 0x80)
        value >>= 7
    return bytes(reversed(result))


def create_midi_with_text(filename: str, texts: list, encoding: str = 'utf-8'):
    """
    Create a simple MIDI file with text events.

    Args:
        filename: Output filename
        texts: List of (meta_type, text) tuples
        encoding: Text encoding to use
    """
    # MIDI header
    header = b'MThd'
    header += struct.pack('>I', 6)  # Header length
    header += struct.pack('>H', 0)  # Format 0
    header += struct.pack('>H', 1)  # 1 track
    header += struct.pack('>H', 480)  # Ticks per quarter note

    # Build track data
    track_data = bytearray()

    # Add text events
    for meta_type, text in texts:
        track_data.extend(write_variable_length(0))  # Delta time = 0
        track_data.append(0xFF)  # Meta event
        track_data.append(meta_type)  # Meta type
        text_bytes = text.encode(encoding)
        track_data.extend(write_variable_length(len(text_bytes)))
        track_data.extend(text_bytes)

    # Add a simple note (C4 for 1 beat)
    track_data.extend(write_variable_length(0))  # Delta = 0
    track_data.extend(bytes([0x90, 60, 100]))  # Note on C4 velocity 100

    track_data.extend(write_variable_length(480))  # Delta = 480 ticks
    track_data.extend(bytes([0x80, 60, 0]))  # Note off C4

    # End of track
    track_data.extend(write_variable_length(0))
    track_data.extend(bytes([0xFF, 0x2F, 0x00]))

    # Track header
    track = b'MTrk'
    track += struct.pack('>I', len(track_data))
    track += bytes(track_data)

    # Write file
    with open(filename, 'wb') as f:
        f.write(header)
        f.write(track)

    print(f"Created: {filename}")


def main():
    # Test 1: Japanese text (Shift_JIS)
    japanese_texts = [
        (0x03, "日本語のテスト"),      # Track name
        (0x05, "さくらさくら"),         # Lyric
        (0x01, "これはテストです"),     # Text event
    ]
    create_midi_with_text("test_japanese.mid", japanese_texts, "shift_jis")

    # Test 2: Chinese text (GBK)
    chinese_texts = [
        (0x03, "中文测试"),             # Track name
        (0x05, "茉莉花"),               # Lyric
        (0x01, "这是一个测试文件"),     # Text event
    ]
    create_midi_with_text("test_chinese.mid", chinese_texts, "gbk")

    # Test 3: Korean text (EUC-KR)
    korean_texts = [
        (0x03, "한국어 테스트"),        # Track name
        (0x05, "아리랑"),               # Lyric
        (0x01, "테스트 파일입니다"),    # Text event
    ]
    create_midi_with_text("test_korean.mid", korean_texts, "euc-kr")

    # Test 4: Mixed ASCII/UTF-8
    utf8_texts = [
        (0x03, "UTF-8 Test Track"),
        (0x02, "Copyright © 2024"),     # Copyright
        (0x05, "Hello World! 你好世界!"),
        (0x06, "Verse 1"),              # Marker
    ]
    create_midi_with_text("test_utf8.mid", utf8_texts, "utf-8")

    print("\nAll test MIDI files created successfully!")
    print("\nTest files:")
    print("  - test_japanese.mid (Shift_JIS encoded)")
    print("  - test_chinese.mid (GBK encoded)")
    print("  - test_korean.mid (EUC-KR encoded)")
    print("  - test_utf8.mid (UTF-8 encoded)")


if __name__ == '__main__':
    main()
