# Makefile for Whisper Transcription macOS App

# Variables
PYTHON := uv run python
APP_NAME := Whisper
DIST_DIR := dist
BUILD_DIR := build
APP_BUNDLE := $(DIST_DIR)/$(APP_NAME).app
INSTALL_DIR := /Applications

# Phony targets (not actual files)
.PHONY: all build build-dev install clean help run test

# Default target
all: build-dev

# Build the app in development/alias mode (faster, for testing)
build-dev: clean
	@echo "Building $(APP_NAME).app in development mode..."
	$(PYTHON) setup.py py2app -A
	@echo "✓ Build complete: $(APP_BUNDLE)"

# Build the app in production mode (standalone, self-contained)
build: clean
	@echo "Building $(APP_NAME).app in production mode..."
	$(PYTHON) setup.py py2app
	@echo "✓ Build complete: $(APP_BUNDLE)"

# Install the app to /Applications
install: build-dev
	@echo "Installing $(APP_NAME).app to $(INSTALL_DIR)..."
	cp -r $(APP_BUNDLE) $(INSTALL_DIR)/
	@echo "✓ Installed to $(INSTALL_DIR)/$(APP_NAME).app"
	@echo "You can now launch via Spotlight (Cmd+Space, type 'Whisper')"

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf $(BUILD_DIR) $(DIST_DIR)
	@echo "✓ Clean complete"

# Run the app from the build directory
run: build-dev
	@echo "Launching $(APP_NAME).app..."
	open $(APP_BUNDLE)

# Run the Python script directly (for development)
dev:
	@echo "Running menu bar app directly..."
	uv run transcribe_menubar.py

# Install Python dependencies
deps:
	@echo "Installing dependencies..."
	uv sync
	@echo "✓ Dependencies installed"

# Uninstall the app from /Applications
uninstall:
	@echo "Uninstalling $(APP_NAME).app from $(INSTALL_DIR)..."
	rm -rf $(INSTALL_DIR)/$(APP_NAME).app
	@echo "✓ Uninstalled"

# Show help
help:
	@echo "Whisper Transcription - Available Make Targets:"
	@echo ""
	@echo "  make              - Build app in development mode (default)"
	@echo "  make build-dev    - Build app in development/alias mode (fast)"
	@echo "  make build        - Build app in production mode (standalone)"
	@echo "  make install      - Build and install app to /Applications"
	@echo "  make run          - Build and launch the app"
	@echo "  make dev          - Run the Python script directly"
	@echo "  make clean        - Remove build artifacts"
	@echo "  make deps         - Install Python dependencies"
	@echo "  make uninstall    - Remove app from /Applications"
	@echo "  make help         - Show this help message"
	@echo ""
