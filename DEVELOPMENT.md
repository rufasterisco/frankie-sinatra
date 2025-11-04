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

### Phase ?: macOS Menu Bar App with rumps
- [ ] Research rumps library and menu bar app patterns
- [ ] Add rumps dependency
- [ ] Create basic menu bar app with icon
- [ ] Implement Start/Stop transcription from menu
- [ ] Add visual indicator for recording state (icon changes)
- [ ] Add menu items for basic settings
- [ ] Test menu bar app functionality
- [ ] Update documentation with menu bar usage

### Phase ?: Dynamic Settings in Menu Bar App
- [ ] Research how to pass live parameters via rumps menus
- [ ] Add language selection submenu
- [ ] Add model selection submenu
- [ ] Add settings for silence threshold/duration
- [ ] Implement settings persistence (save user preferences)
- [ ] Add visual feedback for current settings
- [ ] Update menu dynamically based on state

### Phase ?: Standalone Application Packaging
- [ ] Research py2app configuration
- [ ] Create setup.py for py2app
- [ ] Test building standalone .app bundle
- [ ] Configure app icons and metadata
- [ ] Test launching .app without terminal
- [ ] Add instructions for building standalone app
- [ ] Optional: Add to Login Items instructions

### Phase ?: Audio File Cleanup
- [ ] Add option to delete WAV files after transcription
- [ ] Implement --keep-audio flag to preserve recordings
- [ ] Add cleanup for old recordings (configurable retention period)
- [ ] Add menu option to clean up all recordings
- [ ] Update documentation with cleanup options

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
