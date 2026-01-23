#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for MIDI Encoding Converter

This module contains comprehensive tests for the MIDI encoding converter,
including tests for different encodings, edge cases, and the GUI components.
"""

import os
import sys
import struct
import tempfile
import unittest
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from midi_encoding_converter import MidiEncodingConverter, detect_encoding


def write_variable_length(value: int) -> bytes:
    """Write a variable-length quantity."""
    result = [value & 0x7F]
    value >>= 7
    while value:
        result.append((value & 0x7F) | 0x80)
        value >>= 7
    return bytes(reversed(result))


def create_test_midi(texts: list, encoding: str = 'utf-8') -> bytes:
    """
    Create a test MIDI file in memory.

    Args:
        texts: List of (meta_type, text) tuples
        encoding: Text encoding to use

    Returns:
        MIDI file as bytes
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
        track_data.extend(write_variable_length(0))
        track_data.append(0xFF)
        track_data.append(meta_type)
        text_bytes = text.encode(encoding)
        track_data.extend(write_variable_length(len(text_bytes)))
        track_data.extend(text_bytes)

    # Add a simple note
    track_data.extend(write_variable_length(0))
    track_data.extend(bytes([0x90, 60, 100]))  # Note on
    track_data.extend(write_variable_length(480))
    track_data.extend(bytes([0x80, 60, 0]))  # Note off

    # End of track
    track_data.extend(write_variable_length(0))
    track_data.extend(bytes([0xFF, 0x2F, 0x00]))

    # Track header
    track = b'MTrk'
    track += struct.pack('>I', len(track_data))
    track += bytes(track_data)

    return header + track


class TestVariableLengthEncoding(unittest.TestCase):
    """Tests for variable-length quantity encoding/decoding."""

    def test_read_single_byte(self):
        """Test reading single-byte variable length values."""
        converter = MidiEncodingConverter()

        # Test values 0-127 (single byte)
        for value in [0, 1, 64, 127]:
            data = bytes([value])
            result, pos = converter.read_variable_length(data, 0)
            self.assertEqual(result, value)
            self.assertEqual(pos, 1)

    def test_read_multi_byte(self):
        """Test reading multi-byte variable length values."""
        converter = MidiEncodingConverter()

        # 128 = 0x81 0x00
        data = bytes([0x81, 0x00])
        result, pos = converter.read_variable_length(data, 0)
        self.assertEqual(result, 128)
        self.assertEqual(pos, 2)

        # 255 = 0x81 0x7F
        data = bytes([0x81, 0x7F])
        result, pos = converter.read_variable_length(data, 0)
        self.assertEqual(result, 255)

    def test_write_single_byte(self):
        """Test writing single-byte variable length values."""
        converter = MidiEncodingConverter()

        for value in [0, 1, 64, 127]:
            result = converter.write_variable_length(value)
            self.assertEqual(result, bytes([value]))

    def test_write_multi_byte(self):
        """Test writing multi-byte variable length values."""
        converter = MidiEncodingConverter()

        # 128 should be 0x81 0x00
        result = converter.write_variable_length(128)
        self.assertEqual(result, bytes([0x81, 0x00]))

        # 255 should be 0x81 0x7F
        result = converter.write_variable_length(255)
        self.assertEqual(result, bytes([0x81, 0x7F]))

    def test_roundtrip(self):
        """Test that write and read are inverses."""
        converter = MidiEncodingConverter()

        for value in [0, 1, 127, 128, 255, 256, 1000, 10000, 100000]:
            written = converter.write_variable_length(value)
            read, _ = converter.read_variable_length(written, 0)
            self.assertEqual(read, value, f"Roundtrip failed for {value}")


