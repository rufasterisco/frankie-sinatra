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
import pyperclip
import sounddevice as sd
import soundfile as sf
import whisper
from pynput import keyboard


class HotkeyTranscriber:
    def __init__(self, model_name="base", hotkey="double-cmd", output_dir="transcriptions", double_tap_delay=0.3, auto_paste=True, auto_stop=True, silence_threshold=-40, silence_duration=2.0):
        """
        Initialize the hotkey transcriber.

        Args:
            model_name: Whisper model size
            hotkey: Hotkey activation ('double-cmd' for double-tap right Cmd, or combo like '<cmd>+<shift>+r')
            output_dir: Directory to save transcriptions
            double_tap_delay: Maximum time between taps (seconds) for double-tap mode
            auto_paste: Automatically paste transcription to active application
            auto_stop: Automatically stop recording after silence
            silence_threshold: Audio level threshold in dB for silence detection (default: -40)
            silence_duration: Duration of silence in seconds before auto-stop (default: 2.0)
        """
        self.model_name = model_name
        self.hotkey = hotkey
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.double_tap_delay = double_tap_delay
        self.use_double_tap = (hotkey == "double-cmd")
        self.auto_paste = auto_paste
        self.auto_stop = auto_stop
        self.silence_threshold = silence_threshold
        self.silence_duration = silence_duration

        self.is_recording = False
        self.audio_data = []
        self.sample_rate = 16000
        self.stream = None
        self.model = None
        self.keyboard_controller = keyboard.Controller()

        # Double-tap detection
        self.last_tap_time = 0
        self.tap_count = 0

        # Silence detection
        self.silence_start_time = None
        self.last_audio_time = None

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

        if self.auto_stop:
            print("\n🔴 Recording... (will auto-stop after silence)")
        else:
            print("\n🔴 Recording... Press hotkey again to stop.")

        self.is_recording = True
        self.audio_data = []
        self.silence_start_time = None
        self.last_audio_time = time.time()

        def audio_callback(indata, frames, time_info, status):
            if status:
                print(f"Status: {status}")
            if self.is_recording:
                self.audio_data.append(indata.copy())

                # Silence detection
                if self.auto_stop:
                    # Calculate RMS (Root Mean Square) audio level
                    rms = np.sqrt(np.mean(indata**2))
                    # Convert to dB
                    if rms > 0:
                        db_level = 20 * np.log10(rms)
                    else:
                        db_level = -100  # Very quiet

                    current_time = time.time()

                    if db_level > self.silence_threshold:
                        # Audio detected, reset silence timer
                        self.silence_start_time = None
                        self.last_audio_time = current_time
                    else:
                        # Silence detected
                        if self.silence_start_time is None:
                            self.silence_start_time = current_time
                        else:
                            elapsed = current_time - self.silence_start_time
                            if elapsed >= self.silence_duration:
                                # Silence duration exceeded, stop recording
                                print(f"🔇 Silence detected, stopping...")
                                self.is_recording = False

        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype='float32',
            callback=audio_callback
        )
        self.stream.start()

        # If auto-stop is enabled, start a monitoring thread
        if self.auto_stop:
            def monitor_recording():
                while self.stream and self.stream.active:
                    if not self.is_recording and len(self.audio_data) > 0:
                        # Recording stopped by silence detection
                        time.sleep(0.1)  # Small delay
                        self.stop_recording()
                        break
                    time.sleep(0.5)

            threading.Thread(target=monitor_recording, daemon=True).start()

    def stop_recording(self):
        """Stop recording and transcribe."""
        # Check if we have audio data to process
        if not self.audio_data:
            if self.is_recording:
                self.is_recording = False
                if self.stream:
                    self.stream.stop()
                    self.stream.close()
                    self.stream = None
                print("No audio recorded.")
            return

        # Ensure recording is stopped
        was_recording = self.is_recording
        self.is_recording = False

        if was_recording or self.stream:
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

        # Copy to clipboard and optionally paste
        transcription_text = result["text"].strip()
        pyperclip.copy(transcription_text)
        print(f"📋 Copied to clipboard")

        if self.auto_paste:
            print(f"✨ Pasting to active application...")
            time.sleep(0.1)  # Small delay to ensure clipboard is ready

            # Simulate Cmd+V to paste
            with self.keyboard_controller.pressed(keyboard.Key.cmd):
                self.keyboard_controller.press('v')
                self.keyboard_controller.release('v')

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
        else:
            print(f"Hotkey: {self.hotkey}")

        print(f"Output directory: {self.output_dir}")
        paste_mode = "Auto-paste enabled" if self.auto_paste else "Clipboard only (no auto-paste)"
        print(f"Paste mode: {paste_mode}")

        if self.auto_stop:
            print(f"Auto-stop: Enabled (silence threshold: {self.silence_threshold}dB, duration: {self.silence_duration}s)")
        else:
            print(f"Auto-stop: Disabled (manual stop required)")

        if self.use_double_tap:
            print(f"\n✨ Ready! Double-tap right Cmd key to start recording.")
        else:
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
        default="small",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model size (default: small)"
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
    parser.add_argument(
        "--no-paste",
        action="store_true",
        help="Disable auto-paste (clipboard only)"
    )
    parser.add_argument(
        "--no-auto-stop",
        action="store_true",
        help="Disable automatic stop on silence (requires manual stop)"
    )
    parser.add_argument(
        "--silence-threshold",
        type=float,
        default=-40,
        help="Silence detection threshold in dB (default: -40, lower = more sensitive)"
    )
    parser.add_argument(
        "--silence-duration",
        type=float,
        default=2.0,
        help="Duration of silence in seconds before auto-stop (default: 2.0)"
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
        output_dir=args.output_dir,
        auto_paste=not args.no_paste,
        auto_stop=not args.no_auto_stop,
        silence_threshold=args.silence_threshold,
        silence_duration=args.silence_duration
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
