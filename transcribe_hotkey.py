#!/usr/bin/env python3
"""
Whisper transcription with global hotkey activation for macOS.
Double-tap right Command key to start/stop recording.
"""

import argparse
import os
import threading
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import sounddevice as sd
import soundfile as sf
import whisper
from pynput import keyboard


class HotkeyTranscriber:
    def __init__(self, model_name="base", hotkey="double-cmd", output_dir="transcriptions", double_tap_delay=0.3):
        """
        Initialize the hotkey transcriber.

        Args:
            model_name: Whisper model size
            hotkey: Hotkey activation ('double-cmd' for double-tap right Cmd, or combo like '<cmd>+<shift>+r')
            output_dir: Directory to save transcriptions
            double_tap_delay: Maximum time between taps (seconds) for double-tap mode
        """
        self.model_name = model_name
        self.hotkey = hotkey
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.double_tap_delay = double_tap_delay
        self.use_double_tap = (hotkey == "double-cmd")

        self.is_recording = False
        self.audio_data = []
        self.sample_rate = 16000
        self.stream = None
        self.model = None

        # Double-tap detection
        self.last_tap_time = 0
        self.tap_count = 0

        print(f"Initializing Whisper model: {model_name}...")
        print("(First run will download the model)")
        self.model = whisper.load_model(model_name)
        print("Model loaded successfully!")

    def toggle_recording(self):
        """Toggle recording on/off."""
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self):
        """Start recording audio."""
        if self.is_recording:
            return

        print("\n🔴 Recording started... Press hotkey again to stop.")
        self.is_recording = True
        self.audio_data = []

        def audio_callback(indata, frames, time, status):
            if status:
                print(f"Status: {status}")
            if self.is_recording:
                self.audio_data.append(indata.copy())

        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype='float32',
            callback=audio_callback
        )
        self.stream.start()

    def stop_recording(self):
        """Stop recording and transcribe."""
        if not self.is_recording:
            return

        self.is_recording = False
        print("⏹️  Recording stopped. Transcribing...")

        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

        if not self.audio_data:
            print("No audio recorded.")
            return

        # Combine audio chunks
        audio = np.concatenate(self.audio_data, axis=0)

        # Save audio temporarily
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        audio_path = self.output_dir / f"recording_{timestamp}.wav"
        sf.write(audio_path, audio, self.sample_rate)

        # Transcribe
        print("Processing...")
        result = self.model.transcribe(str(audio_path))

        # Display result
        print("\n" + "="*60)
        print("TRANSCRIPTION:")
        print("="*60)
        print(result["text"])
        print("="*60)

        # Save transcription
        transcription_path = self.output_dir / f"transcription_{timestamp}.txt"
        with open(transcription_path, "w") as f:
            f.write(result["text"])

        print(f"\n✅ Saved to: {transcription_path}")
        print(f"🎤 Audio saved to: {audio_path}")

        if "language" in result:
            print(f"🌍 Detected language: {result['language']}")

        activation_msg = "Double-tap right Cmd" if self.use_double_tap else f"Press {self.hotkey}"
        print(f"\nReady! {activation_msg} to record again.")

    def on_right_cmd_tap(self):
        """Handle right Command key tap for double-tap detection."""
        current_time = time.time()

        if current_time - self.last_tap_time < self.double_tap_delay:
            # Double tap detected!
            self.tap_count = 0
            self.toggle_recording()
        else:
            # First tap
            self.tap_count = 1

        self.last_tap_time = current_time

    def run(self):
        """Start the hotkey listener."""
        print(f"\n{'='*60}")
        print("Whisper Hotkey Transcription")
        print(f"{'='*60}")
        print(f"Model: {self.model_name}")

        if self.use_double_tap:
            print(f"Activation: Double-tap right Command key")
            print(f"Output directory: {self.output_dir}")
            print(f"\n✨ Ready! Double-tap right Cmd key to start recording.")
        else:
            print(f"Hotkey: {self.hotkey}")
            print(f"Output directory: {self.output_dir}")
            print(f"\n✨ Ready! Press {self.hotkey} to start recording.")

        print("Press Ctrl+C to quit.\n")

        if self.use_double_tap:
            # Double-tap mode
            def on_press(key):
                if key == keyboard.Key.cmd_r:
                    self.on_right_cmd_tap()

            def on_release(key):
                pass
        else:
            # Combo hotkey mode
            hotkey_parts = self.hotkey.replace('<', '').replace('>', '').split('+')
            hotkey_combo = set()

            key_mapping = {
                'cmd': keyboard.Key.cmd,
                'ctrl': keyboard.Key.ctrl,
                'alt': keyboard.Key.alt,
                'option': keyboard.Key.alt,
                'shift': keyboard.Key.shift,
            }

            for part in hotkey_parts:
                part = part.lower()
                if part in key_mapping:
                    hotkey_combo.add(key_mapping[part])
                else:
                    # Regular key
                    hotkey_combo.add(keyboard.KeyCode.from_char(part))

            current_keys = set()

            def on_press(key):
                current_keys.add(key)
                if hotkey_combo.issubset(current_keys):
                    self.toggle_recording()

            def on_release(key):
                try:
                    current_keys.remove(key)
                except KeyError:
                    pass

        # Start listener
        with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
            try:
                listener.join()
            except KeyboardInterrupt:
                if self.is_recording:
                    print("\n\nStopping recording...")
                    self.stop_recording()
                print("\nGoodbye!")


def main():
    parser = argparse.ArgumentParser(
        description="Whisper transcription with global hotkey activation"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="base",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model size (default: base)"
    )
    parser.add_argument(
        "--hotkey",
        type=str,
        default="double-cmd",
        help="Hotkey activation: 'double-cmd' for double-tap right Cmd (default), or combo like '<cmd>+<shift>+r'"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="transcriptions",
        help="Output directory for transcriptions (default: transcriptions)"
    )

    args = parser.parse_args()

    print("\n⚠️  IMPORTANT: macOS Accessibility Permissions Required!")
    print("If the hotkey doesn't work, you need to:")
    print("1. Go to System Preferences > Security & Privacy > Privacy")
    print("2. Select 'Accessibility' from the left panel")
    print("3. Add Terminal (or your Python app) to the list")
    print("4. Restart this script\n")

    transcriber = HotkeyTranscriber(
        model_name=args.model,
        hotkey=args.hotkey,
        output_dir=args.output_dir
    )

    try:
        transcriber.run()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure you've granted Accessibility permissions!")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