class TestTextConversion(unittest.TestCase):
    """Tests for text encoding conversion."""

    def test_shift_jis_to_utf8(self):
        """Test converting Shift_JIS to UTF-8."""
        converter = MidiEncodingConverter('shift_jis', 'utf-8')

        # Japanese text in Shift_JIS
        original = "日本語".encode('shift_jis')
        converted = converter.convert_text(original)
        self.assertEqual(converted.decode('utf-8'), "日本語")

    def test_gbk_to_utf8(self):
        """Test converting GBK to UTF-8."""
        converter = MidiEncodingConverter('gbk', 'utf-8')

        # Chinese text in GBK
        original = "中文测试".encode('gbk')
        converted = converter.convert_text(original)
        self.assertEqual(converted.decode('utf-8'), "中文测试")

    def test_euc_kr_to_utf8(self):
        """Test converting EUC-KR to UTF-8."""
        converter = MidiEncodingConverter('euc-kr', 'utf-8')

        # Korean text in EUC-KR
        original = "한국어".encode('euc-kr')
        converted = converter.convert_text(original)
        self.assertEqual(converted.decode('utf-8'), "한국어")

    def test_utf8_passthrough(self):
        """Test that UTF-8 to UTF-8 is passthrough."""
        converter = MidiEncodingConverter('utf-8', 'utf-8')

        original = "Hello 世界!".encode('utf-8')
        converted = converter.convert_text(original)
        self.assertEqual(converted, original)

    def test_ascii_compatibility(self):
        """Test that ASCII text works with any encoding."""
        converter = MidiEncodingConverter('shift_jis', 'utf-8')

        original = b"Hello World"
        converted = converter.convert_text(original)
        self.assertEqual(converted.decode('utf-8'), "Hello World")


