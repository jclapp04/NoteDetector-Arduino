🎶 Real-Time Audio Volume Visualizer (Python + Arduino)

This project measures live microphone volume in Python and displays the loudness level on a 7-segment Arduino display in real time.
The Python script analyzes microphone input, calculates the RMS loudness level, converts it to a digit between 0 and 9, and sends that digit over serial to an Arduino.
The Arduino receives the digit and updates a single-digit 7-segment display accordingly.

🚀 Features

Real-time audio input using PyAudio

Live RMS loudness detection

Smoothed volume measurement (reduces jitter)

Volume mapped to digits (0–9)

Serial communication from Python → Arduino

Physical visualization on a 7-segment display

Runs on macOS (and works on Windows/Linux too)

🧰 Materials Used

Hardware

Arduino Mega 2560 (Uno/Nano also work)

1× Single-digit 7-segment display (common-cathode)

7× current-limiting resistors (220–330 Ω)

Breadboard

Jumper wires

USB cable

Microphone

Built-in laptop mic or external mic

Software

Python 3

Arduino IDE

Python libraries:

pyaudio

numpy

pyserial

🔧 How It Works

1️⃣ Python Reads Microphone Audio
The script captures small chunks of live audio using PyAudio.

2️⃣ Volume is Computed
Each audio chunk is:
Converted to numeric samples
RMS loudness is computed
Loudness is smoothed using a rolling average
The volume is normalized so it always fits 0–9

3️⃣ Digit Sent to Arduino (0–9)
Python sends a single ASCII digit '0'–'9' to the Arduino over serial at 9600 baud.

4️⃣ Arduino Displays the Volume

The Arduino:
Reads the incoming byte
Converts it to a number
Lights the correct segments on the 7-segment display
The display updates in real time with your voice or any sound in the room.

🖥️ System Flow

[ Microphone ]
       ↓
[ Python (PyAudio) ]
       ↓
[ RMS Volume Calculation ]
       ↓
[ Map: Volume → Digit (0–9) ]
       ↓
[ Serial Output (9600 baud) ]
       ↓
[ Arduino Mega ]
       ↓
[ 7-Segment LED Display ]

🛠️ Setup Instructions

1. Arduino Setup

Wiring

Connect segments a–g + dp to pins 4–11

Each pin passes through a 220–330Ω resistor

Common cathode → GND

Upload the Arduino code

Make sure this is in your sketch:

Serial.begin(9600);

Test the display:

Open Serial Monitor (9600 baud)

Type 5 → the 7-segment should show 5

2. Python Setup

Install dependencies:

pip install pyaudio numpy pyserial

Run the script:

python NoteDetection.py

Choose your microphone device when prompted.

Make sure your serial port matches your Arduino:

SERIAL_PORT = "/dev/cu.usbmodemXXXX"

📊 Example Terminal Output

Volume: ██████████.................................  [digit sent: 2]

Volume: ██████████████████......................... [digit sent: 4]

And on the 7-segment display, you’ll see the digit change dynamically as the volume increases or decreases.



