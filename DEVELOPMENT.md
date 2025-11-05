# Development Progress

## Project Goal

Create a simple POC to evaluate the quality of local Whisper transcription for speech-to-text.

## Requirements

- [x] Minimal setup complexity
- [ ] Real-time or near real-time transcription
- [ ] Quality evaluation capability
- [ ] Easy to test different model sizes

## Implementation Plan

### Phase 1: Basic POC ✅
- [x] Create README.md with usage instructions
- [x] Create DEVELOPMENT.md for tracking
- [x] Implement basic transcription script
- [x] Add pyproject.toml for uv dependency management
- [x] Test with default model
- [x] Verify quality is acceptable

### Phase 2: Keystroke Activation ✅
- [x] Research global hotkey libraries for macOS
- [x] Implement global keystroke listener (pynput)
- [x] Integrate hotkey with recording workflow
- [x] Add double-tap right Command key detection
- [x] Support for custom hotkey combinations
- [x] Add visual feedback for recording state (console messages)
- [x] Document accessibility permissions requirements
- [x] Update documentation with hotkey usage

### Phase 3: Auto-Paste Transcription ✅
- [x] Research clipboard and paste automation on macOS
- [x] Implement clipboard integration
- [x] Add auto-paste to active application
- [x] Add option to disable auto-paste (clipboard only)
- [x] Update documentation with auto-paste feature

### Phase 4: Silence Detection Auto-Stop ✅
- [x] Research silence detection algorithms
- [x] Implement audio level monitoring (RMS-based)
- [x] Add configurable silence threshold (dB)
- [x] Add configurable silence duration (seconds before auto-stop)
- [x] Enable auto-stop by default with --no-auto-stop to disable
- [x] Test with different speaking patterns and environments
- [x] Clean implementation with monitoring thread
- [x] Update documentation with tuning parameters

### Phase 5: Audio File Cleanup ✅
- [x] Delete WAV and TXT files by default after transcription
- [x] Add --keep-audio flag to preserve all files
- [x] Update documentation with cleanup options
- [x] Test audio cleanup functionality

### Phase 6: macOS Menu Bar App with rumps ✅
- [x] Research rumps library and menu bar app patterns
- [x] Add rumps dependency
- [x] Create basic menu bar app with icon
- [x] Implement Start/Stop transcription from menu
- [x] Add visual indicator for recording state (icon changes)
- [x] Add menu items for basic settings (auto-paste, auto-stop, keep audio)
- [x] Test menu bar app functionality
- [x] Update documentation with menu bar usage

### Phase 7: Standalone Application Packaging ✅
- [x] Research py2app configuration
- [x] Add py2app dependency
- [x] Create setup.py for py2app with LSUIElement
- [x] Test building .app bundle (alias mode works, production has Python 3.13 issue)
- [x] Configure app metadata (bundle ID, version, microphone permissions)
- [x] Test launching .app without terminal
- [x] Create BUILD.md with detailed build instructions
- [x] Create Makefile for easy building and installation
- [x] Add instructions for Login Items auto-start
- [x] Update README with installation options

### Phase 8: Global Hotkey Support in Menu Bar App ✅
- [x] Integrate double-tap Command key detection into menu bar app
- [x] Run keyboard listener in background thread
- [x] Allow both menu-based and hotkey-based recording triggers
- [x] Update menu to show current hotkey setting
- [x] Test hotkey and menu triggers work together
- [x] Verified working in Python version (minor .app bundle display issue)

### Phase ?: Dynamic Settings in Menu Bar App
- [ ] Research how to pass live parameters via rumps menus
- [ ] Add language selection submenu
- [ ] Add model selection submenu
- [ ] Add settings for silence threshold/duration
- [ ] Implement settings persistence (save user preferences)
- [ ] Add visual feedback for current settings
- [ ] Update menu dynamically based on state

### Phase ?: Quality Evaluation (Future)
- [ ] Compare different model sizes
- [ ] Measure transcription accuracy
- [ ] Benchmark performance (speed vs quality)
- [ ] Test with different audio conditions

### Phase ?: Advanced Features (Future)
- [ ] Add real-time streaming transcription
- [ ] Add support for different languages
- [ ] Implement audio pre-processing
- [ ] Integration with text editors

## Technical Decisions

