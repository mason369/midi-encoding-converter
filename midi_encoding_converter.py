#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIDI Encoding Converter

A Python tool to convert text event encodings in MIDI files.
Supports conversion between various encodings (Shift_JIS, GBK, UTF-8, etc.)

Author: AI Assistant
License: MIT
Version: 1.0.0
"""

import struct
import argparse
import sys
from pathlib import Path
from typing import Tuple, List, Optional

__version__ = "1.0.0"


class MidiEncodingConverter:
    """Convert text event encodings in MIDI files."""

    # Meta event types that contain text
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
        """
        Initialize the converter.

        Args:
            from_encoding: Source encoding (default: shift_jis)
            to_encoding: Target encoding (default: utf-8)
        """
        self.from_encoding = from_encoding
        self.to_encoding = to_encoding
        self.converted_count = 0
        self.error_count = 0
        self.verbose = False

    @staticmethod
    def read_variable_length(data: bytes, pos: int) -> Tuple[int, int]:
        """
        Read a variable-length quantity from MIDI data.

        Args:
            data: MIDI file data
            pos: Current position

        Returns:
            Tuple of (value, new_position)
        """
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
        """
        Write a variable-length quantity.

        Args:
            value: Integer value to encode

        Returns:
            Encoded bytes
        """
        result = [value & 0x7F]
        value >>= 7
        while value:
            result.append((value & 0x7F) | 0x80)
            value >>= 7
        return bytes(reversed(result))

    def convert_text(self, data: bytes) -> bytes:
        """
        Convert text data from source encoding to target encoding.

        Args:
            data: Original text bytes

        Returns:
            Converted text bytes
        """
        try:
            text = data.decode(self.from_encoding, errors='replace')
            return text.encode(self.to_encoding)
        except Exception as e:
            self.error_count += 1
            if self.verbose:
                print(f"Warning: Conversion error - {e}", file=sys.stderr)
            return data

    def convert(self, input_file: str, output_file: Optional[str] = None) -> dict:
        """
        Convert a MIDI file's text encodings.

        Args:
            input_file: Path to input MIDI file
            output_file: Path to output MIDI file (default: input_converted.mid)

        Returns:
            Dictionary with conversion statistics
        """
        input_path = Path(input_file)

        if output_file is None:
            output_file = input_path.stem + "_converted" + input_path.suffix

        with open(input_file, 'rb') as f:
            data = bytearray(f.read())

        # Validate MIDI header
        if data[:4] != b'MThd':
            raise ValueError("Not a valid MIDI file (missing MThd header)")

        self.converted_count = 0
        self.error_count = 0

        pos = 0
        output = bytearray()

        # Copy MIDI header
        header_length = struct.unpack('>I', data[4:8])[0]
        output.extend(data[:8 + header_length])
        pos = 8 + header_length

        # Process each track
        track_count = 0
        while pos < len(data):
            if data[pos:pos+4] != b'MTrk':
                break

            track_count += 1
            track_start = len(output)
            output.extend(data[pos:pos+4])  # MTrk
            pos += 4

            track_length = struct.unpack('>I', data[pos:pos+4])[0]
            pos += 4
            output.extend(b'\x00\x00\x00\x00')  # Placeholder for length

            track_data_start = len(output)
            track_end = pos + track_length

            running_status = 0

            while pos < track_end:
                # Read delta time
                delta, new_pos = self.read_variable_length(data, pos)
                output.extend(self.write_variable_length(delta))
                pos = new_pos

                # Read event
                status = data[pos]

                if status == 0xFF:  # Meta event
                    output.append(data[pos])
                    pos += 1
                    meta_type = data[pos]
                    output.append(data[pos])
                    pos += 1
                    length, new_pos = self.read_variable_length(data, pos)
                    pos = new_pos

                    meta_data = data[pos:pos + length]
                    pos += length

                    # Convert text meta events
                    if meta_type in self.TEXT_META_TYPES:
                        new_data = self.convert_text(bytes(meta_data))
                        self.converted_count += 1
                        if self.verbose and new_data != meta_data:
                            try:
                                old_text = meta_data.decode(self.from_encoding, errors='replace')
                                new_text = new_data.decode(self.to_encoding, errors='replace')
                                print(f"  [{self.TEXT_META_TYPES[meta_type]}] {old_text[:40]}")
                            except:
                                pass
                    else:
                        new_data = meta_data

                    output.extend(self.write_variable_length(len(new_data)))
                    output.extend(new_data)

                elif status == 0xF0 or status == 0xF7:  # SysEx
                    output.append(data[pos])
                    pos += 1
                    length, new_pos = self.read_variable_length(data, pos)
                    output.extend(self.write_variable_length(length))
                    pos = new_pos
                    output.extend(data[pos:pos + length])
                    pos += length
                    running_status = 0

                elif status & 0x80:  # Status byte
                    running_status = status
                    output.append(data[pos])
                    pos += 1

                    if status & 0xF0 in (0x80, 0x90, 0xA0, 0xB0, 0xE0):
                        output.extend(data[pos:pos+2])
                        pos += 2
                    elif status & 0xF0 in (0xC0, 0xD0):
                        output.append(data[pos])
                        pos += 1

                else:  # Running status
                    if running_status:
                        output.append(data[pos])
                        pos += 1
                        if running_status & 0xF0 in (0x80, 0x90, 0xA0, 0xB0, 0xE0):
                            output.append(data[pos])
                            pos += 1
                    else:
                        # Unknown byte, copy it
                        output.append(data[pos])
                        pos += 1

            # Update track length
            track_data_length = len(output) - track_data_start
            struct.pack_into('>I', output, track_start + 4, track_data_length)

        # Write output file
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
    """
    Detect possible encodings in a MIDI file.

    Args:
        input_file: Path to MIDI file

    Returns:
        List of (encoding, confidence) tuples
    """
    try:
        import chardet
    except ImportError:
        print("Warning: chardet not installed. Install with: pip install chardet", file=sys.stderr)
        return []

    with open(input_file, 'rb') as f:
        data = f.read()

    if data[:4] != b'MThd':
        raise ValueError("Not a valid MIDI file")

    # Collect all text data
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
            # Skip delta time
            while data[pos] & 0x80:
                pos += 1
            pos += 1

            status = data[pos]

            if status == 0xFF:
                pos += 1
                meta_type = data[pos]
                pos += 1
                length = 0
                while data[pos] & 0x80:
                    length = (length << 7) | (data[pos] & 0x7F)
                    pos += 1
                length = (length << 7) | data[pos]
                pos += 1

                if meta_type in (0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07):
                    all_text_bytes.extend(data[pos:pos + length])
                pos += length
            elif status == 0xF0 or status == 0xF7:
                pos += 1
                length = 0
                while data[pos] & 0x80:
                    length = (length << 7) | (data[pos] & 0x7F)
                    pos += 1
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


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Convert text encodings in MIDI files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.mid                           # Convert from Shift_JIS to UTF-8
  %(prog)s input.mid -o output.mid             # Specify output file
  %(prog)s input.mid -f gbk -t utf-8           # Convert from GBK to UTF-8
  %(prog)s input.mid --detect                  # Detect encoding only
        """
    )

    parser.add_argument('input', help='Input MIDI file')
    parser.add_argument('-o', '--output', help='Output MIDI file')
    parser.add_argument('-f', '--from-encoding', default='shift_jis',
                        help='Source encoding (default: shift_jis)')
    parser.add_argument('-t', '--to-encoding', default='utf-8',
                        help='Target encoding (default: utf-8)')
    parser.add_argument('-d', '--detect', action='store_true',
                        help='Detect encoding only (do not convert)')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Verbose output')
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')

    args = parser.parse_args()

    if args.detect:
        print(f"Detecting encoding in: {args.input}")
        results = detect_encoding(args.input)
        if results:
            print("\nPossible encodings:")
            for encoding, confidence in results:
                print(f"  {encoding}: {confidence:.1%}")
        else:
            print("No encoding detected or file contains only ASCII text.")
        return

    converter = MidiEncodingConverter(args.from_encoding, args.to_encoding)
    converter.verbose = args.verbose

    print(f"Converting: {args.input}")
    print(f"Encoding: {args.from_encoding} -> {args.to_encoding}")

    result = converter.convert(args.input, args.output)

    print(f"\nConversion complete!")
    print(f"  Output: {result['output_file']}")
    print(f"  Tracks: {result['tracks']}")
    print(f"  Text events converted: {result['converted']}")
    if result['errors'] > 0:
        print(f"  Errors: {result['errors']}")
    print(f"  Size: {result['input_size']} -> {result['output_size']} bytes")


if __name__ == '__main__':
    main()
