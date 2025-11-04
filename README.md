# Whisper Local Transcription POC

A simple proof-of-concept for using OpenAI's Whisper model locally to transcribe speech to text.

## Overview

This project provides a minimal implementation to evaluate the quality of local speech-to-text transcription using Whisper. It allows you to record audio and get instant transcriptions.

## Prerequisites

- Python 3.8+
- A microphone
- FFmpeg (required by Whisper)

### Install FFmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html)

## Installation

1. Clone or navigate to this repository
2. Install dependencies using uv:
```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies (uv will handle the virtual environment automatically)
uv sync
```

## Usage

### Option 1: Hotkey Activation with Auto-Paste (Recommended)

Run the hotkey listener and use a global hotkey to start/stop recording. Transcriptions are automatically pasted wherever your cursor is:

```bash
uv run transcribe_hotkey.py
```

**How it works:**
- **Double-tap right Command key** to start recording
- Speak into your microphone
- **Automatically stops** after 2 seconds of silence (or double-tap again to stop manually)
- Transcription is copied to clipboard AND automatically pasted to your active application

**Options:**

```bash
# Disable auto-paste (clipboard only)
uv run transcribe_hotkey.py --no-paste

# Disable auto-stop (manual stop with double-tap required)
uv run transcribe_hotkey.py --no-auto-stop

# Use a keyboard combination instead of double-tap
uv run transcribe_hotkey.py --hotkey "<cmd>+<shift>+r"

# Adjust silence detection sensitivity
uv run transcribe_hotkey.py --silence-threshold -45  # Lower = more sensitive

# Adjust silence duration before auto-stop
uv run transcribe_hotkey.py --silence-duration 3.0   # Longer pause tolerance
```

**macOS Permissions Required:**
On first run, macOS will require Accessibility permissions:
1. Go to **System Preferences > Security & Privacy > Privacy**
2. Select **Accessibility** from the left panel
3. Add **Terminal** (or your Python app) to the list
4. Restart the script

### Option 2: Manual Transcription

Run the script and speak into your microphone:

```bash
uv run transcribe.py
```

Press `Ctrl+C` to stop recording. The transcription will be displayed.

**Options:**
```bash
# Use a different model size (tiny, base, small, medium, large)
uv run transcribe.py --model base

# Transcribe an existing audio file
uv run transcribe.py --file audio.mp3

# Set recording duration (in seconds)
uv run transcribe.py --duration 10
```

## Model Sizes

| Model  | Parameters | Speed | Quality | Memory |
|--------|-----------|-------|---------|--------|
| tiny   | 39M       | Fast  | Basic   | ~1GB   |
| base   | 74M       | Fast  | Good    | ~1GB   |
| small  | 244M      | Medium| Better  | ~2GB   |
| medium | 769M      | Slow  | Great   | ~5GB   |
| large  | 1550M     | Slowest| Best   | ~10GB  |

**Recommendation:** Start with `base` for quick evaluation, use `small` or `medium` for better quality.

## Output

The transcription will be:
- Displayed in the console
- Saved to `transcription.txt`
- Timestamped in `transcriptions/` directory (if multiple recordings)

## Troubleshooting

**Hotkey not working (macOS):**
- Grant Accessibility permissions (see Usage section above)
- Check that the hotkey isn't already used by another app
- Try a different hotkey combination

**No microphone detected:**
- Check your microphone is connected and permissions are granted
- On macOS: System Preferences > Security & Privacy > Microphone

**Poor transcription quality:**
- Try a larger model (`--model medium`)
- Ensure good microphone quality and minimal background noise
- Speak clearly and at a moderate pace

## License

MIT
