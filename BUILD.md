# Building Whisper as a Standalone macOS App

This guide explains how to build Whisper Transcription as a standalone `.app` bundle that can be dragged to `/Applications` and launched via Spotlight.

## Prerequisites

- Python 3.8+ installed
- All project dependencies installed (`uv sync`)
- macOS (required for py2app)

## Build Instructions

### Development Build (Alias Mode)

For testing and development, use alias mode which creates a lightweight `.app` that links to your source code:

```bash
uv run python setup.py py2app -A
```

This creates `dist/Whisper.app` that:
- ✅ Can be launched by double-clicking
- ✅ Appears in menu bar with 🎤 icon
- ✅ Works via Spotlight search
- ⚠️ Still requires the source code directory (creates symlinks)

### Production Build (Standalone)

**Note:** Currently, production builds fail with Python 3.13 due to a recursion error in py2app/modulegraph. Use alias mode (-A) for now, or downgrade to Python 3.11.

For a fully standalone build that can be distributed:

```bash
uv run python setup.py py2app
```

This would create a completely self-contained app, but requires Python 3.11 or earlier.

## Using the App

### Launch the App

After building, you can:

1. **Double-click** to launch:
   ```bash
   open dist/Whisper.app
   ```

2. **Copy to Applications** folder:
   ```bash
   cp -r dist/Whisper.app /Applications/
   ```

3. **Launch via Spotlight**:
   - Press `Cmd+Space`
   - Type "Whisper"
   - Press Enter

### Using the Menu Bar App

Once launched:
- Look for the 🎤 icon in your menu bar (top-right corner)
- Click it to see the menu
- Select "Start Recording" to begin transcription
- The app has no Dock icon (LSUIElement is set to True)

### Quit the App

- Click the 🎤 icon in the menu bar
- Select "Quit" from the menu

Or force quit:
```bash
pkill -f Whisper.app
```

## Clean Build

To clean build artifacts before rebuilding:

```bash
rm -rf build dist
uv run python setup.py py2app -A
```

## Add to Login Items (Auto-start on Login)

To make Whisper start automatically when you log in:

1. Open **System Preferences** → **Users & Groups**
2. Click **Login Items**
3. Click the **+** button
4. Navigate to `/Applications/Whisper.app` (or `dist/Whisper.app`)
5. Click **Add**

Now Whisper will launch automatically when you log in to macOS.

## Troubleshooting

### App won't launch

Check Console.app for error messages:
1. Open **Console.app** (via Spotlight)
2. Search for "Whisper"
3. Look for errors when launching the app

### Microphone permissions

On first launch, macOS will prompt for microphone access. Grant it in:
- **System Preferences** → **Security & Privacy** → **Privacy** → **Microphone**

### Accessibility permissions

For auto-paste to work, grant Accessibility permissions:
- **System Preferences** → **Security & Privacy** → **Privacy** → **Accessibility**
- Add `Whisper.app` to the list

### Python version issues

If you get recursion errors during build:
```bash
# Check your Python version
python --version

# py2app works best with Python 3.11 or earlier
# Consider using pyenv to install Python 3.11
```

## Configuration

The app is configured in `setup.py` with:

- **Bundle Name**: Whisper
- **Bundle Identifier**: com.whisper.transcription
- **LSUIElement**: True (no Dock icon, menu bar only)
- **Version**: 0.1.0

To customize, edit `setup.py` and rebuild.
