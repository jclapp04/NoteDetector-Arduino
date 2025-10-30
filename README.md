# NoteDetector-Arduino
The purpose of this project is to identify the musical notes played by musical instruments by recording the frequency of the sounds with an Aduino-compatible microphone and transmitting the information to the machine learning model that will be used to classify the notes. It aims to develop a cost effective and simple to assemble note detection system to hobbyists and students.
## Requirements

- **Hardware**
  - Arduino Mega 
  - Microphone sound sensor module
  - USB cable for Arduino
  - Jumper wires and breadboard

- **Software & Accounts**
  - [Arduino IDE](https://www.arduino.cc/en/software)
  - Python
  - [HuggingFace account](https://huggingface.co/) 
  - GitHub account 

Single-Digit 7-Segment Display Setup (Single-Resistor Version)
Components
1 × Arduino Mega 2560 (or Uno)
1 × Single-digit 7-segment display (common cathode)
1 × 220 Ω – 1 kΩ resistor
Breadboard and jumper wires
Wiring Instructions
Place the 7-segment display in the center of the breadboard so that each side of pins sits on a separate row.
Identify the display pins. A typical layout (from top left down one side and up the other) is:
a, f, GND, b,
DP, c, GND, d, e, g
(Refer to your display’s datasheet if the order differs.)
Connect one of the common-cathode pins to Arduino GND through a single resistor (220 Ω – 1 kΩ).
Connect the other common-cathode pin directly to GND.
Connect each segment pin directly to the Arduino pins shown below:
Segment	Arduino Pin
a	D2
b	D3
c	D4
d	D5
e	D6
f	D7
g	D8
(optional) DP	D9
Verify connections:
Only the GND line uses a resistor.
No segment line uses a resistor individually.
Each Arduino pin connects directly to its segment pin.
Power the Arduino from USB or a 5 V source.
Test Code
int segPins[7] = {2, 3, 4, 5, 6, 7, 8}; // a–g pins

int numbers[10][7] = {
  {1,1,1,1,1,1,0}, // 0
  {0,1,1,0,0,0,0}, // 1
  {1,1,0,1,1,0,1}, // 2
  {1,1,1,1,0,0,1}, // 3
  {0,1,1,0,0,1,1}, // 4
  {1,0,1,1,0,1,1}, // 5
  {1,0,1,1,1,1,1}, // 6
  {1,1,1,0,0,0,0}, // 7
  {1,1,1,1,1,1,1}, // 8
  {1,1,1,1,0,1,1}  // 9
};

void setup() {
  for (int i = 0; i < 7; i++) {
    pinMode(segPins[i], OUTPUT);
  }
}

void loop() {
  for (int n = 0; n < 10; n++) {
    for (int i = 0; i < 7; i++) {
      digitalWrite(segPins[i], numbers[n][i]);
    }
    delay(1000); // show each number for 1 second
  }
}
For common-anode displays, invert the logic by replacing:
digitalWrite(segPins[i], numbers[n][i]);
with:
digitalWrite(segPins[i], !numbers[n][i]);
Expected Result
After uploading the sketch:
The display will cycle through digits 0 → 9, showing each for one second.
Brightness may vary slightly between digits because all segments share a single current-limiting resistor.
