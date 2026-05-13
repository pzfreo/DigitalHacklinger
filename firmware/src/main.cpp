// Digital Hacklinger — single-sensor bring-up.
// Reads SS495A1 → ADS1219 AIN0 single-ended, prints raw counts + millivolts.

#include <Arduino.h>
#include <Wire.h>

constexpr uint8_t ADS1219_ADDR  = 0x40;   // SparkX board default

// Commands (datasheet table 13)
constexpr uint8_t CMD_RESET     = 0x06;
constexpr uint8_t CMD_START     = 0x08;
constexpr uint8_t CMD_RDATA     = 0x10;
constexpr uint8_t CMD_WREG      = 0x40;

// Config register (datasheet table 14)
//   bits 7:5  MUX = 011  → AIN0 vs AVSS (single-ended)
//   bit  4    GAIN = 0   → 1×
//   bits 3:2  DR  = 00   → 20 SPS
//   bit  1    CM  = 1    → continuous conversions
//   bit  0    VREF = 0   → internal 2.048 V
constexpr uint8_t CFG_VALUE     = (0b011 << 5) | (0 << 4) | (0b00 << 2) | (1 << 1) | 0;
constexpr float   VREF_MV       = 2048.0f;
constexpr float   FS_COUNTS     = 8388608.0f;   // 2^23 — single-ended range

static void sendCmd(uint8_t cmd) {
  Wire.beginTransmission(ADS1219_ADDR);
  Wire.write(cmd);
  Wire.endTransmission();
}

static void writeConfig(uint8_t value) {
  Wire.beginTransmission(ADS1219_ADDR);
  Wire.write(CMD_WREG);
  Wire.write(value);
  Wire.endTransmission();
}

static int32_t readData() {
  Wire.beginTransmission(ADS1219_ADDR);
  Wire.write(CMD_RDATA);
  Wire.endTransmission();
  Wire.requestFrom((uint8_t)ADS1219_ADDR, (uint8_t)3);
  int32_t v = ((int32_t)Wire.read() << 16)
            | ((int32_t)Wire.read() << 8)
            |  (int32_t)Wire.read();
  if (v & 0x800000) v |= 0xFF000000;   // sign-extend 24 → 32
  return v;
}

void setup() {
  Serial.begin(115200);
  while (!Serial && millis() < 3000) {}
  Wire.begin();

  delay(50);
  sendCmd(CMD_RESET);
  delay(5);
  writeConfig(CFG_VALUE);
  sendCmd(CMD_START);
  delay(100);   // let the first 20-SPS conversion complete

  Serial.println("# raw_counts, mV");
}

void loop() {
  int32_t raw = readData();
  float   mV  = (raw / FS_COUNTS) * VREF_MV;
  Serial.printf("%ld, %.3f\n", (long)raw, mV);
  delay(50);    // sample-rate-matched print at 20 Hz
}