### Package Management
- **Tool:** `uv` (fast, modern Python package manager)
- **Why:** Faster dependency resolution, simpler setup, automatic virtual environment management
- **Alternative considered:** `pip` + `venv` (more traditional, but slower)

### Whisper Implementation
- **Library:** `openai-whisper` (official implementation)
- **Alternative considered:** `faster-whisper` (more performant, but adds complexity)
- **Default model:** `base` (good balance of speed and quality)

### Audio Input
- **Library:** `sounddevice` + `soundfile` for recording
- **Format:** WAV (uncompressed, best quality)
- **Sample rate:** 16000 Hz (Whisper's native rate)

### Hotkey Activation
- **Library:** `pynput` (cross-platform keyboard listener)
- **Default trigger:** Double-tap right Command key (0.3s delay)
- **Why double-tap:** Non-intrusive, unlikely to conflict with other shortcuts
- **Alternative:** Custom hotkey combinations supported via `--hotkey` flag
- **macOS requirement:** Accessibility permissions needed for global hotkey detection

### Auto-Paste Integration
- **Clipboard library:** `pyperclip` (cross-platform clipboard operations)
- **Paste mechanism:** Simulates Cmd+V using pynput keyboard controller
- **Default behavior:** Auto-paste enabled (transcription automatically inserted at cursor)
- **Alternative:** `--no-paste` flag for clipboard-only mode
- **Use case:** Hands-free dictation directly into any application

### Dependencies
- `openai-whisper`: Core transcription
- `sounddevice`: Microphone recording
- `soundfile`: Audio file handling
- `numpy`: Audio data processing
- `pynput`: Global hotkey detection and keyboard simulation
- `pyperclip`: Clipboard operations

## Development Notes

### 2025-11-04
- Project initialized
- Documentation structure created
- Implemented basic transcription script with CLI args
- Switched to uv for package management
- Installed dependencies and tested transcription
- **Phase 1 complete** - Quality verified as acceptable
- Implemented Phase 2: Keystroke activation for macOS
  - Added pynput for global hotkey detection
  - Implemented double-tap right Command key as default activation
  - Supports custom hotkey combinations
  - Updated all documentation
- **Phase 2 complete** - Double-tap activation working

### 2025-11-05
- **Phase 3 complete** - Auto-paste transcription to active application
- **Phase 4 complete** - Silence detection auto-stop
- **Phase 5 complete** - Audio file cleanup
- **Phase 6 complete** - macOS Menu Bar App
  - Added rumps dependency
  - Created transcribe_menubar.py with menu bar interface
  - Visual status indicators (🎤 → 🔴 → ⏳ → 🎤)
  - Settings menu with toggles for auto-paste, auto-stop, and keep-audio
  - Background model loading
  - Integrated all existing transcription features
- **Phase 7 complete** - Standalone Application Packaging
  - Added py2app for building .app bundles
  - Created setup.py with LSUIElement configuration
  - Created Makefile with standard targets (build, install, clean, etc.)
  - Created BUILD.md with comprehensive build and installation instructions
  - App can be installed to /Applications and launched via Spotlight
  - Supports auto-start via Login Items
- **Phase 8 complete** - Global Hotkey Support in Menu Bar App
  - Integrated double-tap right Command key detection
  - Keyboard listener runs in background thread
  - Both menu-based and hotkey triggers work together
  - Added Settings menu toggle for hotkey enable/disable
  - Renamed app to "Lolalola"

## Testing Checklist

- [ ] Test installation on clean environment
- [ ] Test with different microphone inputs
- [ ] Test with pre-recorded audio files
- [ ] Test all model sizes
- [ ] Test transcription accuracy with known text
- [ ] Test error handling (no microphone, interrupted recording, etc.)

## Known Limitations

1. First run downloads the model (~150MB for base, more for larger models)
2. Transcription is not real-time (processes after recording completes)
3. Requires FFmpeg system dependency
4. Larger models require significant RAM

## Performance Targets

- [ ] Transcription should complete within 2x audio duration
- [ ] Memory usage should stay under 2GB for base model
- [ ] Setup should take < 5 minutes for new users

## Future Improvements

- Streaming transcription for real-time feedback
- Web interface for easier usage
- Batch processing for multiple files
- Integration with text editors
- Custom vocabulary/terminology support