class TestMidiConversion(unittest.TestCase):
    """Tests for complete MIDI file conversion."""

    def setUp(self):
        """Create temporary directory for test files."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_convert_japanese_midi(self):
        """Test converting a Japanese MIDI file."""
        # Create test file
        texts = [
            (0x03, "テスト"),
            (0x05, "さくら"),
        ]
        midi_data = create_test_midi(texts, 'shift_jis')

        input_path = os.path.join(self.temp_dir, 'japanese.mid')
        output_path = os.path.join(self.temp_dir, 'japanese_utf8.mid')

        with open(input_path, 'wb') as f:
            f.write(midi_data)

        # Convert
        converter = MidiEncodingConverter('shift_jis', 'utf-8')
        result = converter.convert(input_path, output_path)

        # Verify
        self.assertEqual(result['converted'], 2)
        self.assertEqual(result['errors'], 0)
        self.assertTrue(os.path.exists(output_path))

        # Verify output is valid MIDI
        with open(output_path, 'rb') as f:
            data = f.read()
            self.assertEqual(data[:4], b'MThd')

    def test_convert_chinese_midi(self):
        """Test converting a Chinese MIDI file."""
        texts = [
            (0x03, "测试"),
            (0x01, "中文歌曲"),
        ]
        midi_data = create_test_midi(texts, 'gbk')

        input_path = os.path.join(self.temp_dir, 'chinese.mid')
        output_path = os.path.join(self.temp_dir, 'chinese_utf8.mid')

        with open(input_path, 'wb') as f:
            f.write(midi_data)

        converter = MidiEncodingConverter('gbk', 'utf-8')
        result = converter.convert(input_path, output_path)

        self.assertEqual(result['converted'], 2)
        self.assertEqual(result['errors'], 0)

    def test_track_count(self):
        """Test that track count is correctly reported."""
        texts = [(0x03, "Track Name")]
        midi_data = create_test_midi(texts, 'utf-8')

        input_path = os.path.join(self.temp_dir, 'single_track.mid')
        output_path = os.path.join(self.temp_dir, 'output.mid')

        with open(input_path, 'wb') as f:
            f.write(midi_data)

        converter = MidiEncodingConverter('utf-8', 'utf-8')
        result = converter.convert(input_path, output_path)

        self.assertEqual(result['tracks'], 1)

    def test_all_text_meta_types(self):
        """Test that all text meta event types are converted."""
        texts = [
            (0x01, "Text Event"),
            (0x02, "Copyright"),
            (0x03, "Track Name"),
            (0x04, "Instrument"),
            (0x05, "Lyric"),
            (0x06, "Marker"),
            (0x07, "Cue Point"),
        ]
        midi_data = create_test_midi(texts, 'utf-8')

        input_path = os.path.join(self.temp_dir, 'all_types.mid')
        output_path = os.path.join(self.temp_dir, 'output.mid')

        with open(input_path, 'wb') as f:
            f.write(midi_data)

        converter = MidiEncodingConverter('utf-8', 'utf-8')
        result = converter.convert(input_path, output_path)

        self.assertEqual(result['converted'], 7)

    def test_invalid_midi_file(self):
        """Test handling of invalid MIDI file."""
        input_path = os.path.join(self.temp_dir, 'invalid.mid')
        output_path = os.path.join(self.temp_dir, 'output.mid')

        with open(input_path, 'wb') as f:
            f.write(b'This is not a MIDI file')

        converter = MidiEncodingConverter('utf-8', 'utf-8')

        with self.assertRaises(ValueError) as context:
            converter.convert(input_path, output_path)

        self.assertIn('MThd', str(context.exception))

    def test_default_output_filename(self):
        """Test that default output filename is generated correctly."""
        texts = [(0x03, "Test")]
        midi_data = create_test_midi(texts, 'utf-8')

        input_path = os.path.join(self.temp_dir, 'input.mid')
        with open(input_path, 'wb') as f:
            f.write(midi_data)

        converter = MidiEncodingConverter('utf-8', 'utf-8')
        result = converter.convert(input_path)  # No output path specified

        self.assertIn('_converted', result['output_file'])


class TestEncodingDetection(unittest.TestCase):
    """Tests for encoding detection functionality."""

    def setUp(self):
        """Create temporary directory for test files."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_detect_shift_jis(self):
        """Test detecting Shift_JIS encoding."""
        try:
            import chardet
        except ImportError:
            self.skipTest("chardet not installed")

        texts = [
            (0x03, "日本語のテスト曲"),
            (0x05, "さくらさくら"),
        ]
        midi_data = create_test_midi(texts, 'shift_jis')

        input_path = os.path.join(self.temp_dir, 'japanese.mid')
        with open(input_path, 'wb') as f:
            f.write(midi_data)

        results = detect_encoding(input_path)
        self.assertGreater(len(results), 0)

    def test_detect_gbk(self):
        """Test detecting GBK encoding."""
        try:
            import chardet
        except ImportError:
            self.skipTest("chardet not installed")

        texts = [
            (0x03, "中文歌曲测试"),
            (0x05, "茉莉花茉莉花"),
        ]
        midi_data = create_test_midi(texts, 'gbk')

        input_path = os.path.join(self.temp_dir, 'chinese.mid')
        with open(input_path, 'wb') as f:
            f.write(midi_data)

        results = detect_encoding(input_path)
        self.assertGreater(len(results), 0)

    def test_detect_invalid_file(self):
        """Test detection on invalid MIDI file."""
        input_path = os.path.join(self.temp_dir, 'invalid.mid')
        with open(input_path, 'wb') as f:
            f.write(b'Not a MIDI file')

        with self.assertRaises(ValueError):
            detect_encoding(input_path)


