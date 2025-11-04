#!/usr/bin/env python3
"""
Simple Whisper transcription POC
Record audio from microphone or transcribe existing files
"""

import argparse
import os
from datetime import datetime
from pathlib import Path

import numpy as np
import sounddevice as sd
import soundfile as sf
import whisper


def record_audio(duration=None, sample_rate=16000):
    """
    Record audio from the default microphone.

    Args:
        duration: Recording duration in seconds (None for manual stop)
        sample_rate: Sample rate in Hz (16000 is Whisper's native rate)

    Returns:
        numpy array with audio data
    """
    print("Recording... (Press Ctrl+C to stop)")

    try:
        if duration:
            print(f"Recording for {duration} seconds...")
            audio = sd.rec(
                int(duration * sample_rate),
                samplerate=sample_rate,
                channels=1,
                dtype='float32'
            )
            sd.wait()
        else:
            # Record until Ctrl+C
            audio = []
            with sd.InputStream(samplerate=sample_rate, channels=1, dtype='float32') as stream:
                print("Recording... Press Ctrl+C to stop")
                while True:
                    chunk, _ = stream.read(sample_rate)
                    audio.append(chunk)
    except KeyboardInterrupt:
        print("\nRecording stopped.")
        if not duration:
            audio = np.concatenate(audio, axis=0)

    return audio


def save_audio(audio, sample_rate=16000, filename="recording.wav"):
    """Save audio data to a WAV file."""
    sf.write(filename, audio, sample_rate)
    print(f"Audio saved to {filename}")
    return filename


def transcribe_audio(audio_path, model_name="base"):
    """
    Transcribe audio file using Whisper.

    Args:
        audio_path: Path to audio file
        model_name: Whisper model size (tiny, base, small, medium, large)

    Returns:
        Transcription result dictionary
    """
    print(f"\nLoading Whisper model: {model_name}")
    print("(First run will download the model, this may take a few minutes)")

    model = whisper.load_model(model_name)

    print("Transcribing...")
    result = model.transcribe(audio_path)

    return result


def save_transcription(text, output_dir="transcriptions"):
    """Save transcription with timestamp."""
    Path(output_dir).mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{output_dir}/transcription_{timestamp}.txt"

    with open(filename, "w") as f:
        f.write(text)

    print(f"Transcription saved to {filename}")
    return filename


def main():
    parser = argparse.ArgumentParser(
        description="Simple Whisper transcription POC"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="base",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model size (default: base)"
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Audio file to transcribe (skip recording)"
    )
    parser.add_argument(
        "--duration",
        type=int,
        help="Recording duration in seconds (default: manual stop with Ctrl+C)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="transcription.txt",
        help="Output file for transcription (default: transcription.txt)"
    )
    parser.add_argument(
        "--keep-audio",
        action="store_true",
        help="Keep the recorded audio file"
    )

    args = parser.parse_args()

    # Step 1: Get audio file
    if args.file:
        if not os.path.exists(args.file):
            print(f"Error: File not found: {args.file}")
            return 1
        audio_path = args.file
        print(f"Using audio file: {audio_path}")
    else:
        # Record audio
        audio_data = record_audio(duration=args.duration)
        audio_path = save_audio(audio_data, filename="temp_recording.wav")

    # Step 2: Transcribe
    try:
        result = transcribe_audio(audio_path, model_name=args.model)

        # Step 3: Display and save results
        print("\n" + "="*60)
        print("TRANSCRIPTION:")
        print("="*60)
        print(result["text"])
        print("="*60)

        # Save main transcription
        with open(args.output, "w") as f:
            f.write(result["text"])
        print(f"\nTranscription saved to {args.output}")

        # Save detailed version with timestamps
        save_transcription(result["text"])

        # Display detected language
        if "language" in result:
            print(f"\nDetected language: {result['language']}")

    finally:
        # Cleanup temporary audio file
        if not args.file and not args.keep_audio:
            if os.path.exists(audio_path):
                os.remove(audio_path)
                print(f"\nTemporary audio file removed: {audio_path}")

    return 0


if __name__ == "__main__":
    exit(main())
