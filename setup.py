"""
Setup script for building Whisper Transcription as a standalone macOS app.

Usage:
    python setup.py py2app

This will create a .app bundle in the dist/ directory that can be:
- Dragged to /Applications
- Launched via Spotlight
- Run without Terminal
"""

from setuptools import setup

APP = ['transcribe_menubar.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,  # Not needed for menu bar apps
    'plist': {
        'CFBundleName': 'Lolalola',
        'CFBundleDisplayName': 'Lolalola',
        'CFBundleIdentifier': 'com.lolalola.transcription',
        'CFBundleVersion': '0.1.0',
        'CFBundleShortVersionString': '0.1.0',
        'LSUIElement': True,  # Hide from Dock (menu bar only)
        'NSMicrophoneUsageDescription': 'Lolalola needs microphone access to record audio for transcription.',
    },
    'packages': [
        'rumps',
        'whisper',
        'sounddevice',
        'soundfile',
        'numpy',
        'pynput',
        'pyperclip',
    ],
    'includes': [
        'whisper',
        'whisper.model',
        'whisper.audio',
        'whisper.decoding',
        'whisper.timing',
        'whisper.tokenizer',
    ],
}

setup(
    name='Lolalola',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
