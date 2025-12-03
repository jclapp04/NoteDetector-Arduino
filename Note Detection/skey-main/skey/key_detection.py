import pyaudio
import wave
import numpy as np
from skey import detect_key
import tempfile
import os
from collections import Counter, deque
import sys
import logging
import math
import serial
import time

# --- Suppress logs ---
logging.getLogger().setLevel(logging.ERROR)

# --- Audio settings ---
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

# --- Accuracy settings ---
BUFFER_SECONDS = 15
OVERLAP_SECONDS = 10
MAX_HISTORY = 3
DEVICE = "cpu"

# --- Volume visualization settings ---
SMOOTH_WINDOW = 15      # average last N chunks
DYNAMIC_SCALE = True    # auto-adjusts to mic input
MANUAL_SCALE = 2000     # fallback manual sensitivity
MIN_VALID_SAMPLES = 100 # ignore empty chunks

# --- Initialize PyAudio ---
p = pyaudio.PyAudio()
print("\nAvailable audio input devices:")
for i in range(p.get_device_count()):
    dev = p.get_device_info_by_index(i)
    if dev["maxInputChannels"] > 0:
        print(f"  [{i}] {dev['name']}")

try:
    device_index = int(input("\nEnter the device index to use: "))
except ValueError:
    device_index = None

recent_predictions = []
overlap_frames = []
volume_history = deque(maxlen=SMOOTH_WINDOW)

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=CHUNK)

# -----------------------------
# SERIAL CONNECTION TO ARDUINO
# -----------------------------
# !!! Make sure this matches the port you see in Arduino IDE (Tools -> Port)
SERIAL_PORT = "/dev/cu.usbmodem1101"   # update if needed
BAUD = 9600                            # must match Serial.begin(9600) in Arduino

try:
    ser = serial.Serial(SERIAL_PORT, BAUD, timeout=0)
    time.sleep(2)  # allow Arduino to reset after opening the port
    print(f"\nConnected to Arduino on {SERIAL_PORT} at {BAUD} baud")
except Exception as e:
    print(f"\nFailed to connect to Arduino: {e}")
    ser = None

print("\nStarting live key detection...")
print(f"- Buffer: {BUFFER_SECONDS}s")
print(f"- Overlap: {OVERLAP_SECONDS}s")
print(f"- Smoothing: last {MAX_HISTORY} predictions")
print(f"- Device: {DEVICE}")
print("Press Ctrl+C to stop.\n")

try:
    while True:
        frames = []
        if overlap_frames:
            frames.extend(overlap_frames)

        if overlap_frames:
            new_frames_needed = int(RATE / CHUNK * (BUFFER_SECONDS - OVERLAP_SECONDS))
        else:
            new_frames_needed = int(RATE / CHUNK * BUFFER_SECONDS)

        print("\nRecording... (live volume updates below)")
        for _ in range(new_frames_needed):
            try:
                data = stream.read(CHUNK, exception_on_overflow=False)
            except IOError:
                # Handle stream underrun gracefully
                continue

            frames.append(data)

            # --- Calculate RMS safely ---
            audio_data = np.frombuffer(data, dtype=np.int16)
            if len(audio_data) < MIN_VALID_SAMPLES:
                rms = 0.0
            else:
                rms = math.sqrt(np.mean(audio_data.astype(np.float64) ** 2))

            if math.isnan(rms) or rms < 0:
                rms = 0.0

            # --- Smoothing ---
            volume_history.append(rms)
            avg_rms = np.mean(volume_history)
            if math.isnan(avg_rms):
                avg_rms = 0.0

            # --- Dynamic scaling ---
            if DYNAMIC_SCALE:
                scale = max(MANUAL_SCALE, np.max(volume_history) * 1.5)
            else:
                scale = MANUAL_SCALE

            normalized = min(1.0, avg_rms / scale)
            bar_len = int(normalized * 50)
            bar = "█" * bar_len
            sys.stdout.write(f"\rVolume: {bar:<50} {avg_rms:8.1f}")
            sys.stdout.flush()

            # --- Send volume level to Arduino as digit 0–9 ---
            if ser is not None:
                digit = int(round(normalized * 9))   # 0.0–1.0 -> 0–9
                digit = max(0, min(9, digit))        # clamp to [0, 9]

                try:
                    ser.write(str(digit).encode("ascii"))  # send single char '0'–'9'
                    sys.stdout.write(f"  [digit sent: {digit}]")
                    sys.stdout.flush()
                except Exception:
                    # If serial write fails, do not crash the audio loop
                    pass

        print("\nRecording complete. Analyzing key...\n")

        # --- keep overlap for smoother detection windows ---
        overlap_frame_count = int(RATE / CHUNK * OVERLAP_SECONDS)
        overlap_frames = frames[-overlap_frame_count:]

        # --- Save audio buffer to temp wav file ---
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_path = temp_file.name
            wf = wave.open(temp_path, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
            wf.close()

        # --- Run key detection on the temp file ---
        try:
            result = detect_key(temp_path, extension="wav", device=DEVICE)

            if isinstance(result, list):
                key_detected = result[0] if result else "Unknown"
            elif isinstance(result, dict):
                key_detected = result.get('key', 'Unknown')
            else:
                key_detected = str(result)

            recent_predictions.append(key_detected)
            if len(recent_predictions) > MAX_HISTORY:
                recent_predictions.pop(0)

            key_counts = Counter(recent_predictions)
            smoothed_key = key_counts.most_common(1)[0][0]
            confidence = key_counts.most_common(1)[0][1]

            print(f"Raw detection: {key_detected}")
            print(f"Smoothed key: {smoothed_key} (confidence: {confidence}/{len(recent_predictions)})")
            print(f"Recent history: {recent_predictions}")
            print("-" * 50)

        except Exception as e:
            print(f"Error during detection: {e}")

        finally:
            # Always delete temp file
            os.unlink(temp_path)

except KeyboardInterrupt:
    print("\n\nStopping live key detection...")

    try:
        stream.stop_stream()
        stream.close()
    except Exception:
        pass

    try:
        p.terminate()
    except Exception:
        pass

    print("Done.")