class TestEdgeCases(unittest.TestCase):
    """Tests for edge cases and error handling."""

    def setUp(self):
        """Create temporary directory for test files."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_empty_text_event(self):
        """Test handling of empty text events."""
        texts = [
            (0x03, ""),  # Empty track name
            (0x05, "Lyric"),
        ]
        midi_data = create_test_midi(texts, 'utf-8')

        input_path = os.path.join(self.temp_dir, 'empty.mid')
        output_path = os.path.join(self.temp_dir, 'output.mid')

        with open(input_path, 'wb') as f:
            f.write(midi_data)

        converter = MidiEncodingConverter('utf-8', 'utf-8')
        result = converter.convert(input_path, output_path)

        self.assertEqual(result['converted'], 2)

    def test_long_text_event(self):
        """Test handling of long text events."""
        long_text = "A" * 10000  # Very long text
        texts = [(0x03, long_text)]
        midi_data = create_test_midi(texts, 'utf-8')

        input_path = os.path.join(self.temp_dir, 'long.mid')
        output_path = os.path.join(self.temp_dir, 'output.mid')

        with open(input_path, 'wb') as f:
            f.write(midi_data)

        converter = MidiEncodingConverter('utf-8', 'utf-8')
        result = converter.convert(input_path, output_path)

        self.assertEqual(result['converted'], 1)
        self.assertEqual(result['errors'], 0)

    def test_special_characters(self):
        """Test handling of special characters."""
        texts = [
            (0x03, "Test™ © ® € £ ¥"),
            (0x05, "♪ ♫ ♬ ♩"),
        ]
        midi_data = create_test_midi(texts, 'utf-8')

        input_path = os.path.join(self.temp_dir, 'special.mid')
        output_path = os.path.join(self.temp_dir, 'output.mid')

        with open(input_path, 'wb') as f:
            f.write(midi_data)

        converter = MidiEncodingConverter('utf-8', 'utf-8')
        result = converter.convert(input_path, output_path)

        self.assertEqual(result['errors'], 0)

    def test_file_not_found(self):
        """Test handling of non-existent file."""
        converter = MidiEncodingConverter('utf-8', 'utf-8')

        with self.assertRaises(FileNotFoundError):
            converter.convert('nonexistent.mid', 'output.mid')

    def test_preserves_midi_data(self):
        """Test that MIDI note data is preserved."""
        texts = [(0x03, "Test")]
        midi_data = create_test_midi(texts, 'utf-8')

        input_path = os.path.join(self.temp_dir, 'notes.mid')
        output_path = os.path.join(self.temp_dir, 'output.mid')

        with open(input_path, 'wb') as f:
            f.write(midi_data)

        converter = MidiEncodingConverter('utf-8', 'utf-8')
        converter.convert(input_path, output_path)

        # Read output and verify it's a valid MIDI
        with open(output_path, 'rb') as f:
            data = f.read()

        # Check header
        self.assertEqual(data[:4], b'MThd')

        # Find MTrk marker (after header)
        mtrk_pos = data.find(b'MTrk')
        self.assertGreater(mtrk_pos, 0, "MTrk marker not found")

        # Check that note events exist (0x90 for note on, 0x80 for note off)
        self.assertIn(b'\x90\x3c\x64', data)  # Note on C4 velocity 100
        self.assertIn(b'\x80\x3c\x00', data)  # Note off C4


class TestConverterState(unittest.TestCase):
    """Tests for converter internal state."""

    def test_counts_reset_between_conversions(self):
        """Test that counts are reset between conversions."""
        temp_dir = tempfile.mkdtemp()

        try:
            texts = [(0x03, "Test")]
            midi_data = create_test_midi(texts, 'utf-8')

            input_path = os.path.join(temp_dir, 'test.mid')
            with open(input_path, 'wb') as f:
                f.write(midi_data)

            converter = MidiEncodingConverter('utf-8', 'utf-8')

            # First conversion
            result1 = converter.convert(input_path, os.path.join(temp_dir, 'out1.mid'))
            self.assertEqual(result1['converted'], 1)

            # Second conversion
            result2 = converter.convert(input_path, os.path.join(temp_dir, 'out2.mid'))
            self.assertEqual(result2['converted'], 1)

        finally:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_verbose_mode(self):
        """Test verbose mode setting."""
        converter = MidiEncodingConverter()
        self.assertFalse(converter.verbose)

        converter.verbose = True
        self.assertTrue(converter.verbose)


def run_tests():
    """Run all tests and print summary."""
    # Create a test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestVariableLengthEncoding))
    suite.addTests(loader.loadTestsFromTestCase(TestTextConversion))
    suite.addTests(loader.loadTestsFromTestCase(TestMidiConversion))
    suite.addTests(loader.loadTestsFromTestCase(TestEncodingDetection))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestConverterState))

    # Run with verbosity
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")

    if result.wasSuccessful():
        print("\n[OK] All tests passed!")
    else:
        print("\n[FAIL] Some tests failed!")

        if result.failures:
            print("\nFailures:")
            for test, traceback in result.failures:
                print(f"  - {test}")

        if result.errors:
            print("\nErrors:")
            for test, traceback in result.errors:
                print(f"  - {test}")

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
