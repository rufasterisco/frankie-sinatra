#!/usr/bin/env python3
"""
Whisper transcription with macOS menu bar app.
Provides an easy-to-use menu bar interface for speech-to-text transcription.
"""

import os
import threading
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import pyperclip
import rumps
import sounddevice as sd
import soundfile as sf
import whisper
from pynput import keyboard


class WhisperMenuBarApp(rumps.App):
    def __init__(self):
        super(WhisperMenuBarApp, self).__init__(
            name="Whisper",
            title="🎤",
            quit_button=rumps.MenuItem("Quit", key="q")
        )

        # Default settings
        self.model_name = "small"
        self.output_dir = Path("transcriptions")
        self.output_dir.mkdir(exist_ok=True)
        self.auto_paste = True
        self.auto_stop = True
        self.silence_threshold = -40
        self.silence_duration = 2.0
        self.language = "en"
        self.auto_detect_language = False
        self.keep_audio = False
        self.hotkey_enabled = True
        self.double_tap_delay = 0.3

        # Recording state
        self.is_recording = False
        self.audio_data = []
        self.sample_rate = 16000
        self.stream = None
        self.model = None
        self.keyboard_controller = keyboard.Controller()

        # Silence detection
        self.silence_start_time = None
        self.last_audio_time = None

        # Hotkey detection
        self.last_tap_time = 0
        self.tap_count = 0
        self.keyboard_listener = None

        # Menu items
        self.start_stop_button = rumps.MenuItem(
            title="Start Recording",
            callback=self.toggle_recording
        )
        self.status_item = rumps.MenuItem("Status: Ready", callback=None)

        # Settings menu items
        self.auto_paste_toggle = rumps.MenuItem(
            title="Auto-paste",
            callback=self.toggle_auto_paste
        )
        self.auto_paste_toggle.state = self.auto_paste

        self.auto_stop_toggle = rumps.MenuItem(
            title="Auto-stop on silence",
            callback=self.toggle_auto_stop
        )
        self.auto_stop_toggle.state = self.auto_stop

        self.keep_audio_toggle = rumps.MenuItem(
            title="Keep audio files",
            callback=self.toggle_keep_audio
        )
        self.keep_audio_toggle.state = self.keep_audio

        self.hotkey_toggle = rumps.MenuItem(
            title="Global hotkey (double-tap ⌘)",
            callback=self.toggle_hotkey
        )
        self.hotkey_toggle.state = self.hotkey_enabled

        # Build menu
        self.menu = [
            self.status_item,
            None,  # Separator
            self.start_stop_button,
            None,  # Separator
            {
                "Settings": [
                    self.hotkey_toggle,
                    None,  # Separator
                    self.auto_paste_toggle,
                    self.auto_stop_toggle,
                    self.keep_audio_toggle,
                ]
            },
        ]

        # Initialize model in background
        self.model_loaded = False
        threading.Thread(target=self.load_model, daemon=True).start()

        # Start hotkey listener in background
        if self.hotkey_enabled:
            threading.Thread(target=self.start_hotkey_listener, daemon=True).start()

    def load_model(self):
        """Load Whisper model in background."""
        try:
            self.status_item.title = "Status: Loading model..."
            print(f"Loading Whisper model: {self.model_name}...")
            self.model = whisper.load_model(self.model_name)
            self.model_loaded = True
            self.status_item.title = "Status: Ready"
            print("Model loaded successfully!")
        except Exception as e:
            self.status_item.title = f"Status: Error loading model"
            print(f"Error loading model: {e}")

    def toggle_recording(self, sender):
        """Toggle recording on/off."""
        if not self.model_loaded:
            rumps.alert("Please wait", "Model is still loading...")
            return

        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()

    def toggle_auto_paste(self, sender):
        """Toggle auto-paste setting."""
        self.auto_paste = not self.auto_paste
        sender.state = self.auto_paste
        status = "enabled" if self.auto_paste else "disabled"
        print(f"Auto-paste {status}")

    def toggle_auto_stop(self, sender):
        """Toggle auto-stop setting."""
        self.auto_stop = not self.auto_stop
        sender.state = self.auto_stop
        status = "enabled" if self.auto_stop else "disabled"
        print(f"Auto-stop on silence {status}")

    def toggle_keep_audio(self, sender):
        """Toggle keep audio files setting."""
        self.keep_audio = not self.keep_audio
        sender.state = self.keep_audio
        status = "enabled" if self.keep_audio else "disabled"
        print(f"Keep audio files {status}")

    def toggle_hotkey(self, sender):
        """Toggle global hotkey setting."""
        self.hotkey_enabled = not self.hotkey_enabled
        sender.state = self.hotkey_enabled

        if self.hotkey_enabled:
            # Start the listener
            print("Global hotkey enabled (double-tap right ⌘)")
            threading.Thread(target=self.start_hotkey_listener, daemon=True).start()
        else:
            # Stop the listener
            print("Global hotkey disabled")
            if self.keyboard_listener:
                self.keyboard_listener.stop()
                self.keyboard_listener = None

    def start_hotkey_listener(self):
        """Start listening for global hotkey in background thread."""
        def on_press(key):
            if key == keyboard.Key.cmd_r:
                self.on_right_cmd_tap()

        def on_release(key):
            pass

        # Create and start listener
        self.keyboard_listener = keyboard.Listener(
            on_press=on_press,
            on_release=on_release
        )
        self.keyboard_listener.start()
        print("Hotkey listener started (double-tap right ⌘ to record)")

    def on_right_cmd_tap(self):
        """Handle right Command key tap for double-tap detection."""
        current_time = time.time()

        if current_time - self.last_tap_time < self.double_tap_delay:
            # Double tap detected!
            self.tap_count = 0
            self.toggle_recording(None)
        else:
            # First tap
            self.tap_count = 1

        self.last_tap_time = current_time

    def start_recording(self):
        """Start recording audio."""
        if self.is_recording:
            return

        print("\n🔴 Recording started...")
        self.is_recording = True
        self.audio_data = []
        self.silence_start_time = None
        self.last_audio_time = time.time()

        # Update UI
        self.title = "🔴"
        self.start_stop_button.title = "Stop Recording"
        self.status_item.title = "Status: Recording..."

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
                # Reset UI
                self.title = "🎤"
                self.start_stop_button.title = "Start Recording"
                self.status_item.title = "Status: Ready"
            return

        # Ensure recording is stopped
        was_recording = self.is_recording
        self.is_recording = False

        if was_recording or self.stream:
            print("⏹️  Recording stopped. Transcribing...")

        # Update UI
        self.title = "⏳"
        self.start_stop_button.title = "Start Recording"
        self.status_item.title = "Status: Transcribing..."

        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

        if not self.audio_data:
            print("No audio recorded.")
            self.title = "🎤"
            self.status_item.title = "Status: Ready"
            return

        # Process transcription in background thread to avoid blocking UI
        threading.Thread(
            target=self._process_transcription,
            daemon=True
        ).start()

    def _process_transcription(self):
        """Process transcription in background thread."""
        try:
            # Combine audio chunks
            audio = np.concatenate(self.audio_data, axis=0)

            # Save audio temporarily
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_path = self.output_dir / f"recording_{timestamp}.wav"
            sf.write(audio_path, audio, self.sample_rate)

            # Transcribe
            print("Processing...")
            if self.language:
                result = self.model.transcribe(str(audio_path), language=self.language)
            else:
                result = self.model.transcribe(str(audio_path))

            # Display result
            print("\n" + "="*60)
            print("TRANSCRIPTION:")
            print("="*60)
            print(result["text"])
            print("="*60)

            # Save transcription temporarily (for reference if paste fails)
            transcription_path = self.output_dir / f"transcription_{timestamp}.txt"
            with open(transcription_path, "w") as f:
                f.write(result["text"])

            if self.keep_audio:
                print(f"\n✅ Transcription saved to: {transcription_path}")
                print(f"🎤 Audio saved to: {audio_path}")
            else:
                # Delete both audio and text files after transcription
                print(f"\n✅ Transcription complete")
                try:
                    os.remove(audio_path)
                    os.remove(transcription_path)
                    print(f"🗑️  Temporary files deleted (transcription in clipboard)")
                except Exception as e:
                    print(f"⚠️  Could not delete temporary files: {e}")

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

            # Reset UI
            self.title = "🎤"
            self.status_item.title = "Status: Ready"
            print("\nReady to record again!")

        except Exception as e:
            print(f"Error during transcription: {e}")
            self.title = "❌"
            self.status_item.title = "Status: Error"
            time.sleep(2)
            self.title = "🎤"
            self.status_item.title = "Status: Ready"


def main():
    print("="*60)
    print("Whisper Menu Bar Transcription")
    print("="*60)
    print("\nStarting menu bar app...")
    print("\n⚠️  IMPORTANT: macOS Accessibility Permissions Required!")
    print("If auto-paste doesn't work, you need to:")
    print("1. Go to System Preferences > Security & Privacy > Privacy")
    print("2. Select 'Accessibility' from the left panel")
    print("3. Add Terminal (or Python) to the list")
    print("4. Restart this app\n")
    print("Look for the 🎤 icon in your menu bar!")
    print("="*60 + "\n")

    app = WhisperMenuBarApp()
    app.run()


if __name__ == "__main__":
    main()
